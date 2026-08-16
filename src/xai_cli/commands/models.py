from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.commands.common import execute_models
from xai_cli.domain import ModelsOutputFormat


def models(
    format: Annotated[ModelsOutputFormat, typer.Option("--format", help="Output format")] = (
        ModelsOutputFormat.TEXT
    ),
) -> None:
    """List available models."""
    execute_models(format)
