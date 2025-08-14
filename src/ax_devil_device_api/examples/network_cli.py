#!/usr/bin/env python3
"""CLI for managing network operations."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args
)


def create_network_group():
    """Create and return the network command group."""
    @click.group()
    @click.pass_context
    def network(ctx):
        """Manage network operations."""
        pass

    @network.command('info')
    @click.option('--interface', default='eth0', help='Network interface name')
    @click.pass_context
    def network_info(ctx, interface):
        """Get network interface information."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.network.get_network_info()
                    
                for key, value in result.items():
                    click.echo(f"  {key}: {value}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return network 