#!/usr/bin/env python3
"""Tests for scripts/advisory_grilling_gate_lint.py (Slice 3, WI-3446).

Exercises the DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 contract: advisory-shape
detection, the five classifications, adopt/adapt gate presence + content, the
non-advisory false-positive guards, the waiver path (suppression + ledger), and
the warning-phase / fail-open CLI and Stop-hook behavior.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "advisory_grilling_gate_lint.py"
_spec = importlib.util.spec_from_file_location("advisory_grilling_gate_lint", _SCRIPT)
assert _spec is not None and _spec.loader is not None
lint = importlib.util.module_from_spec(_spec)
# Register before exec so @dataclass can resolve the module (Python 3.14).
sys.modules[_spec.name] = lint
_spec.loader.exec_module(lint)


# ---------------------------------------------------------------------------
# Fixtures / builders
# ---------------------------------------------------------------------------

_COMPLETE_GATE = """\
## Required Prime Builder Owner-Grilling Gate

### Implementation implied
Yes - adopting the pattern requires new scripts and a hook.

### Grill-the-owner questions
1. What is the canonical rule home?
2. What are the failure modes?

### Required durable owner decisions
- Approve the rule-home choice.
- Approve the hook surface.
"""


def _advisory(
    classification: str,
    *,
    mode: str = "Mode: advisory report",
    disposition_heading: str = "## Recommended Prime Builder Disposition",
    gate: str | None = None,
    waiver: str | None = None,
) -> str:
    body = [
        "# Loyal Opposition Advisory",
        "",
        mode,
        "Specs: SPEC-1",
        "",
        "## Summary",
        "Peer-system investigation.",
        "",
        disposition_heading,
        "",
        f"Recommended disposition: {classification}.",
    ]
    if waiver is not None:
        body.append(f"Grilling-gate waiver: {waiver}")
    body.append("")
    if gate is not None:
        body.append(gate)
    return "\n".join(body) + "\n"


def _write(tmp_path: Path, name: str, text: str) -> Path:
    dropbox = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    dropbox.mkdir(parents=True, exist_ok=True)
    path = dropbox / name
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Advisory-shape detection
# ---------------------------------------------------------------------------


def test_mode_header_report_variant_detected() -> None:
    assert lint.has_mode_header("# Title\nMode: advisory report\n")


def test_mode_header_short_variant_detected() -> None:
    assert lint.has_mode_header("Mode: advisory\n")


def test_mode_header_case_insensitive() -> None:
    assert lint.has_mode_header("Mode: Advisory Report\n")


def test_mode_header_only_in_first_20_lines() -> None:
    text = "\n".join(["x"] * 25 + ["Mode: advisory report"]) + "\n"
    assert not lint.has_mode_header(text)


def test_non_advisory_no_mode_header_is_not_shaped() -> None:
    text = _advisory("adopt").replace("Mode: advisory report\n", "")
    result = lint.lint_text(text, rel="INSIGHTS-x.md")
    assert result.shaped is False
    assert result.findings == []


def test_wrong_filename_is_not_shaped() -> None:
    # Has a perfectly shaped adopt advisory missing the gate, but the filename is
    # not INSIGHTS-*.md, so the lint must not flag it (false-positive guard).
    text = _advisory("adopt")
    result = lint.lint_text(text, rel="NOTES-2026.md")
    assert result.shaped is False
    assert result.findings == []


def test_ambiguous_classification_is_not_shaped() -> None:
    text = _advisory("adopt").replace(
        "Recommended disposition: adopt.",
        "We considered adopt but recommend reject.",
    )
    result = lint.lint_text(text, rel="INSIGHTS-x.md")
    assert result.shaped is False
    assert lint.extract_classification(text) is None


# ---------------------------------------------------------------------------
# Classification extraction (all five)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("classification", list(lint.CLASSIFICATIONS))
def test_each_classification_extracted(classification: str) -> None:
    text = _advisory(classification)
    assert lint.extract_classification(text) == classification


def test_classification_under_disposition_heading_variant() -> None:
    text = _advisory("monitor", disposition_heading="## Classification")
    assert lint.extract_classification(text) == "monitor"


# ---------------------------------------------------------------------------
# adopt / adapt gate behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("classification", ["adopt", "adapt"])
def test_gate_required_missing_warns(classification: str) -> None:
    result = lint.lint_text(_advisory(classification), rel="INSIGHTS-x.md")
    assert result.shaped is True
    assert [f.code for f in result.findings] == ["gate_missing"]
    assert result.findings[0].level == "warning"


@pytest.mark.parametrize("classification", ["adopt", "adapt"])
def test_gate_named_subsections_passes(classification: str) -> None:
    result = lint.lint_text(_advisory(classification, gate=_COMPLETE_GATE), rel="INSIGHTS-x.md")
    assert result.shaped is True
    assert result.findings == []


def test_gate_numbered_list_passes() -> None:
    gate = (
        "## Required Prime Builder Owner-Grilling Gate\n"
        "1. Implementation implied: yes.\n"
        "2. Grill the owner about scope.\n"
        "3. Durable decision: approve rule home.\n"
    )
    result = lint.lint_text(_advisory("adopt", gate=gate), rel="INSIGHTS-x.md")
    assert result.findings == []


def test_gate_present_but_insufficient_content_warns() -> None:
    gate = "## Required Prime Builder Owner-Grilling Gate\n- Only one enumeration here.\n"
    result = lint.lint_text(_advisory("adapt", gate=gate), rel="INSIGHTS-x.md")
    assert [f.code for f in result.findings] == ["gate_content_insufficient"]


def test_count_gate_enumerations_complete() -> None:
    assert lint.count_gate_enumerations(_COMPLETE_GATE) >= lint.MIN_GATE_ENUMERATIONS


# ---------------------------------------------------------------------------
# reject / defer / monitor require no gate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("classification", ["reject", "defer", "monitor"])
def test_terminal_classifications_need_no_gate(classification: str) -> None:
    result = lint.lint_text(_advisory(classification), rel="INSIGHTS-x.md")
    assert result.shaped is True
    assert result.findings == []


# ---------------------------------------------------------------------------
# Waiver behaviour
# ---------------------------------------------------------------------------


def test_waiver_suppresses_gate_warning() -> None:
    text = _advisory("adopt", waiver="Owner pre-approved scope in DELIB-9999.")
    result = lint.lint_text(text, rel="INSIGHTS-x.md")
    assert result.findings == []
    assert result.waiver == "Owner pre-approved scope in DELIB-9999."
    # Classification must still be extracted despite the waiver line.
    assert result.classification == "adopt"


def test_waiver_recorded_to_ledger(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "INSIGHTS-2026-06-13-waiver.md",
        _advisory("adapt", waiver="Bounded experiment; gate deferred."),
    )
    lint.lint_paths([path], project_root=tmp_path)
    ledger = tmp_path / lint.WAIVER_LOG_RELATIVE
    assert ledger.is_file()
    record = json.loads(ledger.read_text(encoding="utf-8").strip())
    assert record["classification"] == "adapt"
    assert record["reason"] == "Bounded experiment; gate deferred."
    assert record["file"].endswith("INSIGHTS-2026-06-13-waiver.md")


# ---------------------------------------------------------------------------
# Discovery + file IO fail-open
# ---------------------------------------------------------------------------


def test_discover_finds_dropbox_files(tmp_path: Path) -> None:
    _write(tmp_path, "INSIGHTS-2026-06-13-a.md", _advisory("monitor"))
    _write(tmp_path, "INSIGHTS-2026-06-13-b.md", _advisory("reject"))
    (tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "README.md").write_text(
        "not an advisory", encoding="utf-8"
    )
    found = lint.discover_advisory_files(tmp_path)
    assert len(found) == 2
    assert all(p.name.startswith("INSIGHTS-") for p in found)


def test_lint_file_unreadable_is_fail_open(tmp_path: Path) -> None:
    missing = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "INSIGHTS-missing.md"
    result = lint.lint_file(missing, project_root=tmp_path)
    assert result.shaped is False
    assert result.findings == []


# ---------------------------------------------------------------------------
# CLI / Stop-hook fail-open (warning-only)
# ---------------------------------------------------------------------------


def test_main_returns_zero_even_with_warnings(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write(tmp_path, "INSIGHTS-2026-06-13-c.md", _advisory("adopt"))  # missing gate -> warning
    rc = lint.main(["--project-root", str(tmp_path)])
    assert rc == 0  # Phase 1 never blocks.


def test_main_json_output_reports_warning(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write(tmp_path, "INSIGHTS-2026-06-13-d.md", _advisory("adapt"))  # missing gate
    rc = lint.main(["--project-root", str(tmp_path), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["advisory_files"] == 1
    assert payload["warnings"] == 1
    assert payload["findings"][0]["code"] == "gate_missing"


def test_stop_hook_emits_empty_json_and_exits_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write(tmp_path, "INSIGHTS-2026-06-13-e.md", _advisory("adopt"))  # missing gate
    monkeypatch.setattr("sys.stdin", io.StringIO('{"hook":"Stop"}'))
    rc = lint.main(["--stop-hook", "--project-root", str(tmp_path)])
    assert rc == 0
    assert capsys.readouterr().out == "{}"


def test_stop_hook_fail_open_on_bad_project_root(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    rc = lint.main(["--stop-hook", "--project-root", str(Path("does") / "not" / "exist")])
    assert rc == 0
    assert capsys.readouterr().out == "{}"
