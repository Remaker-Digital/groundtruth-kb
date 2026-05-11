"""One-off script to insert 4 enhancement-class backlog items spotted during S341 autonomous-execution turn.

Inserts directly via the public groundtruth_kb.db API. Each row is a work item
(type='work_item') with origin='new' and resolution_status='open', so it does
NOT trigger the formal-artifact-approval-gate (which gates GOV/SPEC/PB/ADR/DCL
/ deliberation insertions, not work_items). This is intentional: work items
are operational backlog rows, not governance artifacts.

Run from repo root with:
    PYTHONPATH=groundtruth-kb/src python .tmp/add_backlog_items.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add the platform package to sys.path before importing.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402


ITEMS = [
    {
        "id": "WI-3266",
        "title": "GTKB-FORMAL-ARTIFACT-PACKET-VALIDATOR-CLI - canonical formal-artifact packet validator helper",
        "origin": "new",
        "component": "scripts",
        "resolution_status": "open",
        "priority": "MEDIUM",
        "description": (
            "Author scripts/validate_formal_artifact_packet.py as a small CLI/library that imports "
            ".claude/hooks/formal-artifact-approval-gate.py module's validate_packet() function (or "
            "equivalent helper) and exposes a stable command-line interface. Currently 5+ bridge "
            "proposals (workflow-contract-adr, owner-gate-dcl, template-spec, routing-dcl, "
            "dashboard-counters-spec) embed similar inline-Python validation patterns that have been "
            "NO-GO'd twice for (a) PowerShell-escaping fragility, (b) under-validating compared to "
            "the live gate (missing approval_mode / presented_to_user / transcript_captured checks). "
            "A canonical helper script eliminates duplication, prevents drift between proposals and "
            "the live gate, and matches DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE. Slice 1 "
            "acceptance: helper script + paired tests + reference from one bridge proposal IP-4 "
            "in place of inline Python."
        ),
        "source_owner_directive": (
            "S341 owner directive 2026-05-11: 'if you notice an issue which should be fixed or an "
            "opportunity for a useful enhancement that will help us work more effectively in the "
            "future, please add it to the backlog as an item for future implementation consideration.'"
        ),
        "related_bridge_threads": (
            "bridge/gtkb-peer-solution-workflow-contract-adr-006.md (NO-GO F1 + F2); "
            "bridge/gtkb-peer-solution-owner-gate-dcl-004.md (NO-GO F1 + F2)"
        ),
        "regression_visibility": (
            "Cross-thread NO-GO repetition: same F1/F2 pattern in workflow-contract-adr -006 and "
            "owner-gate-dcl -004; will likely repeat in advisory-report-template-spec-001, "
            "advisory-routing-dcl-001, advisory-report-dashboard-counters-spec-001 unless the "
            "helper script lands first."
        ),
        "changed_by": "prime-builder/claude",
        "change_reason": "S341 owner directive on adding useful enhancements; spotted during workflow-contract-adr/owner-gate-dcl REVISED iteration",
    },
    {
        "id": "WI-3267",
        "title": "GTKB-BRIDGE-PROPOSAL-CITATION-FRESHNESS-PREFLIGHT - warn on stale cross-thread state references",
        "origin": "new",
        "component": "scripts",
        "resolution_status": "open",
        "priority": "MEDIUM",
        "description": (
            "When a bridge proposal cites another bridge thread by version (e.g., 'REVISED-3 at "
            "-007'), the cited version may already be superseded by Codex review time. My "
            "advisory-report-protocol-extension-001 cited gtkb-bridge-advisory-status-001 as "
            "'REVISED-3 at -007' but it was already NO-GO at -008 by review time, triggering F1 "
            "NO-GO. Extend scripts/bridge_applicability_preflight.py (or add a sibling "
            "scripts/bridge_citation_freshness_preflight.py) that: (1) parses cross-thread "
            "version references from the proposal body using a stable pattern; (2) cross-checks "
            "each reference against the live bridge/INDEX.md latest status for the cited slug; "
            "(3) emits a warning when the cited version is no longer the latest, with a "
            "suggested updated citation. Slice 1 acceptance: detector handles N=2 fixture cases "
            "(workflow-contract-adr vs runtime thread) + emits cleanup hint + reviewer-facing "
            "markdown section that Codex can cite."
        ),
        "source_owner_directive": (
            "S341 owner directive 2026-05-11: 'add useful enhancements that will help us work "
            "more effectively in the future.'"
        ),
        "related_bridge_threads": (
            "bridge/gtkb-advisory-report-protocol-extension-002.md (NO-GO F1 on stale runtime "
            "thread citation); same pattern observable in advisory-report-protocol-extension-001 "
            "and likely in any cross-referencing proposal."
        ),
        "regression_visibility": (
            "Cross-harness event-driven trigger compresses iteration cycles, so cross-thread "
            "state moves under Prime's feet between filing and review. Without an automated check, "
            "every multi-thread proposal is at risk of stale-citation F1."
        ),
        "changed_by": "prime-builder/claude",
        "change_reason": "S341 owner directive; spotted during advisory-report-protocol-extension review cycle",
    },
    {
        "id": "WI-3268",
        "title": "GTKB-CODEX-FEEDBACK-PATTERN-LINTS - pre-filing lint catching recurrent NO-GO mechanical patterns",
        "origin": "new",
        "component": "scripts",
        "resolution_status": "open",
        "priority": "MEDIUM",
        "description": (
            "Recurring Codex NO-GO findings in S341 are mechanical and detectable pre-filing: "
            "(a) bare `pytest` command instead of `python -m pytest`; (b) 'Codex VERIFIED "
            "(pending)' wording on pre-implementation proposals where 'Codex GO' is correct; "
            "(c) PowerShell-fragile inline-Python escaping with `\\\"` inside `python -c \"...\"`; "
            "(d) missing standalone `OWNER ACTION REQUIRED` block evidence requirement when "
            "narrative-artifact approval packets are part of scope. A scripts/lint_bridge_proposal.py "
            "that runs against a draft proposal and flags these patterns before submission would "
            "shorten the Prime->Codex iteration cycle from 2-3 rounds per defect class to 0. "
            "Slice 1 acceptance: lint detects all 4 pattern classes + emits remediation hint + "
            "exit-1 on detection."
        ),
        "source_owner_directive": (
            "S341 owner directive 2026-05-11: 'add useful enhancements that will help us work "
            "more effectively in the future.'"
        ),
        "related_bridge_threads": (
            "Pattern (a) bare-pytest hit: workflow-contract-adr-002 F1, owner-gate-dcl-002 F2, "
            "advisory-report-protocol-extension-002 F3. Pattern (b) lifecycle-wording hit: "
            "peer-solution-conversion-002 F3, advisory-report-message-type-conversion-002 F3, "
            "mcp-stable-harness-surface-conversion-002 NOTE-P3-001. Pattern (c) PowerShell-"
            "escaping hit: workflow-contract-adr-006 F1, owner-gate-dcl-004 F1. Pattern (d) "
            "OWNER-ACTION-REQUIRED hit: advisory-report-protocol-extension-002 F2, "
            "owner-gate-dcl-002 F1."
        ),
        "regression_visibility": (
            "Defect repetition shows the bridge protocol catches these correctly, but each "
            "round consumes Codex review tokens and adds queue depth. A pre-filing lint converts "
            "post-filing NO-GO cycles into pre-filing self-corrections."
        ),
        "changed_by": "prime-builder/claude",
        "change_reason": "S341 owner directive; spotted across 8+ NO-GO findings this session",
    },
    {
        "id": "WI-3269",
        "title": "GTKB-GT-BACKLOG-ADD-CLI - add `gt backlog add` subcommand for owner-directed backlog additions",
        "origin": "new",
        "component": "groundtruth-kb",
        "resolution_status": "open",
        "priority": "LOW",
        "description": (
            "The unified backlog CLI at groundtruth-kb/src/groundtruth_kb/cli/backlog.py currently "
            "provides only `list` and `migrate-work-list` subcommands. Owner-directed backlog "
            "additions (e.g., this very turn's 'please add to the backlog') require either editing "
            "memory/work_list.md (protected narrative artifact requiring formal approval packet) "
            "or invoking the Python API directly via a one-off script. An `add` subcommand with "
            "required fields (id auto-generated as next WI-NNNN, title, origin, component, "
            "priority) and the rest prompted or accepted via flags would close the operating-model "
            "contract for owner-directed backlog additions. Matches DELIB-S312-DETERMINISTIC-"
            "SERVICES-PRINCIPLE. Slice 1 acceptance: `gt backlog add --title X --origin new "
            "--component scripts --priority MEDIUM --description 'Y'` returns the WI ID and "
            "writes the row."
        ),
        "source_owner_directive": (
            "S341 owner directive 2026-05-11: 'add useful enhancements that will help us work "
            "more effectively in the future.' Self-referential: the absence of `gt backlog add` "
            "is itself the inconvenience being added to the backlog."
        ),
        "regression_visibility": (
            "Without the CLI, every owner-directed backlog addition requires either Python-API "
            "scripting (this turn's .tmp/add_backlog_items.py) or AUQ-mediated work_list.md edits."
        ),
        "changed_by": "prime-builder/claude",
        "change_reason": "S341 owner directive; spotted while attempting to add the three sibling items above and finding no `gt backlog add` subcommand",
    },
]


def main() -> int:
    db = KnowledgeDB("groundtruth.db")
    inserted = []
    for item in ITEMS:
        result = db.insert_work_item(
            id=item["id"],
            title=item["title"],
            origin=item["origin"],
            component=item["component"],
            resolution_status=item["resolution_status"],
            changed_by=item["changed_by"],
            change_reason=item["change_reason"],
            description=item.get("description"),
            priority=item.get("priority"),
            source_owner_directive=item.get("source_owner_directive"),
            related_bridge_threads=item.get("related_bridge_threads"),
            regression_visibility=item.get("regression_visibility"),
        )
        inserted.append((item["id"], result is not None))
        print(f"inserted {item['id']}: {item['title'][:80]}")
    print()
    print(f"total inserted: {sum(1 for _, ok in inserted if ok)}/{len(ITEMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
