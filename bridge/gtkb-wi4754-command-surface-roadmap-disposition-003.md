NEW

# WI-4754 Implementation Report - Command-surface roadmap disposition

bridge_kind: implementation_report
Document: gtkb-wi4754-command-surface-roadmap-disposition
Version: 003
Responds to GO: bridge/gtkb-wi4754-command-surface-roadmap-disposition-002.md
Approved proposal: bridge/gtkb-wi4754-command-surface-roadmap-disposition-001.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; filesystem unrestricted; network enabled

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4754

Recommended commit type: docs

## Implementation Claim

WI-4754 now has a concrete, read-only disposition surface for the preserved CS-2+ command-surface roadmap:

- `config/agent-control/command-surface.toml` records a terminal disposition for CS-2, CS-2.5, CS-3, CS-4, CS-5+, CS-6, and CS-7.
- `scripts/command_surface_disposition.py` validates the disposition registry and renders markdown or JSON evidence.
- `platform_tests/scripts/test_command_surface_disposition.py` proves each preserved slice is explicit, surviving child work is PAUTH/bridge gated, and `::init` / `::wrap` remain covered/superseded rather than reimplemented through a generic dispatcher.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-2026-07-07.md` was generated as the compact disposition report. That dropbox path is git-ignored in this checkout, so the committed durable surface is the TOML registry plus generator/test; the generated report exists as local review evidence.

No live `::` command dispatcher, hook, dashboard UI, slash command, model invocation path, or runtime macro was implemented.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision was required for this disposition helper. The implementation preserves future owner-decision requirements for `CS-3` optional macros instead of treating them as approved runtime work.

## Prior Deliberations

- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` - preserved CS-2+ as reversible carry-forward rather than immediate implementation.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - active Phase 2 authorization context for WI-4754.
- `bridge/gtkb-command-surface-003.md` - corrected command-surface architecture and CS-2+ sequencing.
- `bridge/gtkb-command-surface-006.md` - terminal procedural closure of the architecture thread; future implementation requires separate slice proposals.
- `bridge/gtkb-wi4754-command-surface-roadmap-disposition-001.md` - approved WI-4754 proposal.
- `bridge/gtkb-wi4754-command-surface-roadmap-disposition-002.md` - Loyal Opposition GO.

## Implementation Authorization

- Work-intent claim: `gtkb-wi4754-command-surface-roadmap-disposition`, acquired by Prime Builder session `019f3170-d706-77d3-b3e1-be39d47f3eda` at `2026-07-07T19:03:24Z`.
- Applicability preflight passed with packet hash `sha256:f56c27147ab0b045890532b5fdf847b9c0426081bf8b6bac4b7bdeceea1e41fc`.
- Implementation-start packet succeeded with packet hash `sha256:302ddec6df404740ad1b270f1c553a3f371a0692d22d21acfa70273ff31dbdc7`.
- Target validation succeeded for:
  - `config/agent-control/command-surface.toml`
  - `scripts/command_surface_disposition.py`
  - `platform_tests/scripts/test_command_surface_disposition.py`
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-2026-07-07.md`
- Post-implementation bridge applicability preflight passed again with packet hash `sha256:f56c27147ab0b045890532b5fdf847b9c0426081bf8b6bac4b7bdeceea1e41fc`.
- Post-implementation ADR/DCL clause preflight passed: 5 clauses evaluated, 3 must-apply, 0 blocking gaps.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The TOML registry and generated markdown report record a disposition for every CS-2+ slice: defer, supersede, needs-owner-decision, or retire. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | The registry requires `harness_parity_disposition` on every slice, and tests assert every slice carries non-empty parity disposition text. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation used latest GO, live claim, implementation-start packet, target validation, and a post-implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest and ruff checks were executed and are recorded below. |

## Commands Run

- `python scripts/bridge_claim_cli.py claim gtkb-wi4754-command-surface-roadmap-disposition --ttl-seconds 7200`
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4754-command-surface-roadmap-disposition --expires-minutes 120`
- `python scripts/implementation_authorization.py validate --target config/agent-control/command-surface.toml`
- `python scripts/implementation_authorization.py validate --target scripts/command_surface_disposition.py`
- `python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_command_surface_disposition.py`
- `python scripts/implementation_authorization.py validate --target independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-2026-07-07.md`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\command_surface_disposition.py --project-root . --format markdown`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\command_surface_disposition.py --project-root . --output independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-2026-07-07.md`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_command_surface_disposition.py -q --tb=short --no-header`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/command_surface_disposition.py platform_tests/scripts/test_command_surface_disposition.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format scripts/command_surface_disposition.py platform_tests/scripts/test_command_surface_disposition.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/command_surface_disposition.py platform_tests/scripts/test_command_surface_disposition.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4754-command-surface-roadmap-disposition --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4754-command-surface-roadmap-disposition`

## Observed Results

- `scripts/command_surface_disposition.py --format markdown` rendered the expected report with CS-2, CS-2.5, CS-3, CS-4, CS-5+, CS-6, and CS-7.
- Focused pytest result: `8 passed, 1 warning`.
- Ruff check result: `All checks passed!`
- Ruff format check result after formatting: `2 files already formatted`.
- Generated report file exists at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-2026-07-07.md`.

## Files Changed

- `config/agent-control/command-surface.toml` - new disposition registry.
- `scripts/command_surface_disposition.py` - new read-only disposition renderer/validator.
- `platform_tests/scripts/test_command_surface_disposition.py` - new focused regression tests.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-2026-07-07.md` - generated local report evidence; git-ignored in this checkout.

The wider worktree contains many unrelated dirty files from other active bridge work. This report claims only the WI-4754 target paths above.

## Acceptance Criteria Status

- CS-2..CS-7 have explicit disposition rows and no ambiguous consideration-only residue.
- Implementable or surviving child slices name target paths, required specs, PAUTH needs, and bridge proposal needs.
- `::init` and `::wrap` are preserved as covered/superseded behavior in CS-3.
- No live `::` command dispatcher implementation was added.

## Risk And Rollback

Residual risk is low because this implementation is disposition/planning, not runtime command dispatch. The main review point is whether Loyal Opposition agrees with the specific dispositions. Any future runtime command-surface work remains explicitly unapproved until filed as a fresh bridge-gated child slice.

Rollback is a focused removal of the new TOML registry, generator, tests, and generated report evidence. Bridge files remain append-only.

## Loyal Opposition Asks

1. Verify that the implementation satisfies the approved disposition-only scope.
2. Confirm the report does not implement or authorize a live command dispatcher.
3. Return VERIFIED if satisfied, otherwise return NO-GO with specific disposition or evidence findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
