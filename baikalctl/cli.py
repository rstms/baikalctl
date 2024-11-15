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


@click.group("baikalctl", context_settings={"auto_envvar_prefix": "BAIKAL"})
@click.version_option(message=header)
@click.option("-C", "--config-file", default=Path.home() / ".baikalctl", help="config file (default ~/.baikalctl)")
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option("-u", "--username", help="username (default: admin)")
@click.option("-p", "--password", help="password")
@click.option("-U", "--url", help="password")
@click.option("-a", "--api", help="api url")
@click.option("-A", "--address", help="server listen address (default: 127.0.0.1)")
@click.option("-P", "--port", type=int, help="server listen port (default: 8000)")
@click.option("-l", "--log-level", help="server log level (default: WARNING)")
@click.option("-v", "--verbose", is_flag=True, help="enable diagnostic output")
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.pass_context
def cli(ctx, config_file, username, password, url, api, address, port, log_level, verbose, debug, shell_completion):
    """baikalctl top-level help"""
    cfgfile = Path(config_file)
    if cfgfile.is_file():
        if verbose:
            click.echo(f"config_file={cfgfile}")
        cfgdata = yaml.safe_load(cfgfile.read_text())
        if not url:
            url = cfgdata["url"]
        if not username:
            username = cfgdata.get("username", "admin")
        if not password:
            password = cfgdata["password"]
        if not address:
            address = cfgdata.get("address", "127.0.0.1")
        if not port:
            port = int(cfgdata.get("port", 8000))
        if not log_level:
            log_level = cfgdata.get("log_level", "WARNING")
    if not username:
        raise RuntimeError("username not specified")
    if not password:
        raise RuntimeError("password not specified")
    if not url:
        raise RuntimeError("URL not specified")

    if verbose:
        click.echo(f"username={username}")
        click.echo(f"password={'*'*len(password)}")
        click.echo(f"url={url}")
        click.echo(f"api={api}")
        click.echo(f"address={address}")
        click.echo(f"port={port}")
        click.echo(f"log_level={log_level}")
        click.echo(f"debug={debug}")
        click.echo(f"verbose={verbose}")

    if api:
        baikal.url = api
        baikal.client = True
        baikal.verbose = verbose
    else:
        baikal.startup(url, username, password, address, port, log_level, verbose)
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
@click.pass_obj
def server(ctx):
    click.echo(header)
    uvicorn.run(
        "baikalctl:app",
        host=ctx.address,
        port=ctx.port,
        log_level=ctx.log_level.lower(),
    )


@cli.command
@click.pass_obj
def reset(ctx):
    click.echo(json.dumps(ctx.reset(), indent=2))

@cli.command
@click.pass_obj
def version(ctx):
    """version"""
    click.echo(__version__)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
