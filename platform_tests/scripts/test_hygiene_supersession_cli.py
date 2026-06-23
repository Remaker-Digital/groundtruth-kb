"""Spec-derived tests for WI-4693 ``gt hygiene supersession-scan``.

The scanner is advisory and read-only. It detects live-file supersession,
retirement, withdrawal, and obsolescence signals while preserving audit-history
locations by default.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.hygiene import (
    SupersessionFinding,
    SupersessionScanResult,
    emit_supersession_json,
    emit_supersession_markdown,
    run_supersession_scan,
    scan_supersession_file,
    walk_live_files,
)


def test_scan_supersession_file_detects_live_marker(tmp_path: Path) -> None:
    target = tmp_path / "live-plan.md"
    target.write_text("Current note\nThis runbook is superseded by docs/new-runbook.md.\n", encoding="utf-8")

    findings = scan_supersession_file(target, tmp_path)

    assert len(findings) == 1
    assert findings[0].marker_class == "supersession"
    assert findings[0].file == "live-plan.md"
    assert findings[0].line == 2
    assert "superseded by" in findings[0].matched_excerpt


def test_run_supersession_scan_reports_live_files_but_preserves_bridge_history(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("This checklist is deprecated.\n", encoding="utf-8")
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "old-thread-001.md").write_text("GO\n\nThis proposal was retired by later work.\n", encoding="utf-8")

    result = run_supersession_scan(tmp_path)

    assert result.finding_count == 1
    assert result.findings[0].file == "notes.md"
    assert result.audit_history_preserved is True


def test_run_supersession_scan_can_include_audit_history_when_explicit(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "old-thread-001.md").write_text("GO\n\nThis proposal was retired by later work.\n", encoding="utf-8")

    result = run_supersession_scan(tmp_path, preserve_audit_history=False)

    assert result.finding_count == 1
    assert result.findings[0].file == "bridge/old-thread-001.md"
    assert result.audit_history_preserved is False


def test_walk_live_files_prunes_state_and_cache_dirs(tmp_path: Path) -> None:
    (tmp_path / "live.md").write_text("obsolete\n", encoding="utf-8")
    state_dir = tmp_path / ".gtkb-state"
    state_dir.mkdir()
    (state_dir / "state.md").write_text("obsolete\n", encoding="utf-8")
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "cache.md").write_text("obsolete\n", encoding="utf-8")

    files = {path.relative_to(tmp_path).as_posix() for path in walk_live_files(tmp_path)}

    assert files == {"live.md"}


def _result(findings: tuple[SupersessionFinding, ...]) -> SupersessionScanResult:
    return SupersessionScanResult(
        run_id="20260101T000000Z",
        generated_at="2026-01-01T00:00:00.000000Z",
        root="/repo",
        files_scanned=1,
        findings=findings,
    )


def _finding() -> SupersessionFinding:
    return SupersessionFinding(
        marker_id="obsolete-artifact",
        marker_class="obsolescence",
        classification="candidate_live_obsolescence_signal",
        file="live.md",
        line=1,
        matched_excerpt="obsolete",
        remediation_hint="verify before cleanup",
    )


def test_emit_supersession_json_schema(tmp_path: Path) -> None:
    out = tmp_path / "findings.json"
    emit_supersession_json(_result((_finding(),)), out)

    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert payload["finding_count"] == 1
    assert payload["audit_history_preserved"] is True
    assert payload["findings"][0]["marker_class"] == "obsolescence"


def test_emit_supersession_markdown_groups_by_marker_class(tmp_path: Path) -> None:
    out = tmp_path / "summary.md"
    emit_supersession_markdown(_result((_finding(),)), out)

    text = out.read_text(encoding="utf-8")

    assert "## obsolescence (1)" in text
    assert "`live.md:1`" in text


def test_supersession_scan_is_read_only_against_sources(tmp_path: Path) -> None:
    live = tmp_path / "live.md"
    live.write_text("This document is withdrawn.\n", encoding="utf-8")
    before_paths = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")}
    before_text = live.read_text(encoding="utf-8")

    result = run_supersession_scan(tmp_path)

    after_paths = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")}
    assert result.finding_count == 1
    assert after_paths == before_paths
    assert live.read_text(encoding="utf-8") == before_text


def test_cli_help_lists_supersession_scan() -> None:
    result = CliRunner().invoke(main, ["hygiene", "--help"])

    assert result.exit_code == 0
    assert "supersession-scan" in result.output


def test_cli_supersession_scan_writes_json_only(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "live.md").write_text("This file is no longer authoritative.\n", encoding="utf-8")
    out = tmp_path / "out"

    result = CliRunner().invoke(
        main,
        ["hygiene", "supersession-scan", "--root", str(root), "--output", str(out), "--format", "json"],
    )

    assert result.exit_code == 0, result.output
    assert (out / "findings.json").exists()
    assert not (out / "summary.md").exists()
    payload = json.loads((out / "findings.json").read_text(encoding="utf-8"))
    assert payload["finding_count"] == 1


def test_cli_supersession_scan_fail_on_findings_exits_two(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "live.md").write_text("This file is deprecated.\n", encoding="utf-8")

    result = CliRunner().invoke(
        main,
        ["hygiene", "supersession-scan", "--root", str(root), "--fail-on-findings", "--format", "json"],
    )

    assert result.exit_code == 2
