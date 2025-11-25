#!/usr/bin/env python3
"""Main CLI entry point for ax-devil-device-api - Unified interface for Axis device APIs."""

import click
from .clis.cli_core import common_options

# Import version from package metadata
from importlib.metadata import version
__version__ = version('ax-devil-device-api')


@click.group()
@common_options
@click.version_option(version=__version__, prog_name='ax-devil-device-api')
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, debug):
    """ax-devil-device-api - Unified CLI for Axis device APIs.
    
    Manage Axis network devices through a comprehensive command-line interface.
    Supports device management, network configuration, media streaming, 
    MQTT communication, SSH access, and more.
    """
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


def register_subcommands():
    """Register all subcommand groups."""
    # Import subgroups - delayed import to avoid circular dependencies
    from .clis.device_info_cli import create_device_group
    from .clis.network_cli import create_network_group
    from .clis.media_cli import create_media_group
    from .clis.mqtt_client_cli import create_mqtt_group
    from .clis.ssh_cli import create_ssh_group
    from .clis.geocoordinates_cli import create_geocoordinates_group
    from .clis.analytics_mqtt_cli import create_analytics_group
    from .clis.api_discovery_cli import create_discovery_group
    from .clis.feature_flags_cli import create_features_group
    from .clis.device_debug_cli import create_debug_group
    from .clis.analytics_metadata_cli import create_analytics_metadata_group
    
    # Register subcommands
    cli.add_command(create_device_group(), name='device')
    cli.add_command(create_network_group(), name='network')
    cli.add_command(create_media_group(), name='media')
    cli.add_command(create_mqtt_group(), name='mqtt')
    cli.add_command(create_ssh_group(), name='ssh')
    cli.add_command(create_geocoordinates_group(), name='geocoordinates')
    cli.add_command(create_analytics_group(), name='analytics')
    cli.add_command(create_discovery_group(), name='discovery')
    cli.add_command(create_features_group(), name='features')
    cli.add_command(create_debug_group(), name='debug')
    cli.add_command(create_analytics_metadata_group(), name='analytics-metadata')


# Register subcommands when module is imported
register_subcommands()


if __name__ == '__main__':
    cli()
