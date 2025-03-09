from dataclasses import dataclass
import json
from typing import Dict, Any, Optional, List

import requests
from .base import FeatureClient, TransportEndpoint
from ..utils.errors import FeatureError


class SSHClient(FeatureClient):
    """Client for managing SSH users on Axis devices."""
    
    API_VERSION = "v2beta"
    BASE_PATH = f"/config/rest/ssh/{API_VERSION}/users"

    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse the response from the device."""
        json_response = response.json()
        if not json_response.get("status") == "success":
            return json_response.get("error")
        return json_response.get("data")

    def add_user(self, username: str, password: str, comment: str = "") -> Dict[str, Any]:
        """Add a new SSH user to the device."""
        if not username or not password:
            raise FeatureError("username_password_required", "Username and password are required")
        
        response = self.request(
            TransportEndpoint("POST", self.BASE_PATH),
            json={"data": {
                "username": username,
                "password": password,
                "comment": comment
            }}
        )

        if response.status_code != 201:
            raise FeatureError("add_user_error", json.dumps(self._parse_response(response)))
        
        return self._parse_response(response)

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all SSH users from the device."""
        response = self.request(TransportEndpoint("GET", self.BASE_PATH))
        
        if response.status_code != 200:
            raise FeatureError("get_users_error", json.dumps(self._parse_response(response)))
            
        return self._parse_response(response)

    def get_user(self, username: str) -> Dict[str, Any]:
        """Get a specific SSH user from the device."""
        if not username:
            raise FeatureError("username_required", "Username is required")
            
        response = self.request(TransportEndpoint("GET", f"{self.BASE_PATH}/{username}"))
        
        if response.status_code != 200:
            raise FeatureError("get_user_error", json.dumps(self._parse_response(response)))
            
        return self._parse_response(response)

    def modify_user(self, username: str, password: Optional[str] = None, 
                   comment: Optional[str] = None) -> Dict[str, Any]:
        """Modify an existing SSH user."""
        if not username:
            raise FeatureError("username_required", "Username is required")
        
        if password is None and comment is None:
            raise FeatureError("at_least_one_of_password_or_comment_required", "At least one of password or comment must be specified")
            
        data = {}
        if password is not None:
            data["password"] = password
        if comment is not None:
            data["comment"] = comment
            
        response = self.request(
            TransportEndpoint("PATCH", f"{self.BASE_PATH}/{username}"),
            json={"data": data}
        )
        
        if response.status_code != 200:
            raise FeatureError("modify_user_error", json.dumps(self._parse_response(response)))
            
        return self._parse_response(response)

    def remove_user(self, username: str) -> Dict[str, Any]:
        """Remove an SSH user from the device."""
        if not username:
            raise FeatureError("username_required", "Username is required")
            
        response = self.request(TransportEndpoint("DELETE", f"{self.BASE_PATH}/{username}"))
        
        if response.status_code != 200:
            raise FeatureError("remove_user_error", json.dumps(self._parse_response(response)))
        
        return self._parse_response(response)
