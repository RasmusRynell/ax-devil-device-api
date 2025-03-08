#!/usr/bin/env python3
"""CLI for managing device geocoordinates and orientation settings."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args,
    common_options
)

@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage geographic coordinates."""
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

@cli.group()
def location():
    """Get or set device location coordinates."""
    pass

@location.command('get')
@click.pass_context
def get_location(ctx):
    """Get current location coordinates."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            location = client.geocoordinates.get_location()
            
            click.echo("Location Coordinates:")
            click.echo(f"  Latitude: {location.get('latitude')}°")
            click.echo(f"  Longitude: {location.get('longitude')}°")
            return 0
    except Exception as e:
        return handle_error(ctx, e)

@location.command('set')
@click.argument('latitude', type=float)
@click.argument('longitude', type=float)
@click.pass_context
def set_location(ctx, latitude, longitude):
    """Set device location coordinates."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            client.geocoordinates.set_location(latitude, longitude)
            
            click.echo(click.style("Location coordinates updated successfully!", fg="green"))
            click.echo(click.style("Note: you can see the current location coordinates with the 'get' command", fg="yellow"))
            click.echo(click.style("Note: Changes will take effect after applying settings with the 'apply' command", fg="yellow"))
            return 0
    except Exception as e:
        return handle_error(ctx, e)

@cli.group()
def orientation():
    """Get or set device orientation coordinates."""
    pass

@orientation.command('get')
@click.pass_context
def get_orientation(ctx):
    """Get current orientation coordinates."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            orientation = client.geocoordinates.get_orientation()
            
            click.echo("Device Orientation:")
            click.echo(f"  Heading: {orientation.get('heading')}°")
            click.echo(f"  Tilt: {orientation.get('tilt')}°")
            click.echo(f"  Roll: {orientation.get('roll')}°")
            click.echo(f"  Installation Height: {orientation.get('installation_height')}m")
            return 0
    except Exception as e:
        return handle_error(ctx, e)

@orientation.command('set')
@click.option('--heading', type=float, help='Device heading in degrees')
@click.option('--tilt', type=float, help='Device tilt angle in degrees')
@click.option('--roll', type=float, help='Device roll angle in degrees')
@click.option('--height', type=float, help='Installation height in meters')
@click.pass_context
def set_orientation(ctx, heading, tilt, roll, height):
    """Set device orientation coordinates."""
    if not any(x is not None for x in (heading, tilt, roll, height)):
        click.echo(click.style("Error: At least one orientation parameter must be specified", fg="red"), err=True)
        return 1
        
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            orientation = {
                "heading": heading,
                "tilt": tilt,
                "roll": roll,
                "installation_height": height
            }
            client.geocoordinates.set_orientation(orientation)
            
            click.echo(click.style("Orientation coordinates updated successfully!", fg="green"))
            click.echo(click.style("Note: you can see the current orientation coordinates with the 'get' command", fg="yellow"))
            click.echo(click.style("Note: Changes will take effect after applying settings with the 'apply' command", fg="yellow"))
            return 0
    except Exception as e:
        return handle_error(ctx, e)

@orientation.command('apply')
@click.pass_context
def apply_orientation(ctx):
    """Apply pending orientation coordinate settings."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            client.geocoordinates.apply_settings()
            
            click.echo(click.style("Orientation settings applied successfully!", fg="green"))

            click.echo("\nThe new settings are:")

            orientation = client.geocoordinates.get_orientation()
            click.echo("Device Orientation:")
            click.echo(f"  Heading: {orientation.get('heading')}°")
            click.echo(f"  Tilt: {orientation.get('tilt')}°")
            click.echo(f"  Roll: {orientation.get('roll')}°")
            click.echo(f"  Installation Height: {orientation.get('installation_height')}m")

            location = client.geocoordinates.get_location()
            click.echo("Location Coordinates:")
            click.echo(f"  Latitude: {location.get('latitude')}°")
            click.echo(f"  Longitude: {location.get('longitude')}°")

            return 0
    except Exception as e:
        return handle_error(ctx, e)

if __name__ == '__main__':
    cli() 