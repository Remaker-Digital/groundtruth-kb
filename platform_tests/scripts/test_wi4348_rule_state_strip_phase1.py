# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-4348 Phase-1 guard — rule-file role-state pointer-swaps.

Pins the three Category-A pointer swaps so the baked role/harness *state* cannot
silently return to the protected rule files (the SoT-read-discipline forbidden-
substitute class). Role-resolution authority remains in
``harness-state/harness-registry.json`` / ``harness-state/harness-identities.json``
— these assertions check the *prose* defers to those canonical readers.

- A1 ``.claude/rules/operating-role.md``: identity authority points to
  ``harness-identities.json``; the A/B mapping is marked illustrative.
- A2 ``.claude/rules/prime-builder-role.md``: the active Prime Builder is
  resolved from ``harness-registry.json`` (no baked "until further notice"
  current-holder assignment).
- A3 ``.claude/rules/acting-prime-builder.md``: the Current-Mapping section
  defers to the durable role map and does not pin the current holder.

Per GOV-SESSION-ROLE-AUTHORITY-001 / DCL-SESSION-ROLE-RESOLUTION-001 /
GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v2 / DCL-SOT-READ-HOOK-CONTRACT-001.
Source: ``bridge/gtkb-platform-sot-consolidation-wi4348-phase1-rule-state-strip-001.md``
(GO at ``-002``); owner authorization ``DELIB-20265508``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPERATING_ROLE = ROOT / ".claude" / "rules" / "operating-role.md"
PRIME_BUILDER_ROLE = ROOT / ".claude" / "rules" / "prime-builder-role.md"
ACTING_PRIME = ROOT / ".claude" / "rules" / "acting-prime-builder.md"


def test_operating_role_defers_identity() -> None:
    """A1: identity authority is the artifact; A/B mapping is illustrative."""
    text = OPERATING_ROLE.read_text(encoding="utf-8")
    assert "harness-state/harness-identities.json" in text
    assert "illustrative; not authoritative" in text


def test_prime_builder_role_defers_assignment() -> None:
    """A2: active Prime Builder resolves from the registry; no baked assignment."""
    text = PRIME_BUILDER_ROLE.read_text(encoding="utf-8")
    assert "harness-state/harness-registry.json" in text
    assert "not the record of which harness holds the role" in text
    # The baked current-holder assignment must be gone.
    assert "Mike designates the active AI harness as" not in text


def test_acting_prime_builder_defers_mapping() -> None:
    """A3: Current-Mapping defers to the durable role map."""
    text = ACTING_PRIME.read_text(encoding="utf-8")
    assert "harness-state/harness-registry.json" in text
    assert "does not itself pin" in text
    # The baked current-holder assumption must be gone.
    assert "active AI harness assumes the Prime Builder role until the" not in text
