"""Tests for the WI-4356 work-tree strays doctor check."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from groundtruth_kb.hygiene import strays as strays_mod
from groundtruth_kb.project import doctor as doctor_mod


def _report(
    *,
    workspace_stale: int = 0,
    stash_stale: int = 0,
    worktree_stale: int = 0,
    findings: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    payload = {
        "counts": {
            "workspace_stale": workspace_stale,
            "stash_stale": stash_stale,
            "worktree_stale": worktree_stale,
        },
        "workspace_findings": [],
        "stash_findings": [],
        "worktree_findings": [],
    }
    if findings:
        payload.update(findings)
    return payload


def test_work_tree_strays_clean_report_passes(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(strays_mod, "run_strays", lambda _root: _report())

    check = doctor_mod._check_work_tree_strays(tmp_path)
    rendered = doctor_mod.format_doctor_report(doctor_mod.DoctorReport(checks=[check]))
    rendered_json = doctor_mod.format_doctor_report_json(doctor_mod.DoctorReport(checks=[check]))

    assert check.status == "pass"
    assert check.required is False
    assert "no stale workspace, stash, or worktree findings" in check.message
    assert "Work-tree strays" in rendered
    assert rendered_json["checks"][0]["name"] == "work-tree strays"


def test_work_tree_strays_warning_reports_counts_and_age_distribution(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        strays_mod,
        "run_strays",
        lambda _root: _report(
            workspace_stale=1,
            stash_stale=1,
            worktree_stale=1,
            findings={
                "workspace_findings": [{"classification": "stale", "age_hours": 13}],
                "stash_findings": [{"classification": "stale", "age_hours": 25}],
                "worktree_findings": [{"classification": "stale", "age_hours": 48}],
            },
        ),
    )

    check = doctor_mod._check_work_tree_strays(tmp_path)

    assert check.status == "warning"
    assert "3 stale" in check.message
    assert "workspace=1" in check.message
    assert "stash=1" in check.message
    assert "worktree=1" in check.message
    assert "age_hours=min=13.0 avg=28.7 max=48.0" in check.message
    assert "read-only details" in check.message


def test_work_tree_strays_scan_error_is_warning(monkeypatch, tmp_path: Path) -> None:
    def fail(_root: Path) -> dict[str, Any]:
        raise strays_mod.StraysError("git status failed")

    monkeypatch.setattr(strays_mod, "run_strays", fail)

    check = doctor_mod._check_work_tree_strays(tmp_path)

    assert check.status == "warning"
    assert check.required is False
    assert check.found is False
    assert "scan unavailable: git status failed" in check.message


def test_run_doctor_bridge_profile_wires_work_tree_strays_check() -> None:
    source = inspect.getsource(doctor_mod.run_doctor)

    assert "checks.append(_check_work_tree_strays(target))" in source
