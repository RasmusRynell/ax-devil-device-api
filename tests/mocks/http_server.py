"""Mock HTTP server implementation for testing.

This module provides a threaded HTTP server and request handler that simulates
an Axis device API for integration testing.
"""

import json
import base64
import threading
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.DEBUG)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True
    poll_interval = 0.001  # Customize poll interval for serve_forever()
    
    def serve_forever(self, poll_interval=None):
        """Override serve_forever to use custom poll_interval."""
        if poll_interval is None:
            poll_interval = self.poll_interval
        super().serve_forever(poll_interval)
    
    def handle_error(self, request, client_address):
        """Handle errors in thread pools more gracefully."""
        import sys
        from traceback import format_exc
        
        # Get exception info
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Only log connection resets and broken pipes as info, not as errors
        if issubclass(exc_type, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError)):
            logging.info(f"Connection error with {client_address}: {exc_value}")
        else:
            logging.info(f"Error handling request from {client_address}:")
            logging.info(format_exc())


class MockDeviceHandler(BaseHTTPRequestHandler):
    """Mock HTTP handler that simulates device API behavior."""
    
    # Class variables to control behavior
    auth_required = True
    auth_method = "basic"  # "basic", "digest", or "none"
    simulate_timeout = False
    simulate_connection_error = False
    request_count = 0
    session_tokens = set()
    session_lock = threading.Lock()  # Add lock for thread safety
    use_fixed_session_token = False  # Whether to use a fixed token or generate sequential ones
    
    def __init__(self, *args, **kwargs):
        self.routes = kwargs.pop('routes', {})
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        self._handle_request("GET")
    
    def do_POST(self):
        self._handle_request("POST")
    
    def do_PUT(self):
        self._handle_request("PUT")
    
    def do_DELETE(self):
        self._handle_request("DELETE")
    
    def _handle_request(self, method):
        """Handle all HTTP methods with common logic."""
        MockDeviceHandler.request_count += 1
        thread_id = threading.get_ident()

        # Simulate network issues if configured
        if MockDeviceHandler.simulate_timeout:
            time.sleep(15)  # Sleep longer than client timeout
            return
        
        if MockDeviceHandler.simulate_connection_error:
            self.wfile.close()
            return
        
        # Parse URL and query parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        # Check authentication if required
        if MockDeviceHandler.auth_required:
            if not self._check_auth():
                self.send_response(401)
                if MockDeviceHandler.auth_method == "basic":
                    self.send_header('WWW-Authenticate', 'Basic realm="Device API"')
                elif MockDeviceHandler.auth_method == "digest":
                    self.send_header('WWW-Authenticate', 'Digest realm="Device API", nonce="abc123"')
                self.end_headers()
                return
        
        # Enhanced thread-safe session handling
        cookie_header = self.headers.get('Cookie', '')
        logging.info(f"Thread {thread_id}: Received cookie header: {cookie_header}")
        session_token = None
        
        # Use a single lock acquisition to check and update session tokens
        with MockDeviceHandler.session_lock:
            # Try to extract existing session token from cookie
            if 'session=' in cookie_header:
                try:
                    # Find the session cookie in the header
                    session_parts = [p.strip() for p in cookie_header.split(';')]
                    for part in session_parts:
                        if part.startswith('session='):
                            token = part.split('=', 1)[1]
                            # Only use the token if it's valid
                            if token in MockDeviceHandler.session_tokens:
                                session_token = token
                                logging.info(f"Thread {thread_id}: Found valid session token: {token}")
                                break
                            else:
                                logging.info(f"Thread {thread_id}: Found invalid session token: {token}")
                except (IndexError, ValueError) as e:
                    # If parsing fails, we'll create a new token
                    logging.info(f"Thread {thread_id}: Error parsing cookie: {e}")
                    pass
            
            # If no valid session token was found, create a new one
            if not session_token:
                if MockDeviceHandler.use_fixed_session_token:
                    # Always use a fixed token name for concurrent tests
                    session_token = "mock-session-0"
                    logging.info(f"Thread {thread_id}: Creating new fixed session token: {session_token}")
                else:
                    # Generate sequential tokens for session tests
                    session_token = f"mock-session-{len(MockDeviceHandler.session_tokens)}"
                    logging.info(f"Thread {thread_id}: Creating new sequential session token: {session_token}")
                
                MockDeviceHandler.session_tokens.add(session_token)
        
        # Find matching route
        route_key = f"{method}:{path}"
        if route_key in self.routes:
            status_code, headers, response_data = self.routes[route_key](self, query)
        else:
            # Log that route was not found for debugging
            logging.info(f"[MockDeviceHandler] No route found for '{route_key}'. Available routes: {list(self.routes.keys())}")
            status_code, headers, response_data = 404, {}, {"error": "Not found", "route": route_key}
        
        # Send response
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Set-Cookie', f'session={session_token}; Path=/')
        
        for header, value in headers.items():
            self.send_header(header, value)
        
        self.end_headers()
        
        if response_data:
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
    
    def _check_auth(self):
        """Check if request has valid authentication."""
        auth_header = self.headers.get('Authorization')
        if not auth_header:
            return False
        
        if MockDeviceHandler.auth_method == "basic":
            if not auth_header.startswith('Basic '):
                return False
            
            try:
                credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = credentials.split(':')
                return username == 'test' and password == 'password'
            except Exception:
                return False
        
        elif MockDeviceHandler.auth_method == "digest":
            # Simplified digest auth check for testing
            return 'Digest ' in auth_header
        
        return False 