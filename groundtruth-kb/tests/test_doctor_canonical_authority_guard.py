# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the canonical-authority drift doctor guard."""

from __future__ import annotations

import inspect
from pathlib import Path

from groundtruth_kb.project import doctor as doctor_mod


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_canonical_authority_guard_passes_clean_authority_carriers(tmp_path: Path) -> None:
    _write(
        tmp_path / "config" / "agent-control" / "system-interface-map.toml",
        'authoritative_source = "memory/MEMORY.md"\n'
        'generated_or_authoritative = "non_authoritative_operational_notepad"\n'
        'read_method = "Inspect memory/MEMORY.md only as non-authoritative working state."\n',
    )
    _write(
        tmp_path / "memory" / "topic.md",
        "# Topic Note\n\nNOT canonical; canonical knowledge lives in MemBase.\n",
    )
    _write(
        tmp_path / ".claude" / "rules" / "carrier.md",
        "# Rule\n\n**Source:** `DCL-CARRIER-001`; `DELIB-PROVENANCE`.\n",
    )

    check = doctor_mod._check_canonical_authority_drift(tmp_path)

    assert check.status == "pass"
    assert "No active config" in check.message


def test_canonical_authority_guard_flags_memory_authority_config(tmp_path: Path) -> None:
    _write(
        tmp_path / "config" / "agent-control" / "bad.toml",
        'authoritative_source = "memory/MEMORY.md"\n',
    )

    check = doctor_mod._check_canonical_authority_drift(tmp_path)

    assert check.status == "fail"
    assert "bad.toml:1" in check.message
    assert "labels memory path as authority" in check.message


def test_canonical_authority_guard_flags_skill_frontmatter_in_memory(tmp_path: Path) -> None:
    _write(
        tmp_path / "memory" / "new-rule.md",
        "---\nname: New rule\ndescription: Use this as an active operating rule.\n---\n\n# New Rule\n",
    )

    check = doctor_mod._check_canonical_authority_drift(tmp_path)

    assert check.status == "fail"
    assert "memory/new-rule.md has skill-style frontmatter" in check.message


def test_canonical_authority_guard_flags_imperative_rule_shaped_memory(tmp_path: Path) -> None:
    _write(
        tmp_path / "memory" / "operating-rule.md",
        "# Operational Note\n\n## Rule\n\nAgents MUST treat this memory note as binding.\n",
    )

    check = doctor_mod._check_canonical_authority_drift(tmp_path)

    assert check.status == "fail"
    assert "memory/operating-rule.md has imperative rule-shaped content" in check.message


def test_canonical_authority_guard_flags_delib_sole_rule_source(tmp_path: Path) -> None:
    _write(
        tmp_path / ".claude" / "rules" / "sole-delib.md",
        "# Rule\n\n**Source:** `DELIB-ONLY-AUTHORITY`.\n",
    )

    check = doctor_mod._check_canonical_authority_drift(tmp_path)

    assert check.status == "fail"
    assert ".claude/rules/sole-delib.md:3" in check.message
    assert "DELIB as sole rule authority" in check.message


def test_run_doctor_dual_agent_wires_canonical_authority_guard() -> None:
    source = inspect.getsource(doctor_mod.run_doctor)

    assert "checks.append(_check_canonical_authority_drift(target))" in source
