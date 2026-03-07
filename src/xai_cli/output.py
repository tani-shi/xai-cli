from __future__ import annotations

import json
import sys

from rich.console import Console
from rich.markdown import Markdown


def is_pipe() -> bool:
    return not sys.stdout.isatty()


def get_console() -> Console:
    return Console(force_terminal=not is_pipe(), no_color=is_pipe())


def print_text(text: str) -> None:
    if is_pipe():
        sys.stdout.write(text)
        sys.stdout.flush()
    else:
        console = get_console()
        console.print(Markdown(text))


def print_streaming_text(text: str) -> None:
    if is_pipe():
        sys.stdout.write(text)
        sys.stdout.flush()
    else:
        sys.stdout.write(text)
        sys.stdout.flush()


def print_json(data: object) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    sys.stdout.flush()


def print_error(msg: str) -> None:
    sys.stderr.write(f"Error: {msg}\n")
    sys.stderr.flush()
