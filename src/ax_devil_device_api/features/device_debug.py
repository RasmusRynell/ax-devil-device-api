from dataclasses import dataclass
from typing import Any, Optional
from .base import FeatureClient
from ..core.types import FeatureResponse, FeatureError
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError as UtilsFeatureError


class DeviceDebugClient(FeatureClient[Any]):
    API_VERSION = "1.0"
    
    # Default timeouts for long-running operations (in seconds)
    DOWNLOAD_TIMEOUT = 300  # 5 minutes
    CORE_DUMP_TIMEOUT = 600  # 10 minutes
    
    SERVER_REPORT_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/serverreport.cgi?mode=zip_with_image")
    CRASH_REPORT_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/debug/debug.tgz")
    NETWORK_TRACE_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/debug/debug.tgz?cmd=pcapdump")
    PING_TEST_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/pingtest.cgi")
    TCP_TEST_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/tcptest.cgi")
    CORE_DUMP_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/debug/debug.tgz?listen")
    
    def download_server_report(self) -> FeatureResponse[bytes]:
        response = self.request(
            self.SERVER_REPORT_ENDPOINT,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.DOWNLOAD_TIMEOUT
        )
        if not response.is_success:
            return FeatureResponse.from_transport(response)
        return FeatureResponse.ok(response.raw_response.content)
    
    def download_crash_report(self) -> FeatureResponse[bytes]:
        response = self.request(
            self.CRASH_REPORT_ENDPOINT,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.DOWNLOAD_TIMEOUT
        )
        if not response.is_success:
            return FeatureResponse.from_transport(response)
        return FeatureResponse.ok(response.raw_response.content)
    
    def download_network_trace(self, duration: int = 30, interface: Optional[str] = None) -> FeatureResponse[bytes]:
        params = {"duration": duration}
        if interface:
            params["interface"] = interface
        # Add duration to timeout to account for capture time
        total_timeout = self.DOWNLOAD_TIMEOUT + duration
        response = self.request(
            self.NETWORK_TRACE_ENDPOINT,
            params=params,
            headers={"Content-Type": "application/octet-stream"},
            timeout=total_timeout
        )
        if not response.is_success:
            return FeatureResponse.from_transport(response)
        return FeatureResponse.ok(response.raw_response.content)
    
    def ping_test(self, target: str) -> FeatureResponse[str]:
        if not target:
            return FeatureResponse.create_error(FeatureError("parameter_required", "Target IP or hostname is required"))
        response = self.request(
            self.PING_TEST_ENDPOINT,
            params={"ip": target},
            headers={"Accept": "application/json"}
        )
        if not response.is_success:
            return FeatureResponse.from_transport(response)
        try:
            data = response.raw_response.text
            return FeatureResponse.ok(data)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError("parse_failed", f"Error parsing ping response: {str(e)}"))
    
    def port_open_test(self, address: str, port: int) -> FeatureResponse[str]:
        if not address or not port:
            return FeatureResponse.create_error(FeatureError("parameter_required", "Address and port are required"))
        response = self.request(
            self.TCP_TEST_ENDPOINT,
            params={"address": address, "port": port},
            headers={"Accept": "application/json"}
        )
        if not response.is_success:
            return FeatureResponse.from_transport(response)
        try:
            data = response.raw_response.text
            return FeatureResponse.ok(data)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError("parse_failed", f"Error parsing port test response: {str(e)}"))
    
    def collect_core_dump(self) -> FeatureResponse[bytes]:
        response = self.request(
            self.CORE_DUMP_ENDPOINT,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.CORE_DUMP_TIMEOUT
        )
        if not response.is_success:
            return FeatureResponse.from_transport(response)
        return FeatureResponse.ok(response.raw_response.content) 