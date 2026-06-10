REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-prime-builder-hygiene-sweep-cli-scoping-revised-002
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Revised Scoping Proposal - Deterministic CLI: gt hygiene sweep

bridge_kind: governance_advisory
Document: gtkb-hygiene-sweep-cli-scoping
Version: 002 (REVISED)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)
Responds to: self-detected clause-preflight gap on `-001`

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3420
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Revision Claim

This revision addresses one self-detected clause-preflight gap on
`bridge/gtkb-hygiene-sweep-cli-scoping-001.md`:
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` reported evidence
missing because the `-001` proposal text lacked the literal phrasing the
detector regex requires (`(?i)(?:bridge/INDEX\.md|INDEX update|insert.+top
of.+(?:INDEX|entry))`). The substance of `-001` is unchanged; this revision
adds an explicit "Bridge INDEX Filing" section satisfying the evidence
detector. No content from `-001` is removed.

## Bridge INDEX Filing

This proposal is filed at `bridge/gtkb-hygiene-sweep-cli-scoping-002.md`,
with a corresponding `REVISED:` line inserted at the top of the existing
`gtkb-hygiene-sweep-cli-scoping` entry in `bridge/INDEX.md` per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. The original
NEW filing at `-001` inserted the `Document: gtkb-hygiene-sweep-cli-scoping`
+ `NEW: bridge/gtkb-hygiene-sweep-cli-scoping-001.md` entry at the top of
`bridge/INDEX.md`. No prior version is deleted or rewritten; append-only
discipline preserved.

## Scoping Claim (Unchanged From -001)

This is a non-mutating scoping proposal for a new deterministic CLI surface
`gt hygiene sweep` whose purpose is to enumerate config-drift instances across
the GT-KB repository against an owner-curated pattern set. The CLI emits a
machine-readable JSON inventory plus a human-readable markdown summary.
This proposal does NOT authorize implementation; it requests Loyal Opposition
review of scope, design, target paths, and integration with the existing
deterministic-services portfolio.

After GO and explicit per-slice project authorization, a follow-on implementation
bridge will land the CLI module, the pattern-set TOML registry, and tests.

## Motivation - S363 Class Observation (Unchanged From -001)

Three independent bridge items in session S363 (2026-05-27/28) surfaced the
same underlying defect class: Agent-Red-inherited config drift carried in
GT-KB repo-root files that were not relinked after the GroundTruth-KB rename
and isolation work.

The three observed instances are documented in `-001` § Motivation. Per
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: repetitive plumbing work
performed by AI on a per-instance basis is a defect. Three session-by-session
investigations of the same drift class is the threshold to extract the
discovery work into a service.

## Proposed Scope (Carried Forward From -001)

The proposed scope is unchanged. Three components:

1. **Pattern-set TOML registry** at `config/governance/hygiene-sweep-patterns.toml`
2. **CLI surface** `gt hygiene sweep` in `groundtruth-kb/src/groundtruth_kb/cli.py`
3. **Tests** at `platform_tests/scripts/test_hygiene_sweep_cli.py`

See `-001` for full design details (schema, command semantics, output
contract, test coverage).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this REVISED
  proposal preserves append-only versioning and `bridge/INDEX.md` canonical
  state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the hygiene-sweep CLI itself
  becomes a governed artifact, and its pattern-set registry is a governed
  configuration artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED
  cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the
  Specification-Derived Verification Plan in `-001` maps acceptance to
  verification commands at design-slice and implementation-slice timing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item
  + Project Authorization metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation target
  paths within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - CLI + TOML are durable artifacts.
- `GOV-ARTIFACT-APPROVAL-001` - the pattern-set TOML follows formal
  artifact approval flow at implementation slice.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions captured via
  AskUserQuestion at per-slice implementation bridges.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - governing principle for
  the deterministic-services extraction.
- `DELIB-1473` - LO Hygiene Assessment Skill advisory; sibling-concept
  precedent.
- `DELIB-2070` and `DELIB-1416` - bridge thread
  `session-hygiene-drift-triage-s321-2026-04-29` (VERIFIED); session-bounded
  hygiene precedent.
- `DELIB-2142` - bridge thread `gtkb-gov-010-followup-observations-s342`
  (VERIFIED); adjacent governance-hygiene format precedent.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  - Agent Red migration window context.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - fast-lane pattern for the
  initial-use remediation child-bridges.

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: "Repair
  Testing/Tool Integrations" as session focus.
- `S363 AskUserQuestion answer 2026-05-28 (next action)`: "draft WI-3420/3421
  proposals (parallel-safe, no commit)".
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner-articulated principle.

Implementation authorization for per-slice bridges remains owner authority
via AskUserQuestion plus PAUTH coverage.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level. See `-001` §
Requirement Sufficiency.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One scoping proposal, two named work items in the
deterministic-services portfolio. References to "work item", "standing
backlog", and "inventory" describe this thread's deterministic-service scope.

## Specification-Derived Verification Plan

Carried forward from `-001` unchanged. The acceptance test for this scoping
REVISED is Codex GO with the clause-preflight evidence now satisfied.

## Acceptance Criteria (Scoping Bridge)

1. Loyal Opposition GO on scope, design, target paths, and integration.
2. Clause-preflight evidence detector now matches the explicit `bridge/INDEX.md`
   filing language in this REVISED.
3. Scoping proposal does NOT authorize implementation; per-slice bridges
   required.

## Risks / Rollback

Carried forward from `-001`. Rollback of this REVISED: append-only; `-002`
remains as audit-trail evidence even if a future REVISED supersedes it.

## Files Expected To Change (Implementation Slice, Not This Bridge)

Same as `-001`:

- `config/governance/hygiene-sweep-patterns.toml` (new)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (modified)
- `platform_tests/scripts/test_hygiene_sweep_cli.py` (new)

## In-Root Placement Evidence

All proposed paths within `E:\GT-KB`. No `applications/**` paths touched.

## Sibling Proposals

- `gtkb-hygiene-sweep-skill-scoping` - sibling scoping bridge for WI-3421.
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
