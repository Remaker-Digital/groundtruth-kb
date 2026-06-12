"""Promote approval-staged advisory candidates into real work_items rows.

Stage 3 of ``PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001`` (WI-4469),
chartered by owner decision ``DELIB-20261667``.

Default mode is read-only: load ``.gtkb-state/advisory-candidates/candidates.jsonl``,
filter candidates whose latest append-only event is ``staged``, and emit a
deterministic JSON inventory plus a markdown summary.

Mutation is available only through ``--apply --batch-file``. The approved batch
file must carry a non-empty AUQ id, name staged source_keys, satisfy the batch
size cap, and pass a deterministic batch-hash check before the tool calls
``KnowledgeDB.insert_work_item``. Status transitions are appended as successor
events; prior candidate records are never rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

from scripts import advisory_backlog_router as router  # noqa: E402

DEFAULT_PROJECT_ROOT = REPO_ROOT
MAX_BATCH_SIZE = 50
DEFAULT_CHANGED_BY = "advisory-candidate-promote"
APPROVE_DECISIONS = {"approve", "refine"}
VALID_DECISIONS = APPROVE_DECISIONS | {"reject"}


class PromotionError(RuntimeError):
    """Raised for fail-closed promotion validation errors."""


def _now_iso() -> str:
    return router._now_iso()  # noqa: SLF001 - shared timestamp format for candidate events


def _candidate_store_path(project_root: Path) -> Path:
    return project_root / router.CANDIDATE_STORE_RELATIVE


def _status(record: dict[str, Any]) -> str:
    return str(record.get("status") or record.get("event") or "")


def _latest_candidates_with_order(project_root: Path) -> list[dict[str, Any]]:
    events = router.load_candidate_events(project_root)
    first_seen: dict[str, int] = {}
    latest: dict[str, dict[str, Any]] = {}
    for index, event in enumerate(events):
        source_key = str(event.get("source_key") or "")
        if not source_key:
            continue
        first_seen.setdefault(source_key, index)
        record = dict(event)
        record["status"] = _status(record)
        latest[source_key] = record
    return sorted(latest.values(), key=lambda item: (first_seen[str(item["source_key"])], str(item["source_key"])))


def load_staged_candidates(project_root: Path = DEFAULT_PROJECT_ROOT) -> list[dict[str, Any]]:
    """Return candidates whose latest append-only event is ``staged``."""
    return [
        candidate for candidate in _latest_candidates_with_order(project_root) if candidate.get("status") == "staged"
    ]


def _candidate_view(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_key": candidate.get("source_key"),
        "proposed_title": candidate.get("proposed_title") or candidate.get("title"),
        "priority": candidate.get("priority"),
        "severity_token": candidate.get("severity_token"),
        "source": candidate.get("source"),
        "relative_path": candidate.get("relative_path"),
        "advisory_date": candidate.get("advisory_date"),
        "related_bridge_threads": candidate.get("related_bridge_threads"),
    }


def _markdown_summary(candidates: list[dict[str, Any]]) -> str:
    by_priority: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for candidate in candidates:
        priority = str(candidate.get("priority") or "unknown")
        source = str(candidate.get("source") or "unknown")
        by_priority[priority] = by_priority.get(priority, 0) + 1
        by_source[source] = by_source.get(source, 0) + 1

    lines = [
        "# Stage 3 Advisory Candidate Promotion Dry Run",
        "",
        f"- candidate_count: `{len(candidates)}`",
        "",
        "## Counts By Priority",
    ]
    for priority, count in sorted(by_priority.items()):
        lines.append(f"- `{priority}`: {count}")
    lines.extend(["", "## Counts By Source"])
    for source, count in sorted(by_source.items()):
        lines.append(f"- `{source}`: {count}")
    lines.extend(["", "## First 10 Candidates"])
    for candidate in candidates[:10]:
        lines.append(
            f"- `{candidate.get('source_key')}` - {candidate.get('proposed_title') or candidate.get('title') or ''}"
        )
    return "\n".join(lines)


def build_dry_run(project_root: Path = DEFAULT_PROJECT_ROOT) -> dict[str, Any]:
    candidates = [_candidate_view(candidate) for candidate in load_staged_candidates(project_root)]
    return {
        "status": "ok",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "markdown_summary": _markdown_summary(candidates),
    }


def compute_batch_hash(source_keys: list[str], auq_id: str | None) -> str:
    payload = {"auq_id": auq_id or "", "source_keys": sorted(source_keys)}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def prepare_batch(
    out_path: Path,
    *,
    project_root: Path = DEFAULT_PROJECT_ROOT,
    max_batch_size: int = MAX_BATCH_SIZE,
) -> dict[str, Any]:
    if max_batch_size < 0 or max_batch_size > MAX_BATCH_SIZE:
        raise PromotionError(f"max batch size must be between 0 and {MAX_BATCH_SIZE}")
    candidates = load_staged_candidates(project_root)
    source_keys = [str(candidate["source_key"]) for candidate in candidates[:max_batch_size]]
    packet = {
        "auq_id": None,
        "source_keys": source_keys,
        "batch_hash": compute_batch_hash(source_keys, ""),
        "prepared_at": _now_iso(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return packet


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise PromotionError(f"{path} did not contain a JSON object")
    return payload


def _load_batch_file(path: Path) -> dict[str, Any]:
    packet = _read_json(path)
    source_keys = packet.get("source_keys")
    if not isinstance(source_keys, list) or any(not isinstance(item, str) for item in source_keys):
        raise PromotionError("batch file must contain source_keys as a list of strings")
    if len(source_keys) > MAX_BATCH_SIZE:
        raise PromotionError(f"batch contains {len(source_keys)} source_keys; maximum is {MAX_BATCH_SIZE}")
    auq_id = packet.get("auq_id")
    if not isinstance(auq_id, str) or not auq_id.strip():
        raise PromotionError("batch file must contain a non-empty auq_id")
    batch_hash = packet.get("batch_hash")
    if not isinstance(batch_hash, str) or not batch_hash.strip():
        raise PromotionError("batch file must contain a non-empty batch_hash")
    decision = str(packet.get("decision") or packet.get("action") or "approve").strip().lower()
    if decision not in VALID_DECISIONS:
        raise PromotionError("batch decision must be approve, refine, or reject")
    packet["decision"] = decision
    return packet


def _validate_batch(packet: dict[str, Any], *, project_root: Path) -> list[dict[str, Any]]:
    source_keys = list(packet["source_keys"])
    expected_hash = compute_batch_hash(source_keys, packet["auq_id"])
    if packet["batch_hash"] != expected_hash:
        raise PromotionError("batch hash mismatch; restamp the owner-approved batch with its AUQ id")

    latest = {str(candidate["source_key"]): candidate for candidate in _latest_candidates_with_order(project_root)}
    unknown = sorted(source_key for source_key in source_keys if source_key not in latest)
    if unknown:
        raise PromotionError(f"unknown source_key(s): {', '.join(unknown)}")
    non_staged = sorted(source_key for source_key in source_keys if latest[source_key].get("status") != "staged")
    if non_staged:
        raise PromotionError(f"source_key(s) are not staged: {', '.join(non_staged)}")
    return [latest[source_key] for source_key in source_keys]


def _append_candidate_event(
    *,
    project_root: Path,
    candidate: dict[str, Any],
    status: str,
    packet: dict[str, Any],
    changed_by: str,
    work_item_id: str | None = None,
) -> None:
    carried_fields = (
        "source",
        "source_key",
        "relative_path",
        "proposed_title",
        "title",
        "description",
        "priority",
        "severity_token",
        "related_bridge_threads",
        "advisory_date",
        "origin",
        "component",
        "source_spec_id",
    )
    record = {field: candidate.get(field) for field in carried_fields if field in candidate}
    record.update(
        {
            "event": status,
            "status": status,
            "recorded_at": _now_iso(),
            "auq_id": packet["auq_id"],
            "batch_hash": packet["batch_hash"],
            "decision": packet["decision"],
            "changed_by": changed_by,
        }
    )
    if work_item_id is not None:
        record["promoted_work_item_id"] = work_item_id

    store_path = _candidate_store_path(project_root)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def _allocate_next_work_item_id(db: KnowledgeDB) -> str:
    rows = db._get_conn().execute("SELECT id FROM work_items").fetchall()
    max_n = 0
    for row in rows:
        item_id = row[0]
        if not isinstance(item_id, str) or not item_id.startswith("WI-"):
            continue
        suffix = item_id[3:]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return f"WI-{max_n + 1:04d}"


def _candidate_title(candidate: dict[str, Any]) -> str:
    return str(candidate.get("proposed_title") or candidate.get("title") or candidate["source_key"])


def _insert_promoted_work_item(
    db: KnowledgeDB,
    candidate: dict[str, Any],
    *,
    packet: dict[str, Any],
    changed_by: str,
) -> dict[str, Any]:
    work_item_id = _allocate_next_work_item_id(db)
    if db.get_work_item(work_item_id) is not None:
        raise PromotionError(f"allocated id {work_item_id} already exists; retry the command")
    change_reason = (
        f"Stage 3 promotion; approved by {packet['auq_id']}; batch_hash {packet['batch_hash']}; per DELIB-20261667 D5."
    )
    row = db.insert_work_item(
        id=work_item_id,
        title=_candidate_title(candidate),
        origin=str(candidate.get("origin") or router.ORIGIN),
        component=str(candidate.get("component") or router.WORK_ITEM_COMPONENT),
        resolution_status=router.RESOLUTION_STATUS,
        changed_by=changed_by,
        change_reason=change_reason,
        description=candidate.get("description"),
        source_spec_id=str(candidate.get("source_spec_id") or router.SOURCE_SPEC_ID),
        priority=candidate.get("priority"),
        stage="backlogged",
        approval_state="auq_resolved",
        source_owner_directive=f"Per-batch owner AUQ {packet['auq_id']}",
        source_deliberation_query=f"Stage 3 advisory candidate {candidate['source_key']}",
        related_deliberation_ids=str(candidate["source_key"]),
        related_spec_ids_at_creation=json.dumps([router.SOURCE_SPEC_ID]),
        related_bridge_threads=candidate.get("related_bridge_threads"),
        acceptance_summary="Promoted from Stage 3 advisory candidate after owner batch AUQ.",
        regression_visibility="visible",
    )
    if row is None:
        raise PromotionError(f"insert_work_item returned no row for {work_item_id}")
    return row


def apply_batch(
    *,
    batch_file: Path,
    project_root: Path = DEFAULT_PROJECT_ROOT,
    db_path: Path | None = None,
    changed_by: str = DEFAULT_CHANGED_BY,
) -> dict[str, Any]:
    packet = _load_batch_file(batch_file)
    candidates = _validate_batch(packet, project_root=project_root)

    promoted_ids: list[str] = []
    rejected_keys: list[str] = []
    if packet["decision"] == "reject":
        for candidate in candidates:
            _append_candidate_event(
                project_root=project_root,
                candidate=candidate,
                status="rejected",
                packet=packet,
                changed_by=changed_by,
            )
            rejected_keys.append(str(candidate["source_key"]))
        return {
            "status": "applied",
            "decision": packet["decision"],
            "batch_hash": packet["batch_hash"],
            "auq_id": packet["auq_id"],
            "promoted_count": 0,
            "promoted_ids": [],
            "rejected_source_keys": rejected_keys,
            "rejected_count": len(rejected_keys),
        }

    db = KnowledgeDB(db_path or (project_root / "groundtruth.db"))
    for candidate in candidates:
        row = _insert_promoted_work_item(db, candidate, packet=packet, changed_by=changed_by)
        promoted_ids.append(str(row["id"]))
        _append_candidate_event(
            project_root=project_root,
            candidate=candidate,
            status="promoted",
            packet=packet,
            changed_by=changed_by,
            work_item_id=str(row["id"]),
        )

    return {
        "status": "applied",
        "decision": packet["decision"],
        "batch_hash": packet["batch_hash"],
        "auq_id": packet["auq_id"],
        "promoted_count": len(promoted_ids),
        "promoted_ids": promoted_ids,
        "promoted_source_keys": [str(candidate["source_key"]) for candidate in candidates],
        "rejected_source_keys": [],
        "rejected_count": 0,
    }


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--prepare-batch", type=Path)
    parser.add_argument("--max-batch-size", type=int, default=MAX_BATCH_SIZE)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--batch-file", type=Path)
    parser.add_argument("--changed-by", default=DEFAULT_CHANGED_BY)
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    db_path = args.db if args.db is not None else project_root / "groundtruth.db"
    try:
        if args.apply:
            if not args.batch_file:
                raise PromotionError("--apply requires --batch-file")
            _emit(
                apply_batch(
                    batch_file=args.batch_file,
                    project_root=project_root,
                    db_path=db_path,
                    changed_by=args.changed_by,
                )
            )
            return 0
        if args.prepare_batch:
            packet = prepare_batch(
                args.prepare_batch,
                project_root=project_root,
                max_batch_size=args.max_batch_size,
            )
            _emit({"status": "prepared", "packet": packet, "path": args.prepare_batch.as_posix()})
            return 0
        _emit(build_dry_run(project_root))
        return 0
    except PromotionError as exc:
        _emit({"status": "error", "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
