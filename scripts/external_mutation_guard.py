"""External mutation authorization guard for GT-KB.

This module classifies proposed external side effects before execution. It is a
pure decision layer: it does not call external systems, read credentials, write
receipts, mutate bridge state, or inspect the filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts.post_action_receipt import MUTATION_CLASSES

ACTION_CLOUD_DEPLOYMENT = "cloud_deployment"
ACTION_EXTERNAL_SERVICE = "external_service"
ACTION_HOSTED_APPLICATION = "hosted_application"
ACTION_THIRD_PARTY_API = "third_party_api"
ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM = "credentials_adjacent_external_system"

EXTERNAL_ACTION_CLASSES = frozenset(
    {
        ACTION_CLOUD_DEPLOYMENT,
        ACTION_EXTERNAL_SERVICE,
        ACTION_HOSTED_APPLICATION,
        ACTION_THIRD_PARTY_API,
        ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM,
    }
)

RECEIPT_COMPATIBILITY = {
    ACTION_CLOUD_DEPLOYMENT: frozenset({"cloud_deployment"}),
    ACTION_EXTERNAL_SERVICE: frozenset({"external_service"}),
    ACTION_HOSTED_APPLICATION: frozenset({"external_service"}),
    ACTION_THIRD_PARTY_API: frozenset({"external_service"}),
    ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM: frozenset({"external_service"}),
}

BRIDGE_REQUIRED_ACTIONS = EXTERNAL_ACTION_CLASSES
GO_STATUS = "GO"


@dataclass(frozen=True)
class ExternalAuthority:
    """Owner-visible authority and provenance for a proposed external action."""

    initiating_authority: str = ""
    project_authorization_id: str = ""
    work_item_id: str = ""
    bridge_thread: str = ""
    bridge_version: str = ""
    bridge_status: str = ""
    owner_approval_id: str = ""
    owner_deliberation_id: str = ""
    author_identity: str = ""
    author_harness_id: str = ""
    author_session_context_id: str = ""
    author_model: str = ""
    production_deployment_approved: bool = False
    credential_lifecycle_approved: bool = False
    p_auth_forbids_production_deployment: bool = True
    p_auth_forbids_credential_lifecycle_change: bool = True


@dataclass(frozen=True)
class ReceiptPlan:
    """Required post-action receipt plan for an allowed external action."""

    mutation_class: str
    target_systems: tuple[str, ...] = ()
    verification_evidence_expectation: str = ""
    receipt_required_before_completion: bool = True


@dataclass(frozen=True)
class ExternalGuardDecision:
    """Structured allow/deny decision returned before an external side effect."""

    allowed: bool
    reason_code: str
    details: str
    required_receipt_mutation_class: str = ""
    required_receipt_targets: tuple[str, ...] = ()
    required_follow_up_evidence: tuple[str, ...] = ()
    bridge_thread: str = ""
    bridge_version: str = ""
    work_item_id: str = ""


def _clean(value: object) -> str:
    return str(value or "").strip()


def _authority_present(authority: ExternalAuthority) -> bool:
    return any(
        _clean(value)
        for value in (
            authority.initiating_authority,
            authority.project_authorization_id,
            authority.owner_approval_id,
            authority.owner_deliberation_id,
        )
    )


def _has_harness_provenance(authority: ExternalAuthority) -> bool:
    return all(
        _clean(value)
        for value in (
            authority.author_identity,
            authority.author_harness_id,
            authority.author_session_context_id,
            authority.author_model,
        )
    )


def _has_bridge_go(authority: ExternalAuthority) -> bool:
    return (
        bool(_clean(authority.bridge_thread))
        and bool(_clean(authority.bridge_version))
        and _clean(authority.bridge_status).upper() == GO_STATUS
    )


def _has_explicit_production_approval(authority: ExternalAuthority) -> bool:
    return authority.production_deployment_approved or bool(_clean(authority.owner_approval_id))


def _has_explicit_credential_approval(authority: ExternalAuthority) -> bool:
    return authority.credential_lifecycle_approved or bool(_clean(authority.owner_approval_id))


def evaluate_external_action(
    action_class: str,
    *,
    authority: ExternalAuthority | None,
    receipt_plan: ReceiptPlan | None,
    production: bool = False,
    credential_lifecycle_change: bool = False,
    bridge_required: bool = True,
) -> ExternalGuardDecision:
    """Return a fail-closed decision for a proposed external action.

    The caller is responsible for executing any side effect only after an
    allowed decision and for writing the receipt required by the returned plan.
    """

    normalized_action = _clean(action_class)
    if normalized_action not in EXTERNAL_ACTION_CLASSES:
        return ExternalGuardDecision(
            allowed=False,
            reason_code="unknown_action_class",
            details=f"Unsupported external action class: {normalized_action or '<empty>'}",
        )

    if authority is None or not _authority_present(authority):
        return ExternalGuardDecision(
            allowed=False,
            reason_code="missing_authority",
            details="External actions require owner-visible initiating authority.",
        )

    if bridge_required and normalized_action in BRIDGE_REQUIRED_ACTIONS and not _has_bridge_go(authority):
        return ExternalGuardDecision(
            allowed=False,
            reason_code="missing_bridge_go",
            details="External action requires current bridge GO thread and version evidence.",
            bridge_thread=authority.bridge_thread,
            bridge_version=authority.bridge_version,
            work_item_id=authority.work_item_id,
        )

    if not _has_harness_provenance(authority):
        return ExternalGuardDecision(
            allowed=False,
            reason_code="missing_harness_provenance",
            details="External actions require author identity, harness id, session context, and model provenance.",
            bridge_thread=authority.bridge_thread,
            bridge_version=authority.bridge_version,
            work_item_id=authority.work_item_id,
        )

    if production:
        if not _has_explicit_production_approval(authority):
            return ExternalGuardDecision(
                allowed=False,
                reason_code="production_deployment_requires_owner_approval",
                details="Production deployment requires explicit owner approval before classification can allow it.",
                bridge_thread=authority.bridge_thread,
                bridge_version=authority.bridge_version,
                work_item_id=authority.work_item_id,
            )
        if authority.p_auth_forbids_production_deployment:
            return ExternalGuardDecision(
                allowed=False,
                reason_code="production_deployment_prohibited",
                details="The active project authorization forbids production deployment in this scope.",
                bridge_thread=authority.bridge_thread,
                bridge_version=authority.bridge_version,
                work_item_id=authority.work_item_id,
            )

    credentials_adjacent = normalized_action == ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM
    if credential_lifecycle_change or credentials_adjacent:
        if not _has_explicit_credential_approval(authority):
            return ExternalGuardDecision(
                allowed=False,
                reason_code="credential_lifecycle_requires_owner_approval",
                details="Credential lifecycle or credentials-adjacent external actions require explicit owner approval.",
                bridge_thread=authority.bridge_thread,
                bridge_version=authority.bridge_version,
                work_item_id=authority.work_item_id,
            )
        if authority.p_auth_forbids_credential_lifecycle_change:
            return ExternalGuardDecision(
                allowed=False,
                reason_code="credential_lifecycle_prohibited",
                details="The active project authorization forbids credential lifecycle changes in this scope.",
                bridge_thread=authority.bridge_thread,
                bridge_version=authority.bridge_version,
                work_item_id=authority.work_item_id,
            )

    if receipt_plan is None:
        return ExternalGuardDecision(
            allowed=False,
            reason_code="missing_receipt_plan",
            details="External actions require a post-action receipt plan.",
            bridge_thread=authority.bridge_thread,
            bridge_version=authority.bridge_version,
            work_item_id=authority.work_item_id,
        )

    if (
        not receipt_plan.receipt_required_before_completion
        or not receipt_plan.target_systems
        or not _clean(receipt_plan.verification_evidence_expectation)
    ):
        return ExternalGuardDecision(
            allowed=False,
            reason_code="missing_receipt_plan",
            details="Receipt plan must require a receipt, target at least one system, and state expected evidence.",
            bridge_thread=authority.bridge_thread,
            bridge_version=authority.bridge_version,
            work_item_id=authority.work_item_id,
        )

    compatible_classes = RECEIPT_COMPATIBILITY[normalized_action]
    if receipt_plan.mutation_class not in MUTATION_CLASSES or receipt_plan.mutation_class not in compatible_classes:
        return ExternalGuardDecision(
            allowed=False,
            reason_code="incompatible_receipt_mutation_class",
            details=(
                f"Receipt mutation class {receipt_plan.mutation_class!r} is not compatible with "
                f"external action class {normalized_action!r}."
            ),
            bridge_thread=authority.bridge_thread,
            bridge_version=authority.bridge_version,
            work_item_id=authority.work_item_id,
        )

    return ExternalGuardDecision(
        allowed=True,
        reason_code="authorized",
        details="External action classification is authorized; caller must emit the planned receipt after execution.",
        required_receipt_mutation_class=receipt_plan.mutation_class,
        required_receipt_targets=receipt_plan.target_systems,
        required_follow_up_evidence=("post_action_receipt", receipt_plan.verification_evidence_expectation),
        bridge_thread=authority.bridge_thread,
        bridge_version=authority.bridge_version,
        work_item_id=authority.work_item_id,
    )


__all__ = [
    "ACTION_CLOUD_DEPLOYMENT",
    "ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM",
    "ACTION_EXTERNAL_SERVICE",
    "ACTION_HOSTED_APPLICATION",
    "ACTION_THIRD_PARTY_API",
    "EXTERNAL_ACTION_CLASSES",
    "ExternalAuthority",
    "ExternalGuardDecision",
    "ReceiptPlan",
    "evaluate_external_action",
]
