# cli tests

import os
import shlex

import pytest
from click.testing import CliRunner

import baikalctl
from baikalctl import __version__, cli


def test_version():
    """Test reading version and module name"""
    assert baikalctl.__name__ == "baikalctl"
    assert __version__
    assert isinstance(__version__, str)


@pytest.fixture
def run():
    runner = CliRunner()

    env = os.environ.copy()
    env["TESTING"] = "1"

    def _run(cmd, **kwargs):
        assert_exit = kwargs.pop("assert_exit", 0)
        assert_exception = kwargs.pop("assert_exception", None)
        env.update(kwargs.pop("env", {}))
        kwargs["env"] = env
        result = runner.invoke(cli, cmd, **kwargs)
        if assert_exception is not None:
            assert isinstance(result.exception, assert_exception)
        elif result.exception is not None:
            raise result.exception from result.exception
        elif assert_exit is not None:
            assert result.exit_code == assert_exit, (
                f"Unexpected {result.exit_code=} (expected {assert_exit})\n"
                f"cmd: '{shlex.join(cmd)}'\n"
                f"output: {str(result.output)}"
            )
        return result

    return _run


def test_cli_no_args(run):
    result = run([])
    assert "Usage:" in result.output


def test_cli_help(run):
    result = run(["--help"])
    assert "Show this message and exit." in result.output


def test_cli_exception(run):

    cmd = ["--shell-completion", "and_now_for_something_completely_different"]

    with pytest.raises(RuntimeError) as exc:
        result = run(cmd)
    assert isinstance(exc.value, RuntimeError)

    # example of testing for expected exception
    result = run(cmd, assert_exception=RuntimeError)
    assert result.exception
    assert result.exc_info[0] == RuntimeError
    assert result.exception.args[0] == "cannot determine shell"

    with pytest.raises(AssertionError) as exc:
        result = run(cmd, assert_exception=ValueError)
    assert exc


def test_cli_exit(run):
    result = run(["--help"], assert_exit=None)
    assert result
    result = run(["--help"], assert_exit=0)
    assert result
    with pytest.raises(AssertionError):
        run(["--help"], assert_exit=-1)
