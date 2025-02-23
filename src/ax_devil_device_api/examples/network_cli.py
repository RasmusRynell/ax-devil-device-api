#!/usr/bin/env python3
"""CLI for managing network operations."""

import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)


@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, ca_cert, debug):
    """Manage network operations."""
    ctx.ensure_object(dict)
    ctx.obj.update({
        'device_ip': device_ip,
        'username': username,
        'password': password,
        'port': port,
        'protocol': protocol,
        'no_verify_ssl': no_verify_ssl,
        'ca_cert': ca_cert,
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
            
            if not result.is_success:
                return handle_error(ctx, result.error)
                
            click.echo(f"Interface {interface} information:")
            for key, value in result.data.__dict__.items():
                click.echo(f"  {key}: {value}")
            return 0
    except Exception as e:
        return handle_error(ctx, e)


if __name__ == '__main__':
    cli() 