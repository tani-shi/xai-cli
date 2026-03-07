import typer


class XaiError(Exception):
    exit_code: int = 1


class AuthError(XaiError):
    exit_code = 2


class ApiError(XaiError):
    exit_code = 3


def handle_error(e: Exception) -> None:
    if isinstance(e, AuthError):
        typer.echo(f"Authentication error: {e}", err=True)
        raise SystemExit(2)
    if isinstance(e, ApiError):
        typer.echo(f"API error: {e}", err=True)
        raise SystemExit(3)
    if isinstance(e, XaiError):
        typer.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    typer.echo(f"Unexpected error: {e}", err=True)
    raise SystemExit(1)
