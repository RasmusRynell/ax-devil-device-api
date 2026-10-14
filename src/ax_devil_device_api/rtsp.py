"""RTSP URL builders (pure functions; this library has no RTSP client).

::

    stream = MediaStream(videocodec="h264", resolution="1280x720", fps=15, audio=False)
    url = stream.url("10.0.0.1", credentials=("viewer", "pass"))
    str(url)   # rtsp://viewer:pass@10.0.0.1:554/axis-media/media.amp?videocodec=h264&resolution=1280x720&fps=15&audio=0

Hand the string to a media library. ``repr(url)`` never shows the password.
``Device.rtsp_url`` builds the same URL from a connected device.

Generated APIs expose RTSP endpoints as operations with an ``RtspBinding``
(spec: ``binding: {rtsp: {...}}``). They return an ``RtspUrl`` without any
network call, built by ``Device.rtsp_url_for``.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, fields
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import quote

from ._http.config import BearerToken, Credentials, check_host
from ._http.types import unsafe_path
from ._protocols.base import CallFlow, Model, Operation, register_binding
from ._validate import boolean, bounded_int, non_negative_int
from .errors import ConfigurationError

if TYPE_CHECKING:
    from ._protocols.state import DeviceState

__all__ = ["MEDIA_PATH", "MediaStream", "RtspBinding", "RtspUrl", "build_rtsp_url"]

MEDIA_PATH = "/axis-media/media.amp"
"""The RTSP media endpoint. ``/axis-media/ssm/media.amp`` serves always-multicast streams."""

DEFAULT_PORT = 554

_SAFE_VALUE = ",:/-_.~"
_RESOLUTION = re.compile(r"[0-9]+x[0-9]+")


def _flag(value: bool) -> str:
    return "1" if value else "0"


@dataclass(frozen=True)
class RtspUrl:
    """An ``rtsp://`` URL with optional credentials in the user-info part."""

    host: str
    port: int = DEFAULT_PORT
    path: str = MEDIA_PATH
    query: tuple[tuple[str, str], ...] = ()
    username: str | None = None
    password: str | None = None

    def __post_init__(self) -> None:
        check_host(self.host)
        bounded_int("port", self.port, 1, 65535)
        if not self.path.startswith("/") or "?" in self.path:
            raise ConfigurationError(f"RTSP path must be absolute and without a query: {self.path!r}")
        if unsafe_path(self.path):
            raise ConfigurationError(f"RTSP path must not contain '.' or '..' segments or backslashes (also percent-encoded): {self.path!r}")
        if self.password is not None and self.username is None:
            raise ConfigurationError("a password needs a username")

    def _build(self, *, with_credentials: bool) -> str:
        host = f"[{self.host}]" if ":" in self.host and not self.host.startswith("[") else self.host
        userinfo = ""
        if with_credentials and self.username is not None:
            userinfo = quote(self.username, safe="")
            if self.password is not None:
                userinfo += ":" + quote(self.password, safe="")
            userinfo += "@"
        url = f"rtsp://{userinfo}{host}:{self.port}{quote(self.path, safe='/=')}"
        if self.query:
            url += "?" + "&".join(f"{quote(k, safe='')}={quote(v, safe=_SAFE_VALUE)}" for k, v in self.query)
        return url

    @property
    def url(self) -> str:
        """The URL including credentials, if any."""
        return self._build(with_credentials=True)

    @property
    def safe(self) -> str:
        """The URL without credentials; safe to log."""
        return self._build(with_credentials=False)

    def with_credentials(self, username: str, password: str | None = None) -> RtspUrl:
        return RtspUrl(self.host, self.port, self.path, self.query, username, password)

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"RtspUrl({self.safe!r}{', credentials=<redacted>' if self.username is not None else ''})"


def build_rtsp_url(
    host: str,
    *,
    port: int = DEFAULT_PORT,
    path: str = MEDIA_PATH,
    params: Mapping[str, str | int | bool] | Iterable[tuple[str, str | int | bool]] = (),
    credentials: Credentials | tuple[str, str] | None = None,
) -> RtspUrl:
    """Build an RTSP URL from raw parameters. Booleans become ``1``/``0``; order is kept."""
    pairs = params.items() if isinstance(params, Mapping) else params
    query = tuple((str(k), _flag(v) if isinstance(v, bool) else str(v)) for k, v in pairs)
    if isinstance(credentials, BearerToken):
        raise ConfigurationError("RTSP URLs take a username and password, not a bearer token")
    if isinstance(credentials, tuple):
        credentials = Credentials(*credentials)
    user, password = (credentials.username, credentials.password) if credentials else (None, None)
    return RtspUrl(host, port, path, query, user, password)


_MEDIA_FLAGS = ("audio", "video", "mirror", "color", "squarepixel", "event", "pull")
_MEDIA_TEXT = ("videocodec", "streamprofile", "recordingid", "palette", "eventtopic", "eventcontent")
_MEDIA_CHOICES: dict[str, tuple[int | str, ...]] = {
    "rotation": (0, 90, 180, 270),
    "overlays": ("all", "text", "image", "application", "off", "all-sync", "application-sync"),
    "ptz": ("none", "all", "status", "position"),
    "analytics": ("off", "box", "polygon"),
    "ptz_pantilt_coordinate_space": ("generic", "degrees", "digital"),
    "ptz_zoom_coordinate_space": ("generic", "digital"),
}


@dataclass(frozen=True)
class MediaStream:
    """Parameters of ``/axis-media/media.amp``. Only the ones you set go into the URL, in field order.

    Defaults are the device's (see the VAPIX video streaming documentation);
    nothing is filled in here. ``extra`` adds parameters this class does not
    name (product- or firmware-specific).
    """

    videocodec: str | None = None
    """For example ``h264``, ``h265``, ``av1``, ``jpeg``."""
    streamprofile: str | None = None
    recordingid: str | None = None
    camera: int | Literal["quad"] | None = None
    resolution: str | None = None
    """``WIDTHxHEIGHT``."""
    fps: int | None = None
    compression: int | None = None
    """0..100, higher is smaller."""
    audio: bool | None = None
    video: bool | None = None
    rotation: Literal[0, 90, 180, 270] | None = None
    mirror: bool | None = None
    color: bool | None = None
    squarepixel: bool | None = None
    palette: str | None = None
    overlays: Literal["all", "text", "image", "application", "off", "all-sync", "application-sync"] | None = None
    event: bool | None = None
    """Include event metadata in the stream."""
    eventtopic: str | None = None
    eventcontent: str | None = None
    ptz: Literal["none", "all", "status", "position"] | None = None
    analytics: Literal["off", "box", "polygon"] | None = None
    ptz_pantilt_coordinate_space: Literal["generic", "degrees", "digital"] | None = None
    ptz_zoom_coordinate_space: Literal["generic", "digital"] | None = None
    pull: bool | None = None
    """Download a recording as fast as possible (RTSP over HTTP only)."""
    extra: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.resolution is not None and not (isinstance(self.resolution, str) and _RESOLUTION.fullmatch(self.resolution)):
            raise ConfigurationError(f"resolution must look like 1280x720: {self.resolution!r}")
        for flag in _MEDIA_FLAGS:
            if getattr(self, flag) is not None:
                boolean(flag, getattr(self, flag))
        for name in _MEDIA_TEXT:
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value):
                raise ConfigurationError(f"{name} must be a non-empty string, got {value!r}")
        for name, choices in _MEDIA_CHOICES.items():
            value = getattr(self, name)
            # ``type(...) is`` keeps True/1.0 from passing for 1/90 (and ``in`` would accept both).
            if value is not None and not any(type(value) is type(choice) and value == choice for choice in choices):
                raise ConfigurationError(f"{name} must be one of {', '.join(map(repr, choices))}, got {value!r}")
        if not isinstance(self.extra, tuple) or not all(
            isinstance(pair, tuple) and len(pair) == 2 and all(isinstance(part, str) for part in pair) for pair in self.extra
        ):
            raise ConfigurationError("extra must be a tuple of (name, value) string pairs")
        if self.fps is not None:
            non_negative_int("fps", self.fps)
        if self.compression is not None:
            bounded_int("compression", self.compression, 0, 100)
        if self.camera is not None and self.camera != "quad":
            bounded_int("camera", self.camera, 1)
        if self.streamprofile is not None and self.recordingid is not None:
            raise ConfigurationError("streamprofile and recordingid are mutually exclusive")

    def query(self) -> tuple[tuple[str, str], ...]:
        pairs: list[tuple[str, str]] = []
        for f in fields(self):
            value = getattr(self, f.name)
            if f.name == "extra" or value is None:
                continue
            pairs.append((f.name, _flag(value) if isinstance(value, bool) else str(value)))
        return tuple(pairs) + tuple(self.extra)

    def url(
        self,
        host: str,
        *,
        port: int = DEFAULT_PORT,
        path: str = MEDIA_PATH,
        credentials: Credentials | tuple[str, str] | None = None,
    ) -> RtspUrl:
        return build_rtsp_url(host, port=port, path=path, params=self.query(), credentials=credentials)


# ---------------------------------------------------------------------------
# Generated operations


@dataclass(frozen=True)
class RtspBinding:
    """An operation that builds an RTSP URL instead of calling the device.

    The params model's set fields become query arguments in field order, after
    ``fixed_query``: booleans as ``1``/``0``, lists joined with commas, wire
    names as the model's aliases.
    """

    path: str = MEDIA_PATH
    port: int = DEFAULT_PORT
    fixed_query: tuple[tuple[str, str], ...] = ()


def rtsp_query(binding: RtspBinding, params: Model | None) -> tuple[tuple[str, str | int | bool], ...]:
    """Query arguments of the URL for ``params`` (set fields only)."""
    pairs: list[tuple[str, str | int | bool]] = list(binding.fixed_query)
    for key, value in (params.to_wire() if params is not None else {}).items():
        if value is None:
            continue
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, (list, tuple)):
            value = ",".join(_flag(v) if isinstance(v, bool) else str(v) for v in value)
        elif isinstance(value, (dict, Mapping)):
            raise TypeError(f"RTSP argument {key!r} must be a scalar or a list")
        pairs.append((key, value))
    return tuple(pairs)


def _no_flow(op: Operation[RtspBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    raise ConfigurationError(
        f"{op.api.id}.{op.id} builds an RTSP URL and makes no request; call the API method or Device.rtsp_url_for()"
    )
    yield  # pragma: no cover - makes this a generator


register_binding(RtspBinding, _no_flow)
