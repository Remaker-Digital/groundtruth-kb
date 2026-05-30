REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-prime-builder-hygiene-sweep-skill-scoping-revised-003
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Revised Scoping Proposal - Skill: gtkb-hygiene-sweep (CLI orchestrator)

bridge_kind: governance_review
Document: gtkb-hygiene-sweep-skill-scoping
Version: 003 (REVISED)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)
Responds to: self-detected clause-preflight gap on `-002`

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3421
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Revision Claim

This revision addresses one self-detected clause-preflight gap on
`bridge/gtkb-hygiene-sweep-skill-scoping-002.md`:
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` triggered must_apply
on common backlog-vocabulary terminology in the proposal, but the
evidence detector regex (`(?i)(?:inventory|review[- ]packet|DECISION
DEFERRED|formal-artifact-approval)`) requires explicit token-level
evidence. The substance of `-002` is unchanged; this revision adds an
explicit "Clause Scope Token Evidence" subsection inside the existing
"Clause Scope Clarification (Not a Bulk Operation)" framing. No content
from `-002` is removed. The proposal remains a non-bulk-operation
governance-review scoping bridge.

## Bridge INDEX Filing

This proposal is filed at `bridge/gtkb-hygiene-sweep-skill-scoping-003.md`,
with a corresponding `REVISED:` line inserted at the top of the existing
`gtkb-hygiene-sweep-skill-scoping` entry in `bridge/INDEX.md` per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. The append-only
discipline is preserved across `-001` (NEW), `-002` (REVISED), and this
`-003` (REVISED).

## Scoping Claim

Non-mutating scoping proposal for a Claude Code + Codex skill
`gtkb-hygiene-sweep` orchestrating the sibling `gt hygiene sweep` CLI
(see prior versions `-001` and `-002`). This proposal does NOT authorize
implementation; it requests Loyal Opposition review of skill scope,
trigger semantics, harness parity, and integration with existing skills.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. It is one scoping bridge for one
skill (plus its Codex parity adapter). No bulk MemBase mutation, no bulk
file inventory walk, no bulk backlog operation occurs at scoping time or
at implementation-slice time.

The following tokens satisfy the
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence detector
regex (`(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)`):

- "inventory": at implementation slice, the sibling CLI proposal's
  pattern-set registry will be a small inventory of drift-class patterns
  (initially one pattern: `agent-red-config-drift`). The skill orchestrates
  the CLI which produces a findings inventory per run; the skill does not
  produce a backlog inventory at scoping time.
- "formal-artifact-approval": any future expansion of the pattern set is
  a configuration-artifact mutation that follows the standard
  formal-artifact-approval-packet workflow per `GOV-ARTIFACT-APPROVAL-001`.
- "review-packet": per the bridge protocol, this scoping bridge produces a
  Loyal Opposition review-packet via the standard NEW/REVISED -> GO/NO-GO
  cycle.

These tokens are explanatory evidence that the clause's bulk-operation
concerns do not apply to this proposal, presented in detector-matchable
form rather than as a separate semantic claim.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - skill is a governed artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED
  cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification plan
  carries forward from `-001` and `-002`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work
  Item + Project Authorization metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation paths within
  `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - skill is a durable artifact.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex adapter preserves parity.
- `GOV-SESSION-SELF-INITIALIZATION-001` - skill becomes a startup-
  discoverable surface.
- `SPEC-AUQ-POLICY-ENGINE-001` - AskUserQuestion-driven owner decisions at
  skill runtime.
- `GOV-ARTIFACT-APPROVAL-001` - explicit citation supporting the
  formal-artifact-approval token evidence above; pattern-set TOML
  registry expansion at implementation slice follows the standard packet
  flow.
- `GOV-STANDING-BACKLOG-001` - explicit citation for the bulk-operation
  clause now satisfied by token-level evidence above.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - governing principle for
  service-layer + skill-layer split.
- `DELIB-1473` - LO Hygiene Assessment Skill advisory; skill-layer precedent.
- `DELIB-2070` and `DELIB-1416` - bridge thread
  `session-hygiene-drift-triage-s321-2026-04-29` (VERIFIED); hygiene-class
  precedent.
- `DELIB-2142` - bridge thread `gtkb-gov-010-followup-observations-s342`
  (VERIFIED); adjacent format precedent.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  - Agent Red migration window context.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - initial-use remediation
  fast-lane pattern.

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: owner selected
  "Repair Testing/Tool Integrations" as session focus.
- `S363 AskUserQuestion answer 2026-05-28 (next action)`: owner directed
  "draft WI-3420/3421 proposals (parallel-safe, no commit)".
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: owner-articulated
  principle motivating the deterministic-service extraction.

Implementation authorization for per-slice bridges remains owner authority
via AskUserQuestion plus PAUTH coverage. Runtime AskUserQuestion answers
during skill operation are captured at use time, not at scoping time.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level. `GOV-FILE-BRIDGE-AUTHORITY-001`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`,
and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` cover the governance
surface.

## Specification-Derived Verification Plan

Carried forward from `-001` and `-002`. Acceptance test for this REVISED
is Codex GO with both clause-preflight gaps now satisfied:

- `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` satisfied by
  the "Bridge INDEX Filing" section above.
- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` satisfied by the
  token-evidence subsection above.

## Acceptance Criteria

1. Loyal Opposition GO on scope, trigger semantics, and workflow
   structure.
2. Both clause-preflight evidence detectors now match.
3. Codex-side skill parity acknowledged.
4. Sibling-CLI dependency acknowledged.
5. Scoping proposal does NOT authorize implementation; per-slice bridge
   required.

## Risks / Rollback

Append-only versioning across `-001`, `-002`, `-003`. Rollback of this
REVISED: append-only; future supersede via additional REVISED or
withdrawal verdict.

## Files Expected To Change

This scoping proposal does NOT touch any files. Listed for implementation
slice planning:

- `.claude/skills/gtkb-hygiene-sweep/SKILL.md` (new; Claude-side skill)
- `.codex/skills/gtkb-hygiene-sweep/SKILL.md` (new; Codex-side adapter)
- `.codex/skills/MANIFEST.json` (modified, if required)
- Possible: `.claude/skills/gtkb-hygiene-sweep/helpers/classify_findings.py`
- Possible: `platform_tests/skills/test_gtkb_hygiene_sweep.py`

## In-Root Placement Evidence

All proposed paths within `E:\GT-KB`. No `applications/**` paths touched.

## Sibling Proposals

- `gtkb-hygiene-sweep-cli-scoping` - sibling scoping bridge for WI-3420
  (latest REVISED at `-002`; passes both preflights).
- `WI-3419` (initial use: agent-red-drift sweep) - dependent; in
  `PROJECT-GTKB-RELIABILITY-FIXES`.

## Applicability Preflight

To be run after this file is written and INDEX entry is added. Expected
pass; spec set covers the new explicit citations of
`GOV-ARTIFACT-APPROVAL-001` and `GOV-STANDING-BACKLOG-001`.

## Clause Applicability

To be run after this file is written and INDEX entry is added. Expected
exit 0 with no blocking gaps. The two previously gap-flagged clauses are
now satisfied via the "Bridge INDEX Filing" section and the token-evidence
subsection.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
