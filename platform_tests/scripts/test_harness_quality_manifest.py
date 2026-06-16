from __future__ import annotations

from dataclasses import replace

from scripts.benchmarks import harness_quality_manifest as manifest


def test_manifest_is_valid() -> None:
    assert manifest.validate_manifest() == []
    assert manifest.require_valid_manifest() is manifest.HARNESS_QUALITY_MANIFEST


def test_benchmark_modes_are_cross_role_and_do_not_change_durable_roles() -> None:
    modes = {mode.id: mode for mode in manifest.BENCHMARK_MODES}

    assert set(modes) == {"prime_builder", "loyal_opposition"}
    assert all(mode.durable_role_changes_allowed is False for mode in modes.values())
    assert "implementation-start" in modes["prime_builder"].expected_behavior
    assert "GO/NO-GO/VERIFIED" in modes["loyal_opposition"].expected_behavior


def test_owner_decision_coverage_is_exact() -> None:
    assert manifest.OWNER_DECISION_IDS == (
        "DELIB-20263440",
        "DELIB-20263441",
        "DELIB-20263442",
        "DELIB-20263443",
        "DELIB-20263444",
        "DELIB-20263445",
        "DELIB-20263446",
        "DELIB-20263447",
    )
    assert set(manifest.OWNER_DECISION_IDS) <= set(manifest.HARNESS_QUALITY_MANIFEST.owner_decision_ids)


def test_safety_invariants_forbid_live_mutations_and_enforcement() -> None:
    invariant_ids = {item.id for item in manifest.SAFETY_INVARIANTS}

    assert set(manifest.SAFETY_INVARIANT_IDS) <= invariant_ids
    assert "no_live_cloud_mutation" in invariant_ids
    assert "no_live_deployment_mutation" in invariant_ids
    assert "no_credential_lifecycle_action" in invariant_ids
    assert "no_production_application_mutation" in invariant_ids
    assert "no_durable_role_assignment_change" in invariant_ids
    assert "no_live_bridge_backlog_spec_challenge_mutation" in invariant_ids
    assert "no_dispatcher_ranking_or_eligibility_enforcement" in invariant_ids


def test_evidence_schema_has_required_fields() -> None:
    fields = set(manifest.HARNESS_QUALITY_MANIFEST.evidence_fields)

    for required in (
        "harness_id",
        "benchmark_mode",
        "provider",
        "model",
        "dispatch_envelope_id",
        "fixture_id",
        "run_tier",
        "started_at",
        "ended_at",
        "duration_ms",
        "input_tokens",
        "output_tokens",
        "estimated_cost",
        "deterministic_score",
        "adjudication_score",
        "outcome",
        "verdict",
        "failure_class",
        "required_source_citations",
        "artifact_links",
    ):
        assert required in fields


def test_challenge_families_are_gtkb_native_and_scored() -> None:
    family_ids = {family.id for family in manifest.CHALLENGE_FAMILIES}

    assert {
        "role_adoption",
        "bridge_protocol_compliance",
        "implementation_start_safety",
        "review_verdict_quality",
        "proposal_report_correctness",
        "source_citation_quality",
        "direct_mutation_refusal",
        "cli_first_operation",
        "fixture_isolation",
        "responsiveness_reliability_cost",
        "future_enforcement_readiness",
    } <= family_ids
    for family in manifest.CHALLENGE_FAMILIES:
        assert family.source_material_categories
        assert family.expected_evidence
        assert family.scoring_dimensions
        assert set(family.scoring_dimensions) <= set(manifest.SCORING_DIMENSIONS)
        assert family.deterministic_evidence or family.adjudication_rationale


def test_run_tiers_distinguish_smoke_full_and_adjudicated_calibration() -> None:
    tiers = {tier.id: tier for tier in manifest.RUN_TIERS}

    assert set(tiers) == {"smoke", "full_quality", "adjudicated_calibration"}
    assert tiers["smoke"].expected_cost_profile == "low"
    assert tiers["full_quality"].expected_cost_profile == "medium"
    assert tiers["adjudicated_calibration"].includes_adjudication is True


def test_dispatcher_bridge_cli_contract_is_declared_without_runner() -> None:
    requirements = " ".join(manifest.DISPATCHER_BRIDGE_CLI_REQUIREMENTS)

    assert "Dispatcher/Bridge CLI" in requirements
    assert "direct artifact mutation" in requirements
    assert not hasattr(manifest, "run")
    assert not hasattr(manifest, "main")


def test_validation_rejects_missing_decision_field_and_duplicate_family() -> None:
    duplicate_family = manifest.CHALLENGE_FAMILIES[0]
    bad_manifest = replace(
        manifest.HARNESS_QUALITY_MANIFEST,
        owner_decision_ids=manifest.OWNER_DECISION_IDS[:-1],
        evidence_fields=manifest.REQUIRED_EVIDENCE_FIELDS[:-1],
        challenge_families=manifest.CHALLENGE_FAMILIES + (duplicate_family,),
    )

    errors = manifest.validate_manifest(bad_manifest)

    assert any("missing owner decision coverage" in error for error in errors)
    assert any("missing evidence fields" in error for error in errors)
    assert any("duplicate challenge_families ids" in error for error in errors)


def test_manifest_serializes_to_dict_after_validation() -> None:
    payload = manifest.manifest_to_dict()

    assert payload["owner_decision_ids"] == manifest.OWNER_DECISION_IDS
    assert payload["modes"][0]["id"] == "prime_builder"
    assert payload["challenge_families"]
