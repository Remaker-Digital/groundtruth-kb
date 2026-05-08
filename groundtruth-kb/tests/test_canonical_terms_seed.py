"""Tests for canonical_terms seed plan and apply (idempotent, append-only).

Per `bridge/gtkb-canonical-terminology-system-context-model-001-005.md`
Specification-Derived Test Plan: T-seed-1, T-seed-2, T-seed-3, T-population-1.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb import canonical_terms
from groundtruth_kb.db import KnowledgeDB

SAMPLE_GLOSSARY_MD = """\
# Canonical Terminology — Test

## Canonical Terms (ADR-0001 core vocabulary)

These are the core terms.

### MemBase

**Definition:** The canonical, authoritative store of specifications and
governed knowledge.

### Deliberation Archive

**Canonical alias:** DA

**Definition:** The design-reasoning tier.

## GT-KB Platform & Lifecycle Terms (S327, owner-required minimum)

### platform

**Definition:** GT-KB itself; the lifecycle infrastructure.

## Alias / Canonical Disposition

This section is excluded from seeding.

### Some Alias

This is not a real term and should NOT be parsed (no Definition prose).

## Project-specific Terminology

(Empty for this fixture.)
"""


@pytest.fixture()
def db(tmp_path: Path) -> KnowledgeDB:
    """Fresh KnowledgeDB."""
    db_path = tmp_path / "test.db"
    return KnowledgeDB(str(db_path))


@pytest.fixture()
def glossary_md(tmp_path: Path) -> Path:
    """A small glossary fixture file."""
    p = tmp_path / "canonical-terminology.md"
    p.write_text(SAMPLE_GLOSSARY_MD, encoding="utf-8")
    return p


def test_parse_glossary_returns_only_term_sections(glossary_md: Path) -> None:
    """parse_markdown_glossary picks up real terms and skips non-term sections."""
    text = glossary_md.read_text(encoding="utf-8")
    parsed = canonical_terms.parse_markdown_glossary(text)
    ids = sorted(t["id"] for t in parsed)
    # MEMBASE, DELIBERATION_ARCHIVE, PLATFORM should appear.
    # SOME_ALIAS should NOT — it has no Definition prose and lives outside
    # the relevant ## sections anyway.
    assert "MEMBASE" in ids
    assert "DELIBERATION_ARCHIVE" in ids
    assert "PLATFORM" in ids
    assert "SOME_ALIAS" not in ids


def test_seed_dry_run_lists_inserts_for_empty_db(db: KnowledgeDB, glossary_md: Path) -> None:
    """T-seed-2 (precondition): a dry-run against an empty db plans inserts."""
    plan = canonical_terms.seed_from_markdown(db, glossary_md, dry_run=True)
    assert plan.summary().get("insert", 0) == 3
    assert plan.summary().get("update", 0) == 0
    assert plan.summary().get("retire", 0) == 0
    assert plan.source_hash.startswith("sha256:")
    # Dry-run does not mutate.
    assert canonical_terms.list_terms(db) == []


def test_seed_apply_inserts_terms(db: KnowledgeDB, glossary_md: Path) -> None:
    """T-population-1: after apply, all terms are present at platform_core."""
    canonical_terms.seed_from_markdown(db, glossary_md, dry_run=False, changed_by="test-seed")
    rows = canonical_terms.list_terms(db, authority_level="platform_core")
    ids = sorted(r["id"] for r in rows)
    assert ids == ["DELIBERATION_ARCHIVE", "MEMBASE", "PLATFORM"]
    membase = next(r for r in rows if r["id"] == "MEMBASE")
    assert membase["scope"] == "platform"
    assert "canonical, authoritative store" in membase["definition"]
    assert membase["lifecycle_status"] == "active"
    assert membase["source_authority"].startswith(glossary_md.as_posix())
    assert membase["source_authority"].endswith(_get_hash(glossary_md))


def _get_hash(path: Path) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def test_seed_idempotent(db: KnowledgeDB, glossary_md: Path) -> None:
    """T-seed-1: running apply twice with no markdown change produces all
    'unchanged' on the second run.
    """
    plan1 = canonical_terms.seed_from_markdown(db, glossary_md, dry_run=False, changed_by="test")
    assert plan1.summary().get("insert", 0) == 3
    plan2 = canonical_terms.seed_from_markdown(db, glossary_md, dry_run=False, changed_by="test")
    assert plan2.summary().get("unchanged", 0) == 3
    assert plan2.summary().get("insert", 0) == 0
    assert plan2.summary().get("update", 0) == 0
    # Still only 3 latest rows; no second-version churn.
    rows = canonical_terms.list_terms(db, authority_level="platform_core")
    assert len(rows) == 3
    versions = canonical_terms.list_versions(db, "MEMBASE")
    assert len(versions) == 1


def test_seed_dry_run_and_apply_produce_same_operations(db: KnowledgeDB, glossary_md: Path) -> None:
    """T-seed-2: dry-run and apply produce the same operation list for the
    same markdown source on a clean db.
    """
    dry_plan = canonical_terms.seed_from_markdown(db, glossary_md, dry_run=True)
    apply_plan = canonical_terms.seed_from_markdown(db, glossary_md, dry_run=False, changed_by="test")
    dry_ops = sorted((o.op, o.id) for o in dry_plan.operations)
    apply_ops = sorted((o.op, o.id) for o in apply_plan.operations)
    assert dry_ops == apply_ops


def test_seed_supersede_via_retire(db: KnowledgeDB, tmp_path: Path) -> None:
    """T-seed-3: removing a term from markdown causes 'retire' on next apply.

    The retire op appends a new (id, lifecycle_status='retired') version
    rather than DELETE. The original active row remains in history.
    """
    p1 = tmp_path / "v1.md"
    p1.write_text(SAMPLE_GLOSSARY_MD, encoding="utf-8")
    canonical_terms.seed_from_markdown(db, p1, dry_run=False, changed_by="test-v1")

    # Drop "platform" by writing a new markdown without that section.
    p2 = tmp_path / "v2.md"
    p2.write_text(
        SAMPLE_GLOSSARY_MD.replace(
            "### platform\n\n**Definition:** GT-KB itself; the lifecycle infrastructure.",
            "",
        ),
        encoding="utf-8",
    )
    plan = canonical_terms.seed_from_markdown(db, p2, dry_run=False, changed_by="test-v2")
    retire_ops = [o for o in plan.operations if o.op == "retire"]
    assert len(retire_ops) == 1
    assert retire_ops[0].id == "PLATFORM"

    # The retired row is appended; original is preserved.
    versions = canonical_terms.list_versions(db, "PLATFORM")
    assert len(versions) == 2
    assert versions[-1]["lifecycle_status"] == "retired"
    # list_terms (default include_retired=False) excludes the retired term.
    visible_ids = sorted(t["id"] for t in canonical_terms.list_terms(db))
    assert "PLATFORM" not in visible_ids
    # include_retired=True surfaces the retired row.
    all_ids = sorted(t["id"] for t in canonical_terms.list_terms(db, include_retired=True))
    assert "PLATFORM" in all_ids


def test_seed_revival_after_retire(db: KnowledgeDB, tmp_path: Path) -> None:
    """A previously-retired term becomes 'update' (revived) when it returns
    to the markdown.
    """
    p1 = tmp_path / "v1.md"
    p1.write_text(SAMPLE_GLOSSARY_MD, encoding="utf-8")
    canonical_terms.seed_from_markdown(db, p1, dry_run=False, changed_by="test-v1")

    p2 = tmp_path / "v2.md"
    p2.write_text(
        SAMPLE_GLOSSARY_MD.replace(
            "### platform\n\n**Definition:** GT-KB itself; the lifecycle infrastructure.",
            "",
        ),
        encoding="utf-8",
    )
    canonical_terms.seed_from_markdown(db, p2, dry_run=False, changed_by="test-v2")

    # Now revive the term.
    p3 = p1
    plan = canonical_terms.seed_from_markdown(db, p3, dry_run=False, changed_by="test-v3")
    update_ops = [o for o in plan.operations if o.op == "update" and o.id == "PLATFORM"]
    assert len(update_ops) == 1
    versions = canonical_terms.list_versions(db, "PLATFORM")
    assert len(versions) == 3
    assert versions[-1]["lifecycle_status"] == "active"


def test_seed_against_live_glossary(db: KnowledgeDB) -> None:
    """T-population-1 (integration): seed against the live
    .claude/rules/canonical-terminology.md and verify ≥ 26 platform_core terms.
    """
    repo_root = Path(__file__).resolve().parents[2]
    live_glossary = repo_root / ".claude" / "rules" / "canonical-terminology.md"
    if not live_glossary.exists():
        pytest.skip("live canonical-terminology.md not present at repo root")
    plan = canonical_terms.seed_from_markdown(db, live_glossary, dry_run=False, changed_by="test-live-seed")
    assert plan.summary().get("insert", 0) >= 26, plan.summary()
    rows = canonical_terms.list_terms(db, authority_level="platform_core")
    assert len(rows) >= 26
