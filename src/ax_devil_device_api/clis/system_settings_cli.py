#!/usr/bin/env python3
"""CLI for managing system settings (users, factory default, logs, firmware)."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args
)


def create_system_settings_group():
    """Create and return the system-settings command group."""

    @click.group()
    @click.pass_context
    def system_settings(ctx):
        """Manage system settings (users, factory default, logs, firmware)."""
        pass

    # --- User management ---

    @system_settings.command("list-users")
    @click.pass_context
    def list_users(ctx):
        """List user accounts and group memberships."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                users = client.system_settings.get_users()
                for group, members in users.items():
                    click.echo(f"  {group}: {members}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @system_settings.command("add-user")
    @click.option("--user", required=True, help="Username (1-14 chars, a-z A-Z 0-9).")
    @click.option("--pwd", required=True, help="Password for the account.")
    @click.option("--grp", default="users", help="Primary group (default: users).")
    @click.option("--sgrp", default="viewer", help="Secondary groups / role, e.g. admin:operator:viewer:ptz.")
    @click.option("--comment", default="", help="Optional description.")
    @click.option("--strict-pwd", is_flag=True, help="Enforce VAPIX password standards.")
    @click.pass_context
    def add_user(ctx, user, pwd, grp, sgrp, comment, strict_pwd):
        """Create a new user account."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.system_settings.add_user(
                    user=user, pwd=pwd, grp=grp, sgrp=sgrp,
                    comment=comment, strict_pwd=strict_pwd,
                )
                click.echo(result)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @system_settings.command("update-user")
    @click.option("--user", required=True, help="Username to update.")
    @click.option("--pwd", default=None, help="New password.")
    @click.option("--sgrp", default=None, help="New secondary groups / role.")
    @click.option("--comment", default=None, help="New description.")
    @click.pass_context
    def update_user(ctx, user, pwd, sgrp, comment):
        """Update an existing user account."""
        try:
            if pwd is None and sgrp is None and comment is None:
                click.echo("Nothing to update. Provide at least --pwd, --sgrp, or --comment.", err=True)
                return 1
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.system_settings.update_user(
                    user, pwd=pwd, sgrp=sgrp, comment=comment,
                )
                click.echo(result)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @system_settings.command("remove-user")
    @click.option("--user", required=True, help="Username to remove.")
    @click.pass_context
    def remove_user(ctx, user):
        """Remove a user account."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.system_settings.remove_user(user)
                click.echo(result)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    # --- Factory default ---

    @system_settings.command("factory-default")
    @click.option('--force', is_flag=True, help='Skip confirmation prompt')
    @click.pass_context
    def factory_default(ctx, force):
        """Soft factory default (preserves network settings). Device will restart."""
        try:
            if not force and not click.confirm('Are you sure you want to factory default the device?'):
                click.echo('Factory default cancelled.')
                return 0
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.system_settings.factory_default()
                click.echo(result)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @system_settings.command("hard-factory-default")
    @click.option('--force', is_flag=True, help='Skip confirmation prompt')
    @click.pass_context
    def hard_factory_default(ctx, force):
        """Hard factory default (resets everything including IP). Device will restart."""
        try:
            if not force and not click.confirm(
                'WARNING: This will reset ALL settings including network/IP. '
                'The device may become unreachable. Continue?'
            ):
                click.echo('Hard factory default cancelled.')
                return 0
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.system_settings.hard_factory_default()
                click.echo(result)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    # --- Firmware upgrade ---

    @system_settings.command("firmware-upgrade")
    @click.argument("firmware_path", type=click.Path(exists=True, dir_okay=False, readable=True))
    @click.option("--type", "upgrade_type", default="normal",
                  type=click.Choice(["normal", "factorydefault"]),
                  help="Upgrade type (default: normal).")
    @click.option('--force', is_flag=True, help='Skip confirmation prompt')
    @click.pass_context
    def firmware_upgrade(ctx, firmware_path, upgrade_type, force):
        """Upload and install a firmware file. Device will restart."""
        try:
            if not force and not click.confirm('Are you sure you want to upgrade the firmware? The device will restart.'):
                click.echo('Firmware upgrade cancelled.')
                return 0
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.system_settings.firmware_upgrade(firmware_path, upgrade_type)
                click.echo(result)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    # --- Logs ---

    @system_settings.command("system-log")
    @click.option("--filter", "text_filter", default=None, help="Filter log entries by text.")
    @click.pass_context
    def system_log(ctx, text_filter):
        """Get system log contents."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                log = client.system_settings.get_system_log(text_filter=text_filter)
                click.echo(log)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @system_settings.command("access-log")
    @click.pass_context
    def access_log(ctx):
        """Get access log contents."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                log = client.system_settings.get_access_log()
                click.echo(log)
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    return system_settings
