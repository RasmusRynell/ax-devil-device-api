from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.parse import urlencode


@dataclass
class TransportEndpoint:
    """Definition of a device API endpoint."""
    method: str
    path: str

    def __post_init__(self) -> None:
        """Normalize the endpoint configuration."""
        self.method = self.method.upper()
        self.path = self.path.strip()

        if not self.path.startswith('/'):
            self.path = f"/{self.path}"

    def build_url(self, base_url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build the full URL for this endpoint."""
        url = f"{base_url.rstrip('/')}{self.path}"

        if params:
            param_str = urlencode(params)
            url = f"{url}{'&' if '?' in url else '?'}{param_str}"

        return url

    def __repr__(self) -> str:
        return f"TransportEndpoint({self.method}, {self.path})"
