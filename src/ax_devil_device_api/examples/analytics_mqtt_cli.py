#!/usr/bin/env python3
"""CLI for managing analytics MQTT publishers."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args,
    common_options
)

@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage analytics MQTT publishers."""
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

@cli.command('sources')
@click.pass_context
def list_sources(ctx):
    """List available analytics data sources."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.analytics_mqtt.get_data_sources()

            if not result:
                click.echo("No analytics data sources available")
                return 0
                    
            click.echo("Available Analytics Data Sources:")
            for source in result:
                click.echo(f"  - {source.key}")
            return 0
    except Exception as e:
        return handle_error(ctx, e)

@cli.command('list')
@click.pass_context
def list_publishers(ctx):
    """List configured publishers."""
    try:
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.analytics_mqtt.list_publishers()

            if not result:
                click.echo("No publishers configured")
                return 0
                    
            click.echo("Configured Publishers:")
            for pub in result:
                click.echo(f"\n{click.style(pub.get('id'), fg='green')}:")
                click.echo(f"  Data Source: {pub.get('data_source_key')}")
                click.echo(f"  Topic: {pub.get('mqtt_topic')}")
                click.echo(f"  QoS: {pub.get('qos')}")
                click.echo(f"  Retain: {pub.get('retain')}")
                click.echo(f"  Use Topic Prefix: {pub.get('use_topic_prefix')}")
            return 0
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
    """Create a new publisher."""
    try:
        if not force:
            msg = f"Create publisher '{id}' for data source '{source}' publishing to '{topic}'?"
            if not click.confirm(msg):
                click.echo('Operation cancelled.')
                return 0

        with create_client(**get_client_args(ctx.obj)) as client:
            client.analytics_mqtt.create_publisher(id, source, topic, qos, retain, use_topic_prefix)

            click.echo(click.style("Publisher created successfully!", fg="green"))
            click.echo("\nPublisher details:")
            click.echo(f"  ID: {id}")
            click.echo(f"  Data Source: {source}")
            click.echo(f"  Topic: {topic}")
            click.echo(f"  QoS: {qos}")
            click.echo(f"  Retain: {retain}")
            click.echo(f"  Use Topic Prefix: {use_topic_prefix}")
            return 0
    except Exception as e:
        return handle_error(ctx, e)

@cli.command('remove')
@click.argument('id')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def remove_publisher(ctx, id, force):
    """Remove a publisher."""
    try:
        if not force:
            msg = f"Are you sure you want to remove publisher '{id}'?"
            if not click.confirm(msg):
                click.echo('Operation cancelled.')
                return 0

        with create_client(**get_client_args(ctx.obj)) as client:
            client.analytics_mqtt.remove_publisher(id)

            click.echo(click.style(f"Publisher '{id}' removed successfully!", fg="green"))
            return 0
    except Exception as e:
        return handle_error(ctx, e)

if __name__ == '__main__':
    cli()