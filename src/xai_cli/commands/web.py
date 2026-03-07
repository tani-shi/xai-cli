from __future__ import annotations

from typing import Annotated, Optional

import typer

from xai_cli.client.responses import extract_text_from_response, web_search
from xai_cli.config import get_model, load_config
from xai_cli.errors import handle_error
from xai_cli.output import print_json, print_text


def web(
    query: Annotated[str, typer.Argument(help="Search query")],
    domain: Annotated[
        Optional[list[str]], typer.Option("--domain", help="Limit to specific domains")
    ] = None,
    exclude_domain: Annotated[
        Optional[list[str]], typer.Option("--exclude-domain", help="Exclude specific domains")
    ] = None,
    format: Annotated[str, typer.Option("--format", help="Output format: text, json")] = "",
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Search the web."""
    try:
        config = load_config()
        model = get_model()
        fmt = format or config.defaults.format
        stream = config.defaults.stream and not no_stream

        if fmt != "json" and stream:
            typer.echo(f'Searching the web for "{query}"...\n', err=True)

        result = web_search(
            query,
            model,
            stream=stream and fmt != "json",
            allowed_domains=domain,
            excluded_domains=exclude_domain,
        )

        if isinstance(result, dict):
            if fmt == "json":
                print_json(result)
            else:
                text = extract_text_from_response(result)
                print_text(text)
    except Exception as e:
        handle_error(e)
