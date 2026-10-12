# GENERATED from specs/apis/network-video/analytics-metadata-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List RTSP analytics metadata producers, enable/disable them per video channel and fetch sample metadata frames.

Docs: https://developer.axis.com/vapix/network-video/analytics-metadata-producer-configuration/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class VideoChannel(Model):
    channel: int
    """The video channel number. The docs call it the name of the video channel."""
    enabled: bool
    """The status of the video channel."""


class Producer(Model):
    name: str
    """The producer name."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """Optional. The display friendly name."""
    videochannels: list[VideoChannel]


class ListProducersRequest(Model):
    producers: list[str] | None = None
    """Container for the producers (producer names)."""


class ProducerList(Model):
    producers: list[Producer]


class ProducerChannels(Model):
    name: str
    videochannels: list[VideoChannel]


class SetEnabledProducersRequest(Model):
    producers: list[ProducerChannels]
    """Array of producers with the video channels to enable/disable."""


class GetSupportedMetadataRequest(Model):
    producers: list[str] | None = None
    """Producer names."""


class ProducerSampleFrame(Model):
    name: str
    sample_frame_xml: str | None = Field(
        default=None, validation_alias="sampleFrameXML", serialization_alias="sampleFrameXML"
    )
    """The sample frame associated with the producer (ONVIF XML metadata)."""


class SupportedMetadata(Model):
    producers: list[ProducerSampleFrame]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/analyticsmetadataconfig.cgi"

INFO = ApiInfo(
    id="analytics-metadata-config",
    name="Analytics Metadata Producer Configuration",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("analytics-metadata-config"),),
    docs=("https://developer.axis.com/vapix/network-video/analytics-metadata-producer-configuration/",),
    errors={
        1000: ErrorCode("The application failed to handle the request.", "internal"),
        2000: ErrorCode("The major version number isn't supported.", "unsupported"),
        2001: ErrorCode(
            "The request was not formatted correctly, i.e. does not follow json-schema.", "invalid_argument"
        ),
        2003: ErrorCode("The request has a missing mandatory parameter.", "invalid_argument"),
        2004: ErrorCode("The request has parameter that has an invalid value.", "invalid_argument"),
        2005: ErrorCode("The method in the request is not supported.", "unsupported"),
    },
)


class OPS:
    list_producers = Operation(
        INFO,
        "list_producers",
        JsonRpcBinding("listProducers", PATH),
        params=ListProducersRequest,
        result=ProducerList,
        access="viewer",
        effect="read",
    )
    set_enabled_producers = Operation(
        INFO,
        "set_enabled_producers",
        JsonRpcBinding("setEnabledProducers", PATH),
        params=SetEnabledProducersRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_supported_metadata = Operation(
        INFO,
        "get_supported_metadata",
        JsonRpcBinding("getSupportedMetadata", PATH),
        params=GetSupportedMetadataRequest,
        result=SupportedMetadata,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class AnalyticsMetadataConfigApi(SyncApi):
    """Analytics Metadata Producer Configuration (``analytics-metadata-config``, version 1)."""

    INFO = INFO

    def list_producers(
        self, *, producers: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> ProducerList:
        """Lists all or specific metadata producers with their supported video channels and status.

        All producers are listed when params.producers is absent. If producers is set, the response is
        successful even if some don't exist; those are not listed.

        Access: viewer.
        """
        return self._run(OPS.list_producers, None, {"producers": producers}, request_options)

    @overload
    def set_enabled_producers(
        self, request: SetEnabledProducersRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_enabled_producers(
        self, /, *, producers: list[ProducerChannels], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_enabled_producers(
        self,
        request: SetEnabledProducersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Enables/disables specific metadata producers on their supported video channels.

        Error if a video channel the producer does not support is specified; error if a fault occurs on any
        of the producer's channels, in which case no updates are applied.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_enabled_producers, request, kwargs, request_options)

    def get_supported_metadata(
        self, *, producers: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> SupportedMetadata:
        """Retrieves a sample frame (ONVIF XML metadata format) for all or specific metadata producers.

        All producers are listed if params.producers is absent; missing producers are omitted from the
        response.

        Access: viewer.
        """
        return self._run(OPS.get_supported_metadata, None, {"producers": producers}, request_options)


class AsyncAnalyticsMetadataConfigApi(AsyncApi):
    """Analytics Metadata Producer Configuration (``analytics-metadata-config``, version 1)."""

    INFO = INFO

    async def list_producers(
        self, *, producers: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> ProducerList:
        """Lists all or specific metadata producers with their supported video channels and status.

        All producers are listed when params.producers is absent. If producers is set, the response is
        successful even if some don't exist; those are not listed.

        Access: viewer.
        """
        return await self._run(OPS.list_producers, None, {"producers": producers}, request_options)

    @overload
    async def set_enabled_producers(
        self, request: SetEnabledProducersRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_enabled_producers(
        self, /, *, producers: list[ProducerChannels], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_enabled_producers(
        self,
        request: SetEnabledProducersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Enables/disables specific metadata producers on their supported video channels.

        Error if a video channel the producer does not support is specified; error if a fault occurs on any
        of the producer's channels, in which case no updates are applied.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_enabled_producers, request, kwargs, request_options)

    async def get_supported_metadata(
        self, *, producers: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> SupportedMetadata:
        """Retrieves a sample frame (ONVIF XML metadata format) for all or specific metadata producers.

        All producers are listed if params.producers is absent; missing producers are omitted from the
        response.

        Access: viewer.
        """
        return await self._run(OPS.get_supported_metadata, None, {"producers": producers}, request_options)
