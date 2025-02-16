#!/usr/bin/env python3
import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)
from ..features.media import MediaConfig

@click.group()
@common_options
@click.pass_context
def cli(ctx, camera_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage media operations for an Axis camera.
    
    Provides functionality for capturing snapshots and configuring media parameters.
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

@cli.command('snapshot')
@click.option('--resolution', help='Image resolution (WxH format, e.g., "1920x1080")')
@click.option('--compression', type=int, help='JPEG compression level (1-100)')
@click.option('--camera', type=int, help='Camera head identifier for multi-sensor devices')
@click.option('--rotation', type=int, help='Image rotation in degrees (0, 90, 180, or 270)')
@click.option('--output', '-o', type=click.Path(dir_okay=False), default="snapshot.jpg",
              help='Output file path')
@click.pass_context
def snapshot(ctx, resolution, compression, camera, rotation, output):
    """Capture JPEG snapshot from camera."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        
        # Create config only if any parameters are specified
        config = None
        if any(x is not None for x in (resolution, compression, camera, rotation)):
            config = MediaConfig(
                resolution=resolution,
                compression=compression,
                camera_head=camera,
                rotation=rotation
            )
        
        result = client.media.get_snapshot(config)
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.media.get_snapshot(config)
            
        if result.success:
            try:
                with open(output, 'wb') as f:
                    f.write(result.data)
                click.echo(f"Snapshot saved to {output}")
                return 0
            except IOError as e:
                return handle_error(ctx, f"Failed to save snapshot: {e}")
                
        return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)
