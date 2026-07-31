#!/usr/bin/env python3
"""Execute the eight frozen context-manifest assertions.

Contract vocabulary: glossary, skills, cli, source-of-truth, project and backlog,
operating context, work-subject, deterministic, byte-equivalent, source_id,
read_route, high-churn, live-query-only, role-bootstrap, before-activity,
cannot-alter-role, one-active, ops, deliberation, build, test, spec, project,
missing, expired, unavailable, conflict, recovery, essential-context,
token-budget, must-not-discard.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.activity.profiles import CANONICAL_ACTIVITY_ORDER  # noqa: E402
from groundtruth_kb.context.manifest import (  # noqa: E402
    REQUIRED_CATEGORIES,
    STACK_ORDER,
    ContextManifestError,
    assemble_context_manifest,
    canonical_manifest_bytes,
    validate_manifest_resource_semantics,
)


def run_contract() -> dict:
    fixed = datetime(2026, 7, 13, tzinfo=UTC)
    manifests = {
        activity: assemble_context_manifest(activity=activity, role="Prime Builder", generated_at=fixed)
        for activity in CANONICAL_ACTIVITY_ORDER
    }
    sample = manifests["build"]
    repeated = assemble_context_manifest(activity="build", role="Prime Builder", generated_at=fixed)
    all_items = [item for manifest in manifests.values() for item in manifest["items"]]
    semantic_resource_closure = True
    try:
        for manifest in manifests.values():
            validate_manifest_resource_semantics(manifest)
    except ContextManifestError:
        semantic_resource_closure = False
    freshness_failure = False
    try:
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=fixed,
            evaluated_at=fixed + timedelta(seconds=121),
        )
    except ContextManifestError as exc:
        freshness_failure = "expired" in str(exc) and "recovery=" in str(exc)
    budget_failure = False
    try:
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=fixed,
            hard_token_budget=1,
        )
    except ContextManifestError as exc:
        budget_failure = all(token in str(exc) for token in ("essential-context", "token-budget", "must-not-discard"))
    assertions = [
        {
            "id": "CTX-MANIFEST-A1",
            "status": "PASS"
            if all(
                all(
                    set(categories) == set(REQUIRED_CATEGORIES)
                    for categories in manifest["categories_by_layer"].values()
                )
                for manifest in manifests.values()
            )
            else "FAIL",
            "evidence": {activity: manifest["categories_by_layer"] for activity, manifest in manifests.items()},
        },
        {
            "id": "CTX-MANIFEST-A2",
            "status": "PASS" if canonical_manifest_bytes(sample) == canonical_manifest_bytes(repeated) else "FAIL",
            "evidence": {"byte_equivalent": canonical_manifest_bytes(sample) == canonical_manifest_bytes(repeated)},
        },
        {
            "id": "CTX-MANIFEST-A3",
            "status": "PASS"
            if semantic_resource_closure
            and all(item["source_id"] and item["read_route"] and item["source_version_or_hash"] for item in all_items)
            else "FAIL",
            "evidence": {
                "closed_items": len(all_items),
                "resource_semantics_exact": semantic_resource_closure,
            },
        },
        {
            "id": "CTX-MANIFEST-A4",
            "status": "PASS"
            if all(
                item["content"] is None and item["disposition"] == "live-query-only"
                for item in all_items
                if item["churn_class"] in {"project_status", "work_item_status"}
            )
            else "FAIL",
            "evidence": [item["id"] for item in all_items if item["disposition"] == "live-query-only"],
        },
        {
            "id": "CTX-MANIFEST-A5",
            "status": "PASS"
            if STACK_ORDER.index("role_bootstrap") < STACK_ORDER.index("activity_overlay")
            and sample["role_bootstrap"] == {"role": "Prime Builder", "cannot_alter_role": True}
            else "FAIL",
            "evidence": {"stack_order": sample["stack_order"], "role": sample["role_bootstrap"]},
        },
        {
            "id": "CTX-MANIFEST-A6",
            "status": "PASS"
            if tuple(manifests) == CANONICAL_ACTIVITY_ORDER
            and all(manifest["active_activity"] == activity for activity, manifest in manifests.items())
            else "FAIL",
            "evidence": list(manifests),
        },
        {
            "id": "CTX-MANIFEST-A7",
            "status": "PASS" if freshness_failure else "FAIL",
            "evidence": {"expired_recovery_visible": freshness_failure},
        },
        {
            "id": "CTX-MANIFEST-A8",
            "status": "PASS" if budget_failure else "FAIL",
            "evidence": {"essential_budget_failure_visible": budget_failure},
        },
    ]
    return {
        "schema_version": 1,
        "status": "PASS" if all(item["status"] == "PASS" for item in assertions) else "FAIL",
        "assertions": assertions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        report = run_contract()
    except ContextManifestError as exc:
        print(f"CONTEXT MANIFESTS: FAIL - {exc}", file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"CONTEXT MANIFESTS: {report['status']}")
        for assertion in report["assertions"]:
            print(f"- {assertion['id']}: {assertion['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
