from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .base import FeatureClient, TransportEndpoint
from ..core.types import FeatureResponse, FeatureError

@dataclass
class SSHUser:
    """Define SSH user data structure.
    REQUIRED: Add all fields returned by the API."""
    username: str
    comment: Optional[str] = None

class SSHClient(FeatureClient[SSHUser]):
    """Client for managing SSH users on Axis devices."""
    
    API_VERSION = "v2beta"
    BASE_PATH = f"/config/rest/ssh/{API_VERSION}/users"

    def add_user(self, username: str, password: str, comment: Optional[str] = None) -> FeatureResponse[SSHUser]:
        """Add a new SSH user to the device."""
        if not username or not password:
            return FeatureResponse.create_error(FeatureError("username_password_required", "Username and password are required"))
            
        response = self.request(
            TransportEndpoint("POST", self.BASE_PATH),
            json={"data": {
                "username": username,
                "password": password,
                "comment": comment
            }}
        )
        
        if response.status_code != 201:
            return FeatureResponse.create_error(FeatureError(
                "add_user_error",
                f"Failed to add user: HTTP {response.status_code}"
            ))
            
        return FeatureResponse.ok(SSHUser(
            username=username,
            comment=comment
        ))

    def get_users(self) -> FeatureResponse[List[SSHUser]]:
        """Get all SSH users from the device."""
        response = self.request(TransportEndpoint("GET", self.BASE_PATH))
        
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "get_users_error",
                f"Failed to get users: HTTP {response.status_code}"
            ))
            
        try:
            response_json = response.json()
            if not isinstance(response_json.get("data"), list):
                return FeatureResponse.create_error(FeatureError("invalid_response_format", "Invalid response format"))
                
            users = []
            for user_data in response_json["data"]:
                if "username" not in user_data:
                    continue
                users.append(SSHUser(
                    username=user_data["username"],
                    comment=user_data.get("comment")
                ))
                
            return FeatureResponse.ok(users)
        except (ValueError, KeyError) as e:
            return FeatureResponse.create_error(FeatureError("failed_to_parse_response", f"Failed to parse response: {str(e)}"))

    def get_user(self, username: str) -> FeatureResponse[SSHUser]:
        """Get a specific SSH user from the device."""
        if not username:
            return FeatureResponse.create_error(FeatureError("username_required", "Username is required"))
            
        response = self.request(TransportEndpoint("GET", f"{self.BASE_PATH}/{username}"))
        
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "get_user_error",
                f"Failed to get user: HTTP {response.status_code}"
            ))
            
        try:                
            response_json = response.json()
            data = response_json.get("data")
            if "username" not in data:
                return FeatureResponse.create_error(FeatureError("invalid_response_format", "Invalid response format"))
                
            return FeatureResponse.ok(SSHUser(
                username=data["username"],
                comment=data.get("comment")
            ))
        except (ValueError, KeyError) as e:
            return FeatureResponse.create_error(FeatureError("failed_to_parse_response", f"Failed to parse response: {str(e)}"))

    def modify_user(self, username: str, password: Optional[str] = None, 
                   comment: Optional[str] = None) -> FeatureResponse[SSHUser]:
        """Modify an existing SSH user."""
        if not username:
            return FeatureResponse.create_error(FeatureError("username_required", "Username is required"))
        
        if password is None and comment is None:
            return FeatureResponse.create_error(FeatureError("at_least_one_of_password_or_comment_required", "At least one of password or comment must be specified"))
            
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
            return FeatureResponse.create_error(FeatureError(
                "modify_user_error",
                f"Failed to modify user: HTTP {response.status_code}"
            ))
            
        return FeatureResponse.ok(SSHUser(username=username, comment=comment))

    def remove_user(self, username: str) -> FeatureResponse[None]:
        """Remove an SSH user from the device."""
        if not username:
            return FeatureResponse.create_error(FeatureError("username_required", "Username is required"))
            
        response = self.request(TransportEndpoint("DELETE", f"{self.BASE_PATH}/{username}"))
        
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "remove_user_error",
                f"Failed to remove user: HTTP {response.status_code}"
            ))
            
        return FeatureResponse.ok(None) 