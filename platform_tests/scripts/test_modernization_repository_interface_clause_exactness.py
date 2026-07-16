"""Clause-exact acceptance probes for artifact and runtime modernization.

Passing tests in this module exercise production APIs. Strict xfails are
deliberate gap probes: they describe an objective clause that the current
production surface cannot enforce, and therefore must never be cited as proof.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "groundtruth-kb" / "src"
SCRIPTS = ROOT / "scripts"
for import_root in (PACKAGE_SRC, SCRIPTS):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from check_artifact_decontamination import (  # noqa: E402
    audit_repository,
    discover_effective_loading_graph,
)
from groundtruth_kb.activity.ops import (  # noqa: E402
    collect_ops_snapshot,
    render_ops_activity_context,
)
from groundtruth_kb.activity.profiles import (  # noqa: E402
    ActivityProfile,
    load_activity_profiles,
)
from groundtruth_kb.artifact_lifecycle.decontamination import (  # noqa: E402
    ArtifactAuthorityIndex,
    ArtifactRecord,
    WorkerReference,
    canonical_report_bytes,
    load_repository_snapshot,
)
from groundtruth_kb.context.freshness import (  # noqa: E402
    HIGH_CHURN_CLASSES,
    LOW_CHURN_REQUIRED_FIELDS,
    evaluate_extract,
)
from groundtruth_kb.context.manifest import (  # noqa: E402
    STACK_ORDER,
    ContextManifestError,
    assemble_context_manifest,
)
from groundtruth_kb.runtime_recovery import RecoveryStore  # noqa: E402
from groundtruth_kb.session.envelope import (  # noqa: E402
    EnvelopeError,
    ensure_worker_session,
    load_current,
    open_session,
    open_topic,
    resolve_worker_role_provenance,
)

CHECKER = ROOT / "scripts" / "check_artifact_decontamination.py"
NOW = datetime(2026, 7, 13, 18, 0, tzinfo=UTC)


@dataclass
class ManualClock:
    value: float = 1_000.0

    def __call__(self) -> float:
        return self.value


def _write_harness_state(root: Path, *, durable_role: str = "loyal-opposition") -> None:
    state = root / "harness-state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {"id": "A", "harness_name": "codex", "role": [durable_role]},
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_artifact_repository(
    root: Path,
    *,
    current_content: str = "current\n",
    entrypoint_body: str | None = None,
) -> None:
    registry = root / "config" / "registry"
    control = root / "config" / "agent-control"
    scripts = root / "scripts"
    rules = root / "rules"
    for directory in (registry, control, scripts, rules):
        directory.mkdir(parents=True, exist_ok=True)
    (registry / "sot-artifacts.toml").write_text(
        "[[artifacts]]\n"
        'id = "current"\n'
        'storage_path = "rules/current.md"\n'
        'lifecycle = "active"\n\n'
        "[[artifacts]]\n"
        'id = "history"\n'
        'storage_path = "rules/history.md"\n'
        'lifecycle = "superseded"\n',
        encoding="utf-8",
    )
    (registry / "context-manifests.toml").write_text("items = []\n", encoding="utf-8")
    (control / "SESSION-STARTUP-CONTROL-MAP.md").write_text(
        "| Startup service | `scripts/session_self_initialization.py` | active | loaded |\n"
        "| Current | `rules/current.md` | active | loaded |\n"
        "| History | `rules/history.md` | superseded | history |\n",
        encoding="utf-8",
    )
    (control / "activity-envelope-sharding.toml").write_text(
        "[classes.global_baseline]\nallowed_surfaces = []\n[classes.activity_only]\ndeferred_surfaces = []\n",
        encoding="utf-8",
    )
    (control / "system-interface-map.toml").write_text("systems = []\n", encoding="utf-8")
    (scripts / "session_self_initialization.py").write_text(
        entrypoint_body
        or (
            "from pathlib import Path\n"
            "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
            "def load():\n"
            "    return (PROJECT_ROOT / 'rules' / 'current.md').read_text(encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )
    (rules / "current.md").write_text(current_content, encoding="utf-8")
    (rules / "history.md").write_text("historical\n", encoding="utf-8")


def _freshness_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "source_id": "SPEC-RI06-FIXTURE",
        "source_path": "groundtruth.db:current_specifications",
        "authority_class": "stated",
        "source_version_or_hash": "sha256:abc123",
        "churn_class": "low",
        "generated_at": NOW.isoformat(),
        "ttl_seconds": 120,
        "bounded_usage_context": "session:build",
        "live_query_route": "gt spec show SPEC-RI06-FIXTURE",
        "recovery_route": "gt spec show SPEC-RI06-FIXTURE",
        "embedded_content": {"status": "specified"},
    }
    record.update(overrides)
    return record


def _manifest(activity: str) -> dict[str, object]:
    return assemble_context_manifest(
        activity=activity,
        role="Prime Builder",
        generated_at=NOW,
        evaluated_at=NOW,
        project_root=ROOT,
    )


def _activity_content(manifest: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {}
    for item in manifest["items"]:  # type: ignore[index]
        if item["layer"] == "activity_overlay" and isinstance(item["content"], dict):
            result.update(item["content"])
    return result


# MOD-AD01
def test_mod_ad01_inventory_covers_all_registered_classes_and_effective_worker_loads() -> None:
    index, declared = load_repository_snapshot(ROOT)
    graph = discover_effective_loading_graph(ROOT)
    report = audit_repository(ROOT)

    assert {record.logical_id.split(":", 1)[0] for record in index.records} == {
        "context",
        "interface",
        "sharding",
        "sot",
        "startup",
    }
    assert {reference.purpose for reference in declared} == {
        "context_manifest",
        "context_sharding",
        "interface_startup",
        "startup_inventory",
    }
    assert {entrypoint["kind"] for entrypoint in graph["entrypoints"]} == {
        "console_command",
        "hook_settings",
        "startup_inventory",
        "startup_service",
    }
    effective = {
        (reference["path"], reference["source"]): reference["resolution"]
        for reference in report["audit"]["worker_references"]
        if reference["purpose"] == "effective_loader"
    }
    assert effective
    assert all(effective[(edge["path"], edge["source"])] in {"current", "generated"} for edge in graph["load_edges"])


# MOD-AD02
def test_mod_ad02_lifecycle_currentness_singleton_retirement_supersession_and_archive_rules() -> None:
    index = ArtifactAuthorityIndex(
        [
            ArtifactRecord("guide", "rules/guide-v1.md", "retired", "fixture", 1, "guide"),
            ArtifactRecord("guide", "rules/guide-v2.md", "current", "fixture", 2),
            ArtifactRecord("archive", "archive/report.md", "archive", "fixture"),
            ArtifactRecord("projection", "generated/guide.md", "generated", "fixture"),
        ]
    )

    guide = index.resolve("guide")
    assert guide["status"] == "resolved"
    assert guide["current"]["path"] == "rules/guide-v2.md"
    assert {item["lifecycle"] for item in guide["history"]} == {"retired"}
    assert index.path_status("rules/guide-v1.md")["status"] == "historical"
    assert index.path_status("archive/report.md")["status"] == "historical"
    assert index.resolve("projection")["status"] == "no_current"
    assert index.audit([WorkerReference("rules/guide-v2.md", "worker")])["status"] == "PASS"
    assert index.audit([WorkerReference("rules/guide-v1.md", "worker")])["status"] == "FAIL"

    ambiguous = ArtifactAuthorityIndex(
        [
            ArtifactRecord("guide", "rules/a.md", "current", "fixture"),
            ArtifactRecord("guide", "rules/b.md", "active", "fixture"),
        ]
    )
    assert ambiguous.resolve("guide")["status"] == "ambiguous_current"
    assert ambiguous.audit([])["findings"][0]["severity"] == "P0"


@pytest.mark.xfail(
    strict=True,
    reason="ArtifactAuthorityIndex does not validate superseded_by targets or cycles.",
)
def test_mod_ad02_rejects_broken_or_cyclic_supersession_chains() -> None:
    index = ArtifactAuthorityIndex(
        [
            ArtifactRecord("guide", "rules/v1.md", "superseded", "fixture", 1, "missing"),
            ArtifactRecord("cycle-a", "rules/a.md", "superseded", "fixture", 1, "cycle-b"),
            ArtifactRecord("cycle-b", "rules/b.md", "superseded", "fixture", 1, "cycle-a"),
        ]
    )
    report = index.audit([])
    assert report["status"] == "FAIL"
    assert {item["id"] for item in report["findings"]} >= {
        "broken-supersession:guide",
        "supersession-cycle:cycle-a",
    }


# MOD-AD04
def test_mod_ad04_rejects_stale_authority_and_live_archive_dependencies(tmp_path: Path) -> None:
    _write_artifact_repository(
        tmp_path,
        entrypoint_body=(
            "from pathlib import Path\n"
            "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
            "def load():\n"
            "    return (PROJECT_ROOT / 'rules' / 'history.md').read_text(encoding='utf-8')\n"
        ),
    )

    report = audit_repository(tmp_path)

    assert report["status"] == "FAIL"
    assert any(
        finding["id"] == "rules/history.md"
        and finding["severity"] == "P0"
        and "historical authority" in finding["reason"]
        for finding in report["audit"]["findings"]
    )


@pytest.mark.xfail(
    strict=True,
    reason="The scanner has no semantic policy for obsolete terms, retired commands, routes, or projections.",
)
@pytest.mark.parametrize(
    ("clause", "payload"),
    [
        ("obsolete_term", "harness-state/role-assignments.json is role authority\n"),
        ("retired_command", "Run the retired smart poller for bridge work.\n"),
        ("conflicting_route", "Use both bridge/INDEX.md and TAFE as the live queue.\n"),
        ("unlabeled_projection", "Generated current status with no authority or provenance.\n"),
        ("superseded_as_current", "Governance-rejected Bundle 005 is APPROVED and current.\n"),
    ],
)
def test_mod_ad04_semantic_contamination_categories_fail_closed(
    tmp_path: Path,
    clause: str,
    payload: str,
) -> None:
    _write_artifact_repository(tmp_path, current_content=payload)
    report = audit_repository(tmp_path)
    assert report["status"] == "FAIL"
    assert any(finding.get("category") == clause for finding in report["audit"]["findings"])


# MOD-AD05
@pytest.mark.xfail(
    strict=True,
    reason="The decontamination report has no Gate-1-bound cleanup batch ledger.",
)
def test_mod_ad05_cleanup_is_proven_as_bounded_post_gate_batches() -> None:
    report = audit_repository(ROOT)
    batches = report["cleanup_batches"]
    assert batches
    assert all(batch["gate"] == "Gate 1" and batch["bounded"] is True for batch in batches)
    assert {batch["surface"] for batch in batches} >= {"governance", "specification"}


# MOD-AD06
@pytest.mark.xfail(
    strict=True,
    reason="Hash-valid skill content is not evaluated against retired semantic policy.",
)
def test_mod_ad06_semantically_stale_hash_valid_skill_fails_closed(tmp_path: Path) -> None:
    _write_artifact_repository(
        tmp_path,
        current_content="Skill: read bridge/INDEX.md as the current queue and start the smart poller.\n",
    )
    report = audit_repository(tmp_path)
    assert report["status"] == "FAIL"
    assert any(finding.get("category") == "semantically_stale_skill" for finding in report["audit"]["findings"])


# MOD-AD07
@pytest.mark.xfail(
    strict=True,
    reason="Producer outputs are not executed and semantically checked for retired narratives.",
)
def test_mod_ad07_generated_producer_cannot_recreate_retired_narrative(tmp_path: Path) -> None:
    _write_artifact_repository(
        tmp_path,
        current_content="Generated startup: bridge/INDEX.md is the active queue.\n",
    )
    report = audit_repository(tmp_path)
    assert report["status"] == "FAIL"
    assert any(finding.get("category") == "retired_narrative_recreated" for finding in report["audit"]["findings"])


# MOD-AD08
@pytest.mark.xfail(
    strict=True,
    reason="The artifact checker does not reconcile MemBase lifecycle state.",
)
def test_mod_ad08_reconciles_bridge_project_backlog_membership_and_executable_tests() -> None:
    report = audit_repository(ROOT)
    reconciliation = report["state_reconciliation"]
    assert reconciliation["bridge"] == "consistent"
    assert reconciliation["projects"] == "consistent"
    assert reconciliation["backlog"] == "consistent"
    assert reconciliation["membership"] == "consistent"
    assert reconciliation["executable_tests"] == "consistent"


# MOD-AD11
def test_mod_ad11_governed_preflight_executes_and_rejects_residual_reference(tmp_path: Path) -> None:
    _write_artifact_repository(
        tmp_path,
        entrypoint_body=(
            "from pathlib import Path\n"
            "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
            "def load():\n"
            "    return (PROJECT_ROOT / 'rules' / 'history.md').read_text(encoding='utf-8')\n"
        ),
    )
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--project-root", str(tmp_path), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    report = json.loads(result.stdout)
    assertion = next(item for item in report["assertions"] if item["id"] == "MOD-AD-11")
    assert result.returncode == 1
    assert report["status"] == "FAIL"
    assert assertion["status"] == "FAIL"


# MOD-AD12
def test_mod_ad12_active_path_source_closure_and_lifecycle_reruns_are_deterministic() -> None:
    first = audit_repository(ROOT)
    second = audit_repository(ROOT)
    assert first["status"] == "PASS"
    assert first["audit"]["findings"] == []
    assert first["effective_loading_graph"]["unresolved_imports"] == []
    assert canonical_report_bytes(first) == canonical_report_bytes(second)


@pytest.mark.xfail(
    strict=True,
    reason="Generation-run and independent-review receipts are not bound into the artifact report.",
)
def test_mod_ad12_rerun_binds_generation_and_independent_verification() -> None:
    report = audit_repository(ROOT)
    assert report["generation_check"]["status"] == "PASS"
    assert report["independent_verification"]["status"] == "PASS"
    assert report["independent_verification"]["reviewer_session_id"]


# MOD-RI02
def test_mod_ri02_stack_order_and_priority_precedence_are_enforced(tmp_path: Path) -> None:
    manifest = _manifest("build")
    items = manifest["items"]
    assert manifest["stack_order"] == list(STACK_ORDER)
    assert [STACK_ORDER.index(item["layer"]) for item in items] == sorted(
        STACK_ORDER.index(item["layer"]) for item in items
    )
    for layer in ("session_baseline", "activity_overlay"):
        priorities = [item["priority"] for item in items if item["layer"] == layer]
        assert priorities == sorted(priorities, reverse=True)

    registry_text = (ROOT / "config/registry/context-manifests.toml").read_text(encoding="utf-8")
    conflicting = tmp_path / "context-manifests.toml"
    conflicting.write_text(
        registry_text
        + "\n[[items]]\n"
        + 'id = "baseline.glossary.conflict"\n'
        + 'layer = "session_baseline"\n'
        + 'category = "glossary"\n'
        + 'source_id = "canonical-terms-sync"\n'
        + 'source_path = "config/governance/canonical-terms-sync.toml"\n'
        + 'authority_class = "competing_authority"\n'
        + 'lifecycle = "current"\n'
        + 'churn_class = "low"\n'
        + 'embedding = "embedded"\n'
        + "ttl_seconds = 120\n"
        + 'read_route = "competing read route"\n'
        + 'mutation_route = "none"\n'
        + 'recovery_route = "gt canonical-terms list"\n'
        + 'applicability = ["*"]\n'
        + 'projection = "descriptor"\n'
        + "token_cost = 1\n"
        + "priority = 1\n"
        + "essential = false\n",
        encoding="utf-8",
    )
    with pytest.raises(ContextManifestError, match="conflict for canonical-terms-sync"):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=NOW,
            evaluated_at=NOW,
            registry_path=conflicting,
            project_root=ROOT,
        )


# MOD-RI03
def test_mod_ri03_generated_session_baseline_is_deterministic_and_complete() -> None:
    first = _manifest("build")
    second = _manifest("build")
    assert first == second
    baseline = [item for item in first["items"] if item["layer"] == "session_baseline"]
    assert {item["category"] for item in baseline} == set(first["categories_by_layer"]["session_baseline"])
    assert all(item["freshness"]["eligible_as_current"] for item in baseline)


@pytest.mark.xfail(
    strict=True,
    reason="Session envelopes do not carry or bind the generated baseline for either delivery mode.",
)
def test_mod_ri03_interactive_and_dispatched_envelopes_bind_delivered_baseline(tmp_path: Path) -> None:
    _write_harness_state(tmp_path, durable_role="prime-builder")
    interactive = open_session(
        tmp_path,
        harness_name="codex",
        role="prime-builder",
        session_id="interactive-session",
        worker_role_source="interactive_transcript_explicit",
    )
    dispatched = open_session(
        tmp_path,
        harness_name="codex",
        role="prime-builder",
        session_id="dispatched-session",
        worker_role_source="dispatcher_composition",
        dispatch_run_id="dispatch-run-001",
    )
    assert interactive["context_manifest_sha256"]
    assert dispatched["context_manifest_sha256"]
    assert interactive["context_manifest_sha256"] == dispatched["context_manifest_sha256"]


# MOD-RI04
def test_mod_ri04_explicit_session_role_overrides_mapping_and_survives_resume_compaction(tmp_path: Path) -> None:
    _write_harness_state(tmp_path, durable_role="loyal-opposition")
    issued = ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="session-ri04",
        role="prime-builder",
        role_source="interactive_transcript_explicit",
    )
    assert issued["role"] == "prime-builder"
    assert issued["role_resolution"]["durable_registry_role"] == "loyal-opposition"
    assert issued["role_resolution"]["authority_mode"] == "worker_session_document"

    resumed = ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="session-ri04",
        role="prime-builder",
        role_source="interactive_transcript_explicit",
    )
    provenance = resolve_worker_role_provenance(
        tmp_path,
        current_session_id="session-ri04",
        harness_name="codex",
    )
    assert resumed["session_id"] == issued["session_id"]
    assert resumed["opened_at"] == issued["opened_at"]
    assert provenance["role"] == "prime-builder"
    assert provenance["role_resolution_source"] == "interactive_transcript_explicit"


# MOD-RI05
@pytest.mark.xfail(
    strict=True,
    reason="Runtime resources lack uniform availability, installation, and startup descriptors.",
)
def test_mod_ri05_every_runtime_resource_exposes_uniform_typed_descriptor() -> None:
    required = {
        "availability",
        "authority_class",
        "read_route",
        "mutation_route",
        "installation",
        "startup",
        "recovery_route",
    }
    manifest = _manifest("build")
    assert manifest["items"]
    for resource in manifest["items"]:
        assert required <= set(resource)
        assert all(resource[field] not in {None, ""} for field in required)


# MOD-RI06
def test_mod_ri06_ttl_embedding_expiration_and_live_query_rules_fail_closed() -> None:
    current = evaluate_extract(_freshness_record(), now=NOW)
    assert current["eligible_as_current"] is True

    expired = evaluate_extract(
        _freshness_record(generated_at=(NOW - timedelta(seconds=121)).isoformat()),
        now=NOW,
    )
    assert expired["eligible_as_current"] is False
    assert expired["status"] == "recovery_required"
    assert "expired" in expired["reasons"]

    for churn_class in HIGH_CHURN_CLASSES:
        result = evaluate_extract(
            _freshness_record(churn_class=churn_class, embedded_content={"unsafe": "snapshot"}),
            now=NOW,
        )
        assert result["eligible_as_current"] is False
        assert {"high-churn", "live-query-only"} <= set(result["reasons"])

    for field in LOW_CHURN_REQUIRED_FIELDS:
        record = _freshness_record()
        record.pop(field)
        result = evaluate_extract(record, now=NOW)
        assert result["eligible_as_current"] is False
        assert any(reason == f"missing:{field}" for reason in result["reasons"])


# MOD-RI08
@pytest.mark.xfail(
    strict=True,
    reason="Recovery observations omit size, latency, omissions, conflicts, first-tool timing, and degradation metrics.",
)
def test_mod_ri08_runtime_observation_instruments_all_required_dimensions(tmp_path: Path) -> None:
    clock = ManualClock()
    store = RecoveryStore(tmp_path / "recovery.db", clock=clock)
    decision = store.claim(
        "op-ri08",
        operation_kind="context_delivery",
        input_fingerprint="sha256:ri08",
        owner_id="worker-a",
        lease_seconds=30,
    )
    assert decision.claim is not None
    store.checkpoint(decision.claim, {"omissions": [], "conflicts": []})
    observation = store.observe("op-ri08")
    assert observation is not None
    metrics = observation.metrics
    assert {
        "size_bytes",
        "latency_ms",
        "omissions",
        "conflicts",
        "first_tool_ms",
        "degraded_state",
    } <= set(metrics)


# MOD-RI09
def test_mod_ri09_typed_single_active_activity_runtime_supplants_and_rejects_unknown(tmp_path: Path) -> None:
    profiles = load_activity_profiles()
    assert all(isinstance(profile, ActivityProfile) for profile in profiles.values())
    _write_harness_state(tmp_path, durable_role="prime-builder")
    open_session(tmp_path, harness_name="codex", role="prime-builder", session_id="session-ri09")

    first = open_topic(tmp_path, "build", harness_name="codex")
    second = open_topic(tmp_path, "test", harness_name="codex")
    envelope = load_current(tmp_path, "codex")
    assert envelope is not None
    open_topics = [topic for topic in envelope["topics"] if topic["closed_at"] is None]
    assert first["type"] == "build"
    assert second["type"] == "test"
    assert len(open_topics) == 1
    assert open_topics[0]["type"] == "test"
    assert envelope["topics"][0]["close_outcome"] == "auto_closed_by_open_supplant"
    with pytest.raises(EnvelopeError, match="Unsupported topic type"):
        open_topic(tmp_path, "deploy", harness_name="codex")


# MOD-RI10
def test_mod_ri10_ops_context_uses_live_local_state_and_remains_report_only(tmp_path: Path) -> None:
    ops = tmp_path / ".gtkb-state" / "ops"
    ops.mkdir(parents=True)
    (ops / "health.json").write_text(
        json.dumps({"status": "FAIL", "summary": "runtime check failed"}),
        encoding="utf-8",
    )
    (ops / "support-cases.json").write_text(
        json.dumps({"open_cases": 3, "urgent_cases": 1}),
        encoding="utf-8",
    )

    snapshot = collect_ops_snapshot(tmp_path)
    by_name = {signal.name: signal for signal in snapshot.signals}
    rendered = render_ops_activity_context(tmp_path)
    assert by_name["health"].status == "attention"
    assert by_name["support cases"].status == "attention"
    assert by_name["health"].sources[0].status == "available"
    assert "- status: report-only" in rendered
    assert "- external_actions: none" in rendered
    assert "triage support (priority: P1)" in rendered


@pytest.mark.xfail(
    strict=True,
    reason="Deliberation context carries prose guardrails but no executable no-implementation capability.",
)
def test_mod_ri11_deliberation_context_enforces_no_implementation_boundary() -> None:
    context = _activity_content(_manifest("deliberation"))
    assert context["implementation_allowed"] is False
    assert context["mutation_capability"] is None
    assert context["decision_capture_route"]


@pytest.mark.xfail(
    strict=True,
    reason="Build context does not expose typed authorization, bridge, claim, branch, and mutation-route fields.",
)
def test_mod_ri12_build_context_is_typed_and_clause_complete() -> None:
    context = _activity_content(_manifest("build"))
    assert {
        "authorization",
        "bridge",
        "work_intent",
        "branch_binding",
        "mutation_routes",
    } <= set(context)
    assert context["authorization"]["status"] in {"active", "denied"}


@pytest.mark.xfail(
    strict=True,
    reason="Test context does not expose typed linked-spec, executable-test, environment, result, and evidence fields.",
)
def test_mod_ri13_test_context_is_typed_and_clause_complete() -> None:
    context = _activity_content(_manifest("test"))
    assert {
        "linked_specs",
        "executable_tests",
        "environment",
        "results",
        "evidence_routes",
    } <= set(context)
    assert all(test["executable"] is True for test in context["executable_tests"])


@pytest.mark.xfail(
    strict=True,
    reason="Spec context does not expose typed intake, confirmation, approval, authority, and testability fields.",
)
def test_mod_ri14_spec_context_is_typed_and_clause_complete() -> None:
    context = _activity_content(_manifest("spec"))
    assert {"intake", "confirmation", "approval", "authority", "testability"} <= set(context)
    assert context["testability"]["objective_acceptance_test"]


@pytest.mark.xfail(
    strict=True,
    reason="Project context does not expose typed hierarchy, authorization, backlog, dependency, branch, and CLI fields.",
)
def test_mod_ri15_project_context_is_typed_and_clause_complete() -> None:
    context = _activity_content(_manifest("project"))
    assert {
        "hierarchy",
        "authorization",
        "backlog",
        "dependencies",
        "branch_state",
        "project_cli",
    } <= set(context)
    assert context["project_cli"]["read"] and context["project_cli"]["mutation"]


# MOD-RI16
def test_mod_ri16_internal_runtime_contracts_cover_role_freshness_resources_degradation_and_six_activities() -> None:
    manifests = {activity: _manifest(activity) for activity in load_activity_profiles()}
    assert set(manifests) == {"ops", "deliberation", "build", "test", "spec", "project"}
    assert all(manifest["role_bootstrap"]["cannot_alter_role"] is True for manifest in manifests.values())
    assert all(manifest["stack_order"] == list(STACK_ORDER) for manifest in manifests.values())
    assert all(
        item["freshness"]["eligible_as_current"] for manifest in manifests.values() for item in manifest["items"]
    )
    assert any(item["disposition"] == "live-query-only" for item in manifests["ops"]["items"])


@pytest.mark.xfail(
    strict=True,
    reason="No runtime verifier result binds non-impairment and Gate 3 to this candidate execution.",
)
def test_mod_ri16_candidate_bound_nonimpairment_and_gate3_verdict_exist() -> None:
    manifest = _manifest("build")
    verification = manifest["runtime_verification"]
    assert verification["non_impairment"] == "PASS"
    assert verification["gate_3"] == "PASS"
    assert verification["candidate_head"]
