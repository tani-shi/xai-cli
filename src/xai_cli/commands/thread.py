from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.client.models import ResponseRequest
from xai_cli.client.responses import build_x_search_request
from xai_cli.commands.common import execute_answer
from xai_cli.config import Config
from xai_cli.domain import OutputFormat, validate_post_url


def thread(
    url: Annotated[str, typer.Argument(help="Tweet/post URL")],
    summary: Annotated[
        bool, typer.Option("--summary", help="Show summary instead of full thread")
    ] = False,
    format: Annotated[OutputFormat | None, typer.Option("--format")] = None,
    raw: Annotated[bool, typer.Option("--raw", help="Emit raw API JSON")] = False,
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Generate a cited answer about the X thread at a post URL."""

    def request(model: str, stream: bool, _config: Config) -> ResponseRequest:
        post_url = validate_post_url(url)
        prompt = (
            f"Summarize the X thread at {post_url}, preserving important context and citations."
            if summary
            else f"Explain the full X thread or conversation at {post_url}, with citations."
        )
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
        progress=f"Searching X for thread context at {url}...",
    )
