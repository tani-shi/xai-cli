from xai_cli.config import Config, load_config, save_config


def test_default_config():
    config = Config()
    assert config.defaults.model == "grok-4-1-fast-non-reasoning"
    assert config.defaults.stream is True
    assert config.defaults.format == "text"
    assert config.auth.api_key == ""


def test_save_and_load(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    monkeypatch.setattr("xai_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("xai_cli.config.CONFIG_FILE", config_file)

    config = Config()
    config.auth.api_key = "xai-test-key"
    config.defaults.model = "grok-4-1-fast"
    config.defaults.stream = False
    save_config(config)

    loaded = load_config()
    assert loaded.auth.api_key == "xai-test-key"
    assert loaded.defaults.model == "grok-4-1-fast"
    assert loaded.defaults.stream is False


def test_load_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("xai_cli.config.CONFIG_FILE", tmp_path / "nonexistent.toml")
    config = load_config()
    assert config.defaults.model == "grok-4-1-fast-non-reasoning"
