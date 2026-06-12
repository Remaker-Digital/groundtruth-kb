#!/usr/bin/env python3
"""
Harvest new deliberation sources into the Knowledge Database.

SPEC-2098 Phase C3: Session-wrap harvest script.

Scans for deliberation sources created or finalized since the last harvest:
  - New Loyal Opposition reports (INSIGHTS-*.md)
  - Completed bridge threads (VERIFIED status in bridge/INDEX.md)
  - GO-reviewed bridge proposals
  - Compressed bridge threads (flag-gated via --thread-level, SPEC-DA-THREAD-COMPRESSION)

Usage:
    # Dry run (default) -- shows what would be archived
    python scripts/harvest_session_deliberations.py

    # Apply mode -- actually archives into KB
    python scripts/harvest_session_deliberations.py --apply

    # Restrict to a single session
    python scripts/harvest_session_deliberations.py --apply --session S283

    # Opt into compressed thread-level harvest (in addition to file-level)
    python scripts/harvest_session_deliberations.py --apply --thread-level

    # Emit machine-readable JSON summary to stdout or a file
    python scripts/harvest_session_deliberations.py --apply --json-output summary.json

Prerequisites:
    - GroundTruth KB with deliberation support (v0.2.0+)
    - Agent Red project KB at groundtruth.db

Codex GO chain:
    - Session harvest base: bridge/deliberation-archive-completion-008.md
    - Thread-level compression + JSON summary: bridge/gtkb-da-harvest-coverage-implementation-005.md

Legacy anomaly (F3 resolution): DELIB-0712 remains at its original source_type
for append-only preservation; forward methodology-review content will be
recorded as source_type='report' with source_ref annotation
'methodology-review:<topic>'.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root and standard paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
INSIGHT_DIR = REPO_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
BRIDGE_DIR = REPO_ROOT / "bridge"
BRIDGE_INDEX = BRIDGE_DIR / "INDEX.md"
KB_PATH = REPO_ROOT / "groundtruth.db"

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

SPEC_RE = re.compile(r"\bSPEC-\d+(?:\.\d+)*\b")
WI_RE = re.compile(r"\bWI-\d+\b")
SESSION_RE = re.compile(r"\b(S\d{3,})\b")
_AR_KEY_SURVIVOR_RE = re.compile(r"(ar_live|ar_user|ar_spa_plat|pk_live|arsk)_[A-Za-z0-9_-]{10,}")

# Bridge INDEX.md parsing
_DOC_LINE_RE = re.compile(r"^Document:\s+(.+)$")
_STATUS_LINE_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN|ACCEPTED|BLOCKED):\s+bridge/(.+\.md)$"
)

# Verdict extraction for bridge files
_VERDICT_FIELD_RE = re.compile(
    r"(?:^|\n)[^\S\r\n]*(?:\*{1,2})?[Vv]erdict(?:\*{1,2})?[^\S\r\n]*[:=][^\S\r\n]*(.+)?",
)


# ---------------------------------------------------------------------------
# Bridge INDEX parser
# ---------------------------------------------------------------------------


@dataclass
class BridgeDocument:
    """A document entry from bridge/INDEX.md."""

    name: str
    entries: list[tuple[str, str]]  # [(status, filename), ...] newest first

    @property
    def latest_status(self) -> str:
        return self.entries[0][0] if self.entries else ""

    @property
    def latest_file(self) -> str:
        return self.entries[0][1] if self.entries else ""

    def files_with_status(self, status: str) -> list[str]:
        return [f for s, f in self.entries if s == status]


def parse_bridge_index(index_path: Path) -> list[BridgeDocument]:
    """Parse bridge/INDEX.md into structured document entries."""
    if not index_path.exists():
        return []

    docs: list[BridgeDocument] = []
    current_name: str | None = None
    current_entries: list[tuple[str, str]] = []

    for line in index_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("<!--") or line.startswith("#"):
            continue

        doc_match = _DOC_LINE_RE.match(line)
        if doc_match:
            if current_name is not None:
                docs.append(BridgeDocument(name=current_name, entries=current_entries))
            current_name = doc_match.group(1).strip()
            current_entries = []
            continue

        status_match = _STATUS_LINE_RE.match(line)
        if status_match and current_name is not None:
            current_entries.append((status_match.group(1), status_match.group(2)))

    if current_name is not None:
        docs.append(BridgeDocument(name=current_name, entries=current_entries))

    return docs


# ---------------------------------------------------------------------------
# ID extraction
# ---------------------------------------------------------------------------


def ordered_unique(pattern: re.Pattern[str], text: str) -> list[str]:
    """Extract IDs preserving first-occurrence order, deduplicated."""
    seen: set[str] = set()
    result: list[str] = []
    for m in pattern.finditer(text):
        val = m.group(0)
        if val not in seen:
            seen.add(val)
            result.append(val)
    return result


def extract_title(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Untitled"


def extract_summary(content: str, max_len: int = 200) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
            return stripped[:max_len]
    return ""


def extract_session(content: str, filename: str) -> str | None:
    # Check filename first
    m = SESSION_RE.search(filename)
    if m:
        return m.group(1)
    # Then first 30 lines of content
    for line in content.splitlines()[:30]:
        m = SESSION_RE.search(line)
        if m:
            return m.group(1)
    return None


def extract_bridge_outcome(content: str, filename: str) -> str:
    """Extract outcome for a bridge file based on its role."""
    fname_upper = filename.upper()
    if "VERIFIED" in fname_upper:
        return "go"
    # Check verdict field in content
    m = _VERDICT_FIELD_RE.search(content[:2000])
    if m and m.group(1):
        text = m.group(1).strip().lower()
        if "no-go" in text or "no_go" in text:
            return "no_go"
        if "go" in text or "verified" in text:
            return "go"
    # Filename-based fallback
    if "NO-GO" in fname_upper or "NOGO" in fname_upper:
        return "no_go"
    if "GO" in fname_upper:
        return "go"
    return "informational"


# ---------------------------------------------------------------------------
# Harvest result
# ---------------------------------------------------------------------------


@dataclass
class HarvestResult:
    source_ref: str
    source_type: str
    outcome: str
    action: str  # created, skipped, error
    spec_ids: list[str] = field(default_factory=list)
    wi_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# KB loader
# ---------------------------------------------------------------------------


def _load_kb(kb_path: str | None = None):
    sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
    from db import KnowledgeDB

    path = kb_path or str(KB_PATH)
    return KnowledgeDB(path)


def _simulate_redaction(content: str):
    try:
        sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
        from groundtruth_kb.db import KnowledgeDB as _GT

        return _GT.redact_content(content)
    except (ImportError, AttributeError):
        return content, None


# ---------------------------------------------------------------------------
# Source collectors
# ---------------------------------------------------------------------------


def collect_lo_reports(session_filter: str | None = None) -> list[tuple[str, Path]]:
    """Collect INSIGHTS-*.md files, optionally filtered by session."""
    if not INSIGHT_DIR.exists():
        return []
    files = sorted(INSIGHT_DIR.glob("INSIGHTS-*.md"))
    results = []
    for f in files:
        if f.stat().st_size < 100:
            continue
        source_ref = f"independent-progress-assessments/CODEX-INSIGHT-DROPBOX/{f.name}"
        if session_filter:
            content = f.read_text(encoding="utf-8", errors="ignore")
            session = extract_session(content, f.name)
            if session != session_filter:
                continue
        results.append((source_ref, f))
    return results


def collect_bridge_threads() -> list[tuple[str, Path, str]]:
    """Collect bridge files from VERIFIED and GO threads.

    Returns (source_ref, path, outcome) tuples.
    """
    docs = parse_bridge_index(BRIDGE_INDEX)
    results = []
    seen_files: set[str] = set()

    for doc in docs:
        # Collect VERIFIED files
        for fname in doc.files_with_status("VERIFIED"):
            if fname not in seen_files:
                fpath = BRIDGE_DIR / fname
                if fpath.exists() and fpath.stat().st_size >= 100:
                    results.append((f"bridge/{fname}", fpath, "go"))
                    seen_files.add(fname)

        # Collect GO files (approval decisions)
        for fname in doc.files_with_status("GO"):
            if fname not in seen_files:
                fpath = BRIDGE_DIR / fname
                if fpath.exists() and fpath.stat().st_size >= 100:
                    results.append((f"bridge/{fname}", fpath, "go"))
                    seen_files.add(fname)

        # Collect NO-GO files (rejected approach records)
        for fname in doc.files_with_status("NO-GO"):
            if fname not in seen_files:
                fpath = BRIDGE_DIR / fname
                if fpath.exists() and fpath.stat().st_size >= 100:
                    results.append((f"bridge/{fname}", fpath, "no_go"))
                    seen_files.add(fname)

    return results


# ---------------------------------------------------------------------------
# Compressed thread-level collector (flag-gated, shares logic with retroactive)
# ---------------------------------------------------------------------------


def _load_retroactive_module():
    """Load retroactive_harvest_bridge_threads for shared thread-grouping logic.

    Reuses ``parse_active_index``, ``collect_compressed_bridge_threads``, and
    ``build_thread_summary`` to guarantee the ongoing harvest produces byte-
    identical content for the same inputs (content-hash idempotence).

    The module is registered in sys.modules BEFORE exec_module so that
    dataclass(__module__) lookups succeed during class construction.
    """
    module_name = "retroactive_harvest_bridge_threads"
    if module_name in sys.modules:
        return sys.modules[module_name]
    script_path = REPO_ROOT / "scripts" / "retroactive_harvest_bridge_threads.py"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load retroactive script at {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # register BEFORE exec so @dataclass can find it
    spec.loader.exec_module(module)
    return module


def collect_compressed_bridge_threads() -> list[tuple[str, str, str, str, str]]:
    """Collect one compressed entry per bridge thread.

    Returns a list of tuples:
        (source_ref, title, summary, content, outcome)

    The source_ref is always ``bridge/{thread-name}-*.md`` (canonical wildcard).
    Outcome is ``'go'`` when the thread's latest INDEX status is VERIFIED,
    otherwise ``'informational'``. Orphan threads (not in active INDEX) are
    also included with outcome ``'informational'``.

    Content synthesis reuses the retroactive sweep's ``build_thread_summary``
    so content hashes are identical across the two code paths — a thread
    harvested retroactively and then re-harvested via this collector produces
    zero new rows (content_hash idempotence guaranteed).
    """
    rhbt = _load_retroactive_module()
    records = rhbt.collect_compressed_bridge_threads(BRIDGE_INDEX, BRIDGE_DIR)

    out: list[tuple[str, str, str, str, str]] = []
    for rec in records:
        if not rec.versions:
            continue
        title, summary, content = rhbt.build_thread_summary(rec)
        outcome = "go" if rec.latest_status == "VERIFIED" else "informational"
        out.append((rec.source_ref, title, summary, content, outcome))
    return out


# ---------------------------------------------------------------------------
# Main harvest
# ---------------------------------------------------------------------------


def harvest(
    *,
    apply: bool = False,
    session_filter: str | None = None,
    verbose: bool = False,
    kb_path: str | None = None,
    thread_level: bool = False,
) -> list[HarvestResult]:
    """Harvest deliberation sources into KB.

    Args:
        apply: True to insert into KB; False to dry-run.
        session_filter: Optional session ID to scope LO-report harvesting.
        verbose: Emit per-source detail lines.
        kb_path: Override for groundtruth.db path.
        thread_level: Opt into compressed thread-level harvest (one DELIB per
            bridge thread, canonical wildcard source_ref). Default off for v1
            per implementation plan; flipped on after one successful session.
    """
    results: list[HarvestResult] = []
    action_counts: Counter[str] = Counter()
    source_type_counts: Counter[str] = Counter()

    db = None
    if apply:
        try:
            db = _load_kb(kb_path)
        except ImportError:
            print("ERROR: Cannot import KnowledgeDB.")
            sys.exit(1)

    # --- Phase 1: LO reports ---
    lo_sources = collect_lo_reports(session_filter)
    for source_ref, filepath in lo_sources:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        redacted, _ = _simulate_redaction(content)

        # Check for AR key survivors
        survivors = len(_AR_KEY_SURVIVOR_RE.findall(redacted))
        if survivors > 0:
            results.append(
                HarvestResult(
                    source_ref=source_ref,
                    source_type="lo_review",
                    outcome="informational",
                    action="error",
                    warnings=[f"Redaction survivor: {survivors} AR key(s)"],
                )
            )
            action_counts["error"] += 1
            continue

        spec_ids = ordered_unique(SPEC_RE, content)
        wi_ids = ordered_unique(WI_RE, content)
        session = extract_session(content, filepath.name)

        # Determine outcome using backfill_lo_reports patterns
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from backfill_lo_reports import extract_outcome

        outcome, warnings = extract_outcome(content, filepath.name)

        action = "skipped"
        if apply and db is not None:
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            # Pre-check: skip if already archived with same content
            conn = db._get_conn()
            exists = conn.execute(
                "SELECT 1 FROM current_deliberations WHERE source_ref = ? AND content_hash = ?",
                (source_ref, content_hash),
            ).fetchone()
            if exists:
                action = "skipped"
            else:
                existing_specs = [s for s in spec_ids if db.get_spec(s)]
                existing_wis = [w for w in wi_ids if db.get_work_item(w)]

                delib = db.upsert_deliberation_source(
                    source_type="lo_review",
                    source_ref=source_ref,
                    content=content,
                    title=extract_title(content),
                    summary=extract_summary(content),
                    outcome=outcome,
                    spec_id=existing_specs[0] if existing_specs else None,
                    work_item_id=existing_wis[0] if existing_wis else None,
                    session_id=session,
                    origin_project="agent-red",
                    origin_repo="Remaker-Digital/agent-red-customer-engagement",
                    changed_by="harvest_session_deliberations.py",
                    change_reason="C3 session-wrap harvest",
                )
                action = "created"
                # Link additional IDs
                for sid in existing_specs[1:]:
                    db.link_deliberation_spec(delib["id"], sid)
                for wid in existing_wis[1:]:
                    db.link_deliberation_work_item(delib["id"], wid)
        elif not apply:
            action = "would_create"

        results.append(
            HarvestResult(
                source_ref=source_ref,
                source_type="lo_review",
                outcome=outcome,
                action=action,
                spec_ids=spec_ids,
                wi_ids=wi_ids,
                warnings=warnings,
            )
        )
        action_counts[action] += 1
        source_type_counts["lo_review"] += 1

    # --- Phase 2: Bridge threads ---
    bridge_sources = collect_bridge_threads()
    for source_ref, filepath, outcome in bridge_sources:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        spec_ids = ordered_unique(SPEC_RE, content)
        wi_ids = ordered_unique(WI_RE, content)
        session = extract_session(content, filepath.name)

        # Refine outcome from content if possible
        if outcome == "go":
            refined = extract_bridge_outcome(content, filepath.name)
            if refined != "informational":
                outcome = refined

        source_type = "bridge_thread"
        action = "skipped"

        if apply and db is not None:
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            conn = db._get_conn()
            exists = conn.execute(
                "SELECT 1 FROM current_deliberations WHERE source_ref = ? AND content_hash = ?",
                (source_ref, content_hash),
            ).fetchone()
            if exists:
                action = "skipped"
            else:
                existing_specs = [s for s in spec_ids if db.get_spec(s)]
                existing_wis = [w for w in wi_ids if db.get_work_item(w)]

                delib = db.upsert_deliberation_source(
                    source_type=source_type,
                    source_ref=source_ref,
                    content=content,
                    title=extract_title(content),
                    summary=extract_summary(content),
                    outcome=outcome,
                    spec_id=existing_specs[0] if existing_specs else None,
                    work_item_id=existing_wis[0] if existing_wis else None,
                    session_id=session,
                    origin_project="agent-red",
                    origin_repo="Remaker-Digital/agent-red-customer-engagement",
                    changed_by="harvest_session_deliberations.py",
                    change_reason="C3 session-wrap harvest",
                )
                action = "created"
                for sid in existing_specs[1:]:
                    db.link_deliberation_spec(delib["id"], sid)
                for wid in existing_wis[1:]:
                    db.link_deliberation_work_item(delib["id"], wid)
        elif not apply:
            action = "would_create"

        results.append(
            HarvestResult(
                source_ref=source_ref,
                source_type=source_type,
                outcome=outcome,
                action=action,
                spec_ids=spec_ids,
                wi_ids=wi_ids,
            )
        )
        action_counts[action] += 1
        source_type_counts["bridge_thread"] += 1

    # --- Phase 3: Compressed thread-level harvest (flag-gated) ---
    if thread_level:
        try:
            compressed = collect_compressed_bridge_threads()
        except Exception as exc:  # noqa: BLE001 -- recorded as warning, not silent failure
            compressed = []
            results.append(
                HarvestResult(
                    source_ref="bridge/(thread-level collector)",
                    source_type="bridge_thread",
                    outcome="informational",
                    action="error",
                    warnings=[f"thread-level collector failed: {exc}"],
                )
            )
            action_counts["error"] += 1

        for source_ref, title, summary, content, outcome in compressed:
            spec_ids = ordered_unique(SPEC_RE, content)
            wi_ids = ordered_unique(WI_RE, content)
            action = "skipped"

            if apply and db is not None:
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                conn = db._get_conn()
                exists = conn.execute(
                    "SELECT 1 FROM current_deliberations WHERE source_ref = ? AND content_hash = ?",
                    (source_ref, content_hash),
                ).fetchone()
                if exists:
                    action = "skipped"
                else:
                    existing_specs = [s for s in spec_ids if db.get_spec(s)]
                    existing_wis = [w for w in wi_ids if db.get_work_item(w)]
                    delib = db.upsert_deliberation_source(
                        source_type="bridge_thread",
                        source_ref=source_ref,
                        content=content,
                        title=title,
                        summary=summary,
                        outcome=outcome,
                        spec_id=existing_specs[0] if existing_specs else None,
                        work_item_id=existing_wis[0] if existing_wis else None,
                        origin_project="agent-red",
                        origin_repo="Remaker-Digital/agent-red-customer-engagement",
                        changed_by="harvest_session_deliberations.py",
                        change_reason="C3 session-wrap thread-level harvest",
                    )
                    action = "created"
                    for sid in existing_specs[1:]:
                        db.link_deliberation_spec(delib["id"], sid)
                    for wid in existing_wis[1:]:
                        db.link_deliberation_work_item(delib["id"], wid)
            elif not apply:
                action = "would_create"

            results.append(
                HarvestResult(
                    source_ref=source_ref,
                    source_type="bridge_thread",
                    outcome=outcome,
                    action=action,
                    spec_ids=spec_ids,
                    wi_ids=wi_ids,
                )
            )
            action_counts[action] += 1
            source_type_counts["bridge_thread_compressed"] += 1

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print(f"Session Deliberation Harvest {'[APPLY]' if apply else '[DRY RUN]'}")
    if session_filter:
        print(f"Session filter: {session_filter}")
    print(f"{'=' * 60}")
    print(f"Total sources scanned:  {len(results)}")
    print("By source type:")
    for st, count in source_type_counts.most_common():
        print(f"  {st:20s}  {count}")
    print("By action:")
    for act, count in action_counts.most_common():
        print(f"  {act:20s}  {count}")

    warnings = [w for r in results for w in r.warnings]
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings[:20]:
            print(f"  {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")

    if verbose:
        print("\nDetail:")
        for r in results:
            specs = r.spec_ids[0] if r.spec_ids else "-"
            wis = r.wi_ids[0] if r.wi_ids else "-"
            warn = " [!]" if r.warnings else ""
            print(f"  [{r.action:14s}] {r.source_type:15s} {r.outcome:15s} {specs:12s} {wis:8s} {r.source_ref}{warn}")

    print(f"{'=' * 60}")
    return results


# ---------------------------------------------------------------------------
# Machine-readable JSON summary (Phase 7 loud-wrap consumption)
# ---------------------------------------------------------------------------


def build_summary_json(
    results: list[HarvestResult],
    *,
    exit_status: str,
    applied: bool,
) -> dict:
    """Build machine-readable summary per implementation bridge schema.

    Schema fields (per bridge/gtkb-da-harvest-coverage-implementation-001.md F4):
        exit_status: "ok" | "error"
        new_inserts: int       — count of "created" actions
        skipped_existing: int  — count of "skipped" actions
        warning_count: int     — total warnings across all results
        warnings: list[str]    — flat list of all warning strings
        source_type_counts: dict[str, int]  — breakdown by source_type
        applied: bool          — whether KB was mutated (vs dry-run)
    """
    new_inserts = 0
    skipped_existing = 0
    type_counts: dict[str, int] = defaultdict(int)
    all_warnings: list[str] = []

    for r in results:
        if r.action == "created":
            new_inserts += 1
        elif r.action == "skipped":
            skipped_existing += 1
        type_counts[r.source_type] += 1
        all_warnings.extend(r.warnings)

    return {
        "exit_status": exit_status,
        "applied": applied,
        "new_inserts": new_inserts,
        "skipped_existing": skipped_existing,
        "warning_count": len(all_warnings),
        "warnings": all_warnings,
        "source_type_counts": dict(type_counts),
    }


# ---------------------------------------------------------------------------
# Loud-wrap: baseline-comparison helper (Phase 7)
# ---------------------------------------------------------------------------


def _hash_warning(warning: str) -> str:
    """Content-hash a warning string for baseline-stability."""
    return hashlib.sha256(warning.encode("utf-8")).hexdigest()[:16]


def load_warning_baseline(path: Path) -> dict:
    """Load the baseline JSON, returning an empty baseline if absent.

    Baseline schema:
        {
          "version": 1,
          "established_at": "<ISO8601>",
          "warning_hashes": ["<16-char sha256 prefix>", ...]
        }
    """
    if not path.exists():
        return {"version": 1, "established_at": "", "warning_hashes": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "established_at": "", "warning_hashes": []}
    if not isinstance(data, dict):
        return {"version": 1, "established_at": "", "warning_hashes": []}
    return data


def compute_wrap_verdict(
    summary: dict,
    baseline: dict,
    *,
    loud: bool,
) -> tuple[str, list[str]]:
    """Return (verdict, alarm_reasons) for a harvest summary.

    Verdicts:
        "OK"      — silent-mode (loud=False) regardless of warnings, OR
                    loud-mode with no warnings above baseline and exit_status=ok.
        "ALARM"   — loud-mode with either exit_status != "ok" or new warnings
                    not in baseline.

    Always-silent for v1 means ``loud=False`` and verdict=OK until baseline is
    established and owner flips the default in a follow-up session.
    """
    if not loud:
        return "OK", []

    reasons: list[str] = []

    if summary.get("exit_status") != "ok":
        reasons.append(f"exit_status={summary.get('exit_status')!r}")

    baseline_hashes = set(baseline.get("warning_hashes", []))
    new_warning_hashes = [_hash_warning(w) for w in summary.get("warnings", [])]
    novel = [h for h in new_warning_hashes if h not in baseline_hashes]
    if novel:
        reasons.append(f"{len(novel)} warning(s) not in baseline")

    if reasons:
        return "ALARM", reasons
    return "OK", []


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Harvest session deliberations into KB (SPEC-2098 C3)",
    )
    parser.add_argument("--apply", action="store_true", help="Apply to KB (default: dry run)")
    parser.add_argument("--session", type=str, default=None, help="Filter LO reports to session (e.g., S283)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-source details")
    parser.add_argument("--kb-path", type=str, default=None, help="Path to groundtruth.db")
    parser.add_argument(
        "--thread-level",
        action="store_true",
        help="Include compressed bridge-thread harvest (one DELIB per thread; default off for v1)",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Write machine-readable JSON summary to this path (for session-wrap consumption)",
    )
    parser.add_argument(
        "--loud-wrap",
        action="store_true",
        help=(
            "Enable wrap-hook ALARM semantics: exit non-zero when warnings exceed "
            "baseline or exit_status != ok. Default silent for v1 per implementation plan."
        ),
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=str(REPO_ROOT / "scripts" / "harvest_warning_baseline.json"),
        help="Path to warning-baseline JSON (default: scripts/harvest_warning_baseline.json)",
    )
    args = parser.parse_args()

    results = harvest(
        apply=args.apply,
        session_filter=args.session,
        verbose=args.verbose,
        kb_path=args.kb_path,
        thread_level=args.thread_level,
    )

    has_errors = any(r.action == "error" for r in results)
    exit_status = "error" if has_errors else "ok"
    summary = build_summary_json(results, exit_status=exit_status, applied=args.apply)

    if args.json_output:
        Path(args.json_output).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    baseline = load_warning_baseline(Path(args.baseline))
    verdict, reasons = compute_wrap_verdict(summary, baseline, loud=args.loud_wrap)

    if verdict == "ALARM":
        print(f"\n[WRAP-HOOK ALARM] reasons: {'; '.join(reasons)}", file=sys.stderr)
        return 2

    if args.loud_wrap and verdict == "OK":
        print("\n[WRAP-HOOK OK] warnings within baseline, exit_status=ok", file=sys.stderr)

    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
