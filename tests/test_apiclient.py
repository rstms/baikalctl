# cli tests

import json
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
        parse_json = kwargs.pop("parse_json", True)
        env.update(kwargs.pop("env", {}))
        env.update({"BAIKAL_API": "http://localhost:8000"})
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
        if parse_json:
            return json.loads(result.output)
        return result

    return _run


def test_api_client(run):

    result = run(["mkuser", "test1@example.org", "test1 user", "testpassword"])
    assert result == dict(added_user="test1@example.org")

    result = run(["users"])
    assert isinstance(result, dict)
    assert "test1@example.org" in result.keys()

    result = run(["rmuser", "test1@example.org"])
    assert isinstance(result, dict)
    assert "test1@example.org" not in result.keys()

    result = run(["mkuser", "test1@example.org", "test1 user", "testpassword"])
    assert result == dict(added_user="test1@example.org")

    result = run(["mkbook", "test1@example.org", "testbook1", "testbook one description"])
    assert result == dict(added_address_book="testbook1")

    result = run(["books", "test1@example.org"])
    assert isinstance(result, dict)
    assert "testbook1" in result.keys()

    result = run(["rmbook", "test1@example.org", "testbook1"])
    assert result == dict(deleted_address_book="testbook1")
