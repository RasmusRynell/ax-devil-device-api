#!/usr/bin/env python3
"""CLI for managing camera geocoordinates and orientation settings."""

import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)
from ..features.geocoordinates import GeoCoordinatesOrientation

@click.group()
@common_options
@click.pass_context
def cli(ctx, camera_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage geographic coordinates for an Axis camera.
    
    When using HTTPS (default), the camera must have a valid SSL certificate.
    For cameras with self-signed certificates, use the --no-verify-ssl flag.
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

@cli.group()
def location():
    """Get or set camera location coordinates."""
    pass

@location.command('get')
@click.pass_context
def get_location(ctx):
    """Get current location coordinates."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        result = client.geocoordinates.get_location()
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.geocoordinates.get_location()
            
        if result.success:
            click.echo(f"Latitude: {result.data.latitude}")
            click.echo(f"Longitude: {result.data.longitude}")
            return 0
            
        return handle_error(ctx, result.error)
    except Exception as e:
        return handle_error(ctx, e)

@location.command('set')
@click.argument('latitude', type=float)
@click.argument('longitude', type=float)
@click.pass_context
def set_location(ctx, latitude, longitude):
    """Set camera location coordinates.
    
    LATITUDE and LONGITUDE should be specified in decimal degrees.
    The camera will validate the provided coordinates.
    """
    try:
        client = create_client(**get_client_args(ctx.obj))
        result = client.geocoordinates.set_location(latitude, longitude)
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.geocoordinates.set_location(latitude, longitude)
            
        if result.success:
            click.echo("Location coordinates updated successfully")
            return 0
            
        return handle_error(ctx, result.error)
    except Exception as e:
        return handle_error(ctx, e)

@cli.group()
def orientation():
    """Get or set camera orientation coordinates."""
    pass

@orientation.command('get')
@click.pass_context
def get_orientation(ctx):
    """Get current orientation coordinates."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        result = client.geocoordinates.get_orientation()
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.geocoordinates.get_orientation()
            
        if result.success:
            if result.data.heading is not None:
                click.echo(f"Heading: {result.data.heading}°")
            if result.data.tilt is not None:
                click.echo(f"Tilt: {result.data.tilt}°")
            if result.data.roll is not None:
                click.echo(f"Roll: {result.data.roll}°")
            if result.data.installation_height is not None:
                click.echo(f"Installation Height: {result.data.installation_height}m")
            return 0
            
        return handle_error(ctx, result.error)
    except Exception as e:
        return handle_error(ctx, e)

@orientation.command('set')
@click.option('--heading', type=float, help='Camera heading in degrees')
@click.option('--tilt', type=float, help='Camera tilt angle in degrees')
@click.option('--roll', type=float, help='Camera roll angle in degrees')
@click.option('--height', type=float, help='Installation height in meters')
@click.pass_context
def set_orientation(ctx, heading, tilt, roll, height):
    """Set camera orientation coordinates.
    
    All parameters are optional. Only specified parameters will be updated.
    The camera will validate the provided values.
    """
    if not any(x is not None for x in (heading, tilt, roll, height)):
        click.echo("Error: At least one orientation parameter must be specified", err=True)
        return 1
        
    try:
        client = create_client(**get_client_args(ctx.obj))
        orientation = GeoCoordinatesOrientation(
            heading=heading,
            tilt=tilt,
            roll=roll,
            installation_height=height
        )
        result = client.geocoordinates.set_orientation(orientation)
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.geocoordinates.set_orientation(orientation)
            
        if result.success:
            click.echo("Orientation coordinates updated successfully")
            return 0
            
        return handle_error(ctx, result.error)
    except Exception as e:
        return handle_error(ctx, e)

@orientation.command('apply')
@click.pass_context
def apply_orientation(ctx):
    """Apply pending orientation coordinate settings."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        result = client.geocoordinates.apply_settings()
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.geocoordinates.apply_settings()
            
        if result.success:
            click.echo("Settings applied successfully")
            return 0
            
        return handle_error(ctx, result.error)
    except Exception as e:
        return handle_error(ctx, e)

if __name__ == '__main__':
    cli() 