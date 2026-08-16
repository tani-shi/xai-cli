from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.client.models import ResponseRequest
from xai_cli.client.responses import build_x_search_request
from xai_cli.commands.common import execute_answer
from xai_cli.config import Config
from xai_cli.domain import OutputFormat, TrendingCategory
from xai_cli.errors import InvalidRequestError


def trending(
    topic: Annotated[str | None, typer.Argument(help="Optional topic for details")] = None,
    category: Annotated[
        TrendingCategory | None,
        typer.Option("--category", help="Topic category"),
    ] = None,
    format: Annotated[OutputFormat | None, typer.Option("--format")] = None,
    raw: Annotated[bool, typer.Option("--raw", help="Emit raw API JSON")] = False,
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Generate a cited answer about current trends on X."""

    def request(model: str, stream: bool, _config: Config) -> ResponseRequest:
        if topic and category:
            raise InvalidRequestError("TOPIC and --category cannot be combined.")
        if topic:
            prompt = f'Analyze current X trends and discussion about "{topic}", with citations.'
        elif category:
            prompt = f"Analyze current {category.value} trends on X, with citations."
        else:
            prompt = "Analyze the most important current trends on X, with citations."
        return build_x_search_request(
            prompt,
            model,
            stream=stream,
        )

    execute_answer(
        request,
        format_override=format,
        no_stream=no_stream,
        raw=raw,
        progress="Searching X to analyze current trends...",
    )
