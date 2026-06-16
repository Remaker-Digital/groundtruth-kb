GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop special owner-authorized Loyal Opposition review

# Loyal Opposition Review - No-Index LO Harness Prompt Cleanout

bridge_kind: loyal_opposition_review
Document: gtkb-no-index-lo-harness-prompt-cleanout
Version: 002
Reviewed Proposal: bridge/gtkb-no-index-lo-harness-prompt-cleanout-001.md
Verdict: GO
Date: 2026-06-16 America/Los_Angeles

## Special Owner Authorization

This review is filed from Codex harness A under the owner's one-time
authorization to review corrections that restore Loyal Opposition to a good
state despite the current Codex role/configuration problem.

## Verdict

GO.

The proposal is approved for the scoped cleanup of Ollama/OpenRouter Loyal
Opposition harness prompts and tests so they no longer instruct reviewers to
read, update, or depend on the retired `bridge/INDEX.md`.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: `[]`
- warnings.missing_parent_dirs: `[]`
- missing_advisory_specs:
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

The advisory misses do not block this scoped implementation approval.

## Clause Applicability

- Clauses evaluated: `5`
- must_apply: `4`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`

## Evidence Reviewed

- `bridge/gtkb-no-index-lo-harness-prompt-cleanout-001.md`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-lo-harness-prompt-cleanout --content-file bridge\gtkb-no-index-lo-harness-prompt-cleanout-001.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-no-index-lo-harness-prompt-cleanout --content-file bridge\gtkb-no-index-lo-harness-prompt-cleanout-001.md`
- Targeted `rg` over `scripts\ollama_harness.py`, `scripts\openrouter_harness.py`, and the focused harness tests.

## Findings

Live prompt text still tells both Ollama and OpenRouter to read
`bridge/INDEX.md` before reviewing and to update it after verdicts. The proposal
targets the correct active surfaces and keeps the slice separate from dispatcher
trigger and runtime-tooling cleanup.

## Scope Conditions

- Do not recreate, regenerate, read, or require `bridge/INDEX.md`.
- Harness prompts must direct reviewers to the full versioned bridge-file chain
  and `gt bridge dispatch config|status|health`.
- Guard text may mention the retired index only as a denied/prohibited target
  or historical artifact.
- Tests must assert no-index prompt behavior and keep any remaining index
  mention explicitly negative or historical.

## Verification Expectations

The post-implementation report must include the proposal's listed commands,
including `Test-Path bridge\INDEX.md` returning `False`, the targeted stale
prompt sweep, focused harness tests, ruff check, and ruff format check.
