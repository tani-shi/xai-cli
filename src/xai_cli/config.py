from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_config_dir
from pydantic import BaseModel, Field

CONFIG_DIR = Path(user_config_dir("xai"))
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_MODEL = "grok-4-1-fast-non-reasoning"


class SearchDefaults(BaseModel):
    enable_image_understanding: bool = False
    enable_video_understanding: bool = False


class Defaults(BaseModel):
    model: str = DEFAULT_MODEL
    stream: bool = True
    format: str = "text"


class Auth(BaseModel):
    api_key: str = ""


class Config(BaseModel):
    auth: Auth = Field(default_factory=Auth)
    defaults: Defaults = Field(default_factory=Defaults)
    search: SearchDefaults = Field(default_factory=SearchDefaults)


def _parse_toml(text: str) -> dict:
    import tomllib

    return tomllib.loads(text)


def load_config() -> Config:
    if CONFIG_FILE.exists():
        data = _parse_toml(CONFIG_FILE.read_text())
        return Config(**data)
    return Config()


def save_config(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    lines.append("[auth]")
    lines.append(f'api_key = "{config.auth.api_key}"')
    lines.append("")

    lines.append("[defaults]")
    lines.append(f'model = "{config.defaults.model}"')
    lines.append(f"stream = {'true' if config.defaults.stream else 'false'}")
    lines.append(f'format = "{config.defaults.format}"')
    lines.append("")

    lines.append("[search]")
    ei = "true" if config.search.enable_image_understanding else "false"
    ev = "true" if config.search.enable_video_understanding else "false"
    lines.append(f"enable_image_understanding = {ei}")
    lines.append(f"enable_video_understanding = {ev}")
    lines.append("")

    CONFIG_FILE.write_text("\n".join(lines))


def get_api_key() -> str:
    env_key = os.environ.get("XAI_API_KEY")
    if env_key:
        return env_key
    config = load_config()
    if config.auth.api_key:
        return config.auth.api_key
    return ""


def get_model() -> str:
    env_model = os.environ.get("XAI_DEFAULT_MODEL")
    if env_model:
        return env_model
    config = load_config()
    return config.defaults.model
