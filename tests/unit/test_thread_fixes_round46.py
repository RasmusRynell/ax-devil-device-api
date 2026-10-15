"""A text reply with no key=value line is the device explaining a failure (ApiError); shape failures carry a redacted excerpt."""

from __future__ import annotations

import pytest

from ax_devil_device_api.errors import ApiError, ResponseFormatError
from ax_devil_device_api.testing import MockCamera

PATH = "/axis-cgi/imagesize.cgi"
PROSE = "No camera specified (ex. camera=1)"


def _camera(text: str) -> MockCamera:
    camera = MockCamera()
    camera.cgi(PATH, text=text)
    return camera


def test_no_camera_prose_is_an_api_error_carrying_the_device_text() -> None:
    with _camera(PROSE).device() as dev:
        with pytest.raises(ApiError) as caught:
            dev.apis.video_streaming.get_image_size()
    assert PROSE in caught.value.message and PROSE in str(caught.value.details)


@pytest.mark.anyio
async def test_the_same_prose_through_the_async_path() -> None:
    async with _camera(PROSE).async_device() as dev:
        with pytest.raises(ApiError) as caught:
            await dev.apis.video_streaming.get_image_size()
    assert PROSE in caught.value.message


def test_the_html_comment_form_is_unchanged() -> None:
    with _camera("<!-- Camera 1 not available. -->").device() as dev:
        with pytest.raises(ApiError) as caught:
            dev.apis.video_streaming.get_image_size(camera="1")
    assert "Camera 1 not available." in caught.value.message


@pytest.mark.parametrize("text", ["just some words", "=", "no pairs here\nnor here", "(x=1)"])
def test_any_reply_without_a_key_value_line_is_an_api_error(text: str) -> None:
    with _camera(text).device() as dev, pytest.raises(ApiError):
        dev.apis.video_streaming.get_image_size()


def test_keys_with_spaces_are_still_pairs() -> None:
    with _camera("image width = 720\nimage height=480\n").device() as dev:
        size = dev.apis.video_streaming.get_image_size()
    assert (size.width, size.height) == (720, 480)


def test_a_malformed_key_value_reply_is_a_response_format_error_with_a_redacted_excerpt() -> None:
    with _camera("image width=wide\nimage height=480\npassword=hunter2\n").device() as dev:
        with pytest.raises(ResponseFormatError) as caught:
            dev.apis.video_streaming.get_image_size()
    message = str(caught.value)
    assert "image width" in message and "wide" in message  # the excerpt of what the device sent
    assert "hunter2" not in message  # and nothing secret in it
    assert len(message) < 900
