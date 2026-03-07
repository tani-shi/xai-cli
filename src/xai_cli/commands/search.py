from __future__ import annotations

from typing import Annotated, Optional

import typer

from xai_cli.client.responses import extract_text_from_response, x_search
from xai_cli.config import get_model, load_config
from xai_cli.errors import handle_error
from xai_cli.output import print_json, print_text


def _parse_handles(handles: list[str] | None) -> list[str] | None:
    if not handles:
        return None
    return [h.lstrip("@") for h in handles]


def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    from_date: Annotated[
        Optional[str], typer.Option("--from", help="Start date (YYYY-MM-DD)")
    ] = None,
    to_date: Annotated[Optional[str], typer.Option("--to", help="End date (YYYY-MM-DD)")] = None,
    from_handles: Annotated[
        Optional[list[str]],
        typer.Option("--from-user", help="Limit to specific accounts (@handle)"),
    ] = None,
    exclude_handles: Annotated[
        Optional[list[str]], typer.Option("--exclude", help="Exclude specific accounts (@handle)")
    ] = None,
    images: Annotated[bool, typer.Option("--images", help="Enable image understanding")] = False,
    format: Annotated[
        str, typer.Option("--format", help="Output format: text, json, markdown")
    ] = "",
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Search X (Twitter) posts."""
    try:
        config = load_config()
        model = get_model()
        fmt = format or config.defaults.format
        stream = config.defaults.stream and not no_stream
        enable_images = images or config.search.enable_image_understanding

        if fmt != "json" and stream:
            typer.echo(f'Searching X for "{query}"...\n', err=True)

        result = x_search(
            query,
            model,
            stream=stream and fmt != "json",
            allowed_handles=_parse_handles(from_handles),
            excluded_handles=_parse_handles(exclude_handles),
            from_date=from_date,
            to_date=to_date,
            enable_images=enable_images,
            enable_video=config.search.enable_video_understanding,
        )

        if isinstance(result, dict):
            if fmt == "json":
                print_json(result)
            else:
                text = extract_text_from_response(result)
                print_text(text)
    except Exception as e:
        handle_error(e)
