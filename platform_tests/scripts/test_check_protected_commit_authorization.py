"""Tests for the protected commit authorization pre-commit gate."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import implementation_authorization

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_protected_commit_authorization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_protected_commit_authorization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_protected_commit_authorization"] = module
    spec.loader.exec_module(module)
    return module


def _author(role: str, session_id: str) -> str:
    return f"""author_identity: {role}/codex
author_harness_id: A
author_session_context_id: {session_id}
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: test
"""


def _write_transaction_chain(
    root: Path,
    module,
    monkeypatch: pytest.MonkeyPatch,
    *,
    bridge_id: str = "gtkb-wi5629-fixture",
    protected_paths: list[str] | None = None,
    reviewer_session: str = "lo-session",
    report_session: str = "pb-session",
) -> tuple[list[str], str, str]:
    protected_paths = protected_paths or [
        "scripts/bridge_lifecycle_resolver.py",
        "platform_tests/scripts/test_bridge_lifecycle_resolver.py",
    ]
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    proposal = f"bridge/{bridge_id}-001.md"
    go = f"bridge/{bridge_id}-002.md"
    report = f"bridge/{bridge_id}-003.md"
    verdict = f"bridge/{bridge_id}-004.md"
    selected_paths = [*protected_paths, report, verdict]

    (root / proposal).write_text(
        f"""NEW
{_author("prime-builder", "proposal-session")}
# Proposal

Document: {bridge_id}
Version: 001

target_paths: {json.dumps(protected_paths)}
""",
        encoding="utf-8",
    )
    (root / go).write_text(
        f"""GO
{_author("loyal-opposition", "go-session")}
# Verdict

Document: {bridge_id}
Version: 002
Responds to: {proposal}
""",
        encoding="utf-8",
    )
    (root / report).write_text(
        f"""NEW
{_author("prime-builder", report_session)}
# Implementation Report

bridge_kind: implementation_report
Document: {bridge_id}
Version: 003
Responds to: {go}
""",
        encoding="utf-8",
    )
    manifest = "\n".join(f"- `{path}`" for path in selected_paths)
    (root / verdict).write_text(
        f"""VERIFIED
{_author("loyal-opposition", reviewer_session)}
# Verification

bridge_kind: lo_verdict
Document: {bridge_id}
Version: 004
Responds to: {report}

## Commit Finalization Evidence

- Finalization helper: `fixture`
- Intended commit subject: `fix: fixture`
- Same-transaction path set:
{manifest}
- Final commit SHA is emitted after commit creation.
""",
        encoding="utf-8",
    )

    project_authorization = {
        "id": "PAUTH-TEST",
        "project_id": "PROJECT-TEST",
        "work_item_id": "WI-TEST",
        "proposal_project_id": "PROJECT-TEST",
        "version": 1,
        "normalized_envelope_hash": "test-envelope",
        "target_classifications": [{"path": path, "mutation_class": "source"} for path in protected_paths],
        "evaluator_id": "test-evaluator",
        "evaluator_version": "1",
        "evaluator_sha256": "test-evaluator-sha",
        "taxonomy_version": "1",
        "taxonomy_sha256": "test-taxonomy-sha",
    }
    packet = {
        "bridge_id": bridge_id,
        "created_at": "2026-07-19T00:00:00Z",
        "expires_at": "2099-07-19T00:00:00Z",
        "go_file": go,
        "latest_status": "GO",
        "project_authorization": project_authorization,
        "proposal_file": proposal,
        "schema_version": 2,
        "spec_links": ["GOV-FILE-BRIDGE-AUTHORITY-001"],
        "target_path_globs": protected_paths,
    }
    packet["packet_hash"] = module.packet_hash(packet)
    pre_start_hash = packet["packet_hash"]
    packet.pop("packet_hash")
    packet["schema_version"] = 3
    packet["implementation_start"] = {
        "schema_version": 1,
        "bridge_id": bridge_id,
        "finalized_at": "2026-07-19T00:00:00Z",
        "session_id": "pb-start-session",
        "pre_start_packet_hash": pre_start_hash,
        "target_path_globs": protected_paths,
        "work_intent_claim": {
            "thread_slug": bridge_id,
            "session_id": "pb-start-session",
            "claim_kind": "go_implementation",
            "acting_role": "prime-builder",
            "project_id": "PROJECT-TEST",
        },
        "worker_role_provenance": {
            "schema_version": 1,
            "session_id": "pb-start-session",
            "role": "prime-builder",
            "harness_id": "A",
        },
        "project_authorization_decision": {"allowed": True},
    }
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr(
        module,
        "validate_packet_project_authorization_operation",
        lambda root, packet, *, requested_operations, target_paths: {
            "operation_time_decisions": [{"allowed": True}],
            "requested_operations": requested_operations,
            "target_paths": target_paths,
        },
    )
    return selected_paths, report, verdict


def _stage_transaction(root: Path, selected_paths: list[str], report: str, verdict: str) -> None:
    hooks = root / "empty-hooks"
    hooks.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    proposal = report.replace("-003.md", "-001.md")
    go = report.replace("-003.md", "-002.md")
    subprocess.run(["git", "add", "--", proposal, go], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "fixture predecessors",
        ],
        cwd=root,
        check=True,
    )
    for rel_path in selected_paths:
        if rel_path in {report, verdict}:
            continue
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# staged implementation\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", *selected_paths], cwd=root, check=True)


def _init_committed_paths(root: Path, paths: list[str]) -> None:
    hooks = root / "empty-hooks"
    hooks.mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    for rel_path in paths:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# baseline {rel_path}\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", *paths], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "fixture baseline",
        ],
        cwd=root,
        check=True,
    )


def _seed_current_project_authorization(root: Path) -> None:
    (root / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    taxonomy_source = REPO_ROOT / "config" / "governance" / "project-authorization-operation-taxonomy.toml"
    taxonomy_target = root / "config" / "governance" / taxonomy_source.name
    taxonomy_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(taxonomy_source, taxonomy_target)
    conn = sqlite3.connect(root / "groundtruth.db")
    try:
        conn.execute("CREATE TABLE current_projects (id TEXT PRIMARY KEY, status TEXT NOT NULL)")
        conn.execute(
            """CREATE TABLE current_project_authorizations (
                id TEXT PRIMARY KEY,
                version INTEGER,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                authorization_name TEXT,
                owner_decision_deliberation_id TEXT,
                scope_summary TEXT,
                expires_at TEXT,
                supersedes TEXT,
                superseded_by TEXT,
                allowed_mutation_classes TEXT,
                forbidden_operations TEXT,
                included_work_item_ids TEXT,
                excluded_work_item_ids TEXT,
                included_spec_ids TEXT,
                excluded_spec_ids TEXT
            )"""
        )
        conn.execute("INSERT INTO current_projects (id, status) VALUES ('PROJECT-TEST', 'active')")
        conn.execute(
            """INSERT INTO current_project_authorizations VALUES
               (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "PAUTH-TEST",
                1,
                "PROJECT-TEST",
                "active",
                "Fixture authorization",
                "DELIB-TEST",
                "Authorize the exact source and test fixture.",
                None,
                json.dumps([]),
                json.dumps([]),
                json.dumps(["source", "test"]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def test_blocks_protected_path_without_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert result["findings"][0]["path"] == "scripts/foo.py"


def test_dot_prefixed_protected_surfaces_are_blocked_without_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    paths = [
        ".claude/hooks/h.py",
        ".codex/gtkb-hooks/h.py",
        ".github/workflows/ci.yml",
        ".claude/settings.json",
        ".codex/hooks.json",
    ]
    result = module.evaluate(tmp_path, paths=paths)

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == set(paths)


def test_live_go_packet_allows_protected_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "bridge_id": "gtkb-example",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-example.json",
                "valid": True,
                "target_path_globs": ["scripts/foo.py"],
                "error": None,
            }
        ],
    )

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "pass"
    assert result["cleared"][0]["evidence"] == "live_go_packet"


def test_terminal_verified_thread_allows_without_live_packet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(
        tmp_path,
        module,
        monkeypatch,
        bridge_id="gtkb-example",
        protected_paths=["scripts/foo.py"],
    )
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture terminal",
        ],
        cwd=tmp_path,
        check=True,
    )
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "pass"
    assert result["cleared"][0]["evidence"] == "terminal_verified_bridge_thread"

    proposal_path = tmp_path / report.replace("-003.md", "-001.md")
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace("scripts/foo.py", "scripts/worktree-evil.py"),
        encoding="utf-8",
    )
    pinned_result = module.evaluate(tmp_path, paths=["scripts/foo.py"])
    assert pinned_result["status"] == "pass"

    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / "gtkb-example.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["target_path_globs"] = ["scripts/packet-evil.py"]
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    tampered_result = module.evaluate(tmp_path, paths=["scripts/packet-evil.py"])
    assert tampered_result["status"] == "fail"


def test_terminal_verified_packet_root_must_be_an_object(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(
        tmp_path,
        module,
        monkeypatch,
        bridge_id="gtkb-terminal-root",
        protected_paths=["scripts/foo.py"],
    )
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture terminal",
        ],
        cwd=tmp_path,
        check=True,
    )
    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / "gtkb-terminal-root.json"
    packet_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert any(
        "decoded packet root is not an object" in error
        for finding in result["findings"]
        for error in finding.get("evidence_errors", [])
    )


def test_evaluation_pins_one_head_oid_across_index_and_terminal_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(
        tmp_path,
        module,
        monkeypatch,
        bridge_id="gtkb-pinned-head",
        protected_paths=["scripts/foo.py"],
    )
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    commit_args = [
        "git",
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        f"core.hooksPath={tmp_path / 'empty-hooks'}",
        "commit",
        "-qm",
    ]
    subprocess.run([*commit_args, "good terminal"], cwd=tmp_path, check=True)
    old_oid = subprocess.run(
        ["git", "rev-parse", "HEAD^{commit}"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    proposal_path = tmp_path / report.replace("-003.md", "-001.md")
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace("scripts/foo.py", "scripts/head-evil.py"),
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "--", report.replace("-003.md", "-001.md")], cwd=tmp_path, check=True)
    subprocess.run([*commit_args, "tampered successor"], cwd=tmp_path, check=True)
    new_oid = subprocess.run(
        ["git", "rev-parse", "HEAD^{commit}"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(["git", "update-ref", "HEAD", old_oid, new_oid], cwd=tmp_path, check=True)
    subprocess.run(["git", "read-tree", old_oid], cwd=tmp_path, check=True)
    implementation_path = tmp_path / "scripts" / "foo.py"
    implementation_path.write_text("# staged after captured head\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", "scripts/foo.py"], cwd=tmp_path, check=True)
    original_resolve = module._resolve_head_oid

    def advance_symbolic_head(root: Path) -> str:
        captured = original_resolve(root)
        assert captured == old_oid
        subprocess.run(["git", "update-ref", "HEAD", new_oid, old_oid], cwd=root, check=True)
        return captured

    monkeypatch.setattr(module, "_resolve_head_oid", advance_symbolic_head)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "pass"
    assert result["protected_paths"] == ["scripts/foo.py"]
    assert result["cleared"][0]["evidence"] == "terminal_verified_bridge_thread"


def test_routine_paths_short_circuit_before_packet_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()

    def fail_if_called(root):
        raise AssertionError("routine paths must not read implementation packets")

    monkeypatch.setattr(module, "list_named_packets", fail_if_called)

    result = module.evaluate(
        tmp_path,
        paths=[
            "memory/MEMORY.md",
            "docs/guide.md",
            "bridge/thread-note.md",
            ".gtkb-state/state.json",
            "independent-progress-assessments/report.md",
        ],
    )

    assert result["status"] == "pass"
    assert result["protected_paths"] == []


def test_verified_bridge_file_without_finalization_evidence_blocks(tmp_path: Path) -> None:
    module = _load_module()
    bridge_file = tmp_path / "bridge" / "gtkb-example-004.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text(
        """VERIFIED

# Verdict

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest fixture` | yes | PASS |
""",
        encoding="utf-8",
    )

    result = module.evaluate(tmp_path, paths=["bridge/gtkb-example-004.md"])

    assert result["status"] == "fail"
    assert "Commit Finalization Evidence" in result["findings"][0]["reason"]


def test_verified_bridge_file_with_finalization_evidence_passes(tmp_path: Path) -> None:
    module = _load_module()
    bridge_file = tmp_path / "bridge" / "gtkb-example-004.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text(
        """VERIFIED

# Verdict

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Same-transaction path set:
- `scripts/foo.py`
- `bridge/gtkb-example-003.md`
- `bridge/gtkb-example-004.md`
""",
        encoding="utf-8",
    )

    result = module.evaluate(tmp_path, paths=["bridge/gtkb-example-004.md"])

    assert result["status"] == "pass"
    assert result["findings"] == []


def test_corrupt_packet_blocks_protected_path_when_no_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "path": ".gtkb-state/implementation-authorizations/by-bridge/bad.json",
                "bridge_id": None,
                "valid": False,
                "target_path_globs": [],
                "error": "corrupt or unreadable",
            }
        ],
    )

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert "evidence_errors" in result["findings"][0]


def test_groundtruth_db_and_githooks_are_protected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["groundtruth.db", ".githooks/pre-commit"])

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == {"groundtruth.db", ".githooks/pre-commit"}


def test_bridge_index_and_runtime_state_paths_are_protected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    paths = [
        "bridge/INDEX.md",
        ".gtkb-state/implementation-authorizations/current.json",
        ".gtkb-state/work-intent/thread.json",
        ".gtkb-state/bridge-poller/dispatch-state.json",
        ".gtkb-state/dispatcher-daemon/status.json",
    ]
    result = module.evaluate(tmp_path, paths=paths)

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == set(paths)


def test_non_verified_numbered_bridge_files_remain_helper_commit_compatible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()

    def fail_if_called(root):
        raise AssertionError("non-VERIFIED numbered bridge files should not read implementation packets")

    monkeypatch.setattr(module, "list_named_packets", fail_if_called)
    bridge_file = tmp_path / "bridge" / "example-003.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text("NEW\n\n# Implementation report\n", encoding="utf-8")

    result = module.evaluate(tmp_path, paths=["bridge/example-003.md"])

    assert result["status"] == "pass"
    assert result["protected_paths"] == []


def test_json_shape_for_cli_paths(tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    exit_code = module.main(["--project-root", str(tmp_path), "--paths", "scripts/foo.py", "--json"])
    parsed = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert parsed["status"] == "fail"
    assert parsed["protected_paths"] == ["scripts/foo.py"]
    assert set(parsed) == {
        "status",
        "findings",
        "cleared",
        "skipped_unprotected",
        "protected_paths",
        "evidence_summary",
    }
    assert "transaction-local" not in parsed["findings"][0]["reason"]

    human_exit = module.main(["--project-root", str(tmp_path), "--paths", "scripts/foo.py"])
    human_output = capsys.readouterr().out
    assert human_exit == 1
    assert "transaction-local" not in human_output
    assert "committed terminal VERIFIED evidence" in human_output


def test_evidence_sources_are_loaded_once_for_343_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    calls = {"live": 0, "verified": 0}

    def live_packets(root):
        calls["live"] += 1
        return [
            {
                "bridge_id": "gtkb-live",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-live.json",
                "valid": True,
                "target_path_globs": ["scripts/live-*.py"],
                "error": None,
            }
        ]

    def verified_entry(root):
        calls["verified"] += 1
        return [("gtkb-verified", ["scripts/verified-*.py"])], [], 1

    monkeypatch.setattr(module, "list_named_packets", live_packets)
    monkeypatch.setattr(module, "_load_verified_evidence", lambda root, head_oid=None: verified_entry(root))
    paths = [f"scripts/live-{index}.py" for index in range(172)] + [
        f"scripts/verified-{index}.py" for index in range(171)
    ]

    result = module.evaluate(tmp_path, paths=paths)

    assert result["status"] == "pass"
    assert len(result["cleared"]) == 343
    assert calls == {"live": 1, "verified": 1}
    assert result["evidence_summary"] == {
        "live_go_packets_scanned": 1,
        "live_go_packets_valid": 1,
        "terminal_verified_packets_scanned": 1,
        "terminal_verified_threads_loaded": 1,
    }


def test_live_go_precedence_and_errors_match_snapshot_decisions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "bridge_id": None,
                "path": ".gtkb-state/implementation-authorizations/by-bridge/bad.json",
                "valid": False,
                "target_path_globs": [],
                "error": "corrupt or unreadable",
            },
            {
                "bridge_id": "gtkb-live",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-live.json",
                "valid": True,
                "target_path_globs": ["scripts/shared.py"],
                "error": None,
            },
        ],
    )
    monkeypatch.setattr(
        module,
        "_load_verified_evidence",
        lambda root, head_oid=None: ([("gtkb-verified", ["scripts/shared.py", "scripts/verified.py"])], [], 1),
    )

    result = module.evaluate(
        tmp_path,
        paths=["scripts/shared.py", "scripts/verified.py", "scripts/unauthorized.py"],
    )

    assert result["status"] == "fail"
    assert result["cleared"] == [
        {
            "path": "scripts/shared.py",
            "status": "cleared",
            "evidence": "live_go_packet",
            "source": "gtkb-live",
        },
        {
            "path": "scripts/verified.py",
            "status": "cleared",
            "evidence": "terminal_verified_bridge_thread",
            "source": "gtkb-verified",
        },
    ]
    assert result["findings"][0]["path"] == "scripts/unauthorized.py"
    assert result["findings"][0]["evidence_errors"] == [
        ".gtkb-state/implementation-authorizations/by-bridge/bad.json: corrupt or unreadable"
    ]


def test_transaction_local_verified_manifest_clears_wi5629_shaped_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    immutable_checks = {"anchors": False, "independence": False}
    proposal = report.replace("-003.md", "-001.md")

    def validate_anchors(content: str, project_root: Path):
        del content
        with pytest.raises(PermissionError):
            (project_root / proposal).write_text("transient anchor tamper\n", encoding="utf-8")
        immutable_checks["anchors"] = True
        return []

    def validate_independence(content: str, bridge_id: str, project_root: Path, **kwargs):
        del content, bridge_id, kwargs
        with pytest.raises(PermissionError):
            (project_root / report).write_text("transient independence tamper\n", encoding="utf-8")
        immutable_checks["independence"] = True
        return None

    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", validate_anchors)
    monkeypatch.setattr(module, "verdict_self_review_reason", validate_independence)
    pauth_calls = []

    def validate_pauth(root, packet, *, requested_operations, target_paths):
        pauth_calls.append((requested_operations, target_paths))
        return {"operation_time_decisions": [{"allowed": True}]}

    monkeypatch.setattr(module, "validate_packet_project_authorization_operation", validate_pauth)
    (tmp_path / verdict).write_text("MALFORMED WORKTREE BYTES\n", encoding="utf-8")

    result = module.evaluate(tmp_path)

    assert result["status"] == "pass"
    assert [item["evidence"] for item in result["cleared"]] == [
        "transaction_local_verified_manifest",
        "transaction_local_verified_manifest",
    ]
    assert {item["source"] for item in result["cleared"]} == {"gtkb-wi5629-fixture"}
    assert immutable_checks == {"anchors": True, "independence": True}
    assert pauth_calls == [
        (
            ["protected_mutation"],
            [
                "scripts/bridge_lifecycle_resolver.py",
                "platform_tests/scripts/test_bridge_lifecycle_resolver.py",
            ],
        )
    ]


def test_finalized_packet_uses_real_current_pauth_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    protected_paths, _, _ = _write_transaction_chain(tmp_path, module, monkeypatch)
    protected_paths = protected_paths[:2]
    _seed_current_project_authorization(tmp_path)
    monkeypatch.setattr(
        module,
        "validate_packet_project_authorization_operation",
        implementation_authorization.validate_packet_project_authorization_operation,
    )
    bridge_id = "gtkb-wi5629-fixture"
    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    row = implementation_authorization._project_authorization_row(tmp_path, "PAUTH-TEST")
    packet["project_authorization"] = implementation_authorization.validate_project_authorization_row(
        tmp_path,
        row,
        proposal_project_id="PROJECT-TEST",
        work_item_id=None,
        spec_links=packet["spec_links"],
        target_paths=protected_paths,
        requested_operations=["protected_mutation"],
    )
    start = packet.pop("implementation_start")
    packet.pop("packet_hash")
    packet["schema_version"] = 2
    packet["packet_hash"] = module.packet_hash(packet)
    start["pre_start_packet_hash"] = packet.pop("packet_hash")
    packet["schema_version"] = 3
    packet["implementation_start"] = start
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    chain = module._ApprovedChain(
        proposal_path=f"bridge/{bridge_id}-001.md",
        go_path=f"bridge/{bridge_id}-002.md",
        report_path=f"bridge/{bridge_id}-003.md",
        target_paths=tuple(protected_paths),
    )

    loaded, errors = module._load_finalized_packet(tmp_path, bridge_id, chain, protected_paths)

    assert errors == []
    assert loaded is not None

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute("UPDATE current_project_authorizations SET status = 'revoked' WHERE id = 'PAUTH-TEST'")
        conn.commit()
    finally:
        conn.close()
    loaded, errors = module._load_finalized_packet(tmp_path, bridge_id, chain, protected_paths)
    assert loaded is None
    assert any("PAUTH validation failed" in error and "not active" in error for error in errors)

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "UPDATE current_project_authorizations SET status = 'active', expires_at = '2000-01-01T00:00:00Z' "
            "WHERE id = 'PAUTH-TEST'"
        )
        conn.commit()
    finally:
        conn.close()
    loaded, errors = module._load_finalized_packet(tmp_path, bridge_id, chain, protected_paths)
    assert loaded is None
    assert any("PAUTH validation failed" in error and "expired" in error for error in errors)


def test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    gate_path = tmp_path / ".claude" / "hooks" / "bridge-compliance-gate.py"
    gate_path.parent.mkdir(parents=True)
    shutil.copy2(REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py", gate_path)
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "add", "--", ".claude/hooks/bridge-compliance-gate.py", "groundtruth.toml"], cwd=tmp_path, check=True
    )
    hooks = tmp_path / "empty-hooks"
    hooks.mkdir()
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "fixture authority",
        ],
        cwd=tmp_path,
        check=True,
    )
    bridge_id = "gtkb-hermetic-audit-fixture"
    candidate_rel = f"bridge/{bridge_id}-001.md"
    candidate_path = tmp_path / candidate_rel
    candidate_path.parent.mkdir()
    candidate_path.write_text(
        f"""ADVISORY
{_author("loyal-opposition", "019f0000-0000-7000-8000-000000000001")}
bridge_kind: governance_advisory
Document: {bridge_id}
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-07-19 UTC

# Hermetic audit fixture

## Source

Focused WI-5633 test fixture.

## Claim

The compliance audit must use only the prospective index snapshot.

## Owner Decision Needed

None.

## Recommended Prime Action

Retain fail-closed snapshot isolation.

## Classification Slot

Non-dispatchable governance advisory test fixture.
""",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "--", candidate_rel], cwd=tmp_path, check=True)
    hostile = tmp_path / "hostile-runtime"
    hostile.mkdir()
    marker = tmp_path / "sitecustomize-executed"
    (hostile / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('injected', encoding='utf-8')\n",
        encoding="utf-8",
    )
    (hostile / "git.cmd").write_text("@echo hostile-git-executed\r\n@exit /b 99\r\n", encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", str(hostile))
    monkeypatch.setenv("PYTHONHOME", str(hostile))
    monkeypatch.setenv("PATH", str(hostile))

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, bridge_id, index_snapshot) as bridge_snapshot,
    ):
        snapshot_root = bridge_snapshot.root
        assert snapshot_root.parent == tmp_path / ".gtkb-state"
        assert (snapshot_root / ".claude" / "hooks" / "bridge-compliance-gate.py").is_file()
        snapshot_candidate = snapshot_root / candidate_rel
        candidate = snapshot_candidate.read_text(encoding="utf-8")
        gate_path.write_text(
            "raise RuntimeError('live worktree gate must not execute')\n",
            encoding="utf-8",
        )

        audit = module._run_snapshot_compliance_audit(
            snapshot=bridge_snapshot,
            candidate_path=candidate_rel,
            content=candidate,
        )
        assert snapshot_candidate.is_file()

    assert audit["decision"] == "pass"
    assert not marker.exists()

    mutation_blocked = False

    def mutate_snapshot_authority(*, file_path: Path, content: str, project_root: Path):
        nonlocal mutation_blocked
        del file_path, content
        with pytest.raises(PermissionError):
            (project_root / "groundtruth.toml").write_text("tampered during audit\n", encoding="utf-8")
        mutation_blocked = True
        return {"decision": "pass"}

    monkeypatch.setattr(module, "run_bridge_compliance_audit", mutate_snapshot_authority)
    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, bridge_id, index_snapshot) as bridge_snapshot,
    ):
        module._run_snapshot_compliance_audit(
            snapshot=bridge_snapshot,
            candidate_path=candidate_rel,
            content=(bridge_snapshot.root / candidate_rel).read_text(encoding="utf-8"),
        )
    assert mutation_blocked is True


def test_transaction_local_manifest_must_equal_complete_staged_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    verdict_path = tmp_path / verdict
    verdict_path.write_text(
        verdict_path.read_text(encoding="utf-8").replace(
            "- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`\n",
            "",
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "--", verdict], cwd=tmp_path, check=True)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda content, project_root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(
        "manifest does not equal the staged path set" in error
        for finding in result["findings"]
        for error in finding.get("evidence_errors", [])
    )
    assert "transaction-local VERIFIED manifest evidence" in module._format_human(
        result,
        transaction_available=True,
    )


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        ("duplicate", "duplicate path"),
        ("glob", "glob path"),
        ("second_candidate", "exactly one VERIFIED candidate"),
    ],
)
def test_transaction_local_manifest_rejects_each_ambiguous_form(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    expected: str,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    verdict_path = tmp_path / verdict
    content = verdict_path.read_text(encoding="utf-8")
    staged = [verdict]
    if failure == "duplicate":
        content = content.replace(
            "- `scripts/bridge_lifecycle_resolver.py`\n",
            "- `scripts/bridge_lifecycle_resolver.py`\n- `scripts/bridge_lifecycle_resolver.py`\n",
        )
    elif failure == "glob":
        content = content.replace("- `scripts/bridge_lifecycle_resolver.py`\n", "- `scripts/*.py`\n")
    else:
        second_candidate = "bridge/gtkb-other-004.md"
        (tmp_path / second_candidate).write_text(
            content.replace("gtkb-wi5629-fixture", "gtkb-other"),
            encoding="utf-8",
        )
        staged.append(second_candidate)
    verdict_path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "--", *staged], cwd=tmp_path, check=True)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(expected in error for finding in result["findings"] for error in finding.get("evidence_errors", []))


@pytest.mark.parametrize(
    ("manifest_path", "expected"),
    [
        ("../outside.py", "path escape"),
        (".git/config", "forbidden Git path"),
        ("scripts/*.py", "glob path"),
        ("scripts/", "directory shorthand"),
        (" scripts/leading.py", "non-canonical or unsafe"),
        ("scripts/back\\slash.py", "non-canonical or unsafe"),
        ("scripts/CON.txt", "non-canonical or unsafe"),
    ],
)
def test_transaction_manifest_rejects_unsafe_path_forms(
    tmp_path: Path,
    manifest_path: str,
    expected: str,
) -> None:
    module = _load_module()
    content = f"""VERIFIED

## Commit Finalization Evidence

- Same-transaction path set:
- `{manifest_path}`
"""

    _, errors = module._parse_transaction_manifest(tmp_path, content)

    assert any(expected in error for error in errors)


def test_transaction_manifest_rejects_casefold_collision(tmp_path: Path) -> None:
    module = _load_module()
    content = """VERIFIED

## Commit Finalization Evidence

- Same-transaction path set:
- `Scripts/Authority.py`
- `scripts/authority.py`
"""

    _, errors = module._parse_transaction_manifest(tmp_path, content)

    assert any("casefold or Unicode collision" in error for error in errors)


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        ("self_review", "same-session self-review"),
        ("duplicate_session", "exactly one author_session_context_id"),
        ("duplicate_report_session", "exactly one author_session_context_id"),
        ("missing_packet", "implementation-start packet is absent"),
        ("corrupt_json", "packet is not valid JSON"),
        ("packet_root", "packet root is not an object"),
        ("packet_hash", "packet hash mismatch"),
        ("packet_schema", "unsupported schema"),
        ("missing_start", "packet is not finalized"),
        ("start_schema", "implementation-start evidence has an unsupported schema"),
        ("missing_start_session", "implementation-start lacks a session id"),
        ("missing_claim", "lacks a work-intent claim"),
        ("claim_kind", "claim kind is not go_implementation"),
        ("claim_role", "claim acting role is not prime-builder"),
        ("claim_session", "claim session differs from start session"),
        ("wrong_bridge", "names another bridge"),
        ("not_finalized", "packet is not finalized"),
        ("decision_denied", "lacks an allowed project decision"),
        ("missing_pauth", "lacks project authorization"),
        ("expired", "packet has expired"),
        ("invalid_expiry", "packet has invalid expiry"),
        ("proposal_drift", "resolver-approved proposal"),
        ("go_drift", "resolver-approved GO"),
        ("prestart_hash", "pre-start packet hash mismatch"),
        ("session_drift", "worker session differs from start session"),
        ("provenance_schema", "worker provenance schema is unsupported"),
        ("provenance_role", "worker role is not prime-builder"),
        ("claim_project", "claim project differs from packet PAUTH"),
        ("out_of_scope", "target scope differs"),
        ("pauth_denied", "protected-mutation PAUTH validation failed"),
    ],
)
def test_transaction_local_candidate_fails_closed_on_provenance_and_packet_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    expected: str,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    if failure == "self_review":
        report_path = tmp_path / report
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace("pb-session", "lo-session"),
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "--", report], cwd=tmp_path, check=True)
    elif failure == "duplicate_session":
        verdict_path = tmp_path / verdict
        verdict_path.write_text(
            verdict_path.read_text(encoding="utf-8") + "\nauthor_session_context_id: second-reviewer-session\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "--", verdict], cwd=tmp_path, check=True)
    elif failure == "duplicate_report_session":
        report_path = tmp_path / report
        report_path.write_text(
            report_path.read_text(encoding="utf-8") + "\nauthor_session_context_id: second-pb-session\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "--", report], cwd=tmp_path, check=True)
    elif failure == "pauth_denied":
        monkeypatch.setattr(
            module,
            "validate_packet_project_authorization_operation",
            lambda *args, **kwargs: (_ for _ in ()).throw(module.AuthorizationError("current PAUTH denied")),
        )
    else:
        packet_path = (
            tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / "gtkb-wi5629-fixture.json"
        )
        if failure == "missing_packet":
            packet_path.unlink()
            packet = None
        elif failure == "corrupt_json":
            packet_path.write_text("{", encoding="utf-8")
            packet = None
        elif failure == "packet_root":
            packet_path.write_text("[]", encoding="utf-8")
            packet = None
        else:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        if packet is not None:
            if failure == "packet_hash":
                packet["packet_hash"] = "sha256:wrong"
            elif failure == "packet_schema":
                packet["schema_version"] = 2
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_start":
                packet.pop("implementation_start")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "start_schema":
                packet["implementation_start"]["schema_version"] = 2
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_start_session":
                packet["implementation_start"].pop("session_id")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_claim":
                packet["implementation_start"].pop("work_intent_claim")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_kind":
                packet["implementation_start"]["work_intent_claim"]["claim_kind"] = "draft_review"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_role":
                packet["implementation_start"]["work_intent_claim"]["acting_role"] = "loyal-opposition"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_session":
                packet["implementation_start"]["work_intent_claim"]["session_id"] = "other-session"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "wrong_bridge":
                packet["implementation_start"]["bridge_id"] = "gtkb-other"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "not_finalized":
                packet["implementation_start"].pop("finalized_at")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "decision_denied":
                packet["implementation_start"]["project_authorization_decision"] = {"allowed": False}
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_pauth":
                packet.pop("project_authorization")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "expired":
                packet["expires_at"] = "2000-01-01T00:00:00Z"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "invalid_expiry":
                packet["expires_at"] = "not-a-timestamp"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "proposal_drift":
                packet["proposal_file"] = "bridge/gtkb-other-001.md"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "go_drift":
                packet["go_file"] = "bridge/gtkb-other-002.md"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "prestart_hash":
                packet["implementation_start"]["pre_start_packet_hash"] = "sha256:wrong"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "session_drift":
                packet["implementation_start"]["worker_role_provenance"]["session_id"] = "other-session"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "provenance_schema":
                packet["implementation_start"]["worker_role_provenance"]["schema_version"] = 2
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "provenance_role":
                packet["implementation_start"]["worker_role_provenance"]["role"] = "loyal-opposition"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_project":
                packet["implementation_start"]["work_intent_claim"]["project_id"] = "PROJECT-OTHER"
                packet["packet_hash"] = module.packet_hash(packet)
            else:
                packet["target_path_globs"] = ["scripts/bridge_lifecycle_resolver.py"]
                packet["implementation_start"]["target_path_globs"] = packet["target_path_globs"]
                packet["packet_hash"] = module.packet_hash(packet)
            packet_path.write_text(json.dumps(packet), encoding="utf-8")

    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda content, project_root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(
        finding.get("path") == verdict and any(expected in error for error in finding.get("evidence_errors", []))
        for finding in result["findings"]
    )


def test_explicit_paths_mode_never_grants_transaction_local_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=selected_paths)

    assert result["status"] == "fail"
    assert all(item.get("evidence") != "transaction_local_verified_manifest" for item in result["cleared"])


def test_cli_rejects_staged_and_explicit_paths_together() -> None:
    module = _load_module()

    with pytest.raises(SystemExit):
        module.main(["--staged", "--paths", "scripts/foo.py"])


def test_index_snapshot_includes_deletions_and_both_rename_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["scripts/delete.py", "scripts/old.py"])
    subprocess.run(["git", "rm", "-q", "--", "scripts/delete.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "mv", "scripts/old.py", "scripts/new.py"], cwd=tmp_path, check=True)

    with module._index_snapshot(tmp_path) as snapshot:
        assert set(snapshot.selected_paths) == {
            "scripts/delete.py",
            "scripts/old.py",
            "scripts/new.py",
        }
        assert snapshot.status_by_path == {
            "scripts/delete.py": "D",
            "scripts/old.py": "R-source",
            "scripts/new.py": "R-destination",
        }

    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    result = module.evaluate(tmp_path)
    assert result["status"] == "fail"
    assert set(result["protected_paths"]) == {
        "scripts/delete.py",
        "scripts/old.py",
        "scripts/new.py",
    }


@pytest.mark.parametrize(
    ("mode", "stage", "expected"),
    [
        ("120000", "0", "unsupported index mode 120000"),
        ("160000", "0", "unsupported index mode 160000"),
        ("100664", "0", "unsupported index mode 100664"),
        ("100644", "2", "unmerged index entry"),
    ],
)
def test_raw_index_inventory_rejects_links_gitlinks_modes_and_unmerged_entries(
    mode: str,
    stage: str,
    expected: str,
) -> None:
    module = _load_module()
    raw = f"{mode} {'0' * 40} {stage}\tscripts/unsafe.py\0".encode()

    with pytest.raises(module.GateError, match=expected):
        module._parse_index_inventory(raw)


def test_raw_index_materialization_bypasses_smudge_and_eol_filters(tmp_path: Path) -> None:
    module = _load_module()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitattributes").write_text("*.txt text eol=crlf\n", encoding="utf-8")
    (tmp_path / "authority.txt").write_bytes(b"authority\n")
    subprocess.run(["git", "add", "--", ".gitattributes", "authority.txt"], cwd=tmp_path, check=True)
    hooks = tmp_path / "empty-hooks"
    hooks.mkdir()
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "raw materialization fixture",
        ],
        cwd=tmp_path,
        check=True,
    )

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, "gtkb-unused", index_snapshot) as bridge_snapshot,
    ):
        assert (bridge_snapshot.root / "authority.txt").read_bytes() == b"authority\n"


def test_scratch_root_rejects_parent_junction_or_reparse_point(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    scratch = tmp_path / ".gtkb-state"
    scratch.mkdir()
    original = module._path_is_linklike
    monkeypatch.setattr(
        module,
        "_path_is_linklike",
        lambda path: path == scratch or original(path),
    )

    with pytest.raises(module.GateError, match="symlink, junction, or reparse"):
        module._scratch_root(tmp_path)


def test_raw_materialization_ignores_replace_refs_and_git_environment_injection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["authority.txt"])
    original = subprocess.run(
        ["git", "rev-parse", ":authority.txt"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    original_bytes = subprocess.run(
        ["git", "cat-file", "blob", original],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    ).stdout
    replacement = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=tmp_path,
        check=True,
        input="replacement bytes\n",
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(["git", "replace", original, replacement], cwd=tmp_path, check=True)
    hostile = tmp_path / "hostile-objects"
    hostile.mkdir()
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", str(hostile))
    monkeypatch.setenv("GIT_ALTERNATE_OBJECT_DIRECTORIES", str(hostile))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(hostile))

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, "gtkb-unused", index_snapshot) as bridge_snapshot,
    ):
        assert index_snapshot.object_format == "sha1"
        assert (bridge_snapshot.root / "authority.txt").read_bytes() == original_bytes
        assert index_snapshot.env["GIT_NO_REPLACE_OBJECTS"] == "1"
        assert "GIT_OBJECT_DIRECTORY" not in index_snapshot.env
        assert "GIT_CONFIG_COUNT" not in index_snapshot.env


@pytest.mark.parametrize(
    "raw_path",
    [
        b" scripts/leading.py",
        b"scripts/trailing.py ",
        b"scripts\\backslash.py",
        b"scripts/trailing-dot.",
        b"scripts/CON.txt",
    ],
)
def test_raw_index_inventory_rejects_noncanonical_platform_paths(raw_path: bytes) -> None:
    module = _load_module()
    raw = b"100644 " + (b"0" * 40) + b" 0\t" + raw_path + b"\0"

    with pytest.raises(module.GateError, match="non-canonical|unsafe|platform-reserved"):
        module._parse_index_inventory(raw)


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("Scripts/Authority.py", "scripts/authority.py"),
        ("scripts/\u00e9.py", "scripts/e\u0301.py"),
    ],
)
def test_raw_index_inventory_rejects_casefold_and_unicode_collisions(first: str, second: str) -> None:
    module = _load_module()
    records = [
        f"100644 {'0' * 40} 0\t{first}".encode(),
        f"100644 {'1' * 40} 0\t{second}".encode(),
    ]

    with pytest.raises(module.GateError, match="casefold or Unicode-normalized"):
        module._parse_index_inventory(b"\0".join(records) + b"\0")


def test_raw_materialization_fails_closed_on_blob_resource_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["authority.txt"])
    monkeypatch.setattr(module, "MAX_BLOB_BYTES", 1)

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        pytest.raises(module.GateError, match="materialization limit"),
        module._bridge_snapshot(tmp_path, "gtkb-unused", index_snapshot),
    ):
        pass


def test_index_snapshot_parser_fails_closed_on_unsupported_status() -> None:
    module = _load_module()

    with pytest.raises(module.GateError, match="unsupported staged Git status"):
        module._parse_staged_name_status(b"T\x00scripts/type-change.py\x00")

    with pytest.raises(module.GateError, match="non-canonical path bytes"):
        module._parse_staged_name_status(b"A\x00 scripts/leading.py\x00")


def test_git_resolution_ignores_hostile_path_at_module_startup(tmp_path: Path) -> None:
    hostile = tmp_path / "hostile-path"
    hostile.mkdir()
    marker = tmp_path / "hostile-git-executed"
    (hostile / "git.cmd").write_text(
        f"@echo hostile>{marker}\r\n@exit /b 0\r\n",
        encoding="utf-8",
    )
    hostile_posix = hostile / "git"
    hostile_posix.write_text(
        f"#!/bin/sh\nprintf hostile > {marker!s}\nexit 0\n",
        encoding="utf-8",
    )
    hostile_posix.chmod(0o755)
    child = f"""
import importlib.util
import json
import pathlib
import sys
spec = importlib.util.spec_from_file_location("checker_startup_fixture", {str(SCRIPT_PATH)!r})
module = importlib.util.module_from_spec(spec)
sys.modules["checker_startup_fixture"] = module
spec.loader.exec_module(module)
result = module._run_git(pathlib.Path({str(REPO_ROOT)!r}), "--version", text=True)
print(json.dumps({{"path": module._trusted_git_executable(), "returncode": result.returncode, "stdout": result.stdout}}))
"""
    env = os.environ.copy()
    env["PATH"] = str(hostile)
    result = subprocess.run(
        [str(Path(sys.executable).resolve()), "-I", "-B", "-c", child],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert Path(payload["path"]).resolve().parent != hostile.resolve()
    assert payload["returncode"] == 0
    assert payload["stdout"].startswith("git version ")
    assert not marker.exists()


def test_copied_index_cannot_be_replaced_between_consumers(tmp_path: Path) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["authority.txt"])
    replacement = tmp_path / "replacement-index"
    replacement.write_bytes((tmp_path / ".git" / "index").read_bytes())

    with module._index_snapshot(tmp_path) as snapshot:
        module._index_entries(tmp_path, snapshot)
        with pytest.raises(OSError):
            os.replace(replacement, snapshot.index_file)
        assert module._staged_text(tmp_path, "authority.txt", snapshot).startswith("# baseline")


def test_committed_terminal_snapshot_blocks_transient_substitution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture terminal chain",
        ],
        cwd=tmp_path,
        check=True,
    )
    head_oid = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    original_resolver = module.resolve_bridge_lifecycle
    attempts: list[str] = []

    def attack_snapshot(snapshot_root: Path, bridge_id: str):
        proposal = snapshot_root / f"bridge/{bridge_id}-001.md"
        replacement = snapshot_root.parent / "replacement-proposal.md"
        replacement.write_text("NO-GO\n", encoding="utf-8")
        with pytest.raises(OSError):
            os.replace(replacement, proposal)
        attempts.append("entry")
        renamed_root = snapshot_root.with_name(f"{snapshot_root.name}-renamed")
        with pytest.raises(OSError):
            os.replace(snapshot_root, renamed_root)
        attempts.append("root")
        return original_resolver(snapshot_root, bridge_id)

    monkeypatch.setattr(module, "resolve_bridge_lifecycle", attack_snapshot)
    evidence, errors, count = module._load_verified_evidence(tmp_path, head_oid=head_oid)

    assert count == 1
    assert not errors
    assert evidence
    assert attempts == ["entry", "root"]


def test_snapshot_hardlink_race_fails_closed_on_link_count_drift(tmp_path: Path) -> None:
    module = _load_module()
    bridge_id = "gtkb-hardlink-race-fixture"
    rel_path = f"bridge/{bridge_id}-001.md"
    _init_committed_paths(tmp_path, [rel_path])
    head_oid = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    hardlink = tmp_path / ".gtkb-state" / "hardlink-race"

    with module._bridge_snapshot(tmp_path, bridge_id, head_oid=head_oid) as snapshot:
        authority = snapshot.root / rel_path
        with (
            pytest.raises(module.GateError, match="identity drifted"),
            module._immutable_snapshot(snapshot),
        ):
            os.link(authority, hardlink)

    hardlink.unlink()


# --- WI-5658: protected-commit checker performance (hoist ls-tree; git timeout) -
#
# Governing specs: GOV-FILE-BRIDGE-AUTHORITY-001 (the commit-finalization gate must
# be fast enough to run as a pre-commit hook); DCL-VERIFIED-SPEC-DERIVED-TESTING-
# MANDATORY-001. The committed-bridge enumeration is hoisted out of the
# _load_verified_evidence per-packet loop (O(packets + files) instead of
# O(packets x files)), and every _run_git call is timeout-bounded and fails closed.


def test_wi5658_run_git_times_out_fails_closed(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "_git_command", lambda *a: ["git", *a])
    monkeypatch.setattr(module, "_sanitized_subprocess_env", lambda **k: {})

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["git"], timeout=kwargs.get("timeout"))

    monkeypatch.setattr(module.subprocess, "run", _raise_timeout)
    result = module._run_git(tmp_path, "ls-tree", "-r", "HEAD", text=True)
    # Fails closed (non-zero) with a timeout message instead of hanging or raising.
    assert result.returncode == 124
    assert "timed out" in result.stderr


def test_wi5658_committed_bridge_entries_by_id_groups_by_exact_slug(tmp_path: Path) -> None:
    module = _load_module()
    _init_committed_paths(
        tmp_path,
        [
            "bridge/slug-a-001.md",
            "bridge/slug-a-002.md",
            "bridge/slug-a-v2-001.md",
            "bridge/slug-b-001.md",
            "bridge/not-a-versioned-file.md",
        ],
    )
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True).stdout.strip()
    grouped = module._committed_bridge_entries_by_id(tmp_path, head)
    assert {e.rel_path for e in grouped.get("slug-a", ())} == {"bridge/slug-a-001.md", "bridge/slug-a-002.md"}
    # Exact-slug: slug-a-v2 is a DIFFERENT chain, not folded into slug-a.
    assert {e.rel_path for e in grouped.get("slug-a-v2", ())} == {"bridge/slug-a-v2-001.md"}
    assert {e.rel_path for e in grouped.get("slug-b", ())} == {"bridge/slug-b-001.md"}
    # Non-versioned bridge files are excluded.
    assert all("not-a-versioned-file" not in e.rel_path for entries in grouped.values() for e in entries)


def test_wi5658_load_verified_evidence_enumerates_committed_bridge_once(monkeypatch, tmp_path: Path) -> None:
    # Core perf property: for N packets, the committed bridge tree is enumerated via
    # ls-tree exactly ONCE (not once per packet, which was the O(packets x files) hang).
    module = _load_module()
    _init_committed_paths(tmp_path, ["bridge/seed-001.md"])
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True).stdout.strip()
    pkt_dir = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    pkt_dir.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        (pkt_dir / f"slug-{i}.json").write_text(json.dumps({"bridge_id": f"slug-{i}"}), encoding="utf-8")

    ls_tree_calls = {"n": 0}
    real_run_git = module._run_git

    def _counting_run_git(root, *args, **kwargs):
        if args and args[0] == "ls-tree":
            ls_tree_calls["n"] += 1
        return real_run_git(root, *args, **kwargs)

    monkeypatch.setattr(module, "_run_git", _counting_run_git)
    module._load_verified_evidence(tmp_path, head_oid=head)
    assert ls_tree_calls["n"] == 1, (
        f"committed bridge tree must be enumerated once, not per-packet; got {ls_tree_calls['n']}"
    )
