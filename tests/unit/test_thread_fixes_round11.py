"""Carried enum values are scoped to their model; reaping tells a normal close from a failure; sub-codes classify errors."""

from __future__ import annotations

import time
from typing import Literal

import pytest
from pydantic import ValidationError
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, api_error
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.apis import axis_object_analytics as aoa
from ax_devil_device_api.apis.network_settings_api import OPS as NETWORK
from ax_devil_device_api.errors import ApiUnavailable

QUICK = Heartbeat(None)


# -- 1: carried values are keyed by (model, field, value) -----------------------------


def test_carried_value_of_one_model_is_not_accepted_in_a_same_named_field_of_another() -> None:
    current = aoa.Configuration.model_validate(
        {
            "devices": [{"id": 1, "type": "camera", "rotation": 0}],
            "scenarios": [{"id": 1, "name": "s", "type": "motion", "devices": [], "triggers": []}],
        },
        context={"ax_devil_response": True},
    )
    data = current.request_data()
    data["devices"][0]["type"] = "thermal-camera"  # a future Device.type, as a newer firmware could return
    request = aoa.Configuration.from_response_data(data)
    request.revalidated()  # the value is carried where it came from
    assert request.scenarios is not None
    request.scenarios[0].type = "thermal-camera"  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        request.revalidated()


def test_same_field_name_in_two_models_does_not_share_carried_values() -> None:
    class A(Model):
        kind: Literal["x"]

    class B(Model):
        kind: Literal["x"]

    class Both(Model):
        a: A
        b: B

    model = Both.from_response_data({"a": {"kind": "new"}, "b": {"kind": "x"}})
    model.revalidated()
    model.b.kind = "new"  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        model.revalidated()


# -- 2: a queued normal close is not an abnormal end -----------------------------------


def _age_last_frame(dev: Device | AsyncDevice, seconds: float) -> None:
    dev._ledger._tracks[EVENTS.key].last_seen -= seconds  # noqa: SLF001


def test_queued_normal_close_ends_the_session_at_the_close_time() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK):
            _age_last_frame(dev, 3600)  # an idle stream: the last data frame was an hour ago
            camera.sockets[0].close(1000)
            time.sleep(0.3)
            with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None and again.gap.duration < 60  # not an hour of false loss


def test_queued_abnormal_close_keeps_the_last_frame_time() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK):
            _age_last_frame(dev, 3600)
            camera.sockets[0].close(1011)
            time.sleep(0.3)
            with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None and again.gap.duration > 3000


@pytest.mark.anyio
async def test_async_queued_normal_close_ends_the_session_at_the_close_time() -> None:
    import anyio

    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK):
            _age_last_frame(dev, 3600)
            camera.sockets[0].close(1001)
            await anyio.sleep(0.3)
            async with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None and again.gap.duration < 60


@pytest.mark.anyio
async def test_async_queued_abnormal_close_keeps_the_last_frame_time() -> None:
    import anyio

    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK):
            _age_last_frame(dev, 3600)
            camera.sockets[0].close(1011)
            await anyio.sleep(0.3)
            async with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None and again.gap.duration > 3000


# -- 3: details.subCode selects composite error entries -----------------------------------


def test_add_vlan_sub_code_202_is_unavailable() -> None:
    op = NETWORK.add_vlan
    assert (op.error_code(4004, "Invalid parameter(s)", 202) or ErrorCode("")).kind == "unavailable"
    assert (op.error_code(4004, "Invalid parameter(s)", 201) or ErrorCode("")).kind == "invalid_argument"
    error = api_error(
        op, 4004, "Invalid parameter(s)", http_status=200, details={"code": 4004, "details": {"subCode": 202}}
    )
    assert isinstance(error, ApiUnavailable) and error.kind == "unavailable"


def test_sub_code_falls_back_to_the_plain_code_and_reads_both_placements() -> None:
    info = ApiInfo(id="t", name="T", family=Family.JSONRPC)
    op = Operation(
        info,
        "x",
        binding=object(),
        errors={4004: ErrorCode("plain", "invalid_argument"), "4004/subCode 9": ErrorCode("nine", "unavailable")},
    )
    assert api_error(op, 4004, "m", http_status=200, details={"subCode": 9}).kind == "unavailable"
    assert api_error(op, 4004, "m", http_status=200, details={"details": {"subCode": 9}}).kind == "unavailable"
    assert api_error(op, 4004, "m", http_status=200, details=[{"details": {"subCode": 9}}]).kind == "unavailable"
    assert api_error(op, 4004, "m", http_status=200, details={"subCode": 77}).kind == "invalid_argument"
    assert api_error(op, 4004, "m", http_status=200, details="text").kind == "invalid_argument"
