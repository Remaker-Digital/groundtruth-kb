from __future__ import annotations

from datetime import UTC, datetime

from groundtruth_kb.governance.project_authorization_operation_time import (
    classify_target,
    evaluate_envelope,
    load_operation_taxonomy,
    normalize_mutation_class,
    normalized_envelope_hash,
)

NOW = datetime(2026, 7, 13, tzinfo=UTC)


def _authorization(
    *,
    allowed: list[str] | None = None,
    forbidden: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": "PAUTH-FIXTURE",
        "version": 3,
        "project_id": "PROJECT-FIXTURE",
        "status": "active",
        "owner_decision_deliberation_id": "DELIB-FIXTURE",
        "expires_at": "2026-08-01T00:00:00Z",
        "supersedes": None,
        "superseded_by": None,
        "allowed_mutation_classes": allowed or ["source", "test_addition"],
        "forbidden_operations": forbidden or [],
        "included_work_item_ids": ["WI-FIXTURE"],
        "excluded_work_item_ids": [],
        "included_spec_ids": ["SPEC-FIXTURE"],
        "excluded_spec_ids": [],
    }


def test_target_taxonomy_assigns_one_stable_class() -> None:
    taxonomy = load_operation_taxonomy()
    assert taxonomy.evaluator_id == "project-authorization-operation-time-enforcement"
    assert classify_target("scripts/example.py").mutation_class == "source"
    assert classify_target("platform_tests/scripts/test_example.py").mutation_class == "test"
    assert classify_target("config/example.toml").mutation_class == "configuration"
    assert classify_target(".gitattributes").mutation_class == "repository_metadata"
    assert classify_target("bridge/example-001.md").mutation_class == "bridge"


def test_bridge_metadata_only_envelope_cannot_authorize_source() -> None:
    decision = evaluate_envelope(
        _authorization(allowed=["bridge", "metadata"]),
        requested_operation="implementation-packet-create",
        target_paths=["scripts/example.py"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "target_mutation_class_not_allowed"
    assert decision.classified_targets[0].mutation_class == "source"


def test_forbidden_operation_precedes_allowed_target_class() -> None:
    decision = evaluate_envelope(
        _authorization(forbidden=["implementation_packet_create"]),
        requested_operation="implementation-packet-create",
        target_paths=["scripts/example.py"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "forbidden_operation"


def test_unknown_operation_fails_closed() -> None:
    decision = evaluate_envelope(
        _authorization(),
        requested_operation="invented-side-effect",
        target_paths=["scripts/example.py"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "unknown_operation"


def test_unclassified_target_fails_closed() -> None:
    decision = evaluate_envelope(
        _authorization(allowed=["metadata"]),
        requested_operation="protected_mutation",
        target_paths=["unknown-target.bin"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "target_mutation_class_not_allowed"
    assert decision.classified_targets[0].mutation_class == "unclassified"


def test_unregistered_negative_word_class_does_not_grant_source_authority() -> None:
    decision = evaluate_envelope(
        _authorization(allowed=["no_source_changes"]),
        requested_operation="protected_mutation",
        target_paths=["scripts/example.py"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "unknown_mutation_class"


def test_unregistered_source_prefix_does_not_grant_source_authority() -> None:
    assert normalize_mutation_class("source_changes_forbidden") is None


def test_unknown_free_form_forbidden_operation_invalidates_envelope() -> None:
    decision = evaluate_envelope(
        _authorization(forbidden=["do not make unrelated changes"]),
        requested_operation="implementation_packet_create",
        target_paths=["scripts/example.py"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "unknown_forbidden_operation"


def test_registered_deployment_alias_is_forbidden() -> None:
    decision = evaluate_envelope(
        _authorization(forbidden=["production-deploy"]),
        requested_operation="production_deployment",
        target_paths=["scripts/example.py"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "forbidden_operation"


def test_retirement_reconciliation_does_not_grant_source_authority() -> None:
    decision = evaluate_envelope(
        _authorization(allowed=["project_retirement_reconciliation"]),
        requested_operation="protected_mutation",
        target_paths=["scripts/example.py"],
        decision_time=NOW,
    )

    assert decision.allowed is False
    assert decision.reason_code == "target_mutation_class_not_allowed"


def test_bounded_envelope_produces_machine_readable_allow() -> None:
    decision = evaluate_envelope(
        _authorization(),
        requested_operation="implementation_packet_create",
        target_paths=["scripts/example.py", "platform_tests/scripts/test_example.py"],
        decision_time=NOW,
    )

    payload = decision.as_dict()
    assert payload["allowed"] is True
    assert payload["reason_code"] == "allowed"
    assert payload["authorization_version"] == 3
    assert payload["normalized_operation"] == "implementation_packet_create"
    assert payload["evaluator_version"] == "1"
    assert len(payload["evaluator_sha256"]) == 64
    assert len(payload["taxonomy_sha256"]) == 64
    assert payload["decision_time"] == "2026-07-13T00:00:00Z"


def test_all_work_intent_operations_are_registered_and_allowed_by_default() -> None:
    for operation in (
        "work_intent_acquire",
        "work_intent_renew",
        "work_intent_reclassify",
        "work_intent_extend",
    ):
        decision = evaluate_envelope(
            _authorization(),
            requested_operation=operation,
            target_paths=["scripts/example.py"],
            decision_time=NOW,
        )
        assert decision.allowed is True
        assert decision.normalized_operation == operation


def test_envelope_hash_is_deterministic_and_changes_on_scope_drift() -> None:
    original = _authorization()
    reordered = dict(reversed(list(original.items())))
    reordered["allowed_mutation_classes"] = list(reversed(original["allowed_mutation_classes"]))
    drifted = {**original, "allowed_mutation_classes": ["bridge", "metadata"]}

    assert normalized_envelope_hash(original) == normalized_envelope_hash(reordered)
    assert normalized_envelope_hash(original) != normalized_envelope_hash(drifted)
