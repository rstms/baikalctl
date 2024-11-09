"""Console script for baikalctl."""

import atexit
import json
import sys
import yaml
from pathlib import Path

import click
import click.core

from .client import Client
from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


def _cleanup(client):
    client.close()


@click.group("baikalctl", context_settings={"auto_envvar_prefix": "BAIKALCTL"})
@click.version_option(message=header)
@click.option("-c", "--config", envvar="BAIKAL_CONFIG", default=Path.home() / ".baikalctl", help="config file")
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option("-u", "--username", envvar="BAIKAL_USERNAME", default="admin", help="username")
@click.option("-p", "--password", envvar="BAIKAL_PASSWORD", help="password")
@click.option("-U", "--url", envvar="BAIKAL_URL", help="password")
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.pass_context
def cli(ctx, config, username, password, url, debug, shell_completion):
    """baikalctl top-level help"""
    cfgfile = Path(config)
    if cfgfile.is_file():
        cfgdata = yaml.safe_load(cfgfile.read_text())
        if not url:
            url = cfgdata['url']
        if not username:
            username = cfgdata['username']
        if not password:
            password = cfgdata['password']
    if not username:
        raise RuntimeError("username not specified")
    if not password:
        raise RuntimeError("password not specified")
    if not url:
        raise RuntimeError("URL not specified")
    ctx.obj = Client(url, username, password)
    atexit.register(_cleanup, ctx.obj)


@cli.command
@click.pass_obj
def users(ctx):
    """list users"""
    click.echo(json.dumps(ctx.list_users(), indent=2))


@cli.command
@click.argument("username")
@click.argument("display-name")
@click.argument("password")
@click.pass_obj
def add_user(ctx, username, display_name, email_address, password):
    """add user account"""
    ctx.add_user(username, display_name, password)


@cli.command
@click.argument("username")
@click.pass_obj
def delete_user(ctx, username):
    """delete user account"""
    ctx.delete_user(username)


@cli.command
@click.argument("username")
@click.pass_obj
def address_books(ctx, username):
    """list address books for user"""
    click.echo(json.dumps(ctx.list_address_books(username), indent=2))


@cli.command
@click.argument("username")
@click.argument("name")
@click.argument("description")
@click.pass_obj
def add_address_book(ctx, username, name, description):
    """add address book for user"""
    click.echo(json.dumps(ctx.add_address_book(username, name, description), indent=2))

@cli.command
@click.argument("username")
@click.argument("name")
@click.pass_obj
def delete_address_book(ctx, username, name):
    """delete address book for user"""
    click.echo(json.dumps(ctx.delete_address_book(username, name), indent=2))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
