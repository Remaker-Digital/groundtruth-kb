"""Tests for WI-4655 Agent Red app-root minimization validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))


def _validate_app_root_minimization(*args, **kwargs):
    from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization

    return validate_app_root_minimization(*args, **kwargs)


def _doctor_agent_red_app_root_check(project_root: Path):
    from groundtruth_kb.project.doctor import _check_agent_red_app_root_minimization

    return _check_agent_red_app_root_minimization(project_root)


def _write_registry(app_root: Path, entries: list[dict[str, str]]) -> None:
    payload = {
        "schema_version": "1.0",
        "application": "Agent_Red",
        "top_level_artifacts": entries,
        "validator_contract": {
            "scan_path": "applications/Agent_Red/",
            "depth": "top-level only",
            "rules": [
                "Every top-level entry must match a registry entry by name+type",
                "Registry entries with bucket=A require non-empty purpose",
                "Registry entries with bucket=B require non-empty tool and justification",
                "Bucket=C and bucket=D are not allowed at app root",
                "Unmatched entries fail the gate",
            ],
            "implementation_status": "test fixture",
        },
    }
    (app_root / ".gtkb-app-isolation.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _registry_file_entry() -> dict[str, str]:
    return {
        "name": ".gtkb-app-isolation.json",
        "type": "FILE",
        "bucket": "B",
        "tool": "GT-KB release-gate scan",
        "justification": "Self-referential registry required by the validator.",
    }


def test_raw_filesystem_validator_passes_when_entries_match(tmp_path):
    app_root = tmp_path / "applications" / "Agent_Red"
    (app_root / "src").mkdir(parents=True)
    (app_root / "CLAUDE.md").write_text("Agent Red instructions\n", encoding="utf-8")
    _write_registry(
        app_root,
        [
            _registry_file_entry(),
            {"name": "src", "type": "DIR", "bucket": "A", "purpose": "Application source code."},
            {
                "name": "CLAUDE.md",
                "type": "FILE",
                "bucket": "B",
                "tool": "Claude Code",
                "justification": "Agent Red working-directory instructions.",
            },
        ],
    )

    result = _validate_app_root_minimization(app_root, project_root=tmp_path, tracked_only=False)

    assert result.ok, result.first_error_message()
    assert {entry.name for entry in result.actual_entries} == {".gtkb-app-isolation.json", "CLAUDE.md", "src"}


def test_raw_filesystem_validator_fails_unregistered_top_level_entry(tmp_path):
    app_root = tmp_path / "applications" / "Agent_Red"
    app_root.mkdir(parents=True)
    (app_root / "EXTRA.md").write_text("unregistered\n", encoding="utf-8")
    _write_registry(app_root, [_registry_file_entry()])

    result = _validate_app_root_minimization(app_root, project_root=tmp_path, tracked_only=False)

    assert not result.ok
    assert {finding.code for finding in result.findings} >= {"unregistered_top_level_artifact"}
    assert "EXTRA.md" in result.first_error_message()


def test_validator_enforces_bucket_metadata_and_forbidden_buckets(tmp_path):
    app_root = tmp_path / "applications" / "Agent_Red"
    (app_root / "docs").mkdir(parents=True)
    (app_root / "tool.json").write_text("{}", encoding="utf-8")
    (app_root / "future").mkdir()
    _write_registry(
        app_root,
        [
            _registry_file_entry(),
            {"name": "docs", "type": "DIR", "bucket": "A"},
            {"name": "tool.json", "type": "FILE", "bucket": "B", "tool": "Example Tool"},
            {"name": "future", "type": "DIR", "bucket": "C", "purpose": "Not yet allowed."},
        ],
    )

    result = _validate_app_root_minimization(app_root, project_root=tmp_path, tracked_only=False)
    codes = {finding.code for finding in result.findings}

    assert not result.ok
    assert "entry_missing_purpose" in codes
    assert "entry_missing_justification" in codes
    assert "entry_forbidden_bucket" in codes


def test_live_agent_red_registry_passes_tracked_app_root():
    result = _validate_app_root_minimization(
        REPO_ROOT / "applications" / "Agent_Red",
        project_root=REPO_ROOT,
        tracked_only=True,
    )

    assert result.ok, result.first_error_message(limit=10)


def test_project_doctor_agent_red_app_root_check_passes():
    check = _doctor_agent_red_app_root_check(REPO_ROOT)

    assert check.status == "pass", check.message
