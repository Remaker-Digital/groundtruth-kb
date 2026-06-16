"""Retired historical-phantom allowlist behavior for wrap_scan_consistency."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import wrap_scan_consistency as w2  # noqa: E402


def _make_project_with_allowlist(tmp_path: Path, allowlist_text: str) -> Path:
    project = tmp_path / "fake_repo"
    bridge_dir = project / "bridge"
    allowlist_dir = project / ".groundtruth" / "wrap-scan"
    bridge_dir.mkdir(parents=True)
    allowlist_dir.mkdir(parents=True)
    (bridge_dir / "missing-status-001.md").write_text("# Heading first\n", encoding="utf-8")
    (allowlist_dir / "historical-phantoms.toml").write_text(allowlist_text, encoding="utf-8")
    return project


def test_absent_allowlist_does_not_affect_status_check(tmp_path: Path) -> None:
    project = tmp_path / "fake_repo"
    bridge_dir = project / "bridge"
    bridge_dir.mkdir(parents=True)
    (bridge_dir / "missing-status-001.md").write_text("# Heading first\n", encoding="utf-8")

    findings = w2.check_bridge_numbered_files_have_status(project)

    assert [finding["check"] for finding in findings] == ["bridge_numbered_file_missing_status"]


def test_retired_allowlist_file_is_not_consulted(tmp_path: Path) -> None:
    project = _make_project_with_allowlist(
        tmp_path,
        "schema_version = 1\nphantoms = []\n",
    )

    findings = w2.check_bridge_numbered_files_have_status(project)

    assert [finding["check"] for finding in findings] == ["bridge_numbered_file_missing_status"]
    assert findings[0]["severity"] == w2.SEVERITY_ERROR


def test_malformed_retired_allowlist_does_not_fail_status_check(tmp_path: Path) -> None:
    project = _make_project_with_allowlist(tmp_path, "this is not valid toml = {[}\n")

    findings = w2.check_bridge_numbered_files_have_status(project)

    assert [finding["check"] for finding in findings] == ["bridge_numbered_file_missing_status"]


def test_run_all_checks_includes_numbered_status_check(tmp_path: Path) -> None:
    project = tmp_path / "fake_repo"
    bridge_dir = project / "bridge"
    bridge_dir.mkdir(parents=True)
    (bridge_dir / "missing-status-001.md").write_text("# Heading first\n", encoding="utf-8")

    findings = w2.run_all_checks(project)

    assert any(finding["check"] == "bridge_numbered_file_missing_status" for finding in findings)
