import pytest

TEST_API_KEY = "xai-test-key-12345678"

RESPONSE = {
    "id": "resp_123",
    "model": "grok-4.7",
    "status": "completed",
    "citations": None,
    "output": [
        {"type": "custom_tool_call", "name": "x_keyword_search"},
        {
            "type": "message",
            "content": [
                {
                    "type": "output_text",
                    "text": "An answer.",
                    "annotations": [
                        {"type": "url_citation", "url": "https://x.com/i/status/1"},
                        {"type": "url_citation", "url": "https://x.com/i/status/2"},
                        {"type": "url_citation", "url": "https://x.com/i/status/1"},
                        {"type": "file_citation"},
                    ],
                }
            ],
        },
    ],
    "usage": {"server_side_tool_usage_details": {"x_search_calls": 2, "x_posts_fetched": 5}},
}


@pytest.fixture(autouse=True)
def _isolate_credentials(monkeypatch, request):
    if request.node.get_closest_marker("live") is None:
        monkeypatch.setenv("XAI_API_KEY", TEST_API_KEY)
        monkeypatch.delenv("XAI_DEFAULT_MODEL", raising=False)
        monkeypatch.setattr("xai_cli.api._read_keychain", lambda: "")
