"""WI-5027 tests for the read-only worktree finalization triage planner."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import worktree_finalization_triage as triage  # noqa: E402
from groundtruth_kb.hygiene import auto_resolve  # noqa: E402


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "triage-tests@example.invalid")
    _git(repo, "config", "user.name", "Triage Tests")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "existing_tool.py").write_text("print('base')\n", encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")


def _status(repo: Path) -> str:
    result = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    assert result.returncode == 0, result.stderr
    return result.stdout


def _make_dirty_repo(repo: Path) -> None:
    (repo / "scripts" / "existing_tool.py").write_text("print('changed')\n", encoding="utf-8")
    (repo / "bridge").mkdir()
    (repo / "bridge" / "thread-a-001.md").write_text(
        "NEW\nDocument: thread-a\nVersion: 001\n",
        encoding="utf-8",
    )
    (repo / "bridge" / "thread-a-002.md").write_text(
        "VERIFIED\nDocument: thread-a\nVersion: 002\n",
        encoding="utf-8",
    )
    (repo / ".cursor" / "gtkb-hooks").mkdir(parents=True)
    (repo / ".cursor" / "gtkb-hooks" / "last-session-start.json").write_text("{}\n", encoding="utf-8")
    (repo / ".temp_verdict_body").write_text("scratch\n", encoding="utf-8")
    (repo / "notes.txt").write_text("manual\n", encoding="utf-8")


def _write_sot_registry(repo: Path, *, storage_path: str = ".gtkb-state/") -> None:
    registry = repo / "config" / "registry" / "sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        f"""
[[artifacts]]
id = "owner-runtime-state"
domain = "runtime_state"
lifecycle = "active"
storage_path = "{storage_path}"
authority_spec_id = "SPEC-INTAKE-99a602"
mutation_api = "owner-managed local runtime state; GT-KB records path authority only"
versioning_policy = "overwrite_single_writer"
backup_policy = "gitignored_runtime"
health_check_function = ""
owner_role = "owner_only"
notes = "Registered runtime state is preserved by cleanup planning."
""".lstrip(),
        encoding="utf-8",
    )


def _items_by_path(plan: dict) -> dict[str, dict]:
    return {item["path"]: item for item in plan["items"]}


def test_plan_groups_dirty_paths_and_blocks_forbidden_actions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _make_dirty_repo(repo)

    plan = triage.build_plan(repo)
    by_path = _items_by_path(plan)

    assert plan["read_only"] is True
    assert plan["candidate_actions_only"] is True
    assert by_path["bridge/thread-a-002.md"]["bucket"] == "bridge_thread_chain"
    assert by_path["bridge/thread-a-002.md"]["bridge_status"] == "VERIFIED"
    assert by_path["bridge/thread-a-002.md"]["candidate_action"] == "blocked_commit_requires_specific_apply_evidence"
    assert by_path["bridge/thread-a-002.md"]["actuator_action"] == "safe_commit"
    assert by_path["bridge/thread-a-002.md"]["apply_status"] == "blocked_missing_specific_apply_evidence"
    assert by_path["scripts/existing_tool.py"]["bucket"] == "protected_source_test_config"
    assert by_path["scripts/existing_tool.py"]["actuator_action"] == "manual_owner_review"
    assert by_path[".cursor/gtkb-hooks/last-session-start.json"]["bucket"] == "harness_runtime_projection"
    assert by_path[".cursor/gtkb-hooks/last-session-start.json"]["actuator_action"] == "auto_ignore"
    assert by_path[".temp_verdict_body"]["bucket"] == "scratch_junk"
    assert (
        by_path[".temp_verdict_body"]["candidate_action"] == "blocked_untracked_file_deletion_requires_apply_evidence"
    )
    assert by_path[".temp_verdict_body"]["actuator_action"] == "auto_drop_byte_identical"
    assert by_path["notes.txt"]["bucket"] == "manual_owner_review"
    assert "destructive_bulk_cleanup" in plan["forbidden_operations"]
    assert "committing_another_session_stale_work_without_specific_apply_evidence" in plan["forbidden_operations"]
    assert plan["action_taxonomy"] == list(auto_resolve.ACTUATOR_ACTIONS)
    assert plan["counts"]["actuator_actions"]["safe_commit"] == 1


def test_tracked_modified_terminal_verdict_requires_manual_review(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    verdict = repo / "bridge" / "thread-b-001.md"
    verdict.parent.mkdir()
    verdict.write_text("VERIFIED\nDocument: thread-b\nVersion: 001\n", encoding="utf-8")
    _git(repo, "add", "bridge/thread-b-001.md")
    _git(repo, "commit", "-q", "-m", "verified verdict")
    verdict.write_text("VERIFIED\nDocument: thread-b\nVersion: 001\nchanged: true\n", encoding="utf-8")

    item = _items_by_path(triage.build_plan(repo))["bridge/thread-b-001.md"]

    assert item["tracked"] is True
    assert item["change_kind"] == "modified"
    assert item["bridge_status"] == "VERIFIED"
    assert item["candidate_action"] == "manual_review_modified_terminal_verdict"
    assert item["actuator_action"] == "manual_owner_review"
    assert item["apply_status"] == "manual_review_required_modified_terminal_verdict"


def test_tracked_deleted_terminal_verdict_requires_manual_review(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    verdict = repo / "bridge" / "thread-c-001.md"
    verdict.parent.mkdir()
    verdict.write_text("VERIFIED\nDocument: thread-c\nVersion: 001\n", encoding="utf-8")
    _git(repo, "add", "bridge/thread-c-001.md")
    _git(repo, "commit", "-q", "-m", "verified verdict")
    verdict.unlink()

    item = _items_by_path(triage.build_plan(repo))["bridge/thread-c-001.md"]

    assert item["tracked"] is True
    assert item["change_kind"] == "deleted"
    assert item["bridge_status"] == "VERIFIED"
    assert item["candidate_action"] == "manual_review_modified_terminal_verdict"
    assert item["actuator_action"] == "manual_owner_review"
    assert item["apply_status"] == "manual_review_required_modified_terminal_verdict"


def test_cursor_runtime_projection_detection_keeps_durable_hooks_visible(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    cursor_hooks = repo / ".cursor" / "gtkb-hooks"
    cursor_hooks.mkdir(parents=True)
    (cursor_hooks / "last-session-start.json").write_text("{}\n", encoding="utf-8")
    (cursor_hooks / "last-user-visible-startup-pb.md").write_text("cache\n", encoding="utf-8")
    (cursor_hooks / "last-user-visible-startup-pb.meta.json").write_text("{}\n", encoding="utf-8")
    (cursor_hooks / "session_start_dispatch.py").write_text("# durable dispatcher\n", encoding="utf-8")
    (cursor_hooks / "cursor-hook-env.cmd").write_text("@echo off\n", encoding="utf-8")

    plan = triage.build_plan(repo)
    by_path = _items_by_path(plan)

    assert by_path[".cursor/gtkb-hooks/last-session-start.json"]["bucket"] == "harness_runtime_projection"
    assert by_path[".cursor/gtkb-hooks/last-user-visible-startup-pb.md"]["actuator_action"] == "auto_ignore"
    assert by_path[".cursor/gtkb-hooks/last-user-visible-startup-pb.meta.json"]["actuator_action"] == "auto_ignore"
    assert by_path[".cursor/gtkb-hooks/session_start_dispatch.py"]["bucket"] == "manual_owner_review"
    assert by_path[".cursor/gtkb-hooks/cursor-hook-env.cmd"]["bucket"] == "manual_owner_review"
    assert plan["counts"]["actuator_actions"]["auto_ignore"] == 3
    assert plan["counts"]["actuator_actions"]["manual_owner_review"] == 2


def test_cursor_runtime_projection_gitignore_patterns_are_exact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    (repo / ".gitignore").write_text(
        "\n".join(
            (
                ".cursor/gtkb-hooks/last-session-start*",
                ".cursor/gtkb-hooks/last-user-visible-startup*",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-q", "-m", "ignore cursor runtime caches")

    cursor_hooks = repo / ".cursor" / "gtkb-hooks"
    cursor_hooks.mkdir(parents=True)
    for name in (
        "last-session-start.json",
        "last-session-start.err",
        "last-user-visible-startup-pb.md",
        "last-user-visible-startup-pb.meta.json",
        "session_start_dispatch.py",
        "cursor-hook-env.cmd",
    ):
        (cursor_hooks / name).write_text("content\n", encoding="utf-8")

    ignored = _git(
        repo,
        "check-ignore",
        ".cursor/gtkb-hooks/last-session-start.json",
        ".cursor/gtkb-hooks/last-session-start.err",
        ".cursor/gtkb-hooks/last-user-visible-startup-pb.md",
        ".cursor/gtkb-hooks/last-user-visible-startup-pb.meta.json",
    )
    visible = _git(
        repo,
        "check-ignore",
        ".cursor/gtkb-hooks/session_start_dispatch.py",
        ".cursor/gtkb-hooks/cursor-hook-env.cmd",
    )
    plan = triage.build_plan(repo)
    by_path = _items_by_path(plan)

    assert ignored.returncode == 0
    assert visible.returncode == 1
    assert ".cursor/gtkb-hooks/last-session-start.json" not in by_path
    assert ".cursor/gtkb-hooks/last-user-visible-startup-pb.md" not in by_path
    assert by_path[".cursor/gtkb-hooks/session_start_dispatch.py"]["bucket"] == "manual_owner_review"
    assert by_path[".cursor/gtkb-hooks/cursor-hook-env.cmd"]["bucket"] == "manual_owner_review"


def test_plan_is_json_serializable_and_stably_sorted(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _make_dirty_repo(repo)

    plan = triage.build_plan(repo)
    restored = json.loads(json.dumps(plan, sort_keys=True))

    paths = [item["path"] for item in restored["items"]]
    assert paths == sorted(paths)
    bucket_names = [summary["bucket"] for summary in restored["bucket_summaries"]]
    assert bucket_names == sorted(bucket_names)


def test_plan_does_not_mutate_git_status(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _make_dirty_repo(repo)
    before = _status(repo)

    triage.build_plan(repo)

    assert _status(repo) == before


def test_plan_preserves_registered_artifact_before_scratch_or_runtime_buckets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _write_sot_registry(repo)
    _git(repo, "add", "config/registry/sot-artifacts.toml")
    _git(repo, "commit", "-q", "-m", "registry")

    registered_runtime_scratch = ".gtkb-state/.temp_verdict_body"
    assert auto_resolve._is_scratch_junk(registered_runtime_scratch)
    assert auto_resolve._is_harness_runtime_projection(registered_runtime_scratch)

    target = repo / registered_runtime_scratch
    target.parent.mkdir(parents=True)
    target.write_text("registered local state\n", encoding="utf-8")

    plan = triage.build_plan(repo)
    item = _items_by_path(plan)[registered_runtime_scratch]

    assert item["bucket"] == "registered_artifact"
    assert item["candidate_action"] == "preserve_registered_artifact"
    assert item["actuator_action"] == "skip"
    assert item["apply_status"] == "preserved_registered_sot_artifact"
    assert item["registered_artifact_ids"] == ["owner-runtime-state"]
    assert "destructive_bulk_cleanup" in item["forbidden_operations_enforced"]
    assert "untracked_file_deletion" in item["forbidden_operations_enforced"]
    assert plan["counts"]["actuator_actions"]["auto_ignore"] == 0
    assert plan["counts"]["actuator_actions"]["auto_drop_byte_identical"] == 0
    assert plan["counts"]["actuator_actions"]["skip"] == 1


def test_cli_emits_json_and_markdown_without_mutation(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _make_dirty_repo(repo)
    before = _status(repo)

    assert triage.main(["--root", str(repo), "--format", "json"]) == 0
    json_output = capsys.readouterr().out
    assert json.loads(json_output)["counts"]["dirty_paths"] == 6

    assert triage.main(["--root", str(repo), "--format", "markdown"]) == 0
    markdown_output = capsys.readouterr().out
    assert "# Worktree Finalization Triage" in markdown_output
    assert "blocked_commit_requires_specific_apply_evidence" in markdown_output
    assert _status(repo) == before


def test_script_exports_canonical_auto_resolve_engine() -> None:
    assert triage.build_plan is auto_resolve.build_plan
    assert triage.classify_entry is auto_resolve.classify_entry
    assert triage.FORBIDDEN_OPERATIONS is auto_resolve.FORBIDDEN_OPERATIONS
    assert triage.ACTUATOR_ACTIONS is auto_resolve.ACTUATOR_ACTIONS
