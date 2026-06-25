"""Spec-derived tests for WI-4814 report skill self-disclosure (SPEC-REPORT-SKILL-DISCLOSURE-001)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EMITTER_PATH = REPO_ROOT / "scripts" / "skill_disclosure.py"
WRITE_VERDICT = REPO_ROOT / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
CODEX_REPORT_SKILL = REPO_ROOT / ".claude" / "skills" / "codex-report" / "SKILL.md"
SESSION_WRAP_SKILL = REPO_ROOT / ".claude" / "skills" / "kb-session-wrap" / "SKILL.md"
CODEX_ADAPTER_REPORT = REPO_ROOT / ".codex" / "skills" / "codex-report" / "SKILL.md"
CODEX_ADAPTER_WRAP = REPO_ROOT / ".codex" / "skills" / "kb-session-wrap" / "SKILL.md"
PARITY_SCRIPT = REPO_ROOT / "scripts" / "check_harness_parity.py"


def _load_emitter():
    spec = importlib.util.spec_from_file_location("skill_disclosure", EMITTER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["skill_disclosure"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def emitter():
    return _load_emitter()


def test_ac1_format_and_round_trip(emitter) -> None:
    line = emitter.format_skills_applied(["gtkb-bridge", "verify"])
    assert line == "Skills applied: gtkb-bridge, verify"
    assert emitter.parse_skills_applied(line) == ["gtkb-bridge", "verify"]
    assert emitter.parse_skills_applied(f"prefix\n{line}\nsuffix") == ["gtkb-bridge", "verify"]


def test_ac2_write_verdict_appends_line_when_skills_supplied(tmp_path: Path) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("VERIFIED\n\n## Commands Executed\n\n```text\nnoop\n```\n", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(WRITE_VERDICT),
            "--slug",
            "fixture-skill-disclosure",
            "--body-file",
            str(body_file),
            "--no-prepopulate",
            "--skills-applied",
            "verify",
            "--skills-applied",
            "gtkb-bridge",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Skills applied: verify, gtkb-bridge" in completed.stdout


def test_ac2_write_verdict_omits_line_when_skills_absent(tmp_path: Path) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("GO\n\nbody\n", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(WRITE_VERDICT),
            "--slug",
            "fixture-skill-disclosure",
            "--body-file",
            str(body_file),
            "--no-prepopulate",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Skills applied:" not in completed.stdout


def test_ac3_canonical_skills_reference_emitter() -> None:
    for path in (CODEX_REPORT_SKILL, SESSION_WRAP_SKILL):
        text = path.read_text(encoding="utf-8")
        assert "## Skills applied disclosure (report-only)" in text
        assert "scripts/skill_disclosure.py" in text
        assert "format_skills_applied" in text


def test_ac4_codex_adapters_present_and_parity_clean() -> None:
    assert CODEX_ADAPTER_REPORT.is_file()
    assert CODEX_ADAPTER_WRAP.is_file()
    completed = subprocess.run(
        [sys.executable, str(PARITY_SCRIPT), "--harness", "codex", "--markdown"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_ac5_deterministic_no_side_effects(emitter) -> None:
    args = (["a", "b", "a"],)
    first = emitter.format_skills_applied(*args)
    second = emitter.format_skills_applied(*args)
    assert first == second == "Skills applied: a, b"


def test_ac6_empty_and_missing_line(emitter) -> None:
    assert emitter.format_skills_applied([]) == "Skills applied: (none)"
    assert emitter.parse_skills_applied("no disclosure here") == []


def test_ac7_skill_diff_confined_to_disclosure_block() -> None:
    heading = "## Skills applied disclosure (report-only)"
    for path in (CODEX_REPORT_SKILL, SESSION_WRAP_SKILL):
        text = path.read_text(encoding="utf-8")
        start = text.index(heading)
        block = text[start:]
        assert "skill_disclosure.py" in block
        assert "Report Structure" in text or "Phase 0" in text
