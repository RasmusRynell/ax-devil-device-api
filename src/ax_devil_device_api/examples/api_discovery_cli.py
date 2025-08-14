#!/usr/bin/env python3
"""CLI for discovering and inspecting available discoverable APIs."""

import click
import webbrowser
from urllib.parse import urljoin

from .cli_core import (
    format_json,
    create_client, handle_error, get_client_args
)


def create_discovery_group():
    """Create and return the discovery command group."""
    @click.group()
    @click.pass_context
    def discovery(ctx):
        """Discover and inspect available discoverable APIs."""
        pass

    @discovery.command('list')
    @click.pass_context
    def list_apis(ctx):
        """List all available APIs on the device."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                apis = client.discovery.discover()
                
                click.echo(f"\nFound {len(apis.get_all_apis())} APIs:")
                for api in apis.get_all_apis():
                    click.echo(f"- {api.name} {api.version} ({api.state})")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @discovery.command('info')
    @click.argument('api-name')
    @click.option('--version', '-v', help='Specific version of the API to inspect')
    @click.option('--docs-md', is_flag=True, help='Open markdown documentation in browser')
    @click.option('--docs-md-raw', is_flag=True, help='Show raw markdown content')
    @click.option('--docs-md-link', is_flag=True, help='Show documentation URL')
    @click.option('--docs-html', is_flag=True, help='Open HTML documentation in browser')
    @click.option('--docs-html-raw', is_flag=True, help='Show raw HTML content')
    @click.option('--docs-html-link', is_flag=True, help='Show documentation URL')
    @click.option('--model', is_flag=True, help='Open model in browser')
    @click.option('--model-raw', is_flag=True, help='Show raw JSON model')
    @click.option('--model-link', is_flag=True, help='Show model URL')
    @click.option('--rest-api', is_flag=True, help='Open REST API in browser')
    @click.option('--rest-api-raw', is_flag=True, help='Show raw API documentation')
    @click.option('--rest-api-link', is_flag=True, help='Show API URL')
    @click.option('--rest-openapi', is_flag=True, help='Open OpenAPI spec in browser')
    @click.option('--rest-openapi-raw', is_flag=True, help='Show raw OpenAPI JSON')
    @click.option('--rest-openapi-link', is_flag=True, help='Show OpenAPI URL')
    @click.option('--rest-ui', is_flag=True, help='Open Swagger UI in browser')
    @click.option('--rest-ui-raw', is_flag=True, help='Show raw Swagger UI HTML')
    @click.option('--rest-ui-link', is_flag=True, help='Show Swagger UI URL')
    @click.pass_context
    def get_api_info(ctx, api_name, version,
                     docs_md, docs_md_raw, docs_md_link,
                     docs_html, docs_html_raw, docs_html_link,
                     model, model_raw, model_link,
                     rest_api, rest_api_raw, rest_api_link,
                     rest_openapi, rest_openapi_raw, rest_openapi_link,
                     rest_ui, rest_ui_raw, rest_ui_link):
        """Get detailed information about a specific API.
        
        API-NAME: Name of the API to inspect (e.g. 'analytics-mqtt')
        
        When no version is specified, the latest released version is used.
        Use --all-versions to show information for all available versions.
        
        For all content types (documentation, model, API, etc.):
        - Default: Open in browser
        - --*-raw: Show raw content
        - --*-link: Show URL only
        """
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                apis = client.discovery.discover()

                api = apis.get_api(api_name, version)
                if not api:
                    if version:
                        click.echo(f"Error: API {api_name} version {version} not found", err=True)
                    else:
                        click.echo(f"Error: API {api_name} not found", err=True)
                    return 1
                
                show_api_info(api, ctx,
                            docs_md, docs_md_raw, docs_md_link,
                            docs_html, docs_html_raw, docs_html_link,
                            model, model_raw, model_link,
                            rest_api, rest_api_raw, rest_api_link,
                            rest_openapi, rest_openapi_raw, rest_openapi_link,
                            rest_ui, rest_ui_raw, rest_ui_link)
                    
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @discovery.command('versions')
    @click.argument('api-name')
    @click.pass_context
    def list_versions(ctx, api_name):
        """List all available versions of a specific API."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                apis = client.discovery.discover()
                versions = apis.get_apis_by_name(api_name)
                
                if not versions:
                    click.echo(f"Error: API {api_name} not found", err=True)
                    return 1
                    
                click.echo(f"\nFound {len(versions)} versions of {api_name}:")
                for api in sorted(versions, key=lambda x: x.version):
                    click.echo(f"- {api.version} ({api.version_string})")
                    click.echo(f"  State: {api.state}")
                    click.echo(f"  REST API: {api.rest_api_url}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return discovery


def show_api_info(api, ctx,
                 docs_md, docs_md_raw, docs_md_link,
                 docs_html, docs_html_raw, docs_html_link,
                 model, model_raw, model_link,
                 rest_api, rest_api_raw, rest_api_link,
                 rest_openapi, rest_openapi_raw, rest_openapi_link,
                 rest_ui, rest_ui_raw, rest_ui_link):
    """Show information for a single API version."""

    click.echo(click.style(f"\nAPI: {api.name} {api.version}", fg="green"))
    click.echo(f"State: {api.state}")
    click.echo(f"Version: {api.version_string}")

    def _get_full_url(path: str) -> str:
        """Helper to construct full URLs with protocol and port."""
        base_url = f"http{'s' if ctx.obj['protocol'] == 'https' else ''}://{ctx.obj['device_ip']}"
        if ctx.obj['port']:
            base_url += f":{ctx.obj['port']}"
        return urljoin(base_url, path)

    def handle_content(name: str, url: str, show: bool, show_raw: bool, show_link: bool,
                      get_raw_content=None, is_json=False):
        """Helper to handle all content types consistently."""
        if not (show or show_raw or show_link):
            return

        click.echo(click.style(f"\n{name}:", fg="yellow"))
        full_url = _get_full_url(url)

        if show_link:
            click.echo(click.style(f"URL: {full_url}", fg="bright_blue"))
        elif show_raw and get_raw_content:
            click.echo("Fetching content:")
            result = get_raw_content()

            if is_json:
                click.echo(format_json(result))
            else:
                click.echo(result)
        elif show:
            click.echo("Opening in browser...")
            webbrowser.open(full_url)

    if docs_md or docs_md_raw or docs_md_link:
        handle_content(
            "Markdown Documentation",
            api._urls['doc'],
            docs_md, docs_md_raw, docs_md_link,
            api.get_documentation
        )

    if docs_html or docs_html_raw or docs_html_link:
        handle_content(
            "HTML Documentation",
            api._urls['doc_html'],
            docs_html, docs_html_raw, docs_html_link,
            api.get_documentation_html
        )

    if model or model_raw or model_link:
        handle_content(
            "API Model",
            api._urls['model'],
            model, model_raw, model_link,
            api.get_model,
            is_json=True
        )

    if rest_api or rest_api_raw or rest_api_link:
        handle_content(
            "REST API",
            api.rest_api_url,
            rest_api, rest_api_raw, rest_api_link
        )

    if rest_openapi or rest_openapi_raw or rest_openapi_link:
        handle_content(
            "OpenAPI Specification",
            api._urls['rest_openapi'],
            rest_openapi, rest_openapi_raw, rest_openapi_link,
            api.get_openapi_spec,
            is_json=True
        )

    if rest_ui or rest_ui_raw or rest_ui_link:
        handle_content(
            "Swagger UI",
            api.rest_ui_url,
            rest_ui, rest_ui_raw, rest_ui_link,
            api.get_documentation_html
        ) 