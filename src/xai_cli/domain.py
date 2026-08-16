from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from urllib.parse import urlparse

from xai_cli.errors import InvalidRequestError

HANDLE_PATTERN = re.compile(r"^[A-Za-z0-9_]{1,15}$")
DOMAIN_LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
POST_HOSTS = frozenset({"x.com", "www.x.com", "twitter.com", "www.twitter.com"})


class OutputFormat(StrEnum):
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"


class ModelsOutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"


class TrendingCategory(StrEnum):
    TECH = "tech"
    POLITICS = "politics"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"


def normalize_handle(value: str) -> str:
    handle = value.removeprefix("@").strip()
    if not HANDLE_PATTERN.fullmatch(handle):
        raise InvalidRequestError(
            f"Invalid X handle {value!r}; use 1-15 letters, numbers, or underscores."
        )
    return handle


def normalize_domain(value: str) -> str:
    candidate = value.strip().lower().rstrip(".")
    if "://" in candidate or any(character in candidate for character in "/?#:@"):
        raise InvalidRequestError(
            f"Invalid domain {value!r}; provide a hostname without a scheme, port, or path."
        )
    try:
        ascii_domain = candidate.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise InvalidRequestError(f"Invalid domain {value!r}.") from exc
    labels = ascii_domain.split(".")
    if (
        len(labels) < 2
        or len(ascii_domain) > 253
        or any(not DOMAIN_LABEL_PATTERN.fullmatch(label) for label in labels)
    ):
        raise InvalidRequestError(f"Invalid domain {value!r}.")
    return ascii_domain


def validate_date_range(from_date: date | None, to_date: date | None) -> None:
    if from_date is not None and to_date is not None and from_date > to_date:
        raise InvalidRequestError("--from must be earlier than or equal to --to.")


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidRequestError(f"Invalid date {value!r}; use YYYY-MM-DD.") from exc
    if parsed.isoformat() != value:
        raise InvalidRequestError(f"Invalid date {value!r}; use YYYY-MM-DD.")
    return parsed


def validate_post_url(value: str) -> str:
    parsed = urlparse(value)
    path_parts = [part for part in parsed.path.split("/") if part]
    valid_path = len(path_parts) >= 3 and path_parts[-2] == "status" and path_parts[-1].isdigit()
    if parsed.scheme != "https" or parsed.hostname not in POST_HOSTS or not valid_path:
        raise InvalidRequestError("Post URL must be an https://x.com/<handle>/status/<id> URL.")
    return value
