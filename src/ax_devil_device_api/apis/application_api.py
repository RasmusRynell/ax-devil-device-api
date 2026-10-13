# GENERATED from specs/apis/applications/application-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control (start/stop/restart/remove), configure and list ACAP applications and manage their license keys.

Docs: https://developer.axis.com/vapix/applications/application-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._http.upload import UploadSource, UploadSpec
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextOk, Xml
from .._protocols.xmlmap import XmlField, XmlMap, XmlStatusError
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ApplicationStatus = Literal["Running", "Stopped", "Idle"]
LicenseStatus = Literal["Valid", "Invalid", "Missing", "Custom", "None"]
ConfigName = Literal["AllowUnsigned", "AllowRoot"]


class PackageRequest(Model):
    package: str
    """The application package to perform the action on (the package name)."""
    returnpage: str | None = None
    """The web page to return to after performing the action."""


class LicensePackageRequest(Model):
    package: str
    """The name of the application package to which the license key belongs."""


class ConfigNameRequest(Model):
    name: ConfigName


class SetConfigRequest(Model):
    name: ConfigName
    value: bool
    """The new value of the configuration parameter."""


class ConfigValue(Model):
    """A configuration parameter as returned in ``<param name=".." value=".."/>``."""

    name: str
    value: str
    """``true`` or ``false``."""


class ApplicationResource(Model):
    name: str
    """The name of the resource, for example ``DeepLearningProcessor``."""
    used: Literal["Yes", "No"]
    """Whether the application uses the resource."""


class CompatibleOsVersionRange(Model):
    min: str | None = None
    """Minimum compatible AXIS OS version."""
    max: str | None = None
    """Maximum compatible AXIS OS version."""


class InstalledApplication(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Application short name."""
    nice_name: str | None = Field(default=None, validation_alias="NiceName", serialization_alias="NiceName")
    """Application official name."""
    vendor: str | None = Field(default=None, validation_alias="Vendor", serialization_alias="Vendor")
    version: str | None = Field(default=None, validation_alias="Version", serialization_alias="Version")
    bundled: Literal["Yes", "No"] | None = Field(
        default=None, validation_alias="Bundled", serialization_alias="Bundled"
    )
    """Whether the application is bundled with the device software."""
    application_id: int | None = Field(
        default=None, validation_alias="ApplicationID", serialization_alias="ApplicationID"
    )
    license: LicenseStatus | None = Field(default=None, validation_alias="License", serialization_alias="License")
    license_expiration_date: str | None = Field(
        default=None, validation_alias="LicenseExpirationDate", serialization_alias="LicenseExpirationDate"
    )
    """Date (YYYY-MM-DD) when the license expires."""
    license_name: str | None = Field(default=None, validation_alias="LicenseName", serialization_alias="LicenseName")
    status: ApplicationStatus | None = Field(default=None, validation_alias="Status", serialization_alias="Status")
    configuration_page: str | None = Field(
        default=None, validation_alias="ConfigurationPage", serialization_alias="ConfigurationPage"
    )
    """Relative URL to the application configuration page."""
    validation_result: str | None = Field(
        default=None, validation_alias="ValidationResult", serialization_alias="ValidationResult"
    )
    """Complete URL to a validation or result page."""
    vendor_home_page: str | None = Field(
        default=None, validation_alias="VendorHomePage", serialization_alias="VendorHomePage"
    )
    signature_status: str | None = Field(
        default=None, validation_alias="SignatureStatus", serialization_alias="SignatureStatus"
    )
    """``Signed``, ``Unsigned`` or ``Unknown`` (needs reinstalling on AXIS OS 12.8 or later)."""
    signed_status: str | None = Field(default=None, validation_alias="SignedStatus", serialization_alias="SignedStatus")
    """The attribute name used in the response XSD; see ``SignatureStatus``."""
    resources: list[ApplicationResource] | None = Field(
        default=None, validation_alias="Resources", serialization_alias="Resources"
    )
    compatible_os_versions: list[CompatibleOsVersionRange] | None = Field(
        default=None, validation_alias="CompatibleOsVersions", serialization_alias="CompatibleOsVersions"
    )


class ApplicationList(Model):
    applications: list[InstalledApplication]


class AcapInfo(Model):
    supported_sdks: list[str] | None = Field(
        default=None, validation_alias="supportedSdks", serialization_alias="supportedSdks"
    )
    """SDKs whose applications are able to run on the device, for example ``acap3``, ``acap4-cv``, ``acap4-native``."""


class UploadApplicationRequest(Model):
    package: UploadSource = Field(exclude=True, repr=False)
    """The application package (.eap), as bytes, a Path or an Upload(stream, size)."""


class UploadLicenseKeyRequest(Model):
    package: str
    """The name of the application package to which the license key belongs."""
    license_key: UploadSource = Field(exclude=True, repr=False)
    """The license key file, as bytes, a Path or an Upload(stream, size)."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/applications/control.cgi"

INFO = ApiInfo(
    id="application-api",
    name="Application API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.EmbeddedDevelopment.Version"),),
    docs=("https://developer.axis.com/vapix/applications/application-api/",),
    errors={
        1: ErrorCode(
            "Invalid application package. The package is not an Embedded Axis Package or it contains an invalid manifest.",
            "invalid_argument",
        ),
        4: ErrorCode("Application not found. The specified application package could not be found.", "not_found"),
        6: ErrorCode("The application is already running."),
        7: ErrorCode("Application not running. The application must be running to perform the action."),
        8: ErrorCode("Application is in a failure state. The application must be stopped before it can start again."),
        9: ErrorCode(
            "Too many applications are running. The application cannot be started. This limitation was removed in AXIS OS 12.6."
        ),
        10: ErrorCode("Unspecified error. See the system log for more information.", "internal"),
        15: ErrorCode(
            "Operation timed out. The outcome of the operation could not be determined. Check logs for more information.",
            "unavailable",
        ),
    },
)


class OPS:
    start_application = Operation(
        INFO,
        "start_application",
        CgiBinding(
            PATH,
            method="POST",
            fixed_query=(("action", "start"),),
            args=(CgiArg("package"), CgiArg("returnpage")),
            reply=TextOk(),
        ),
        params=PackageRequest,
        access="admin",
        effect="action",
    )
    stop_application = Operation(
        INFO,
        "stop_application",
        CgiBinding(
            PATH,
            method="POST",
            fixed_query=(("action", "stop"),),
            args=(CgiArg("package"), CgiArg("returnpage")),
            reply=TextOk(),
        ),
        params=PackageRequest,
        access="admin",
        effect="action",
    )
    restart_application = Operation(
        INFO,
        "restart_application",
        CgiBinding(
            PATH,
            method="POST",
            fixed_query=(("action", "restart"),),
            args=(CgiArg("package"), CgiArg("returnpage")),
            reply=TextOk(),
        ),
        params=PackageRequest,
        access="admin",
        effect="action",
    )
    remove_application = Operation(
        INFO,
        "remove_application",
        CgiBinding(
            PATH,
            method="POST",
            fixed_query=(("action", "remove"),),
            args=(CgiArg("package"), CgiArg("returnpage")),
            reply=TextOk(),
        ),
        params=PackageRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_application_config = Operation(
        INFO,
        "get_application_config",
        CgiBinding(
            "/axis-cgi/applications/config.cgi",
            method="POST",
            fixed_query=(("action", "get"),),
            args=(CgiArg("name"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("name"), XmlField("value")), root="param"),
                status_error=XmlStatusError(attribute="result", value="error"),
            ),
        ),
        params=ConfigNameRequest,
        result=ConfigValue,
        access="admin",
        effect="read",
        errors={
            1: ErrorCode(
                "Malformed request. ``value`` must be either true or false. From AXIS OS 12.2 this is replaced with HTTP 400 Bad Request.",
                "invalid_argument",
            )
        },
    )
    set_application_config = Operation(
        INFO,
        "set_application_config",
        CgiBinding(
            "/axis-cgi/applications/config.cgi",
            method="POST",
            fixed_query=(("action", "set"),),
            args=(CgiArg("name"), CgiArg("value")),
            reply=Xml(
                map=XmlMap(fields=(XmlField("name"), XmlField("value")), root="param"),
                status_error=XmlStatusError(attribute="result", value="error"),
            ),
        ),
        params=SetConfigRequest,
        result=ConfigValue,
        access="admin",
        effect="write",
        write="patch",
        errors={
            1: ErrorCode(
                "Malformed request. ``value`` must be either true or false. From AXIS OS 12.2 this is replaced with HTTP 400 Bad Request.",
                "invalid_argument",
            )
        },
    )
    remove_license_key = Operation(
        INFO,
        "remove_license_key",
        CgiBinding(
            "/axis-cgi/applications/license.cgi",
            method="POST",
            fixed_query=(("action", "removelicensekey"),),
            args=(CgiArg("package"),),
            reply=TextOk(),
        ),
        params=LicensePackageRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={
            21: ErrorCode("Invalid license key file.", "invalid_argument"),
            22: ErrorCode("File upload failed. See the system log for more information.", "internal"),
            23: ErrorCode(
                "Failed to remove the license key file. See the system log for more information.", "internal"
            ),
            24: ErrorCode("The application is not installed.", "not_found"),
            25: ErrorCode("The key's application ID does not match the installed application.", "invalid_argument"),
            26: ErrorCode("The license key cannot be used with this version of the application.", "unsupported"),
            30: ErrorCode("Wrong serial number.", "invalid_argument"),
            31: ErrorCode("The license key has expired.", "invalid_argument"),
        },
    )
    list_applications = Operation(
        INFO,
        "list_applications",
        CgiBinding(
            "/axis-cgi/applications/list.cgi",
            method="POST",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "applications",
                            source="path",
                            name="application",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("Name"),
                                    XmlField("NiceName"),
                                    XmlField("Vendor"),
                                    XmlField("Version"),
                                    XmlField("Bundled"),
                                    XmlField("ApplicationID"),
                                    XmlField("License"),
                                    XmlField("LicenseExpirationDate"),
                                    XmlField("LicenseName"),
                                    XmlField("Status"),
                                    XmlField("ConfigurationPage"),
                                    XmlField("ValidationResult"),
                                    XmlField("VendorHomePage"),
                                    XmlField("SignatureStatus"),
                                    XmlField("SignedStatus"),
                                    XmlField(
                                        "Resources",
                                        source="path",
                                        name="Resources/Resource",
                                        many=True,
                                        nested=XmlMap(fields=(XmlField("name"), XmlField("used"))),
                                    ),
                                    XmlField(
                                        "CompatibleOsVersions",
                                        source="path",
                                        name="CompatibleOsVersions/VersionRange",
                                        many=True,
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("min", source="child", name="Min"),
                                                XmlField("max", source="child", name="Max"),
                                            )
                                        ),
                                    ),
                                )
                            ),
                        ),
                    )
                ),
                status_error=XmlStatusError(attribute="result", value="error"),
            ),
        ),
        result=ApplicationList,
        access="admin",
        effect="read",
    )
    get_info = Operation(
        INFO,
        "get_info",
        CgiBinding(
            "/axis-cgi/applications/info.cgi",
            method="POST",
            reply=Xml(
                map=XmlMap(fields=(XmlField("supportedSdks", source="path", name="supportedSdks/sdk", many=True),)),
                status_error=XmlStatusError(attribute="result", value="error"),
            ),
        ),
        result=AcapInfo,
        access="admin",
        effect="read",
    )
    upload_application = Operation(
        INFO,
        "upload_application",
        CgiBinding(
            "/axis-cgi/applications/upload.cgi",
            method="POST",
            encoding="multipart",
            uploads=(UploadSpec("package", part="file", content_type="application/octet-stream"),),
            reply=TextOk(),
        ),
        params=UploadApplicationRequest,
        access="admin",
        effect="write",
        write="create",
        errors={
            2: ErrorCode(
                "Verification failed. The signature of the application package is either missing or invalid.",
                "invalid_argument",
            ),
            3: ErrorCode(
                "Application package too large. The package file is too large or the disk is full.", "invalid_argument"
            ),
            5: ErrorCode(
                "Application package not compatible with the Axis device. See the system log for more information.",
                "unsupported",
            ),
            12: ErrorCode("Upload currently unavailable. An application package upload is ongoing.", "unavailable"),
            13: ErrorCode(
                "Installation failed. The application package requires a user or group that is not allowed.",
                "invalid_argument",
            ),
            14: ErrorCode(
                "Application package already exists in the application store but with a different letter case.",
                "invalid_argument",
            ),
            27: ErrorCode(
                "Upgrade not allowed. The vendor ID of the package must be the same as the vendor ID of the application it replaces.",
                "invalid_argument",
            ),
            29: ErrorCode("Invalid manifest.json or package.conf file.", "invalid_argument"),
            51: ErrorCode(
                "Serial number in Developer Mode does not match the device serial number.", "invalid_argument"
            ),
            52: ErrorCode(
                "Developer Mode application upgrade not allowed. The vendor ID for Developer Mode has changed.",
                "invalid_argument",
            ),
            53: ErrorCode("Application vendor ID does not match the Developer Mode vendor ID.", "invalid_argument"),
            54: ErrorCode(
                "Developer Mode application does not allow the application's manifest contents.", "invalid_argument"
            ),
        },
    )
    upload_license_key = Operation(
        INFO,
        "upload_license_key",
        CgiBinding(
            "/axis-cgi/applications/license.cgi",
            method="POST",
            encoding="multipart",
            url_query=(("action", "uploadlicensekey"),),
            args=(CgiArg("package", place="query"),),
            uploads=(UploadSpec("license_key", part="file", content_type="application/octet-stream"),),
            reply=TextOk(),
        ),
        params=UploadLicenseKeyRequest,
        access="admin",
        effect="write",
        write="create",
        errors={
            21: ErrorCode("Invalid license key file.", "invalid_argument"),
            22: ErrorCode("File upload failed. See the system log for more information.", "internal"),
            24: ErrorCode("The application is not installed.", "not_found"),
            25: ErrorCode("The key's application ID does not match the installed application.", "invalid_argument"),
            26: ErrorCode("The license key cannot be used with this version of the application.", "unsupported"),
            30: ErrorCode("Wrong serial number.", "invalid_argument"),
            31: ErrorCode("The license key has expired.", "invalid_argument"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class ApplicationApi(SyncApi):
    """Application API (``application-api``)."""

    INFO = INFO

    def start_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Start the application. Access: admin."""
        self._run(OPS.start_application, None, {"package": package, "returnpage": returnpage}, request_options)

    def stop_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Stop the application. Access: admin."""
        self._run(OPS.stop_application, None, {"package": package, "returnpage": returnpage}, request_options)

    def restart_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Restart the application. Access: admin."""
        self._run(OPS.restart_application, None, {"package": package, "returnpage": returnpage}, request_options)

    def remove_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the application and its data. Access: admin."""
        self._run(OPS.remove_application, None, {"package": package, "returnpage": returnpage}, request_options)

    def get_application_config(self, name: ConfigName, *, request_options: RequestOptions | None = None) -> ConfigValue:
        """Retrieve the value of a config parameter that applies to all ACAP applications.

        Requires AXIS OS 11.2 or later.

        Access: admin.
        """
        return self._run(OPS.get_application_config, None, {"name": name}, request_options)

    def set_application_config(
        self, name: ConfigName, value: bool, *, request_options: RequestOptions | None = None
    ) -> ConfigValue:
        """Set the value of a config parameter that applies to all ACAP applications.

        Requires AXIS OS 11.2 or later.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.set_application_config, None, {"name": name, "value": value}, request_options)

    def remove_license_key(self, package: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a license key. Access: admin."""
        self._run(OPS.remove_license_key, None, {"package": package}, request_options)

    def list_applications(self, *, request_options: RequestOptions | None = None) -> ApplicationList:
        """List information about installed ACAP applications.

        Requires ``Properties.EmbeddedDevelopment.Version`` 1.20 or later.

        Access: admin.
        """
        return self._run(OPS.list_applications, None, {}, request_options)

    def get_info(self, *, request_options: RequestOptions | None = None) -> AcapInfo:
        """Retrieve general information related to ACAP support on the device (supported SDKs).

        Access: admin.
        """
        return self._run(OPS.get_info, None, {}, request_options)

    def upload_application(self, package: UploadSource, *, request_options: RequestOptions | None = None) -> None:
        """Upload and install an ACAP application package (.eap).

        The application is installed but not started. If an application with the same name exists, the
        upload upgrades it: data and parameters are kept, the version is not compared and a running
        application is restarted. A failed or interrupted upgrade removes both versions. Installing a signed
        application needs about twice the size of the package in free RAM.

        Access: admin.
        """
        self._run(OPS.upload_application, None, {"package": package}, request_options)

    def upload_license_key(
        self, package: str, license_key: UploadSource, *, request_options: RequestOptions | None = None
    ) -> None:
        """Upload and install a license key for an application.

        The docs name the action and the package parameter but not how the key file is sent; it is sent as a
        multipart file part named file, as for upload.cgi.

        Access: admin.
        """
        self._run(OPS.upload_license_key, None, {"package": package, "license_key": license_key}, request_options)


class AsyncApplicationApi(AsyncApi):
    """Application API (``application-api``)."""

    INFO = INFO

    async def start_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Start the application. Access: admin."""
        await self._run(OPS.start_application, None, {"package": package, "returnpage": returnpage}, request_options)

    async def stop_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Stop the application. Access: admin."""
        await self._run(OPS.stop_application, None, {"package": package, "returnpage": returnpage}, request_options)

    async def restart_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Restart the application. Access: admin."""
        await self._run(OPS.restart_application, None, {"package": package, "returnpage": returnpage}, request_options)

    async def remove_application(
        self, package: str, *, returnpage: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the application and its data. Access: admin."""
        await self._run(OPS.remove_application, None, {"package": package, "returnpage": returnpage}, request_options)

    async def get_application_config(
        self, name: ConfigName, *, request_options: RequestOptions | None = None
    ) -> ConfigValue:
        """Retrieve the value of a config parameter that applies to all ACAP applications.

        Requires AXIS OS 11.2 or later.

        Access: admin.
        """
        return await self._run(OPS.get_application_config, None, {"name": name}, request_options)

    async def set_application_config(
        self, name: ConfigName, value: bool, *, request_options: RequestOptions | None = None
    ) -> ConfigValue:
        """Set the value of a config parameter that applies to all ACAP applications.

        Requires AXIS OS 11.2 or later.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.set_application_config, None, {"name": name, "value": value}, request_options)

    async def remove_license_key(self, package: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a license key. Access: admin."""
        await self._run(OPS.remove_license_key, None, {"package": package}, request_options)

    async def list_applications(self, *, request_options: RequestOptions | None = None) -> ApplicationList:
        """List information about installed ACAP applications.

        Requires ``Properties.EmbeddedDevelopment.Version`` 1.20 or later.

        Access: admin.
        """
        return await self._run(OPS.list_applications, None, {}, request_options)

    async def get_info(self, *, request_options: RequestOptions | None = None) -> AcapInfo:
        """Retrieve general information related to ACAP support on the device (supported SDKs).

        Access: admin.
        """
        return await self._run(OPS.get_info, None, {}, request_options)

    async def upload_application(self, package: UploadSource, *, request_options: RequestOptions | None = None) -> None:
        """Upload and install an ACAP application package (.eap).

        The application is installed but not started. If an application with the same name exists, the
        upload upgrades it: data and parameters are kept, the version is not compared and a running
        application is restarted. A failed or interrupted upgrade removes both versions. Installing a signed
        application needs about twice the size of the package in free RAM.

        Access: admin.
        """
        await self._run(OPS.upload_application, None, {"package": package}, request_options)

    async def upload_license_key(
        self, package: str, license_key: UploadSource, *, request_options: RequestOptions | None = None
    ) -> None:
        """Upload and install a license key for an application.

        The docs name the action and the package parameter but not how the key file is sent; it is sent as a
        multipart file part named file, as for upload.cgi.

        Access: admin.
        """
        await self._run(OPS.upload_license_key, None, {"package": package, "license_key": license_key}, request_options)
