from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import cast

import httpx
from pydantic import ValidationError

from xai_cli.client.models import (
    CompletedEvent,
    DeltaEvent,
    ErrorEvent,
    FailedEvent,
    IncompleteEvent,
    ModelsResponse,
    ResponseEnvelope,
    ResponseRequest,
    StreamEvent,
)
from xai_cli.errors import (
    ApiError,
    AuthError,
    IncompleteResponseError,
    InvalidRequestError,
    NetworkError,
    RateLimitError,
    StreamError,
)

BASE_URL = "https://api.x.ai/v1"
DEFAULT_TIMEOUT = httpx.Timeout(120.0, connect=10.0)
MAX_RETRIES = 2
MAX_RETRY_DELAY = 2.0
RETRYABLE_GET_STATUS_CODES = frozenset({429, 502, 503, 504})
RETRYABLE_POST_STATUS_CODES = frozenset({429, 503})


class ApiClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        timeout: httpx.Timeout = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not api_key:
            raise AuthError("API key is not configured. Run 'xai config init' or set XAI_API_KEY.")
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
            transport=transport,
        )
        self._api_key = api_key
        self._sleep = sleep

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def create_response(self, request: ResponseRequest) -> ResponseEnvelope:
        response = self._request(
            "POST",
            "/responses",
            json_body=request.model_dump(mode="json", exclude_none=True),
        )
        try:
            parsed = ResponseEnvelope.model_validate(response.json())
        except (json.JSONDecodeError, ValidationError) as exc:
            raise IncompleteResponseError("The API returned an invalid response document.") from exc
        _require_complete(parsed)
        return parsed

    def list_models(self) -> ModelsResponse:
        response = self._request("GET", "/models")
        try:
            return ModelsResponse.model_validate(response.json())
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ApiError("The models endpoint returned invalid JSON.") from exc

    @contextmanager
    def stream_response(self, request: ResponseRequest) -> Iterator[Iterator[StreamEvent]]:
        try:
            for attempt in range(MAX_RETRIES + 1):
                with self._client.stream(
                    "POST",
                    "/responses",
                    json=request.model_dump(mode="json", exclude_none=True),
                ) as response:
                    retry_delay = _retry_delay(response, "POST", attempt)
                    if retry_delay is not None:
                        response.read()
                        self._sleep(retry_delay)
                        continue
                    _raise_for_status(response, self._api_key)
                    yield self._decode_stream(response)
                    return
        except (AuthError, ApiError, InvalidRequestError, RateLimitError):
            raise
        except httpx.TimeoutException as exc:
            raise NetworkError("The streaming request timed out.") from exc
        except httpx.RequestError as exc:
            raise NetworkError("The streaming connection was interrupted.") from exc

    def _decode_stream(self, response: httpx.Response) -> Iterator[StreamEvent]:
        terminal = False
        for data in _iter_sse_data(response.iter_lines()):
            if data == "[DONE]":
                break
            event = _parse_stream_event(data)
            if event is None:
                continue
            yield event
            if isinstance(event, CompletedEvent):
                _require_complete(event.response)
                terminal = True
                break
            if isinstance(event, FailedEvent):
                message = event.error.message if event.error else "The response failed."
                raise StreamError(message)
            if isinstance(event, IncompleteEvent):
                raise IncompleteResponseError("The API reported an incomplete response.")
            if isinstance(event, ErrorEvent):
                raise StreamError(event.detail.message)
        if not terminal:
            raise IncompleteResponseError("The stream ended before a completion event.")

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, object] | None = None,
    ) -> httpx.Response:
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.request(method, path, json=json_body)
            except httpx.TimeoutException as exc:
                raise NetworkError("The API request timed out.") from exc
            except httpx.RequestError as exc:
                raise NetworkError("The API request could not be completed.") from exc
            retry_delay = _retry_delay(response, method, attempt)
            if retry_delay is not None:
                response.close()
                self._sleep(retry_delay)
                continue
            _raise_for_status(response, self._api_key)
            return response
        raise RuntimeError("Retry loop ended without returning a response.")


def _require_complete(response: ResponseEnvelope) -> None:
    if response.status not in {None, "completed"}:
        raise IncompleteResponseError(
            f"The API returned response status {response.status!r} instead of 'completed'."
        )
    if not response.text:
        raise IncompleteResponseError("The API response contains no generated text.")


def _raise_for_status(response: httpx.Response, api_key: str) -> None:
    status = response.status_code
    if 200 <= status < 300:
        return
    response.read()
    message = _api_error_message(response).replace(api_key, "[redacted]")
    if status in {401, 403}:
        raise AuthError(f"xAI rejected authentication ({status}): {message}")
    if status in {400, 422}:
        raise InvalidRequestError(f"xAI rejected the request ({status}): {message}")
    if status == 429:
        raise RateLimitError(f"xAI rate limit exceeded (429): {message}")
    if status >= 500:
        raise ApiError(f"xAI service error ({status}); retry later: {message}")
    raise ApiError(f"xAI API returned HTTP {status}: {message}")


def _api_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict) and isinstance(error.get("message"), str):
            return cast(str, error["message"])[:500]
        if isinstance(error, str):
            return error[:500]
        if isinstance(payload.get("message"), str):
            return cast(str, payload["message"])[:500]
    text = response.text.strip()
    return text[:500] if text else "No error details were returned."


def _retry_delay(response: httpx.Response, method: str, attempt: int) -> float | None:
    normalized_method = method.upper()
    retryable_statuses = (
        RETRYABLE_GET_STATUS_CODES if normalized_method == "GET" else RETRYABLE_POST_STATUS_CODES
    )
    if (
        normalized_method not in {"GET", "POST"}
        or response.status_code not in retryable_statuses
        or attempt >= MAX_RETRIES
    ):
        return None
    retry_after = response.headers.get("Retry-After")
    if normalized_method == "POST" and retry_after is None:
        return None
    if retry_after is None:
        return min(0.25 * 2.0**attempt, MAX_RETRY_DELAY)
    delay = _parse_retry_after(retry_after)
    if delay is None or delay > MAX_RETRY_DELAY:
        return None
    return delay


def _parse_retry_after(value: str) -> float | None:
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=UTC)
    return max(0.0, (retry_at - datetime.now(UTC)).total_seconds())


def _iter_sse_data(lines: Iterator[str]) -> Iterator[str]:
    data_lines: list[str] = []
    for line in lines:
        if not line:
            if data_lines:
                yield "\n".join(data_lines)
                data_lines.clear()
            continue
        if line.startswith(":"):
            continue
        field, separator, value = line.partition(":")
        if field == "data":
            data_lines.append(value.removeprefix(" ") if separator else "")
    if data_lines:
        yield "\n".join(data_lines)


def _parse_stream_event(data: str) -> StreamEvent | None:
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as exc:
        raise StreamError("The stream contained invalid JSON.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("type"), str):
        raise StreamError("The stream contained an event without a valid type.")
    event_type = payload["type"]
    try:
        if event_type == "response.output_text.delta":
            return DeltaEvent.model_validate(payload)
        if event_type == "response.completed":
            return CompletedEvent.model_validate(payload)
        if event_type == "response.failed":
            return FailedEvent.model_validate(payload)
        if event_type == "response.incomplete":
            return IncompleteEvent.model_validate(payload)
        if event_type == "error":
            return ErrorEvent.model_validate(payload)
        return None
    except ValidationError as exc:
        raise StreamError(f"The stream contained a malformed {event_type!r} event.") from exc
