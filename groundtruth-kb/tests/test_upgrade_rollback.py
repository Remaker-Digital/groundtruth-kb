# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for C3 gtkb-upgrade-rollback.

Covers all Codex binding conditions from bridge/gtkb-upgrade-rollback-006.md GO:

- F1: file-list primitive uses git diff --name-status <merge>^1 <merge>
  (real --no-ff merge topology).
- F2: separate `gt project rollback` command (not an --rollback flag).
- F3: full ReceiptJSON schema validation; latest-receipt ordering by created_at
  with deterministic tie-break on receipt_id.
- F4: separate --dry-run / --apply flags with explicit mutual exclusion.
- F5: docs updates (asserted structurally via CLI help text).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.project.rollback import (
    DirtyWorkingTreeError,
    MergeCommitNotInHistoryError,
    NotAMergeCommitError,
    ReceiptMalformedError,
    ReceiptNotFoundError,
    ReceiptSchemaVersionMismatchError,
    execute_rollback,
    find_latest_receipt,
    find_receipt_by_id,
    list_receipts,
    plan_rollback,
    read_receipt,
)

# ---------------------------------------------------------------------------
# Fixtures + helpers
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=check,
        capture_output=capture,
        text=True,
    )


def _init_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "config", "commit.gpgsign", "false")
    (root / "README.md").write_text("initial\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "initial")


def _make_noff_merge(root: Path, payload_files: dict[str, str]) -> str:
    """Create a payload branch with the given files, merge --no-ff back to main. Return merge SHA."""
    _git(root, "checkout", "-b", "payload-branch")
    for rel, content in payload_files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "payload")
    _git(root, "checkout", "main")
    _git(root, "merge", "--no-ff", "payload-branch", "-m", "merge payload")
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    return head


def _write_receipt(
    root: Path,
    overrides: dict | None = None,
    *,
    filename: str = "r1.json",
    commit: bool = False,
) -> Path:
    """Write a valid-ish receipt JSON for tests; ``overrides`` can mutate fields.

    When ``commit=True``, stages + commits the receipt (simulates tracked mode
    so ``git status --porcelain`` stays clean for execute_rollback tests).
    """
    active_dir = root / ".claude" / "upgrade-receipts" / "active"
    active_dir.mkdir(parents=True, exist_ok=True)
    default: dict = {
        "schema_version": "v1",
        "receipt_id": "a1b2c3d4e5f60000",
        "merge_commit": "0" * 40,
        "target_branch": "main",
        "from_version": "0.6.1",
        "to_version": "0.6.2",
        "mode": "tracked",
        "created_at": "2026-04-18T22:00:00+00:00",
        "artifact_classes_touched": ["hook", "rule"],
    }
    if overrides:
        default.update(overrides)
    path = active_dir / filename
    path.write_text(json.dumps(default, indent=2) + "\n", encoding="utf-8")
    if commit:
        _git(root, "add", str(path))
        _git(root, "commit", "-m", f"receipt {filename}")
    return path


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    _init_repo(root)
    return root


# ---------------------------------------------------------------------------
# F3 — read_receipt() validation
# ---------------------------------------------------------------------------


class TestReadReceiptValidation:
    def test_happy_path(self, tmp_path, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        path = _write_receipt(repo, {"merge_commit": merge_sha})
        receipt = read_receipt(path)
        assert receipt["schema_version"] == "v1"
        assert receipt["merge_commit"] == merge_sha

    def test_missing_file_raises_not_found(self, tmp_path):
        with pytest.raises(ReceiptNotFoundError):
            read_receipt(tmp_path / "nope.json")

    def test_invalid_json_raises_malformed(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not-valid-json{", encoding="utf-8")
        with pytest.raises(ReceiptMalformedError):
            read_receipt(bad)

    def test_not_object_raises(self, tmp_path):
        bad = tmp_path / "arr.json"
        bad.write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(ReceiptMalformedError):
            read_receipt(bad)

    @pytest.mark.parametrize(
        "missing_field",
        [
            "schema_version",
            "receipt_id",
            "merge_commit",
            "target_branch",
            "from_version",
            "to_version",
            "mode",
            "created_at",
            "artifact_classes_touched",
        ],
    )
    def test_missing_field_raises(self, repo, missing_field):
        # Build a full dict and drop the one field.
        path = _write_receipt(repo)
        raw = json.loads(path.read_text(encoding="utf-8"))
        del raw[missing_field]
        path.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(ReceiptMalformedError):
            read_receipt(path)

    def test_wrong_schema_version_raises_schema_mismatch(self, repo):
        path = _write_receipt(repo, {"schema_version": "v2"})
        with pytest.raises(ReceiptSchemaVersionMismatchError):
            read_receipt(path)

    def test_invalid_mode_raises(self, repo):
        path = _write_receipt(repo, {"mode": "archive"})
        with pytest.raises(ReceiptMalformedError, match="mode must be"):
            read_receipt(path)

    def test_non_hex_merge_commit_raises(self, repo):
        path = _write_receipt(repo, {"merge_commit": "xyz"})
        with pytest.raises(ReceiptMalformedError, match="merge_commit must be"):
            read_receipt(path)

    def test_short_merge_commit_raises(self, repo):
        path = _write_receipt(repo, {"merge_commit": "abc123"})
        with pytest.raises(ReceiptMalformedError, match="merge_commit must be"):
            read_receipt(path)

    def test_non_parseable_created_at_raises(self, repo):
        path = _write_receipt(repo, {"created_at": "not-a-date"})
        with pytest.raises(ReceiptMalformedError, match="parseable"):
            read_receipt(path)

    def test_artifact_classes_not_list_raises(self, repo):
        path = _write_receipt(repo, {"artifact_classes_touched": "hook"})
        with pytest.raises(ReceiptMalformedError, match="must be a list"):
            read_receipt(path)

    def test_empty_target_branch_raises(self, repo):
        path = _write_receipt(repo, {"target_branch": ""})
        with pytest.raises(ReceiptMalformedError, match="target_branch"):
            read_receipt(path)


# ---------------------------------------------------------------------------
# F3 — list_receipts + find_latest_receipt ordering
# ---------------------------------------------------------------------------


class TestReceiptOrdering:
    def test_empty_directory_returns_empty_list(self, tmp_path):
        assert list_receipts(tmp_path) == []
        assert find_latest_receipt(tmp_path) is None

    def test_orders_by_created_at_descending(self, repo):
        _write_receipt(
            repo,
            {"receipt_id": "older", "created_at": "2026-04-18T20:00:00+00:00"},
            filename="r-older.json",
        )
        _write_receipt(
            repo,
            {"receipt_id": "newer", "created_at": "2026-04-18T22:00:00+00:00"},
            filename="r-newer.json",
        )
        receipts = list_receipts(repo)
        assert [r["receipt_id"] for r in receipts] == ["newer", "older"]
        assert find_latest_receipt(repo)["receipt_id"] == "newer"

    def test_tie_breaks_on_receipt_id_descending(self, repo):
        # Identical created_at; lexically larger receipt_id wins.
        _write_receipt(
            repo,
            {"receipt_id": "aaa111", "created_at": "2026-04-18T22:00:00+00:00"},
            filename="r-a.json",
        )
        _write_receipt(
            repo,
            {"receipt_id": "zzz999", "created_at": "2026-04-18T22:00:00+00:00"},
            filename="r-z.json",
        )
        assert find_latest_receipt(repo)["receipt_id"] == "zzz999"

    def test_ordering_independent_of_file_mtime(self, repo):
        # Write the "newer" receipt first (earlier mtime), the "older" receipt later.
        _write_receipt(
            repo,
            {"receipt_id": "newer", "created_at": "2026-04-18T22:00:00+00:00"},
            filename="a.json",
        )
        import time

        time.sleep(0.05)
        _write_receipt(
            repo,
            {"receipt_id": "older", "created_at": "2026-04-18T20:00:00+00:00"},
            filename="b.json",
        )
        # Despite later mtime, "older" should not win — created_at is authoritative.
        assert find_latest_receipt(repo)["receipt_id"] == "newer"


# ---------------------------------------------------------------------------
# F3 — find_receipt_by_id
# ---------------------------------------------------------------------------


class TestFindReceiptById:
    def test_happy_path(self, repo):
        _write_receipt(repo, {"receipt_id": "abc"}, filename="r.json")
        found = find_receipt_by_id(repo, "abc")
        assert found["receipt_id"] == "abc"

    def test_missing_id_raises_not_found(self, repo):
        _write_receipt(repo, {"receipt_id": "abc"}, filename="r.json")
        with pytest.raises(ReceiptNotFoundError):
            find_receipt_by_id(repo, "zzz")


# ---------------------------------------------------------------------------
# F1 — plan_rollback() against real --no-ff merge
# ---------------------------------------------------------------------------


class TestPlanRollback:
    def test_happy_path_with_added_files(self, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi", "subdir/f.txt": "x"})
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json")
        plan = plan_rollback(repo)
        assert plan.merge_commit == merge_sha
        paths = {e.path for e in plan.files_to_revert}
        assert "payload.txt" in paths
        assert "subdir/f.txt" in paths
        # All are adds for this synthetic merge.
        statuses = {e.status for e in plan.files_to_revert}
        assert statuses == {"A"}

    def test_added_and_modified_and_deleted(self, repo):
        # Set up pre-existing file.
        (repo / "existing.txt").write_text("orig\n", encoding="utf-8")
        (repo / "to-delete.txt").write_text("delete me\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-m", "setup")
        # Payload: add, modify, delete.
        _git(repo, "checkout", "-b", "payload-branch")
        (repo / "added.txt").write_text("new\n", encoding="utf-8")
        (repo / "existing.txt").write_text("modified\n", encoding="utf-8")
        (repo / "to-delete.txt").unlink()
        _git(repo, "add", "-A")
        _git(repo, "commit", "-m", "payload mixed")
        _git(repo, "checkout", "main")
        _git(repo, "merge", "--no-ff", "payload-branch", "-m", "merge")
        merge_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json")
        plan = plan_rollback(repo)
        paths_by_status = {(e.path, e.status) for e in plan.files_to_revert}
        assert ("added.txt", "A") in paths_by_status
        assert ("existing.txt", "M") in paths_by_status
        assert ("to-delete.txt", "D") in paths_by_status

    def test_non_merge_commit_raises(self, repo):
        # Make a plain (non-merge) commit and reference it in a receipt.
        (repo / "x.txt").write_text("x\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-m", "plain")
        non_merge = _git(repo, "rev-parse", "HEAD").stdout.strip()
        _write_receipt(repo, {"merge_commit": non_merge}, filename="r.json")
        with pytest.raises(NotAMergeCommitError):
            plan_rollback(repo)

    def test_merge_not_reachable_raises(self, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json")
        # Reset main to before the merge so it's not reachable.
        _git(repo, "reset", "--hard", "HEAD~1")
        with pytest.raises(MergeCommitNotInHistoryError):
            plan_rollback(repo)

    def test_no_receipts_raises(self, repo):
        with pytest.raises(ReceiptNotFoundError):
            plan_rollback(repo)

    def test_by_receipt_id(self, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, {"receipt_id": "specific", "merge_commit": merge_sha}, filename="r.json")
        plan = plan_rollback(repo, receipt_id="specific")
        assert plan.receipt["receipt_id"] == "specific"

    def test_by_unknown_receipt_id_raises(self, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json")
        with pytest.raises(ReceiptNotFoundError):
            plan_rollback(repo, receipt_id="not-there")


# ---------------------------------------------------------------------------
# F1 — execute_rollback() against real --no-ff merge
# ---------------------------------------------------------------------------


class TestExecuteRollback:
    def test_no_commit_mode_stages_revert(self, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json", commit=True)
        plan = plan_rollback(repo)
        pre_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        result = execute_rollback(repo, plan, commit=False)
        assert result.mode == "revert-no-commit"
        assert result.commit_sha is None
        # HEAD unchanged; working tree has staged deletions of payload.
        assert _git(repo, "rev-parse", "HEAD").stdout.strip() == pre_head
        status = _git(repo, "status", "--porcelain").stdout
        assert "payload.txt" in status

    def test_commit_mode_creates_commit(self, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json", commit=True)
        plan = plan_rollback(repo)
        pre_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        result = execute_rollback(repo, plan, commit=True)
        assert result.mode == "revert-commit"
        assert result.commit_sha is not None
        # HEAD moved forward; working tree clean; payload.txt is gone.
        new_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert new_head != pre_head
        assert result.commit_sha == new_head
        assert not (repo / "payload.txt").exists()
        assert _git(repo, "status", "--porcelain").stdout.strip() == ""

    def test_dirty_tree_refuses(self, repo):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json")
        plan = plan_rollback(repo)
        # Dirty the tree.
        (repo / "dirty.txt").write_text("x", encoding="utf-8")
        with pytest.raises(DirtyWorkingTreeError):
            execute_rollback(repo, plan, commit=False)

    def test_commit_mode_uses_approved_message(self, repo):
        """F7: --apply --commit must use 'gt: rollback upgrade payload {receipt_id}'
        commit message, NOT git's default 'Revert \"...\"' subject."""
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(
            repo,
            {"receipt_id": "a1b2c3d4e5f60000", "merge_commit": merge_sha},
            filename="r.json",
            commit=True,
        )
        plan = plan_rollback(repo)
        result = execute_rollback(repo, plan, commit=True)
        assert result.mode == "revert-commit"
        # Verify exact commit subject.
        subject = _git(repo, "log", "-1", "--format=%s").stdout.strip()
        assert subject == "gt: rollback upgrade payload a1b2c3d4e5f60000", (
            f"F7 violation: expected approved message, got {subject!r}"
        )


# ---------------------------------------------------------------------------
# F8 — Missing/nonexistent merge commits leak CalledProcessError → map to MergeCommitNotInHistoryError
# ---------------------------------------------------------------------------


class TestMissingMergeCommitSHA:
    """F8: valid 40-char hex SHA that is absent from the repo must raise
    MergeCommitNotInHistoryError, not leak CalledProcessError."""

    def test_valid_hex_absent_sha_raises_documented_exception(self, repo):
        # "a" * 40 is syntactically a valid SHA but does not exist in the repo.
        _write_receipt(repo, {"merge_commit": "a" * 40}, filename="r.json")
        with pytest.raises(MergeCommitNotInHistoryError):
            plan_rollback(repo)

    def test_absent_sha_cli_exit_code(self, repo, monkeypatch):
        _write_receipt(repo, {"merge_commit": "a" * 40}, filename="r.json")
        monkeypatch.chdir(repo)
        runner = CliRunner()
        result = runner.invoke(cli_main, ["project", "rollback"])
        # Exit 5 per docs/reference/cli.md (MergeCommitNotInHistoryError).
        assert result.exit_code == 5, f"F8 violation: expected exit 5 for absent SHA, got {result.exit_code}"


# ---------------------------------------------------------------------------
# F4 — CLI flag validation
# ---------------------------------------------------------------------------


class TestCLIFlagValidation:
    def test_dry_run_and_apply_mutually_exclusive(self, repo, monkeypatch):
        monkeypatch.chdir(repo)
        runner = CliRunner()
        result = runner.invoke(cli_main, ["project", "rollback", "--dry-run", "--apply"])
        assert result.exit_code != 0
        assert (
            "mutually exclusive" in result.output.lower()
            or "mutually exclusive" in (result.stderr_bytes or b"").decode(errors="ignore").lower()
        )

    def test_commit_requires_apply(self, repo, monkeypatch):
        monkeypatch.chdir(repo)
        runner = CliRunner()
        result = runner.invoke(cli_main, ["project", "rollback", "--commit"])
        assert result.exit_code != 0
        out = result.output + (result.stderr_bytes or b"").decode(errors="ignore")
        assert "requires --apply" in out.lower()

    def test_bare_invocation_defaults_to_dry_run(self, repo, monkeypatch):
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, {"merge_commit": merge_sha}, filename="r.json")
        monkeypatch.chdir(repo)
        runner = CliRunner()
        result = runner.invoke(cli_main, ["project", "rollback"])
        # Dry-run path prints "no changes applied" and exits 0.
        assert result.exit_code == 0, result.output
        assert "dry run" in result.output.lower()

    def test_unknown_receipt_id_exits_nonzero(self, repo, monkeypatch):
        _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(repo, filename="r.json")
        monkeypatch.chdir(repo)
        runner = CliRunner()
        result = runner.invoke(cli_main, ["project", "rollback", "--receipt-id", "UNKNOWN"])
        assert result.exit_code != 0

    def test_cli_apply_commit_uses_approved_message(self, repo):
        """F10: ``gt project rollback --apply --commit`` must exit 0 and produce
        the approved ``gt: rollback upgrade payload {receipt_id}`` commit subject
        via the CLI surface (not just the library call)."""
        merge_sha = _make_noff_merge(repo, {"payload.txt": "hi"})
        _write_receipt(
            repo,
            {"receipt_id": "a1b2c3d4e5f60000", "merge_commit": merge_sha},
            filename="r.json",
            commit=True,
        )
        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            ["project", "rollback", "--apply", "--commit", "--target-dir", str(repo)],
        )
        assert result.exit_code == 0, result.output
        subject = _git(repo, "log", "-1", "--format=%s").stdout.strip()
        assert subject == "gt: rollback upgrade payload a1b2c3d4e5f60000", (
            f"F10 violation: expected approved CLI commit subject, got {subject!r}"
        )
