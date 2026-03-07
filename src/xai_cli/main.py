import typer

from xai_cli.commands.config_cmd import app as config_app
from xai_cli.commands.models import models
from xai_cli.commands.search import search
from xai_cli.commands.thread import thread
from xai_cli.commands.trending import trending
from xai_cli.commands.user import user
from xai_cli.commands.web import web

app = typer.Typer(
    name="xai",
    help="CLI tool for searching and browsing X (Twitter) content via xAI API.",
    no_args_is_help=True,
)

app.command()(search)
app.command()(user)
app.command()(thread)
app.command()(trending)
app.command()(web)
app.command()(models)
app.add_typer(config_app, name="config", help="Manage configuration")

if __name__ == "__main__":
    app()
