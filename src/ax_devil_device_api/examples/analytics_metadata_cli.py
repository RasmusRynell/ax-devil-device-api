#!/usr/bin/env python3
"""CLI for managing analytics metadata producer configuration."""

import json
import sys
from typing import List

import click
from .cli_core import (
    create_client, handle_error, get_client_args
)


def create_analytics_metadata_group():
    """Create and return the analytics metadata command group."""
    @click.group()
    @click.pass_context
    def analytics_metadata(ctx):
        """Manage analytics metadata producer configuration."""
        pass

    @analytics_metadata.command('list')
    @click.option('--format', type=click.Choice(['table', 'json']), default='table',
                  help='Output format')
    @click.pass_context
    def list_producers(ctx, format):
        """List all available metadata producers."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                producers = client.analytics_metadata.list_producers()
                
                if format == 'json':
                    output = []
                    for producer in producers:
                        channels = [
                            {"channel": ch.channel, "enabled": ch.enabled}
                            for ch in producer.video_channels
                        ]
                        output.append({
                            "name": producer.name,
                            "niceName": producer.nice_name,
                            "videoChannels": channels
                        })
                    click.echo(json.dumps(output, indent=2))
                else:
                    if not producers:
                        click.echo("No metadata producers found.")
                        return 0
                    
                    click.echo(f"{'Producer Name':<30} {'Nice Name':<40} {'Channels'}")
                    click.echo("-" * 80)
                    
                    for producer in producers:
                        channels_str = ", ".join([
                            f"Ch{ch.channel}({'✓' if ch.enabled else '✗'})"
                            for ch in producer.video_channels
                        ])
                        click.echo(f"{producer.name:<30} {producer.nice_name:<40} {channels_str}")
                
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @analytics_metadata.command('enable')
    @click.argument('producer_name')
    @click.option('--channel', '-c', type=int, multiple=True,
                  help='Video channel(s) to enable. Can be specified multiple times.')
    @click.pass_context
    def enable_producer(ctx, producer_name, channel):
        """Enable a metadata producer on specified channels."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                # First get current producers to preserve other settings
                current_producers = client.analytics_metadata.list_producers()
                
                # Find the target producer
                target_producer = None
                for producer in current_producers:
                    if producer.name == producer_name:
                        target_producer = producer
                        break
                
                if not target_producer:
                    return handle_error(ctx, f"Producer '{producer_name}' not found")
                
                # If no channels specified, enable on all available channels
                if not channel:
                    channels_to_enable = [ch.channel for ch in target_producer.video_channels]
                else:
                    channels_to_enable = list(channel)
                
                # Create updated producer configuration
                from ..features.analytics_metadata import Producer, VideoChannel
                
                updated_channels = []
                for ch in target_producer.video_channels:
                    enabled = ch.channel in channels_to_enable
                    updated_channels.append(VideoChannel(channel=ch.channel, enabled=enabled))
                
                updated_producer = Producer(
                    name=target_producer.name,
                    nice_name=target_producer.nice_name,
                    video_channels=updated_channels
                )
                
                client.analytics_metadata.set_enabled_producers([updated_producer])
                
                enabled_channels = [ch for ch in channels_to_enable]
                click.echo(click.style(
                    f"Enabled producer '{producer_name}' on channels: {enabled_channels}",
                    fg="green"
                ))
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @analytics_metadata.command('disable')
    @click.argument('producer_name')
    @click.option('--channel', '-c', type=int, multiple=True,
                  help='Video channel(s) to disable. Can be specified multiple times.')
    @click.pass_context
    def disable_producer(ctx, producer_name, channel):
        """Disable a metadata producer on specified channels."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                # First get current producers
                current_producers = client.analytics_metadata.list_producers()
                
                # Find the target producer
                target_producer = None
                for producer in current_producers:
                    if producer.name == producer_name:
                        target_producer = producer
                        break
                
                if not target_producer:
                    return handle_error(ctx, f"Producer '{producer_name}' not found")
                
                # If no channels specified, disable on all channels
                if not channel:
                    channels_to_disable = [ch.channel for ch in target_producer.video_channels]
                else:
                    channels_to_disable = list(channel)
                
                # Create updated producer configuration
                from ..features.analytics_metadata import Producer, VideoChannel
                
                updated_channels = []
                for ch in target_producer.video_channels:
                    enabled = ch.enabled and ch.channel not in channels_to_disable
                    updated_channels.append(VideoChannel(channel=ch.channel, enabled=enabled))
                
                updated_producer = Producer(
                    name=target_producer.name,
                    nice_name=target_producer.nice_name,
                    video_channels=updated_channels
                )
                
                client.analytics_metadata.set_enabled_producers([updated_producer])
                
                click.echo(click.style(
                    f"Disabled producer '{producer_name}' on channels: {channels_to_disable}",
                    fg="green"
                ))
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @analytics_metadata.command('sample')
    @click.argument('producer_names', nargs=-1, required=True)
    @click.option('--format', type=click.Choice(['xml', 'json']), default='xml',
                  help='Output format for sample data')
    @click.option('--output', '-o', type=click.Path(dir_okay=False),
                  help='Save sample to file instead of stdout')
    @click.pass_context
    def get_sample(ctx, producer_names, format, output):
        """Get sample metadata frames from specified producers."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                samples = client.analytics_metadata.get_supported_metadata(list(producer_names))
                
                if format == 'json':
                    output_data = []
                    for sample in samples:
                        sample_data = {
                            "producerName": sample.producer_name,
                            "sampleFrameXML": sample.sample_frame_xml
                        }
                        if sample.schema_xml:
                            sample_data["schemaXML"] = sample.schema_xml
                        output_data.append(sample_data)
                    
                    content = json.dumps(output_data, indent=2)
                else:
                    # XML format
                    content_parts = []
                    for sample in samples:
                        content_parts.append(f"<!-- Producer: {sample.producer_name} -->")
                        content_parts.append(sample.sample_frame_xml)
                        if sample.schema_xml:
                            content_parts.append(f"<!-- Schema for {sample.producer_name} -->")
                            content_parts.append(sample.schema_xml)
                        content_parts.append("")  # Empty line for separation
                    
                    content = "\n".join(content_parts)
                
                if output:
                    try:
                        with open(output, 'w') as f:
                            f.write(content)
                        click.echo(click.style(f"Sample metadata saved to {output}", fg="green"))
                    except IOError as e:
                        return handle_error(ctx, f"Failed to save sample: {e}")
                else:
                    click.echo(content)
                
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @analytics_metadata.command('versions')
    @click.option('--format', type=click.Choice(['table', 'json']), default='table',
                  help='Output format')
    @click.pass_context
    def get_versions(ctx, format):
        """Get supported API versions."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                versions = client.analytics_metadata.get_supported_versions()
                
                if format == 'json':
                    click.echo(json.dumps({"versions": versions}, indent=2))
                else:
                    if not versions:
                        click.echo("No supported versions found.")
                        return 0
                    
                    click.echo("Supported API Versions:")
                    for version in versions:
                        click.echo(f"  • {version}")
                
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return analytics_metadata