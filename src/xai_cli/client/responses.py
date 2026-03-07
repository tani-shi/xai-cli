from __future__ import annotations

import json
from typing import Any

from xai_cli.client.base import post_json, post_stream
from xai_cli.output import print_streaming_text


def _build_x_search_tool(
    allowed_handles: list[str] | None = None,
    excluded_handles: list[str] | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    enable_images: bool = False,
    enable_video: bool = False,
) -> dict[str, Any]:
    tool: dict[str, Any] = {"type": "x_search"}
    params: dict[str, Any] = {}
    if allowed_handles:
        params["allowed_x_handles"] = allowed_handles
    if excluded_handles:
        params["excluded_x_handles"] = excluded_handles
    if from_date:
        params["from_date"] = from_date
    if to_date:
        params["to_date"] = to_date
    if enable_images:
        params["enable_image_understanding"] = True
    if enable_video:
        params["enable_video_understanding"] = True
    if params:
        tool["x_search"] = params
    return tool


def _build_web_search_tool(
    allowed_domains: list[str] | None = None,
    excluded_domains: list[str] | None = None,
) -> dict[str, Any]:
    tool: dict[str, Any] = {"type": "web_search"}
    params: dict[str, Any] = {}
    if allowed_domains:
        params["allowed_domains"] = allowed_domains
    if excluded_domains:
        params["excluded_domains"] = excluded_domains
    if params:
        tool["web_search"] = params
    return tool


def x_search(
    query: str,
    model: str,
    *,
    stream: bool = True,
    allowed_handles: list[str] | None = None,
    excluded_handles: list[str] | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    enable_images: bool = False,
    enable_video: bool = False,
) -> dict[str, Any] | str:
    tool = _build_x_search_tool(
        allowed_handles=allowed_handles,
        excluded_handles=excluded_handles,
        from_date=from_date,
        to_date=to_date,
        enable_images=enable_images,
        enable_video=enable_video,
    )
    payload: dict[str, Any] = {
        "model": model,
        "tools": [tool],
        "input": query,
        "stream": stream,
    }

    if stream:
        return _handle_stream(payload)
    else:
        return post_json("/v1/responses", payload)


def web_search(
    query: str,
    model: str,
    *,
    stream: bool = True,
    allowed_domains: list[str] | None = None,
    excluded_domains: list[str] | None = None,
) -> dict[str, Any] | str:
    tool = _build_web_search_tool(
        allowed_domains=allowed_domains,
        excluded_domains=excluded_domains,
    )
    payload: dict[str, Any] = {
        "model": model,
        "tools": [tool],
        "input": query,
        "stream": stream,
    }

    if stream:
        return _handle_stream(payload)
    else:
        return post_json("/v1/responses", payload)


def _handle_stream(payload: dict[str, Any]) -> str:
    full_text = ""
    for data in post_stream("/v1/responses", payload):
        if data == "[DONE]":
            break
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue

        event_type = event.get("type", "")
        if event_type == "response.output_text.delta":
            delta = event.get("delta", "")
            print_streaming_text(delta)
            full_text += delta

    if full_text:
        print_streaming_text("\n")
    return full_text


def extract_text_from_response(response: dict[str, Any]) -> str:
    output = response.get("output", [])
    texts: list[str] = []
    for item in output:
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    texts.append(content.get("text", ""))
    return "\n".join(texts)
