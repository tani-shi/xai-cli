import httpx
import pytest

from tests.conftest import MOCK_RESPONSE, TEST_API_KEY
from xai_cli.client.responses import build_x_search_request
from xai_cli.client.transport import BASE_URL, ApiClient
from xai_cli.errors import (
    ApiError,
    AuthError,
    IncompleteResponseError,
    InvalidRequestError,
    NetworkError,
    RateLimitError,
)


def request():
    return build_x_search_request("query", "grok-4.6", stream=False)


def test_response_request_and_authorization_are_exact(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)

    with ApiClient(TEST_API_KEY) as client:
        response = client.create_response(request())

    sent = httpx_mock.get_request()
    assert sent is not None
    assert sent.headers["Authorization"] == f"Bearer {TEST_API_KEY}"
    assert sent.read().decode() == (
        '{"model":"grok-4.6","input":[{"role":"user","content":"query"}],'
        '"tools":[{"type":"x_search"}],"stream":false}'
    )
    assert response.text.startswith("A cited answer")
    assert response.citation_urls == ["https://example.com/source"]


@pytest.mark.parametrize("status", [401, 403])
def test_authentication_errors(httpx_mock, status):
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        status_code=status,
        json={"error": {"message": "invalid token"}},
    )
    with ApiClient(TEST_API_KEY) as client, pytest.raises(AuthError, match=str(status)):
        client.create_response(request())


def test_api_key_is_redacted_from_server_error(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        status_code=401,
        json={"error": {"message": f"rejected {TEST_API_KEY}"}},
    )
    with ApiClient(TEST_API_KEY) as client, pytest.raises(AuthError) as caught:
        client.create_response(request())
    assert TEST_API_KEY not in str(caught.value)


def test_422_is_invalid_request(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", status_code=422, text="bad field")
    with ApiClient(TEST_API_KEY) as client, pytest.raises(InvalidRequestError, match="422"):
        client.create_response(request())


def test_429_is_rate_limit(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", status_code=429)
    with ApiClient(TEST_API_KEY) as client, pytest.raises(RateLimitError, match="429"):
        client.create_response(request())


@pytest.mark.parametrize("status", [429, 503])
def test_retry_after_recovers_transient_post_errors(httpx_mock, status):
    waits: list[float] = []
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        status_code=status,
        headers={"Retry-After": "0"},
    )
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)

    with ApiClient(TEST_API_KEY, sleep=waits.append) as client:
        response = client.create_response(request())

    assert response.id == "resp_123"
    assert waits == [0.0]
    assert len(httpx_mock.get_requests()) == 2


def test_retry_limit_returns_last_error(httpx_mock):
    waits: list[float] = []
    for _ in range(3):
        httpx_mock.add_response(
            url=f"{BASE_URL}/responses",
            status_code=503,
            headers={"Retry-After": "0"},
        )

    with (
        ApiClient(TEST_API_KEY, sleep=waits.append) as client,
        pytest.raises(ApiError, match="503"),
    ):
        client.create_response(request())

    assert waits == [0.0, 0.0]
    assert len(httpx_mock.get_requests()) == 3


def test_post_is_not_retried_without_bounded_retry_after(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        status_code=429,
        headers={"Retry-After": "60"},
    )
    with (
        ApiClient(TEST_API_KEY, sleep=lambda _: pytest.fail("unexpected retry")) as client,
        pytest.raises(RateLimitError),
    ):
        client.create_response(request())
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.parametrize(
    "retry_after",
    ["-1", "nan", "NaN", "inf", "Infinity", "-inf", "-Infinity"],
)
def test_post_is_not_retried_with_negative_or_nonfinite_retry_after(httpx_mock, retry_after):
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        status_code=429,
        headers={"Retry-After": retry_after},
    )
    with (
        ApiClient(TEST_API_KEY, sleep=lambda _: pytest.fail("unexpected retry")) as client,
        pytest.raises(RateLimitError),
    ):
        client.create_response(request())
    assert len(httpx_mock.get_requests()) == 1


def test_post_accepts_maximum_bounded_retry_after(httpx_mock):
    waits: list[float] = []
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        status_code=503,
        headers={"Retry-After": "2"},
    )
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=MOCK_RESPONSE)

    with ApiClient(TEST_API_KEY, sleep=waits.append) as client:
        response = client.create_response(request())

    assert response.id == "resp_123"
    assert waits == [2.0]
    assert len(httpx_mock.get_requests()) == 2


@pytest.mark.parametrize("status", [500, 502, 504])
def test_ambiguous_post_server_errors_are_not_retried(httpx_mock, status):
    httpx_mock.add_response(
        url=f"{BASE_URL}/responses",
        status_code=status,
        headers={"Retry-After": "0"},
    )
    with (
        ApiClient(TEST_API_KEY, sleep=lambda _: pytest.fail("unexpected retry")) as client,
        pytest.raises(ApiError, match=str(status)),
    ):
        client.create_response(request())
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_server_errors(httpx_mock, status):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", status_code=status)
    with ApiClient(TEST_API_KEY) as client, pytest.raises(ApiError, match=str(status)):
        client.create_response(request())


def test_timeout_is_network_error(httpx_mock):
    httpx_mock.add_exception(httpx.ReadTimeout("timed out"), url=f"{BASE_URL}/responses")
    with ApiClient(TEST_API_KEY) as client, pytest.raises(NetworkError, match="timed out"):
        client.create_response(request())


def test_invalid_json_is_incomplete_response(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", text="not json")
    with ApiClient(TEST_API_KEY) as client, pytest.raises(IncompleteResponseError, match="invalid"):
        client.create_response(request())


@pytest.mark.parametrize(
    "response",
    [
        {"id": "r", "status": "incomplete", "output": []},
        {"id": "r", "status": "completed", "output": []},
    ],
)
def test_incomplete_responses(httpx_mock, response):
    httpx_mock.add_response(url=f"{BASE_URL}/responses", json=response)
    with ApiClient(TEST_API_KEY) as client, pytest.raises(IncompleteResponseError):
        client.create_response(request())
