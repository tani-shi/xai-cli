import pytest


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test-key-12345678")


@pytest.fixture(autouse=True)
def _isolate_config(tmp_path, monkeypatch):
    monkeypatch.setattr("xai_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("xai_cli.config.CONFIG_FILE", tmp_path / "config.toml")
