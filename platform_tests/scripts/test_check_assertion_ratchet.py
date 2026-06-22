from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "guardrails" / "check_assertion_ratchet.py"


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )


def _write_test_file(repo: Path, assertion_count: int) -> None:
    test_path = repo / "tests" / "foo" / "test_a.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    assertions = "\n".join(f"    assert {idx} == {idx}" for idx in range(assertion_count))
    test_path.write_text(f"def test_example():\n{assertions}\n", encoding="utf-8")


def _write_baseline(repo: Path, assertion_count: int) -> Path:
    baseline_path = repo / "scripts" / "guardrails" / "assertion-baseline.json"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(
        json.dumps(
            {
                "_metadata": {
                    "description": "test baseline",
                    "generator": "scripts/guardrails/generate_assertion_baseline.py",
                    "total_assertions": assertion_count,
                    "total_files": 1,
                },
                "baselines": {"tests/foo/test_a.py": assertion_count},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return baseline_path


def _init_repo(tmp_path: Path, *, assertion_count: int = 1) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init")
    _run_git(repo, "config", "user.name", "GTKB Test")
    _run_git(repo, "config", "user.email", "gtkb-test@example.invalid")
    _write_test_file(repo, assertion_count)
    _write_baseline(repo, assertion_count)
    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-m", "initial")
    return repo


def _load_ratchet(monkeypatch: pytest.MonkeyPatch, repo: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_assertion_ratchet_under_test", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "PROJECT_ROOT", repo)
    monkeypatch.setattr(module, "BASELINE_PATH", repo / "scripts" / "guardrails" / "assertion-baseline.json")
    return module


def _cached_names(repo: Path) -> list[str]:
    result = _run_git(repo, "diff", "--cached", "--name-only")
    return result.stdout.strip().splitlines()


def _baseline_count(repo: Path) -> int:
    data = json.loads((repo / "scripts" / "guardrails" / "assertion-baseline.json").read_text(encoding="utf-8"))
    return data["baselines"]["tests/foo/test_a.py"]


def test_ratchet_does_not_stage_baseline_on_increase(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_repo(tmp_path)
    module = _load_ratchet(monkeypatch, repo)
    _write_test_file(repo, 2)
    _run_git(repo, "add", "tests/foo/test_a.py")

    before = _cached_names(repo)
    assert before == ["tests/foo/test_a.py"]

    assert module.main() == 0

    assert _cached_names(repo) == before
    assert _baseline_count(repo) == 2


def test_ratchet_leaves_unrelated_staged_set_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_repo(tmp_path)
    module = _load_ratchet(monkeypatch, repo)
    _write_test_file(repo, 2)
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _run_git(repo, "add", "README.md", "tests/foo/test_a.py")

    before = _cached_names(repo)
    assert before == ["README.md", "tests/foo/test_a.py"]

    assert module.main() == 0

    assert _cached_names(repo) == before


def test_ratchet_still_blocks_assertion_decrease(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_repo(tmp_path, assertion_count=2)
    module = _load_ratchet(monkeypatch, repo)
    _write_test_file(repo, 1)
    _run_git(repo, "add", "tests/foo/test_a.py")

    assert module.main() == 1

    assert _cached_names(repo) == ["tests/foo/test_a.py"]
    assert _baseline_count(repo) == 2


def test_ratchet_increase_returns_zero_and_baseline_unstaged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_repo(tmp_path)
    module = _load_ratchet(monkeypatch, repo)
    _write_test_file(repo, 2)
    _run_git(repo, "add", "tests/foo/test_a.py")

    assert module.main() == 0

    assert _cached_names(repo) == ["tests/foo/test_a.py"]
    status = _run_git(repo, "status", "--short", "--", "scripts/guardrails/assertion-baseline.json")
    assert status.stdout.startswith(" M ")
