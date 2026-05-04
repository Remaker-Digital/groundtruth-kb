"""Tests for Sub-slice B: AUQ-only declaration in Prime Builder rule files.

Per
bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md
(Codex GO at -004), F1+F2: explicit per-token per-file assertions that prove
the AUQ-only contract is present in both target rule files.

- F1 (acting-file parity): the same required-token set is asserted against
  both .claude/rules/prime-builder-role.md and .claude/rules/acting-prime-builder.md.
- F2 (decision-class completeness): all 8 in-scope decision classes are
  asserted as substring-present (per-class membership), not alternation count.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRIME_RULE = REPO_ROOT / ".claude" / "rules" / "prime-builder-role.md"
ACTING_RULE = REPO_ROOT / ".claude" / "rules" / "acting-prime-builder.md"

# Six required tokens proving the AUQ-only declaration is structurally present.
REQUIRED_TOKENS = [
    "## AskUserQuestion as the Only Valid Owner-Decision Channel",
    "gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md",
    "PROSE_DECISION_PATTERNS",
    '"decision": "block"',
    "detected_via: ask_user_question",
    "Owner Decisions / Input",
]

# Eight in-scope decision classes (per Sub-slice B Goal §3, owner directive).
DECISION_CLASSES = [
    "approvals",
    "waivers",
    "priority choices",
    "formal artifact approvals",
    "requirement clarifications",
    "destructive actions",
    "deployments",
    "blocking owner decisions",
]


def _check_file_contains_all(path: Path, tokens: list[str]) -> list[str]:
    """Return list of missing tokens (empty list = all present)."""
    content = path.read_text(encoding="utf-8")
    return [t for t in tokens if t not in content]


def test_prime_builder_role_has_auq_only_section():
    missing = _check_file_contains_all(PRIME_RULE, REQUIRED_TOKENS)
    assert not missing, f"prime-builder-role.md missing tokens: {missing}"


def test_prime_builder_role_lists_all_decision_classes():
    missing = _check_file_contains_all(PRIME_RULE, DECISION_CLASSES)
    assert not missing, f"prime-builder-role.md missing decision classes: {missing}"


def test_acting_prime_builder_has_auq_only_section():
    missing = _check_file_contains_all(ACTING_RULE, REQUIRED_TOKENS)
    assert not missing, f"acting-prime-builder.md missing tokens: {missing}"


def test_acting_prime_builder_lists_all_decision_classes():
    missing = _check_file_contains_all(ACTING_RULE, DECISION_CLASSES)
    assert not missing, f"acting-prime-builder.md missing decision classes: {missing}"
