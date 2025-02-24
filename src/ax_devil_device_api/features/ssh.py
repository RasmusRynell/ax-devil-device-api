from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .base import FeatureClient, DeviceEndpoint
from ..core.types import FeatureResponse

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
        if not username or not password:  # Basic validation
            return FeatureResponse.create_error("Username and password are required")
            
        response = self.request(
            DeviceEndpoint("POST", self.BASE_PATH),
            json={"data": {
                "username": username,
                "password": password,
                "comment": comment
            }}
        )
        
        if not response.is_success:
            return response
            
        return FeatureResponse.ok(SSHUser(
            username=username,
            comment=comment
        ))

    def get_users(self) -> FeatureResponse[List[SSHUser]]:
        """Get all SSH users from the device."""
        response = self.request(DeviceEndpoint("GET", self.BASE_PATH))
        
        if not response.is_success:
            return response
            
        try:
            if not response.raw_response:
                return FeatureResponse.create_error("No response received")
                
            response_json = response.raw_response.json()
            if not isinstance(response_json.get("data"), list):
                return FeatureResponse.create_error("Invalid response format")
                
            users = []
            for user_data in response_json["data"]:
                if "username" not in user_data:
                    continue  # Skip invalid entries
                users.append(SSHUser(
                    username=user_data["username"],
                    comment=user_data.get("comment")
                ))
                
            return FeatureResponse.ok(users)
        except (ValueError, KeyError) as e:
            return FeatureResponse.create_error(f"Failed to parse response: {str(e)}")

    def get_user(self, username: str) -> FeatureResponse[SSHUser]:
        """Get a specific SSH user from the device."""
        if not username:  # Basic validation
            return FeatureResponse.create_error("Username is required")
            
        response = self.request(DeviceEndpoint("GET", f"{self.BASE_PATH}/{username}"))
        
        if not response.is_success:
            return response
            
        try:
            if not response.raw_response:
                return FeatureResponse.create_error("No response received")
                
            response_json = response.raw_response.json()
            data = response_json.get("data", {})
            if "username" not in data:
                return FeatureResponse.create_error("Invalid response format")
                
            return FeatureResponse.ok(SSHUser(
                username=data["username"],
                comment=data.get("comment")
            ))
        except (ValueError, KeyError) as e:
            return FeatureResponse.create_error(f"Failed to parse response: {str(e)}")

    def modify_user(self, username: str, password: Optional[str] = None, 
                   comment: Optional[str] = None) -> FeatureResponse[SSHUser]:
        """Modify an existing SSH user."""
        if not username:  # Basic validation
            return FeatureResponse.create_error("Username is required")
        
        if password is None and comment is None:
            return FeatureResponse.create_error("At least one of password or comment must be specified")
            
        data = {}
        if password is not None:
            data["password"] = password
        if comment is not None:
            data["comment"] = comment
            
        response = self.request(
            DeviceEndpoint("PATCH", f"{self.BASE_PATH}/{username}"),
            json={"data": data}
        )
        
        if not response.is_success:
            return response
            
        return FeatureResponse.ok(SSHUser(username=username, comment=comment))

    def remove_user(self, username: str) -> FeatureResponse[None]:
        """Remove an SSH user from the device."""
        if not username:  # Basic validation
            return FeatureResponse.create_error("Username is required")
            
        response = self.request(DeviceEndpoint("DELETE", f"{self.BASE_PATH}/{username}"))
        
        if not response.is_success:
            return response
            
        return FeatureResponse.ok(None) 