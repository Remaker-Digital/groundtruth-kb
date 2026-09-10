"""Read-only root confinement and bounded Git failure in the doctor stray scan."""

import subprocess
from pathlib import Path

import pytest


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=15)


def _init_repo(root: Path) -> Path:
    _git(root, "init")
    _git(root, "config", "user.name", "Qualification")
    _git(root, "config", "user.email", "qualification@example.invalid")
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", "tracked.txt")
    _git(root, "commit", "-m", "Disposable base")
    return root


def test_strays_exact_checkout_still_returns_read_only_clean_report(tmp_path):
    from groundtruth_kb.hygiene.strays import run_strays

    root = _init_repo(tmp_path)
    index_before = (root / ".git/index").read_bytes()
    report = run_strays(root)
    assert report["source"]["root"] == str(root.resolve())
    assert report["source"]["read_only"] is True
    assert report["candidate_actions_only"] is True
    assert report["counts"]["workspace_total"] == 0
    assert (root / ".git/index").read_bytes() == index_before


def test_strays_refuses_ancestor_discovery_before_reading_workspace_or_peers(tmp_path, monkeypatch):
    from groundtruth_kb.hygiene import strays

    root = _init_repo(tmp_path)
    nested = root / "nested-project"
    nested.mkdir()
    sentinel = root / "foreign.txt"
    sentinel.write_bytes(b"Foreign work must not be scanned or changed")
    _git(root, "add", "foreign.txt")
    index_before = (root / ".git/index").read_bytes()

    def unexpected(*args, **kwargs):
        pytest.fail("An ancestor root refusal must precede all content and worktree collectors")

    for name in (
        "_load_active_registry_records",
        "collect_workspace_entries",
        "collect_stash_entries",
        "collect_worktree_entries",
    ):
        monkeypatch.setattr(strays, name, unexpected)
    with pytest.raises(strays.StraysError, match="exact Git checkout root"):
        strays.run_strays(nested)
    assert sentinel.read_bytes() == b"Foreign work must not be scanned or changed"
    assert (root / ".git/index").read_bytes() == index_before


def test_doctor_reports_nested_root_refusal_without_inheriting_parent_scan(tmp_path, monkeypatch):
    from groundtruth_kb.hygiene import strays
    from groundtruth_kb.project.doctor import _check_work_tree_strays

    root = _init_repo(tmp_path)
    nested = root / "nested-project"
    nested.mkdir()

    def unexpected(*args, **kwargs):
        pytest.fail("Doctor must not scan an ancestor checkout")

    monkeypatch.setattr(strays, "collect_workspace_entries", unexpected)
    result = _check_work_tree_strays(nested)
    assert result.status == "warning"
    assert result.found is False
    assert "exact Git checkout root" in result.message


@pytest.mark.parametrize("failure", ["timeout", "missing-executable"])
def test_strays_git_failure_is_bounded_and_usefully_reported(tmp_path, monkeypatch, failure):
    from groundtruth_kb.hygiene import strays

    def unavailable(argv, **kwargs):
        assert kwargs["timeout"] == 15
        if failure == "timeout":
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
        raise FileNotFoundError("git unavailable")

    monkeypatch.setattr(strays.subprocess, "run", unavailable)
    with pytest.raises(strays.StraysError, match="git rev-parse unavailable or exceeded the 15-second read bound"):
        strays.run_strays(tmp_path)
