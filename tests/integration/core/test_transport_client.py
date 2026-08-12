"""Integration tests for TransportClient.

These tests verify that the TransportClient correctly handles real HTTP interactions,
session management, authentication, and error conditions using a mock server that
simulates actual device behavior.
"""

import concurrent.futures
import json
from unittest.mock import Mock, patch

import pytest
import requests
from requests.adapters import HTTPAdapter

from src.ax_devil_device_api.core.config import AuthMethod, DeviceConfig, Protocol
from src.ax_devil_device_api.core.debug import emit_request_debug_info
from src.ax_devil_device_api.core.endpoints import TransportEndpoint
from src.ax_devil_device_api.core.transport_client import TransportClient
from src.ax_devil_device_api.features.api_discovery import ClassicAPIDiscoveryClient
from src.ax_devil_device_api.utils.errors import (
    AuthenticationError,
    FeatureError,
    NetworkError,
)
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
    def test_request_debug_callback_includes_request_details(self, mock_server):
        """Test that authenticated requests emit request details to the debug callback."""
        captured_requests = []
        _, port = mock_server

        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=5.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)

        endpoint = TransportEndpoint("POST", "/api/data")
        payload = {"name": "test_device", "value": 42}

        response = client.request(
            endpoint,
            params={"mode": "fast"},
            json=payload,
            headers={"X-Debug-Test": "true"},
        )

        assert response.status_code == 201
        assert len(captured_requests) == 2
        assert captured_requests[0]["request"]["method"] == "POST"
        assert (
            captured_requests[0]["request"]["url"]
            == f"http://localhost:{port}/api/data?mode=fast"
        )
        assert captured_requests[0]["request"]["params"] == {"mode": "fast"}
        assert captured_requests[0]["request"]["json"] == payload
        assert captured_requests[0]["request"]["headers"]["X-Debug-Test"] == "true"
        assert captured_requests[0]["settings"] == {"timeout": 5.0, "ssl_verify": False}

    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_request_debug_callback_for_no_auth_requests(self, mock_server):
        """Test that unauthenticated requests emit request details to the debug callback."""
        captured_requests = []
        _, port = mock_server
        MockDeviceHandler.auth_required = False

        config = DeviceConfig(
            host=f"localhost:{port}",
            username="",
            password="",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=5.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)

        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request_no_auth(endpoint, params={"detail": "short"})

        assert response.status_code == 200
        assert len(captured_requests) == 1
        assert captured_requests[0]["request"]["method"] == "GET"
        assert (
            captured_requests[0]["request"]["url"]
            == f"http://localhost:{port}/api/info?detail=short"
        )
        assert captured_requests[0]["request"]["params"] == {"detail": "short"}
        assert captured_requests[0]["request"]["json"] is None
        assert captured_requests[0]["settings"] == {"timeout": 5.0, "ssl_verify": False}

    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_explicit_timeout_is_passed_to_authenticated_request(self, mock_server):
        """An explicit timeout reaches the underlying authenticated session request."""
        _, port = mock_server
        captured_requests = []
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=10.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)
        response = Mock(status_code=200)

        with patch.object(client._session, "request", return_value=response) as request:
            result = client.request(TransportEndpoint("GET", "/api/info"), timeout=2.5)

        assert result is response
        assert request.call_args.kwargs["timeout"] == 2.5
        assert captured_requests[0]["settings"]["timeout"] == 2.5

    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_explicit_timeout_is_passed_to_challenge_retry(self, mock_server):
        """An explicit timeout reaches the authenticated challenge retry."""
        _, port = mock_server
        captured_requests = []
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=10.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)
        challenge_response = Mock(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Device API"'},
        )
        response = Mock(status_code=200)

        with patch.object(client._session, "request", return_value=response) as request:
            result = client.request_after_challenge(
                TransportEndpoint("GET", "/api/info"),
                challenge_response,
                timeout=2.5,
            )

        assert result is response
        assert request.call_args.kwargs["timeout"] == 2.5
        assert captured_requests[0]["settings"]["timeout"] == 2.5
        challenge_response.close.assert_called_once()

    @pytest.mark.http
    @pytest.mark.basic_operation
    @pytest.mark.unit
    def test_explicit_timeout_is_passed_to_no_auth_request(self, mock_server):
        """An explicit timeout reaches the temporary no-auth session request."""
        _, port = mock_server
        captured_requests = []
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="",
            password="",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=10.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)
        response = Mock(status_code=200)

        with patch.object(
            requests.Session, "request", return_value=response
        ) as request:
            result = client.request_no_auth(
                TransportEndpoint("GET", "/api/info"), timeout=2.5
            )

        assert result is response
        assert request.call_args.kwargs["timeout"] == 2.5
        assert captured_requests[0]["settings"]["timeout"] == 2.5

    @pytest.mark.http
    @pytest.mark.error
    @pytest.mark.unit
    def test_explicit_timeout_is_reported_for_authenticated_timeout(self, mock_server):
        """Authenticated timeout errors use the explicit effective timeout."""
        _, port = mock_server
        captured_requests = []
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=10.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)

        with (
            patch.object(
                client._session, "request", side_effect=requests.exceptions.Timeout
            ) as request,
            pytest.raises(NetworkError, match="Request timed out after 2.5s"),
        ):
            client.request(TransportEndpoint("GET", "/api/info"), timeout=2.5)

        assert request.call_args.kwargs["timeout"] == 2.5
        assert captured_requests[0]["settings"]["timeout"] == 2.5

    @pytest.mark.http
    @pytest.mark.error
    @pytest.mark.unit
    def test_explicit_timeout_is_reported_for_challenge_retry_timeout(
        self, mock_server
    ):
        """Challenge-retry timeout errors use the explicit effective timeout."""
        _, port = mock_server
        captured_requests = []
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=10.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)
        challenge_response = Mock(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Device API"'},
        )

        with (
            patch.object(
                client._session, "request", side_effect=requests.exceptions.Timeout
            ) as request,
            pytest.raises(NetworkError, match="Request timed out after 2.5s"),
        ):
            client.request_after_challenge(
                TransportEndpoint("GET", "/api/info"),
                challenge_response,
                timeout=2.5,
            )

        assert request.call_args.kwargs["timeout"] == 2.5
        assert captured_requests[0]["settings"]["timeout"] == 2.5
        challenge_response.close.assert_called_once()

    @pytest.mark.http
    @pytest.mark.error
    @pytest.mark.unit
    def test_explicit_timeout_is_reported_for_no_auth_timeout(self, mock_server):
        """No-auth timeout errors use the explicit effective timeout."""
        _, port = mock_server
        captured_requests = []
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="",
            password="",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.BASIC,
            timeout=10.0,
            allow_insecure=True,
            debug_request_callback=captured_requests.append,
        )
        client = TransportClient(config)

        with (
            patch.object(
                requests.Session, "request", side_effect=requests.exceptions.Timeout
            ) as request,
            pytest.raises(NetworkError, match="Request timed out after 2.5s"),
        ):
            client.request_no_auth(TransportEndpoint("GET", "/api/info"), timeout=2.5)

        assert request.call_args.kwargs["timeout"] == 2.5
        assert captured_requests[0]["settings"]["timeout"] == 2.5

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
            "Accept": "application/xml",  # This should override the default Accept header
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
            allow_insecure=True,
        )
        client = TransportClient(config)

        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request(endpoint)

        assert response.status_code == 200
        assert len(MockDeviceHandler.request_records) == 2
        assert "Authorization" not in MockDeviceHandler.request_records[0]["headers"]
        assert MockDeviceHandler.request_records[1]["headers"][
            "Authorization"
        ].startswith("Digest ")

    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_auto_auth_basic(self, mock_server):
        """AUTO selects Basic only after the server advertises it."""
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
            allow_insecure=True,
        )
        client = TransportClient(config)

        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request(endpoint)

        assert response.status_code == 200
        assert len(MockDeviceHandler.request_records) == 2
        assert "Authorization" not in MockDeviceHandler.request_records[0]["headers"]
        assert MockDeviceHandler.request_records[1]["headers"][
            "Authorization"
        ].startswith("Basic ")

    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_auto_auth_digest(self, mock_server):
        """AUTO selects Digest from the advertised challenge."""
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
            allow_insecure=True,
        )
        client = TransportClient(config)

        endpoint = TransportEndpoint("GET", "/api/info")
        response = client.request(endpoint)

        assert response.status_code == 200
        assert len(MockDeviceHandler.request_records) == 2
        assert "Authorization" not in MockDeviceHandler.request_records[0]["headers"]
        assert MockDeviceHandler.request_records[1]["headers"][
            "Authorization"
        ].startswith("Digest ")

    @pytest.mark.parametrize("auth_method", ["basic", "digest"])
    def test_auto_auth_failed_fallback_sends_exactly_two_requests(
        self, mock_server, auth_method
    ):
        """A rejected fallback must not trigger an auth-library retry."""
        MockDeviceHandler.auth_method = auth_method
        MockDeviceHandler.reject_authenticated = True
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )
        client = TransportClient(config)

        with pytest.raises(AuthenticationError):
            client.request(TransportEndpoint("GET", "/api/info"))

        assert len(MockDeviceHandler.request_records) == 2
        assert "Authorization" not in MockDeviceHandler.request_records[0]["headers"]
        assert "Authorization" in MockDeviceHandler.request_records[1]["headers"]

    def test_classic_combined_challenge_fallback_sends_exactly_two_requests(
        self, mock_server
    ):
        """Challenge-triggered classic fallback uses one preferred retry."""
        MockDeviceHandler.advertised_auth_methods = ["basic", "digest"]
        MockDeviceHandler.reject_authenticated = True
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )
        client = TransportClient(config)

        with pytest.raises(FeatureError):
            ClassicAPIDiscoveryClient(client).get_supported_versions()

        assert len(MockDeviceHandler.request_records) == 2
        assert MockDeviceHandler.request_records[1]["headers"][
            "Authorization"
        ].startswith("Digest ")

    @pytest.mark.parametrize(
        "challenge",
        [
            'Bearer realm="basic realm"',
            'Bearer realm="Device", note="Digest value"',
        ],
    )
    def test_auto_auth_ignores_basic_digest_words_in_quoted_parameters(
        self, mock_server, challenge
    ):
        """Quoted parameter text must not cause an authenticated retry."""
        MockDeviceHandler.www_authenticate_header = challenge
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )
        client = TransportClient(config)

        with pytest.raises(AuthenticationError):
            client.request(TransportEndpoint("GET", "/api/info"))

        assert len(MockDeviceHandler.request_records) == 1

    @pytest.mark.parametrize("session_operation", ["clear", "new"])
    def test_session_reset_does_not_reuse_cached_auth(
        self, mock_server, session_operation
    ):
        """Replacing a session also clears the cached method and credentials."""
        MockDeviceHandler.auth_method = "digest"
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )
        client = TransportClient(config)
        endpoint = TransportEndpoint("GET", "/api/info")
        assert client.request(endpoint).status_code == 200
        assert len(MockDeviceHandler.request_records) == 2

        if session_operation == "clear":
            client.clear_session()
            client.request(endpoint)
        else:
            with client.new_session():
                client.request(endpoint)

        assert len(MockDeviceHandler.request_records) == 4
        assert "Authorization" not in MockDeviceHandler.request_records[2]["headers"]

    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_auto_auth_prefers_digest_when_both_are_advertised(self, mock_server):
        """AUTO must not send Basic when a Digest challenge is available."""
        MockDeviceHandler.advertised_auth_methods = ["basic", "digest"]

        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )
        client = TransportClient(config)

        response = client.request(TransportEndpoint("GET", "/api/info"))

        assert response.status_code == 200
        assert MockDeviceHandler.request_records[1]["headers"][
            "Authorization"
        ].startswith("Digest ")

    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_auto_auth_preserves_query_headers_and_body(self, mock_server):
        """AUTO retries the same request data after receiving its challenge."""
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )
        client = TransportClient(config)

        response = client.request(
            TransportEndpoint("POST", "/api/data"),
            params={"mode": "fast"},
            data=b'{"value": 42}',
            headers={"X-Retry-Test": "yes"},
        )

        assert response.status_code == 201
        assert len(MockDeviceHandler.request_records) == 2
        first, second = MockDeviceHandler.request_records
        assert first["path"] == second["path"] == "/api/data?mode=fast"
        assert first["body"] == second["body"] == b'{"value": 42}'
        assert second["headers"]["X-Retry-Test"] == "yes"

    @pytest.mark.parametrize("auth_method", ["basic", "digest"])
    def test_classic_discovery_legacy_fallback_is_exactly_one_retry(
        self, mock_server, auth_method
    ):
        """Classic fallback reuses the received challenge and sends exactly two requests."""
        MockDeviceHandler.auth_method = auth_method
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )

        client = TransportClient(config)
        try:
            result = ClassicAPIDiscoveryClient(client).get_supported_versions()

            assert result == ("1.0",)
            assert len(MockDeviceHandler.request_records) == 2
            first, second = MockDeviceHandler.request_records
            assert first["method"] == second["method"] == "POST"
            assert first["path"] == second["path"] == "/axis-cgi/apidiscovery.cgi"
            assert "Authorization" not in first["headers"]
            assert "Cookie" not in first["headers"]
            assert "Authorization" in second["headers"]
            assert first["body"] == second["body"]

            subsequent = client.request(
                TransportEndpoint("POST", "/axis-cgi/apidiscovery.cgi"),
                json={"method": "getSupportedVersions"},
            )
            assert subsequent.status_code == 200
            if auth_method == "digest":
                assert len(MockDeviceHandler.request_records) == 4
                third, fourth = MockDeviceHandler.request_records[2:]
                assert "Authorization" not in third["headers"]
                assert fourth["headers"]["Authorization"].startswith("Digest ")
            else:
                assert len(MockDeviceHandler.request_records) == 3
                assert MockDeviceHandler.request_records[2]["headers"][
                    "Authorization"
                ].startswith("Basic ")
        finally:
            client._session.close()

    @pytest.mark.parametrize("auth_method", [AuthMethod.BASIC, AuthMethod.DIGEST])
    def test_classic_discovery_fallback_honors_explicit_auth_method(
        self, mock_server, auth_method
    ):
        """Classic fallback uses the explicitly configured challenge scheme."""
        MockDeviceHandler.auth_method = auth_method.value
        MockDeviceHandler.advertised_auth_methods = ["basic", "digest"]
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=auth_method,
            timeout=5.0,
            allow_insecure=True,
        )

        result = ClassicAPIDiscoveryClient(
            TransportClient(config)
        ).get_supported_versions()

        assert result == ("1.0",)
        assert len(MockDeviceHandler.request_records) == 2
        assert MockDeviceHandler.request_records[1]["headers"][
            "Authorization"
        ].startswith(f"{auth_method.value.title()} ")

    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_auto_auth_does_not_cache_non_successful_response(self, mock_server):
        """AUTO must not treat a non-401 error as proof of valid auth."""
        config = DeviceConfig(
            host=f"localhost:{mock_server[1]}",
            username="test",
            password="password",
            protocol=Protocol.HTTP,
            auth_method=AuthMethod.AUTO,
            timeout=5.0,
            allow_insecure=True,
        )
        client = TransportClient(config)
        endpoint = TransportEndpoint("GET", "/api/server-error")

        first = client.request(endpoint)
        MockDeviceHandler.auth_required = True
        second = client.request(TransportEndpoint("GET", "/api/info"))

        assert first.status_code == 500
        assert second.status_code == 200
        assert len(MockDeviceHandler.request_records) == 4

    @pytest.mark.http
    @pytest.mark.auth
    @pytest.mark.unit
    def test_request_no_auth_ignores_cached_auth(self, mock_server, http_client):
        """No-auth requests must not inherit session-level Authorization."""
        MockDeviceHandler.auth_required = False
        http_client.request(TransportEndpoint("GET", "/api/info"))
        http_client.request_no_auth(
            TransportEndpoint("GET", "/api/info"),
            headers={"Authorization": "Bearer secret", "Cookie": "session=secret"},
        )

        assert "Authorization" not in MockDeviceHandler.request_records[-1]["headers"]
        assert "Cookie" not in MockDeviceHandler.request_records[-1]["headers"]

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
            allow_insecure=True,
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
            allow_insecure=True,
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
            allow_insecure=True,
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
    def test_https_is_verified_by_default(self, mock_https_server):
        """Default HTTPS rejects the local self-signed certificate."""
        port, _ = mock_https_server
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTPS,
            auth_method=AuthMethod.BASIC,
            timeout=5.0,
        )

        with pytest.raises(NetworkError):
            TransportClient(config).request(TransportEndpoint("GET", "/api/info"))

    @pytest.mark.https
    @pytest.mark.unit
    def test_https_accepts_ca_bundle_path(self, mock_https_server):
        """HTTPS accepts a PEM CA bundle path through Requests' verify option."""
        port, cert_path = mock_https_server
        config = DeviceConfig(
            host=f"localhost:{port}",
            username="test",
            password="password",
            protocol=Protocol.HTTPS,
            auth_method=AuthMethod.BASIC,
            timeout=5.0,
            verify_ssl=str(cert_path),
        )

        response = TransportClient(config).request(
            TransportEndpoint("GET", "/api/info")
        )

        assert response.status_code == 200

    @pytest.mark.https
    @pytest.mark.error
    @pytest.mark.unit
    def test_protocol_specific_default_ports(self):
        """Only the active protocol's default port is omitted."""
        https = DeviceConfig.https("camera", "user", "pass")
        http = DeviceConfig.http("camera", "user", "pass")
        https_explicit_http_port = DeviceConfig.https("camera", "user", "pass", port=80)

        assert https.get_base_url() == "https://camera"
        assert http.get_base_url() == "http://camera"
        assert https_explicit_http_port.get_base_url() == "https://camera:80"

    @pytest.mark.unit
    def test_debug_output_redacts_nested_secrets(self):
        """Debug payloads redact secrets recursively without changing safe values."""
        callback = Mock()
        emit_request_debug_info(
            callback,
            method="POST",
            url="https://user:password@example.test/api?token=url-secret&safe=yes",
            headers={"Authorization": "Basic abc", "X-Safe": "yes"},
            timeout=5.0,
            verify_ssl=True,
            params={"api_key": "query-secret", "safe": "yes"},
            json_body={"nested": [{"password": "body-secret", "safe": "yes"}]},
            data=json.dumps({"secret": "data-secret"}).encode(),
        )

        payload = callback.call_args.args[0]
        serialized = json.dumps(payload)
        assert "url-secret" not in serialized
        assert "query-secret" not in serialized
        assert "body-secret" not in serialized
        assert "data-secret" not in serialized
        assert "safe" in serialized

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
            MockDeviceHandler.use_fixed_session_token = (
                True  # Use fixed token for this test
            )

        # Store a reference to the session object to verify it's being reused
        original_session_id = id(http_client._session)

        endpoint = TransportEndpoint("GET", "/api/info")
        num_requests = 5  # Reduced from 10 to make debugging easier

        # Execute requests concurrently
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_requests
        ) as executor:
            futures = [
                executor.submit(http_client.request, endpoint)
                for _ in range(num_requests)
            ]
            responses = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        assert len(responses) == num_requests
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["version"] == "1.0"

        # Verify the client is still using the same session object
        assert id(http_client._session) == original_session_id, (
            "Session object changed during concurrent requests"
        )

        # Should still only have one session token since we're reusing the same client
        assert len(MockDeviceHandler.session_tokens) == 1

        # Reset back to default behavior
        MockDeviceHandler.use_fixed_session_token = False

    @pytest.mark.http
    @pytest.mark.unit
    def test_connection_pool_configuration(self, http_client):
        """Test that the client has the expected adapter configuration."""
        # Test that the client has the expected adapter configuration
        adapter = http_client._session.adapters["http://"]

        # Check that we're using the HTTPAdapter
        assert isinstance(adapter, HTTPAdapter)

        # Verify both HTTP and HTTPS adapters are configured
        assert "http://" in http_client._session.adapters
        assert "https://" in http_client._session.adapters

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
        assert MockDeviceHandler.request_count == initial_count + num_requests + 1

        # Verify that a single session was used (connection pooling working)
        assert len(MockDeviceHandler.session_tokens) == 1
