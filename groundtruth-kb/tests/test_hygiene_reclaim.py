from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from groundtruth_kb.hygiene.reclaim import (
    ReclaimError,
    history_reclaim,
    plan_reclaim,
    restore_reclaim,
    trash_reclaim,
)
from groundtruth_kb.project.sot_registry import load_toml, sync_projection

NOW = datetime(2026, 7, 16, 4, 0, tzinfo=UTC)


def _git(root: Path, *args: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_projection(root: Path) -> None:
    db_path = root / "groundtruth.db"
    if db_path.exists():
        return
    with sqlite3.connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE sot_artifacts (
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                domain TEXT NOT NULL,
                lifecycle TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                authority_spec_id TEXT NOT NULL,
                mutation_api TEXT NOT NULL,
                versioning_policy TEXT NOT NULL,
                backup_policy TEXT NOT NULL,
                health_check_function TEXT,
                owner_role TEXT NOT NULL,
                depends_on TEXT,
                forbidden_substitutes TEXT,
                notes TEXT,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL,
                PRIMARY KEY (id, version)
            );
            CREATE VIEW current_sot_artifacts AS
            SELECT artifact.* FROM sot_artifacts artifact
            INNER JOIN (
                SELECT id, MAX(version) AS max_version FROM sot_artifacts GROUP BY id
            ) current
            ON artifact.id = current.id AND artifact.version = current.max_version;
            """
        )


def _write_registry(root: Path, storage_path: str | None = None, *, sync: bool = True) -> None:
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    if storage_path is None:
        registry.write_text("artifacts = []\n", encoding="utf-8")
    else:
        registry.write_text(
            "\n".join(
                [
                    "[[artifacts]]",
                    'id = "protected-fixture"',
                    'domain = "runtime_state"',
                    'lifecycle = "active"',
                    f'storage_path = "{storage_path}"',
                    'authority_spec_id = "TEST-SPEC"',
                    'mutation_api = "fixture"',
                    'versioning_policy = "overwrite_single_writer"',
                    'backup_policy = "gitignored_runtime"',
                    'restore_action = "noop"',
                    'health_check_function = ""',
                    'owner_role = "shared"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
    _init_projection(root)
    if sync:
        sync_projection(load_toml(registry), root / "groundtruth.db", changed_by="test", change_reason="fixture")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.name", "Reclaim Test")
    _git(root, "config", "user.email", "reclaim@example.invalid")
    _write_registry(root)
    _git(root, "add", "config/registry/sot-artifacts.toml")
    _git(root, "commit", "-m", "fixture registry")
    return root


def _old_scratch(root: Path, content: str = "stale scratch\n") -> Path:
    path = root / "scratch" / ".harness-tmp" / "candidate.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    old = (NOW - timedelta(hours=200)).timestamp()
    os.utime(path, (old, old))
    return path


def _single_plan(root: Path) -> tuple[dict[str, object], str]:
    plan = plan_reclaim(root, now=NOW)
    assert plan["candidate_count"] == 1
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))
    item_id = str(manifest["items"][0]["item_id"])
    return plan, item_id


def _trash(root: Path, plan: dict[str, object], item_id: str) -> dict[str, object]:
    return trash_reclaim(
        root,
        run_id=str(plan["run_id"]),
        plan_hash=str(plan["plan_hash"]),
        item_ids=[item_id],
        owner_evidence=["DELIB-TEST-OWNER-APPLY"],
        quiescence_evidence=["TEST-QUIESCENCE-OK"],
    )


def test_plan_hashes_and_item_ids_are_stable(repo: Path) -> None:
    _old_scratch(repo)

    first = plan_reclaim(repo, now=NOW, actor="tester", session_id="session-1")
    second = plan_reclaim(repo, now=NOW, actor="tester", session_id="session-1")

    assert first["plan_hash"] == second["plan_hash"]
    assert first["run_id"] == second["run_id"]
    assert first["item_preview"] == second["item_preview"]
    assert first["executable"] is True
    assert Path(str(first["manifest_path"])).is_file()
    assert Path(str(first["summary_path"])).is_file()
    assert Path(str(first["events_path"])).is_file()


def test_registry_match_is_a_preservation_veto(repo: Path) -> None:
    candidate = _old_scratch(repo)
    rel_path = candidate.relative_to(repo).as_posix()
    _write_registry(repo, rel_path)
    _git(repo, "add", "config/registry/sot-artifacts.toml")
    _git(repo, "commit", "-m", "register fixture")

    plan = plan_reclaim(repo, now=NOW)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))

    assert plan["candidate_count"] == 0
    assert any(item["classification"] == "registered_veto" for item in manifest["preserved"])


def test_bad_registry_allows_enumeration_but_blocks_execution(repo: Path) -> None:
    _old_scratch(repo)
    registry = repo / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text('[[artifacts]]\nid = "broken"\n', encoding="utf-8")

    plan, item_id = _single_plan(repo)

    assert plan["executable"] is False
    assert "registry_load_failed" in plan["blockers"]
    with pytest.raises(ReclaimError, match="plan_not_executable"):
        _trash(repo, plan, item_id)
    history = history_reclaim(repo, run_id=str(plan["run_id"]), item_id=item_id)
    assert history["items"][0]["status"] == "refused"


def test_git_roots_and_tracked_paths_are_preserved(repo: Path) -> None:
    tracked_scratch = repo / "tracked" / ".harness-tmp" / "tracked.txt"
    tracked_scratch.parent.mkdir(parents=True)
    tracked_scratch.write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", tracked_scratch.relative_to(repo).as_posix())
    staged_oid = _git(repo, "hash-object", tracked_scratch.relative_to(repo).as_posix())
    old = (NOW - timedelta(hours=200)).timestamp()
    staged_object = repo / ".git" / "objects" / staged_oid[:2] / staged_oid[2:]
    os.utime(staged_object, (old, old))

    loose_source = repo / "loose-source"
    loose_source.write_text("unreachable\n", encoding="utf-8")
    unreachable_oid = _git(repo, "hash-object", "-w", "loose-source")
    loose_source.unlink()
    unreachable_path = repo / ".git" / "objects" / unreachable_oid[:2] / unreachable_oid[2:]
    os.utime(unreachable_path, (old, old))

    plan = plan_reclaim(repo, now=NOW)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))
    paths = {item["path"] for item in manifest["items"]}

    assert tracked_scratch.relative_to(repo).as_posix() not in paths
    assert staged_object.relative_to(repo).as_posix() not in paths
    assert unreachable_path.relative_to(repo).as_posix() in paths


def test_git_temp_and_malformed_object_artifacts_are_preserved(repo: Path) -> None:
    fanout = repo / ".git" / "objects" / "aa"
    fanout.mkdir(exist_ok=True)
    temporary = fanout / "tmp_obj_incomplete"
    malformed = fanout / "not-an-object"
    temporary.write_bytes(b"partial")
    malformed.write_bytes(b"ambiguous")
    old = (NOW - timedelta(hours=200)).timestamp()
    os.utime(temporary, (old, old))
    os.utime(malformed, (old, old))

    plan = plan_reclaim(repo, now=NOW)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))
    classes = {item["classification"] for item in manifest["preserved"]}
    paths = {item["path"] for item in manifest["items"]}

    assert "ambiguous_git_temp_object" in classes
    assert "malformed_loose_object" in classes
    assert temporary.relative_to(repo).as_posix() not in paths
    assert malformed.relative_to(repo).as_posix() not in paths


def test_trash_refuses_missing_evidence_and_changed_candidate(repo: Path) -> None:
    candidate = _old_scratch(repo)
    plan, item_id = _single_plan(repo)

    with pytest.raises(ReclaimError, match="evidence_missing"):
        trash_reclaim(
            repo,
            run_id=str(plan["run_id"]),
            plan_hash=str(plan["plan_hash"]),
            item_ids=[item_id],
            owner_evidence=[],
            quiescence_evidence=["quiet"],
        )

    candidate.write_text("changed after planning\n", encoding="utf-8")
    with pytest.raises(ReclaimError, match="candidate_revalidation_failed"):
        _trash(repo, plan, item_id)
    assert candidate.read_text(encoding="utf-8") == "changed after planning\n"


def test_trash_and_restore_are_reversible_and_report_zero_physical_bytes(repo: Path) -> None:
    candidate = _old_scratch(repo, "reversible\n")
    expected_size = candidate.stat().st_size
    plan, item_id = _single_plan(repo)

    trashed = _trash(repo, plan, item_id)

    assert trashed["status"] == "trashed"
    assert trashed["physical_bytes_reclaimed"] == 0
    assert trashed["logical_bytes_removed"] == expected_size
    assert not candidate.exists()
    assert history_reclaim(repo, run_id=str(plan["run_id"]))["status"] == "trashed"

    restored = restore_reclaim(repo, run_id=str(plan["run_id"]), item_ids=[item_id])

    assert restored["status"] == "restored"
    assert restored["physical_bytes_reclaimed"] == 0
    assert candidate.read_text(encoding="utf-8") == "reversible\n"
    assert history_reclaim(repo, run_id=str(plan["run_id"]))["status"] == "restored"


def test_restore_refuses_overwrite_and_preserves_payload(repo: Path) -> None:
    candidate = _old_scratch(repo, "payload\n")
    plan, item_id = _single_plan(repo)
    trashed = _trash(repo, plan, item_id)
    payload = Path(str(plan["manifest_path"])).parent / str(trashed["trashed"][0]["payload_path"])
    candidate.write_text("collision\n", encoding="utf-8")

    with pytest.raises(ReclaimError, match="restore_revalidation_failed"):
        restore_reclaim(repo, run_id=str(plan["run_id"]), item_ids=[item_id])

    assert candidate.read_text(encoding="utf-8") == "collision\n"
    assert payload.read_text(encoding="utf-8") == "payload\n"


def test_history_detects_event_tampering(repo: Path) -> None:
    _old_scratch(repo)
    plan, _item_id = _single_plan(repo)
    events_path = Path(str(plan["events_path"]))
    lines = events_path.read_text(encoding="utf-8").splitlines()
    event = json.loads(lines[-1])
    event["details"]["path"] = "tampered"
    lines[-1] = json.dumps(event, separators=(",", ":"), sort_keys=True)
    events_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    history = history_reclaim(repo, run_id=str(plan["run_id"]))

    assert history["status"] == "corrupt"
    assert history["integrity"]["valid"] is False
    assert any("event_hash_mismatch" in error for error in history["integrity"]["errors"])


def test_history_detects_partial_event_log(repo: Path) -> None:
    _old_scratch(repo)
    plan, _item_id = _single_plan(repo)
    events_path = Path(str(plan["events_path"]))
    payload = events_path.read_bytes()
    events_path.write_bytes(payload.rstrip(b"\n"))

    history = history_reclaim(repo, run_id=str(plan["run_id"]))

    assert history["status"] == "corrupt"
    assert history["integrity"]["valid"] is False
    assert history["integrity"]["partial"] is True
    assert "events_truncated_final_line" in history["integrity"]["errors"]


def test_projection_drift_blocks_execution_but_preserves_candidates(repo: Path) -> None:
    _old_scratch(repo)
    _write_registry(repo, "config/registry/sot-artifacts.toml")
    registry = repo / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8").replace('mutation_api = "fixture"', 'mutation_api = "changed"'),
        encoding="utf-8",
    )

    plan, _item_id = _single_plan(repo)

    assert plan["executable"] is False
    assert "registry_projection_out_of_sync" in plan["blockers"]


def test_history_detects_summary_tampering(repo: Path) -> None:
    _old_scratch(repo)
    plan, _item_id = _single_plan(repo)
    summary_path = Path(str(plan["summary_path"]))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["candidate_count"] = 999
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    history = history_reclaim(repo, run_id=str(plan["run_id"]))

    assert history["status"] == "corrupt"
    assert "summary_field_mismatch:candidate_count" in history["integrity"]["errors"]
    assert "summary_hash_mismatch" in history["integrity"]["errors"]


def test_operation_lock_refuses_concurrent_actuator(repo: Path) -> None:
    candidate = _old_scratch(repo)
    plan, item_id = _single_plan(repo)
    run_dir = Path(str(plan["manifest_path"])).parent
    (run_dir / "operation.lock").write_text("occupied\n", encoding="utf-8")

    with pytest.raises(ReclaimError, match="operation_in_progress"):
        _trash(repo, plan, item_id)

    assert candidate.is_file()


def test_trash_refuses_symlinked_destination_root(repo: Path) -> None:
    candidate = _old_scratch(repo)
    plan, item_id = _single_plan(repo)
    run_dir = Path(str(plan["manifest_path"])).parent
    outside = repo / "outside-trash"
    outside.mkdir()
    try:
        (run_dir / "trash").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks unavailable: {exc}")

    with pytest.raises(ReclaimError, match="trash_destination_failed"):
        _trash(repo, plan, item_id)

    assert candidate.is_file()
    assert list(outside.iterdir()) == []


def test_run_level_refusal_is_visible_in_compact_history(repo: Path) -> None:
    _old_scratch(repo)
    plan, _item_id = _single_plan(repo)

    with pytest.raises(ReclaimError, match="unknown_item_id"):
        trash_reclaim(
            repo,
            run_id=str(plan["run_id"]),
            plan_hash=str(plan["plan_hash"]),
            item_ids=["item-does-not-exist"],
            owner_evidence=["DELIB-TEST-OWNER-APPLY"],
            quiescence_evidence=["TEST-QUIESCENCE-OK"],
        )

    history = history_reclaim(repo, run_id=str(plan["run_id"]))
    assert history["status"] == "refused"
    assert history["run_refusals"][0]["code"] == "unknown_item_id"
