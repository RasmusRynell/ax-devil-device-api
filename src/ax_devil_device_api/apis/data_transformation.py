# GENERATED from specs/apis/device-configuration/data-transformation-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Transform JSON data of Device Data Hub topics with jq expressions, and read the runtime statistics of each transform.

Docs: https://developer.axis.com/vapix/device-configuration/data-transformation/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Topic = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^([a-zA-Z0-9_-]+)(\.[a-zA-Z0-9_-]+)*$")]
Version = Annotated[str, Field(min_length=1, max_length=32, pattern=r"^\d+\.\d+(\.\d+)?(\-(alpha|beta)\.\d+)?$")]
JqExpression = Annotated[str, Field(min_length=1, max_length=20480)]


class Statistics(Model):
    """Runtime statistics for a transform. Reset when the transform is modified or the device restarts."""

    avg_msg_processing_time_ns: int | None = Field(
        default=None, validation_alias="avgMsgProcessingTimeNs", serialization_alias="avgMsgProcessingTimeNs"
    )
    """Average processing time over the last 30 messages, in nanoseconds."""
    max_msg_processing_time_ns: int | None = Field(
        default=None, validation_alias="maxMsgProcessingTimeNs", serialization_alias="maxMsgProcessingTimeNs"
    )
    """Maximum processing time over the last 30 messages, in nanoseconds."""
    avg_msgs_per_sec: float | None = Field(
        default=None, validation_alias="avgMsgsPerSec", serialization_alias="avgMsgsPerSec"
    )
    """Average number of input messages per second over the last 30 messages."""
    msg_in_count: int | None = Field(default=None, validation_alias="msgInCount", serialization_alias="msgInCount")
    """Total number of input messages."""
    msg_out_count: int | None = Field(default=None, validation_alias="msgOutCount", serialization_alias="msgOutCount")
    """Total number of output messages (errors do not count)."""
    msg_dropped_count: int | None = Field(
        default=None, validation_alias="msgDroppedCount", serialization_alias="msgDroppedCount"
    )
    """Number of dropped messages."""
    byte_in_count: int | None = Field(default=None, validation_alias="byteInCount", serialization_alias="byteInCount")
    """Total number of bytes received."""
    byte_out_count: int | None = Field(
        default=None, validation_alias="byteOutCount", serialization_alias="byteOutCount"
    )
    """Total number of bytes sent after jq processing."""
    jq_transformation_err_count: int | None = Field(
        default=None, validation_alias="jqTransformationErrCount", serialization_alias="jqTransformationErrCount"
    )
    """Number of jq transformation errors."""
    publish_err_count: int | None = Field(
        default=None, validation_alias="publishErrCount", serialization_alias="publishErrCount"
    )
    """Number of failed Device Data Hub publications (for example a missing key field)."""
    last_err_msg: str | None = Field(default=None, validation_alias="lastErrMsg", serialization_alias="lastErrMsg")
    """Last error message when failing to transform or send a message."""


class TopicInfo(Model):
    """A Device Data Hub topic."""

    topic_name: Topic = Field(validation_alias="topicName", serialization_alias="topicName")
    description: str | None = None
    """Topic description."""
    version: str | None = None
    """Topic version."""
    keys: list[str] | None = None
    """Topic key paths."""


class AvailableTopics(Model):
    """Topics that can be used as an input."""

    topics: list[TopicInfo]


class Transform(Model):
    """A configured transform from an input topic to an output topic."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"statistics"})
    input_topic: Topic = Field(validation_alias="inputTopic", serialization_alias="inputTopic")
    jq_expression: JqExpression = Field(validation_alias="jqExpression", serialization_alias="jqExpression")
    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")
    output_topic_description: str | None = Field(
        default=None, validation_alias="outputTopicDescription", serialization_alias="outputTopicDescription"
    )
    """Output topic description. Defaults to a text naming the input topic and its version."""
    output_topic_version: Version | None = Field(
        default=None, validation_alias="outputTopicVersion", serialization_alias="outputTopicVersion"
    )
    statistics: Statistics | None = None


class DataTransformation(Model):
    """The whole API tree."""

    available_topics: AvailableTopics | None = Field(
        default=None, validation_alias="availableTopics", serialization_alias="availableTopics"
    )
    transforms: list[Transform] | None = None


class AddTransformRequest(Model):
    """Arguments of ``add_transform``."""

    input_topic: Topic = Field(validation_alias="inputTopic", serialization_alias="inputTopic")
    jq_expression: JqExpression = Field(validation_alias="jqExpression", serialization_alias="jqExpression")
    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")
    output_topic_description: str | None = Field(
        default=None, validation_alias="outputTopicDescription", serialization_alias="outputTopicDescription"
    )
    """Output topic description. Defaults to a text naming the input topic and its version."""
    output_topic_version: Version | None = Field(
        default=None, validation_alias="outputTopicVersion", serialization_alias="outputTopicVersion"
    )

    @classmethod
    def from_current(cls, transform: Transform) -> AddTransformRequest:
        """A request that rewrites ``transform`` unchanged: copy it, edit fields, send it back."""
        data = transform.request_data()
        return cls.from_response_data(data)


class UpdateTransformRequest(Model):
    """Arguments of ``update_transform``. The output topic identifies the transform and cannot be changed."""

    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")
    input_topic: Topic | None = Field(default=None, validation_alias="inputTopic", serialization_alias="inputTopic")
    jq_expression: JqExpression | None = Field(
        default=None, validation_alias="jqExpression", serialization_alias="jqExpression"
    )
    output_topic_description: str | None = Field(
        default=None, validation_alias="outputTopicDescription", serialization_alias="outputTopicDescription"
    )
    output_topic_version: Version | None = Field(
        default=None, validation_alias="outputTopicVersion", serialization_alias="outputTopicVersion"
    )


class TransformOutputTopicRequest(Model):
    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")


class SetTransformInputTopicRequest(Model):
    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")
    input_topic: Topic = Field(validation_alias="inputTopic", serialization_alias="inputTopic")


class SetTransformJqExpressionRequest(Model):
    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")
    jq_expression: JqExpression = Field(validation_alias="jqExpression", serialization_alias="jqExpression")


class SetTransformOutputTopicDescriptionRequest(Model):
    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")
    output_topic_description: str = Field(
        validation_alias="outputTopicDescription", serialization_alias="outputTopicDescription"
    )


class SetTransformOutputTopicVersionRequest(Model):
    output_topic: Topic = Field(validation_alias="outputTopic", serialization_alias="outputTopic")
    output_topic_version: Version = Field(
        validation_alias="outputTopicVersion", serialization_alias="outputTopicVersion"
    )


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/data-transformation/v1"

INFO = ApiInfo(
    id="data-transformation-config",
    name="Data transformation API",
    family=Family.DCA,
    discovery=(DcaDiscovery("data-transformation", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/data-transformation/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=DataTransformation, access="admin", effect="read"
    )
    get_available_topics = Operation(
        INFO,
        "get_available_topics",
        DcaBinding("GET", f"{ROOT}/availableTopics"),
        result=AvailableTopics,
        access="admin",
        effect="read",
    )
    list_transforms = Operation(
        INFO,
        "list_transforms",
        DcaBinding("GET", f"{ROOT}/transforms"),
        result=list[Transform],
        access="admin",
        effect="read",
    )
    get_transform = Operation(
        INFO,
        "get_transform",
        DcaBinding("GET", f"{ROOT}/transforms/{{outputTopic}}", key_styles=(("outputTopic", "dots_to_slashes"),)),
        params=TransformOutputTopicRequest,
        result=Transform,
        access="admin",
        effect="read",
    )
    get_transform_statistics = Operation(
        INFO,
        "get_transform_statistics",
        DcaBinding(
            "GET", f"{ROOT}/transforms/{{outputTopic}}/statistics", key_styles=(("outputTopic", "dots_to_slashes"),)
        ),
        params=TransformOutputTopicRequest,
        result=Statistics,
        access="operator",
        effect="read",
    )
    add_transform = Operation(
        INFO,
        "add_transform",
        DcaBinding("POST", f"{ROOT}/transforms", body="object"),
        params=AddTransformRequest,
        access="admin",
        effect="write",
        write="create",
    )
    update_transform = Operation(
        INFO,
        "update_transform",
        DcaBinding(
            "PATCH",
            f"{ROOT}/transforms/{{outputTopic}}",
            body="object",
            key_styles=(("outputTopic", "dots_to_slashes"),),
        ),
        params=UpdateTransformRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_transform = Operation(
        INFO,
        "remove_transform",
        DcaBinding("DELETE", f"{ROOT}/transforms/{{outputTopic}}", key_styles=(("outputTopic", "dots_to_slashes"),)),
        params=TransformOutputTopicRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_transform_input_topic = Operation(
        INFO,
        "set_transform_input_topic",
        DcaBinding(
            "PATCH",
            f"{ROOT}/transforms/{{outputTopic}}/inputTopic",
            body="value",
            body_field="inputTopic",
            key_styles=(("outputTopic", "dots_to_slashes"),),
        ),
        params=SetTransformInputTopicRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_transform_jq_expression = Operation(
        INFO,
        "set_transform_jq_expression",
        DcaBinding(
            "PATCH",
            f"{ROOT}/transforms/{{outputTopic}}/jqExpression",
            body="value",
            body_field="jqExpression",
            key_styles=(("outputTopic", "dots_to_slashes"),),
        ),
        params=SetTransformJqExpressionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_transform_output_topic_description = Operation(
        INFO,
        "set_transform_output_topic_description",
        DcaBinding(
            "PATCH",
            f"{ROOT}/transforms/{{outputTopic}}/outputTopicDescription",
            body="value",
            body_field="outputTopicDescription",
            key_styles=(("outputTopic", "dots_to_slashes"),),
        ),
        params=SetTransformOutputTopicDescriptionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_transform_output_topic_version = Operation(
        INFO,
        "set_transform_output_topic_version",
        DcaBinding(
            "PATCH",
            f"{ROOT}/transforms/{{outputTopic}}/outputTopicVersion",
            body="value",
            body_field="outputTopicVersion",
            key_styles=(("outputTopic", "dots_to_slashes"),),
        ),
        params=SetTransformOutputTopicVersionRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class DataTransformationApi(SyncApi):
    """Data transformation API (``data-transformation-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> DataTransformation:
        """The whole API tree. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_available_topics(self, *, request_options: RequestOptions | None = None) -> AvailableTopics:
        """Topics that can be used as transform inputs.

        Other topics can appear at any time, so a transform can also be set up for an input topic that does
        not exist yet.

        Access: admin.
        """
        return self._run(OPS.get_available_topics, None, {}, request_options)

    def list_transforms(self, *, request_options: RequestOptions | None = None) -> list[Transform]:
        """List the configured transforms. Access: admin."""
        return self._run(OPS.list_transforms, None, {}, request_options)

    def get_transform(self, output_topic: Topic, *, request_options: RequestOptions | None = None) -> Transform:
        """Get one transform. Access: admin."""
        return self._run(OPS.get_transform, None, {"output_topic": output_topic}, request_options)

    def get_transform_statistics(
        self, output_topic: Topic, *, request_options: RequestOptions | None = None
    ) -> Statistics:
        """Runtime statistics of one transform. Access: operator."""
        return self._run(OPS.get_transform_statistics, None, {"output_topic": output_topic}, request_options)

    @overload
    def add_transform(
        self, request: AddTransformRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_transform(
        self,
        /,
        *,
        input_topic: Topic,
        jq_expression: JqExpression,
        output_topic: Topic,
        output_topic_description: str | MISSING = MISSING,
        output_topic_version: Version | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_transform(
        self,
        request: AddTransformRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a transform.

        The output topic must start with ``com.axis.dt.``.

        Access: admin.
        """
        self._run(OPS.add_transform, request, kwargs, request_options)

    @overload
    def update_transform(
        self, request: UpdateTransformRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_transform(
        self,
        /,
        *,
        output_topic: Topic,
        input_topic: Topic | MISSING = MISSING,
        jq_expression: JqExpression | MISSING = MISSING,
        output_topic_description: str | MISSING = MISSING,
        output_topic_version: Version | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_transform(
        self,
        request: UpdateTransformRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the settings of a transform.

        Only the given settings change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_transform, request, kwargs, request_options)

    def remove_transform(self, output_topic: Topic, *, request_options: RequestOptions | None = None) -> None:
        """Remove a transform. Access: admin."""
        self._run(OPS.remove_transform, None, {"output_topic": output_topic}, request_options)

    def set_transform_input_topic(
        self, output_topic: Topic, *, input_topic: Topic, request_options: RequestOptions | None = None
    ) -> None:
        """Set the input topic of a transform. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_transform_input_topic,
            None,
            {"output_topic": output_topic, "input_topic": input_topic},
            request_options,
        )

    def set_transform_jq_expression(
        self, output_topic: Topic, *, jq_expression: JqExpression, request_options: RequestOptions | None = None
    ) -> None:
        """Set the jq expression of a transform. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_transform_jq_expression,
            None,
            {"output_topic": output_topic, "jq_expression": jq_expression},
            request_options,
        )

    def set_transform_output_topic_description(
        self, output_topic: Topic, *, output_topic_description: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the output topic description of a transform.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_transform_output_topic_description,
            None,
            {"output_topic": output_topic, "output_topic_description": output_topic_description},
            request_options,
        )

    def set_transform_output_topic_version(
        self, output_topic: Topic, *, output_topic_version: Version, request_options: RequestOptions | None = None
    ) -> None:
        """Set the output topic version of a transform. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_transform_output_topic_version,
            None,
            {"output_topic": output_topic, "output_topic_version": output_topic_version},
            request_options,
        )


class AsyncDataTransformationApi(AsyncApi):
    """Data transformation API (``data-transformation-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> DataTransformation:
        """The whole API tree. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_available_topics(self, *, request_options: RequestOptions | None = None) -> AvailableTopics:
        """Topics that can be used as transform inputs.

        Other topics can appear at any time, so a transform can also be set up for an input topic that does
        not exist yet.

        Access: admin.
        """
        return await self._run(OPS.get_available_topics, None, {}, request_options)

    async def list_transforms(self, *, request_options: RequestOptions | None = None) -> list[Transform]:
        """List the configured transforms. Access: admin."""
        return await self._run(OPS.list_transforms, None, {}, request_options)

    async def get_transform(self, output_topic: Topic, *, request_options: RequestOptions | None = None) -> Transform:
        """Get one transform. Access: admin."""
        return await self._run(OPS.get_transform, None, {"output_topic": output_topic}, request_options)

    async def get_transform_statistics(
        self, output_topic: Topic, *, request_options: RequestOptions | None = None
    ) -> Statistics:
        """Runtime statistics of one transform. Access: operator."""
        return await self._run(OPS.get_transform_statistics, None, {"output_topic": output_topic}, request_options)

    @overload
    async def add_transform(
        self, request: AddTransformRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_transform(
        self,
        /,
        *,
        input_topic: Topic,
        jq_expression: JqExpression,
        output_topic: Topic,
        output_topic_description: str | MISSING = MISSING,
        output_topic_version: Version | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_transform(
        self,
        request: AddTransformRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a transform.

        The output topic must start with ``com.axis.dt.``.

        Access: admin.
        """
        await self._run(OPS.add_transform, request, kwargs, request_options)

    @overload
    async def update_transform(
        self, request: UpdateTransformRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_transform(
        self,
        /,
        *,
        output_topic: Topic,
        input_topic: Topic | MISSING = MISSING,
        jq_expression: JqExpression | MISSING = MISSING,
        output_topic_description: str | MISSING = MISSING,
        output_topic_version: Version | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_transform(
        self,
        request: UpdateTransformRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the settings of a transform.

        Only the given settings change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_transform, request, kwargs, request_options)

    async def remove_transform(self, output_topic: Topic, *, request_options: RequestOptions | None = None) -> None:
        """Remove a transform. Access: admin."""
        await self._run(OPS.remove_transform, None, {"output_topic": output_topic}, request_options)

    async def set_transform_input_topic(
        self, output_topic: Topic, *, input_topic: Topic, request_options: RequestOptions | None = None
    ) -> None:
        """Set the input topic of a transform. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_transform_input_topic,
            None,
            {"output_topic": output_topic, "input_topic": input_topic},
            request_options,
        )

    async def set_transform_jq_expression(
        self, output_topic: Topic, *, jq_expression: JqExpression, request_options: RequestOptions | None = None
    ) -> None:
        """Set the jq expression of a transform. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_transform_jq_expression,
            None,
            {"output_topic": output_topic, "jq_expression": jq_expression},
            request_options,
        )

    async def set_transform_output_topic_description(
        self, output_topic: Topic, *, output_topic_description: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the output topic description of a transform.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_transform_output_topic_description,
            None,
            {"output_topic": output_topic, "output_topic_description": output_topic_description},
            request_options,
        )

    async def set_transform_output_topic_version(
        self, output_topic: Topic, *, output_topic_version: Version, request_options: RequestOptions | None = None
    ) -> None:
        """Set the output topic version of a transform. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_transform_output_topic_version,
            None,
            {"output_topic": output_topic, "output_topic_version": output_topic_version},
            request_options,
        )
