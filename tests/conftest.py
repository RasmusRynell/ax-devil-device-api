"""Test configuration and shared fixtures."""
import pytest
import os
from ax_devil_device_api import Client, DeviceConfig
import ssl
import socket
import threading
import datetime
from functools import partial
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from ax_devil_device_api.core.transport_client import TransportClient
from ax_devil_device_api.core.config import Protocol, AuthMethod
from tests.mocks.http_server import ThreadedHTTPServer, MockDeviceHandler
from tests.mocks.mock_api_routes import get_standard_routes

def pytest_addoption(parser):
    """Add custom command line options for tests."""
    parser.addoption(
        "--run-restart",
        action="store_true",
        default=False,
        help="Run device restart tests (potentially disruptive)"
    )
    parser.addoption(
        "--protocol",
        choices=["http", "https"],
        default="https",
        help="Protocol to use for device communication (default: https)"
    )

def pytest_configure(config):
    """Configure test environment."""
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "restart: mark test as requiring device restart (potentially disruptive)"
    )
    config.addinivalue_line(
        "markers",
        "skip_health_check: mark test to skip automatic health checks"
    )

def pytest_collection_modifyitems(config, items):
    """Skip restart tests unless explicitly enabled."""
    if not config.getoption("--run-restart"):
        skip_restart = pytest.mark.skip(reason="Need --run-restart option to run")
        for item in items:
            if "restart" in item.keywords:
                item.add_marker(skip_restart)

@pytest.fixture(scope="session")
def protocol(request):
    """Get the protocol to use for tests."""
    return request.config.getoption("--protocol")

@pytest.fixture(scope="session")
def client(protocol):
    """Create a client instance that persists for the entire test session."""
    device_ip = os.getenv("AX_DEVIL_TARGET_ADDR")
    device_user = os.getenv("AX_DEVIL_TARGET_USER")
    device_pass = os.getenv("AX_DEVIL_TARGET_PASS")

    if not all([device_ip, device_user, device_pass]):
        pytest.skip("Required environment variables not set")
    
    if protocol == "http":
        config = DeviceConfig.http(
            host=device_ip,
            username=device_user,
            password=device_pass
        )
    else:
        config = DeviceConfig.https(
            host=device_ip,
            username=device_user,
            password=device_pass,
            verify_ssl=False
        )
    
    client = Client(config)
    try:
        yield client
    finally:
        client.close()

@pytest.fixture
def mock_server():
    """Start a mock HTTP server for testing."""
    # Get standard routes
    routes = get_standard_routes()
    
    # Find an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        port = s.getsockname()[1]
    
    # Create and start server
    handler = partial(MockDeviceHandler, routes=routes)
    server = ThreadedHTTPServer(('localhost', port), handler)
    
    # Reset class variables
    with MockDeviceHandler.session_lock:
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "basic"
        MockDeviceHandler.simulate_timeout = False
        MockDeviceHandler.simulate_connection_error = False
        MockDeviceHandler.request_count = 0
        MockDeviceHandler.session_tokens = set()
        MockDeviceHandler.use_fixed_session_token = False
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    yield server, port
    
    server.shutdown()
    server.server_close()

@pytest.fixture
def mock_https_server(tmp_path):
    """Create a mock HTTPS server for testing."""
    # Generate a self-signed certificate for testing
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Create a self-signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Test City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Corp"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=10)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Save the certificate and key to temporary files
    cert_path = tmp_path / "server.crt"
    key_path = tmp_path / "server.key"
    
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Define routes - same as in the HTTP server fixture
    routes = get_standard_routes()
    
    # Create and start the HTTPS server - use partial to pass routes to handler
    handler = partial(MockDeviceHandler, routes=routes)
    server = ThreadedHTTPServer(("localhost", 0), handler)
    
    # Create SSL context with the certificate and key
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
    
    # Wrap the socket with the SSL context
    server.socket = ssl_context.wrap_socket(
        server.socket,
        server_side=True
    )
    
    # Reset class variables
    with MockDeviceHandler.session_lock:
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "basic"
        MockDeviceHandler.simulate_timeout = False
        MockDeviceHandler.simulate_connection_error = False
        MockDeviceHandler.request_count = 0
        MockDeviceHandler.session_tokens = set()
        MockDeviceHandler.use_fixed_session_token = False
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    port = server.server_address[1]
    
    yield port, cert_path
    
    server.shutdown()
    server.server_close()

@pytest.fixture
def http_client(mock_server):
    """Create a TransportClient configured for HTTP."""
    _, port = mock_server
    
    # Reset session tokens to ensure clean test state
    MockDeviceHandler.session_tokens = set()
    
    config = DeviceConfig(
        host=f"localhost:{port}",
        username="test",
        password="password",
        protocol=Protocol.HTTP,
        auth_method=AuthMethod.BASIC,
        timeout=5.0,
        allow_insecure=True
    )
    client = TransportClient(config)
    yield client

@pytest.fixture
def https_client(mock_https_server):
    """Create a client for HTTPS testing."""
    port, cert_path = mock_https_server
    
    # Reset session tokens to ensure clean test state
    MockDeviceHandler.session_tokens = set()
    
    # Create client with SSL verification disabled
    config = DeviceConfig(
        host=f"localhost:{port}",
        username="test",
        password="password",
        protocol=Protocol.HTTPS,
        auth_method=AuthMethod.BASIC,
        timeout=5.0,
        verify_ssl=False  # SSL verification is disabled
    )
    client = TransportClient(config)
    yield client

@pytest.fixture(autouse=True)
def reset_mock_handler():
    """Reset the MockDeviceHandler state before each test."""
    print("\nResetting MockDeviceHandler state")
    with MockDeviceHandler.session_lock:
        MockDeviceHandler.auth_required = True
        MockDeviceHandler.auth_method = "basic"
        MockDeviceHandler.simulate_timeout = False
        MockDeviceHandler.simulate_connection_error = False
        MockDeviceHandler.request_count = 0
        MockDeviceHandler.session_tokens = set()
        MockDeviceHandler.use_fixed_session_token = False
    yield
