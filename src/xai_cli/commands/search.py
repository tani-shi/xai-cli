from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.client.models import ResponseRequest
from xai_cli.client.responses import build_x_search_request
from xai_cli.commands.common import execute_answer
from xai_cli.config import Config
from xai_cli.domain import OutputFormat, parse_date


def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    from_date: Annotated[
        str | None, typer.Option("--from", help="Inclusive start date (YYYY-MM-DD)")
    ] = None,
    to_date: Annotated[
        str | None, typer.Option("--to", help="Inclusive end date (YYYY-MM-DD)")
    ] = None,
    from_handles: Annotated[
        list[str] | None,
        typer.Option("--from-user", help="Limit to specific accounts (@handle)"),
    ] = None,
    exclude_handles: Annotated[
        list[str] | None, typer.Option("--exclude", help="Exclude specific accounts (@handle)")
    ] = None,
    images: Annotated[bool, typer.Option("--images", help="Enable image understanding")] = False,
    format: Annotated[OutputFormat | None, typer.Option("--format", help="Output format")] = None,
    raw: Annotated[
        bool, typer.Option("--raw", help="Emit the raw API response; requires JSON format")
    ] = False,
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Generate a cited answer using xAI's X Search tool."""

    def request(model: str, stream: bool, config: Config) -> ResponseRequest:
        return build_x_search_request(
            query,
            model,
            stream=stream,
            allowed_handles=from_handles,
            excluded_handles=exclude_handles,
            from_date=parse_date(from_date),
            to_date=parse_date(to_date),
            enable_images=images or config.search.enable_image_understanding,
            enable_video=config.search.enable_video_understanding,
        )

    execute_answer(
        request,
        format_override=format,
        no_stream=no_stream,
        raw=raw,
        progress=f'Searching X to answer "{query}"...',
    )
