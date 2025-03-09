#!/usr/bin/env python3
import click
from typing import Optional
from .cli_core import create_client, common_options, get_client_args

@click.group()
@common_options
@click.pass_context
def cli(ctx, **options):
    """Manage SSH users on Axis devices."""
    ctx.obj = options

@cli.command()
@click.argument('username')
@click.argument('password')
@click.option('--comment', '-c', help='Optional comment or full name for the user')
@click.pass_context
def add(ctx, username: str, password: str, comment: Optional[str] = None):
    """Add a new SSH user."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.ssh.add_user(username, password, comment)
        click.echo(f"Successfully added SSH user: {result.data.username}")
        return 0

@cli.command()
@click.pass_context
def list(ctx):
    """List all SSH users."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.ssh.get_users()
        
        if len(result) == 0:
            click.echo("No SSH users found")
            return 0
            
        click.echo("SSH Users:")
        for user in result:
            comment_str = f" ({user.comment})" if user.comment else ""
            click.echo(f"- {user.username}{comment_str}")
        return 0

@cli.command()
@click.argument('username')
@click.pass_context
def show(ctx, username: str):
    """Show details for a specific SSH user."""
    with create_client(**get_client_args(ctx.obj)) as client:
        user = client.ssh.get_user(username)

        comment_str = f"\nComment: {user.comment}" if user.comment else ""
        click.echo(f"Username: {user.username}{comment_str}")
        return 0

@cli.command()
@click.argument('username')
@click.option('--password', '-p', help='New password for the user')
@click.option('--comment', '-c', help='New comment or full name for the user')
@click.pass_context
def modify(ctx, username: str, password: Optional[str] = None, 
          comment: Optional[str] = None):
    """Modify an existing SSH user."""
    if not password and not comment:
        click.echo("Error: Must specify at least one of --password or --comment")
        return 1
        
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.ssh.modify_user(username, password=password, comment=comment)
        click.echo(f"Successfully modified SSH user: {username}")
        return 0

@cli.command()
@click.argument('username')
@click.confirmation_option(prompt='Are you sure you want to remove this SSH user?')
@click.pass_context
def remove(ctx, username: str):
    """Remove an SSH user."""
    with create_client(**get_client_args(ctx.obj)) as client:
        client.ssh.remove_user(username)
        click.echo(f"Successfully removed SSH user: {username}")
        return 0

if __name__ == '__main__':
    cli() 