# Working with Layer 1: Communications Layer

## Overview
Layer 1 handles device communication via HTTP/HTTPS. It's designed to be stable and provide a consistent interface to Layer 2 while isolating transport-level concerns.

## Key Components & Responsibilities

### `DeviceClient`
- Central request coordinator
- Manages connection pooling via `requests.Session`
- Translates network exceptions to `TransportResponse`
- Ensures thread-safe operation for concurrent requests

### `TransportResponse`
- Wraps HTTP responses or errors
- Provides `.is_success`, `.raw_response`, and `.error` properties
- Never throws exceptions - all errors are contained in the response
- Immutable dataclass with factory methods for creation from response or error

### `DeviceEndpoint`
- Defines HTTP method and path for API endpoints
- Handles URL construction including query parameters
- Normalizes paths to ensure consistent format

### `AuthHandler`
- Applies authentication to requests
- Supports Basic and Digest authentication
- Features AUTO mode that automatically detects and uses the correct method
- Caches detected authentication method for subsequent requests

### `ProtocolHandler`
- Manages HTTP vs HTTPS protocol selection
- Handles SSL/TLS configuration and certificate verification
- Implements certificate pinning for enhanced security
- Supports custom CA certificates and client certificates for mutual TLS

### `DeviceConfig`
- Contains connection parameters (host, port, protocol)
- Stores authentication credentials
- Configures SSL/TLS behavior
- Provides factory methods (`http()`, `https()`) for simplified configuration

## Critical Implementation Details

### Request Flow
1. `DeviceClient.request()` receives endpoint and parameters
2. URL is constructed from endpoint and config
3. Auth and protocol handlers process the request
4. Network errors are caught and wrapped in `TransportResponse`
5. Raw response is returned without any content processing

### Error Handling
- All network exceptions (timeout, connection errors) are caught
- Exceptions are converted to `TransportResponse` with `.is_success = False`
- Original exception details are preserved in `.error`
- Specific error types include `SecurityError`, `NetworkError`, and `AuthenticationError`
- Layer 1 never interprets response content or status codes semantically

### Connection Management
- Connection pooling is handled via the requests library
- Sessions are configured with:
  ```python
  adapter = requests.adapters.HTTPAdapter(
      pool_connections=10,  # Connection pools to cache
      pool_maxsize=100,     # Max connections per pool
      max_retries=0         # Retries handled at higher level
  )
  ```
- Session resources must be properly cleaned up via `close()`

### Thread Safety
- `DeviceClient` is designed to be thread-safe for concurrent requests
- Shared session state (cookies, etc.) is maintained across requests

### Security Features
- Certificate verification with options to use custom CA certificates
- Certificate pinning via fingerprint verification
- Support for client certificates (mutual TLS)
- Automatic handling of insecure connection warnings

## Extending Layer 1

When modifying Layer 1:

1. **Maintain the Interface Contract**
   - `request()` must always return a `TransportResponse`
   - Never throw exceptions from public methods
   - Don't change existing method signatures

2. **Keep Raw Access**
   - Always preserve access to the raw response
   - Don't interpret response content at this layer

3. **Critical Dependencies**
   - The `requests` library is the only major external dependency
   - Avoid adding new external dependencies