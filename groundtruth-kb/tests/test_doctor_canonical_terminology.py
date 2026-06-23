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
    assert "MEMORY.md" in content, "Generated AGENTS.md must reference root 'MEMORY.md' in the startup checklist."


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
        f"harness-memory must skip MEMORY.md content check; got {check.status}: {check.message}"
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
    assert ct.status == "pass", f"profile {profile}: canonical terminology check failed on fresh scaffold: {ct.message}"


@pytest.mark.parametrize("profile", ["local-only", "dual-agent", "dual-agent-webapp"])
def test_run_doctor_fresh_scaffold_zero_error(tmp_path: Path, profile: str) -> None:
    """Fresh scaffold produces zero ERROR findings from run_doctor.

    Per bridge -005 §Verification. Scoped to non-isolation checks: GTKB-ISOLATION-017
    Slice 1 added ``isolation:*`` checks that measure post-isolation invariants (Phase 9
    §4 lines 199-228), which a pre-isolation fresh scaffold legitimately does not yet
    satisfy (e.g., writable product hook paths). Isolation-check behavior is asserted
    separately in tests/test_doctor_isolation.py.
    """
    target = _scaffold(tmp_path, profile)
    report = run_doctor(target, profile)
    errors = [c for c in report.checks if c.status == "fail" and c.required and not c.name.startswith("isolation:")]
    assert not errors, f"profile {profile}: fresh scaffold produced ERROR findings: " + "; ".join(
        f"{c.name}: {c.message}" for c in errors
    )


# ---------------------------------------------------------------------------
# GTKB-GOV-TERM-PRIMER-STARTUP Slice 1 (S327, 2026-05-02): primer-content
# coverage contract (`required_primer_terms` evaluated against the primer
# file, distinct from `required_startup_terms` evaluated against required_files).
# Per Codex `gtkb-gov-term-primer-startup-2026-05-02-004.md` F1 option 1.
# ---------------------------------------------------------------------------


# Adopter-template required_primer_terms covers 21 generic terms (per S327 + smoke-test
# leakage rule). "Agent Red" is GT-KB-checkout-only and added post-template-render to
# the GT-KB self-install (`.claude/rules/canonical-terminology.{md,toml}`); it does NOT
# appear in adopter scaffolds.
_TEMPLATE_REQUIRED_21_TERMS = [
    "MemBase",
    "Deliberation Archive",
    "MEMORY.md",
    "Prime Builder",
    "Loyal Opposition",
    "GT-KB",
    "GroundTruth-KB",
    "GTKB",
    "platform",
    "application",
    "hosted application",
    "adopter",
    "project",
    "work item",
    "backlog",
    "specification",
    "requirement",
    "implementation proposal",
    "implementation report",
    "verification",
    "dashboard",
    "bridge",
]


@pytest.mark.parametrize("profile", ["local-only", "dual-agent", "dual-agent-webapp", "harness-memory"])
def test_required_primer_terms_cover_21_template_minimum(tmp_path: Path, profile: str) -> None:
    """T2 (template): every profile in the canonical-terminology.toml TEMPLATE has
    `required_primer_terms` covering the 21 generic owner-required terms verbatim
    per S327 directive. "Agent Red" is intentionally NOT in the template (smoke
    test enforces no Agent Red leakage in adopter scaffolds); it lives only in
    the GT-KB checkout self-install.
    """
    import tomllib

    toml_path = Path(__file__).resolve().parents[1] / "templates" / "rules" / "canonical-terminology.toml"
    config = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    profile_cfg = _resolve_profile_config(config, profile)
    assert profile_cfg is not None, f"profile {profile} not configured"
    primer_terms = profile_cfg.get("required_primer_terms", [])
    assert isinstance(primer_terms, list), f"profile {profile}: required_primer_terms must be a list"
    missing = [t for t in _TEMPLATE_REQUIRED_21_TERMS if t not in primer_terms]
    assert not missing, (
        f"profile {profile}: required_primer_terms missing {len(missing)} owner-required term(s): {missing}"
    )
    # Inverse check: "Agent Red" must NOT be in the adopter template.
    assert "Agent Red" not in primer_terms, (
        f"profile {profile}: 'Agent Red' must not appear in adopter template (GT-KB-self-install only)"
    )


def test_doctor_passes_when_primer_contains_all_required_primer_terms(tmp_path: Path) -> None:
    """T5: fresh dual-agent scaffold passes the canonical-terminology check
    on both contracts (required_startup_terms in required_files AND
    required_primer_terms in primer file).
    """
    target = _scaffold(tmp_path, "dual-agent")
    primer = target / ".claude" / "rules" / "canonical-terminology.md"
    assert primer.exists(), "scaffold must install primer file at .claude/rules/canonical-terminology.md"
    primer_text = primer.read_text(encoding="utf-8")
    for term in _TEMPLATE_REQUIRED_21_TERMS:
        assert term in primer_text, f"primer missing owner-required term {term!r}"
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "pass", f"expected pass, got {check.status}: {check.message}"


def test_doctor_fails_when_primer_missing_a_required_term(tmp_path: Path) -> None:
    """T6: removing a primer-required term from the primer file causes the
    canonical-terminology check to FAIL with primer_missing_severity (ERROR).
    """
    target = _scaffold(tmp_path, "dual-agent")
    primer = target / ".claude" / "rules" / "canonical-terminology.md"
    text = primer.read_text(encoding="utf-8")
    # Strip every occurrence of "GTKB" (a primer-required term that's not in
    # required_startup_terms; ensures the failure is attributable to the new
    # primer-content contract, not the existing startup-term contract).
    primer.write_text(text.replace("GTKB", "REDACTED"), encoding="utf-8")
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "fail", f"expected fail, got {check.status}: {check.message}"
    assert "GTKB" in check.message, f"failure message should cite the missing primer term; got: {check.message}"
    assert "primer term" in check.message, (
        f"failure message should distinguish primer-term failures from startup-term failures; got: {check.message}"
    )


def test_doctor_does_not_force_22_terms_into_startup_files(tmp_path: Path) -> None:
    """T6b (Codex `-004.md` F1 acceptance): the failure mode being avoided.
    Removing all primer-only terms (those NOT in required_startup_terms) from
    CLAUDE.md must NOT cause the doctor to fail. Existing required_startup_terms
    semantics preserved.
    """
    target = _scaffold(tmp_path, "dual-agent")
    claude_md = target / "CLAUDE.md"
    text = claude_md.read_text(encoding="utf-8")
    # Strip primer-only terms (NOT in dual-agent required_startup_terms).
    primer_only = [
        "GT-KB",
        "GroundTruth-KB",
        "GTKB",
        "platform",
        "application",
        "hosted application",
        "adopter",
        "project",
        "work item",
        "backlog",
        "specification",
        "requirement",
        "implementation proposal",
        "implementation report",
        "verification",
        "dashboard",
        "bridge",
    ]
    for term in primer_only:
        text = text.replace(term, "REDACTED")
    claude_md.write_text(text, encoding="utf-8")
    check = _check_canonical_terminology(target, "dual-agent")
    # Must still pass: required_startup_terms evaluated only against required_files
    # which is the (now-stripped) CLAUDE.md, but only the 5 startup terms matter.
    # MemBase / Deliberation Archive / MEMORY.md / Prime Builder / Loyal Opposition
    # were not in the strip list, so they remain present.
    assert check.status == "pass", (
        f"primer-only terms removed from CLAUDE.md must NOT fail the doctor "
        f"(existing required_startup_terms semantics preserved); got: {check.status}: {check.message}"
    )


def test_doctor_fails_when_primer_file_missing(tmp_path: Path) -> None:
    """Removing the primer file entirely causes the canonical-terminology check
    to FAIL — but at the existing 'glossary file missing' branch (not the new
    primer-term branch). This existing behavior is preserved by Slice 1.
    """
    target = _scaffold(tmp_path, "dual-agent")
    primer = target / ".claude" / "rules" / "canonical-terminology.md"
    primer.unlink()
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "fail", f"expected fail, got {check.status}: {check.message}"
    # Existing glossary-missing branch fires first.
    assert "canonical-terminology.md missing" in check.message


def test_gt_kb_self_doctor_passes_canonical_terminology() -> None:
    """Codex `-013.md` F1 acceptance: `gt project doctor` against the GT-KB
    checkout itself must report OK on the canonical-terminology check via the
    public `dual-agent` profile (the only valid project profile applicable
    to GT-KB's bridge-using layout per `profiles.py::PROFILES`).

    The fix path per Codex `-011.md` recommended action 1: GT-KB has a small
    root `MEMORY.md` redirect doc carrying the 5 canonical-startup-term
    content strings; the actual operational notepad lives at
    `memory/MEMORY.md`. AGENTS.md and `.claude/rules/deliberation-protocol.md`
    also carry the canonical-term content per REVISED-2.
    """
    repo_root = Path(__file__).resolve().parents[2]
    check = _check_canonical_terminology(repo_root, "dual-agent")
    assert check.status == "pass", (
        f"GT-KB self-doctor canonical-terminology check must pass under "
        f"dual-agent profile. Got status={check.status}: {check.message}"
    )


def test_primer_severity_independent_of_startup_severity(tmp_path: Path) -> None:
    """Codex `-008.md` F1 acceptance: missing_severity and primer_missing_severity
    are independent contracts. Setting startup=WARN and primer=ERROR, then
    removing a primer-only term, must produce status=fail (driven by the primer
    contract's ERROR severity), not warning.

    This test specifically guards against the regression Codex identified: the
    initial Slice 1 implementation collapsed both contracts into a single
    missing_report and used only missing_severity for status, making
    primer_missing_severity decorative.
    """
    target = _scaffold(tmp_path, "dual-agent")

    # Override the dual-agent profile's missing_severity to WARN via regex-based
    # rewrite (keeps primer_missing_severity at ERROR; targets only the dual-agent
    # block to avoid disturbing other profiles).
    import re as _re

    toml_path = target / ".claude" / "rules" / "canonical-terminology.toml"
    text = toml_path.read_text(encoding="utf-8")
    # Match: [config.profiles.dual-agent] block, then lazily match anything
    # (DOTALL) until the FIRST `missing_severity` (with \b to exclude
    # primer_missing_severity, which has `_` adjacency).
    pattern = _re.compile(
        r"(\[config\.profiles\.dual-agent\].*?)\bmissing_severity\s*=\s*\"ERROR\"",
        _re.DOTALL,
    )
    new_text, sub_count = pattern.subn(r'\1missing_severity = "WARN"', text, count=1)
    assert sub_count == 1, "differential-severity setup must override exactly one dual-agent missing_severity"
    toml_path.write_text(new_text, encoding="utf-8")

    # Remove a primer-only term from the primer file. "GTKB" is in primer_terms
    # but NOT in required_startup_terms, so its absence affects only contract 2.
    primer = target / ".claude" / "rules" / "canonical-terminology.md"
    primer_text = primer.read_text(encoding="utf-8")
    primer.write_text(primer_text.replace("GTKB", "REDACTED"), encoding="utf-8")

    check = _check_canonical_terminology(target, "dual-agent")
    # Primer contract is ERROR, so status must be fail (not warning, which would
    # indicate the doctor is using missing_severity for the primer contract).
    assert check.status == "fail", (
        f"primer_missing_severity=ERROR with missing primer term must produce status=fail "
        f"regardless of startup-side missing_severity (which is now WARN). "
        f"Got status={check.status}: {check.message}"
    )
    # The failure must cite the primer term, not a startup-file term.
    assert "missing primer term" in check.message and "GTKB" in check.message
