"""Review round 3: firmware minimum in supports(), kwargs revalidation, enum tolerance in containers,
session close bookkeeping, and Data Hub / event filter validation."""

from __future__ import annotations

from typing import Any, Literal

import pytest
from pydantic import ValidationError
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device, Support
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, parse_result
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api._runtime.ws_codecs import datahub_setup, events_setup
from ax_devil_device_api.apis.scene_profile import AsyncSceneProfileApi, SceneProfileApi
from ax_devil_device_api.errors import ResponseFormatError, SessionClosed
from ax_devil_device_api.testing import MockCamera

QUICK = Heartbeat(None)
INFO = ApiInfo(id="t", name="T", family=Family.CGI)


# -- #4 requires.firmware -------------------------------------------------------


def test_generated_metadata_carries_the_firmware_minimum() -> None:
    assert SceneProfileApi.INFO.requires_firmware == "6.25"


def _camera(firmware: str) -> MockCamera:
    camera = MockCamera()
    camera.identity(firmware=firmware)
    camera.api_list({})
    camera.cgi("/axis-cgi/param.cgi", text="root.Properties.API.HTTP.Version=3\n")
    return camera


def test_supports_is_no_below_the_firmware_minimum() -> None:
    with _camera("6.20.1").device() as dev:
        result = dev.supports(SceneProfileApi)
    assert result.status is Support.NO and "6.25" in result.reason


@pytest.mark.parametrize("firmware", ["6.25", "6.25.1", "11.11.65", "10.12"])
def test_supports_is_yes_at_or_above_the_minimum(firmware: str) -> None:
    with _camera(firmware).device() as dev:
        assert dev.supports(SceneProfileApi).status is Support.YES


def test_supports_many_honors_the_minimum() -> None:
    with _camera("6.20.1").device() as dev:
        assert dev.supports_many([SceneProfileApi])[SceneProfileApi].status is Support.NO


def test_supports_is_unknown_when_the_firmware_cannot_be_read() -> None:
    camera = MockCamera()
    camera.api_list({})
    camera.cgi("/axis-cgi/param.cgi", text="root.Properties.API.HTTP.Version=3\n")
    with camera.device() as dev:  # no identity route: the request fails
        result = dev.supports(SceneProfileApi)
    assert result.status is Support.UNKNOWN and result.errors


@pytest.mark.anyio
async def test_async_supports_honors_the_minimum() -> None:
    async with _camera("6.20.1").async_device() as dev:
        assert (await dev.supports(AsyncSceneProfileApi)).status is Support.NO


# -- #5 kwargs path revalidates pre-built nested models ---------------------------


class Inner(Model):
    mode: Literal["a", "b"]


class Outer(Model):
    inner: Inner


def test_kwargs_path_revalidates_prebuilt_nested_models() -> None:
    from ax_devil_device_api.apis._base import build_params

    op = Operation(INFO, "set", binding=object(), params=Outer)
    inner = Inner(mode="a")
    inner.mode = "c"  # type: ignore[assignment]  # assignment skips validation
    with pytest.raises(ValidationError):
        build_params(op, None, {"inner": inner})
    assert build_params(op, None, {"inner": Inner(mode="b")}) is not None


def test_kwargs_path_keeps_unknown_values_a_nested_round_trip_carried() -> None:
    from ax_devil_device_api.apis._base import build_params

    op = Operation(INFO, "set", binding=object(), params=Outer)
    inner = Inner.from_response_data({"mode": "newer"})
    assert build_params(op, None, {"inner": inner}) is not None


# -- #6 unknown enum values are scoped to (field, value) --------------------------


def test_carried_unknown_value_is_not_accepted_in_another_field() -> None:
    class Cfg(Model):
        topic_prefix: Literal["a", "b"] | None = None
        retain: Literal["x", "y"] | None = None

    model = Cfg.from_response_data({"topic_prefix": "vendor"})
    model.revalidated()
    model.retain = "vendor"  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        model.revalidated()


# -- #12 unknown enum values inside mappings, lists and unions of results -----------


def _op(result: Any) -> Operation[Any]:
    return Operation(INFO, "get", binding=object(), result=result)


def test_mapping_result_keeps_unknown_enum_values() -> None:
    assert parse_result(_op(dict[str, Literal["input", "output"]]), {"1": "input", "2": "bidirectional"}) == {
        "1": "input", "2": "bidirectional",
    }


def test_nested_container_and_union_results_keep_unknown_enum_values() -> None:
    state = Literal["open", "closed"]
    assert parse_result(_op(dict[str, list[state]]), {"a": ["open", "ajar"]}) == {"a": ["open", "ajar"]}
    assert parse_result(_op(list[dict[str, state]]), [{"a": "ajar"}]) == [{"a": "ajar"}]
    assert parse_result(_op(dict[str, state] | None), {"a": "ajar"}) == {"a": "ajar"}
    assert parse_result(_op(dict[str, state | None]), {"a": None, "b": "ajar"}) == {"a": None, "b": "ajar"}


def test_mapping_result_still_rejects_other_types() -> None:
    with pytest.raises(ResponseFormatError):
        parse_result(_op(dict[str, Literal["a", "b"]]), {"1": 5})
    with pytest.raises(ResponseFormatError):
        parse_result(_op(dict[str, Literal["a", "b"]]), {"1": None})


def test_model_field_mapping_keeps_unknown_enum_values_in_responses_only() -> None:
    class Ports(Model):
        states: dict[str, Literal["input", "output"]]

    parsed = parse_result(_op(Ports), {"states": {"1": "input", "2": "bidirectional"}})
    assert parsed.states == {"1": "input", "2": "bidirectional"}
    with pytest.raises(ValidationError):
        Ports(states={"1": "bidirectional"})  # type: ignore[arg-type]


def test_round_trip_carries_unknown_values_inside_a_mapping_field() -> None:
    class Ports(Model):
        states: dict[str, Literal["input", "output"]]

    model = Ports.from_response_data({"states": {"1": "bidirectional"}})
    assert model.revalidated().states == {"1": "bidirectional"}
    model.states["2"] = "other"  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        model.revalidated()


# -- #11 Session.close() ends gap tracking ----------------------------------------


def test_close_ends_gap_tracking_for_the_session() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as first:
            first.close()
            assert dev._ledger._tracks[EVENTS.key].active == 0  # noqa: SLF001
            with dev.connect_session(EVENTS, heartbeat=QUICK) as second:
                assert second.gap is not None  # the closed session no longer counts as open


@pytest.mark.anyio
async def test_async_close_ends_gap_tracking_for_the_session() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as first:
            await first.close()
            assert dev._ledger._tracks[EVENTS.key].active == 0  # noqa: SLF001


def test_a_device_side_close_ends_gap_tracking() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close()
            with pytest.raises(SessionClosed):
                session.receive(timeout=3)
            assert dev._ledger._tracks[EVENTS.key].active == 0  # noqa: SLF001


# -- #13 subscription and filter mappings are validated -----------------------------


@pytest.mark.parametrize(
    "bad",
    [
        {"filters": []},
        {"subscriptionId": "s", "filters": [{"topics": ["t"]}], "startFrom": {"position": "sideways"}},
        {"filters": [{"topics": []}]},
        {"filters": [{"topics": ["t"], "bogus": 1}]},
        {"subscriptionId": "s"},
    ],
)
def test_malformed_subscription_mappings_fail_locally(bad: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        datahub_setup({"subscriptions": [bad]})


def test_valid_subscription_is_serialized_with_wire_names() -> None:
    [(method, params)] = datahub_setup(
        {
            "subscriptions": [
                {
                    "subscription_id": "s",
                    "filters": [{"topics": ["t"], "instance_filter": [{"a": "b"}]}],
                    "start_from": {"position": "oldest"},
                }
            ]
        }
    )
    assert method == "data-hub_v1:subscribe"
    assert params == {
        "subscriptionId": "s",
        "filters": [{"topics": ["t"], "instanceFilter": [{"a": "b"}]}],
        "startFrom": {"position": "oldest"},
    }


def test_subscription_model_edits_are_revalidated() -> None:
    from ax_devil_device_api.apis.device_data_hub_ws import Subscription

    sub = Subscription(filters=[{"topics": ["t"]}])  # type: ignore[list-item]
    sub.filters.clear()
    with pytest.raises(ValidationError):
        datahub_setup({"subscriptions": [sub]})


def test_subscriptions_must_be_a_sequence() -> None:
    with pytest.raises(TypeError):
        datahub_setup({"subscriptions": {"filters": []}})


@pytest.mark.parametrize("bad", [{}, {"topicFilter": 5}, {"topicFilter": "t", "extra": "x"}, {"contentFilter": None}])
def test_malformed_event_filter_mappings_fail_locally(bad: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        events_setup({"event_filter_list": [bad]})


def test_valid_event_filter_mapping_is_sent() -> None:
    assert events_setup({"event_filter_list": [{"topicFilter": "t"}]}) == [
        ("events:configure", {"eventFilterList": [{"topicFilter": "t"}]})
    ]
