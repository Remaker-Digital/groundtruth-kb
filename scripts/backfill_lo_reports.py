#!/usr/bin/env python3
"""
Backfill existing Loyal Opposition reports into the GroundTruth deliberation archive.

WI-3162: Imports INSIGHTS-*.md files from CODEX-INSIGHT-DROPBOX into the
Agent Red project Knowledge Database as deliberation sources with structured
outcome metadata (go, no_go, owner_decision, informational).

Usage:
    # Dry run (default) -- shows what would be imported
    python scripts/backfill_lo_reports.py

    # Apply mode -- actually imports into KB
    python scripts/backfill_lo_reports.py --apply

    # Verbose dry run
    python scripts/backfill_lo_reports.py --verbose

Prerequisites:
    - GroundTruth KB must have AR key family redaction patterns
    - Agent Red project KB must be accessible

Codex GO: bridge/lo-report-backfill-018.md

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# SPEC/WI extraction
# ---------------------------------------------------------------------------

SPEC_RE = re.compile(r"\bSPEC-\d+(?:\.\d+)*\b")
WI_RE = re.compile(r"\bWI-\d+\b")

# ---------------------------------------------------------------------------
# Agent Red key families for redaction survivor scanning
# ---------------------------------------------------------------------------

_AR_KEY_SURVIVOR_RE = re.compile(r"(ar_live|ar_user|ar_spa_plat|pk_live|arsk)_[A-Za-z0-9_-]{10,}")

# ---------------------------------------------------------------------------
# Verdict field regex -- newline-safe (horizontal whitespace only after colon)
# ---------------------------------------------------------------------------

_VERDICT_FIELD_RE = re.compile(
    r"(?:^|\n)"
    r"[^\S\r\n]*"
    r"(?:\*{1,2})?"
    r"[Vv]erdict"
    r"(?:\*{1,2})?"
    r"[^\S\r\n]*[:=][^\S\r\n]*"
    r"(.+)?",
)

# Bullet verdict metadata (- verdict: GO)
_BULLET_VERDICT_RE = re.compile(
    r"^[-*]\s*[Vv]erdict\s*[:=]\s*(?P<verdict>.+)",
    re.MULTILINE,
)

# Verdict section heading (any level, optional qualifier)
_VERDICT_SECTION_RE = re.compile(
    r"^(#{1,6})\s+"
    r"(?:Executive|Overall|Summary|Final|Advisory)?\s*"
    r"[Vv]erdict"
    r"(?:\s*[:\-]\s*(?P<inline>.+))?"
    r"\s*$",
    re.MULTILINE,
)

# Unparsed structured signal detection (scan window only)
_UNPARSED_SIGNAL_RE = re.compile(
    r"(?:^#{1,6}\s+.*[Vv]erdict|"
    r"^\s*\*?\*?[Vv]erdict\*?\*?\s*[:=]|"
    r"^[-*]\s*[Vv]erdict\s*[:=])",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Verdict text parser
# ---------------------------------------------------------------------------


def _parse_verdict_text(raw: str) -> str | None:
    """Parse a verdict string into an outcome enum value."""
    # Strip Markdown formatting (backticks, bold) but NOT underscores
    # since owner_decision contains underscores
    text = re.sub(r"[`*]", "", raw).strip().lower()
    if not text:
        return None
    if "owner_decision" in text or "owner decision" in text:
        return "owner_decision"
    if "no-go" in text or "no_go" in text or "nogo" in text:
        return "no_go"
    if "verified" in text:
        return "go"
    if "lgtm" in text:
        return "go"
    if re.search(r"\bgo\b", text):
        return "go"
    return None


# ---------------------------------------------------------------------------
# Filename verdict tokens
# ---------------------------------------------------------------------------


def _extract_filename_signals(filename: str) -> list[str]:
    """Extract verdict signals from filename tokens."""
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    normalized = stem.upper().replace("NO-GO", "NOGO")
    tokens = re.split(r"[^A-Z0-9]+", normalized)
    signals = []
    for token in tokens:
        if token == "NOGO":
            signals.append("no_go")
        elif token in ("GO", "VERIFIED", "VERIFICATION", "REVERIFICATION", "LGTM"):
            signals.append("go")
    return signals


# ---------------------------------------------------------------------------
# Top-field signal extraction (newline-safe + bullet metadata)
# ---------------------------------------------------------------------------


def _extract_top_field_signals(content: str) -> list[tuple[str, str]]:
    """Extract verdict signals from top-of-file fields."""
    signals: list[tuple[str, str]] = []
    top = "\n".join(content.split("\n")[:30])

    for m in _VERDICT_FIELD_RE.finditer(top):
        captured = m.group(1)
        if captured and captured.strip():
            parsed = _parse_verdict_text(captured)
            if parsed:
                signals.append(("top_field", parsed))
        else:
            after = content[m.end() :]
            for line in after.split("\n")[:10]:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    break
                bullet_text = re.sub(r"^[-*]\s*", "", stripped)
                parsed = _parse_verdict_text(bullet_text)
                if parsed:
                    signals.append(("top_field", parsed))

    for m in _BULLET_VERDICT_RE.finditer(top):
        parsed = _parse_verdict_text(m.group("verdict"))
        if parsed:
            signals.append(("top_field", parsed))

    return signals


# ---------------------------------------------------------------------------
# Verdict section signal extraction (multi-signal)
# ---------------------------------------------------------------------------


def _extract_section_verdicts(content: str) -> list[tuple[str, str]]:
    """Collect all verdict signals from the verdict section."""
    match = _VERDICT_SECTION_RE.search(content)
    if not match:
        return []

    signals: list[tuple[str, str]] = []

    inline = match.group("inline")
    if inline:
        parsed = _parse_verdict_text(inline)
        if parsed:
            signals.append(("section", parsed))

    after_heading = content[match.end() :]
    for line in after_heading.split("\n")[:15]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            break
        verdict_line = re.sub(r"^[-*]\s*", "", stripped)
        parsed = _parse_verdict_text(verdict_line)
        if parsed:
            signals.append(("section", parsed))

    return signals


# ---------------------------------------------------------------------------
# Unparsed signal warnings (structured locations only)
# ---------------------------------------------------------------------------


def _check_unparsed_signals(content: str, filename: str) -> list[str]:
    """Detect structured verdict content the parser didn't extract."""
    warnings: list[str] = []
    lines = content.split("\n")

    title_line = ""
    for line in lines:
        if line.startswith("#"):
            title_line = line
            break

    top_window = "\n".join(lines[:30])

    section_match = _VERDICT_SECTION_RE.search(content)
    section_window = ""
    if section_match:
        start = section_match.start()
        end_area = content.find("\n#", section_match.end())
        if end_area == -1:
            end_area = min(section_match.end() + 500, len(content))
        section_window = content[start:end_area]

    scan_text = title_line + "\n" + top_window + "\n" + section_window

    structured_signals = _UNPARSED_SIGNAL_RE.findall(scan_text)
    if structured_signals:
        warnings.append(
            f"Unparsed structured verdict signal in {filename}: "
            f"{len(structured_signals)} match(es) in scan window. "
            f"First: {structured_signals[0][:60]}"
        )

    return warnings


# ---------------------------------------------------------------------------
# Main outcome extractor
# ---------------------------------------------------------------------------


def extract_outcome(content: str, filename: str) -> tuple[str, list[str]]:
    """Extract outcome using structured fields first, filename fallback last.

    Returns (outcome, warnings).
    """
    signals: list[tuple[str, str]] = []
    warnings: list[str] = []

    # Source 1: top-of-file fields + bullet metadata
    signals.extend(_extract_top_field_signals(content))

    # Source 2: verdict section (multi-signal)
    signals.extend(_extract_section_verdicts(content))

    # Source 3: filename tokens (fallback)
    for sig in _extract_filename_signals(filename):
        signals.append(("filename", sig))

    # Resolution
    if not signals:
        unparsed = _check_unparsed_signals(content, filename)
        warnings.extend(unparsed)
        return "informational", warnings

    unique_outcomes = set(outcome for _, outcome in signals)

    if len(unique_outcomes) == 1:
        return unique_outcomes.pop(), warnings

    structured = [(src, out) for src, out in signals if src != "filename"]
    if structured:
        structured_outcomes = set(out for _, out in structured)
        if len(structured_outcomes) == 1:
            return structured_outcomes.pop(), warnings

    warnings.append(f"Conflicting verdict signals in {filename}: " + ", ".join(f"{src}={out}" for src, out in signals))
    return "informational", warnings


# ---------------------------------------------------------------------------
# SPEC/WI ID extraction (ordered unique, title/filename priority)
# ---------------------------------------------------------------------------


def ordered_unique_ids(pattern: re.Pattern[str], text: str) -> list[str]:
    """Extract IDs preserving first-occurrence order, deduplicated."""
    seen: set[str] = set()
    result: list[str] = []
    for match in pattern.finditer(text):
        value = match.group(0)
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def extract_artifact_ids(content: str, filename: str) -> tuple[list[str], list[str]]:
    """Extract SPEC/WI IDs, filename+title first, then body."""
    title_line = ""
    for line in content.split("\n"):
        if line.startswith("#"):
            title_line = line
            break
    priority_text = filename + "\n" + title_line
    full_text = priority_text + "\n" + content

    spec_ids = ordered_unique_ids(SPEC_RE, full_text)
    wi_ids = ordered_unique_ids(WI_RE, full_text)
    return spec_ids, wi_ids


# ---------------------------------------------------------------------------
# Report processing result
# ---------------------------------------------------------------------------


@dataclass
class ReportResult:
    filename: str
    outcome: str
    spec_ids: list[str]
    wi_ids: list[str]
    warnings: list[str] = field(default_factory=list)
    redaction_count: int = 0
    pre_redaction_survivors: int = 0
    post_redaction_survivors: int = 0
    action: str = "skipped"  # created, skipped, changed_source


def _extract_title(content: str) -> str:
    """Extract the first heading as the report title."""
    for line in content.split("\n"):
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Untitled LO Report"


def _extract_summary(content: str, max_len: int = 200) -> str:
    """Extract a short summary from the first non-heading paragraph."""
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
            return stripped[:max_len]
    return ""


def _extract_session_id(filename: str) -> str | None:
    """Extract session ID (S###) from filename if present."""
    m = re.search(r"\b(S\d{3})\b", filename)
    return m.group(1) if m else None


def _make_source_ref(filename: str) -> str:
    """Build stable POSIX source_ref for dedup."""
    return f"independent-progress-assessments/CODEX-INSIGHT-DROPBOX/{filename}"


def _load_kb(kb_path: str | None = None):
    """Import and instantiate the Agent Red KnowledgeDB shim."""
    sys.path.insert(
        0,
        str(Path(__file__).resolve().parents[1] / "tools" / "knowledge-db"),
    )
    from db import KnowledgeDB

    path = kb_path or str(Path(__file__).resolve().parents[1] / "tools" / "knowledge-db" / "knowledge.db")
    return KnowledgeDB(path)


def _simulate_redaction(content: str):
    """Import KnowledgeDB just for redact_content, without full DB init."""
    try:
        sys.path.insert(
            0,
            str(Path(__file__).resolve().parents[1] / "tools" / "knowledge-db"),
        )
        from groundtruth_kb.db import KnowledgeDB as _GT

        return _GT.redact_content(content)
    except ImportError:
        return content, None


# ---------------------------------------------------------------------------
# Dry-run / apply entry point
# ---------------------------------------------------------------------------


def process_reports(
    report_dir: Path,
    *,
    apply: bool = False,
    verbose: bool = False,
    kb_path: str | None = None,
) -> list[ReportResult]:
    """Process all INSIGHTS-*.md files in report_dir.

    Returns list of ReportResult for summary reporting.
    """
    files = sorted(report_dir.glob("INSIGHTS-*.md"))
    if not files:
        print(f"No INSIGHTS-*.md files found in {report_dir}")
        return []

    results: list[ReportResult] = []
    outcome_counts: Counter[str] = Counter()
    total_warnings = 0
    total_conflicts = 0
    total_missing_ids = 0
    total_pre_survivors = 0
    total_post_survivors = 0
    total_redactions = 0
    created_count = 0
    skipped_count = 0
    changed_count = 0
    links_created = 0
    missing_link_ids = 0

    db = None
    if apply:
        try:
            db = _load_kb(kb_path)
        except ImportError:
            print("ERROR: Cannot import KnowledgeDB. Ensure tools/knowledge-db/db.py exists.")
            sys.exit(1)

    for filepath in files:
        filename = filepath.name
        content = filepath.read_text(encoding="utf-8", errors="ignore")

        # Extract outcome
        outcome, warnings = extract_outcome(content, filename)
        outcome_counts[outcome] += 1

        # Extract SPEC/WI IDs
        spec_ids, wi_ids = extract_artifact_ids(content, filename)

        if not spec_ids and not wi_ids:
            total_missing_ids += 1
            if verbose:
                warnings.append(f"No SPEC or WI IDs found in {filename}")

        total_warnings += len(warnings)
        total_conflicts += sum(1 for w in warnings if "Conflicting" in w)

        # Pre-redaction AR key scan
        pre_survivors = len(_AR_KEY_SURVIVOR_RE.findall(content))
        total_pre_survivors += pre_survivors

        # Redaction simulation (both dry-run and apply)
        redacted_content, redaction_notes = _simulate_redaction(content)
        redaction_count = 0
        if redaction_notes:
            for note in redaction_notes.split(";"):
                if ":" in note:
                    try:
                        redaction_count += int(note.split(":")[1].strip().split()[0])
                    except (ValueError, IndexError):
                        pass
        total_redactions += redaction_count

        # Post-redaction survivor check
        post_survivors = len(_AR_KEY_SURVIVOR_RE.findall(redacted_content))
        total_post_survivors += post_survivors
        if post_survivors > 0:
            warnings.append(f"REDACTION SURVIVOR in {filename}: {post_survivors} AR key(s) remain after redaction")

        # Apply mode: upsert deliberation + link IDs
        action = "skipped"
        if apply and db is not None:
            import hashlib

            source_ref = _make_source_ref(filename)
            title = _extract_title(content)
            summary = _extract_summary(content)
            session_id = _extract_session_id(filename)
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # --- Existence checks for SPEC/WI IDs ---
            existing_specs = []
            missing_specs = []
            for sid in spec_ids:
                if db.get_spec(sid) is not None:
                    existing_specs.append(sid)
                else:
                    missing_specs.append(sid)

            existing_wis = []
            missing_wis = []
            for wid in wi_ids:
                if db.get_work_item(wid) is not None:
                    existing_wis.append(wid)
                else:
                    missing_wis.append(wid)

            if missing_specs or missing_wis:
                missing_link_ids += len(missing_specs) + len(missing_wis)
                if verbose:
                    if missing_specs:
                        warnings.append(f"Missing SPECs in KB for {filename}: {', '.join(missing_specs)}")
                    if missing_wis:
                        warnings.append(f"Missing WIs in KB for {filename}: {', '.join(missing_wis)}")

            # Only use existing IDs for primary fields
            primary_spec = existing_specs[0] if existing_specs else None
            primary_wi = existing_wis[0] if existing_wis else None

            # --- Pre-upsert classification ---
            # Check ALL current rows for source_ref (not just one)
            conn = db._get_conn()
            existing_rows = conn.execute(
                "SELECT content_hash FROM current_deliberations WHERE source_ref = ?",
                (source_ref,),
            ).fetchall()
            existing_hashes = {r["content_hash"] for r in existing_rows}

            if content_hash in existing_hashes:
                # Exact content already imported — idempotent skip
                action = "skipped"
                skipped_count += 1
            elif existing_rows:
                # Same source_ref but different content — changed source
                action = "same_source_changed_content"
                changed_count += 1
            else:
                action = "created"

            # --- Upsert (skip if idempotent) ---
            delib = None
            if action == "skipped":
                pass
            else:
                delib = db.upsert_deliberation_source(
                    source_type="lo_review",
                    source_ref=source_ref,
                    content=content,
                    title=title,
                    summary=summary,
                    outcome=outcome,
                    spec_id=primary_spec,
                    work_item_id=primary_wi,
                    session_id=session_id,
                    origin_project="agent-red",
                    origin_repo="Remaker-Digital/agent-red-customer-engagement",
                    changed_by="backfill_lo_reports.py",
                    change_reason="WI-3162 automated backfill",
                )
                if action == "created":
                    created_count += 1

            # --- Link additional existing IDs ---
            # Use the upsert-returned dict for the correct delib ID
            if delib is not None and action != "skipped":
                delib_id = delib["id"]
                for sid in existing_specs[1:]:
                    db.link_deliberation_spec(delib_id, sid)
                    links_created += 1
                for wid in existing_wis[1:]:
                    db.link_deliberation_work_item(delib_id, wid)
                    links_created += 1

        result = ReportResult(
            filename=filename,
            outcome=outcome,
            spec_ids=spec_ids,
            wi_ids=wi_ids,
            warnings=warnings,
            redaction_count=redaction_count,
            pre_redaction_survivors=pre_survivors,
            post_redaction_survivors=post_survivors,
            action=action,
        )
        results.append(result)

        if verbose:
            primary_spec = spec_ids[0] if spec_ids else "-"
            primary_wi = wi_ids[0] if wi_ids else "-"
            action_flag = f" [{action}]" if apply else ""
            warn_flag = " [!]" if warnings else ""
            print(f"  {outcome:15s} {primary_spec:12s} {primary_wi:8s} {filename}{action_flag}{warn_flag}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"LO Report Backfill {'[APPLY]' if apply else '[DRY RUN]'}")
    print(f"{'=' * 60}")
    print(f"Total reports:            {len(files)}")
    print("Outcome distribution:")
    for outcome_val in ["go", "no_go", "owner_decision", "informational"]:
        count = outcome_counts.get(outcome_val, 0)
        print(f"  {outcome_val:20s}  {count}")
    print(f"Conflict warnings:        {total_conflicts}")
    print(f"Total warnings:           {total_warnings}")
    print(f"Reports with no IDs:      {total_missing_ids}")
    print(f"Pre-redaction AR keys:    {total_pre_survivors}")
    print(f"Post-redaction survivors: {total_post_survivors}")
    print(f"Total redactions:         {total_redactions}")
    if apply:
        print(f"Created:                  {created_count}")
        print(f"Skipped (idempotent):     {skipped_count}")
        print(f"Changed source:           {changed_count}")
        print(f"Relation links created:   {links_created}")
        print(f"Missing referenced IDs:   {missing_link_ids}")
    print(f"{'=' * 60}")

    if total_conflicts > 0:
        print(f"\nConflicting verdicts ({total_conflicts}):")
        for r in results:
            for w in r.warnings:
                if "Conflicting" in w:
                    print(f"  {w}")

    unparsed = [w for r in results for w in r.warnings if "Unparsed" in w]
    if unparsed:
        print(f"\nUnparsed structured signals ({len(unparsed)}):")
        for w in unparsed[:10]:
            print(f"  {w}")
        if len(unparsed) > 10:
            print(f"  ... and {len(unparsed) - 10} more")

    survivors = [w for r in results for w in r.warnings if "SURVIVOR" in w]
    if survivors:
        print(f"\nRedaction survivors ({len(survivors)}):")
        for w in survivors:
            print(f"  {w}")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Backfill LO reports into deliberation archive")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually import into KB (default: dry run)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show per-file details",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX",
        help="Directory containing INSIGHTS-*.md files",
    )
    parser.add_argument(
        "--kb-path",
        type=str,
        default=None,
        help="Path to knowledge.db (default: tools/knowledge-db/knowledge.db)",
    )
    args = parser.parse_args()

    if args.apply:
        print("WARNING: Apply mode will import reports into the Knowledge Database.")
        print("Press Ctrl+C to cancel.\n")

    process_reports(
        args.report_dir,
        apply=args.apply,
        verbose=args.verbose,
        kb_path=args.kb_path,
    )


if __name__ == "__main__":
    main()
