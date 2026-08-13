from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from groundtruth_kb.governance.project_authorization_operation_time import (
    TaxonomyError,
    classify_target,
    evaluate_envelope,
    load_operation_taxonomy,
    normalize_mutation_class,
    normalized_envelope_hash,
)

NOW = datetime(2026, 7, 13, tzinfo=UTC)


def _taxonomy_with_suffix(tmp_path: Path, suffix: str):
    current = load_operation_taxonomy()
    target = tmp_path / "config/governance/project-authorization-operation-taxonomy.toml"
    target.parent.mkdir(parents=True)
    target.write_text(Path(current.source_path).read_text(encoding="utf-8") + suffix, encoding="utf-8")
    return load_operation_taxonomy(tmp_path)


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


def test_governed_githooks_rule_classifies_slash_forms_and_authorizes_configuration() -> None:
    taxonomy = load_operation_taxonomy()
    assert taxonomy.taxonomy_version == "2"
    # Exact-equality pin on the COMPLETE registered rule set: any rule added to the
    # taxonomy must consciously update this list. WI-6196 added the .goosehints rule,
    # which classifies the Goose harness hint file as configuration so proposals may
    # declare it in target_paths.
    assert [(rule.pattern, rule.mutation_class) for rule in taxonomy.path_rules] == [
        (".githooks/**", "configuration"),
        (".goosehints", "configuration"),
    ]
    assert classify_target(".githooks/pre-commit", taxonomy).mutation_class == "configuration"
    assert classify_target(r".githooks\pre-commit", taxonomy).mutation_class == "configuration"
    assert classify_target("nested/.githooks/pre-commit", taxonomy).mutation_class == "unclassified"

    allowed = evaluate_envelope(
        _authorization(allowed=["configuration"]),
        requested_operation="protected_mutation",
        target_paths=[".githooks/pre-commit"],
        decision_time=NOW,
        taxonomy=taxonomy,
    )
    denied = evaluate_envelope(
        _authorization(allowed=["source"]),
        requested_operation="protected_mutation",
        target_paths=[".githooks/pre-commit"],
        decision_time=NOW,
        taxonomy=taxonomy,
    )
    assert allowed.allowed is True
    assert denied.allowed is False
    assert denied.reason_code == "target_mutation_class_not_allowed"


@pytest.mark.parametrize(
    "suffix",
    [
        '\n[[path_rule]]\npattern = ".other/**"\nmutation_class = "unknown"\n',
        '\n[[path_rule]]\npattern = ".githooks/**"\nmutation_class = "source"\n',
        '\n[[path_rule]]\npattern = "../.other/**"\nmutation_class = "source"\n',
    ],
)
def test_path_rule_loader_rejects_unknown_duplicate_or_non_root_rule(tmp_path: Path, suffix: str) -> None:
    with pytest.raises(TaxonomyError):
        _taxonomy_with_suffix(tmp_path, suffix)


def test_overlapping_governed_path_rule_classes_fail_closed(tmp_path: Path) -> None:
    taxonomy = _taxonomy_with_suffix(
        tmp_path,
        '\n[[path_rule]]\npattern = ".githooks/pre-*"\nmutation_class = "source"\n',
    )
    assert classify_target(".githooks/pre-commit", taxonomy).mutation_class == "unclassified"


def test_transient_index_target_classification_is_exact_and_case_preserving() -> None:
    assert classify_target(".gtkb-index-hl705ij2/index").mutation_class == "repository_metadata"
    assert classify_target(r".gtkb-index-hl705ij2\index").mutation_class == "repository_metadata"

    expected = {
        ".gtkb-index-HL705IJ2/index": "unclassified",
        ".gtkb-index-short/index": "unclassified",
        ".gtkb-index-hl705ij20/index": "unclassified",
        ".gtkb-index-hl705ij2/": "unclassified",
        "nested/.gtkb-index-hl705ij2/index": "unclassified",
        ".gtkb-index-hl705ij2//index": "unclassified",
        "../.gtkb-index-hl705ij2/index": "unclassified",
        ".gtkb-index-hl705ij2/index.md": "governance_evidence",
        ".gtkb-index-hl705ij2/index.json": "governance_evidence",
        ".gtkb-index-hl705ij2/index.jsonl": "governance_evidence",
    }
    for path, expected_class in expected.items():
        actual = classify_target(path).mutation_class
        assert actual == expected_class, path
        assert actual != "repository_metadata", path


def test_transient_index_matcher_pins_cpython_private_name_contract() -> None:
    expected_characters = "abcdefghijklmnopqrstuvwxyz0123456789_"
    assert tempfile._RandomNameSequence.characters == expected_characters

    sequence = tempfile._RandomNameSequence()
    samples = [next(sequence) for _ in range(128)]
    assert all(len(sample) == 8 for sample in samples)
    assert all(set(sample) <= set(expected_characters) for sample in samples)
    assert all(
        classify_target(f".gtkb-index-{sample}/index").mutation_class == "repository_metadata" for sample in samples
    )


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
