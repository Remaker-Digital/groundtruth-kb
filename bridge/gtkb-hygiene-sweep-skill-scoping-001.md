NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-prime-builder-hygiene-sweep-skill-scoping
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Scoping Proposal - Skill: gtkb-hygiene-sweep (CLI orchestrator)

bridge_kind: governance_advisory
Document: gtkb-hygiene-sweep-skill-scoping
Version: 001 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3421
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Scoping Claim

This is a non-mutating scoping proposal for a new Claude Code + Codex skill
`gtkb-hygiene-sweep` that orchestrates the deterministic `gt hygiene sweep`
CLI (sibling proposal `gtkb-hygiene-sweep-cli-scoping`), classifies the CLI's
findings, and guides remediation child-bridge filing. This proposal does NOT
authorize implementation; it requests Loyal Opposition review of skill scope,
trigger semantics, harness parity, and integration with existing skills.

After GO and explicit per-slice project authorization, a follow-on
implementation bridge will land the Claude-side SKILL.md, the Codex-side
SKILL.md, and any helper scripts.

## Motivation - Service Layer vs Procedure Layer Separation

The sibling CLI proposal extracts the drift-discovery deterministic plumbing
into a service. This proposal extracts the orchestration around that service
into a skill. The separation matches the existing pattern across the
deterministic-services portfolio:

| Service | CLI | Skill |
|---|---|---|
| Bridge proposal authoring | `gt bridge propose` | `gtkb-bridge-propose` |
| Assertion triage | `scripts/assertion_categorize.py` | `assertion-triage` |
| Hygiene sweep (this thread) | `gt hygiene sweep` (sibling proposal) | `gtkb-hygiene-sweep` (this proposal) |

The CLI does the deterministic work (enumerate, classify, emit). The skill
provides the operator-facing entry point: when to invoke, what owner
clarification is needed, how to interpret findings, and how to convert
findings into remediation child-bridges.

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: the service-layer/skill-layer
split keeps the deterministic work outside session-by-session AI exploration
while preserving the human-judgment surface (which findings warrant remediation
bridges, which are acceptable residuals, which expand the pattern set).

## Proposed Scope

### Component 1 - Claude-side skill

Location: `.claude/skills/gtkb-hygiene-sweep/SKILL.md`

Frontmatter:

```yaml
---
name: gtkb-hygiene-sweep
description: Orchestrate the deterministic `gt hygiene sweep` CLI; classify findings; guide remediation child-bridge filing. Use when investigating config-drift class observations, after seeing repeated similar config-defect bridges in a session, or proactively at session start when the S363-style class observation pattern fires.
---
```

Section structure:

1. **When to invoke** - Trigger conditions: explicit owner direction, after
   2+ similar config-defect bridges in a session, S363-class class
   observations from the surfacing hook.
2. **What this skill does** - Calls the CLI, reads findings, presents
   classification to owner via AskUserQuestion.
3. **Mandatory pre-flight** - Read findings inventory; never auto-file
   remediation bridges without owner-decided priorities.
4. **Workflow** - Sequence: invoke CLI -> read findings -> classify by
   class (config_drift, agent_red_inherited, etc.) -> present
   AskUserQuestion menu of remediation options -> file child-bridges
   on owner approval.
5. **Output** - Reports findings count by class, ranked remediation
   options, per-finding child-bridge slugs to consider.
6. **Does NOT** - Auto-file bridges, expand the pattern set without
   owner approval, modify source files directly.

### Component 2 - Codex-side skill adapter

Location: `.codex/skills/gtkb-hygiene-sweep/SKILL.md`

Per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, the Codex adapter mirrors the
Claude-side skill with Codex-appropriate invocation patterns (apply_patch
authoring constraints, deliberation-search adapter helper). The adapter
references the same CLI surface.

### Component 3 - Optional helper

Location: `.claude/skills/gtkb-hygiene-sweep/helpers/classify_findings.py`
(if needed)

If the classification logic is non-trivial (e.g., grouping findings by
shared file, deduplicating cross-pattern hits), a small helper script
under the skill's directory keeps the SKILL.md focused on owner-facing
guidance.

### Component 4 - Skill registration

Skill is auto-discovered by the Claude Code + Codex harness via the
`.claude/skills/` and `.codex/skills/` directory conventions. No manifest
edit required for Claude side. Codex side may require an entry in
`.codex/skills/MANIFEST.json` per the harness adapter pattern.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal
  follows NEW scoping discipline.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the skill is a governed artifact
  (operator-facing automation surface).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the
  Specification-Derived Verification Plan below maps acceptance to
  verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item +
  Project Authorization metadata present; authorization explicitly disclaims
  implementation per the governance_review pattern.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation target paths
  are within `E:\GT-KB` under `.claude/skills/`, `.codex/skills/`; no
  `applications/**` paths touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the skill is a durable artifact.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Codex-side skill adapter
  preserves harness parity.
- `GOV-SESSION-SELF-INITIALIZATION-001` - the skill becomes an available
  startup-discoverable surface; startup payload may surface "hygiene sweep
  recommended" when class-observation thresholds fire.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions on which findings warrant
  remediation bridges are captured via AskUserQuestion, never prose.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - establishes the service-layer
  extraction principle that motivates the CLI + skill split.
- `DELIB-1473` - Loyal Opposition Advisory: LO Hygiene Assessment Skill;
  precedent for skill-layer governance work on hygiene topics.
- `DELIB-2070` and `DELIB-1416` - bridge thread
  `session-hygiene-drift-triage-s321-2026-04-29` (VERIFIED); session-bounded
  hygiene work that this skill extracts into a reusable surface.
- `DELIB-2142` - bridge thread `gtkb-gov-010-followup-observations-s342`
  (VERIFIED); adjacent governance-hygiene work; format precedent.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  - Agent Red migration window context.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - relevant for the initial-use
  remediation bridge filing flow; small remediation child-bridges from
  CLI findings fit the fast-lane shape.

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: owner selected
  "Repair Testing/Tool Integrations" as session focus.
- `S363 AskUserQuestion answer 2026-05-28 (next action)`: owner directed
  "draft WI-3420/3421 proposals (parallel-safe, no commit)".
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner-articulated principle
  that motivates the skill-layer extraction.

Implementation authorization for the future per-slice bridge remains owner
authority via AskUserQuestion plus PAUTH coverage. AskUserQuestion-driven
owner decisions during skill operation (which findings warrant remediation
bridges) are captured at runtime, not at scoping time.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level. `GOV-FILE-BRIDGE-AUTHORITY-001`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`,
and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` cover the governance surface.
The skill is a thin orchestration layer over the CLI; no new GOV/SPEC/ADR/DCL
required.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One scoping proposal, one named work item, one skill
(plus its Codex adapter). The skill orchestrates a single CLI surface; it
does not perform bulk MemBase mutations, bulk file inspection, or bulk
backlog operations. The CLI it orchestrates is itself bounded by
`exclusion_globs` per the sibling proposal.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Slice timing |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread NEW -> GO/NO-GO -> implementation slice bridge | This scoping bridge |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | SKILL.md frontmatter + body structure inspection | Implementation slice |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links inspection above | This scoping bridge |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table | This scoping bridge |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection | This scoping bridge |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All proposed paths under `E:\GT-KB` | Implementation slice |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Skill lifecycle inspection | Implementation slice |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Both `.claude/skills/` and `.codex/skills/` adapter present | Implementation slice |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Startup payload surfaces skill availability | Implementation slice |
| `SPEC-AUQ-POLICY-ENGINE-001` | AskUserQuestion usage at skill runtime | Implementation slice (runtime) |

The acceptance test for this scoping proposal is Codex GO on scope, design,
harness parity, and integration with the sibling CLI proposal.

## Acceptance Criteria (Scoping Bridge)

1. Loyal Opposition GO on the proposed skill scope, trigger semantics, and
   workflow structure.
2. Codex side skill parity acknowledged (Codex adapter mirrors Claude
   surface).
3. Sibling-CLI dependency acknowledged (skill orchestrates the CLI; CLI must
   land first or in parallel).
4. Scoping proposal does NOT authorize implementation; per-slice bridge
   required.

## Risks / Rollback

- Risk: the skill may auto-fire remediation bridges without owner approval.
  Mitigation: SKILL.md explicitly forbids auto-filing; all remediation
  bridges go through AskUserQuestion-gated decisions.
- Risk: skill discovery latency could be high if findings are many.
  Mitigation: CLI emits structured JSON; skill reads and summarizes; no
  per-finding AskUserQuestion (instead: ranked-options menus).
- Risk: harness parity drift between Claude and Codex skill adapters.
  Mitigation: parity check in `scripts/check_codex_hook_parity.py`-equivalent
  or new skill-parity test if needed (added at implementation slice).
- Rollback: scoping proposal can be withdrawn at NEW status (no file
  mutation). Implementation slice would document its own rollback (delete
  the skill directories).

## Files Expected To Change (Implementation Slice, Not This Bridge)

This scoping proposal does NOT touch any of these files. Listed for
implementation slice planning:

- `.claude/skills/gtkb-hygiene-sweep/SKILL.md` (new; Claude-side skill)
- `.codex/skills/gtkb-hygiene-sweep/SKILL.md` (new; Codex-side adapter)
- `.codex/skills/MANIFEST.json` (modified; add new skill entry if required
  by harness manifest convention)
- Possible: `.claude/skills/gtkb-hygiene-sweep/helpers/classify_findings.py`
  (new; classification helper if non-trivial)
- Possible: `platform_tests/skills/test_gtkb_hygiene_sweep.py` (new; skill
  smoke test)

## In-Root Placement Evidence

All proposed paths above are within `E:\GT-KB`. No `applications/**` paths
touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied at
the design level.

## Sibling Proposals

- WI-3420 (gt hygiene sweep CLI) - sibling scoping bridge filed in parallel
  at `bridge/gtkb-hygiene-sweep-cli-scoping-001.md`. This skill depends on
  that CLI for the deterministic enumeration; the CLI is the data source.
- WI-3419 (initial use: agent-red-drift sweep) - dependent work item; blocked
  by both this skill and the CLI; in `PROJECT-GTKB-RELIABILITY-FIXES`.

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry is
added. Expected: `preflight_passed: true`; `missing_required_specs: []`.

## Clause Applicability

Clause preflight will be run after this file is written. Expected exit 0 with
no blocking gaps; governance-review kind disclaims implementation, so
implementation-clauses apply to the design-level plan rather than executed
evidence.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
