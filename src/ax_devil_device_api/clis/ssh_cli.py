"""CLI for managing SSH users on Axis devices."""

from __future__ import annotations

import click

from ..features.ssh import validate_comment
from .cli_core import create_client, get_client_args, handle_error


def create_ssh_group():
    """Create and return the ssh command group."""

    @click.group()
    @click.pass_context
    def ssh(ctx):
        """Manage SSH users on Axis devices."""

    @ssh.command()
    @click.argument("username")
    @click.option("--comment", "-c", help="Optional comment or full name for the user")
    @click.pass_context
    def add(ctx, username: str, comment: str | None = None):
        """Add a new SSH user."""
        try:
            validate_comment(comment)
            password = click.prompt(
                "Password", hide_input=True, confirmation_prompt=True
            )
            with create_client(**get_client_args(ctx.obj)) as client:
                client.ssh.add_user(username, password, comment)
                click.echo(f"Successfully added SSH user: {username}")
            return 0
        except Exception as e:  # noqa: BLE001 - CLI boundary
            handle_error(ctx, e)
            return 1

    @ssh.command()
    @click.pass_context
    def list(ctx):
        """List all SSH users."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.ssh.get_users()
            if len(result) == 0:
                click.echo("No SSH users found")
                return 0

            click.echo("SSH Users:")
            for user in result:
                comment_str = f" ({user.get('comment')})" if user.get("comment") else ""
                click.echo(f"- {user.get('username')}{comment_str}")
            return 0
        except Exception as e:  # noqa: BLE001 - CLI boundary
            handle_error(ctx, e)
            return 1

    @ssh.command()
    @click.argument("username")
    @click.pass_context
    def show(ctx, username: str):
        """Show details for a specific SSH user."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                user = client.ssh.get_user(username)

            comment_str = (
                f"\nComment: {user.get('comment')}" if user.get("comment") else ""
            )
            click.echo(f"Username: {user.get('username')}{comment_str}")
            return 0
        except Exception as e:  # noqa: BLE001 - CLI boundary
            handle_error(ctx, e)
            return 1

    @ssh.command()
    @click.argument("username")
    @click.option(
        "--password",
        "password_requested",
        is_flag=True,
        help="Prompt for a new password for the user",
    )
    @click.option("--comment", "-c", help="New comment or full name for the user")
    @click.pass_context
    def modify(
        ctx,
        username: str,
        password_requested: bool = False,
        comment: str | None = None,
    ):
        """Modify an existing SSH user."""
        try:
            validate_comment(comment)
            if not password_requested and comment is None:
                click.echo(
                    "Error: Must specify at least one of --password or --comment"
                )
                return 1

            password = (
                click.prompt("New password", hide_input=True, confirmation_prompt=True)
                if password_requested
                else None
            )
            with create_client(**get_client_args(ctx.obj)) as client:
                client.ssh.modify_user(username, password=password, comment=comment)
                click.echo(f"Successfully modified SSH user: {username}")
                return 0
        except Exception as e:  # noqa: BLE001 - CLI boundary
            handle_error(ctx, e)
            return 1

    @ssh.command()
    @click.argument("username")
    @click.confirmation_option(prompt="Are you sure you want to remove this SSH user?")
    @click.pass_context
    def remove(ctx, username: str):
        """Remove an SSH user."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                client.ssh.remove_user(username)
                click.echo(f"Successfully removed SSH user: {username}")
                return 0
        except Exception as e:  # noqa: BLE001 - CLI boundary
            handle_error(ctx, e)
            return 1

    return ssh
