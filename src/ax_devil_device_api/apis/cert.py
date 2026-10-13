# GENERATED from specs/apis/device-configuration/cert-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Generate and install certificates, and fetch, replace and remove installed certificates, CA certificates and keystores.

Docs: https://developer.axis.com/vapix/device-configuration/certificate-management/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, ErrorCode, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Alias = Annotated[str, Field(min_length=1, max_length=128)]
SubjectAltName = Annotated[str, Field(pattern="^(IP|DNS):.+$")]
SanList = list[SubjectAltName]
KeystoreCertifications = list[str]
KeystoreKeyType = Literal["RSA-1024", "RSA-2048", "RSA-3072", "RSA-4096", "EC-P256", "EC-P384", "EC-P521"]
SecurityLevel = Literal["SOFTWARE", "TRUSTED_ENVIRONMENT", "STRONG"]


class CaCertificate(Model):
    """An installed CA certificate (never has a private key)."""

    alias: Alias
    """Identifier for this certificate entry."""
    certificate: str
    """The X.509 certificate in PEM format. Can be replaced with a newer version."""


class Certificate(Model):
    """An installed server or client certificate with its private key. The private key is never returned."""

    alias: Alias
    """Identifier for this certificate entry."""
    certificate: str
    """The X.509 certificate in PEM format. Can be replaced with a freshly signed version for the same private key."""
    keystore: str
    """The keystore this private key is protected by. Can not be changed once the private key has been protected."""


class Keystore(Model):
    """A keystore available for protecting private keys."""

    id: str
    """Keystore identifier."""
    certifications: KeystoreCertifications
    """The security standards of the subsystem that this keystore is certified with."""
    key_types: list[KeystoreKeyType]
    """The key types offered by the keystore."""
    security_level: SecurityLevel
    """The level of protection for private keys that this keystore offers."""


class Settings(Model):
    """Global settings for certificate management."""

    keystore: str
    """The selected keystore. Newly installed or generated private keys are protected in it by default."""


class Cert(Model):
    """The whole API tree."""

    ca_certificates: list[CaCertificate]
    certificates: list[Certificate]
    keystores: list[Keystore]
    settings: Settings


class CreateCertificateRequest(Model):
    """Arguments of ``create_certificate``."""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"key_type", "keystore", "subject_alt_names", "valid_from", "valid_to"}
    )
    alias: Alias
    """Identifier for this certificate."""
    subject: str
    """Subject distinguished name, defined in RFC 4514."""
    key_type: str | None = None
    """The key algorithm and strength that should be used. Default is EC-P256 or the keystore default. RSA keys are RSA-<bitlength>, e.g. RSA-2048; EC keys are EC-P256, EC-P384 or EC-P521. Not all keystores support all key types."""
    keystore: str | None = None
    """The keystore in which this private key should be generated. If not specified, the configured default keystore is used."""
    subject_alt_names: SanList | None = None
    """Subject alternative names."""
    valid_from: int | None = None
    """The validity start date for the certificate. Default value is today. Number of seconds since Unix epoch."""
    valid_to: int | None = None
    """The validity end date for the certificate. Default value is one year from today. Number of seconds since Unix epoch."""


class InstallFromPkcs12Request(Model):
    """Arguments of ``install_from_pkcs12``."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"keystore"})
    __masked__: ClassVar[frozenset[str]] = frozenset({"passphrase", "pkcs12"})
    alias: Alias
    """New identifier for this certificate."""
    pkcs12: str
    """The raw data for the PKCS12 archive, base64-encoded."""
    passphrase: str | None = None
    """The passphrase for the PKCS12 archive."""
    keystore: str | None = None
    """The keystore protecting the private key. The configured default keystore will be used if this parameter is not specified."""


class AddCaCertificateRequest(Model):
    """Arguments of ``add_ca_certificate``."""

    alias: Alias
    """Identifier for this certificate entry."""
    certificate: str
    """The X.509 certificate in PEM format."""


class UpdateCaCertificateRequest(Model):
    """Arguments of ``update_ca_certificate``. The new certificate must be for the same public key."""

    alias: Alias
    certificate: str | None = None
    """The X.509 certificate in PEM format."""


class AddCertificateRequest(Model):
    """Arguments of ``add_certificate``."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"private_key"})
    alias: Alias
    """Identifier for this certificate entry."""
    certificate: str
    """The X.509 certificate in PEM format."""
    private_key: str
    """The private key in PEM format. It can not be extracted again once it is protected."""
    keystore: str | None = None
    """The keystore to protect the private key in. The configured default keystore is used if not specified."""


class UpdateCertificateRequest(Model):
    """Arguments of ``update_certificate``. The private key is kept."""

    alias: Alias
    certificate: str | None = None
    """The X.509 certificate in PEM format, signed for the same private key."""


class GetCsrRequest(Model):
    """Arguments of ``get_csr``. Omitted fields are copied from the existing certificate; an empty value leaves the field out of the request."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"subject", "subject_alt_names"})
    alias: Alias
    subject: str | None = None
    """Optional new subject DN, which if used, will replace the original."""
    subject_alt_names: SanList | None = None
    """Optional new list of alternative names, which if used, will replace the original."""


class CaCertificateAliasRequest(Model):
    alias: Alias


class CertificateAliasRequest(Model):
    alias: Alias


class KeystoreIdRequest(Model):
    id: str
    """Keystore identifier."""


class SetSettingsKeystoreRequest(Model):
    keystore: str
    """The selected keystore. Newly installed or generated private keys are protected in it by default."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/cert/v1"

INFO = ApiInfo(
    id="cert-config",
    name="Certificate Management",
    family=Family.DCA,
    discovery=(DcaDiscovery("cert", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/certificate-management/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Cert, access="viewer", effect="read")
    create_certificate = Operation(
        INFO,
        "create_certificate",
        DcaBinding("POST", f"{ROOT}/create_certificate", body="object"),
        params=CreateCertificateRequest,
        access="admin",
        effect="action",
        errors={
            5: ErrorCode("The key type is not supported by the selected keystore", "invalid_argument"),
            100: ErrorCode("Maintenance is required on the device before the key type can be generated", "unavailable"),
        },
    )
    install_from_pkcs12 = Operation(
        INFO,
        "install_from_pkcs12",
        DcaBinding("POST", f"{ROOT}/install_from_pkcs12", body="object"),
        params=InstallFromPkcs12Request,
        access="admin",
        effect="action",
        errors={
            5: ErrorCode("The private key type is not supported by the selected keystore", "invalid_argument"),
            100: ErrorCode(
                "Maintenance is required on the device before the private key type can be uploaded", "unavailable"
            ),
        },
    )
    list_ca_certificates = Operation(
        INFO,
        "list_ca_certificates",
        DcaBinding("GET", f"{ROOT}/ca_certificates"),
        result=list[CaCertificate],
        access="viewer",
        effect="read",
    )
    get_ca_certificate = Operation(
        INFO,
        "get_ca_certificate",
        DcaBinding("GET", f"{ROOT}/ca_certificates/{{alias}}"),
        params=CaCertificateAliasRequest,
        result=CaCertificate,
        access="viewer",
        effect="read",
    )
    add_ca_certificate = Operation(
        INFO,
        "add_ca_certificate",
        DcaBinding("POST", f"{ROOT}/ca_certificates", body="object"),
        params=AddCaCertificateRequest,
        access="admin",
        effect="write",
        write="create",
    )
    update_ca_certificate = Operation(
        INFO,
        "update_ca_certificate",
        DcaBinding("PATCH", f"{ROOT}/ca_certificates/{{alias}}", body="object"),
        params=UpdateCaCertificateRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_ca_certificate = Operation(
        INFO,
        "remove_ca_certificate",
        DcaBinding("DELETE", f"{ROOT}/ca_certificates/{{alias}}"),
        params=CaCertificateAliasRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    list_certificates = Operation(
        INFO,
        "list_certificates",
        DcaBinding("GET", f"{ROOT}/certificates"),
        result=list[Certificate],
        access="viewer",
        effect="read",
    )
    get_certificate = Operation(
        INFO,
        "get_certificate",
        DcaBinding("GET", f"{ROOT}/certificates/{{alias}}"),
        params=CertificateAliasRequest,
        result=Certificate,
        access="viewer",
        effect="read",
    )
    add_certificate = Operation(
        INFO,
        "add_certificate",
        DcaBinding("POST", f"{ROOT}/certificates", body="object"),
        params=AddCertificateRequest,
        access="admin",
        effect="write",
        write="create",
    )
    update_certificate = Operation(
        INFO,
        "update_certificate",
        DcaBinding("PATCH", f"{ROOT}/certificates/{{alias}}", body="object"),
        params=UpdateCertificateRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_certificate = Operation(
        INFO,
        "remove_certificate",
        DcaBinding("DELETE", f"{ROOT}/certificates/{{alias}}"),
        params=CertificateAliasRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_csr = Operation(
        INFO,
        "get_csr",
        DcaBinding("POST", f"{ROOT}/certificates/{{alias}}/get_csr", body="object"),
        params=GetCsrRequest,
        result=str,
        access="admin",
        effect="action",
    )
    list_keystores = Operation(
        INFO,
        "list_keystores",
        DcaBinding("GET", f"{ROOT}/keystores"),
        result=list[Keystore],
        access="viewer",
        effect="read",
    )
    get_keystore = Operation(
        INFO,
        "get_keystore",
        DcaBinding("GET", f"{ROOT}/keystores/{{id}}"),
        params=KeystoreIdRequest,
        result=Keystore,
        access="viewer",
        effect="read",
    )
    get_settings = Operation(
        INFO, "get_settings", DcaBinding("GET", f"{ROOT}/settings"), result=Settings, access="viewer", effect="read"
    )
    set_settings_keystore = Operation(
        INFO,
        "set_settings_keystore",
        DcaBinding("PATCH", f"{ROOT}/settings/keystore", body="value", body_field="keystore"),
        params=SetSettingsKeystoreRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class CertApi(SyncApi):
    """Certificate Management (``cert-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Cert:
        """All CA certificates, certificates, keystores and settings. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    @overload
    def create_certificate(
        self, request: CreateCertificateRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def create_certificate(
        self,
        /,
        *,
        alias: Alias,
        subject: str,
        key_type: str | None | MISSING = MISSING,
        keystore: str | None | MISSING = MISSING,
        subject_alt_names: SanList | None | MISSING = MISSING,
        valid_from: int | None | MISSING = MISSING,
        valid_to: int | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def create_certificate(
        self,
        request: CreateCertificateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Generate a self-signed certificate with a new private key inside a keystore.

        The private key never leaves the device. Fetch a signing request with ``get_csr`` and replace the
        certificate with ``update_certificate`` to get it signed by a CA.

        Access: admin.
        """
        self._run(OPS.create_certificate, request, kwargs, request_options)

    def install_from_pkcs12(
        self,
        *,
        alias: Alias,
        pkcs12: str,
        passphrase: str | MISSING = MISSING,
        keystore: str | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Install a certificate and private key from a passphrase protected PKCS12 archive.

        Access: admin.
        """
        self._run(
            OPS.install_from_pkcs12,
            None,
            {"alias": alias, "pkcs12": pkcs12, "passphrase": passphrase, "keystore": keystore},
            request_options,
        )

    def list_ca_certificates(self, *, request_options: RequestOptions | None = None) -> list[CaCertificate]:
        """List the installed CA certificates. Access: viewer."""
        return self._run(OPS.list_ca_certificates, None, {}, request_options)

    def get_ca_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> CaCertificate:
        """Get one CA certificate. Access: viewer."""
        return self._run(OPS.get_ca_certificate, None, {"alias": alias}, request_options)

    def add_ca_certificate(
        self, *, alias: Alias, certificate: str, request_options: RequestOptions | None = None
    ) -> None:
        """Install a CA certificate. Access: admin."""
        self._run(OPS.add_ca_certificate, None, {"alias": alias, "certificate": certificate}, request_options)

    def update_ca_certificate(
        self, alias: Alias, *, certificate: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Replace a CA certificate with a newer version for the same public key.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_ca_certificate, None, {"alias": alias, "certificate": certificate}, request_options)

    def remove_ca_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> None:
        """Remove a CA certificate. Access: admin."""
        self._run(OPS.remove_ca_certificate, None, {"alias": alias}, request_options)

    def list_certificates(self, *, request_options: RequestOptions | None = None) -> list[Certificate]:
        """List the installed certificates with private keys. Private keys are never returned.

        Access: viewer.
        """
        return self._run(OPS.list_certificates, None, {}, request_options)

    def get_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> Certificate:
        """Get one certificate with a private key. Access: viewer."""
        return self._run(OPS.get_certificate, None, {"alias": alias}, request_options)

    def add_certificate(
        self,
        *,
        alias: Alias,
        certificate: str,
        private_key: str,
        keystore: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Install a certificate together with its private key. Access: admin."""
        self._run(
            OPS.add_certificate,
            None,
            {"alias": alias, "certificate": certificate, "private_key": private_key, "keystore": keystore},
            request_options,
        )

    def update_certificate(
        self, alias: Alias, *, certificate: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Replace a certificate, keeping its private key.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_certificate, None, {"alias": alias, "certificate": certificate}, request_options)

    def remove_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> None:
        """Remove a certificate and its private key. Access: admin."""
        self._run(OPS.remove_certificate, None, {"alias": alias}, request_options)

    def get_csr(
        self,
        alias: Alias,
        *,
        subject: str | None | MISSING = MISSING,
        subject_alt_names: SanList | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get a PKCS10 certificate signing request in PEM format for an installed certificate.

        Access: admin.
        """
        return self._run(
            OPS.get_csr,
            None,
            {"alias": alias, "subject": subject, "subject_alt_names": subject_alt_names},
            request_options,
        )

    def list_keystores(self, *, request_options: RequestOptions | None = None) -> list[Keystore]:
        """List the keystores available for protecting private keys. Access: viewer."""
        return self._run(OPS.list_keystores, None, {}, request_options)

    def get_keystore(self, id: str, *, request_options: RequestOptions | None = None) -> Keystore:
        """Get one keystore. Access: viewer."""
        return self._run(OPS.get_keystore, None, {"id": id}, request_options)

    def get_settings(self, *, request_options: RequestOptions | None = None) -> Settings:
        """Get the global certificate management settings. Access: viewer."""
        return self._run(OPS.get_settings, None, {}, request_options)

    def set_settings_keystore(self, *, keystore: str, request_options: RequestOptions | None = None) -> None:
        """Select the default keystore for new private keys.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_settings_keystore, None, {"keystore": keystore}, request_options)


class AsyncCertApi(AsyncApi):
    """Certificate Management (``cert-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Cert:
        """All CA certificates, certificates, keystores and settings. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    @overload
    async def create_certificate(
        self, request: CreateCertificateRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def create_certificate(
        self,
        /,
        *,
        alias: Alias,
        subject: str,
        key_type: str | None | MISSING = MISSING,
        keystore: str | None | MISSING = MISSING,
        subject_alt_names: SanList | None | MISSING = MISSING,
        valid_from: int | None | MISSING = MISSING,
        valid_to: int | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def create_certificate(
        self,
        request: CreateCertificateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Generate a self-signed certificate with a new private key inside a keystore.

        The private key never leaves the device. Fetch a signing request with ``get_csr`` and replace the
        certificate with ``update_certificate`` to get it signed by a CA.

        Access: admin.
        """
        await self._run(OPS.create_certificate, request, kwargs, request_options)

    async def install_from_pkcs12(
        self,
        *,
        alias: Alias,
        pkcs12: str,
        passphrase: str | MISSING = MISSING,
        keystore: str | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Install a certificate and private key from a passphrase protected PKCS12 archive.

        Access: admin.
        """
        await self._run(
            OPS.install_from_pkcs12,
            None,
            {"alias": alias, "pkcs12": pkcs12, "passphrase": passphrase, "keystore": keystore},
            request_options,
        )

    async def list_ca_certificates(self, *, request_options: RequestOptions | None = None) -> list[CaCertificate]:
        """List the installed CA certificates. Access: viewer."""
        return await self._run(OPS.list_ca_certificates, None, {}, request_options)

    async def get_ca_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> CaCertificate:
        """Get one CA certificate. Access: viewer."""
        return await self._run(OPS.get_ca_certificate, None, {"alias": alias}, request_options)

    async def add_ca_certificate(
        self, *, alias: Alias, certificate: str, request_options: RequestOptions | None = None
    ) -> None:
        """Install a CA certificate. Access: admin."""
        await self._run(OPS.add_ca_certificate, None, {"alias": alias, "certificate": certificate}, request_options)

    async def update_ca_certificate(
        self, alias: Alias, *, certificate: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Replace a CA certificate with a newer version for the same public key.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_ca_certificate, None, {"alias": alias, "certificate": certificate}, request_options)

    async def remove_ca_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> None:
        """Remove a CA certificate. Access: admin."""
        await self._run(OPS.remove_ca_certificate, None, {"alias": alias}, request_options)

    async def list_certificates(self, *, request_options: RequestOptions | None = None) -> list[Certificate]:
        """List the installed certificates with private keys. Private keys are never returned.

        Access: viewer.
        """
        return await self._run(OPS.list_certificates, None, {}, request_options)

    async def get_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> Certificate:
        """Get one certificate with a private key. Access: viewer."""
        return await self._run(OPS.get_certificate, None, {"alias": alias}, request_options)

    async def add_certificate(
        self,
        *,
        alias: Alias,
        certificate: str,
        private_key: str,
        keystore: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Install a certificate together with its private key. Access: admin."""
        await self._run(
            OPS.add_certificate,
            None,
            {"alias": alias, "certificate": certificate, "private_key": private_key, "keystore": keystore},
            request_options,
        )

    async def update_certificate(
        self, alias: Alias, *, certificate: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Replace a certificate, keeping its private key.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_certificate, None, {"alias": alias, "certificate": certificate}, request_options)

    async def remove_certificate(self, alias: Alias, *, request_options: RequestOptions | None = None) -> None:
        """Remove a certificate and its private key. Access: admin."""
        await self._run(OPS.remove_certificate, None, {"alias": alias}, request_options)

    async def get_csr(
        self,
        alias: Alias,
        *,
        subject: str | None | MISSING = MISSING,
        subject_alt_names: SanList | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get a PKCS10 certificate signing request in PEM format for an installed certificate.

        Access: admin.
        """
        return await self._run(
            OPS.get_csr,
            None,
            {"alias": alias, "subject": subject, "subject_alt_names": subject_alt_names},
            request_options,
        )

    async def list_keystores(self, *, request_options: RequestOptions | None = None) -> list[Keystore]:
        """List the keystores available for protecting private keys. Access: viewer."""
        return await self._run(OPS.list_keystores, None, {}, request_options)

    async def get_keystore(self, id: str, *, request_options: RequestOptions | None = None) -> Keystore:
        """Get one keystore. Access: viewer."""
        return await self._run(OPS.get_keystore, None, {"id": id}, request_options)

    async def get_settings(self, *, request_options: RequestOptions | None = None) -> Settings:
        """Get the global certificate management settings. Access: viewer."""
        return await self._run(OPS.get_settings, None, {}, request_options)

    async def set_settings_keystore(self, *, keystore: str, request_options: RequestOptions | None = None) -> None:
        """Select the default keystore for new private keys.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_settings_keystore, None, {"keystore": keystore}, request_options)
