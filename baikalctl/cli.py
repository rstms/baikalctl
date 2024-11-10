"""Console script for baikalctl."""

import atexit
import json
import sys
from pathlib import Path

import click
import click.core
import uvicorn
import yaml

from .client import baikal
from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


def _cleanup():
    baikal.shutdown()

@click.group("baikalctl", context_settings={"auto_envvar_prefix": "BAIKALCTL"})
@click.version_option(message=header)
@click.option("-C", "--config-file", envvar="BAIKAL_CONFIG", default=Path.home() / ".baikalctl", help="config file")
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option("-u", "--username", envvar="BAIKAL_USERNAME", default="admin", help="username")
@click.option("-p", "--password", envvar="BAIKAL_PASSWORD", help="password")
@click.option("-U", "--url", envvar="BAIKAL_URL", help="password")
@click.option("-a", "--api", envvar="BAIKAL_API", help="api url")
@click.option("-A", "--address", envvar="BAIKAL_SERVER_ADDRESS", help="server listen address")
@click.option("-P", "--port", type=int, default=None, envvar="BAIKAL_SERVER_PORT", help="server listen port")
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.pass_context
def cli(ctx, config_file, username, password, url, api, address, port, debug, shell_completion):
    """baikalctl top-level help"""
    cfgfile = Path(config_file)
    if cfgfile.is_file():
        cfgdata = yaml.safe_load(cfgfile.read_text())
        if not url:
            url = cfgdata["url"]
        if not username:
            username = cfgdata["username"]
        if not password:
            password = cfgdata["password"]
        if not address:
            address = cfgdata['address']
        if not port:
            port = int(cfgdata['port'])
    if not username:
        raise RuntimeError("username not specified")
    if not password:
        raise RuntimeError("password not specified")
    if not url:
        raise RuntimeError("URL not specified")

    if api:
        baikal.url = api
        baikal.client = True
    else:
        baikal.startup(url, username, password, address, port)
        atexit.register(_cleanup)
    ctx.obj = baikal


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
def mkuser(ctx, username, display_name, password):
    """add user account"""
    click.echo(json.dumps(ctx.add_user(username, display_name, password), indent=2))


@cli.command
@click.argument("username")
@click.pass_obj
def rmuser(ctx, username):
    """delete user account"""
    click.echo(json.dumps(ctx.delete_user(username), indent=2))


@cli.command
@click.argument("username")
@click.pass_obj
def books(ctx, username):
    """list address books for user"""
    click.echo(json.dumps(ctx.list_address_books(username), indent=2))


@cli.command
@click.argument("username")
@click.argument("name")
@click.argument("description")
@click.pass_obj
def mkbook(ctx, username, name, description):
    """add address book for user"""
    click.echo(json.dumps(ctx.add_address_book(username, name, description), indent=2))


@cli.command
@click.argument("username")
@click.argument("name")
@click.pass_obj
def rmbook(ctx, username, name):
    """delete address book for user"""
    click.echo(json.dumps(ctx.delete_address_book(username, name), indent=2))


@cli.command
@click.option("-l", "--log-level", default="ERROR", help="log level")
@click.pass_obj
def server(ctx, log_level):
    uvicorn.run(
        "baikalctl:app",
        host=ctx.address,
        port=ctx.port,
        log_level=log_level.lower(),
    )


@cli.command
@click.pass_obj
def reset(ctx):
    click.echo(json.dumps(ctx.reset(), indent=2))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
