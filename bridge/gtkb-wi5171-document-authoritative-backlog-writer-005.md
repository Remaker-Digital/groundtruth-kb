REVISED

bridge_kind: prime_proposal
Document: gtkb-wi5171-document-authoritative-backlog-writer
Version: 005
Date: 2026-07-10 UTC
Responds to: bridge/gtkb-wi5171-document-authoritative-backlog-writer-004.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES
Work Item: WI-5171

target_paths: ["scripts/_kb_attribution.py", "scripts/session_self_initialization.py", "scripts/check_dispatched_role_bootstrap.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "platform_tests/scripts/test_kb_attribution.py", "platform_tests/scripts/test_kb_attribution_session_role.py", "platform_tests/scripts/test_cli_backlog_add.py", "platform_tests/scripts/test_cli_backlog_add_work_item.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_dispatched_role_bootstrap.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_backlog_update_source_spec_id.py", "platform_tests/cli/test_backlog_update_title_desc.py"]

implementation_scope: source and tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5171 Revision - complete role-authority matrix and update-writer fixtures

## Revision Claim

This revision responds to the post-implementation NO-GO at -004. It retains the approved document-authoritative worker-role design and widens only the missing test scope needed to bring canonical backlog update coverage green and demonstrate the complete five-assertion GOV v5 and ten-assertion DCL v6 outer matrix. No registry, dispatcher configuration, database, generated projection, formal artifact, or unrelated source path is added.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-ROLE-AUTHORITY-001 v5 and DCL-SESSION-ROLE-RESOLUTION-001 v6 already define the required behavior and exact outer assertion inventory. The -004 finding identifies a proposal scope gap, not an unmet product or governance requirement.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` v5 - requires all five explicit worker-envelope authority assertions to execute and pass.
- `DCL-SESSION-ROLE-RESOLUTION-001` v6 - requires each of `ROLE-DCL-A1` through `ROLE-DCL-A10` to execute without skipped, partial, metadata-only, or missing entries.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this fresh REVISED proposal and an independent GO before the additional protected test paths are edited.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - constrains the revision to the active WI-5171 PAUTH and its exact target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - links the two formal role-authority requirements to concrete scope and verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - makes the complete executable matrix and green canonical writer suite prerequisites for a renewed implementation report.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - carries the live PAUTH, project, WI, and inline JSON target set.
- `ADR-ENVELOPE-META-MODEL-001`, `DCL-ENVELOPE-META-MODEL-001`, and `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - retain the explicit envelope and dispatch-audit-only boundary.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires behavior to remain independent of direct dispatcher configuration reads.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all source and test work inside the GT-KB root.

## Prior Deliberations

- `DELIB-202666073` - owner authorization for the bounded WI-5171/WI-5086 document-authoritative worker-role correction.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-GOV-V5-FORMALIZATION-RESULT` - formal GOV v5 baseline and assertion inventory.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-DCL-V6-APPROVAL` - owner approval of the ten DCL v6 outer assertions.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-AUTHORITY-PAIR-RESULT` - paired worker-role authority result.
- `DELIB-20260710-GTKB-INTERACTIVE-KB-ATTRIBUTION-GLOBAL-MARKER-COLLISION` - reproduced shared-marker attribution defect.
- `gtkb-wi5171-document-authoritative-backlog-writer-004` - NO-GO requiring a scope amendment and complete matrix.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666073` and the formal GOV/DCL approval deliberations already authorize the document-authoritative worker-role correction. This revision only adds the omitted test coverage that the approved requirements and -004 already require.

## Findings Addressed

### F1 [P1] GO advisory verification condition is unmet

The implementation will replace the partial role-authority evidence with a deterministic complete matrix. The renewed implementation report must show passing executed evidence for GOV v5 assertions 1 through 5 and DCL v6 assertions `ROLE-DCL-A1` through `ROLE-DCL-A10`: explicit dispatch provenance, bootstrap without dispatcher configuration, audit-only mismatch behavior, role-before-activity ordering, invalid-evidence failure, interactive explicit-role preservation, subject-only resolver fallback classification, session-matched marker isolation, non-mutation/non-authority registry boundaries, and cross-harness/read-classification semantics. No assertion may remain skipped, partial, metadata-only, or unexecuted.

### F2 [P1] Canonical update-writer suite was outside the original scope

The revision adds exactly the three fixtures named by -004. Their temporary project/session setup will provide valid worker-role envelope provenance matching the invocation session where the test exercises normal update behavior, while preserving negative tests' intended authorization and GOV-15 assertions. The focused baseline on this tree is 29 passing and 9 failing; all nine current failures originate in the title/description fixture before its text-edit gate runs because its worker envelope session id is stale.

## Scope Changes

- Add `groundtruth-kb/tests/test_backlog_update_cli.py`.
- Add `groundtruth-kb/tests/test_backlog_update_source_spec_id.py`.
- Add `platform_tests/cli/test_backlog_update_title_desc.py`.
- Expand the already-authorized role-authority source and test paths only as needed to expose and execute the complete GOV v5 / DCL v6 matrix.
- Do not add database, registry projection, dispatcher-rule, formal-artifact, bridge-helper, or unrelated test paths.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| GOV v5 assertions 1-5 | Run the focused envelope, attribution, bootstrap, add, add-work-item, and update-writer tests and report a one-to-one assertion matrix. | Each GOV assertion executes and passes; none is partial. |
| DCL v6 `ROLE-DCL-A1` through `ROLE-DCL-A10` | Add deterministic tests or evaluator evidence across the listed target paths and report each ID separately. | Exactly ten executed passing entries, with no skipped, metadata-only, partial, or missing entry. |
| Canonical update writers | Run `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest groundtruth-kb\\tests\\test_backlog_update_cli.py groundtruth-kb\\tests\\test_backlog_update_source_spec_id.py platform_tests\\cli\\test_backlog_update_title_desc.py -q --tb=short --basetemp .harness-tmp\\wi5171-update-writers`. | All three fixtures pass with valid document-role provenance and retain their intended text-edit/GOV-15 assertions. |
| Worker-role cutover | Run `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests\\scripts\\test_kb_attribution.py platform_tests\\scripts\\test_kb_attribution_session_role.py platform_tests\\scripts\\test_session_envelope_runtime.py platform_tests\\scripts\\test_dispatched_role_bootstrap.py platform_tests\\scripts\\test_cli_backlog_add.py platform_tests\\scripts\\test_cli_backlog_add_work_item.py -q --tb=short --basetemp .harness-tmp\\wi5171-role-authority`. | Existing document-authority behavior remains green. |
| Proposal governance | Run applicability and clause preflights before filing; after GO, acquire implementation authorization for every source/test edit. | No missing required spec or authorization gap. |
| Scope hygiene | Inspect `git diff --cached --name-only` before commit. | Staged paths are a subset of the sixteen target paths; no database or generated registry projection is staged. |

## Acceptance Criteria

- The three canonical update-writer fixtures run green under valid per-session worker-role provenance.
- All five GOV v5 and all ten DCL v6 outer assertions have direct, executed, passing evidence.
- Shared markers, registry roles, dispatcher selection, harness identity, and model identity cannot substitute a document-derived behavior role.
- Missing, malformed, stale, conflicting, and session-mismatched evidence fails before writer mutation with recovery guidance.
- No acceptance criterion is reported as blocked, partial, skipped, metadata-only, or not yet complete.
- The final commit excludes `groundtruth.db` and generated `harness-state/harness-registry.json`.

## Risk And Rollback

The main risk is accidentally weakening legacy authorization tests while making their fixtures document-authoritative. Each fixture must preserve its original text-edit or GOV-15 claim and only add valid session evidence needed to reach that claim. Rollback is a scoped revert of the refreshed source/test paths; bridge and deliberation records remain append-only.

## Recommended Commit Type

`test` - completes required behavior coverage and test-fixture alignment for an already implemented role-authority cutover.
