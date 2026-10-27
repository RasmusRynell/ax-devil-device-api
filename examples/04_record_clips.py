"""Record a short video clip from many cameras straight to disk.

Streaming operations return a managed stream instead of bytes: the body is
written chunk by chunk and the connection is released when the ``with`` block
ends, even on error or Ctrl-C. Streams use their own per-camera slots
(``max_streams``), so a long recording never blocks ordinary calls to the same
camera.

A clip is cut after ``CLIP_BYTES`` bytes (a real service would also watch the
clock). Only complete clips get their final name.

    python 04_record_clips.py 10.20.0.11 10.20.0.12
"""

import os
import sys
from pathlib import Path

from ax_devil_device_api import Device, RequestOptions
from ax_devil_device_api.errors import DeviceError

OUT = Path("clips")
CREDENTIALS = (os.environ["CAM_USER"], os.environ["CAM_PASS"])
CLIP_BYTES = 8 * 1024 * 1024
SLOW = RequestOptions(timeout=120)  # only this call waits longer; the device default stays 10 s


def record(dev: Device) -> Path:
    target = OUT / f"{dev.config.host}.mp4"
    partial = target.with_suffix(".mp4.part")
    with dev.apis.media_stream.get_media_stream(container="mp4", videocodec="h264", request_options=SLOW) as stream:
        print(f"{dev.config.host}: {stream.response.media_type}")
        written = 0
        with partial.open("wb") as f:
            for chunk in stream:  # leaving the loop early closes the connection
                f.write(chunk)
                written += len(chunk)
                if written >= CLIP_BYTES:
                    break
    partial.rename(target)  # only complete clips get the final name
    return target


def main(hosts: list[str]) -> None:
    OUT.mkdir(exist_ok=True)
    for host in hosts:
        with Device(host, credentials=CREDENTIALS) as dev:
            try:
                path = record(dev)
                print(f"{host}: {path} ({path.stat().st_size // 1024} KiB)")
            except DeviceError as e:  # every library error derives from DeviceError
                print(f"{host}: failed: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
