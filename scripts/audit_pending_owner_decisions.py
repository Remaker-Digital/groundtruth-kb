"""Read-only audit + bounded cleanup of memory/pending-owner-decisions.md.

Per Sub-slice D of GTKB-GOV-AUQ-ENFORCEMENT-STACK
(bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-003.md
GO at -004).

Usage:
    python scripts/audit_pending_owner_decisions.py            # human report
    python scripts/audit_pending_owner_decisions.py --json     # JSON report
    python scripts/audit_pending_owner_decisions.py --cleanup  # apply cleanup mutation

The audit is non-mutating; it copies the live durable file to a tempfile
before invoking the canonical parser. The parser has a corruption-rename
side-effect on parse failure (renames target to .corrupted-<ts>), so the
copy-to-tempfile dance keeps the live file safe.

The --cleanup mode moves historical-FP entries (entries in ## Pending
with detected_via starting "prose:" AND asked_at predating Sub-slice A
-014 VERIFIED) to ## History via the canonical _write_pending_file
atomic writer. Idempotent (skips entries already marked) and AUQ-safe
(aborts before any write if any candidate has detected_via:
ask_user_question).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
PENDING_PATH = REPO_ROOT / "memory" / "pending-owner-decisions.md"
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "owner-decision-tracker.py"
AUDIT_LOG_DIR = REPO_ROOT / "memory" / "audit-log"
AUDIT_LOG_PATH = AUDIT_LOG_DIR / "sub-slice-d-cleanup-2026-05-04.log"

# Sub-slice A -014 VERIFIED date threshold (UTC, start-of-day). Entries
# with asked_at strictly before this are pre-tightening false-positive
# candidates per the umbrella's historical-FP definition.
SUBSLICE_A_VERIFIED_DATE = datetime(2026, 5, 4, 0, 0, 0, tzinfo=timezone.utc)

# Recognized detected_via values per Sub-slice A -014 split + AUQ.
RECOGNIZED_DETECTED_VIA = frozenset({
    "ask_user_question",
    "prose:offering_or_choice",
    "prose:should_i_or",
    "prose:awaiting_input",            # legacy pre-Sub-slice-A-007 split
    "prose:awaiting_input_q",          # post-split interrogative variant
    "prose:awaiting_input_first_person",
    "prose:standing_by_for",           # legacy pre-Sub-slice-A-007 split
    "prose:standing_by_for_q",
    "prose:standing_by_for_first_person",
    "prose:your_decision_q",
})

# Idempotency marker appended to moved entries' notes field.
CLEANUP_NOTES_MARKER = "Sub-slice D cleanup audit"

# Reference scanner: matches DECISION-NNNN tokens in free text.
DECISION_REF_RE = re.compile(r"\bDECISION-\d+\b")


def _load_hook_module():
    """Load the owner-decision-tracker hook as a module via importlib.

    The hook is at .claude/hooks/owner-decision-tracker.py (not on
    sys.path); importlib.util.spec_from_file_location is the canonical
    way to load it as a regular Python module.
    """
    spec = importlib.util.spec_from_file_location("owner_decision_tracker_audit_hook", HOOK_PATH)
    assert spec and spec.loader, f"failed to load hook spec from {HOOK_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["owner_decision_tracker_audit_hook"] = module
    spec.loader.exec_module(module)
    return module


def _parse_iso(value: str) -> datetime | None:
    """Parse an ISO-8601 timestamp; return None on failure. Treat trailing Z as UTC."""
    if not value:
        return None
    try:
        s = value.replace("Z", "+00:00") if value.endswith("Z") else value
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _audit_parsed_sections(sections: dict[str, list], hook) -> dict[str, Any]:
    """Validate parsed sections and return a findings dict.

    Sections is the dict returned by hook._read_pending_file (keys:
    "pending", "resolved", "history"; values: list[DecisionEntry]).
    """
    all_entries: list = []
    for entries in sections.values():
        all_entries.extend(entries)

    # --- Schema validation ---
    missing_required: list[dict] = []
    bad_id: list[str] = []
    bad_asked_at: list[str] = []
    unrecognized_detected_via: list[dict] = []
    duplicate_ids: list[str] = []
    section_mismatch: list[dict] = []

    seen_ids: dict[str, int] = Counter()

    for entry in all_entries:
        seen_ids[entry.id] += 1
        # Required fields.
        if not entry.id or not entry.id.startswith("DECISION-"):
            bad_id.append(entry.id)
        elif not re.fullmatch(r"DECISION-\d+", entry.id):
            bad_id.append(entry.id)
        if not entry.asked_at:
            missing_required.append({"id": entry.id, "field": "asked_at"})
        elif _parse_iso(entry.asked_at) is None:
            bad_asked_at.append(entry.id)
        if not entry.status:
            missing_required.append({"id": entry.id, "field": "status"})
        if not getattr(entry, "detected_via", None):
            missing_required.append({"id": entry.id, "field": "detected_via"})
        elif entry.detected_via not in RECOGNIZED_DETECTED_VIA:
            unrecognized_detected_via.append({"id": entry.id, "value": entry.detected_via})

    duplicate_ids = sorted(eid for eid, count in seen_ids.items() if count > 1)

    # Section/status placement: entries in "pending" should have status="pending";
    # entries in "resolved"/"history" should have status="resolved" (or other non-pending).
    for section_name, entries in sections.items():
        for entry in entries:
            if section_name == "pending" and entry.status != "pending":
                section_mismatch.append({
                    "id": entry.id, "section": section_name, "status": entry.status,
                })
            elif section_name in ("resolved", "history") and entry.status == "pending":
                section_mismatch.append({
                    "id": entry.id, "section": section_name, "status": entry.status,
                })

    # --- Orphan-ID detection (F1) ---
    all_ids = set(seen_ids.keys())
    referenced_ids: set[str] = set()
    for entry in all_entries:
        for field in ("notes", "question", "answer"):
            text = getattr(entry, field, "") or ""
            for m in DECISION_REF_RE.finditer(text):
                referenced_ids.add(m.group(0))
    orphan_refs = sorted(referenced_ids - all_ids)

    # --- Distributions ---
    detected_via_distribution = dict(Counter(
        getattr(e, "detected_via", None) for e in all_entries
    ))
    status_distribution = dict(Counter(
        e.status for e in all_entries
    ))
    section_counts = {s: len(es) for s, es in sections.items()}

    # --- Historical-FP candidates (F3 prep) ---
    historical_fp_candidates: list[dict] = []
    for entry in sections.get("pending", []):
        if entry.detected_via and entry.detected_via.startswith("prose:"):
            asked_dt = _parse_iso(entry.asked_at)
            if asked_dt is not None and asked_dt < SUBSLICE_A_VERIFIED_DATE:
                already_cleaned = CLEANUP_NOTES_MARKER in (entry.notes or "")
                historical_fp_candidates.append({
                    "id": entry.id,
                    "asked_at": entry.asked_at,
                    "detected_via": entry.detected_via,
                    "already_marked": already_cleaned,
                })

    return {
        "section_counts": section_counts,
        "total_entries": len(all_entries),
        "detected_via_distribution": detected_via_distribution,
        "status_distribution": status_distribution,
        "schema_findings": {
            "missing_required": missing_required,
            "bad_id_format": bad_id,
            "bad_asked_at": bad_asked_at,
            "unrecognized_detected_via": unrecognized_detected_via,
            "duplicate_ids": duplicate_ids,
            "section_status_mismatch": section_mismatch,
        },
        "orphan_id_references": orphan_refs,
        "historical_fp_candidates": historical_fp_candidates,
    }


def audit(path: Path = PENDING_PATH) -> dict[str, Any]:
    """Audit the durable file. Copies to tempfile before parsing (corruption-safe)."""
    if not path.exists():
        return {"error": f"file not found: {path}", "total_entries": 0}

    hook = _load_hook_module()

    # Copy-to-tempfile dance: corruption-rename in _read_pending_file
    # would target the temp copy, leaving the live file untouched.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tf:
        tmp_path = Path(tf.name)
    try:
        shutil.copy2(path, tmp_path)
        sections = hook._read_pending_file(tmp_path)
        return _audit_parsed_sections(sections, hook)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        # If parser triggered the corruption-rename path, also clean up the
        # renamed temp file (.corrupted-<ts> sibling).
        for sibling in tmp_path.parent.glob(tmp_path.name + ".corrupted-*"):
            try:
                sibling.unlink()
            except OSError:
                pass


def _build_cleanup_notes(existing: str) -> str:
    """Append the cleanup marker to the entry's notes field (idempotent)."""
    marker_line = (
        f"{CLEANUP_NOTES_MARKER} 2026-05-04 per "
        "DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE; pre-tightening false positive "
        "(Sub-slice A -014 VERIFIED 2026-05-04)."
    )
    if not existing:
        return marker_line
    if CLEANUP_NOTES_MARKER in existing:
        return existing
    return f"{existing} | {marker_line}"


def cleanup(path: Path = PENDING_PATH, *, log_path: Path = AUDIT_LOG_PATH) -> dict[str, Any]:
    """Apply bounded cleanup. Move historical-FP candidates from pending to history.

    Idempotent (entries already marked are skipped). AUQ-safe (aborts
    before any write if any candidate is an AUQ entry). Atomic-write via
    canonical _write_pending_file (which uses .tmp + os.replace).
    """
    if not path.exists():
        return {"error": f"file not found: {path}", "moved": 0}

    hook = _load_hook_module()

    # First pass: audit live (non-mutating; uses tempfile copy)
    pre_audit = audit(path)

    # AUQ safety guard: if any candidate is an AUQ entry, abort.
    for cand in pre_audit.get("historical_fp_candidates", []):
        if cand.get("detected_via") == "ask_user_question":
            raise RuntimeError(
                f"AUQ-entry safety violation: candidate {cand['id']} has "
                f"detected_via=ask_user_question; cleanup aborted before any write."
            )

    # Second pass: re-parse the LIVE file (need to mutate this parsed view).
    # Using the live path here is safe because the parser would only mutate the
    # live file via corruption-rename if the file is malformed; we already
    # established it parses cleanly in the audit pass above. If pre_audit
    # reports ANY schema findings, abort cleanup before any write — the
    # mutating tool must not proceed against a state the audit itself flags
    # as anomalous (per Codex -006 F2).
    sf = pre_audit.get("schema_findings", {})
    schema_finding_classes = (
        "missing_required",
        "bad_id_format",
        "bad_asked_at",
        "unrecognized_detected_via",
        "duplicate_ids",
        "section_status_mismatch",
    )
    nonempty_classes = [cls for cls in schema_finding_classes if sf.get(cls)]
    if nonempty_classes:
        return {
            "moved": 0,
            "skipped_due_to_schema_findings": True,
            "schema_finding_classes_nonempty": nonempty_classes,
            "pre_audit": pre_audit,
        }

    sections = hook._read_pending_file(path)

    # Identify candidates in the LIVE parse (re-derive to ensure consistency).
    moved_entries: list = []
    new_pending = []
    for entry in sections.get("pending", []):
        is_candidate = (
            entry.detected_via
            and entry.detected_via.startswith("prose:")
            and (_parse_iso(entry.asked_at) or datetime.max.replace(tzinfo=timezone.utc))
            < SUBSLICE_A_VERIFIED_DATE
        )
        if not is_candidate:
            new_pending.append(entry)
            continue
        if CLEANUP_NOTES_MARKER in (entry.notes or ""):
            # Idempotency: already cleaned; leave in place.
            new_pending.append(entry)
            continue
        # Move: mark with cleanup notes, change status to resolved if pending.
        entry.notes = _build_cleanup_notes(entry.notes)
        if entry.status == "pending":
            entry.status = "resolved"
        moved_entries.append(entry)

    # Always create the audit-log directory and write a run-marker line so
    # the log file exists as evidence of every cleanup invocation, even when
    # no entries are moved (correct no-op outcome).
    log_path.parent.mkdir(parents=True, exist_ok=True)
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with log_path.open("a", encoding="utf-8") as lf:
        lf.write(
            f"{run_ts} run started cleanup invocation against {path.name} "
            f"per DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE\n"
        )

        if not moved_entries:
            lf.write(
                f"{run_ts} run completed no-op (0 historical-FP candidates "
                f"in ## Pending; pending section size={len(sections.get('pending', []))})\n"
            )

    if not moved_entries:
        return {
            "moved": 0,
            "noop": True,
            "pre_audit": pre_audit,
        }

    sections["pending"] = new_pending
    sections["history"] = list(sections.get("history", [])) + moved_entries

    # Atomic write via canonical writer.
    hook._write_pending_file(path, sections)

    # Append per-entry move lines to audit log (run-marker already written).
    with log_path.open("a", encoding="utf-8") as lf:
        for entry in moved_entries:
            lf.write(
                f"{run_ts} moved {entry.id} (detected_via={entry.detected_via}, "
                f"asked_at={entry.asked_at}) from pending to history "
                f"per DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE\n"
            )

    return {
        "moved": len(moved_entries),
        "moved_ids": [e.id for e in moved_entries],
        "pre_audit": pre_audit,
    }


def _human_format(report: dict[str, Any]) -> str:
    out = []
    out.append(f"=== Audit of {PENDING_PATH.relative_to(REPO_ROOT)} ===")
    out.append(f"Section counts: {report.get('section_counts')}")
    out.append(f"Total entries: {report.get('total_entries')}")
    out.append("")
    out.append(f"detected_via distribution: {report.get('detected_via_distribution')}")
    out.append(f"status distribution: {report.get('status_distribution')}")
    out.append("")
    sf = report.get("schema_findings", {})
    out.append("Schema findings:")
    out.append(f"  missing_required: {len(sf.get('missing_required', []))}")
    out.append(f"  bad_id_format: {len(sf.get('bad_id_format', []))}")
    out.append(f"  bad_asked_at: {len(sf.get('bad_asked_at', []))}")
    out.append(f"  unrecognized_detected_via: {len(sf.get('unrecognized_detected_via', []))}")
    out.append(f"  duplicate_ids: {len(sf.get('duplicate_ids', []))}")
    out.append(f"  section_status_mismatch: {len(sf.get('section_status_mismatch', []))}")
    out.append("")
    out.append(f"Orphan ID references: {len(report.get('orphan_id_references', []))}")
    out.append(f"Historical-FP candidates (in ## Pending, prose:*, pre-Sub-slice-A-014): "
               f"{len(report.get('historical_fp_candidates', []))}")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--cleanup", action="store_true",
                        help="Apply bounded cleanup mutation (move historical-FP candidates "
                             "from ## Pending to ## History; atomic, idempotent, AUQ-safe).")
    args = parser.parse_args()

    if args.cleanup:
        try:
            result = cleanup(PENDING_PATH)
        except RuntimeError as exc:
            print(f"CLEANUP ABORTED: {exc}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Cleanup complete. Moved {result.get('moved', 0)} entries.")
            if result.get("moved_ids"):
                for eid in result["moved_ids"]:
                    print(f"  moved: {eid}")
            if result.get("noop"):
                print("  (no candidates found; cleanup ran as no-op)")
        return 0

    report = audit(PENDING_PATH)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(_human_format(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
