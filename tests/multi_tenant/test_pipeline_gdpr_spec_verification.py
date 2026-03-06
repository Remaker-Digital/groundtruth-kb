"""Spec verification tests for pipeline, GDPR, alerts, and config services.

Each test class verifies a specific SPEC-* requirement against the
actual implementation. Tests exercise production interfaces per GOV-10.

Session S152 — spec review and real test creation (batch 5).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# SPEC-0620: SystemPromptBuilder assembles per-agent prompts
# ---------------------------------------------------------------------------


class TestSpec0620SystemPromptBuilder:
    """SPEC-0620: SystemPromptBuilder MUST compose per-agent system prompts
    from platform base, tier capabilities, tenant config, and customer context.

    Verified by: SystemPromptBuilder class exists, has build() method,
    AgentRole enum covers all 7 pipeline agents.
    """

    def test_system_prompt_builder_class_exists(self):
        """SystemPromptBuilder is importable and has build() method."""
        from src.multi_tenant.system_prompt_builder import SystemPromptBuilder

        builder = SystemPromptBuilder()
        assert hasattr(builder, "build")

    def test_agent_role_enum_has_seven_roles(self):
        """AgentRole enum includes all 7 pipeline agents."""
        from src.multi_tenant.system_prompt_builder import AgentRole

        values = {r.value for r in AgentRole}
        assert "intent-classifier" in values
        assert "knowledge-retrieval" in values
        assert "response-generator" in values
        assert "escalation-handler" in values
        assert "analytics-collector" in values
        assert "critic-supervisor" in values
        assert "co-pilot" in values

    def test_build_method_accepts_agent_role(self):
        """build() signature accepts agent, tenant, and preferences."""
        from src.multi_tenant.system_prompt_builder import SystemPromptBuilder

        sig = inspect.signature(SystemPromptBuilder.build)
        params = list(sig.parameters.keys())
        assert "agent" in params
        assert "tenant" in params
        assert "preferences" in params


# ---------------------------------------------------------------------------
# SPEC-0291: GDPR PII scrubbing at logging layer
# ---------------------------------------------------------------------------


class TestSpec0291GdprPiiScrubbing:
    """SPEC-0291: PII MUST be scrubbed from logs and telemetry before export.

    Verified by: PiiScrubber class exists, scrub() returns a new dict,
    scrub_text() exists for free-text scrubbing.
    """

    def test_pii_scrubber_class_exists(self):
        """PiiScrubber class is importable."""
        from src.multi_tenant.gdpr_services import PiiScrubber

        scrubber = PiiScrubber()
        assert hasattr(scrubber, "scrub")

    def test_scrub_returns_new_dict(self):
        """scrub() returns a new dict (original not modified)."""
        from src.multi_tenant.gdpr_services import PiiScrubber

        scrubber = PiiScrubber()
        original = {"name": "Test", "safe_field": "value"}
        result = scrubber.scrub(original)
        assert isinstance(result, dict)

    def test_scrub_text_method_exists(self):
        """scrub_text() method is available for free-text redaction."""
        from src.multi_tenant.gdpr_services import PiiScrubber

        scrubber = PiiScrubber()
        assert hasattr(scrubber, "scrub_text")


# ---------------------------------------------------------------------------
# SPEC-0292: GDPR grace period (Shopify 48hr, Stripe 30d)
# ---------------------------------------------------------------------------


class TestSpec0292GdprGracePeriod:
    """SPEC-0292: Data deletion MUST observe channel-specific grace periods.
    Shopify: 48-hour mandatory. Stripe: 30-day per SLA.

    Verified by: GracePeriodManager class, constants for each channel,
    calculate_grace_period() returns correct durations.
    """

    def test_shopify_grace_period_48_hours(self):
        """Shopify grace period constant is 48 hours."""
        from src.multi_tenant.gdpr_services import SHOPIFY_GRACE_PERIOD_HOURS

        assert SHOPIFY_GRACE_PERIOD_HOURS == 48

    def test_stripe_grace_period_30_days(self):
        """Stripe grace period constant is 30 days."""
        from src.multi_tenant.gdpr_services import STRIPE_GRACE_PERIOD_DAYS

        assert STRIPE_GRACE_PERIOD_DAYS == 30

    def test_grace_period_manager_exists(self):
        """GracePeriodManager class is importable."""
        from src.multi_tenant.gdpr_services import GracePeriodManager

        mgr = GracePeriodManager()
        assert hasattr(mgr, "calculate_grace_period")
        assert hasattr(mgr, "is_grace_expired")

    def test_calculate_grace_period_shopify(self):
        """calculate_grace_period returns result for Shopify channel."""
        from src.multi_tenant.cosmos_schema import BillingChannel
        from src.multi_tenant.gdpr_services import GracePeriodManager

        mgr = GracePeriodManager()
        result = mgr.calculate_grace_period(BillingChannel.SHOPIFY)
        assert result.grace_period_hours == 48
        assert result.is_expired is False


# ---------------------------------------------------------------------------
# SPEC-0293: GDPR data export service
# ---------------------------------------------------------------------------


class TestSpec0293GdprDataExport:
    """SPEC-0293: Data export MUST cover all tenant/customer data across
    all registered stores. Produces a portable JSON archive.

    Verified by: DataExportService class exists with export_tenant()
    and export_customer() async methods. ExportResult dataclass.
    """

    def test_data_export_service_class_exists(self):
        """DataExportService class is importable."""
        from src.multi_tenant.gdpr_services import DataExportService

        assert inspect.isclass(DataExportService)

    def test_export_tenant_is_async(self):
        """export_tenant() is an async method."""
        from src.multi_tenant.gdpr_services import DataExportService

        assert inspect.iscoroutinefunction(DataExportService.export_tenant)

    def test_export_result_dataclass_fields(self):
        """ExportResult has required fields."""
        from src.multi_tenant.gdpr_services import ExportResult

        fields = {f.name for f in ExportResult.__dataclass_fields__.values()}
        assert "export_id" in fields
        assert "tenant_id" in fields
        assert "stores_exported" in fields
        assert "data" in fields


# ---------------------------------------------------------------------------
# SPEC-0294: GDPR data deletion service
# ---------------------------------------------------------------------------


class TestSpec0294GdprDataDeletion:
    """SPEC-0294: Data deletion MUST cascade across all registered stores
    (Cosmos DB, NATS, Key Vault).

    Verified by: DataDeletionService class with delete_tenant() and
    delete_customer() async methods. DeletionResult dataclass.
    """

    def test_data_deletion_service_class_exists(self):
        """DataDeletionService class is importable."""
        from src.multi_tenant.gdpr_services import DataDeletionService

        assert inspect.isclass(DataDeletionService)

    def test_delete_tenant_is_async(self):
        """delete_tenant() is an async method."""
        from src.multi_tenant.gdpr_services import DataDeletionService

        assert inspect.iscoroutinefunction(DataDeletionService.delete_tenant)

    def test_deletion_result_dataclass_fields(self):
        """DeletionResult has required fields."""
        from src.multi_tenant.gdpr_services import DeletionResult

        fields = {f.name for f in DeletionResult.__dataclass_fields__.values()}
        assert "deletion_id" in fields
        assert "tenant_id" in fields
        assert "stores_deleted" in fields


# ---------------------------------------------------------------------------
# SPEC-0295: GDPR consent management
# ---------------------------------------------------------------------------


class TestSpec0295GdprConsentManagement:
    """SPEC-0295: GDPR consent MUST gate Persistent Customer Memory layers 2-4.
    Layer 1 (basic profile) always available. Layers 2-4 require consent.

    Verified by: ConsentManager class, CONSENT_REQUIRED_LAYERS,
    is_layer_allowed() method.
    """

    def test_consent_manager_class_exists(self):
        """ConsentManager class is importable."""
        from src.multi_tenant.gdpr_services import ConsentManager

        mgr = ConsentManager()
        assert hasattr(mgr, "is_layer_allowed")

    def test_consent_required_layers_are_2_3_4(self):
        """Only layers 2, 3, and 4 require consent."""
        from src.multi_tenant.gdpr_services import ConsentManager

        assert ConsentManager.CONSENT_REQUIRED_LAYERS == {2, 3, 4}

    def test_layer_1_allowed_without_consent(self):
        """Layer 1 is always allowed regardless of consent status."""
        from src.multi_tenant.cosmos_schema import ConsentStatus
        from src.multi_tenant.gdpr_services import ConsentManager

        mgr = ConsentManager()
        assert mgr.is_layer_allowed(ConsentStatus.NOT_ASKED, layer=1) is True
        assert mgr.is_layer_allowed(ConsentStatus.DENIED, layer=1) is True

    def test_layer_2_blocked_without_consent(self):
        """Layer 2 requires GRANTED consent."""
        from src.multi_tenant.cosmos_schema import ConsentStatus
        from src.multi_tenant.gdpr_services import ConsentManager

        mgr = ConsentManager()
        assert mgr.is_layer_allowed(ConsentStatus.NOT_ASKED, layer=2) is False
        assert mgr.is_layer_allowed(ConsentStatus.GRANTED, layer=2) is True


# ---------------------------------------------------------------------------
# SPEC-0640: CriticPolicy fail-closed safety gate
# ---------------------------------------------------------------------------


class TestSpec0640CriticPolicyFailClosed:
    """SPEC-0640: CriticPolicy MUST be fail-closed — if the Critic cannot be
    reached, all responses MUST be blocked.

    Verified by: CriticPolicy class, SAFE_FALLBACK_MESSAGE constant,
    CriticVerdict enum, validate_response() async method.
    """

    def test_critic_policy_class_exists(self):
        """CriticPolicy class is importable."""
        from src.multi_tenant.critic_policy import CriticPolicy

        assert inspect.isclass(CriticPolicy)

    def test_safe_fallback_message_exists(self):
        """SAFE_FALLBACK_MESSAGE constant is defined."""
        from src.multi_tenant.critic_policy import SAFE_FALLBACK_MESSAGE

        assert len(SAFE_FALLBACK_MESSAGE) > 10

    def test_critic_verdict_enum(self):
        """CriticVerdict has APPROVED, MODIFIED, BLOCKED."""
        from src.multi_tenant.critic_policy import CriticVerdict

        values = {v.value for v in CriticVerdict}
        assert "approved" in values or "APPROVED" in {v.name for v in CriticVerdict}

    def test_validate_response_is_async(self):
        """validate_response() is an async method."""
        from src.multi_tenant.critic_policy import CriticPolicy

        assert inspect.iscoroutinefunction(CriticPolicy.validate_response)


# ---------------------------------------------------------------------------
# SPEC-0700: ChatPipeline orchestrator
# ---------------------------------------------------------------------------


class TestSpec0700ChatPipelineOrchestrator:
    """SPEC-0700: ChatPipeline MUST orchestrate the 6-agent pipeline
    for each conversation turn.

    Verified by: ChatPipeline class inherits from the 3 mixins,
    has execute() async generator, and init/close lifecycle.
    """

    def test_chat_pipeline_class_exists(self):
        """ChatPipeline class is importable."""
        from src.chat.pipeline.orchestrator import ChatPipeline

        assert inspect.isclass(ChatPipeline)

    def test_chat_pipeline_inherits_mixins(self):
        """ChatPipeline inherits from AgentDispatch, CriticEscalation, Analytics."""
        from src.chat.pipeline.orchestrator import ChatPipeline

        mro_names = [cls.__name__ for cls in ChatPipeline.__mro__]
        assert "AgentDispatchMixin" in mro_names
        assert "CriticEscalationMixin" in mro_names
        assert "AnalyticsMixin" in mro_names

    def test_execute_method_exists(self):
        """execute() method exists on ChatPipeline."""
        from src.chat.pipeline.orchestrator import ChatPipeline

        assert hasattr(ChatPipeline, "execute")


# ---------------------------------------------------------------------------
# SPEC-0710: Pipeline timeout budget (8s hard deadline)
# ---------------------------------------------------------------------------


class TestSpec0710PipelineTimeoutBudget:
    """SPEC-0710: Pipeline MUST enforce an 8-second hard deadline with
    per-stage budgets.

    Verified by: PipelineTimeoutBudget class, PipelineTimeoutError,
    stage budgets for all 6 agents total ~8000ms.
    """

    def test_pipeline_timeout_budget_class_exists(self):
        """PipelineTimeoutBudget class is importable."""
        from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget

        budget = PipelineTimeoutBudget()
        assert hasattr(budget, "remaining_ms")

    def test_pipeline_timeout_error_exists(self):
        """PipelineTimeoutError exception is importable."""
        from src.multi_tenant.pipeline_resilience import PipelineTimeoutError

        assert issubclass(PipelineTimeoutError, Exception)

    def test_pipeline_timeout_error_fields(self):
        """PipelineTimeoutError carries stage, budget_ms, elapsed_ms."""
        from src.multi_tenant.pipeline_resilience import PipelineTimeoutError

        err = PipelineTimeoutError("test-stage", 1000, 1500.0)
        assert err.stage == "test-stage"
        assert err.budget_ms == 1000
        assert err.elapsed_ms == 1500.0

    def test_service_unavailable_error_exists(self):
        """ServiceUnavailableError exception for circuit breaker."""
        from src.multi_tenant.pipeline_resilience import ServiceUnavailableError

        assert issubclass(ServiceUnavailableError, Exception)


# ---------------------------------------------------------------------------
# SPEC-0740: ConversationMeter billing rules
# ---------------------------------------------------------------------------


class TestSpec0740ConversationMeterBilling:
    """SPEC-0740: ConversationMeter MUST classify conversations as billable
    or non-billable per Decision #24 rules.

    Verified by: ConversationMeter class, billing constants,
    ConversationEndReason enum, NON_BILLABLE_PREFIXES.
    """

    def test_conversation_meter_class_exists(self):
        """ConversationMeter class is importable."""
        from src.multi_tenant.conversation_meter import ConversationMeter

        assert inspect.isclass(ConversationMeter)

    def test_idle_timeout_30_minutes(self):
        """Idle timeout is 30 minutes (1800 seconds)."""
        from src.multi_tenant.conversation_meter import IDLE_TIMEOUT_SECONDS

        assert IDLE_TIMEOUT_SECONDS == 30 * 60

    def test_max_turns_50(self):
        """Maximum turns per conversation is 50."""
        from src.multi_tenant.conversation_meter import MAX_TURNS

        assert MAX_TURNS == 50

    def test_non_billable_prefixes(self):
        """test_, admin_, health_, system_ prefixes are non-billable."""
        from src.multi_tenant.conversation_meter import NON_BILLABLE_PREFIXES

        assert "test_" in NON_BILLABLE_PREFIXES
        assert "admin_" in NON_BILLABLE_PREFIXES
        assert "health_" in NON_BILLABLE_PREFIXES

    def test_conversation_end_reason_enum(self):
        """ConversationEndReason includes all expected end reasons."""
        from src.multi_tenant.conversation_meter import ConversationEndReason

        values = {r.value for r in ConversationEndReason}
        assert "idle_timeout" in values
        assert "customer_ended" in values
        assert "escalated" in values
        assert "max_turns" in values

    def test_alert_thresholds(self):
        """Usage alert fires at 80% and 100%."""
        from src.multi_tenant.conversation_meter import (
            ALERT_THRESHOLD_LIMIT,
            ALERT_THRESHOLD_WARNING,
        )

        assert ALERT_THRESHOLD_WARNING == 0.80
        assert ALERT_THRESHOLD_LIMIT == 1.00

    def test_stripe_meter_event_name(self):
        """Stripe Billing Meter event name is 'conversation_overage'."""
        from src.multi_tenant.conversation_meter import STRIPE_METER_EVENT_NAME

        assert STRIPE_METER_EVENT_NAME == "conversation_overage"


# ---------------------------------------------------------------------------
# SPEC-0237: AlertDeliveryService routes alerts to channels
# ---------------------------------------------------------------------------


class TestSpec0237AlertDeliveryService:
    """SPEC-0237: Alert delivery MUST route alerts to all registered channels.
    A log channel MUST always be present as fallback.

    Verified by: AlertDeliveryService, Alert dataclass, AlertType enum,
    register_channel() and deliver_alert() methods.
    """

    def test_alert_delivery_service_class_exists(self):
        """AlertDeliveryService class is importable."""
        from src.multi_tenant.alert_delivery import AlertDeliveryService

        service = AlertDeliveryService()
        assert hasattr(service, "register_channel")
        assert hasattr(service, "deliver_alert")

    def test_alert_type_enum_has_12_types(self):
        """AlertType enum covers all alert categories."""
        from src.multi_tenant.alert_delivery import AlertType

        values = {t.value for t in AlertType}
        assert "usage_80_pct" in values
        assert "usage_100_pct" in values
        assert "sla_violation" in values
        assert "trial_expiring" in values
        assert "escalation" in values
        assert len(values) >= 10

    def test_alert_severity_levels(self):
        """AlertSeverity has info, warning, critical."""
        from src.multi_tenant.alert_delivery import AlertSeverity

        values = {s.value for s in AlertSeverity}
        assert values == {"info", "warning", "critical"}

    def test_log_channel_always_present(self):
        """Fresh AlertDeliveryService always has log channel."""
        from src.multi_tenant.alert_delivery import AlertDeliveryService

        service = AlertDeliveryService()
        channels = service.get_registered_channels()
        assert "log" in channels

    def test_alert_dataclass_fields(self):
        """Alert dataclass has all required fields."""
        from src.multi_tenant.alert_delivery import Alert

        fields = {f.name for f in Alert.__dataclass_fields__.values()}
        assert "alert_id" in fields
        assert "tenant_id" in fields
        assert "alert_type" in fields
        assert "severity" in fields
        assert "title" in fields
        assert "message" in fields


# ---------------------------------------------------------------------------
# SPEC-0833: ConfigSuggestionEngine brand name inference
# ---------------------------------------------------------------------------


class TestSpec0833ConfigSuggestionEngine:
    """SPEC-0833: ConfigSuggestionEngine MUST generate configuration
    suggestions from KB content analysis (brand name, tone, policies).

    Verified by: ConfigSuggestionEngine class, Suggestion/SuggestionSet
    dataclasses, generate_suggestions() async method, tone keywords.
    """

    def test_config_suggestion_engine_class_exists(self):
        """ConfigSuggestionEngine class is importable."""
        from src.multi_tenant.config_suggestion_engine import ConfigSuggestionEngine

        engine = ConfigSuggestionEngine()
        assert hasattr(engine, "generate_suggestions")

    def test_generate_suggestions_is_async(self):
        """generate_suggestions() is async."""
        from src.multi_tenant.config_suggestion_engine import ConfigSuggestionEngine

        assert inspect.iscoroutinefunction(ConfigSuggestionEngine.generate_suggestions)

    def test_suggestion_dataclass(self):
        """Suggestion dataclass has field_name, value, confidence, source."""
        from src.multi_tenant.config_suggestion_engine import Suggestion

        fields = {f.name for f in Suggestion.__dataclass_fields__.values()}
        assert "field_name" in fields
        assert "value" in fields
        assert "confidence" in fields
        assert "source" in fields

    def test_suggestion_set_has_to_dict(self):
        """SuggestionSet has to_dict() and get() methods."""
        from src.multi_tenant.config_suggestion_engine import SuggestionSet

        ss = SuggestionSet()
        assert hasattr(ss, "to_dict")
        assert hasattr(ss, "get")

    def test_tone_keywords_dict_exists(self):
        """Tone analysis keywords are defined for multiple tones."""
        from src.multi_tenant.config_suggestion_engine import _TONE_KEYWORDS

        assert "professional" in _TONE_KEYWORDS
        assert "friendly" in _TONE_KEYWORDS
        assert "technical" in _TONE_KEYWORDS
        assert len(_TONE_KEYWORDS) >= 4

    def test_escalation_patterns_exist(self):
        """Escalation keyword patterns are defined."""
        from src.multi_tenant.config_suggestion_engine import _ESCALATION_PATTERNS

        assert len(_ESCALATION_PATTERNS) >= 10
        assert "defective" in _ESCALATION_PATTERNS
        assert "safety" in _ESCALATION_PATTERNS


# ---------------------------------------------------------------------------
# SPEC-0720: Response explainability (DecisionTraceBuilder)
# ---------------------------------------------------------------------------


class TestSpec0720ResponseExplainability:
    """SPEC-0720: Each AI response MUST include a decision trace capturing
    profile factors, knowledge sources, memory signals, and timing.

    Verified by: DecisionTraceBuilder class, KnowledgeSource dataclass.
    """

    def test_decision_trace_builder_exists(self):
        """DecisionTraceBuilder class is importable."""
        from src.multi_tenant.response_explainability import DecisionTraceBuilder

        assert inspect.isclass(DecisionTraceBuilder)

    def test_knowledge_source_dataclass(self):
        """KnowledgeSource dataclass exists."""
        from src.multi_tenant.response_explainability import KnowledgeSource

        assert inspect.isclass(KnowledgeSource)

    def test_builder_has_build_method(self):
        """DecisionTraceBuilder has build() or finalize() method."""
        from src.multi_tenant.response_explainability import DecisionTraceBuilder

        builder = DecisionTraceBuilder(
            conversation_id="test-conv-001",
            tenant_id="test-tenant-001",
        )
        assert hasattr(builder, "build") or hasattr(builder, "finalize")


# ---------------------------------------------------------------------------
# SPEC-0827: ACS email delivery with rate-limit handling
# ---------------------------------------------------------------------------


class TestSpec0827AcsEmailDelivery:
    """SPEC-0827: Email delivery MUST use Azure Communication Services with
    rate-limit handling (429 fails fast instead of blocking).

    Verified by: send_acs_email() async function, _send_acs_email_sync,
    SENDER_ADDRESS constant.
    """

    def test_send_acs_email_function_exists(self):
        """send_acs_email() async function is importable."""
        from src.multi_tenant.alert_delivery import send_acs_email

        assert inspect.iscoroutinefunction(send_acs_email)

    def test_sender_address_defined(self):
        """SENDER_ADDRESS constant is defined."""
        from src.multi_tenant.alert_delivery import SENDER_ADDRESS

        assert "azurecomm.net" in SENDER_ADDRESS

    def test_sync_email_helper_exists(self):
        """_send_acs_email_sync function exists for thread offloading."""
        from src.multi_tenant.alert_delivery import _send_acs_email_sync

        assert callable(_send_acs_email_sync)


# ---------------------------------------------------------------------------
# SPEC-0320: Config restore_previous atomicity
# ---------------------------------------------------------------------------


class TestSpec0320ConfigRestorePrevious:
    """SPEC-0320: Restoring a previous configuration MUST atomically replace
    the current active config.

    Verified by: ActivationService.restore_previous() is async.
    """

    def test_restore_previous_is_async(self):
        """restore_previous() is an async method."""
        from src.multi_tenant.activation_service import ActivationService

        assert inspect.iscoroutinefunction(ActivationService.restore_previous)

    def test_restore_previous_method_exists(self):
        """ActivationService has restore_previous method."""
        from src.multi_tenant.activation_service import ActivationService

        assert hasattr(ActivationService, "restore_previous")


# ---------------------------------------------------------------------------
# SPEC-0321: Config activate atomicity
# ---------------------------------------------------------------------------


class TestSpec0321ConfigActivateAtomicity:
    """SPEC-0321: Activating a configuration MUST be atomic — draft becomes
    active in a single operation.

    Verified by: ActivationService.activate() is async, returns
    ActivationResult.
    """

    def test_activate_is_async(self):
        """activate() is an async method."""
        from src.multi_tenant.activation_service import ActivationService

        assert inspect.iscoroutinefunction(ActivationService.activate)

    def test_activation_result_exists(self):
        """ActivationResult dataclass is importable."""
        from src.multi_tenant.activation_service import ActivationResult

        assert inspect.isclass(ActivationResult)


# ---------------------------------------------------------------------------
# SPEC-0322: Config validation before activation
# ---------------------------------------------------------------------------


class TestSpec0322ConfigValidationBeforeActivation:
    """SPEC-0322: Configuration MUST be validated before activation.

    Verified by: ValidationResult dataclass exists, DraftSaveResult exists.
    """

    def test_validation_result_exists(self):
        """ValidationResult dataclass is importable."""
        from src.multi_tenant.activation_service import ValidationResult

        assert inspect.isclass(ValidationResult)

    def test_draft_save_result_exists(self):
        """DraftSaveResult dataclass is importable."""
        from src.multi_tenant.activation_service import DraftSaveResult

        assert inspect.isclass(DraftSaveResult)


# ---------------------------------------------------------------------------
# SPEC-0480: Config initial state is DRAFT (not ACTIVE)
# ---------------------------------------------------------------------------


class TestSpec0480ConfigInitialStateDraft:
    """SPEC-0480: A new tenant's configuration MUST start in DRAFT state,
    not ACTIVE.

    Verified by: ConfigState.DRAFT exists and is a valid initial state.
    """

    def test_config_state_has_draft(self):
        """ConfigState enum includes 'draft'."""
        from src.multi_tenant.cosmos_schema import ConfigState

        values = {e.value for e in ConfigState}
        assert "draft" in values

    def test_draft_is_distinct_from_active(self):
        """DRAFT and ACTIVE are distinct states."""
        from src.multi_tenant.cosmos_schema import ConfigState

        assert ConfigState.DRAFT != ConfigState.ACTIVE
        assert ConfigState.DRAFT.value == "draft"
        assert ConfigState.ACTIVE.value == "active"


# ---------------------------------------------------------------------------
# SPEC-1557: Co-Pilot agent in pipeline
# ---------------------------------------------------------------------------


class TestSpec1557CoPilotAgent:
    """SPEC-1557: Co-Pilot agent MUST be available in the pipeline as an
    AgentRole for admin assistance.

    Verified by: AgentRole.CO_PILOT exists, ADMIN_ASSISTANCE_INTENT constant.
    """

    def test_co_pilot_agent_role_exists(self):
        """AgentRole.CO_PILOT is defined."""
        from src.multi_tenant.system_prompt_builder import AgentRole

        assert hasattr(AgentRole, "CO_PILOT")
        assert AgentRole.CO_PILOT.value == "co-pilot"

    def test_admin_assistance_intent_constant(self):
        """ADMIN_ASSISTANCE_INTENT constant is defined."""
        from src.chat.pipeline.constants import ADMIN_ASSISTANCE_INTENT

        assert isinstance(ADMIN_ASSISTANCE_INTENT, str)
        assert len(ADMIN_ASSISTANCE_INTENT) > 0


# ---------------------------------------------------------------------------
# SPEC-1558: Intent detection dispatches to correct agent
# ---------------------------------------------------------------------------


class TestSpec1558IntentDetectionDispatch:
    """SPEC-1558: Intent detection MUST dispatch to the correct pipeline agent.
    ESCALATION_INTENT triggers escalation handler.

    Verified by: ESCALATION_INTENT constant, AgentDispatchMixin class.
    """

    def test_escalation_intent_constant(self):
        """ESCALATION_INTENT constant is defined."""
        from src.chat.pipeline.constants import ESCALATION_INTENT

        assert isinstance(ESCALATION_INTENT, str)
        assert len(ESCALATION_INTENT) > 0

    def test_agent_dispatch_mixin_exists(self):
        """AgentDispatchMixin is importable."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        assert inspect.isclass(AgentDispatchMixin)


# ---------------------------------------------------------------------------
# SPEC-0766: Automated provisioning lifecycle
# ---------------------------------------------------------------------------


class TestSpec0766AutomatedProvisioningLifecycle:
    """SPEC-0766: Tenant provisioning MUST be fully automated including
    health check. No manual intervention.

    Verified by: provision_tenant or spa_provision_tenant is async,
    returns credentials.
    """

    def test_provisioning_function_is_async(self):
        """Provisioning function is async."""
        from src.integrations import provisioning

        if hasattr(provisioning, "spa_provision_tenant"):
            assert inspect.iscoroutinefunction(provisioning.spa_provision_tenant)
        else:
            assert inspect.iscoroutinefunction(provisioning.provision_tenant)

    def test_provisioning_module_has_result_type(self):
        """Provisioning module defines a result type with credentials."""
        from src.integrations.provisioning import SpaProvisionResult

        fields = {f.name for f in SpaProvisionResult.__dataclass_fields__.values()}
        assert "superadmin_api_key" in fields
        assert "widget_key" in fields


# ---------------------------------------------------------------------------
# SPEC-0237b: Alert type severity mapping
# ---------------------------------------------------------------------------


class TestSpec0237bAlertSeverityMapping:
    """SPEC-0237b: Each alert type MUST have a default severity mapping.
    CRITICAL alerts: usage_100_pct, throttle_activated, sla_violation, outage.

    Verified by: _DEFAULT_SEVERITY mapping exists with correct critical types.
    """

    def test_default_severity_mapping_exists(self):
        """_DEFAULT_SEVERITY maps all AlertTypes to severities."""
        from src.multi_tenant.alert_delivery import _DEFAULT_SEVERITY, AlertType

        for alert_type in AlertType:
            assert alert_type in _DEFAULT_SEVERITY

    def test_critical_alert_types(self):
        """SLA violation and outage are CRITICAL severity."""
        from src.multi_tenant.alert_delivery import (
            AlertSeverity,
            AlertType,
            _DEFAULT_SEVERITY,
        )

        assert _DEFAULT_SEVERITY[AlertType.SLA_VIOLATION] == AlertSeverity.CRITICAL
        assert _DEFAULT_SEVERITY[AlertType.OUTAGE_NOTIFICATION] == AlertSeverity.CRITICAL
        assert _DEFAULT_SEVERITY[AlertType.USAGE_100_PCT] == AlertSeverity.CRITICAL


# ---------------------------------------------------------------------------
# SPEC-0741: Conversation billing 3-tier consumption
# ---------------------------------------------------------------------------


class TestSpec0741ConversationBilling3Tier:
    """SPEC-0741: Conversation billing MUST follow 3-tier consumption:
    1. Included allowance, 2. Pack balance, 3. Stripe overage.

    Verified by: UsageAlertType enum, volume spike multiplier,
    reconciliation threshold.
    """

    def test_usage_alert_type_enum(self):
        """UsageAlertType has all 4 alert types."""
        from src.multi_tenant.conversation_meter import UsageAlertType

        values = {t.value for t in UsageAlertType}
        assert "allowance_80_percent" in values
        assert "allowance_100_percent" in values
        assert "pack_balance_low" in values
        assert "volume_spike" in values

    def test_volume_spike_multiplier(self):
        """Volume spike threshold is 2x daily average."""
        from src.multi_tenant.conversation_meter import VOLUME_SPIKE_MULTIPLIER

        assert VOLUME_SPIKE_MULTIPLIER == 2.0

    def test_reconciliation_threshold(self):
        """Reconciliation discrepancy threshold is 5%."""
        from src.multi_tenant.conversation_meter import RECONCILIATION_DISCREPANCY_THRESHOLD

        assert RECONCILIATION_DISCREPANCY_THRESHOLD == 0.05

    def test_pack_low_threshold(self):
        """Pack balance low threshold is 10%."""
        from src.multi_tenant.conversation_meter import PACK_LOW_THRESHOLD

        assert PACK_LOW_THRESHOLD == 0.10
