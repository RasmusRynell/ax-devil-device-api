"""Discovery alternatives are all evaluated; identity refresh invalidates on a different device; the token is fetched
after a stream slot is held."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ax_devil_device_api import Support
from ax_devil_device_api._protocols.base import AcapDiscovery, ApiDiscovery, ApiInfo, Family, ParamDiscovery
from ax_devil_device_api._runtime.capabilities import Advertised, Capabilities, decide_support


def _caps(**kw: Any) -> Capabilities:
    base: dict[str, Any] = {"classic_apis": None, "dca_apis": None, "properties": None, "errors": {}, "observed_at": datetime.now(UTC)}
    return Capabilities(**{**base, **kw})


def _info(*discovery: Any, major: int | None = 1) -> ApiInfo:
    return ApiInfo(id="basic-device-info", name="b", family=Family.JSONRPC, major=major, discovery=discovery)


MARKERS = (ApiDiscovery("basic-device-info"), ParamDiscovery("Properties.API.Basic.Info", "yes"))
GROUP = frozenset({"Properties.API"})


# -- B2 ---------------------------------------------------------------------------------------------------------------------


def test_an_incompatible_classic_version_plus_a_satisfied_property_is_yes() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties={"Properties.API.Basic.Info": "yes"}, property_groups=GROUP)
    result = decide_support(_info(*MARKERS), caps)
    assert result.status is Support.YES and "parameter" in result.reason


def test_the_order_of_the_alternatives_does_not_matter() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties={"Properties.API.Basic.Info": "yes"}, property_groups=GROUP)
    assert decide_support(_info(*reversed(MARKERS)), caps).status is Support.YES


def test_an_incompatible_version_and_every_other_alternative_saying_no_is_no_with_the_version_reason() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties={"Properties.API.Other": "x"}, property_groups=GROUP)
    result = decide_support(_info(*MARKERS), caps)
    assert result.status is Support.NO and "version 2.0" in result.reason


def test_an_incompatible_version_and_an_alternative_that_could_not_be_evaluated_is_unknown() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties=None, errors={"properties": "ReadTimeout: slow"})
    result = decide_support(_info(*MARKERS), caps)
    assert result.status is Support.UNKNOWN and any("slow" in error for error in result.errors)


def test_an_incompatible_version_then_an_installed_application_is_yes() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 applications={"Thing": "1.0"})
    assert decide_support(_info(ApiDiscovery("basic-device-info"), AcapDiscovery("thing")), caps).status is Support.YES


def test_a_fitting_version_is_still_yes_and_a_lone_incompatible_version_is_still_no() -> None:
    fits = _caps(classic_apis={"basic-device-info": "1.0"}, classic_versions={"basic-device-info": Advertised(("1.0",))})
    assert decide_support(_info(ApiDiscovery("basic-device-info")), fits).status is Support.YES
    lone = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))})
    assert decide_support(_info(ApiDiscovery("basic-device-info")), lone).status is Support.NO
