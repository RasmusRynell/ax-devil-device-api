#!/usr/bin/env python3
"""CLI for querying device system readiness."""

import click
from .cli_core import (
    create_client,
    create_client_no_auth,
    handle_error,
    get_client_args,
)


def create_systemready_group():
    """Create and return the systemready command group."""

    @click.group()
    @click.pass_context
    def systemready(ctx):
        """Check device system readiness."""
        pass

    @systemready.command("check")
    @click.option(
        "--timeout",
        "-t",
        default=20,
        type=int,
        show_default=True,
        help="Maximum seconds to wait for the device to become ready.",
    )
    @click.pass_context
    def check(ctx, timeout):
        """Check if the device is ready for operation.

        This endpoint does not require authentication. The request will block
        up to TIMEOUT seconds waiting for the device to respond.
        """
        try:
            args = get_client_args(ctx.obj)
            with create_client_no_auth(
                device_ip=args["device_ip"],
                port=args.get("port"),
                protocol=args.get("protocol", "https"),
                no_verify_ssl=args.get("no_verify_ssl", False),
                debug=args.get("debug", False),
            ) as client:
                data = client.systemready.systemready(timeout=timeout)

                ready = data.get("systemready", "no")
                if ready == "yes":
                    click.echo(click.style("System is ready!", fg="green"))
                else:
                    click.echo(click.style("System is NOT ready.", fg="red"))

                for key, value in data.items():
                    click.echo(f"  {key}: {value}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @systemready.command("versions")
    @click.pass_context
    def versions(ctx):
        """List supported API versions for the systemready endpoint."""
        try:
            args = get_client_args(ctx.obj)
            with create_client_no_auth(
                device_ip=args["device_ip"],
                port=args.get("port"),
                protocol=args.get("protocol", "https"),
                no_verify_ssl=args.get("no_verify_ssl", False),
                debug=args.get("debug", False),
            ) as client:
                api_versions = client.systemready.get_supported_versions()
                click.echo("Supported API versions:")
                for v in api_versions:
                    click.echo(f"  {v}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    return systemready
