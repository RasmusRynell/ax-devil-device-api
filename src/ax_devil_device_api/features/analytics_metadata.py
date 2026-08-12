"""Axis analytics metadata producer configuration client."""

from dataclasses import dataclass
from typing import Any

from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from .base import FeatureClient


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
    video_channels: list[VideoChannel]

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> "Producer":
        """Create Producer from API response data."""
        if not isinstance(data, dict) or not isinstance(data.get("name"), str):
            raise FeatureError(
                "invalid_response", "Metadata producer entry must contain a name"
            )
        raw_channels = data.get("videochannels")
        if not isinstance(raw_channels, list):
            raise FeatureError(
                "invalid_response",
                f"Metadata producer '{data['name']}' channels must be an array",
            )
        channels = [
            _video_channel_from_api_data(data["name"], ch) for ch in raw_channels
        ]
        nice_name = data.get("niceName")
        if "niceName" in data and not isinstance(nice_name, str):
            raise FeatureError(
                "invalid_response", "Metadata field 'niceName' must be a string"
            )
        return cls(
            name=data["name"],
            nice_name=nice_name,
            video_channels=channels,
        )


@dataclass(frozen=True)
class MetadataSample:
    """Represents a metadata sample frame.

    Attributes:
        producer_name: Name of the producer that generated this sample
        sample_frame_xml: XML content of the sample frame
    """

    producer_name: str
    sample_frame_xml: str

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> "MetadataSample":
        """Create MetadataSample from API response data."""
        if not isinstance(data, dict) or not isinstance(data.get("name"), str):
            raise FeatureError(
                "invalid_response", "Analytics metadata sample entry is invalid"
            )
        if not isinstance(data.get("sampleFrameXML"), str):
            raise FeatureError(
                "invalid_response",
                f"Metadata sample for '{data['name']}' is invalid",
            )
        return cls(
            producer_name=data["name"],
            sample_frame_xml=data.get("sampleFrameXML", ""),
        )


class AnalyticsMetadataClient(FeatureClient[list[Producer]]):
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
    ) -> dict[str, Any]:
        """Make a JSON-RPC style request to the analytics metadata API."""
        payload: dict[str, Any] = {"context": "cli", "method": method}
        if method != "getSupportedVersions":
            payload["apiVersion"] = "1.0"
            if params is not None:
                payload["params"] = params

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
            error = result["error"]
            if not isinstance(error, dict):
                raise FeatureError(
                    "api_error_unknown",
                    str(error) if error is not None else "Unknown API error",
                )
            raise FeatureError(
                f"api_error_{error.get('code', 'unknown')}",
                str(error.get("message", "Unknown API error")),
                details=error,
            )

        data = result.get("data")
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Analytics metadata response data must be an object"
            )
        return data

    def list_producers(self) -> list[Producer]:
        """List all available metadata producers.

        Returns:
            List of Producer objects with their channel configurations
        """
        data = self._make_request("listProducers")
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Analytics metadata producers must be an object"
            )

        producers: list[Producer] = []
        raw_producers = data.get("producers")
        if not isinstance(raw_producers, list):
            raise FeatureError(
                "invalid_response", "Analytics metadata producers must be an array"
            )
        for producer_data in raw_producers:
            producers.append(Producer.from_api_data(producer_data))

        return producers

    def set_enabled_producers(self, producers: list[Producer]) -> None:
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

    def get_supported_metadata(
        self, producer_names: list[str] | None = None
    ) -> list[MetadataSample]:
        """Get sample metadata frames for specified producers or all producers.

        Args:
            producer_names: Optional list of producer names. Omit to request all.

        Returns:
            List of MetadataSample objects containing sample frames
        """
        params = {"producers": producer_names} if producer_names else None
        data = self._make_request("getSupportedMetadata", params)
        raw_samples = data.get("producers")
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
            samples.append(MetadataSample.from_api_data(sample))
        return samples

    def get_supported_versions(self) -> list[str]:
        """Get supported API versions.

        Returns:
            List of supported version strings
        """
        data = self._make_request("getSupportedVersions")
        return _version_list(data.get("apiVersions"), "apiVersions")
