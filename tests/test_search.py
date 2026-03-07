import json

from typer.testing import CliRunner

from xai_cli.client.base import BASE_URL
from xai_cli.main import app

runner = CliRunner()

MOCK_RESPONSE = {
    "id": "resp_123",
    "output": [
        {
            "type": "message",
            "content": [
                {
                    "type": "output_text",
                    "text": "Here are some posts about Rust programming...",
                }
            ],
        }
    ],
}


def test_search_json(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["search", "Rust programming", "--format", "json", "--no-stream"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "output" in data


def test_search_text(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["search", "Rust programming", "--no-stream"])
    assert result.exit_code == 0
    assert "Rust" in result.stdout


def test_search_with_dates(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(
        app,
        ["search", "AI", "--from", "2026-01-01", "--to", "2026-03-01", "--no-stream"],
    )
    assert result.exit_code == 0


def test_user_command(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["user", "@elonmusk", "--no-stream"])
    assert result.exit_code == 0


def test_thread_command(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["thread", "https://x.com/user/status/123456789", "--no-stream"])
    assert result.exit_code == 0


def test_trending_command(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["trending", "--no-stream"])
    assert result.exit_code == 0


def test_trending_with_category(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["trending", "--category", "tech", "--no-stream"])
    assert result.exit_code == 0


def test_web_command(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/v1/responses", json=MOCK_RESPONSE)
    result = runner.invoke(app, ["web", "Python", "--no-stream"])
    assert result.exit_code == 0


def test_config_list():
    result = runner.invoke(app, ["config", "list"])
    assert result.exit_code == 0
    assert "model" in result.stdout


def test_config_set_and_get():
    result = runner.invoke(app, ["config", "set", "model", "grok-4-1-fast"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["config", "get", "model"])
    assert result.exit_code == 0
    assert "grok-4-1-fast" in result.stdout
