from __future__ import annotations

import json
import sys
from collections.abc import Mapping

from pydantic import BaseModel
from rich.console import Console
from rich.markdown import Markdown

from xai_cli.client.models import Answer


def is_pipe() -> bool:
    return not sys.stdout.isatty()


def get_console() -> Console:
    return Console(file=sys.stdout, force_terminal=not is_pipe(), no_color=is_pipe())


def write_text(text: str) -> None:
    sys.stdout.write(text)
    if text and not text.endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.flush()


def write_markdown(text: str) -> None:
    if is_pipe():
        write_text(text)
        return
    get_console().print(Markdown(text))


def write_stream_delta(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


def finish_stream() -> None:
    sys.stdout.write("\n")
    sys.stdout.flush()


def write_json(data: BaseModel | Mapping[str, object]) -> None:
    value = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    sys.stdout.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    sys.stdout.flush()


def write_answer(answer: Answer, *, raw: BaseModel | None = None) -> None:
    write_json(raw or answer)


def write_diagnostic(message: str) -> None:
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()


def write_error(label: str, message: str) -> None:
    sys.stderr.write(f"{label}: {message}\n")
    sys.stderr.flush()
