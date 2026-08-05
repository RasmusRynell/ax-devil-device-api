"""Axis analytics metadata producer configuration client."""

from dataclasses import dataclass, field
from typing import Any, List, Optional

from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


def _video_channel_from_api_data(producer_name: str, data: Any) -> "VideoChannel":
    """Validate and convert one advertised producer channel."""
    if not isinstance(data, dict):
        raise FeatureError(
            "invalid_response",
            f"Metadata producer '{producer_name}' channel entry is invalid",
        )
    channel = data.get("channel")
    enabled = data.get("enabled")
    if (
        not isinstance(channel, int)
        or isinstance(channel, bool)
        or not isinstance(enabled, bool)
    ):
        raise FeatureError(
            "invalid_response",
            f"Metadata producer '{producer_name}' channel entry is invalid",
        )
    return VideoChannel(channel=channel, enabled=enabled)


def _version_list(value: Any, context: str) -> list[str]:
    """Validate a response version list."""
    if not isinstance(value, list) or not all(
        isinstance(version, str) for version in value
    ):
        raise FeatureError(
            "invalid_response",
            f"Metadata versions for '{context}' must be an array of strings",
        )
    return value


def _api_error_details(error: Any) -> tuple[str, str]:
    """Normalize an API error object without assuming its advertised shape."""
    if not isinstance(error, dict):
        return "unknown", str(error) if error is not None else "Unknown API error"
    return str(error.get("code", "unknown")), str(
        error.get("message", "Unknown API error")
    )


def _optional_string(value: Any, field_name: str) -> str | None:
    """Validate an optional string field in a device response."""
    if value is not None and not isinstance(value, str):
        raise FeatureError(
            "invalid_response", f"Metadata field '{field_name}' must be a string"
        )
    return value


@dataclass(frozen=True)
class VideoChannel:
    """Represents a video channel configuration for a producer.

    Attributes:
        channel: Channel number/identifier
        enabled: Whether the producer is enabled on this channel
    """

    channel: int
    enabled: bool


@dataclass(frozen=True)
class Producer:
    """Represents an analytics metadata producer.

    Attributes:
        name: Internal name of the producer
        nice_name: Human-readable name of the producer
        video_channels: List of video channels this producer can operate on
    """

    name: str
    nice_name: str | None
    video_channels: List[VideoChannel]
    api_versions: list[str] = field(default_factory=list)

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> "Producer":
        """Create Producer from API response data."""
        if not isinstance(data, dict) or not isinstance(data.get("name"), str):
            raise FeatureError(
                "invalid_response", "Metadata producer entry must contain a name"
            )
        raw_channels = data.get("videochannels", data.get("videoChannels", []))
        if not isinstance(raw_channels, list):
            raise FeatureError(
                "invalid_response",
                f"Metadata producer '{data['name']}' channels must be an array",
            )
        channels = [
            _video_channel_from_api_data(data["name"], ch) for ch in raw_channels
        ]
        return cls(
            name=data["name"],
            nice_name=_optional_string(data.get("niceName"), "niceName"),
            video_channels=channels,
            api_versions=_version_list(data.get("apiVersions", []), data["name"]),
        )


@dataclass(frozen=True)
class MetadataSample:
    """Represents a metadata sample frame.

    Attributes:
        producer_name: Name of the producer that generated this sample
        sample_frame_xml: XML content of the sample frame
        schema_xml: XML schema for the metadata (if available)
    """

    producer_name: str
    sample_frame_xml: str
    schema_xml: Optional[str] = None

    @classmethod
    def from_api_data(
        cls, producer_name: str, data: dict[str, Any]
    ) -> "MetadataSample":
        """Create MetadataSample from API response data."""
        if not isinstance(data, dict) or not isinstance(
            data.get("sampleFrameXML"), str
        ):
            raise FeatureError(
                "invalid_response", f"Metadata sample for '{producer_name}' is invalid"
            )
        return cls(
            producer_name=producer_name,
            sample_frame_xml=data.get("sampleFrameXML", ""),
            schema_xml=_optional_string(data.get("schemaXML"), "schemaXML"),
        )


class AnalyticsMetadataClient(FeatureClient[List[Producer]]):
    """Client for analytics metadata producer configuration.

    Provides functionality for:
    - Listing available metadata producers
    - Enabling/disabling producers on video channels
    - Getting sample metadata frames
    - Checking supported API versions
    """

    ANALYTICS_METADATA_ENDPOINT = TransportEndpoint(
        "POST", "/axis-cgi/analyticsmetadataconfig.cgi"
    )

    def _make_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a JSON-RPC style request to the analytics metadata API."""
        if params is None:
            params = {}

        payload = {"context": "cli", "method": method, "params": params}
        if method != "getSupportedVersions":
            payload["apiVersion"] = "1.0"

        response = self.request(
            self.ANALYTICS_METADATA_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 200:
            raise FeatureError(
                "request_failed",
                f"Analytics metadata request failed: HTTP {response.status_code}, {response.text}",
            )

        try:
            result = response.json()
        except ValueError as e:
            raise FeatureError(
                "invalid_response", f"Failed to parse JSON response: {e}"
            )

        if not isinstance(result, dict):
            raise FeatureError(
                "invalid_response", "Analytics metadata response must be a JSON object"
            )

        if "error" in result:
            error_code, error_message = _api_error_details(result["error"])
            raise FeatureError(
                f"api_error_{error_code}",
                error_message,
            )

        return result.get("data", {})

    def list_producers(self) -> List[Producer]:
        """List all available metadata producers.

        Returns:
            List of Producer objects with their channel configurations
        """
        data = self._make_request("listProducers")
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Analytics metadata producers must be an object"
            )

        producers = []
        raw_producers = data.get("producers")
        if not isinstance(raw_producers, list):
            raise FeatureError(
                "invalid_response", "Analytics metadata producers must be an array"
            )
        for producer_data in raw_producers:
            producers.append(Producer.from_api_data(producer_data))

        return producers

    def set_enabled_producers(self, producers: List[Producer]) -> None:
        """Enable or disable producers on specific video channels.

        Args:
            producers: List of producers with desired channel configurations
        """
        if not producers:
            raise FeatureError(
                "invalid_parameter", "At least one producer must be specified"
            )

        producer_configs = []
        for producer in producers:
            channels = [
                {"channel": ch.channel, "enabled": ch.enabled}
                for ch in producer.video_channels
            ]
            producer_configs.append({"name": producer.name, "videochannels": channels})

        params = {"producers": producer_configs}
        self._make_request("setEnabledProducers", params)

    def get_supported_metadata(self, producer_names: List[str]) -> List[MetadataSample]:
        """Get sample metadata frames for specified producers.

        Args:
            producer_names: List of producer names to get samples for

        Returns:
            List of MetadataSample objects containing sample frames
        """
        if not producer_names:
            raise FeatureError(
                "invalid_parameter", "At least one producer name must be specified"
            )

        params = {"producers": producer_names}
        data = self._make_request("getSupportedMetadata", params)
        if isinstance(data, dict):
            raw_samples = data.get("producers")
        else:
            raw_samples = data
        if not isinstance(raw_samples, list):
            raise FeatureError(
                "invalid_response", "Analytics metadata samples must be an array"
            )

        samples = []
        for sample in raw_samples:
            if not isinstance(sample, dict):
                raise FeatureError(
                    "invalid_response", "Analytics metadata sample entry is invalid"
                )
            producer_name = sample.get("producerName", sample.get("name"))
            if not isinstance(producer_name, str):
                raise FeatureError(
                    "invalid_response", "Analytics metadata sample entry is invalid"
                )
            samples.append(MetadataSample.from_api_data(producer_name, sample))
        return samples

    def get_supported_versions(self) -> List[str]:
        """Get supported API versions.

        Returns:
            List of supported version strings
        """
        data = self._make_request("getSupportedVersions")

        if isinstance(data, list):
            return _version_list(data, "response")
        if isinstance(data, dict) and "supportedVersions" in data:
            return _version_list(data["supportedVersions"], "supportedVersions")
        if isinstance(data, dict) and "versions" in data:
            return _version_list(data["versions"], "versions")
        raise FeatureError(
            "invalid_response",
            "Analytics metadata supported versions must be an array or version envelope",
        )
