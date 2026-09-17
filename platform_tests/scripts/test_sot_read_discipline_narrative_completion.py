"""Check authored retrieval guidance; generated prose is never a second glossary.

These are structural guidance checks. Native read behavior and actual current
term definitions require their own service/behavioral qualification.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / ".harness-baseline-configuration/rules"


def test_prime_builder_role_has_sot_read_clause():
    text = (RULES / "prime-builder-role.md").read_text(encoding="utf-8")
    assert "GOV-SOURCE-OF-TRUTH-FRESHNESS-001" in text
    assert "sot-read-discipline.md" in text
    assert "canonical CLI/domain" in text


def test_canonical_terminology_has_sot_read_discipline_entry():
    text = (RULES / "canonical-terminology.md").read_text(encoding="utf-8")
    assert "gt terms list" in text and "gt terms show" in text
    assert "does not contain a second glossary" in text


def test_canonical_terminology_has_forbidden_substitute_entry():
    text = (RULES / "sot-read-discipline.md").read_text(encoding="utf-8")
    assert "forbidden_substitutes" in text
    assert "DCL-SOT-READ-HOOK-CONTRACT-001" in text
    assert "empty list declares no path restrictions" in text
    assert "native event delivery" in text.lower()
