# GENERATED from specs/apis/network-video/on-screen-controls.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List the features an operator can trigger from a video client, in several languages. Add, remove, enable and disable feature descriptions.

Docs: https://developer.axis.com/vapix/network-video/on-screen-controls/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, Applicability, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

VmsHint = Literal[
    "windowClose",
    "audioOutDisable",
    "audioOutEnable",
    "audioOutToggle",
    "audioInDisable",
    "audioInEnable",
    "audioInToggle",
    "hidden",
]
VmsReq = Literal["eventStream"]
JsonVariableFormat = Literal["string", "integer", "fraction", "exponent", "boolean", "null"]


class MultiOptionValue(Model):
    value: str | None = None
    """Value that should be part of requestURL."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """Translated name."""


class RequestUrlParameter(Model):
    """One parameter of a feature request. Which fields apply depends on ``type``."""

    type: str | None = None
    """Parameter type: a range, a geometric type (coordinate, line, box, polygon), a string, a multiOption, transmitAudioData, or a JSON-only type (fixed, context, keyOnly)."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """Short description (one or two words) of the parameter."""
    info: str | None = None
    """Optional information about the parameter."""
    key: str | None = Field(default=None, validation_alias="Key", serialization_alias="Key")
    """String to use as a key for parameters in a JSON payload."""
    json_variable_format: JsonVariableFormat | None = Field(
        default=None, validation_alias="jsonVariableFormat", serialization_alias="jsonVariableFormat"
    )
    """Format of the value in a JSON payload."""
    value: str | None = None
    """Value for the JSON-only types ``fixed`` and ``context``."""
    default_value: str | None = Field(default=None, validation_alias="defaultValue", serialization_alias="defaultValue")
    """Default value for range, string and multiOption parameters."""
    unit: Literal["integer", "fraction"] | None = None
    """Range parameters, the type of value."""
    min: str | None = None
    """Range parameters, minimum value."""
    max: str | None = None
    """Range parameters, maximum value."""
    step: str | None = None
    """Range parameters, step size."""
    values: list[MultiOptionValue] | None = None
    """multiOption parameters, the possible values."""
    content_type: str | list[str] | None = Field(
        default=None, validation_alias="contentType", serialization_alias="contentType"
    )
    """transmitAudioData parameters, the accepted audio content types: g711, g726, axis-mulaw-128."""


class Feature(Model):
    """One feature, with the request a client sends to the camera to trigger it."""

    name: str
    """Name of the feature in English, used as an identifier."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """Translated name of the feature according to the requested locale."""
    user: list[Literal["operator", "admin", "event"]] | None = None
    """Recommended user level for accessing this feature."""
    info: str | None = None
    """Translated information string about the feature."""
    request_type: Literal["GET", "POST"] | None = Field(
        default=None, validation_alias="requestType", serialization_alias="requestType"
    )
    """How the CGI request should be sent to the camera."""
    request_payload: Literal["JSON", "BINARY"] | None = Field(
        default=None, validation_alias="requestPayload", serialization_alias="requestPayload"
    )
    """The format of the request payload. SOAP and XML are reserved for future use."""
    request_url: str | None = Field(default=None, validation_alias="requestURL", serialization_alias="requestURL")
    """URL that triggers the feature; ``<param>`` placeholders are replaced by parameter values."""
    response: bool | None = None
    """Whether the request returns a value to the video client."""
    vms_hint: list[VmsHint] | None = Field(default=None, validation_alias="vmsHint", serialization_alias="vmsHint")
    """Client side actions that are suitable when the button is pressed. Not mandatory."""
    vms_req: list[VmsReq] | None = Field(default=None, validation_alias="vmsReq", serialization_alias="vmsReq")
    """Requirements on the client that must be fulfilled for the button to be useful."""
    json_template: str | None = Field(default=None, validation_alias="jsonTemplate", serialization_alias="jsonTemplate")
    """Template for the JSON payload of a POST request; only present when requestPayload is JSON."""
    parameters: dict[str, RequestUrlParameter] | None = None
    """The parameters to use in requestURL, keyed by parameter name."""


class FeatureGroup(Model):
    """A group of features, possibly with nested groups. The root group is named ``root``."""

    name: str
    """Name of the group in English, used as an identifier."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """Translated name of the group according to the requested locale."""
    feature_groups: list[FeatureGroup] | None = Field(
        default=None, validation_alias="featureGroups", serialization_alias="featureGroups"
    )
    """Nested groups, used for grouping features together like PTZ features. Features added with addFeatures are placed in a post install group, and then an individual group for the specific request."""
    features: list[Feature] | None = None
    """The features located in this group."""
    status: Literal["enabled", "disabled"] | None = None
    """Whether the group is enabled. Appears in examples only; not in the field tables."""


class Language(Model):
    language: str
    """Name of the language."""
    locale: str
    """Locale specifier, for example en-us."""


class Languages(Model):
    languages: list[Language]


class FeatureDescription(Model):
    feature_description: FeatureGroup = Field(
        validation_alias="featureDescription", serialization_alias="featureDescription"
    )
    """Root feature group (name "root")."""


FeaturesByLocale = dict[str, FeatureGroup]


class AddedFeature(Model):
    name: str
    """Name of the added feature group."""
    locales: list[Language]
    """The locales the feature group was added for."""


class AddedFeatures(Model):
    added_features: list[AddedFeature] = Field(validation_alias="addedFeatures", serialization_alias="addedFeatures")


class FeaturesRequest(Model):
    locale: str | None = None
    """A locale specifier, for example en-us, from the languages operation. Default: 'en-us'."""
    accept_locale_mismatch: bool | None = Field(
        default=None, validation_alias="acceptLocaleMismatch", serialization_alias="acceptLocaleMismatch"
    )
    """If set to true, feature information that is not available in the given locale or in English will be included in the response in the first found language. Otherwise it will be ignored. Defaults to false. Default: False."""
    channel: int | None = None
    """A channel/source specifier that filters the returning information. If set, the default returned information will contain both the features with the chosen channel ID and the features without a channel ID."""


class AddFeaturesRequest(Model):
    locale: str = Field(pattern="^[a-z]{2}(-[a-z]{2})?$")
    """Must be formatted in on of two ways, `ab` or `ab-xy`."""
    language: str
    """Name of the language."""
    feature_description: FeatureGroup = Field(
        validation_alias="featureDescription", serialization_alias="featureDescription"
    )
    """The feature group to add. The field table points to the feature structure, but the examples pass a feature group."""


class RemoveFeaturesRequest(Model):
    locale: str
    """The locale for which the feature group should be removed."""
    name: str
    """The feature group to remove."""


class GetAllFeaturesRequest(Model):
    show_disabled: bool | None = Field(
        default=None, validation_alias="showDisabled", serialization_alias="showDisabled"
    )
    """Include disabled features. Used in the docs' example only; the docs say the method takes no parameters."""


class EnableFeatureRequest(Model):
    name: str
    """The name of the feature that should be enabled."""


class DisableFeatureRequest(Model):
    name: str
    """The name of the feature that should be disabled."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/axis-onscreencontrols/onscreencontrols.cgi"

INFO = ApiInfo(
    id="on-screen-controls",
    name="On-screen controls API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1), ApiVersion(1, 3), ApiVersion(1, 4)),
    discovery=(ParamDiscovery("Properties.AddOnFramework.Version", "1.0", ">="),),
    requires_firmware="7.10",
    docs=("https://developer.axis.com/vapix/network-video/on-screen-controls/",),
    errors={
        1001: ErrorCode("Out of memory.", "internal"),
        1002: ErrorCode("Error in the CGI request.", "invalid_argument"),
        1003: ErrorCode("CGI request is an invalid method.", "invalid_argument"),
        2001: ErrorCode("Error in the database.", "internal"),
        2002: ErrorCode("Invalid locale.", "invalid_argument"),
        2003: ErrorCode("Invalid JSON.", "invalid_argument"),
        2004: ErrorCode("Unsupported API version.", "unsupported"),
        2005: ErrorCode("Missing data param.", "invalid_argument"),
        9999: ErrorCode("Internal error.", "internal"),
    },
)


class OPS:
    languages = Operation(
        INFO, "languages", JsonRpcBinding("languages", PATH), result=Languages, access="viewer", effect="read"
    )
    features = Operation(
        INFO,
        "features",
        JsonRpcBinding("features", PATH),
        params=FeaturesRequest,
        result=FeatureDescription,
        access="viewer",
        effect="read",
        applicability=(Applicability("channel", ApiVersion(1, 4)),),
    )
    add_features = Operation(
        INFO,
        "add_features",
        JsonRpcBinding("addFeatures", PATH),
        params=AddFeaturesRequest,
        access="admin",
        effect="write",
        write="create",
    )
    list_added_features = Operation(
        INFO,
        "list_added_features",
        JsonRpcBinding("listAddedFeatures", PATH),
        result=AddedFeatures,
        access="admin",
        effect="read",
    )
    remove_features = Operation(
        INFO,
        "remove_features",
        JsonRpcBinding("removeFeatures", PATH),
        params=RemoveFeaturesRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_all_features = Operation(
        INFO,
        "get_all_features",
        JsonRpcBinding("getAllFeatures", PATH),
        params=GetAllFeaturesRequest,
        result=FeaturesByLocale,
        access="viewer",
        effect="read",
        since=ApiVersion(1, 1),
    )
    enable_feature = Operation(
        INFO,
        "enable_feature",
        JsonRpcBinding("enableFeature", PATH),
        params=EnableFeatureRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 3),
        write="patch",
    )
    disable_feature = Operation(
        INFO,
        "disable_feature",
        JsonRpcBinding("disableFeature", PATH),
        params=DisableFeatureRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 3),
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class OnScreenControlsApi(SyncApi):
    """On-screen controls API (``on-screen-controls``, version 1)."""

    INFO = INFO

    def languages(self, *, request_options: RequestOptions | None = None) -> Languages:
        """Get a list of supported languages and locales. Access: viewer."""
        return self._run(OPS.languages, None, {}, request_options)

    def features(
        self,
        *,
        locale: str | MISSING = MISSING,
        accept_locale_mismatch: bool | MISSING = MISSING,
        channel: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FeatureDescription:
        """Get descriptions of available features in one of the supported languages.

        Features without a description in the requested locale fall back to en-us. An unsupported locale
        gives an error.

        Access: viewer.
        """
        return self._run(
            OPS.features,
            None,
            {"locale": locale, "accept_locale_mismatch": accept_locale_mismatch, "channel": channel},
            request_options,
        )

    @overload
    def add_features(
        self, request: AddFeaturesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_features(
        self,
        /,
        *,
        locale: str,
        language: str,
        feature_description: FeatureGroup,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_features(
        self,
        request: AddFeaturesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add information about a manually installed feature.

        Saves the feature descriptions for the given locale.

        Access: admin.
        """
        self._run(OPS.add_features, request, kwargs, request_options)

    def list_added_features(self, *, request_options: RequestOptions | None = None) -> AddedFeatures:
        """Get a list of manually added features. Access: admin."""
        return self._run(OPS.list_added_features, None, {}, request_options)

    def remove_features(self, *, locale: str, name: str, request_options: RequestOptions | None = None) -> None:
        """Remove information about a manually installed feature.

        Removes the feature group added for a locale.

        Access: admin.
        """
        self._run(OPS.remove_features, None, {"locale": locale, "name": name}, request_options)

    def get_all_features(
        self, *, show_disabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> FeaturesByLocale:
        """Get a collection of feature descriptions in all available languages.

        A CGI method for retrieving all feature descriptions in all available languages. The returned
        collection contains all feature descriptions arranged in JSON objects identical with
        [Features](#features-api-specification), using locales as keys. The locales are the same as returned
        by [Languages](#languages-api-specification).

        Access: viewer.
        """
        return self._run(OPS.get_all_features, None, {"show_disabled": show_disabled}, request_options)

    def enable_feature(self, *, name: str, request_options: RequestOptions | None = None) -> None:
        """Show the option to enable/disable a feature.

        Changes the status of a feature to ``enabled``.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.enable_feature, None, {"name": name}, request_options)

    def disable_feature(self, *, name: str, request_options: RequestOptions | None = None) -> None:
        """Remove the option to enable/disable a feature.

        Changes the status of a feature to ``disabled``.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.disable_feature, None, {"name": name}, request_options)


class AsyncOnScreenControlsApi(AsyncApi):
    """On-screen controls API (``on-screen-controls``, version 1)."""

    INFO = INFO

    async def languages(self, *, request_options: RequestOptions | None = None) -> Languages:
        """Get a list of supported languages and locales. Access: viewer."""
        return await self._run(OPS.languages, None, {}, request_options)

    async def features(
        self,
        *,
        locale: str | MISSING = MISSING,
        accept_locale_mismatch: bool | MISSING = MISSING,
        channel: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FeatureDescription:
        """Get descriptions of available features in one of the supported languages.

        Features without a description in the requested locale fall back to en-us. An unsupported locale
        gives an error.

        Access: viewer.
        """
        return await self._run(
            OPS.features,
            None,
            {"locale": locale, "accept_locale_mismatch": accept_locale_mismatch, "channel": channel},
            request_options,
        )

    @overload
    async def add_features(
        self, request: AddFeaturesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_features(
        self,
        /,
        *,
        locale: str,
        language: str,
        feature_description: FeatureGroup,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_features(
        self,
        request: AddFeaturesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add information about a manually installed feature.

        Saves the feature descriptions for the given locale.

        Access: admin.
        """
        await self._run(OPS.add_features, request, kwargs, request_options)

    async def list_added_features(self, *, request_options: RequestOptions | None = None) -> AddedFeatures:
        """Get a list of manually added features. Access: admin."""
        return await self._run(OPS.list_added_features, None, {}, request_options)

    async def remove_features(self, *, locale: str, name: str, request_options: RequestOptions | None = None) -> None:
        """Remove information about a manually installed feature.

        Removes the feature group added for a locale.

        Access: admin.
        """
        await self._run(OPS.remove_features, None, {"locale": locale, "name": name}, request_options)

    async def get_all_features(
        self, *, show_disabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> FeaturesByLocale:
        """Get a collection of feature descriptions in all available languages.

        A CGI method for retrieving all feature descriptions in all available languages. The returned
        collection contains all feature descriptions arranged in JSON objects identical with
        [Features](#features-api-specification), using locales as keys. The locales are the same as returned
        by [Languages](#languages-api-specification).

        Access: viewer.
        """
        return await self._run(OPS.get_all_features, None, {"show_disabled": show_disabled}, request_options)

    async def enable_feature(self, *, name: str, request_options: RequestOptions | None = None) -> None:
        """Show the option to enable/disable a feature.

        Changes the status of a feature to ``enabled``.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.enable_feature, None, {"name": name}, request_options)

    async def disable_feature(self, *, name: str, request_options: RequestOptions | None = None) -> None:
        """Remove the option to enable/disable a feature.

        Changes the status of a feature to ``disabled``.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.disable_feature, None, {"name": name}, request_options)
