"""Benchmark: Backlog Triage Classifier.

Stage 0 of ``PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001`` (WI-4442), chartered
by owner decision ``DELIB-20261667``.

Read-only. Snapshots the backlog from the ``current_work_items`` view (latest
version per id) and classifies every open work item by deterministic hard
signals: advisory-router provenance, content-hash duplication, bridge/spec/owner
linkage, approval_state, origin, component, age, articulation length, and
``project_name``-vs-membership-table consistency. Partitions platform-scope vs
Agent-Red-scope items (decision D1). Assigns a conservative disposition label
(a *candidate* flag only -- never an instruction to retire) for later stages.

Outputs:

- ``run.json`` / ``summary.md`` via the shared benchmark writer. ``dimensions``
  carries only aggregate scalar counts so the markdown summary stays readable
  (Codex ``-004`` GO implementation note 1).
- ``backlog_triage_items.json`` companion file in the same run directory holding
  the full per-item signal vectors that Stages 1, 2, 4, and 5 consume.

No mutation: the database is opened with a read-only SQLite URI
(``file:...?mode=ro``) and only ``SELECT`` statements are issued. Determinism:
all time-derived signals reference the passed ``window_end`` (never the wall
clock), and every collection is sorted before emission, so two runs over an
identical database produce identical output.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path

from scripts.benchmarks.common import (
    BenchmarkResult,
    benchmark_output_dir,
    current_source_commit,
    new_run_id,
)

BENCHMARK_ID = "backlog_triage"

# resolution_status values treated as "open backlog"; everything else is a
# terminal/non-open disposition (resolved, verified, wont_fix, not_a_defect,
# retired, deferred, ...).
_OPEN_STATES = {None, "", "open"}

_ROUTER_CHANGED_BY = re.compile(r"^advisory-backlog-router\b", re.IGNORECASE)
_AGENT_RED = re.compile(r"AGENT[-_]?RED", re.IGNORECASE)

# Conservative disposition labels. Only the two ``retire_candidate_*`` labels
# flag an item for a later owner batch-approval AUQ; a missing signal never
# forces retirement -- it only marks a candidate.
LABEL_KEEP_SIGNAL = "keep_signal"
LABEL_RETIRE_DUPLICATE = "retire_candidate_duplicate"
LABEL_RETIRE_UNAPPROVED_NOISE = "retire_candidate_unapproved_noise"
LABEL_REVIEW = "review"


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _is_nonempty(value: object) -> bool:
    """True when a JSON-array / text column carries real content.

    Empty strings, ``None``, ``"[]"``, ``"null"``, and whitespace are treated
    as absent so a stored-but-empty JSON array does not count as a link.
    """
    text = _as_text(value).strip()
    return text not in ("", "[]", "null", "{}")


def _age_days(changed_at: str, reference: datetime | None) -> int | None:
    if not changed_at or reference is None:
        return None
    try:
        dt = datetime.fromisoformat(changed_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=reference.tzinfo)
    return (reference - dt).days


def _parse_reference(window_end: str) -> datetime | None:
    if not window_end:
        return None
    try:
        return datetime.fromisoformat(window_end.replace("Z", "+00:00"))
    except ValueError:
        return None


def _content_hash(title: str, description: str) -> str:
    norm = " ".join((title + " " + description).split()).lower()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def _bucket_articulation(length: int) -> str:
    if length == 0:
        return "0_empty"
    if length < 80:
        return "1_lt80"
    if length < 300:
        return "2_80_300"
    if length < 800:
        return "3_300_800"
    return "4_800plus"


def _bucket_age(days: int | None) -> str:
    if days is None:
        return "unknown"
    if days < 7:
        return "a_lt7"
    if days < 30:
        return "b_7_30"
    if days < 60:
        return "c_30_60"
    if days < 120:
        return "d_60_120"
    return "e_120plus"


def _table_exists(con: sqlite3.Connection, name: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE name = ? AND type IN ('table', 'view') LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def _load_memberships(con: sqlite3.Connection) -> dict[str, list[str]]:
    """Map work_item_id -> sorted list of active project ids."""
    if not _table_exists(con, "current_project_work_item_memberships"):
        return {}
    out: dict[str, set[str]] = {}
    rows = con.execute("SELECT work_item_id, project_id, status FROM current_project_work_item_memberships").fetchall()
    for wid, pid, status in rows:
        if status not in (None, "", "active"):
            continue
        out.setdefault(wid, set()).add(pid)
    return {wid: sorted(pids) for wid, pids in out.items()}


def _classify(
    rows: list[sqlite3.Row],
    memberships: dict[str, list[str]],
    reference: datetime | None,
) -> list[dict]:
    """Build the per-item signal vector for every open work item.

    Two passes: pass one computes content hashes so duplicate groups can be
    resolved (canonical = lowest id in a group); pass two assigns the
    conservative disposition label.
    """
    open_items: list[dict] = []
    hash_to_ids: dict[str, list[str]] = {}

    for r in rows:
        resolution = r["resolution_status"]
        if resolution not in _OPEN_STATES:
            continue
        wid = r["id"]
        title = _as_text(r["title"])
        description = _as_text(r["description"])
        acceptance = _as_text(r["acceptance_summary"])
        bridge_linked = _is_nonempty(r["related_bridge_threads"])
        # source_spec_id is intentionally NOT a signal. The advisory-backlog-router stamps
        # source_spec_id='GOV-STANDING-BACKLOG-001' on every item it creates (confirmed 748/748
        # on the live corpus), so counting it would mark ~all router items "spec-linked" and
        # defeat the classifier -- a rubber-stamp signal that GOV-18 (SPEC-1662) forbids.
        # Genuine per-item spec linkage lives in related_spec_ids_at_creation. The boilerplate
        # source_spec_id is still surfaced as the informational has_source_spec_id field.
        spec_linked = _is_nonempty(r["related_spec_ids_at_creation"])
        has_source_spec_id = _is_nonempty(r["source_spec_id"])
        owner_sourced = _is_nonempty(r["source_owner_directive"])
        chash = _content_hash(title, description)
        hash_to_ids.setdefault(chash, []).append(wid)
        member_projects = memberships.get(wid, [])
        project_name_field = _as_text(r["project_name"])
        scope = (
            "agent_red"
            if (_AGENT_RED.search(project_name_field) or any(_AGENT_RED.search(pid) for pid in member_projects))
            else "platform"
        )
        # project_name field is consistent with memberships when both are empty,
        # or the field names a project the item is actually a member of.
        if not project_name_field and not member_projects:
            name_consistent = True
        elif project_name_field and member_projects:
            name_consistent = any(
                project_name_field in pid or pid.endswith(project_name_field) for pid in member_projects
            )
        else:
            name_consistent = False
        open_items.append(
            {
                "id": wid,
                "version": r["version"],
                "resolution_status": resolution or "open",
                "router_generated": bool(_ROUTER_CHANGED_BY.match(_as_text(r["changed_by"]))),
                "bridge_linked": bridge_linked,
                "spec_linked": spec_linked,
                "has_source_spec_id": has_source_spec_id,
                "owner_sourced": owner_sourced,
                "signal_bearing": bool(bridge_linked or spec_linked or owner_sourced),
                "approval_state": _as_text(r["approval_state"]) or "unset",
                "origin": _as_text(r["origin"]) or "unset",
                "component": _as_text(r["component"]) or "unset",
                "age_days": _age_days(_as_text(r["changed_at"]), reference),
                "articulation_len": len(description) + len(acceptance),
                "content_hash": chash,
                "scope": scope,
                "project_name_field": project_name_field,
                "membership_projects": member_projects,
                "project_name_consistent": name_consistent,
            }
        )

    # Resolve duplicate groups: canonical = lexicographically lowest id.
    canonical = {chash: sorted(ids)[0] for chash, ids in hash_to_ids.items()}
    group_size = {chash: len(ids) for chash, ids in hash_to_ids.items()}

    for item in open_items:
        chash = item["content_hash"]
        is_dup_member = group_size[chash] > 1 and item["id"] != canonical[chash]
        item["duplicate_of"] = canonical[chash] if is_dup_member else None
        if item["signal_bearing"]:
            label = LABEL_KEEP_SIGNAL
        elif is_dup_member:
            label = LABEL_RETIRE_DUPLICATE
        elif item["router_generated"] and item["approval_state"] in ("unapproved", "unset"):
            label = LABEL_RETIRE_UNAPPROVED_NOISE
        else:
            label = LABEL_REVIEW
        item["label"] = label

    open_items.sort(key=lambda d: d["id"])
    return open_items


def _aggregate(rows: list[sqlite3.Row], open_items: list[dict]) -> dict:
    total_rows = len(rows)
    total_open = len(open_items)
    nonopen = sorted(
        Counter((r["resolution_status"] or "open") for r in rows if r["resolution_status"] not in _OPEN_STATES).items()
    )
    by_label = Counter(i["label"] for i in open_items)
    by_scope = Counter(i["scope"] for i in open_items)
    by_approval = Counter(i["approval_state"] for i in open_items)
    by_origin = Counter(i["origin"] for i in open_items)
    artic = Counter(_bucket_articulation(i["articulation_len"]) for i in open_items)
    age = Counter(_bucket_age(i["age_days"]) for i in open_items)
    dup_groups = sorted({i["content_hash"] for i in open_items if i["duplicate_of"] is not None})
    return {
        "total_rows_latest_version": total_rows,
        "total_open": total_open,
        "total_nonopen": total_rows - total_open,
        "nonopen_by_status": dict(nonopen),
        "router_generated": sum(1 for i in open_items if i["router_generated"]),
        "signal_bearing": sum(1 for i in open_items if i["signal_bearing"]),
        "unapproved": sum(1 for i in open_items if i["approval_state"] in ("unapproved", "unset")),
        "duplicate_items": sum(1 for i in open_items if i["duplicate_of"] is not None),
        "duplicate_groups": len(dup_groups),
        "project_name_inconsistent": sum(1 for i in open_items if not i["project_name_consistent"]),
        "by_label": dict(sorted(by_label.items())),
        "by_scope": dict(sorted(by_scope.items())),
        "by_approval_state": dict(sorted(by_approval.items())),
        "by_origin": dict(sorted(by_origin.items())),
        "articulation_buckets": dict(sorted(artic.items())),
        "age_buckets": dict(sorted(age.items())),
    }


def run(window_start, window_end, project_root=None):
    """Read-only backlog classification benchmark.

    Returns a :class:`BenchmarkResult` whose ``value`` is the open-backlog count
    and whose ``dimensions`` are aggregate scalars. The full per-item signal
    vectors are written to ``backlog_triage_items.json`` in the run directory.
    """
    root = Path(project_root or Path(__file__).resolve().parents[2])
    db_path = root / "groundtruth.db"
    reference = _parse_reference(window_end)

    rows: list[sqlite3.Row] = []
    memberships: dict[str, list[str]] = {}
    if db_path.exists():
        con = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        try:
            con.row_factory = sqlite3.Row
            if _table_exists(con, "current_work_items"):
                rows = con.execute(
                    "SELECT id, version, resolution_status, changed_by, changed_at, "
                    "title, description, acceptance_summary, approval_state, origin, "
                    "component, related_bridge_threads, related_spec_ids_at_creation, "
                    "source_spec_id, source_owner_directive, project_name "
                    "FROM current_work_items"
                ).fetchall()
            memberships = _load_memberships(con)
        finally:
            con.close()

    open_items = _classify(rows, memberships, reference)
    dimensions = _aggregate(rows, open_items)

    run_id = new_run_id()
    out_dir = benchmark_output_dir(run_id, project_root=root)
    items_path = out_dir / "backlog_triage_items.json"
    items_path.write_text(
        json.dumps({"run_id": run_id, "items": open_items}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    dimensions["items_file"] = items_path.name
    dimensions["items_count"] = len(open_items)

    return BenchmarkResult(
        run_id=run_id,
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=float(dimensions["total_open"]),
        dimensions=dimensions,
        source_commit=current_source_commit(root),
        source_query=(
            "current_work_items (+current_project_work_item_memberships) "
            "read-only; classified by router-provenance / content-hash / "
            "bridge-spec-owner linkage / approval_state / age / articulation"
        ),
    )
