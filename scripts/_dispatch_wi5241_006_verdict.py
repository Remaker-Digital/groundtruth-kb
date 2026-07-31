#!/usr/bin/env python3
"""One-shot dispatch helper: preflights + git status + write WI-5241-006 NO-GO."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.adr_dcl_clause_preflight import (  # noqa: E402
    evaluate_clauses,
    find_operative_file,
    load_clauses,
)
from scripts.adr_dcl_clause_preflight import (  # noqa: E402
    render_markdown as render_clause_markdown,
)
from scripts.bridge_applicability_preflight import build_packet, format_markdown  # noqa: E402
from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

SLUG = "gtkb-wi5241-wi5219-pauth-registered-vocabulary"
VERSION = 6
OUT_JSON = PROJECT_ROOT / "scripts" / "_dispatch_wi5241_006_out.json"


def git_status_scoped() -> str:
    paths = [
        "groundtruth.db",
        ".claude/skills/verify/helpers/write_verdict.py",
        "scripts/bridge_review_independence.py",
        f"bridge/{SLUG}-001.md",
        f"bridge/{SLUG}-002.md",
        f"bridge/{SLUG}-003.md",
        f"bridge/{SLUG}-004.md",
        f"bridge/{SLUG}-005.md",
    ]
    proc = subprocess.run(
        ["git", "status", "--short", "--", *paths],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return (proc.stdout or proc.stderr or "").strip()


def main() -> int:
    bridge_dir = PROJECT_ROOT / "bridge"
    packet = build_packet(bridge_id=SLUG, bridge_dir=bridge_dir)
    applicability_md = format_markdown(packet)

    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    operative = find_operative_file(SLUG, bridge_dir)
    assert operative is not None
    operative_content = operative.read_text(encoding="utf-8")
    clause_results = evaluate_clauses(clauses, operative_content, SLUG, [f"bridge/{operative.name}"])
    clause_md = render_clause_markdown(SLUG, operative, clause_results, content=operative_content, report_only=False)

    git_scoped = git_status_scoped()
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

    content = f"""NO-GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T09-03-44Z-loyal-opposition-E-a79a7e
author_model: composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor headless bridge auto-dispatch; Loyal Opposition harness E

# Loyal Opposition Disposition Verdict - WI-5241 WI-5219 PAUTH Registered Vocabulary Stand-Down

bridge_kind: lo_verdict
Document: {SLUG}
Version: {VERSION:03d}
Responds to: bridge/{SLUG}-005.md
Reviewed prior verdict: bridge/{SLUG}-004.md
Date: 2026-07-16 UTC

## Verdict

NO-GO (disposition-scoped; substance-affirming). Prime's version-005 stand-down is substantively correct: accepting the version-004 NO-GO and declining to finalize the commingled `groundtruth.db` carrier under WI-5241 alone is the right call, and I agree with every substantive claim in the stand-down. NO-GO is issued only because a REVISED `implementation_report` cannot be the thread's resting state -- it stays Loyal-Opposition-actionable and the dispatcher keeps re-selecting it -- and neither available terminal verdict fits. VERIFIED is both semantically wrong (the report performs no implementation and explicitly states WI-5241 is not verified) and mechanically blocked (the branch VERIFIED finalizer is itself dirty and unverified). The correct terminal state for a work item parked pending a precondition is owner-directed DEFERRED, which only a durable Prime Builder harness can file, with owner evidence. This verdict routes the thread out of the Loyal Opposition queue to Prime for that filing.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (headless bridge auto-dispatch, dispatch id `2026-07-16T09-03-44Z-loyal-opposition-E-a79a7e`, harness E/cursor).
- Status authored here: `NO-GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/{SLUG}-005.md`, status `REVISED`, `bridge_kind: implementation_report`, author session `2026-07-16T01-48-03Z-prime-builder-A-b8e790`.
- Reviewer session context: `2026-07-16T09-03-44Z-loyal-opposition-E-a79a7e`, distinct from the report author session. Not same-session self-review; author metadata is present and readable.

## Why Not VERIFIED (two independent blockers)

1. No implementation to verify. The version-005 report is an explicit stand-down: its `target_paths` is only the bridge file itself, its Files Changed section lists only this bridge report, and its Acceptance Status states that WI-5241 is not VERIFIED by this report. VERIFIED is dated evidence that an implementation has been verified against the linked specifications (operating-model section 1). There is no such implementation here -- the report withdraws the finalization request. Recording VERIFIED would falsely mark WI-5241 verified-complete when its finalization is deliberately deferred.

2. Branch finalizer is dirty/unverified. VERIFIED is a commit-finalization outcome, and the only governed path is `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`. On this `{branch}` branch that finalizer is unstaged-dirty (`git status --short` scoped output below), carrying the uncommitted, not-yet-VERIFIED WI-5113 git-no-window change (thread `gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2` latest is `-004` NO-GO) plus a co-dependent review-independence change. Running that unreviewed finalizer to produce a terminal governed commit is the same finalizer-machinery-commingle block already recorded against parallel PAUTH carrier threads this week. No clean governed VERIFIED commit can be produced on this branch until WI-5113 lands.

## Positive Confirmations (substance affirmed)

- The version-002 GO and version-004 NO-GO are both sound; the version-005 stand-down honors the version-004 required action.
- The commingled-carrier premise is live: scoped `git status --short` shows a modified tracked binary `groundtruth.db`, which per the version-003 report and version-004 NO-GO carries both the WI-5241 PAUTH v2 append and the separately GO-authorized-but-unverified WI-5240 append. An atomic WI-5241-only VERIFIED commit of that binary would consume WI-5240 unverified work, and refusing it is correct.
- The version-005 report performs no implementation mutation: the dirty `groundtruth.db`, `write_verdict.py`, and `bridge_review_independence.py` are pre-existing working-tree state from other work, not products of this bridge-only report.
- The cited remediation dependencies are real and pending: `bridge/gtkb-wi5329-bounded-database-carrier-restoration-003.md` (restore a valid committed DB baseline) latest status is `NEW`; the sibling `bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-005.md` is likewise `REVISED`, a parallel stand-down over the same carrier.

## Findings

### P1 - REVISED implementation_report stand-down cannot reach a stable parked state; needs owner-directed DEFERRED

Observation: version-005 is a Prime stand-down/deferral filed as a REVISED `implementation_report` that declares no new owner decision is required and defers WI-5241 pending WI-5329. REVISED is Loyal-Opposition-actionable, so the thread remains in the dispatch queue and will be re-selected; it is not a resting state.

Deficiency rationale: the canonical non-actionable parking state for holding a work item until a precondition is met is `DEFERRED`, which is owner-only and must be filed by a durable Prime Builder harness with concrete Owner Decisions/Input evidence, a deferral reason, and a clear/resume condition (file-bridge-protocol.md section DEFERRED Status). Prime cannot self-file DEFERRED from a REVISED report, and a headless worker cannot supply the owner evidence. Deferring WI-5241 on Prime's own authority via a REVISED report both leans into owner-only DEFERRED territory and leaves the thread perpetually LO-actionable.

Impact: without a terminal or parked transition the thread churns the LO dispatch pool; and if a headless Prime re-files another REVISED stand-down in response to this NO-GO, the churn simply becomes a NO-GO/REVISED loop. Neither is a correct resting state.

Required action (route to Prime; do NOT headlessly re-file another REVISED): an interactive durable Prime Builder session must either (a) file owner-directed `DEFERRED` for this thread -- first non-blank line `DEFERRED`, `bridge_kind: operational_state_change`, with a cited owner decision (AUQ/DELIB), the deferral reason, and the clear/resume condition that WI-5329 restores a valid committed `groundtruth.db` baseline and WI-5113 lands a clean VERIFIED finalizer -- or (b) once WI-5329 and WI-5113 have landed, produce a fresh exact WI-5241-only carrier candidate (per version-004 Required Revisions) and re-file the implementation report for a real VERIFIED against a clean finalizer.

## Required Revisions

1. Do not respond to this NO-GO with another headless REVISED stand-down; that cannot terminate the thread.
2. From an interactive durable Prime Builder session, file `DEFERRED` for `{SLUG}` with owner-decision evidence, a deferral reason, and the clear/resume condition tied to WI-5329 (clean committed carrier) and WI-5113 (clean finalizer). This parks the thread non-actionably and ends the dispatch churn.
3. Alternatively, after WI-5329 and WI-5113 land, reconstruct the committed-HEAD DB, replay only the WI-5241 PAUTH vocabulary append, produce a reviewed exact WI-5241-only binary candidate (per version-004), and re-file the implementation report for VERIFIED against the clean finalizer. If the owner instead prefers whole-carrier finalization, the governed precedent is a WI-5241-specific hunk-scoped/by-reference finalization waiver (as owner granted for WI-5210 and WI-4841); note that path still requires a clean finalizer (WI-5113) and does not exist for WI-5241 today.
4. Keep the version-005 stand-down in the audit trail regardless; it correctly narrows the WI-5241 claim surface and is not rejected on substance.

{applicability_md}
{clause_md}

## Specification-Derived Verification

| Requirement | Applicability | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` numbered-chain correction | must apply | PASS: this NO-GO is the next numbered bridge file and preserves the audit trail |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must apply | PASS: `-005` carries concrete governing links; applicability preflight clean |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must apply | NO-GO: VERIFIED withheld - deferred work plus dirty branch finalizer; no clean spec-derived finalization is possible now |
| Terminal disposition authority | must apply | NO-GO: correct terminal state (owner-directed `DEFERRED`) is outside Loyal Opposition authority; routed to Prime |

## Prior Deliberations

- `DELIB-202666173` - owner evidence carried forward for the WI-5219/WI-5241 repair.
- `bridge/{SLUG}-001.md` - approved proposal.
- `bridge/{SLUG}-002.md` - independent GO.
- `bridge/{SLUG}-003.md` - implementation report that claimed `groundtruth.db`.
- `bridge/{SLUG}-004.md` - NO-GO on the whole-carrier finalization; this verdict affirms it.
- `bridge/gtkb-wi5329-bounded-database-carrier-restoration-003.md` - NEW; the cited clean-carrier-baseline dependency.
- `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-004.md` - NO-GO; the finalizer fix is itself uncommitted, keeping the branch finalizer dirty.
- `bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-005.md` - parallel stand-down over the same commingled carrier.
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` and `DELIB-20260710-WI4841-HUNK-SCOPED-FINALIZATION-WAIVER` - owner precedent for WI-specific hunk-scoped/by-reference finalization waivers over shared carriers; no equivalent WI-5241 waiver exists, so whole-carrier finalization under WI-5241 remains unauthorized.

## Commands Executed

- `git rev-parse --abbrev-ref HEAD` => `{branch}`
- `git status --short` scoped to `write_verdict.py`, `groundtruth.db`, `bridge_review_independence.py`, and the thread files:
```
{git_scoped}
```
- Read of the full `{SLUG}` thread chain (versions 001 through 005)
- `python scripts/bridge_applicability_preflight.py --bridge-id {SLUG}`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id {SLUG}`

## Opportunity Radar

The recurring blocker is a shared binary `groundtruth.db` carrier that cannot be atomically finalized per-work-item, compounded by a dirty branch finalizer. Both are already tracked (WI-5329 for a clean committed carrier baseline; WI-5113 for the finalizer). No new automation candidate is warranted here; the missing artifacts are those two landings plus an owner-directed DEFERRED to park WI-5241 in the meantime.

## Owner Action Required

None for me (headless). The DEFERRED filing itself requires an interactive durable Prime Builder session with an owner decision; that is Prime's routing action, not a blocking owner decision I can or should solicit here.

Recommended commit type: this verdict is non-terminal and is left untracked; no commit is produced by this NO-GO.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: bridge, verify, code-review-audit, lo-opportunity-radar
"""

    path = write_bridge_file(
        SLUG,
        VERSION,
        content,
        PROJECT_ROOT,
        author_metadata={
            "author_identity": "loyal-opposition/cursor",
            "author_harness_id": "E",
            "author_session_context_id": "2026-07-16T09-03-44Z-loyal-opposition-E-a79a7e",
        },
        require_author_metadata=False,
    )

    OUT_JSON.write_text(
        json.dumps(
            {
                "written_path": str(path),
                "applicability_md": applicability_md,
                "clause_md": clause_md,
                "git_scoped": git_scoped,
                "branch": branch,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
