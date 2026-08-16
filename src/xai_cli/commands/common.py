from __future__ import annotations

from collections.abc import Callable

import typer

from xai_cli.client.models import (
    Answer,
    CompletedEvent,
    DeltaEvent,
    ResponseEnvelope,
    ResponseRequest,
)
from xai_cli.client.transport import ApiClient
from xai_cli.config import Config, get_api_key, get_model, load_config
from xai_cli.domain import ModelsOutputFormat, OutputFormat
from xai_cli.errors import InvalidRequestError, XaiError
from xai_cli.output import (
    finish_stream,
    write_answer,
    write_diagnostic,
    write_error,
    write_json,
    write_markdown,
    write_stream_delta,
    write_text,
)

RequestFactory = Callable[[str, bool, Config], ResponseRequest]


def execute_answer(
    request_factory: RequestFactory,
    *,
    format_override: OutputFormat | None,
    no_stream: bool,
    raw: bool,
    progress: str,
) -> None:
    def action() -> None:
        config = load_config()
        output_format = format_override or config.defaults.format
        if raw and output_format is not OutputFormat.JSON:
            raise InvalidRequestError("--raw requires --format json.")
        stream = config.defaults.stream and not no_stream and output_format is not OutputFormat.JSON
        request = request_factory(get_model(config), stream, config)
        write_diagnostic(progress)
        with ApiClient(get_api_key(config)) as client:
            if stream:
                with client.stream_response(request) as events:
                    wrote_delta = False
                    completed = False
                    for event in events:
                        if isinstance(event, DeltaEvent):
                            write_stream_delta(event.delta)
                            wrote_delta = True
                        elif isinstance(event, CompletedEvent):
                            completed = True
                    if wrote_delta:
                        finish_stream()
                    if not completed:
                        raise InvalidRequestError("The response stream did not complete.")
                return
            response = client.create_response(request)
        answer = response_to_answer(response)
        if output_format is OutputFormat.JSON:
            write_answer(answer, raw=response if raw else None)
        elif output_format is OutputFormat.MARKDOWN:
            write_markdown(answer.text)
        else:
            write_text(answer.text)

    run_cli(action)


def execute_models(format_override: ModelsOutputFormat) -> None:
    def action() -> None:
        with ApiClient(get_api_key()) as client:
            models = client.list_models()
        if format_override is ModelsOutputFormat.JSON:
            write_json(
                {
                    "schema_version": 1,
                    "models": [
                        {
                            "id": model.identifier,
                            "owned_by": model.owned_by,
                        }
                        for model in models.data
                    ],
                }
            )
            return
        if not models.data:
            write_text("No models found.")
            return
        lines = ["Available models:"]
        for model in models.data:
            suffix = f" (by {model.owned_by})" if model.owned_by else ""
            lines.append(f"  {model.identifier}{suffix}")
        write_text("\n".join(lines))

    run_cli(action)


def run_cli(action: Callable[[], None]) -> None:
    try:
        action()
    except XaiError as exc:
        write_error(exc.label, str(exc))
        raise typer.Exit(int(exc.exit_code)) from exc


def response_to_answer(response: ResponseEnvelope) -> Answer:
    return Answer.from_response(response)
