# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/startup_payload_budget_report.py (WI-4360, Slice A).

Per bridge ``gtkb-startup-payload-budget-report-001.md`` Verification Plan
(Specification-Derived). Each spec/acceptance criterion maps to named tests:

- DCL-SESSION-STARTUP-TOKEN-BUDGET-001 (per-harness byte/token budgets):
  ``test_build_report_by_harness``, ``test_cross_harness_totals``.
- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 (mandatory vs expandable):
  ``test_mandatory_vs_expandable_classification``,
  ``test_unknown_section_flagged_and_defaulted``.
- GOV-SESSION-SELF-INITIALIZATION-001 (deterministic, replayable):
  ``test_determinism_same_input_same_output``, ``test_render_markdown_shape``.
- Contract integrity (gtkb-startup-payload-profile-v1):
  ``test_load_skips_non_contract_json``, ``test_contract_version_constant``.
- Read-only / robustness:
  ``test_empty_profiles_dir_returns_empty_report``, ``test_inputs_not_mutated``.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "startup_payload_budget_report.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("startup_payload_budget_report", _SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before exec: with ``from __future__ import annotations`` the
    # module's frozen dataclasses resolve string annotations via
    # ``sys.modules[cls.__module__].__dict__``; an unregistered path-loaded
    # module would resolve to None and raise during class definition.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def _profile(
    *,
    harness_id: str,
    harness_name: str,
    role_profile: str,
    sections: dict,
) -> dict:
    return {
        "contract_version": mod.CONTRACT_VERSION,
        "generated_at": "2026-06-13T20:00:00Z",
        "harness_id": harness_id,
        "harness_name": harness_name,
        "payload_emitted_at": "2026-06-13T20:00:04Z",
        "profile_path": f".gtkb-state/startup-payload-profiles/last-{harness_name}.json",
        "role_profile": role_profile,
        "sections": sections,
    }


def _section(*, utf8_bytes: int, tokens: int, lines: int, chars: int) -> dict:
    return {
        "utf8_bytes": utf8_bytes,
        "rough_token_estimate": tokens,
        "line_count": lines,
        "character_count": chars,
        "sha256": "0" * 64,
    }


_CLAUDE = _profile(
    harness_id="B",
    harness_name="claude",
    role_profile="prime-builder",
    sections={
        "additionalContext": _section(utf8_bytes=100, tokens=25, lines=5, chars=100),
        "startupDisclosure": _section(utf8_bytes=400, tokens=100, lines=20, chars=398),
    },
)

_CODEX = _profile(
    harness_id="A",
    harness_name="codex",
    role_profile="loyal-opposition",
    sections={
        "additionalContext": _section(utf8_bytes=200, tokens=50, lines=8, chars=200),
        "startupDisclosure": _section(utf8_bytes=800, tokens=200, lines=40, chars=796),
    },
)


# --- DCL-SESSION-STARTUP-TOKEN-BUDGET-001 ---------------------------------


def test_build_report_by_harness():
    report = mod.build_budget_report([_CLAUDE, _CODEX], now="2026-06-13T21:00:00Z")
    # Sorted by harness_name: codex before claude.
    names = [h.harness_name for h in report.harnesses]
    assert names == ["claude", "codex"]

    by_name = {h.harness_name: h for h in report.harnesses}
    claude = by_name["claude"]
    assert claude.harness_id == "B"
    assert claude.role_profile == "prime-builder"
    assert claude.mandatory_bytes == 100
    assert claude.mandatory_tokens == 25
    assert claude.expandable_bytes == 400
    assert claude.expandable_tokens == 100
    assert claude.total_bytes == 500
    assert claude.total_tokens == 125


def test_cross_harness_totals():
    report = mod.build_budget_report([_CLAUDE, _CODEX], now="2026-06-13T21:00:00Z")
    t = report.totals
    assert t.harness_count == 2
    assert t.mandatory_bytes == 300  # 100 + 200
    assert t.mandatory_tokens == 75  # 25 + 50
    assert t.expandable_bytes == 1200  # 400 + 800
    assert t.expandable_tokens == 300  # 100 + 200
    assert t.total_bytes == 1500
    assert t.total_tokens == 375


# --- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 ------------------------


def test_mandatory_vs_expandable_classification():
    assert mod.classify_section("additionalContext") == "mandatory"
    assert mod.classify_section("startupDisclosure") == "expandable"

    report = mod.build_budget_report([_CLAUDE], now="2026-06-13T21:00:00Z")
    sections = {s.name: s for s in report.harnesses[0].sections}
    assert sections["additionalContext"].klass == "mandatory"
    assert sections["startupDisclosure"].klass == "expandable"


def test_unknown_section_flagged_and_defaulted():
    profile = _profile(
        harness_id="C",
        harness_name="future",
        role_profile="prime-builder",
        sections={
            "additionalContext": _section(utf8_bytes=10, tokens=3, lines=1, chars=10),
            "newSection": _section(utf8_bytes=60, tokens=15, lines=2, chars=60),
        },
    )
    # Unknown name defaults to "expandable".
    assert mod.classify_section("newSection") == "expandable"

    report = mod.build_budget_report([profile], now="2026-06-13T21:00:00Z")
    flagged = {(u.harness_name, u.section_name) for u in report.unknown_sections}
    assert ("future", "newSection") in flagged
    # additionalContext is known and must NOT be flagged.
    assert ("future", "additionalContext") not in flagged

    harness = report.harnesses[0]
    assert harness.expandable_bytes == 60  # newSection counted as expandable
    assert harness.mandatory_bytes == 10  # additionalContext


# --- GOV-SESSION-SELF-INITIALIZATION-001 ----------------------------------


def test_determinism_same_input_same_output():
    now = "2026-06-13T21:00:00Z"
    a = mod.render_json(mod.build_budget_report([_CLAUDE, _CODEX], now=now))
    # Reverse input order: sorting by harness_name must normalize it.
    b = mod.render_json(mod.build_budget_report([_CODEX, _CLAUDE], now=now))
    assert a == b

    md_a = mod.render_markdown(mod.build_budget_report([_CLAUDE, _CODEX], now=now))
    md_b = mod.render_markdown(mod.build_budget_report([_CODEX, _CLAUDE], now=now))
    assert md_a == md_b


def test_render_markdown_shape():
    report = mod.build_budget_report([_CLAUDE, _CODEX], now="2026-06-13T21:00:00Z")
    md = mod.render_markdown(report)
    assert "# Startup Payload Budget Report" in md
    assert "gtkb-startup-payload-profile-v1" in md
    # A row per harness + a totals row.
    assert "| claude |" in md
    assert "| codex |" in md
    assert "**TOTAL**" in md
    # Class columns present in the header.
    assert "Mandatory bytes" in md
    assert "Expandable tokens" in md


# --- Contract integrity (gtkb-startup-payload-profile-v1) -----------------


def test_load_skips_non_contract_json(tmp_path: Path):
    good = tmp_path / "last-claude.json"
    good.write_text(json.dumps(_CLAUDE), encoding="utf-8")

    bad_version = tmp_path / "last-old.json"
    bad_version.write_text(
        json.dumps({**_CODEX, "contract_version": "gtkb-startup-payload-profile-v0"}),
        encoding="utf-8",
    )

    not_json = tmp_path / "last-broken.json"
    not_json.write_text("{ this is not json", encoding="utf-8")

    not_dict = tmp_path / "last-list.json"
    not_dict.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    loaded = mod.load_profiles(tmp_path)
    names = [p["harness_name"] for p in loaded]
    assert names == ["claude"]  # only the contract-matching record


def test_contract_version_constant():
    # The module constant must track the producer's emitted contract version.
    live_dir = Path(__file__).resolve().parents[2] / ".gtkb-state" / "startup-payload-profiles"
    live_files = sorted(live_dir.glob("last-*.json")) if live_dir.is_dir() else []
    if not live_files:
        pytest.skip("no live profile files present to cross-check contract version")
    for path in live_files:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(raw, dict) or "contract_version" not in raw:
            continue
        assert raw["contract_version"] == mod.CONTRACT_VERSION, (
            f"{path.name} emits {raw['contract_version']!r} but module CONTRACT_VERSION is {mod.CONTRACT_VERSION!r}"
        )


# --- Read-only / robustness ----------------------------------------------


def test_empty_profiles_dir_returns_empty_report(tmp_path: Path):
    empty = tmp_path / "does-not-exist"
    assert mod.load_profiles(empty) == []

    present_empty = tmp_path / "present"
    present_empty.mkdir()
    assert mod.load_profiles(present_empty) == []

    report = mod.build_budget_report([], now="2026-06-13T21:00:00Z")
    assert report.totals.harness_count == 0
    assert report.harnesses == ()
    assert report.unknown_sections == ()
    # Markdown still renders without crashing.
    md = mod.render_markdown(report)
    assert "# Startup Payload Budget Report" in md


def test_inputs_not_mutated():
    claude_copy = copy.deepcopy(_CLAUDE)
    mod.build_budget_report([claude_copy], now="2026-06-13T21:00:00Z")
    assert claude_copy == _CLAUDE  # input dict unchanged after compute
