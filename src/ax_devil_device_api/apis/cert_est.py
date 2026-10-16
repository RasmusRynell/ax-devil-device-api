# GENERATED from specs/apis/device-configuration/cert-est-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure EST profiles so the device enrolls and renews certificates automatically.

Docs: https://developer.axis.com/vapix/device-configuration/enrollment-over-secure-transport-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Alias = Annotated[str, Field(min_length=1, max_length=128)]
CertificateList = list[Alias]
CommonName = Annotated[str, Field(min_length=1, max_length=64)]
Service = Literal["WEBSERVER", "NETAUTH", "MQTT", "RTSPS"]
ServiceList = list[Service]
Status = Literal["UNCONNECTED", "CONNECTED", "ENROLLED"]


class Subject(Model):
    """Subject of the CSR that will be sent to the EST server. Uses the default subject settings if left empty."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"cn"})
    cn: CommonName | None = None
    """Common Name"""


SubjectAlternativeName = Annotated[str, Field(pattern="^(IP|DNS):.+$")]
SubjectAltNameList = list[SubjectAlternativeName]


class Profile(Model):
    """EST profiles."""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"ca_certificates", "certificate", "server", "services", "subject", "subject_alternative_names"}
    )
    __read_only__: ClassVar[frozenset[str]] = frozenset({"status"})
    ca_certificates: CertificateList | None = Field(
        default=None, validation_alias="caCertificates", serialization_alias="caCertificates"
    )
    """EST server CA certificates"""
    certificate: Alias | None = None
    """Existing certificate to base CSR on"""
    id: Alias
    """EST profile identifier."""
    server: str | None = None
    """EST server hostname."""
    services: ServiceList | None = None
    """Services to assign enrolled certificate to"""
    status: Status | None = None
    """Status of the setup of the EST profile"""
    subject: Subject | None = None
    """x509 subject of the enrolled certificate"""
    subject_alternative_names: SubjectAltNameList | None = Field(
        default=None, validation_alias="subjectAlternativeNames", serialization_alias="subjectAlternativeNames"
    )
    """Subject alternative names, each prefixed with either "IP:" or "DNS:", e.g. "DNS:example.org\""""


class CertEst(Model):
    """The whole API tree."""

    supported_services: ServiceList = Field(
        validation_alias="supportedServices", serialization_alias="supportedServices"
    )
    """List of the services that can have enrolled certificates assigned to it."""
    profiles: list[Profile] | None = None


class UpdateProfileRequest(Model):
    """Arguments of ``update_profile``."""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"ca_certificates", "certificate", "server", "services", "subject", "subject_alternative_names"}
    )
    id: Alias
    ca_certificates: CertificateList | None = Field(
        default=None, validation_alias="caCertificates", serialization_alias="caCertificates"
    )
    """EST server CA certificates"""
    certificate: Alias | None = None
    """Existing certificate to base CSR on"""
    server: str | None = None
    """EST server hostname."""
    services: ServiceList | None = None
    """Services to assign enrolled certificate to"""
    subject: Subject | None = None
    """x509 subject of the enrolled certificate"""
    subject_alternative_names: SubjectAltNameList | None = Field(
        default=None, validation_alias="subjectAlternativeNames", serialization_alias="subjectAlternativeNames"
    )
    """Subject alternative names, each prefixed with either "IP:" or "DNS:", e.g. "DNS:example.org\""""

    @classmethod
    def from_current(cls, profile: Profile) -> UpdateProfileRequest:
        """A request that rewrites ``profile`` unchanged: copy it, edit fields, send it back."""
        data = profile.request_data()
        return cls.from_response_data(data)


class AddProfileRequest(Model):
    """Arguments of ``add_profile``."""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"ca_certificates", "certificate", "server", "services", "subject", "subject_alternative_names"}
    )
    id: Alias
    """EST profile identifier."""
    server: str | None = None
    """EST server hostname."""
    ca_certificates: CertificateList | None = Field(
        default=None, validation_alias="caCertificates", serialization_alias="caCertificates"
    )
    """EST server CA certificates"""
    certificate: Alias | None = None
    """Existing certificate to base CSR on"""
    subject: Subject | None = None
    """x509 subject of the enrolled certificate"""
    subject_alternative_names: SubjectAltNameList | None = Field(
        default=None, validation_alias="subjectAlternativeNames", serialization_alias="subjectAlternativeNames"
    )
    """Subject alternative names, each prefixed with either "IP:" or "DNS:", e.g. "DNS:example.org\""""
    services: ServiceList | None = None
    """Services to assign enrolled certificate to"""

    @classmethod
    def from_current(cls, profile: Profile) -> AddProfileRequest:
        """A request that rewrites ``profile`` unchanged: copy it, edit fields, send it back."""
        data = profile.request_data()
        return cls.from_response_data(data)


class ProfileIdRequest(Model):
    id: Alias


class SetProfileCaCertificatesRequest(Model):
    id: Alias
    ca_certificates: CertificateList = Field(validation_alias="caCertificates", serialization_alias="caCertificates")
    """EST server CA certificates"""


class SetProfileCertificateRequest(Model):
    id: Alias
    certificate: Alias
    """Existing certificate to base CSR on"""


class SetProfileServerRequest(Model):
    id: Alias
    server: str
    """EST server hostname."""


class SetProfileServicesRequest(Model):
    id: Alias
    services: ServiceList
    """Services to assign enrolled certificate to"""


class SetProfileSubjectRequest(Model):
    id: Alias
    subject: Subject
    """x509 subject of the enrolled certificate"""


class SetProfileSubjectAlternativeNamesRequest(Model):
    id: Alias
    subject_alternative_names: SubjectAltNameList = Field(
        validation_alias="subjectAlternativeNames", serialization_alias="subjectAlternativeNames"
    )
    """Subject alternative names, each prefixed with either "IP:" or "DNS:", e.g. "DNS:example.org\""""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/cert-est/v1"

INFO = ApiInfo(
    id="cert-est-config",
    name="Enrollment over secure transport",
    family=Family.DCA,
    discovery=(DcaDiscovery("cert-est", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/enrollment-over-secure-transport-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=CertEst, access="admin", effect="read")
    get_supported_services = Operation(
        INFO,
        "get_supported_services",
        DcaBinding("GET", f"{ROOT}/supportedServices"),
        result=ServiceList,
        access="viewer",
        effect="read",
    )
    list_profiles = Operation(
        INFO,
        "list_profiles",
        DcaBinding("GET", f"{ROOT}/profiles"),
        result=list[Profile],
        access="admin",
        effect="read",
    )
    get_profile = Operation(
        INFO,
        "get_profile",
        DcaBinding("GET", f"{ROOT}/profiles/{{id}}"),
        params=ProfileIdRequest,
        result=Profile,
        access="admin",
        effect="read",
    )
    update_profile = Operation(
        INFO,
        "update_profile",
        DcaBinding("PATCH", f"{ROOT}/profiles/{{id}}", body="object"),
        params=UpdateProfileRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    add_profile = Operation(
        INFO,
        "add_profile",
        DcaBinding("POST", f"{ROOT}/profiles", body="object"),
        params=AddProfileRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_profile = Operation(
        INFO,
        "remove_profile",
        DcaBinding("DELETE", f"{ROOT}/profiles/{{id}}"),
        params=ProfileIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_profile_ca_certificates = Operation(
        INFO,
        "set_profile_ca_certificates",
        DcaBinding("PATCH", f"{ROOT}/profiles/{{id}}/caCertificates", body="value", body_field="caCertificates"),
        params=SetProfileCaCertificatesRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_profile_certificate = Operation(
        INFO,
        "set_profile_certificate",
        DcaBinding("PATCH", f"{ROOT}/profiles/{{id}}/certificate", body="value", body_field="certificate"),
        params=SetProfileCertificateRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_profile_server = Operation(
        INFO,
        "set_profile_server",
        DcaBinding("PATCH", f"{ROOT}/profiles/{{id}}/server", body="value", body_field="server"),
        params=SetProfileServerRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_profile_services = Operation(
        INFO,
        "set_profile_services",
        DcaBinding("PATCH", f"{ROOT}/profiles/{{id}}/services", body="value", body_field="services"),
        params=SetProfileServicesRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_profile_subject = Operation(
        INFO,
        "set_profile_subject",
        DcaBinding("PATCH", f"{ROOT}/profiles/{{id}}/subject", body="value", body_field="subject"),
        params=SetProfileSubjectRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_profile_subject_alternative_names = Operation(
        INFO,
        "set_profile_subject_alternative_names",
        DcaBinding(
            "PATCH",
            f"{ROOT}/profiles/{{id}}/subjectAlternativeNames",
            body="value",
            body_field="subjectAlternativeNames",
        ),
        params=SetProfileSubjectAlternativeNamesRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class CertEstApi(SyncApi):
    """Enrollment over secure transport (``cert-est-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> CertEst:
        """Supported services and all EST profiles. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_supported_services(self, *, request_options: RequestOptions | None = None) -> ServiceList:
        """Services that can be assigned an enrolled certificate. Access: viewer."""
        return self._run(OPS.get_supported_services, None, {}, request_options)

    def list_profiles(self, *, request_options: RequestOptions | None = None) -> list[Profile]:
        """List the profiles. Access: admin."""
        return self._run(OPS.list_profiles, None, {}, request_options)

    def get_profile(self, id: Alias, *, request_options: RequestOptions | None = None) -> Profile:
        """Get one profile. Access: admin."""
        return self._run(OPS.get_profile, None, {"id": id}, request_options)

    @overload
    def update_profile(
        self, request: UpdateProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_profile(
        self,
        /,
        *,
        id: Alias,
        ca_certificates: CertificateList | None | MISSING = MISSING,
        certificate: Alias | None | MISSING = MISSING,
        server: str | None | MISSING = MISSING,
        services: ServiceList | None | MISSING = MISSING,
        subject: Subject | None | MISSING = MISSING,
        subject_alternative_names: SubjectAltNameList | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_profile(
        self,
        request: UpdateProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a profile. Changes only the fields given. Access: admin."""
        self._run(OPS.update_profile, request, kwargs, request_options)

    @overload
    def add_profile(self, request: AddProfileRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def add_profile(
        self,
        /,
        *,
        id: Alias,
        server: str | None | MISSING = MISSING,
        ca_certificates: CertificateList | None | MISSING = MISSING,
        certificate: Alias | None | MISSING = MISSING,
        subject: Subject | None | MISSING = MISSING,
        subject_alternative_names: SubjectAltNameList | None | MISSING = MISSING,
        services: ServiceList | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_profile(
        self,
        request: AddProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a profile. Access: admin."""
        self._run(OPS.add_profile, request, kwargs, request_options)

    def remove_profile(self, id: Alias, *, request_options: RequestOptions | None = None) -> None:
        """Remove a profile. Access: admin."""
        self._run(OPS.remove_profile, None, {"id": id}, request_options)

    def set_profile_ca_certificates(
        self, id: Alias, *, ca_certificates: CertificateList, request_options: RequestOptions | None = None
    ) -> None:
        """Set the ca certificates of a profile. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_profile_ca_certificates, None, {"id": id, "ca_certificates": ca_certificates}, request_options
        )

    def set_profile_certificate(
        self, id: Alias, *, certificate: Alias, request_options: RequestOptions | None = None
    ) -> None:
        """Set the certificate of a profile. Changes only the fields given. Access: admin."""
        self._run(OPS.set_profile_certificate, None, {"id": id, "certificate": certificate}, request_options)

    def set_profile_server(self, id: Alias, *, server: str, request_options: RequestOptions | None = None) -> None:
        """Set the server of a profile. Changes only the fields given. Access: admin."""
        self._run(OPS.set_profile_server, None, {"id": id, "server": server}, request_options)

    def set_profile_services(
        self, id: Alias, *, services: ServiceList, request_options: RequestOptions | None = None
    ) -> None:
        """Set the services of a profile. Changes only the fields given. Access: admin."""
        self._run(OPS.set_profile_services, None, {"id": id, "services": services}, request_options)

    @overload
    def set_profile_subject(
        self, request: SetProfileSubjectRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_profile_subject(
        self, /, *, id: Alias, subject: Subject, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_profile_subject(
        self,
        request: SetProfileSubjectRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the subject of a profile. Changes only the fields given. Access: admin."""
        self._run(OPS.set_profile_subject, request, kwargs, request_options)

    def set_profile_subject_alternative_names(
        self, id: Alias, *, subject_alternative_names: SubjectAltNameList, request_options: RequestOptions | None = None
    ) -> None:
        """Set the subject alternative names of a profile.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_profile_subject_alternative_names,
            None,
            {"id": id, "subject_alternative_names": subject_alternative_names},
            request_options,
        )


class AsyncCertEstApi(AsyncApi):
    """Enrollment over secure transport (``cert-est-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> CertEst:
        """Supported services and all EST profiles. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_supported_services(self, *, request_options: RequestOptions | None = None) -> ServiceList:
        """Services that can be assigned an enrolled certificate. Access: viewer."""
        return await self._run(OPS.get_supported_services, None, {}, request_options)

    async def list_profiles(self, *, request_options: RequestOptions | None = None) -> list[Profile]:
        """List the profiles. Access: admin."""
        return await self._run(OPS.list_profiles, None, {}, request_options)

    async def get_profile(self, id: Alias, *, request_options: RequestOptions | None = None) -> Profile:
        """Get one profile. Access: admin."""
        return await self._run(OPS.get_profile, None, {"id": id}, request_options)

    @overload
    async def update_profile(
        self, request: UpdateProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_profile(
        self,
        /,
        *,
        id: Alias,
        ca_certificates: CertificateList | None | MISSING = MISSING,
        certificate: Alias | None | MISSING = MISSING,
        server: str | None | MISSING = MISSING,
        services: ServiceList | None | MISSING = MISSING,
        subject: Subject | None | MISSING = MISSING,
        subject_alternative_names: SubjectAltNameList | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_profile(
        self,
        request: UpdateProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a profile. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_profile, request, kwargs, request_options)

    @overload
    async def add_profile(
        self, request: AddProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_profile(
        self,
        /,
        *,
        id: Alias,
        server: str | None | MISSING = MISSING,
        ca_certificates: CertificateList | None | MISSING = MISSING,
        certificate: Alias | None | MISSING = MISSING,
        subject: Subject | None | MISSING = MISSING,
        subject_alternative_names: SubjectAltNameList | None | MISSING = MISSING,
        services: ServiceList | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_profile(
        self,
        request: AddProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a profile. Access: admin."""
        await self._run(OPS.add_profile, request, kwargs, request_options)

    async def remove_profile(self, id: Alias, *, request_options: RequestOptions | None = None) -> None:
        """Remove a profile. Access: admin."""
        await self._run(OPS.remove_profile, None, {"id": id}, request_options)

    async def set_profile_ca_certificates(
        self, id: Alias, *, ca_certificates: CertificateList, request_options: RequestOptions | None = None
    ) -> None:
        """Set the ca certificates of a profile. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_profile_ca_certificates, None, {"id": id, "ca_certificates": ca_certificates}, request_options
        )

    async def set_profile_certificate(
        self, id: Alias, *, certificate: Alias, request_options: RequestOptions | None = None
    ) -> None:
        """Set the certificate of a profile. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_profile_certificate, None, {"id": id, "certificate": certificate}, request_options)

    async def set_profile_server(
        self, id: Alias, *, server: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the server of a profile. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_profile_server, None, {"id": id, "server": server}, request_options)

    async def set_profile_services(
        self, id: Alias, *, services: ServiceList, request_options: RequestOptions | None = None
    ) -> None:
        """Set the services of a profile. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_profile_services, None, {"id": id, "services": services}, request_options)

    @overload
    async def set_profile_subject(
        self, request: SetProfileSubjectRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_profile_subject(
        self, /, *, id: Alias, subject: Subject, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_profile_subject(
        self,
        request: SetProfileSubjectRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the subject of a profile. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_profile_subject, request, kwargs, request_options)

    async def set_profile_subject_alternative_names(
        self, id: Alias, *, subject_alternative_names: SubjectAltNameList, request_options: RequestOptions | None = None
    ) -> None:
        """Set the subject alternative names of a profile.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_profile_subject_alternative_names,
            None,
            {"id": id, "subject_alternative_names": subject_alternative_names},
            request_options,
        )
