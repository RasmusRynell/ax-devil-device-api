#!/usr/bin/env python3
import click
import json
import os
import traceback
import sys
from ax_devil_device_api import Client, DeviceConfig
from ax_devil_device_api.utils.errors import SecurityError, NetworkError, FeatureError, BaseError
from ax_devil_device_api.core.types import FeatureResponse
from typing import Union


class OperationCancelled(Exception):
    """Raised when user cancels an operation."""
    pass


def create_client(device_ip, username, password, port, protocol='https', no_verify_ssl=False) -> Client:
    """Create and return a Client instance within a context manager.
    
    Returns:
        A context manager that yields a Client instance.
        
    Example:
        with create_client(...) as client:
            result = client.device.get_info()
    """
    assert protocol in ['http', 'https'], "Invalid protocol"
    assert port is None or isinstance(port, int), "\n\tInvalid port"
    assert username is not None and password is not None, "\n\tUsername and password are required, use --username and --password options or set AX_DEVIL_TARGET_USER and AX_DEVIL_TARGET_PASS environment variables"
    assert device_ip is not None, "\n\tDevice IP is required, use --device-ip option or set AX_DEVIL_TARGET_ADDR environment variable"
    assert no_verify_ssl is False or protocol == 'https', "\n\tSSL verification can only be disabled for HTTPS connections"

    if protocol == 'https':
        config = DeviceConfig.https(
            host=device_ip,
            username=username,
            password=password,
            port=port,
            verify_ssl=not no_verify_ssl
        )
    else:
        if os.getenv('AX_DEVIL_USAGE_CLI', "safe") == "safe":
            if not click.confirm('Warning: Using HTTP is insecure. Continue?', default=False):
                raise OperationCancelled("HTTP connection cancelled by user")

        config = DeviceConfig.http(
            host=device_ip,
            username=username,
            password=password,
            port=port
        )

    return Client(config).__enter__() # Return context manager


def show_debug_info(ctx, error=None):
    """Show detailed debug information if debug mode is enabled."""
    if error is not None:
        debug_info = {
            "connection": {
                "protocol": ctx.obj['protocol'],
                "host": ctx.obj['device_ip'],
                "port": ctx.obj['port'],
                "ssl_verify": not ctx.obj['no_verify_ssl']
            },
            "error": {
                "type": error.__class__.__name__,
                "code": getattr(error, 'code', None),
                "message": str(error),
                "details": ""
            }
        }

    if hasattr(error, 'details') and error.details and 'response' in error.details:
        debug_info['error']['details'] = json.loads(error.details['response'])
    else:
        if hasattr(error, 'details') and error.details:
            debug_info['error']['details'] = error.details
        else:
            debug_info['error']['details'] = ""
    click.secho("\nDebug Information:", fg='blue', err=True)
    try:
        click.echo(format_json(debug_info), err=True)
    except Exception as e:
        click.echo(f"Error: {e}, {debug_info}", err=True)

    # Show traceback if available
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_traceback:
        formatted_tb = ''.join(traceback.format_exception(
            exc_type, exc_value, exc_traceback))
        click.secho("\nFull Traceback:", fg='red', err=True)
        click.echo(formatted_tb, err=True)


def format_error_message(error: Union[Exception, BaseError]) -> tuple[str, str]:
    """Format error message and determine color based on error type."""
    # Map error codes to user-friendly messages
    error_messages = {
        # Security Errors
        "ssl_verification_failed": (
            "Cannot establish secure connection to device.\n"
            "The device uses a built-in device identity certificate that needs to be verified.\n\n"
            "Available options:\n"
            "1. Use HTTP instead:     --protocol http (not secure, development only)\n"
            "2. Skip verification:    --no-verify-ssl (not secure, development only)\n"
        ),
        # Network Errors
        "connection_refused": (
            "Cannot reach device. Please check:\n"
            "1. Device IP address is correct\n"
            "2. Device is powered on and connected to network\n"
            "3. No firewall is blocking the connection"
        ),
        "request_timeout": (
            "Request timed out. Please check:\n"
            "1. Device is responsive\n"
            "2. Network connection is stable"
        ),
        # Feature Errors
        "fetch_failed": (
            "Failed to fetch device parameters.\n"
            "Please check device connectivity and try again."
        ),
        "info_parse_failed": (
            "Failed to parse device information.\n"
            "The device response was not in the expected format."
        ),
        "restart_failed": (
            "Failed to restart device.\n"
            "Please check permissions and try again."
        ),
        "health_check_failed": (
            "Device health check failed.\n"
            "The device is not responding correctly."
        ),
        "username_password_required": (
            "Username and password are required.\n"
            "Please provide a username and password using the --username and --password options."
            "\nOptionally: you can set the AX_DEVIL_TARGET_USER and AX_DEVIL_TARGET_PASS environment variables."
        ),
        "authentication_failed": (
            "Authentication failed.\n"
            "Please check your username and password and try again."
        ),
        "unsupported_auth_method": (
            "Unsupported authentication method.\n"
            "Please check your authentication method and try again."
        ),
        "invalid_port": (
            "Invalid port number.\n"
            "Please check your port number and try again."
        ),
        "http_protocol_requested": (
            "HTTP protocol requested but allow_insecure=False.\n"
            "Please use the --protocol http option to connect to the device."
        ),  
        "request_failed": (
            "Request failed.\n"
            "Please check your request and try again."
        ),
        "parse_failed": (
            "Failed to parse the response.\n"
            "Please check the response and try again."
        ),
        "invalid_response": (
            "Invalid response.\n"
            "Please check the response and try again."
        ),
    }

    if isinstance(error, OperationCancelled):
        return str(error), 'white'
    elif not isinstance(error, (SecurityError, NetworkError, FeatureError)):
        return f"Internal Error: {str(error)}", 'red'

    if error.code == "ssl_error":
        error.code = "ssl_verification_failed"

    message = error_messages.get(error.code, f"{error.code}: {error.message}")
    color = 'yellow' if isinstance(error, SecurityError) else 'red'

    if hasattr(error, 'details') and error.details and 'original_error' in error.details:
        original_error = error.details['original_error']
        message += f"\n---\n{error_messages.get(original_error.code, f'{original_error.code}: {original_error.message}')}"

    if hasattr(error, 'details') and error.details and 'response' in error.details:
        json_response = json.loads(error.details['response'])
        if 'error' in json_response and 'message' in json_response['error']:
            message += f"\n---\n{json_response['error']['message']}"
            
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
    if not result.is_success:
        return handle_error(ctx, result.error, show_prefix=False)
    
    if hasattr(result.data, 'to_dict'):
        data = result.data.to_dict()
    elif isinstance(result.data, list) and all(hasattr(item, 'to_dict') for item in result.data):
        data = [item.to_dict() for item in result.data]
    elif hasattr(result.data, '__dict__'):
        data = result.data.__dict__
    else:
        data = result.data
    
    click.echo(format_json(data))
    return 0


def get_client_args(ctx_obj: dict) -> dict:
    """Extract client-specific arguments from context object."""
    return {k: v for k, v in ctx_obj.items()
            if k in ['device_ip', 'username', 'password', 'port',
                     'protocol', 'no_verify_ssl']}


def format_json(data: dict, indent: int = 2) -> str:
    """Format JSON data with syntax highlighting using click.style."""
    formatted_json = json.dumps(data, indent=indent)
    
    if os.getenv('AX_DEVIL_COLOR') == 'false':
        return formatted_json
    
    colored_lines = []
    for line in formatted_json.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            colored_key = click.style(key, fg='blue')
            
            value = value.strip()
            if value.startswith('"'):
                colored_value = click.style(value, fg='green')
            elif value in ('true', 'false'):
                colored_value = click.style(value, fg='yellow')
            elif value == 'null':
                colored_value = click.style(value, fg='blue')
            elif value.replace('.', '').replace('-', '').isdigit():
                colored_value = click.style(value, fg='cyan')
            else:
                colored_value = value
                
            colored_lines.append(f"{colored_key}:{colored_value}")
        else:
            colored_lines.append(line)
    
    return '\n'.join(colored_lines)


def common_options(f):
    """Common CLI options decorator."""
    f = click.option('--device-ip', default=lambda: os.getenv('AX_DEVIL_TARGET_ADDR'),
                     required=False, help='Device IP address or hostname')(f)
    f = click.option('--username', default=lambda: os.getenv('AX_DEVIL_TARGET_USER'),
                     required=False, help='Username for authentication')(f)
    f = click.option('--password', default=lambda: os.getenv('AX_DEVIL_TARGET_PASS'),
                     required=False, help='Password for authentication')(f)
    f = click.option('--port', type=int, required=False, help='Port number')(f)
    f = click.option('--protocol', type=click.Choice(['http', 'https']),
                     default='https',
                     help='Connection protocol (default: https)')(f)
    f = click.option('--no-verify-ssl', is_flag=True, default=False if os.getenv('AX_DEVIL_USAGE_CLI', "safe") == 'safe' else True,
                     help='Disable SSL certificate verification for HTTPS (use with self-signed certificates)')(f)
    f = click.option('--debug', is_flag=True,
                     help='Show detailed debug information for troubleshooting')(f)
    return f
