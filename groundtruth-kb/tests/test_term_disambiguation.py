# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL Slice 1.

Per bridge `gtkb-gov-term-disambiguation-mechanical-2026-05-02-005.md` Test Plan T1:
verify the policy file exists, registers correctly in managed-artifacts.toml,
declares all 7 pinned defaults, and covers the 21 generic owner-required terms
(adopter template; "Agent Red" is GT-KB-self-only and added post-render).

Tier A/B/C lint behavior (T2-T17) is exercised in Slices 2-3.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from groundtruth_kb.term_disambiguation import PolicyConfig, evaluate_content

_REPO_ROOT = Path(__file__).resolve().parents[1]
_POLICY_PATH = _REPO_ROOT / "templates" / "rules" / "canonical-terminology-policy.toml"
_MANAGED_ARTIFACTS_PATH = _REPO_ROOT / "templates" / "managed-artifacts.toml"

# 21 generic owner-required terms (template; "Agent Red" added in GT-KB self-install
# post-render per primer Slice 1 pattern).
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

_PINNED_DEFAULTS_KEYS = [
    "tier_b_severity_in_bridge_proposals",
    "tier_b_severity_elsewhere",
    "tier_c_strictness",
    "forbidden_uses_severity",
    "sentence_initial_capitalization",
    "file_level_disable_marker",
    "override_syntax",
]


def test_canonical_terminology_policy_toml_exists() -> None:
    """Policy file is present at the expected template path."""
    assert _POLICY_PATH.exists(), f"canonical-terminology-policy.toml must exist at {_POLICY_PATH}"


def test_policy_registered_in_managed_artifacts() -> None:
    """The policy file is registered as `rule.canonical-terminology-policy`
    in managed-artifacts.toml following the same pattern as the existing
    `rule.canonical-terminology` and `rule.canonical-terminology-config` rows.
    """
    text = _MANAGED_ARTIFACTS_PATH.read_text(encoding="utf-8")
    assert 'id = "rule.canonical-terminology-policy"' in text, (
        "managed-artifacts.toml must register the policy file as 'rule.canonical-terminology-policy'"
    )
    assert 'template_path = "rules/canonical-terminology-policy.toml"' in text
    assert 'target_path = ".claude/rules/canonical-terminology-policy.toml"' in text


def test_policy_declares_all_seven_pinned_defaults() -> None:
    """The [defaults] section declares all 7 pinned values per Codex `-002.md` F4
    (resolved in REVISED-1) + `-004.md` F1 (PreToolUse enforcement event clarified).
    """
    config = tomllib.loads(_POLICY_PATH.read_text(encoding="utf-8"))
    defaults = config.get("defaults", {})
    missing = [k for k in _PINNED_DEFAULTS_KEYS if k not in defaults]
    assert not missing, f"[defaults] missing pinned key(s): {missing}"
    # Specific pinned values per the scoping proposal §"Pinned defaults".
    assert defaults["tier_b_severity_in_bridge_proposals"] == "error"
    assert defaults["tier_b_severity_elsewhere"] == "warn"
    assert defaults["tier_c_strictness"] == "strict"
    assert defaults["forbidden_uses_severity"] == "error"
    assert defaults["sentence_initial_capitalization"] == "ignore"
    assert defaults["file_level_disable_marker"] == "<!-- term-disambiguation: off -->"
    assert defaults["override_syntax"] == "{!common: <term>}"


def test_policy_covers_21_generic_owner_required_terms() -> None:
    """The [term.*] section covers the 21 generic owner-required terms per S327
    directive (excluding Agent Red, which is GT-KB-self-only post-render).
    """
    config = tomllib.loads(_POLICY_PATH.read_text(encoding="utf-8"))
    terms = config.get("term", {})
    missing = [t for t in _TEMPLATE_REQUIRED_21_TERMS if t not in terms]
    assert not missing, f"[term.*] missing {len(missing)} owner-required term(s): {missing}"
    # Inverse: Agent Red must NOT be in the adopter template
    # (smoke-test no-leakage rule per primer Slice 1 lesson).
    assert "Agent Red" not in terms, "'Agent Red' must not appear in the adopter template (GT-KB-self-install only)"


def test_policy_term_entries_have_disambiguation_tier() -> None:
    """Every [term.*] entry declares a disambiguation_tier of A, B, or C."""
    config = tomllib.loads(_POLICY_PATH.read_text(encoding="utf-8"))
    terms = config.get("term", {})
    for term_name, entry in terms.items():
        tier = entry.get("disambiguation_tier")
        assert tier in ("A", "B", "C"), f"term {term_name!r}: disambiguation_tier must be A/B/C, got {tier!r}"


def test_policy_config_load_parses_without_error() -> None:
    """`PolicyConfig.load(policy_path)` parses the TOML without raising."""
    policy = PolicyConfig.load(_POLICY_PATH)
    assert policy.defaults  # non-empty
    assert policy.terms  # non-empty
    assert "MemBase" in policy.terms
    assert policy.terms["MemBase"]["disambiguation_tier"] == "A"
    assert policy.terms["MemBase"]["distinctive_form"] == "MemBase"


def test_evaluate_content_returns_empty_list_in_slice1(tmp_path: Path) -> None:
    """Slice 1: `evaluate_content` API surface is callable and returns an
    empty list (Tier A/B/C lint logic implemented in Slices 2-3).
    """
    policy = PolicyConfig.load(_POLICY_PATH)
    fake_file = tmp_path / "scratch.md"
    fake_file.write_text("Some content with backlog and MemBase.", encoding="utf-8")
    violations = evaluate_content(
        "Some content with backlog and MemBase.",
        file_path=fake_file,
        policy=policy,
    )
    assert violations == []


def test_evaluate_content_honors_file_level_disable_marker(tmp_path: Path) -> None:
    """File-level disable marker exempts the file from all checks (Slice 1
    behavior; preserved through Slices 2-3).
    """
    policy = PolicyConfig.load(_POLICY_PATH)
    fake_file = tmp_path / "exempt.md"
    content = "<!-- term-disambiguation: off -->\nbacklog without qualification."
    fake_file.write_text(content, encoding="utf-8")
    violations = evaluate_content(
        content,
        file_path=fake_file,
        policy=policy,
    )
    assert violations == []


def test_violation_dataclass_field_shape() -> None:
    """Slice 1: `Violation` dataclass has the expected fields per the API
    contract that Slices 2-3 populate.
    """
    from groundtruth_kb.term_disambiguation import Violation

    v = Violation(
        term="backlog",
        tier="B",
        severity="warn",
        line=42,
        message="lowercase 'backlog' in canonical context",
        suggestion="capitalize as 'Backlog' or use {!common: backlog}",
    )
    assert v.term == "backlog"
    assert v.tier == "B"
    assert v.severity == "warn"
    assert v.line == 42
    assert v.suggestion  # non-empty when set
