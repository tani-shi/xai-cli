import pytest

from xai_cli.client.base import BASE_URL, _get_headers, post_json
from xai_cli.errors import ApiError, AuthError


def test_get_headers():
    headers = _get_headers()
    assert headers["Authorization"] == "Bearer xai-test-key-12345678"
    assert headers["Content-Type"] == "application/json"


def test_get_headers_missing_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(AuthError, match="API key not configured"):
        _get_headers()


def test_post_json_success(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE_URL}/v1/responses",
        json={"output": [{"type": "message", "content": [{"type": "output_text", "text": "hi"}]}]},
    )
    result = post_json("/v1/responses", {"model": "test", "input": "hello"})
    assert "output" in result


def test_post_json_auth_error(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", status_code=401)
    with pytest.raises(AuthError, match="Invalid API key"):
        post_json("/v1/responses", {"model": "test", "input": "hello"})


def test_post_json_api_error(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", status_code=500, text="Server error")
    with pytest.raises(ApiError, match="500"):
        post_json("/v1/responses", {"model": "test", "input": "hello"})
