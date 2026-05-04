"""Tests for Sub-slice F: release-metric gate enforcement.

Per bridge/gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04-001.md
GO at -002.

Verifies:
  - 3 doctor checks pass on clean fixtures, fail on synthetic pollution.
  - Release-gate script exits 0 on clean baseline, exits 1 on polluted baseline.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "release_governance_metrics.py"


def _make_clean_fixture(tmp_path: Path) -> Path:
    """Construct a target tree with clean baseline."""
    project = tmp_path / "project"
    (project / "memory").mkdir(parents=True)
    (project / "memory" / "pending-owner-decisions.md").write_text(
        "# Pending Owner Decisions\n\nThis file is owned by .claude/hooks/owner-decision-tracker.py.\n\n---\n\n"
        "## Pending\n\n(none)\n\n## Resolved\n\n(none)\n\n## History\n\n(none)\n",
        encoding="utf-8",
    )
    (project / "bridge").mkdir()
    (project / "bridge" / "INDEX.md").write_text(
        "# Bridge Index\n\n",
        encoding="utf-8",
    )
    # Hook files needed for parser-helper imports
    (project / ".claude" / "hooks").mkdir(parents=True)
    # Symlink/copy the canonical hooks so doctor's importlib calls resolve.
    import shutil
    for hook_name in ("owner-decision-tracker.py", "bridge-compliance-gate.py"):
        src = REPO_ROOT / ".claude" / "hooks" / hook_name
        if src.exists():
            shutil.copy2(src, project / ".claude" / "hooks" / hook_name)
    return project


def _add_prose_pending_entry(target: Path, decision_id: str = "DECISION-9001") -> None:
    pending_path = target / "memory" / "pending-owner-decisions.md"
    text = pending_path.read_text(encoding="utf-8")
    entry = (
        f"- id: {decision_id}\n"
        f"  asked_at: 2026-05-10T08:00:00Z\n"
        f"  question: \"\"\n"
        f"  detected_via: prose:offering_or_choice\n"
        f"  status: pending\n"
        f"  question_hash: deadbeefcafebabe\n"
        f"  notes: \"\"\n"
    )
    new_text = text.replace("## Pending\n\n(none)\n", f"## Pending\n\n{entry}\n")
    pending_path.write_text(new_text, encoding="utf-8")


def _add_non_auq_resolved_entry(target: Path, decision_id: str = "DECISION-9002") -> None:
    pending_path = target / "memory" / "pending-owner-decisions.md"
    text = pending_path.read_text(encoding="utf-8")
    entry = (
        f"- id: {decision_id}\n"
        f"  asked_at: 2026-05-10T08:00:00Z\n"
        f"  question: \"\"\n"
        f"  detected_via: prose:awaiting_input_q\n"
        f"  status: resolved\n"
        f"  question_hash: aaaa1111bbbb2222\n"
        f"  resolved_at: 2026-05-10T08:30:00Z\n"
        f"  notes: \"\"\n"
    )
    new_text = text.replace("## Resolved\n\n(none)\n", f"## Resolved\n\n{entry}\n")
    pending_path.write_text(new_text, encoding="utf-8")


def _add_offending_verified_bridge(target: Path) -> None:
    """Adds a VERIFIED bridge file claiming owner approval but missing the section."""
    bridge_dir = target / "bridge"
    fname = "test-offender-001.md"
    (bridge_dir / fname).write_text(
        "REVISED\n\n"  # Note: NOT a verdict file (verdict files are excluded)
        "# Implementation Proposal\n\n"
        "## Specification Links\n\n- SPEC-X\n\n"
        "This proposal cites Sub-slice B per "
        "bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md "
        "but provides no Owner Decisions / Input section.\n",
        encoding="utf-8",
    )
    index_path = bridge_dir / "INDEX.md"
    index_path.write_text(
        f"# Bridge Index\n\nDocument: test-offender\nVERIFIED: bridge/{fname}\n",
        encoding="utf-8",
    )
    # Touch mtime to be in-window
    import os
    from datetime import datetime
    ts = datetime(2026, 5, 10, 12, 0, 0).timestamp()
    os.utime(bridge_dir / fname, (ts, ts))


def _add_realistic_verified_thread(target: Path) -> None:
    """Adds a realistic VERIFIED thread: VERIFIED line points at LO verdict;
    NEW line points at the Prime report claiming owner approval but missing
    Owner Decisions / Input section. Per Codex -004 F1."""
    bridge_dir = target / "bridge"
    verdict_fname = "realistic-offender-002.md"
    report_fname = "realistic-offender-001.md"
    # LO verdict file (starts with VERIFIED first line — must be SKIPPED by check)
    (bridge_dir / verdict_fname).write_text(
        "VERIFIED\n\n"
        "# Loyal Opposition Verification\n\nLooks fine.\n",
        encoding="utf-8",
    )
    # Prime report (the actual offender — no verdict prefix; claims owner approval; missing section)
    (bridge_dir / report_fname).write_text(
        "NEW\n\n"
        "# Prime Implementation Report\n\n"
        "## Specification Links\n\n- SPEC-X\n\n"
        "This report cites Sub-slice B's AUQ-only rule per "
        "bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md "
        "and asserts owner approval was obtained. But there is no Owner Decisions / Input section.\n",
        encoding="utf-8",
    )
    # INDEX with realistic protocol topology: VERIFIED first, NEW underneath
    index_path = bridge_dir / "INDEX.md"
    index_path.write_text(
        "# Bridge Index\n\n"
        "Document: realistic-offender\n"
        f"VERIFIED: bridge/{verdict_fname}\n"
        f"NEW: bridge/{report_fname}\n",
        encoding="utf-8",
    )
    import os
    from datetime import datetime
    ts = datetime(2026, 5, 10, 12, 0, 0).timestamp()
    os.utime(bridge_dir / verdict_fname, (ts, ts))
    os.utime(bridge_dir / report_fname, (ts, ts))


def _run_doctor_check(target: Path, check_name: str):
    """Import doctor and run a single check function."""
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
    import importlib
    import groundtruth_kb.project.doctor as doctor_module
    importlib.reload(doctor_module)
    fn = getattr(doctor_module, check_name)
    return fn(target)


# ---- Doctor check unit tests ----


def test_check_untriaged_prose_decisions_pass_on_empty_pending(tmp_path):
    target = _make_clean_fixture(tmp_path)
    r = _run_doctor_check(target, "_check_untriaged_prose_decisions")
    assert r.status == "pass", f"Expected pass; got {r.status}: {r.message}"


def test_check_untriaged_prose_decisions_fail_on_prose_pending(tmp_path):
    target = _make_clean_fixture(tmp_path)
    _add_prose_pending_entry(target)
    r = _run_doctor_check(target, "_check_untriaged_prose_decisions")
    assert r.status == "fail", f"Expected fail; got {r.status}: {r.message}"
    assert "DECISION-9001" in r.message


def test_check_auq_coverage_pass_at_100pct(tmp_path):
    """Empty-window edge case: no in-window entries → pass."""
    target = _make_clean_fixture(tmp_path)
    r = _run_doctor_check(target, "_check_auq_coverage")
    assert r.status == "pass", f"Expected pass; got {r.status}: {r.message}"


def test_check_auq_coverage_fail_below_100pct(tmp_path, monkeypatch):
    target = _make_clean_fixture(tmp_path)
    # Add a non-AUQ entry in a generous window
    _add_non_auq_resolved_entry(target)
    monkeypatch.setenv("GTKB_AUQ_METRICS_CUTOFF_DATE", "2026-01-01")
    r = _run_doctor_check(target, "_check_auq_coverage")
    assert r.status == "fail", f"Expected fail; got {r.status}: {r.message}"


def test_check_auq_coverage_pass_when_empty_window(tmp_path, monkeypatch):
    target = _make_clean_fixture(tmp_path)
    monkeypatch.setenv("GTKB_AUQ_METRICS_CUTOFF_DATE", "2099-01-01")
    r = _run_doctor_check(target, "_check_auq_coverage")
    assert r.status == "pass", f"Expected pass; got {r.status}: {r.message}"


def test_check_uncited_owner_input_bridges_pass_when_compliant(tmp_path):
    target = _make_clean_fixture(tmp_path)
    r = _run_doctor_check(target, "_check_uncited_owner_input_bridges")
    assert r.status == "pass", f"Expected pass; got {r.status}: {r.message}"


def test_check_uncited_owner_input_bridges_fail_when_section_missing(tmp_path, monkeypatch):
    target = _make_clean_fixture(tmp_path)
    _add_offending_verified_bridge(target)
    monkeypatch.setenv("GTKB_AUQ_METRICS_CUTOFF_DATE", "2026-01-01")
    r = _run_doctor_check(target, "_check_uncited_owner_input_bridges")
    assert r.status == "fail", f"Expected fail; got {r.status}: {r.message}"
    assert "test-offender-001.md" in r.message


# ---- Release-gate script E2E tests ----


def test_release_gate_script_exits_0_on_clean_baseline(tmp_path, monkeypatch):
    target = _make_clean_fixture(tmp_path)
    monkeypatch.setenv("GTKB_AUQ_METRICS_CUTOFF_DATE", "2099-01-01")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, (
        f"Expected exit 0; got {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS: all 3 release governance metrics clean" in result.stdout


def test_release_gate_script_exits_1_on_polluted_baseline(tmp_path, monkeypatch):
    target = _make_clean_fixture(tmp_path)
    _add_prose_pending_entry(target)
    monkeypatch.setenv("GTKB_AUQ_METRICS_CUTOFF_DATE", "2099-01-01")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 1, (
        f"Expected exit 1; got {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "BLOCK" in result.stderr or "FAIL" in result.stderr


# ---- Codex -004 regression tests ----


def test_check_uncited_owner_input_bridges_fail_on_realistic_verified_thread(tmp_path, monkeypatch):
    """Per Codex -004 F1: VERIFIED thread topology is verdict file at top + Prime
    report below. Check must inspect non-verdict files in VERIFIED threads, not
    only the verdict file itself."""
    target = _make_clean_fixture(tmp_path)
    _add_realistic_verified_thread(target)
    monkeypatch.setenv("GTKB_AUQ_METRICS_CUTOFF_DATE", "2026-01-01")
    r = _run_doctor_check(target, "_check_uncited_owner_input_bridges")
    assert r.status == "fail", (
        f"Realistic verified-thread topology must produce fail; got {r.status}: {r.message}"
    )
    assert "realistic-offender-001.md" in r.message, (
        f"Offender Prime report (realistic-offender-001.md) must be flagged; got {r.message}"
    )


def test_release_gate_script_blocks_on_warning_status(tmp_path, monkeypatch):
    """Per Codex -004 F2: invalid GTKB_AUQ_METRICS_CUTOFF_DATE produces warning
    status for two checks; release script must block (exit 1), not exit 0
    with 'all clean' message."""
    target = _make_clean_fixture(tmp_path)
    monkeypatch.setenv("GTKB_AUQ_METRICS_CUTOFF_DATE", "not-a-date")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 1, (
        f"Expected exit 1 on warning status; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "all 3 release governance metrics clean" not in result.stdout, (
        "Misconfiguration produced warnings but stdout claimed all-clean — false-pass path"
    )
    assert "BLOCK" in result.stderr, "Expected BLOCK message in stderr"
