"""Detect and fix configuration drift against a baseline, with a dry-run mode.

Reads the parameter groups the baseline cares about, prints every value that
differs, and (with --apply) writes only the drifted parameters back.

    python 02_parameter_drift.py 10.20.0.17 baseline.json [--apply]
"""

import argparse
import json
import os

from ax_devil_device_api import Device
from ax_devil_device_api.errors import ApiError


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("baseline", help='JSON object, e.g. {"Network.Bonjour.Enabled": "no"}')
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with open(args.baseline) as f:
        baseline: dict[str, str] = json.load(f)

    # List only the top-level groups the baseline touches, in one request.
    groups = sorted({name.split(".", 1)[0] for name in baseline})

    with Device(args.host, credentials=(os.environ["CAM_USER"], os.environ["CAM_PASS"])) as dev:
        params = dev.apis.parameter_management
        current = params.list(groups)

        drift = {name: want for name, want in baseline.items() if current.get(name) != want}
        missing = [name for name in drift if name not in current]

        for name, want in sorted(drift.items()):
            print(f"{name}: {current.get(name, '<missing>')!r} -> {want!r}")
        if missing:
            print(f"warning: {len(missing)} parameter(s) do not exist on this model; skipping them")
            for name in missing:
                del drift[name]

        if args.apply and drift:
            try:
                params.update(drift)
            except ApiError as e:  # param.cgi reports "# Error: ..." with HTTP 200
                raise SystemExit(f"update rejected: {e.message}")
            print(f"applied {len(drift)} change(s)")


if __name__ == "__main__":
    main()
