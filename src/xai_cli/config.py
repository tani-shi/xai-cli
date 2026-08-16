from __future__ import annotations

import os
import tempfile
import tomllib
from pathlib import Path

from platformdirs import user_config_dir
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from tomli_w import dumps as dump_toml

from xai_cli.domain import OutputFormat
from xai_cli.errors import ConfigError

CONFIG_DIR = Path(user_config_dir("xai"))
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_MODEL = "grok-4.6"


class ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class SearchDefaults(ConfigModel):
    enable_image_understanding: bool = False
    enable_video_understanding: bool = False


class Defaults(ConfigModel):
    model: str = Field(default=DEFAULT_MODEL, min_length=1)
    stream: bool = True
    format: OutputFormat = OutputFormat.TEXT

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("model cannot be blank")
        return value


class Auth(ConfigModel):
    api_key: str = ""


class Config(ConfigModel):
    auth: Auth = Field(default_factory=Auth)
    defaults: Defaults = Field(default_factory=Defaults)
    search: SearchDefaults = Field(default_factory=SearchDefaults)


def load_config() -> Config:
    if not CONFIG_FILE.exists():
        return Config()
    try:
        _restrict_path_permissions(CONFIG_FILE)
        text = CONFIG_FILE.read_text(encoding="utf-8")
        return Config.model_validate(tomllib.loads(text))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {CONFIG_FILE}: {exc}") from exc
    except ValidationError as exc:
        detail = exc.errors(include_url=False)[0]
        location = ".".join(str(part) for part in detail["loc"])
        raise ConfigError(
            f"Invalid setting {location!r} in {CONFIG_FILE}: {detail['msg']}"
        ) from exc
    except OSError as exc:
        raise ConfigError(f"Could not read {CONFIG_FILE}: {exc.strerror or exc}") from exc


def save_config(config: Config) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
        serialized = dump_toml(config.model_dump(mode="json"))
        descriptor, temporary_name = tempfile.mkstemp(prefix=".config-", dir=CONFIG_DIR)
        temporary = Path(temporary_name)
        try:
            _restrict_path_permissions(temporary)
            with os.fdopen(descriptor, "w", encoding="utf-8") as output:
                output.write(serialized)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, CONFIG_FILE)
            _restrict_path_permissions(CONFIG_FILE)
            _sync_directory(CONFIG_DIR)
        finally:
            temporary.unlink(missing_ok=True)
    except OSError as exc:
        raise ConfigError(f"Could not save {CONFIG_FILE}: {exc.strerror or exc}") from exc


def get_api_key(config: Config | None = None) -> str:
    env_key = os.environ.get("XAI_API_KEY")
    if env_key:
        return env_key
    resolved_config = config or load_config()
    if resolved_config.auth.api_key:
        return resolved_config.auth.api_key
    return ""


def get_model(config: Config | None = None) -> str:
    env_model = os.environ.get("XAI_DEFAULT_MODEL")
    if env_model:
        return env_model
    resolved_config = config or load_config()
    return resolved_config.defaults.model


def parse_boolean(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ConfigError(f"Invalid boolean {value!r}; use true or false.")


def _is_posix() -> bool:
    return os.name == "posix"


def _restrict_path_permissions(path: Path) -> None:
    if _is_posix():
        os.chmod(path, 0o600)


def _sync_directory(path: Path) -> None:
    if not _is_posix():
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
