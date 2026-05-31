"""Deterministic audit for early-project requirement quality drift.

The audit is intentionally read-only against ``groundtruth.db``. It evaluates
historical version-1 specification rows created before the Loyal Opposition
review gate matured, excludes rows whose current version was touched after the
maturation cutoff, and emits deterministic JSON plus an optional Markdown
classification manifest.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("groundtruth.db")
DEFAULT_CHANGED_BEFORE = "2026-04-01"
DEFAULT_FOCUS_REQUIREMENT_BEFORE = "2026-03-01"
DEFAULT_REPORT_TITLE = "Early Project Requirements Quality Audit"

ALLOWED_STATES = (
    "accept_as_is",
    "correction_candidate",
    "supersession_candidate",
    "retirement_candidate",
    "requires_owner_clarification",
)

STOPWORDS = {
    "and",
    "are",
    "for",
    "from",
    "into",
    "must",
    "not",
    "shall",
    "should",
    "the",
    "this",
    "that",
    "with",
}

HISTORICAL_BASE_SQL = "SELECT COUNT(*) FROM specifications WHERE version = 1 AND changed_at < :changed_before"

FOCUS_REQUIREMENT_SQL = (
    "SELECT COUNT(*) FROM specifications "
    "WHERE version = 1 AND type = 'requirement' AND status = 'specified' "
    "AND changed_at < :focus_before"
)

MATURATION_EXCLUSION_SQL = (
    "SELECT COUNT(DISTINCT s.id) FROM specifications s "
    "JOIN current_specifications cs ON cs.id = s.id "
    "WHERE s.version = 1 AND s.changed_at < :changed_before "
    "AND cs.changed_at >= :changed_before"
)

CORPUS_SQL = (
    "SELECT s.id, s.version, s.title, COALESCE(s.description, '') AS description, "
    "COALESCE(s.priority, '') AS priority, COALESCE(s.scope, '') AS scope, "
    "COALESCE(s.section, '') AS section, COALESCE(s.handle, '') AS handle, "
    "COALESCE(s.tags, '') AS tags, s.status, COALESCE(s.assertions, '') AS assertions, "
    "s.changed_at, COALESCE(s.change_reason, '') AS change_reason, "
    "COALESCE(s.type, '') AS type, COALESCE(s.authority, '') AS authority, "
    "COALESCE(s.constraints, '') AS constraints, COALESCE(s.affected_by, '') AS affected_by, "
    "COALESCE(s.testability, '') AS testability, COALESCE(s.source_paths, '') AS source_paths, "
    "cs.version AS current_version, COALESCE(cs.title, '') AS current_title, "
    "COALESCE(cs.description, '') AS current_description, COALESCE(cs.status, '') AS current_status, "
    "cs.changed_at AS current_changed_at "
    "FROM specifications s "
    "LEFT JOIN current_specifications cs ON cs.id = s.id "
    "WHERE s.version = 1 AND s.changed_at < :changed_before "
    "AND NOT EXISTS ("
    "  SELECT 1 FROM current_specifications post "
    "  WHERE post.id = s.id AND post.changed_at >= :changed_before"
    ") "
    "ORDER BY s.id"
)


@dataclass(frozen=True)
class AuditRow:
    spec_id: str
    historical_version: int
    title: str
    description: str
    status: str
    spec_type: str
    changed_at: str
    assertions: str
    testability: str
    source_paths: str
    current_version: int | None
    current_title: str
    current_description: str
    current_status: str
    current_changed_at: str | None


def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2 and token not in STOPWORDS}


def _normalize_title(title: str) -> str:
    return " ".join(sorted(_tokens(title)))


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _fetch_counts(conn: sqlite3.Connection, *, changed_before: str, focus_before: str) -> dict[str, Any]:
    params = {"changed_before": changed_before, "focus_before": focus_before}
    base = conn.execute(HISTORICAL_BASE_SQL, params).fetchone()[0]
    focus = conn.execute(FOCUS_REQUIREMENT_SQL, params).fetchone()[0]
    excluded = conn.execute(MATURATION_EXCLUSION_SQL, params).fetchone()[0]
    corpus_count = conn.execute(f"SELECT COUNT(*) FROM ({CORPUS_SQL})", params).fetchone()[0]
    return {
        "historical_version_1_before_cutoff": base,
        "focus_requirement_specified_before_focus_cutoff": focus,
        "maturation_excluded_spec_ids": excluded,
        "post_exclusion_corpus_count": corpus_count,
    }


def _fetch_rows(conn: sqlite3.Connection, *, changed_before: str) -> list[AuditRow]:
    rows = conn.execute(CORPUS_SQL, {"changed_before": changed_before}).fetchall()
    return [
        AuditRow(
            spec_id=row["id"],
            historical_version=row["version"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            spec_type=row["type"],
            changed_at=row["changed_at"],
            assertions=row["assertions"],
            testability=row["testability"],
            source_paths=row["source_paths"],
            current_version=row["current_version"],
            current_title=row["current_title"],
            current_description=row["current_description"],
            current_status=row["current_status"],
            current_changed_at=row["current_changed_at"],
        )
        for row in rows
    ]


def _duplicate_map(rows: list[AuditRow]) -> dict[str, list[str]]:
    by_exact_title: dict[str, list[str]] = defaultdict(list)
    token_sets: dict[str, set[str]] = {}
    for row in rows:
        normalized = _normalize_title(row.title)
        if normalized:
            by_exact_title[normalized].append(row.spec_id)
        token_sets[row.spec_id] = _tokens(row.title)

    duplicates: dict[str, set[str]] = defaultdict(set)
    for group in by_exact_title.values():
        if len(group) > 1:
            for spec_id in group:
                duplicates[spec_id].update(other for other in group if other != spec_id)

    indexed = [(row.spec_id, token_sets[row.spec_id]) for row in rows if token_sets[row.spec_id]]
    for index, (left_id, left_tokens) in enumerate(indexed):
        for right_id, right_tokens in indexed[index + 1 :]:
            if _jaccard(left_tokens, right_tokens) >= 0.88:
                duplicates[left_id].add(right_id)
                duplicates[right_id].add(left_id)

    return {spec_id: sorted(matches) for spec_id, matches in sorted(duplicates.items())}


def _flags_for_row(row: AuditRow, duplicates: dict[str, list[str]]) -> dict[str, list[str]]:
    text = f"{row.title}\n{row.description}".lower()
    flags: dict[str, list[str]] = {
        "canonical_terminology_alignment": [],
        "operating_model_alignment": [],
        "implementation_evidence_coherence": [],
        "internal_contradiction_duplicate_detection": [],
        "scope_clarity": [],
        "obsolescence_off_target_detection": [],
    }

    if re.search(r"agent red.+(?:part of|inside|within|owned by).+gt-?kb", text):
        flags["canonical_terminology_alignment"].append("agent_red_gtkb_boundary_confusion")
        flags["operating_model_alignment"].append("application_platform_boundary_confusion")
        flags["obsolescence_off_target_detection"].append("agent_red_boundary_superseded")
    if "claude-playground" in text or "claude playground" in text:
        flags["canonical_terminology_alignment"].append("archive_path_referenced_as_live_surface")
        flags["obsolescence_off_target_detection"].append("archive_surface_reference")
    if "os poller" in text or "smart poller" in text:
        flags["obsolescence_off_target_detection"].append("retired_poller_surface_reference")
    if re.search(r"\b(?:multi[- ]application|multiple active applications|concurrent applications)\b", text):
        flags["operating_model_alignment"].append("concurrent_multi_application_model")

    if row.status in {"implemented", "verified"} and not (row.assertions or row.testability or row.source_paths):
        flags["implementation_evidence_coherence"].append("implemented_or_verified_without_evidence_fields")
    if row.status == "specified" and row.assertions and "test" not in row.assertions.lower():
        flags["implementation_evidence_coherence"].append("assertions_present_but_not_test_mapped")

    if row.spec_id in duplicates:
        flags["internal_contradiction_duplicate_detection"].append(
            "near_duplicate_title:" + ",".join(duplicates[row.spec_id][:5])
        )

    if len(row.description.strip()) < 40:
        flags["scope_clarity"].append("description_too_short")
    if re.search(r"\b(?:tbd|todo|stuff|things|etc\.|as needed|miscellaneous)\b", text):
        flags["scope_clarity"].append("vague_or_placeholder_language")
    domain_hits = sum(
        bool(re.search(pattern, text))
        for pattern in (
            r"\b(?:ui|frontend|screen|button|widget)\b",
            r"\b(?:database|db|schema|table|sql)\b",
            r"\b(?:deploy|release|ci|docker|container)\b",
            r"\b(?:harness|hook|agent|prompt)\b",
        )
    )
    if domain_hits >= 3:
        flags["scope_clarity"].append("multiple_concerns_in_single_requirement")

    return flags


def _state_for_flags(flags: dict[str, list[str]]) -> tuple[str, str]:
    if "vague_or_placeholder_language" in flags["scope_clarity"]:
        return ("requires_owner_clarification", "Clarify owner intent before changing the live specification.")
    if flags["obsolescence_off_target_detection"]:
        return (
            "retirement_candidate",
            "Review for retirement or replacement by current GT-KB operating-model language.",
        )
    if flags["internal_contradiction_duplicate_detection"]:
        return (
            "supersession_candidate",
            "Compare with the flagged related specs and retain the best current authority.",
        )
    if any(flags.values()):
        return (
            "correction_candidate",
            "Revise wording or evidence linkage while preserving the underlying requirement.",
        )
    return ("accept_as_is", "No deterministic quality concern found in this audit pass.")


def _row_result(row: AuditRow, flags: dict[str, list[str]]) -> dict[str, Any]:
    state, recommendation = _state_for_flags(flags)
    active_flags = [flag for values in flags.values() for flag in values]
    rationale = "; ".join(active_flags[:4]) if active_flags else "No deterministic quality concern found."
    return {
        "audit_state": state,
        "current_changed_at": row.current_changed_at,
        "current_status": row.current_status or row.status,
        "current_title": row.current_title,
        "current_version": row.current_version,
        "dimension_flags": flags,
        "historical_changed_at": row.changed_at,
        "historical_status": row.status,
        "historical_text_excerpt": row.description[:240],
        "historical_title": row.title,
        "historical_version": row.historical_version,
        "rationale": rationale,
        "recommended_action": recommendation,
        "spec_id": row.spec_id,
        "type": row.spec_type,
    }


def run_audit(
    db_path: Path = DEFAULT_DB_PATH,
    *,
    changed_before: str = DEFAULT_CHANGED_BEFORE,
    focus_before: str = DEFAULT_FOCUS_REQUIREMENT_BEFORE,
) -> dict[str, Any]:
    with _connect_read_only(db_path) as conn:
        counts = _fetch_counts(conn, changed_before=changed_before, focus_before=focus_before)
        rows = _fetch_rows(conn, changed_before=changed_before)

    duplicates = _duplicate_map(rows)
    manifest = [_row_result(row, _flags_for_row(row, duplicates)) for row in rows]
    state_counts = Counter(row["audit_state"] for row in manifest)
    dimension_counts = Counter(
        dimension for row in manifest for dimension, values in row["dimension_flags"].items() if values
    )
    return {
        "allowed_states": list(ALLOWED_STATES),
        "corpus_selection": {
            "changed_before": changed_before,
            "counts": counts,
            "focus_requirement_before": focus_before,
            "sql": {
                "corpus": CORPUS_SQL,
                "focus_requirement": FOCUS_REQUIREMENT_SQL,
                "historical_base": HISTORICAL_BASE_SQL,
                "maturation_exclusion": MATURATION_EXCLUSION_SQL,
            },
        },
        "manifest": manifest,
        "schema_version": 1,
        "summary": {
            "dimension_flag_counts": dict(sorted(dimension_counts.items())),
            "state_counts": {state: state_counts.get(state, 0) for state in ALLOWED_STATES},
            "total_rows": len(manifest),
        },
    }


def _manifest_flag_summary(row: dict[str, Any]) -> str:
    parts = []
    for dimension, values in row["dimension_flags"].items():
        if values:
            parts.append(f"{dimension}={','.join(values)}")
    return "; ".join(parts) if parts else "none"


def render_markdown_report(result: dict[str, Any], *, title: str = DEFAULT_REPORT_TITLE) -> str:
    lines: list[str] = [
        f"# {title}",
        "",
        "## Claim",
        "",
        "This audit evaluates historical version-1 specification text for early-project quality drift. It is a "
        "read-only audit of specification rows and does not mutate formal specifications. Classifications are "
        "remediation candidates, not approved remediation actions.",
        "",
        "## Methodology",
        "",
        f"- Historical cutoff: `{result['corpus_selection']['changed_before']}`.",
        f"- Focus requirement cutoff: `{result['corpus_selection']['focus_requirement_before']}`.",
        "- Corpus: `specifications.version = 1` rows before the cutoff, excluding spec IDs whose current version "
        "was changed on or after the cutoff.",
        "- Deterministic dimensions: canonical terminology alignment, implementation evidence coherence, and "
        "duplicate detection.",
        "- Structured-analysis dimensions: operating-model alignment, scope clarity, and obsolescence/off-target "
        "detection, bounded to the deterministic corpus and expressed as rule-backed candidate labels.",
        "",
        "## Corpus Counts",
        "",
    ]
    for key, value in result["corpus_selection"]["counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Summary",
        "",
        "### State Counts",
        "",
    ]
    for state, count in result["summary"]["state_counts"].items():
        lines.append(f"- `{state}`: {count}")
    lines += ["", "### Dimension Flag Counts", ""]
    if result["summary"]["dimension_flag_counts"]:
        for dimension, count in result["summary"]["dimension_flag_counts"].items():
            lines.append(f"- `{dimension}`: {count}")
    else:
        lines.append("- none")

    lines += [
        "",
        "## Representative Findings",
        "",
    ]
    for state in ALLOWED_STATES:
        sample = [row for row in result["manifest"] if row["audit_state"] == state][:5]
        if not sample:
            continue
        lines += [f"### {state}", ""]
        for row in sample:
            lines.append(f"- `{row['spec_id']}`: {row['historical_title']} - {row['rationale']}")
        lines.append("")

    lines += [
        "## Classification Manifest",
        "",
        "| spec_id | historical_version | current_version | current_status | audit_state | flags | recommended_action |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for row in result["manifest"]:
        current_version = row["current_version"] if row["current_version"] is not None else ""
        flags = _manifest_flag_summary(row).replace("|", "\\|")
        title = row["recommended_action"].replace("|", "\\|")
        lines.append(
            f"| `{row['spec_id']}` | {row['historical_version']} | {current_version} | "
            f"{row['current_status']} | `{row['audit_state']}` | {flags} | {title} |"
        )

    lines += [
        "",
        "## Downstream Disposition",
        "",
        "The manifest rows are candidates for future bridge-scoped remediation. Promotion to work items, specification "
        "corrections, supersessions, or retirements is out of scope for this audit slice.",
        "",
        "End of report.",
        "",
    ]
    return "\n".join(lines)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--changed-before", default=DEFAULT_CHANGED_BEFORE)
    parser.add_argument("--focus-before", default=DEFAULT_FOCUS_REQUIREMENT_BEFORE)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-report", type=Path)
    parser.add_argument("--report-title", default=DEFAULT_REPORT_TITLE)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    result = run_audit(args.db, changed_before=args.changed_before, focus_before=args.focus_before)
    json_text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out_json:
        _write_text(args.out_json, json_text)
    if args.out_report:
        _write_text(args.out_report, render_markdown_report(result, title=args.report_title))
    if not args.out_json and not args.out_report:
        print(json_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
