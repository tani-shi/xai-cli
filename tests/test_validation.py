from datetime import date

import pytest
from typer.testing import CliRunner

from xai_cli.client.responses import build_web_search_request, build_x_search_request
from xai_cli.domain import normalize_domain, normalize_handle, parse_date, validate_post_url
from xai_cli.errors import InvalidRequestError
from xai_cli.main import app

runner = CliRunner()


def test_x_handle_filters_are_mutually_exclusive():
    with pytest.raises(InvalidRequestError, match="cannot be combined"):
        build_x_search_request(
            "query",
            "grok-4.6",
            stream=False,
            allowed_handles=["xai"],
            excluded_handles=["spam"],
        )


@pytest.mark.parametrize("count", [20])
def test_x_handle_limit_accepts_twenty(count):
    handles = [f"user{index}" for index in range(count)]
    build_x_search_request("query", "grok-4.6", stream=False, allowed_handles=handles)


def test_x_handle_limit_rejects_twenty_one():
    handles = [f"user{index}" for index in range(21)]
    with pytest.raises(InvalidRequestError, match="20"):
        build_x_search_request("query", "grok-4.6", stream=False, allowed_handles=handles)


def test_domain_filters_are_mutually_exclusive():
    with pytest.raises(InvalidRequestError, match="cannot be combined"):
        build_web_search_request(
            "query",
            "grok-4.6",
            stream=False,
            allowed_domains=["example.com"],
            excluded_domains=["spam.example"],
        )


def test_domain_limit_accepts_five():
    domains = [f"host{index}.example" for index in range(5)]
    build_web_search_request("query", "grok-4.6", stream=False, allowed_domains=domains)


def test_domain_limit_rejects_six():
    domains = [f"host{index}.example" for index in range(6)]
    with pytest.raises(InvalidRequestError, match="5"):
        build_web_search_request("query", "grok-4.6", stream=False, allowed_domains=domains)


def test_date_order_is_validated():
    with pytest.raises(InvalidRequestError, match="earlier"):
        build_x_search_request(
            "query",
            "grok-4.6",
            stream=False,
            from_date=date(2026, 2, 1),
            to_date=date(2026, 1, 1),
        )


@pytest.mark.parametrize("value", ["2026-02-30", "01-02-2026", "2026-1-2"])
def test_invalid_dates(value):
    with pytest.raises(InvalidRequestError, match="YYYY-MM-DD"):
        parse_date(value)


@pytest.mark.parametrize("value", ["@", "bad-handle", "a" * 16])
def test_invalid_handles(value):
    with pytest.raises(InvalidRequestError, match="Invalid X handle"):
        normalize_handle(value)


@pytest.mark.parametrize(
    "value", ["https://example.com", "example.com/path", "example.com:443", "localhost"]
)
def test_invalid_domains(value):
    with pytest.raises(InvalidRequestError, match="Invalid domain"):
        normalize_domain(value)


def test_thread_url_validation():
    assert validate_post_url("https://x.com/xai/status/123456") == "https://x.com/xai/status/123456"
    with pytest.raises(InvalidRequestError, match="Post URL"):
        validate_post_url("https://example.com/post/123")


def test_invalid_format_is_a_usage_error():
    result = runner.invoke(app, ["search", "query", "--format", "yaml"])
    assert result.exit_code == 2
    assert "Invalid value" in result.stderr


def test_invalid_category_is_a_usage_error():
    result = runner.invoke(app, ["trending", "--category", "finance"])
    assert result.exit_code == 2
    assert "Invalid value" in result.stderr
