"""One error-category rule for every protocol: the HTTP status decides when it fixes a category (401 auth, 403 access
denied, 503 unavailable); otherwise the documented kind does. The code and description are kept either way."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from ax_devil_device_api._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Operation
from ax_devil_device_api._protocols.cgi import CgiBinding, JsonReply
from ax_devil_device_api._protocols.dca import DcaBinding
from ax_devil_device_api._protocols.jsonrpc import FixedVersion, JsonRpcBinding
from ax_devil_device_api._protocols.rest import RestBinding
from ax_devil_device_api._protocols.service_json import ServiceJsonBinding
from ax_devil_device_api._protocols.soap import SoapBinding
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import AccessDenied, ApiError, AuthError, DeviceError, Unavailable

KINDS = ["invalid_argument", "not_found", "access_denied", "unavailable"]
ENV = "http://www.w3.org/2003/05/soap-envelope"


def _errors(code_of: Callable[[int], Any]) -> dict[Any, ErrorCode]:
    return {code_of(n): ErrorCode(f"documented {kind}", kind) for n, kind in enumerate(KINDS, start=7)}  # type: ignore[arg-type]


def _cgi(code: Any, status: int) -> httpx.Response:
    return httpx.Response(status, json={"error": {"id": code, "message": "m"}})


def _jsonrpc(code: Any, status: int) -> httpx.Response:
    return httpx.Response(status, json={"apiVersion": "1.0", "error": {"code": code, "message": "m"}})


def _dca(code: Any, status: int) -> httpx.Response:
    return httpx.Response(status, json={"status": "error", "error": {"code": code, "message": "m"}})


def _service_json(code: Any, status: int) -> httpx.Response:
    return httpx.Response(
        status, json={"Fault": "env:Receiver", "FaultCode": "ter:Action", "FaultSubCode": code, "FaultReason": "r", "FaultMsg": "m"}
    )


def _soap(code: Any, status: int) -> httpx.Response:
    body = (
        f'<env:Envelope xmlns:env="{ENV}"><env:Body><env:Fault><env:Code><env:Value>env:Sender</env:Value>'
        f"<env:Subcode><env:Value>{code}</env:Value></env:Subcode></env:Code>"
        '<env:Reason><env:Text xml:lang="en">m</env:Text></env:Reason></env:Fault></env:Body></env:Envelope>'
    )
    return httpx.Response(status, text=body)


def _numeric(n: int) -> int:
    return n


def _named(n: int) -> str:
    return f"ns:E{n}"


PROTOCOLS: dict[str, tuple[Family, Any, Callable[[Any, int], httpx.Response], Callable[[int], Any]]] = {
    "cgi": (Family.CGI, CgiBinding("/x.cgi", reply=JsonReply()), _cgi, _numeric),
    "jsonrpc": (Family.JSONRPC, JsonRpcBinding("m", "/rpc", negotiation=FixedVersion(ApiVersion(1, 0))), _jsonrpc, _numeric),
    "dca": (Family.DCA, DcaBinding("GET", "/config/x"), _dca, _numeric),
    "service_json": (Family.SERVICE_JSON, ServiceJsonBinding("/vapix/x", "ns:Op"), _service_json, _named),
    "soap": (Family.SOAP, SoapBinding("a", "Act", "urn:x"), _soap, _named),
}


def _invoke(name: str, code: Any, status: int) -> DeviceError:
    family, binding, make, code_of = PROTOCOLS[name]
    info = ApiInfo(id="t", name="T", family=family, major=1 if family is Family.JSONRPC else None, errors=_errors(code_of))
    op = Operation(info, "op", binding=binding, result=dict if family is not Family.SOAP else None)
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(lambda request: make(code, status))) as dev:
        with pytest.raises(DeviceError) as caught:
            dev.invoke(op)
    return caught.value


@pytest.mark.parametrize("protocol", list(PROTOCOLS))
def test_http_status_decides_the_category_whatever_the_documented_kind(protocol: str) -> None:
    code_of = PROTOCOLS[protocol][3]
    for index, documented in enumerate(KINDS, start=7):
        code = code_of(index)
        assert isinstance(_invoke(protocol, code, 401), AuthError), (protocol, documented)
        forbidden = _invoke(protocol, code, 403)
        assert isinstance(forbidden, AccessDenied) and isinstance(forbidden, ApiError), (protocol, documented)
        unavailable = _invoke(protocol, code, 503)
        assert isinstance(unavailable, Unavailable) and isinstance(unavailable, ApiError), (protocol, documented)
        for error in (forbidden, unavailable):  # the API code and description are kept
            assert isinstance(error, ApiError) and error.code == code and error.description == f"documented {documented}"
            assert error.kind == documented


@pytest.mark.parametrize("protocol", list(PROTOCOLS))
def test_a_2xx_envelope_is_categorised_by_its_documented_kind(protocol: str) -> None:
    code_of = PROTOCOLS[protocol][3]
    for index, documented in enumerate(KINDS, start=7):
        error = _invoke(protocol, code_of(index), 200)
        assert isinstance(error, ApiError) and error.kind == documented
        assert isinstance(error, AccessDenied) == (documented == "access_denied")
        assert isinstance(error, Unavailable) == (documented == "unavailable")


def test_rest_statuses_decide_the_category() -> None:
    info = ApiInfo(id="t", name="T", family=Family.REST, errors={409: ErrorCode("Conflict", "invalid_argument")})
    op = Operation(info, "op", binding=RestBinding("GET", "/x"))

    def error_for(status: int) -> DeviceError:
        handler = lambda request: httpx.Response(status, text=json.dumps({"x": 1}))  # noqa: E731
        with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler)) as dev:
            with pytest.raises(DeviceError) as caught:
                dev.invoke(op)
        return caught.value

    assert isinstance(error_for(401), AuthError)
    assert isinstance(error_for(403), AccessDenied)
    assert isinstance(error_for(503), Unavailable)
    conflict = error_for(409)
    assert isinstance(conflict, ApiError) and conflict.kind == "invalid_argument"


def test_jsonrpc_401_with_a_documented_numeric_code_is_an_auth_error() -> None:
    error = _invoke("jsonrpc", 7, 401)  # code 7 is documented as invalid_argument
    assert isinstance(error, AuthError)


def test_a_message_keyed_401_the_spec_documents_stays_an_api_error() -> None:
    from ax_devil_device_api._protocols.base import api_error

    text = "initial admin user must be created first."
    errors: dict[int | str, ErrorCode] = {"first": ErrorCode("No admin yet", "access_denied", message=text)}
    info = ApiInfo(id="t", name="T", family=Family.CGI, errors=errors)
    error = api_error(Operation(info, "op", binding=object()), None, text, http_status=401, details="")
    assert isinstance(error, ApiError) and isinstance(error, AccessDenied)
