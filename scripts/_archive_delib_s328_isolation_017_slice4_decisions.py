# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Archive DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE.

Captures the three S328 owner decisions for GTKB-ISOLATION-017 Slice 4
(`gt project upgrade` isolation + migration) per the scoping bridge
`bridge/gtkb-isolation-017-scoping-003.md` Decision Map. Each decision
cited by the upcoming Slice 4 implementation bridge.

Run: python scripts/_archive_delib_s328_isolation_017_slice4_decisions.py \\
       --formal-approval-packet \\
       .groundtruth/formal-artifact-approvals/2026-05-02-isolation-017-slice4-decisions.json
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

DELIB_ID = "DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE"

CONTENT = """## Context

GTKB-ISOLATION-017 scoping bridge `bridge/gtkb-isolation-017-scoping-003.md` (Codex GO at `-004`) Decision Map clusters three Phase 9 owner decisions on Slice 4 (`gt project upgrade` isolation + migration kit invocation):

- Decision 1: Mandatory vs opt-in isolation for existing adopters
- Decision 3: Backward-compatibility policy (paired with decision 1)
- Decision 7: Phase 8 rehearsal-evidence integration into upgrade

Per the scoping bridge: "If the owner pre-decides any of these now, the corresponding slice bridge cites the decision DELIB; otherwise the slice bridge surfaces it via AskUserQuestion at filing time."

This DELIB captures the owner's pre-decisions, surfaced via AskUserQuestion at S328 (2026-05-02) before filing the Slice 4 implementation bridge.

## Decision 1 — Isolation mode for existing adopters

**Question (verbatim):** "When `gt project upgrade` detects an existing adopter root with mixed-root state (failing one or more of the 9 isolation doctor checks from Slice 1), how should it behave?"

**Owner answer:** `mandatory_at_upgrade`.

**Implementation consequence:** `gt project upgrade` refuses to upgrade an unmigrated adopter unless `--accept-migration` is passed. This is the sole isolation gate at upgrade time; opt-out exists for sandboxed/experimental adopters.

**Reasoning shared at decision time:** Simplest semantics, fits 'clean-adopter productization' framing for v0.7.0-rc1, lowest upgrade.py complexity. Adopters get one explicit gate.

## Decision 3 — Backward-compatibility policy (paired with decision 1)

**Question (verbatim):** "What backward-compatibility policy should `gt project upgrade` apply when an existing adopter is found in pre-isolation layout?"

**Owner answer:** `one_shot_migration_at_upgrade`.

**Implementation consequence:** At v0.7.0-rc1 launch, the upgrade runs the migration in a single payload-branch + rollback-receipt cycle. No deprecation window; the upgrade either migrates (when `--accept-migration` is passed) or refuses (per decision 1). Release notes carry the cutover statement.

**Reasoning shared at decision time:** Natural pair with decision 1 = mandatory; lowest upgrade.py branching; no deprecation window code-path. Agent Red is the only known adopter and already used the freeze-window runbook in S325; multi-adopter coordination is not currently a constraint.

## Decision 7 — Phase 8 rehearsal-evidence integration

**Question (verbatim):** "How should `gt project upgrade` integrate with the Phase 8 rehearsal driver (`scripts/rehearse_isolation.py`)?"

**Owner answer:** `out_of_band_recipe_only`.

**Implementation consequence:** `gt project upgrade` documents the rehearsal recipe in CLI output and the adopter README; the adopter runs `python scripts/rehearse_isolation.py --execute` themselves before invoking `gt project upgrade --accept-migration`. The upgrade flow never invokes the rehearsal driver. Rehearsal evidence remains adopter-owned and out-of-band.

**Reasoning shared at decision time:** Lowest upgrade.py code addition; preserves rehearsal/upgrade separation; rehearsal evidence stays adopter-owned. Avoids upgrade-time failure modes from rehearsal-driver wiring (sandbox path validation, freshness checks, evidence-file format coupling).

## Composite Slice 4 implementation shape

The three answers compose to:

1. Pre-flight: `gt project upgrade --apply` runs the 9 isolation doctor checks (`run_isolation_checks` from `groundtruth_kb.project.doctor_isolation`).
2. If any check fails AND `--accept-migration` not present → refuse (mandatory gate per decision 1).
3. If `--accept-migration` is present → migration plan runs as additional UpgradeAction rows in the existing payload-branch + rollback-receipt flow (one-shot per decision 3).
4. CLI output (and adopter README scaffolded by Slice 3) document the rehearsal recipe; upgrade does NOT call the rehearsal driver (out-of-band per decision 7).

Estimated source delta: ~150-200 LOC source + ~250-300 LOC tests (under the 450/550 envelope from scoping bridge §"Slice 4 — Estimated envelope").

## Disposition

This DELIB is cited by the upcoming Slice 4 implementation bridge `bridge/gtkb-isolation-017-slice4-upgrade-001.md` in the `Specification Links` and `Prior Deliberations` sections. Per the file-bridge protocol Mandatory Specification Linkage Gate, the linked tests for each decision will derive from this DELIB.

## Sequencing

This DELIB precedes the Slice 4 NEW filing in the same session turn. Slice 4 implementation lifecycle then follows the standard NEW → review → GO → impl → post-impl → VERIFIED cycle.
"""

SUMMARY = (
    "S328 owner pre-decided GTKB-ISOLATION-017 Slice 4's three Phase 9 "
    "decisions before bridge filing per the scoping bridge Decision Map "
    "directive. Decisions: 1 = mandatory_at_upgrade, 3 = "
    "one_shot_migration_at_upgrade, 7 = out_of_band_recipe_only. Composite "
    "shape: gt project upgrade --apply runs 9 isolation doctor checks; "
    "refuses on failure unless --accept-migration; with the flag runs a "
    "one-shot migration in the existing payload-branch + rollback-receipt "
    "flow; rehearsal driver invocation stays out-of-band (recipe documented "
    "in CLI output + adopter README only). Estimated envelope ~150-200 LOC "
    "source + ~250-300 LOC tests."
)


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")

    result = db.insert_deliberation(
        id=DELIB_ID,
        source_type="owner_conversation",
        title="S328 owner pre-decisions for GTKB-ISOLATION-017 Slice 4 (decisions 1, 3, 7 from scoping Decision Map)",
        summary=SUMMARY,
        content=CONTENT,
        changed_by="prime-builder/claude-code",
        change_reason=(
            "Archive S328 owner pre-decisions for GTKB-ISOLATION-017 Slice 4 "
            "per scoping bridge gtkb-isolation-017-scoping-003.md Decision "
            "Map directive. Cited by upcoming Slice 4 implementation bridge."
        ),
        outcome="owner_decision",
        session_id="S328",
        source_ref="owner_conversation:2026-05-02-S328-isolation-017-slice4-decisions",
    )
    delib_id = result.get("id") if result else DELIB_ID
    version = result.get("version") if result else "?"
    print(f"insert_deliberation id={delib_id} version={version}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
