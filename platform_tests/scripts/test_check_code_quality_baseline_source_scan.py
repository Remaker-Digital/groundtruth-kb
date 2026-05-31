from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_code_quality_baseline_source_scan.py"


def test_source_scan_returns_result_against_head() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--since", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode in {0, 1}
    assert result.stdout


def _init_repo(repo: Path) -> str:
    (repo / "sample.py").write_text("value = 1\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def test_source_scan_flags_secret_and_absolute_path(tmp_path: Path) -> None:
    base = _init_repo(tmp_path)
    (tmp_path / "sample.py").write_text(
        "api_key = '1234567890123456'\npath = 'C:\\\\Temp\\\\x'\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--since", base, "--project-root", str(tmp_path)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "CQ-SECRETS-001" in result.stdout
    assert "CQ-PATHS-001" in result.stdout


def test_source_scan_flags_large_numeric_literal(tmp_path: Path) -> None:
    base = _init_repo(tmp_path)
    (tmp_path / "sample.py").write_text("value = 10000\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--since", base, "--project-root", str(tmp_path)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "CQ-CONSTANTS-001" in result.stdout


def test_source_scan_clean_diff_returns_zero(tmp_path: Path) -> None:
    base = _init_repo(tmp_path)
    (tmp_path / "sample.py").write_text("value = 2\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--since", base, "--project-root", str(tmp_path)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0


def test_source_scan_pathspec_limits_dirty_tree(tmp_path: Path) -> None:
    base = _init_repo(tmp_path)
    (tmp_path / "sample.py").write_text("value = 10000\n", encoding="utf-8")
    (tmp_path / "other.py").write_text("value = 2\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--since", base, "--project-root", str(tmp_path), "other.py"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0


def test_source_scan_reports_complexity_status() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--since", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode in {0, 1}
    assert "CQ-COMPLEXITY-001" in result.stdout or "Code Quality Baseline source scan clean" in result.stdout
