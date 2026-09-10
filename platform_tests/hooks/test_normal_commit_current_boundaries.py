"""Exercise normal Git hooks and the Windows mirror against real staged bytes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import groundtruth_kb
import pytest
from groundtruth_kb.governance.commit_preflight import preflight_exit_code, run_commit_preflight
from groundtruth_kb.secrets import GitScanError, scan_staged

ROOT = Path(__file__).resolve().parents[2]
TOKEN = "AK" + "IA" + "R" * 16
SECOND_TOKEN = "gh" + "p_" + "Z" * 36


def git(root, *args, check=True, input=None):
    return subprocess.run(["git", "-C", str(root), *args], input=input, capture_output=True, check=check, timeout=60)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "core.autocrlf", "false")
    git(tmp_path, "config", "user.email", "test@invalid.example")
    git(tmp_path, "config", "user.name", "Normal Hook Test")
    # Establish historical bytes before installing the hook under test.
    old = tmp_path / "bridge/obsolete.md"
    old.parent.mkdir()
    old.write_text("old disposable message\n")
    git(tmp_path, "add", "--", "bridge/obsolete.md")
    git(tmp_path, "commit", "-qm", "historical fixture")
    for name in [
        ".githooks/pre-commit",
        ".githooks/pre-commit-ps1-parse.ps1",
        "scripts/scan_secrets.py",
        "scripts/check_ruff_format.py",
        "scripts/check_commit_pathspec_safety.py",
        "scripts/check_projection_drift.py",
    ]:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    git(tmp_path, "config", "core.hooksPath", ".githooks")
    monkeypatch.setenv("PYTHON", sys.executable)
    monkeypatch.setenv("PYTHONPATH", str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    monkeypatch.setenv("PATH", str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"])
    return tmp_path


def stage(repo, name, content):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    git(repo, "add", "--", name)


def preserved(repo):
    # Git commit may refresh stat/cache-tree fields even when a hook refuses.
    # Preserve every staged path, mode, object and merge stage plus HEAD.
    return git(repo, "rev-parse", "HEAD").stdout, git(repo, "ls-files", "--stage", "-z").stdout


def test_normal_commit_accepts_product_and_forward_removal_preserving_foreign_bytes(repo):
    stage(repo, "src/product.txt", "reviewed product\n")
    (repo / "foreign.txt").write_bytes(b"unrelated\x00bytes")
    git(repo, "rm", "--", "bridge/obsolete.md")
    evidence = run_commit_preflight(repo, python_bin=sys.executable)
    assert preflight_exit_code(evidence) == 0, evidence
    result = git(repo, "commit", "-m", "complete product", check=False)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert b"PASS staged work product" in result.stderr
    assert git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout == b"src/product.txt\n"
    assert (repo / "foreign.txt").read_bytes() == b"unrelated\x00bytes"
    assert not (repo / ".tmp").exists()


@pytest.mark.parametrize("path", ["bridge/new.md", ".codex/hooks.json", ".groundtruth/inventory/public.json"])
def test_normal_commit_and_windows_preflight_refuse_nonproduct_postimages(repo, path):
    stage(repo, path, "not product\n")
    before = preserved(repo)
    evidence = run_commit_preflight(repo, python_bin=sys.executable)
    assert preflight_exit_code(evidence) == 1
    result = git(repo, "commit", "-m", "must refuse", check=False)
    assert result.returncode != 0
    assert b"not_work_product" in result.stderr
    assert preserved(repo) == before


@pytest.mark.parametrize("path", ["src/credential.txt", "dist/payload", "docs/café [1].txt", "notes/with space.txt"])
def test_staged_secret_is_blocked_after_working_copy_is_cleaned(repo, path):
    stage(repo, path, f"sample: {TOKEN} {SECOND_TOKEN}\n")
    (repo / path).write_text("clean unstaged replacement\n", encoding="utf-8")
    before = preserved(repo)
    result = git(repo, "commit", "-m", "must refuse", check=False)
    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert b'"status": "fail"' in output
    assert TOKEN.encode() not in output and SECOND_TOKEN.encode() not in output
    assert preserved(repo) == before
    assert (repo / path).read_text() == "clean unstaged replacement\n"
    assert not (repo / ".tmp").exists()


def test_clean_index_does_not_scan_or_overwrite_unstaged_secret(repo):
    stage(repo, "src/product.txt", "clean staged product\n")
    (repo / "src/product.txt").write_text(TOKEN, encoding="utf-8")
    result = git(repo, "commit", "-m", "exact staged product", check=False)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert git(repo, "show", "HEAD:src/product.txt").stdout == b"clean staged product\n"
    assert (repo / "src/product.txt").read_text() == TOKEN
    assert TOKEN.encode() not in result.stdout + result.stderr


def test_staged_scan_uses_selected_candidate_index_without_changing_foreign_index(repo, monkeypatch):
    stage(repo, "safe.txt", "product\n")
    original = (repo / ".git/index").read_bytes()
    candidate = repo / "candidate-index"
    candidate.write_bytes(original)
    monkeypatch.setenv("GIT_INDEX_FILE", str(candidate))
    stage(repo, "selected.txt", SECOND_TOKEN)
    candidate_before = candidate.read_bytes()
    result = scan_staged(repo_root=repo)
    # The default library registry covers OAuth; the hook additionally retains
    # its existing GitHub PAT patterns. Use the shared scan with that registry.
    command = subprocess.run(
        [sys.executable, str(repo / "scripts/scan_secrets.py"), "--staged"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert command.returncode == 1
    assert json.loads(command.stdout)["finding_count"] >= 1
    assert result.paths_scanned == 2
    assert (repo / ".git/index").read_bytes() == original
    assert candidate.read_bytes() == candidate_before


def test_staged_scan_refuses_unavailable_index_without_outputting_raw_git_diagnostics(repo, monkeypatch):
    bad_index = repo / "invalid-index"
    bad_index.write_bytes(b"invalid " + TOKEN.encode())
    monkeypatch.setenv("GIT_INDEX_FILE", str(bad_index))
    with pytest.raises(GitScanError, match="staged_scan_unavailable"):
        scan_staged(repo_root=repo)
    result = subprocess.run(
        [sys.executable, str(repo / "scripts/scan_secrets.py"), "--staged"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["reason"] == "secret_scan_unavailable"
    assert TOKEN not in result.stdout + result.stderr


@pytest.mark.parametrize(
    "name",
    [
        "scripts/scan_secrets.py",
        "groundtruth-kb/tests/test_credential_patterns.py",
        "groundtruth-kb/tests/test_intake.py",
    ],
)
def test_scanner_source_and_synthetic_fixtures_pass_without_line_exemptions(repo, name):
    target = repo / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((ROOT / name).read_bytes())
    git(repo, "add", "--", name)
    before = (repo / ".git/index").read_bytes()
    result = subprocess.run(
        [sys.executable, str(repo / "scripts/scan_secrets.py"), "--staged"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert all(f["severity"] != "candidate-high" for f in json.loads(result.stdout)["findings"])
    assert (repo / ".git/index").read_bytes() == before
