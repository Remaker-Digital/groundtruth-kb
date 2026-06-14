"""Startup payload budget report (WI-4360, Slice A).

Deterministic, read-only consumer of the ``gtkb-startup-payload-profile-v1``
profile files written by the WI-4361 startup instrumentation
(``.gtkb-state/startup-payload-profiles/last-<harness>.json``). It aggregates
those per-session profiles into a by-harness startup-payload *budget report*:
per-harness byte/token totals split into a mandatory tier (compact routing
facts in ``additionalContext``) and an expandable tier (demand-loaded detail
in ``startupDisclosure``), plus cross-harness totals.

Design invariants (per bridge ``gtkb-startup-payload-budget-report`` GO@-002):

- **Decoupled consumer.** This module imports nothing from the startup
  producer ``scripts/session_self_initialization.py``; it reads only the
  stable versioned JSON contract. Any coupling to the producer would require a
  fresh Loyal Opposition review.
- **Pure compute core.** ``classify_section``, ``build_harness_budget``,
  ``build_budget_report``, and ``render_markdown`` are pure: no clock, no
  randomness, no I/O, no input mutation. ``now`` is injected so identical
  inputs + identical ``now`` produce byte-identical output.
- **Read-only / additive.** The only writes are to the gitignored runtime dir
  ``.gtkb-state/startup-payload-profiles/`` (``budget-report.json`` /
  ``budget-report.md``); no canonical/tracked path is written, and the
  init-keyword disclosure path is never touched.

Specification links:
  - ``DCL-SESSION-STARTUP-TOKEN-BUDGET-001`` — per-harness byte/token budgets.
  - ``DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`` — mandatory vs expandable
    tier split.
  - ``GOV-SESSION-SELF-INITIALIZATION-001`` — deterministic, replayable report.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

# Must track the producer's contract emitted in
# .gtkb-state/startup-payload-profiles/last-*.json. A producer rename is
# detectable via this field (and asserted by the test suite).
CONTRACT_VERSION = "gtkb-startup-payload-profile-v1"

SectionClass = Literal["mandatory", "expandable"]

# Documented section -> tier classification per
# DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001. Sections not listed default to
# "expandable" and are surfaced in BudgetReport.unknown_sections so a future
# producer section is flagged rather than silently mis-bucketed.
SECTION_CLASS: dict[str, SectionClass] = {
    "additionalContext": "mandatory",
    "startupDisclosure": "expandable",
}

DEFAULT_PROFILES_DIR = Path(".gtkb-state") / "startup-payload-profiles"
_PROFILE_GLOB = "last-*.json"


@dataclass(frozen=True)
class SectionMetrics:
    """One section's size metrics plus its mandatory/expandable tier."""

    name: str
    utf8_bytes: int
    rough_token_estimate: int
    line_count: int
    character_count: int
    klass: SectionClass


@dataclass(frozen=True)
class HarnessBudget:
    """Per-harness aggregate of all profiled sections, split by tier."""

    harness_id: str
    harness_name: str
    role_profile: str
    total_bytes: int
    total_tokens: int
    mandatory_bytes: int
    mandatory_tokens: int
    expandable_bytes: int
    expandable_tokens: int
    sections: tuple[SectionMetrics, ...]


@dataclass(frozen=True)
class ReportTotals:
    """Cross-harness totals."""

    harness_count: int
    total_bytes: int
    total_tokens: int
    mandatory_bytes: int
    mandatory_tokens: int
    expandable_bytes: int
    expandable_tokens: int


@dataclass(frozen=True)
class UnknownSection:
    """A profiled section name with no SECTION_CLASS entry (defaulted)."""

    harness_name: str
    section_name: str


@dataclass(frozen=True)
class BudgetReport:
    """The full by-harness budget report."""

    contract_version: str
    generated_at: str
    harnesses: tuple[HarnessBudget, ...]
    totals: ReportTotals
    unknown_sections: tuple[UnknownSection, ...]


def classify_section(name: str) -> SectionClass:
    """Map a section name to its budget tier.

    Unknown names default to ``"expandable"`` (the conservative tier: detail
    that need not be paid up front) and are flagged separately by the caller.
    """

    return SECTION_CLASS.get(name, "expandable")


def _coerce_int(value: object) -> int:
    """Best-effort non-negative int coercion for a metric field."""

    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def build_harness_budget(
    profile: dict,
) -> tuple[HarnessBudget, list[UnknownSection]]:
    """Aggregate one profile record's sections into a :class:`HarnessBudget`.

    Pure: does not mutate ``profile``. Returns the budget plus the list of
    unknown (unclassified) sections discovered in this record.
    """

    harness_name = str(profile.get("harness_name", ""))
    raw_sections = profile.get("sections") or {}

    metrics: list[SectionMetrics] = []
    unknown: list[UnknownSection] = []
    # Sort by section name so output ordering is deterministic regardless of
    # JSON key order.
    for section_name in sorted(raw_sections):
        data = raw_sections[section_name] or {}
        klass = classify_section(section_name)
        if section_name not in SECTION_CLASS:
            unknown.append(UnknownSection(harness_name=harness_name, section_name=section_name))
        metrics.append(
            SectionMetrics(
                name=section_name,
                utf8_bytes=_coerce_int(data.get("utf8_bytes")),
                rough_token_estimate=_coerce_int(data.get("rough_token_estimate")),
                line_count=_coerce_int(data.get("line_count")),
                character_count=_coerce_int(data.get("character_count")),
                klass=klass,
            )
        )

    mandatory_bytes = sum(m.utf8_bytes for m in metrics if m.klass == "mandatory")
    mandatory_tokens = sum(m.rough_token_estimate for m in metrics if m.klass == "mandatory")
    expandable_bytes = sum(m.utf8_bytes for m in metrics if m.klass == "expandable")
    expandable_tokens = sum(m.rough_token_estimate for m in metrics if m.klass == "expandable")

    budget = HarnessBudget(
        harness_id=str(profile.get("harness_id", "")),
        harness_name=harness_name,
        role_profile=str(profile.get("role_profile", "")),
        total_bytes=mandatory_bytes + expandable_bytes,
        total_tokens=mandatory_tokens + expandable_tokens,
        mandatory_bytes=mandatory_bytes,
        mandatory_tokens=mandatory_tokens,
        expandable_bytes=expandable_bytes,
        expandable_tokens=expandable_tokens,
        sections=tuple(metrics),
    )
    return budget, unknown


def build_budget_report(profiles: list[dict], *, now: str) -> BudgetReport:
    """Aggregate profile records into a by-harness :class:`BudgetReport`.

    Pure: ``now`` (a UTC ISO string) is injected for determinism. Harnesses are
    sorted by ``harness_name`` so identical inputs + identical ``now`` produce
    byte-identical output.
    """

    budgets: list[HarnessBudget] = []
    unknown: list[UnknownSection] = []
    for profile in profiles:
        budget, profile_unknown = build_harness_budget(profile)
        budgets.append(budget)
        unknown.extend(profile_unknown)

    budgets.sort(key=lambda b: b.harness_name)
    unknown.sort(key=lambda u: (u.harness_name, u.section_name))

    totals = ReportTotals(
        harness_count=len(budgets),
        total_bytes=sum(b.total_bytes for b in budgets),
        total_tokens=sum(b.total_tokens for b in budgets),
        mandatory_bytes=sum(b.mandatory_bytes for b in budgets),
        mandatory_tokens=sum(b.mandatory_tokens for b in budgets),
        expandable_bytes=sum(b.expandable_bytes for b in budgets),
        expandable_tokens=sum(b.expandable_tokens for b in budgets),
    )

    return BudgetReport(
        contract_version=CONTRACT_VERSION,
        generated_at=now,
        harnesses=tuple(budgets),
        totals=totals,
        unknown_sections=tuple(unknown),
    )


def report_to_dict(report: BudgetReport) -> dict:
    """Convert a report to a JSON-serializable dict (deterministic field order)."""

    return asdict(report)


def render_json(report: BudgetReport) -> str:
    """Render the report as deterministic pretty-printed JSON."""

    return json.dumps(report_to_dict(report), indent=2, ensure_ascii=False)


def render_markdown(report: BudgetReport) -> str:
    """Render a by-harness comparison table plus an unknown-sections note.

    Pure: one table row per harness with byte/token columns and the
    mandatory/expandable split, a totals row, and (when present) a note listing
    sections that had no classification and were defaulted to expandable.
    """

    lines: list[str] = []
    lines.append("# Startup Payload Budget Report")
    lines.append("")
    lines.append(f"- contract_version: `{report.contract_version}`")
    lines.append(f"- generated_at: `{report.generated_at}`")
    lines.append(f"- harness_count: {report.totals.harness_count}")
    lines.append("")
    lines.append(
        "| Harness | Role | Total bytes | Total tokens | "
        "Mandatory bytes | Mandatory tokens | Expandable bytes | Expandable tokens |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for b in report.harnesses:
        lines.append(
            f"| {b.harness_name} | {b.role_profile} | {b.total_bytes} | "
            f"{b.total_tokens} | {b.mandatory_bytes} | {b.mandatory_tokens} | "
            f"{b.expandable_bytes} | {b.expandable_tokens} |"
        )
    t = report.totals
    lines.append(
        f"| **TOTAL** | — | {t.total_bytes} | {t.total_tokens} | "
        f"{t.mandatory_bytes} | {t.mandatory_tokens} | "
        f"{t.expandable_bytes} | {t.expandable_tokens} |"
    )
    lines.append("")

    if report.unknown_sections:
        lines.append("## Unknown sections (defaulted to expandable)")
        lines.append("")
        lines.append(
            "These section names have no `SECTION_CLASS` entry; a producer "
            "change may have added a section. Classify them in "
            "`SECTION_CLASS` to budget them correctly."
        )
        lines.append("")
        for u in report.unknown_sections:
            lines.append(f"- `{u.section_name}` (harness: {u.harness_name})")
        lines.append("")

    return "\n".join(lines)


def load_profiles(profiles_dir: Path) -> list[dict]:
    """Read ``last-*.json`` profile records from ``profiles_dir``.

    Thin I/O wrapper: returns only records whose ``contract_version`` matches
    :data:`CONTRACT_VERSION`; non-contract or unparseable files are skipped.
    Files are read in sorted filename order for determinism. Inputs are never
    mutated. A missing directory yields an empty list.
    """

    if not profiles_dir.is_dir():
        return []

    records: list[dict] = []
    for path in sorted(profiles_dir.glob(_PROFILE_GLOB)):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(raw, dict):
            continue
        if raw.get("contract_version") != CONTRACT_VERSION:
            continue
        records.append(raw)
    return records


def _utc_now_iso() -> str:
    """Current UTC time as a ``YYYY-MM-DDTHH:MM:SSZ`` string (I/O boundary only)."""

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint: build the report and write it (or print with --stdout)."""

    parser = argparse.ArgumentParser(
        description=(
            "Deterministic by-harness startup-payload budget report over gtkb-startup-payload-profile-v1 profile data."
        )
    )
    parser.add_argument(
        "--profiles-dir",
        type=Path,
        default=DEFAULT_PROFILES_DIR,
        help=f"Directory holding last-<harness>.json profile files (default: {DEFAULT_PROFILES_DIR}).",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the markdown report to stdout instead of writing files.",
    )
    args = parser.parse_args(argv)

    profiles = load_profiles(args.profiles_dir)
    report = build_budget_report(profiles, now=_utc_now_iso())

    markdown = render_markdown(report)
    if args.stdout:
        print(markdown)
        return 0

    out_dir: Path = args.profiles_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "budget-report.json").write_text(render_json(report), encoding="utf-8")
    (out_dir / "budget-report.md").write_text(markdown, encoding="utf-8")
    print(
        f"Wrote {out_dir / 'budget-report.json'} and "
        f"{out_dir / 'budget-report.md'} "
        f"({report.totals.harness_count} harness profile(s))."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
