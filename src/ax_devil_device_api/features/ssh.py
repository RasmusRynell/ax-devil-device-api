from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from ..core.config import Protocol
from ..core.endpoints import TransportEndpoint
from ..core.transport_client import TransportClient
from ..utils.errors import FeatureError
from .api_discovery import DiscoveryClient
from .base import FeatureClient


def validate_comment(comment: str | None) -> None:
    """Reject an explicitly empty SSH user comment."""
    if comment == "":
        raise FeatureError("comment_required", "Comment must not be empty")


class SSHClient(FeatureClient):
    """Client for the released SSH Management API."""

    API_NAME = "ssh"

    def __init__(self, device_client: TransportClient) -> None:
        """Initialize the SSH client and its lazy discovered endpoint cache."""
        super().__init__(device_client)
        self._users_path: str | None = None

    def _ensure_https(self) -> None:
        """Reject SSH management over an insecure transport."""
        if self.device.config.protocol != Protocol.HTTPS:
            raise FeatureError(
                "https_required", "SSH management requires an HTTPS connection"
            )

    def _get_users_path(self) -> str:
        """Discover and cache the released SSH users collection path."""
        self._ensure_https()
        if self._users_path is not None:
            return self._users_path

        collection = DiscoveryClient(self.device).discover()
        api = collection.get_api(self.API_NAME)
        if api is None:
            raise FeatureError(
                "ssh_api_not_found",
                "The released SSH Management API was not discovered",
            )

        rest_api = api.rest_api_url
        if not rest_api or rest_api == "No REST API available":
            raise FeatureError(
                "invalid_response", "The discovered SSH Management API has no REST API"
            )
        self._users_path = f"{rest_api.rstrip('/')}/users"
        return self._users_path

    @staticmethod
    def _decode_response(response: requests.Response, operation: str) -> dict[str, Any]:
        """Decode a DCA response object or raise a precise response error."""
        try:
            payload = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response", f"{operation} response is not valid JSON"
            ) from error
        if not isinstance(payload, dict):
            raise FeatureError(
                "invalid_response", f"{operation} response is not an object"
            )
        return payload

    @classmethod
    def _parse_response(
        cls,
        response: requests.Response,
        operation: str,
        data_type: type[list[dict[str, Any]] | dict[str, Any]] | None = None,
    ) -> Any:
        """Validate a strict DCA envelope and optionally return typed data."""
        if response.status_code != 200:
            try:
                payload = response.json()
            except ValueError as error:
                raise FeatureError(
                    f"{operation}_error",
                    f"{operation} failed: HTTP {response.status_code}",
                ) from error
            if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
                error = payload["error"]
                raise FeatureError(
                    str(error.get("code", f"{operation}_error")),
                    str(error.get("message", "Unknown API error")),
                    details=error,
                )
            raise FeatureError(
                f"{operation}_error",
                f"{operation} failed: HTTP {response.status_code}",
            )

        payload = cls._decode_response(response, operation)
        error = payload.get("error")
        if payload.get("status") != "success":
            if not isinstance(error, dict):
                raise FeatureError(
                    "invalid_response",
                    f"{operation} error envelope is malformed",
                )
            raise FeatureError(
                str(error.get("code", f"{operation}_error")),
                str(error.get("message", "Unknown API error")),
                details=error,
            )

        if data_type is None:
            return None

        data = payload.get("data")
        if data_type is list:
            if not isinstance(data, list) or not all(
                isinstance(user, dict) for user in data
            ):
                raise FeatureError(
                    "invalid_response", f"{operation} data is not a list of users"
                )
        elif not isinstance(data, dict):
            raise FeatureError("invalid_response", f"{operation} data is not a user")
        return data

    @staticmethod
    def _user_path(users_path: str, username: str) -> str:
        """Append a username as one fully encoded URL path segment."""
        return f"{users_path}/{quote(username, safe='')}"

    def add_user(
        self, username: str, password: str, comment: str | None = None
    ) -> None:
        """Add an SSH user using the collection POST operation."""
        if not username or not password:
            raise FeatureError(
                "username_password_required", "Username and password are required"
            )
        validate_comment(comment)
        users_path = self._get_users_path()
        data = {"username": username, "password": password}
        if comment is not None:
            data["comment"] = comment
        response = self.request(
            TransportEndpoint("POST", users_path), json={"data": data}
        )
        self._parse_response(response, "add_user")

    def get_users(self) -> list[dict[str, Any]]:
        """List SSH users from the collection GET operation."""
        response = self.request(TransportEndpoint("GET", self._get_users_path()))
        return self._parse_response(response, "get_users", list)

    def get_user(self, username: str) -> dict[str, Any]:
        """Get one SSH user from the item GET operation."""
        if not username:
            raise FeatureError("username_required", "Username is required")
        users_path = self._get_users_path()
        response = self.request(
            TransportEndpoint("GET", self._user_path(users_path, username))
        )
        return self._parse_response(response, "get_user", dict)

    def modify_user(
        self, username: str, password: str | None = None, comment: str | None = None
    ) -> None:
        """Patch only the supplied password and/or comment fields."""
        if not username:
            raise FeatureError("username_required", "Username is required")
        validate_comment(comment)
        if password is None and comment is None:
            raise FeatureError(
                "at_least_one_of_password_or_comment_required",
                "At least one of password or comment must be specified",
            )

        data: dict[str, str] = {}
        if password is not None:
            data["password"] = password
        if comment is not None:
            data["comment"] = comment
        response = self.request(
            TransportEndpoint(
                "PATCH", self._user_path(self._get_users_path(), username)
            ),
            json={"data": data},
        )
        self._parse_response(response, "modify_user")

    def remove_user(self, username: str) -> None:
        """Delete one SSH user from the item DELETE operation."""
        if not username:
            raise FeatureError("username_required", "Username is required")
        response = self.request(
            TransportEndpoint(
                "DELETE", self._user_path(self._get_users_path(), username)
            )
        )
        self._parse_response(response, "remove_user")
