from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    GENERAL = 1
    USAGE = 2
    AUTH = 3
    API = 4
    RATE_LIMIT = 5
    NETWORK = 6
    CONFIG = 7
    INCOMPLETE = 8


class XaiError(Exception):
    exit_code = ExitCode.GENERAL
    label = "Error"


class AuthError(XaiError):
    exit_code = ExitCode.AUTH
    label = "Authentication error"


class ApiError(XaiError):
    exit_code = ExitCode.API
    label = "API error"


class InvalidRequestError(XaiError):
    exit_code = ExitCode.USAGE
    label = "Invalid request"


class RateLimitError(XaiError):
    exit_code = ExitCode.RATE_LIMIT
    label = "Rate limit error"


class NetworkError(XaiError):
    exit_code = ExitCode.NETWORK
    label = "Network error"


class ConfigError(XaiError):
    exit_code = ExitCode.CONFIG
    label = "Configuration error"


class IncompleteResponseError(XaiError):
    exit_code = ExitCode.INCOMPLETE
    label = "Incomplete response"


class StreamError(ApiError):
    label = "Stream error"
