"""Deterministic CLI contracts for SSH password handling."""

from contextlib import contextmanager
from unittest.mock import Mock

from click.testing import CliRunner

from src.ax_devil_device_api.clis import ssh_cli


class FakeClient:
    """Minimal context manager used to isolate the CLI from transport code."""

    def __init__(self) -> None:
        self.ssh = Mock()
        self.ssh.add_user.return_value = None
        self.ssh.modify_user.return_value = None

    def __enter__(self):
        """Return the fake client."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Close the fake client context."""


def fake_client_factory(client):
    """Return a patched client factory for one CLI invocation."""

    @contextmanager
    def create_client(**_kwargs):
        yield client

    return create_client


def test_add_prompts_for_hidden_confirmed_password_without_leaking_it(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(ssh_cli, "create_client", fake_client_factory(client))
    result = CliRunner().invoke(
        ssh_cli.create_ssh_group(),
        ["add", "new-user", "--comment", "Service account"],
        input="super-secret\nsuper-secret\n",
        obj={},
    )

    assert result.exit_code == 0
    assert "super-secret" not in result.output
    client.ssh.add_user.assert_called_once_with(
        "new-user", "super-secret", "Service account"
    )


def test_modify_password_flag_prompts_without_leaking_password(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(ssh_cli, "create_client", fake_client_factory(client))
    result = CliRunner().invoke(
        ssh_cli.create_ssh_group(),
        ["modify", "new-user", "--password", "--comment", "Updated"],
        input="new-secret\nnew-secret\n",
        obj={},
    )

    assert result.exit_code == 0
    assert "new-secret" not in result.output
    client.ssh.modify_user.assert_called_once_with(
        "new-user", password="new-secret", comment="Updated"
    )


def test_add_rejects_explicit_empty_comment_before_password_prompt(monkeypatch):
    client = FakeClient()
    create_client = Mock(side_effect=fake_client_factory(client))
    monkeypatch.setattr(ssh_cli, "create_client", create_client)
    result = CliRunner().invoke(
        ssh_cli.create_ssh_group(),
        ["add", "new-user", "--comment", ""],
        obj={},
    )

    assert "Comment must not be empty" in result.output
    assert "Password" not in result.output
    create_client.assert_not_called()


def test_modify_rejects_explicit_empty_comment_before_client_call(monkeypatch):
    client = FakeClient()
    create_client = Mock(side_effect=fake_client_factory(client))
    monkeypatch.setattr(ssh_cli, "create_client", create_client)
    result = CliRunner().invoke(
        ssh_cli.create_ssh_group(),
        ["modify", "new-user", "--comment", ""],
        obj={},
    )

    assert "Comment must not be empty" in result.output
    create_client.assert_not_called()
    client.ssh.modify_user.assert_not_called()


def test_ssh_cli_does_not_expose_password_argument():
    result = CliRunner().invoke(ssh_cli.create_ssh_group(), ["add", "--help"])

    assert result.exit_code == 0
    assert "PASSWORD" not in result.output
    assert "--comment" in result.output
