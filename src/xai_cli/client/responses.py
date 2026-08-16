from __future__ import annotations

from datetime import date

from pydantic import ValidationError

from xai_cli.client.models import (
    InputMessage,
    ResponseRequest,
    WebSearchFilters,
    WebSearchTool,
    XSearchTool,
)
from xai_cli.errors import InvalidRequestError


def build_x_search_request(
    query: str,
    model: str,
    *,
    stream: bool,
    allowed_handles: list[str] | None = None,
    excluded_handles: list[str] | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    enable_images: bool = False,
    enable_video: bool = False,
) -> ResponseRequest:
    try:
        tool = XSearchTool(
            allowed_x_handles=allowed_handles,
            excluded_x_handles=excluded_handles,
            from_date=from_date,
            to_date=to_date,
            enable_image_understanding=True if enable_images else None,
            enable_video_understanding=True if enable_video else None,
        )
        return _build_request(query, model, tool, stream)
    except ValidationError as exc:
        raise InvalidRequestError(_validation_message(exc)) from exc


def build_web_search_request(
    query: str,
    model: str,
    *,
    stream: bool,
    allowed_domains: list[str] | None = None,
    excluded_domains: list[str] | None = None,
) -> ResponseRequest:
    try:
        filters = None
        if allowed_domains or excluded_domains:
            filters = WebSearchFilters(
                allowed_domains=allowed_domains,
                excluded_domains=excluded_domains,
            )
        tool = WebSearchTool(filters=filters)
        return _build_request(query, model, tool, stream)
    except ValidationError as exc:
        raise InvalidRequestError(_validation_message(exc)) from exc


def _build_request(
    query: str,
    model: str,
    tool: XSearchTool | WebSearchTool,
    stream: bool,
) -> ResponseRequest:
    if not query.strip():
        raise InvalidRequestError("The query cannot be empty.")
    return ResponseRequest(
        model=model,
        input=[InputMessage(content=query)],
        tools=[tool],
        stream=stream,
    )


def _validation_message(exc: ValidationError) -> str:
    error = exc.errors(include_url=False)[0]
    location = ".".join(str(part) for part in error["loc"])
    prefix = f"{location}: " if location else ""
    return prefix + str(error["msg"])
