#!/usr/bin/env python3
"""Tests for the bridge-only advisory owner-grilling warning lint."""

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
sys.modules[_spec.name] = lint
_spec.loader.exec_module(lint)

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
    status: str = "ADVISORY",
    disposition_heading: str = "## Recommended Prime Builder Disposition",
    gate: str | None = None,
    waiver: str | None = None,
) -> str:
    body = [
        status,
        "",
        "# Loyal Opposition Advisory",
        "",
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


def _write_bridge(
    project_root: Path,
    slug: str,
    text: str,
    *,
    version: int = 1,
) -> Path:
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    path = bridge / f"{slug}-{version:03d}.md"
    path.write_text(text, encoding="utf-8")
    return path


def _write_legacy_dropbox(project_root: Path, name: str, text: str) -> Path:
    dropbox = project_root / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    dropbox.mkdir(parents=True, exist_ok=True)
    path = dropbox / name
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Canonical advisory-shape detection
# ---------------------------------------------------------------------------


def test_canonical_status_is_detected_without_legacy_mode_header() -> None:
    text = _advisory("adopt")
    assert lint.bridge_status(text) == "ADVISORY"
    assert lint.is_advisory_shaped(text, file_name="gtkb-example-001.md") is True


def test_non_advisory_status_is_not_shaped() -> None:
    text = _advisory("adopt", status="NEW")
    result = lint.lint_text(text, rel="bridge/gtkb-example-001.md")
    assert result.shaped is False
    assert result.findings == []


def test_unnumbered_bridge_file_is_not_shaped() -> None:
    result = lint.lint_text(_advisory("adopt"), rel="bridge/gtkb-example.md")
    assert result.shaped is False
    assert result.findings == []


def test_legacy_dropbox_file_is_not_shaped_even_with_advisory_status() -> None:
    result = lint.lint_text(
        _advisory("adopt"),
        rel="independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-legacy.md",
    )
    assert result.shaped is False
    assert result.findings == []


def test_ambiguous_classification_is_not_shaped() -> None:
    text = _advisory("adopt").replace(
        "Recommended disposition: adopt.",
        "We considered adopt but recommend reject.",
    )
    result = lint.lint_text(text, rel="bridge/gtkb-example-001.md")
    assert result.shaped is False
    assert lint.extract_classification(text) is None


# ---------------------------------------------------------------------------
# Classification extraction and gate behavior
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("classification", list(lint.CLASSIFICATIONS))
def test_each_classification_extracted(classification: str) -> None:
    assert lint.extract_classification(_advisory(classification)) == classification


def test_classification_under_disposition_heading_variant() -> None:
    text = _advisory("monitor", disposition_heading="## Classification")
    assert lint.extract_classification(text) == "monitor"


@pytest.mark.parametrize("classification", ["adopt", "adapt"])
def test_gate_required_missing_warns(classification: str) -> None:
    result = lint.lint_text(_advisory(classification), rel="bridge/gtkb-example-001.md")
    assert result.shaped is True
    assert [finding.code for finding in result.findings] == ["gate_missing"]
    assert result.findings[0].level == "warning"


@pytest.mark.parametrize("classification", ["adopt", "adapt"])
def test_gate_named_subsections_passes(classification: str) -> None:
    result = lint.lint_text(
        _advisory(classification, gate=_COMPLETE_GATE),
        rel="bridge/gtkb-example-001.md",
    )
    assert result.shaped is True
    assert result.findings == []


def test_gate_numbered_list_passes() -> None:
    gate = (
        "## Required Prime Builder Owner-Grilling Gate\n"
        "1. Implementation implied: yes.\n"
        "2. Grill the owner about scope.\n"
        "3. Durable decision: approve rule home.\n"
    )
    result = lint.lint_text(_advisory("adopt", gate=gate), rel="bridge/gtkb-example-001.md")
    assert result.findings == []


def test_gate_present_but_insufficient_content_warns() -> None:
    gate = "## Required Prime Builder Owner-Grilling Gate\n- Only one enumeration here.\n"
    result = lint.lint_text(_advisory("adapt", gate=gate), rel="bridge/gtkb-example-001.md")
    assert [finding.code for finding in result.findings] == ["gate_content_insufficient"]


def test_count_gate_enumerations_complete() -> None:
    assert lint.count_gate_enumerations(_COMPLETE_GATE) >= lint.MIN_GATE_ENUMERATIONS


@pytest.mark.parametrize("classification", ["reject", "defer", "monitor"])
def test_terminal_classifications_need_no_gate(classification: str) -> None:
    result = lint.lint_text(_advisory(classification), rel="bridge/gtkb-example-001.md")
    assert result.shaped is True
    assert result.findings == []


# ---------------------------------------------------------------------------
# Waiver behavior
# ---------------------------------------------------------------------------


def test_waiver_suppresses_gate_warning() -> None:
    text = _advisory("adopt", waiver="Owner pre-approved scope in DELIB-9999.")
    result = lint.lint_text(text, rel="bridge/gtkb-example-001.md")
    assert result.findings == []
    assert result.waiver == "Owner pre-approved scope in DELIB-9999."
    assert result.classification == "adopt"


def test_waiver_recorded_to_ledger(tmp_path: Path) -> None:
    path = _write_bridge(
        tmp_path,
        "gtkb-waiver",
        _advisory("adapt", waiver="Bounded experiment; gate deferred."),
    )
    lint.lint_paths([path], project_root=tmp_path)
    ledger = tmp_path / lint.WAIVER_LOG_RELATIVE
    assert ledger.is_file()
    record = json.loads(ledger.read_text(encoding="utf-8").strip())
    assert record["classification"] == "adapt"
    assert record["reason"] == "Bounded experiment; gate deferred."
    assert record["file"].endswith("bridge/gtkb-waiver-001.md")


# ---------------------------------------------------------------------------
# Discovery and fail-open behavior
# ---------------------------------------------------------------------------


def test_discovery_returns_only_latest_live_bridge_advisories(tmp_path: Path) -> None:
    _write_bridge(tmp_path, "gtkb-live", _advisory("monitor"))
    _write_bridge(tmp_path, "gtkb-superseded", _advisory("adopt"))
    _write_bridge(tmp_path, "gtkb-superseded", _advisory("adopt", status="NEW"), version=2)
    (tmp_path / "bridge" / "README.md").write_text("not an advisory", encoding="utf-8")
    _write_legacy_dropbox(tmp_path, "INSIGHTS-legacy.md", _advisory("adapt"))

    found = lint.discover_advisory_files(tmp_path)

    assert [path.name for path in found] == ["gtkb-live-001.md"]


def test_explicit_legacy_dropbox_path_is_rejected(tmp_path: Path) -> None:
    path = _write_legacy_dropbox(tmp_path, "INSIGHTS-legacy.md", _advisory("adopt"))
    result = lint.lint_file(path, project_root=tmp_path)
    assert result.shaped is False
    assert result.findings == []


def test_lint_file_unreadable_is_fail_open(tmp_path: Path) -> None:
    missing = tmp_path / "bridge" / "gtkb-missing-001.md"
    result = lint.lint_file(missing, project_root=tmp_path)
    assert result.shaped is False
    assert result.findings == []


# ---------------------------------------------------------------------------
# CLI / Stop-hook warning-only behavior
# ---------------------------------------------------------------------------


def test_main_returns_zero_even_with_warnings(tmp_path: Path) -> None:
    _write_bridge(tmp_path, "gtkb-warning", _advisory("adopt"))
    assert lint.main(["--project-root", str(tmp_path)]) == 0


def test_main_json_output_reports_warning(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_bridge(tmp_path, "gtkb-json-warning", _advisory("adapt"))
    assert lint.main(["--project-root", str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["advisory_files"] == 1
    assert payload["warnings"] == 1
    assert payload["findings"][0]["code"] == "gate_missing"


def test_stop_hook_emits_empty_json_and_exits_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_bridge(tmp_path, "gtkb-stop-warning", _advisory("adopt"))
    monkeypatch.setattr("sys.stdin", io.StringIO('{"hook":"Stop"}'))
    assert lint.main(["--stop-hook", "--project-root", str(tmp_path)]) == 0
    assert capsys.readouterr().out == "{}"


def test_stop_hook_fail_open_on_bad_project_root(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert lint.main(["--stop-hook", "--project-root", str(Path("does") / "not" / "exist")]) == 0
    assert capsys.readouterr().out == "{}"
