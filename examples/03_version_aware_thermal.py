"""Set thermal isotherm levels on a mixed fleet with different firmware.

Thermometry API 1.2 added an optional ``min`` level to ``setIsothermLevels``.
The client negotiates the API version once per camera; if ``min`` is set and
the camera only speaks 1.0 or 1.1, the call fails with ``NotSupported``
*before anything is sent*, so the code can fall back cleanly.

Status: target. ``thermometry`` is not generated yet; names and fields come
from specs/apis/network-video/thermometry.yaml. ``supports()`` runs today.
"""

import os

from ax_devil_device_api import Device, Support
from ax_devil_device_api.apis.thermometry import ThermometryApi
from ax_devil_device_api.errors import NotSupported

CREDENTIALS = (os.environ["CAM_USER"], os.environ["CAM_PASS"])


def set_levels(host: str, low: int, middle: int, high: int, floor: int) -> None:
    with Device(host, credentials=CREDENTIALS) as dev:
        support = dev.supports(ThermometryApi)
        if support.status is Support.NO:
            print(f"{host}: not a thermal camera ({support.reason})")
            return
        if support.status is Support.UNKNOWN:
            # Discovery itself failed (timeout, 403, starting up); try anyway and let the call decide.
            print(f"{host}: support unknown, trying anyway: {'; '.join(support.errors)}")

        thermo = dev.apis.thermometry
        caps = thermo.get_configuration_capabilities()
        if not caps.min_temperature + 3 <= high <= caps.max_temperature:
            raise ValueError(f"{host}: high={high} outside the camera's range")

        try:
            thermo.set_isotherm_levels(low=low, middle=middle, high=high, min=floor, render_overlay=True)
        except NotSupported as e:
            # e.reason == "min requires API version 1.2, device speaks 1.1"; e.required == "1.2"
            print(f"{host}: {e.reason}; setting levels without a floor")
            thermo.set_isotherm_levels(low=low, middle=middle, high=high, render_overlay=True)


if __name__ == "__main__":
    for camera in ["10.30.0.5", "10.30.0.6", "10.30.0.7"]:
        set_levels(camera, low=20, middle=45, high=80, floor=5)
