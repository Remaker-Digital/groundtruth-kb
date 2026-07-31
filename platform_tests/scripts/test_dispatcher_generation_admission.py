# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for WI-5429: dispatcher generation admission.

Validates that only terminal focused VERIFIED commits produce admissible
generations, and that materialized bytes match Git objects exactly.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import dispatcher_generation_admission as admission  # noqa: E402


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _init_git_repo(tmp_path: Path) -> Path:
    """Create a minimal git repo and return its root."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@gtkb.local"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "GT-KB Test"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return repo


def _write_and_commit(
    repo: Path,
    paths: dict[str, str],
    message: str,
) -> str:
    """Write files and commit, returning the commit SHA."""
    for rel, content in paths.items():
        fpath = repo / rel
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
    subprocess.run(
        ["git", "add", *paths.keys()],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    proc = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )
    # Extract SHA
    sha_proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )
    return sha_proc.stdout.strip()


def _init_generations_dir(repo: Path) -> Path:
    gd = repo / ".gtkb-state" / "dispatcher-generations"
    gd.mkdir(parents=True, exist_ok=True)
    return gd


# ---------------------------------------------------------------------------
# git operations
# ---------------------------------------------------------------------------


class TestGitOperations:
    def test_git_show_bytes_returns_correct_content(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        sha = _write_and_commit(
            repo,
            {"scripts/test.py": "print('hello')\n"},
            "feat: initial commit",
        )
        result = admission.git_show_bytes(repo, sha, "scripts/test.py")
        assert result == b"print('hello')\n"

    def test_git_show_bytes_returns_none_for_missing_path(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        sha = _write_and_commit(repo, {"a.txt": "hello"}, "feat: init")
        assert admission.git_show_bytes(repo, sha, "nonexistent.py") is None

    def test_git_commit_exists_detects_valid_commit(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        sha = _write_and_commit(repo, {"a.txt": "hi"}, "feat: init")
        assert admission.git_commit_exists(repo, sha) is True

    def test_git_commit_exists_rejects_bogus(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        assert admission.git_commit_exists(repo, "deadbeef") is False

    def test_git_changed_paths_lists_files(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        _write_and_commit(repo, {"a.txt": "a"}, "feat: first")
        sha = _write_and_commit(
            repo, {"scripts/daemon.py": "code", "bridge/verdict.md": "GO"}, "verify: commit"
        )
        changed = admission.git_changed_paths(repo, sha)
        assert "scripts/daemon.py" in changed
        assert "bridge/verdict.md" in changed

    def test_git_log_range_returns_commits_between(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        first = _write_and_commit(repo, {"a.txt": "a"}, "feat: first")
        second = _write_and_commit(repo, {"b.txt": "b"}, "fix: second")
        third = _write_and_commit(repo, {"c.txt": "c"}, "verify: third")
        between = admission.git_log_range(repo, first, third)
        assert second in between
        assert third in between


# ---------------------------------------------------------------------------
# provenance validation
# ---------------------------------------------------------------------------


class TestProvenanceValidation:
    def test_rejects_nonexistent_candidate(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        result = admission.validate_runtime_provenance(repo, "deadbeef")
        assert result["valid"] is False
        assert "candidate_commit_not_found" in result["errors"]

    def test_first_admission_requires_verified_commit(self, tmp_path):
        """When no predecessor exists, the candidate commit itself must be a
        VERIFIED terminal commit."""
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        # Create a commit that looks like a VERIFIED finalization
        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/wi5429-verdict-001.md": "VERIFIED",
            },
            "verify(dispatcher): WI-5429 generation admission",
        )
        result = admission.validate_runtime_provenance(repo, sha, rt_paths)
        assert result["valid"] is True, f"errors={result.get('errors')}"
        assert result["generation"] is not None
        assert result["generation"].startswith("sha256:")

    def test_rejects_commit_without_bridge_file(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {"scripts/daemon.py": "print('v1')"},
            "verify(dispatcher): should fail - no bridge file",
        )
        result = admission.validate_runtime_provenance(repo, sha, rt_paths)
        assert result["valid"] is False

    def test_rejects_commit_without_verify_in_subject(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/verdict.md": "GO",
            },
            "feat: not a verified commit",
        )
        result = admission.validate_runtime_provenance(repo, sha, rt_paths)
        assert result["valid"] is False

    def test_second_admission_validates_commit_range(self, tmp_path):
        """After a first admission, validate that the range between
        predecessor and candidate consists of VERIFIED commits."""
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        # First admission
        first = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/wi5429-001.md": "VERIFIED",
            },
            "verify(dispatcher): WI-5429 first admission",
        )

        # Record first admission
        admission.write_last_admitted(
            repo,
            {
                "generation": "sha256:first",
                "commit": first,
                "admitted_at": "2026-07-19T00:00:00Z",
                "runtime_paths": list(rt_paths),
                "manifest": [],
                "materialization_dir": str(repo / "gen-dir"),
                "predecessor_generation": None,
                "predecessor_commit": None,
            },
        )

        # A non-verified change in between
        intermediate = _write_and_commit(
            repo,
            {"scripts/daemon.py": "print('v2-unverified')"},
            "feat: unverified change",
        )

        # Candidate commit (not verified, but after intermediate)
        candidate = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v3')",
                "bridge/wi5429-002.md": "VERIFIED",
            },
            "verify(dispatcher): WI-5429 second admission",
        )

        result = admission.validate_runtime_provenance(repo, candidate, rt_paths)
        # Should be INVALID because intermediate commit is not verified
        assert result["valid"] is False
        assert "not_verified" in str(result["errors"]).lower()

    def test_all_runtime_paths_must_exist(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py", "scripts/supervisor.py")

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): only one runtime path",
        )
        result = admission.validate_runtime_provenance(repo, sha, rt_paths)
        assert result["valid"] is False
        assert any("missing" in e.lower() for e in result["errors"])

    def test_rejects_candidate_not_descendant_of_predecessor(self, tmp_path):
        """If candidate is not a descendant, reject."""
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        first = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/v1.md": "VERIFIED",
            },
            "verify: first",
        )

        # Simulate predecessor on a different branch
        admission.write_last_admitted(
            repo,
            {
                "generation": "sha256:prev",
                "commit": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
                "admitted_at": "2026-07-19T00:00:00Z",
                "runtime_paths": list(rt_paths),
                "manifest": [],
                "materialization_dir": str(repo / "gen-dir"),
                "predecessor_generation": None,
                "predecessor_commit": None,
            },
        )

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v2')",
                "bridge/v2.md": "VERIFIED",
            },
            "verify: second",
        )
        result = admission.validate_runtime_provenance(repo, sha, rt_paths)
        # Should fail because "deadbeef" doesn't exist
        assert result["valid"] is False


# ---------------------------------------------------------------------------
# materialization
# ---------------------------------------------------------------------------


class TestMaterialization:
    def test_materializes_files_from_git_objects(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py", "scripts/supervisor.py")

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('daemon v1')",
                "scripts/supervisor.py": "print('supervisor v1')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): materialize test",
        )

        result = admission.materialize_generation(repo, sha, rt_paths)
        assert result["materialized"] is True
        assert result["generation"].startswith("sha256:")
        assert len(result["manifest"]) == 2
        assert len(result["written_paths"]) == 2

        mat_dir = Path(result["materialization_dir"])
        assert mat_dir.is_dir()
        assert (mat_dir / "scripts" / "daemon.py").read_text() == "print('daemon v1')"
        assert (mat_dir / "scripts" / "supervisor.py").read_text() == "print('supervisor v1')"
        assert (mat_dir / "manifest.json").is_file()

    def test_materialize_rejects_missing_paths(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py", "scripts/missing.py")

        sha = _write_and_commit(
            repo,
            {"scripts/daemon.py": "print('v1')"},
            "feat: only one path",
        )
        result = admission.materialize_generation(repo, sha, rt_paths)
        assert result["materialized"] is False

    def test_materialized_bytes_match_git_objects(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        content = "print('exact content match test')"
        sha = _write_and_commit(
            repo,
            {"scripts/daemon.py": content},
            "feat: init",
        )
        result = admission.materialize_generation(repo, sha, rt_paths)
        assert result["materialized"] is True

        git_bytes = admission.git_show_bytes(repo, sha, "scripts/daemon.py")
        mat_dir = Path(result["materialization_dir"])
        mat_bytes = (mat_dir / "scripts" / "daemon.py").read_bytes()
        assert mat_bytes == git_bytes


# ---------------------------------------------------------------------------
# admission pipeline
# ---------------------------------------------------------------------------


class TestAdmissionPipeline:
    def test_full_admission_pipeline(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('admitted v1')",
                "bridge/wi5429-verdict-001.md": "VERIFIED",
            },
            "verify(dispatcher): WI-5429 full admission test",
        )

        result = admission.admit_generation(repo, sha, rt_paths)
        assert result["admitted"] is True
        assert result["generation"].startswith("sha256:")

        # Verify last-admitted pointer
        last = admission.read_last_admitted(repo)
        assert last is not None
        assert last["commit"] == sha

    def test_admit_rejects_unverified(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {"scripts/daemon.py": "print('unverified')"},
            "feat: not verified",
        )

        result = admission.admit_generation(repo, sha, rt_paths)
        assert result["admitted"] is False
        assert "provenance" in result["reason"]

    def test_admit_noop_same_generation(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): first admit",
        )

        first = admission.admit_generation(repo, sha, rt_paths)
        assert first["admitted"] is True

        second = admission.admit_generation(repo, sha, rt_paths)
        assert second["admitted"] is False
        assert second["reason"] == "generation_already_admitted"

    def test_dry_run_does_not_write_pointer(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): dry run test",
        )

        result = admission.admit_generation(repo, sha, rt_paths, dry_run=True)
        assert result["admitted"] is True

        last = admission.read_last_admitted(repo)
        assert last is None  # dry run should not write


# ---------------------------------------------------------------------------
# candidate_admission_status
# ---------------------------------------------------------------------------


class TestCandidateAdmissionStatus:
    def test_no_admitted_generation_exists(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        _write_and_commit(repo, {"scripts/daemon.py": "print('v1')"}, "feat: init")

        status = admission.candidate_admission_status(repo, ("scripts/daemon.py",))
        assert status["no_admitted_generation_exists"] is True
        assert status["last_admitted_generation"] is None

    def test_current_already_admitted(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): already admitted",
        )
        admission.admit_generation(repo, sha, rt_paths)

        status = admission.candidate_admission_status(repo, rt_paths)
        assert status["current_already_admitted"] is True

    def test_current_unfinalized_detected(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        # First: create and admit a generation
        sha1 = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): first admission",
        )
        admission.admit_generation(repo, sha1, rt_paths)

        # Second: change the working tree without admitting
        (repo / "scripts" / "daemon.py").write_text("print('v2-unadmitted')")

        status = admission.candidate_admission_status(repo, rt_paths)
        assert status["current_already_admitted"] is False
        assert status["current_unfinalized"] is True


# ---------------------------------------------------------------------------
# in-root boundary
# ---------------------------------------------------------------------------


class TestInRootBoundary:
    def test_materialization_stays_in_root(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('in-root')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): boundary test",
        )
        result = admission.admit_generation(repo, sha, rt_paths)
        mat_dir = Path(result["materialization"]["materialization_dir"])
        assert str(repo.resolve()) in str(mat_dir.resolve())
        assert ".gtkb-state" in str(mat_dir)


# ---------------------------------------------------------------------------
# hash verification
# ---------------------------------------------------------------------------


class TestHashVerification:
    def test_generation_hash_is_deterministic(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py", "scripts/supervisor.py")

        sha = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('daemon')",
                "scripts/supervisor.py": "print('supervisor')",
                "bridge/verdict.md": "VERIFIED",
            },
            "verify(dispatcher): deterministic hash",
        )

        result1 = admission.admit_generation(repo, sha, rt_paths)
        # Clear the pointer so we can re-admit
        admission.last_admitted_path(repo).unlink()
        result2 = admission.admit_generation(repo, sha, rt_paths)

        assert result1["generation"] == result2["generation"]

    def test_different_content_produces_different_hash(self, tmp_path):
        repo = _init_git_repo(tmp_path)
        rt_paths = ("scripts/daemon.py",)

        sha1 = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v1')",
                "bridge/v1.md": "VERIFIED",
            },
            "verify(dispatcher): v1",
        )
        r1 = admission.admit_generation(repo, sha1, rt_paths)

        admission.last_admitted_path(repo).unlink()

        sha2 = _write_and_commit(
            repo,
            {
                "scripts/daemon.py": "print('v2')",
                "bridge/v2.md": "VERIFIED",
            },
            "verify(dispatcher): v2",
        )
        r2 = admission.admit_generation(repo, sha2, rt_paths)

        assert r1["generation"] != r2["generation"]