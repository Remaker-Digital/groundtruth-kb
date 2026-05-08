"""Integration tests for the canonical-terms registry doctor check.

Exercises ``groundtruth_kb.project.doctor._check_canonical_terms_registry``
against a temp project root with a real KnowledgeDB. Verifies the four
outcome paths: skip (table absent), pass (clean), warning (parity drift /
cross-field collision), fail (parity error / platform_core redefinition).

Per `bridge/gtkb-canonical-terminology-system-context-model-001-005.md`
T-doctor-1 and T-doctor-2.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb import canonical_terms
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.doctor import _check_canonical_terms_registry

SAMPLE_GLOSSARY_MD = """\
# Canonical Terminology — Test

## Canonical Terms

### MemBase

**Definition:** The canonical store of specifications and governed knowledge.

### Deliberation Archive

**Definition:** The design-reasoning tier.
"""


def _setup_project(tmp_path: Path) -> Path:
    """Create a minimal project root with a canonical-terminology.md fixture."""
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "canonical-terminology.md").write_text(SAMPLE_GLOSSARY_MD, encoding="utf-8")
    return tmp_path


def _open_db(tmp_path: Path) -> KnowledgeDB:
    return KnowledgeDB(str(tmp_path / "groundtruth.db"))


def test_pass_when_table_empty(tmp_path: Path) -> None:
    """Table provisioned but no rows yet: backing registry hasn't been seeded;
    pass with informational message.
    """
    target = _setup_project(tmp_path)
    db = _open_db(target)
    db.close()

    check = _check_canonical_terms_registry(target)
    assert check.status == "pass"
    assert "empty" in check.message.lower() or "seed" in check.message.lower()


def test_pass_when_seeded_clean(tmp_path: Path) -> None:
    """T-doctor-1 (positive): seeded table, markdown matches, no collisions."""
    target = _setup_project(tmp_path)
    db = _open_db(target)
    glossary = target / ".claude" / "rules" / "canonical-terminology.md"
    canonical_terms.seed_from_markdown(db, glossary, dry_run=False, changed_by="test")
    db.close()

    check = _check_canonical_terms_registry(target)
    assert check.status == "pass"
    assert "OK" in check.message or "clean" in check.message


def test_warning_on_parity_missing_in_table(tmp_path: Path) -> None:
    """T-doctor-2 (parity): markdown has a term not seeded; surfaces as warning."""
    target = _setup_project(tmp_path)
    db = _open_db(target)
    glossary = target / ".claude" / "rules" / "canonical-terminology.md"
    canonical_terms.seed_from_markdown(db, glossary, dry_run=False, changed_by="test")
    # Add a new term to the markdown without re-seeding.
    new_md = SAMPLE_GLOSSARY_MD + ("\n### NewTerm\n\n**Definition:** A freshly-added term.\n")
    glossary.write_text(new_md, encoding="utf-8")
    db.close()

    check = _check_canonical_terms_registry(target)
    assert check.status == "warning"
    assert "missing_in_table" in check.message


def test_fail_on_parity_missing_in_markdown(tmp_path: Path) -> None:
    """T-doctor-2 (parity): table has a platform_core term not in markdown;
    surfaces as fail (the table claims canonical authority for a row the
    markdown source has dropped without retire).
    """
    target = _setup_project(tmp_path)
    db = _open_db(target)
    glossary = target / ".claude" / "rules" / "canonical-terminology.md"
    canonical_terms.seed_from_markdown(db, glossary, dry_run=False, changed_by="test")

    # Inject a platform_core row that has no markdown counterpart, bypassing
    # the seed path (simulates someone hand-editing the table — exactly the
    # drift the parity check is designed to catch).
    canonical_terms.insert_term(
        db,
        id="ROGUE",
        canonical_term="Rogue",
        definition="Inserted without markdown source.",
        authority_level="platform_core",
        scope="platform",
        source_authority="manual-test-injection",
        changed_by="test",
        change_reason="parity-drift fixture",
    )
    db.close()

    check = _check_canonical_terms_registry(target)
    assert check.status == "fail"
    assert "missing_in_markdown" in check.message
    assert "ROGUE" in check.message


def test_fail_on_platform_core_redefinition(tmp_path: Path) -> None:
    """T-doctor-1 (collision): adopter_extension redefines a platform_core
    term via shared display text; surfaces as fail with classification
    platform_core_redefinition.

    The adopter uses a different ``id`` (their own) but the same
    ``canonical_term`` display string as the platform_core MemBase. The
    unified text-surface key catches this and reports
    platform_core_redefinition because the levels mix platform_core and
    adopter_extension on the shared ("text", "membase") key.
    """
    target = _setup_project(tmp_path)
    db = _open_db(target)
    glossary = target / ".claude" / "rules" / "canonical-terminology.md"
    canonical_terms.seed_from_markdown(db, glossary, dry_run=False, changed_by="test")

    # Adopter introduces their own id but reuses the platform_core display term.
    canonical_terms.insert_term(
        db,
        id="ADOPTER_MEMBASE",
        canonical_term="MemBase",  # collides with platform_core MEMBASE display
        definition="Adopter's reuse of the core display term.",
        authority_level="adopter_extension",
        scope="adopter:test_adopter",
        source_authority="test-adopter",
        changed_by="test",
        change_reason="platform_core redefinition fixture",
    )
    db.close()

    check = _check_canonical_terms_registry(target)
    assert check.status == "fail"
    assert "platform_core_redefinition" in check.message or "platform_core redefinition" in check.message


def test_warning_on_cross_field_text_reuse(tmp_path: Path) -> None:
    """T-doctor-2 (collision): same-scope cross-field synonym reuse warns
    without elevating to fail.
    """
    target = _setup_project(tmp_path)
    db = _open_db(target)
    glossary = target / ".claude" / "rules" / "canonical-terminology.md"
    canonical_terms.seed_from_markdown(db, glossary, dry_run=False, changed_by="test")

    # Two adopter_extension terms in the same scope reusing text across fields.
    canonical_terms.insert_term(
        db,
        id="ADOPTER_A",
        canonical_term="Adopter A",
        definition="d",
        authority_level="adopter_extension",
        scope="adopter:test_adopter",
        accepted_synonyms=["customer signal"],
        source_authority="test",
        changed_by="test",
        change_reason="fixture",
    )
    canonical_terms.insert_term(
        db,
        id="ADOPTER_B",
        canonical_term="Adopter B",
        definition="d",
        authority_level="adopter_extension",
        scope="adopter:test_adopter",
        forbidden_uses=["customer signal"],
        source_authority="test",
        changed_by="test",
        change_reason="fixture",
    )
    db.close()

    check = _check_canonical_terms_registry(target)
    assert check.status == "warning"
    assert "cross_field_text_reuse" in check.message
    assert "customer signal" in check.message


def test_pass_when_table_not_provisioned(tmp_path: Path) -> None:
    """If groundtruth.db exists but does not yet have the canonical_terms
    table (older schema), the check passes with an upgrade hint rather than
    blocking.
    """
    target = _setup_project(tmp_path)
    # Create groundtruth.db without the canonical_terms table.
    import sqlite3

    db_path = target / "groundtruth.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE specifications (id TEXT)")
    conn.commit()
    conn.close()

    check = _check_canonical_terms_registry(target)
    assert check.status == "pass"
    assert "upgrade" in check.message.lower() or "provisioned" in check.message.lower()


def test_pass_when_db_not_present(tmp_path: Path) -> None:
    """No groundtruth.db at the project root: skip with pass."""
    target = _setup_project(tmp_path)
    check = _check_canonical_terms_registry(target)
    assert check.status == "pass"


def test_pass_when_glossary_not_present(tmp_path: Path) -> None:
    """No canonical-terminology.md: skip with pass (different concern from
    the existing _check_canonical_terminology surface, which fails on the
    missing markdown — this registry check stays out of that role)."""
    # Don't call _setup_project here: leave the project bare.
    check = _check_canonical_terms_registry(tmp_path)
    assert check.status == "pass"
