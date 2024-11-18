"""Console script for baikalctl."""

import atexit
import json
import logging
import socket
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


DEFAULT_URL = "http://caldav." + ".".join(socket.getfqdn().split(".")[1:]) + "/baikal"
DEFAULT_PROFILE_DIR = Path.home() / ".profile"

DEFAULTS = dict(
    username="admin", address="0.0.0.0", port=8000, log_level="WARNING", url=DEFAULT_URL, profile=DEFAULT_PROFILE_DIR
)


@click.group("baikalctl", invoke_without_command=True, context_settings={"auto_envvar_prefix": "BAIKALCTL"})
@click.version_option(message=header)
@click.option("-C", "--config-file", default=Path.home() / ".baikalctl", help="config file (default ~/.baikalctl)")
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option("-u", "--username", help="username (default: admin)")
@click.option("-p", "--password", help="password")
@click.option("-U", "--url", help="baikal server URL")
@click.option("-a", "--api", help="api url (selects client mode)")
@click.option("-A", "--address", help="server listen address (default: 0.0.0.0)")
@click.option("-P", "--port", type=int, help="server listen port (default: 8000)")
@click.option("-l", "--log-level", default="WARNING", help="server log level (default: WARNING)")
@click.option("-v", "--verbose", is_flag=True, help="enable diagnostic output")
@click.option("--profile", help="profile directory")
@click.option("--cert", help="cient certificate file")
@click.option("--key", help="client certificate key file")
@click.option("--show-config", is_flag=True, help="show configuration")
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.pass_context
def cli(
    ctx,
    config_file,
    username,
    password,
    url,
    api,
    address,
    port,
    profile,
    cert,
    key,
    log_level,
    verbose,
    debug,
    shell_completion,
    show_config,
):
    """baikalctl - admin CLI for baikal webdav/webcal server"""

    if ctx.invoked_subcommand == "version":
        click.echo(__version__)
        sys.exit(0)

    cfgdata = {}
    cfgfile = Path(config_file)
    if cfgfile.is_file():
        if verbose:
            click.echo(f"Using config file {cfgfile}", err=True)
        cfgtext = cfgfile.read_text()
        if cfgtext:
            cfgdata = yaml.safe_load(cfgfile.read_text())

    for k, v in DEFAULTS.items():
        cfgdata.setdefault(k, v)

    try:
        if not url:
            url = cfgdata["url"]
        if not username:
            username = cfgdata["username"]
        if not password:
            password = cfgdata.get("password", None)
        if not address:
            address = cfgdata["address"]
        if not port:
            port = int(cfgdata["port"])
        if not log_level:
            log_level = cfgdata["log_level"]
        if not profile:
            profile = cfgdata["profile"]
        if not cert:
            cert = cfgdata.get("cert", None)
        if not key:
            key = cfgdata.get("key", None)

    except KeyError as ex:
        raise RuntimeError(f"Missing config value '{ex.args[0]}'")

    if show_config:
        click.echo(f"username: {username}")
        click.echo(f"password: {"'" + '*'*len(password) + "'" if password else None}")
        click.echo(f"url: {url}")
        click.echo(f"api: {api}")
        click.echo(f"address: {address}")
        click.echo(f"port: {port}")
        click.echo(f"profile: {profile}")
        click.echo(f"cert: {cert}")
        click.echo(f"key: {key}")
        click.echo(f"log_level: {log_level}")
        click.echo(f"verbose: {verbose}")
        click.echo(f"debug: {debug}")
        click.echo(f"log_level: {log_level}")
        sys.exit(0)

    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help(), err=True)
        sys.exit(1)

    logging.basicConfig(level=baikal.log_level)

    baikal.log_level = log_level
    baikal.debug = debug
    baikal.verbose = verbose
    baikal.header = header

    if api:
        baikal.url = api
        baikal.client = True
    else:
        if not password:
            raise RuntimeError("Missing config value: 'password'")
        baikal.startup(url, username, password, address, port, profile, cert, key)
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
    """API server"""
    uvicorn.run(
        "baikalctl:app",
        host=ctx.address,
        port=ctx.port,
        log_level=ctx.log_level.lower(),
    )


@cli.command
@click.pass_obj
def reset(ctx):
    """restart client driver"""
    click.echo(json.dumps(ctx.reset(), indent=2))


@cli.command
@click.pass_obj
def version(ctx):
    """print version number"""
    click.echo(__version__)


@cli.command
@click.pass_obj
def status(ctx):
    """output status"""
    click.echo(json.dumps(ctx.status(), indent=2))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
