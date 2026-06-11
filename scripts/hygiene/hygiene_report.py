"""GT-KB hygiene-investigation chunked report generator (FAB-20, WI-4432).

Renders a list of structured hygiene findings (``HygieneFinding``) into the
v1-style investigation report, split into **size-bounded chunks** so a large
finding corpus does not exceed a single context window. Also emits each finding
in a form **routable to the ``work_items`` backlog** (``finding_to_work_item``),
so findings become governed backlog candidates rather than markdown-only context
(``GOV-08``, ``GOV-STANDING-BACKLOG-001``).

The module is pure and side-effect-free: every entry point is a function that
takes findings and returns strings or dicts. It performs NO subprocess execution,
NO ``groundtruth.db`` / MemBase write, NO ``gt backlog add`` invocation, and NO
bridge mutation. ``finding_to_work_item`` produces the routable *form*; the actual
routing run is a separate, owner-gated step under ``GOV-STANDING-BACKLOG-001``
(capture is not implementation approval). This separation is what makes the
generator testable without a live agent run and keeps bulk backlog mutation out
of the generator (Codex GO constraint, ``-004``).

It also implements NO delta mode and consumes NO FAB-19 evidence pack: the delta
differ is a deferred follow-on (FAB-19 producer contract pending).

Bridge: bridge/gtkb-fab-20-hygiene-investigation-skill-004.md (GO).
Project Authorization: PAUTH-FAB20-20260610 (PROJECT-FABLE-INVESTIGATION / WI-4432).
Specs: GOV-08, GOV-STANDING-BACKLOG-001, SPEC-DSI-DOCTOR-CHECK-001,
       DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

# Make the sibling baseline module importable whether this file is run as a
# script (its directory is sys.path[0]) or loaded by file location in a test.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from hygiene_baseline import HygieneFinding, load_baseline  # noqa: E402

DEFAULT_MAX_CHARS = 12000
"""Default per-chunk character budget (well under a single context window)."""

_HEADER_RESERVE = 256
"""Chars reserved per chunk for the chunk header, kept out of the block budget."""

WORK_ITEM_ORIGIN = "hygiene"
"""Origin label for findings routed to the backlog (a valid ``gt backlog add`` origin)."""

DEFAULT_COMPONENT = "gtkb-platform"
"""Component used when a finding has no FAB-cluster mapping."""


def _section(label: str, value: str | None) -> list[str]:
    if not value:
        return []
    return [f"**{label}:** {value}", ""]


def render_finding(finding: HygieneFinding) -> str:
    """Render a single finding into a self-contained markdown block.

    Only fields that are present are emitted, so the frozen-baseline subset
    (id/title/class/ratings) renders cleanly alongside rich live-probe findings.
    """
    lines: list[str] = [f"### {finding.id} — {finding.title}", ""]

    meta: list[str] = [f"- Class: {finding.finding_class}"]
    ratings = [r for r in (finding.impact, finding.effort, finding.confidence) if r]
    if ratings:
        meta.append(
            "- Impact / Effort / Confidence: "
            f"{finding.impact or '?'} / {finding.effort or '?'} / {finding.confidence or '?'}"
        )
    if finding.fab_cluster:
        meta.append(f"- FAB cluster: {finding.fab_cluster}")
    if finding.source:
        meta.append(f"- Source: {finding.source}")
    lines.extend(meta)
    lines.append("")

    lines.extend(_section("Problem statement", finding.problem_statement))

    if finding.locations:
        lines.append("**Locations:**")
        lines.extend(f"- {loc}" for loc in finding.locations)
        lines.append("")

    lines.extend(_section("Verification", finding.verification))

    if finding.current_state or finding.expected_state:
        lines.append("**Current vs expected:**")
        if finding.current_state:
            lines.append(f"- Current: {finding.current_state}")
        if finding.expected_state:
            lines.append(f"- Expected: {finding.expected_state}")
        lines.append("")

    if finding.owner_touchpoint_required:
        question = finding.owner_question or "(owner decision required; question not recorded)"
        lines.extend(_section("Owner touchpoint", question))
        if finding.decision_complexity:
            lines.append(f"Decision complexity: {finding.decision_complexity}")
            lines.append("")

    lines.extend(_section("Proposed approach", finding.proposed_approach))

    if finding.related_items:
        lines.extend(_section("Related", ", ".join(finding.related_items)))

    return "\n".join(lines).rstrip() + "\n"


def _chunk_header(title: str, index: int, total: int) -> str:
    return f"# {title} — chunk {index}/{total}\n\n"


def generate_report_chunks(
    findings: Sequence[HygieneFinding],
    *,
    title: str = "GT-KB Hygiene Investigation Report",
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[str]:
    """Render findings into size-bounded markdown chunks.

    Each returned chunk is ``<= max_chars`` characters, EXCEPT a chunk holding a
    single finding whose rendered block alone exceeds the block budget
    (``max_chars - _HEADER_RESERVE``); such a finding becomes its own chunk and
    is never split mid-finding. With no findings, returns a single empty-corpus
    chunk so callers always get at least one renderable string.
    """
    if max_chars <= _HEADER_RESERVE:
        raise ValueError(f"max_chars must exceed {_HEADER_RESERVE} (got {max_chars})")
    block_budget = max_chars - _HEADER_RESERVE

    blocks = [render_finding(finding) for finding in findings]
    if not blocks:
        return [f"# {title} — chunk 1/1\n\n_No findings in this corpus._\n"]

    # Greedily pack blocks into groups that fit the block budget.
    groups: list[list[str]] = []
    current: list[str] = []
    current_len = 0
    for block in blocks:
        block_len = len(block) + 1  # +1 for the inter-block newline
        if current and current_len + block_len > block_budget:
            groups.append(current)
            current = []
            current_len = 0
        current.append(block)
        current_len += block_len
    if current:
        groups.append(current)

    total = len(groups)
    return [
        _chunk_header(title, index, total) + "\n".join(group).rstrip() + "\n"
        for index, group in enumerate(groups, start=1)
    ]


def finding_to_work_item(finding: HygieneFinding) -> dict[str, Any]:
    """Return a finding in a form routable to the ``work_items`` backlog.

    The returned dict carries exactly the fields ``gt backlog add`` consumes
    (``title``, ``origin``, ``component``, ``change_reason``, ``description``)
    plus ``source_finding_id`` for traceability. This produces the routable
    FORM only; it performs no mutation. Routing a finding into ``work_items`` is
    a separate, per-finding, owner-gated step (``GOV-STANDING-BACKLOG-001``).
    """
    description_parts: list[str] = []
    if finding.problem_statement:
        description_parts.append(finding.problem_statement)
    if finding.current_state:
        description_parts.append(f"Current: {finding.current_state}")
    if finding.expected_state:
        description_parts.append(f"Expected: {finding.expected_state}")
    if finding.proposed_approach:
        description_parts.append(f"Proposed: {finding.proposed_approach}")
    if finding.locations:
        description_parts.append("Locations: " + "; ".join(finding.locations))
    description = "\n\n".join(description_parts) or finding.title

    change_reason = (
        f"Hygiene-investigation finding {finding.id} ({finding.finding_class}); "
        "GOV-STANDING-BACKLOG-001 capture (not implementation approval)."
    )
    return {
        "title": finding.title,
        "origin": WORK_ITEM_ORIGIN,
        "component": finding.fab_cluster or DEFAULT_COMPONENT,
        "change_reason": change_reason,
        "description": description,
        "source_finding_id": finding.id,
    }


def findings_to_work_items(findings: Sequence[HygieneFinding]) -> list[dict[str, Any]]:
    """Map findings to routable work-item forms (no mutation; see ``finding_to_work_item``)."""
    return [finding_to_work_item(finding) for finding in findings]


def main(argv: list[str] | None = None) -> int:
    """CLI: render the frozen baseline (``--baseline``) as a chunked report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Render the frozen HYG baseline registry as a chunked report.",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Per-chunk character budget (default {DEFAULT_MAX_CHARS}).",
    )
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Print only the number of chunks, not the chunk bodies.",
    )
    args = parser.parse_args(argv)

    if not args.baseline:
        parser.print_help()
        return 2

    registry = load_baseline()
    chunks = generate_report_chunks(
        registry.findings,
        title=f"GT-KB Hygiene Baseline ({registry.baseline_id})",
        max_chars=args.max_chars,
    )
    if args.count_only:
        print(len(chunks))
        return 0
    for index, chunk in enumerate(chunks, start=1):
        print(chunk)
        if index < len(chunks):
            print("\n---\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
