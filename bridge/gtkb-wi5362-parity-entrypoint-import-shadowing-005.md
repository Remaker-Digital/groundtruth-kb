REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope
author_metadata_source: explicit_interactive_session_metadata

# WI-5362 Revised Proposal - Parity Entrypoint Import Shadowing Now Unblocked

bridge_kind: prime_proposal
Document: gtkb-wi5362-parity-entrypoint-import-shadowing
Version: 005
Responds to: bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-004.md
Approved proposal carried forward: bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-001.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5362-PARITY-ENTRYPOINT-IMPORT-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5362

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity_entrypoint_import.py"]

implementation_scope: source and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED proposal carries forward the original WI-5362 two-file implementation scope and verification plan after the sole blocker identified in the version-004 NO-GO reached terminal bridge state.

The version-004 NO-GO did not reject the substance of the WI-5362 repair. It held the proposal because `scripts/check_harness_parity.py` was then owned by the non-terminal peer thread `gtkb-wi5144-hp08-semantic-adapter-drift`. That peer thread is now latest `VERIFIED` at `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-010.md`, and `git status --short -- scripts/check_harness_parity.py` reports no dirty target entry.

No source, test, configuration, dispatcher, TAFE, runtime, credential, Git, release, deployment, or external-system mutation is made by this revision. It only asks Loyal Opposition to review the now-unblocked proposal state and, if satisfied, reissue a fresh GO that can pass current implementation-start shared-path checks.

## Requirement Sufficiency

Existing requirements remain sufficient. `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` still requires a deterministic executable Phase 1 parity evaluator, and the original proposal still confines the implementation to deterministic local generator loading for the parity checker. No new parity policy, harness lifecycle rule, activity-envelope rule, or owner decision is introduced by this unblock revision.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - governs the Phase 1 parity evaluator and requires deterministic, truthful cross-harness parity evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent review before either protected target is changed and preserves numbered bridge state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds implementation to the active WI-5362 project authorization and exact proposal paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires a live claim and implementation-start packet before protected mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - is the shared-path conflict rule that previously blocked WI-5362 and now must be rechecked after WI-5144 terminal closure.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the concrete specification links carried in this revised proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the machine-readable PAUTH, project, work-item, and target-path linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the later implementation report and verification verdict to map specifications to executed evidence.
- `GOV-STANDING-BACKLOG-001` - governs preservation of the reproduced defect as WI-5362 and linked TEST-11478 before implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the reproduced failure, authorization, proposal, test, and eventual verdict to remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - establishes the artifact-first workflow used to move this defect from evidence through independent verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the concrete parity failure to trigger a work item and governed implementation proposal rather than an untracked repair.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every source, test, draft, and bridge artifact used by this repair to remain within `E:\GT-KB`.
- `GOV-WORK-TREE-HYGIENE-001` - requires foreign hunks and target ownership to be preserved rather than absorbed silently.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers for newly reproduced fleet black-box defects while preserving every normal bridge, claim, start, verification, and commit gate.
- `bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-001.md` - original two-target proposal and verification plan.
- `bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-004.md` - current NO-GO, which held the thread solely on non-terminal WI-5144 shared-path ownership.
- `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-010.md` - terminal VERIFIED evidence for the prior shared-path owner.

## Owner Decisions / Input

No new owner decision is required. `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` remains the controlling authorization for this bounded defect carrier. This revision does not request a waiver of shared-path gates; it records that the previously named peer blocker is now terminal and requires normal claim/start validation after a fresh GO.

## Findings Addressed

### F1 - P1 - Shared-path ownership gate was open

Resolved for proposal activation. The version-004 NO-GO identified `gtkb-wi5144-hp08-semantic-adapter-drift` as latest `NO-GO` and therefore non-terminal. Current readback shows that thread is latest `VERIFIED` at `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-010.md`.

### F2 - P1 - `scripts/check_harness_parity.py` carried foreign dirty bytes

Resolved for proposal activation. Current path-scoped Git status reports no dirty entry for `scripts/check_harness_parity.py`. This does not by itself authorize WI-5362 implementation; it means a fresh GO may now be tested by a new work-intent claim and implementation-start packet without the recorded WI-5144 conflict.

## Scope Changes

None.

The authorized and requested target set remains exactly:

- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_check_harness_parity_entrypoint_import.py`

The implementation must still preserve the original proposal constraints:

- Do not depend on or create `scripts/__init__.py`.
- Do not catch broad `ImportError` in a way that masks genuine local generator failures.
- Do not change dispatcher, TAFE, runtime, harness eligibility, routing, leases, registry semantics, credentials, release, deployment, or Git history.
- Preserve existing parity evaluation, lifecycle filtering, waiver, and exit-status semantics.

## Pre-Filing Preflight Subsection

Candidate-content gates were run against this completed draft before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5362-parity-entrypoint-import-shadowing --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5362-parity-entrypoint-import-shadowing-005.md` returned `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5362-parity-entrypoint-import-shadowing --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5362-parity-entrypoint-import-shadowing-005.md` exited 0 with 4 must-apply clauses, zero evidence gaps in must-apply clauses, and zero blocking gaps.

The governed revision helper must rerun both gates before writing the live bridge file.

## Spec-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | After fresh GO, acquire a new `go_implementation` claim and run `scripts/implementation_authorization.py begin` for this exact bridge thread and session. | Claim/start succeeds only if no current peer implementation report owns either target path. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `python scripts/check_harness_parity.py --all --markdown` | Reaches the parity report with no external `win32.scripts` provenance and no import traceback; parity result remains data-driven. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, TEST-11478 | `python -m pytest platform_tests/scripts/test_check_harness_parity_entrypoint_import.py -q --tb=short` | Conflicting external `scripts` package cannot shadow local generators; local module provenance and genuine import-failure visibility pass. |
| Regression preservation | `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py -q --tb=short` | Existing checker and generator behavior remains green, except for separately adjudicated unrelated failures explicitly called out in the report. |
| Phase parity integration | `python scripts/harness_parity_phase2.py --project-root . --format markdown` and `python scripts/parity_discovery_diff.py --project-root . --markdown` | Later parity phases execute with their existing semantics after the Phase 1 import repair. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Applicability preflight, clause preflight, live claim, implementation-start packet, and exact target validation. | Every governance gate passes before protected mutation. |
| Source quality | Ruff check/format on both target paths plus `git diff --check -- <two targets>`. | No lint, format, or whitespace errors. |

## Risk And Rollback

Risk is low because this revision does not change implementation scope and the previously blocking peer thread is terminal. The remaining implementation risk is the original import-precedence change: local generator provenance must be deterministic without swallowing genuine generator import failures.

Rollback for any later implementation remains a focused revert of the checker bootstrap and the new focused test after normal bridge authorization. No registry, generated adapter, dispatcher, TAFE, runtime, credential, release, deployment, or Git-history rollback is involved.

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
