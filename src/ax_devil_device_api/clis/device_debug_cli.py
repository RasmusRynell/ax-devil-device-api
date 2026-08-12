"""CLI for managing device debugging operations."""

import click

from .cli_core import create_client, get_client_args


def create_debug_group():
    """Create and return the debug command group."""

    @click.group()
    @click.pass_context
    def debug(ctx):
        """Manage device debugging operations."""

    @debug.command()
    @click.argument("output_file", type=click.Path(dir_okay=False, writable=True))
    @click.option(
        "--mode",
        type=click.Choice(["zip", "zip_with_image"]),
        default="zip",
        show_default=True,
        help="Server report mode; zip is portable across more products.",
    )
    @click.pass_context
    def download_server_report(ctx, output_file, mode):
        """Download a legacy CGI server report ZIP to OUTPUT_FILE."""
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device_debug.download_server_report(mode=mode)
            try:
                with open(output_file, "wb") as f:
                    f.write(result)
                click.echo(f"Server report saved to {output_file}")
            except OSError as e:
                click.echo(f"Error saving file: {e!s}", err=True)
                return 1

    @debug.command()
    @click.argument("output_file", type=click.Path(dir_okay=False, writable=True))
    @click.pass_context
    def download_crash_report(ctx, output_file):
        """Download a legacy CGI crash report gzip artifact to OUTPUT_FILE."""
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device_debug.download_crash_report()
            try:
                with open(output_file, "wb") as f:
                    f.write(result)
                click.echo(f"Crash report saved to {output_file}")
            except OSError as e:
                click.echo(f"Error saving file: {e!s}", err=True)
                return 1

    @debug.command()
    @click.argument("output_file", type=click.Path(dir_okay=False, writable=True))
    @click.option(
        "--duration",
        default=30,
        type=click.IntRange(min=1),
        show_default=True,
        help="Capture duration in seconds; timeout includes capture grace.",
    )
    @click.option("--interface", default="", help="Interface(s) for network trace")
    @click.pass_context
    def download_network_trace(ctx, output_file, duration, interface):
        """Download a legacy CGI network trace to OUTPUT_FILE."""
        with create_client(**get_client_args(ctx.obj)) as client:
            iface = interface if interface else None
            result = client.device_debug.download_network_trace(
                duration=duration, interface=iface
            )
            try:
                with open(output_file, "wb") as f:
                    f.write(result)
                click.echo(f"Network trace saved to {output_file}")
            except OSError as e:
                click.echo(f"Error saving file: {e!s}", err=True)
                return 1

    @debug.command()
    @click.argument("target")
    @click.pass_context
    def ping_test(ctx, target):
        """Perform a ping test from the device to the target IP or hostname."""
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device_debug.ping_test(target)
            click.echo(result)

    @debug.command()
    @click.argument("address")
    @click.argument("port", type=click.IntRange(1, 65535))
    @click.pass_context
    def port_open_test(ctx, address, port):
        """Check if a port is open on a target address from the device."""
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device_debug.port_open_test(address, port)
            click.echo(result)

    @debug.command()
    @click.argument("output_file", type=click.Path(dir_okay=False, writable=True))
    @click.pass_context
    def collect_core_dump(ctx, output_file):
        """Collect a legacy CGI core dump using buffered, non-streaming I/O."""
        with create_client(**get_client_args(ctx.obj)) as client:
            result = client.device_debug.collect_core_dump()
            try:
                with open(output_file, "wb") as f:
                    f.write(result)
                click.echo(f"Core dump saved to {output_file}")
            except OSError as e:
                click.echo(f"Error saving file: {e!s}", err=True)
                return 1

    return debug
