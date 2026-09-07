"""The export guard's expected source set is pinned against the live schema (WI-7694).

``postgres_kernel.py`` line 2007 raises ``snapshot_table_set_mismatch`` -- *"SQLite source is not the
exact reviewed 49-table set"* -- when a snapshot's table inventory does not equal ``SOURCE_TABLES``
exactly. The live schema no longer matches, so ``gt db postgres export-current`` refuses the real
database.

The mismatch is **not** purely additive, and that changed during the session that filed this work.
When WI-7694 was written the difference was 17 extras and zero missing, making ``SOURCE_TABLES`` a
strict subset. It now carries one table the live schema lacks: ``project_authorizations``, dropped by
the PAUTH abolition canon requires. So ``SOURCE_TABLES`` expects a table for a retired instrument, and
a repair that only widened the set to admit drift would leave the export contract asserting that a
retired table must exist -- failing on a correct schema, for the opposite reason to the one recorded.

This file does not repair the guard; ``postgres_kernel.py`` is staged and unreviewed under WI-7707.
It pins what the difference *is*, in both directions, so the repair is scoped from measurement rather
than from a stale description and so further drift is visible the day it happens.

Bound to TEST-12609.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_DB = REPO_ROOT / "groundtruth.db"

#: Tables the live schema carries that ``SOURCE_TABLES`` does not expect. Every one is a subsystem
#: added after the 49-set was reviewed, and all are additive drift.
EXPECTED_EXTRAS = frozenset(
    {
        "dispatch_default_metric_events",
        "dispatch_default_metrics_snapshots",
        "dispatch_lane_matrix",
        "dispatch_lane_projection_metadata",
        "emergency_bootstrap_operational_event_tombstones",
        "emergency_bootstrap_operational_events",
        "governed_operational_events",
        "operational_event_tombstones",
        "operational_event_versions",
        "operational_events",
        "session_context_envelope_terminal_facts",
        "session_context_envelopes",
        "session_init_bindings",
        "session_role_attestations",
        "sot_registry_bridge_publication_capabilities",
        "sot_registry_bridge_recovery_receipts",
        "sot_registry_transition_requests",
        "test_artifact_update_requests",
    }
)

#: Tables ``SOURCE_TABLES`` expects that the live schema no longer has.
#:
#: ``project_authorizations`` held the retired PAUTH instrument. Its absence is correct; the defect is
#: that the export contract still requires it. This is the half of the mismatch that a widening repair
#: would miss, which is why it is pinned separately rather than folded into a single count.
EXPECTED_MISSING = frozenset({"project_authorizations"})


def _live_tables() -> set[str]:
    if not LIVE_DB.exists():
        pytest.skip("live MemBase not present in this checkout")
    conn = sqlite3.connect(f"file:{LIVE_DB}?mode=ro", uri=True)
    try:
        return {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        }
    finally:
        conn.close()


def _source_tables() -> set[str]:
    """``SOURCE_TABLES`` as the kernel declares it.

    Imported rather than parsed: the kernel is importable as of the ``PostgreSQLConfig`` port, and an
    import reads the value the guard actually uses rather than a transcription of it.
    """
    try:
        from groundtruth_kb.postgres_kernel import SOURCE_TABLES
    except ImportError as exc:  # pragma: no cover - the port is landed; this guards a regression
        pytest.skip(f"postgres_kernel not importable: {exc}")
    return set(SOURCE_TABLES)


def test_the_export_guard_would_still_refuse_the_live_schema() -> None:
    """The premise: the sets are unequal, so ``export-current`` refuses the real database.

    Asserted rather than assumed. If this ever passes as equal, the guard no longer blocks export and
    the rest of this file is describing a defect that has been fixed.
    """
    assert _live_tables() != _source_tables(), (
        "live schema now equals SOURCE_TABLES; the export guard no longer refuses the real database "
        "and WI-7694 is resolved. Retire this pin in the same change."
    )


def test_the_extras_are_exactly_the_pinned_additive_drift() -> None:
    """Equality on the extras, so the pin fails in both directions.

    A new subsystem table appearing fails this, and so does one of these being admitted into
    ``SOURCE_TABLES``. Either way the set below must be edited deliberately.
    """
    extras = _live_tables() - _source_tables()
    assert extras == EXPECTED_EXTRAS, (
        f"additive drift changed. new extras: {sorted(extras - EXPECTED_EXTRAS)}; "
        f"no longer extra: {sorted(EXPECTED_EXTRAS - extras)}"
    )


def test_source_tables_still_expects_the_retired_pauth_table() -> None:
    """The non-additive half: ``SOURCE_TABLES`` requires a table canon retires.

    This is the assertion the original diagnosis could not have carried, because when it was written
    ``project_authorizations`` still existed. It fails when the export contract stops expecting the
    retired table -- which is what the repair must do, and is the point at which this pin is updated.
    """
    missing = _source_tables() - _live_tables()
    assert missing == EXPECTED_MISSING, (
        f"the missing-table set changed. now missing: {sorted(missing)}; "
        f"previously pinned: {sorted(EXPECTED_MISSING)}. If SOURCE_TABLES no longer expects "
        "project_authorizations the PAUTH half of this defect is repaired; update the pin."
    )


def test_the_mismatch_is_not_purely_additive() -> None:
    """The characterisation the repair must be scoped from.

    Stated as its own assertion because it is the claim most likely to be lost: a reader who sees
    eighteen extras and stops there will scope a widening fix, and a widening fix leaves the export
    contract demanding a retired table.
    """
    live, source = _live_tables(), _source_tables()
    assert source - live, (
        "SOURCE_TABLES is now a subset of the live schema, so the mismatch IS purely additive and a "
        "widening repair is sufficient. That was true when WI-7694 was filed and is no longer; if it "
        "is true again, the PAUTH half has been repaired independently."
    )
