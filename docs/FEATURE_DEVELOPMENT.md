# Feature Development Guide

This guide explains how to add new features to the ax-devil-device-api project, following our three-layer architecture and SOLID principles.

## Overview

Adding a new feature requires implementing three main components:
1. Feature Module (Layer 2)
2. Feature Tests
3. CLI Interface (Layer 3)

## 1. Feature Module Implementation

### Location
```
src/ax_devil_device_api/features/your_feature.py
```

### Structure
```python
from dataclasses import dataclass
from typing import Optional, Dict, List
from .base import FeatureClient
from ..core.types import TransportResponse, FeatureResponse
from ..core.endpoints import CameraEndpoint
from ..utils.errors import FeatureError

@dataclass
class YourFeatureInfo:
    """Information returned by your feature.
    
    Attributes:
        field1: Description of field 1
        field2: Description of field 2
        optional_field: Optional field description
    """
    field1: str
    field2: List[str]
    optional_field: Optional[int] = None

    @classmethod
    def from_params(cls, params: Dict[str, str]) -> 'YourFeatureInfo':
        """Create instance from parameter dictionary."""
        def get_param(key: str, default: str = "unknown") -> str:
            return params.get(f"YourFeature.{key}", params.get(key, default))
            
        return cls(
            field1=get_param("Field1"),
            field2=[x for x in get_param("Field2").split(",") if x],
            optional_field=int(get_param("OptionalField", "0")) if get_param("OptionalField", "0").isdigit() else None
        )

class YourFeatureClient(FeatureClient):
    """Client for your feature operations."""
    
    # Define endpoints
    PARAMS_ENDPOINT = CameraEndpoint("GET", "/axis-cgi/param.cgi")
    ACTION_ENDPOINT = CameraEndpoint("POST", "/axis-cgi/action.cgi")
    
    def get_info(self) -> FeatureResponse[YourFeatureInfo]:
        """Get feature information.
        
        Returns:
            FeatureResponse containing the feature information
        """
        response = self.request(
            self.PARAMS_ENDPOINT,
            params={"action": "list", "group": "YourFeature"},
            headers={"Accept": "text/plain"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        raw_response = response.raw_response
        if raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "invalid_response",
                f"Invalid response: HTTP {raw_response.status_code}"
            ))
            
        try:
            lines = raw_response.text.strip().split('\n')
            params = dict(line.split('=', 1) for line in lines if '=' in line)
            return FeatureResponse.ok(YourFeatureInfo.from_params(params))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_error",
                f"Failed to parse response: {str(e)}"
            ))
            
    def perform_action(self, action: str) -> FeatureResponse[bool]:
        """Perform a feature action.
        
        Args:
            action: Action to perform
            
        Returns:
            FeatureResponse indicating success/failure
        """
        response = self.request(
            self.ACTION_ENDPOINT,
            params={"action": action}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "action_failed",
                f"Action failed: HTTP {response.raw_response.status_code}"
            ))
            
        return FeatureResponse.ok(True)

### Adding to Client
The feature needs to be integrated into `src/ax_devil_device_api/client.py`. Follow these steps:

1. Import your feature client at the top:
```python
from .features.your_feature import YourFeatureClient
```

2. Add a private attribute for lazy loading:
```python
class Client:
    def __init__(self, config: CameraConfig) -> None:
        self._core = CameraClient(config)
        # ... other features ...
        self._your_feature: Optional[YourFeatureClient] = None
```

3. Add a property accessor that implements lazy loading:
```python
    @property
    def your_feature(self) -> YourFeatureClient:
        """Access your feature operations."""
        if not self._your_feature:
            self._your_feature = YourFeatureClient(self._core)
        return self._your_feature
```

The feature will then be accessible through the client as:
```python
client = Client(config)
result = client.your_feature.your_operation()
```

Note: Features are lazy-loaded, meaning they are only instantiated when first accessed through their property.

## 2. Feature Tests

### Location
```
tests/features/test_your_feature.py
```

### Structure
```python
"""Tests for your feature operations."""

import pytest
from ax_devil_device_api.features.your_feature import YourFeatureConfig
from ax_devil_device_api.utils.errors import FeatureError

class TestYourFeature:
    """Test suite for your feature."""
    
    def test_operation_default(self, client):
        """Test operation with default settings."""
        response = client.your_feature.your_operation()
        assert response.success, f"Operation failed: {response.error}"
        self._verify_response_data(response.data)
        
    def test_operation_with_config(self, client):
        """Test operation with custom configuration."""
        config = YourFeatureConfig(
            param1="value1",
            param2=42
        )
        response = client.your_feature.your_operation(config)
        assert response.success, f"Operation failed: {response.error}"
        self._verify_response_data(response.data)
        
    def test_invalid_config(self, client):
        """Test error handling for invalid configuration."""
        config = YourFeatureConfig(param1="")  # Invalid: empty param1
        response = client.your_feature.your_operation(config)
        assert not response.success
        assert response.error.code == "invalid_config"
        assert "param1" in response.error.details["error"]
        
    def test_transport_error(self, client):
        """Test handling of transport-level errors."""
        # Simulate transport error (implementation depends on your testing setup)
        response = client.your_feature.your_operation()
        if not response.success and response.error.code == "transport_error":
            assert "Failed to connect" in response.error.message
        
    def test_config_validation(self):
        """Test configuration validation logic."""
        # Valid configurations
        valid_configs = [
            YourFeatureConfig(param1="valid"),
            YourFeatureConfig(param1="valid", param2=42)
        ]
        for config in valid_configs:
            assert config.validate() is None, f"Valid config failed validation: {config}"
            
        # Invalid configurations
        invalid_configs = [
            (YourFeatureConfig(param1=""), "param1 is required"),
            (YourFeatureConfig(param1="valid", param2=-1), "must be non-negative")
        ]
        for config, expected_error in invalid_configs:
            error = config.validate()
            assert error is not None, f"Invalid config passed validation: {config}"
            assert expected_error in error
            
    def _verify_response_data(self, data: T):
        """Helper to verify response data structure and content."""
        # Add specific verification logic based on expected response type
        assert data is not None
        # Add more specific checks based on your data type
```

## 3. CLI Interface

### Location
```
src/ax_devil_device_api/examples/your_feature_cli.py
```

### Structure
```python
#!/usr/bin/env python3
import click
from .cli_core import (
    create_client, handle_result, handle_error, get_client_args,
    common_options
)
from ..features.your_feature import YourFeatureConfig


@click.group()
@common_options
@click.pass_context
def cli(ctx, camera_ip, username, password, port, protocol, no_verify_ssl, debug):
    """Manage your feature operations for an Axis camera.

    When using HTTPS (default), the camera must have a valid SSL certificate. For cameras with
    self-signed certificates, use the --no-verify-ssl flag to disable certificate verification.
    """
    ctx.ensure_object(dict)
    ctx.obj.update({
        'camera_ip': camera_ip,
        'username': username,
        'password': password,
        'port': port,
        'protocol': protocol,
        'no_verify_ssl': no_verify_ssl,
        'debug': debug
    })


@cli.command('operation')
@click.option('--param1', help='Description of parameter 1')
@click.option('--param2', type=int, help='Description of parameter 2')
@click.option('--output', '-o', type=click.Path(dir_okay=False),
              help='Optional output file path')
@click.pass_context
def operation(ctx, param1, param2, output):
    """Perform your feature operation."""
    try:
        client = create_client(**get_client_args(ctx.obj))
        
        config = None
        if any(x is not None for x in (param1, param2)):
            config = YourFeatureConfig(
                param1=param1,
                param2=param2
            )
        
        result = client.your_feature.your_operation(config)
        
        # If HTTPS fails, try HTTP fallback
        if not result.success and result.error.code == "ssl_error":
            click.echo("HTTPS connection failed, trying HTTP fallback...", err=True)
            ctx.obj['protocol'] = 'http'
            client = create_client(**get_client_args(ctx.obj))
            result = client.your_feature.your_operation(config)
            
        if result.success and output:
            try:
                with open(output, 'wb') as f:
                    f.write(result.data)
                click.echo(f"Result saved to {output}")
                return 0
            except IOError as e:
                return handle_error(ctx, f"Failed to save output: {e}")
                
        return handle_result(ctx, result)
    except Exception as e:
        return handle_error(ctx, e)


if __name__ == '__main__':
    cli()
```

### Adding to pyproject.toml
In the `[project.scripts]` section:
```toml
[project.scripts]
ax-devil-device-api-your-feature = "ax_devil_device_api.examples.your_feature_cli:cli"
```

## Best Practices

1. **Feature Module**
   - Follow Single Responsibility Principle
   - Use proper type hints and generics
   - Implement comprehensive validation
   - Handle all error cases with proper details
   - Document all public interfaces
   - Use properties for feature names

2. **Tests**
   - Test both success and failure paths
   - Include transport error tests
   - Validate error details
   - Use specific verification helpers
   - Follow existing test patterns

3. **CLI**
   - Keep commands focused and simple
   - Handle file output consistently
   - Provide clear error messages
   - Include SSL fallback handling
   - Follow existing CLI patterns

## Integration Checklist

- [ ] Feature module created in correct location
- [ ] Feature uses proper type hints and generics
- [ ] Feature added to AxisClient
- [ ] Tests cover all error cases
- [ ] CLI matches existing patterns
- [ ] CLI added to pyproject.toml
- [ ] Documentation updated
- [ ] Error handling includes details
- [ ] Code formatted according to project standards 