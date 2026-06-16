#!/usr/bin/env python3
"""Inventory Loyal Opposition reports and bridge history for DA backfill (WI-3162, Slice 1).

This is the **inventory-only** Slice 1 of WI-3162 ("Backfill existing LO reports
and bridge history"). It enumerates two file classes and classifies each file
against the live Deliberation Archive (DA) coverage, then emits a deterministic
JSON manifest and a human-readable summary under
``.gtkb-state/lo-bridge-history-backfill/``.

Slice 1 is strictly read-only with respect to canonical state:

  * It performs **no** ``groundtruth.db`` write.
  * It inserts/updates **no** Deliberation Archive rows.
  * It mutates **no** MemBase ``work_items`` / ``specifications``.
  * It performs **no** harvest/backfill mutation.

The actual harvest/backfill mutation is a separately-specified Slice 2 proposal
to be filed after the owner and Loyal Opposition inspect this inventory output.

Specification linkage (see bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-009.md):
  * SPEC-DA-HARVEST-INCLUSION / SPEC-DA-HARVEST-EXCLUSION — inclusion/exclusion criteria.
  * SPEC-DA-RETROACTIVE-SWEEP — retroactive back-harvest idempotence (manifest determinism).
  * SPEC-DA-THREAD-COMPRESSION — one DELIB per bridge thread in compressed wildcard form.
  * SPEC-DA-COVERAGE-METRIC — per-file evidence for the DA bridge-thread coverage metric.
  * SPEC-DA-MECHANICAL-ENFORCE — mutation stays disabled and observable.
  * SPEC-2098 — Deliberation Archive feature spec and parent of WI-3162.
  * ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all outputs stay under E:\\GT-KB.

Usage:
    python scripts/inventory_lo_bridge_history_backfill.py \\
        --output-dir .gtkb-state/lo-bridge-history-backfill/

There is intentionally **no** ``--apply`` mode in Slice 1.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root and standard paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]

SCHEMA_VERSION = 1
MIN_HARVEST_SIZE_BYTES = 100  # matches harvest_session_deliberations exclusion

# Credential-survivor pattern (mirrors harvest_session_deliberations._AR_KEY_SURVIVOR_RE)
_AR_KEY_SURVIVOR_RE = re.compile(r"(ar_live|ar_user|ar_spa_plat|pk_live|arsk)_[A-Za-z0-9_-]{10,}")

# Bridge filename -> thread stem: strip the trailing ``-NNN.md`` version suffix.
_VERSION_SUFFIX_RE = re.compile(r"-\d{3,}\.md$")

# Manifest classification labels.
ALREADY_HARVESTED = "already_harvested"
EXCLUDED_PER_SPEC = "excluded_per_spec"
ELIGIBLE_FOR_HARVEST = "eligible_for_harvest"


# ---------------------------------------------------------------------------
# Record model
# ---------------------------------------------------------------------------


@dataclass
class InventoryRecord:
    """One inventory row per enumerated file."""

    path: str
    thread_stem: str
    file_class: str  # "lo_report" | "bridge"
    size_bytes: int
    sha256: str
    classification: str
    classification_reason: str
    current_da_row_id: str | None
    current_da_content_hash: str | None
    bridge_status: str | None


@dataclass
class DASnapshot:
    """Read-only snapshot of current Deliberation Archive source coverage."""

    # exact source_ref -> {content_hash, ...}; preserves the row id per ref.
    exact_ref_hashes: dict[str, set[str]] = field(default_factory=dict)
    exact_ref_row_id: dict[str, str] = field(default_factory=dict)
    # compressed wildcard thread stems harvested as ``bridge/{stem}-*.md``.
    wildcard_stems: set[str] = field(default_factory=set)
    total_rows: int = 0
    bridge_exact_refs: int = 0
    bridge_wildcard_refs: int = 0
    lo_report_refs: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _thread_stem_for_bridge(filename: str) -> str:
    """``foo-bar-003.md`` -> ``foo-bar``; non-versioned names keep their stem."""
    stripped = _VERSION_SUFFIX_RE.sub("", filename)
    if stripped == filename and filename.endswith(".md"):
        stripped = filename[: -len(".md")]
    return stripped


def _redact_survivor_count(content: str) -> int:
    """Count credential survivors after simulated redaction.

    Mirrors harvest_session_deliberations: redact via the KnowledgeDB classmethod
    when importable, then count any AR-key survivors in the redacted text. When
    the redaction helper is unavailable, fall back to scanning raw content so the
    exclusion is conservative (never under-reports a survivor).
    """
    redacted = content
    try:
        from groundtruth_kb.db import KnowledgeDB

        redacted, _ = KnowledgeDB.redact_content(content)
    except (ImportError, AttributeError):
        redacted = content
    return len(_AR_KEY_SURVIVOR_RE.findall(redacted))


# ---------------------------------------------------------------------------
# Source enumeration
# ---------------------------------------------------------------------------


def iter_lo_reports(repo_root: Path) -> list[tuple[str, Path]]:
    """Class A: ``INSIGHTS-*.md`` under the LO insight dropbox.

    Returns (source_ref, path) tuples in deterministic sorted order.
    """
    insight_dir = repo_root / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    if not insight_dir.exists():
        return []
    out: list[tuple[str, Path]] = []
    for f in sorted(insight_dir.glob("INSIGHTS-*.md")):
        source_ref = f"independent-progress-assessments/CODEX-INSIGHT-DROPBOX/{f.name}"
        out.append((source_ref, f))
    return out


def iter_bridge_files(repo_root: Path) -> list[tuple[str, Path]]:
    """Class B: status-bearing numbered bridge markdown files.

    Returns (source_ref, path) tuples in deterministic sorted order.
    """
    bridge_dir = repo_root / "bridge"
    if not bridge_dir.exists():
        return []
    out: list[tuple[str, Path]] = []
    for f in sorted(bridge_dir.glob("*.md")):
        if not _VERSION_SUFFIX_RE.search(f.name):
            continue
        out.append((f"bridge/{f.name}", f))
    return out


# ---------------------------------------------------------------------------
# Bridge file status lookup
# ---------------------------------------------------------------------------


def load_bridge_file_status(repo_root: Path) -> dict[str, str]:
    """Map ``bridge/<file>.md`` -> the file's first canonical status token."""
    gt_src = repo_root / "groundtruth-kb" / "src"
    if str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))
    from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

    status_by_file: dict[str, str] = {}
    for source_ref, path in iter_bridge_files(repo_root):
        status = status_from_bridge_file(path)
        if status:
            status_by_file[source_ref] = status
    return status_by_file


# ---------------------------------------------------------------------------
# DA snapshot (read-only)
# ---------------------------------------------------------------------------


def load_da_snapshot(db_path: Path) -> DASnapshot:
    """Read current Deliberation Archive source coverage. READ-ONLY.

    Opens the SQLite database in read-only URI mode so this inventory can never
    mutate canonical state (SPEC-DA-MECHANICAL-ENFORCE).
    """
    snap = DASnapshot()
    if not db_path.exists():
        return snap
    uri = f"file:{db_path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        # current_deliberations is the latest-version view; fall back to the
        # base table only if the view is absent (older DBs).
        table = "current_deliberations"
        exists = conn.execute("SELECT name FROM sqlite_master WHERE name = ?", (table,)).fetchone()
        if not exists:
            table = "deliberations"
        rows = conn.execute(
            f"SELECT id, source_ref, content_hash FROM {table} "  # noqa: S608 - table name is a fixed allowlist
            "WHERE source_ref IS NOT NULL"
        ).fetchall()
    finally:
        conn.close()

    for row_id, source_ref, content_hash in rows:
        snap.total_rows += 1
        if not source_ref:
            continue
        if source_ref.startswith("bridge/") and source_ref.endswith("-*.md"):
            stem = source_ref[len("bridge/") : -len("-*.md")]
            snap.wildcard_stems.add(stem)
            snap.bridge_wildcard_refs += 1
        else:
            snap.exact_ref_hashes.setdefault(source_ref, set())
            if content_hash:
                snap.exact_ref_hashes[source_ref].add(content_hash)
            # First-seen row id wins for stable reporting.
            snap.exact_ref_row_id.setdefault(source_ref, str(row_id))
            if source_ref.startswith("bridge/") and source_ref.endswith(".md"):
                snap.bridge_exact_refs += 1
            elif "CODEX-INSIGHT-DROPBOX" in source_ref:
                snap.lo_report_refs += 1
    return snap


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify_file(
    source_ref: str,
    path: Path,
    file_class: str,
    snap: DASnapshot,
    bridge_status: dict[str, str],
) -> InventoryRecord:
    """Classify exactly one file into one of the three classifications.

    Deterministic precedence:
      1. exact-path DA row present:
           - stored hash matches current content -> already_harvested/exact_path_match
           - stored hash differs               -> eligible_for_harvest/content_drift_since_harvest
      2. compressed wildcard covers the thread  -> already_harvested/compressed_wildcard_coverage
      3. size < 100 bytes                        -> excluded_per_spec/size_under_100_bytes
      4. credential survivor after redaction     -> excluded_per_spec/redaction_survivor
      5. default                                 -> eligible_for_harvest/not_yet_harvested
    """
    # Size uses the raw on-disk byte count (matches harvest's stat().st_size gate).
    size_bytes = path.stat().st_size
    # Content hash uses read_text-normalized content so it matches the DA
    # content_hash semantics (harvest computes sha256(read_text().encode())),
    # which also makes the hash portable across CRLF/LF checkouts.
    content = path.read_text(encoding="utf-8", errors="ignore")
    file_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    thread_stem = _thread_stem_for_bridge(path.name) if file_class == "bridge" else path.stem
    status = bridge_status.get(source_ref)

    current_da_row_id = snap.exact_ref_row_id.get(source_ref)
    stored_hashes = snap.exact_ref_hashes.get(source_ref)
    current_da_content_hash = None
    if stored_hashes:
        # Report a single representative stored hash deterministically.
        current_da_content_hash = sorted(stored_hashes)[0]

    classification: str
    reason: str

    if stored_hashes is not None:
        if file_sha in stored_hashes:
            classification, reason = ALREADY_HARVESTED, "exact_path_match"
        else:
            classification, reason = ELIGIBLE_FOR_HARVEST, "content_drift_since_harvest"
    elif file_class == "bridge" and thread_stem in snap.wildcard_stems:
        classification, reason = ALREADY_HARVESTED, "compressed_wildcard_coverage"
    elif size_bytes < MIN_HARVEST_SIZE_BYTES:
        classification, reason = EXCLUDED_PER_SPEC, "size_under_100_bytes"
    elif _redact_survivor_count(content) > 0:
        classification, reason = EXCLUDED_PER_SPEC, "redaction_survivor"
    else:
        classification, reason = ELIGIBLE_FOR_HARVEST, "not_yet_harvested"

    return InventoryRecord(
        path=source_ref,
        thread_stem=thread_stem,
        file_class=file_class,
        size_bytes=size_bytes,
        sha256=file_sha,
        classification=classification,
        classification_reason=reason,
        current_da_row_id=current_da_row_id,
        current_da_content_hash=current_da_content_hash,
        bridge_status=status,
    )


# ---------------------------------------------------------------------------
# Inventory build
# ---------------------------------------------------------------------------


def build_inventory(repo_root: Path, db_path: Path) -> tuple[list[InventoryRecord], DASnapshot]:
    """Build the full inventory record list (read-only)."""
    snap = load_da_snapshot(db_path)
    bridge_status = load_bridge_file_status(repo_root)
    records: list[InventoryRecord] = []
    for source_ref, path in iter_lo_reports(repo_root):
        records.append(classify_file(source_ref, path, "lo_report", snap, bridge_status))
    for source_ref, path in iter_bridge_files(repo_root):
        records.append(classify_file(source_ref, path, "bridge", snap, bridge_status))
    # Deterministic ordering: by path.
    records.sort(key=lambda r: r.path)
    return records, snap


def _script_sha256() -> str:
    return _sha256_bytes(Path(__file__).resolve().read_bytes())


def build_manifest(repo_root: Path, records: list[InventoryRecord], snap: DASnapshot) -> dict:
    """Build the byte-stable manifest dict.

    Intentionally excludes volatile ``generated_at`` and filesystem ``mtime``.
    """
    on_disk_counts = {
        "lo_report": sum(1 for r in records if r.file_class == "lo_report"),
        "bridge": sum(1 for r in records if r.file_class == "bridge"),
        "total": len(records),
    }
    return {
        "_meta": {
            "schema_version": SCHEMA_VERSION,
            "gt_repo_root": repo_root.name,
            "script_sha256": _script_sha256(),
            "da_snapshot_counts": {
                "total_rows": snap.total_rows,
                "bridge_exact_refs": snap.bridge_exact_refs,
                "bridge_wildcard_refs": snap.bridge_wildcard_refs,
                "lo_report_refs": snap.lo_report_refs,
            },
            "on_disk_counts": on_disk_counts,
        },
        "records": [asdict(r) for r in records],
    }


def manifest_to_bytes(manifest: dict) -> bytes:
    """Serialize the manifest to byte-stable JSON (sorted keys, fixed separators)."""
    text = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)
    return (text + "\n").encode("utf-8")


def build_summary(repo_root: Path, records: list[InventoryRecord], snap: DASnapshot, generated_at: str) -> str:
    """Build the human-readable summary (volatile fields allowed here)."""
    from collections import Counter

    by_class = Counter(r.classification for r in records)
    by_reason = Counter(r.classification_reason for r in records)
    eligible = [r for r in records if r.classification == ELIGIBLE_FOR_HARVEST]
    unstatused_stems = sorted({r.thread_stem for r in records if r.file_class == "bridge" and r.bridge_status is None})

    lines: list[str] = []
    lines.append("# LO / Bridge History Backfill — Slice 1 Inventory Summary")
    lines.append("")
    lines.append(f"- Generated: {generated_at}")
    lines.append(f"- Repo root: {repo_root}")
    lines.append("- Slice: 1 (inventory-only; no DA/MemBase mutation)")
    lines.append("- Work item: WI-3162")
    lines.append("")
    lines.append("## Counts by classification")
    lines.append("")
    for cls in (ALREADY_HARVESTED, EXCLUDED_PER_SPEC, ELIGIBLE_FOR_HARVEST):
        lines.append(f"- `{cls}`: {by_class.get(cls, 0)}")
    lines.append(f"- total files inventoried: {len(records)}")
    lines.append("")
    lines.append("## Counts by reason")
    lines.append("")
    for reason, count in sorted(by_reason.items()):
        lines.append(f"- `{reason}`: {count}")
    lines.append("")
    lines.append("## DA snapshot")
    lines.append("")
    lines.append(f"- total current deliberation rows: {snap.total_rows}")
    lines.append(f"- bridge exact-path source refs: {snap.bridge_exact_refs}")
    lines.append(f"- bridge compressed-wildcard source refs: {snap.bridge_wildcard_refs}")
    lines.append(f"- LO-report source refs: {snap.lo_report_refs}")
    lines.append("")
    lines.append(f"## Eligible-for-harvest candidates ({len(eligible)})")
    lines.append("")
    if eligible:
        for r in eligible:
            lines.append(f"- `{r.path}` — {r.classification_reason}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append(f"## Bridge threads without status token ({len(unstatused_stems)})")
    lines.append("")
    if unstatused_stems:
        for stem in unstatused_stems:
            lines.append(f"- `{stem}`")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------


def write_outputs(output_dir: Path, manifest_bytes: bytes, summary_text: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "inventory-manifest.json"
    summary_path = output_dir / "inventory-summary.md"
    manifest_path.write_bytes(manifest_bytes)
    summary_path.write_text(summary_text, encoding="utf-8")
    return manifest_path, summary_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inventory LO reports + bridge history for DA backfill (WI-3162 Slice 1; read-only).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / ".gtkb-state" / "lo-bridge-history-backfill"),
        help="Directory for inventory-manifest.json + inventory-summary.md.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to enumerate (defaults to the GT-KB checkout).",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Path to groundtruth.db (defaults to <repo-root>/groundtruth.db). Opened read-only.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    db_path = Path(args.db_path).resolve() if args.db_path else repo_root / "groundtruth.db"
    output_dir = Path(args.output_dir).resolve()

    records, snap = build_inventory(repo_root, db_path)
    manifest = build_manifest(repo_root, records, snap)
    manifest_bytes = manifest_to_bytes(manifest)
    generated_at = datetime.now(UTC).isoformat()
    summary_text = build_summary(repo_root, records, snap, generated_at)
    manifest_path, summary_path = write_outputs(output_dir, manifest_bytes, summary_text)

    print(f"inventory-manifest.json -> {manifest_path} ({len(manifest_bytes)} bytes)")
    print(f"inventory-summary.md    -> {summary_path}")
    print(
        "classification: "
        + ", ".join(
            f"{cls}={sum(1 for r in records if r.classification == cls)}"
            for cls in (ALREADY_HARVESTED, EXCLUDED_PER_SPEC, ELIGIBLE_FOR_HARVEST)
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
