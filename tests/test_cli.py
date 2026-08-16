import json

import pytest
from typer.testing import CliRunner

from tests.conftest import MOCK_RESPONSE, TEST_API_KEY
from xai_cli.client.transport import BASE_URL
from xai_cli.main import app

runner = CliRunner()


def sse_event(event):
    return f"data: {json.dumps(event)}\n\n"


@pytest.mark.parametrize(
    "command",
    [
        ["search", "query"],
        ["user", "@xai"],
        ["thread", "https://x.com/xai/status/123"],
        ["trending"],
        ["web", "query"],
    ],
)
def test_answer_commands_emit_stable_json_and_progress(httpx_mock, command):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)

    result = runner.invoke(app, [*command, "--format", "json", "--no-stream"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload == {
        "schema_version": 1,
        "response_id": "resp_123",
        "model": "grok-4.6",
        "status": "completed",
        "text": "A cited answer.[[1]](https://example.com/source)",
        "citations": ["https://example.com/source"],
    }
    assert "Searching" in result.stderr


def test_search_all_options_payload(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    result = runner.invoke(
        app,
        [
            "search",
            "query",
            "--from",
            "2026-01-01",
            "--to",
            "2026-02-01",
            "--from-user",
            "@xai",
            "--images",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0
    sent = httpx_mock.get_request()
    assert sent is not None
    body = json.loads(sent.read())
    assert body["tools"] == [
        {
            "type": "x_search",
            "allowed_x_handles": ["xai"],
            "from_date": "2026-01-01",
            "to_date": "2026-02-01",
            "enable_image_understanding": True,
        }
    ]


def test_web_domain_payload(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    result = runner.invoke(
        app,
        ["web", "query", "--exclude-domain", "spam.example", "--format", "json"],
    )
    assert result.exit_code == 0
    sent = httpx_mock.get_request()
    assert sent is not None
    assert json.loads(sent.read())["tools"] == [
        {
            "type": "web_search",
            "filters": {"excluded_domains": ["spam.example"]},
        }
    ]


def test_search_excluded_handles_payload(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    result = runner.invoke(
        app,
        ["search", "query", "--exclude", "@spam", "--format", "json"],
    )
    assert result.exit_code == 0
    sent = httpx_mock.get_request()
    assert sent is not None
    assert json.loads(sent.read())["tools"] == [
        {"type": "x_search", "excluded_x_handles": ["spam"]}
    ]


def test_user_dates_are_sent(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    result = runner.invoke(
        app,
        ["user", "@xai", "topic", "--from", "2026-01-01", "--to", "2026-01-31", "--format", "json"],
    )
    assert result.exit_code == 0
    sent = httpx_mock.get_request()
    assert sent is not None
    tool = json.loads(sent.read())["tools"][0]
    assert tool["allowed_x_handles"] == ["xai"]
    assert tool["from_date"] == "2026-01-01"
    assert tool["to_date"] == "2026-01-31"


def test_thread_summary_and_trending_category_prompts(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    thread_result = runner.invoke(
        app,
        ["thread", "https://x.com/xai/status/123", "--summary", "--format", "json"],
    )
    assert thread_result.exit_code == 0
    thread_request = httpx_mock.get_request()
    assert thread_request is not None
    assert "Summarize" in json.loads(thread_request.read())["input"][0]["content"]

    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    trend_result = runner.invoke(app, ["trending", "--category", "tech", "--format", "json"])
    assert trend_result.exit_code == 0
    requests = httpx_mock.get_requests()
    assert "current tech trends" in json.loads(requests[-1].read())["input"][0]["content"]


def test_text_and_markdown_contracts(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    text_result = runner.invoke(app, ["search", "query", "--format", "text", "--no-stream"])
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    markdown_result = runner.invoke(app, ["search", "query", "--format", "markdown", "--no-stream"])
    expected = "A cited answer.[[1]](https://example.com/source)\n"
    assert text_result.stdout == expected
    assert markdown_result.stdout == expected


def test_raw_json_is_explicit(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["search", "query", "--format", "json", "--raw", "--no-stream"])
    payload = json.loads(result.stdout)
    assert payload["id"] == "resp_123"
    assert "schema_version" not in payload


def test_raw_requires_json():
    result = runner.invoke(app, ["search", "query", "--raw"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "--raw requires" in result.stderr


def test_streaming_writes_deltas_and_keeps_diagnostics_on_stderr(httpx_mock):
    body = "".join(
        [
            sse_event({"type": "response.output_text.delta", "delta": "A cited "}),
            sse_event({"type": "response.output_text.delta", "delta": "answer."}),
            sse_event({"type": "response.completed", "response": MOCK_RESPONSE}),
        ]
    )
    httpx_mock.add_response(url=f"{BASE_URL}/responses", text=body)
    result = runner.invoke(app, ["search", "query"])
    assert result.exit_code == 0
    assert result.stdout == "A cited answer.\n"
    assert result.stderr == 'Searching X to answer "query"...\n'


def test_streaming_markdown_is_rendered_after_completion(httpx_mock, monkeypatch):
    body = "".join(
        [
            sse_event({"type": "response.output_text.delta", "delta": "# "}),
            sse_event({"type": "response.output_text.delta", "delta": "Heading"}),
            sse_event({"type": "response.completed", "response": MOCK_RESPONSE}),
        ]
    )
    rendered: list[str] = []
    monkeypatch.setattr("xai_cli.commands.common.write_markdown", rendered.append)
    httpx_mock.add_response(url=f"{BASE_URL}/responses", text=body)

    result = runner.invoke(app, ["search", "query", "--format", "markdown"])

    assert result.exit_code == 0
    assert rendered == ["# Heading"]
    assert result.stdout == ""


def test_models_json_contract(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE_URL}/models",
        json={"data": [{"id": "grok-4.6", "owned_by": "xai"}]},
    )
    result = runner.invoke(app, ["models", "--format", "json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "schema_version": 1,
        "models": [{"id": "grok-4.6", "owned_by": "xai"}],
    }


def test_error_has_empty_stdout(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", status_code=429)
    result = runner.invoke(app, ["search", "query", "--no-stream"])
    assert result.exit_code == 5
    assert result.stdout == ""
    assert "Rate limit error" in result.stderr


def test_config_commands_never_print_api_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    result = runner.invoke(
        app, ["config", "set", "api_key"], input=f"{TEST_API_KEY}\n{TEST_API_KEY}\n"
    )
    assert result.exit_code == 0
    assert TEST_API_KEY not in result.output
    assert "[configured]" in result.stdout

    get_result = runner.invoke(app, ["config", "get", "api_key"])
    list_result = runner.invoke(app, ["config", "list"])
    assert TEST_API_KEY not in get_result.output + list_result.output
    assert get_result.stdout == "[configured]\n"


def test_config_set_rejects_api_key_argument():
    result = runner.invoke(app, ["config", "set", "api_key", TEST_API_KEY])
    assert result.exit_code == 7
    assert TEST_API_KEY not in result.output
    assert "hidden prompt" in result.stderr


def test_config_validates_format():
    result = runner.invoke(app, ["config", "set", "format", "yaml"])
    assert result.exit_code == 7
    assert "text, markdown, or json" in result.stderr


def test_usage_and_authentication_exit_codes_do_not_overlap(monkeypatch):
    invalid_format = runner.invoke(app, ["search", "query", "--format", "yaml"])
    assert invalid_format.exit_code == 2

    monkeypatch.delenv("XAI_API_KEY", raising=False)
    missing_key = runner.invoke(app, ["search", "query", "--no-stream"])
    assert missing_key.exit_code == 3
    assert "Authentication error" in missing_key.stderr
