# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for session-start ORIENT validation and doctor enforcement."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.project import doctor, session_start_orientation as orient


WELL_FORMED_ORIENT = """\
ORIENT S301 @ 16:41Z
  1 bridge:     clear (0 actionable)
  2 branch:     develop@abc1234 (ahead 0)
  3 worktree:   2 modified, 0 untracked
  4 wrap:       DELIB-0820
  5 blockers:   none
  6 refresh:    none
  7 next:       continue bridge queue
"""


def test_orient_block_format_parses_well_formed() -> None:
    result = orient.validate_orient_block(WELL_FORMED_ORIENT)
    assert result.valid is True
    assert result.item_count == 7


def test_orient_block_format_rejects_count_mismatch() -> None:
    short = "\n".join(WELL_FORMED_ORIENT.splitlines()[:6])
    result = orient.validate_orient_block(short)
    assert result.valid is False
    assert "expected 7" in result.reason


def test_orient_block_format_rejects_malformed_header() -> None:
    bad = WELL_FORMED_ORIENT.replace("ORIENT S301 @ 16:41Z", "ORIENT bad header")
    result = orient.validate_orient_block(bad)
    assert result.valid is False


def test_orient_block_requires_structured_unknown_tags() -> None:
    bad = WELL_FORMED_ORIENT.replace("clear (0 actionable)", "UNKNOWN")
    result = orient.validate_orient_block(bad)
    assert result.valid is False
    assert "structured tags" in result.reason


def test_orient_block_accepts_structured_unknown_tags() -> None:
    accepted = WELL_FORMED_ORIENT.replace("clear (0 actionable)", "UNKNOWN:no-remote-access")
    assert orient.validate_orient_block(accepted).valid is True


def _write_transcript(path: Path, assistant_text: str) -> None:
    events = [
        {"type": "user", "message": {"content": "continue"}},
        {"type": "assistant", "message": {"content": assistant_text}},
    ]
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")


def test_doctor_warns_on_transcript_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(tmp_path / "missing"))
    monkeypatch.delenv("CLAUDE_TRANSCRIPT_PATH", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_HASH", raising=False)
    status, message = orient.check_session_wrap_had_orient(tmp_path)
    assert status == "info"
    assert "first-ever session" in message


def test_doctor_errors_on_missing_orient_in_prior_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    transcript_dir = tmp_path / "projects" / "T--demo"
    transcript_dir.mkdir(parents=True)
    _write_transcript(transcript_dir / "session.jsonl", "No orient here")
    monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("CLAUDE_PROJECT_HASH", "T--demo")
    status, message = orient.check_session_wrap_had_orient(tmp_path)
    assert status == "fail"
    assert "without an ORIENT block" in message


def test_doctor_passes_on_well_formed_prior_orient(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    transcript_dir = tmp_path / "projects" / "T--demo"
    transcript_dir.mkdir(parents=True)
    _write_transcript(transcript_dir / "session.jsonl", WELL_FORMED_ORIENT)
    monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("CLAUDE_PROJECT_HASH", "T--demo")
    status, message = orient.check_session_wrap_had_orient(tmp_path)
    assert status == "pass"
    assert "well-formed ORIENT" in message


def test_doctor_check_wiring(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLAUDE_TRANSCRIPT_DIR", str(tmp_path / "missing"))
    check = doctor._check_session_wrap_had_orient(tmp_path)
    assert check.name == "Prior-session ORIENT block"
    assert check.status in {"info", "warning", "pass", "fail"}
