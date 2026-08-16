from __future__ import annotations

from typing import Annotated

import typer

from xai_cli.client.models import ResponseRequest
from xai_cli.client.responses import build_web_search_request
from xai_cli.commands.common import execute_answer
from xai_cli.config import Config
from xai_cli.domain import OutputFormat


def web(
    query: Annotated[str, typer.Argument(help="Search query")],
    domain: Annotated[
        list[str] | None, typer.Option("--domain", help="Limit to specific domains")
    ] = None,
    exclude_domain: Annotated[
        list[str] | None, typer.Option("--exclude-domain", help="Exclude specific domains")
    ] = None,
    format: Annotated[OutputFormat | None, typer.Option("--format")] = None,
    raw: Annotated[bool, typer.Option("--raw", help="Emit raw API JSON")] = False,
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Generate a cited answer using xAI's Web Search tool."""

    def request(model: str, stream: bool, _config: Config) -> ResponseRequest:
        return build_web_search_request(
            query,
            model,
            stream=stream,
            allowed_domains=domain,
            excluded_domains=exclude_domain,
        )

    execute_answer(
        request,
        format_override=format,
        no_stream=no_stream,
        raw=raw,
        progress=f'Searching the web to answer "{query}"...',
    )
