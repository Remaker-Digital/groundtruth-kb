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
from datetime import UTC, datetime
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
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.sot_registry import load_toml, sync_projection  # noqa: E402
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
    registry_payload = (
        "[[artifacts]]\n"
        'id = "current"\n'
        'domain = "narrative_authority"\n'
        'storage_path = "rules/current.md"\n'
        'coverage_mode = "exact"\n'
        'lifecycle = "active"\n'
        'authority_spec_id = "GOV-X"\n'
        'mutation_api = "test fixture"\n'
        'versioning_policy = "git_tracked"\n'
        'backup_policy = "git_tracked"\n'
        'health_check_function = ""\n'
        'owner_role = "shared"\n\n'
        "[[artifacts]]\n"
        'id = "history"\n'
        'domain = "narrative_authority"\n'
        'storage_path = "rules/history.md"\n'
        'coverage_mode = "exact"\n'
        'lifecycle = "archive"\n'
        'authority_spec_id = "GOV-X"\n'
        'mutation_api = "test fixture"\n'
        'versioning_policy = "git_tracked"\n'
        'backup_policy = "git_tracked"\n'
        'health_check_function = ""\n'
        'owner_role = "shared"\n'
    )
    canonical_registry = registry / "sot-artifacts.toml"
    canonical_registry.write_text(registry_payload, encoding="utf-8")
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
    packaged_registry = (
        root
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    packaged_registry.parent.mkdir(parents=True)
    packaged_registry.write_text(registry_payload, encoding="utf-8")
    db_path = root / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(
        load_toml(canonical_registry),
        db_path,
        changed_by="test",
        change_reason="fixture sync",
    )


# MOD-AD01
def test_mod_ad01_inventory_covers_all_registered_classes_and_effective_worker_loads() -> None:
    index, declared = load_repository_snapshot(ROOT)
    graph = discover_effective_loading_graph(ROOT)
    report = audit_repository(ROOT)

    assert {record.logical_id.split(":", 1)[0] for record in index.records} == {
        "interface",
        "sharding",
        "sot",
        "startup",
    }
    assert {reference.purpose for reference in declared} == {
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


# MOD-RI03


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


# MOD-RI06


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


# MOD-RI16
