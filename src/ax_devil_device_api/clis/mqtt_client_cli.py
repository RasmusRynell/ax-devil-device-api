#!/usr/bin/env python3
"""CLI for managing MQTT client operations."""

import click
from .cli_core import create_client, handle_error, get_client_args


def create_mqtt_group():
    """Create and return the mqtt command group."""

    @click.group()
    @click.pass_context
    def mqtt(ctx):
        """Manage MQTT client settings."""
        pass

    @mqtt.command("activate")
    @click.pass_context
    def activate(ctx):
        """Activate MQTT client."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                _ = client.mqtt_client.activate()
                click.echo(
                    click.style("MQTT client activated successfully!", fg="green")
                )
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command("deactivate")
    @click.pass_context
    def deactivate(ctx):
        """Deactivate MQTT client."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                _ = client.mqtt_client.deactivate()

                click.echo(
                    click.style("MQTT client deactivated successfully!", fg="yellow")
                )
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command("configure")
    @click.option(
        "--broker-address",
        "-b",
        envvar="AX_DEVIL_MQTT_BROKER_ADDR",
        show_envvar=True,
        required=True,
        help="Broker hostname or IP address",
    )
    @click.option(
        "--broker-port",
        "-P",
        type=click.IntRange(1, 65535),
        default=1883,
        show_default=True,
        help="Broker port number",
    )
    @click.option("--broker-username", "-U", help="Broker authentication username")
    @click.option(
        "--broker-password",
        "-W",
        envvar="AX_DEVIL_MQTT_BROKER_PASS",
        show_envvar=True,
        help="Broker authentication password",
    )
    @click.option(
        "--keep-alive",
        type=click.IntRange(min=0),
        default=60,
        show_default=True,
        help="Keep alive interval in seconds",
    )
    @click.option(
        "--protocol",
        type=click.Choice(["tcp", "ssl", "ws", "wss"]),
        default="tcp",
        show_default=True,
        help="MQTT transport protocol.",
    )
    @click.option("--use-tls", is_flag=True, help="Use TLS encryption")
    @click.pass_context
    def configure(
        ctx,
        broker_address,
        broker_port,
        broker_username,
        broker_password,
        keep_alive,
        protocol,
        use_tls,
    ):
        """Configure MQTT broker settings."""
        try:
            if use_tls and protocol not in {"tcp", "ssl"}:
                raise click.UsageError(
                    "--use-tls can only be combined with --protocol tcp or ssl"
                )
            with create_client(**get_client_args(ctx.obj)) as client:
                client.mqtt_client.configure(
                    host=broker_address,
                    port=broker_port,
                    username=broker_username,
                    password=broker_password,
                    protocol=protocol,
                    use_tls=True if use_tls and protocol == "tcp" else None,
                    keep_alive_interval=keep_alive,
                )

                click.echo(
                    click.style(
                        "MQTT broker configuration updated successfully!", fg="green"
                    )
                )
                click.echo("\nBroker Configuration:")
                click.echo(f"  Host: {broker_address}")
                click.echo(f"  Port: {broker_port}")
                click.echo(f"  Protocol: {protocol if not use_tls else 'ssl'}")
                click.echo(f"  Keep Alive: {keep_alive}s")
                if broker_username:
                    click.echo("  Authentication: Enabled")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command("status")
    @click.pass_context
    def status(ctx):
        """Get MQTT client status."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                state_data = client.mqtt_client.get_state()
                status = state_data.get("status") or {}
                click.echo("MQTT Client Status:")
                click.echo(
                    f"  state: {click.style(status.get('state'), fg='green' if status.get('state') == 'active' else 'yellow')}"
                )
                click.echo(
                    f"  connectionStatus: {click.style(status.get('connectionStatus'), fg='green' if status.get('connectionStatus') == 'connected' else 'yellow')}"
                )
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command("config")
    @click.pass_context
    def config(ctx):
        """Get MQTT client configuration."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                state_data = client.mqtt_client.get_state()
                config = state_data.get("config") or {}
                server = config.get("server") or {}
                click.echo("MQTT Client Configuration:")
                click.echo(f"  Host: {server.get('host')}")
                click.echo(f"  Port: {server.get('port')}")
                click.echo(f"  protocol: {server.get('protocol')}")
                click.echo(f"  alpnProtocol: {server.get('alpnProtocol')}")
                click.echo(
                    f"  username: {'configured' if config.get('username') else 'not configured'}"
                )
                click.echo(
                    "  password: configured"
                    if config.get("password")
                    else "  password: not configured"
                )
                click.echo(f"  clientId: {config.get('clientId')}")
                click.echo(f"  keepAliveInterval: {config.get('keepAliveInterval')}s")
                click.echo(f"  connectTimeout: {config.get('connectTimeout')}s")
                click.echo(f"  cleanSession: {config.get('cleanSession')}")
                click.echo(f"  autoReconnect: {config.get('autoReconnect')}")
                click.echo(f"  deviceTopicPrefix: {config.get('deviceTopicPrefix')}")
                click.echo(f"  httpProxy: {config.get('httpProxy')}")
                click.echo(f"  httpsProxy: {config.get('httpsProxy')}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    return mqtt
