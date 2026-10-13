"""An XML declaration naming an unknown encoding is a ResponseFormatError at every XML parse site."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx
import pytest
from test_cgi_replies import INFO as CGI_INFO
from test_cgi_replies import call as cgi_call
from test_new_protocols import SOAP_OP, Recorder, connect

from ax_devil_device_api._protocols.base import Operation
from ax_devil_device_api._protocols.cgi import CgiBinding, Xml
from ax_devil_device_api._protocols.xmlmap import parse_xml
from ax_devil_device_api.errors import ResponseFormatError
from ax_devil_device_api.testing import MockCamera

BAD = b'<?xml version="1.0" encoding="no-such-codec"?><root/>'


def test_parse_xml_reports_every_malformed_document_as_parse_error() -> None:
    for content in (BAD, b'<?xml version="1.0" encoding="utf-8" standalone="maybe"?><r/>', b"<a>"):
        with pytest.raises(ET.ParseError):
            parse_xml(content)
    assert parse_xml(b"<ok/>").tag == "ok"


def test_soap_reply_with_unknown_encoding_is_a_response_format_error() -> None:
    rec = Recorder(httpx.Response(200, content=BAD))
    with connect(rec) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(SOAP_OP, topic="t", enabled=True, tags=["x"])


def test_cgi_xml_reply_with_unknown_encoding_is_a_response_format_error() -> None:
    op = Operation(CGI_INFO, "op", CgiBinding("/x.cgi", reply=Xml()), result=ET.Element)
    with pytest.raises(ResponseFormatError):
        cgi_call(op, BAD.decode())


def test_discovery_probes_report_unknown_encoding_as_a_probe_error_not_a_crash() -> None:
    camera = MockCamera()
    camera.cgi("/axis-cgi/applications/list.cgi", text=BAD)
    camera.cgi("/vapix/services", text=BAD)
    with camera.device() as dev:
        caps = dev._collect(("applications", "services"))  # noqa: SLF001
    assert caps.applications is None and caps.services is None
    assert "applications" in caps.errors and "services" in caps.errors
    assert all("ResponseFormatError" in caps.errors[k] for k in ("applications", "services"))
