"""Mock device API endpoints.

This module provides standard mock API routes used for testing the TransportClient.
"""

def get_standard_routes():
    """Return a dictionary of standard API routes for testing.
    
    Each route is defined as a function that takes a request handler and
    query parameters and returns a tuple of (status_code, headers, response_data).
    """
    return {
        # Basic API operations
        "GET:/api/info": lambda req, params: (200, {}, {"version": "1.0", "model": "Test Device"}),
        "POST:/api/data": lambda req, params: (201, {}, {"status": "created"}),
        "PUT:/api/data": lambda req, params: (200, {}, {"status": "updated"}),
        "DELETE:/api/resource": lambda req, params: (204, {}, None),
        
        # Error responses
        "GET:/api/error": lambda req, params: (500, {}, {"error": "Internal error"}),
        "GET:/api/server-error": lambda req, params: (500, {}, {"error": "Internal server error"}),
        
        # Special test endpoints
        "GET:/api/slow": lambda req, params: (200, {}, {"status": "slow_response"}),
    } 