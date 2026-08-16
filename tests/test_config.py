import os
import stat

import pytest

from xai_cli.config import Config, get_api_key, get_model, load_config, save_config
from xai_cli.domain import OutputFormat
from xai_cli.errors import ConfigError


def test_default_config():
    config = Config()
    assert config.defaults.model == "grok-4.6"
    assert config.defaults.stream is True
    assert config.defaults.format is OutputFormat.TEXT
    assert config.auth.api_key == ""


def test_save_and_load(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    monkeypatch.setattr("xai_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("xai_cli.config.CONFIG_FILE", config_file)

    config = Config()
    config.auth.api_key = "xai-test-key"
    config.defaults.model = "custom-model"
    config.defaults.stream = False
    save_config(config)

    loaded = load_config()
    assert loaded.auth.api_key == "xai-test-key"
    assert loaded.defaults.model == "custom-model"
    assert loaded.defaults.stream is False
    if os.name == "posix":
        assert stat.S_IMODE(config_file.stat().st_mode) == 0o600


def test_toml_special_characters_round_trip():
    config = Config()
    config.auth.api_key = 'xai-"quote"\\slash\nline'
    config.defaults.model = 'model-"quoted"\\path'
    save_config(config)

    loaded = load_config()

    assert loaded.auth.api_key == config.auth.api_key
    assert loaded.defaults.model == config.defaults.model


def test_load_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("xai_cli.config.CONFIG_FILE", tmp_path / "nonexistent.toml")
    config = load_config()
    assert config.defaults.model == "grok-4.6"


def test_environment_overrides_config(monkeypatch):
    config = Config()
    config.auth.api_key = "configured-key"
    config.defaults.model = "configured-model"
    save_config(config)
    monkeypatch.setenv("XAI_API_KEY", "environment-key")
    monkeypatch.setenv("XAI_DEFAULT_MODEL", "environment-model")

    assert get_api_key() == "environment-key"
    assert get_model() == "environment-model"


def test_config_fallback_when_environment_is_absent(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("XAI_DEFAULT_MODEL", raising=False)
    config = Config()
    config.auth.api_key = "configured-key"
    config.defaults.model = "configured-model"
    save_config(config)

    assert get_api_key() == "configured-key"
    assert get_model() == "configured-model"


def test_invalid_toml_has_specific_error():
    from xai_cli.config import CONFIG_FILE

    CONFIG_FILE.write_text("[defaults\nmodel = 1", encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid TOML"):
        load_config()


def test_invalid_utf8_has_specific_error_without_exposing_content():
    from xai_cli.config import CONFIG_FILE

    secret = b"xai-secret-value"
    CONFIG_FILE.write_bytes(b'[auth]\napi_key = "' + secret + b'\xff"\n')

    with pytest.raises(ConfigError, match="not valid UTF-8") as caught:
        load_config()

    assert secret.decode() not in str(caught.value)


def test_invalid_config_value_has_specific_error():
    from xai_cli.config import CONFIG_FILE

    CONFIG_FILE.write_text('[defaults]\nformat = "yaml"\n', encoding="utf-8")

    with pytest.raises(ConfigError, match=r"defaults\.format"):
        load_config()


def test_atomic_save_preserves_old_file_on_replace_failure(monkeypatch):
    from xai_cli.config import CONFIG_FILE

    CONFIG_FILE.write_text("old content", encoding="utf-8")
    os.chmod(CONFIG_FILE, 0o600)

    def fail_replace(source, destination):
        raise OSError("replace failed")

    monkeypatch.setattr("xai_cli.config.os.replace", fail_replace)

    with pytest.raises(ConfigError, match="replace failed"):
        save_config(Config())

    assert CONFIG_FILE.read_text(encoding="utf-8") == "old content"
    assert not list(CONFIG_FILE.parent.glob(".config-*"))


@pytest.mark.skipif(os.name != "posix", reason="POSIX permissions are not available")
def test_load_migrates_existing_config_permissions():
    from xai_cli.config import CONFIG_FILE

    save_config(Config())
    os.chmod(CONFIG_FILE, 0o644)

    load_config()

    assert stat.S_IMODE(CONFIG_FILE.stat().st_mode) == 0o600


def test_windows_save_path_skips_posix_operations(monkeypatch):
    monkeypatch.setattr("xai_cli.config._is_posix", lambda: False)

    config = Config()
    config.defaults.model = "windows-model"
    save_config(config)

    assert load_config().defaults.model == "windows-model"
