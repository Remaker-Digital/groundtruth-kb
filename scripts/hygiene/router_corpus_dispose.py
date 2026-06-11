"""Stage 2 advisory-router corpus disposition tool.

Stage 2 of ``PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001`` (WI-4456),
chartered by owner decision ``DELIB-20261667``.

Default mode is read-only: load the newest complete Stage 0 backlog-triage
manifest, filter the conservative retire-candidate platform cohort, enrich it
from ``current_work_items``, and emit deterministic JSON.

Mutation is available only through ``--apply --batch-file``. The batch file
must name the exact owner-approved id set, carry an AUQ id, match the latest
complete manifest, and pass a deterministic batch-hash check before the tool
calls ``KnowledgeDB.update_work_item``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("groundtruth.db")
DEFAULT_BENCHMARKS_DIR = Path(".gtkb-state") / "benchmarks"
ITEMS_FILE = "backlog_triage_items.json"
RUN_FILE = "run.json"
BACKLOG_TRIAGE_BENCHMARK_ID = "backlog_triage"
LABEL_RETIRE_UNAPPROVED_NOISE = "retire_candidate_unapproved_noise"
PLATFORM_SCOPE = "platform"
MAX_BATCH_SIZE = 50
OPEN_STATES = {None, "", "open"}
RUN_ID_RE = re.compile(r"^\d{8}-\d{6}$")

ENRICHMENT_FIELDS = (
    "id",
    "title",
    "changed_at",
    "source_spec_id",
    "priority",
    "origin",
    "component",
    "resolution_status",
)


class DispositionError(RuntimeError):
    """Raised for fail-closed disposition validation errors."""


@dataclass(frozen=True)
class Manifest:
    run_dir: Path
    run_id: str
    idempotency_key: str
    source_commit: str | None
    items: list[dict[str, Any]]


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise DispositionError(f"{path} did not contain a JSON object")
    return payload


def _backlog_result(run_json: dict[str, Any]) -> dict[str, Any] | None:
    for result in run_json.get("results") or []:
        if isinstance(result, dict) and result.get("benchmark_id") == BACKLOG_TRIAGE_BENCHMARK_ID:
            return result
    return None


def _manifest_from_dir(run_dir: Path) -> Manifest | None:
    run_path = run_dir / RUN_FILE
    items_path = run_dir / ITEMS_FILE
    if not run_path.exists() or not items_path.exists():
        return None

    run_json = _read_json(run_path)
    items_json = _read_json(items_path)
    result = _backlog_result(run_json)
    run_id = str(items_json.get("run_id") or "")
    result_run_id = str((result or {}).get("run_id") or "")
    if not run_id or result_run_id != run_id:
        return None

    items = items_json.get("items")
    if not isinstance(items, list):
        raise DispositionError(f"{items_path} is missing an items array")

    return Manifest(
        run_dir=run_dir,
        run_id=run_id,
        idempotency_key=str(run_json.get("idempotency_key") or ""),
        source_commit=(str(result.get("source_commit")) if result and result.get("source_commit") else None),
        items=[item for item in items if isinstance(item, dict)],
    )


def _run_sort_key(manifest: Manifest) -> tuple[int, str, str]:
    if RUN_ID_RE.match(manifest.run_id):
        return (1, manifest.run_id, manifest.run_dir.name)
    return (0, f"{manifest.run_dir.stat().st_mtime_ns:020d}", manifest.run_id)


def load_latest_manifest(benchmarks_dir: Path = DEFAULT_BENCHMARKS_DIR) -> Manifest:
    manifests: list[Manifest] = []
    for child in sorted(benchmarks_dir.iterdir()) if benchmarks_dir.exists() else []:
        if not child.is_dir():
            continue
        manifest = _manifest_from_dir(child)
        if manifest is not None:
            manifests.append(manifest)
    if not manifests:
        raise DispositionError(f"no complete backlog-triage manifest found under {benchmarks_dir}")
    return max(manifests, key=_run_sort_key)


def _cohort_items(manifest: Manifest) -> list[dict[str, Any]]:
    cohort = [
        item
        for item in manifest.items
        if item.get("label") == LABEL_RETIRE_UNAPPROVED_NOISE and item.get("scope") == PLATFORM_SCOPE
    ]
    return sorted(cohort, key=lambda item: str(item.get("id") or ""))


def _ro_connect(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    return con


def _load_current_rows(db_path: Path, ids: list[str]) -> dict[str, dict[str, Any]]:
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    fields = ", ".join(ENRICHMENT_FIELDS)
    con = _ro_connect(db_path)
    try:
        rows = con.execute(
            f"SELECT {fields} FROM current_work_items WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
    finally:
        con.close()
    return {row["id"]: dict(row) for row in rows}


def build_dry_run(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    benchmarks_dir: Path = DEFAULT_BENCHMARKS_DIR,
) -> dict[str, Any]:
    manifest = load_latest_manifest(benchmarks_dir)
    cohort = _cohort_items(manifest)
    ids = [str(item["id"]) for item in cohort if item.get("id")]
    current_rows = _load_current_rows(db_path, ids)

    candidates: list[dict[str, Any]] = []
    missing_ids: list[str] = []
    for item in cohort:
        item_id = str(item.get("id") or "")
        if not item_id:
            continue
        current = current_rows.get(item_id)
        if current is None:
            missing_ids.append(item_id)
            continue
        enriched = {
            "id": item_id,
            "title": current.get("title"),
            "changed_at": current.get("changed_at"),
            "source_spec_id": current.get("source_spec_id"),
            "priority": current.get("priority"),
            "origin": current.get("origin"),
            "component": current.get("component"),
            "resolution_status": current.get("resolution_status"),
            "label": item.get("label"),
            "scope": item.get("scope"),
            "router_generated": item.get("router_generated"),
            "approval_state": item.get("approval_state"),
        }
        candidates.append(enriched)

    summary = _markdown_summary(manifest, candidates, missing_ids)
    return {
        "status": "ok" if not missing_ids else "defect",
        "run_id": manifest.run_id,
        "idempotency_key": manifest.idempotency_key,
        "source_commit": manifest.source_commit,
        "manifest_dir": manifest.run_dir.as_posix(),
        "candidate_count": len(candidates),
        "defects": {"missing_current_work_items": sorted(missing_ids)},
        "candidates": sorted(candidates, key=lambda item: item["id"]),
        "markdown_summary": summary,
    }


def _markdown_summary(manifest: Manifest, candidates: list[dict[str, Any]], missing_ids: list[str]) -> str:
    by_origin: dict[str, int] = {}
    for item in candidates:
        origin = str(item.get("origin") or "unknown")
        by_origin[origin] = by_origin.get(origin, 0) + 1
    lines = [
        "# Stage 2 Router-Corpus Disposition Dry Run",
        "",
        f"- run_id: `{manifest.run_id}`",
        f"- idempotency_key: `{manifest.idempotency_key}`",
        f"- source_commit: `{manifest.source_commit or 'unknown'}`",
        f"- candidate_count: `{len(candidates)}`",
        f"- missing_current_work_items: `{len(missing_ids)}`",
        "",
        "## Counts By Origin",
    ]
    for origin, count in sorted(by_origin.items()):
        lines.append(f"- `{origin}`: {count}")
    lines.extend(["", "## First 10 Candidates"])
    for item in candidates[:10]:
        lines.append(f"- `{item['id']}` - {item.get('title') or ''}")
    return "\n".join(lines)


def compute_batch_hash(ids: list[str], manifest_run_id: str, auq_id: str | None) -> str:
    payload = {
        "auq_id": auq_id or "",
        "ids": sorted(ids),
        "manifest_run_id": manifest_run_id,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def prepare_batch(
    out_path: Path,
    *,
    db_path: Path = DEFAULT_DB_PATH,
    benchmarks_dir: Path = DEFAULT_BENCHMARKS_DIR,
    max_batch_size: int = MAX_BATCH_SIZE,
) -> dict[str, Any]:
    if max_batch_size < 0 or max_batch_size > MAX_BATCH_SIZE:
        raise DispositionError(f"max batch size must be between 0 and {MAX_BATCH_SIZE}")
    dry_run = build_dry_run(db_path=db_path, benchmarks_dir=benchmarks_dir)
    missing = dry_run["defects"]["missing_current_work_items"]
    if missing:
        raise DispositionError(f"refusing to prepare batch; missing current_work_items rows: {', '.join(missing)}")
    ids = [item["id"] for item in dry_run["candidates"][:max_batch_size]]
    packet = {
        "auq_id": None,
        "manifest_run_id": dry_run["run_id"],
        "idempotency_key": dry_run["idempotency_key"],
        "ids": ids,
        "batch_hash": compute_batch_hash(ids, dry_run["run_id"], ""),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return packet


def _load_batch_file(path: Path) -> dict[str, Any]:
    packet = _read_json(path)
    ids = packet.get("ids")
    if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
        raise DispositionError("batch file must contain ids as a list of strings")
    if len(ids) > MAX_BATCH_SIZE:
        raise DispositionError(f"batch contains {len(ids)} ids; maximum is {MAX_BATCH_SIZE}")
    auq_id = packet.get("auq_id")
    if not isinstance(auq_id, str) or not auq_id.strip():
        raise DispositionError("batch file must contain a non-empty auq_id")
    manifest_run_id = packet.get("manifest_run_id")
    if not isinstance(manifest_run_id, str) or not manifest_run_id.strip():
        raise DispositionError("batch file must contain a non-empty manifest_run_id")
    batch_hash = packet.get("batch_hash")
    if not isinstance(batch_hash, str) or not batch_hash.strip():
        raise DispositionError("batch file must contain a non-empty batch_hash")
    return packet


def _validate_batch(
    packet: dict[str, Any],
    *,
    db_path: Path,
    benchmarks_dir: Path,
    confirm_manifest: str,
) -> tuple[Manifest, list[str], dict[str, dict[str, Any]]]:
    manifest = load_latest_manifest(benchmarks_dir)
    manifest_run_id = packet["manifest_run_id"]
    if confirm_manifest != manifest_run_id:
        raise DispositionError("stale manifest: --confirm-manifest does not match the batch file")
    if manifest.run_id != manifest_run_id:
        raise DispositionError("stale manifest: batch file does not match the newest complete manifest on disk")

    ids = sorted(packet["ids"])
    expected_hash = compute_batch_hash(ids, manifest_run_id, packet["auq_id"])
    if packet["batch_hash"] != expected_hash:
        raise DispositionError("batch hash mismatch; re-prepare or restamp the owner-approved batch")

    cohort_ids = {str(item["id"]) for item in _cohort_items(manifest) if item.get("id")}
    unknown = sorted(set(ids) - cohort_ids)
    if unknown:
        raise DispositionError(f"batch id(s) not in retire-candidate platform cohort: {', '.join(unknown)}")

    current_rows = _load_current_rows(db_path, ids)
    missing = sorted(set(ids) - set(current_rows))
    if missing:
        raise DispositionError(f"batch id(s) missing from current_work_items: {', '.join(missing)}")

    non_open = sorted(wid for wid in ids if current_rows[wid].get("resolution_status") not in OPEN_STATES)
    if non_open:
        raise DispositionError(
            f"batch id(s) are no longer open; re-prepare from a fresh dry-run: {', '.join(non_open)}"
        )

    return manifest, ids, current_rows


def apply_batch(
    *,
    batch_file: Path,
    confirm_manifest: str,
    db_path: Path = DEFAULT_DB_PATH,
    benchmarks_dir: Path = DEFAULT_BENCHMARKS_DIR,
    changed_by: str = "router-corpus-dispose",
) -> dict[str, Any]:
    packet = _load_batch_file(batch_file)
    manifest, ids, _current_rows = _validate_batch(
        packet,
        db_path=db_path,
        benchmarks_dir=benchmarks_dir,
        confirm_manifest=confirm_manifest,
    )

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src"))
    from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415

    db = KnowledgeDB(db_path)
    change_reason = (
        f"Stage 2 router-corpus disposition; batch approved by {packet['auq_id']}; "
        f"manifest {manifest.run_id}; batch_hash {packet['batch_hash']}; per DELIB-20261667 D4."
    )
    updated: list[str] = []
    for wid in ids:
        db.update_work_item(
            wid,
            changed_by,
            change_reason,
            owner_approved=True,
            resolution_status="wont_fix",
        )
        updated.append(wid)
    return {
        "status": "applied",
        "run_id": manifest.run_id,
        "batch_hash": packet["batch_hash"],
        "auq_id": packet["auq_id"],
        "updated_ids": updated,
        "updated_count": len(updated),
    }


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--benchmarks-dir", type=Path, default=DEFAULT_BENCHMARKS_DIR)
    parser.add_argument("--prepare-batch", type=Path)
    parser.add_argument("--max-batch-size", type=int, default=MAX_BATCH_SIZE)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--batch-file", type=Path)
    parser.add_argument("--confirm-manifest")
    parser.add_argument("--changed-by", default="router-corpus-dispose")
    args = parser.parse_args(argv)

    try:
        if args.apply:
            if not args.batch_file or not args.confirm_manifest:
                raise DispositionError("--apply requires --batch-file and --confirm-manifest")
            _emit(
                apply_batch(
                    batch_file=args.batch_file,
                    confirm_manifest=args.confirm_manifest,
                    db_path=args.db,
                    benchmarks_dir=args.benchmarks_dir,
                    changed_by=args.changed_by,
                )
            )
            return 0
        if args.prepare_batch:
            _emit(
                {
                    "status": "prepared",
                    "packet": prepare_batch(
                        args.prepare_batch,
                        db_path=args.db,
                        benchmarks_dir=args.benchmarks_dir,
                        max_batch_size=args.max_batch_size,
                    ),
                    "path": args.prepare_batch.as_posix(),
                }
            )
            return 0
        dry_run = build_dry_run(db_path=args.db, benchmarks_dir=args.benchmarks_dir)
        _emit(dry_run)
        return 0 if dry_run["status"] == "ok" else 1
    except DispositionError as exc:
        _emit({"status": "error", "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
