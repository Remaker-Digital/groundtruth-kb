#!/usr/bin/env python3
"""
Retroactive back-harvest of bridge threads into the Knowledge Database.

One-time sweep that emits one compressed DELIB per bridge thread (not per
file), keyed on source_ref = "bridge/{thread-name}-*.md" with content-hash
idempotence.

Governance:
- Scope bridge: bridge/gtkb-da-harvest-coverage-002.md (Codex scope GO)
- Implementation bridge: bridge/gtkb-da-harvest-coverage-implementation-005.md
  (Codex implementation GO with 5 verification conditions)
- Specs: SPEC-DA-HARVEST-INCLUSION, SPEC-DA-HARVEST-EXCLUSION,
  SPEC-DA-THREAD-COMPRESSION, SPEC-DA-COVERAGE-METRIC,
  SPEC-DA-RETROACTIVE-SWEEP, SPEC-DA-DOCTOR-CHECK,
  SPEC-DA-MECHANICAL-ENFORCE

Usage:
    # Dry run (default) -- emits JSON summary, no DB mutation
    python scripts/retroactive_harvest_bridge_threads.py

    # Execute (mutates DA) -- requires owner approval of dry-run JSON
    python scripts/retroactive_harvest_bridge_threads.py --execute

    # Sample N threads in dry-run output
    python scripts/retroactive_harvest_bridge_threads.py --sample 10

Phase 3 of the implementation plan requires owner review of the dry-run
output before the --execute run.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from datetime import UTC, datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = REPO_ROOT / "bridge"
BRIDGE_INDEX = BRIDGE_DIR / "INDEX.md"
KB_PATH = REPO_ROOT / "groundtruth.db"

FILENAME_VERSION_RE = re.compile(r"^(.+)-(\d{3})\.md$")
_DOC_LINE_RE = re.compile(r"^Document:\s+(.+)$")
_STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+bridge/(.+\.md)$")
_HEADER_COMMENT_KEEPERS = (
    "Prime inserts new document entries",
    "Codex scans for NEW/REVISED",
    "Statuses:",
    "When this file exceeds",
    "STARTUP-PRUNED",
)
_COMMENT_COMPACTION_THRESHOLD_BYTES = 8_000
_COMMENT_COMPACTION_THRESHOLD_LINES = 12


# ---------------------------------------------------------------------------
# Thread identity
# ---------------------------------------------------------------------------


def extract_thread_stem(filename: str) -> str | None:
    """Return the thread name for a bridge filename.

    A bridge file's thread identity is the full filename stem before the final
    -NNN segment. No prefix-based merging is applied: retired parent scope
    threads with prefix-overlapping child implementation/editplan threads stay
    distinct because their FULL stems differ (e.g. `gtkb-da-harvest-coverage`
    vs `gtkb-da-harvest-coverage-implementation`).
    """
    match = FILENAME_VERSION_RE.match(filename)
    return match.group(1) if match else None


@dataclass
class IndexEntry:
    name: str
    versions: list[tuple[str, str]]  # [(status, filename), ...] newest first

    @property
    def latest_status(self) -> str:
        return self.versions[0][0] if self.versions else ""


def parse_active_index(index_path: Path) -> list[IndexEntry]:
    """Parse bridge/INDEX.md into active Document entries (newest-first)."""
    if not index_path.exists():
        return []

    entries: list[IndexEntry] = []
    current_name: str | None = None
    current_versions: list[tuple[str, str]] = []

    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("<!--") or line.startswith("#"):
            continue

        doc_match = _DOC_LINE_RE.match(line)
        if doc_match:
            if current_name is not None:
                entries.append(IndexEntry(name=current_name, versions=current_versions))
            current_name = doc_match.group(1).strip()
            current_versions = []
            continue

        status_match = _STATUS_LINE_RE.match(line)
        if status_match and current_name is not None:
            current_versions.append((status_match.group(1), status_match.group(2)))

    if current_name is not None:
        entries.append(IndexEntry(name=current_name, versions=current_versions))

    return entries


# ---------------------------------------------------------------------------
# Thread-compression collector
# ---------------------------------------------------------------------------


@dataclass
class ThreadRecord:
    thread_name: str
    source_ref: str  # always "bridge/{thread-name}-*.md"
    versions: list[Path]  # in reverse-chronological order when known
    active: bool  # True if in active INDEX
    latest_status: str  # "VERIFIED" for active threads, "ORPHAN" otherwise
    warnings: list[str] = field(default_factory=list)


def group_orphans_by_strict_stem(orphan_files: list[Path]) -> dict[str, list[Path]]:
    """Group orphan bridge files by their exact thread stem.

    No prefix merging. Retired parent scope threads remain distinct from child
    implementation/editplan threads with the same leading prefix.
    """
    groups: dict[str, list[Path]] = defaultdict(list)
    for f in orphan_files:
        stem = extract_thread_stem(f.name)
        if stem is None:
            continue
        groups[stem].append(f)
    return dict(groups)


def collect_compressed_bridge_threads(
    index_path: Path,
    bridge_dir: Path,
) -> list[ThreadRecord]:
    """Return one ThreadRecord per bridge thread (active + orphan)."""
    active_entries = parse_active_index(index_path)
    indexed_files: set[str] = set()
    records: list[ThreadRecord] = []

    for entry in active_entries:
        version_paths = []
        for _status, fname in entry.versions:
            path = bridge_dir / fname
            indexed_files.add(fname)
            if path.exists():
                version_paths.append(path)
        records.append(ThreadRecord(
            thread_name=entry.name,
            source_ref=f"bridge/{entry.name}-*.md",
            versions=version_paths,
            active=True,
            latest_status=entry.latest_status,
        ))

    all_files = [f for f in bridge_dir.glob("*.md") if f.name != "INDEX.md"]
    orphan_files = [f for f in all_files if f.name not in indexed_files]
    orphan_groups = group_orphans_by_strict_stem(orphan_files)

    for stem, files in sorted(orphan_groups.items()):
        files_sorted = sorted(files, reverse=True)
        records.append(ThreadRecord(
            thread_name=stem,
            source_ref=f"bridge/{stem}-*.md",
            versions=files_sorted,
            active=False,
            latest_status="ORPHAN",
        ))

    return records


# ---------------------------------------------------------------------------
# Content synthesis
# ---------------------------------------------------------------------------


_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _extract_heading(body: str, default: str) -> str:
    m = _TITLE_RE.search(body)
    return m.group(1).strip() if m else default


def build_thread_summary(record: ThreadRecord) -> tuple[str, str, str]:
    """Return (title, summary, content) for a compressed thread DELIB."""
    version_count = len(record.versions)
    status_label = record.latest_status or "UNKNOWN"
    title = f"Bridge thread: {record.thread_name} ({version_count} versions, {status_label})"

    first_body = record.versions[0].read_text(encoding="utf-8", errors="ignore") if record.versions else ""
    first_heading = _extract_heading(first_body, record.thread_name)
    summary_preview = first_heading[:200]
    summary = (
        f"Compressed bridge thread '{record.thread_name}' with {version_count} version(s). "
        f"Latest status: {status_label}. {'Active in INDEX.' if record.active else 'Orphan (not in active INDEX).'} "
        f"Heading: {summary_preview}"
    )[:500]

    lines = [
        f"# Bridge Thread: {record.thread_name}",
        "",
        f"- Source ref: `{record.source_ref}`",
        f"- Active in INDEX: {record.active}",
        f"- Latest status: {status_label}",
        f"- Version count: {version_count}",
        "",
        "## Version Trail",
        "",
    ]
    for path in record.versions:
        try:
            size = path.stat().st_size
            body = path.read_text(encoding="utf-8", errors="ignore")
            heading = _extract_heading(body, path.name)
            first_non_heading = ""
            for line in body.splitlines():
                s = line.strip()
                if s and not s.startswith("#") and not s.startswith("-"):
                    first_non_heading = s[:200]
                    break
            lines.append(f"### {path.name} ({size} bytes)")
            lines.append("")
            lines.append(f"**Heading:** {heading}")
            if first_non_heading:
                lines.append("")
                lines.append(f"**First line:** {first_non_heading}")
            lines.append("")
        except OSError as exc:
            lines.append(f"### {path.name} -- UNREADABLE: {exc}")
            lines.append("")

    content = "\n".join(lines)
    return title, summary, content


# ---------------------------------------------------------------------------
# KB loading
# ---------------------------------------------------------------------------


def _load_db(kb_path: str | None):
    sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
    from db import KnowledgeDB  # type: ignore[import-not-found]
    return KnowledgeDB(kb_path or str(KB_PATH))


# ---------------------------------------------------------------------------
# Coverage formula
# ---------------------------------------------------------------------------


def compute_active_bridge_thread_coverage(
    records: list[ThreadRecord],
    db,
) -> dict:
    """Return coverage metrics for active VERIFIED bridge threads.

    Numerator and denominator are both DISTINCT thread-name SETS. Cannot exceed
    100% by construction.
    """
    active_verified: set[str] = {r.thread_name for r in records if r.active and r.latest_status == "VERIFIED"}

    covered: set[str] = set()
    for name in active_verified:
        hits = db.list_deliberations(
            source_type="bridge_thread",
            source_ref=f"bridge/{name}-*.md",
        )
        if hits:
            covered.add(name)

    denom = len(active_verified)
    num = len(covered)
    return {
        "denominator_threads": denom,
        "numerator_threads": num,
        "coverage_pct": round(100.0 * num / denom, 2) if denom else 100.0,
        "uncovered_thread_names": sorted(active_verified - covered),
        "covered_thread_names": sorted(covered),
    }


# ---------------------------------------------------------------------------
# Verified-thread archival + INDEX pruning
# ---------------------------------------------------------------------------


def _write_pruned_index(index_path: Path, archived_thread_names: set[str]) -> int:
    """Remove archived VERIFIED document entries from bridge/INDEX.md.

    Bridge files are never deleted. Only the active coordination entry is
    removed after the corresponding compressed thread row exists in the
    Deliberation Archive.
    """
    if not archived_thread_names or not index_path.exists():
        return 0

    lines = index_path.read_text(encoding="utf-8").splitlines()
    kept: list[str] = []
    removed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        doc_match = _DOC_LINE_RE.match(line.strip())
        if not doc_match:
            kept.append(line)
            i += 1
            continue

        doc_name = doc_match.group(1).strip()
        block: list[str] = [line]
        i += 1
        while i < len(lines) and not _DOC_LINE_RE.match(lines[i].strip()):
            block.append(lines[i])
            i += 1

        if doc_name in archived_thread_names:
            removed += 1
            continue
        kept.extend(block)

    if removed:
        # Collapse excessive blank runs left by removed blocks while preserving
        # the header/comment structure.
        compact: list[str] = []
        blank_run = 0
        for line in kept:
            if line.strip():
                blank_run = 0
                compact.append(line)
            else:
                blank_run += 1
                if blank_run <= 2:
                    compact.append(line)
        index_path.write_text("\n".join(compact).rstrip() + "\n", encoding="utf-8")
    return removed


def _comment_marker(block_text: str) -> str:
    upper = block_text.upper()
    if "RETIRED" in upper:
        return "RETIRED"
    if "PAUSED" in upper:
        return "PAUSED"
    if "DEFERRAL" in upper or "DEFERRED" in upper:
        return "DEFERRED"
    if "PARKED" in upper:
        return "PARKED"
    return "HISTORICAL"


def _compact_comment_block(block: list[str]) -> tuple[list[str], int, int]:
    comment_lines = [line for line in block if line.strip().startswith("<!--")]
    block_bytes = sum(len((line + "\n").encode("utf-8")) for line in block)
    if (
        len(comment_lines) <= _COMMENT_COMPACTION_THRESHOLD_LINES
        and block_bytes <= _COMMENT_COMPACTION_THRESHOLD_BYTES
    ):
        return block, 0, 0

    marker = _comment_marker("\n".join(block))
    compact = [
        (
            f"<!-- STARTUP-PRUNED {marker} COMMENT BLOCK: removed "
            f"{len(comment_lines)} comment lines / {block_bytes} bytes from active bridge/INDEX.md. "
            "Original text was archived to the Deliberation Archive before compaction; "
            "bridge files remain on disk. Preserve this marker's pause/retirement meaning. -->"
        ),
        "",
    ]
    return compact, len(comment_lines), block_bytes


def _compact_index_comments(index_path: Path, db) -> dict:
    """Archive then compact oversized INDEX comments that bloat startup context."""
    if not index_path.exists():
        return {"compacted_blocks": 0, "removed_comment_lines": 0, "removed_bytes": 0, "archive_id": None}

    original = index_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    kept: list[str] = []
    removed_lines = 0
    removed_bytes = 0
    compacted_blocks = 0
    pre_document = True
    preamble_pruned = False
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("Document: "):
            pre_document = False
            kept.append(line)
            i += 1
            continue

        if line.strip().startswith("<!--") or (not line.strip() and i + 1 < len(lines) and lines[i + 1].strip().startswith("<!--")):
            block: list[str] = []
            while i < len(lines) and (lines[i].strip().startswith("<!--") or not lines[i].strip()):
                block.append(lines[i])
                i += 1

            if pre_document:
                keep_block = [
                    item for item in block
                    if (
                        not item.strip()
                        or item.startswith("#")
                        or any(keeper in item for keeper in _HEADER_COMMENT_KEEPERS)
                    )
                ]
                dropped = [item for item in block if item not in keep_block and item.strip().startswith("<!--")]
                if dropped:
                    preamble_pruned = True
                    removed_lines += len(dropped)
                    removed_bytes += sum(len((item + "\n").encode("utf-8")) for item in dropped)
                kept.extend(keep_block)
                continue

            compacted, block_removed_lines, block_removed_bytes = _compact_comment_block(block)
            if block_removed_lines:
                compacted_blocks += 1
                removed_lines += block_removed_lines
                removed_bytes += block_removed_bytes
            kept.extend(compacted)
            continue

        kept.append(line)
        i += 1

    if preamble_pruned:
        insert_at = 0
        while insert_at < len(kept) and (kept[insert_at].startswith("#") or not kept[insert_at].strip() or kept[insert_at].strip().startswith("<!--")):
            insert_at += 1
        kept.insert(
            insert_at,
            "<!-- STARTUP-PRUNED HISTORICAL PREAMBLE: retired maintenance comments removed from active bridge/INDEX.md after DA archival. -->",
        )
        compacted_blocks += 1

    compact_lines: list[str] = []
    blank_run = 0
    for line in kept:
        if line.strip():
            blank_run = 0
            compact_lines.append(line)
        else:
            blank_run += 1
            if blank_run <= 2:
                compact_lines.append(line)
    compacted_text = "\n".join(compact_lines).rstrip() + "\n"

    if not removed_lines:
        if compacted_text != original:
            index_path.write_text(compacted_text, encoding="utf-8")
        return {"compacted_blocks": 0, "removed_comment_lines": 0, "removed_bytes": 0, "archive_id": None}

    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    archive = db.upsert_deliberation_source(
        source_type="bridge_thread",
        source_ref="bridge/INDEX.md#startup-comment-prune",
        content=original,
        title=f"Bridge INDEX startup comment compaction snapshot {timestamp}",
        summary=(
            f"Pre-compaction bridge/INDEX.md snapshot archived before removing "
            f"{removed_lines} historical comment line(s) from startup context."
        ),
        outcome="informational",
        origin_project="agent-red",
        origin_repo="Remaker-Digital/agent-red-customer-engagement",
        changed_by="retroactive_harvest_bridge_threads.py",
        change_reason="Owner-authorized startup pruning of oversized bridge/INDEX.md comment history",
    )
    archive_id = archive.get("id") if isinstance(archive, dict) else None
    index_path.write_text(compacted_text, encoding="utf-8")
    return {
        "compacted_blocks": compacted_blocks,
        "removed_comment_lines": removed_lines,
        "removed_bytes": removed_bytes,
        "archive_id": archive_id,
    }


def archive_verified_threads_and_prune_index(
    *,
    index_path: Path = BRIDGE_INDEX,
    bridge_dir: Path = BRIDGE_DIR,
    kb_path: str | None = None,
) -> dict:
    """Archive active VERIFIED bridge threads, then remove them from INDEX.

    This is intentionally stricter than ``run_sweep(execute=True)``: it only
    touches active INDEX entries whose latest status is VERIFIED. GO, NO-GO,
    NEW, REVISED, and orphan bridge files are left alone.
    """
    records = collect_compressed_bridge_threads(index_path, bridge_dir)
    verified_records = [r for r in records if r.active and r.latest_status == "VERIFIED"]
    db = _load_db(kb_path)
    existing_rows = db.list_deliberations(source_type="bridge_thread")

    archived_thread_names: set[str] = set()
    inserted = 0
    already_archived = 0
    failed: list[str] = []

    for rec in verified_records:
        if not rec.versions:
            failed.append(f"{rec.thread_name}: no readable bridge versions")
            continue

        title, summary, content = build_thread_summary(rec)
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        exact_existing = [
            row for row in existing_rows
            if row.get("source_ref") == rec.source_ref and row.get("content_hash") == content_hash
        ]
        if exact_existing:
            already_archived += 1
            archived_thread_names.add(rec.thread_name)
            continue

        try:
            row = db.upsert_deliberation_source(
                source_type="bridge_thread",
                source_ref=rec.source_ref,
                content=content,
                title=title,
                summary=summary,
                outcome="go",
                origin_project="agent-red",
                origin_repo="Remaker-Digital/agent-red-customer-engagement",
                changed_by="retroactive_harvest_bridge_threads.py",
                change_reason=(
                    "Owner-authorized startup maintenance: archive VERIFIED "
                    "bridge thread before removing it from bridge/INDEX.md"
                ),
            )
            inserted += 1
            existing_rows.append({
                "source_type": "bridge_thread",
                "source_ref": rec.source_ref,
                "content_hash": row.get("content_hash", content_hash) if isinstance(row, dict) else content_hash,
            })
            archived_thread_names.add(rec.thread_name)
        except Exception as exc:  # noqa: BLE001 - keep unarchived entries visible
            failed.append(f"{rec.thread_name}: {exc}")

    pruned = _write_pruned_index(index_path, archived_thread_names)
    try:
        comment_compaction = _compact_index_comments(index_path, db)
    except Exception as exc:  # noqa: BLE001 - index comments remain if archival/compaction fails
        comment_compaction = {
            "compacted_blocks": 0,
            "removed_comment_lines": 0,
            "removed_bytes": 0,
            "archive_id": None,
            "error": str(exc),
        }
    return {
        "verified_threads_seen": len(verified_records),
        "already_archived": already_archived,
        "inserted": inserted,
        "pruned_from_index": pruned,
        "comment_compaction": comment_compaction,
        "failed_count": len(failed),
        "failed": failed,
        "kept_unarchived": len(verified_records) - len(archived_thread_names),
    }


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------


def run_sweep(
    *,
    execute: bool,
    sample: int,
    kb_path: str | None,
) -> dict:
    records = collect_compressed_bridge_threads(BRIDGE_INDEX, BRIDGE_DIR)
    db = _load_db(kb_path)

    before_coverage = compute_active_bridge_thread_coverage(records, db)

    existing_rows = db.list_deliberations(source_type="bridge_thread")
    existing_canonical_refs = {r["source_ref"] for r in existing_rows if "*" in (r.get("source_ref") or "")}
    existing_legacy_refs = {r["source_ref"] for r in existing_rows if r.get("source_ref") and "*" not in r["source_ref"]}

    # Legacy thread coverage: threads that have ANY legacy file-level row
    legacy_thread_stems: set[str] = set()
    for ref in existing_legacy_refs:
        if not ref.startswith("bridge/"):
            continue
        fname = ref.split("bridge/", 1)[1]
        stem = extract_thread_stem(fname)
        if stem:
            legacy_thread_stems.add(stem)

    canonical_thread_stems: set[str] = {
        ref.split("bridge/", 1)[1].rsplit("-*.md", 1)[0]
        for ref in existing_canonical_refs
        if ref.startswith("bridge/") and ref.endswith("-*.md")
    }
    threads_with_legacy_but_no_canonical = legacy_thread_stems - canonical_thread_stems

    skip_reasons: dict[str, int] = defaultdict(int)
    new_inserts_planned = 0
    new_inserts_applied = 0
    already_canonical = 0
    warning_count = 0
    warnings: list[str] = []
    sample_records: list[dict] = []

    for rec in records:
        if not rec.versions:
            skip_reasons["empty_thread"] += 1
            warnings.append(f"empty thread: {rec.thread_name}")
            warning_count += 1
            continue
        title, summary, content = build_thread_summary(rec)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        existing = [
            r for r in existing_rows
            if r.get("source_ref") == rec.source_ref and r.get("content_hash") == content_hash
        ]
        if existing:
            already_canonical += 1
            skip_reasons["content_hash_dupe"] += 1
            continue

        new_inserts_planned += 1
        if len(sample_records) < sample:
            sample_records.append({
                "thread_name": rec.thread_name,
                "source_ref": rec.source_ref,
                "versions": len(rec.versions),
                "active": rec.active,
                "latest_status": rec.latest_status,
                "title": title,
                "summary_preview": summary[:200],
            })

        if execute:
            outcome = "go" if rec.latest_status == "VERIFIED" else "informational"
            try:
                db.upsert_deliberation_source(
                    source_type="bridge_thread",
                    source_ref=rec.source_ref,
                    content=content,
                    title=title,
                    summary=summary,
                    outcome=outcome,
                    origin_project="agent-red",
                    origin_repo="Remaker-Digital/agent-red-customer-engagement",
                    changed_by="retroactive_harvest_bridge_threads.py",
                    change_reason="Retroactive thread-compressed DA harvest (bridge gtkb-da-harvest-coverage-implementation-005)",
                )
                new_inserts_applied += 1
            except Exception as exc:  # noqa: BLE001 -- report to warnings, not silent
                warnings.append(f"insert failure for {rec.thread_name}: {exc}")
                warning_count += 1

    if execute:
        records_after = records
        after_coverage = compute_active_bridge_thread_coverage(records_after, db)
    else:
        # Project post-execute coverage by counting threads we'd insert for active VERIFIED threads
        projected_covered = set(before_coverage["covered_thread_names"])
        for rec in records:
            if rec.active and rec.latest_status == "VERIFIED" and rec.versions:
                projected_covered.add(rec.thread_name)
        denom = before_coverage["denominator_threads"]
        after_coverage = {
            "denominator_threads": denom,
            "numerator_threads": len(projected_covered),
            "coverage_pct": round(100.0 * len(projected_covered) / denom, 2) if denom else 100.0,
            "uncovered_thread_names": sorted(
                {r.thread_name for r in records if r.active and r.latest_status == "VERIFIED"}
                - projected_covered
            ),
            "covered_thread_names": sorted(projected_covered),
            "note": "projected (dry-run)",
        }

    return {
        "mode": "execute" if execute else "dry-run",
        "summary": {
            "candidate_threads": len(records),
            "active_threads": sum(1 for r in records if r.active),
            "orphan_threads": sum(1 for r in records if not r.active),
            "existing_canonical_wildcard_matches": already_canonical,
            "existing_legacy_file_level_matches": len(existing_legacy_refs),
            "new_compressed_inserts_planned": new_inserts_planned,
            "new_compressed_inserts_applied": new_inserts_applied if execute else 0,
            "skip_reasons": dict(skip_reasons),
            "warning_count": warning_count,
            "coverage_before_pct": before_coverage["coverage_pct"],
            "coverage_after_pct_projected": after_coverage["coverage_pct"],
        },
        "legacy_file_level_thread_coverage": {
            "threads_with_any_legacy_row": len(legacy_thread_stems),
            "threads_with_legacy_but_no_canonical": len(threads_with_legacy_but_no_canonical),
            "note": "Legacy rows are left untouched and do not count toward canonical wildcard coverage.",
        },
        "coverage_before": before_coverage,
        "coverage_after_projected": after_coverage,
        "warnings": warnings[:50],
        "sample_inserts": sample_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Retroactive back-harvest of compressed bridge threads (GO'd at bridge gtkb-da-harvest-coverage-implementation-005)",
    )
    parser.add_argument("--execute", action="store_true", help="Apply inserts (default: dry-run)")
    parser.add_argument(
        "--archive-and-prune-verified",
        action="store_true",
        help="Archive active VERIFIED threads and remove those entries from bridge/INDEX.md.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run (default behavior; opposite of --execute). "
        "Included as a no-op flag for command-history clarity; errors if combined with --execute.",
    )
    parser.add_argument("--sample", type=int, default=5, help="Sample inserts to include in output (default 5)")
    parser.add_argument("--kb-path", type=str, default=None, help="Override path to groundtruth.db")
    parser.add_argument("--output", type=str, default=None, help="Write JSON report to this path (in addition to stdout)")
    args = parser.parse_args()

    if args.dry_run and args.execute:
        parser.error("--dry-run and --execute are mutually exclusive")
    if args.archive_and_prune_verified and (args.execute or args.dry_run):
        parser.error("--archive-and-prune-verified cannot be combined with --execute or --dry-run")

    if args.archive_and_prune_verified:
        report = archive_verified_threads_and_prune_index(kb_path=args.kb_path)
        json_output = json.dumps(report, indent=2, sort_keys=True)
        print(json_output)
        if args.output:
            Path(args.output).write_text(json_output, encoding="utf-8")
        return 1 if report["failed_count"] else 0

    report = run_sweep(
        execute=args.execute,
        sample=args.sample,
        kb_path=args.kb_path,
    )

    json_output = json.dumps(report, indent=2, sort_keys=True)
    print(json_output)
    if args.output:
        Path(args.output).write_text(json_output, encoding="utf-8")

    if report["summary"]["warning_count"] > 0 and report["mode"] == "execute":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
