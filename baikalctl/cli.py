"""Console script for baikalctl."""

import sys
from pathlib import Path

import click
import click.core

from .version import __version__, __timestamp__
from .exception_handler import ExceptionHandler


from .shell import _shell_completion

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug



@click.group("baikalctl", context_settings={"auto_envvar_prefix": "BAIKALCTL"})
@click.version_option(message=header)
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option("--shell-completion", is_flag=False, flag_value="[auto]", callback=_shell_completion, help="configure shell completion")
@click.pass_context
def cli(ctx, debug, shell_completion):
    """baikalctl top-level help"""
    pass

@cli.command
@click.option("-r", "--raises", type=str, show_envvar=True, help='example option')
@click.option("-f", "--flag", is_flag=True, help='example flag option')
@click.option("-i", "--input-file", type=click.Path(dir_okay=False, readable=True, exists=True, path_type=Path), help="input file")
@click.option("-o", "--output-file", type=click.Path(dir_okay=False, writable=True, exists=False, path_type=Path), help="output file")
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'), required=False, default='-')
@click.pass_context
def action(ctx, raises, flag, input_file, output_file, input, output):
    """action command help"""

    if raises == "exception":
        raise RuntimeError(raises)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
