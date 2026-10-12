"""SOAP 1.2 APIs (``POST /vapix/services``).

Request:  Content-Type ``application/soap+xml; charset=utf-8; action="<action>"``
          <Envelope><Body><Element xmlns="<namespace>">...params...</Element></Body></Envelope>
Success:  <Envelope><Body><ResponseElement>...</ResponseElement></Body></Envelope>
Fault:    <Body><Fault><Code><Value/><Subcode><Value/>[<Subcode>..]</Subcode></Code>
                       <Reason><Text/></Reason>[<Detail/>]</Fault></Body>

Faults come with HTTP 400/500, so the body is inspected before the status.
The error code is the subcode value (innermost documented one, else the
innermost), falling back to the code value (``env:Sender``). Reply bodies are
read with the existing XML mapping (``XmlMap``), applied to the first element
inside ``Body``, so ``XmlMap.root`` is relative to that element.

Params become child elements in the request element's namespace, in field
order: scalars as text (``true``/``false`` for booleans), lists as repeated
elements, nested objects as nested elements. A wire key starting with ``@`` is
an attribute of its parent element instead.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from typing import Any
from xml.sax.saxutils import escape, quoteattr

from ..errors import ResponseFormatError
from .._http.types import AuthPolicy, RawBody, Request, Response
from .base import CallFlow, Model, Operation, api_error, check_applicability, http_error, parse_result, register_binding
from .state import DeviceState
from .xmlmap import XmlMap, extract, local

ENVELOPE_NS = "http://www.w3.org/2003/05/soap-envelope"
SERVICES_PATH = "/vapix/services"


@dataclass(frozen=True)
class SoapBinding:
    """Wire binding of one SOAP operation."""

    action: str
    """SOAP action URI, e.g. ``http://www.axis.com/vapix/ws/event1/GetEventInstances``."""
    element: str
    """Local name of the request element, e.g. ``GetEventInstances``."""
    namespace: str
    """Namespace of the request element (and its children), e.g. ``http://www.axis.com/vapix/ws/event1``."""
    reply: XmlMap | None = None
    """How to read the reply element into the result model; ``None`` ignores the reply."""
    path: str = SERVICES_PATH
    auth: AuthPolicy = "required"
    timeout: float | None = None


def _text(value: Any) -> str:
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _render(name: str, value: Any, out: list[str]) -> None:
    attrs: list[str] = []
    children: list[tuple[str, Any]] = []
    text = ""
    if isinstance(value, dict):
        for key, item in value.items():
            if key.startswith("@"):
                attrs.append(f" {key[1:]}={quoteattr(_text(item))}")
            elif isinstance(item, list):
                children.extend((key, entry) for entry in item)
            elif item is not None:
                children.append((key, item))
    elif value is not None:
        text = escape(_text(value))
    out.append(f"<{name}{''.join(attrs)}>")
    out.append(text)
    for key, item in children:
        _render(key, item, out)
    out.append(f"</{name}>")


def build_envelope(binding: SoapBinding, args: dict[str, Any]) -> bytes:
    out = [f'<?xml version="1.0" encoding="utf-8"?><env:Envelope xmlns:env="{ENVELOPE_NS}"><env:Body>']
    element = []
    _render(binding.element, args, element)
    # The request element declares the default namespace, which its children inherit.
    element[0] = element[0].replace(">", f" xmlns={quoteattr(binding.namespace)}>", 1)
    out.extend(element)
    out.append("</env:Body></env:Envelope>")
    return "".join(out).encode("utf-8")


def _child(element: ET.Element | None, name: str) -> ET.Element | None:
    if element is None:
        return None
    return next((c for c in element if local(c.tag) == name), None)


def _value(element: ET.Element | None) -> str | None:
    value = _child(element, "Value")
    return (value.text or "").strip() or None if value is not None else None


def _fault_codes(fault: ET.Element) -> list[str]:
    """Codes from most to least specific: innermost subcode ... outer subcode, code value."""
    code = _child(fault, "Code")
    chain: list[str] = []
    top = _value(code)
    node = _child(code, "Subcode")
    while node is not None:
        value = _value(node)
        if value:
            chain.append(value)
        node = _child(node, "Subcode")
    chain.reverse()
    if top:
        chain.append(top)
    return chain


def _fault_error(op: Operation[SoapBinding], fault: ET.Element, status: int) -> Exception:
    codes = _fault_codes(fault)
    code = next((c for c in codes if op.error_code(c) is not None), codes[0] if codes else None)
    reason = _child(fault, "Reason")
    text = _child(reason, "Text")
    message = (text.text or "").strip() if text is not None else ""
    if not message:
        detail = _child(fault, "Detail")
        message = "".join(detail.itertext()).strip() if detail is not None else ""
    return api_error(
        op, code, message or "SOAP fault", http_status=status, details=ET.tostring(fault, encoding="unicode")
    )


def _decode(op: Operation[SoapBinding], response: Response) -> Any:
    root: ET.Element | None = None
    if response.content:
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            root = None
    body = _child(root, "Body") if root is not None and local(root.tag) == "Envelope" else None
    first = next(iter(body), None) if body is not None else None

    if first is not None and local(first.tag) == "Fault":
        raise _fault_error(op, first, response.status)
    if not 200 <= response.status < 300:
        raise http_error(op, response)
    if root is None or body is None:
        raise ResponseFormatError(op.api.id, op.id, "response is not a SOAP envelope")
    reply = op.binding.reply
    if reply is None:
        return {}
    if first is None:
        raise ResponseFormatError(op.api.id, op.id, "SOAP body is empty")
    return extract(first, reply)


def flow(op: Operation[SoapBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    binding = op.binding
    check_applicability(op, params, None)
    args = params.to_wire() if params is not None else {}
    response = yield Request(
        "POST",
        binding.path,
        body=RawBody(build_envelope(binding, args), f'application/soap+xml; charset=utf-8; action="{binding.action}"'),
        accept="application/soap+xml",
        auth=binding.auth,
        timeout=binding.timeout,
    )
    data = _decode(op, response)
    if op.result is None:
        return None
    return parse_result(op, data)


register_binding(SoapBinding, flow)
