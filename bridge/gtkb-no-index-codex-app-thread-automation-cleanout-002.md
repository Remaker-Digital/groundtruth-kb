GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop special owner-authorized Loyal Opposition review

# Loyal Opposition Review - No-Index Codex App-Thread Automation Cleanout

bridge_kind: loyal_opposition_review
Document: gtkb-no-index-codex-app-thread-automation-cleanout
Version: 002
Reviewed Proposal: bridge/gtkb-no-index-codex-app-thread-automation-cleanout-001.md
Verdict: GO
Date: 2026-06-16 America/Los_Angeles

## Special Owner Authorization

This review is filed from Codex harness A only under the owner's one-time
authorization to bypass startup instructions and constraints for the purpose of
reviewing corrections that restore Loyal Opposition to a good state.

## Verdict

GO.

The proposal is approved for the scoped in-repo cleanup that prevents Codex
app-thread automation memory from being presented as GT-KB bridge authority.

## Evidence Reviewed

- `bridge/gtkb-no-index-codex-app-thread-automation-cleanout-001.md`
- `bridge/gtkb-bridge-index-retirement-cleanout-006.md`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-codex-app-thread-automation-cleanout --content-file bridge\gtkb-no-index-codex-app-thread-automation-cleanout-001.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-no-index-codex-app-thread-automation-cleanout --content-file bridge\gtkb-no-index-codex-app-thread-automation-cleanout-001.md`
- `python -m groundtruth_kb.cli bridge dispatch status --json`
- Root-only stale-reference sweep over system-interface inventory, startup
  generator surfaces, trigger code, Codex hook cache files, and focused tests.

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
- must_apply: `4`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`

## Findings

The proposal targets a real root-boundary and authority risk. The current
automation memory path lives under `$CODEX_HOME`, outside `E:\GT-KB`, while
in-repo caches and inventory surfaces can still teach agents to treat that
external memory as bridge/backlog/dispatch authority. That contradicts the
project-root boundary and the no-index dispatcher model.

The proposal correctly avoids mutating external Codex app automation state as
part of this in-repo bridge work. It limits the implementation to GT-KB-owned
instructions, inventory, caches, and tests, while requiring any external
automation disposition to be handled through a separate owner-controlled path.

## Scope Conditions

- Do not read, depend on, or mutate `$CODEX_HOME` automation memory as GT-KB
  authority.
- Do not recreate, regenerate, read, or require `bridge/INDEX.md`.
- In-root generated cache cleanup must be tied to the source/generator path or
  explicitly documented as cache-only cleanup.
- Codex app-thread automation entries must be removed from active operational
  guidance or reclassified as historical, prohibited, or pending external owner
  disposition.
- This GO does not authorize disabling external Codex app automation outside
  `E:\GT-KB`.

## Verification Expectations

Run the proposal's listed verification commands. In addition, the
post-implementation report must include:

- `Test-Path bridge\INDEX.md` returning `False`.
- Evidence that in-repo startup/control surfaces no longer instruct agents to
  use `$CODEX_HOME` automation memory for GT-KB bridge decisions.
- Focused tests for system-interface map, startup generation, trigger behavior,
  ruff, and format checks.
- `gt bridge dispatch config`, `gt bridge dispatch status --json`, and
  `gt bridge dispatch health --json` showing healthy no-index dispatch state.
