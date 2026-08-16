from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.commands.common import run_cli
from xai_cli.config import CONFIG_FILE, Config, load_config, parse_boolean, save_config
from xai_cli.domain import OutputFormat
from xai_cli.errors import ConfigError
from xai_cli.output import write_text

app = typer.Typer(help="Manage configuration.")


@app.command()
def init() -> None:
    """Initialize configuration (interactive setup)."""

    def action() -> None:
        api_key = typer.prompt(
            "Enter your xAI API key",
            default="",
            show_default=False,
            hide_input=True,
            confirmation_prompt=True,
        )
        config = load_config()
        if api_key:
            config.auth.api_key = api_key
        save_config(config)
        write_text(f"Config saved to {CONFIG_FILE}")

    run_cli(action)


@app.command()
def set(
    key: Annotated[str, typer.Argument(help="Config key (e.g. api_key, default_model)")],
    value: Annotated[str | None, typer.Argument(help="Config value")] = None,
) -> None:
    """Set a configuration value."""

    def action() -> None:
        config = load_config()
        setting_value = value
        if key == "api_key":
            if value is not None:
                raise ConfigError("Pass API keys through the hidden prompt: xai config set api_key")
            setting_value = typer.prompt(
                "Enter your xAI API key",
                hide_input=True,
                confirmation_prompt=True,
            )
        elif value is None:
            raise ConfigError(f"A value is required for {key!r}.")
        _set_config_value(config, key, setting_value or "")
        save_config(config)
        displayed = "[configured]" if key == "api_key" else setting_value
        write_text(f"Set {key} = {displayed}")

    run_cli(action)


@app.command()
def get(
    key: Annotated[str, typer.Argument(help="Config key to get")],
) -> None:
    """Get a configuration value."""

    def action() -> None:
        config = load_config()
        values = _config_values(config)
        if key not in values:
            raise ConfigError(f"Unknown config key: {key}")
        write_text(str(values[key]))

    run_cli(action)


@app.command("list")
def list_config() -> None:
    """List all configuration values."""

    def action() -> None:
        config = load_config()
        values = _config_values(config)
        write_text(
            "\n".join(
                [
                    f"Config file: {CONFIG_FILE}",
                    "",
                    "[auth]",
                    f"  api_key = {values['api_key']}",
                    "",
                    "[defaults]",
                    f"  model = {values['model']}",
                    f"  stream = {values['stream']}",
                    f"  format = {values['format']}",
                    "",
                    "[search]",
                    f"  enable_image_understanding = {values['enable_image_understanding']}",
                    f"  enable_video_understanding = {values['enable_video_understanding']}",
                ]
            )
        )

    run_cli(action)


@app.command()
def path() -> None:
    """Print the platform-specific configuration file path."""
    write_text(str(CONFIG_FILE))


def _set_config_value(config: Config, key: str, value: str) -> None:
    if key == "api_key":
        config.auth.api_key = value
    elif key in {"default_model", "model"}:
        if not value.strip():
            raise ConfigError("The model name cannot be empty.")
        config.defaults.model = value.strip()
    elif key == "stream":
        config.defaults.stream = parse_boolean(value)
    elif key == "format":
        try:
            config.defaults.format = OutputFormat(value.lower())
        except ValueError as exc:
            raise ConfigError("Format must be text, markdown, or json.") from exc
    elif key == "enable_image_understanding":
        config.search.enable_image_understanding = parse_boolean(value)
    elif key == "enable_video_understanding":
        config.search.enable_video_understanding = parse_boolean(value)
    else:
        raise ConfigError(f"Unknown config key: {key}")


def _config_values(config: Config) -> dict[str, str | bool]:
    return {
        "api_key": "[configured]" if config.auth.api_key else "[not configured]",
        "default_model": config.defaults.model,
        "model": config.defaults.model,
        "stream": config.defaults.stream,
        "format": config.defaults.format.value,
        "enable_image_understanding": config.search.enable_image_understanding,
        "enable_video_understanding": config.search.enable_video_understanding,
    }
