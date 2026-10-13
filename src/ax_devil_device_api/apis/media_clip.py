# GENERATED from specs/apis/audio-systems/media-clip-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Play, stop, upload, remove, rename and download audio media clips stored on the device.

Docs: https://developer.axis.com/vapix/audio-systems/media-clip-api/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._http.upload import UploadSource, UploadSpec
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import Binary, CgiArg, CgiBinding, Text, TextKv
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PlayClipRequest(Model):
    clip: int | None = Field(default=None, ge=0)
    """The media clip to play (the number of MediaClip.M#). Not needed when location is used."""
    audiooutput: int | None = Field(default=None, ge=1)
    """Deprecated as of AXIS OS 11.7; use audiodeviceid and audiooutputid. The audio output that plays the clip (index + 1 of Properties.Audio.Source.A[index].Output = yes). Cannot be combined with audiodeviceid."""
    repeat: int | None = Field(default=None, ge=-1)
    """Times to repeat the clip: -1 repeats forever, 0 (default) plays once. Only supported if Properties.AudioClip.PlayOptions includes repeat."""
    volume: int | None = Field(default=None, ge=0, le=1000)
    """Clip volume in percent on a linear scale; 0 mutes, 100 is the default. Only supported if PlayOptions includes volume."""
    location: str | None = None
    """Location of the clip; clip is then not needed. * is a wildcard that plays a random matching clip. Only supported if PlayOptions includes location."""
    audiodeviceid: int | None = Field(default=None, ge=0)
    """The audio device that plays the clip. An alternative to audiooutput; it must be paired with audiooutputid. Only supported if PlayOptions includes audiodeviceid."""
    audiooutputid: int | None = Field(default=None, ge=0)
    """The output on the audio device that plays the clip. Required when audiodeviceid is given."""


class RemoveClipRequest(Model):
    clip: int = Field(ge=0)
    """The media clip to remove."""


class SetClipNameRequest(Model):
    clip: int = Field(ge=0)
    """The media clip to rename."""
    name: str
    """The new name of the media clip."""


class DownloadClipRequest(Model):
    clip: int = Field(ge=0)
    """The media clip to download."""


class PlayClipAsViewerRequest(Model):
    clip: int | None = Field(default=None, ge=0)
    """The media clip to play (the number of MediaClip.M#). Not needed when location is used."""
    audiooutput: int | None = Field(default=None, ge=1)
    """Deprecated as of AXIS OS 11.7; use audiodeviceid and audiooutputid. The audio output that plays the clip (index + 1 of Properties.Audio.Source.A[index].Output = yes). Cannot be combined with audiodeviceid."""
    repeat: int | None = Field(default=None, ge=-1)
    """Times to repeat the clip: -1 repeats forever, 0 (default) plays once. Only supported if Properties.AudioClip.PlayOptions includes repeat."""
    volume: int | None = Field(default=None, ge=0, le=1000)
    """Clip volume in percent on a linear scale; 0 mutes, 100 is the default. Only supported if PlayOptions includes volume."""
    location: str | None = None
    """Location of the clip; clip is then not needed. * is a wildcard that plays a random matching clip. Only supported if PlayOptions includes location."""
    audiodeviceid: int | None = Field(default=None, ge=0)
    """The audio device that plays the clip. An alternative to audiooutput; it must be paired with audiooutputid. Only supported if PlayOptions includes audiodeviceid."""
    audiooutputid: int | None = Field(default=None, ge=0)
    """The output on the audio device that plays the clip. Required when audiodeviceid is given."""


class UploadClipRequest(Model):
    clip: UploadSource = Field(exclude=True, repr=False)
    """The audio file, as bytes, a Path or an Upload(stream, size)."""
    name: str | None = None
    """The name of the media clip."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/mediaclip.cgi"

INFO = ApiInfo(
    id="media-clip-api",
    name="Media clip API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.Audio.Audio", "yes"),),
    docs=("https://developer.axis.com/vapix/audio-systems/media-clip-api/",),
)


class OPS:
    play_clip = Operation(
        INFO,
        "play_clip",
        CgiBinding(
            PATH,
            fixed_query=(("action", "play"),),
            args=(
                CgiArg("clip"),
                CgiArg("audiooutput"),
                CgiArg("repeat"),
                CgiArg("volume"),
                CgiArg("location"),
                CgiArg("audiodeviceid"),
                CgiArg("audiooutputid"),
            ),
            reply=Text(),
        ),
        params=PlayClipRequest,
        result=str,
        access="operator",
        effect="action",
    )
    stop_clip = Operation(
        INFO,
        "stop_clip",
        CgiBinding(PATH, fixed_query=(("action", "stop"),), reply=Text()),
        result=str,
        access="operator",
        effect="action",
    )
    remove_clip = Operation(
        INFO,
        "remove_clip",
        CgiBinding(PATH, fixed_query=(("action", "remove"),), args=(CgiArg("clip"),), reply=Text()),
        params=RemoveClipRequest,
        result=str,
        access="operator",
        effect="write",
        write="delete",
    )
    set_clip_name = Operation(
        INFO,
        "set_clip_name",
        CgiBinding(PATH, fixed_query=(("action", "update"),), args=(CgiArg("clip"), CgiArg("name")), reply=Text()),
        params=SetClipNameRequest,
        result=str,
        access="operator",
        effect="write",
        write="patch",
    )
    download_clip = Operation(
        INFO,
        "download_clip",
        CgiBinding(PATH, fixed_query=(("action", "download"),), args=(CgiArg("clip"),), reply=Binary()),
        params=DownloadClipRequest,
        result=bytes,
        access="operator",
        effect="read",
    )
    play_clip_as_viewer = Operation(
        INFO,
        "play_clip_as_viewer",
        CgiBinding(
            "/axis-cgi/playclip.cgi",
            args=(
                CgiArg("clip"),
                CgiArg("audiooutput"),
                CgiArg("repeat"),
                CgiArg("volume"),
                CgiArg("location"),
                CgiArg("audiodeviceid"),
                CgiArg("audiooutputid"),
            ),
            reply=Text(),
        ),
        params=PlayClipAsViewerRequest,
        result=str,
        access="viewer",
        effect="action",
    )
    stop_clip_as_viewer = Operation(
        INFO,
        "stop_clip_as_viewer",
        CgiBinding("/axis-cgi/stopclip.cgi", reply=Text()),
        result=str,
        access="viewer",
        effect="action",
    )
    list_clips = Operation(
        INFO,
        "list_clips",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "list"), ("group", "MediaClip")),
            reply=TextKv(strip_prefix="root."),
        ),
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    upload_clip = Operation(
        INFO,
        "upload_clip",
        CgiBinding(
            PATH,
            method="POST",
            encoding="multipart",
            url_query=(("action", "upload"), ("media", "audio")),
            args=(CgiArg("name", place="query"),),
            uploads=(UploadSpec("clip", part="file", content_type="audio/basic"),),
            reply=Text(),
        ),
        params=UploadClipRequest,
        result=str,
        access="operator",
        effect="write",
        write="create",
    )


# ---------------------------------------------------------------------------
# API classes


class MediaClipApi(SyncApi):
    """Media clip API (``media-clip-api``)."""

    INFO = INFO

    @overload
    def play_clip(self, request: PlayClipRequest, /, *, request_options: RequestOptions | None = None) -> str: ...
    @overload
    def play_clip(
        self,
        clip: int | MISSING = MISSING,
        /,
        *,
        audiooutput: int | MISSING = MISSING,
        repeat: int | MISSING = MISSING,
        volume: int | MISSING = MISSING,
        location: str | MISSING = MISSING,
        audiodeviceid: int | MISSING = MISSING,
        audiooutputid: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    def play_clip(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> str:
        """Play a clip (operator and above).

        The result is the device reply, for example OK followed by playing=0.

        Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, PlayClipRequest):
            kwargs = {**dict(zip(("clip",), (request, *args), strict=False)), **kwargs}
            request = None
        return self._run(OPS.play_clip, request, kwargs, request_options)

    def stop_clip(self, *, request_options: RequestOptions | None = None) -> str:
        """Stop any currently playing clip (operator and above). Access: operator."""
        return self._run(OPS.stop_clip, None, {}, request_options)

    def remove_clip(self, clip: int, *, request_options: RequestOptions | None = None) -> str:
        """Remove a clip. Access: operator."""
        return self._run(OPS.remove_clip, None, {"clip": clip}, request_options)

    def set_clip_name(self, clip: int, name: str, *, request_options: RequestOptions | None = None) -> str:
        """Change the name of a clip. Changes only the fields given. Access: operator."""
        return self._run(OPS.set_clip_name, None, {"clip": clip, "name": name}, request_options)

    def download_clip(self, clip: int, *, request_options: RequestOptions | None = None) -> bytes:
        """Download a clip (for backup or editing).

        The device sends the stored audio file; the docs name audio/basic (au format).

        Access: operator.
        """
        return self._run(OPS.download_clip, None, {"clip": clip}, request_options)

    @overload
    def play_clip_as_viewer(
        self, request: PlayClipAsViewerRequest, /, *, request_options: RequestOptions | None = None
    ) -> str: ...
    @overload
    def play_clip_as_viewer(
        self,
        clip: int | MISSING = MISSING,
        /,
        *,
        audiooutput: int | MISSING = MISSING,
        repeat: int | MISSING = MISSING,
        volume: int | MISSING = MISSING,
        location: str | MISSING = MISSING,
        audiodeviceid: int | MISSING = MISSING,
        audiooutputid: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    def play_clip_as_viewer(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> str:
        """Play a clip (viewer and above), through playclip.cgi. Access: viewer."""
        if request is MISSING:
            request = None
        elif args or not isinstance(request, PlayClipAsViewerRequest):
            kwargs = {**dict(zip(("clip",), (request, *args), strict=False)), **kwargs}
            request = None
        return self._run(OPS.play_clip_as_viewer, request, kwargs, request_options)

    def stop_clip_as_viewer(self, *, request_options: RequestOptions | None = None) -> str:
        """Stop any currently playing clip (viewer and above), through stopclip.cgi.

        Supported if Properties.AudioClip.StopClip is yes.

        Access: viewer.
        """
        return self._run(OPS.stop_clip_as_viewer, None, {}, request_options)

    def list_clips(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List the media clips as ``{"MediaClip.M0.Name": "value"}`` (``root.`` removed).

        Goes through the parameter management CGI. Each clip has Name, Location and Type; MaxGroups and
        MaxUploadSize are also in the MediaClip group.

        Access: viewer.
        """
        return self._run(OPS.list_clips, None, {}, request_options)

    def upload_clip(
        self, clip: UploadSource, *, name: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Upload an audio file as a new media clip.

        POST with the audio file as multipart/form-data (RFC 1867). media=audio is required for the upload.

        Access: operator.
        """
        return self._run(OPS.upload_clip, None, {"clip": clip, "name": name}, request_options)


class AsyncMediaClipApi(AsyncApi):
    """Media clip API (``media-clip-api``)."""

    INFO = INFO

    @overload
    async def play_clip(self, request: PlayClipRequest, /, *, request_options: RequestOptions | None = None) -> str: ...
    @overload
    async def play_clip(
        self,
        clip: int | MISSING = MISSING,
        /,
        *,
        audiooutput: int | MISSING = MISSING,
        repeat: int | MISSING = MISSING,
        volume: int | MISSING = MISSING,
        location: str | MISSING = MISSING,
        audiodeviceid: int | MISSING = MISSING,
        audiooutputid: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    async def play_clip(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> str:
        """Play a clip (operator and above).

        The result is the device reply, for example OK followed by playing=0.

        Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, PlayClipRequest):
            kwargs = {**dict(zip(("clip",), (request, *args), strict=False)), **kwargs}
            request = None
        return await self._run(OPS.play_clip, request, kwargs, request_options)

    async def stop_clip(self, *, request_options: RequestOptions | None = None) -> str:
        """Stop any currently playing clip (operator and above). Access: operator."""
        return await self._run(OPS.stop_clip, None, {}, request_options)

    async def remove_clip(self, clip: int, *, request_options: RequestOptions | None = None) -> str:
        """Remove a clip. Access: operator."""
        return await self._run(OPS.remove_clip, None, {"clip": clip}, request_options)

    async def set_clip_name(self, clip: int, name: str, *, request_options: RequestOptions | None = None) -> str:
        """Change the name of a clip. Changes only the fields given. Access: operator."""
        return await self._run(OPS.set_clip_name, None, {"clip": clip, "name": name}, request_options)

    async def download_clip(self, clip: int, *, request_options: RequestOptions | None = None) -> bytes:
        """Download a clip (for backup or editing).

        The device sends the stored audio file; the docs name audio/basic (au format).

        Access: operator.
        """
        return await self._run(OPS.download_clip, None, {"clip": clip}, request_options)

    @overload
    async def play_clip_as_viewer(
        self, request: PlayClipAsViewerRequest, /, *, request_options: RequestOptions | None = None
    ) -> str: ...
    @overload
    async def play_clip_as_viewer(
        self,
        clip: int | MISSING = MISSING,
        /,
        *,
        audiooutput: int | MISSING = MISSING,
        repeat: int | MISSING = MISSING,
        volume: int | MISSING = MISSING,
        location: str | MISSING = MISSING,
        audiodeviceid: int | MISSING = MISSING,
        audiooutputid: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    async def play_clip_as_viewer(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> str:
        """Play a clip (viewer and above), through playclip.cgi. Access: viewer."""
        if request is MISSING:
            request = None
        elif args or not isinstance(request, PlayClipAsViewerRequest):
            kwargs = {**dict(zip(("clip",), (request, *args), strict=False)), **kwargs}
            request = None
        return await self._run(OPS.play_clip_as_viewer, request, kwargs, request_options)

    async def stop_clip_as_viewer(self, *, request_options: RequestOptions | None = None) -> str:
        """Stop any currently playing clip (viewer and above), through stopclip.cgi.

        Supported if Properties.AudioClip.StopClip is yes.

        Access: viewer.
        """
        return await self._run(OPS.stop_clip_as_viewer, None, {}, request_options)

    async def list_clips(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List the media clips as ``{"MediaClip.M0.Name": "value"}`` (``root.`` removed).

        Goes through the parameter management CGI. Each clip has Name, Location and Type; MaxGroups and
        MaxUploadSize are also in the MediaClip group.

        Access: viewer.
        """
        return await self._run(OPS.list_clips, None, {}, request_options)

    async def upload_clip(
        self, clip: UploadSource, *, name: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Upload an audio file as a new media clip.

        POST with the audio file as multipart/form-data (RFC 1867). media=audio is required for the upload.

        Access: operator.
        """
        return await self._run(OPS.upload_clip, None, {"clip": clip, "name": name}, request_options)
