import json

import pytest
from typer.testing import CliRunner

from tests.conftest import RESPONSE, TEST_API_KEY
from xai_cli import api
from xai_cli.main import app

URL = "https://api.x.ai/v1/responses"
runner = CliRunner()


def sent_body(httpx_mock):
    return json.loads(httpx_mock.get_request().read())


def test_search_sends_tool_parameters(httpx_mock):
    httpx_mock.add_response(url=URL, json=RESPONSE)
    result = runner.invoke(
        app,
        [
            "search", "q", "--from", "2026-01-01", "--to", "2026-01-01",
            "--from-user", "@xai", "--from-user", "grok", "--images", "--video",
        ],
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    assert sent_body(httpx_mock) == {
        "model": "grok-4.7",
        "input": "q",
        "tools": [
            {
                "type": "x_search",
                "from_date": "2026-01-01",
                "to_date": "2026-01-02",
                "allowed_x_handles": ["xai", "grok"],
                "enable_image_understanding": True,
                "enable_video_understanding": True,
            }
        ],
        "include": ["no_inline_citations"],
    }


def test_web_sends_filters_and_model_override(httpx_mock, monkeypatch):
    monkeypatch.setenv("XAI_DEFAULT_MODEL", "grok-x")
    httpx_mock.add_response(url=URL, json=RESPONSE)
    result = runner.invoke(app, ["web", "q", "--exclude-domain", "medium.com"])
    assert result.exit_code == 0, result.output
    body = sent_body(httpx_mock)
    assert body["model"] == "grok-x"
    assert body["tools"] == [
        {"type": "web_search", "filters": {"excluded_domains": ["medium.com"]}}
    ]


def test_text_output_lists_unique_sources(httpx_mock):
    httpx_mock.add_response(url=URL, json=RESPONSE)
    result = runner.invoke(app, ["search", "q"])
    assert result.stdout == (
        "An answer.\n\nSources:\n- https://x.com/i/status/1\n- https://x.com/i/status/2\n"
    )


def test_json_output(httpx_mock):
    httpx_mock.add_response(url=URL, json=RESPONSE)
    result = runner.invoke(app, ["search", "q", "--json"])
    assert json.loads(result.stdout) == {
        "response_id": "resp_123",
        "model": "grok-4.7",
        "text": "An answer.",
        "sources": ["https://x.com/i/status/1", "https://x.com/i/status/2"],
        "usage": {"server_side_tool_usage_details": {"x_search_calls": 2, "x_posts_fetched": 5}},
    }


def test_http_error_is_reported_with_redacted_key(httpx_mock):
    httpx_mock.add_response(url=URL, status_code=400, text=f"bad request {TEST_API_KEY}")
    result = runner.invoke(app, ["search", "q"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "HTTP 400: bad request [redacted]" in result.stderr


@pytest.mark.parametrize(
    "payload",
    [{**RESPONSE, "status": "incomplete"}, {**RESPONSE, "output": None}, {"unexpected": True}],
)
def test_unusable_response_fails(httpx_mock, payload):
    httpx_mock.add_response(url=URL, json=payload)
    result = runner.invoke(app, ["search", "q"])
    assert result.exit_code == 1
    assert result.stdout == ""


@pytest.mark.parametrize("args", [["--from", "2026/01/01"], ["--to", "9999-12-31"]])
def test_invalid_dates_are_usage_errors(args):
    result = runner.invoke(app, ["search", "q", *args])
    assert result.exit_code == 2


def test_keychain_is_used_without_environment_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY")
    monkeypatch.setattr("sys.platform", "darwin")
    monkeypatch.setattr("xai_cli.api._read_keychain", lambda: "keychain-key")
    assert api.get_api_key() == "keychain-key"


def test_missing_key_fails(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY")
    result = runner.invoke(app, ["search", "q"])
    assert result.exit_code == 1
    assert "API key not found" in result.stderr
