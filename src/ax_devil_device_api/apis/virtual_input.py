# GENERATED from specs/apis/network-video/virtual-input.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Activate/deactivate virtual input ports (/axis-cgi/virtualinput/*.cgi, XML) and the legacy manual trigger (/axis-cgi/io/virtualinput.cgi).

Docs: https://developer.axis.com/vapix/network-video/input-and-outputs/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ActivateResult(Model):
    state_changed: bool = Field(validation_alias="StateChanged", serialization_alias="StateChanged")
    """true if the port state was changed, false if it was not changed."""


class DeactivateResult(Model):
    state_changed: bool = Field(validation_alias="StateChanged", serialization_alias="StateChanged")
    """true if the port state was changed, false if it was not changed."""


class SchemaVersion(Model):
    major_version: int = Field(validation_alias="MajorVersion", serialization_alias="MajorVersion")
    """The major version of the XML schema."""
    minor_version: int = Field(validation_alias="MinorVersion", serialization_alias="MinorVersion")
    """The minor version of the XML schema."""
    deprecated: str | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """"true" if this version of the XML schema is deprecated and should not be used. The syntax shows an empty element when it is not deprecated."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class ActivateRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    port: int
    """The virtual input to activate. The number of ports may vary between devices; the default is 64."""
    duration: int | None = Field(default=None, ge=0)
    """Seconds until the port is automatically deactivated. If the port is already active it stays active and is deactivated after the time. 0 activates and then deactivates the port directly. If not given the port is not deactivated automatically."""


class DeactivateRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    port: int
    """The virtual input to deactivate. The number of ports may vary between devices; the default is 64."""


class ManualTriggerRequest(Model):
    action: str = Field(pattern=r"^[0-9]*:[/\\]([0-9]+[/\\])*$")
    """The port and action sequence, e.g. 6:/2000\\ to activate port 6 for 2 seconds."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/virtualinput/activate.cgi"

INFO = ApiInfo(
    id="virtual-input",
    name="Virtual input API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.VirtualInput.VirtualInput", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/input-and-outputs/",),
    errors={
        10: ErrorCode("Missing argument.", "invalid_argument"),
        20: ErrorCode("The specified virtual input does not exist.", "not_found"),
        30: ErrorCode("The specified schema version is not supported.", "unsupported"),
        40: ErrorCode("Internal server error.", "internal"),
        50: ErrorCode("Invalid duration.", "invalid_argument"),
    },
)


class OPS:
    activate = Operation(
        INFO,
        "activate",
        CgiBinding(
            PATH,
            args=(CgiArg("schemaversion"), CgiArg("port"), CgiArg("duration")),
            reply=Xml(map=XmlMap(fields=(XmlField("StateChanged", source="child"),), root="Success/ActivateSuccess")),
        ),
        params=ActivateRequest,
        result=ActivateResult,
        access="operator",
        effect="action",
    )
    deactivate = Operation(
        INFO,
        "deactivate",
        CgiBinding(
            "/axis-cgi/virtualinput/deactivate.cgi",
            args=(CgiArg("schemaversion"), CgiArg("port")),
            reply=Xml(map=XmlMap(fields=(XmlField("StateChanged", source="child"),), root="Success/DeactivateSuccess")),
        ),
        params=DeactivateRequest,
        result=DeactivateResult,
        access="operator",
        effect="action",
    )
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            "/axis-cgi/virtualinput/getschemaversions.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "SchemaVersion",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("MajorVersion", source="child"),
                                    XmlField("MinorVersion", source="child"),
                                    XmlField("Deprecated", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetSchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="operator",
        effect="read",
    )
    manual_trigger = Operation(
        INFO,
        "manual_trigger",
        CgiBinding("/axis-cgi/io/virtualinput.cgi", args=(CgiArg("action"),), reply=Text()),
        params=ManualTriggerRequest,
        access="viewer",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class VirtualInputApi(SyncApi):
    """Virtual input API (``virtual-input``)."""

    INFO = INFO

    def activate(
        self,
        port: int,
        *,
        schemaversion: int,
        duration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ActivateResult:
        """Activate a virtual input port (state high). Access: operator."""
        return self._run(
            OPS.activate, None, {"schemaversion": schemaversion, "port": port, "duration": duration}, request_options
        )

    def deactivate(
        self, port: int, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> DeactivateResult:
        """Deactivate a virtual input port (state low). Access: operator."""
        return self._run(OPS.deactivate, None, {"schemaversion": schemaversion, "port": port}, request_options)

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List supported XML schema versions and whether they are deprecated. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def manual_trigger(self, action: str, *, request_options: RequestOptions | None = None) -> None:
        """Activate/deactivate the manual trigger or simulate physical input ports, optionally for a time.

        The action is a sequence of port, action characters and delays: ``[<port>]:<a>[<wait><a>...]`` where
        ``/`` activates, ``\\`` deactivates and ``<wait>`` is a delay in milliseconds. The port defaults to
        input 1. The manual trigger is normally port 6 or port 1. For example ``6:/2000\\`` activates port 6,
        waits 2 seconds and deactivates it. The client percent-encodes the ``:``, ``/`` and ``\\``
        characters.

        Access: viewer.
        """
        self._run(OPS.manual_trigger, None, {"action": action}, request_options)


class AsyncVirtualInputApi(AsyncApi):
    """Virtual input API (``virtual-input``)."""

    INFO = INFO

    async def activate(
        self,
        port: int,
        *,
        schemaversion: int,
        duration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ActivateResult:
        """Activate a virtual input port (state high). Access: operator."""
        return await self._run(
            OPS.activate, None, {"schemaversion": schemaversion, "port": port, "duration": duration}, request_options
        )

    async def deactivate(
        self, port: int, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> DeactivateResult:
        """Deactivate a virtual input port (state low). Access: operator."""
        return await self._run(OPS.deactivate, None, {"schemaversion": schemaversion, "port": port}, request_options)

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List supported XML schema versions and whether they are deprecated. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def manual_trigger(self, action: str, *, request_options: RequestOptions | None = None) -> None:
        """Activate/deactivate the manual trigger or simulate physical input ports, optionally for a time.

        The action is a sequence of port, action characters and delays: ``[<port>]:<a>[<wait><a>...]`` where
        ``/`` activates, ``\\`` deactivates and ``<wait>`` is a delay in milliseconds. The port defaults to
        input 1. The manual trigger is normally port 6 or port 1. For example ``6:/2000\\`` activates port 6,
        waits 2 seconds and deactivates it. The client percent-encodes the ``:``, ``/`` and ``\\``
        characters.

        Access: viewer.
        """
        await self._run(OPS.manual_trigger, None, {"action": action}, request_options)
