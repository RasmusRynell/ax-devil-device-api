from typing import Any, Optional
from .base import FeatureClient
from ..core.types import FeatureError
from ..core.endpoints import TransportEndpoint


class DeviceDebugClient(FeatureClient[Any]):
    API_VERSION = "1.0"
    
    # Default timeouts for long-running operations (in seconds)
    DOWNLOAD_TIMEOUT = 300  # 5 minutes
    CORE_DUMP_TIMEOUT = 600  # 10 minutes
    
    SERVER_REPORT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/serverreport.cgi?mode=zip_with_image")
    CRASH_REPORT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/debug/debug.tgz")
    NETWORK_TRACE_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/debug/debug.tgz?cmd=pcapdump")
    PING_TEST_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/pingtest.cgi")
    TCP_TEST_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/tcptest.cgi")
    CORE_DUMP_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/debug/debug.tgz?listen")
    
    def download_server_report(self) -> bytes:
        response = self.request(
            self.SERVER_REPORT_ENDPOINT,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.DOWNLOAD_TIMEOUT
        )
        if response.status_code != 200:
            raise FeatureError(
                "download_server_report_error",
                f"Failed to download server report: HTTP {response.status_code}"
            )
        return response.content
    
    def download_crash_report(self) -> bytes:
        response = self.request(
            self.CRASH_REPORT_ENDPOINT,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.DOWNLOAD_TIMEOUT
        )
        if response.status_code != 200:
            raise FeatureError(
                "download_crash_report_error",
                f"Failed to download crash report: HTTP {response.status_code}"
            )
        return response.content
    
    def download_network_trace(self, duration: int = 30, interface: Optional[str] = None) -> bytes:
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
        if response.status_code != 200:
            raise FeatureError(
                "network_trace_error",
                f"Failed to download network trace: HTTP {response.status_code}"
            )
        return response.content
    
    def ping_test(self, target: str) -> str:
        if not target:
            raise FeatureError("parameter_required", "Target IP or hostname is required")
        response = self.request(
            self.PING_TEST_ENDPOINT,
            params={"ip": target},
            headers={"Accept": "application/json"}
        )
        if response.status_code != 200:
            raise FeatureError(
                "ping_test_error",
                f"Failed to ping test: HTTP {response.status_code}"
            )
        return response.text
    
    def port_open_test(self, address: str, port: int) -> str:
        if not address or not port:
            raise FeatureError("parameter_required", "Address and port are required")
        response = self.request(
            self.TCP_TEST_ENDPOINT,
            params={"address": address, "port": port},
            headers={"Accept": "application/json"}
        )
        if response.status_code != 200:
            raise FeatureError(
                "port_open_test_error",
                f"Failed to port open test: HTTP {response.status_code}"
            )
        return response.text
    
    def collect_core_dump(self) -> bytes:
        response = self.request(
            self.CORE_DUMP_ENDPOINT,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.CORE_DUMP_TIMEOUT
        )
        if response.status_code != 200:
            raise FeatureError(
                "core_dump_error",
                f"Failed to collect core dump: HTTP {response.status_code}"
            )
        return response.content
