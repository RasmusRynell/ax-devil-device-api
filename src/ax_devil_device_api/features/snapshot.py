"""JPEG snapshot, built on the generated ``video_streaming`` API (``get_jpeg``)."""

from __future__ import annotations

from typing import Any, Literal

from ..apis.video_streaming import JpegRequest
from ..device import AsyncDevice, Device


def _request(
    resolution: str | None,
    camera: str | None,
    compression: int | None,
    color: int | None,
    rotation: Literal[0, 90, 180, 270] | None,
    mirror: int | None,
    palette: str | None,
    squarepixel: int | None,
    overlays: Any,
    text: int | None,
    textstring: str | None,
) -> JpegRequest:
    """Unset (``None``) options are left to the device's configured defaults."""
    given = dict(
        resolution=resolution, camera=camera, compression=compression, color=color, rotation=rotation,
        mirror=mirror, palette=palette, squarepixel=squarepixel, overlays=overlays, text=text, textstring=textstring,
    )
    return JpegRequest.model_validate({k: v for k, v in given.items() if v is not None})


def snapshot(
    dev: Device,
    *,
    resolution: str | None = None,
    camera: str | None = None,
    compression: int | None = None,
    color: int | None = None,
    rotation: Literal[0, 90, 180, 270] | None = None,
    mirror: int | None = None,
    palette: str | None = None,
    squarepixel: int | None = None,
    overlays: Any = None,
    text: int | None = None,
    textstring: str | None = None,
) -> bytes:
    """Fetch one JPEG image. Options are those of ``JpegRequest``; unset ones use the device defaults."""
    request = _request(resolution, camera, compression, color, rotation, mirror, palette, squarepixel, overlays, text, textstring)
    return dev.apis.video_streaming.get_jpeg(request)


async def async_snapshot(
    dev: AsyncDevice,
    *,
    resolution: str | None = None,
    camera: str | None = None,
    compression: int | None = None,
    color: int | None = None,
    rotation: Literal[0, 90, 180, 270] | None = None,
    mirror: int | None = None,
    palette: str | None = None,
    squarepixel: int | None = None,
    overlays: Any = None,
    text: int | None = None,
    textstring: str | None = None,
) -> bytes:
    request = _request(resolution, camera, compression, color, rotation, mirror, palette, squarepixel, overlays, text, textstring)
    return await dev.apis.video_streaming.get_jpeg(request)
