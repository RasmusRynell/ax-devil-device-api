# Feature Development Guide

## CRITICAL WARNING - READ FIRST
```
NEVER MODIFY EXISTING PROJECT ARCHITECTURE OR BASE CLASSES!
Your scope is LIMITED to:
1. Creating your new feature file(s)
2. Adding ONE import line to client.py and wire it up to the client in the __init__ method
3. Adding ONE entry point to pyproject.toml

If you think there are issues with the core architecture:
- Create a separate issue/PR
- Do NOT modify core files while implementing features
- Do NOT try to "fix" working code
```

## Required Steps for Adding a New Feature

### 1. Create Feature Module
Create a new file `src/ax_devil_device_api/features/your_feature.py`:

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import FeatureClient
from ..core.types import FeatureResponse, FeatureError
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError


@dataclass
class YourFeatureData:
    """Define your feature's data structure.
    REQUIRED: Add all fields your feature needs."""
    field_one: str
    field_two: int

class YourFeatureClient(FeatureClient[YourFeatureData]):
    """REQUIRED: Set your feature's API version."""
    API_VERSION = "1.0"
    
    """REQUIRED: Define your feature's endpoint."""
    ENDPOINT = DeviceEndpoint("POST", "/axis-cgi/your_endpoint.cgi")
    
    def _make_request(self, method: str, params: Optional[Dict] = None) -> FeatureResponse[Dict]:
        """Handles the standard API request format."""
        payload = {
            "apiVersion": self.API_VERSION,
            "method": method
        }
        if params:
            payload["params"] = params
            
        response = self.request(
            self.ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return response
        
    def your_method(self, param: str) -> FeatureResponse[YourFeatureData]:
        """REQUIRED: Implement at least one feature method."""
        if not param:
            return FeatureResponse.create_error(FeatureError("parameter_required", "Parameter required"))
            
        response = self._make_request("yourMethod", {"param": param}) # if multiple requests can be made in the same way. Not required. 
        if not response.is_success:
            return response
            
        return FeatureResponse.ok(YourFeatureData(
            field_one=response.data["fieldOne"],
            field_two=response.data["fieldTwo"]
        ))
```

### 2. Register in Client
Add to `src/ax_devil_device_api/client.py`:

```python
# REQUIRED: Add import
from ax_devil_device_api.features.your_feature import YourFeatureClient

class Client:
    def __init__(self):
        # REQUIRED: Add instance variable
        self._your_feature: Optional[YourFeatureClient] = None

    # REQUIRED: Add property
    @property
    def your_feature(self) -> YourFeatureClient:
        if not self._your_feature:
            self._your_feature = YourFeatureClient(self._core)
        return self._your_feature
```

### 3. Create CLI Interface
Create `src/ax_devil_device_api/examples/your_feature_cli.py`:

```python
#!/usr/bin/env python3
# REQUIRED: Standard imports
import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options, format_json
)

# REQUIRED: Main CLI group
@click.group()
@common_options
@click.pass_context
def cli(ctx, device_ip, username, password, port, protocol, no_verify_ssl, ca_cert, debug):
    """Manage your feature."""
    ctx.ensure_object(dict)
    ctx.obj.update({
        'device_ip': device_ip,
        'username': username,
        'password': password,
        'port': port,
        'protocol': protocol,
        'no_verify_ssl': no_verify_ssl,
        'ca_cert': ca_cert,
        'debug': debug
    })

# REQUIRED: At least one command
@cli.command()
@click.argument('param')
@click.pass_context
def your_command(ctx, param):
    """Command description."""
    with create_client(**get_client_args(ctx.obj)) as client:
        result = client.your_feature.your_method(param)
        if not result.is_success:
            return handle_error(ctx, result.error)
        
        # IMPORTANT:
        # There are many ways to print the result.
        # You can either return the result or print it yourself.
        # See examples below:
        # click.echo(format_json(result.data))
        # or
        # click.echo(result.data)
        # or
        # click.echo(f"Success: {result.data}")
        # or
        # click.echo(f"Error: {result.error}")
        # And then return 0 or 1 to indicate success or failure.
        # or if you don't care about handling the result yourself, you can just return handle_result(ctx, result)

if __name__ == '__main__':
    cli()
```

### 4. Add Tests
IMPORTANT: MAKE SURE ALL TESTS CLEAN UP AFTER THEMSELVES.

Create `tests/features/test_your_feature.py`:

```python
import pytest
from ax_devil_device_api.features.your_feature import YourFeatureClient, YourFeatureData

# REQUIRED: Basic test cases
def test_your_method(client):
    """REQUIRED: Test your main method."""
    result = client.your_feature.your_method("test")
    assert result.is_success
    assert isinstance(result.data, YourFeatureData)
    assert result.data.field_one == "expected"
    assert result.data.field_two == 42

def test_invalid_input(client):
    """REQUIRED: Test basic error case."""
    result = client.your_feature.your_method("")
    assert not result.is_success
```

### 5. Update Setup
Add to `pyproject.toml` or `setup.py`:

```toml
[project.scripts]
ax-devil-device-api-your-feature = "ax_devil_device_api.examples.your_feature_cli:cli"
```

## Checklist

Before submitting your feature:

- [ ] Feature module created with required components
  - [ ] Data model with all needed fields
  - [ ] Client class with API_VERSION and ENDPOINT
  - [ ] At least one feature method
  
- [ ] Client registration complete
  - [ ] Import added
  - [ ] Instance variable added
  - [ ] Property getter added
  
- [ ] CLI interface implemented
  - [ ] Main group with common options
  - [ ] At least one command
  - [ ] Error handling in place
  
- [ ] Tests written
  - [ ] Success case tested
  - [ ] Error case tested
  
- [ ] Setup updated
  - [ ] CLI script entry point added

## Common API Response Format

All API responses follow this structure:
```json
{
    "apiVersion": "1.0",
    "method": "methodName",
    "data": {
        // Your response data here
        "fieldOne": "value",
        "fieldTwo": 42
    }
}
```

## Error Handling Requirements

1. **Always check**:
   - Empty/invalid input parameters
   - API response success (`response.is_success`)
   - Required response fields present

2. **Don't check**:
   - API version in responses (handled by core)
   - HTTP status codes (handled by core)
   - Response format (handled by core)

## Examples

See these complete implementations:
- `feature_flags.py`: Simple boolean flags
- `analytics_mqtt.py`: Data publishing
- `geocoordinates.py`: Location data

Need help? Ask about:
1. API endpoint details
2. Response format for your feature
3. Required fields for your data model