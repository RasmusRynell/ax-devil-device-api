# GENERATED from specs/apis/audio-systems/auto-speaker-test-service-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Calibrate and execute automatic speaker tests (test tones compared with reference values via the built-in microphone).

Docs: https://developer.axis.com/vapix/audio-systems/auto-speaker-test-service-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

SpeakerTestStatus = Literal[
    "OK", "Failed", "Calibrated", "Pending", "Uncalibrated", "DisabledInHardware", "InternalError"
]


class SpeakerTestReport(Model):
    """Test report of the latest speaker test. All fields mandatory."""

    speaker_test_status: SpeakerTestStatus = Field(
        validation_alias="SpeakerTestStatus", serialization_alias="SpeakerTestStatus"
    )
    """The test result."""
    test_timestamp: str = Field(validation_alias="TestTimestamp", serialization_alias="TestTimestamp")
    """The date and time that the test was performed. Empty if no test has been performed."""
    calibration_timestamp: str = Field(
        validation_alias="CalibrationTimestamp", serialization_alias="CalibrationTimestamp"
    )
    """The date and time when the test was calibrated. Empty if the test is not calibrated."""


class GetSpeakerTestReportResult(Model):
    speaker_test_report: SpeakerTestReport = Field(
        validation_alias="SpeakerTestReport", serialization_alias="SpeakerTestReport"
    )
    """The current speaker test report."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/axast"

INFO = ApiInfo(
    id="auto-speaker-test-service-api",
    name="Auto speaker test service API",
    family=Family.SERVICE_JSON,
    discovery=(
        ParamDiscovery("Properties.API.SpeakerTest.AutomaticTest", "yes"),
        ParamDiscovery("Properties.API.SpeakerTest.Version", "1.0"),
    ),
    docs=("https://developer.axis.com/vapix/audio-systems/auto-speaker-test-service-api/",),
)


class OPS:
    calibrate_speaker_test = Operation(
        INFO,
        "calibrate_speaker_test",
        ServiceJsonBinding(PATH, "axast:CalibrateSpeakerTest"),
        access="admin",
        effect="action",
        errors={
            "axast:DisabledInHardware": ErrorCode(
                "Calibration could not be performed because the microphone is disabled in the hardware.", "unavailable"
            ),
            "ter:Failure": ErrorCode(
                "Internal error in the Axis product. Check the logs for more information.", "internal"
            ),
        },
    )
    perform_speaker_test = Operation(
        INFO,
        "perform_speaker_test",
        ServiceJsonBinding(PATH, "axast:PerformSpeakerTest"),
        access="admin",
        effect="action",
        errors={
            "axast:DisabledInHardware": ErrorCode(
                "The speaker test could not be executed because the microphone is disabled in the hardware.",
                "unavailable",
            ),
            "axast:DeviceNotCalibrated": ErrorCode(
                "The speaker test could not be performed because the test is not calibrated. Calibration must be run before the speaker test.",
                "unavailable",
            ),
            "ter:Failure": ErrorCode(
                "Internal error in the Axis product. Check the logs for more information.", "internal"
            ),
        },
    )
    get_speaker_test_report = Operation(
        INFO,
        "get_speaker_test_report",
        ServiceJsonBinding(PATH, "axast:GetSpeakerTestReport"),
        result=GetSpeakerTestReportResult,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class AutoSpeakerTestServiceApi(SyncApi):
    """Auto speaker test service API (``auto-speaker-test-service-api``)."""

    INFO = INFO

    def calibrate_speaker_test(self, *, request_options: RequestOptions | None = None) -> None:
        """Initiate speaker test calibration.

        Calibration starts as soon as possible when the command has been sent. The calibration result is
        available in SpeakerTestStatus in the SpeakerTestReport and the calibration time in
        CalibrationTimestamp.

        Access: admin.
        """
        self._run(OPS.calibrate_speaker_test, None, {}, request_options)

    def perform_speaker_test(self, *, request_options: RequestOptions | None = None) -> None:
        """Initiate a speaker test.

        The speaker test will be executed as soon as possible when the command has been sent. The result is
        available in SpeakerTestReport.

        Access: admin.
        """
        self._run(OPS.perform_speaker_test, None, {}, request_options)

    def get_speaker_test_report(self, *, request_options: RequestOptions | None = None) -> GetSpeakerTestReportResult:
        """Retrieve the speaker test report from the latest speaker test. Access: admin."""
        return self._run(OPS.get_speaker_test_report, None, {}, request_options)


class AsyncAutoSpeakerTestServiceApi(AsyncApi):
    """Auto speaker test service API (``auto-speaker-test-service-api``)."""

    INFO = INFO

    async def calibrate_speaker_test(self, *, request_options: RequestOptions | None = None) -> None:
        """Initiate speaker test calibration.

        Calibration starts as soon as possible when the command has been sent. The calibration result is
        available in SpeakerTestStatus in the SpeakerTestReport and the calibration time in
        CalibrationTimestamp.

        Access: admin.
        """
        await self._run(OPS.calibrate_speaker_test, None, {}, request_options)

    async def perform_speaker_test(self, *, request_options: RequestOptions | None = None) -> None:
        """Initiate a speaker test.

        The speaker test will be executed as soon as possible when the command has been sent. The result is
        available in SpeakerTestReport.

        Access: admin.
        """
        await self._run(OPS.perform_speaker_test, None, {}, request_options)

    async def get_speaker_test_report(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSpeakerTestReportResult:
        """Retrieve the speaker test report from the latest speaker test. Access: admin."""
        return await self._run(OPS.get_speaker_test_report, None, {}, request_options)
