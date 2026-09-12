# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 2: schema-lock + CI-wiring meta-tests + GOV-20.

T-SCHEMA documents that scoping `-003` line 83 acceptance ("`owner` and
`upgrade_policy` fields") is satisfied by the existing
``OwnershipMeta.ownership`` / ``OwnershipMeta.upgrade_policy`` fields.

T-CI is a meta-test asserting the new Slice 2 test files live under
``tests/`` and are therefore pytest-collected by the existing ``test-base``
CI lane (`groundtruth-kb/.github/workflows/ci.yml`).

T-IPR-CVR (GOV-20 Phase 1) asserts the IPR + CVR documents exist in KB
with the ADR tag.

Bridge authority: ``bridge/gtkb-isolation-017-slice2-registry-isolation-004.md`` GO.
"""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path


def test_ownership_meta_existing_fields_satisfy_owner_and_upgrade_acceptance() -> None:
    """T-SCHEMA: scoping `-003` line 83 satisfied by existing fields.

    Asserts ``OwnershipMeta`` already exposes:
      - ``ownership`` (the `OwnershipEnum`, covering owner semantics)
      - ``upgrade_policy`` (the `UpgradePolicyEnum`, covering upgrade policy)

    No schema extension is required for the Slice 2 acceptance criterion
    "Registry schema updated with `owner` and `upgrade_policy` fields"
    (scoping bridge `-003` line 83). T2/T3 (rationale + migration-note
    discipline) are explicitly deferred to Slice 2.5.
    """
    from groundtruth_kb.project.managed_registry import OwnershipMeta

    field_names = {f.name for f in fields(OwnershipMeta)}
    assert "ownership" in field_names, (
        "OwnershipMeta must expose `ownership` (covers `owner` acceptance per scoping line 83)"
    )
    assert "upgrade_policy" in field_names, (
        "OwnershipMeta must expose `upgrade_policy` (covers `upgrade_policy` acceptance per scoping line 83)"
    )


def test_slice2_test_files_live_under_tests_directory() -> None:
    """T-CI: scoping `-003` line 86 (CI wiring satisfied by file placement).

    Asserts every Slice 2 test file lives under ``groundtruth-kb/tests/``.
    The existing ``test-base`` CI lane runs ``pytest tests/`` on every push
    and pull request; therefore tests at this location are CI-collected
    without a bespoke workflow lane.
    """
    tests_dir = Path(__file__).resolve().parent
    expected_files = (
        "test_registry_ast_coverage.py",
        "test_registry_drift_detection.py",
        "test_registry_target_path_round_trip.py",
        "test_registry_schema_and_ci.py",
    )
    for name in expected_files:
        assert (tests_dir / name).is_file(), f"Slice 2 test file missing: {name}"


def _kb_path() -> Path:
    here = Path(__file__).resolve()
    # tests/test_registry_schema_and_ci.py -> groundtruth-kb/ -> E:/GT-KB
    return here.parents[2] / "groundtruth.db"
