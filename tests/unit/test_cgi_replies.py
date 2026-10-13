"""CGI reply handling: XML child errors, empty values, int enums as text, text_kv, comment and JSON errors, floats."""

from __future__ import annotations

from typing import Any, Literal

import httpx
import pytest
from pydantic import Field

from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation
from ax_devil_device_api._protocols.cgi import CgiArg, CgiBinding, JsonReply, Text, TextKv, Xml
from ax_devil_device_api._protocols.xmlmap import XmlField, XmlMap, XmlStatusError
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import ApiError

INFO = ApiInfo(id="t", name="T", family=Family.CGI)


def call(op: Operation[Any], body: str, params: Any = None, status: int = 200, sink: list | None = None) -> Any:
    def handler(request: httpx.Request) -> httpx.Response:
        if sink is not None:
            sink.append(request)
        return httpx.Response(status, text=body)

    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler)) as dev:
        return dev.invoke(op, params)


class Item(Model):
    name: str = Field(validation_alias="name")
    level: int | None = None
    on: bool | None = None
    mode: Literal[0, 90, 180] | None = None


class Items(Model):
    items: list[Item] | None = None
    tags: list[str] | None = None
    note: str | None = None


ITEM_MAP = XmlMap(fields=(
    XmlField("name"), XmlField("level"), XmlField("on"), XmlField("mode"),
))
ITEMS_MAP = XmlMap(
    fields=(
        XmlField("items", source="path", name="item", many=True, nested=ITEM_MAP),
        XmlField("tags", source="path", name="tag/@value", many=True),
        XmlField("note"),
    ),
    root="reply",
)


def doc(inner: str, attrs: str = "") -> str:
    return f"<top><reply{attrs}>{inner}</reply></top>"


def xml_op(**kw: Any) -> Operation[CgiBinding]:
    return Operation(INFO, "op", CgiBinding("/x.cgi", reply=Xml(map=ITEMS_MAP, **kw)), result=Items)


def test_status_error_child_element() -> None:
    op = Operation(INFO, "op", CgiBinding("/x.cgi", reply=Xml(status_error=XmlStatusError(value="error"))), result=None)
    body = '<reply result="error"><error type="no_such_application" message="No application"/></reply>'
    with pytest.raises(ApiError) as caught:
        call(op, body)
    assert caught.value.code == "no_such_application"
    assert "No application" in caught.value.message


def test_empty_values_are_absent_for_non_strings() -> None:
    body = doc('<item name="" level="" on="" mode=""/>', ' note=""')
    result = call(xml_op(), body)
    assert result.note == ""
    assert result.items is not None and result.items[0].name == ""
    assert result.items[0].level is None and result.items[0].on is None and result.items[0].mode is None


def test_integer_enum_from_text_and_unknown_value() -> None:
    result = call(xml_op(), doc('<item name="a" level="3" mode="90"/><item name="b" mode="45"/>'))
    assert result.items is not None
    assert (result.items[0].level, result.items[0].mode) == (3, 90)
    assert result.items[1].mode == 45  # newer firmware value of the same type is kept


def test_optional_array_without_elements_is_none() -> None:
    result = call(xml_op(), doc(""))
    assert result.items is None and result.tags is None


def test_scalar_array_from_attribute() -> None:
    result = call(xml_op(), doc('<tag value="a"/><tag value=" b "/><tag/>'))
    assert result.tags == ["a", "b"]


class Kv(Model):
    names: list[str] | None = None
    title: str | None = None
    count: Literal[1, 2] | None = None


def test_text_kv_strip_unquote_and_split_only_arrays() -> None:
    op = Operation(INFO, "op", CgiBinding("/x.cgi", reply=TextKv()), result=Kv)
    result = call(op, 'names = "a, b" \ntitle="x,y"\ncount= 2\n')
    assert result.names == ["a", "b"] and result.title == "x,y" and result.count == 2
    plain = Operation(INFO, "op", CgiBinding("/x.cgi", reply=TextKv()), result=dict[str, str])
    assert call(plain, 'u="root,joe"\nv= 1 ') == {"u": "root,joe", "v": "1"}


@pytest.mark.parametrize("codec", [Text(), TextKv()])
def test_html_comment_is_an_error(codec: Any) -> None:
    op = Operation(INFO, "op", CgiBinding("/x.cgi", reply=codec), result=dict[str, str])
    with pytest.raises(ApiError) as caught:
        call(op, "<!-- Camera 1 not available. -->\n")
    assert caught.value.message == "Camera 1 not available."
    assert call(Operation(INFO, "op", CgiBinding("/x.cgi"), result=str), "a\n<!-- fine -->\n") == "a\n<!-- fine -->\n"


@pytest.mark.parametrize("codec", [JsonReply(), Text()])
def test_json_error_envelope(codec: Any) -> None:
    op = Operation(INFO, "op", CgiBinding("/x.cgi", reply=codec), result=dict[str, Any])
    with pytest.raises(ApiError) as caught:
        call(op, '{"error": {"id": 503, "message": "Unknown index"}}')
    assert (caught.value.code, caught.value.message) == (503, "Unknown index")
    assert call(Operation(INFO, "op", CgiBinding("/x.cgi", reply=JsonReply()), result=dict[str, Any]), '{"error": 1, "x": 2}') == {"error": 1, "x": 2}


def test_empty_bodies() -> None:
    assert call(Operation(INFO, "op", CgiBinding("/x.cgi", reply=JsonReply())), "") is None
    assert call(Operation(INFO, "op", CgiBinding("/x.cgi", reply=Xml())), " \n") is None


class Q(Model):
    pan: float | None = None
    zoom: float | None = None


def test_float_query_minimal_form() -> None:
    op = Operation(INFO, "op", CgiBinding("/x.cgi", args=(CgiArg("pan"), CgiArg("zoom"))), params=Q)
    sink: list[httpx.Request] = []
    call(op, "OK", Q(pan=10.0, zoom=-0.25), sink=sink)
    assert dict(sink[0].url.params.items()) == {"pan": "10", "zoom": "-0.25"}
    call(op, "OK", Q(pan=1e-05, zoom=0.1), sink=sink)
    assert dict(sink[1].url.params.items()) == {"pan": "0.00001", "zoom": "0.1"}


def test_xml_fragment_with_several_top_level_elements_is_wrapped() -> None:
    import xml.etree.ElementTree as ET

    op = Operation(INFO, "op", CgiBinding("/x.cgi", reply=Xml()), result=ET.Element)
    root = call(op, '<?xml version="1.0"?>\n<entry value="a"/>\n<entry value="b"/>')
    assert [e.get("value") for e in root] == ["a", "b"]
    single = call(op, '<entry value="a"/>')
    assert single.tag == "entry"


def test_malformed_xml_still_raises() -> None:
    from ax_devil_device_api.errors import ResponseFormatError

    op = Operation(INFO, "op", CgiBinding("/x.cgi", reply=Xml()), result=None)
    with pytest.raises(ResponseFormatError):
        call(op, "<a><b></a>")
