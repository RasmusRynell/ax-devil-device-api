#!/usr/bin/env python3
"""CLI for managing media operations."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args
)

def create_media_group():
    """Create and return the media command group."""
    @click.group()
    @click.pass_context
    def media(ctx):
        """Manage media operations."""
        pass

    @media.command('snapshot')
    @click.option('--resolution', help='Image resolution (WxH format, e.g., "1920x1080")', default="1920x1080")
    @click.option('--compression', type=int, help='JPEG compression level (1-100)', default=0)
    @click.option('--device', type=int, help='Camera head identifier for multi-sensor devices', default=0)
    @click.option('--output', '-o', type=click.Path(dir_okay=False), default="snapshot.jpg",
                  help='Output file path')
    @click.pass_context
    def snapshot(ctx, resolution, compression, device, output):
        """Capture JPEG snapshot from device."""
        try:
            
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.media.get_snapshot(resolution, compression, device)

                try:
                    with open(output, 'wb') as f:
                        f.write(result)

                    click.echo(click.style(f"Snapshot saved to {output}", fg="green"))
                    return 0
                except IOError as e:
                    return handle_error(ctx, f"Failed to save snapshot: {e}")
        except Exception as e:
            return handle_error(ctx, e)
    
    return media
