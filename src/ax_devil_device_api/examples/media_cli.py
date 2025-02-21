#!/usr/bin/env python3
"""CLI for managing media operations."""

import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)
from ..features.media import MediaConfig


@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, ca_cert, debug):
    """Manage media operations."""
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


@cli.command('snapshot')
@click.option('--resolution', help='Image resolution (WxH format, e.g., "1920x1080")')
@click.option('--compression', type=int, help='JPEG compression level (1-100)')
@click.option('--device', type=int, help='Camera head identifier for multi-sensor devices')
@click.option('--rotation', type=int, help='Image rotation in degrees (0, 90, 180, or 270)')
@click.option('--output', '-o', type=click.Path(dir_okay=False), default="snapshot.jpg",
              help='Output file path')
@click.pass_context
def snapshot(ctx, resolution, compression, device, rotation, output):
    """Capture JPEG snapshot from device."""
    try:
        config = None
        if any(x is not None for x in (resolution, compression, device, rotation)):
            config = MediaConfig(
                resolution=resolution,
                compression=compression,
                device_head=device,
                rotation=rotation
            )
        
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.media.get_snapshot(config)
            
            if result.success:
                try:
                    with open(output, 'wb') as f:
                        f.write(result.data)
                    click.echo(click.style(f"Snapshot saved to {output}", fg="green"))
                    return 0
                except IOError as e:
                    return handle_error(ctx, f"Failed to save snapshot: {e}")
                    
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


if __name__ == '__main__':
    cli()
