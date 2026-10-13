# GENERATED from specs/apis/network-video/action-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""SOAP web service (namespace http://www.axis.com/vapix/ws/action1) to list action/recipient templates and manage action configurations, recipient configurations...

Docs: https://developer.axis.com/vapix/network-video/event-and-action-services/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ServiceDiscovery
from .._protocols.soap import SoapBinding
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ActionRule(Model):
    rule_id: int = Field(validation_alias="RuleID", serialization_alias="RuleID")
    """Action Rule ID."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """User defined name for the action rule."""
    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """If false, then the rule is idle and the action is never executed. If true, the rule is active."""
    activation_timeout: str | None = Field(
        default=None, validation_alias="ActivationTimeout", serialization_alias="ActivationTimeout"
    )
    """Minimum time between successive action executions. This is used to prevent the action rule from being triggered repeatedly. If not specified, action will be executed as soon as possible. (format=duration)"""
    primary_action: int = Field(validation_alias="PrimaryAction", serialization_alias="PrimaryAction")
    """The primary action to be executed, specified by its Action Configuration ID."""
    failover_action: int | None = Field(
        default=None, validation_alias="FailoverAction", serialization_alias="FailoverAction"
    )
    """Action Configuration ID for the fallback action. The fallback action will be executed if the primary action fails."""


class ActionRules(Model):
    action_rule: list[ActionRule] | None = Field(
        default=None, validation_alias="ActionRule", serialization_alias="ActionRule"
    )
    """Action rule description."""


class ActionParameter(Model):
    name: str = Field(validation_alias="@Name", serialization_alias="@Name")
    """Parameter name (XML attribute)."""
    value: str = Field(validation_alias="@Value", serialization_alias="@Value")
    """Parameter value (XML attribute). All parameters of a template must be given; use an empty string for a parameter that is not used."""


class ActionParameters(Model):
    """Parameter values to send, as Parameter elements with Name and Value attributes."""

    parameter: list[ActionParameter] | None = Field(
        default=None, validation_alias="Parameter", serialization_alias="Parameter"
    )


class NewRecipientConfiguration(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """User defined name for the recipient configuration."""
    template_token: str = Field(validation_alias="TemplateToken", serialization_alias="TemplateToken")
    """Recipient type, specified as a recipient template token."""
    parameters: ActionParameters | None = Field(
        default=None, validation_alias="Parameters", serialization_alias="Parameters"
    )
    """Recipient configuration parameter values."""


class StoredActionParameter(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Parameter name (XML attribute)."""
    value: str = Field(validation_alias="Value", serialization_alias="Value")
    """Parameter value (XML attribute)."""


class StoredActionParameters(Model):
    """Parameter values as stored, one Parameter element per parameter."""

    parameter: list[StoredActionParameter] | None = Field(
        default=None, validation_alias="Parameter", serialization_alias="Parameter"
    )


class RecipientConfiguration(Model):
    configuration_id: int = Field(validation_alias="ConfigurationID", serialization_alias="ConfigurationID")
    """Recipient Configuration ID."""
    template_token: str = Field(validation_alias="TemplateToken", serialization_alias="TemplateToken")
    """Recipient type, specified as a recipient template token."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """User defined name for the recipient."""
    parameters: StoredActionParameters | None = Field(
        default=None, validation_alias="Parameters", serialization_alias="Parameters"
    )
    """Recipient parameter values."""


class RecipientConfigurations(Model):
    recipient_configuration: list[RecipientConfiguration] | None = Field(
        default=None, validation_alias="RecipientConfiguration", serialization_alias="RecipientConfiguration"
    )


class ActionTemplateParameter(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Parameter name (XML attribute)."""
    type: str = Field(validation_alias="Type", serialization_alias="Type")
    """Parameter data type (XML attribute)."""


class ActionTemplateParameters(Model):
    parameter: list[ActionTemplateParameter] = Field(validation_alias="Parameter", serialization_alias="Parameter")


class RecipientTemplate(Model):
    template_token: str = Field(validation_alias="TemplateToken", serialization_alias="TemplateToken")
    """Token used to identify the recipient template."""
    parameters: ActionTemplateParameters | None = Field(
        default=None, validation_alias="Parameters", serialization_alias="Parameters"
    )
    """Supported recipient parameters."""


class RecipientTemplates(Model):
    recipient_template: list[RecipientTemplate] | None = Field(
        default=None, validation_alias="RecipientTemplate", serialization_alias="RecipientTemplate"
    )
    """Recipient type description."""


class ActionConfiguration(Model):
    configuration_id: int = Field(validation_alias="ConfigurationID", serialization_alias="ConfigurationID")
    """Action Configuration ID."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """User defined name for the action configuration."""
    template_token: str = Field(validation_alias="TemplateToken", serialization_alias="TemplateToken")
    """Action type, specified as an action template token."""
    parameters: StoredActionParameters | None = Field(
        default=None, validation_alias="Parameters", serialization_alias="Parameters"
    )
    """Action configuration parameter values."""


class ActionConfigurations(Model):
    action_configuration: list[ActionConfiguration] | None = Field(
        default=None, validation_alias="ActionConfiguration", serialization_alias="ActionConfiguration"
    )
    """Action configuration description."""


class NewActionConfiguration(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """User defined name for the action configuration."""
    template_token: str = Field(validation_alias="TemplateToken", serialization_alias="TemplateToken")
    """A token used to identify the action template to use."""
    parameters: ActionParameters | None = Field(
        default=None, validation_alias="Parameters", serialization_alias="Parameters"
    )
    """Action configuration parameter values."""


class ActionTemplate(Model):
    template_token: str = Field(validation_alias="TemplateToken", serialization_alias="TemplateToken")
    """A token used to identify the action template."""
    recipient_template: str | None = Field(
        default=None, validation_alias="RecipientTemplate", serialization_alias="RecipientTemplate"
    )
    """The recipient template to be used with this action. The recipient template lists the recipient parameters needed for this action."""
    parameters: ActionTemplateParameters | None = Field(
        default=None, validation_alias="Parameters", serialization_alias="Parameters"
    )
    """List of action configuration parameters."""


class ActionTemplates(Model):
    action_template: list[ActionTemplate] | None = Field(
        default=None, validation_alias="ActionTemplate", serialization_alias="ActionTemplate"
    )
    """Action template description."""


class GetActionTemplatesResult(Model):
    action_templates: ActionTemplates | None = Field(
        default=None, validation_alias="ActionTemplates", serialization_alias="ActionTemplates"
    )
    """List of supported action types."""


class AddActionConfigurationRequest(Model):
    new_action_configuration: NewActionConfiguration = Field(
        validation_alias="NewActionConfiguration", serialization_alias="NewActionConfiguration"
    )
    """Action configuration description."""


class AddActionConfigurationResult(Model):
    configuration_id: int | None = Field(
        default=None, validation_alias="ConfigurationID", serialization_alias="ConfigurationID"
    )
    """Action Configuration ID."""


class RemoveActionConfigurationRequest(Model):
    configuration_id: int = Field(validation_alias="ConfigurationID", serialization_alias="ConfigurationID")
    """Action Configuration ID of the action configuration to be removed."""


class GetActionConfigurationsResult(Model):
    action_configurations: ActionConfigurations | None = Field(
        default=None, validation_alias="ActionConfigurations", serialization_alias="ActionConfigurations"
    )
    """List of stored action configurations."""


class GetRecipientTemplatesResult(Model):
    recipient_templates: RecipientTemplates | None = Field(
        default=None, validation_alias="RecipientTemplates", serialization_alias="RecipientTemplates"
    )
    """List of supported recipient types."""


class AddRecipientConfigurationRequest(Model):
    new_recipient_configuration: NewRecipientConfiguration = Field(
        validation_alias="NewRecipientConfiguration", serialization_alias="NewRecipientConfiguration"
    )
    """New recipient configuration."""


class AddRecipientConfigurationResult(Model):
    configuration_id: int | None = Field(
        default=None, validation_alias="ConfigurationID", serialization_alias="ConfigurationID"
    )
    """Recipient configuration ID."""


class RemoveRecipientConfigurationRequest(Model):
    configuration_id: int = Field(validation_alias="ConfigurationID", serialization_alias="ConfigurationID")
    """Recipient configuration ID of the recipient configuration to be removed."""


class GetRecipientConfigurationsResult(Model):
    recipient_configurations: RecipientConfigurations | None = Field(
        default=None, validation_alias="RecipientConfigurations", serialization_alias="RecipientConfigurations"
    )
    """List of configured recipients."""


class GetActionRulesResult(Model):
    action_rules: ActionRules | None = Field(
        default=None, validation_alias="ActionRules", serialization_alias="ActionRules"
    )
    """List of configured action rules."""


class RemoveActionRuleRequest(Model):
    rule_id: int = Field(validation_alias="RuleID", serialization_alias="RuleID")
    """Action Rule ID of the action rule to be removed."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/services"

INFO = ApiInfo(
    id="action-service",
    name="Action service (VAPIX Action service API, action1)",
    family=Family.SOAP,
    discovery=(ServiceDiscovery("http://www.axis.com/vapix/ws/action1"),),
    docs=("https://developer.axis.com/vapix/network-video/event-and-action-services/",),
)


class OPS:
    get_action_templates = Operation(
        INFO,
        "get_action_templates",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/GetActionTemplates",
            "GetActionTemplates",
            "http://www.axis.com/vapix/ws/action1",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "ActionTemplates",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "ActionTemplate",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(
                                            XmlField("TemplateToken", source="child"),
                                            XmlField("RecipientTemplate", source="child"),
                                            XmlField(
                                                "Parameters",
                                                source="path",
                                                nested=XmlMap(
                                                    fields=(
                                                        XmlField(
                                                            "Parameter",
                                                            source="path",
                                                            many=True,
                                                            nested=XmlMap(fields=(XmlField("Name"), XmlField("Type"))),
                                                        ),
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        result=GetActionTemplatesResult,
        access="admin",
        effect="read",
    )
    add_action_configuration = Operation(
        INFO,
        "add_action_configuration",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/AddActionConfiguration",
            "AddActionConfiguration",
            "http://www.axis.com/vapix/ws/action1",
            reply=XmlMap(fields=(XmlField("ConfigurationID", source="child"),)),
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        params=AddActionConfigurationRequest,
        result=AddActionConfigurationResult,
        access="admin",
        effect="write",
        write="create",
    )
    remove_action_configuration = Operation(
        INFO,
        "remove_action_configuration",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/RemoveActionConfiguration",
            "RemoveActionConfiguration",
            "http://www.axis.com/vapix/ws/action1",
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        params=RemoveActionConfigurationRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_action_configurations = Operation(
        INFO,
        "get_action_configurations",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/GetActionConfigurations",
            "GetActionConfigurations",
            "http://www.axis.com/vapix/ws/action1",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "ActionConfigurations",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "ActionConfiguration",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(
                                            XmlField("ConfigurationID", source="child"),
                                            XmlField("Name", source="child"),
                                            XmlField("TemplateToken", source="child"),
                                            XmlField(
                                                "Parameters",
                                                source="path",
                                                nested=XmlMap(
                                                    fields=(
                                                        XmlField(
                                                            "Parameter",
                                                            source="path",
                                                            many=True,
                                                            nested=XmlMap(fields=(XmlField("Name"), XmlField("Value"))),
                                                        ),
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        result=GetActionConfigurationsResult,
        access="admin",
        effect="read",
    )
    get_recipient_templates = Operation(
        INFO,
        "get_recipient_templates",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/GetRecipientTemplates",
            "GetRecipientTemplates",
            "http://www.axis.com/vapix/ws/action1",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "RecipientTemplates",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "RecipientTemplate",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(
                                            XmlField("TemplateToken", source="child"),
                                            XmlField(
                                                "Parameters",
                                                source="path",
                                                nested=XmlMap(
                                                    fields=(
                                                        XmlField(
                                                            "Parameter",
                                                            source="path",
                                                            many=True,
                                                            nested=XmlMap(fields=(XmlField("Name"), XmlField("Type"))),
                                                        ),
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        result=GetRecipientTemplatesResult,
        access="admin",
        effect="read",
    )
    add_recipient_configuration = Operation(
        INFO,
        "add_recipient_configuration",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/AddRecipientConfiguration",
            "AddRecipientConfiguration",
            "http://www.axis.com/vapix/ws/action1",
            reply=XmlMap(fields=(XmlField("ConfigurationID", source="child"),)),
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        params=AddRecipientConfigurationRequest,
        result=AddRecipientConfigurationResult,
        access="admin",
        effect="write",
        write="create",
    )
    remove_recipient_configuration = Operation(
        INFO,
        "remove_recipient_configuration",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/RemoveRecipientConfiguration",
            "RemoveRecipientConfiguration",
            "http://www.axis.com/vapix/ws/action1",
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        params=RemoveRecipientConfigurationRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_recipient_configurations = Operation(
        INFO,
        "get_recipient_configurations",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/GetRecipientConfigurations",
            "GetRecipientConfigurations",
            "http://www.axis.com/vapix/ws/action1",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "RecipientConfigurations",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "RecipientConfiguration",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(
                                            XmlField("ConfigurationID", source="child"),
                                            XmlField("TemplateToken", source="child"),
                                            XmlField("Name", source="child"),
                                            XmlField(
                                                "Parameters",
                                                source="path",
                                                nested=XmlMap(
                                                    fields=(
                                                        XmlField(
                                                            "Parameter",
                                                            source="path",
                                                            many=True,
                                                            nested=XmlMap(fields=(XmlField("Name"), XmlField("Value"))),
                                                        ),
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        result=GetRecipientConfigurationsResult,
        access="admin",
        effect="read",
    )
    get_action_rules = Operation(
        INFO,
        "get_action_rules",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/GetActionRules",
            "GetActionRules",
            "http://www.axis.com/vapix/ws/action1",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "ActionRules",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "ActionRule",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(
                                            XmlField("RuleID", source="child"),
                                            XmlField("Name", source="child"),
                                            XmlField("Enabled", source="child"),
                                            XmlField("ActivationTimeout", source="child"),
                                            XmlField("PrimaryAction", source="child"),
                                            XmlField("FailoverAction", source="child"),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        result=GetActionRulesResult,
        access="admin",
        effect="read",
    )
    remove_action_rule = Operation(
        INFO,
        "remove_action_rule",
        SoapBinding(
            "http://www.axis.com/vapix/ws/action1/RemoveActionRule",
            "RemoveActionRule",
            "http://www.axis.com/vapix/ws/action1",
            namespaces=(
                ("aa", "http://www.axis.com/vapix/ws/action1"),
                ("wsnt", "http://docs.oasis-open.org/wsn/b-2"),
                ("tns1", "http://www.onvif.org/ver10/topics"),
                ("tnsaxis", "http://www.axis.com/2009/event/topics"),
            ),
        ),
        params=RemoveActionRuleRequest,
        access="admin",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class ActionServiceApi(SyncApi):
    """Action service (VAPIX Action service API, action1) (``action-service``)."""

    INFO = INFO

    def get_action_templates(self, *, request_options: RequestOptions | None = None) -> GetActionTemplatesResult:
        """List the action templates supported by the Axis product. Access: admin."""
        return self._run(OPS.get_action_templates, None, {}, request_options)

    @overload
    def add_action_configuration(
        self, request: AddActionConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddActionConfigurationResult: ...
    @overload
    def add_action_configuration(
        self, /, *, new_action_configuration: NewActionConfiguration, request_options: RequestOptions | None = None
    ) -> AddActionConfigurationResult: ...
    def add_action_configuration(
        self,
        request: AddActionConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AddActionConfigurationResult:
        """Add a new action configuration. Access: admin."""
        return self._run(OPS.add_action_configuration, request, kwargs, request_options)

    def remove_action_configuration(
        self, *, configuration_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an action configuration. Access: admin."""
        self._run(OPS.remove_action_configuration, None, {"configuration_id": configuration_id}, request_options)

    def get_action_configurations(
        self, *, request_options: RequestOptions | None = None
    ) -> GetActionConfigurationsResult:
        """List currently stored action configurations. Access: admin."""
        return self._run(OPS.get_action_configurations, None, {}, request_options)

    def get_recipient_templates(self, *, request_options: RequestOptions | None = None) -> GetRecipientTemplatesResult:
        """List the recipient templates supported by the Axis product. Access: admin."""
        return self._run(OPS.get_recipient_templates, None, {}, request_options)

    @overload
    def add_recipient_configuration(
        self, request: AddRecipientConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddRecipientConfigurationResult: ...
    @overload
    def add_recipient_configuration(
        self,
        /,
        *,
        new_recipient_configuration: NewRecipientConfiguration,
        request_options: RequestOptions | None = None,
    ) -> AddRecipientConfigurationResult: ...
    def add_recipient_configuration(
        self,
        request: AddRecipientConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AddRecipientConfigurationResult:
        """Add a new recipient configuration. Access: admin."""
        return self._run(OPS.add_recipient_configuration, request, kwargs, request_options)

    def remove_recipient_configuration(
        self, *, configuration_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a recipient configuration. Access: admin."""
        self._run(OPS.remove_recipient_configuration, None, {"configuration_id": configuration_id}, request_options)

    def get_recipient_configurations(
        self, *, request_options: RequestOptions | None = None
    ) -> GetRecipientConfigurationsResult:
        """List currently stored recipient configurations. Access: admin."""
        return self._run(OPS.get_recipient_configurations, None, {}, request_options)

    def get_action_rules(self, *, request_options: RequestOptions | None = None) -> GetActionRulesResult:
        """List currently stored action rules. Access: admin."""
        return self._run(OPS.get_action_rules, None, {}, request_options)

    def remove_action_rule(self, *, rule_id: int, request_options: RequestOptions | None = None) -> None:
        """Remove an action rule. Access: admin."""
        self._run(OPS.remove_action_rule, None, {"rule_id": rule_id}, request_options)


class AsyncActionServiceApi(AsyncApi):
    """Action service (VAPIX Action service API, action1) (``action-service``)."""

    INFO = INFO

    async def get_action_templates(self, *, request_options: RequestOptions | None = None) -> GetActionTemplatesResult:
        """List the action templates supported by the Axis product. Access: admin."""
        return await self._run(OPS.get_action_templates, None, {}, request_options)

    @overload
    async def add_action_configuration(
        self, request: AddActionConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddActionConfigurationResult: ...
    @overload
    async def add_action_configuration(
        self, /, *, new_action_configuration: NewActionConfiguration, request_options: RequestOptions | None = None
    ) -> AddActionConfigurationResult: ...
    async def add_action_configuration(
        self,
        request: AddActionConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AddActionConfigurationResult:
        """Add a new action configuration. Access: admin."""
        return await self._run(OPS.add_action_configuration, request, kwargs, request_options)

    async def remove_action_configuration(
        self, *, configuration_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an action configuration. Access: admin."""
        await self._run(OPS.remove_action_configuration, None, {"configuration_id": configuration_id}, request_options)

    async def get_action_configurations(
        self, *, request_options: RequestOptions | None = None
    ) -> GetActionConfigurationsResult:
        """List currently stored action configurations. Access: admin."""
        return await self._run(OPS.get_action_configurations, None, {}, request_options)

    async def get_recipient_templates(
        self, *, request_options: RequestOptions | None = None
    ) -> GetRecipientTemplatesResult:
        """List the recipient templates supported by the Axis product. Access: admin."""
        return await self._run(OPS.get_recipient_templates, None, {}, request_options)

    @overload
    async def add_recipient_configuration(
        self, request: AddRecipientConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddRecipientConfigurationResult: ...
    @overload
    async def add_recipient_configuration(
        self,
        /,
        *,
        new_recipient_configuration: NewRecipientConfiguration,
        request_options: RequestOptions | None = None,
    ) -> AddRecipientConfigurationResult: ...
    async def add_recipient_configuration(
        self,
        request: AddRecipientConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AddRecipientConfigurationResult:
        """Add a new recipient configuration. Access: admin."""
        return await self._run(OPS.add_recipient_configuration, request, kwargs, request_options)

    async def remove_recipient_configuration(
        self, *, configuration_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a recipient configuration. Access: admin."""
        await self._run(
            OPS.remove_recipient_configuration, None, {"configuration_id": configuration_id}, request_options
        )

    async def get_recipient_configurations(
        self, *, request_options: RequestOptions | None = None
    ) -> GetRecipientConfigurationsResult:
        """List currently stored recipient configurations. Access: admin."""
        return await self._run(OPS.get_recipient_configurations, None, {}, request_options)

    async def get_action_rules(self, *, request_options: RequestOptions | None = None) -> GetActionRulesResult:
        """List currently stored action rules. Access: admin."""
        return await self._run(OPS.get_action_rules, None, {}, request_options)

    async def remove_action_rule(self, *, rule_id: int, request_options: RequestOptions | None = None) -> None:
        """Remove an action rule. Access: admin."""
        await self._run(OPS.remove_action_rule, None, {"rule_id": rule_id}, request_options)
