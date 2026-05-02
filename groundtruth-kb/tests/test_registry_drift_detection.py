# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 2: registry drift detection.

Compares the live ``OwnershipResolver.all_records()`` ID set against a
deterministic golden fixture. Mismatches fail the test with a list of
added/removed IDs and a remediation message pointing at the snapshot
regeneration recipe.

Bridge authority: ``bridge/gtkb-isolation-017-slice2-registry-isolation-004.md`` GO.
Spec: Phase 9 §"Regression Visibility" line 407 ("Registry drift must be
detectable").
"""

from __future__ import annotations

from pathlib import Path


def _fixtures_dir() -> Path:
    """Locate ``groundtruth-kb/tests/fixtures/`` from this test file."""
    return Path(__file__).resolve().parent / "fixtures"


def test_registry_drift_against_id_snapshot() -> None:
    """T4: registry ID set matches the golden snapshot.

    Per Phase 9 §"Regression Visibility" line 407. To intentionally accept
    drift (after adding/removing a record), regenerate the snapshot via
    the recipe in the assertion message below.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    live_ids = sorted(r.id for r in resolver.all_records())
    snapshot_path = _fixtures_dir() / "registry-id-set.txt"
    expected_ids = sorted(
        line.strip()
        for line in snapshot_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    )

    added = sorted(set(live_ids) - set(expected_ids))
    removed = sorted(set(expected_ids) - set(live_ids))

    assert not added and not removed, (
        f"Registry drift detected:\n"
        f"  added ({len(added)}): {added[:5]}{'...' if len(added) > 5 else ''}\n"
        f"  removed ({len(removed)}): {removed[:5]}{'...' if len(removed) > 5 else ''}\n"
        f"To intentionally accept this drift, regenerate the snapshot:\n"
        f'  cd E:/GT-KB && python -c "from groundtruth_kb.project.ownership '
        f"import OwnershipResolver; print(chr(10).join(sorted(r.id for r in "
        f'OwnershipResolver().all_records())))" '
        f"> groundtruth-kb/tests/fixtures/registry-id-set.txt\n"
        f"(then re-prepend the comment header from the existing file)."
    )
