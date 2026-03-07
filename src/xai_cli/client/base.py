from __future__ import annotations

from collections.abc import Generator
from typing import Any

import httpx

from xai_cli.config import get_api_key
from xai_cli.errors import ApiError, AuthError

BASE_URL = "https://api.x.ai"


def _get_headers() -> dict[str, str]:
    api_key = get_api_key()
    if not api_key:
        raise AuthError("API key not configured. Run 'xai config init' or set XAI_API_KEY.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload, headers=_get_headers())
    except httpx.HTTPError as e:
        raise ApiError(f"HTTP request failed: {e}") from e

    if resp.status_code == 401:
        raise AuthError("Invalid API key.")
    if resp.status_code != 200:
        raise ApiError(f"API returned status {resp.status_code}: {resp.text}")
    return resp.json()


def post_stream(path: str, payload: dict[str, Any]) -> Generator[str, None, None]:
    url = f"{BASE_URL}{path}"
    try:
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", url, json=payload, headers=_get_headers()) as resp:
                if resp.status_code == 401:
                    raise AuthError("Invalid API key.")
                if resp.status_code != 200:
                    resp.read()
                    raise ApiError(f"API returned status {resp.status_code}: {resp.text}")
                for line in resp.iter_lines():
                    if line.startswith("data: "):
                        yield line[6:]
    except AuthError:
        raise
    except ApiError:
        raise
    except httpx.HTTPError as e:
        raise ApiError(f"HTTP streaming failed: {e}") from e


def get_json(path: str) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, headers=_get_headers())
    except httpx.HTTPError as e:
        raise ApiError(f"HTTP request failed: {e}") from e

    if resp.status_code == 401:
        raise AuthError("Invalid API key.")
    if resp.status_code != 200:
        raise ApiError(f"API returned status {resp.status_code}: {resp.text}")
    return resp.json()
