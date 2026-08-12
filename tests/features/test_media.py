"""Tests for media operations."""

from unittest.mock import Mock

import pytest

from src.ax_devil_device_api.features.media import MediaClient
from src.ax_devil_device_api.utils.errors import FeatureError


class TestStreamProfiles:
    """Tests for saved video stream profiles."""

    def test_list_stream_profiles(self):
        """Profiles expose names and parsed stream settings."""
        transport = Mock()
        response = Mock(status_code=200)
        response.json.return_value = {
            "data": {
                "streamProfile": [
                    {
                        "name": "HD",
                        "description": "Full HD at 25 FPS",
                        "parameters": "videocodec=h264&resolution=1920x1080&fps=25",
                    }
                ],
                "maxProfiles": 26,
            }
        }
        transport.request.return_value = response

        profiles = MediaClient(transport).list_stream_profiles()

        assert len(profiles) == 1
        assert profiles[0].name == "HD"
        assert profiles[0].description == "Full HD at 25 FPS"
        assert profiles[0].parameters == {
            "videocodec": "h264",
            "resolution": "1920x1080",
            "fps": "25",
        }
        _, request = transport.request.call_args
        assert request["json"] == {
            "apiVersion": "1.0",
            "method": "list",
            "params": {"streamProfileName": []},
        }

    def test_list_named_stream_profiles(self):
        """A name filter uses the VAPIX streamProfileName shape."""
        transport = Mock()
        response = Mock(status_code=200)
        response.json.return_value = {"data": {"streamProfile": []}}
        transport.request.return_value = response

        MediaClient(transport).list_stream_profiles(["HD", "Low bandwidth"])

        _, request = transport.request.call_args
        assert request["json"]["params"] == {
            "streamProfileName": [{"name": "HD"}, {"name": "Low bandwidth"}]
        }

    def test_list_stream_profiles_reports_api_error(self):
        """VAPIX errors returned with HTTP 200 are not treated as success."""
        transport = Mock()
        response = Mock(status_code=200)
        response.json.return_value = {
            "error": {"code": 2006, "message": "Profile does not exist"}
        }
        transport.request.return_value = response

        with pytest.raises(FeatureError) as error:
            MediaClient(transport).list_stream_profiles(["missing"])

        assert error.value.code == "stream_profiles_api_error_2006"
        assert error.value.message == "Profile does not exist"

    def test_list_stream_profiles_falls_back_to_parameter_api(self):
        """Older devices expose stream profiles through Parameter Management."""
        transport = Mock()
        unavailable = Mock(status_code=404, text="Not found")
        legacy = Mock(status_code=200)
        legacy.text = """root.StreamProfile.S0.Name=HD
root.StreamProfile.S0.Description=Full HD
root.StreamProfile.S0.Parameters=videocodec=h264&resolution=1920x1080
root.StreamProfile.S1.Name=Low
root.StreamProfile.S1.Parameters=resolution=640x360
"""
        transport.request.side_effect = [unavailable, legacy]

        profiles = MediaClient(transport).list_stream_profiles(["HD"])

        assert len(profiles) == 1
        assert profiles[0].name == "HD"
        assert profiles[0].parameters["resolution"] == "1920x1080"
        _, request = transport.request.call_args
        assert request["params"] == {"action": "list", "group": "StreamProfile"}

    def test_list_stream_profiles_rejects_malformed_response(self):
        """Malformed successful JSON uses the feature error model."""
        transport = Mock()
        response = Mock(status_code=200)
        response.json.return_value = {"data": {"streamProfile": [{"description": "No name"}]}}
        transport.request.return_value = response

        with pytest.raises(FeatureError) as error:
            MediaClient(transport).list_stream_profiles()

        assert error.value.code == "invalid_response"

    @pytest.mark.integration
    def test_list_stream_profiles_on_device(self, client):
        """Probe stream profile support and response shape on a real device."""
        profiles = client.media.list_stream_profiles()

        assert isinstance(profiles, list)
        for profile in profiles:
            assert profile.name
            assert isinstance(profile.description, str)
            assert isinstance(profile.parameters, dict)


class TestVideoChannels:
    """Tests for configured video channel discovery."""

    def test_list_video_channels(self):
        """Channel defaults and codec-specific capabilities are kept distinct."""
        transport = Mock()
        response = Mock(status_code=200)
        response.text = """root.Image.NbrOfConfigs=2
root.Image.I0.Name=Overview
root.Image.I0.Enabled=yes
root.Image.I0.Source=0
root.Image.I0.Type=Source
root.Image.I0.Appearance.Resolution=1920x1080
root.Image.I0.Stream.FPS=30
root.Image.I1.Name=Crop
root.Image.I1.Enabled=no
root.Image.I1.Source=0
root.Image.I1.Type=Viewarea,Thermal
root.Image.I1.Appearance.Resolution=640x360
root.Image.I1.Stream.FPS=15
root.Properties.Image.Format=jpeg,h264,h265
root.Properties.Image.I0.Resolution=1920x1080,1280x720
root.Properties.Image.I0.H264.Resolution=1920x1080,1280x720
root.Properties.Image.I0.H265.Resolution=1920x1080
root.Properties.Image.I1.Resolution=640x360,320x180
root.Properties.Image.I1.JPEG.Resolution=640x360,320x180
"""
        transport.request.return_value = response

        channels = MediaClient(transport).list_video_channels()

        assert [channel.channel for channel in channels] == [1, 2]
        assert channels[0].name == "Overview"
        assert channels[0].enabled is True
        assert channels[0].default_resolution == "1920x1080"
        assert channels[0].default_fps == "30"
        assert channels[0].supported_codecs == ("jpeg", "h264", "h265")
        assert channels[0].supported_resolutions == ("1920x1080", "1280x720")
        assert channels[0].resolutions_by_codec["h265"] == ("1920x1080",)
        assert channels[1].enabled is False
        assert channels[1].channel_types == ("Viewarea", "Thermal")
        assert channels[1].resolutions_by_codec == {"jpeg": ("640x360", "320x180")}

        _, request = transport.request.call_args
        assert request["params"] == {"action": "list", "group": "Image,Properties.Image"}

    def test_list_video_channels_uses_legacy_global_resolutions(self):
        """Older devices can expose one global resolution list."""
        transport = Mock()
        response = Mock(status_code=200)
        response.text = """root.Image.NbrOfConfigs=1
root.Image.I0.Name=Camera
root.Image.I0.Enabled=yes
root.Properties.Image.Format=jpeg,h264
root.Properties.Image.Resolution=1280x720,640x360
"""
        transport.request.return_value = response

        channel = MediaClient(transport).list_video_channels()[0]

        assert channel.supported_resolutions == ("1280x720", "640x360")
        assert channel.resolutions_by_codec == {}

    def test_list_video_channels_reports_parameter_error(self):
        """Parameter API errors use the feature error model."""
        transport = Mock()
        response = Mock(status_code=200, text="# Error: Requested group does not exist")
        transport.request.return_value = response

        with pytest.raises(FeatureError) as error:
            MediaClient(transport).list_video_channels()

        assert error.value.code == "video_channels_failed"

    @pytest.mark.integration
    def test_list_video_channels_on_device(self, client):
        """Probe video channel discovery on a real device."""
        channels = client.media.list_video_channels()

        assert channels
        for channel in channels:
            assert channel.channel >= 1
            assert channel.name
            assert channel.supported_codecs
            assert channel.supported_resolutions


class TestMediaFeature:
    """Test suite for media feature."""

    def test_get_snapshot_accepts_jpeg_content_type(self):
        """A successful snapshot with the JPEG media type returns its content."""
        transport = Mock()
        response = Mock(
            status_code=200,
            headers={"Content-Type": "IMAGE/JPEG"},
            content=b"snapshot",
        )
        transport.request.return_value = response

        assert MediaClient(transport).get_snapshot() == b"snapshot"

    def test_get_snapshot_accepts_content_type_parameters(self):
        """A JPEG Content-Type may include parameters."""
        transport = Mock()
        response = Mock(
            status_code=200,
            headers={"Content-Type": "image/jpeg; charset=binary"},
            content=b"snapshot",
        )
        transport.request.return_value = response

        assert MediaClient(transport).get_snapshot() == b"snapshot"

    @pytest.mark.parametrize("headers", [{"Content-Type": "image/png"}, {}])
    def test_get_snapshot_rejects_wrong_or_missing_content_type(self, headers):
        """A successful snapshot must identify itself as JPEG."""
        transport = Mock()
        transport.request.return_value = Mock(status_code=200, headers=headers)

        with pytest.raises(FeatureError) as error:
            MediaClient(transport).get_snapshot()

        assert error.value.code == "invalid_response"

    def test_get_snapshot_sends_exact_optional_query_parameters(self):
        """Snapshot tuning parameters map to the documented query names."""
        transport = Mock()
        transport.request.return_value = Mock(
            status_code=200,
            headers={"Content-Type": "image/jpeg"},
            content=b"snapshot",
        )

        MediaClient(transport).get_snapshot(
            resolution="1280x720",
            compression=75,
            camera_head=1,
        )

        _, request = transport.request.call_args
        assert request["params"] == {
            "resolution": "1280x720",
            "compression": 75,
            "camera": 1,
        }

    def test_get_snapshot_preserves_http_failure_behavior(self):
        """Non-200 snapshot responses retain the snapshot_failed error."""
        transport = Mock()
        transport.request.return_value = Mock(
            status_code=503,
            text="Service unavailable",
        )

        with pytest.raises(FeatureError) as error:
            MediaClient(transport).get_snapshot()

        assert error.value.code == "snapshot_failed"

    def test_get_snapshot_rejects_camera_head_before_request(self):
        """Camera heads are one-based without imposing a device-specific maximum."""
        transport = Mock()

        with pytest.raises(FeatureError) as error:
            MediaClient(transport).get_snapshot(camera_head=0)

        assert error.value.code == "invalid_parameter"
        transport.request.assert_not_called()

    @pytest.mark.integration
    def test_get_snapshot_without_optional_parameters(self, client):
        """Test snapshot capture without providing optional parameters."""
        response = client.media.get_snapshot()
        self._verify_snapshot_data(response)
        
    @pytest.mark.integration
    def test_get_snapshot_with_config(self, client):
        """Test snapshot capture with custom configuration."""
        response = client.media.get_snapshot(
            resolution="1280x720",
            compression=75,
            camera_head=1
        )
        self._verify_snapshot_data(response)
        
    @pytest.mark.unit
    def test_invalid_compression(self, client):
        """Test error handling for invalid compression value."""
        with pytest.raises(FeatureError) as e:
            client.media.get_snapshot(resolution="1920x1080", compression=101, camera_head=1)
        assert e.value.code == "invalid_parameter"
        assert "Compression" in e.value.message

    @pytest.mark.unit
    def test_invalid_compression_type(self, client):
        """Test error handling for invalid compression type."""
        with pytest.raises(FeatureError) as e:
            client.media.get_snapshot(compression="bad")
        assert e.value.code == "invalid_parameter"
        assert "Compression" in e.value.message
        
    def _verify_snapshot_data(self, data):
        """Helper to verify snapshot response data."""
        assert isinstance(data, bytes), "Snapshot data should be bytes"
        assert len(data) > 0, "Snapshot data should not be empty"
        
        # Basic JPEG header check (FF D8)
        assert data[:2] == b'\xFF\xD8', "Data should start with JPEG header"
        # Basic JPEG footer check (FF D9)
        assert data[-2:] == b'\xFF\xD9', "Data should end with JPEG footer" 