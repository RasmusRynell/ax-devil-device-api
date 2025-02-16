#!/usr/bin/env python3
"""CLI interface for MQTT client operations."""

import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)
from ..features.mqtt_client import BrokerConfig, MqttStatus
from ..core.types import FeatureResponse

@click.group()
@common_options
@click.pass_context
def cli(ctx, camera_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage MQTT client settings for an Axis camera.
    
    When using HTTPS (default), the camera must have a valid SSL certificate. For cameras with
    self-signed certificates, use the --no-verify-ssl flag to disable certificate verification.
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

@cli.command('activate')
@click.pass_context
def activate(ctx):
    """Activate MQTT client."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        result = client.mqtt_client.activate()
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.mqtt_client.activate()
            
        return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

@cli.command('deactivate')
@click.pass_context
def deactivate(ctx):
    """Deactivate MQTT client."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        result = client.mqtt_client.deactivate()
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.mqtt_client.deactivate()
            
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
        client = create_client(**get_client_args(ctx.obj))
        
        config = BrokerConfig(
            host=broker_host,
            port=broker_port,
            username=broker_username,
            password=broker_password,
            use_tls=use_tls,
            keep_alive_interval=keep_alive
        )
        
        result = client.mqtt_client.configure(config)
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.mqtt_client.configure(config)
            
        return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

@cli.command('status')
@click.pass_context
def status(ctx):
    """Get MQTT client status."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        result = client.mqtt_client.get_status()
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.mqtt_client.get_status()
            
        if result.success:
            # Convert MqttStatus to dict for JSON serialization
            data = result.data.to_dict()
            return handle_result(ctx, FeatureResponse.ok(data))
        return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

if __name__ == '__main__':
    cli() 