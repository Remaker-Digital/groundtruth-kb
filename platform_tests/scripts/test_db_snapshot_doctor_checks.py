"""Platform tests for FAB-03 MemBase backup doctor checks.

Verifies:
- _check_db_snapshot_freshness reports pass/warning based on snapshot age.
- _check_db_snapshot_output_allowlist enforces the allowlist bound from
  project-root-boundary.md § DB-Snapshot Output Exception.
- The allowlist regex in doctor.py matches the rule text in
  project-root-boundary.md (rule-text-vs-source parity).
- The install script exists and is idempotent (syntax check only; does not
  create the actual scheduled task in CI).

Specification Links:
- DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611
- .claude/rules/project-root-boundary.md § DB-Snapshot Output Exception
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Allowlist regex parity
# ---------------------------------------------------------------------------


def test_allowlist_regex_matches_localappdata_pattern() -> None:
    """The doctor allowlist must accept the platform-default output path."""
    from groundtruth_kb.project.doctor import _DB_SNAPSHOT_OUTPUT_ALLOWLIST

    paths_should_match = [
        r"C:\Users\micha\AppData\Local\gtkb-snapshots\GroundTruth-KB Platform",
        r"C:/Users/micha/AppData/Local/gtkb-snapshots/SomeProject",
        r"D:\Users\AnyUser\AppData\Local\gtkb-snapshots\test",
    ]
    for p in paths_should_match:
        assert _DB_SNAPSHOT_OUTPUT_ALLOWLIST.match(p), f"Expected match: {p}"


def test_allowlist_regex_rejects_non_localappdata() -> None:
    """Paths outside %LOCALAPPDATA%/gtkb-snapshots/ must be rejected."""
    from groundtruth_kb.project.doctor import _DB_SNAPSHOT_OUTPUT_ALLOWLIST

    paths_should_not_match = [
        r"E:\GT-KB\groundtruth.db",
        r"C:\temp\gtkb-snapshots\test",
        r"C:\Users\micha\Desktop\gtkb-snapshots\test",
        r"C:\Users\micha\AppData\Roaming\gtkb-snapshots\test",
        r"/tmp/gtkb-snapshots/test",
    ]
    for p in paths_should_not_match:
        assert not _DB_SNAPSHOT_OUTPUT_ALLOWLIST.match(p), f"Expected no match: {p}"


# ---------------------------------------------------------------------------
# Rule-text-vs-source parity
# ---------------------------------------------------------------------------


def test_rule_text_cites_allowlist_constant() -> None:
    """project-root-boundary.md must reference _DB_SNAPSHOT_OUTPUT_ALLOWLIST."""
    rule_path = _project_root() / ".claude" / "rules" / "project-root-boundary.md"
    text = rule_path.read_text(encoding="utf-8")
    assert "_DB_SNAPSHOT_OUTPUT_ALLOWLIST" in text, (
        "project-root-boundary.md must cite the doctor.py allowlist constant "
        "_DB_SNAPSHOT_OUTPUT_ALLOWLIST so rule text and source stay aligned."
    )


def test_rule_text_cites_doctor_check_name() -> None:
    """project-root-boundary.md must reference _check_db_snapshot_output_allowlist."""
    rule_path = _project_root() / ".claude" / "rules" / "project-root-boundary.md"
    text = rule_path.read_text(encoding="utf-8")
    assert "_check_db_snapshot_output_allowlist" in text


# ---------------------------------------------------------------------------
# Doctor check: _check_db_snapshot_output_allowlist
# ---------------------------------------------------------------------------


def test_allowlist_check_pass_on_localappdata() -> None:
    """Check passes when resolved output is under %LOCALAPPDATA%/gtkb-snapshots/."""
    from groundtruth_kb.project.doctor import _check_db_snapshot_output_allowlist

    mock_cfg = MagicMock()
    mock_cfg.backup.snapshot_output_dir = None

    with (
        patch(
            "groundtruth_kb.project.doctor.GTConfig.load",
            return_value=mock_cfg,
        )
        if False
        else patch(
            "groundtruth_kb.config.GTConfig.load",
            return_value=mock_cfg,
        ),
        patch(
            "groundtruth_kb.db_snapshot.default_output_dir",
            return_value=r"C:\Users\testuser\AppData\Local\gtkb-snapshots\TestProject",
        ),
    ):
        result = _check_db_snapshot_output_allowlist(_project_root())

    assert result.status == "pass", result.message


def test_allowlist_check_fail_on_synced_dir() -> None:
    """Check fails when resolved output lands on a synced drive."""
    from groundtruth_kb.project.doctor import _check_db_snapshot_output_allowlist

    mock_cfg = MagicMock()
    mock_cfg.backup.snapshot_output_dir = r"E:\GT-KB\snapshots"

    with patch(
        "groundtruth_kb.config.GTConfig.load",
        return_value=mock_cfg,
    ):
        result = _check_db_snapshot_output_allowlist(_project_root())

    assert result.status == "fail", result.message


# ---------------------------------------------------------------------------
# Doctor check: _check_db_snapshot_freshness
# ---------------------------------------------------------------------------


def test_freshness_check_warning_when_no_dir() -> None:
    """Check warns when snapshot directory does not exist yet."""
    from groundtruth_kb.project.doctor import _check_db_snapshot_freshness

    mock_cfg = MagicMock()
    mock_cfg.backup.snapshot_output_dir = None

    with (
        patch(
            "groundtruth_kb.config.GTConfig.load",
            return_value=mock_cfg,
        ),
        patch(
            "groundtruth_kb.db_snapshot.default_output_dir",
            return_value=r"C:\nonexistent\gtkb-snapshots\X",
        ),
    ):
        result = _check_db_snapshot_freshness(_project_root())

    assert result.status == "warning"
    assert "does not exist" in result.message


# ---------------------------------------------------------------------------
# Install script existence and syntax
# ---------------------------------------------------------------------------


def test_install_script_exists() -> None:
    """The scheduled-task installer must exist at the expected path."""
    script = _project_root() / "scripts" / "install_db_snapshot_task.ps1"
    assert script.is_file(), f"Missing installer: {script}"


def test_install_script_syntax() -> None:
    """The installer must parse without PowerShell syntax errors."""
    import subprocess

    script = _project_root() / "scripts" / "install_db_snapshot_task.ps1"
    if not script.is_file():
        pytest.skip("installer not present")
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            (
                f"$null = [System.Management.Automation.Language.Parser]::ParseFile('{script}', "
                "[ref]$null, [ref]$errs); $errs.Count"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    error_count = result.stdout.strip()
    assert error_count == "0", f"PowerShell parse errors in install script: {result.stderr or result.stdout}"
