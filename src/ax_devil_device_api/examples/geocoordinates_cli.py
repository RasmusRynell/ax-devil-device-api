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
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.geocoordinates.get_location()
            
            if result.success:
                click.echo("Location Coordinates:")
                click.echo(f"  Latitude: {result.data.latitude}°")
                click.echo(f"  Longitude: {result.data.longitude}°")
                return 0
                
            return handle_result(ctx, result)
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
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.geocoordinates.set_location(latitude, longitude)
            
            if result.success:
                click.echo(click.style("Location coordinates updated successfully!", fg="green"))
                click.echo("\nNew Location:")
                click.echo(f"  Latitude: {latitude}°")
                click.echo(f"  Longitude: {longitude}°")
                return 0
                
            return handle_result(ctx, result)
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
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.geocoordinates.get_orientation()
            
            if result.success:
                click.echo("Camera Orientation:")
                if result.data.heading is not None:
                    click.echo(f"  Heading: {result.data.heading}°")
                if result.data.tilt is not None:
                    click.echo(f"  Tilt: {result.data.tilt}°")
                if result.data.roll is not None:
                    click.echo(f"  Roll: {result.data.roll}°")
                if result.data.installation_height is not None:
                    click.echo(f"  Installation Height: {result.data.installation_height}m")
                return 0
                
            return handle_result(ctx, result)
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
        click.echo(click.style("Error: At least one orientation parameter must be specified", fg="red"), err=True)
        return 1
        
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            orientation = GeoCoordinatesOrientation(
                heading=heading,
                tilt=tilt,
                roll=roll,
                installation_height=height
            )
            result = client.geocoordinates.set_orientation(orientation)
            
            if result.success:
                click.echo(click.style("Orientation coordinates updated successfully!", fg="green"))
                click.echo("\nUpdated Parameters:")
                if heading is not None:
                    click.echo(f"  Heading: {heading}°")
                if tilt is not None:
                    click.echo(f"  Tilt: {tilt}°")
                if roll is not None:
                    click.echo(f"  Roll: {roll}°")
                if height is not None:
                    click.echo(f"  Installation Height: {height}m")
                click.echo(click.style("\nNote: Changes will take effect after applying settings", fg="yellow"))
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

@orientation.command('apply')
@click.pass_context
def apply_orientation(ctx):
    """Apply pending orientation coordinate settings."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.geocoordinates.apply_settings()
            
            if result.success:
                click.echo(click.style("Orientation settings applied successfully!", fg="green"))
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

if __name__ == '__main__':
    cli() 