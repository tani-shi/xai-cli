from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.client.responses import extract_text_from_response, x_search
from xai_cli.config import get_model, load_config
from xai_cli.errors import handle_error
from xai_cli.output import print_json, print_text


def thread(
    url: Annotated[str, typer.Argument(help="Tweet/post URL")],
    summary: Annotated[
        bool, typer.Option("--summary", help="Show summary instead of full thread")
    ] = False,
    format: Annotated[str, typer.Option("--format", help="Output format: text, json")] = "",
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Retrieve a thread/conversation from a post URL."""
    try:
        config = load_config()
        model = get_model()
        fmt = format or config.defaults.format
        stream = config.defaults.stream and not no_stream

        if summary:
            prompt = f"Summarize the thread at {url}"
        else:
            prompt = f"Show the full thread/conversation at {url}"

        if fmt != "json" and stream:
            typer.echo(f"Fetching thread from {url}...\n", err=True)

        result = x_search(
            prompt,
            model,
            stream=stream and fmt != "json",
        )

        if isinstance(result, dict):
            if fmt == "json":
                print_json(result)
            else:
                text = extract_text_from_response(result)
                print_text(text)
    except Exception as e:
        handle_error(e)
