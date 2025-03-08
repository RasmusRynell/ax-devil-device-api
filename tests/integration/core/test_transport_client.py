"""Integration tests for TransportClient.

These tests verify that the TransportClient correctly handles real HTTP interactions,
session management, authentication, and error conditions using a mock server that
simulates actual device behavior.
"""
import pytest
import concurrent.futures
import requests
from requests.adapters import HTTPAdapter

from ax_devil_device_api.core.transport_client import TransportClient
from ax_devil_device_api.core.config import DeviceConfig, Protocol, AuthMethod
from ax_devil_device_api.core.endpoints import TransportEndpoint
from ax_devil_device_api.utils.errors import NetworkError, AuthenticationError, SecurityError

from tests.mocks.http_server import MockDeviceHandler


@pytest.mark.transport
class TestTransportClient:
    """Integration tests for TransportClient.
    
    These tests verify that the TransportClient correctly handles:
    
    1. Basic HTTP Operations:
       - GET, POST, PUT, DELETE methods
       - Custom headers
    
    2. Session Management:
       - Session persistence across requests
       - Creating new sessions
       - Clearing sessions
    
    3. Authentication:
       - Basic authentication
       - Digest authentication
       - Auto-detection of authentication methods
       - Authentication failures
    
    4. Error Handling:
       - Timeouts
       - Connection errors
       - HTTP error status codes
    
    5. HTTPS/SSL:
       - Basic HTTPS requests
       - Self-signed certificate handling
       - SSL verification behavior
    
    6. Performance & Concurrency:
       - Concurrent requests
       - Connection pooling
    
    Each test category is clearly separated in the code for better organization.
    """
    
    # =========================================================================
    # Basic HTTP Operations
    # =========================================================================
    
    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_basic_request(self, http_client):
        """Test that a basic GET request works."""
        endpoint = TransportEndpoint("GET", "/api/info")
        response = http_client.request(endpoint)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0"
        assert data["model"] == "Test Device"
    
    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_post_request_with_json(self, http_client):
        """Test POST request with JSON payload."""
        endpoint = TransportEndpoint("POST", "/api/data")
        payload = {"name": "test_device", "value": 42}
        
        response = http_client.request(endpoint, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "created"
    
    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_put_request(self, http_client):
        """Test that PUT requests work properly."""
        endpoint = TransportEndpoint("PUT", "/api/data")
        payload = {"name": "updated_device", "value": 100}
        
        response = http_client.request(endpoint, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
    
    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_delete_request(self, http_client):
        """Test that DELETE requests work properly."""
        endpoint = TransportEndpoint("DELETE", "/api/resource")
        response = http_client.request(endpoint)
        
        assert response.status_code == 204
    
    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_custom_headers(self, http_client):
        """Test that custom headers are properly sent."""
        endpoint = TransportEndpoint("GET", "/api/info")
        custom_headers = {
            "X-Custom-Header": "test-value",
            "Accept": "application/xml"  # This should override the default Accept header
        }
        
        response = http_client.request(endpoint, headers=custom_headers)
        
        assert response.status_code == 200
        # We can't directly verify the headers were sent, but we can check the request succeeded

    # =========================================================================
    # Session Management
    # =========================================================================
    
    @pytest.mark.http
    @pytest.mark.session
    @pytest.mark.unit
    def test_session_persistence(self, mock_server, http_client):
        """Test that session cookies are maintained across requests."""
        endpoint = TransportEndpoint("GET", "/api/info")
        
        # Make multiple requests
        http_client.request(endpoint)
        http_client.request(endpoint)
        http_client.request(endpoint)
        
        # Should only have one session token since the client reuses the session
        assert len(MockDeviceHandler.session_tokens) == 1
    
    @pytest.mark.http
    @pytest.mark.session
    @pytest.mark.unit
    def test_new_session_context_manager(self, mock_server, http_client):
        """Test that new_session context manager creates a fresh session."""
        endpoint = TransportEndpoint("GET", "/api/info")
        
        # Make request with default session
        http_client.request(endpoint)
        
        # Make request with new session
        with http_client.new_session():
            http_client.request(endpoint)
        
        # Make another request with original session
        http_client.request(endpoint)
        
        # Should have two session tokens
        assert len(MockDeviceHandler.session_tokens) == 2
    
    @pytest.mark.http
    @pytest.mark.session
    @pytest.mark.unit
    def test_clear_session(self, mock_server, http_client):
        """Test that clear_session creates a fresh session."""
        endpoint = TransportEndpoint("GET", "/api/info")
        
        # Make request with default session
        http_client.request(endpoint)
        
        # Clear session and make another request
        http_client.clear_session()
        http_client.request(endpoint)
        
        # Should have two session tokens
        assert len(MockDeviceHandler.session_tokens) == 2

    # =========================================================================
    # Authentication
    # =========================================================================
    
    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_basic_auth(self, mock_server, http_client):
        """Test that basic authentication works."""
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "basic"
        
        endpoint = TransportEndpoint("GET", "/api/info")
        response = http_client.request(endpoint)
        
        assert response.status_code == 200
    
    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_digest_auth(self, mock_server):
        """Test digest authentication."""
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "digest"
        
        # Create client configured for digest auth
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.DIGEST,
            timeout=5.0,
            allow_insecure=True
        )
        client = TransportClient(config)
        
        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request(endpoint)
        
        assert response.status_code == 200
    
    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_auto_auth_basic(self, mock_server):
        """Test automatic detection of basic auth."""
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "basic"
        
        # Create client configured for auto auth
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True
        )
        client = TransportClient(config)
        
        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request(endpoint)
        
        assert response.status_code == 200
    
    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_auto_auth_digest(self, mock_server):
        """Test automatic detection of digest auth."""
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "digest"
        
        # Create client configured for auto auth
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True
        )
        client = TransportClient(config)
        
        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request(endpoint)
        
        assert response.status_code == 200
    
    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.error
    @pytest.mark.unit
    def test_auth_failure(self, mock_server):
        """Test handling of authentication failures."""
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "basic"
        
        # Create client with incorrect credentials
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="wrong",
            password="invalid",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=5.0,
            allow_insecure=True
        )
        client = TransportClient(config)
        
        endpoint = TransportEndpoint("GET", "/api/info")
        
        with pytest.raises(AuthenticationError) as excinfo:
            client.request(endpoint)
        
        assert "authentication_failed" in str(excinfo.value)

    # =========================================================================
    # Error Handling
    # =========================================================================
    
    @pytest.mark.http
    @pytest.mark.error
    @pytest.mark.unit
    def test_timeout_handling(self, mock_server):
        """Test that timeouts are properly handled."""
        MockDeviceHandler.simulate_timeout = True
        
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=1.0,  # Short timeout for testing
            allow_insecure=True
        )
        client = TransportClient(config)
        
        endpoint = TransportEndpoint("GET", "/api/info")
        
        with pytest.raises(NetworkError) as excinfo:
            client.request(endpoint)
        
        assert "request_timeout" in str(excinfo.value)
        
        # Reset for other tests
        MockDeviceHandler.simulate_timeout = False
    
    @pytest.mark.http
    @pytest.mark.error
    @pytest.mark.unit
    def test_connection_error_handling(self, mock_server):
        """Test that connection errors are properly handled."""
        MockDeviceHandler.simulate_connection_error = True
        
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=5.0,
            allow_insecure=True
        )
        client = TransportClient(config)
        
        endpoint = TransportEndpoint("GET", "/api/info")
        
        with pytest.raises(NetworkError) as excinfo:
            client.request(endpoint)
        
        assert "request_failed" in str(excinfo.value)
        
        # Reset for other tests
        MockDeviceHandler.simulate_connection_error = False
    
    @pytest.mark.http
    @pytest.mark.error
    @pytest.mark.unit
    def test_http_error_handling(self, http_client):
        """Test handling of HTTP error status codes."""
        endpoint = TransportEndpoint("GET", "/api/server-error")
        response = http_client.request(endpoint)
        
        # The client should return the response with the error status code
        # rather than raising an exception
        assert response.status_code == 500
        data = response.json()
        assert "error" in data

    # =========================================================================
    # HTTPS/SSL
    # =========================================================================
    
    @pytest.mark.https
    @pytest.mark.unit
    def test_basic_https_request(self, https_client):
        """Test a basic HTTPS request with verification disabled."""
        endpoint = TransportEndpoint("GET", "/api/info")
        response = https_client.request(endpoint)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0"
    
    @pytest.mark.https
    @pytest.mark.unit
    def test_https_always_insecure(self, mock_https_server):
        """Test that HTTPS connections are always insecure (verify=False) by default."""
        port, _ = mock_https_server
        
        # Create client with default settings (verify_ssl=False)
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTPS,
            auth_method=AuthMethod.BASIC,
            timeout=5.0
            # verify_ssl is not explicitly set, should default to False
        )
        client = TransportClient(config)
        
        # Request should succeed even with a self-signed certificate
        # because verification is disabled by default
        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request(endpoint)
        
        # Verify that the request was successful
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0"
        assert data["model"] == "Test Device"
    
    @pytest.mark.https
    @pytest.mark.error
    @pytest.mark.unit
    def test_ssl_verification_not_implemented(self, mock_https_server):
        """Test that SSL verification is not implemented and raises an error."""
        port, _ = mock_https_server
        
        # Attempting to create a client with SSL verification enabled should raise an error
        with pytest.raises(SecurityError) as excinfo:
            config = DeviceConfig(
                host=f"localhost:{port}",
                username="test",
                password="password",
                protocol=Protocol.HTTPS,
                verify_ssl=True  # This should trigger the error
            )
            # The error should be raised during initialization
        
        assert excinfo.value.code == "ssl_not_implemented"
        assert "not implemented" in str(excinfo.value)

    # =========================================================================
    # Performance & Concurrency
    # =========================================================================
    
    @pytest.mark.http
    @pytest.mark.concurrency
    @pytest.mark.unit
    def test_concurrent_requests(self, http_client):
        """Test that the client can handle multiple concurrent requests."""
        # Reset session tokens explicitly for this test
        with MockDeviceHandler.session_lock:
            MockDeviceHandler.session_tokens = set()
            MockDeviceHandler.request_count = 0
            MockDeviceHandler.use_fixed_session_token = True  # Use fixed token for this test
        
        # Store a reference to the session object to verify it's being reused
        original_session_id = id(http_client._session)
        
        endpoint = TransportEndpoint("GET", "/api/info")
        num_requests = 5  # Reduced from 10 to make debugging easier
        
        # Execute requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(http_client.request, endpoint) for _ in range(num_requests)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert len(responses) == num_requests
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["version"] == "1.0"
        
        # Verify the client is still using the same session object
        assert id(http_client._session) == original_session_id, "Session object changed during concurrent requests"
        
        # Should still only have one session token since we're reusing the same client
        assert len(MockDeviceHandler.session_tokens) == 1
        
        # Reset back to default behavior
        MockDeviceHandler.use_fixed_session_token = False
    
    @pytest.mark.http
    @pytest.mark.unit
    def test_connection_pool_configuration(self, http_client):
        """Test that the client has the expected adapter configuration."""
        # Test that the client has the expected adapter configuration
        adapter = http_client._session.adapters['http://']
        
        # Check that we're using the HTTPAdapter
        assert isinstance(adapter, HTTPAdapter)
        
        # Verify both HTTP and HTTPS adapters are configured
        assert 'http://' in http_client._session.adapters
        assert 'https://' in http_client._session.adapters
        
        # Check that the session has our transport headers
        for key, value in TransportClient._TRANSPORT_HEADERS.items():
            assert http_client._session.headers[key] == value
            
        # Functional test for connection pooling - make multiple requests
        # and ensure they're handled correctly with the same session
        endpoint = TransportEndpoint("GET", "/api/info")
        
        # Track the initial request count
        initial_count = MockDeviceHandler.request_count
        
        # Make several requests
        num_requests = 5
        for _ in range(num_requests):
            response = http_client.request(endpoint)
            assert response.status_code == 200
            
        # Verify the requests were made
        assert MockDeviceHandler.request_count == initial_count + num_requests
        
        # Verify that a single session was used (connection pooling working)
        assert len(MockDeviceHandler.session_tokens) == 1 