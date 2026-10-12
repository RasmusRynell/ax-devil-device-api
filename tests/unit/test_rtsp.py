"""RTSP URL builders."""

from __future__ import annotations

import pytest

from ax_devil_device_api import BearerToken, Device, errors
from ax_devil_device_api.rtsp import MEDIA_PATH, MediaStream, build_rtsp_url


def test_media_stream_url_keeps_field_order_and_flags() -> None:
    stream = MediaStream(videocodec="h264", resolution="1280x720", fps=15, audio=False, camera=2)
    url = stream.url("10.0.0.1")
    assert str(url) == "rtsp://10.0.0.1:554/axis-media/media.amp?videocodec=h264&camera=2&resolution=1280x720&fps=15&audio=0"
    assert url.safe == str(url)


def test_credentials_are_encoded_and_never_in_repr() -> None:
    url = MediaStream(streamprofile="my profile").url("cam.local", port=8554, credentials=("ro@ot", "p:w/d"))
    assert str(url) == "rtsp://ro%40ot:p%3Aw%2Fd@cam.local:8554/axis-media/media.amp?streamprofile=my%20profile"
    assert "p:w" not in repr(url) and "ro@ot" not in repr(url) and "p%3Aw" not in url.safe
    assert url.safe.startswith("rtsp://cam.local:8554/")


def test_event_metadata_and_filters() -> None:
    stream = MediaStream(video=False, event=True, eventtopic="onvif:Device/axis:IO/Port,axis:Status", eventcontent='boolean(//SimpleItem[@Name="a"])', ptz="all")
    text = str(stream.url("h"))
    assert "event=1" in text and "eventtopic=onvif:Device/axis:IO/Port,axis:Status" in text
    assert "eventcontent=boolean%28//SimpleItem%5B%40Name%3D%22a%22%5D%29" in text and "ptz=all" in text


def test_ipv6_and_custom_path_and_extra() -> None:
    url = build_rtsp_url("fe80::1", path="/axis-media/ssm/media.amp", params=[("audio", True), ("x", 3)])
    assert str(url) == "rtsp://[fe80::1]:554/axis-media/ssm/media.amp?audio=1&x=3"
    assert str(MediaStream(extra=(("custom", "1"),)).url("h")).endswith("media.amp?custom=1")
    assert str(MediaStream().url("h")) == "rtsp://h:554" + MEDIA_PATH


def test_validation() -> None:
    for bad in (
        lambda: MediaStream(resolution="big"),
        lambda: MediaStream(fps=-1),
        lambda: MediaStream(compression=101),
        lambda: MediaStream(camera=0),
        lambda: MediaStream(streamprofile="a", recordingid="b"),
        lambda: build_rtsp_url("a/b"),
        lambda: build_rtsp_url("h", port=0),
        lambda: build_rtsp_url("h", path="x"),
        lambda: build_rtsp_url("h", credentials=BearerToken("t")),  # type: ignore[arg-type]
    ):
        with pytest.raises(errors.ConfigurationError):
            bad()


def test_device_rtsp_url() -> None:
    with Device("10.0.0.5", credentials=("root", "pw")) as dev:
        stream = MediaStream(videocodec="h265")
        assert dev.rtsp_url(stream) .safe == "rtsp://10.0.0.5:554/axis-media/media.amp?videocodec=h265"
        assert str(dev.rtsp_url(stream, include_credentials=True)) == "rtsp://root:pw@10.0.0.5:554/axis-media/media.amp?videocodec=h265"
        assert str(dev.rtsp_url()) == "rtsp://10.0.0.5:554/axis-media/media.amp"
    with Device("10.0.0.5", credentials=BearerToken("t")) as dev:
        assert dev.rtsp_url().safe.startswith("rtsp://10.0.0.5")
        with pytest.raises(errors.ConfigurationError):
            dev.rtsp_url(include_credentials=True)
