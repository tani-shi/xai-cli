from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Annotated, Any

import typer

from xai_cli.api import Answer, XaiError, create_answer

app = typer.Typer(
    help="Ask Grok through xAI's X Search or Web Search tool and print the answer with sources.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

DATE_FORMAT = ["%Y-%m-%d"]
Json = Annotated[bool, typer.Option("--json", help="Print JSON.")]
Images = Annotated[bool, typer.Option("--images", help="Let Grok read images.")]


@app.command()
def search(
    query: str,
    from_date: Annotated[
        datetime | None, typer.Option("--from", formats=DATE_FORMAT, help="First day (UTC).")
    ] = None,
    to_date: Annotated[
        datetime | None,
        typer.Option("--to", formats=DATE_FORMAT, help="Last day, inclusive (UTC)."),
    ] = None,
    from_user: Annotated[
        list[str] | None, typer.Option("--from-user", help="Only these handles (max 20).")
    ] = None,
    exclude: Annotated[
        list[str] | None, typer.Option("--exclude", help="Exclude these handles (max 20).")
    ] = None,
    images: Images = False,
    video: Annotated[bool, typer.Option("--video", help="Let Grok read videos.")] = False,
    json_output: Json = False,
) -> None:
    """Answer with X Search."""
    tool: dict[str, Any] = {"type": "x_search"}
    if from_date:
        tool["from_date"] = from_date.date().isoformat()
    if to_date:
        tool["to_date"] = _day_after(to_date)
    if from_user:
        tool["allowed_x_handles"] = [handle.removeprefix("@") for handle in from_user]
    if exclude:
        tool["excluded_x_handles"] = [handle.removeprefix("@") for handle in exclude]
    if images:
        tool["enable_image_understanding"] = True
    if video:
        tool["enable_video_understanding"] = True
    _run(query, tool, json_output)


@app.command()
def web(
    query: str,
    domain: Annotated[
        list[str] | None, typer.Option("--domain", help="Only these domains (max 5).")
    ] = None,
    exclude_domain: Annotated[
        list[str] | None, typer.Option("--exclude-domain", help="Exclude these domains (max 5).")
    ] = None,
    images: Images = False,
    json_output: Json = False,
) -> None:
    """Answer with Web Search."""
    tool: dict[str, Any] = {"type": "web_search"}
    filters = {"allowed_domains": domain, "excluded_domains": exclude_domain}
    if any(filters.values()):
        tool["filters"] = {key: value for key, value in filters.items() if value}
    if images:
        tool["enable_image_understanding"] = True
    _run(query, tool, json_output)


def _day_after(day: datetime) -> str:
    # xAI's to_date is exclusive; the same from/to date would silently search nothing.
    try:
        return (day + timedelta(days=1)).date().isoformat()
    except OverflowError as exc:
        raise typer.BadParameter("date is out of range", param_hint="--to") from exc


def _run(query: str, tool: dict[str, Any], json_output: bool) -> None:
    try:
        answer = create_answer(query, tool)
    except XaiError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(render(answer, json_output=json_output))


def render(answer: Answer, *, json_output: bool) -> str:
    if json_output:
        return json.dumps(asdict(answer), ensure_ascii=False, indent=2)
    if not answer.sources:
        return answer.text
    sources = "\n".join(f"- {url}" for url in answer.sources)
    return f"{answer.text}\n\nSources:\n{sources}"
