"""Tests for scripts/external_mutation_guard.py."""

from __future__ import annotations

from pathlib import Path

from scripts.external_mutation_guard import (
    ACTION_CLOUD_DEPLOYMENT,
    ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM,
    ACTION_EXTERNAL_SERVICE,
    ExternalAuthority,
    ReceiptPlan,
    evaluate_external_action,
)


def _authority(**overrides: object) -> ExternalAuthority:
    values = {
        "initiating_authority": "PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA",
        "project_authorization_id": "PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA",
        "work_item_id": "WI-4589",
        "bridge_thread": "agent-disposition-wi4589-external-mutation-gate-slice1",
        "bridge_version": "002",
        "bridge_status": "GO",
        "author_identity": "prime-builder/codex/A",
        "author_harness_id": "A",
        "author_session_context_id": "session-123",
        "author_model": "gpt-5-codex",
    }
    values.update(overrides)
    return ExternalAuthority(**values)


def _receipt(**overrides: object) -> ReceiptPlan:
    values = {
        "mutation_class": "external_service",
        "target_systems": ("sandbox-api",),
        "verification_evidence_expectation": "receipt JSON plus caller verification command",
        "receipt_required_before_completion": True,
    }
    values.update(overrides)
    return ReceiptPlan(**values)


def test_unknown_action_class_denies_with_stable_reason_code() -> None:
    decision = evaluate_external_action("unknown", authority=_authority(), receipt_plan=_receipt())

    assert decision.allowed is False
    assert decision.reason_code == "unknown_action_class"


def test_missing_owner_visible_authority_denies() -> None:
    decision = evaluate_external_action(
        ACTION_EXTERNAL_SERVICE,
        authority=_authority(
            initiating_authority="",
            project_authorization_id="",
            owner_approval_id="",
            owner_deliberation_id="",
        ),
        receipt_plan=_receipt(),
    )

    assert decision.allowed is False
    assert decision.reason_code == "missing_authority"


def test_missing_bridge_go_denies_when_bridge_required() -> None:
    decision = evaluate_external_action(
        ACTION_EXTERNAL_SERVICE,
        authority=_authority(bridge_status="NO-GO"),
        receipt_plan=_receipt(),
    )

    assert decision.allowed is False
    assert decision.reason_code == "missing_bridge_go"


def test_missing_harness_provenance_denies() -> None:
    decision = evaluate_external_action(
        ACTION_EXTERNAL_SERVICE,
        authority=_authority(author_session_context_id=""),
        receipt_plan=_receipt(),
    )

    assert decision.allowed is False
    assert decision.reason_code == "missing_harness_provenance"


def test_production_deployment_requires_explicit_owner_approval() -> None:
    decision = evaluate_external_action(
        ACTION_CLOUD_DEPLOYMENT,
        authority=_authority(),
        receipt_plan=_receipt(mutation_class="cloud_deployment"),
        production=True,
    )

    assert decision.allowed is False
    assert decision.reason_code == "production_deployment_requires_owner_approval"


def test_production_deployment_remains_prohibited_in_active_pauth_scope() -> None:
    decision = evaluate_external_action(
        ACTION_CLOUD_DEPLOYMENT,
        authority=_authority(owner_approval_id="AUQ-123", production_deployment_approved=True),
        receipt_plan=_receipt(mutation_class="cloud_deployment"),
        production=True,
    )

    assert decision.allowed is False
    assert decision.reason_code == "production_deployment_prohibited"


def test_credential_lifecycle_action_requires_owner_approval() -> None:
    decision = evaluate_external_action(
        ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM,
        authority=_authority(),
        receipt_plan=_receipt(),
    )

    assert decision.allowed is False
    assert decision.reason_code == "credential_lifecycle_requires_owner_approval"


def test_credential_lifecycle_remains_prohibited_in_active_pauth_scope() -> None:
    decision = evaluate_external_action(
        ACTION_CREDENTIALS_ADJACENT_EXTERNAL_SYSTEM,
        authority=_authority(owner_approval_id="AUQ-456", credential_lifecycle_approved=True),
        receipt_plan=_receipt(),
    )

    assert decision.allowed is False
    assert decision.reason_code == "credential_lifecycle_prohibited"


def test_missing_receipt_plan_denies() -> None:
    decision = evaluate_external_action(ACTION_EXTERNAL_SERVICE, authority=_authority(), receipt_plan=None)

    assert decision.allowed is False
    assert decision.reason_code == "missing_receipt_plan"


def test_incomplete_receipt_plan_denies() -> None:
    decision = evaluate_external_action(
        ACTION_EXTERNAL_SERVICE,
        authority=_authority(),
        receipt_plan=_receipt(target_systems=()),
    )

    assert decision.allowed is False
    assert decision.reason_code == "missing_receipt_plan"


def test_incompatible_receipt_mutation_class_denies() -> None:
    decision = evaluate_external_action(
        ACTION_EXTERNAL_SERVICE,
        authority=_authority(),
        receipt_plan=_receipt(mutation_class="cloud_deployment"),
    )

    assert decision.allowed is False
    assert decision.reason_code == "incompatible_receipt_mutation_class"


def test_non_production_external_service_allows_with_full_evidence() -> None:
    decision = evaluate_external_action(ACTION_EXTERNAL_SERVICE, authority=_authority(), receipt_plan=_receipt())

    assert decision.allowed is True
    assert decision.reason_code == "authorized"
    assert decision.required_receipt_mutation_class == "external_service"
    assert decision.required_receipt_targets == ("sandbox-api",)
    assert decision.required_follow_up_evidence == (
        "post_action_receipt",
        "receipt JSON plus caller verification command",
    )
    assert decision.bridge_thread == "agent-disposition-wi4589-external-mutation-gate-slice1"
    assert decision.bridge_version == "002"
    assert decision.work_item_id == "WI-4589"


def test_decision_evaluation_does_not_mutate_filesystem(tmp_path: Path) -> None:
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    decision = evaluate_external_action(ACTION_EXTERNAL_SERVICE, authority=_authority(), receipt_plan=_receipt())

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert decision.allowed is True
    assert after == before
