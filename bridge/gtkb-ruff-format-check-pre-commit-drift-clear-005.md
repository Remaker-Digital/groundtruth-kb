REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T10-28-45Z-prime-builder-A-f21df9
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; workspace=E:/GT-KB
author_metadata_source: explicit bridge auto-dispatch metadata

# Revised Implementation Proposal - groundtruth-kb ruff drift target expansion

bridge_kind: prime_proposal
Document: gtkb-ruff-format-check-pre-commit-drift-clear
Version: 005 (REVISED)
Date: 2026-06-23 UTC
Responds to: bridge/gtkb-ruff-format-check-pre-commit-drift-clear-004.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3498

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "groundtruth-kb/templates/hooks/_delib_common.py", "groundtruth-kb/templates/hooks/gov09-capture.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/scripts/audit_adr_dcl_metadata.py", "groundtruth-kb/tests/framework/test_dispatch_state_recovery.py", "groundtruth-kb/tests/test_bridge_paths.py", "groundtruth-kb/tests/test_cli_projects.py", "groundtruth-kb/tests/test_doctor_canonical_terminology.py", "groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py", "groundtruth-kb/tests/test_full_tree_type_checks.py", "groundtruth-kb/tests/test_internal_helpers_type_checks.py", "groundtruth-kb/tests/test_public_api_type_checks.py", "groundtruth-kb/tests/test_slice_4_doctor_test_layout.py", "groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py", "groundtruth-kb/tests/test_spec_event_surfacer.py", "groundtruth-kb/tests/test_term_disambiguation.py", "platform_tests/scripts/test_groundtruth_kb_ruff_clean.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py", "groundtruth-kb/templates/hooks/assertion-check.py", "groundtruth-kb/templates/hooks/spec-classifier.py"]

## Revision Claim

This revision responds to the Loyal Opposition NO-GO at `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-004.md` by expanding the implementation target set for WI-3498 to include the three current whole-tree ruff-check drift files that blocked verification of the already-added guard:

- `groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py`
- `groundtruth-kb/templates/hooks/assertion-check.py`
- `groundtruth-kb/templates/hooks/spec-classifier.py`

No source or test implementation is performed in this REVISED filing. If Loyal Opposition records GO on this version, Prime Builder will run the implementation-start authorization packet for this same bridge thread, make only the approved ruff-clean edits needed for those three files and any affected approved target file, rerun the whole-tree ruff guard, and file a new post-implementation report.

## First-Line Role Eligibility Check

- Resolved durable harness identity: `codex` -> harness `A` from `harness-state/harness-identities.json`.
- Resolved role source: `groundtruth-kb/.venv/Scripts/gt.exe harness roles`.
- Resolved role: `prime-builder`.
- Live latest bridge status before drafting: `NO-GO` at `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-004.md`.
- Status authored here: `REVISED`.
- Eligibility result: Prime Builder is authorized to write a `REVISED` response to a latest `NO-GO` thread after acquiring a work-intent claim.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-ruff-format-check-pre-commit-drift-clear` acquired for session `2026-06-23T10-28-45Z-prime-builder-A-f21df9`.

## Requirement Sufficiency

Existing requirements sufficient. WI-3498 remains open and already covers clearing current `groundtruth-kb/` ruff drift and preserving the whole-tree ruff-check/format guard. The existing governing surface remains `groundtruth-kb/pyproject.toml` ruff configuration plus the bridge and project-authorization rules cited below. This revision does not add a new policy, new formal specification, new work item, or formal artifact mutation; it only brings the live failing files into the authorized implementation target set needed to satisfy the accepted whole-tree ruff-clean acceptance criteria.

## In-Root Placement Evidence

All active files and generated bridge artifacts for this revised proposal remain under the project root `E:\GT-KB`. The live bridge artifact will be `E:\GT-KB\bridge\gtkb-ruff-format-check-pre-commit-drift-clear-005.md`. All implementation target paths are relative in-root paths under `E:\GT-KB\groundtruth-kb\` or `E:\GT-KB\platform_tests\`. No path resolves outside `E:\GT-KB`, and no `applications/` or external Agent Red repository surface is in scope.

## NO-GO Findings Addressed

### P1 - Whole-tree ruff guard fails on three out-of-scope files

Accepted. The prior implementation report correctly avoided editing files outside the approved `target_paths`, but the whole-tree guard cannot verify while those files still fail `ruff check`. This revision adds the three files to `target_paths` and preserves the whole-tree verification requirement:

- `groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py`: `SIM102`.
- `groundtruth-kb/templates/hooks/assertion-check.py`: `E501`, `SIM105`.
- `groundtruth-kb/templates/hooks/spec-classifier.py`: `E501`, `I001`, `SIM110`.

The implementation remains mechanical ruff cleanup. It will not change `groundtruth-kb/pyproject.toml`, application code, formal specifications, or runtime behavior beyond lint-equivalent rewrites.

### P2 - Prior report missing explicit in-root evidence

Accepted. This revised proposal includes explicit `E:\GT-KB` root-boundary evidence in the `In-Root Placement Evidence` section. The follow-on post-implementation report will carry forward the same root-boundary statement so `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` can be mechanically satisfied.

## Scope Changes

The originally approved 18 target paths remain included for continuity and verification scope. The implementation delta requested by this REVISED filing is the addition of three source/template paths:

- `groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py`
- `groundtruth-kb/templates/hooks/assertion-check.py`
- `groundtruth-kb/templates/hooks/spec-classifier.py`

Out of scope:

- `groundtruth-kb/pyproject.toml` ruff configuration changes.
- Any formal GOV/ADR/DCL/SPEC mutation.
- Any path outside `E:\GT-KB`.
- Any `applications/` path or Agent Red lifecycle-independent repository path.
- Any non-ruff behavior refactor.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision preserves the numbered file-chain audit trail and waits for Loyal Opposition GO before any source/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED proposal cites the governing specifications, project authorization, ruff configuration, and spec-derived verification plan for the expanded target set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification remains whole-tree ruff check/format evidence plus execution of the guard test created under the prior GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the required `Project Authorization`, `Project`, and `Work Item` metadata lines are present above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths and the bridge artifact are explicitly declared under `E:\GT-KB`, satisfying the in-root placement clause.
- `GOV-STANDING-BACKLOG-001` - WI-3498 remains the MemBase backlog authority for this ruff-cleanup work and is still open.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the ruff drift is preserved as bridge/review evidence and resolved through governed artifacts instead of silent cleanup.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source, template, test, bridge, and verification artifacts stay traceable through the bridge file chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the regression guard intentionally surfaces future `groundtruth-kb/` ruff drift as a failing test.
- `SPEC-AUQ-POLICY-ENGINE-001` - precautionary seed only; this implementation does not modify AUQ policy engine behavior and requires no new owner decision in the auto-dispatch worker context.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - precautionary seed only; the touched hook-template files are lint/format cleanup targets, not hook-registration or Codex-parity changes.
- `groundtruth-kb/pyproject.toml` ruff configuration - operative lint/format configuration for the target tree: `line-length = 120`, lint selection `E`, `F`, `W`, `I`, `UP`, `B`, `SIM`, and formatter quote style.

## Prior Deliberations

- `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-001.md` - original approved implementation proposal.
- `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-002.md` - Loyal Opposition GO verdict for the original target set.
- `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-003.md` - post-implementation report showing the approved target set clean but whole-tree ruff check blocked by later out-of-scope drift.
- `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-004.md` - Loyal Opposition NO-GO requiring target-path expansion and explicit in-root evidence.
- `DELIB-20261528` - prior verified platform-tests ruff cleanup precedent.
- `DELIB-2697` - sibling ruff-cleanup verification precedent.
- `DELIB-20264740` - ruff format pre-file gate verification.
- `DELIB-20262374` - ruff pre-file-gate thread context.
- `DELIB-20265457` - owner authorization for the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane batch.
- `gtkb-rehearsal-package-ruff-clean-001` GO at `-002` - prior drift-prevention regression-guard precedent.
- `bridge/gtkb-wi3326-sessionstart-phantom-spec-citation-repoint-007.md` - historical resolved thread that touched the same three file paths for a different purpose; not an active duplicate of this ruff-drift cleanup.

## Owner Decisions / Input

- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane batch.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - active project-scoped implementation authorization. `gt projects show-authorization` reports scope as bounded authorization for 15 non-fast-lane open reliability WIs admitted per `DELIB-20265457`; implementation proposals and source/test implementation only; each WI still requires its own bridge proposal, Loyal Opposition GO, and verification.
- `WI-3498` - `gt backlog show WI-3498` reports stage `backlogged`, resolution status `open`, and status detail `Expanded with live ruff drift evidence from advisory triage; still open.`

No new owner decision is required for this REVISED filing because the three added files are needed to satisfy the already-approved WI-3498 whole-tree ruff-clean objective under the active non-fast-lane project authorization. If Loyal Opposition disagrees that the existing PAUTH covers the expanded target set, the correct bridge outcome is NO-GO with a specific authorization-freshness finding; this headless worker cannot ask the owner interactively.

## Proposed Implementation Plan

After GO:

1. Run `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-ruff-format-check-pre-commit-drift-clear` and verify the packet includes all 21 target paths.
2. Apply mechanical ruff cleanup for the three newly authorized files:
   - combine the nested `if` in `groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py` for `SIM102`;
   - wrap the two long lines and replace the JSON stdin consume block with `contextlib.suppress` in `groundtruth-kb/templates/hooks/assertion-check.py`;
   - format imports, wrap long strings/doc text, and replace the spec-pattern loop with `any(...)` in `groundtruth-kb/templates/hooks/spec-classifier.py`.
3. Run focused ruff check and ruff format-check on all 21 approved paths.
4. Run whole-tree `ruff check groundtruth-kb/` and `ruff format --check groundtruth-kb/`.
5. Run `pytest platform_tests/scripts/test_groundtruth_kb_ruff_clean.py`.
6. File a new post-implementation report carrying forward the explicit `E:\GT-KB` root-boundary evidence and observed command results.

## Specification-Derived Verification Plan

| Spec / governing surface | Derived verification | Acceptance assertion |
| --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` plus `groundtruth-kb/pyproject.toml` ruff lint config | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/` | Exits 0 after the three newly authorized files are cleaned. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` plus `groundtruth-kb/pyproject.toml` ruff format config | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/` | Exits 0 with all files already formatted. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_groundtruth_kb_ruff_clean.py -q --tb=short` | Both guard tests pass, proving future whole-tree ruff drift remains visible as a failing artifact. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | post-implementation report path review plus clause preflight | Report declares all active paths and the bridge artifact under `E:\GT-KB`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | implementation authorization begin plus bridge chain review | Source/template edits occur only after GO and only within the approved `target_paths`. |

## Acceptance Criteria

1. `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/` exits 0.
2. `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/` exits 0.
3. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_groundtruth_kb_ruff_clean.py -q --tb=short` exits 0.
4. Focused ruff check and format-check pass on all 21 approved target paths.
5. The implementation report includes explicit `E:\GT-KB` root-boundary evidence.
6. No `groundtruth-kb/pyproject.toml`, formal specification, or `applications/` file is modified.

## Risk And Rollback

- Risk: Mechanical lint cleanup in hook templates accidentally changes generated hook behavior. Mitigation: keep edits minimal, review the diff line-by-line, and run focused ruff plus the whole-tree guard.
- Risk: The PAUTH scope is judged insufficient for adding these three paths. Mitigation: this REVISED proposal makes the scope expansion explicit for Loyal Opposition review before any implementation begins.
- Risk: New unrelated ruff drift appears before implementation. Mitigation: the post-GO report must show current whole-tree command output; any additional out-of-scope drift remains a bridge blocker rather than silent cleanup.
- Rollback: if implemented and later rejected, revert the mechanical ruff changes to the three newly authorized files. Bridge files are append-only audit artifacts and are not rewritten or deleted.

## Commands Already Run For This Revision

- `groundtruth-kb/.venv/Scripts/gt.exe harness roles`
- `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status`
- `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health`
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-ruff-format-check-pre-commit-drift-clear --format json --preview-lines 260`
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/revise_bridge.py plan gtkb-ruff-format-check-pre-commit-drift-clear`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-ruff-format-check-pre-commit-drift-clear`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py groundtruth-kb/templates/hooks/assertion-check.py groundtruth-kb/templates/hooks/spec-classifier.py`
- `groundtruth-kb/.venv/Scripts/gt.exe projects show-authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21`
- `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-3498`

## Observed Results Before Filing

- Latest status remains `NO-GO` at `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-004.md`.
- Revision plan computed next live path as `bridge/gtkb-ruff-format-check-pre-commit-drift-clear-005.md`.
- Focused ruff check over the three newly requested files currently fails with the expected 9 findings:
  - `groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py`: `SIM102`.
  - `groundtruth-kb/templates/hooks/assertion-check.py`: `E501`, `SIM105`.
  - `groundtruth-kb/templates/hooks/spec-classifier.py`: `E501`, `I001`, `SIM110`.
- Project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` is active.
- WI-3498 is still open.

## Pre-Filing Preflight Subsection

Candidate content preflights were run before live filing with:

- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-ruff-format-check-pre-commit-drift-clear --content-file .tmp/bridge-revisions/gtkb-ruff-format-check-pre-commit-drift-clear-005.content.md --json`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ruff-format-check-pre-commit-drift-clear --content-file .tmp/bridge-revisions/gtkb-ruff-format-check-pre-commit-drift-clear-005.content.md`

Applicability Preflight:

- packet_hash: `sha256:86cb3bcb13b83a143413cbe407196da15d20e60d8b8a6e50424116c530fe0333`
- content_source: pending content file `.tmp/bridge-revisions/gtkb-ruff-format-check-pre-commit-drift-clear-005.content.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- warnings.missing_parent_dirs: `[]`

Clause Applicability:

- clauses_evaluated: 5
- must_apply: 4
- may_apply: 1
- evidence_gaps_in_must_apply_clauses: 0
- blocking_gaps_gate_failing: 0
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: evidence found `yes`
- `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`: evidence found `yes`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`: evidence found `yes`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`: evidence found `yes`
- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: may_apply

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
