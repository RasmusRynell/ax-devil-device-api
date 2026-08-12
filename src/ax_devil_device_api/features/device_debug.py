from typing import Any

from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from .base import FeatureClient


class DeviceDebugClient(FeatureClient[Any]):
    API_VERSION = "1.0"

    # Default timeouts for long-running operations (in seconds)
    DOWNLOAD_TIMEOUT = 300  # 5 minutes
    CORE_DUMP_TIMEOUT = 600  # 10 minutes

    SERVER_REPORT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/serverreport.cgi")
    CRASH_REPORT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/debug/debug.tgz")
    NETWORK_TRACE_ENDPOINT = TransportEndpoint(
        "GET", "/axis-cgi/debug/debug.tgz?cmd=pcapdump"
    )
    PING_TEST_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/pingtest.cgi")
    TCP_TEST_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/tcptest.cgi")
    CORE_DUMP_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/debug/debug.tgz?listen")

    SERVER_REPORT_MODES = frozenset({"zip", "zip_with_image"})
    ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
    PCAP_SIGNATURES = (
        b"\xd4\xc3\xb2\xa1",
        b"\xa1\xb2\xc3\xd4",
        b"\x4d\x3c\xb2\xa1",
        b"\xa1\xb2\x3c\x4d",
        b"\x0a\x0d\x0d\x0a",
    )

    def download_server_report(self, mode: str = "zip_with_image") -> bytes:
        """Download a ZIP server report from the legacy CGI endpoint.

        ``zip_with_image`` preserves the existing Python API default. Use
        ``mode="zip"`` for the portable report format supported across more
        products.
        """
        if not isinstance(mode, str) or mode not in self.SERVER_REPORT_MODES:
            raise FeatureError(
                "invalid_parameter", "mode must be 'zip' or 'zip_with_image'"
            )

        response = self.request(
            self.SERVER_REPORT_ENDPOINT,
            params={"mode": mode},
            headers={"Content-Type": None, "Accept-Encoding": "identity"},
            timeout=self.DOWNLOAD_TIMEOUT,
        )
        return self._validate_binary_response(
            response,
            "download_server_report",
            self.ZIP_SIGNATURES,
            expected_content_type="application/zip",
            resource_name="server report",
        )

    def download_crash_report(self) -> bytes:
        """Download a gzip-compressed crash report from the device."""
        response = self.request(
            self.CRASH_REPORT_ENDPOINT,
            headers={"Content-Type": None, "Accept-Encoding": "identity"},
            timeout=self.DOWNLOAD_TIMEOUT,
        )
        return self._validate_binary_response(
            response,
            "download_crash_report",
            (b"\x1f\x8b\x08",),
            resource_name="crash report",
        )

    def download_network_trace(
        self, duration: int = 30, interface: str | None = None
    ) -> bytes:
        """Capture and download a PCAP or PCAPNG trace from a legacy CGI endpoint.

        The Requests inactivity timeout includes grace for the requested
        capture duration. It is not a hard wall-clock deadline.
        """
        if isinstance(duration, bool) or not isinstance(duration, int) or duration <= 0:
            raise FeatureError(
                "invalid_parameter", "duration must be a positive integer"
            )

        if interface is not None and (
            not isinstance(interface, str) or not interface.strip()
        ):
            raise FeatureError(
                "invalid_parameter",
                "interface must be a nonempty string when supplied",
            )

        params: dict[str, int | str] = {"duration": duration}
        if interface is not None:
            params["interface"] = interface
        # Requests treats this as an inactivity timeout, not a hard deadline.
        total_timeout = self.DOWNLOAD_TIMEOUT + duration
        response = self.request(
            self.NETWORK_TRACE_ENDPOINT,
            params=params,
            headers={"Content-Type": None, "Accept-Encoding": "identity"},
            timeout=total_timeout,
        )
        return self._validate_binary_response(
            response,
            "network_trace",
            self.PCAP_SIGNATURES,
            resource_name="network trace",
        )

    def ping_test(self, target: str) -> str:
        """Run a ping test and return the device's raw text response."""
        if not isinstance(target, str) or not target.strip():
            raise FeatureError(
                "parameter_required", "Target IP or hostname is required"
            )
        response = self.request(
            self.PING_TEST_ENDPOINT,
            params={"ip": target},
            headers={"Accept": None},
        )
        if response.status_code != 200:
            raise FeatureError(
                "ping_test_error",
                f"Failed to ping test: HTTP {response.status_code}",
            )
        return response.text

    def port_open_test(self, address: str, port: int) -> str:
        """Check a TCP port and return the device's raw text response."""
        if not isinstance(address, str) or not address.strip():
            raise FeatureError("parameter_required", "Address is required")
        if (
            isinstance(port, bool)
            or not isinstance(port, int)
            or not 1 <= port <= 65535
        ):
            raise FeatureError("invalid_parameter", "port must be between 1 and 65535")
        response = self.request(
            self.TCP_TEST_ENDPOINT,
            params={"address": address, "port": port},
            headers={"Accept": None},
        )
        if response.status_code != 200:
            raise FeatureError(
                "port_open_test_error",
                f"Failed to port open test: HTTP {response.status_code}",
            )
        return response.text

    def collect_core_dump(self) -> bytes:
        """Collect a legacy CGI core dump using buffered, non-streaming I/O.

        The request can remain alive for a long time and the complete artifact
        is held in memory before this method returns.
        """
        response = self.request(
            self.CORE_DUMP_ENDPOINT,
            headers={
                "Content-Type": "application/octet-stream",
                "Accept-Encoding": "identity",
            },
            timeout=self.CORE_DUMP_TIMEOUT,
        )
        if response.status_code != 200:
            raise FeatureError(
                "core_dump_error",
                f"Failed to collect core dump: HTTP {response.status_code}",
            )
        return response.content

    @staticmethod
    def _validate_binary_response(
        response: Any,
        operation: str,
        signatures: tuple[bytes, ...],
        expected_content_type: str | None = None,
        resource_name: str | None = None,
    ) -> bytes:
        """Apply representation guards without fully parsing the artifact.

        Requests transparently decodes HTTP ``Content-Encoding`` before
        exposing ``response.content``. Returning that content preserves the
        diagnostic artifact rather than applying a second decompression step.
        """
        error_code = f"{operation}_error"
        name = resource_name or operation.replace("_", " ")
        if response.status_code != 200:
            raise FeatureError(
                error_code,
                f"Failed to download {name}: HTTP {response.status_code}",
            )

        content = response.content
        if not isinstance(content, bytes) or not content:
            raise FeatureError(error_code, f"{name.capitalize()} response is empty")

        if expected_content_type is not None:
            content_type = response.headers.get("Content-Type", "")
            media_type = content_type.split(";", 1)[0].strip().lower()
            if media_type != expected_content_type:
                raise FeatureError(
                    error_code,
                    f"{name.capitalize()} response has invalid Content-Type",
                )

        if not any(content.startswith(signature) for signature in signatures):
            raise FeatureError(
                error_code,
                f"{name.capitalize()} response has an invalid file signature",
            )
        return content
