"""Device Configuration (DCA) REST protocol, exercised through the analytics_mqtt API."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from ax_devil_device_api.device import AsyncDevice, Device
from ax_devil_device_api.errors import ApiError, HttpError, NotSupported, ResponseFormatError

ROOT = "/config/rest/analytics-mqtt/v1"


class Recorder:
    """Records requests and answers with one scripted response."""

    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.response

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    def last_body(self) -> Any:
        return json.loads(self.last.content)


def connect(response: httpx.Response) -> tuple[Device, Recorder]:
    handler = Recorder(response)
    dev = Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler))
    return dev, handler


def connect_async(response: httpx.Response) -> tuple[AsyncDevice, Recorder]:
    handler = Recorder(response)
    dev = AsyncDevice("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler))
    return dev, handler


def success(data: Any) -> httpx.Response:
    return httpx.Response(200, json={"status": "success", "data": data})


# ---------------------------------------------------------------------------
# Successful calls


def test_list_publishers_parses_list() -> None:
    dev, handler = connect(
        success(
            [
                {"id": "p1", "data_source_key": "tns1:Foo", "mqtt_topic": "a/b", "qos": 1, "retain": False},
                {"id": "p2", "data_source_key": "tns1:Bar", "mqtt_topic": "c", "use_topic_prefix": True},
            ]
        )
    )
    with dev:
        publishers = dev.apis.analytics_mqtt.list_publishers()

    assert [p.id for p in publishers] == ["p1", "p2"]
    assert publishers[0].qos == 1
    assert publishers[0].retain is False
    assert publishers[1].use_topic_prefix is True
    assert handler.last.method == "GET"
    assert handler.last.url.path == f"{ROOT}/publishers"


def test_list_publishers_ignores_unknown_response_fields() -> None:
    dev, _ = connect(success([{"id": "p1", "data_source_key": "tns1:Foo", "mqtt_topic": "a", "futureField": {"x": 1}}]))
    with dev:
        [publisher] = dev.apis.analytics_mqtt.list_publishers()

    assert publisher.id == "p1"


def test_get_publisher_percent_encodes_path_parameter() -> None:
    dev, handler = connect(success({"id": "a/b c", "data_source_key": "tns1:Foo", "mqtt_topic": "a"}))
    with dev:
        publisher = dev.apis.analytics_mqtt.get_publisher("a/b c")

    assert publisher.id == "a/b c"
    assert handler.last.url.raw_path == f"{ROOT}/publishers/a%2Fb%20c".encode()


def test_add_publisher_sends_data_object_without_unset_fields() -> None:
    dev, handler = connect(httpx.Response(201))
    with dev:
        dev.apis.analytics_mqtt.add_publisher(id="p1", data_source_key="tns1:Foo", mqtt_topic="a/b")

    assert handler.last.method == "POST"
    assert handler.last.url.path == f"{ROOT}/publishers"
    assert handler.last_body() == {"data": {"id": "p1", "data_source_key": "tns1:Foo", "mqtt_topic": "a/b"}}


def test_add_publisher_includes_set_optional_fields() -> None:
    dev, handler = connect(httpx.Response(201))
    with dev:
        dev.apis.analytics_mqtt.add_publisher(id="p1", data_source_key="tns1:Foo", mqtt_topic="a/b", qos=2, retain=True)

    assert handler.last_body() == {
        "data": {"id": "p1", "data_source_key": "tns1:Foo", "mqtt_topic": "a/b", "qos": 2, "retain": True}
    }


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(201),
        httpx.Response(201, content=b""),
        httpx.Response(201, json={"status": "success", "data": None}),
    ],
    ids=["empty-body", "empty-bytes", "success-envelope"],
)
def test_add_publisher_201_is_success(response: httpx.Response) -> None:
    dev, _ = connect(response)
    with dev:
        assert dev.apis.analytics_mqtt.add_publisher(id="p1", data_source_key="tns1:Foo", mqtt_topic="a/b") is None


def test_remove_publisher_204_with_empty_body_returns_none() -> None:
    dev, handler = connect(httpx.Response(204))
    with dev:
        assert dev.apis.analytics_mqtt.remove_publisher("p1") is None

    assert handler.last.method == "DELETE"
    assert handler.last.url.path == f"{ROOT}/publishers/p1"


# ---------------------------------------------------------------------------
# Errors


def test_error_envelope_with_4xx_is_api_error() -> None:
    dev, _ = connect(httpx.Response(400, json={"status": "error", "error": {"code": 2002, "message": "bad topic"}}))
    with dev, pytest.raises(ApiError) as caught:
        dev.apis.analytics_mqtt.list_publishers()

    assert caught.value.code == 2002
    assert caught.value.message == "bad topic"
    assert caught.value.http_status == 400


def test_404_without_json_is_not_supported() -> None:
    dev, _ = connect(httpx.Response(404, text="Not Found"))
    with dev, pytest.raises(NotSupported, match="not found"):
        dev.apis.analytics_mqtt.list_publishers()


def test_500_non_json_is_http_error() -> None:
    dev, _ = connect(httpx.Response(500, text="kaboom"))
    with dev, pytest.raises(HttpError) as caught:
        dev.apis.analytics_mqtt.list_publishers()

    assert caught.value.status == 500


def test_200_non_envelope_json_is_response_format_error() -> None:
    dev, _ = connect(httpx.Response(200, json={"publishers": []}))
    with dev, pytest.raises(ResponseFormatError):
        dev.apis.analytics_mqtt.list_publishers()


# ---------------------------------------------------------------------------
# AsyncDevice


@pytest.mark.anyio
async def test_async_list_publishers_parses_list() -> None:
    dev, handler = connect_async(success([{"id": "p1", "data_source_key": "tns1:Foo", "mqtt_topic": "a/b"}]))
    async with dev:
        [publisher] = await dev.apis.analytics_mqtt.list_publishers()

    assert publisher.id == "p1"
    assert handler.last.url.path == f"{ROOT}/publishers"


@pytest.mark.anyio
async def test_async_error_envelope_with_4xx_is_api_error() -> None:
    dev, _ = connect_async(httpx.Response(400, json={"status": "error", "error": {"code": 2002, "message": "bad"}}))
    async with dev:
        with pytest.raises(ApiError) as caught:
            await dev.apis.analytics_mqtt.list_publishers()

    assert caught.value.http_status == 400


@pytest.mark.anyio
async def test_async_remove_publisher_204_returns_none() -> None:
    dev, _ = connect_async(httpx.Response(204))
    async with dev:
        assert await dev.apis.analytics_mqtt.remove_publisher("p1") is None
