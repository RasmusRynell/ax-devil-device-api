#!/usr/bin/env python3
"""CLI for managing media operations."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args,
    common_options
)

@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage media operations."""
    ctx.ensure_object(dict)
    ctx.obj.update({
        'device_ip': device_ip,
        'username': username,
        'password': password,
        'port': port,
        'protocol': protocol,
        'no_verify_ssl': no_verify_ssl,
        'debug': debug
    })


@cli.command('snapshot')
@click.option('--resolution', help='Image resolution (WxH format, e.g., "1920x1080")', default="1920x1080")
@click.option('--compression', type=int, help='JPEG compression level (1-100)', default=0)
@click.option('--device', type=int, help='Camera head identifier for multi-sensor devices', default=0)
@click.option('--rotation', type=int, help='Image rotation in degrees (0, 90, 180, or 270)', default=0)
@click.option('--output', '-o', type=click.Path(dir_okay=False), default="snapshot.jpg",
              help='Output file path')
@click.pass_context
def snapshot(ctx, resolution, compression, device, rotation, output):
    """Capture JPEG snapshot from device."""
    try:
        
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.media.get_snapshot(resolution, compression, device, rotation)

            try:
                with open(output, 'wb') as f:
                    f.write(result)

                click.echo(click.style(f"Snapshot saved to {output}", fg="green"))
                return 0
            except IOError as e:
                return handle_error(ctx, f"Failed to save snapshot: {e}")
    except Exception as e:
        return handle_error(ctx, e)


if __name__ == '__main__':
    cli()
