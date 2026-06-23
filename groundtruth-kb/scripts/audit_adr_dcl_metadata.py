"""Audit ADR/DCL specification metadata population in groundtruth.db.

Read-only audit of the `specifications` table for ADR (architecture_decision)
and DCL (design_constraint) records. Produces a structured report on
population state of `tags`, `source_paths`, and `assertions` fields, identifies
records needing backfill (the principal target identified in the parent
scoping bridge gtkb-adr-evaluation-enforcement-2026-04-30), and recommends a
`concern_tags` normalization decision based on observed tag distribution.

Per `bridge/gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30-006.md` (GO).

Usage:
    python audit_adr_dcl_metadata.py [--db PATH] [--format {json,markdown}]
                                      [--output PATH] [--frozen-timestamp ISO]

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

# Theme-tag heuristic: tags appearing in >=3 records OR matching explicit
# governance/architecture theme markers are "theme" tags. Everything else is
# "topic" tags.
EXPLICIT_THEME_MARKERS: frozenset[str] = frozenset(
    {
        "design-constraint",
        "mechanical-enforcement",
        "governance",
        "architecture",
        "audit-trail",
        "platform",
        "platform-purity",
    }
)
THEME_THRESHOLD = 3  # tag appearing in >= N records is theme-classified


def _resolve_default_db_path() -> Path:
    """Return the canonical groundtruth.db location for GT-KB."""
    return Path(r"E:\GT-KB\groundtruth.db")


def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    """Open groundtruth.db in read-only mode using URI parameter."""
    if not db_path.is_file():
        raise FileNotFoundError(f"groundtruth.db not found at {db_path}")
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _is_populated(value: str | None) -> bool:
    """Return True iff value is a non-empty JSON list with at least 1 element."""
    if value is None:
        return False
    stripped = value.strip()
    if stripped in ("", "[]", "null", "None"):
        return False
    try:
        parsed = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return False
    return isinstance(parsed, list) and len(parsed) > 0


def _categorize_tag(tag: str, count: int) -> str:
    """Classify a tag as 'theme' or 'topic' per the documented heuristic."""
    if tag in EXPLICIT_THEME_MARKERS:
        return "theme"
    if count >= THEME_THRESHOLD:
        return "theme"
    return "topic"


def _query_records(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Fetch latest version per id for ADR/DCL specifications."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, type, MAX(version) AS v, tags, source_paths, assertions
        FROM specifications
        WHERE type IN ('architecture_decision', 'design_constraint')
        GROUP BY id
        ORDER BY id
        """
    )
    return [
        {
            "id": row[0],
            "type": row[1],
            "version": row[2],
            "tags": row[3],
            "source_paths": row[4],
            "assertions": row[5],
        }
        for row in cur.fetchall()
    ]


def _compute_totals(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Aggregate per-type population counts."""
    totals: dict[str, dict[str, int]] = {}
    for record in records:
        type_key = record["type"]
        bucket = totals.setdefault(
            type_key,
            {"total": 0, "with_tags": 0, "with_source_paths": 0, "with_assertions": 0},
        )
        bucket["total"] += 1
        if _is_populated(record["tags"]):
            bucket["with_tags"] += 1
        if _is_populated(record["source_paths"]):
            bucket["with_source_paths"] += 1
        if _is_populated(record["assertions"]):
            bucket["with_assertions"] += 1
    return totals


def _missing_source_paths(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Return records lacking source_paths, sorted by id."""
    return sorted(
        [
            {"id": record["id"], "type": record["type"]}
            for record in records
            if not _is_populated(record["source_paths"])
        ],
        key=lambda x: x["id"],
    )


def _tags_histogram(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build tag-frequency histogram with theme/topic categorization."""
    counter: Counter[str] = Counter()
    for record in records:
        if not _is_populated(record["tags"]):
            continue
        try:
            tags = json.loads(record["tags"])
        except (json.JSONDecodeError, ValueError):
            continue
        for tag in tags:
            if isinstance(tag, str):
                counter[tag] += 1

    histogram = [
        {
            "tag": tag,
            "count": count,
            "category": _categorize_tag(tag, count),
        }
        for tag, count in counter.items()
    ]
    # Deterministic sort: category ascending, count descending, tag ascending.
    histogram.sort(key=lambda x: (x["category"], -x["count"], x["tag"]))
    return histogram


def _normalization_recommendation(histogram: list[dict[str, Any]]) -> dict[str, Any]:
    """Recommend concern_tags normalization decision based on tag distribution."""
    theme_count = sum(1 for h in histogram if h["category"] == "theme")
    topic_count = sum(1 for h in histogram if h["category"] == "topic")
    ambiguous = sum(1 for h in histogram if h["category"] == "topic" and h["count"] >= THEME_THRESHOLD - 1)
    if theme_count >= 5 and topic_count >= 10:
        decision = "normalize_to_taxonomy"
        rationale = (
            f"{theme_count} theme tags and {topic_count} topic tags observed; "
            "the topic-tag spread is broad enough that a closed concern_tags "
            "taxonomy would meaningfully reduce ambiguity for the validator."
        )
    else:
        decision = "use_existing_tags"
        rationale = (
            f"{theme_count} theme tags and {topic_count} topic tags observed; "
            "tag distribution is narrow enough that existing tags can serve "
            "as concern_tags directly with low ambiguity cost."
        )
    return {
        "decision": decision,
        "rationale": rationale,
        "evidence": {
            "theme_tag_count": theme_count,
            "topic_tag_count": topic_count,
            "ambiguous_count": ambiguous,
        },
    }


def build_report(
    records: list[dict[str, Any]],
    db_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Construct the full structured audit report."""
    totals = _compute_totals(records)
    missing = _missing_source_paths(records)
    histogram = _tags_histogram(records)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "db_path": str(db_path),
        "totals": totals,
        "missing_source_paths": missing,
        "tags_histogram": histogram,
        "concern_tags_normalization_recommendation": _normalization_recommendation(histogram),
        "records_needing_backfill_count": len(missing),
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render the report as human-readable markdown."""
    lines: list[str] = [
        "# ADR/DCL Metadata Audit Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Database: `{report['db_path']}`",
        f"Schema version: {report['schema_version']}",
        "",
        "## Totals",
        "",
        "| Type | Total | with tags | with source_paths | with assertions |",
        "|---|---|---|---|---|",
    ]
    for type_key, bucket in sorted(report["totals"].items()):
        lines.append(
            f"| {type_key} | {bucket['total']} | {bucket['with_tags']} | "
            f"{bucket['with_source_paths']} | {bucket['with_assertions']} |"
        )
    lines += [
        "",
        f"## Records needing backfill: {report['records_needing_backfill_count']}",
        "",
        "(Records lacking `source_paths`, sorted by id.)",
        "",
    ]
    for entry in report["missing_source_paths"]:
        lines.append(f"- `{entry['id']}` ({entry['type']})")
    lines += [
        "",
        "## Tags histogram",
        "",
        "| Tag | Count | Category |",
        "|---|---|---|",
    ]
    for entry in report["tags_histogram"]:
        lines.append(f"| `{entry['tag']}` | {entry['count']} | {entry['category']} |")
    rec = report["concern_tags_normalization_recommendation"]
    lines += [
        "",
        "## concern_tags normalization recommendation",
        "",
        f"**Decision:** `{rec['decision']}`",
        "",
        f"**Rationale:** {rec['rationale']}",
        "",
        "**Evidence:**",
        f"- Theme tag count: {rec['evidence']['theme_tag_count']}",
        f"- Topic tag count: {rec['evidence']['topic_tag_count']}",
        f"- Ambiguous (topic but high-frequency) count: {rec['evidence']['ambiguous_count']}",
        "",
    ]
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    """Render the report as deterministic JSON."""
    return json.dumps(report, indent=2, sort_keys=True)


def _validate_iso_timestamp(value: str) -> str:
    """Ensure --frozen-timestamp is a valid ISO 8601 string."""
    try:
        # Accept Z suffix (Python 3.11+ handles fromisoformat) or explicit offset.
        normalized = value.replace("Z", "+00:00")
        dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"--frozen-timestamp {value!r} is not a valid ISO 8601 timestamp") from exc
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=_resolve_default_db_path(),
        help=f"Path to groundtruth.db. Default: {_resolve_default_db_path()}",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format. Default: json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to file instead of stdout. Default: stdout.",
    )
    parser.add_argument(
        "--frozen-timestamp",
        type=_validate_iso_timestamp,
        default=None,
        help=(
            "Freeze the report's generated_at timestamp for deterministic "
            "test snapshots. Format: ISO 8601. Default: current UTC time."
        ),
    )

    args = parser.parse_args(argv)

    generated_at = args.frozen_timestamp if args.frozen_timestamp is not None else dt.datetime.now(dt.UTC).isoformat()

    db_path = Path(args.db).resolve()

    try:
        with _connect_read_only(db_path) as conn:
            records = _query_records(conn)
    except FileNotFoundError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 2

    report = build_report(records, db_path, generated_at)

    rendered = render_json(report) if args.format == "json" else render_markdown(report)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    sys.exit(main())
