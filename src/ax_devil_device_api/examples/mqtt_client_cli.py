#!/usr/bin/env python3
"""CLI for managing MQTT client operations."""

import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)
from ..features.mqtt_client import BrokerConfig, MqttStatus


@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, ca_cert, debug):
    """Manage MQTT client settings."""
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


@cli.command('activate')
@click.pass_context
def activate(ctx):
    """Activate MQTT client."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.mqtt_client.activate()
            
            if result.success:
                click.echo(click.style("MQTT client activated successfully!", fg="green"))
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


@cli.command('deactivate')
@click.pass_context
def deactivate(ctx):
    """Deactivate MQTT client."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.mqtt_client.deactivate()
            
            if result.success:
                click.echo(click.style("MQTT client deactivated successfully!", fg="yellow"))
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


@cli.command('configure')
@click.option('--broker-host', required=True, help='Broker hostname or IP address')
@click.option('--broker-port', type=int, default=1883, help='Broker port number')
@click.option('--broker-username', help='Broker authentication username')
@click.option('--broker-password', help='Broker authentication password')
@click.option('--keep-alive', type=int, default=60, help='Keep alive interval in seconds')
@click.option('--use-tls', is_flag=True, help='Use TLS encryption')
@click.pass_context
def configure(ctx, broker_host, broker_port, broker_username, broker_password,
             keep_alive, use_tls):
    """Configure MQTT broker settings."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            config = BrokerConfig(
                host=broker_host,
                port=broker_port,
                username=broker_username,
                password=broker_password,
                use_tls=use_tls,
                keep_alive_interval=keep_alive
            )
            
            result = client.mqtt_client.configure(config)
            
            if result.success:
                click.echo(click.style("MQTT broker configuration updated successfully!", fg="green"))
                click.echo("\nBroker Configuration:")
                click.echo(f"  Host: {broker_host}")
                click.echo(f"  Port: {broker_port}")
                click.echo(f"  TLS Enabled: {use_tls}")
                click.echo(f"  Keep Alive: {keep_alive}s")
                if broker_username:
                    click.echo("  Authentication: Enabled")
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


@cli.command('status')
@click.pass_context
def status(ctx):
    """Get MQTT client status."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.mqtt_client.get_status()
            
            if result.success:
                status = result.data
                click.echo("MQTT Client Status:")
                click.echo(f"  State: {click.style(status.state, fg='green' if status.state == 'CONNECTED' else 'yellow')}")
                click.echo(f"  Status: {click.style(status.status, fg='green' if status.status == 'CONNECTED' else 'yellow')}")
                click.echo(f"  Host: {status.config.host}")
                click.echo(f"  Port: {status.config.port}")
                click.echo(f"  TLS Enabled: {status.config.use_tls}")
                click.echo(f"  Keep Alive: {status.config.keep_alive_interval}s")
                click.echo(f"  Client ID: {status.config.client_id}")
                click.echo(f"  Clean Session: {status.config.clean_session}")
                click.echo(f"  Auto Reconnect: {status.config.auto_reconnect}")
                click.echo(f"  Device Topic Prefix: {status.config.device_topic_prefix}")
                click.echo(f"  Error: {status.error}")
                click.echo(f"  Connected To: {status.connected_to}")
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


if __name__ == '__main__':
    cli() 