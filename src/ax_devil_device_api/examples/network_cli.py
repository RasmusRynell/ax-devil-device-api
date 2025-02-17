#!/usr/bin/env python3
import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)


@click.group()
@common_options
@click.pass_context
def cli(ctx, camera_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage network operations for an Axis camera.

    When using HTTPS (default), the camera must have a valid SSL certificate. For cameras with
    self-signed certificates, use the --no-verify-ssl flag to disable certificate verification.
    """
    # Store common parameters in the context
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
@click.option('--interface', default='eth0', help='Network interface name')
@click.pass_context
def network_info(ctx, interface):
    """Get network interface information."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.network.get_network_info(interface)
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e) 