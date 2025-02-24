# Feature Development Guide

## Table of Contents
1. [Core Philosophy](#core-philosophy)
2. [Project Structure](#project-structure)
3. [Development Flow](#development-flow)
4. [Implementation Guidelines](#implementation-guidelines)
5. [Testing Strategy](#testing-strategy)
6. [Examples](#examples)

## Core Philosophy

- **Keep it Simple**: Write code that solves real problems, not theoretical ones
- **Trust Your Components**: The API and framework are designed to work - don't duplicate their validation
- **Handle Real Errors**: Focus on actual error cases that affect users
- **Clear Over Clever**: Readable code is better than clever code
- **Stay Focused**: Each component should do one thing well

## Project Structure

```
src/ax_devil_device_api/
├── features/
│   └── your_feature.py        # Feature implementation
├── examples/
│   └── your_feature_cli.py    # CLI interface
└── client.py                  # Client registration
tests/
└── features/
    └── test_your_feature.py   # Tests
```

## Development Flow

### 1. Feature Implementation

Create your feature module (`src/ax_devil_device_api/features/your_feature.py`):

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import FeatureClient
from ..core.types import FeatureResponse

@dataclass
class FeatureData:
    name: str
    value: bool

class YourFeatureClient(FeatureClient[FeatureData]):
    API_VERSION = "1.0"
    
    def do_something(self, param: str) -> FeatureResponse[FeatureData]:
        """Perform feature operation."""
        response = self._make_request("doSomething", {"param": param})
        if not response.is_success:
            return response
            
        return FeatureResponse.ok(FeatureData(
            name=response.data["name"],
            value=response.data["value"]
        ))
```

### 2. Client Registration

Add to `src/ax_devil_device_api/client.py`:

```python
from .features.your_feature import YourFeatureClient

class Client:
    @property
    def your_feature(self) -> YourFeatureClient:
        if not self._your_feature:
            self._your_feature = YourFeatureClient(self._core)
        return self._your_feature
```

### 3. CLI Implementation

Create CLI interface (`src/ax_devil_device_api/examples/your_feature_cli.py`):

```python
#!/usr/bin/env python3
import click
from .cli_core import create_client, common_options

@click.group()
@common_options
@click.pass_context
def cli(ctx, **options):
    """Manage your feature."""
    ctx.obj = options

@cli.command()
@click.argument('name')
@click.pass_context
def do_something(ctx, name):
    """Perform feature operation."""
    with create_client(**ctx.obj) as client:
        result = client.your_feature.do_something(name)
        if not result.is_success:
            click.echo(f"Error: {result.error}")
            return 1
        click.echo(f"Success: {result.data}")
        return 0
```

## Implementation Guidelines

### Error Handling

Focus on three key areas:
1. **Input Validation**: Basic parameter checks
2. **API Errors**: Handle explicit API error responses
3. **System Errors**: Handle network/connection issues

Example:
```python
def get_feature(self, name: str) -> FeatureResponse[FeatureData]:
    """Get feature by name."""
    if not name:  # Basic input validation
        return FeatureResponse.create_error("Name required")
        
    response = self._make_request("getFeature", {"name": name})
    return response  # API/system errors already handled by _make_request
```

### Response Handling

Trust the API response structure. Only validate what's necessary:
```python
def process_response(self, response: Dict[str, Any]) -> FeatureData:
    """Process API response."""
    return FeatureData(
        name=response["name"],
        value=response.get("value", False)  # Use sensible defaults
    )
```

## Testing Strategy

Focus on real use cases:

```python
def test_feature_operations(client):
    """Test main feature operations."""
    # Test success case
    result = client.your_feature.do_something("test")
    assert result.is_success
    assert result.data.name == "test"
    
    # Test API error
    result = client.your_feature.do_something("")
    assert not result.is_success
    
    # Test system error (if applicable, not needed in most cases)
    with mock_network_error():
        result = client.your_feature.do_something("test")
        assert not result.is_success
```

## Examples

See these implemented features for reference:
- `feature_flags.py`: Feature flag management
- `analytics_mqtt.py`: Analytics data publishing
- `geocoordinates.py`: Device location and orientation

Remember: The best code is the code that solves the problem without adding unnecessary complexity. 