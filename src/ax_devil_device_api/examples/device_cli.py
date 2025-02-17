#!/usr/bin/env python3
"""CLI for managing device operations."""

import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)


@click.group()
@common_options
@click.pass_context
def cli(ctx, camera_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage device operations for an Axis camera.

    When using HTTPS (default), the camera must have a valid SSL certificate. For cameras with
    self-signed certificates, use the --no-verify-ssl flag to disable certificate verification.
    """
    ctx.ensure_object(dict)
    ctx.obj.update({
        'camera_ip': camera_ip,
        'username': username,
        'password': password,
        'port': port,
        'protocol': protocol,
        'no_verify_ssl': no_verify_ssl,
        'debug': debug
    })


@cli.command('info')
@click.pass_context
def get_info(ctx):
    """Get device information including model, firmware, and capabilities."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device.get_info()
            
            if result.success:
                info = result.data
                click.echo("Device Information:")
                for key, value in info.__dict__.items():
                    click.echo(f"{key}: {value}")
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


@cli.command('health')
@click.pass_context
def check_health(ctx):
    """Check if the camera is responsive and healthy."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device.check_health()
            
            if result.success:
                click.echo(click.style("Device is healthy!", fg="green"))
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


@cli.command('restart')
@click.option('--force', is_flag=True, help='Force restart without confirmation')
@click.pass_context
def restart(ctx, force):
    """Restart the camera (requires confirmation unless --force is used)."""
    try:
        if not force and not click.confirm('Are you sure you want to restart the camera?'):
            click.echo('Restart cancelled.')
            return 0

        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device.restart()

            if result.success:
                click.echo(click.style(
                    "Camera restart initiated. The device will be unavailable for a few minutes.",
                    fg="yellow"
                ))
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


if __name__ == '__main__':
    cli()
