"""Download server reports from many cameras straight to disk.

Server reports can be tens of megabytes. Streaming operations return a
managed stream instead of bytes: the body is written chunk by chunk and the
connection is released when the ``with`` block ends, even on error or
Ctrl-C. Streams use their own per-camera slots, so a long download never
blocks ordinary calls to the same camera.

Status: target. ``system_settings`` is not generated yet; the operation and
its ``mode`` values come from specs/apis/network-video/system-settings.yaml.
"""

import os
import sys
from pathlib import Path

from ax_devil_device_api import Device, RequestOptions
from ax_devil_device_api.errors import DeviceError

OUT = Path("reports")
CREDENTIALS = (os.environ["CAM_USER"], os.environ["CAM_PASS"])
SLOW = RequestOptions(timeout=120)  # only this call waits longer; the device default stays 10 s


def fetch(dev: Device) -> Path:
    target = OUT / f"{dev.config.host}.zip"
    partial = target.with_suffix(".zip.part")
    with dev.apis.system_settings.server_report(mode="zip_with_image", request_options=SLOW) as stream:
        total = stream.response.headers.get("content-length")
        with partial.open("wb") as f:
            for chunk in stream:
                f.write(chunk)
                if total:
                    print(f"\r{dev.config.host}: {f.tell() * 100 // int(total)}%", end="")
    partial.rename(target)  # only complete downloads get the final name
    return target


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for host in sys.argv[1:]:
        with Device(host, credentials=CREDENTIALS) as dev:
            try:
                path = fetch(dev)
                print(f"\r{host}: {path} ({path.stat().st_size // 1024} KiB)")
            except DeviceError as e:  # every library error derives from DeviceError
                print(f"\r{host}: failed: {e}")
