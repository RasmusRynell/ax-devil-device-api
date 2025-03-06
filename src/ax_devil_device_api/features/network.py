import requests
from dataclasses import dataclass
from typing import Optional, Dict, List
from .base import FeatureClient
from ..core.types import FeatureResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError

@dataclass
class NetworkInfo:
    """Network interface information.
    
    Attributes:
        interface_name: Name of the network interface (e.g., "eth0")
        mac_address: MAC address of the interface
        ip_address: Current IP address
        subnet_mask: Network subnet mask
        gateway: Default gateway
        dns_servers: List of configured DNS servers
        link_status: Whether the link is up
        link_speed: Current link speed in Mbps
        duplex_mode: Full or half duplex
    """
    interface_name: str
    mac_address: str
    ip_address: str
    subnet_mask: str
    gateway: str
    dns_servers: List[str]
    link_status: bool
    link_speed: Optional[int] = None
    duplex_mode: Optional[str] = None

    @classmethod
    def from_params(cls, params: Dict[str, str], interface: str = "eth0") -> 'NetworkInfo':
        """Create instance from parameter dictionary."""
        def get_param(key: str, default: str = "unknown") -> str:
            return params.get(f"Network.{interface}.{key}", params.get(key, default))
        
        dns_servers = []
        for i in range(1, 5):  # Check up to 4 DNS servers
            dns = get_param(f"DNS.Server{i}")
            if dns and dns != "unknown":
                dns_servers.append(dns)
                
        return cls(
            interface_name=interface,
            mac_address=get_param("MacAddress"),
            ip_address=get_param("IPAddress"),
            subnet_mask=get_param("SubnetMask"),
            gateway=get_param("Gateway"),
            dns_servers=dns_servers,
            link_status=get_param("LinkStatus").lower() == "up",
            link_speed=int(get_param("LinkSpeed", "0")) if get_param("LinkSpeed", "0").isdigit() else None,
            duplex_mode=get_param("Duplex", None)
        )

class NetworkClient(FeatureClient):
    """Client for network configuration operations."""
    
    # Endpoint definitions
    PARAMS_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/param.cgi")
    NETWORK_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/network_status.cgi")
    
    def _parse_param_response(self, response: requests.Response) -> FeatureResponse[Dict[str, str]]:
        """Parse raw parameter response into dictionary."""
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "invalid_response",
                f"Invalid parameter response: HTTP {response.status_code}"
            ))
            
        try:
            lines = response.text.strip().split('\n')
            params = dict(line.split('=', 1) for line in lines if '=' in line)
            return FeatureResponse.ok(params)
        except Exception as e:
            return FeatureResponse(error=FeatureError(
                "parse_error",
                f"Failed to parse parameters: {str(e)}"
            ))

    def get_network_info(self, interface: str = "eth0") -> FeatureResponse[NetworkInfo]:
        """Get network interface information."""
        response = self.request(
            self.PARAMS_ENDPOINT,
            params={"action": "list", "group": "Network"},
            headers={"Accept": "text/plain"}
        )
        
        parsed = self._parse_param_response(response)
        if not parsed.is_success:
            return FeatureResponse.create_error(FeatureError(
                "fetch_failed",
                "Failed to get network parameters",
                details={"original_error": parsed.error}
            ))
            
        try:
            return FeatureResponse.ok(NetworkInfo.from_params(parsed.data, interface))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "network_parse_failed",
                "Failed to parse network info",
                details={"error": str(e)}
            )) 