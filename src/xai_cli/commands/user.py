from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.client.models import ResponseRequest
from xai_cli.client.responses import build_x_search_request
from xai_cli.commands.common import execute_answer
from xai_cli.config import Config
from xai_cli.domain import OutputFormat, normalize_handle, parse_date


def user(
    handle: Annotated[str, typer.Argument(help="User handle (e.g. @elonmusk)")],
    query: Annotated[str | None, typer.Argument(help="Optional topic filter")] = None,
    from_date: Annotated[
        str | None, typer.Option("--from", help="Inclusive start date (YYYY-MM-DD)")
    ] = None,
    to_date: Annotated[
        str | None, typer.Option("--to", help="Inclusive end date (YYYY-MM-DD)")
    ] = None,
    format: Annotated[OutputFormat | None, typer.Option("--format")] = None,
    raw: Annotated[bool, typer.Option("--raw", help="Emit raw API JSON")] = False,
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Generate a cited answer about an X user's posts."""

    def request(model: str, stream: bool, config: Config) -> ResponseRequest:
        username = normalize_handle(handle)
        prompt = (
            f"Use X posts from @{username} to answer: {query}"
            if query
            else (f"Summarize the recent X posts from @{username}, with citations.")
        )
        return build_x_search_request(
            prompt,
            model,
            stream=stream,
            allowed_handles=[username],
            from_date=parse_date(from_date),
            to_date=parse_date(to_date),
        )

    execute_answer(
        request,
        format_override=format,
        no_stream=no_stream,
        raw=raw,
        progress=f"Searching X to answer about @{handle.removeprefix('@')}...",
    )
