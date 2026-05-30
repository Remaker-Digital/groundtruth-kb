#!/usr/bin/env python3
"""Read-only inventory for the verified-untested spec hygiene cluster (Slice 1).

Bridge thread: ``gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory``
(Codex GO at ``-006``). Source work items: WI-3178, WI-3179, WI-3180, WI-3181,
WI-3182. Project authorization:
``PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001`` (owner decision
``DELIB-2511``).

In-scope specs (all currently ``status='implemented'`` requirement rows whose
linked test coverage is suspected weak): SPEC-1076, SPEC-1078, SPEC-0661,
SPEC-0811, SPEC-1138.

This slice is STRICTLY READ-ONLY against MemBase. It never writes to
``groundtruth.db``; it only SELECTs through the ``groundtruth_kb`` read API and
statically parses test files on disk. The only writes it performs are the two
generated artifacts under ``.gtkb-state/verified-untested-spec-hygiene-cluster/``.

Outputs:

- ``inventory-manifest.json`` - one record per in-scope spec with current spec
  state, linked tests, open work-item context, on-disk test-symbol presence,
  result history, a closed-vocabulary classification, the classification
  reason, and a recommended Slice 2 action.
- ``inventory-summary.md`` - per-spec recommended Slice 2 actions plus
  classification counts.

Classification is deterministic: it is a pure function of the spec text, the
linked test rows, and the on-disk test-symbol probe. The five buckets are:

- ``fixable_test_present`` - a linked test resolves on disk; Slice 2 can
  strengthen its assertions in place.
- ``live_server_required_test`` - the spec describes an HTTP endpoint /
  service surface; meaningful verification needs a live server harness.
- ``performance_oracle_required_test`` - the spec states a timing / budget /
  percentile requirement; meaningful verification needs a performance oracle.
- ``behavioral_mismatch`` - a linked test row exists but its file/function are
  absent on disk; recorded coverage does not match reality.
- ``unresolvable_in_scope`` - no linked test and no live-server / performance
  signal; the right Slice 2 action cannot be determined from current evidence.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# In-scope specs for this cluster. Order is significant: it fixes the record
# order in the manifest so output is deterministic for fixed inputs.
IN_SCOPE_SPECS: tuple[str, ...] = (
    "SPEC-1076",
    "SPEC-1078",
    "SPEC-0661",
    "SPEC-0811",
    "SPEC-1138",
)

DEFAULT_OUTPUT_DIR = Path(".gtkb-state/verified-untested-spec-hygiene-cluster")
MANIFEST_FILENAME = "inventory-manifest.json"
SUMMARY_FILENAME = "inventory-summary.md"
SCHEMA_VERSION = 1

BRIDGE_THREAD = "gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory"
PAUTH_ID = "PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001"
OWNER_DECISION = "DELIB-2511"

# Closed classification vocabulary.
BUCKET_FIXABLE = "fixable_test_present"
BUCKET_LIVE_SERVER = "live_server_required_test"
BUCKET_PERFORMANCE = "performance_oracle_required_test"
BUCKET_BEHAVIORAL = "behavioral_mismatch"
BUCKET_UNRESOLVABLE = "unresolvable_in_scope"

ALL_BUCKETS: tuple[str, ...] = (
    BUCKET_FIXABLE,
    BUCKET_LIVE_SERVER,
    BUCKET_PERFORMANCE,
    BUCKET_BEHAVIORAL,
    BUCKET_UNRESOLVABLE,
)

# Timing / budget / percentile terms => needs a performance oracle. Checked
# first because a perf requirement is a stronger signal than the endpoint it
# may also mention.
PERFORMANCE_KEYWORDS: tuple[str, ...] = (
    "p50",
    "p90",
    "p99",
    "timeout",
    "latency",
    "throughput",
    "budget",
    "milliseconds",
    "ms ",
    "ms,",
    "ms.",
    "response time",
    "sla",
)

# HTTP / service-surface terms => needs a live server harness.
LIVE_SERVER_KEYWORDS: tuple[str, ...] = (
    "endpoint",
    "post /",
    "get /",
    "put /",
    "delete /",
    "patch /",
    "superadmin_api",
    "rest api",
    "http",
)

RECOMMENDED_SLICE2_ACTION: dict[str, str] = {
    BUCKET_FIXABLE: (
        "Strengthen the existing linked test's assertions to meaningfully "
        "verify the spec obligation; no new harness required."
    ),
    BUCKET_LIVE_SERVER: (
        "Author an integration test against a live or ephemeral server "
        "instance in a Slice that provisions the server harness; out of "
        "pure-unit scope."
    ),
    BUCKET_PERFORMANCE: (
        "Author a performance test that measures the stated percentile / "
        "budget against a timing oracle; requires a load/timing harness."
    ),
    BUCKET_BEHAVIORAL: (
        "Reconcile the linked test record with disk reality (recreate the "
        "test or correct the coverage record) before strengthening assertions."
    ),
    BUCKET_UNRESOLVABLE: (
        "Escalate to owner/triage: current evidence is insufficient to choose "
        "a Slice 2 verification approach within this cluster's scope."
    ),
}


class SpecReader(Protocol):
    """Minimal read surface the inventory needs.

    ``KnowledgeDB`` satisfies this in production; tests inject a lightweight
    fake so they never touch live ``groundtruth.db``.
    """

    def get_spec(self, spec_id: str) -> dict[str, Any] | None: ...

    def get_tests_for_spec(self, spec_id: str) -> list[dict[str, Any]]: ...

    def get_test_coverage_for_spec(self, spec_id: str) -> list[dict[str, Any]]: ...

    def get_open_work_items(self) -> list[dict[str, Any]]: ...


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def probe_test_on_disk(project_root: Path, test: dict[str, Any]) -> dict[str, Any]:
    """Statically probe whether a linked test's file and symbol exist on disk.

    Static only: never imports or executes the test module. For ``.py`` files
    the symbol check uses ``ast``; for other files it falls back to a literal
    substring search for the function name.
    """
    test_file = test.get("test_file")
    test_function = test.get("test_function")
    result: dict[str, Any] = {
        "test_id": test.get("id"),
        "test_file": test_file,
        "test_function": test_function,
        "file_present": False,
        "function_present": False,
    }
    if not test_file:
        return result
    path = project_root / test_file
    if not path.is_file():
        return result
    result["file_present"] = True
    if not test_function:
        return result
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return result
    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError:
            result["function_present"] = f"def {test_function}" in text
        else:
            names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
            result["function_present"] = test_function in names
    else:
        result["function_present"] = test_function in text
    return result


def classify_spec(
    spec: dict[str, Any],
    linked_tests: list[dict[str, Any]],
    disk_probes: list[dict[str, Any]],
) -> tuple[str, str]:
    """Return ``(bucket, reason)``. Pure function of the inputs.

    Rule order is deliberate: performance and live-server signals are intrinsic
    to the requirement and dominate; only when neither fires do we fall back to
    test-presence reasoning.
    """
    haystack = f"{spec.get('title', '')} {spec.get('description', '')}".lower()

    perf_hits = [kw for kw in PERFORMANCE_KEYWORDS if kw in haystack]
    if perf_hits:
        return (
            BUCKET_PERFORMANCE,
            "Spec text contains performance/timing terms "
            f"{sorted(set(h.strip() for h in perf_hits))}; meaningful "
            "verification needs a performance oracle (load harness + "
            "percentile/budget measurement), which is out of unit-test scope.",
        )

    server_hits = [kw for kw in LIVE_SERVER_KEYWORDS if kw in haystack]
    if server_hits:
        return (
            BUCKET_LIVE_SERVER,
            "Spec text contains HTTP/service-surface terms "
            f"{sorted(set(server_hits))}; meaningful verification needs a live "
            "server harness (integration test), which is out of pure-unit scope.",
        )

    resolved = [p for p in disk_probes if p.get("function_present")]
    if linked_tests and resolved:
        resolved_ids = [p.get("test_id") for p in resolved]
        return (
            BUCKET_FIXABLE,
            f"{len(resolved)} linked test function(s) {resolved_ids} resolve on "
            "disk; Slice 2 can strengthen their assertions in place without a "
            "new harness.",
        )

    if linked_tests and not resolved:
        return (
            BUCKET_BEHAVIORAL,
            "Linked test record(s) exist but the referenced file/function are "
            "absent on disk; the recorded coverage does not match reality and "
            "must be reconciled before strengthening.",
        )

    return (
        BUCKET_UNRESOLVABLE,
        "No linked test and no live-server/performance signal in the spec text; "
        "the right Slice 2 action cannot be determined from current evidence.",
    )


def _open_work_items_for_spec(open_work_items: list[dict[str, Any]], spec_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for wi in open_work_items:
        if wi.get("source_spec_id") == spec_id:
            items.append(
                {
                    "id": wi.get("id"),
                    "title": wi.get("title"),
                    "resolution_status": wi.get("resolution_status"),
                    "priority": wi.get("priority"),
                    "origin": wi.get("origin"),
                    "component": wi.get("component"),
                }
            )
    items.sort(key=lambda item: str(item.get("id")))
    return items


def build_spec_record(
    reader: SpecReader,
    project_root: Path,
    spec_id: str,
    open_work_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the inventory record for a single spec. Read-only."""
    spec = reader.get_spec(spec_id)
    if spec is None:
        return {
            "spec_id": spec_id,
            "found": False,
            "spec_state": None,
            "linked_tests": [],
            "test_coverage_rows": [],
            "open_work_items": _open_work_items_for_spec(open_work_items, spec_id),
            "disk_probe": [],
            "result_history": [],
            "classification": BUCKET_UNRESOLVABLE,
            "classification_reason": ("Spec id is not present in MemBase; cannot inventory a missing spec."),
            "recommended_slice2_action": RECOMMENDED_SLICE2_ACTION[BUCKET_UNRESOLVABLE],
        }

    linked_tests = reader.get_tests_for_spec(spec_id) or []
    coverage = reader.get_test_coverage_for_spec(spec_id) or []

    linked_test_view = [
        {
            "id": t.get("id"),
            "test_file": t.get("test_file"),
            "test_function": t.get("test_function"),
            "test_class": t.get("test_class"),
            "test_type": t.get("test_type"),
            "last_result": t.get("last_result"),
            "last_executed_at": t.get("last_executed_at"),
        }
        for t in linked_tests
    ]
    linked_test_view.sort(key=lambda t: str(t.get("id")))

    disk_probes = [probe_test_on_disk(project_root, t) for t in linked_tests]
    disk_probes.sort(key=lambda p: str(p.get("test_id")))

    result_history = [
        {
            "test_id": t.get("id"),
            "last_result": t.get("last_result"),
            "last_executed_at": t.get("last_executed_at"),
        }
        for t in linked_tests
    ]
    result_history.sort(key=lambda r: str(r.get("test_id")))

    classification, reason = classify_spec(spec, linked_tests, disk_probes)

    return {
        "spec_id": spec_id,
        "found": True,
        "spec_state": {
            "status": spec.get("status"),
            "type": spec.get("type"),
            "title": spec.get("title"),
            "testability": spec.get("testability"),
            "priority": spec.get("priority"),
            "source_paths": spec.get("source_paths"),
            "implementation_verified_at": spec.get("implementation_verified_at"),
        },
        "linked_tests": linked_test_view,
        "test_coverage_rows": [
            {
                "test_file": c.get("test_file"),
                "test_function": c.get("test_function"),
                "test_class": c.get("test_class"),
                "confidence": c.get("confidence"),
                "match_reason": c.get("match_reason"),
            }
            for c in coverage
        ],
        "open_work_items": _open_work_items_for_spec(open_work_items, spec_id),
        "disk_probe": disk_probes,
        "result_history": result_history,
        "classification": classification,
        "classification_reason": reason,
        "recommended_slice2_action": RECOMMENDED_SLICE2_ACTION[classification],
    }


def build_inventory(
    reader: SpecReader,
    project_root: Path,
    *,
    specs: tuple[str, ...] = IN_SCOPE_SPECS,
    generated_at: str | None = None,
    database_path: str | None = None,
    database_sha256: str | None = None,
    generator_sha256: str | None = None,
) -> dict[str, Any]:
    """Build the full inventory manifest dict. Read-only.

    ``generated_at`` is injectable so tests can pin it and assert byte-identical
    idempotency; production passes a UTC timestamp.
    """
    open_work_items = reader.get_open_work_items() or []
    records = [build_spec_record(reader, project_root, spec_id, open_work_items) for spec_id in specs]
    counts = Counter(record["classification"] for record in records)
    classification_counts = {bucket: counts.get(bucket, 0) for bucket in ALL_BUCKETS}

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "generator": "scripts/inventory_verified_untested_spec_hygiene_cluster.py",
        "generator_sha256": generator_sha256,
        "bridge_thread": BRIDGE_THREAD,
        "project_authorization": PAUTH_ID,
        "owner_decision": OWNER_DECISION,
        "database_path": database_path,
        "database_sha256": database_sha256,
        "in_scope_specs": list(specs),
        "classification_counts": classification_counts,
        "records": records,
    }


def render_summary(manifest: dict[str, Any]) -> str:
    """Render the human-readable Markdown summary from a manifest dict."""
    lines: list[str] = []
    lines.append("# Verified-Untested Spec Hygiene Cluster - Slice 1 Inventory")
    lines.append("")
    lines.append(f"- Generated: {manifest.get('generated_at')}")
    lines.append(f"- Generator: {manifest.get('generator')}")
    lines.append(f"- Generator SHA-256: {manifest.get('generator_sha256')}")
    lines.append(f"- Database: {manifest.get('database_path')}")
    lines.append(f"- Database SHA-256: {manifest.get('database_sha256')}")
    lines.append(f"- Bridge thread: {manifest.get('bridge_thread')}")
    lines.append(f"- Project authorization: {manifest.get('project_authorization')}")
    lines.append(f"- Owner decision: {manifest.get('owner_decision')}")
    lines.append("")
    lines.append("## Classification Counts")
    lines.append("")
    for bucket in ALL_BUCKETS:
        count = manifest.get("classification_counts", {}).get(bucket, 0)
        lines.append(f"- {bucket}: {count}")
    lines.append("")
    lines.append("## Per-Spec Recommended Slice 2 Actions")
    lines.append("")
    lines.append("| Spec | Status | Classification | Recommended Slice 2 Action |")
    lines.append("|------|--------|----------------|----------------------------|")
    for record in manifest.get("records", []):
        spec_state = record.get("spec_state") or {}
        status = spec_state.get("status", "(missing)")
        lines.append(
            f"| {record.get('spec_id')} | {status} | "
            f"{record.get('classification')} | "
            f"{record.get('recommended_slice2_action')} |"
        )
    lines.append("")
    lines.append("## Classification Reasons")
    lines.append("")
    for record in manifest.get("records", []):
        lines.append(f"### {record.get('spec_id')}")
        lines.append("")
        lines.append(f"- Classification: {record.get('classification')}")
        lines.append(f"- Reason: {record.get('classification_reason')}")
        linked = record.get("linked_tests") or []
        lines.append(f"- Linked tests: {len(linked)}")
        wis = record.get("open_work_items") or []
        wi_ids = ", ".join(str(w.get("id")) for w in wis) or "(none)"
        lines.append(f"- Open work items: {wi_ids}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(manifest: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    """Write the manifest JSON and summary Markdown. The ONLY writes performed."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / MANIFEST_FILENAME
    summary_path = output_dir / SUMMARY_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_path.write_text(render_summary(manifest), encoding="utf-8")
    return {"manifest": manifest_path, "summary": summary_path}


def _build_live_reader(db_path: Path) -> SpecReader:
    import sys

    src = str(PROJECT_ROOT / "groundtruth-kb" / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415

    return KnowledgeDB(str(db_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-path",
        type=Path,
        default=PROJECT_ROOT / "groundtruth.db",
        help="Path to groundtruth.db (read-only).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / DEFAULT_OUTPUT_DIR,
        help="Directory for generated inventory artifacts.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root for on-disk test probing.",
    )
    parser.add_argument("--json", action="store_true", help="Print manifest to stdout.")
    args = parser.parse_args(argv)

    reader = _build_live_reader(args.db_path)
    generator_sha = _sha256_file(Path(__file__).resolve())
    db_sha = _sha256_file(args.db_path)
    generated_at = datetime.now(UTC).isoformat()

    manifest = build_inventory(
        reader,
        args.project_root,
        generated_at=generated_at,
        database_path=str(args.db_path),
        database_sha256=db_sha,
        generator_sha256=generator_sha,
    )
    paths = write_outputs(manifest, args.output_dir)

    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        counts = manifest["classification_counts"]
        print(f"Inventory written: {paths['manifest']}")
        print(f"Summary written:   {paths['summary']}")
        print(f"Records: {len(manifest['records'])} | counts: {dict(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
