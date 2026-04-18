# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for canonical-terminology doctor check (SPEC-TERMINOLOGY-DOCTOR-CHECK).

Covers the four profiles per SPEC-TERMINOLOGY-PROFILE-MATRIX:
- local-only (no AGENTS.md; 3 required terms in CLAUDE.md + MEMORY.md)
- dual-agent (5 required terms in CLAUDE.md + AGENTS.md + MEMORY.md + rules)
- dual-agent-webapp (identical to dual-agent for terminology)
- harness-memory (opt-in; skips MEMORY.md content check)

Plus the P1-1 assertion from Codex GO conditions: generated ``AGENTS.md`` names
``MEMORY.md`` (repo-root) and NOT ``memory/MEMORY.md``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.doctor import (
    _check_canonical_terminology,
    _resolve_profile_config,
    run_doctor,
)
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project


def _scaffold(tmp_path: Path, profile: str) -> Path:
    """Scaffold a minimal project for *profile* and return its target path."""
    target = tmp_path / "project"
    options = ScaffoldOptions(
        project_name="Canonical Terminology Test",
        profile=profile,
        owner="Test Owner",
        target_dir=target,
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    return target


# ---------------------------------------------------------------------------
# local-only profile
# ---------------------------------------------------------------------------


def test_doctor_canonical_terminology_local_only(tmp_path: Path) -> None:
    """local-only: check passes on fresh scaffold (3 required terms, no AGENTS.md)."""
    target = _scaffold(tmp_path, "local-only")
    check = _check_canonical_terminology(target, "local-only")
    assert check.status == "pass", f"expected pass, got {check.status}: {check.message}"
    assert "local-only" in check.message
    assert "3 required terms" in check.message
    assert "2 required files" in check.message


def test_doctor_canonical_terminology_local_only_missing_membase_errors(tmp_path: Path) -> None:
    """local-only: removing MemBase from CLAUDE.md triggers ERROR per missing_severity."""
    target = _scaffold(tmp_path, "local-only")
    claude_md = target / "CLAUDE.md"
    content = claude_md.read_text(encoding="utf-8")
    # Strip every occurrence of MemBase (keep file otherwise intact)
    claude_md.write_text(content.replace("MemBase", "GNATS"), encoding="utf-8")
    check = _check_canonical_terminology(target, "local-only")
    assert check.status == "fail"
    assert "MemBase" in check.message


def test_doctor_canonical_terminology_local_only_no_agents_md_check(tmp_path: Path) -> None:
    """local-only: AGENTS.md is NOT in required_files — absence is silent (no false ERROR)."""
    target = _scaffold(tmp_path, "local-only")
    assert not (target / "AGENTS.md").exists()
    check = _check_canonical_terminology(target, "local-only")
    assert check.status == "pass"


# ---------------------------------------------------------------------------
# dual-agent profile
# ---------------------------------------------------------------------------


def test_doctor_canonical_terminology_dual_agent(tmp_path: Path) -> None:
    """dual-agent: check passes on fresh scaffold (5 required terms, 4 required files)."""
    target = _scaffold(tmp_path, "dual-agent")
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "pass", f"expected pass, got {check.status}: {check.message}"
    assert "5 required terms" in check.message
    assert "4 required files" in check.message


def test_doctor_canonical_terminology_dual_agent_missing_prime_builder_errors(
    tmp_path: Path,
) -> None:
    """dual-agent: removing 'Prime Builder' from AGENTS.md triggers ERROR."""
    target = _scaffold(tmp_path, "dual-agent")
    agents_md = target / "AGENTS.md"
    content = agents_md.read_text(encoding="utf-8")
    agents_md.write_text(content.replace("Prime Builder", "Main Actor"), encoding="utf-8")
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "fail"
    assert "Prime Builder" in check.message


def test_dual_agent_scaffold_agents_md_names_memory_md_not_memory_subdir(
    tmp_path: Path,
) -> None:
    """P1-1 Codex GO condition: generated AGENTS.md names MEMORY.md, not memory/MEMORY.md."""
    target = _scaffold(tmp_path, "dual-agent")
    agents_md = target / "AGENTS.md"
    assert agents_md.exists(), "dual-agent profile must create AGENTS.md"
    content = agents_md.read_text(encoding="utf-8")
    assert "memory/MEMORY.md" not in content, (
        "Generated AGENTS.md must NOT reference 'memory/MEMORY.md' — GT-KB places "
        "MEMORY.md at repo root per ADR-0001. Codex GO condition P1-1."
    )
    assert "MEMORY.md" in content, (
        "Generated AGENTS.md must reference root 'MEMORY.md' in the startup checklist."
    )


# ---------------------------------------------------------------------------
# dual-agent-webapp profile
# ---------------------------------------------------------------------------


def test_doctor_canonical_terminology_dual_agent_webapp(tmp_path: Path) -> None:
    """dual-agent-webapp: check passes on fresh scaffold (same matrix as dual-agent via extends)."""
    target = _scaffold(tmp_path, "dual-agent-webapp")
    check = _check_canonical_terminology(target, "dual-agent-webapp")
    assert check.status == "pass", f"expected pass, got {check.status}: {check.message}"
    assert "dual-agent-webapp" in check.message
    # Extends contract: same 5 terms as dual-agent.
    assert "5 required terms" in check.message


# ---------------------------------------------------------------------------
# harness-memory opt-in (MEMORY.md content check skipped)
# ---------------------------------------------------------------------------


def test_doctor_canonical_terminology_harness_memory_skips_memory_md_content(
    tmp_path: Path,
) -> None:
    """harness-memory: MEMORY.md content check is skipped.

    Simulates Agent Red's harness where MEMORY.md is held outside the project
    repo. Under harness-memory, deleting MEMORY.md or removing all canonical
    terms from it MUST still pass because the profile config opts out.
    """
    # harness-memory is a terminology-config-only profile; scaffold on
    # dual-agent then resolve doctor against harness-memory to exercise
    # the opt-out path.
    target = _scaffold(tmp_path, "dual-agent")

    # Remove MEMORY.md entirely to simulate harness placement.
    (target / "MEMORY.md").unlink()

    check = _check_canonical_terminology(target, "harness-memory")
    assert check.status == "pass", (
        f"harness-memory must skip MEMORY.md content check; got "
        f"{check.status}: {check.message}"
    )


# ---------------------------------------------------------------------------
# Config loading and extends resolution
# ---------------------------------------------------------------------------


def test_resolve_profile_config_extends_inheritance(tmp_path: Path) -> None:
    """Config resolver merges extended parent profile into child overrides."""
    target = _scaffold(tmp_path, "dual-agent-webapp")
    import tomllib

    with open(target / ".claude" / "rules" / "canonical-terminology.toml", "rb") as f:
        config = tomllib.load(f)

    # dual-agent-webapp extends dual-agent — the resolved config should
    # inherit all of dual-agent's required_startup_terms.
    effective = _resolve_profile_config(config, "dual-agent-webapp")
    assert effective is not None
    terms = effective.get("required_startup_terms")
    assert isinstance(terms, list)
    assert "MemBase" in terms
    assert "Prime Builder" in terms
    assert "Loyal Opposition" in terms
    assert effective.get("missing_severity") == "ERROR"


def test_missing_config_is_error(tmp_path: Path) -> None:
    """Missing `.claude/rules/canonical-terminology.toml` → ERROR on doctor check."""
    target = _scaffold(tmp_path, "local-only")
    (target / ".claude" / "rules" / "canonical-terminology.toml").unlink()
    check = _check_canonical_terminology(target, "local-only")
    assert check.status == "fail"
    assert "canonical-terminology.toml" in check.message


# ---------------------------------------------------------------------------
# End-to-end via run_doctor
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("profile", ["local-only", "dual-agent", "dual-agent-webapp"])
def test_run_doctor_includes_canonical_terminology_check(tmp_path: Path, profile: str) -> None:
    """Every profile's run_doctor() output includes the canonical-terminology check."""
    target = _scaffold(tmp_path, profile)
    report = run_doctor(target, profile)
    names = {c.name for c in report.checks}
    assert "canonical terminology" in names, f"profile {profile}: missing canonical terminology check"
    # And that check is pass on a fresh scaffold.
    ct = [c for c in report.checks if c.name == "canonical terminology"][0]
    assert ct.status == "pass", (
        f"profile {profile}: canonical terminology check failed on fresh scaffold: {ct.message}"
    )


@pytest.mark.parametrize("profile", ["local-only", "dual-agent", "dual-agent-webapp"])
def test_run_doctor_fresh_scaffold_zero_error(tmp_path: Path, profile: str) -> None:
    """Fresh scaffold produces zero ERROR findings from run_doctor (per bridge -005 §Verification)."""
    target = _scaffold(tmp_path, profile)
    report = run_doctor(target, profile)
    errors = [c for c in report.checks if c.status == "fail"]
    assert not errors, (
        f"profile {profile}: fresh scaffold produced ERROR findings: "
        + "; ".join(f"{c.name}: {c.message}" for c in errors)
    )
