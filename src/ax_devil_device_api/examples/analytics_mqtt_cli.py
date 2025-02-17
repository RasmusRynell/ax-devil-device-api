#!/usr/bin/env python3
"""CLI for managing analytics MQTT publishers."""

import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)
from ..features.analytics_mqtt import PublisherConfig

@click.group()
@common_options
@click.pass_context
def cli(ctx, camera_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage analytics MQTT publishers for an Axis camera.
    
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

@cli.command('sources')
@click.pass_context
def list_sources(ctx):
    """List available analytics data sources."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.analytics_mqtt.get_data_sources()
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

@cli.command('list')
@click.pass_context
def list_publishers(ctx):
    """List configured publishers."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.analytics_mqtt.list_publishers()
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

@cli.command('create')
@click.argument('id')
@click.argument('source')
@click.argument('topic')
@click.option('--qos', type=int, default=0, help='QoS level (0-2)')
@click.option('--retain', is_flag=True, help='Retain messages')
@click.option('--use-topic-prefix', is_flag=True, help='Use device topic prefix')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def create_publisher(ctx, id, source, topic, qos, retain, use_topic_prefix, force):
    """Create a new publisher.
    
    Arguments:
        ID: Unique identifier for the publisher
        SOURCE: Analytics data source key
        TOPIC: MQTT topic to publish to
    """
    try:
        if not force:
            msg = f"Create publisher '{id}' for data source '{source}' publishing to '{topic}'?"
            if not click.confirm(msg):
                click.echo('Operation cancelled.')
                return 0

        with create_client(**get_client_args(ctx.obj)) as client:
            config = PublisherConfig(
                id=id,
                data_source_key=source,
                mqtt_topic=topic,
                qos=qos,
                retain=retain,
                use_topic_prefix=use_topic_prefix
            )
            result = client.analytics_mqtt.create_publisher(config)
            
            if result.success:
                click.echo(click.style("Publisher created successfully!", fg="green"))
                publisher = result.data
                click.echo("\nPublisher details:")
                click.echo(f"  ID: {publisher.id}")
                click.echo(f"  Data Source: {publisher.data_source_key}")
                click.echo(f"  Topic: {publisher.mqtt_topic}")
                click.echo(f"  QoS: {publisher.qos}")
                click.echo(f"  Retain: {publisher.retain}")
                click.echo(f"  Use Topic Prefix: {publisher.use_topic_prefix}")
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

@cli.command('remove')
@click.argument('id')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def remove_publisher(ctx, id, force):
    """Remove a publisher.
    
    Arguments:
        ID: Publisher ID to remove
    """
    try:
        if not force:
            msg = f"Are you sure you want to remove publisher '{id}'?"
            if not click.confirm(msg):
                click.echo('Operation cancelled.')
                return 0

        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.analytics_mqtt.remove_publisher(id)
            
            if result.success:
                click.echo(click.style(f"Publisher '{id}' removed successfully!", fg="green"))
                return 0
                
            return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)

if __name__ == '__main__':
    cli()