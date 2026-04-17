# GT-KB Phase A Metrics Collector (Tier A #6)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Scope-tracking VERIFIED:** `bridge/gtkb-operational-skills-tier-a-008.md`
**Target repo:** `groundtruth-kb` at main (`0a60054` — Tier A #3 VERIFIED)
**Blocking predecessor:** Tier A #2 `gtkb-hook-scanner-safe-writer` VERIFIED
  (`b5e5c6c` + `37a88cc`). Schema v1 stable and committed.

## Summary

Add the final Phase A deliverable: `scripts/collect_phase_a_metrics.py`.
Consumes the JSONL log produced by the scanner-safe-writer hook
(Tier A #2) and emits Phase A success metrics. Governed by schema v1
stable-interface contract — indexes on stable fields only
(`pattern_name`, `catalog_source`, `session_id`, `file_path`,
`timestamp_utc`). **Never indexes on `pattern_description`** (per
schema v1 explicit non-contractual declaration at
`templates/hooks/scanner-safe-writer.py:60-70`).

Deliverables:

1. Collector script (~250 lines).
2. Fixtures under `tests/fixtures/phase_a_metrics/` covering
   canonical-only logs, fallback-only logs, mixed-catalog logs,
   malformed lines, and forward-compat schema drift cases.
3. Test module `tests/test_phase_a_metrics_collector.py` with ~10
   tests.
4. No changes to the hook log schema, no edits to
   `scanner-safe-writer.py`, no new KB APIs.

## Prior Deliberations

No prior DELIB-* deliberations matching this collector's topic.
`search_deliberations(query="phase a metrics collector scanner deny")`
returns nothing.

Relevant prior bridge threads:

- `bridge/gtkb-operational-skills-tier-a-004.md` (parent scope GO —
  G5 review gate: "scanner-deny record schema must be a stable
  interface agreed between hook and collector")
- `bridge/gtkb-hook-scanner-safe-writer-012.md` (Tier A #2 VERIFIED —
  source of the JSONL schema v1 contract)
- `bridge/gtkb-hook-scanner-safe-writer-010.md` (NO-GO that forced
  the `pattern_description` non-contractual declaration in schema v1)

## Scope

### In scope

1. Script at `scripts/collect_phase_a_metrics.py`. Executable as
   `python scripts/collect_phase_a_metrics.py [options]`.
2. Consumes `.claude/hooks/scanner-safe-writer.log` by default.
   `--log-path <path>` override for testing and alternative deployments.
3. Emits metrics in two formats:
   - `--format json` (default): structured JSON on stdout for automation
   - `--format markdown`: human-readable summary on stdout
4. Handles JSONL line-by-line, resilient to malformed lines.
5. Schema v1 fence: processes only records with `schema_version == 1`.
   Forward-compat behavior for other versions is
   **warn-and-skip** (explicitly stated, not silent).
6. Fixtures under `tests/fixtures/phase_a_metrics/` for deterministic
   test coverage.
7. Test module `tests/test_phase_a_metrics_collector.py` with ~10
   tests isolating each metric and edge case.

### Out of scope (deferred)

1. No database write. The collector is read-only. Metrics go to stdout.
2. No CI integration or dashboard. Downstream work.
3. No multi-file log aggregation (single log file per invocation).
4. No Prometheus/OTEL exporter. JSON output is the contract.
5. No live-tail / watch mode. Single-shot collection.
6. No schema_version migration logic. Future schema v2 would be
   handled by a future bridge.

## Schema v1 Stable Interface Contract (G5)

From `templates/hooks/scanner-safe-writer.py:46-70`:

**Stable fields** (collectors may index on):
- `schema_version` (int, always `1` in v1)
- `timestamp_utc` (ISO-8601 UTC Z)
- `hook` (string, always `"scanner-safe-writer"`)
- `event` (string, always `"deny"`)
- `file_path` (string)
- `catalog_source` (string, `"canonical"` or `"fallback"`)
- `hits[].pattern_name` (string — the canonical PatternSpec name)
- `hits[].span[0]`, `hits[].span[1]` (int offsets)
- `session_id` (string or `null`)

**Explicitly NOT stable** (must not be indexed on):
- `hits[].pattern_description` — human-readable context only; may
  differ between canonical and fallback catalogs.

The collector indexes on `pattern_name` everywhere. It includes
`pattern_description` in JSON output as pass-through data but never
uses it as a grouping key.

## Design

### Metric set (schema v1)

The collector computes the following metrics from a schema-v1 log:

1. **Total deny events** — count of records with `event == "deny"`.
2. **Per-pattern deny counts** — dict keyed on `pattern_name`,
   values are record counts. Order by descending count.
3. **Per-catalog-source deny counts** — dict keyed on
   `catalog_source`, values are record counts. Two values typical:
   `canonical` and `fallback`.
4. **Per-session deny counts** — dict keyed on `session_id` (with
   `null` folded to literal string `"(unknown)"` for display),
   values are record counts.
5. **Unique file_paths denied** — list of distinct `file_path`
   values. Useful for spotting repeated attempts on the same bridge.
6. **Time distribution** — dict keyed on `date` (UTC, YYYY-MM-DD
   from `timestamp_utc`), values are record counts.
7. **Forward-compat indicators:**
   - `unknown_schema_versions` — count of records with
     `schema_version != 1` (warned about, not processed)
   - `malformed_lines` — count of lines that failed JSON parse
   - `lines_skipped_wrong_event` — count of records with
     `event != "deny"`
   - `lines_skipped_wrong_hook` — count of records with
     `hook != "scanner-safe-writer"`

### Output format — JSON (default)

```
{
  "schema_version": 1,
  "log_path": "<resolved path>",
  "collected_at_utc": "2026-04-17T12:34:56Z",
  "total_deny_events": <int>,
  "by_pattern_name": {"ar_live_key": 7, "anthropic_api_key": 3, ...},
  "by_catalog_source": {"canonical": 9, "fallback": 1},
  "by_session_id": {"S298": 6, "S299": 4},
  "unique_file_paths": ["bridge/foo-001.md", "bridge/bar-001.md"],
  "by_date": {"2026-04-16": 3, "2026-04-17": 7},
  "forward_compat": {
    "unknown_schema_versions": 0,
    "malformed_lines": 0,
    "lines_skipped_wrong_event": 0,
    "lines_skipped_wrong_hook": 0
  }
}
```

### Output format — Markdown

```markdown
# Phase A Scanner-Safe-Writer Metrics

**Log:** .claude/hooks/scanner-safe-writer.log
**Collected:** 2026-04-17T12:34:56Z
**Total deny events (schema v1):** 10

## By pattern name

| pattern_name | count |
|---|---|
| ar_live_key | 7 |
| anthropic_api_key | 3 |

## By catalog source

| catalog_source | count |
|---|---|
| canonical | 9 |
| fallback | 1 |

## By session

| session_id | count |
|---|---|
| S298 | 6 |
| S299 | 4 |

## By date (UTC)

| date | count |
|---|---|
| 2026-04-16 | 3 |
| 2026-04-17 | 7 |

## Unique bridge files attracting denies

- bridge/foo-001.md
- bridge/bar-001.md

## Forward-compat indicators

- unknown_schema_versions: 0
- malformed_lines: 0
- lines_skipped_wrong_event: 0
- lines_skipped_wrong_hook: 0
```

### Implementation sketch

```python
# scripts/collect_phase_a_metrics.py
"""Phase A metrics collector for scanner-safe-writer deny records.

Reads .claude/hooks/scanner-safe-writer.log (JSONL schema v1) and
emits aggregated metrics. Schema v1 stable-interface contract:
indexes only on pattern_name, not on pattern_description.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION_SUPPORTED = 1
DEFAULT_LOG_PATH = Path(".claude/hooks/scanner-safe-writer.log")


def _parse_line(line: str) -> tuple[str, dict[str, Any] | None]:
    """Return (classification, record_or_none). Classification is one of
    'deny', 'wrong_event', 'wrong_hook', 'unknown_version', 'malformed'.
    """
    stripped = line.strip()
    if not stripped:
        return ("malformed", None)
    try:
        rec = json.loads(stripped)
    except json.JSONDecodeError:
        return ("malformed", None)
    if not isinstance(rec, dict):
        return ("malformed", None)
    version = rec.get("schema_version")
    if version != SCHEMA_VERSION_SUPPORTED:
        return ("unknown_version", None)
    if rec.get("hook") != "scanner-safe-writer":
        return ("wrong_hook", None)
    if rec.get("event") != "deny":
        return ("wrong_event", None)
    return ("deny", rec)


def collect_metrics(log_path: Path) -> dict[str, Any]:
    """Aggregate deny metrics from log_path. Returns JSON-shape dict."""
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

    if not log_path.exists():
        return _empty_report(log_path)

    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            classification, rec = _parse_line(line)
            if classification == "malformed":
                fc_malformed += 1
                continue
            if classification == "unknown_version":
                fc_unknown += 1
                continue
            if classification == "wrong_hook":
                fc_wrong_hook += 1
                continue
            if classification == "wrong_event":
                fc_wrong_event += 1
                continue

            assert rec is not None
            total_deny += 1

            # catalog_source (stable)
            cs = rec.get("catalog_source", "(unknown)")
            if isinstance(cs, str):
                catalog_counts[cs] += 1

            # session_id (stable; null → "(unknown)")
            sid = rec.get("session_id")
            session_counts[sid if isinstance(sid, str) else "(unknown)"] += 1

            # file_path (stable)
            fp = rec.get("file_path", "")
            if isinstance(fp, str) and fp:
                unique_files.add(fp)

            # date from timestamp_utc (stable)
            ts = rec.get("timestamp_utc", "")
            if isinstance(ts, str) and ts:
                try:
                    dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    date_counts[dt.strftime("%Y-%m-%d")] += 1
                except ValueError:
                    pass  # drop bad timestamps; already counted in total

            # hits[].pattern_name only — NEVER pattern_description
            hits = rec.get("hits", [])
            if isinstance(hits, list):
                for hit in hits:
                    if isinstance(hit, dict):
                        pname = hit.get("pattern_name")
                        if isinstance(pname, str):
                            pattern_counts[pname] += 1

    return {
        "schema_version": SCHEMA_VERSION_SUPPORTED,
        "log_path": str(log_path),
        "collected_at_utc": datetime.datetime.now(tz=datetime.UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "total_deny_events": total_deny,
        "by_pattern_name": dict(
            sorted(pattern_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
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


def _empty_report(log_path: Path) -> dict[str, Any]:
    """Return an empty report when the log file doesn't exist."""
    return {
        "schema_version": SCHEMA_VERSION_SUPPORTED,
        "log_path": str(log_path),
        "collected_at_utc": datetime.datetime.now(tz=datetime.UTC)
        .isoformat()
        .replace("+00:00", "Z"),
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


def format_markdown(report: dict[str, Any]) -> str:
    """Render the metrics report as human-readable Markdown."""
    # ... table-rendering details elided for brevity ...


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Collect Phase A metrics from scanner-safe-writer log"
    )
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH)
    parser.add_argument(
        "--format", choices=("json", "markdown"), default="json"
    )
    args = parser.parse_args(argv)

    report = collect_metrics(args.log_path)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Approximate size: ~250 lines total. Straight-line code, no
dependencies beyond stdlib.

### Fixtures (`tests/fixtures/phase_a_metrics/`)

Files (all short, <30 lines each):

1. `canonical_only.log` — 3 deny records all with
   `catalog_source="canonical"`, varied pattern names.
2. `fallback_only.log` — 2 deny records all with
   `catalog_source="fallback"`, different session IDs.
3. `mixed_catalogs.log` — 5 records spanning canonical and fallback.
4. `malformed_lines.log` — 4 records: 2 valid deny records, 1
   invalid JSON, 1 empty line.
5. `unknown_schema_version.log` — 3 records: 1 valid schema=1 deny,
   1 schema=2 pretending to be future version, 1 schema missing.
6. `wrong_event.log` — 1 valid deny record + 1 record with
   `event="pass"` (shouldn't be in the log but defensive).
7. `empty.log` — zero-byte file.

Each fixture record is a JSONL line authored in prose (no
credential values). Example (conceptual — described in prose, not
literal keys in this proposal):

- `catalog_source="canonical"`, `pattern_name` value is the
  canonical-pattern name string (e.g., `"ar_live_key"` — the
  tenant-scoped key name, which is a short identifier without a
  credential value), `hits[].span` is two integers, `session_id`
  is an `"S298"`-style string or `null`, `timestamp_utc` is an
  ISO-8601 string.

The fixtures contain **no literal credential values** — they
contain `pattern_name` strings (like `"api_key"` and
`"anthropic_api_key"` — the canonical names, which are the data
the collector indexes on), **span integers** (e.g., `[0, 24]`),
and `file_path` strings pointing at fictional `bridge/*.md` paths.
This ensures the fixtures themselves never trigger the hook when
written.

### Tests (`tests/test_phase_a_metrics_collector.py`)

Approximately 10 tests:

1. `test_empty_log_returns_zero_metrics` — nonexistent log path;
   all counters are 0.
2. `test_canonical_only_fixture` — loads `canonical_only.log`;
   asserts `by_catalog_source == {"canonical": 3}`, pattern counts
   match fixture.
3. `test_fallback_only_fixture` — similar, fallback.
4. `test_mixed_catalogs_fixture` — asserts both catalog counts
   > 0, summed equals `total_deny_events`.
5. `test_malformed_lines_counted_in_forward_compat` — asserts
   `forward_compat.malformed_lines == 2`, total deny == 2.
6. `test_unknown_schema_version_skipped_and_counted` — asserts
   `forward_compat.unknown_schema_versions >= 1`, only schema=1
   records contribute to totals.
7. `test_wrong_event_counted_in_forward_compat` — asserts
   `forward_compat.lines_skipped_wrong_event == 1`.
8. `test_pattern_names_indexed_not_descriptions` — authored
   fixture: same `pattern_name` but different
   `pattern_description`; asserts the group-by key is
   `pattern_name` (collapsing to one key, count 2), NOT
   `pattern_description`. **This is the G5 stability contract
   test.**
9. `test_by_date_groups_utc_date_from_timestamp` — authored
   fixture across two UTC dates; asserts correct date grouping.
10. `test_markdown_format_emits_deterministic_output` —
    collector called with `--format markdown`; asserts specific
    table headers and counts in output.

### Additional tests (optional, may include if time permits)

- `test_unique_file_paths_deduplicates` — same `file_path` across
  3 records; asserts 1 unique entry.
- `test_session_id_null_folded_to_unknown` — record with
  `session_id=null`; asserts `by_session_id["(unknown)"] == 1`.
- `test_cli_json_output_parses` — subprocess call; assert stdout
  is valid JSON matching report shape.

**Expected suite delta: 1161 → ~1171 (if #5 lands first, to ~1181).**

## Exit Criteria

1. `scripts/collect_phase_a_metrics.py` exists, executable, follows
   the design above.
2. Indexes only on stable-interface fields (`pattern_name`,
   `catalog_source`, `session_id`, `file_path`, `timestamp_utc`).
   **Never** on `pattern_description`. Enforced by
   `test_pattern_names_indexed_not_descriptions`.
3. Schema v1 fence enforced: records with other `schema_version`
   values are counted under `forward_compat.unknown_schema_versions`
   and NOT included in metric totals.
4. Malformed lines are counted, not crashing.
5. Output formats: JSON (default) and Markdown, both deterministic
   given the same input.
6. 7 fixture files under `tests/fixtures/phase_a_metrics/`.
7. ~10 tests in `tests/test_phase_a_metrics_collector.py`, all pass.
8. `mypy --strict` clean on the script (run via the existing
   `tests/test_full_tree_type_checks.py` or a direct
   `mypy --strict scripts/`).
9. `ruff check scripts/ tests/` clean.
10. Full suite: 1161 → ~1171 tests, all pass.
11. No edits to `scanner-safe-writer.py`, `templates/`, or any
    other production source file.
12. Single GT-KB commit after Codex GO.

## Review Gates Addressed (G1-G5)

- **G1** (High, #1 credential-patterns): N/A — this is a collector,
  not a pattern consumer. It indexes on `pattern_name` strings.
- **G2** (High, first skill bridge): N/A.
- **G3** (Medium, all): This is #6 of the six authorized bridges.
  Reports reference six-bridge counts consistently.
- **G4** (Medium, #5): N/A — #5's concern (outcome value).
- **G5** (Medium, #2 + #6): ✅ **Stable-interface contract honored.**
  The collector indexes only on schema-v1 stable fields. The
  `test_pattern_names_indexed_not_descriptions` test is the
  contract test: if a future change attempts to group on
  `pattern_description`, the test fails, protecting the contract.

## Dependencies and Parallel Work

- **Blocking predecessor resolved**: Tier A #2 scanner-safe-writer
  VERIFIED. Schema v1 committed. Contract language declaring
  `pattern_description` non-contractual is in the source docstring
  (not a drift risk).
- **Can parallel with**: Tier A #5 `gtkb-skill-spec-intake`
  (different files entirely: #5 touches
  `templates/skills/spec-intake/` + 3 `project/*.py` files;
  #6 touches `scripts/collect_phase_a_metrics.py` + fixtures +
  new test file). Zero file-ownership conflict.
- **Unblocks**: Phase A completion + v0.6.0 release bundle.
- **Long-term**: the metric output is the baseline dataset for
  future Phase B observability work. Keeping the JSON schema
  stable here enables CI integration without future bridge churn.

## Open Questions

1. **Log rotation**: `.claude/hooks/scanner-safe-writer.log` grows
   unbounded. Not this bridge's concern — but flagging it: a future
   bridge may want to implement rotation, or the collector may want
   a `--since <timestamp>` filter. Out of scope for #6.
2. **CI integration**: should `python scripts/collect_phase_a_metrics.py
   --format json` be wired into any CI workflow? Out of scope for
   #6; downstream adoption work.
3. **Log location in adopter projects**: the collector resolves
   `.claude/hooks/scanner-safe-writer.log` relative to CWD. Is
   that sufficient, or should it resolve via `get_templates_dir()`
   / project root discovery? For a simple script, CWD-relative is
   the convention. Can be revisited if adopter feedback warrants.

## Scanner Safety

Pre-flight scan (manual review, not helper-mediated — this bridge
file is being written via Write tool, which triggers the
scanner-safe-writer hook):

This proposal describes the scanner-safe-writer log schema in
prose. All examples of `pattern_name` values are canonical pattern
**names** (short string identifiers like `ar_live_key`,
`anthropic_api_key`, `api_key`). No literal credential values
(access-key IDs, full API tokens, JWT payloads, private-key blocks,
connection-string values) appear in this text. Span examples are
integer pairs. `file_path` values in fixtures are fictional
`bridge/foo-001.md`-style paths.

Expected hook verdict: **pass** (no credential-class regex matches).

If the hook denies this write, the first hit will identify the
specific match, and this proposal will be revised (not `--force`'d).

## GO Request

Codex, please review this proposal for:

1. **G5 stability contract test** — is
   `test_pattern_names_indexed_not_descriptions` sufficient as the
   contract guard? Would you prefer a stricter structural check
   (e.g., AST scan of the collector asserting that
   `pattern_description` never appears as a dict key or grouping
   argument)?
2. **Forward-compat semantics** — warn-and-skip for unknown
   `schema_version` values. Acceptable? Or should the collector
   refuse to run if ANY non-1 version is seen, forcing explicit
   upgrade?
3. **Metric set completeness** — the 7-metric set listed under
   "Metric set (schema v1)" covers counts, distributions, and
   forward-compat indicators. Is any obvious metric missing (e.g.,
   per-hour distribution, per-pattern time trend, session/pattern
   cross-tab)? If so, add to Phase A or defer to Phase B
   observability?
4. **Output contract** — JSON is the stable, testable contract.
   Markdown is a presentation concern. Is that the right split?
5. **Fixture authorship** — each fixture is described here as
   "N records with properties X". During implementation I will
   materialize each as actual JSONL files. Should I include the
   actual fixture contents inline in this proposal as examples,
   or is prose description sufficient for the review?

If approved: single GT-KB commit. ~300 net lines added (script +
fixtures + tests). Ruff/mypy/full-suite clean.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
