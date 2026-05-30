REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-prime-builder-hygiene-sweep-skill-scoping-revised-002
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Revised Scoping Proposal - Skill: gtkb-hygiene-sweep (CLI orchestrator)

bridge_kind: governance_review
Document: gtkb-hygiene-sweep-skill-scoping
Version: 002 (REVISED)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)
Responds to: self-detected clause-preflight gap on `-001`

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3421
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Revision Claim

This revision addresses one self-detected clause-preflight gap on
`bridge/gtkb-hygiene-sweep-skill-scoping-001.md`:
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` reported evidence
missing because the `-001` proposal text lacked the literal phrasing the
detector regex requires (`(?i)(?:bridge/INDEX\.md|INDEX update|insert.+top
of.+(?:INDEX|entry))`). The substance of `-001` is unchanged; this revision
adds an explicit "Bridge INDEX Filing" section satisfying the evidence
detector. No content from `-001` is removed.

## Bridge INDEX Filing

This proposal is filed at `bridge/gtkb-hygiene-sweep-skill-scoping-002.md`,
with a corresponding `REVISED:` line inserted at the top of the existing
`gtkb-hygiene-sweep-skill-scoping` entry in `bridge/INDEX.md` per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. The original
NEW filing at `-001` inserted the
`Document: gtkb-hygiene-sweep-skill-scoping` +
`NEW: bridge/gtkb-hygiene-sweep-skill-scoping-001.md` entry at the top of
`bridge/INDEX.md`. No prior version is deleted or rewritten; append-only
discipline preserved.

## Scoping Claim (Unchanged From -001)

This is a non-mutating scoping proposal for a new Claude Code + Codex skill
`gtkb-hygiene-sweep` that orchestrates the deterministic `gt hygiene sweep`
CLI (sibling proposal `gtkb-hygiene-sweep-cli-scoping`), classifies the CLI's
findings, and guides remediation child-bridge filing. This proposal does NOT
authorize implementation; it requests Loyal Opposition review of skill scope,
trigger semantics, harness parity, and integration with existing skills.

After GO and explicit per-slice project authorization, a follow-on
implementation bridge will land the Claude-side SKILL.md, the Codex-side
SKILL.md, and any helper scripts.

## Motivation - Service Layer vs Procedure Layer Separation (Unchanged From -001)

The sibling CLI proposal extracts drift-discovery deterministic plumbing into
a service. This proposal extracts the orchestration into a skill. The
separation matches the existing pattern across the deterministic-services
portfolio (bridge-propose CLI + skill; assertion triage script + skill).

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: the service-layer /
skill-layer split keeps deterministic work outside session-by-session AI
exploration while preserving the human-judgment surface.

## Proposed Scope (Carried Forward From -001)

Four components, unchanged from `-001`:

1. **Claude-side skill** at `.claude/skills/gtkb-hygiene-sweep/SKILL.md`
2. **Codex-side skill adapter** at `.codex/skills/gtkb-hygiene-sweep/SKILL.md`
3. **Optional helper** at `.claude/skills/gtkb-hygiene-sweep/helpers/classify_findings.py`
4. **Skill registration** via `.claude/skills/` + `.codex/skills/` auto-discovery
   (with possible `.codex/skills/MANIFEST.json` entry)

See `-001` for full design details (frontmatter, section structure, workflow,
output contract, forbidden auto-behavior).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this REVISED
  preserves append-only versioning and `bridge/INDEX.md` canonical state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - skill is a governed artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED
  cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the
  Specification-Derived Verification Plan in `-001` maps acceptance to
  verification at design-slice and implementation-slice timing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item
  + Project Authorization metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation paths within
  `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - skill is a durable artifact.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex adapter preserves parity.
- `GOV-SESSION-SELF-INITIALIZATION-001` - skill becomes startup-discoverable
  surface.
- `SPEC-AUQ-POLICY-ENGINE-001` - AskUserQuestion-driven owner decisions at
  skill runtime.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

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
  pattern.

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: "Repair
  Testing/Tool Integrations" as session focus.
- `S363 AskUserQuestion answer 2026-05-28 (next action)`: "draft WI-3420/3421
  proposals (parallel-safe, no commit)".
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner-articulated principle.

Implementation authorization for per-slice bridges remains owner authority
via AskUserQuestion plus PAUTH coverage. Runtime AskUserQuestion answers
during skill operation captured at use time, not at scoping time.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level. See `-001`
§ Requirement Sufficiency.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One scoping proposal, one named work item, one skill
plus Codex adapter. The skill orchestrates a single CLI; no bulk MemBase
mutations, bulk file inspection, or bulk backlog operations.

## Specification-Derived Verification Plan

Carried forward from `-001` unchanged. Acceptance test for this REVISED is
Codex GO with the clause-preflight evidence now satisfied.

## Acceptance Criteria (Scoping Bridge)

1. Loyal Opposition GO on scope, trigger semantics, and workflow structure.
2. Clause-preflight evidence detector now matches the explicit
   `bridge/INDEX.md` filing language in this REVISED.
3. Codex-side skill parity acknowledged.
4. Sibling-CLI dependency acknowledged.
5. Scoping proposal does NOT authorize implementation; per-slice bridge
   required.

## Risks / Rollback

Carried forward from `-001`. Rollback of this REVISED: append-only.

## Files Expected To Change (Implementation Slice, Not This Bridge)

Same as `-001`:

- `.claude/skills/gtkb-hygiene-sweep/SKILL.md` (new)
- `.codex/skills/gtkb-hygiene-sweep/SKILL.md` (new)
- `.codex/skills/MANIFEST.json` (modified, if required)
- Possible: `.claude/skills/gtkb-hygiene-sweep/helpers/classify_findings.py`
- Possible: `platform_tests/skills/test_gtkb_hygiene_sweep.py`

## In-Root Placement Evidence

All proposed paths within `E:\GT-KB`. No `applications/**` paths touched.

## Sibling Proposals

- `gtkb-hygiene-sweep-cli-scoping` - sibling scoping bridge for WI-3420; the
  CLI this skill orchestrates.
- `WI-3419` (initial use: agent-red-drift sweep) - dependent; in
  `PROJECT-GTKB-RELIABILITY-FIXES`.

## Applicability Preflight

To be run after this file is written and INDEX entry is added. Expected
pass; spec set unchanged from `-001` which passed.

## Clause Applicability

To be run after this file is written and INDEX entry is added. Expected
exit 0 with no blocking gaps; the new "Bridge INDEX Filing" section above
satisfies the `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`
evidence detector that was gap-flagged on `-001`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
