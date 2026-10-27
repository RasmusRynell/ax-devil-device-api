# GENERATED from specs/apis/device-configuration/speaker-display-notification-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The VAPIX® Speaker display notification API provides an interface to trigger new notifications on the display, or stop an ongoing notification.

Docs: https://developer.axis.com/vapix/device-configuration/speaker-display-notification/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ColorFormat = Annotated[str, Field(pattern="^#[0-9a-fA-F]{6}$")]
DurationInt = Annotated[int, Field(ge=1, le=2147483647)]


class NotificationResponse(Model):
    """Response received from a simple notification request."""

    duration: int
    """Estimated duration of the notification in milliseconds. 0 means the notification lasts until interrupted."""


ScrollDirectionEnum = Literal["fromRightToLeft", "fromBottomToTop", "fromLeftToRight"]
ScrollSpeedInt = Annotated[int, Field(ge=0, le=10)]
SimpleDurationType = Literal["repetitions", "time", "timeCompleteMessage"]


class SimpleDurationObject(Model):
    """Duration object for simple notification."""

    type: SimpleDurationType | None = None
    """Duration type can be repetitions, time or timeCompleteMessage."""
    value: DurationInt | None = None
    """If type is repetitions, the message will be displayed for a number of repetitions; otherwise, it will be displayed for a duration in milliseconds."""


SimpleMessageStr = Annotated[str, Field(max_length=1000)]
TextSizeEnum = Literal["small", "medium", "large"]


class SimpleNotificationRequest(Model):
    """Available fields to send a simple notification request."""

    background_color: ColorFormat | None = Field(
        default=None, validation_alias="backgroundColor", serialization_alias="backgroundColor"
    )
    """Background color. Format is RGB in hex 6 digits '#RRGGBB'."""
    duration: SimpleDurationObject | None = None
    """Duration. Default is infinite repetitions."""
    message: SimpleMessageStr | None = None
    """The display message. Max length is 1000 characters."""
    scroll_direction: ScrollDirectionEnum | None = Field(
        default=None, validation_alias="scrollDirection", serialization_alias="scrollDirection"
    )
    """The scrolling direction. Can be either from right to left or bottom to top."""
    scroll_speed: ScrollSpeedInt | None = Field(
        default=None, validation_alias="scrollSpeed", serialization_alias="scrollSpeed"
    )
    """Message scroll speed. 1 is slow and 10 is fast. 0 means no scrolling."""
    text_color: ColorFormat | None = Field(default=None, validation_alias="textColor", serialization_alias="textColor")
    """The color of the message letters. Format is RGB in hex 6 digits '#RRGGBB'."""
    text_size: TextSizeEnum | None = Field(default=None, validation_alias="textSize", serialization_alias="textSize")
    """The text size. Can be either small, medium or large."""


class SpeakerDisplayNotification(Model):
    """The whole API tree. The root entity has no properties."""


class StopNotificationRequest(Model):
    pass


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/speaker-display-notification/v1"

INFO = ApiInfo(
    id="speaker-display-notification-config",
    name="Speaker display notification",
    family=Family.DCA,
    discovery=(DcaDiscovery("speaker-display-notification", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/speaker-display-notification/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=SpeakerDisplayNotification, access="admin", effect="read"
    )
    simple = Operation(
        INFO,
        "simple",
        DcaBinding("POST", f"{ROOT}/simple", body="object"),
        params=SimpleNotificationRequest,
        result=NotificationResponse,
        access="admin",
        effect="action",
    )
    stop = Operation(
        INFO,
        "stop",
        DcaBinding("POST", f"{ROOT}/stop", body="object"),
        params=StopNotificationRequest,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class SpeakerDisplayNotificationApi(SyncApi):
    """Speaker display notification (``speaker-display-notification-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> SpeakerDisplayNotification:
        """All data of the Speaker display notification API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    @overload
    def simple(
        self, request: SimpleNotificationRequest, /, *, request_options: RequestOptions | None = None
    ) -> NotificationResponse: ...
    @overload
    def simple(
        self,
        /,
        *,
        background_color: ColorFormat | MISSING = MISSING,
        duration: SimpleDurationObject | MISSING = MISSING,
        message: SimpleMessageStr | MISSING = MISSING,
        scroll_direction: ScrollDirectionEnum | MISSING = MISSING,
        scroll_speed: ScrollSpeedInt | MISSING = MISSING,
        text_color: ColorFormat | MISSING = MISSING,
        text_size: TextSizeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> NotificationResponse: ...
    def simple(
        self,
        request: SimpleNotificationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> NotificationResponse:
        """A simple notification which can either be static or scrolling. Access: admin."""
        return self._run(OPS.simple, request, kwargs, request_options)

    def stop(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop the ongoing notification. Access: admin."""
        self._run(OPS.stop, None, {}, request_options)


class AsyncSpeakerDisplayNotificationApi(AsyncApi):
    """Speaker display notification (``speaker-display-notification-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> SpeakerDisplayNotification:
        """All data of the Speaker display notification API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    @overload
    async def simple(
        self, request: SimpleNotificationRequest, /, *, request_options: RequestOptions | None = None
    ) -> NotificationResponse: ...
    @overload
    async def simple(
        self,
        /,
        *,
        background_color: ColorFormat | MISSING = MISSING,
        duration: SimpleDurationObject | MISSING = MISSING,
        message: SimpleMessageStr | MISSING = MISSING,
        scroll_direction: ScrollDirectionEnum | MISSING = MISSING,
        scroll_speed: ScrollSpeedInt | MISSING = MISSING,
        text_color: ColorFormat | MISSING = MISSING,
        text_size: TextSizeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> NotificationResponse: ...
    async def simple(
        self,
        request: SimpleNotificationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> NotificationResponse:
        """A simple notification which can either be static or scrolling. Access: admin."""
        return await self._run(OPS.simple, request, kwargs, request_options)

    async def stop(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop the ongoing notification. Access: admin."""
        await self._run(OPS.stop, None, {}, request_options)
