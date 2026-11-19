from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

import httpx

BASE_URL = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-4.7"
KEYCHAIN_SERVICE = "xai-api-key"
TIMEOUT = httpx.Timeout(300.0, connect=10.0)


class XaiError(Exception):
    pass


@dataclass(frozen=True)
class Answer:
    response_id: str
    model: str
    text: str
    sources: list[str]
    usage: dict[str, Any]


def create_answer(query: str, tool: dict[str, Any]) -> Answer:
    api_key = get_api_key()
    body = {
        "model": os.environ.get("XAI_DEFAULT_MODEL", "").strip() or DEFAULT_MODEL,
        "input": query,
        "tools": [tool],
        # Sources then come from the search tool, not from where Grok chooses to cite.
        # https://docs.x.ai/developers/tools/citations
        "include": ["no_inline_citations"],
    }
    try:
        response = httpx.post(
            f"{BASE_URL}/responses",
            json=body,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
    except httpx.HTTPError as exc:
        detail = str(exc).replace(api_key, "[redacted]")
        raise XaiError(f"Request failed: {type(exc).__name__}: {detail}") from exc
    if response.is_error:
        detail = response.text.strip().replace(api_key, "[redacted]")
        raise XaiError(f"xAI returned HTTP {response.status_code}: {detail}")
    try:
        return parse_answer(response.json())
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise XaiError(f"Unexpected xAI response: {exc}") from exc


def parse_answer(payload: dict[str, Any]) -> Answer:
    if payload["status"] != "completed":
        raise XaiError(f"xAI response status is {payload['status']!r}, not 'completed'.")
    contents = [
        content
        for item in payload["output"] or []
        if item["type"] == "message"
        for content in item["content"] or []
        if content["type"] == "output_text"
    ]
    text = "\n".join(content["text"] or "" for content in contents).strip()
    if not text:
        raise XaiError("xAI returned no answer text.")
    urls = [
        *(payload.get("citations") or []),
        *(a.get("url") for content in contents for a in content.get("annotations") or []),
    ]
    return Answer(
        response_id=payload["id"],
        model=payload.get("model") or "",
        text=text,
        sources=list(dict.fromkeys(url for url in urls if url)),
        usage=payload.get("usage") or {},
    )


def get_api_key() -> str:
    if key := os.environ.get("XAI_API_KEY", "").strip():
        return key
    if key := _read_keychain():
        return key
    raise XaiError(
        "API key not found. Set XAI_API_KEY or, on macOS, store it in the Keychain "
        f"as service '{KEYCHAIN_SERVICE}'."
    )


def _read_keychain() -> str:
    if sys.platform != "darwin":  # mypy also skips the macOS-only code below
        return ""
    import pwd

    # Matches `id -un`, which the README uses to store the item.
    account = pwd.getpwuid(os.geteuid()).pw_name
    error = f"Could not read '{KEYCHAIN_SERVICE}' from the Keychain"
    try:
        # A locked Keychain can wait on an access prompt indefinitely.
        result = subprocess.run(
            ["security", "find-generic-password", "-a", account, "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise XaiError(f"{error}: {exc}") from exc
    if result.returncode == 44:  # errSecItemNotFound
        return ""
    if result.returncode != 0:
        raise XaiError(
            f"{error} (security exit status {result.returncode}). "
            "Unlock it or allow access, then retry."
        )
    return result.stdout.strip()
