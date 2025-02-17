#!/usr/bin/env python3
import click
import json
import os
import traceback
import sys
from typing import Dict, Any, Optional
from ax_devil_device_api import Client, CameraConfig
from ax_devil_device_api.core.config import Protocol
from ax_devil_device_api.utils.errors import SecurityError, NetworkError, FeatureError, AxisError
from ax_devil_device_api.core.types import FeatureResponse
from typing import Union
from datetime import datetime


class OperationCancelled(Exception):
    """Raised when user cancels an operation."""
    pass


def create_client(camera_ip, username, password, port, protocol='https', no_verify_ssl=False) -> Client:
    """Create and return a Client instance within a context manager.
    
    Returns:
        A context manager that yields a Client instance.
        
    Example:
        with create_client(...) as client:
            result = client.device.get_info()
    """
    if protocol == 'https':
        config = CameraConfig.https(
            host=camera_ip,
            username=username,
            password=password,
            port=port,
            verify_ssl=not no_verify_ssl
        )
    else:
        if not click.confirm('Warning: Using HTTP is insecure. Continue?', default=False):
            raise OperationCancelled("HTTP connection cancelled by user")

        config = CameraConfig.http(
            host=camera_ip,
            username=username,
            password=password,
            port=port
        )

    return Client(config).__enter__()  # Return context manager


def show_debug_info(ctx, error=None):
    """Show detailed debug information if debug mode is enabled."""
    if error is not None:
        debug_info = {
            "connection": {
                "protocol": ctx.obj['protocol'],
                "host": ctx.obj['camera_ip'],
                "port": ctx.obj['port'],
                "ssl_verify": not ctx.obj['no_verify_ssl']
            },
            "error": {
                "type": error.__class__.__name__,
                "code": getattr(error, 'code', None),
                "message": str(error),
                "details": getattr(error, 'details', None)
            }
        }
        click.secho("\nDebug Information:", fg='blue', err=True)

        # Remove and print debug info without (unprintable) details
        info_without_details = debug_info.copy()
        print(info_without_details["error"]["details"])
        info_without_details["error"].pop("details", None)
        click.echo(json.dumps(info_without_details,
                   indent=2, sort_keys=True), err=True)

    # Show traceback if available
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_traceback:
        formatted_tb = ''.join(traceback.format_exception(
            exc_type, exc_value, exc_traceback))
        click.secho("\nFull Traceback:", fg='red', err=True)
        click.echo(formatted_tb, err=True)


def format_error_message(error: Union[Exception, AxisError]) -> tuple[str, str]:
    """Format error message and determine color based on error type."""
    # Map error codes to user-friendly messages
    error_messages = {
        # Security Errors
        "ssl_verification_failed": (
            "Cannot establish secure connection to camera.\n"
            "The camera appears to be using a self-signed certificate.\n\n"
            "Available options:\n"
            "1. Use HTTP instead:     --protocol http\n"
            "2. Skip verification:    --no-verify-ssl\n"
            "3. Install a valid certificate on the camera"
        ),
        # Network Errors
        "connection_refused": (
            "Cannot reach camera. Please check:\n"
            "1. Camera IP address is correct\n"
            "2. Camera is powered on and connected to network\n"
            "3. No firewall is blocking the connection"
        ),
        "request_timeout": (
            "Request timed out. Please check:\n"
            "1. Camera is responsive\n"
            "2. Network connection is stable"
        ),
        # Feature Errors
        "fetch_failed": (
            "Failed to fetch camera parameters.\n"
            "Please check camera connectivity and try again."
        ),
        "info_parse_failed": (
            "Failed to parse device information.\n"
            "The camera response was not in the expected format."
        ),
        "restart_failed": (
            "Failed to restart camera.\n"
            "Please check permissions and try again."
        ),
        "health_check_failed": (
            "Camera health check failed.\n"
            "The camera is not responding correctly."
        ),
    }

    if isinstance(error, OperationCancelled):
        return str(error), 'white'
    elif not isinstance(error, (SecurityError, NetworkError, FeatureError)):
        return f"Internal Error: {str(error)}", 'red'

    # Use the same message for all SSL-related errors
    if error.code == "ssl_error":
        error.code = "ssl_verification_failed"

    message = error_messages.get(error.code, f"{error.code}: {error.message}")
    color = 'yellow' if isinstance(error, SecurityError) else 'red'

    # Also print the message of the original error if it exists
    if hasattr(error, 'details') and error.details and 'original_error' in error.details:
        original_error = error.details['original_error']
        message += f"\n---\n{error_messages.get(original_error.code, f'{original_error.code}: {original_error.message}')}"
    return message, color


def handle_error(ctx, error: Exception, show_prefix: bool = True) -> int:
    """Handle any type of error consistently."""
    message, color = format_error_message(error)
    if show_prefix and not isinstance(error, OperationCancelled):
        message = f"Error: {message}"

    click.secho(message, fg=color, err=True)

    if ctx.obj.get('debug'):
        show_debug_info(ctx, error)

    return 1


def handle_result(ctx, result: FeatureResponse) -> int:
    """Handle command result and return appropriate exit code."""
    if result.success:
        if hasattr(result.data, '__dict__'):
            data = result.data.__dict__
        else:
            data = result.data
        click.echo(json.dumps(data, indent=2))
        return 0

    return handle_error(ctx, result.error, show_prefix=False)


def get_client_args(ctx_obj: dict) -> dict:
    """Extract client-specific arguments from context object."""
    return {k: v for k, v in ctx_obj.items()
            if k in ['camera_ip', 'username', 'password', 'port',
                     'protocol', 'no_verify_ssl']}


def common_options(f):
    """Common CLI options decorator."""
    f = click.option('--camera-ip', default=lambda: os.getenv('AXIS_TARGET_ADDR'),
                     required=False, help='Camera IP address or hostname')(f)
    f = click.option('--username', default=lambda: os.getenv('AXIS_TARGET_USER'),
                     required=False, help='Username for authentication')(f)
    f = click.option('--password', default=lambda: os.getenv('AXIS_TARGET_PASS'),
                     required=False, help='Password for authentication')(f)
    f = click.option('--port', type=int, required=False, help='Port number')(f)
    f = click.option('--protocol', type=click.Choice(['http', 'https']),
                     default='https', help='Connection protocol (default: https)')(f)
    f = click.option('--no-verify-ssl', is_flag=True,
                     help='Disable SSL certificate verification for HTTPS (use with self-signed certificates)')(f)
    f = click.option('--debug', is_flag=True,
                     help='Show detailed debug information for troubleshooting')(f)
    return f
