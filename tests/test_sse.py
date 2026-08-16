import json

import httpx
import pytest

from tests.conftest import MOCK_RESPONSE, TEST_API_KEY
from xai_cli.client.models import CompletedEvent, DeltaEvent
from xai_cli.client.responses import build_x_search_request
from xai_cli.client.transport import BASE_URL, ApiClient
from xai_cli.errors import IncompleteResponseError, NetworkError, StreamError


def sse(*events):
    return "".join(f"data: {json.dumps(event)}\n\n" for event in events)


def stream_request():
    return build_x_search_request("query", "grok-4.6", stream=True)


def test_stream_deltas_completion_and_citations(httpx_mock):
    body = sse(
        {"type": "response.created", "response": {"id": "resp_123"}},
        {"type": "response.output_text.delta", "delta": "A cited "},
        {"type": "response.output_text.delta", "delta": "answer."},
        {"type": "response.completed", "response": MOCK_RESPONSE},
    )
    httpx_mock.add_response(url=f"{BASE_URL}/responses", text=body)

    with ApiClient(TEST_API_KEY) as client, client.stream_response(stream_request()) as events:
        received = list(events)

    assert [event.delta for event in received if isinstance(event, DeltaEvent)] == [
        "A cited ",
        "answer.",
    ]
    completed = next(event for event in received if isinstance(event, CompletedEvent))
    assert completed.response.citation_urls == ["https://example.com/source"]


def test_stream_error_event(httpx_mock):
    body = sse({"type": "error", "error": {"message": "tool failed", "code": "bad"}})
    httpx_mock.add_response(url=f"{BASE_URL}/responses", text=body)

    with (
        ApiClient(TEST_API_KEY) as client,
        pytest.raises(StreamError, match="tool failed"),
        client.stream_response(stream_request()) as events,
    ):
        list(events)


@pytest.mark.parametrize(
    "event, error_type",
    [
        (
            {"type": "response.failed", "error": {"message": "generation failed"}},
            StreamError,
        ),
        ({"type": "response.incomplete"}, IncompleteResponseError),
    ],
)
def test_failure_terminal_events(httpx_mock, event, error_type):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", text=sse(event))
    with (
        ApiClient(TEST_API_KEY) as client,
        pytest.raises(error_type),
        client.stream_response(stream_request()) as events,
    ):
        list(events)


@pytest.mark.parametrize(
    "body, message",
    [
        ("data: {bad json}\n\n", "invalid JSON"),
        (sse({"delta": "missing type"}), "valid type"),
        (sse({"type": "response.output_text.delta", "delta": 42}), "malformed"),
    ],
)
def test_malformed_stream_events(httpx_mock, body, message):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", text=body)
    with (
        ApiClient(TEST_API_KEY) as client,
        pytest.raises(StreamError, match=message),
        client.stream_response(stream_request()) as events,
    ):
        list(events)


def test_stream_ending_before_completion(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        text=sse({"type": "response.output_text.delta", "delta": "partial"}),
    )
    with (
        ApiClient(TEST_API_KEY) as client,
        pytest.raises(IncompleteResponseError, match="ended"),
        client.stream_response(stream_request()) as events,
    ):
        list(events)


class BrokenStream(httpx.SyncByteStream):
    def __iter__(self):
        yield b'data: {"type":"response.output_text.delta","delta":"partial"}\n\n'
        raise httpx.ReadError("connection reset")


def test_stream_connection_break_is_network_error():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, request=request, stream=BrokenStream())
    )
    with (
        ApiClient(TEST_API_KEY, transport=transport) as client,
        pytest.raises(NetworkError, match="interrupted"),
        client.stream_response(stream_request()) as events,
    ):
        list(events)
