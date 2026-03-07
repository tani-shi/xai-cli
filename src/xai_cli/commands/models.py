from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.client.base import get_json
from xai_cli.errors import handle_error
from xai_cli.output import print_json


def models(
    format: Annotated[str, typer.Option("--format", help="Output format: text, json")] = "",
) -> None:
    """List available models."""
    try:
        result = get_json("/v1/models")

        if format == "json":
            print_json(result)
            return

        data = result.get("data", result.get("models", []))
        if not data:
            typer.echo("No models found.")
            return

        typer.echo("Available models:\n")
        for model in data:
            model_id = model.get("id", model.get("name", "unknown"))
            owned_by = model.get("owned_by", "")
            line = f"  {model_id}"
            if owned_by:
                line += f"  (by {owned_by})"
            typer.echo(line)
    except Exception as e:
        handle_error(e)
