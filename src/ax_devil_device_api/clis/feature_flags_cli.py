#!/usr/bin/env python3
"""CLI for managing feature flags."""

import click
from typing import Dict

from .cli_core import (
    create_client, print_table_list_with_dict, handle_error, get_client_args,
    format_json
)


def parse_flag_values(flags: tuple[str, ...]) -> Dict[str, bool]:
    """Parse flag=value pairs into a dictionary."""
    flag_values = {}
    
    for flag in flags:
        try:
            name, value = flag.split('=', 1)
            if value.lower() not in ('true', 'false'):
                click.secho(f"Error: Invalid value for {name}: {value}. Use \"feature_flag_name=true\" or \"feature_flag_name=false\"", fg='red', err=True)
                raise click.Abort()
            flag_values[name] = value.lower() == 'true'
        except ValueError:
            click.secho(f"Error: Invalid format: {flag}. Use: feature_flag_name=true or feature_flag_name=false", fg='red', err=True)
            raise click.Abort()
            
    return flag_values


def create_features_group():
    """Create and return the features command group."""
    @click.group()
    @click.pass_context
    def features(ctx):
        """Manage device feature flags."""
        pass

    @features.command('list')
    @click.pass_context
    def list_flags(ctx):
        """List all available feature flags with their current values."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.feature_flags.list_all()
                print_table_list_with_dict(result, keys_with_order=['name', 'enabled', "defaultValue", "description"])
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @features.command('get')
    @click.argument('names', nargs=-1, required=True)
    @click.pass_context
    def get_flags(ctx, names):
        """Get values of specific feature flags."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.feature_flags.get_flags(list(names))
                click.echo(format_json(result))
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @features.command('set')
    @click.argument('flags', nargs=-1, required=True)
    @click.option('--force', is_flag=True, help='Skip confirmation prompt')
    @click.pass_context
    def set_flags(ctx, flags, force):
        """Set values for one or more feature flags."""
        flag_values = parse_flag_values(flags)
        
        # Show what will be changed
        click.echo("\nFeature flags to be set:")
        click.echo(format_json(flag_values))
        if not force and not click.confirm('\nProceed with these changes?'):
            click.echo('Operation cancelled.')
            return 0

        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.feature_flags.set_flags(flag_values)
                click.echo(result)
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return features 