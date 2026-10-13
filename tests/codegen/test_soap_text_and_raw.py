"""SOAP: elements with attributes and text (``#text``), and the raw reply element as a result."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx
import pytest
from test_bindings import NS, base_spec, build, device, load_module

from codegen.loader import SpecError

ENV = "http://www.w3.org/2003/05/soap-envelope"

EXPR = {
    "type": "object", "required": ["@Dialect", "#text"],
    "properties": {
        "@Dialect": {"type": "string", "x-python-name": "dialect", "x-xml": {"attribute": "Dialect"}},
        "#text": {"type": "string", "x-python-name": "value", "x-xml": "text"},
    },
}  # fmt: skip

SPEC = base_spec(
    "soap",
    {"namespace": NS, "namespaces": {"wsnt": "http://docs.oasis-open.org/wsn/b-2"}},
    {
        "add_rule": {
            "summary": "Add.", "effect": "write", "binding": {"action": f"{NS}/AddRule", "element": "AddRule"},
            "params": {"type": "object", "required": ["Rule"], "properties": {"Rule": {"$ref": "#/types/Rule"}}},
            "result": {"type": "object", "properties": {"RuleID": {"type": "integer"}}},
        },
        "get_rules": {
            "summary": "Get.", "effect": "read", "binding": {"action": f"{NS}/GetRules", "element": "GetRules"},
            "result": {"type": "object", "properties": {"Rule": {"type": "array", "items": {"$ref": "#/types/Rule"}}}},
        },
        "instances": {
            "summary": "Raw.", "effect": "read", "binding": {"action": f"{NS}/Instances", "element": "Instances"},
            "result": {"x-xml": True},
        },
    },
    types={
        "Expr": EXPR,
        "Rule": {"type": "object", "properties": {"Name": {"type": "string"}, "wsnt:Topic": {"$ref": "#/types/Expr"}}},
    },
)  # fmt: skip


def respond(body: str):
    return lambda request: httpx.Response(200, content=f'<s:Envelope xmlns:s="{ENV}"><s:Body>{body}</s:Body></s:Envelope>')


def test_attributes_and_text_in_one_element() -> None:
    module = load_module(SPEC)
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return respond(f'<AddRuleResponse xmlns="{NS}"><RuleID>7</RuleID></AddRuleResponse>')(request)

    with device(handler) as dev:
        rule = module.Rule(name="r", topic=module.Expr(dialect="urn:d", value="a<b & c"))
        assert dev.api(module.DemoApi).add_rule(rule=rule).rule_id == 7
    sent = seen[0].content.decode()
    assert '<wsnt:Topic Dialect="urn:d">a&lt;b &amp; c</wsnt:Topic>' in sent
    assert sent.index("<Name>") < sent.index("<wsnt:Topic")


def test_attributes_and_text_are_read_back() -> None:
    module = load_module(SPEC)
    reply = (
        f'<GetRulesResponse xmlns="{NS}" xmlns:w="http://docs.oasis-open.org/wsn/b-2"><Rule><Name>x</Name>'
        '<w:Topic Dialect="urn:d"> tns1:A/B </w:Topic></Rule></GetRulesResponse>'
    )
    with device(respond(reply)) as dev:
        (rule,) = dev.api(module.DemoApi).get_rules().rule
    assert rule.topic is not None and (rule.topic.dialect, rule.topic.value) == ("urn:d", "tns1:A/B")


def test_raw_reply_element_is_returned() -> None:
    module = load_module(SPEC)
    reply = f'<InstancesResponse xmlns="{NS}"><TopicSet><tns1:Device xmlns:tns1="urn:t"/></TopicSet></InstancesResponse>'
    with device(respond(reply)) as dev:
        element = dev.api(module.DemoApi).instances()
    assert isinstance(element, ET.Element) and element.tag == f"{{{NS}}}InstancesResponse"
    assert [c.tag for c in element[0]] == ["{urn:t}Device"]


def test_raw_reply_still_raises_faults() -> None:
    module = load_module(SPEC)
    fault = "<Fault><Code><Value>env:Sender</Value></Code><Reason><Text>no</Text></Reason></Fault>"
    from ax_devil_device_api.errors import ApiError

    with device(lambda r: httpx.Response(500, content=f'<s:Envelope xmlns:s="{ENV}"><s:Body>{fault}</s:Body></s:Envelope>')) as dev:
        with pytest.raises(ApiError):
            dev.api(module.DemoApi).instances()


def test_other_non_object_results_are_still_rejected() -> None:
    bad = {"summary": "x", "binding": {"action": "a", "element": "E"}, "result": {"type": "string"}}
    with pytest.raises(SpecError, match="x-xml: true"):
        build(base_spec("soap", {"namespace": NS}, {"go": bad}))
