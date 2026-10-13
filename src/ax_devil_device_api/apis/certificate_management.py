# GENERATED from specs/apis/network-video/certificate-management.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Create, upload, list and delete client/CA certificates and private keys via SOAP web services (Axis certificates service + ONVIF device service), set the HTTPS certificate and assign a certificate to IEEE 802.1x.

Docs: https://developer.axis.com/vapix/network-video/certificate-management-api/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ServiceDiscovery
from .._protocols.soap import SoapBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class CertificateIds(Model):
    """A list of certificates by Id (acert:Id)."""

    id: list[str] | None = Field(default=None, validation_alias="acert:Id", serialization_alias="acert:Id")


class CertificateData(Model):
    """A payload holder (tt:Data)."""

    data: str = Field(validation_alias="tt:Data", serialization_alias="tt:Data")
    """The payload."""


class CertificateSubject(Model):
    """The certificate subject; empty elements are allowed."""

    c: str | None = Field(default=None, validation_alias="acert:C", serialization_alias="acert:C")
    """Country."""
    st: str | None = Field(default=None, validation_alias="acert:ST", serialization_alias="acert:ST")
    """State or province."""
    l: str | None = Field(default=None, validation_alias="acert:L", serialization_alias="acert:L")
    """Locality."""
    o: str | None = Field(default=None, validation_alias="acert:O", serialization_alias="acert:O")
    """Organization."""
    ou: str | None = Field(default=None, validation_alias="acert:OU", serialization_alias="acert:OU")
    """Organizational unit."""
    cn: str | None = Field(default=None, validation_alias="acert:CN", serialization_alias="acert:CN")
    """Common name."""


class CreateCertificate2Request(Model):
    id: str = Field(validation_alias="acertificates:Id", serialization_alias="acertificates:Id")
    """Certificate ID."""
    subject: CertificateSubject = Field(
        validation_alias="acertificates:Subject", serialization_alias="acertificates:Subject"
    )
    """The certificate subject; empty elements are allowed."""
    valid_not_before: str | None = Field(
        default=None,
        validation_alias="acertificates:ValidNotBefore",
        serialization_alias="acertificates:ValidNotBefore",
    )
    """Start of validity, e.g. 2020-10-16T04:08:32."""
    valid_not_after: str | None = Field(
        default=None, validation_alias="acertificates:ValidNotAfter", serialization_alias="acertificates:ValidNotAfter"
    )
    """End of validity, e.g. 2040-10-16T04:08:32."""


class DeleteCertificatesRequest(Model):
    certificate_id: str = Field(validation_alias="CertificateID", serialization_alias="CertificateID")


class CertificateWithPrivateKey(Model):
    certificate_id: str = Field(validation_alias="tt:CertificateID", serialization_alias="tt:CertificateID")
    certificate: CertificateData | None = Field(
        default=None, validation_alias="tt:Certificate", serialization_alias="tt:Certificate"
    )
    private_key: CertificateData | None = Field(
        default=None, validation_alias="tt:PrivateKey", serialization_alias="tt:PrivateKey"
    )


class LoadCertificateWithPrivateKeyRequest(Model):
    certificate_with_private_key: CertificateWithPrivateKey = Field(
        validation_alias="CertificateWithPrivateKey", serialization_alias="CertificateWithPrivateKey"
    )


class CaCertificate(Model):
    certificate_id: str = Field(validation_alias="tt:CertificateID", serialization_alias="tt:CertificateID")
    certificate: CertificateData | None = Field(
        default=None, validation_alias="tt:Certificate", serialization_alias="tt:Certificate"
    )


class LoadCaCertificatesRequest(Model):
    ca_certificate: CaCertificate = Field(validation_alias="CACertificate", serialization_alias="CACertificate")


class Pkcs12Container(Model):
    id: str = Field(validation_alias="acert:Id", serialization_alias="acert:Id")
    certificate: str = Field(validation_alias="acert:Certificate", serialization_alias="acert:Certificate")
    """The PKCS#12 payload."""
    password: str = Field(validation_alias="acert:Password", serialization_alias="acert:Password")


class LoadPkcs12Request(Model):
    pkcs12: Pkcs12Container = Field(validation_alias="Pkcs12", serialization_alias="Pkcs12")


class ConnectionPolicies(Model):
    """Connection policy per role, e.g. Https. For AXIS OS 7.10 and later the example omits Operator and Viewer."""

    admin: str | None = Field(default=None, validation_alias="aweb:Admin", serialization_alias="aweb:Admin")
    operator: str | None = Field(default=None, validation_alias="aweb:Operator", serialization_alias="aweb:Operator")
    viewer: str | None = Field(default=None, validation_alias="aweb:Viewer", serialization_alias="aweb:Viewer")


class TlsCiphers(Model):
    """The enabled ciphers; the listed ciphers are subject to change with AXIS OS updates."""

    cipher: list[str] | None = Field(default=None, validation_alias="acert:Cipher", serialization_alias="acert:Cipher")


class TlsCertificateSet(Model):
    certificates: CertificateIds | None = Field(
        default=None, validation_alias="acert:Certificates", serialization_alias="acert:Certificates"
    )
    ca_certificates: CertificateIds | None = Field(
        default=None, validation_alias="acert:CACertificates", serialization_alias="acert:CACertificates"
    )
    trusted_certificates: CertificateIds | None = Field(
        default=None, validation_alias="acert:TrustedCertificates", serialization_alias="acert:TrustedCertificates"
    )


class WebServerTlsConfiguration(Model):
    tls: bool = Field(validation_alias="Tls", serialization_alias="Tls")
    connection_policies: ConnectionPolicies | None = Field(
        default=None, validation_alias="aweb:ConnectionPolicies", serialization_alias="aweb:ConnectionPolicies"
    )
    """Connection policy per role, e.g. Https. For AXIS OS 7.10 and later the example omits Operator and Viewer."""
    ciphers: TlsCiphers | None = Field(
        default=None, validation_alias="aweb:Ciphers", serialization_alias="aweb:Ciphers"
    )
    """The enabled ciphers; the listed ciphers are subject to change with AXIS OS updates."""
    certificate_set: TlsCertificateSet | None = Field(
        default=None, validation_alias="aweb:CertificateSet", serialization_alias="aweb:CertificateSet"
    )


class SetWebServerTlsConfigurationRequest(Model):
    configuration: WebServerTlsConfiguration = Field(
        validation_alias="Configuration", serialization_alias="Configuration"
    )


class TlsConfiguration(Model):
    certificate_id: str = Field(validation_alias="tt:CertificateID", serialization_alias="tt:CertificateID")
    """Must be the certificate common name, e.g. Default(self-signed)."""


class EapMethodConfiguration(Model):
    tls_configuration: TlsConfiguration | None = Field(
        default=None, validation_alias="tt:TLSConfiguration", serialization_alias="tt:TLSConfiguration"
    )


class Dot1XConfiguration(Model):
    dot1_x_configuration_token: str = Field(
        validation_alias="tt:Dot1XConfigurationToken", serialization_alias="tt:Dot1XConfigurationToken"
    )
    """e.g. EAPTLS_WIRED"""
    identity: str = Field(validation_alias="tt:Identity", serialization_alias="tt:Identity")
    eap_method: int = Field(validation_alias="tt:EAPMethod", serialization_alias="tt:EAPMethod")
    """e.g. 13 (EAP-TLS)."""
    eap_method_configuration: EapMethodConfiguration | None = Field(
        default=None, validation_alias="tt:EAPMethodConfiguration", serialization_alias="tt:EAPMethodConfiguration"
    )


class SetDot1xConfigurationRequest(Model):
    dot1_x_configuration: Dot1XConfiguration = Field(
        validation_alias="Dot1XConfiguration", serialization_alias="Dot1XConfiguration"
    )


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/services"

INFO = ApiInfo(
    id="certificate-management",
    name="Certificate management API",
    family=Family.SOAP,
    discovery=(ServiceDiscovery("http://www.axis.com/vapix/ws/certificates"),),
    docs=("https://developer.axis.com/vapix/network-video/certificate-management-api/",),
)


class OPS:
    create_certificate2 = Operation(
        INFO,
        "create_certificate2",
        SoapBinding(
            "http://www.axis.com/vapix/ws/certificates/CreateCertificate2",
            "CreateCertificate2",
            "http://www.axis.com/vapix/ws/certificates",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        params=CreateCertificate2Request,
        access="admin",
        effect="write",
        write="create",
    )
    get_client_certificates = Operation(
        INFO,
        "get_client_certificates",
        SoapBinding(
            "http://www.onvif.org/ver10/device/wsdl/GetCertificates",
            "GetCertificates",
            "http://www.onvif.org/ver10/device/wsdl",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        access="admin",
        effect="read",
    )
    get_ca_certificates = Operation(
        INFO,
        "get_ca_certificates",
        SoapBinding(
            "http://www.onvif.org/ver10/device/wsdl/GetCACertificates",
            "GetCACertificates",
            "http://www.onvif.org/ver10/device/wsdl",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        access="admin",
        effect="read",
    )
    delete_certificates = Operation(
        INFO,
        "delete_certificates",
        SoapBinding(
            "http://www.onvif.org/ver10/device/wsdl/DeleteCertificates",
            "DeleteCertificates",
            "http://www.onvif.org/ver10/device/wsdl",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        params=DeleteCertificatesRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    load_certificate_with_private_key = Operation(
        INFO,
        "load_certificate_with_private_key",
        SoapBinding(
            "http://www.onvif.org/ver10/device/wsdl/LoadCertificateWithPrivateKey",
            "LoadCertificateWithPrivateKey",
            "http://www.onvif.org/ver10/device/wsdl",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        params=LoadCertificateWithPrivateKeyRequest,
        access="admin",
        effect="write",
        write="create",
    )
    load_ca_certificates = Operation(
        INFO,
        "load_ca_certificates",
        SoapBinding(
            "http://www.onvif.org/ver10/device/wsdl/LoadCACertificates",
            "LoadCACertificates",
            "http://www.onvif.org/ver10/device/wsdl",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        params=LoadCaCertificatesRequest,
        access="admin",
        effect="write",
        write="create",
    )
    load_pkcs12 = Operation(
        INFO,
        "load_pkcs12",
        SoapBinding(
            "http://www.axis.com/vapix/ws/certificates/LoadPkcs12",
            "LoadPkcs12",
            "http://www.axis.com/vapix/ws/certificates",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        params=LoadPkcs12Request,
        access="admin",
        effect="write",
        write="create",
    )
    set_web_server_tls_configuration = Operation(
        INFO,
        "set_web_server_tls_configuration",
        SoapBinding(
            "http://www.axis.com/vapix/ws/webserver/SetWebServerTlsConfiguration",
            "SetWebServerTlsConfiguration",
            "http://www.axis.com/vapix/ws/webserver",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        params=SetWebServerTlsConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_dot1x_configuration = Operation(
        INFO,
        "set_dot1x_configuration",
        SoapBinding(
            "http://www.onvif.org/ver10/device/wsdl/SetDot1XConfiguration",
            "SetDot1XConfiguration",
            "http://www.onvif.org/ver10/device/wsdl",
            namespaces=(
                ("acertificates", "http://www.axis.com/vapix/ws/certificates"),
                ("acert", "http://www.axis.com/vapix/ws/cert"),
                ("tds", "http://www.onvif.org/ver10/device/wsdl"),
                ("tt", "http://www.onvif.org/ver10/schema"),
                ("aweb", "http://www.axis.com/vapix/ws/webserver"),
            ),
        ),
        params=SetDot1xConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class CertificateManagementApi(SyncApi):
    """Certificate management API (``certificate-management``)."""

    INFO = INFO

    @overload
    def create_certificate2(
        self, request: CreateCertificate2Request, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def create_certificate2(
        self,
        /,
        *,
        id: str,
        subject: CertificateSubject,
        valid_not_before: str | MISSING = MISSING,
        valid_not_after: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def create_certificate2(
        self,
        request: CreateCertificate2Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a self-signed certificate (generated by the device; only for initial configuration, replace it with a CA-signed certificate afterwards).

        Access: admin.
        """
        self._run(OPS.create_certificate2, request, kwargs, request_options)

    def get_client_certificates(self, *, request_options: RequestOptions | None = None) -> None:
        """Return a list of the currently uploaded client certificates (sent to external servers to validate the device).

        Access: admin.
        """
        self._run(OPS.get_client_certificates, None, {}, request_options)

    def get_ca_certificates(self, *, request_options: RequestOptions | None = None) -> None:
        """Return a list of the currently uploaded CA certificates (used by the device to validate external servers).

        Access: admin.
        """
        self._run(OPS.get_ca_certificates, None, {}, request_options)

    def delete_certificates(self, *, certificate_id: str, request_options: RequestOptions | None = None) -> None:
        """Delete either a CA certificate or a client certificate. Access: admin."""
        self._run(OPS.delete_certificates, None, {"certificate_id": certificate_id}, request_options)

    @overload
    def load_certificate_with_private_key(
        self, request: LoadCertificateWithPrivateKeyRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def load_certificate_with_private_key(
        self,
        /,
        *,
        certificate_with_private_key: CertificateWithPrivateKey,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def load_certificate_with_private_key(
        self,
        request: LoadCertificateWithPrivateKeyRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Upload a client certificate where the certificate and corresponding private key are two separate files.

        Access: admin.
        """
        self._run(OPS.load_certificate_with_private_key, request, kwargs, request_options)

    @overload
    def load_ca_certificates(
        self, request: LoadCaCertificatesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def load_ca_certificates(
        self, /, *, ca_certificate: CaCertificate, request_options: RequestOptions | None = None
    ) -> None: ...
    def load_ca_certificates(
        self,
        request: LoadCaCertificatesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Upload a CA certificate. Access: admin."""
        self._run(OPS.load_ca_certificates, request, kwargs, request_options)

    @overload
    def load_pkcs12(self, request: LoadPkcs12Request, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def load_pkcs12(self, /, *, pkcs12: Pkcs12Container, request_options: RequestOptions | None = None) -> None: ...
    def load_pkcs12(
        self,
        request: LoadPkcs12Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Upload a password-protected PKCS#12 container holding both the client certificate and its private key.

        Access: admin.
        """
        self._run(OPS.load_pkcs12, request, kwargs, request_options)

    @overload
    def set_web_server_tls_configuration(
        self, request: SetWebServerTlsConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_web_server_tls_configuration(
        self, /, *, configuration: WebServerTlsConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_web_server_tls_configuration(
        self,
        request: SetWebServerTlsConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Select a previously uploaded client certificate to be used for HTTPS connections (Set HTTPS certificate).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_web_server_tls_configuration, request, kwargs, request_options)

    @overload
    def set_dot1x_configuration(
        self, request: SetDot1xConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_dot1x_configuration(
        self, /, *, dot1_x_configuration: Dot1XConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_dot1x_configuration(
        self,
        request: SetDot1xConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Assign an uploaded certificate to the wired IEEE 802.1x configuration (then configurable with setWired8021XConfiguration).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_dot1x_configuration, request, kwargs, request_options)


class AsyncCertificateManagementApi(AsyncApi):
    """Certificate management API (``certificate-management``)."""

    INFO = INFO

    @overload
    async def create_certificate2(
        self, request: CreateCertificate2Request, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def create_certificate2(
        self,
        /,
        *,
        id: str,
        subject: CertificateSubject,
        valid_not_before: str | MISSING = MISSING,
        valid_not_after: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def create_certificate2(
        self,
        request: CreateCertificate2Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a self-signed certificate (generated by the device; only for initial configuration, replace it with a CA-signed certificate afterwards).

        Access: admin.
        """
        await self._run(OPS.create_certificate2, request, kwargs, request_options)

    async def get_client_certificates(self, *, request_options: RequestOptions | None = None) -> None:
        """Return a list of the currently uploaded client certificates (sent to external servers to validate the device).

        Access: admin.
        """
        await self._run(OPS.get_client_certificates, None, {}, request_options)

    async def get_ca_certificates(self, *, request_options: RequestOptions | None = None) -> None:
        """Return a list of the currently uploaded CA certificates (used by the device to validate external servers).

        Access: admin.
        """
        await self._run(OPS.get_ca_certificates, None, {}, request_options)

    async def delete_certificates(self, *, certificate_id: str, request_options: RequestOptions | None = None) -> None:
        """Delete either a CA certificate or a client certificate. Access: admin."""
        await self._run(OPS.delete_certificates, None, {"certificate_id": certificate_id}, request_options)

    @overload
    async def load_certificate_with_private_key(
        self, request: LoadCertificateWithPrivateKeyRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def load_certificate_with_private_key(
        self,
        /,
        *,
        certificate_with_private_key: CertificateWithPrivateKey,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def load_certificate_with_private_key(
        self,
        request: LoadCertificateWithPrivateKeyRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Upload a client certificate where the certificate and corresponding private key are two separate files.

        Access: admin.
        """
        await self._run(OPS.load_certificate_with_private_key, request, kwargs, request_options)

    @overload
    async def load_ca_certificates(
        self, request: LoadCaCertificatesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def load_ca_certificates(
        self, /, *, ca_certificate: CaCertificate, request_options: RequestOptions | None = None
    ) -> None: ...
    async def load_ca_certificates(
        self,
        request: LoadCaCertificatesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Upload a CA certificate. Access: admin."""
        await self._run(OPS.load_ca_certificates, request, kwargs, request_options)

    @overload
    async def load_pkcs12(
        self, request: LoadPkcs12Request, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def load_pkcs12(
        self, /, *, pkcs12: Pkcs12Container, request_options: RequestOptions | None = None
    ) -> None: ...
    async def load_pkcs12(
        self,
        request: LoadPkcs12Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Upload a password-protected PKCS#12 container holding both the client certificate and its private key.

        Access: admin.
        """
        await self._run(OPS.load_pkcs12, request, kwargs, request_options)

    @overload
    async def set_web_server_tls_configuration(
        self, request: SetWebServerTlsConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_web_server_tls_configuration(
        self, /, *, configuration: WebServerTlsConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_web_server_tls_configuration(
        self,
        request: SetWebServerTlsConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Select a previously uploaded client certificate to be used for HTTPS connections (Set HTTPS certificate).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_web_server_tls_configuration, request, kwargs, request_options)

    @overload
    async def set_dot1x_configuration(
        self, request: SetDot1xConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_dot1x_configuration(
        self, /, *, dot1_x_configuration: Dot1XConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_dot1x_configuration(
        self,
        request: SetDot1xConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Assign an uploaded certificate to the wired IEEE 802.1x configuration (then configurable with setWired8021XConfiguration).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_dot1x_configuration, request, kwargs, request_options)
