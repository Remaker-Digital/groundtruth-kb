"""Canonicalize ``work_items.priority`` field values to P0/P1/P2/P3.

Implementation script for the
gtkb-work-item-priority-canonical-p0p3-migration bridge thread (WI-3396).
Migrates open work items whose priority is set to a legacy non-canonical
value (``high``/``HIGH``/``medium``/``MEDIUM``/``low``/``LOW``) to the
canonical P0/P1/P2/P3 schema by inserting new append-only versions via
``KnowledgeDB.insert_work_item()``.

Canonical mapping:

- ``low`` / ``LOW``    -> ``P3``
- ``medium`` / ``MEDIUM`` -> ``P2``
- ``high`` / ``HIGH``  -> ``P1``
- ``P0`` / ``P1`` / ``P2`` / ``P3`` -> identity (no migration needed)
- ``None`` / empty -> preserved as null (no auto-fill)
- any other value -> raises ``UnknownPriorityValueError``

Defaults to dry-run; ``--apply`` is required to mutate MemBase. Idempotent:
a second applied run reports zero mutations.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add groundtruth-kb/src to import path before importing the DB module.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_KB_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_KB_SRC) not in sys.path:
    sys.path.insert(0, str(_KB_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402


CANONICAL_PRIORITIES = frozenset({"P0", "P1", "P2", "P3"})

# Lowercase-input → canonical mapping. The script normalizes by .lower()
# before lookup, so this table covers all case variants (high, HIGH, High).
_MAPPING_LOWER = {
    "low": "P3",
    "medium": "P2",
    "high": "P1",
    "p0": "P0",
    "p1": "P1",
    "p2": "P2",
    "p3": "P3",
}


class UnknownPriorityValueError(ValueError):
    """Raised when a priority value is not in the known set."""


def _canonical_mapping(value: str | None) -> str | None:
    """Return the canonical priority for a given input value.

    None and empty string return None (null preservation). Known values
    (case-insensitive) return their canonical form. Anything else raises
    UnknownPriorityValueError.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise UnknownPriorityValueError(repr(value))
    s = value.strip()
    if s == "":
        return None
    lowered = s.lower()
    if lowered not in _MAPPING_LOWER:
        raise UnknownPriorityValueError(repr(value))
    return _MAPPING_LOWER[lowered]


def _migration_change_reason(original: str, canonical: str) -> str:
    return (
        "S363 F3 priority canonicalization migration; "
        f"original={original} -> canonical={canonical} "
        "per WI-3396 / DELIB-2239 / PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001"
    )


def _carry_forward_kwargs(row: dict[str, Any]) -> dict[str, Any]:
    """Build kwargs for insert_work_item that carry forward all backlog/optional fields."""
    optional_fields = [
        "description",
        "source_spec_id",
        "source_test_id",
        "failure_description",
        "stage",
        "approval_state",
        "project_name",
        "subproject_name",
        "implementation_order",
        "status_detail",
        "source_owner_directive",
        "source_deliberation_query",
        "related_deliberation_ids",
        "related_spec_ids_at_creation",
        "related_bridge_threads",
        "depends_on_work_items",
        "blocks_work_items",
        "acceptance_summary",
        "regression_visibility",
        "completion_evidence",
        "supersedes",
        "superseded_by",
    ]
    kwargs: dict[str, Any] = {}
    for field in optional_fields:
        if field in row and row[field] is not None:
            kwargs[field] = row[field]
    return kwargs


def collect_targets(db: KnowledgeDB) -> list[dict[str, Any]]:
    """Return open WIs whose priority is non-null and non-canonical."""
    open_wis = db.list_work_items(resolution_status="open")
    targets = []
    for row in open_wis:
        priority = row.get("priority")
        if priority is None or priority == "":
            continue  # null preservation
        if priority in CANONICAL_PRIORITIES:
            continue
        canonical = _canonical_mapping(priority)
        if canonical is None:
            # null-coalesced; should never happen since we filtered None above
            continue
        if canonical == priority:
            continue  # already canonical
        targets.append({"row": row, "canonical": canonical, "original": priority})
    return targets


def apply_migration(
    db: KnowledgeDB,
    targets: list[dict[str, Any]],
    *,
    changed_by: str,
) -> dict[str, Any]:
    """Apply the migration by inserting new versions for each target.

    Returns a summary dict with counts and per-WI details.
    """
    migrated: list[dict[str, Any]] = []
    for target in targets:
        row = target["row"]
        canonical = target["canonical"]
        original = target["original"]

        # Required positional args
        kwargs = _carry_forward_kwargs(row)
        kwargs["priority"] = canonical
        kwargs["description"] = row.get("description")
        # Stage carries forward (don't override default 'created')
        if "stage" not in kwargs and row.get("stage") is not None:
            kwargs["stage"] = row["stage"]
        result = db.insert_work_item(
            id=row["id"],
            title=row["title"],
            origin=row["origin"],
            component=row["component"],
            resolution_status=row["resolution_status"],
            changed_by=changed_by,
            change_reason=_migration_change_reason(original, canonical),
            **kwargs,
        )
        migrated.append(
            {
                "id": row["id"],
                "original_priority": original,
                "canonical_priority": canonical,
                "new_version": (result or {}).get("version") if isinstance(result, dict) else None,
            }
        )
    return {
        "migrated_count": len(migrated),
        "migrated": migrated,
    }


def post_migration_invariant_holds(db: KnowledgeDB) -> dict[str, Any]:
    """Return (holds, observations) for the post-migration invariant."""
    open_wis = db.list_work_items(resolution_status="open")
    counts: Counter = Counter()
    noncanonical_nonnull: list[dict[str, Any]] = []
    for row in open_wis:
        priority = row.get("priority")
        counts[priority] += 1
        if priority is not None and priority not in CANONICAL_PRIORITIES and priority != "":
            noncanonical_nonnull.append({"id": row["id"], "priority": priority})
    holds = len(noncanonical_nonnull) == 0
    return {
        "invariant_holds": holds,
        "open_wi_total": len(open_wis),
        "counts": {str(k): v for k, v in counts.items()},
        "noncanonical_nonnull_remaining": noncanonical_nonnull,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Canonicalize work_items.priority values to P0/P1/P2/P3.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the migration (default is dry-run).",
    )
    parser.add_argument(
        "--changed-by",
        default="prime-builder/claude/B",
        help="Attribution string for the new version rows (default: prime-builder/claude/B).",
    )
    parser.add_argument(
        "--db-path",
        default=Path("groundtruth.db"),
        type=Path,
        help="Path to groundtruth.db (default: ./groundtruth.db).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary on stdout.",
    )
    args = parser.parse_args(argv)

    db = KnowledgeDB(args.db_path)
    targets = collect_targets(db)

    pre_distribution = Counter()
    open_wis = db.list_work_items(resolution_status="open")
    for row in open_wis:
        pre_distribution[row.get("priority")] += 1

    summary: dict[str, Any] = {
        "mode": "apply" if args.apply else "dry-run",
        "started_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "db_path": str(args.db_path),
        "changed_by": args.changed_by,
        "pre_migration": {
            "open_total": len(open_wis),
            "non_canonical_non_null_count": len(targets),
            "priority_distribution": {str(k): v for k, v in pre_distribution.items()},
        },
        "targets_preview": [
            {
                "id": t["row"]["id"],
                "original": t["original"],
                "canonical": t["canonical"],
            }
            for t in targets[:10]
        ],
    }

    if args.apply:
        result = apply_migration(db, targets, changed_by=args.changed_by)
        summary["applied"] = result
        invariant = post_migration_invariant_holds(db)
        summary["post_migration"] = invariant
        # Reproducibility check: idempotency on second pass
        re_targets = collect_targets(db)
        summary["idempotent_check"] = {
            "second_pass_target_count": len(re_targets),
            "is_idempotent": len(re_targets) == 0,
        }
    else:
        summary["dry_run"] = {
            "would_migrate_count": len(targets),
            "would_migrate_distribution": {f"{t['original']}->{t['canonical']}": 1 for t in targets},
        }
        # Compact the distribution for human reading
        agg = Counter()
        for t in targets:
            agg[f"{t['original']}->{t['canonical']}"] += 1
        summary["dry_run"]["would_migrate_distribution"] = dict(agg)

    if args.json:
        sys.stdout.write(json.dumps(summary, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(
            f"Mode: {summary['mode']}\n"
            f"DB: {summary['db_path']}\n"
            f"Pre-migration: {summary['pre_migration']['open_total']} open WIs; "
            f"{summary['pre_migration']['non_canonical_non_null_count']} non-canonical non-null priorities.\n"
        )
        if args.apply:
            sys.stdout.write(
                f"Migrated: {summary['applied']['migrated_count']} rows.\n"
                f"Post-migration invariant holds: {summary['post_migration']['invariant_holds']}\n"
                f"Idempotent (second-pass target count): "
                f"{summary['idempotent_check']['second_pass_target_count']}\n"
            )
        else:
            sys.stdout.write(
                f"Dry-run: would migrate {summary['dry_run']['would_migrate_count']} rows.\n"
                f"Distribution: {summary['dry_run']['would_migrate_distribution']}\n"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
