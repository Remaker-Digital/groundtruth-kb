Document: gtkb-lo-opportunity-radar-skill

Project Authorization: PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE
Project: PROJECT-GTKB-LO-OPPORTUNITY-RADAR
Work Item: WI-3324
target_paths: [".claude/skills/lo-opportunity-radar/SKILL.md", ".codex/skills/lo-opportunity-radar/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "tests/skills/test_lo_opportunity_radar_skill.py"]

# Implementation Proposal: lo-opportunity-radar Skill (First Slice)

Status: NEW
Author: Prime Builder (claude / harness B)
Date: 2026-05-15 (S353+)
Origin: Loyal Opposition advisory INSIGHTS-2026-05-15-10-58-lo-opportunity-radar.md (Finding 1), converted to scoped implementation work.
Source advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-10-58-lo-opportunity-radar.md`

## Summary

Implement the first slice of `SPEC-LO-OPPORTUNITY-RADAR-001`: a canonical
`lo-opportunity-radar` skill that gives Loyal Opposition a structured review
posture biased toward finding — beyond defects — token-savings opportunities
and deterministic-service / automation candidates, and routing material
findings through the existing advisory-router.

This slice is the skill only. Per the owner-approved scope boundary in
`SPEC-LO-OPPORTUNITY-RADAR-001`, the advisory's deferred Findings 2-4 (the
`scripts/lo_opportunity_radar.py` scanner, the `gt check` CLI command, and
dedicated hook surfaces) are explicitly out of scope and remain backlog
candidates pending a future owner decision.

## Specification Links

- SPEC-LO-OPPORTUNITY-RADAR-001 — the governing requirement; this proposal implements its first-slice scope (the skill). Status `specified`.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — project-scoped implementation authorization; this work is bounded by PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Claude / Codex parity; the skill ships with a generated Codex adapter so both harnesses carry it.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — platform / application placement; this skill is a GT-KB platform artifact under `.claude/skills/`, not an adopter-application file.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority governing this proposal as a bridge artifact.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — cross-cutting constraint requiring the VERIFIED step to rest on executed spec-derived tests; the Spec-Derived Test Plan maps every behavior clause to a test.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — bridge-proposal project-linkage; satisfied by the Project Authorization / Project / Work Item header metadata lines.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 — work item must belong to an approved project; WI-3324 is a member of PROJECT-GTKB-LO-OPPORTUNITY-RADAR under an active authorization.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — artifact-oriented governance baseline; this work is captured as governed artifacts (SPEC, DELIB, project, WI, bridge thread, tests).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — durable artifact-graph model; the SPEC, project, WI, and bridge thread form the artifact graph for this work.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle trigger discipline; the LO advisory triggered a work item, a spec, and this implementation proposal.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-LO-OPPORTUNITY-RADAR-001` (owner-approved
this session, status `specified`) fully specifies the capability and the
first-slice scope boundary. No new or revised requirement or specification is
created by this work. On successful verification, a separate `kb-promote`
operation may later advance `SPEC-LO-OPPORTUNITY-RADAR-001` toward
`implemented`; that promotion is out of scope here.

## Prior Deliberations

- DELIB-S353-LO-OPPORTUNITY-RADAR-DISPOSITION-2026-05-15 — owner-decision deliberation for this session: owner chose the skill-only first slice and approved SPEC-LO-OPPORTUNITY-RADAR-001. The owner-approval anchor for this proposal.
- DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15 — the grill-me-for-clarification skill project decision; structural precedent for delivering a new skill as SPEC -> project + authorization -> WI -> bridge proposal -> implementation.

No prior deliberation rejected an LO opportunity-radar skill or a comparable
review-posture skill; this is the first proposal on the topic.

## Owner Decisions / Input

This proposal depends on owner approval, authorized by the following
AskUserQuestion decisions captured this session (2026-05-15, S353+) and
archived as `DELIB-S353-LO-OPPORTUNITY-RADAR-DISPOSITION-2026-05-15`:

1. Disposition of advisory `INSIGHTS-2026-05-15-10-58-lo-opportunity-radar.md` — owner selected **"Pursue skill-only first slice"** (over pursue-full and defer).
2. Specification approval — owner selected **"Approve as written"** for `SPEC-LO-OPPORTUNITY-RADAR-001`.
3. Project + authorization approval — owner selected **"Approve as written"** for `PROJECT-GTKB-LO-OPPORTUNITY-RADAR` and `PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE`.

## Objective

Deliver a canonical `lo-opportunity-radar` skill that adds a required short
structured pass to applicable Loyal Opposition review work, per
`SPEC-LO-OPPORTUNITY-RADAR-001`:

1. Defect pass — concrete errors, unsafe assumptions, contradictions, missing tests, governance drift.
2. Token-savings pass — large repeated reads, oversized hook payloads, noisy generated summaries, repeated context relays, over-broad searches.
3. Deterministic-service pass — repeated manual sequences with stable inputs, objective outputs, idempotent behavior.
4. Surface-eligibility pass — classify a candidate as hook / benchmark / doctor check / gt CLI / script / skill-only guidance.
5. Routing pass — record material findings as a Loyal Opposition advisory routed through the existing advisory-router.

## Proposed Implementation

1. Author `.claude/skills/lo-opportunity-radar/SKILL.md` — the canonical skill with frontmatter (`name`, `description`) and a body presenting the five-pass review posture, with explicit guidance to keep findings compact and to route material findings via the existing advisory mechanism rather than mutating the backlog directly.
2. Generate the Codex parity adapter `.codex/skills/lo-opportunity-radar/SKILL.md` and refresh `.codex/skills/MANIFEST.json` via `scripts/generate_codex_skill_adapters.py`. The adapter and manifest are generator outputs and are listed in `target_paths`.
3. Register the skill in `config/agent-control/harness-capability-registry.toml` as a `loyal-opposition`-relevant skill.
4. Add `tests/skills/test_lo_opportunity_radar_skill.py` with the spec-derived tests below.

The skill is guidance content; it carries no executable code, creates no CLI
surface, and adds no hook. The deferred scanner, CLI, and hook surfaces
(advisory Findings 2-4) are NOT implemented in this slice.

## Files Expected To Change

- `.claude/skills/lo-opportunity-radar/SKILL.md` — new canonical skill.
- `.codex/skills/lo-opportunity-radar/SKILL.md` — generated Codex adapter.
- `.codex/skills/MANIFEST.json` — generator rewrites the adapter inventory.
- `config/agent-control/harness-capability-registry.toml` — new loyal-opposition skill entry.
- `tests/skills/test_lo_opportunity_radar_skill.py` — new spec-derived tests.

## Spec-Derived Test Plan

All tests are added to `tests/skills/test_lo_opportunity_radar_skill.py` and
derive from `SPEC-LO-OPPORTUNITY-RADAR-001`.

- T1 — the canonical skill `.claude/skills/lo-opportunity-radar/SKILL.md` exists and carries valid frontmatter (`name`, `description`). Covers the "delivered as a canonical skill" clause.
- T2 — the skill body presents all five passes (defect, token-savings, deterministic-service, surface-eligibility, routing). Covers the five-pass requirement clause.
- T3 — the Codex adapter `.codex/skills/lo-opportunity-radar/SKILL.md` exists, carries the generated-adapter marker, and is content-consistent with the canonical skill. Covers ADR-CODEX-HOOK-PARITY-FALLBACK-001.
- T4 — `config/agent-control/harness-capability-registry.toml` registers `lo-opportunity-radar` as a `loyal-opposition`-relevant skill. Covers the "biases Loyal Opposition" delivery clause.
- T5 — harness parity: the skill is present and consistent across the Claude and Codex capability surfaces (verified via the adapter-generation check). Covers ADR-CODEX-HOOK-PARITY-FALLBACK-001 and the cross-harness delivery requirement.

Verification commands:

```
python -m pytest tests/skills/test_lo_opportunity_radar_skill.py -q --tb=short
python scripts/generate_codex_skill_adapters.py --check --update-registry
python -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

1. `.claude/skills/lo-opportunity-radar/SKILL.md` exists with valid frontmatter and the five-pass posture body.
2. The Codex adapter and `.codex/skills/MANIFEST.json` are regenerated and consistent; `generate_codex_skill_adapters.py --check` is clean.
3. The skill is registered loyal-opposition-relevant in `harness-capability-registry.toml`.
4. All T1-T5 tests pass; `ruff check` and `ruff format --check` are clean.
5. No scanner, CLI, or hook surface is added (scope boundary respected).

## Recommended Commit Type

`feat:` — adds a new skill, a net-new capability surface, not a repair or a
maintenance-only change.

## Risk and Rollback

- Scope is a single new skill plus its generated adapter, registry entry, and
  tests. The skill is guidance content; it adds no executable path, so the
  blast radius is limited to LO review behavior.
- Rollback: remove the skill directory, the adapter, the registry entry, and
  the test file; re-run the adapter generator to restore `MANIFEST.json`.
- The deferred scanner / CLI / hook surfaces are explicitly excluded, so this
  slice carries none of the hook-token-bloat risk the source advisory flags.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-skill implementation. It is not a bulk backlog
operation. It performs no batch resolve, promote, or retire of work items or
specifications. References to "work item", "backlog", and "advisory" describe
the single work item WI-3324 and its governed bridge filing path only. The
applicable evidence pattern is a single-WI implementation proposal with
formal-artifact-approval discipline preserved unchanged; the inventory of
touched files is the five `target_paths` entries above.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this proposal content before
filing:

- `bridge_applicability_preflight.py` — `preflight_passed: true`, no missing required or advisory specs.
- `adr_dcl_clause_preflight.py` — exit 0; no blocking gaps.

## Review Questions for Loyal Opposition

1. Is the five-test plan sufficient coverage of `SPEC-LO-OPPORTUNITY-RADAR-001`, or should a test assert the routing-pass guidance explicitly names the advisory-router?
2. Should the skill body include a short worked example of a token-savings or deterministic-service finding, or stay posture-only for the first slice?
