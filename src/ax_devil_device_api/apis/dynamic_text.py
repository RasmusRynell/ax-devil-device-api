# GENERATED from specs/apis/network-video/dynamic-text.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Set and get the dynamic text slots that text overlays show through the D1 to D16 modifiers.

Docs: https://developer.axis.com/vapix/network-video/overlay-api/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, Text
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SetTextRequest(Model):
    text: str
    """The overlay text to apply."""
    text_index: int | None = Field(default=None, ge=1, le=16)
    """Select a dynamic text slot. A text index for a slot maps text to the modifiers `#D1...#D16`. For example, `text_index=3&text=Hello` means that `Hello` will be mapped to `#D3`."""
    camera: list[str] | None = None
    """Video channels to select. The device uses channel 1 when omitted. Only valid on products with more than one video channel."""


class GetTextRequest(Model):
    text_index: int | None = Field(default=None, ge=1, le=16)
    """Select a dynamic text slot. A text index for a slot maps text to the modifiers `#D1...#D16`. For example, `text_index=3&text=Hello` means that `Hello` will be mapped to `#D3`."""
    camera: list[str] | None = None
    """Video channels to select. The device uses channel 1 when omitted. Only valid on products with more than one video channel."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/dynamicoverlay.cgi"

INFO = ApiInfo(
    id="dynamic-text",
    name="Dynamic text",
    family=Family.CGI,
    docs=("https://developer.axis.com/vapix/network-video/overlay-api/",),
)


class OPS:
    set_text = Operation(
        INFO,
        "set_text",
        CgiBinding(
            PATH,
            fixed_query=(("action", "settext"),),
            args=(CgiArg("text"), CgiArg("text_index"), CgiArg("camera", style="csv")),
            reply=Text(),
        ),
        params=SetTextRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_text = Operation(
        INFO,
        "get_text",
        CgiBinding(
            PATH,
            fixed_query=(("action", "gettext"),),
            args=(CgiArg("text_index"), CgiArg("camera", style="csv")),
            reply=Text(),
        ),
        params=GetTextRequest,
        result=str,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class DynamicTextApi(SyncApi):
    """Dynamic text (``dynamic-text``)."""

    INFO = INFO

    def set_text(
        self,
        text: str,
        *,
        text_index: int | MISSING = MISSING,
        camera: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the dynamic text. Changes only the fields given. Access: operator."""
        self._run(OPS.set_text, None, {"text": text, "text_index": text_index, "camera": camera}, request_options)

    def get_text(
        self,
        text_index: int | MISSING = MISSING,
        *,
        camera: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get the dynamic text. Access: operator."""
        return self._run(OPS.get_text, None, {"text_index": text_index, "camera": camera}, request_options)


class AsyncDynamicTextApi(AsyncApi):
    """Dynamic text (``dynamic-text``)."""

    INFO = INFO

    async def set_text(
        self,
        text: str,
        *,
        text_index: int | MISSING = MISSING,
        camera: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the dynamic text. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_text, None, {"text": text, "text_index": text_index, "camera": camera}, request_options)

    async def get_text(
        self,
        text_index: int | MISSING = MISSING,
        *,
        camera: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get the dynamic text. Access: operator."""
        return await self._run(OPS.get_text, None, {"text_index": text_index, "camera": camera}, request_options)
