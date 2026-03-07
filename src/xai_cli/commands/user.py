from __future__ import annotations

from typing import Annotated, Optional

import typer

from xai_cli.client.responses import extract_text_from_response, x_search
from xai_cli.config import get_model, load_config
from xai_cli.errors import handle_error
from xai_cli.output import print_json, print_text


def user(
    handle: Annotated[str, typer.Argument(help="User handle (e.g. @elonmusk)")],
    query: Annotated[Optional[str], typer.Argument(help="Optional topic filter")] = None,
    from_date: Annotated[
        Optional[str], typer.Option("--from", help="Start date (YYYY-MM-DD)")
    ] = None,
    to_date: Annotated[Optional[str], typer.Option("--to", help="End date (YYYY-MM-DD)")] = None,
    format: Annotated[str, typer.Option("--format", help="Output format: text, json")] = "",
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Search posts from a specific user."""
    try:
        config = load_config()
        model = get_model()
        fmt = format or config.defaults.format
        stream = config.defaults.stream and not no_stream

        username = handle.lstrip("@")
        prompt = f"Show recent posts from @{username}"
        if query:
            prompt += f" {query}"

        if fmt != "json" and stream:
            typer.echo(f"Searching posts from @{username}...\n", err=True)

        result = x_search(
            prompt,
            model,
            stream=stream and fmt != "json",
            allowed_handles=[username],
            from_date=from_date,
            to_date=to_date,
        )

        if isinstance(result, dict):
            if fmt == "json":
                print_json(result)
            else:
                text = extract_text_from_response(result)
                print_text(text)
    except Exception as e:
        handle_error(e)
