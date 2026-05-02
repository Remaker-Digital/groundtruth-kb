# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 2.5: rationale + migration-note discipline + schema lock.

T2 enforces that every product-scope record (`gt-kb-managed` or
`gt-kb-scaffolded`) has non-empty `notes` rationale.

T3 enforces that ownership flips against the golden snapshot include a
`notes` migration marker citing the prior value.

T-SCHEMA-NOTES proves the `OwnershipMeta.notes` field exists and round-trips
through `_to_ownership_record()` for FILE-class records.

T-IPR-CVR (GOV-20 Phase 1 advisory pilot) asserts the IPR + CVR docs exist
in KB with the ADR tag.

Bridge authority: ``bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-006.md`` GO.
"""

from __future__ import annotations

import sqlite3
from dataclasses import fields
from pathlib import Path

import pytest


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def test_every_product_managed_row_has_rationale() -> None:
    """T2 per Slice 2.5: every product-scope record has non-empty notes.

    Closure proof for the rationale-discipline acceptance item from scoping
    bridge `-003` line 84. Per Codex `-004` recommendation: this is the
    executable form of the closure (not a fixed N-row count) so it stays
    self-correcting against registry drift.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    missing: list[str] = []
    for record in resolver.all_records():
        if record.ownership in ("gt-kb-managed", "gt-kb-scaffolded") and not (record.notes or "").strip():
            missing.append(f"{record.id} ({record.ownership})")

    assert not missing, (
        f"{len(missing)} product-scope records lack `notes` rationale. "
        f"First 10: {missing[:10]}. Add a `notes = '...'` line to the row "
        f"in templates/managed-artifacts.toml or templates/scaffold-ownership.toml."
    )


def test_ownership_flips_require_migration_note() -> None:
    """T3 per Slice 2.5: ownership changes vs golden snapshot require notes marker.

    Loads tests/fixtures/registry-ownership-snapshot.tsv (id<TAB>ownership) and
    diffs against live state. For each record whose ownership differs from the
    snapshot, asserts the live record's `notes` contains a 'migration:' or
    'flipped from:' marker citing the prior value.

    To intentionally accept a flip (after an owner-approved ownership change):
    add the migration marker to the row's notes, then regenerate the snapshot
    via the recipe in the snapshot file's header comment.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    snapshot_path = _fixtures_dir() / "registry-ownership-snapshot.tsv"
    snapshot: dict[str, str] = {}
    for line in snapshot_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        snapshot[parts[0]] = parts[1]

    resolver = OwnershipResolver()
    flips_without_marker: list[str] = []
    for record in resolver.all_records():
        prior = snapshot.get(record.id)
        if prior is None or prior == record.ownership:
            continue
        notes_lower = (record.notes or "").lower()
        if "migration:" not in notes_lower and "flipped from:" not in notes_lower:
            flips_without_marker.append(
                f"{record.id}: snapshot={prior!r} -> live={record.ownership!r}, notes={record.notes!r}"
            )

    assert not flips_without_marker, (
        f"{len(flips_without_marker)} ownership flips lack migration markers. "
        f"First 5: {flips_without_marker[:5]}. Add 'migration: prev=<old> reason=<why>' "
        f"to the row's notes, then regenerate the snapshot."
    )


def test_ownership_meta_has_notes_field_with_round_trip() -> None:
    """T-SCHEMA-NOTES per Slice 2.5: OwnershipMeta.notes exists and round-trips.

    Asserts the schema extension is in place:
      1. `OwnershipMeta` exposes a `notes: str` field with default empty.
      2. `OwnershipResolver` returns at least one FILE-class record with
         non-empty notes (proving the projection in `_to_ownership_record()`
         forwards the field for non-glob source classes).
    """
    from groundtruth_kb.project.managed_registry import OwnershipMeta
    from groundtruth_kb.project.ownership import OwnershipResolver

    field_names = {f.name for f in fields(OwnershipMeta)}
    assert "notes" in field_names, "OwnershipMeta must expose `notes` field per Slice 2.5"

    meta = OwnershipMeta(
        ownership="adopter-owned",
        upgrade_policy="preserve",
        adopter_divergence_policy=None,
    )
    assert meta.notes == "", f"OwnershipMeta.notes default must be empty; got {meta.notes!r}"

    resolver = OwnershipResolver()
    file_records_with_notes = [
        r for r in resolver.all_records() if r.source_class == "file" and (r.notes or "").strip()
    ]
    assert file_records_with_notes, (
        "At least one FILE-class record must have non-empty notes (proves projection works); "
        "found 0. Either the schema extension didn't ship or no TOML row populated notes."
    )


def _kb_path() -> Path:
    here = Path(__file__).resolve()
    return here.parents[2] / "groundtruth.db"


def test_ipr_and_cvr_slice2_5_documents_exist_with_adr_tag() -> None:
    """T-IPR-CVR: GOV-20 Phase 1 advisory pilot - IPR + CVR docs in KB."""
    db_path = _kb_path()
    if not db_path.exists():
        pytest.skip(f"groundtruth.db not available at {db_path}")
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, category, tags FROM documents WHERE id IN (?, ?)",
            ("IPR-SLICE2-5-RATIONALE-SCHEMA-001", "CVR-SLICE2-5-RATIONALE-SCHEMA-001"),
        ).fetchall()
    finally:
        conn.close()

    found_ids = {r["id"] for r in rows}
    assert "IPR-SLICE2-5-RATIONALE-SCHEMA-001" in found_ids, "IPR-SLICE2-5 missing from KB"
    assert "CVR-SLICE2-5-RATIONALE-SCHEMA-001" in found_ids, "CVR-SLICE2-5 missing from KB"

    for r in rows:
        tags = (r["tags"] or "").lower()
        assert "adr-isolation-application-placement-001" in tags, f"{r['id']} missing ADR tag; got tags={r['tags']!r}"
