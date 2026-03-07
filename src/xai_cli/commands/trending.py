from __future__ import annotations

from typing import Annotated, Optional

import typer

from xai_cli.client.responses import extract_text_from_response, x_search
from xai_cli.config import get_model, load_config
from xai_cli.errors import handle_error
from xai_cli.output import print_json, print_text


def trending(
    topic: Annotated[Optional[str], typer.Argument(help="Optional topic for details")] = None,
    category: Annotated[
        Optional[str],
        typer.Option("--category", help="Category: tech, politics, sports, entertainment"),
    ] = None,
    format: Annotated[str, typer.Option("--format", help="Output format: text, json")] = "",
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Get trending topics on X."""
    try:
        config = load_config()
        model = get_model()
        fmt = format or config.defaults.format
        stream = config.defaults.stream and not no_stream

        if topic:
            prompt = f'Show trending posts and discussions about "{topic}" on X right now'
        elif category:
            prompt = f"What are the current trending topics on X in the {category} category?"
        else:
            prompt = "What are the current trending topics on X?"

        if fmt != "json" and stream:
            typer.echo("Fetching trending topics...\n", err=True)

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
