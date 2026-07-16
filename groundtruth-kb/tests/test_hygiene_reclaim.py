from __future__ import annotations

import json
import os
import sqlite3
import stat
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from groundtruth_kb.hygiene.reclaim import (
    ReclaimError,
    _append_event,
    deep_clean_reclaim,
    history_reclaim,
    plan_reclaim,
    purge_reclaim,
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


def _write_generated_state_registry(root: Path) -> None:
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text(
        "\n".join(
            [
                "[[artifacts]]",
                'id = "generated-runtime-state-tree"',
                'domain = "runtime_state"',
                'lifecycle = "generated"',
                'storage_path = ".gtkb-state/"',
                'authority_spec_id = "TEST-SPEC"',
                'mutation_api = "test runtime generator"',
                'versioning_policy = "regenerated_from_source"',
                'backup_policy = "gitignored_runtime"',
                'restore_action = "regenerate_from_source"',
                'health_check_function = ""',
                'owner_role = "automated_only"',
                "",
                "[[artifacts]]",
                'id = "dispatch-state"',
                'domain = "runtime_state"',
                'lifecycle = "active"',
                'storage_path = ".gtkb-state/bridge-poller/dispatch-state.json"',
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


def _purge(root: Path, plan: dict[str, object], item_id: str) -> dict[str, object]:
    return purge_reclaim(
        root,
        run_id=str(plan["run_id"]),
        plan_hash=str(plan["plan_hash"]),
        item_ids=[item_id],
        owner_evidence=["DELIB-TEST-OWNER-PURGE"],
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


def test_git_roots_are_preserved_but_registry_decides_scratch(repo: Path) -> None:
    tracked_scratch = repo / "tracked" / ".harness-tmp" / "tracked.txt"
    tracked_scratch.parent.mkdir(parents=True)
    tracked_scratch.write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", tracked_scratch.relative_to(repo).as_posix())
    staged_oid = _git(repo, "hash-object", tracked_scratch.relative_to(repo).as_posix())
    old = (NOW - timedelta(hours=200)).timestamp()
    os.utime(tracked_scratch, (old, old))
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

    assert tracked_scratch.relative_to(repo).as_posix() in paths
    assert staged_object.relative_to(repo).as_posix() not in paths
    assert unreachable_path.relative_to(repo).as_posix() in paths


def test_registry_preserves_tracked_scratch_candidate(repo: Path) -> None:
    tracked_scratch = repo / "tracked" / ".harness-tmp" / "tracked.txt"
    tracked_scratch.parent.mkdir(parents=True)
    tracked_scratch.write_text("tracked but registered\n", encoding="utf-8")
    old = (NOW - timedelta(hours=200)).timestamp()
    os.utime(tracked_scratch, (old, old))
    rel_path = tracked_scratch.relative_to(repo).as_posix()
    _git(repo, "add", rel_path)
    _write_registry(repo, rel_path)
    _git(repo, "add", "config/registry/sot-artifacts.toml")
    _git(repo, "commit", "-m", "register tracked scratch fixture")

    plan = plan_reclaim(repo, now=NOW)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))
    paths = {item["path"] for item in manifest["items"]}

    assert rel_path not in paths
    assert any(
        item["path"] == rel_path and item["classification"] == "registered_veto" for item in manifest["preserved"]
    )


def test_malformed_git_tmp_object_is_deep_clean_detritus(repo: Path) -> None:
    garbage = repo / ".git" / "objects" / "ab" / "tmp_obj_TEST123"
    garbage.parent.mkdir(parents=True, exist_ok=True)
    garbage.write_text("interrupted git object write\n", encoding="utf-8")

    plan = plan_reclaim(repo, now=NOW)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))
    items = {item["path"]: item for item in manifest["items"]}

    rel_path = ".git/objects/ab/tmp_obj_TEST123"
    assert rel_path in items
    assert items[rel_path]["candidate_class"] == "malformed_git_object_garbage"

    result = deep_clean_reclaim(
        repo,
        now=NOW,
        owner_evidence=["TEST-OWNER-DEEP-CLEAN"],
        quiescence_evidence=["TEST-QUIESCENCE"],
    )

    assert result["status"] == "clean"
    assert not garbage.exists()


def test_root_pytest_directory_is_deep_clean_detritus(repo: Path) -> None:
    candidate = repo / ".pytest-A-lo-wi5249" / "nested" / "result.txt"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("transient test output\n", encoding="utf-8")

    plan = plan_reclaim(repo, now=NOW)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))
    items = {item["path"]: item for item in manifest["items"]}

    assert ".pytest-A-lo-wi5249" in items
    assert items[".pytest-A-lo-wi5249"]["candidate_class"] == "stale_workspace_detritus"
    assert items[".pytest-A-lo-wi5249"]["source_kind"] == "worktree_directory"

    result = deep_clean_reclaim(
        repo,
        now=NOW,
        owner_evidence=["TEST-OWNER-DEEP-CLEAN"],
        quiescence_evidence=["TEST-QUIESCENCE"],
    )

    assert result["status"] == "clean"
    assert not (repo / ".pytest-A-lo-wi5249").exists()


def test_generated_state_detritus_is_reclaimed_without_preserving_generated_root(repo: Path) -> None:
    _write_generated_state_registry(repo)
    detritus = repo / ".gtkb-state" / "pytest-basetemp" / "case" / "result.txt"
    detritus.parent.mkdir(parents=True)
    detritus.write_text("temporary state\n", encoding="utf-8")
    dispatch = repo / ".gtkb-state" / "bridge-poller" / "dispatch-state.json"
    dispatch.parent.mkdir(parents=True)
    dispatch.write_text("{}", encoding="utf-8")

    plan = plan_reclaim(repo, now=NOW)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))
    paths = {item["path"] for item in manifest["items"]}

    assert ".gtkb-state/pytest-basetemp" in paths
    assert ".gtkb-state/bridge-poller" not in paths

    result = deep_clean_reclaim(
        repo,
        now=NOW,
        owner_evidence=["TEST-OWNER-DEEP-CLEAN"],
        quiescence_evidence=["TEST-QUIESCENCE"],
    )

    assert result["status"] == "clean"
    assert not (repo / ".gtkb-state" / "pytest-basetemp").exists()
    assert dispatch.read_text(encoding="utf-8") == "{}"


def test_outside_worktree_index_roots_are_preserved_without_blocking(repo: Path) -> None:
    outside = repo.parent / "outside-worktree"
    _git(repo, "worktree", "add", "-b", "outside-preserve", str(outside), "HEAD")
    outside_file = outside / "outside-staged.txt"
    outside_file.write_text("outside staged\n", encoding="utf-8")
    _git(outside, "add", "outside-staged.txt")
    staged_oid = _git(outside, "hash-object", "outside-staged.txt")
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

    assert plan["executable"] is True
    assert str(outside.resolve()) in manifest["git"]["outside_worktrees"]
    assert staged_object.relative_to(repo).as_posix() not in paths
    assert unreachable_path.relative_to(repo).as_posix() in paths


def test_index_only_missing_roots_are_reported_without_blocking(repo: Path) -> None:
    staged = repo / "staged-only.txt"
    staged.write_text("staged only\n", encoding="utf-8")
    _git(repo, "add", "staged-only.txt")
    staged_oid = _git(repo, "hash-object", "staged-only.txt")
    staged_object = repo / ".git" / "objects" / staged_oid[:2] / staged_oid[2:]
    os.chmod(staged_object, 0o666)
    staged_object.unlink()
    _old_scratch(repo)

    plan, _item_id = _single_plan(repo)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))

    assert plan["executable"] is True
    assert plan["blockers"] == []
    assert manifest["git"]["missing_index_root_count"] == 1
    assert manifest["git"]["missing_index_roots"][0]["oid"] == staged_oid


def test_reflog_only_missing_roots_are_reported_without_blocking(repo: Path) -> None:
    missing_oid = "f" * 40
    head_oid = _git(repo, "rev-parse", "HEAD")
    with (repo / ".git" / "logs" / "HEAD").open("a", encoding="utf-8") as handle:
        handle.write(
            f"{head_oid} {missing_oid} Reclaim Test <reclaim@example.invalid> 1780000000 +0000\tfixture stale reflog\n"
        )
    _old_scratch(repo)

    plan, _item_id = _single_plan(repo)
    manifest = json.loads(Path(str(plan["manifest_path"])).read_text(encoding="utf-8"))

    assert plan["executable"] is True
    assert plan["blockers"] == []
    assert manifest["git"]["missing_reflog_root_count"] == 1
    assert manifest["git"]["missing_reflog_roots"][0]["oid"] == missing_oid


def test_git_temp_object_is_reclaimed_and_unknown_malformed_object_is_preserved(repo: Path) -> None:
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
    items = {item["path"]: item for item in manifest["items"]}

    assert "malformed_loose_object" in classes
    assert items[temporary.relative_to(repo).as_posix()]["candidate_class"] == "malformed_git_object_garbage"
    assert malformed.relative_to(repo).as_posix() not in items


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


def test_trash_and_restore_read_only_candidate(repo: Path) -> None:
    candidate = _old_scratch(repo, "read only\n")
    os.chmod(candidate, stat.S_IREAD)
    plan, item_id = _single_plan(repo)
    run_dir = Path(str(plan["manifest_path"])).parent
    payload = run_dir / "trash" / item_id / "payload"
    try:
        trashed = _trash(repo, plan, item_id)

        assert trashed["status"] == "trashed"
        assert not candidate.exists()
        assert payload.is_file()

        restored = restore_reclaim(repo, run_id=str(plan["run_id"]), item_ids=[item_id])

        assert restored["status"] == "restored"
        assert candidate.read_text(encoding="utf-8") == "read only\n"
    finally:
        for path in (candidate, payload):
            if path.exists():
                os.chmod(path, stat.S_IREAD | stat.S_IWRITE)


def test_trash_refuses_unexpected_existing_payload(repo: Path) -> None:
    candidate = _old_scratch(repo, "source\n")
    plan, item_id = _single_plan(repo)
    payload = Path(str(plan["manifest_path"])).parent / "trash" / item_id / "payload"
    payload.parent.mkdir(parents=True)
    payload.write_text("collision\n", encoding="utf-8")

    with pytest.raises(ReclaimError, match="unexpected_existing_payload"):
        _trash(repo, plan, item_id)

    assert candidate.read_text(encoding="utf-8") == "source\n"
    assert payload.read_text(encoding="utf-8") == "collision\n"


def test_trash_retries_matching_payload_after_atomic_move_failure(repo: Path) -> None:
    candidate = _old_scratch(repo, "recoverable\n")
    os.chmod(candidate, stat.S_IREAD)
    plan, item_id = _single_plan(repo)
    run_dir = Path(str(plan["manifest_path"])).parent
    payload = run_dir / "trash" / item_id / "payload"
    payload.parent.mkdir(parents=True)
    payload.write_bytes(candidate.read_bytes())
    os.chmod(payload, stat.S_IREAD)
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    _append_event(
        run_dir,
        events,
        action="trash_started",
        item_id=item_id,
        details={
            "path": candidate.relative_to(repo).as_posix(),
            "payload_path": payload.relative_to(run_dir).as_posix(),
        },
    )
    _append_event(
        run_dir,
        events,
        action="refused",
        item_id=item_id,
        details={"operation": "trash", "code": "atomic_move_failed", "detail": "fixture"},
    )

    try:
        trashed = _trash(repo, plan, item_id)

        assert trashed["status"] == "trashed"
        assert not candidate.exists()
        assert payload.read_text(encoding="utf-8") == "recoverable\n"
        assert history_reclaim(repo, run_id=str(plan["run_id"]))["status"] == "trashed"
    finally:
        for path in (candidate, payload):
            if path.exists():
                os.chmod(path, stat.S_IREAD | stat.S_IWRITE)


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


def test_purge_deletes_payload_and_reports_physical_bytes(repo: Path) -> None:
    candidate = _old_scratch(repo, "purge me\n")
    expected_size = candidate.stat().st_size
    plan, item_id = _single_plan(repo)
    trashed = _trash(repo, plan, item_id)
    payload = Path(str(plan["manifest_path"])).parent / str(trashed["trashed"][0]["payload_path"])

    purged = _purge(repo, plan, item_id)

    assert purged["status"] == "purged"
    assert purged["logical_bytes_purged"] == expected_size
    assert purged["physical_bytes_reclaimed"] == expected_size
    assert not payload.exists()
    history = history_reclaim(repo, run_id=str(plan["run_id"]))
    assert history["status"] == "purged"
    assert history["counts"] == {"purged": 1}


def test_purge_allows_recreated_source_and_deletes_only_payload(repo: Path) -> None:
    candidate = _old_scratch(repo, "old payload\n")
    plan, item_id = _single_plan(repo)
    trashed = _trash(repo, plan, item_id)
    payload = Path(str(plan["manifest_path"])).parent / str(trashed["trashed"][0]["payload_path"])
    candidate.write_text("new source\n", encoding="utf-8")

    purged = _purge(repo, plan, item_id)

    assert purged["status"] == "purged"
    assert not payload.exists()
    assert candidate.read_text(encoding="utf-8") == "new source\n"


def test_purge_refuses_changed_payload_and_preserves_it(repo: Path) -> None:
    _old_scratch(repo, "payload\n")
    plan, item_id = _single_plan(repo)
    trashed = _trash(repo, plan, item_id)
    payload = Path(str(plan["manifest_path"])).parent / str(trashed["trashed"][0]["payload_path"])
    payload.write_text("changed\n", encoding="utf-8")

    with pytest.raises(ReclaimError, match="purge_revalidation_failed"):
        _purge(repo, plan, item_id)

    assert payload.read_text(encoding="utf-8") == "changed\n"
    history = history_reclaim(repo, run_id=str(plan["run_id"]), item_id=item_id)
    assert history["items"][0]["status"] == "refused"
    assert history["items"][0]["payload_state"] == "trashed"


def test_purge_refuses_untrashed_item(repo: Path) -> None:
    candidate = _old_scratch(repo, "still active\n")
    plan, item_id = _single_plan(repo)

    with pytest.raises(ReclaimError, match="purge_revalidation_failed"):
        _purge(repo, plan, item_id)

    assert candidate.read_text(encoding="utf-8") == "still active\n"
    history = history_reclaim(repo, run_id=str(plan["run_id"]), item_id=item_id)
    assert history["items"][0]["status"] == "refused"
    assert history["items"][0]["payload_state"] == "planned"


def test_deep_clean_reclaim_runs_to_zero_without_per_item_owner_prompt(repo: Path) -> None:
    candidate = _old_scratch(repo, "deep clean\n")
    expected_size = candidate.stat().st_size

    cleaned = deep_clean_reclaim(
        repo,
        owner_evidence=["OPS-ENVELOPE-TEST-DEEP-CLEAN"],
        quiescence_evidence=["TEST-QUIESCENCE-OK"],
        max_cycles=3,
        batch_size=1,
    )

    assert cleaned["status"] == "clean"
    assert cleaned["total_trashed"] == 1
    assert cleaned["total_purged"] == 1
    assert cleaned["logical_bytes_removed"] == expected_size
    assert cleaned["physical_bytes_reclaimed"] == expected_size
    assert cleaned["final_candidate_count"] == 0
    assert not candidate.exists()
    assert history_reclaim(repo, run_id=str(cleaned["cycles"][0]["run_id"]))["status"] == "purged"
    assert history_reclaim(repo, run_id=str(cleaned["final_run_id"]))["item_count"] == 0


def test_deep_clean_requires_evidence(repo: Path) -> None:
    _old_scratch(repo)

    with pytest.raises(ReclaimError, match="owner_evidence"):
        deep_clean_reclaim(
            repo,
            owner_evidence=[],
            quiescence_evidence=["TEST-QUIESCENCE-OK"],
        )


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
