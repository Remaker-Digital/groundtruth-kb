# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 2: target-path classify round-trip sanity (T6).

Per Codex `-002` F1 fix: ``OwnershipResolver.classify_path()`` is keyed
on **scaffold target paths**, not template-source paths. T6 proves the
contract by round-tripping every FILE-class record's ``target_path``
through ``classify_path()`` and asserting the same record returns.

Bridge authority: ``bridge/gtkb-isolation-017-slice2-registry-isolation-004.md`` GO.
"""

from __future__ import annotations


def test_classify_path_round_trip_for_file_class_target_paths() -> None:
    """T6: classify_path(target_path) returns the same record by id.

    Sanity check: for every FILE-class registry row, calling
    ``OwnershipResolver.classify_path(record.source.target_path)`` returns
    a record with the same ``id``. Proves the resolver is consistent and
    that target_path is the correct key for the public classify_path API.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    mismatches: list[str] = []

    for record in resolver.all_records():
        if record.source_class != "file" or record.source is None:
            continue
        target_path = getattr(record.source, "target_path", None)
        if not target_path:
            continue
        round_tripped = resolver.classify_path(target_path)
        if round_tripped.id != record.id:
            mismatches.append(f"{record.id} -> classify({target_path!r}).id == {round_tripped.id!r}")

    assert not mismatches, (
        f"{len(mismatches)} FILE-class records do not round-trip through "
        f"classify_path(target_path). First 5: {mismatches[:5]}. This "
        f"indicates a resolver inconsistency or duplicate target_path."
    )
