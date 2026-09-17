"""Report current ADR/DCL metadata through the configured native authority.

Usage: python audit_adr_dcl_metadata.py [--config PATH] [--format json|markdown]
                                      [--output PATH] [--frozen-timestamp ISO]

Only native GET requests are used. Counts describe declaration population and
tag usage; they do not establish architecture conformance or select a taxonomy.
Pagination observes current records across requests, not one atomic snapshot.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig

SCHEMA_VERSION = 2
ARCHITECTURE_TYPES = frozenset({"architecture_decision", "design_constraint"})


def _query_records(client: AuthorityClient) -> list[dict[str, Any]]:
    """Read every bounded native page without accepting duplicate identities."""
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursors: set[str] = set()
    after = None
    while True:
        page = client.request("GET", "/v1/specifications", query={"limit": 1000, "after": after})
        if not isinstance(page, dict) or not isinstance(page.get("records"), list) or "next_after" not in page:
            raise ValueError("The authority returned an invalid specification page")
        for record in page["records"]:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
                raise ValueError("The authority returned a record without a valid identity")
            if record["id"] in seen:
                raise ValueError("The authority repeated a specification identity; read current state again")
            seen.add(record["id"])
            if record.get("type") in ARCHITECTURE_TYPES:
                records.append(record)
        after = page["next_after"]
        if after is None:
            return sorted(records, key=lambda record: record["id"])
        if not isinstance(after, str) or not after or after in cursors or not page["records"]:
            raise ValueError("The authority returned a non-progressing specification cursor")
        cursors.add(after)


def _is_populated(value: Any) -> bool:
    """A nonempty native array is populated; this does not assess its adequacy."""
    return isinstance(value, list) and bool(value)


def _compute_totals(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {}
    for record in records:
        bucket = totals.setdefault(
            record["type"], {"total": 0, "with_tags": 0, "with_source_paths": 0, "with_assertions": 0}
        )
        bucket["total"] += 1
        for field in ("tags", "source_paths", "assertions"):
            bucket["with_" + field] += int(_is_populated(record.get(field)))
    return totals


def _missing_source_paths(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    return sorted(
        [{"id": r["id"], "type": r["type"]} for r in records if not _is_populated(r.get("source_paths"))],
        key=lambda record: record["id"],
    )


def _tags_histogram(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for record in records:
        tags = record.get("tags")
        if isinstance(tags, list):
            counts.update({tag for tag in tags if isinstance(tag, str) and tag.strip()})
    return [{"tag": tag, "count": count} for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def build_report(records: list[dict[str, Any]], authority_url: str, generated_at: str) -> dict[str, Any]:
    """Report observations without introducing another decision or audit state."""
    missing = _missing_source_paths(records)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "authority_url": authority_url,
        "totals": _compute_totals(records),
        "status_counts": dict(sorted(Counter(r.get("status") or "unspecified" for r in records).items())),
        "missing_source_paths": missing,
        "records_needing_backfill_count": len(missing),
        "tags_histogram": _tags_histogram(records),
        "evidence_limit": (
            "Current ADR/DCL declarations observed across native pages. Includes inactive current rows, "
            "identified in status_counts. Population and tag frequency do not establish content adequacy, "
            "implementation, conformance, independent verification or a taxonomy decision."
        ),
    }


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ADR/DCL Metadata Audit Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Authority: `{report['authority_url']}`",
        f"Schema version: {report['schema_version']}",
        "",
        report["evidence_limit"],
        "",
        "## Totals",
        "",
        "| Type | Total | with tags | with source_paths | with assertions |",
        "|---|---|---|---|---|",
    ]
    for kind, bucket in sorted(report["totals"].items()):
        lines.append(
            f"| {kind} | {bucket['total']} | {bucket['with_tags']} | "
            f"{bucket['with_source_paths']} | {bucket['with_assertions']} |"
        )
    lines.extend(
        [
            "",
            "Current row statuses: "
            + ", ".join(f"{status}: {count}" for status, count in report["status_counts"].items()),
            "",
            f"## Records needing backfill: {report['records_needing_backfill_count']}",
            "",
            "Records lacking source_paths; inspect the requirement before choosing a correction.",
            "",
        ]
    )
    lines.extend(f"- `{r['id']}` ({r['type']})" for r in report["missing_source_paths"])
    lines.extend(
        [
            "",
            "## Tags histogram",
            "",
            "Count is the number of observed records containing the tag.",
            "",
            "| Tag | Count |",
            "|---|---|",
        ]
    )
    lines.extend(f"| `{r['tag'].replace('|', '&#124;')}` | {r['count']} |" for r in report["tags_histogram"])
    return "\n".join(lines)


def _validate_iso_timestamp(value: str) -> str:
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"Invalid ISO 8601 timestamp: {value!r}") from error
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Select the normal GroundTruth configuration with authority_url.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--frozen-timestamp", type=_validate_iso_timestamp)
    args = parser.parse_args(argv)
    try:
        config = GTConfig.load(config_path=args.config)
        if not config.authority_url:
            raise ValueError("No authority_url is configured; select a native configuration with --config")
        client = AuthorityClient(config.authority_url)
        records = _query_records(client)
    except (AuthorityClientError, OSError, ValueError) as error:
        sys.stderr.write(f"Error: {error}\n")
        return 2
    timestamp = args.frozen_timestamp or dt.datetime.now(dt.UTC).isoformat()
    report = build_report(records, client.url, timestamp)
    rendered = render_json(report) if args.format == "json" else render_markdown(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
