from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.config import CONFIG_FILE, load_config, save_config

app = typer.Typer(help="Manage configuration.")


@app.command()
def init() -> None:
    """Initialize configuration (interactive setup)."""
    typer.echo("xai CLI setup\n")

    api_key = typer.prompt("Enter your xAI API key", default="", show_default=False)
    if not api_key:
        typer.echo("Skipped API key. Set it later with: xai config set api_key <key>")

    config = load_config()
    if api_key:
        config.auth.api_key = api_key
    save_config(config)

    typer.echo(f"\nConfig saved to {CONFIG_FILE}")


@app.command()
def set(
    key: Annotated[str, typer.Argument(help="Config key (e.g. api_key, default_model)")],
    value: Annotated[str, typer.Argument(help="Config value")],
) -> None:
    """Set a configuration value."""
    config = load_config()

    key_map = {
        "api_key": lambda v: setattr(config.auth, "api_key", v),
        "default_model": lambda v: setattr(config.defaults, "model", v),
        "model": lambda v: setattr(config.defaults, "model", v),
        "stream": lambda v: setattr(config.defaults, "stream", v.lower() in ("true", "1", "yes")),
        "format": lambda v: setattr(config.defaults, "format", v),
        "enable_image_understanding": lambda v: setattr(
            config.search, "enable_image_understanding", v.lower() in ("true", "1", "yes")
        ),
        "enable_video_understanding": lambda v: setattr(
            config.search, "enable_video_understanding", v.lower() in ("true", "1", "yes")
        ),
    }

    setter = key_map.get(key)
    if setter is None:
        typer.echo(f"Unknown config key: {key}", err=True)
        raise typer.Exit(1)

    setter(value)
    save_config(config)
    typer.echo(f"Set {key} = {value}")


@app.command()
def get(
    key: Annotated[str, typer.Argument(help="Config key to get")],
) -> None:
    """Get a configuration value."""
    config = load_config()

    key_map = {
        "api_key": config.auth.api_key,
        "default_model": config.defaults.model,
        "model": config.defaults.model,
        "stream": str(config.defaults.stream),
        "format": config.defaults.format,
        "enable_image_understanding": str(config.search.enable_image_understanding),
        "enable_video_understanding": str(config.search.enable_video_understanding),
    }

    value = key_map.get(key)
    if value is None:
        typer.echo(f"Unknown config key: {key}", err=True)
        raise typer.Exit(1)

    typer.echo(value)


@app.command("list")
def list_config() -> None:
    """List all configuration values."""
    config = load_config()

    typer.echo(f"Config file: {CONFIG_FILE}\n")
    typer.echo("[auth]")
    masked = (
        config.auth.api_key[:8] + "..." if len(config.auth.api_key) > 8 else config.auth.api_key
    )
    typer.echo(f"  api_key = {masked}")
    typer.echo("\n[defaults]")
    typer.echo(f"  model = {config.defaults.model}")
    typer.echo(f"  stream = {config.defaults.stream}")
    typer.echo(f"  format = {config.defaults.format}")
    typer.echo("\n[search]")
    typer.echo(f"  enable_image_understanding = {config.search.enable_image_understanding}")
    typer.echo(f"  enable_video_understanding = {config.search.enable_video_understanding}")
