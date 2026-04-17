#!/usr/bin/env python3
"""Phase A metrics collector for scanner-safe-writer deny records.

Consumes ``.claude/hooks/scanner-safe-writer.log`` (JSONL, schema v1) and
emits aggregated metrics to stdout in JSON (default, stable automation
contract) or Markdown (human presentation) format.

Schema v1 stable-interface contract
-----------------------------------
Within ``schema_version: 1``, the stable fields collectors may index on are:

- ``schema_version`` (int, always ``1``)
- ``timestamp_utc`` (ISO-8601 UTC ``Z``)
- ``hook`` (string, always ``"scanner-safe-writer"``)
- ``event`` (string, always ``"deny"``)
- ``file_path`` (string)
- ``catalog_source`` (string, ``"canonical"`` or ``"fallback"``)
- ``hits[].pattern_name`` (string - canonical PatternSpec name)
- ``hits[].span[0]``, ``hits[].span[1]`` (int offsets)
- ``session_id`` (string or ``null``)

``hits[].pattern_description`` is explicitly human-readable context only and
MUST NOT be used as a grouping key or appear in stable output. See
``templates/hooks/scanner-safe-writer.py:60-70``.

Forward-compat behavior
-----------------------
Records whose ``schema_version != 1`` are counted under
``forward_compat.unknown_schema_versions`` and skipped. A concise warning is
emitted to stderr (once per distinct unknown version observed) so operators
see the drift without muting JSON stdout.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, TextIO

SCHEMA_VERSION_SUPPORTED = 1
DEFAULT_LOG_PATH = Path(".claude/hooks/scanner-safe-writer.log")

_UNKNOWN_SESSION = "(unknown)"


def _parse_line(
    line: str,
) -> tuple[str, dict[str, Any] | None, Any]:
    """Classify one JSONL line.

    Returns ``(classification, record_or_none, raw_version)``. Classification
    is one of ``"deny"``, ``"wrong_event"``, ``"wrong_hook"``,
    ``"unknown_version"``, or ``"malformed"``. ``raw_version`` is the
    observed ``schema_version`` value (possibly ``None``/non-int) when the
    classification is ``"unknown_version"``; otherwise ``None``.
    """
    stripped = line.strip()
    if not stripped:
        return ("malformed", None, None)
    try:
        rec = json.loads(stripped)
    except json.JSONDecodeError:
        return ("malformed", None, None)
    if not isinstance(rec, dict):
        return ("malformed", None, None)
    version = rec.get("schema_version")
    if version != SCHEMA_VERSION_SUPPORTED:
        return ("unknown_version", None, version)
    if rec.get("hook") != "scanner-safe-writer":
        return ("wrong_hook", None, None)
    if rec.get("event") != "deny":
        return ("wrong_event", None, None)
    return ("deny", rec, None)


def _now_utc_iso() -> str:
    return datetime.datetime.now(tz=datetime.UTC).isoformat().replace("+00:00", "Z")


def _empty_report(log_path: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION_SUPPORTED,
        "log_path": str(log_path),
        "collected_at_utc": _now_utc_iso(),
        "total_deny_events": 0,
        "by_pattern_name": {},
        "by_catalog_source": {},
        "by_session_id": {},
        "unique_file_paths": [],
        "by_date": {},
        "forward_compat": {
            "unknown_schema_versions": 0,
            "malformed_lines": 0,
            "lines_skipped_wrong_event": 0,
            "lines_skipped_wrong_hook": 0,
        },
    }


def collect_metrics(
    log_path: Path,
    *,
    warn_stream: TextIO | None = None,
) -> dict[str, Any]:
    """Aggregate deny metrics from ``log_path``.

    ``warn_stream`` receives one stderr line per distinct unknown
    ``schema_version`` value observed. Pass ``None`` to suppress warnings
    (tests rely on this).

    Per-pattern counts increment once per hit, not once per record. A deny
    record can contain multiple hits (one per catalog pattern matched); each
    hit increments ``by_pattern_name[hit.pattern_name]`` by 1.
    ``total_deny_events`` counts records, not hits.
    """
    pattern_counts: Counter[str] = Counter()
    catalog_counts: Counter[str] = Counter()
    session_counts: Counter[str] = Counter()
    date_counts: Counter[str] = Counter()
    unique_files: set[str] = set()
    fc_unknown = 0
    fc_malformed = 0
    fc_wrong_event = 0
    fc_wrong_hook = 0
    total_deny = 0
    warned_versions: set[str] = set()

    if not log_path.exists():
        return _empty_report(log_path)

    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            classification, rec, raw_version = _parse_line(line)
            if classification == "malformed":
                fc_malformed += 1
                continue
            if classification == "unknown_version":
                fc_unknown += 1
                if warn_stream is not None:
                    version_key = repr(raw_version)
                    if version_key not in warned_versions:
                        warned_versions.add(version_key)
                        print(
                            f"warning: skipping record(s) with unsupported "
                            f"schema_version={version_key} "
                            f"(collector supports schema_version={SCHEMA_VERSION_SUPPORTED})",
                            file=warn_stream,
                        )
                continue
            if classification == "wrong_hook":
                fc_wrong_hook += 1
                continue
            if classification == "wrong_event":
                fc_wrong_event += 1
                continue

            assert rec is not None  # noqa: S101 - narrowing guard after classifier
            total_deny += 1

            cs = rec.get("catalog_source")
            if isinstance(cs, str):
                catalog_counts[cs] += 1

            sid = rec.get("session_id")
            session_counts[sid if isinstance(sid, str) else _UNKNOWN_SESSION] += 1

            fp = rec.get("file_path")
            if isinstance(fp, str) and fp:
                unique_files.add(fp)

            ts = rec.get("timestamp_utc")
            if isinstance(ts, str) and ts:
                try:
                    dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    date_counts[dt.strftime("%Y-%m-%d")] += 1
                except ValueError:
                    pass

            # pattern_name ONLY - never pattern_description (G5 stability contract)
            hits = rec.get("hits")
            if isinstance(hits, list):
                for hit in hits:
                    if isinstance(hit, dict):
                        pname = hit.get("pattern_name")
                        if isinstance(pname, str):
                            pattern_counts[pname] += 1

    return {
        "schema_version": SCHEMA_VERSION_SUPPORTED,
        "log_path": str(log_path),
        "collected_at_utc": _now_utc_iso(),
        "total_deny_events": total_deny,
        "by_pattern_name": dict(sorted(pattern_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "by_catalog_source": dict(sorted(catalog_counts.items())),
        "by_session_id": dict(sorted(session_counts.items())),
        "unique_file_paths": sorted(unique_files),
        "by_date": dict(sorted(date_counts.items())),
        "forward_compat": {
            "unknown_schema_versions": fc_unknown,
            "malformed_lines": fc_malformed,
            "lines_skipped_wrong_event": fc_wrong_event,
            "lines_skipped_wrong_hook": fc_wrong_hook,
        },
    }


def _render_kv_table(
    header_key: str,
    header_val: str,
    rows: dict[str, int],
) -> list[str]:
    lines: list[str] = []
    lines.append(f"| {header_key} | {header_val} |")
    lines.append("|---|---|")
    for key, value in rows.items():
        lines.append(f"| {key} | {value} |")
    return lines


def format_markdown(report: dict[str, Any]) -> str:
    """Render a deterministic Markdown summary of the metrics report.

    Keyed on stable fields only. ``pattern_description`` is never emitted.
    """
    lines: list[str] = []
    lines.append("# Phase A Scanner-Safe-Writer Metrics")
    lines.append("")
    lines.append(f"**Log:** {report['log_path']}")
    lines.append(f"**Collected:** {report['collected_at_utc']}")
    lines.append(f"**Total deny events (schema v{report['schema_version']}):** {report['total_deny_events']}")
    lines.append("")

    lines.append("## By pattern name")
    lines.append("")
    by_pattern: dict[str, int] = report["by_pattern_name"]
    if by_pattern:
        lines.extend(_render_kv_table("pattern_name", "count", by_pattern))
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("## By catalog source")
    lines.append("")
    by_catalog: dict[str, int] = report["by_catalog_source"]
    if by_catalog:
        lines.extend(_render_kv_table("catalog_source", "count", by_catalog))
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("## By session")
    lines.append("")
    by_session: dict[str, int] = report["by_session_id"]
    if by_session:
        lines.extend(_render_kv_table("session_id", "count", by_session))
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("## By date (UTC)")
    lines.append("")
    by_date: dict[str, int] = report["by_date"]
    if by_date:
        lines.extend(_render_kv_table("date", "count", by_date))
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("## Unique bridge files attracting denies")
    lines.append("")
    unique_files: list[str] = report["unique_file_paths"]
    if unique_files:
        for path in unique_files:
            lines.append(f"- {path}")
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("## Forward-compat indicators")
    lines.append("")
    fc: dict[str, int] = report["forward_compat"]
    for key in (
        "unknown_schema_versions",
        "malformed_lines",
        "lines_skipped_wrong_event",
        "lines_skipped_wrong_hook",
    ):
        lines.append(f"- {key}: {fc[key]}")
    lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Collect Phase A metrics from a scanner-safe-writer JSONL deny log. "
            "Indexes only on schema-v1 stable fields (pattern_name, not "
            "pattern_description)."
        ),
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help=f"Path to deny log (default: {DEFAULT_LOG_PATH})",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json, the stable automation contract)",
    )
    args = parser.parse_args(argv)

    report = collect_metrics(args.log_path, warn_stream=sys.stderr)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
