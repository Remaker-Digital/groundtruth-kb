"""Clause-exact modernization harness, assurance, and Git-lifecycle tests.

Local tests in this module prove only behavior available from production APIs.
Real harness invocations, historical observations, shadow operation, activation
slices, clean runs, and hosted promotion remain collector-receipt obligations.
"""

from __future__ import annotations

import functools
import hashlib
import json
import sys
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "groundtruth-kb" / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.activity.profiles import (  # noqa: E402
    CANONICAL_ACTIVITY_ORDER,
    load_activity_profiles,
)
from groundtruth_kb.bridge.disposition import disposition_for_status  # noqa: E402
from groundtruth_kb.context import manifest as context_manifest  # noqa: E402
from groundtruth_kb.context.freshness import evaluate_extract  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.git_lifecycle.models import OperationDenied  # noqa: E402
from groundtruth_kb.git_lifecycle.service import (  # noqa: E402
    GitLifecycleService,
    deterministic_work_branch,
)
from groundtruth_kb.session.envelope import (  # noqa: E402
    EnvelopeError,
    ensure_worker_session,
    open_session,
    open_topic,
    resolve_worker_role_provenance,
)

from scripts import check_artifact_evaluability as artifact_evaluability  # noqa: E402
from scripts import check_context_manifests as context_checker  # noqa: E402
from scripts import check_harness_parity as harness_checker  # noqa: E402
from scripts import check_modernization_git_lifecycle as git_acceptance  # noqa: E402
from scripts import check_modernization_nonimpairment as nonimpairment  # noqa: E402
from scripts import collect_modernization_semantic_evidence as collector  # noqa: E402
from scripts.benchmarks import activity_envelope_load  # noqa: E402

MANIFEST = json.loads(
    (ROOT / "config" / "governance" / "modernization-release-candidate.json").read_text(encoding="utf-8")
)
PRIMARY_HARNESSES = {"claude", "codex", "cursor", "antigravity"}
HEADLESS_HARNESSES = {"ollama", "openrouter", "alibaba-cloud-studio"}
ACTIVITIES = set(CANONICAL_ACTIVITY_ORDER)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def _seed_harness_state(root: Path, roles: dict[str, tuple[str, str]]) -> None:
    identities = {name: {"id": harness_id} for name, (harness_id, _role) in roles.items()}
    registry = [
        {
            "id": harness_id,
            "harness_name": name,
            "harness_type": name,
            "status": "active",
            "role": [role],
        }
        for name, (harness_id, role) in roles.items()
    ]
    _write_json(root / "harness-state" / "harness-identities.json", {"schema_version": 1, "harnesses": identities})
    _write_json(root / "harness-state" / "harness-registry.json", {"schema_version": 1, "harnesses": registry})


@functools.lru_cache(maxsize=1)
def _parity_report() -> harness_checker.ParityReport:
    return harness_checker.check_harness_parity(ROOT, harness="all", include_all=True)


def _registry() -> dict[str, Any]:
    return tomllib.loads(
        (ROOT / "config" / "agent-control" / "harness-capability-registry.toml").read_text(encoding="utf-8")
    )


def _projection_rows() -> list[dict[str, Any]]:
    return json.loads((ROOT / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))["harnesses"]


def _plan(handle_id: str) -> collector.Plan:
    matches = [plan for plan in collector.PLANS if plan.handle_id == handle_id]
    assert len(matches) == 1, f"{handle_id} must have exactly one collector plan"
    return matches[0]


def _assert_hashed_reference(reference: dict[str, Any]) -> None:
    path = ROOT / str(reference["path"])
    assert path.is_file(), reference
    assert hashlib.sha256(path.read_bytes()).hexdigest().upper() == str(reference["sha256"]).upper()


def test_mod_hp01_registered_harness_audit_covers_every_required_behavioral_domain() -> None:
    """MOD-HP01: every registered harness and named audit domain is mechanically evaluated."""
    report = _parity_report()
    registered = {str(row["harness_name"]) for row in _projection_rows()}
    assert set(report.selected_harnesses) == registered
    assert not report.errors
    assert not [row for row in report.results if row.parity_class == "required" and row.state == "MISSING"]

    required_domains = {
        "prompt",
        "rule",
        "memory",
        "hook",
        "skill",
        "plugin",
        "mcp",
        "cli",
        "session_envelope",
        "activity_envelope",
        "result_envelope",
        "evidence",
    }
    declared_domains = {
        str(domain)
        for capability in _registry()["capabilities"]
        for domain in capability.get("audit_domains", [capability.get("kind")])
        if domain
    }
    assert required_domains <= declared_domains, (
        "the parity service cannot claim MOD-HP01 until every objective domain is a structured audit dimension; "
        f"missing={sorted(required_domains - declared_domains)}"
    )


def test_mod_hp02_normalized_worker_contract_exposes_all_required_behavioral_sections(tmp_path: Path) -> None:
    """MOD-HP02: session, role, activity, resource, access, degradation, and result are normalized."""
    _seed_harness_state(tmp_path, {"codex": ("A", "prime-builder")})
    envelope = open_session(
        tmp_path,
        harness_name="codex",
        session_id="mod-hp02-session",
        role="prime-builder",
        worker_role_source="dispatcher_composition",
        dispatch_run_id="mod-hp02-dispatch",
    )
    activity = open_topic(tmp_path, "build", harness_name="codex")
    normalized = {
        "session": envelope.get("session_contract"),
        "role": envelope.get("role_contract") or envelope.get("worker_role_provenance"),
        "activity": envelope.get("activity_contract") or activity,
        "resource": envelope.get("resource_contract"),
        "access": envelope.get("access_contract"),
        "degradation": envelope.get("degradation_contract"),
        "result": envelope.get("result_contract"),
    }
    assert all(normalized.values()), f"normalized minimum contract is incomplete: {normalized}"


@pytest.mark.parametrize(
    ("handle_id", "harness_name", "receipt_name", "expected_mode"),
    [
        ("MOD-HP03", "claude", "harness-claude-live", "native"),
        ("MOD-HP04", "codex", "harness-codex-live", "native"),
        ("MOD-HP05", "cursor", "harness-cursor-live", "native"),
        (
            "MOD-HP06",
            "antigravity",
            "harness-antigravity-optimized-startup",
            "optimized-startup",
        ),
    ],
    ids=["MOD-HP03-claude", "MOD-HP04-codex", "MOD-HP05-cursor", "MOD-HP06-antigravity"],
)
def test_mod_hp03_hp06_local_delivery_is_complete_and_live_proof_is_receipt_backed(
    handle_id: str,
    harness_name: str,
    receipt_name: str,
    expected_mode: str,
) -> None:
    """MOD-HP03..06: static delivery is executable; verification remains a real-invocation receipt."""
    rows = [row for row in _parity_report().results if row.harness == harness_name]
    assert rows
    assert not [row for row in rows if row.parity_class == "required" and row.state == "MISSING"]
    projection = next(row for row in rows if row.capability_id == "activity_envelope.activity_envelope_projection_mode")
    assert projection.configured_status == expected_mode
    plan = _plan(handle_id)
    assert (plan.receipt_name, plan.kind, plan.harnesses) == (receipt_name, "live-harness", (harness_name,))


def test_mod_hp07_every_registered_headless_provider_has_static_conformance_and_live_receipt_route() -> None:
    """MOD-HP07: all registered headless providers have conformance and honest live-evidence routing."""
    rows = _projection_rows()
    registered = {
        str(row["harness_name"])
        for row in rows
        if str(row.get("harness_type")) in HEADLESS_HARNESSES or str(row.get("harness_name")) in HEADLESS_HARNESSES
    }
    assert registered == HEADLESS_HARNESSES
    report_rows = [row for row in _parity_report().results if row.harness in registered]
    assert {row.harness for row in report_rows} == registered
    assert not [row for row in report_rows if row.parity_class == "required" and row.state == "MISSING"]
    plan = _plan("MOD-HP07")
    assert plan.kind == "live-harness" and set(plan.harnesses) == registered


def test_mod_hp08_semantic_skill_drift_is_rejected_even_when_adapter_hash_metadata_is_current(tmp_path: Path) -> None:
    """MOD-HP08 negative: refreshed metadata must not hide behaviorally contradictory adapter content."""
    source_path = tmp_path / ".claude" / "skills" / "example" / "SKILL.md"
    adapter_path = tmp_path / ".codex" / "skills" / "example" / "SKILL.md"
    source_path.parent.mkdir(parents=True)
    adapter_path.parent.mkdir(parents=True)
    source = "---\nname: example\ndescription: example skill\n---\n\nDeny protected mutation without authority.\n"
    source_path.write_text(source, encoding="utf-8")
    source_hash = harness_checker._canonical_hash(source)
    adapter_path.write_text(
        "---\nname: example\ndescription: example skill\n---\n"
        "<!-- GTKB-CODEX-SKILL-ADAPTER\n"
        "Canonical source: .claude/skills/example/SKILL.md\n"
        f"Canonical source sha256: {source_hash}\n"
        "GTKB-CODEX-SKILL-ADAPTER -->\n\n"
        "Allow protected mutation without authority.\n",
        encoding="utf-8",
    )
    capability = {
        "id": "skill.example",
        "canonical_name": "example",
        "kind": "skill",
        "parity_class": "required",
        "required_for_roles": ["prime-builder"],
        "canonical_source": ".claude/skills/example/SKILL.md",
        "codex": {
            "status": "adapter",
            "surface": ".codex/skills/example/SKILL.md",
            "adapter_source": ".claude/skills/example/SKILL.md",
            "source_sha256": source_hash,
        },
    }
    result = harness_checker._status_for_surface(tmp_path, capability, "codex")
    assert result.state in {"MISSING", "STALE"}, "hash-current semantic contradiction was accepted"


def test_mod_hp09_operational_parity_models_every_discoverability_domain() -> None:
    """MOD-HP09: CLI, plugin, MCP, installation, availability, and recovery are executable dimensions."""
    required = {"cli", "plugin", "mcp", "installation", "service_availability", "recovery_route"}
    declared = {
        str(domain)
        for capability in _registry()["capabilities"]
        for domain in capability.get("operational_domains", [])
    }
    assert required <= declared, f"operational parity has no executable coverage for {sorted(required - declared)}"


def test_mod_hp12_confusion_corpus_plan_binds_scenarios_and_real_replays() -> None:
    """MOD-HP12: the collector must name the corpus scenarios replayed by three real harnesses."""
    plan = _plan("MOD-HP12")
    assert plan.kind == "live-harness" and set(plan.harnesses) == {"claude", "codex", "cursor"}
    assert plan.command and plan.required_assertions, (
        "live harness presence alone is not a confusion-corpus replay; bind executable corpus scenario IDs"
    )


def test_mod_hp13_fallback_is_explicit_degraded_and_cannot_replace_session_authority(tmp_path: Path) -> None:
    """MOD-HP13: fallbacks are observable and preserve explicit worker authority."""
    _seed_harness_state(tmp_path, {"codex": ("A", "prime-builder")})
    fallback = open_session(tmp_path, harness_name="codex", session_id="fallback-session")
    assert fallback["role_resolved"] == "prime-builder"
    assert fallback["role_resolution"]["authority_mode"] == "durable_registry_fallback"

    ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="explicit-worker-session",
        role="loyal-opposition",
        role_source="dispatcher_composition",
        dispatch_run_id="explicit-worker-dispatch",
    )
    authority = resolve_worker_role_provenance(
        tmp_path,
        current_session_id="explicit-worker-session",
        harness_name="codex",
    )
    assert authority["role"] == "loyal-opposition"
    with pytest.raises(EnvelopeError, match="missing|does not match"):
        resolve_worker_role_provenance(
            tmp_path,
            current_session_id="unrelated-session",
            harness_name="codex",
        )

    degraded = [row for row in _parity_report().results if row.harness == "codex" and row.state == "DEGRADED"]
    assert degraded and all(row.configured_status == "fallback" and row.note for row in degraded)


def test_mod_hp14_verification_matrix_executes_each_named_contract_class(tmp_path: Path) -> None:
    """MOD-HP14: aggregate verification covers all nine named behavioral classes."""
    _seed_harness_state(tmp_path, {"codex": ("A", "prime-builder")})
    session = ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="mod-hp14-session",
        role="prime-builder",
        role_source="dispatcher_composition",
        dispatch_run_id="mod-hp14-dispatch",
    )
    activity = open_topic(tmp_path, "test", harness_name="codex")
    report = _parity_report()
    profiles = load_activity_profiles()
    codex_rows = [row for row in report.results if row.harness == "codex"]
    coverage = {
        "contract": bool(codex_rows),
        "semantic": any(row.capability_id.startswith("skill.") and row.state == "PASS" for row in codex_rows),
        "resource": bool(profiles["test"].skills and profiles["test"].history_state.get("sources")),
        "isolation": resolve_worker_role_provenance(
            tmp_path, current_session_id="mod-hp14-session", harness_name="codex"
        )["session_id"]
        == session["session_id"],
        "role": session["worker_role_provenance"]["role"] == "prime-builder",
        "activity": activity["type"] == "test" and bool(activity["route_target"]),
        "transcript": any(
            row.capability_id == "activity_envelope.full_transcript_archive_independence" and row.state == "PASS"
            for row in codex_rows
        ),
        "fallback": any(row.state == "DEGRADED" for row in codex_rows),
        "result_envelope": any(
            row.capability_id == "activity_envelope.compact_result_envelope_mode" and row.state == "PASS"
            for row in codex_rows
        ),
    }
    assert all(coverage.values()), coverage


def test_mod_as01_historical_baseline_is_reproducible_hashed_and_dimension_complete() -> None:
    """MOD-AS01: use actual pre-cutoff artifacts; never synthesize absent measurements."""
    measurement = collector.Collector(project_root=ROOT)._pre_baseline()
    assert measurement == collector.Collector(project_root=ROOT)._pre_baseline()
    assert set(measurement["dimensions"]) == {
        "transcripts",
        "payloads",
        "confusion",
        "tokens",
        "latency",
        "first_tool_behavior",
        "failures",
        "regressions",
    }
    assert datetime.fromisoformat(measurement["cutoff"]).astimezone(UTC) == datetime(2026, 7, 10, tzinfo=UTC)
    for name, reference in measurement["historical_sources"].items():
        if name == "session_envelopes":
            for session_reference in reference:
                _assert_hashed_reference(session_reference)
        else:
            _assert_hashed_reference(reference)
    for dimension in measurement["dimensions"].values():
        assert dimension.get("status") or dimension.get("passed") is not None


def test_mod_as02_every_governing_carrier_has_executable_current_evidence() -> None:
    """MOD-AS02: every stated governing carrier is registered and passes its executable assertions."""
    db = KnowledgeDB(ROOT / "groundtruth.db")
    try:
        carriers = [
            row
            for row in db.list_specs()
            if row.get("type") in artifact_evaluability.CHANGE_CONTROLLED_TYPES
            and row.get("authority") == "stated"
            and row.get("status") not in {"retired", "superseded"}
        ]
        report = artifact_evaluability.evaluate_specs(
            db,
            project_root=ROOT,
            spec_ids=[str(row["id"]) for row in carriers],
        )
    finally:
        db.close()
    assert carriers
    by_id = {str(row["subject_id"]): row for row in report["evaluations"]}
    assert set(by_id) == {str(row["id"]) for row in carriers}
    failures = {
        carrier_id: row["evaluation_reason"] for carrier_id, row in by_id.items() if row["carrier_result"] != "PASS"
    }
    assert not failures, f"hard-invariant registry is incomplete or non-current: {failures}"


def test_mod_as03_fresh_worker_simulator_accepts_only_generated_context_and_bounded_prompt() -> None:
    """MOD-AS03: the simulator is a production API with an enforced prompt bound."""
    simulator = getattr(context_manifest, "simulate_fresh_worker", None)
    assert callable(simulator), "fresh-worker behavior exists only in test helpers; provide a production simulator API"
    result = simulator(activity="build", role="Prime Builder", task_prompt="inspect one approved work item")
    assert result["context_origin"] in {"generated", "packaged_default"}
    assert result["task_prompt_bytes"] <= result["task_prompt_limit_bytes"]
    with pytest.raises((ValueError, context_manifest.ContextManifestError)):
        simulator(activity="build", role="Prime Builder", task_prompt="x" * (result["task_prompt_limit_bytes"] + 1))


def test_mod_as04_orientation_report_has_seven_by_five_executable_scenario_matrix() -> None:
    """MOD-AS04: every context category is exercised in positive/absent/stale/conflicting/degraded states."""
    report = context_checker.run_contract()
    expected_categories = set(context_manifest.REQUIRED_CATEGORIES)
    expected_states = {"positive", "absent", "stale", "conflicting", "degraded"}
    matrix = report.get("orientation_scenario_matrix")
    assert isinstance(matrix, dict), "context checker has no objective scenario matrix"
    assert set(matrix) == expected_categories
    assert all(set(matrix[category]) == expected_states for category in expected_categories)
    assert all(
        matrix[category][state].get("status") == "PASS" and matrix[category][state].get("evidence")
        for category in expected_categories
        for state in expected_states
    )


def test_mod_as05_six_activity_profiles_define_authority_actions_prohibitions_resources_routes_and_next_steps() -> None:
    """MOD-AS05: execute the complete six-activity behavior matrix."""
    profiles = load_activity_profiles()
    assert tuple(profiles) == CANONICAL_ACTIVITY_ORDER
    for name, profile in profiles.items():
        guardrails = [str(item).lower() for item in profile.direction.get("guardrails", [])]
        assert profile.headless_eligibility
        assert profile.direction.get("stance") and profile.direction.get("manipulates")
        assert any(token in guardrail for guardrail in guardrails for token in ("no ", "do not", "must", "requires"))
        assert profile.skills and profile.terminology and profile.history_state.get("sources")
        assert profile.classification["history_state"] == "explicit_query"
        assert profile.classification["direction"] == "activity_only"
        assert name in ACTIVITIES


def test_mod_as07_known_transcript_and_advisory_confusion_cases_replay_fail_closed(tmp_path: Path) -> None:
    """MOD-AS07: stale context, ambiguous role, and advisory-as-approval confusion stay closed."""
    now = datetime(2026, 7, 13, tzinfo=UTC)
    stale = evaluate_extract(
        {
            "source_id": "confusion-stale",
            "source_path": "groundtruth.db:current_specifications",
            "authority_class": "stated",
            "source_version_or_hash": "v1",
            "churn_class": "high",
            "generated_at": (now - timedelta(seconds=121)).isoformat(),
            "ttl_seconds": 120,
            "bounded_usage_context": "confusion-replay",
            "live_query_route": "gt spec show confusion-stale",
            "recovery_route": "gt spec show confusion-stale",
            "embedded_content": {"status": "specified"},
        },
        now=now,
    )
    assert stale["eligible_as_current"] is False

    _seed_harness_state(
        tmp_path,
        {"codex": ("A", "prime-builder"), "claude": ("B", "loyal-opposition")},
    )
    for name, role in (("codex", "prime-builder"), ("claude", "loyal-opposition")):
        ensure_worker_session(
            tmp_path,
            harness_name=name,
            session_id="confused-shared-session",
            role=role,
            role_source="dispatcher_composition",
            dispatch_run_id=f"confusion-{name}",
        )
    with pytest.raises(EnvelopeError, match="ambiguous"):
        resolve_worker_role_provenance(tmp_path, current_session_id="confused-shared-session")

    advisory = disposition_for_status("ADVISORY", "prime-builder")
    assert advisory.actionable is True
    assert advisory.dispatchable is False
    assert advisory.next_action == "owner_disposition"
    assert advisory.reason_code == "prime_advisory_disposition"


def test_mod_as08_nonimpairment_orchestrator_executes_every_named_regression_suite() -> None:
    """MOD-AS08: the orchestrator must run all thirteen objective suite classes."""
    required_suites = {
        "bridge",
        "dispatcher",
        "role",
        "project",
        "backlog",
        "git",
        "skill",
        "cli",
        "startup",
        "activity",
        "assertion",
        "doctor",
        "governance",
    }
    plan = _plan("MOD-AS08")
    configured = {item.strip().lower() for item in (plan.prerequisite or "").split(",") if item.strip()}
    assert required_suites <= configured, (
        "a single AT-HARD-INVARIANTS clean-run result is not the thirteen-suite non-impairment orchestrator; "
        f"missing={sorted(required_suites - configured)}"
    )


def test_mod_as09_live_repository_measurements_cover_every_required_dimension() -> None:
    """MOD-AS09: measure current context and actual dispatch telemetry without minting a receipt."""
    benchmark = activity_envelope_load.build_report(project_root=ROOT)
    assert benchmark["status"] in {"PASS", "WARN"}
    assert set(benchmark["activities"]) == ACTIVITIES
    assert all(row["explicit_query_source_count"] > 0 for row in benchmark["activities"].values())
    assert not benchmark["never_startup"]["missing_required_forbidden_payloads"]

    telemetry_dir = ROOT / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
    telemetry = [
        json.loads(path.read_text(encoding="utf-8")) for path in sorted(telemetry_dir.glob("*.telemetry.json"))
    ]
    usable = [
        row
        for row in telemetry
        if row.get("schema_id") == "gtkb.shim_dispatch_telemetry.v1"
        and isinstance(row.get("timing", {}).get("elapsed_ms"), int)
    ]
    statuses = {str(row.get("outcome", {}).get("exit_status")) for row in usable}
    assert len(usable) >= 2 and {"succeeded", "failed"} <= statuses
    assert benchmark["summary"]["global_surface_token_estimate"] > 0
    assert benchmark["summary"]["activity_auto_payload_token_estimate_total"] > 0


def test_mod_as11_threshold_service_requires_baseline_shadow_and_zero_tolerance_evidence() -> None:
    """MOD-AS11 local clause: threshold calibration depends on receipts and cannot relax hard failures."""
    plan = _plan("MOD-AS11")
    assert plan.kind == "dependent-receipts"
    missing_hard = nonimpairment.evaluate_evidence(
        {
            "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
            "primary_read_route": "gt status",
            "primary_mutation_route": "gt projects",
            "measurements": [{"id": "latency", "baseline": 5, "result": 4, "direction": "lower_or_equal"}],
            "rollback": {"instructions": "restore", "tested": True, "evidence": "receipt"},
            "hard_invariants": [],
            "worker_loading_paths": [],
            "superseded_guidance": [],
        }
    )
    assert missing_hard["status"] == "FAIL"
    assert any(row["severity"] == "P0" and row["id"] == "hard-invariant" for row in missing_hard["findings"])


def test_mod_as12_activation_slice_plan_requires_before_after_and_executed_rollback_evidence() -> None:
    """MOD-AS12: passing install/portability tests cannot substitute for an observed activation rollback."""
    plan = _plan("MOD-AS12")
    assert plan.kind == "activation-slice"
    assert set(plan.required_assertions) >= {"before", "after", "rollback_executed", "rollback_restored_baseline"}


def test_mod_as13_operational_observation_binds_activities_harnesses_promotion_and_quiescence() -> None:
    """MOD-AS13: recurrence evidence must cover every named dimension, not merely any successful run."""
    plan = _plan("MOD-AS13")
    assert plan.kind == "pilot-observation"
    assert set(plan.harnesses) == PRIMARY_HARNESSES
    assert set(plan.required_assertions) >= {
        *{f"activity:{name}" for name in ACTIVITIES},
        "branch_promotion",
        "bounded_quiescence",
        "recurrence",
    }


def test_mod_gl02_confirmed_intake_and_all_authority_clauses_execute(tmp_path: Path) -> None:
    """MOD-GL02: confirmed intake plus branch, promotion, commit, lease, recovery, and denial behavior."""
    db = KnowledgeDB(ROOT / "groundtruth.db")
    try:
        intake = db.get_deliberation("INTAKE-c5792b0c")
        requirement = db.get_spec("REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001")
    finally:
        db.close()
    assert intake is not None and requirement is not None
    content = json.loads(str(intake["content"]))
    assert content["intake_status"] == "confirmed"
    assert content["confirmed_spec_id"] == requirement["id"]
    assert intake["outcome"] == "owner_decision"

    assert deterministic_work_branch("WI-5158", "Git binding bootstrap").startswith("work-item/wi-5158-")
    for target in ("develop", "stage", "main"):
        with pytest.raises(OperationDenied, match="governed target branches") as denied:
            GitLifecycleService.validate_remote_push("work-item/wi-5158-git-binding-bootstrap", target)
        assert denied.value.code == "direct_push_prohibited"

    executable_clauses = {
        "two-tier-branch": git_acceptance._assert_a1,
        "commit-scope": git_acceptance._assert_a4,
        "lease": git_acceptance._assert_a7,
        "promotion": git_acceptance._assert_a11,
        "recovery": git_acceptance._assert_a12,
        "forbidden-operations": git_acceptance._assert_a16,
    }
    evidence = {clause: assertion(tmp_path / clause) for clause, assertion in executable_clauses.items()}
    assert set(evidence) == set(executable_clauses)
    assert all(value for value in evidence.values())
