"""Discover orphan work-item project memberships in MemBase.

Read-only discovery script for the gtkb-orphan-wi-membership-discovery-slice-1
bridge thread (WI-3397). Produces:

- JSON **inventory artifact** at
  ``.gtkb-state/orphan-wi-discovery/<run-id>/report.json`` enumerating each
  orphan WI by recoverability class with stable schema fields.
- Markdown **review packet** at
  ``.gtkb-state/orphan-wi-discovery/<run-id>/summary.md`` summarizing the
  inventory for the future Slice 2 backfill bridge thread.

An *orphan* is a WI in ``current_work_items`` with ``resolution_status='open'``
that has **no active row** (status='active' OR status IS NULL) in
``project_work_item_memberships``. The legacy ``current_work_items.project_name``
field is informational only; the canonical authority is the membership table.

Recoverability classification (highest-confidence first):

1. ``recoverable_via_source_spec`` (confidence 0.95) - WI has
   ``source_spec_id``; the spec is linked to a project via
   ``current_project_artifact_links`` (artifact_type='specification').
2. ``recoverable_via_bridge_thread`` (confidence 0.85) - WI's ``change_reason``
   contains a ``bridge/<slug>-NNN.md`` path; the bridge file's parent project
   can be derived via ``current_project_artifact_links``
   (artifact_type='bridge_thread') or parsed from the bridge file itself.
3. ``recoverable_via_id_match`` (confidence 0.80) - WI id prefix matches a
   project id prefix (e.g., ``WI-GTKB-GOV-CODE-QUALITY-BASELINE-SLICE-2``
   matches ``PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE``).
4. ``recoverable_via_title_match`` (confidence 0.70) - WI title's leading
   token sequence matches a project's name prefix.
5. ``unrecoverable`` (confidence 0.00) - none of the above heuristics yield
   a candidate project.

Outputs under ``.gtkb-state/orphan-wi-discovery/`` are runtime-only (gitignored
per ``.gtkb-state/`` convention). The bridge file is the durable governed
evidence; the JSON/markdown are working artifacts for the Slice 2 backfill
review packet.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
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


RECOVERABILITY_CLASSES = (
    "recoverable_via_source_spec",
    "recoverable_via_bridge_thread",
    "recoverable_via_id_match",
    "recoverable_via_title_match",
    "unrecoverable",
)

CONFIDENCE_BY_CLASS = {
    "recoverable_via_source_spec": 0.95,
    "recoverable_via_bridge_thread": 0.85,
    "recoverable_via_id_match": 0.80,
    "recoverable_via_title_match": 0.70,
    "unrecoverable": 0.00,
}

_BRIDGE_PATH_RE = re.compile(r"bridge/([a-z0-9][a-z0-9\-]*?)-\d{3}\.md", re.IGNORECASE)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _default_run_id() -> str:
    return "audit-" + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _open_db(db_path: Path) -> KnowledgeDB:
    return KnowledgeDB(db_path)


def _fetch_open_work_items(db: KnowledgeDB) -> list[dict[str, Any]]:
    """Return all open work items per the proposal's scope."""
    return db.list_work_items(resolution_status="open")


def _fetch_active_memberships(db: KnowledgeDB) -> dict[str, str]:
    """Return {work_item_id: project_id} for active membership rows."""
    conn = db._get_conn()  # noqa: SLF001 - read-only access of the connection
    rows = conn.execute(
        """SELECT work_item_id, project_id FROM project_work_item_memberships
           WHERE status = 'active' OR status IS NULL"""
    ).fetchall()
    return {r["work_item_id"]: r["project_id"] for r in rows}


def _fetch_v1_creators(db: KnowledgeDB, orphan_ids: list[str]) -> dict[str, str]:
    """Return {work_item_id: version_1_changed_by} for each orphan WI.

    Per GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 append-only versioning, version=1
    is the immutable creator row. Subsequent migrations append version>=2 rows
    that overwrite mutable fields like ``changed_by`` on the "current" view,
    but version=1 retains the original creator. This is the stable origin
    signal required by acceptance criterion 4 (root-cause attribution).
    """
    if not orphan_ids:
        return {}
    conn = db._get_conn()  # noqa: SLF001 - read-only access of the connection
    placeholders = ",".join("?" for _ in orphan_ids)
    rows = conn.execute(
        f"SELECT id, changed_by FROM work_items "  # noqa: S608 - placeholders are int-count derived
        f"WHERE id IN ({placeholders}) AND version = 1",
        list(orphan_ids),
    ).fetchall()
    return {r["id"]: r["changed_by"] for r in rows}


def _fetch_spec_to_project(db: KnowledgeDB) -> dict[str, str]:
    """Return {spec_id: project_id} from current_project_artifact_links."""
    conn = db._get_conn()  # noqa: SLF001
    rows = conn.execute(
        """SELECT artifact_ref, project_id FROM current_project_artifact_links
           WHERE artifact_type = 'specification'
             AND (status = 'active' OR status IS NULL)"""
    ).fetchall()
    return {r["artifact_ref"]: r["project_id"] for r in rows}


def _fetch_bridge_to_project(db: KnowledgeDB) -> dict[str, str]:
    """Return {bridge_thread_slug: project_id} from current_project_artifact_links."""
    conn = db._get_conn()  # noqa: SLF001
    rows = conn.execute(
        """SELECT artifact_ref, project_id FROM current_project_artifact_links
           WHERE artifact_type = 'bridge_thread'
             AND (status = 'active' OR status IS NULL)"""
    ).fetchall()
    return {r["artifact_ref"]: r["project_id"] for r in rows}


def _fetch_project_index(db: KnowledgeDB) -> list[tuple[str, str]]:
    """Return [(project_id, project_name)] for active projects."""
    conn = db._get_conn()  # noqa: SLF001
    rows = conn.execute(
        """SELECT id, name FROM current_projects
           WHERE status = 'active'
           ORDER BY LENGTH(id) DESC, LENGTH(name) DESC"""
    ).fetchall()
    return [(r["id"], r["name"]) for r in rows]


def _classify_orphan(
    wi: dict[str, Any],
    spec_to_project: dict[str, str],
    bridge_to_project: dict[str, str],
    project_index: list[tuple[str, str]],
) -> dict[str, Any]:
    """Classify a single orphan WI; return classification metadata dict."""
    wi_id = wi.get("id") or ""
    title = wi.get("title") or ""
    source_spec_id = wi.get("source_spec_id")
    change_reason = wi.get("change_reason") or ""

    # Class 1: source_spec_id linkage
    if source_spec_id:
        project_id = spec_to_project.get(source_spec_id)
        if project_id:
            return {
                "recoverability_class": "recoverable_via_source_spec",
                "candidate_project_id": project_id,
                "evidence_path": f"source_spec_id={source_spec_id}",
                "confidence_score": CONFIDENCE_BY_CLASS["recoverable_via_source_spec"],
            }

    # Class 2: bridge-thread reference in change_reason
    bridge_match = _BRIDGE_PATH_RE.search(change_reason)
    if bridge_match:
        slug = bridge_match.group(1)
        # Try both with-and-without version-number variants
        project_id = bridge_to_project.get(slug)
        if project_id:
            return {
                "recoverability_class": "recoverable_via_bridge_thread",
                "candidate_project_id": project_id,
                "evidence_path": f"change_reason cites bridge thread '{slug}'",
                "confidence_score": CONFIDENCE_BY_CLASS["recoverable_via_bridge_thread"],
            }

    # Class 3: WI id prefix matches project id prefix
    # E.g., WI-GTKB-GOV-CODE-QUALITY-BASELINE-SLICE-2 → PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE
    if wi_id.startswith("WI-"):
        wi_id_body = wi_id[3:]  # strip 'WI-'
        for project_id, _ in project_index:
            if not project_id.startswith("PROJECT-"):
                continue
            project_body = project_id[8:]  # strip 'PROJECT-'
            if wi_id_body.startswith(project_body + "-") or wi_id_body == project_body:
                return {
                    "recoverability_class": "recoverable_via_id_match",
                    "candidate_project_id": project_id,
                    "evidence_path": f"WI id prefix matches project id '{project_id}'",
                    "confidence_score": CONFIDENCE_BY_CLASS["recoverable_via_id_match"],
                }

    # Class 4: WI title prefix matches project name prefix
    title_upper = title.upper()
    for project_id, project_name in project_index:
        name_upper = (project_name or "").upper()
        if name_upper and title_upper.startswith(name_upper):
            return {
                "recoverability_class": "recoverable_via_title_match",
                "candidate_project_id": project_id,
                "evidence_path": f"WI title starts with project name '{project_name}'",
                "confidence_score": CONFIDENCE_BY_CLASS["recoverable_via_title_match"],
            }

    # Class 5: unrecoverable
    return {
        "recoverability_class": "unrecoverable",
        "candidate_project_id": None,
        "evidence_path": "no heuristic yielded a candidate project",
        "confidence_score": CONFIDENCE_BY_CLASS["unrecoverable"],
    }


def build_inventory(
    db: KnowledgeDB,
    *,
    run_id: str,
) -> dict[str, Any]:
    """Build the JSON inventory artifact dict."""
    open_wis = _fetch_open_work_items(db)
    active_memberships = _fetch_active_memberships(db)
    spec_to_project = _fetch_spec_to_project(db)
    bridge_to_project = _fetch_bridge_to_project(db)
    project_index = _fetch_project_index(db)

    orphan_ids = [
        (wi.get("id") or "")
        for wi in open_wis
        if (wi.get("id") or "") and (wi.get("id") or "") not in active_memberships
    ]
    v1_creators = _fetch_v1_creators(db, orphan_ids)

    orphan_records: list[dict[str, Any]] = []
    for wi in open_wis:
        wi_id = wi.get("id") or ""
        if wi_id in active_memberships:
            continue  # has active membership; not an orphan
        classification = _classify_orphan(wi, spec_to_project, bridge_to_project, project_index)
        orphan_records.append(
            {
                "id": wi_id,
                "title": wi.get("title") or "",
                "priority": wi.get("priority"),
                "origin": wi.get("origin"),
                "recoverability_class": classification["recoverability_class"],
                "candidate_project_id": classification["candidate_project_id"],
                "confidence_score": classification["confidence_score"],
                "evidence_path": classification["evidence_path"],
                # Root-cause attribution: version=1 immutable creator row per
                # GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 append-only versioning.
                # Fixes NO-GO-008 acceptance criterion 4: identifies which
                # changed_by author *created* the orphan, not whichever later
                # migration touched it.
                "root_cause_changed_by": v1_creators.get(wi_id, "<unknown>"),
                # Diagnostic context: latest mutable changed_by (forensic only;
                # not to be confused with root cause). Kept for explanability
                # of why later migrations may show different attribution.
                "latest_mutator_changed_by": wi.get("changed_by"),
            }
        )

    class_counts = Counter(rec["recoverability_class"] for rec in orphan_records)
    return {
        "run_id": run_id,
        "generated_at": _utc_now_iso(),
        "total_open_wi_count": len(open_wis),
        "orphan_count": len(orphan_records),
        "orphan_count_by_class": {cls: class_counts.get(cls, 0) for cls in RECOVERABILITY_CLASSES},
        "orphans": orphan_records,
    }


def _render_review_packet(inventory: dict[str, Any]) -> str:
    """Render the markdown review packet text."""
    orphans: list[dict[str, Any]] = inventory["orphans"]
    counts = inventory["orphan_count_by_class"]

    lines: list[str] = []
    lines.append(f"# Orphan WI Membership Discovery — Review Packet")
    lines.append("")
    lines.append(f"**Run ID:** `{inventory['run_id']}`")
    lines.append(f"**Generated:** {inventory['generated_at']}")
    lines.append(f"**Total open WIs:** {inventory['total_open_wi_count']}")
    lines.append(f"**Orphan count:** {inventory['orphan_count']}")
    lines.append("")

    # Section 1: orphan-count-by-class
    lines.append("## Orphan Count By Class")
    lines.append("")
    lines.append("| Recoverability Class | Count |")
    lines.append("|---|---:|")
    for cls in RECOVERABILITY_CLASSES:
        lines.append(f"| `{cls}` | {counts.get(cls, 0)} |")
    lines.append("")

    # Section 2: top-10-orphans-by-confidence
    lines.append("## Top 10 Orphans By Confidence")
    lines.append("")
    sorted_by_conf = sorted(orphans, key=lambda r: (-r["confidence_score"], r["id"]))[:10]
    if sorted_by_conf:
        lines.append("| WI ID | Title | Class | Candidate Project | Confidence |")
        lines.append("|---|---|---|---|---:|")
        for rec in sorted_by_conf:
            title_short = (rec["title"] or "")[:60].replace("|", "\\|")
            candidate = rec.get("candidate_project_id") or "—"
            lines.append(
                f"| `{rec['id']}` | {title_short} | `{rec['recoverability_class']}` | "
                f"`{candidate}` | {rec['confidence_score']:.2f} |"
            )
    else:
        lines.append("_No orphans found._")
    lines.append("")

    # Section 3: root-cause-attribution-table
    lines.append("## Root Cause Attribution Table")
    lines.append("")
    if orphans:
        author_counts: Counter = Counter()
        for rec in orphans:
            author = rec.get("root_cause_changed_by") or "<unknown>"
            author_counts[author] += 1
        lines.append("| changed_by | Orphan WI Count |")
        lines.append("|---|---:|")
        for author, n in author_counts.most_common():
            lines.append(f"| `{author}` | {n} |")
    else:
        lines.append("_No orphans to attribute._")
    lines.append("")

    # Section 4: unrecoverable-list-with-resolution-options
    lines.append("## Unrecoverable Orphans — Resolution Options")
    lines.append("")
    unrec = [r for r in orphans if r["recoverability_class"] == "unrecoverable"]
    if unrec:
        lines.append(
            "For each unrecoverable orphan, the Slice 2 backfill thread should "
            "obtain an owner decision via AskUserQuestion. Suggested options:"
        )
        lines.append("")
        lines.append("- **Assign to an existing project** (specify which).")
        lines.append("- **Create a new project** to group this and similar work.")
        lines.append("- **Retire** as no-longer-applicable.")
        lines.append("- **Defer**: leave as orphan pending more context (records the deferral).")
        lines.append("")
        lines.append("| WI ID | Title | Origin | Priority |")
        lines.append("|---|---|---|---|")
        for rec in unrec:
            title_short = (rec["title"] or "")[:80].replace("|", "\\|")
            lines.append(
                f"| `{rec['id']}` | {title_short} | "
                f"`{rec.get('origin') or '—'}` | `{rec.get('priority') or '—'}` |"
            )
    else:
        lines.append("_No unrecoverable orphans._")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.")
    return "\n".join(lines) + "\n"


def emit_outputs(inventory: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    """Write the inventory JSON + review packet markdown to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.json"
    summary_path = output_dir / "summary.md"
    report_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    summary_path.write_text(_render_review_packet(inventory), encoding="utf-8")
    return {"report": report_path, "summary": summary_path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover orphan WI project memberships.")
    parser.add_argument("--run-id", default=None, help="Run ID (default: UTC timestamp).")
    parser.add_argument(
        "--output-dir",
        default=None,
        type=Path,
        help="Output directory (default: .gtkb-state/orphan-wi-discovery/<run-id>/).",
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
        help="Emit only the JSON inventory to stdout; no file outputs.",
    )
    args = parser.parse_args(argv)

    run_id = args.run_id or _default_run_id()
    db = _open_db(args.db_path)
    inventory = build_inventory(db, run_id=run_id)

    if args.json:
        sys.stdout.write(json.dumps(inventory, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    output_dir = args.output_dir or (
        _REPO_ROOT / ".gtkb-state" / "orphan-wi-discovery" / run_id
    )
    paths = emit_outputs(inventory, output_dir)

    sys.stdout.write(
        f"Discovery complete: run_id={run_id} "
        f"orphan_count={inventory['orphan_count']} "
        f"total_open={inventory['total_open_wi_count']}\n"
    )
    sys.stdout.write(f"  Inventory artifact: {paths['report']}\n")
    sys.stdout.write(f"  Review packet:      {paths['summary']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
