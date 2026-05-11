#!/usr/bin/env python3
"""Apply the Tier A subset of the GT-KB scaffold upgrade plan.

Per bridge ``gtkb-scaffold-upgrade-tier-a-009.md`` GO.

Tier A scope:
    - Apply only ``add`` and ``append-gitignore`` actions from ``plan_upgrade()``.
    - Do NOT apply ``merge-event-hooks`` (Tier B).
    - Do NOT apply ``skip`` rows (Tier C; preserved for later).
    - Do NOT mutate ``groundtruth.toml`` ``scaffold_version`` so deferred
      ``SKIP`` rows remain visible in subsequent ``plan_upgrade()`` calls.

The applier calls
``execute_upgrade(..., enforce_isolation=False, update_manifest=False)`` —
``enforce_isolation=False`` because the GT-KB platform root already
satisfies isolation invariants by construction, and ``update_manifest=False``
per the F1 fix from ``bridge/gtkb-scaffold-upgrade-tier-a-006.md`` (carried
forward as design through ``-009``).

Usage::

    python scripts/scaffold_upgrade_tier_a_apply.py [--target PATH] [--dry-run]

Emits a JSON action listing to stdout describing pre/post manifest version,
plan counts, kept-action listing, and applier results. Exit 0 on success;
non-zero on any pre-condition failure.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from groundtruth_kb.project.manifest import read_manifest  # noqa: E402
from groundtruth_kb.project.upgrade import (  # noqa: E402
    UpgradeAction,
    execute_upgrade,
    plan_upgrade,
)

# Tier A scope: ADD pure-new files + APPEND gitignore patterns only.
KEPT_ACTION_KINDS: frozenset[str] = frozenset({"add", "append-gitignore"})


def _summarize_plan(actions: list[UpgradeAction]) -> dict[str, int]:
    """Return a Counter-style mapping of action -> count, plus 'total'."""
    counter: Counter[str] = Counter(a.action for a in actions)
    summary = {kind: int(counter.get(kind, 0)) for kind in counter}
    summary["total"] = int(sum(counter.values()))
    return summary


def _action_to_dict(action: UpgradeAction) -> dict[str, str]:
    """Serialize an :class:`UpgradeAction` for JSON output."""
    return {
        "file": action.file,
        "action": action.action,
        "reason": action.reason,
        "payload": action.payload,
        "event": action.event,
    }


def apply_tier_a(target: Path, *, dry_run: bool = False) -> dict[str, object]:
    """Plan, filter, and (unless ``dry_run``) execute Tier A actions.

    Returns a structured dict describing the operation, suitable for
    JSON serialization to stdout.
    """
    pre_manifest = read_manifest(target / "groundtruth.toml")
    pre_version = pre_manifest.scaffold_version if pre_manifest else None

    all_actions = plan_upgrade(target)
    plan_counts = _summarize_plan(all_actions)
    kept_actions = [a for a in all_actions if a.action in KEPT_ACTION_KINDS]

    output: dict[str, object] = {
        "target": str(target),
        "dry_run": dry_run,
        "pre_manifest_version": pre_version,
        "plan_counts": plan_counts,
        "kept_action_count": len(kept_actions),
        "kept_actions": [_action_to_dict(a) for a in kept_actions],
    }

    if dry_run:
        output["applier_results"] = None
        output["post_manifest_version"] = pre_version
        return output

    results = execute_upgrade(
        target,
        kept_actions,
        force=False,
        enforce_isolation=False,
        update_manifest=False,
    )
    post_manifest = read_manifest(target / "groundtruth.toml")
    post_version = post_manifest.scaffold_version if post_manifest else None

    output["applier_results"] = results
    output["post_manifest_version"] = post_version
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scaffold_upgrade_tier_a_apply",
        description="Apply Tier A subset of GT-KB scaffold upgrade.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=REPO_ROOT,
        help="Target project root (default: GT-KB repo root).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan and filter only; do not call execute_upgrade.",
    )
    args = parser.parse_args(argv)

    target = args.target.resolve()
    output = apply_tier_a(target, dry_run=args.dry_run)
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
