from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

import psutil
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
for module_name in list(sys.modules):
    if module_name == "groundtruth_kb" or module_name.startswith("groundtruth_kb."):
        del sys.modules[module_name]

from groundtruth_kb.bridge_dispatch_config import set_operator_quiesce  # noqa: E402
from groundtruth_kb.cli import main  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        """
schema_version = 1
selection_order = ["reviewer_precedence", "harness_id"]

[harnesses.A]
max_items = 3

[harnesses.D]
max_items = 2

rules = []
""".lstrip(),
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["prime-builder"],
                        "can_fire_events": True,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": True,
                        "reviewer_precedence": 20,
                    },
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "can_fire_events": False,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": True,
                        "reviewer_precedence": 10,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root, config


def _write_runtime(root: Path) -> None:
    state_dir = root / ".gtkb-state" / "bridge-poller"
    runs_dir = state_dir / "dispatch-runs"
    runs_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at": "2026-06-23T10:00:00Z",
                "recipients": {
                    "loyal-opposition:D": {
                        "pending_count": 3,
                        "raw_pending_count": 4,
                        "selected_count": 1,
                        "last_result": "launch_failed",
                        "failure_class": "provider_failure",
                        "last_launch": {
                            "reason": "concurrency_cap_reached",
                            "exit_failure_reason": "no_verdict_produced",
                            "live_count": 2,
                            "cap": 2,
                        },
                        "circuit_breaker_tripped": True,
                    },
                    "prime-builder:A": {
                        "pending_count": 1,
                        "selected_count": 1,
                        "last_result": "launched",
                        "last_launch": {"reason": "started"},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "dispatch-failures.jsonl").write_text(
        json.dumps({"reason": "provider_failure", "failure_class": "provider_failure"}) + "\n",
        encoding="utf-8",
    )
    (state_dir / "dispatch-suppressions.jsonl").write_text(
        json.dumps({"reason": "work_intent_already_held"}) + "\n",
        encoding="utf-8",
    )
    (state_dir / "trigger-diagnostic.jsonl").write_text(json.dumps({"event": "tick"}) + "\n", encoding="utf-8")
    (state_dir / "starvation-telemetry.json").write_text(json.dumps({"starved_roles": []}), encoding="utf-8")
    (runs_dir / "2026-06-23T09-59-00Z-loyal-opposition-D-demo.stdout.log").write_text("", encoding="utf-8")
    (runs_dir / "2026-06-23T09-59-00Z-loyal-opposition-D-demo.stderr.log").write_text("", encoding="utf-8")
    (runs_dir / "2026-06-23T09-59-00Z-loyal-opposition-D-demo.exit_code").write_text("1", encoding="utf-8")
    live_id = "2026-06-23T10-00-00Z-prime-builder-A-live"
    (runs_dir / f"{live_id}.stdout.log").write_text("", encoding="utf-8")
    (runs_dir / f"{live_id}.pid").write_text(str(os.getpid()), encoding="utf-8")
    create_time = float(psutil.Process(os.getpid()).create_time())
    (runs_dir / f"{live_id}.create_time_epoch").write_text(f"{create_time:.6f}", encoding="utf-8")


def _write_workflow_membase(root: Path) -> None:
    with sqlite3.connect(root / "groundtruth.db") as connection:
        connection.executescript(
            """
            CREATE TABLE current_work_items (id TEXT, title TEXT, source_spec_id TEXT);
            CREATE TABLE current_specifications (id TEXT, status TEXT);
            CREATE TABLE current_project_authorizations (
                id TEXT,
                project_id TEXT,
                status TEXT,
                included_work_item_ids TEXT,
                excluded_work_item_ids TEXT
            );
            CREATE TABLE current_project_work_item_memberships (
                project_id TEXT,
                work_item_id TEXT,
                status TEXT
            );
            """
        )
        connection.executemany(
            "INSERT INTO current_work_items VALUES (?, ?, ?)",
            [
                ("WI-7001", "Ready workflow item", "SPEC-7001"),
                ("WI-7002", "Missing specification", None),
                ("WI-7003", "Missing authorization", "SPEC-7001"),
            ],
        )
        connection.execute("INSERT INTO current_specifications VALUES (?, ?)", ("SPEC-7001", "specified"))
        connection.execute(
            "INSERT INTO current_project_authorizations VALUES (?, ?, ?, ?, ?)",
            ("PAUTH-TEST-7001", "PROJECT-TEST-7000", "active", json.dumps(["WI-7001"]), json.dumps([])),
        )
        connection.executemany(
            "INSERT INTO current_project_work_item_memberships VALUES (?, ?, ?)",
            [("PROJECT-TEST-7000", work_item_id, "active") for work_item_id in ("WI-7001", "WI-7002", "WI-7003")],
        )


def _metrics_snapshot(*, freshness: str = "fresh", partial: bool = False) -> dict[str, object]:
    missing = 1 if partial else 0
    observed = 1 if partial else 2
    coverage = {
        "observed_count": observed,
        "missing_count": missing,
        "record_count": 2,
        "coverage_ratio": observed / 2,
    }
    return {
        "id": "dispatch-metrics-test",
        "snapshot_schema_id": "gtkb.dispatch_default_metrics_snapshot.v1",
        "generated_at": "2026-07-11T06:00:00Z",
        "source_window_start": "2026-07-11T05:00:00Z",
        "source_window_end": "2026-07-11T06:00:00Z",
        "source_event_ids": ["event-1", "event-2"],
        "source_record_count": 2,
        "max_records": 50,
        "counts_by_harness": {f"harness-{index:02d}": 1 for index in range(25)},
        "counts_by_model_profile": {"model-safe": 2},
        "counts_by_role": {"prime-builder": 2},
        "counts_by_bridge_outcome": {"VERIFIED": 2},
        "counts_by_failure_class": {"none": 2},
        "elapsed_distribution": {"under_1s": 1, "1_to_5s": 1},
        "turns_distribution": {"under_10": 2},
        "tools_distribution": {"1_to_10": 2},
        "usage_coverage": {"turns": coverage, "tools": coverage, "usage": coverage},
        "cost_coverage": {
            "provider_reported": coverage,
            "benchmark_estimated": {**coverage, "observed_count": 1, "missing_count": 1},
        },
        "quality_coverage": coverage,
        "adaptation_coverage": coverage,
        "freshness": {"status": freshness, "generated_at": "2026-07-11T06:00:00Z"},
        "prompt": "forbidden prompt content",
        "tool_arguments": {"secret": "forbidden credential"},
        "provider_body": {"generated_text": "forbidden provider content"},
    }


def _write_metrics_snapshot(root: Path, snapshot: dict[str, object]) -> None:
    with sqlite3.connect(root / "groundtruth.db") as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS current_documents (
                id TEXT,
                title TEXT,
                category TEXT,
                status TEXT,
                content TEXT,
                version INTEGER,
                changed_at TEXT
            )
            """
        )
        connection.execute(
            "INSERT INTO current_documents VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                snapshot["id"],
                "Canonical default dispatch metrics snapshot",
                "dispatch_default_metrics_snapshot",
                "active",
                json.dumps(snapshot),
                1,
                "2026-07-11T06:00:00Z",
            ),
        )


def _write_workflow_bridge(
    root: Path,
    slug: str,
    status: str,
    *,
    work_item_id: str | None = None,
    authorization_id: str | None = None,
    project_id: str | None = "PROJECT-TEST-7000",
) -> Path:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    metadata = [
        status,
        f"bridge_kind: {'lo_verdict' if status in {'GO', 'NO-GO'} else 'prime_proposal'}",
        f"Document: {slug}",
    ]
    if work_item_id:
        metadata.append(f"Work Item: {work_item_id}")
    if authorization_id:
        metadata.append(f"Project Authorization: {authorization_id}")
    if project_id:
        metadata.append(f"Project: {project_id}")
    path = bridge_dir / f"{slug}-001.md"
    path.write_text("\n".join(metadata) + "\n", encoding="utf-8")
    return path


def test_bridge_dispatch_report_json_exposes_required_sections_and_cause_taxonomy(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert set(payload) == {
        "configuration",
        "history",
        "live_state",
        "performance",
        "reliability",
        "summary",
        "topology",
    }
    assert "consistency_findings" in payload["reliability"]
    assert "runtime_classifications" in payload["reliability"]
    assert payload["topology"]["effective_per_cycle_ceiling"] == {
        "loyal-opposition": 2,
        "prime-builder": 3,
    }
    taxonomy = payload["reliability"]["failure_taxonomy"]
    assert taxonomy["last_result"]["launch_failed"] == 1
    assert taxonomy["failure_class"]["provider_failure"] == 2
    assert taxonomy["last_launch.reason"]["concurrency_cap_reached"] == 1
    assert taxonomy["last_launch.exit_failure_reason"]["no_verdict_produced"] == 1
    assert taxonomy["suppression.reason"]["work_intent_already_held"] == 1
    assert payload["live_state"]["live_worker_count"] == 1
    assert payload["history"]["recent_runs"][0]["state"] == "live"


def test_bridge_dispatch_report_is_read_only_for_config_registry_and_runtime(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)
    tracked = [
        root / "config" / "dispatcher" / "rules.toml",
        root / "harness-state" / "harness-registry.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-failures.jsonl",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-suppressions.jsonl",
    ]
    before = {path: path.read_bytes() for path in tracked}

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])

    assert result.exit_code == 0, result.output
    assert {path: path.read_bytes() for path in tracked} == before


def test_bridge_dispatch_report_human_output_is_compact(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report"])

    assert result.exit_code == 0, result.output
    assert "Bridge dispatch workflow:" in result.output
    assert "Prime Builder:" in result.output
    assert "Loyal Opposition:" in result.output


def test_dispatch_health_status_and_report_json_expose_dimension_rollup(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root, config = _project(tmp_path)
    (root / "scripts").mkdir()
    (root / "scripts" / "gtkb_dispatcher_daemon.py").write_text("# test marker\n", encoding="utf-8")
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.collect_complex_health",
        lambda project_root: {
            "health_status": "WARN",
            "aggregate_status": "degraded",
            "healthy": False,
            "components": {"daemon": {"severity": "WARN"}},
            "findings": ["WARN daemon: dispatcher daemon is not running"],
        },
    )

    health = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])
    assert health.exit_code == 0, health.output
    health_payload = json.loads(health.output)
    assert health_payload["health_status"] == "WARN"
    assert set(health_payload["dimensions"]) == {"complex_lifecycle", "routing_config"}
    assert health_payload["complex_lifecycle"]["health_status"] == "WARN"
    assert health_payload["routing_config"]["health_status"] == "PASS"

    status = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "status", "--json"])
    assert status.exit_code == 0, status.output
    status_payload = json.loads(status.output)
    assert status_payload["health_rollup"]["dimensions"]["complex_lifecycle"]["health_status"] == "WARN"

    report = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])
    assert report.exit_code == 0, report.output
    report_payload = json.loads(report.output)
    assert report_payload["summary"]["health_status"] == "WARN"
    assert report_payload["reliability"]["health_rollup"]["dimensions"]["routing_config"]["health_status"] == "PASS"


def test_dispatch_status_health_and_report_surface_operator_quiesce(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    set_operator_quiesce(
        root,
        reason="commit window",
        actor="operator",
        ttl_seconds=600,
    )

    status = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "status", "--json"])
    assert status.exit_code == 0, status.output
    status_payload = json.loads(status.output)
    assert status_payload["operator_quiesce"]["active"] is True
    assert status_payload["health_status"] == "WARN"

    health = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])
    assert health.exit_code == 0, health.output
    health_payload = json.loads(health.output)
    assert any("dispatch operator quiesce active" in finding for finding in health_payload["findings"])

    report = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])
    assert report.exit_code == 0, report.output
    report_payload = json.loads(report.output)
    assert any("dispatch operator quiesce active" in finding for finding in report_payload["reliability"]["findings"])
    assert report_payload["summary"]["health_status"] == "WARN"


def test_bridge_dispatch_report_does_not_count_stdout_stderr_only_sidecars_as_live(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    runs_dir = root / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
    runs_dir.mkdir(parents=True)
    (runs_dir / "2026-06-23T10-01-00Z-loyal-opposition-D-ghost.stdout.log").write_text("", encoding="utf-8")
    (runs_dir / "2026-06-23T10-01-00Z-loyal-opposition-D-ghost.stderr.log").write_text("", encoding="utf-8")

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["live_state"]["live_worker_count"] == 0
    assert payload["history"]["recent_runs"][0]["state"] == "stale"


def test_bridge_dispatch_report_treats_document_lease_held_as_stale_failure_context(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    state_dir = root / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at": "2026-07-03T12:00:00Z",
                "recipients": {
                    "loyal-opposition:D": {
                        "pending_count": 1,
                        "selected_count": 1,
                        "last_result": "document_lease_held",
                        "failure_class": "subprocess_execution_failed",
                        "last_launch": {
                            "reason": "document_lease_held",
                            "recipient": "loyal-opposition:D",
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    findings = "\n".join(payload["reliability"]["findings"])
    assert "dispatch runtime failure: loyal-opposition:D failure_class=subprocess_execution_failed" not in findings
    assert "stale failure evidence ignored (current document_lease_held non-launch)" in findings
    classification = next(
        row for row in payload["reliability"]["runtime_classifications"] if row["recipient"] == "loyal-opposition:D"
    )
    assert classification["severity"] == "WARN"
    assert classification["stale_failure_reason"] == "current document_lease_held non-launch"


def test_wi5000_dispatch_health_passes_for_impl_auth_quarantine_visibility(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    state_dir = root / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at": "2026-07-03T18:00:00Z",
                "recipients": {
                    "prime-builder:A": {
                        "pending_count": 1,
                        "selected_count": 0,
                        "last_result": "all_impl_auth_quarantined",
                        "failure_class": "subprocess_execution_failed",
                        "last_launch": {
                            "reason": "all_impl_auth_quarantined",
                            "recipient": "prime-builder:A",
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    health = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])
    assert health.exit_code == 0, health.output
    health_payload = json.loads(health.output)
    assert health_payload["health_status"] == "PASS"
    assert any(
        "stale failure evidence ignored (current all_impl_auth_quarantined non-launch)" in finding
        for finding in health_payload["findings"]
    )

    report = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])
    assert report.exit_code == 0, report.output
    report_payload = json.loads(report.output)
    assert report_payload["summary"]["health_status"] == "PASS"
    findings = "\n".join(report_payload["reliability"]["findings"])
    assert "dispatch runtime failure: prime-builder:A failure_class=subprocess_execution_failed" not in findings
    assert "stale failure evidence ignored (current all_impl_auth_quarantined non-launch)" in findings
    classification = next(
        row for row in report_payload["reliability"]["runtime_classifications"] if row["recipient"] == "prime-builder:A"
    )
    assert classification["severity"] == "PASS"
    assert classification["stale_failure_reason"] == "current all_impl_auth_quarantined non-launch"


def test_wi5174_compact_workflow_report_uses_canonical_queue_and_membase_prerequisites(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)
    _write_workflow_membase(root)
    _write_workflow_bridge(root, "go-ready", "GO", work_item_id="WI-7001", authorization_id="PAUTH-TEST-7001")
    _write_workflow_bridge(root, "go-missing-spec", "GO", work_item_id="WI-7002", authorization_id="PAUTH-TEST-7001")
    _write_workflow_bridge(root, "go-missing-pauth", "GO", work_item_id="WI-7003", authorization_id="PAUTH-TEST-7003")
    _write_workflow_bridge(root, "revise-me", "NO-GO")
    _write_workflow_bridge(root, "review-new", "NEW")
    _write_workflow_bridge(root, "review-revised", "REVISED")
    _write_workflow_bridge(root, "owner-advisory", "ADVISORY")

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "report", "--compact", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema_version"] == "gtkb.dispatch_workflow.v1"
    assert set(payload["queues"]["prime_builder"]) == {"actionable_now", "candidate_next", "blocked"}
    assert set(payload["queues"]["loyal_opposition"]) == {"actionable_now", "candidate_next", "blocked"}
    assert payload["in_flight"][0]["recipient"] == "prime-builder:A"

    prime_now = {row["id"] for row in payload["queues"]["prime_builder"]["actionable_now"]}
    assert {"go-ready", "revise-me"} <= prime_now
    prime_blocks = {row["id"]: row["reason_code"] for row in payload["queues"]["prime_builder"]["blocked"]}
    assert prime_blocks["go-missing-spec"] == "missing_source_spec"
    assert prime_blocks["go-missing-pauth"] == "missing_matching_pauth"
    assert payload["queues"]["prime_builder"]["candidate_next"][0]["reason_code"] == "advisory_requires_owner_intake"

    loyal_now = {row["id"] for row in payload["queues"]["loyal_opposition"]["actionable_now"]}
    assert {"review-new", "review-revised"} <= loyal_now


def test_wi5174_default_and_explicit_compact_human_report_are_workflow_views(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)

    default = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report"])
    explicit = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--compact"])

    assert default.exit_code == 0, default.output
    assert explicit.exit_code == 0, explicit.output
    for output in (default.output, explicit.output):
        assert "Bridge dispatch workflow:" in output
        assert "Prime Builder:" in output
        assert "Loyal Opposition:" in output


def test_wi5174_compact_workflow_is_bounded_and_read_only(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)
    for number in range(21):
        _write_workflow_bridge(root, f"review-{number:02d}", "NEW")

    tracked = [
        root / "config" / "dispatcher" / "rules.toml",
        root / "harness-state" / "harness-registry.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json",
        root / "bridge" / "review-00-001.md",
    ]
    before = {path: path.read_bytes() for path in tracked}
    result = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "report", "--compact", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    loyal_now = payload["queues"]["loyal_opposition"]["actionable_now"]
    assert len(loyal_now) == 20
    assert payload["bounds"]["per_section_limit"] == 20
    assert payload["bounds"]["truncated"]["queues"]["loyal_opposition"]["actionable_now"] is True
    assert {path: path.read_bytes() for path in tracked} == before


def test_wi5181_compact_and_human_views_use_same_bounded_canonical_snapshot(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)
    _write_metrics_snapshot(root, _metrics_snapshot())
    tracked = [
        root / "groundtruth.db",
        root / "config" / "dispatcher" / "rules.toml",
        root / "harness-state" / "harness-registry.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json",
    ]
    before = {path: path.read_bytes() for path in tracked}

    full = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])
    compact = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "report", "--compact", "--json"],
    )
    human = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report"])

    assert full.exit_code == 0, full.output
    assert compact.exit_code == 0, compact.output
    assert human.exit_code == 0, human.output
    assert "recent_work_metrics" not in json.loads(full.output)
    metrics = json.loads(compact.output)["recent_work_metrics"]
    assert metrics["snapshot_id"] == "dispatch-metrics-test"
    assert metrics["availability"] == "observed"
    assert metrics["record_count"] == 2
    assert len(metrics["breakouts"]["harness"]) == 20
    assert set(metrics["cost_coverage"]) == {"benchmark_estimated", "provider_reported"}
    assert "Recent-work metrics:" in human.output
    assert "Snapshot: dispatch-metrics-test" in human.output
    assert "Availability: observed" in human.output
    serialized = json.dumps(metrics)
    assert "forbidden" not in serialized
    assert "prompt" not in serialized
    assert "tool_arguments" not in serialized
    assert "provider_body" not in serialized
    assert {path: path.read_bytes() for path in tracked} == before


def test_wi5181_unavailable_snapshot_preserves_workflow_queues(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)
    _write_workflow_bridge(root, "review-new", "NEW")

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "report", "--compact", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["recent_work_metrics"]["availability"] == "unavailable"
    assert payload["recent_work_metrics"]["reason"] == "canonical_snapshot_store_unavailable"
    assert payload["queues"]["loyal_opposition"]["actionable_now"][0]["id"] == "review-new"


def test_wi5181_partial_snapshot_is_explicit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_metrics_snapshot(root, _metrics_snapshot(partial=True))

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "report", "--compact", "--json"],
    )

    assert result.exit_code == 0, result.output
    metrics = json.loads(result.output)["recent_work_metrics"]
    assert metrics["availability"] == "partial"
    assert metrics["reason"] == "canonical_snapshot_partial"
    assert metrics["coverage"]["token_cache"]["missing_count"] == 1


def test_wi5181_stale_snapshot_is_not_silently_substituted(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_metrics_snapshot(root, _metrics_snapshot(freshness="stale"))

    compact = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "report", "--compact", "--json"],
    )
    human = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report"])

    assert compact.exit_code == 0, compact.output
    metrics = json.loads(compact.output)["recent_work_metrics"]
    assert metrics["availability"] == "stale"
    assert metrics["reason"] == "canonical_snapshot_stale"
    assert "stale: canonical_snapshot_stale" in human.output
