"""Tests for ``scripts/check_whole_file_reformat.py`` (WI-4824)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_whole_file_reformat.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = _load_module(SCRIPT_PATH, "check_whole_file_reformat")


def _init_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)


def _commit_all(repo: Path, message: str = "init") -> None:
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=repo, check=True)


def _run_checker(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def test_classifies_suspicious_whitespace_dominated_churn() -> None:
    stats = checker.DiffStats(
        path="scripts/example.py",
        raw_additions=120,
        raw_deletions=120,
        ignored_additions=1,
        ignored_deletions=1,
    )

    finding = checker.classify_finding(stats, min_raw_changes=100)

    assert finding is not None
    assert finding.path == "scripts/example.py"
    assert finding.raw_changes == 240
    assert finding.ignored_changes == 2
    assert "whitespace_ignored_changes<=10" in finding.reason


def test_allows_large_substantive_edit() -> None:
    stats = checker.DiffStats(
        path="scripts/example.py",
        raw_additions=120,
        raw_deletions=120,
        ignored_additions=90,
        ignored_deletions=90,
    )

    assert checker.classify_finding(stats, min_raw_changes=100) is None


def test_threshold_configuration_controls_minimum_raw_changes() -> None:
    stats = checker.DiffStats(path="scripts/example.py", raw_additions=40, raw_deletions=40)

    assert checker.classify_finding(stats, min_raw_changes=100) is None
    assert checker.classify_finding(stats, min_raw_changes=50) is not None


def test_generated_and_bridge_paths_are_excluded() -> None:
    assert checker.exclusion_reason("dist/generated.js") == "excluded_by_pattern:dist/**"
    assert checker.exclusion_reason("bridge/gtkb-example-002.md") == "excluded_by_pattern:bridge/**"


def test_binary_numstat_entries_are_marked_for_skip() -> None:
    parsed = checker._parse_numstat("-\t-\timages/logo.png\n")

    assert parsed["images/logo.png"].binary is True


def test_cli_warns_on_whitespace_reformat_without_blocking(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    sample = repo / "sample.txt"
    sample.write_text("\n".join(f"key_{index}=value_{index}" for index in range(40)) + "\n", encoding="utf-8")
    _commit_all(repo)

    sample.write_text("\n".join(f"key_{index} = value_{index}" for index in range(40)) + "\n", encoding="utf-8")

    result = _run_checker(repo, "--paths", "sample.txt", "--min-raw-changes", "20")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[WARN]" in result.stdout
    assert "sample.txt" in result.stdout
    assert "whitespace_ignored_changes" in result.stdout


def test_cli_strict_blocks_whitespace_reformat(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    sample = repo / "sample.txt"
    sample.write_text("\n".join(f"key_{index}=value_{index}" for index in range(40)) + "\n", encoding="utf-8")
    _commit_all(repo)

    sample.write_text("\n".join(f"key_{index} = value_{index}" for index in range(40)) + "\n", encoding="utf-8")

    result = _run_checker(repo, "--strict", "--paths", "sample.txt", "--min-raw-changes", "20")

    assert result.returncode == 1
    assert "[FAIL]" in result.stderr
    assert "sample.txt" in result.stderr


def test_cli_skips_generated_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    generated = repo / "dist" / "generated.txt"
    generated.parent.mkdir()
    generated.write_text("\n".join(f"key_{index}=value_{index}" for index in range(40)) + "\n", encoding="utf-8")
    _commit_all(repo)

    generated.write_text("\n".join(f"key_{index} = value_{index}" for index in range(40)) + "\n", encoding="utf-8")

    result = _run_checker(
        repo,
        "--strict",
        "--json",
        "--paths",
        "dist/generated.txt",
        "--min-raw-changes",
        "20",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert '"status": "pass"' in result.stdout
    assert '"excluded_by_pattern:dist/**"' in result.stdout
