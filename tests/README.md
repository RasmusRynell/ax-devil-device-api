# Testing Guide for ax-devil-device-api

This directory contains tests for the ax-devil-device-api library. The tests are organized into unit tests and integration tests.

## Test Structure

```
tests/
├── integration/          # Integration tests that test multiple components together
│   ├── core/             # Tests for core functionality
│   └── features/         # Tests for specific features
├── unit/                 # Unit tests for individual components
├── mocks/                # Mock implementations for testing
│   ├── device_api.py     # Mock API endpoints
│   └── http_server.py    # Mock HTTP server implementation
└── conftest.py           # Shared pytest fixtures
```

## Test Categories and Marks

We use pytest marks to categorize tests. This allows you to run specific types of tests:

### Test Types

- `integration`: Integration tests that test multiple components together
- `unit`: Unit tests for individual components

### Protocol Types

- `http`: Tests for HTTP functionality
- `https`: Tests for HTTPS functionality

### Feature Categories

- `basic_operation`: Tests for basic HTTP operations (GET, POST, PUT, DELETE)
- `session`: Tests for session management
- `auth`: Tests for authentication functionality
- `error`: Tests for error handling
- `concurrency`: Tests for concurrent operations
- `transport`: Tests for the transport layer

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Run Only HTTP Tests

```bash
pytest -m http
```

### Run Only Authentication Tests

```bash
pytest -m auth
```

### Run Tests with Multiple Marks

```bash
pytest -m "http and auth"  # Run HTTP authentication tests
pytest -m "https and error"  # Run HTTPS error handling tests
```

## Mock HTTP Server

The `tests/mocks` package provides a mock HTTP server implementation that simulates a device API. This is used by the integration tests to verify that the client correctly handles different scenarios.

Key components:

- `ThreadedHTTPServer`: A threaded HTTP server that can handle concurrent requests
- `MockDeviceHandler`: A request handler that simulates device API behavior
- `get_standard_routes()`: A function that returns a dictionary of standard API routes

## Fixtures

Fixtures are defined in `conftest.py` and provide common test setup:

- `mock_server`: Starts a mock HTTP server
- `mock_https_server`: Starts a mock HTTPS server
- `http_client`: Creates a TransportClient configured for HTTP
- `https_client`: Creates a TransportClient configured for HTTPS
- `reset_mock_handler`: Resets the mock handler state before each test (automatically applied) 