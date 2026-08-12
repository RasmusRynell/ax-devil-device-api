from dataclasses import dataclass
from urllib.parse import parse_qsl

from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from .base import FeatureClient


@dataclass(frozen=True)
class StreamProfile:
    """Saved video stream configuration on a device."""

    name: str
    description: str
    parameters: dict[str, str]

    @classmethod
    def from_api_data(cls, data: dict) -> "StreamProfile":
        """Create a stream profile from a VAPIX response object."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            parameters=dict(parse_qsl(data.get("parameters", ""), keep_blank_values=True)),
        )


@dataclass(frozen=True)
class VideoChannel:
    """Configured video channel and its streaming capabilities."""

    channel: int
    name: str
    enabled: bool
    source: str
    channel_types: tuple[str, ...]
    default_resolution: str | None
    default_fps: str | None
    supported_codecs: tuple[str, ...]
    supported_resolutions: tuple[str, ...]
    resolutions_by_codec: dict[str, tuple[str, ...]]


class MediaClient(FeatureClient):
    """Client for camera media operations.
    
    Provides functionality for:
    - Capturing JPEG snapshots
    - Configuring media parameters
    - Retrieving media capabilities
    """
    
    # Endpoint definitions
    SNAPSHOT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/jpg/image.cgi")
    STREAM_PROFILE_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/streamprofile.cgi")
    PARAMETERS_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/param.cgi")

    def list_video_channels(self) -> list[VideoChannel]:
        """List configured video channels, defaults, and supported capabilities."""
        response = self.request(
            self.PARAMETERS_ENDPOINT,
            params={"action": "list", "group": "Image,Properties.Image"},
            headers={"Accept": "text/plain"},
        )
        parameters = self._parse_parameter_response(response)

        try:
            channel_count = int(parameters["Image.NbrOfConfigs"])
        except (KeyError, ValueError) as error:
            raise FeatureError(
                "invalid_response",
                "Video channel response has no valid Image.NbrOfConfigs value",
            ) from error

        supported_codecs = self._split_values(parameters.get("Properties.Image.Format", ""))
        channels = []
        for channel_index in range(channel_count):
            channels.append(self._create_video_channel(channel_index, parameters, supported_codecs))
        return channels

    def _create_video_channel(
        self,
        channel_index: int,
        parameters: dict[str, str],
        supported_codecs: tuple[str, ...],
    ) -> VideoChannel:
        """Create one video channel from Image and Properties.Image parameters."""
        image_prefix = f"Image.I{channel_index}"
        properties_prefix = f"Properties.Image.I{channel_index}"
        name = parameters.get(f"{image_prefix}.Name")
        enabled = parameters.get(f"{image_prefix}.Enabled")
        if name is None or enabled not in {"yes", "no"}:
            raise FeatureError(
                "invalid_response",
                f"Video channel {channel_index + 1} has no valid name or enabled state",
            )

        generic_resolutions = self._split_values(
            parameters.get(
                f"{properties_prefix}.Resolution",
                parameters.get("Properties.Image.Resolution", ""),
            )
        )
        resolutions_by_codec = {}
        for codec in supported_codecs:
            property_codec = "JPEG" if codec in {"jpeg", "mjpeg"} else codec.upper()
            resolutions = self._split_values(
                parameters.get(f"{properties_prefix}.{property_codec}.Resolution", "")
            )
            if resolutions:
                resolutions_by_codec[codec] = resolutions

        return VideoChannel(
            channel=channel_index + 1,
            name=name,
            enabled=enabled == "yes",
            source=parameters.get(f"{image_prefix}.Source", ""),
            channel_types=self._split_values(parameters.get(f"{image_prefix}.Type", "")),
            default_resolution=parameters.get(f"{image_prefix}.Appearance.Resolution"),
            default_fps=parameters.get(f"{image_prefix}.Stream.FPS"),
            supported_codecs=supported_codecs,
            supported_resolutions=generic_resolutions,
            resolutions_by_codec=resolutions_by_codec,
        )

    @staticmethod
    def _parse_parameter_response(response) -> dict[str, str]:
        """Parse a Parameter Management API response."""
        if response.status_code != 200:
            raise FeatureError(
                "video_channels_failed",
                f"Failed to list video channels: HTTP {response.status_code}, {response.text}",
            )

        lines = [line.strip() for line in response.text.splitlines() if line.strip()]
        error_line = next((line for line in lines if line.startswith("#")), None)
        if error_line is not None:
            raise FeatureError("video_channels_failed", error_line)

        parameters = {}
        for line in lines:
            if "=" not in line:
                raise FeatureError("invalid_response", f"Invalid video channel parameter: {line}")
            name, value = line.split("=", 1)
            parameters[name.removeprefix("root.")] = value
        return parameters

    @staticmethod
    def _split_values(value: str) -> tuple[str, ...]:
        """Split a comma-separated VAPIX parameter value."""
        return tuple(item.strip() for item in value.split(",") if item.strip())

    def list_stream_profiles(self, names: list[str] | None = None) -> list[StreamProfile]:
        """List saved video stream profiles, optionally filtered by name."""
        requested_profiles = [{"name": name} for name in names or []]
        payload = {
            "apiVersion": "1.0",
            "method": "list",
            "params": {"streamProfileName": requested_profiles},
        }
        response = self.request(
            self.STREAM_PROFILE_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 404:
            return self._list_legacy_stream_profiles(names)

        if response.status_code != 200:
            raise FeatureError(
                "stream_profiles_failed",
                f"Failed to list stream profiles: HTTP {response.status_code}, {response.text}",
            )

        try:
            result = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response",
                f"Failed to parse stream profile response: {error}",
            ) from error

        if not isinstance(result, dict):
            raise FeatureError("invalid_response", "Stream profile response is not an object")

        if "error" in result:
            error = result["error"]
            raise FeatureError(
                f"stream_profiles_api_error_{error.get('code', 'unknown')}",
                error.get("message", "Unknown stream profile API error"),
            )

        data = result.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("streamProfile"), list):
            raise FeatureError("invalid_response", "Stream profile response has no profile list")

        profiles = data["streamProfile"]
        if any(not isinstance(profile, dict) or not isinstance(profile.get("name"), str) for profile in profiles):
            raise FeatureError("invalid_response", "Stream profile response contains an invalid profile")
        return [StreamProfile.from_api_data(profile) for profile in profiles]

    def _list_legacy_stream_profiles(self, names: list[str] | None) -> list[StreamProfile]:
        """List profiles through Parameter Management on older devices."""
        response = self.request(
            self.PARAMETERS_ENDPOINT,
            params={"action": "list", "group": "StreamProfile"},
            headers={"Accept": "text/plain"},
        )
        parameters = self._parse_parameter_response(response)
        profiles_by_group: dict[str, dict[str, str]] = {}
        for parameter_name, value in parameters.items():
            parts = parameter_name.split(".", 2)
            if len(parts) != 3 or parts[0] != "StreamProfile":
                continue
            profiles_by_group.setdefault(parts[1], {})[parts[2]] = value

        profiles = []
        for profile_data in profiles_by_group.values():
            name = profile_data.get("Name")
            if name is None:
                raise FeatureError("invalid_response", "Legacy stream profile has no name")
            if names is None or name in names:
                profiles.append(
                    StreamProfile.from_api_data(
                        {
                            "name": name,
                            "description": profile_data.get("Description", ""),
                            "parameters": profile_data.get("Parameters", ""),
                        }
                    )
                )
        return profiles
    
    def get_snapshot(
        self,
        resolution: str | None = None,
        compression: int | None = None,
        camera_head: int | None = None,
    ) -> bytes:
        """Capture a JPEG snapshot from the camera.
        
        Args:
            resolution: Optional device-supported image resolution
            compression: Optional JPEG compression level between 0 and 100
            camera_head: Optional camera head identifier for multi-sensor devices
            
        Returns:
            bytes containing the image data on success
        """
        if compression is not None and not isinstance(compression, int):
            raise FeatureError(
                "invalid_parameter", 
                "Compression must be an integer between 0 and 100"
            )
            
        if compression is not None and not (0 <= compression <= 100):
            raise FeatureError(
                "invalid_parameter",
                "Compression must be between 0 and 100"
            )

        if camera_head is not None and camera_head < 1:
            raise FeatureError(
                "invalid_parameter",
                "Camera head must be at least 1"
            )
            
        params = {}
        if resolution is not None:
            params["resolution"] = resolution
        if compression is not None:
            params["compression"] = compression
        if camera_head is not None:
            params["camera"] = camera_head

        response = self.request(
            self.SNAPSHOT_ENDPOINT,
            params=params or None,
            headers={"Accept": "image/jpeg"}
        )
            
        if response.status_code != 200:
            raise FeatureError(
                "snapshot_failed",
                f"Failed to capture snapshot: HTTP {response.status_code}, {response.text}"
            )

        content_type = response.headers.get("Content-Type", "")
        media_type = content_type.split(";", 1)[0].strip().lower()
        if media_type != "image/jpeg":
            raise FeatureError(
                "invalid_response",
                f"Snapshot response has invalid Content-Type: {content_type or 'missing'}"
            )
            
        return response.content