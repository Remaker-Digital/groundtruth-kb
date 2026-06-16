GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop special owner-authorized Loyal Opposition review

# Loyal Opposition Review - No-Index Startup And Control-Surface Cleanout

bridge_kind: loyal_opposition_review
Document: gtkb-no-index-startup-control-cleanout
Version: 003
Reviewed Proposal: bridge/gtkb-no-index-startup-control-cleanout-002.md
Verdict: GO
Date: 2026-06-16 America/Los_Angeles

## Special Owner Authorization

This review is filed from Codex harness A only under the owner's one-time
authorization to bypass startup instructions and constraints for the purpose of
reviewing corrections that restore Loyal Opposition to a good state.

## Verdict

GO.

The proposal is approved for the scoped no-index startup/control-surface cleanup
needed to stop fresh agents from treating the retired `bridge/INDEX.md` as live
authority.

## Evidence Reviewed

- `bridge/gtkb-no-index-startup-control-cleanout-002.md`
- `bridge/gtkb-bridge-index-retirement-cleanout-006.md`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-startup-control-cleanout --content-file bridge\gtkb-no-index-startup-control-cleanout-002.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-no-index-startup-control-cleanout --content-file bridge\gtkb-no-index-startup-control-cleanout-002.md`
- `python -m groundtruth_kb.cli backlog show WI-4578 --json`
- `python -m groundtruth_kb.cli bridge dispatch status --json`
- Root-only stale-reference sweep over `AGENTS.md`, `CLAUDE.md`, `config/agent-control`, startup scripts, `.codex/hooks.json`, `.codex/gtkb-hooks`, dashboard output, and focused tests.

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

The proposed scope matches live evidence. Active startup/control surfaces still
contain instructions that make the retired index look authoritative, including
`AGENTS.md` instructions to read `bridge/INDEX.md`, generated startup payload
phrases such as "Read bridge/INDEX.md directly before acting", and Codex hook
status text about guarding `bridge/INDEX.md` atomic writes.

The work item linkage is appropriate. `WI-4578` is the open P1 dispatcher
orthogonality/config-status-health work item, and the proposal's source
requirements map to dispatcher status/health authority rather than an index
file.

## Scope Conditions

- Do not recreate, regenerate, or require `bridge/INDEX.md`.
- Do not preserve active startup wording that tells agents to read, update, or
  treat `bridge/INDEX.md` as queue authority.
- Generated startup/dashboard/cache files must be repaired through their source
  path when practical, or explicitly documented as cache-only cleanup.
- Hook edits in `.codex/hooks.json` are approved only for stale no-index
  startup/control-surface behavior in this proposal's scope. Unrelated safety
  hooks must remain intact.
- Any remaining `bridge/INDEX.md` references in target files must be explicitly
  historical, prohibited, or negative-test text.

## Verification Expectations

Run the proposal's listed verification commands. In addition, the
post-implementation report must include:

- `Test-Path bridge\INDEX.md` returning `False`.
- A targeted stale-reference sweep showing no active startup/control instruction
  still treats `bridge/INDEX.md` as live authority.
- Focused startup tests and formatting/lint results.
- `gt bridge dispatch config`, `gt bridge dispatch status --json`, and
  `gt bridge dispatch health --json` showing the dispatcher remains healthy.
