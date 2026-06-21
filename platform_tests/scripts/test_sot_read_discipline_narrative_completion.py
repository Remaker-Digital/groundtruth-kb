# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slice 2A narrative-completion guard (WI-4345 / WI-4350).

Pins the two narrative deliverables that completed Slice 2A read-discipline so
they cannot silently regress:

- WI-4345: ``.claude/rules/prime-builder-role.md`` carries a SoT-read-discipline
  clause that routes reads through canonical readers and avoids registered
  forbidden substitutes (per GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v2 +
  .claude/rules/sot-read-discipline.md).
- WI-4350: ``.claude/rules/canonical-terminology.md`` defines the
  ``SoT read discipline`` and ``forbidden substitute`` glossary entries
  (per DCL-SOT-READ-HOOK-CONTRACT-001 / DCL-CONCEPT-ON-CONTACT-001 /
  GOV-GLOSSARY-AS-DA-READ-SURFACE-001).

Source: ``bridge/gtkb-platform-sot-consolidation-slice-2a-completion-001.md``
(GO at ``-002``); owner authorization ``DELIB-20265458``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIME_BUILDER_ROLE = ROOT / ".claude" / "rules" / "prime-builder-role.md"
CANONICAL_TERMINOLOGY = ROOT / ".claude" / "rules" / "canonical-terminology.md"


def test_prime_builder_role_has_sot_read_clause() -> None:
    """WI-4345: interrogative-default carries the SoT-read-discipline clause."""
    text = PRIME_BUILDER_ROLE.read_text(encoding="utf-8")
    assert "SoT-read discipline" in text, "SoT-read-discipline clause missing"
    # The clause must anchor to its governing spec, the rule, and the substitute concept.
    assert "GOV-SOURCE-OF-TRUTH-FRESHNESS-001" in text
    assert "sot-read-discipline.md" in text
    assert "forbidden_substitutes" in text


def test_canonical_terminology_has_sot_read_discipline_entry() -> None:
    """WI-4350: 'SoT read discipline' glossary entry exists."""
    text = CANONICAL_TERMINOLOGY.read_text(encoding="utf-8")
    assert "### SoT read discipline" in text, "SoT read discipline glossary entry missing"
    assert "DCL-SOT-READ-HOOK-CONTRACT-001" in text


def test_canonical_terminology_has_forbidden_substitute_entry() -> None:
    """WI-4350: 'forbidden substitute' glossary entry exists."""
    text = CANONICAL_TERMINOLOGY.read_text(encoding="utf-8")
    assert "### forbidden substitute" in text, "forbidden substitute glossary entry missing"
    assert "forbidden_substitutes" in text
