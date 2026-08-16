import pytest

TEST_API_KEY = "xai-test-key-12345678"

MOCK_RESPONSE = {
    "id": "resp_123",
    "model": "grok-4.6",
    "status": "completed",
    "output": [
        {
            "type": "message",
            "content": [
                {
                    "type": "output_text",
                    "text": "A cited answer.[[1]](https://example.com/source)",
                    "annotations": [
                        {
                            "type": "url_citation",
                            "url": "https://example.com/source",
                            "title": "1",
                            "start_index": 15,
                            "end_index": 47,
                        }
                    ],
                }
            ],
        }
    ],
    "citations": ["https://example.com/source"],
}


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch, request):
    if request.node.get_closest_marker("live") is None:
        monkeypatch.setenv("XAI_API_KEY", TEST_API_KEY)


@pytest.fixture(autouse=True)
def _isolate_config(tmp_path, monkeypatch):
    monkeypatch.setattr("xai_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("xai_cli.config.CONFIG_FILE", tmp_path / "config.toml")
