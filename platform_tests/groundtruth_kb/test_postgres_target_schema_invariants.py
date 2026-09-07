"""The PostgreSQL target schema has a declared, reviewable relationship to the live one (WI-7622).

WI-6246, the database-migration charter, states no target-schema invariant set. The consequence is
measurable rather than theoretical: the PostgreSQL v1 target declares 21 tables, the live MemBase
schema has 67, and nothing in the platform objects to that difference or even names it. A Bundle 1
activation against v1 as it stands would satisfy every existing gate and still carry 20 of 67 tables.

``governed_operational_events`` is the demonstration. It entered the live schema under WI-6992 with
no target counterpart, and nothing objected, because nothing existed to object.

The load-bearing assertion here is :func:`test_every_live_table_is_classified_exactly_once`. The
other assertions describe today's state and stay true until someone edits a list; only that one fails
when the world changes without permission. A new table cannot be absorbed by a default or a
wildcard -- it must be classified deliberately, which is the mechanical stop this work exists to put
in place.

Bound to TEST-12537. Governed by ``DCL-POSTGRES-TARGET-SCHEMA-INVARIANTS-001``.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_DB = REPO_ROOT / "groundtruth.db"
TARGET_DDL = REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "postgresql_v1.sql"

# --- the four classes -----------------------------------------------------
#
# Every live MemBase table belongs to exactly one. The lists are declared here rather than inferred
# from the schema, because a rule that derives its answer from the schema can never disagree with
# the schema, and disagreeing with the schema is the entire job.

#: Governed records that already have a home in the PostgreSQL v1 target.
IN_TARGET = frozenset(
    {
        "canonical_terms",
        "deliberation_specs",
        "deliberation_work_items",
        "deliberations",
        "documents",
        "environment_config",
        "harnesses",
        "operational_procedures",
        "project_artifact_links",
        "project_dependencies",
        "project_work_item_memberships",
        "projects",
        "specification_deliberation_sources",
        "specifications",
        "test_plan_phases",
        "test_plans",
        "test_procedures",
        "testable_elements",
        "tests",
        "work_items",
    }
)

#: Governed records with **no** target home. This is the gap, and it is the point of the file.
#: ``CLAUDE.md`` names several of these as managed or supporting record types; ``sot_artifacts`` and
#: ``sot_artifact_revisions`` are the source-of-truth registry itself.
MUST_MIGRATE = frozenset(
    {
        "assertion_runs",
        "backlog_snapshots",
        "governed_operational_events",
        "quality_scores",
        "session_prompts",
        "sot_artifact_revisions",
        "sot_artifacts",
        "spec_quality_scores",
        "test_artifact_update_requests",
        "test_coverage",
    }
)

#: Coordination, telemetry and lease state. Legitimately not migrated: these describe how work was
#: dispatched and observed, not what the project decided, and a fresh installation regenerates them.
EXCLUDE_EPHEMERAL = frozenset(
    {
        "agent_capability_snapshots",
        "dispatch_default_metric_events",
        "dispatch_default_metrics_snapshots",
        "dispatch_events",
        "dispatch_lane_matrix",
        "dispatch_lane_projection_metadata",
        "dispatch_lane_projection_snapshots",
        "dispatch_lane_score_dimensions",
        "dispatch_lane_score_snapshots",
        "dispatch_lane_scoring_evidence",
        "dispatch_lanes",
        "flow_artifacts",
        "flow_definitions",
        "flow_events",
        "flow_instances",
        "pipeline_events",
        "session_context_envelope_terminal_facts",
        "session_context_envelopes",
        "session_init_bindings",
        "session_role_attestations",
        "session_snapshots",
        "sot_quarantine_receipts",
        "sot_registry_bridge_publication_capabilities",
        "sot_registry_bridge_recovery_receipts",
        "sot_registry_observation_capabilities",
        "sot_registry_transaction_journal",
        "sot_registry_transition_requests",
        "stage_attempt_telemetry",
        "stage_instances",
        "stage_leases",
        "work_intent_claims",
    }
)

#: Tables the canon abolishes or supersedes. ``project_authorizations`` carries the retired PAUTH
#: instrument -- canon section 3 makes authorization a field on the project row. The operational-event
#: family is superseded by ``governed_operational_events`` under WI-6992, which is why that successor
#: sits in ``MUST_MIGRATE`` while its predecessors sit here.
EXCLUDE_RETIRED = frozenset(
    {
        "emergency_bootstrap_operational_event_tombstones",
        "emergency_bootstrap_operational_events",
        "operational_event_tombstones",
        "operational_event_versions",
        "operational_events",
        "project_authorizations",
    }
)

CLASSES = {
    "in_target": IN_TARGET,
    "must_migrate": MUST_MIGRATE,
    "exclude_ephemeral": EXCLUDE_EPHEMERAL,
    "exclude_retired": EXCLUDE_RETIRED,
}


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


def _target_tables() -> set[str]:
    """Table names declared by the v1 target DDL.

    The DDL qualifies every name with a ``{schema}`` placeholder substituted at apply time, so the
    prefix is part of the grammar rather than noise -- a pattern that ignores it silently matches
    nothing and reports an empty target schema, which reads as "no tables declared" rather than as a
    parse failure.
    """
    if not TARGET_DDL.exists():
        pytest.skip("PostgreSQL v1 target DDL not present in this checkout")
    text = TARGET_DDL.read_text(encoding="utf-8")
    return set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?\{schema\}\.([a-z_]+)", text, re.I))


# --- coverage family ------------------------------------------------------


def test_every_live_table_is_classified_exactly_once() -> None:
    """The load-bearing assertion: a new table must be classified, not absorbed.

    There is no default class and no wildcard. Adding a table to the live schema fails this test
    until someone decides, in a reviewable edit, whether it must migrate or why it need not. Had this
    existed on the day ``governed_operational_events`` was added, it would have failed then.
    """
    live = _live_tables()
    declared: set[str] = set()
    for names in CLASSES.values():
        declared |= names

    unclassified = sorted(live - declared)
    assert unclassified == [], (
        f"live tables with no declared migration class: {unclassified}. "
        "Assign each to in_target, must_migrate, exclude_ephemeral or exclude_retired "
        "per DCL-POSTGRES-TARGET-SCHEMA-INVARIANTS-001."
    )

    vanished = sorted(declared - live)
    assert vanished == [], f"classified tables no longer in the live schema: {vanished}"


def test_the_four_classes_are_disjoint() -> None:
    """A table in two classes has no single answer, which is the same defect as having none."""
    overlaps: list[str] = []
    names = list(CLASSES)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            shared = CLASSES[left] & CLASSES[right]
            if shared:
                overlaps.append(f"{left} & {right}: {sorted(shared)}")
    assert overlaps == [], f"classes overlap: {overlaps}"


# --- the declared classification agrees with the target schema ------------


def test_declared_in_target_matches_the_target_ddl() -> None:
    """The hand-declared ``IN_TARGET`` list is checked against the DDL it claims to describe.

    ``IN_TARGET`` is declared rather than derived so the classification survives the DDL being
    absent, but a declared list can drift from its subject. This is the reconciliation.
    """
    target = _target_tables()
    live = _live_tables()
    assert (target & live) == IN_TARGET, (
        "declared IN_TARGET disagrees with the DDL: "
        f"declared-not-in-DDL={sorted(IN_TARGET - target)}, "
        f"DDL-not-declared={sorted((target & live) - IN_TARGET)}"
    )


def test_the_must_migrate_set_genuinely_has_no_target_home() -> None:
    """``must_migrate`` means exactly this: present live, absent from the target.

    Asserted positively so the class cannot quietly become a synonym for "not yet reviewed". If a
    target home is added for one of these, this test fails and the table moves to ``IN_TARGET`` --
    which is the intended way for the gap to close.
    """
    target = _target_tables()
    housed = sorted(MUST_MIGRATE & target)
    assert housed == [], f"tables classified must_migrate that already have a target home: {housed}"


def test_the_target_declares_exactly_one_table_with_no_live_counterpart() -> None:
    """``record_history`` is target-only by design: it is the append-only history carrier.

    Recorded because a second target-only table would mean the target had grown a concept the live
    schema does not have, which is a different and unreviewed kind of divergence.
    """
    target = _target_tables()
    live = _live_tables()
    assert sorted(target - live) == ["record_history"]


def test_the_gap_is_not_silently_widening() -> None:
    """The gap's size is pinned at its reviewed value.

    A bare count would be brittle for its own sake; this one is not. ``MUST_MIGRATE`` can only change
    by an edit to the list above, and this assertion makes that edit visible as a deliberate change
    to a reviewed number rather than a line lost in a diff.
    """
    assert len(MUST_MIGRATE) == 10, (
        f"the must_migrate set changed size ({len(MUST_MIGRATE)}); if a table gained a target home or "
        "a new governed table was added, update DCL-POSTGRES-TARGET-SCHEMA-INVARIANTS-001 with it."
    )
