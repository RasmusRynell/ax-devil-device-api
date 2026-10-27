"""Discovery entries are any-of, so each must identify the API on its own.

A generic platform marker (Package Manager, the Add-on Framework flag, the shared HTTP API version) is true on many
devices that do not have the API. It may therefore be an API's only discovery entry, but never one alternative next to
a more specific entry: it would satisfy discovery by itself.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SPECS = sorted((ROOT / "specs" / "apis").rglob("*.yaml"))

GENERIC_MARKERS = frozenset({
    "Properties.PackageManager.PackageManager",
    "Properties.AddOnFramework.AddOnFramework",
    "Properties.EmbeddedDevelopment.Version",
    "Properties.API.HTTP.Version",
})


def generic_alternatives(discovery: list[dict[str, Any]] | None) -> list[str]:
    """Generic markers listed next to other alternatives (each would make discovery succeed alone)."""
    entries = discovery or []
    if len(entries) < 2:
        return []
    return [e["param"]["name"] for e in entries if "param" in e and e["param"]["name"] in GENERIC_MARKERS]


def test_the_guard_flags_a_generic_marker_next_to_a_specific_one() -> None:
    bad = [
        {"param": {"name": "Properties.PackageManager.PackageManager", "value": "yes"}},
        {"param": {"name": "Properties.AddOnFramework.Version", "value": "1.0", "compare": ">="}},
    ]
    assert generic_alternatives(bad) == ["Properties.PackageManager.PackageManager"]
    assert generic_alternatives(bad[:1]) == []  # alone, there is nothing more specific to prefer
    assert generic_alternatives([{"param": {"name": "Properties.Radar.Radar", "value": "yes"}}, {"api_discovery": "x"}]) == []


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_no_spec_lists_a_generic_marker_as_one_of_several_alternatives(path: Path) -> None:
    data = yaml.safe_load(path.read_text())
    assert generic_alternatives(data.get("discovery")) == [], (
        f"{path.name}: a generic marker satisfies discovery alone; keep the specific entry and note the other "
        "prerequisite in provenance.open_questions"
    )
