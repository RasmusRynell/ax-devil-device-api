#!/usr/bin/env python3
"""CLI for managing device operations."""

import click
from .cli_core import (
    create_client, create_client_no_auth, handle_error, get_client_args
)


def create_device_group():
    """Create and return the device command group."""
    @click.group()
    @click.pass_context
    def device(ctx):
        """Manage device operations."""
        pass

    @device.command('info')
    @click.pass_context
    def get_info(ctx):
        """Get device information including model, firmware, and capabilities."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                info = client.device.get_info()
                click.echo("Device Information:")
                for key, value in info.items():
                    click.echo(f"   {key}: {value}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)
        
    @device.command('info-detailed')
    @click.pass_context
    def get_info_detailed(ctx):
        """Get detailed device information including all parameters."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                info = client.device.get_info_detailed()
                click.echo("Detailed Device Information:")
                for key, value in info.items():
                    click.echo(f"   {key}: {value}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @device.command('info-no-auth')
    @click.pass_context
    def get_info_no_auth(ctx):
        """Get basic device information without authentication."""
        try:
            args = get_client_args(ctx.obj)
            with create_client_no_auth(
                device_ip=args["device_ip"],
                port=args.get("port"),
                protocol=args.get("protocol", "https"),
                no_verify_ssl=args.get("no_verify_ssl", False),
                debug=args.get("debug", False),
            ) as client:
                info = client.device.get_info_no_auth()
                click.echo("Basic Device Information (Unauthenticated):")
                for key, value in info.items():
                    click.echo(f"   {key}: {value}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @device.command('info-auth')
    @click.pass_context
    def get_info_auth(ctx):
        """Get basic device information with authentication."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                info = client.device.get_info_auth()
                click.echo("Basic Device Information (Authenticated):")
                for key, value in info.items():
                    click.echo(f"   {key}: {value}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @device.command('health')
    @click.pass_context
    def check_health(ctx):
        """Check if the device is responsive and healthy."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.device.check_health()
                
                if not result:
                    return handle_error(ctx, "Device is not healthy")
                    
                click.echo(click.style("Device is healthy!", fg="green"))
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @device.command('restart')
    @click.option('--force', is_flag=True, help='Force restart without confirmation')
    @click.pass_context
    def restart(ctx, force):
        """Restart the device (requires confirmation unless --force is used)."""
        try:
            if not force and not click.confirm('Are you sure you want to restart the device?'):
                click.echo('Restart cancelled.')
                return 0

            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.device.restart()

                if not result:
                    return handle_error(ctx, "Failed to restart device")
                    
                click.echo(click.style(
                    "Device restart initiated. The device will be unavailable for a few minutes.",
                    fg="yellow"
                ))
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return device
