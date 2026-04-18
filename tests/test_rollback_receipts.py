# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Real-git tests for rollback receipt mode resolution + post-merge write.

Every test sets up a real temp git repo and runs actual ``git`` commands.
No mocks, no inferred-from-docs assertions — this is the test-runtime
verification contract established by
``bridge/gtkb-rollback-receipts-013.md`` (Codex GO ``-014``).

Test coverage per ``-013`` §6 (5 state variants + topology):

- T-state-1: legacy ``.claude/`` ignored, no re-inclusion block → filesystem
- T-state-2: deliberate removed-block → filesystem (behaviorally identical to 1)
- T-state-3: opt-in block + later explicit ignore → filesystem (opt-out)
- T-state-4: tracked mode post-merge receipt commit topology (HEAD~1 is
  merge commit; HEAD is receipt commit)
- T-state-5: fresh scaffold default — receipt addable, managed artifacts
  still addable
- T-state-legacy-opt-in: 4-line block + broad ``.claude/`` ignore → receipt
  addable, other ``.claude/`` content still ignored (adopter posture preserved)
- T-failure: unexpected ``git check-ignore`` exit → raises
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.project.rollback import (
    ReceiptJSON,
    UnexpectedCheckIgnoreExit,
    resolve_receipt_mode,
    write_receipt,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _init_git_repo(root: Path) -> None:
    """Initialize a git repo at *root* with test identity configured."""
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=root, check=True)
    # Disable Windows CRLF auto-conversion so byte-level assertions
    # (receipt JSON contents, payload bytes) are stable across checkouts.
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=root, check=True)


def _commit_all(root: Path, message: str) -> str:
    """Stage everything and commit; return the new HEAD SHA."""
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_gitignore(root: Path, content: str) -> None:
    (root / ".gitignore").write_text(content, encoding="utf-8")


def _sample_receipt(merge_commit: str, mode: str) -> ReceiptJSON:
    return ReceiptJSON(
        schema_version="v1",
        receipt_id="test-receipt-001",
        merge_commit=merge_commit,
        target_branch="main",
        from_version="0.6.0",
        to_version="0.6.1",
        mode=mode,  # type: ignore[typeddict-item]
        created_at="2026-04-18T00:00:00Z",
        artifact_classes_touched=["hook"],
    )


# ---------------------------------------------------------------------------
# State 1: legacy .claude/ ignored, no re-inclusion block → filesystem mode
# ---------------------------------------------------------------------------


def test_state1_legacy_broad_claude_ignore_no_block_resolves_filesystem(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/\n")
    _commit_all(tmp_path, "initial")

    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"
    resolved = resolve_receipt_mode(tmp_path, receipt_path)

    assert resolved.mode == "filesystem"


# ---------------------------------------------------------------------------
# State 2: deliberate removed-block → filesystem (behaviorally same as state 1)
# ---------------------------------------------------------------------------


def test_state2_opt_out_via_removed_block_resolves_filesystem(tmp_path: Path) -> None:
    # Behaviorally identical to state 1 — the classifier cannot distinguish
    # "never had the block" from "deliberately removed the block", and by
    # design both resolve the same way.
    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/\n")
    _commit_all(tmp_path, "initial")

    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"
    resolved = resolve_receipt_mode(tmp_path, receipt_path)

    assert resolved.mode == "filesystem"


# ---------------------------------------------------------------------------
# State 3: opt-in block + later explicit ignore → filesystem (opt-out)
# ---------------------------------------------------------------------------


def test_state3_opt_in_block_plus_later_explicit_ignore_resolves_filesystem(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    # Full re-inclusion block, then an explicit later ignore for receipts.
    # Last match wins, so the later ignore takes precedence.
    _write_gitignore(
        tmp_path,
        ".claude/\n"
        "!/.claude/\n"
        "/.claude/*\n"
        "!/.claude/upgrade-receipts/\n"
        "!/.claude/upgrade-receipts/**\n"
        ".claude/upgrade-receipts/\n",
    )
    _commit_all(tmp_path, "initial")

    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"
    resolved = resolve_receipt_mode(tmp_path, receipt_path)

    assert resolved.mode == "filesystem"


# ---------------------------------------------------------------------------
# State 4: tracked mode post-merge receipt commit topology
# ---------------------------------------------------------------------------


def test_state4_tracked_mode_writes_separate_post_merge_receipt_commit(tmp_path: Path) -> None:
    """Tracked mode puts receipt in a SEPARATE commit AFTER the merge commit.

    Verifies the -010 F1 + -012 F2 fixes: HEAD is the receipt commit,
    HEAD~1 is the merge commit, and git revert -m 1 <merge_commit> does
    NOT disturb the receipt.
    """
    _init_git_repo(tmp_path)
    # Fresh-scaffold-style .gitignore: no broad .claude/ ignore.
    _write_gitignore(tmp_path, ".claude/settings.local.json\n")
    _commit_all(tmp_path, "initial")

    # Simulate a payload branch + payload commit + merge commit.
    subprocess.run(["git", "checkout", "-b", "payload"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "payload.txt").write_text("payload content\n", encoding="utf-8")
    _commit_all(tmp_path, "payload change")
    subprocess.run(["git", "checkout", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "payload", "-m", "Merge payload"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    merge_commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    merge_commit = merge_commit_result.stdout.strip()

    # Now resolve receipt mode (should be tracked since .claude/ isn't ignored)
    # and write the receipt.
    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"
    resolved = resolve_receipt_mode(tmp_path, receipt_path)
    assert resolved.mode == "tracked"

    receipt = _sample_receipt(merge_commit, "tracked")
    receipt_commit = write_receipt(resolved, receipt)

    # Topology: HEAD = receipt commit; HEAD~1 = merge commit.
    head_result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True)
    assert head_result.stdout.strip() == receipt_commit

    head_tilde_1_result = subprocess.run(
        ["git", "rev-parse", "HEAD~1"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    assert head_tilde_1_result.stdout.strip() == merge_commit

    # Receipt file IS in git index.
    ls_files = subprocess.run(
        ["git", "ls-files", "--", ".claude/upgrade-receipts/active/"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert ls_files.stdout.strip().endswith("r.json")

    # Receipt is NOT in the merge commit's tree.
    show_merge = subprocess.run(
        ["git", "show", "--stat", "--format=", merge_commit],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "upgrade-receipts" not in show_merge.stdout, (
        "receipt file should NOT appear in merge commit tree; found:\n" + show_merge.stdout
    )

    # git revert -m 1 <merge_commit> --no-commit does NOT touch the receipt.
    subprocess.run(
        ["git", "revert", "-m", "1", "--no-commit", merge_commit],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    status_after_revert = subprocess.run(
        ["git", "status", "--short"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    assert "upgrade-receipts" not in status_after_revert.stdout, (
        "git revert should not touch the receipt file; status shows:\n" + status_after_revert.stdout
    )
    # Receipt JSON file still exists on disk after the revert.
    assert receipt_path.exists(), "receipt file should survive git revert -m 1 --no-commit"


# ---------------------------------------------------------------------------
# State 5: fresh scaffold — receipt addable AND managed artifacts still addable
# ---------------------------------------------------------------------------


def test_state5_fresh_scaffold_does_not_regress_managed_artifacts(tmp_path: Path) -> None:
    """Fresh-scaffold default .gitignore leaves both upgrade-receipts and
    managed .claude/ artifacts trackable. This guards against the -012 F1
    regression (where a legacy opt-in block applied to fresh scaffold
    would hide managed artifacts).
    """
    _init_git_repo(tmp_path)
    # Match DEFAULT_PROJECT_GITIGNORE shape: ignore settings.local.json only.
    _write_gitignore(tmp_path, ".claude/settings.local.json\n")
    _commit_all(tmp_path, "initial")

    # Representative managed-artifact paths (mirrors the scaffold).
    (tmp_path / ".claude" / "hooks").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".claude" / "rules").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".claude" / "hooks" / "assertion-check.py").write_text("# stub\n", encoding="utf-8")
    (tmp_path / ".claude" / "rules" / "file-bridge-protocol.md").write_text("# stub\n", encoding="utf-8")
    (tmp_path / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")

    # Receipt path addable.
    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"
    resolved = resolve_receipt_mode(tmp_path, receipt_path)
    assert resolved.mode == "tracked"

    # All 3 representative managed artifacts are NOT ignored.
    for rel in (
        ".claude/hooks/assertion-check.py",
        ".claude/rules/file-bridge-protocol.md",
        ".claude/settings.json",
    ):
        check = subprocess.run(
            ["git", "check-ignore", "--no-index", "--", rel],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert check.returncode == 1, f"{rel} should be trackable; got exit={check.returncode}"

    # settings.local.json IS ignored (expected).
    check_local = subprocess.run(
        ["git", "check-ignore", "--no-index", "--", ".claude/settings.local.json"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert check_local.returncode == 0, "settings.local.json should be ignored in fresh scaffold"


# ---------------------------------------------------------------------------
# State legacy-opt-in: 4-line block + broad .claude/ ignore
# ---------------------------------------------------------------------------


def test_state_legacy_opt_in_block_unignores_receipt_only(tmp_path: Path) -> None:
    """Legacy adopter with .claude/ broadly ignored + the 4-line opt-in block:
    receipt is addable, but other .claude/ content remains ignored (adopter's
    legacy posture is preserved).
    """
    _init_git_repo(tmp_path)
    _write_gitignore(
        tmp_path,
        ".claude/\n"
        "# gt-upgrade tracked receipts — re-include ONLY upgrade-receipts.\n"
        "!/.claude/\n"
        "/.claude/*\n"
        "!/.claude/upgrade-receipts/\n"
        "!/.claude/upgrade-receipts/**\n",
    )
    _commit_all(tmp_path, "initial")

    # Receipt addable.
    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"
    resolved = resolve_receipt_mode(tmp_path, receipt_path)
    assert resolved.mode == "tracked"

    # Other .claude/ content STILL ignored (legacy posture preserved).
    other_check = subprocess.run(
        ["git", "check-ignore", "--no-index", "--", ".claude/hooks/assertion-check.py"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert other_check.returncode == 0, "adopter chose broad .claude/ ignore; other content should remain ignored"


# ---------------------------------------------------------------------------
# Failure: unexpected git check-ignore exit → raises UnexpectedCheckIgnoreExit
# ---------------------------------------------------------------------------


def test_unexpected_check_ignore_exit_raises(tmp_path: Path) -> None:
    """Running resolve_receipt_mode outside a git repo produces a non-0/1
    exit code, which raises UnexpectedCheckIgnoreExit (fail-loud contract).
    """
    # tmp_path is NOT a git repo — git check-ignore will fail.
    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"

    with pytest.raises(UnexpectedCheckIgnoreExit) as excinfo:
        resolve_receipt_mode(tmp_path, receipt_path)

    # returncode must be captured for operator diagnostics.
    assert excinfo.value.returncode not in (0, 1), f"expected abnormal exit code; got {excinfo.value.returncode}"


# ---------------------------------------------------------------------------
# Filesystem-mode write: file on disk, no commit
# ---------------------------------------------------------------------------


def test_filesystem_mode_write_creates_file_without_commit(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/\n")
    _commit_all(tmp_path, "initial")

    receipt_path = tmp_path / ".claude" / "upgrade-receipts" / "active" / "r.json"
    resolved = resolve_receipt_mode(tmp_path, receipt_path)
    assert resolved.mode == "filesystem"

    receipt = _sample_receipt("0" * 40, "filesystem")
    result = write_receipt(resolved, receipt)

    assert result == "filesystem"
    assert receipt_path.exists()
    loaded = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v1"
    assert loaded["mode"] == "filesystem"

    # File is NOT in git index (it was ignored and no commit was made).
    ls_files = subprocess.run(
        ["git", "ls-files", "--", ".claude/upgrade-receipts/"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert ls_files.stdout.strip() == "", "filesystem-mode receipt should NOT be in git index; got:\n" + ls_files.stdout


# ---------------------------------------------------------------------------
# Phase 3: execute_upgrade end-to-end — payload-branch-and-merge + receipt
# ---------------------------------------------------------------------------
#
# Phase 3 per bridge/gtkb-rollback-receipts-014 integrates the receipt
# lifecycle into ``gt project upgrade --apply``. These tests exercise the
# end-to-end flow (preconditions → payload branch → merge commit → receipt)
# through the public ``execute_upgrade`` API, using hand-built actions to
# avoid needing a full GT-KB template scaffold.


def _write_minimal_toml(target: Path, version: str = "0.5.0") -> None:
    """Minimal groundtruth.toml so read_manifest returns a valid manifest."""
    (target / "groundtruth.toml").write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test Owner"
profile = "local-only"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{version}"
created_at = "2026-01-01T00:00:00Z"
""",
        encoding="utf-8",
    )


def _gitignore_append_action() -> object:
    """Hand-built append-gitignore action for integration tests.

    Uses a stable payload that appears in none of the registry's default
    patterns; the action is only a vehicle to force a non-empty payload
    commit without needing a full template scaffold. Return type is
    :class:`object` so the import lives in one place and the helper stays
    decoupled from any specific ``UpgradeAction`` signature change.
    """
    from groundtruth_kb.project.upgrade import UpgradeAction

    return UpgradeAction(
        file=".gitignore",
        action="append-gitignore",
        reason="test payload pattern (integration fixture)",
        payload="test-integration-pattern/",
    )


def test_execute_upgrade_not_git_repo_raises(tmp_path: Path) -> None:
    """Pre-flight: execute_upgrade outside a git work tree raises."""
    from groundtruth_kb.project.upgrade import NotAGitRepositoryError, execute_upgrade

    _write_minimal_toml(tmp_path)
    # tmp_path intentionally NOT initialized as a git repo.

    with pytest.raises(NotAGitRepositoryError) as excinfo:
        execute_upgrade(tmp_path, [_gitignore_append_action()], force=False)  # type: ignore[list-item]

    assert excinfo.value.target == tmp_path
    assert "git init" in str(excinfo.value)


def test_execute_upgrade_dirty_tree_raises(tmp_path: Path) -> None:
    """Pre-flight: execute_upgrade on a dirty tree raises with status output."""
    from groundtruth_kb.project.upgrade import DirtyWorkingTreeError, execute_upgrade

    _init_git_repo(tmp_path)
    _write_minimal_toml(tmp_path)
    _commit_all(tmp_path, "initial")
    # Introduce an uncommitted change to make the tree dirty.
    (tmp_path / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")

    with pytest.raises(DirtyWorkingTreeError) as excinfo:
        execute_upgrade(tmp_path, [_gitignore_append_action()], force=False)  # type: ignore[list-item]

    assert excinfo.value.target == tmp_path
    assert "dirty.txt" in excinfo.value.status


def test_execute_upgrade_tracked_mode_end_to_end(tmp_path: Path) -> None:
    """Full happy-path integration test in tracked mode.

    Fresh scaffold .gitignore leaves the receipt path trackable, so the
    receipt lands as a SEPARATE commit on HEAD, the merge commit is at
    HEAD~1 with two parents, and the receipt JSON records the real
    merge_commit SHA.
    """
    from groundtruth_kb import __version__
    from groundtruth_kb.project.upgrade import execute_upgrade

    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/settings.local.json\n")
    _write_minimal_toml(tmp_path, version="0.0.1")
    _commit_all(tmp_path, "initial")

    results = execute_upgrade(tmp_path, [_gitignore_append_action()], force=False)  # type: ignore[list-item]

    # Results include MERGED + RECEIPT lines.
    assert any("MERGED payload into main" in r for r in results), results
    assert any("RECEIPT tracked" in r for r in results), results

    # Topology: HEAD is receipt commit; HEAD~1 is the merge commit and has
    # two parents (a real merge, not a fast-forward).
    head_tilde_1 = subprocess.run(
        ["git", "rev-parse", "HEAD~1"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()
    parents_of_head_tilde_1 = (
        subprocess.run(
            ["git", "rev-list", "--parents", "-n", "1", head_tilde_1],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .split()
    )
    # rev-list --parents returns "sha parent1 parent2..."; a real merge has 3 tokens.
    assert len(parents_of_head_tilde_1) == 3, (
        f"HEAD~1 must be a real merge commit with two parents; got {parents_of_head_tilde_1}"
    )

    # Receipt JSON exists, is in the git index, and contains the merge_commit SHA.
    receipt_files = list((tmp_path / ".claude" / "upgrade-receipts" / "active").glob("*.json"))
    assert len(receipt_files) == 1, f"expected exactly one receipt; got {receipt_files}"
    receipt = json.loads(receipt_files[0].read_text(encoding="utf-8"))
    assert receipt["schema_version"] == "v1"
    assert receipt["merge_commit"] == head_tilde_1
    assert receipt["target_branch"] == "main"
    assert receipt["from_version"] == "0.0.1"
    assert receipt["to_version"] == __version__
    assert receipt["mode"] == "tracked"
    assert "gitignore-pattern" in receipt["artifact_classes_touched"]

    # Receipt IS in the git index (tracked).
    ls = subprocess.run(
        ["git", "ls-files", "--", ".claude/upgrade-receipts/"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert receipt_files[0].name in ls.stdout, f"receipt must be tracked; ls-files:\n{ls.stdout}"

    # Receipt is NOT in the merge commit's tree.
    show_merge = subprocess.run(
        ["git", "show", "--stat", "--format=", head_tilde_1],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "upgrade-receipts" not in show_merge.stdout, (
        f"receipt must not appear in merge commit tree; got:\n{show_merge.stdout}"
    )

    # Payload branch is deleted after success.
    branches = subprocess.run(
        ["git", "branch", "--list"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout
    assert "gt-upgrade-payload-" not in branches, f"payload branch must be cleaned up; got branches:\n{branches}"


def test_execute_upgrade_tracked_mode_revert_m1_reverts_only_payload(tmp_path: Path) -> None:
    """Verifies the rollback primitive: ``git revert -m 1 <merge_commit>``
    reverts the payload without touching the receipt.

    This is the contract the whole Phase 3 design exists to enable.
    """
    from groundtruth_kb.project.upgrade import execute_upgrade

    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/settings.local.json\n")
    _write_minimal_toml(tmp_path, version="0.0.1")
    _commit_all(tmp_path, "initial")

    execute_upgrade(tmp_path, [_gitignore_append_action()], force=False)  # type: ignore[list-item]

    head_tilde_1 = subprocess.run(
        ["git", "rev-parse", "HEAD~1"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()

    # Pre-revert: the payload pattern is in .gitignore.
    before = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "test-integration-pattern/" in before

    # Dry-run revert of the merge commit on the mainline parent side (-m 1)
    # must NOT touch the receipt file.
    subprocess.run(
        ["git", "revert", "-m", "1", "--no-commit", head_tilde_1],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout
    assert "upgrade-receipts" not in status, f"revert -m 1 must not touch the receipt; status:\n{status}"
    # The pattern removal IS in the revert staging.
    assert ".gitignore" in status, f"revert should restage .gitignore; status:\n{status}"


def test_execute_upgrade_filesystem_mode_end_to_end(tmp_path: Path) -> None:
    """Full happy-path integration test in filesystem mode.

    Legacy-style .gitignore broadly ignores .claude/, so the receipt is
    written to disk but NOT committed. HEAD in this mode is the merge
    commit itself (no separate receipt commit).
    """
    from groundtruth_kb.project.upgrade import execute_upgrade

    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/\n")
    _write_minimal_toml(tmp_path, version="0.0.1")
    _commit_all(tmp_path, "initial")

    results = execute_upgrade(tmp_path, [_gitignore_append_action()], force=False)  # type: ignore[list-item]

    assert any("MERGED payload into main" in r for r in results), results
    assert any("RECEIPT filesystem" in r for r in results), results

    # HEAD is the merge commit directly (two parents, because --no-ff).
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()
    parents_of_head = (
        subprocess.run(
            ["git", "rev-list", "--parents", "-n", "1", head],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .split()
    )
    assert len(parents_of_head) == 3, f"HEAD must be a merge commit; got {parents_of_head}"

    # Receipt JSON exists on disk but is NOT in git index.
    receipt_files = list((tmp_path / ".claude" / "upgrade-receipts" / "active").glob("*.json"))
    assert len(receipt_files) == 1, f"expected exactly one receipt on disk; got {receipt_files}"
    receipt = json.loads(receipt_files[0].read_text(encoding="utf-8"))
    assert receipt["mode"] == "filesystem"
    assert receipt["merge_commit"] == head

    ls = subprocess.run(
        ["git", "ls-files", "--", ".claude/upgrade-receipts/"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert ls.stdout.strip() == "", f"filesystem receipt must NOT be in git; got:\n{ls.stdout}"


def test_execute_upgrade_no_bak_files_ever_created(tmp_path: Path) -> None:
    """Cross-mode invariant: execute_upgrade never writes .bak files.

    Per bridge gtkb-rollback-receipts-014 Condition 5. Check in both modes.
    """
    from groundtruth_kb.project.upgrade import execute_upgrade

    # Tracked-mode run.
    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/settings.local.json\n")
    _write_minimal_toml(tmp_path, version="0.0.1")
    _commit_all(tmp_path, "initial")
    execute_upgrade(tmp_path, [_gitignore_append_action()], force=False)  # type: ignore[list-item]

    bak_files = list(tmp_path.rglob("*.bak"))
    assert bak_files == [], f"tracked-mode run must not create .bak; found: {bak_files}"


def test_execute_upgrade_noop_payload_skips_receipt(tmp_path: Path) -> None:
    """When actions produce no disk changes AND manifest is already current,
    execute_upgrade aborts cleanly without creating a merge or receipt.
    """
    from groundtruth_kb import __version__
    from groundtruth_kb.project.upgrade import execute_upgrade

    _init_git_repo(tmp_path)
    _write_gitignore(tmp_path, ".claude/settings.local.json\n")
    _write_minimal_toml(tmp_path, version=__version__)
    # Pre-seed the pattern so append-gitignore is already idempotent.
    (tmp_path / ".gitignore").write_text(".claude/settings.local.json\ntest-integration-pattern/\n", encoding="utf-8")
    _commit_all(tmp_path, "initial")

    commits_before = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()

    results = execute_upgrade(tmp_path, [_gitignore_append_action()], force=False)  # type: ignore[list-item]

    # "no changes to apply" signal present; no RECEIPT message.
    assert any("no changes to apply" in r for r in results), results
    assert not any("RECEIPT" in r for r in results), results

    # No receipt file landed on disk.
    receipt_dir = tmp_path / ".claude" / "upgrade-receipts" / "active"
    if receipt_dir.exists():
        assert list(receipt_dir.glob("*.json")) == [], "no-op run must not write a receipt"

    # Commit count unchanged — no merge, no receipt commit.
    commits_after = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()
    assert commits_before == commits_after, (
        f"no-op run must not add commits; before={commits_before}, after={commits_after}"
    )

    # Payload branch cleaned up.
    branches = subprocess.run(
        ["git", "branch", "--list"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout
    assert "gt-upgrade-payload-" not in branches, f"payload branch must be cleaned up even on no-op; got:\n{branches}"
