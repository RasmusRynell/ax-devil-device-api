#!/usr/bin/env python3
import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options, format_json
)

@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, ca_cert, debug):
    """Manage device debugging operations."""
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

@cli.command()
@click.argument('output_file', type=click.Path(dir_okay=False, writable=True))
@click.pass_context
def download_server_report(ctx, output_file):
    """Download the server report from the device to OUTPUT_FILE."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.device_debug.download_server_report()
        if not result.is_success:
            return handle_error(ctx, result.error)
        try:
            with open(output_file, 'wb') as f:
                f.write(result.data)
            click.echo(f"Server report saved to {output_file}")
        except IOError as e:
            click.echo(f"Error saving file: {str(e)}", err=True)
            return 1

@cli.command()
@click.argument('output_file', type=click.Path(dir_okay=False, writable=True))
@click.pass_context
def download_crash_report(ctx, output_file):
    """Download the crash report from the device to OUTPUT_FILE."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.device_debug.download_crash_report()
        if not result.is_success:
            return handle_error(ctx, result.error)
        try:
            with open(output_file, 'wb') as f:
                f.write(result.data)
            click.echo(f"Crash report saved to {output_file}")
        except IOError as e:
            click.echo(f"Error saving file: {str(e)}", err=True)
            return 1

@cli.command()
@click.argument('output_file', type=click.Path(dir_okay=False, writable=True))
@click.option('--duration', default=30, help='Duration in seconds for network trace')
@click.option('--interface', default='', help='Interface(s) for network trace')
@click.pass_context
def download_network_trace(ctx, output_file, duration, interface):
    """Download a network trace from the device to OUTPUT_FILE."""
    with create_client(**get_client_args(ctx.obj)) as client:
        iface = interface if interface else None
        result = client.device_debug.download_network_trace(duration=duration, interface=iface)
        if not result.is_success:
            return handle_error(ctx, result.error)
        try:
            with open(output_file, 'wb') as f:
                f.write(result.data)
            click.echo(f"Network trace saved to {output_file}")
        except IOError as e:
            click.echo(f"Error saving file: {str(e)}", err=True)
            return 1

@cli.command()
@click.argument('target')
@click.pass_context
def ping_test(ctx, target):
    """Perform a ping test from the device to the target IP or hostname."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.device_debug.ping_test(target)
        if not result.is_success:
            return handle_error(ctx, result.error)
        click.echo(result.data)

@cli.command()
@click.argument('address')
@click.argument('port', type=int)
@click.pass_context
def port_open_test(ctx, address, port):
    """Check if a port is open on a target address from the device."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.device_debug.port_open_test(address, port)
        if not result.is_success:
            return handle_error(ctx, result.error)
        click.echo(result.data)

@cli.command()
@click.argument('output_file', type=click.Path(dir_okay=False, writable=True))
@click.pass_context
def collect_core_dump(ctx, output_file):
    """Collect a core dump from the device to OUTPUT_FILE."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.device_debug.collect_core_dump()
        if not result.is_success:
            return handle_error(ctx, result.error)
        try:
            with open(output_file, 'wb') as f:
                f.write(result.data)
            click.echo(f"Core dump saved to {output_file}")
        except IOError as e:
            click.echo(f"Error saving file: {str(e)}", err=True)
            return 1

if __name__ == '__main__':
    cli() 