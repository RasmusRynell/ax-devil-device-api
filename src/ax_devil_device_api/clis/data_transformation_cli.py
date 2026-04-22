#!/usr/bin/env python3
"""CLI for managing data transformations."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args
)


def create_data_transformation_group():
    """Create and return the data transformation command group."""
    @click.group()
    @click.pass_context
    def data_transformation(ctx):
        """Manage data transformations (jq expression-based transforms)."""
        pass

    @data_transformation.command('topics')
    @click.pass_context
    def list_topics(ctx):
        """List available topics."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.data_transformation.get_available_topics()

                if not result:
                    click.echo("No topics available")
                    return 0
                        
                click.echo("Available topics:")
                for topic in result:
                    click.echo(f"  - {topic.get('topic')}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @data_transformation.command('list')
    @click.pass_context
    def list_transforms(ctx):
        """List configured transforms."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.data_transformation.list_transforms()

                if not result:
                    click.echo("No transforms configured")
                    return 0
                        
                click.echo("Configured Transforms:")
                for transform in result:
                    click.echo(f"\n{click.style(transform.get('outputTopic'), fg='green')}:")
                    click.echo(f"  - Input Topic \"{transform.get('inputTopic')}\"")
                    click.echo(f"  - Output Topic \"{transform.get('outputTopic')}\"")
                    click.echo(f"  - jq Expression \"{transform.get('jqExpression')}\"")
                    click.echo(f"  - Status: {transform.get('status')}")

                    statistics = transform.get('statistics', {})
                    click.echo("  - Statistics:")
                    for key, value in statistics.items():
                        click.echo(f"      - {key}: {value}")

                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @data_transformation.command('create')
    @click.argument('input-topic')
    @click.argument('output-topic')
    @click.argument('jq-expression')
    @click.pass_context
    def create_publisher(ctx, input_topic, output_topic, jq_expression):
        """Create a new data transform with a jq expression."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                client.data_transformation.create_transform(
                    input_topic=input_topic,
                    output_topic=output_topic,
                    jq_expression=jq_expression
                )

                click.echo(click.style("Publisher created successfully!", fg="green"))
                click.echo("\nPublisher details:")
                click.echo(f"  - Input Topic \"{input_topic}\"")
                click.echo(f"  - Output Topic \"{output_topic}\"")
                click.echo(f"  - jq Expression \"{jq_expression}\"")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @data_transformation.command('remove')
    @click.argument('output-topic')
    @click.option('--force', is_flag=True, help='Skip confirmation')
    @click.pass_context
    def remove_transform(ctx, output_topic, force):
        """Remove a transform."""
        try:
            if not force:
                msg = f"Are you sure you want to remove transform '{output_topic}'?"
                if not click.confirm(msg):
                    click.echo('Operation cancelled.')
                    return 0

            with create_client(**get_client_args(ctx.obj)) as client:
                client.data_transformation.remove_transform(output_topic=output_topic)

                click.echo(click.style(f"Transform '{output_topic}' removed successfully!", fg="green"))
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return data_transformation
