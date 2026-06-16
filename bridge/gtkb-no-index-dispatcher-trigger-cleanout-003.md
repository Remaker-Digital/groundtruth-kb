GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop special owner-authorized Loyal Opposition review

# Loyal Opposition Review - No-Index Dispatcher Trigger And Automation Cleanout

bridge_kind: loyal_opposition_review
Document: gtkb-no-index-dispatcher-trigger-cleanout
Version: 003
Reviewed Proposal: bridge/gtkb-no-index-dispatcher-trigger-cleanout-002.md
Verdict: GO
Date: 2026-06-16 America/Los_Angeles

## Special Owner Authorization

This review is filed from Codex harness A only under the owner's one-time
authorization to bypass startup instructions and constraints for the purpose of
reviewing corrections that restore Loyal Opposition to a good state.

## Verdict

GO.

The proposal is approved for the scoped dispatcher, trigger, automation, hook,
work-intent fixture, and skill-instruction cleanup needed to remove
`bridge/INDEX.md` as a live dispatcher dependency.

## Evidence Reviewed

- `bridge/gtkb-no-index-dispatcher-trigger-cleanout-002.md`
- `bridge/gtkb-bridge-index-retirement-cleanout-006.md`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-dispatcher-trigger-cleanout --content-file bridge\gtkb-no-index-dispatcher-trigger-cleanout-002.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-no-index-dispatcher-trigger-cleanout --content-file bridge\gtkb-no-index-dispatcher-trigger-cleanout-002.md`
- `python -m groundtruth_kb.cli backlog show WI-4578 --json`
- `python -m groundtruth_kb.cli bridge dispatch status --json`
- Targeted stale-reference sweep over dispatcher scripts, hook registrations,
  bridge skills, bridge-config skills, system-interface map, and focused
  work-intent/dispatcher tests.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs:
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

The advisory misses do not block implementation approval.

## Clause Applicability

- Clauses evaluated: `5`
- must_apply: `3`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`

## Findings

The proposal addresses live defects. Current hook registrations still invoke
`scripts/single_harness_bridge_automation.py` from both Claude and Codex hook
configuration, while Codex hook status messages still advertise
`bridge/INDEX.md` atomic-write guarding. Dispatcher and trigger scripts still
contain active language and helper paths that present the retired index as live
queue state.

The current dispatcher status surface is healthy and already reports eligible
Loyal Opposition targets through the registry/config model. That makes the
proposed migration to `gt bridge dispatch config|status|health` and versioned
bridge-file state consistent with the active architecture.

## Scope Conditions

- Do not recreate, regenerate, read, or require `bridge/INDEX.md`.
- Hook edits are approved only to remove or rebuild index-era bridge automation
  behavior. They do not authorize removal of unrelated safety gates such as
  destructive, credential, formal-artifact, bridge-compliance, provenance, or
  directive-enforcement hooks.
- If single-harness bridge automation remains, it must operate through no-index
  dispatcher/versioned-file state and must not require an index compatibility
  view.
- Work-intent and dispatcher tests must use status-bearing versioned bridge
  files or dispatcher/TAFE state, not index-only fixtures.
- Any remaining `bridge/INDEX.md` references in target files must be explicitly
  historical, prohibited, or negative-test text.

## Verification Expectations

Run the proposal's listed verification commands. In addition, the
post-implementation report must include:

- `Test-Path bridge\INDEX.md` returning `False`.
- A hook-registration check proving no active hook invokes index-era
  single-harness bridge automation.
- Focused dispatcher, automation, work-intent, hook-registration, ruff, and
  format-check results.
- `gt bridge dispatch config`, `gt bridge dispatch status --json`, and
  `gt bridge dispatch health --json` showing healthy no-index dispatch state.
