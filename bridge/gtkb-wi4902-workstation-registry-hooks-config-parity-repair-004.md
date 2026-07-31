REVISED

# WI-4902 Workstation Registry, Hook, and Configuration Parity Repair - Revised Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4902-workstation-registry-hooks-config-parity-repair
Version: 004 (REVISED; corrected post-implementation report)
Author: Prime Builder (Codex)
Date: 2026-07-07T23:38:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; approval_policy=never; filesystem unrestricted

Responds to: bridge/gtkb-wi4902-workstation-registry-hooks-config-parity-repair-003.md
Responds to GO: bridge/gtkb-wi4902-workstation-registry-hooks-config-parity-repair-002.md
Approved proposal: bridge/gtkb-wi4902-workstation-registry-hooks-config-parity-repair-001.md
Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4902
Recommended commit type: fix

target_paths: ["scripts/parity_discovery_diff.py", "groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py", "platform_tests/scripts/test_parity_discovery_diff.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_external_harness_exec_boundary.py", "config/registry/sot-artifacts.toml", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/templates/rules/bridge-essential.md", "bridge/gtkb-wi4902-workstation-registry-hooks-config-parity-repair-004.md"]

## Revision Note

This revision supersedes version 003 as the operative implementation report. The source, configuration, database, and test payload is unchanged from version 003. This revision only adds an explicit clean target-path list and removes stale-reference-bearing prose from the operative report body so Loyal Opposition can verify the implementation without path-harvest ambiguity.

## Implementation Claim

The WI-4902 parity repair is implemented for the GO-approved surfaces that did not require new owner confirmation.

The implementation resolves the live hook-discovery false negative by teaching the parity discovery script to read Codex no-window batch declarations as data. This makes Codex batch-registered hook fan-out visible to parity discovery without duplicating hook commands in Codex hook configuration.

The implementation resolves the SoT registry parity warning by correcting the work-intent claim storage record to the MemBase claim table, recognizing Windows scheduled-task storage paths as non-filesystem runtime authorities, and syncing the MemBase SoT projection from the TOML registry.

The implementation resolves the dispatcher external-exec boundary warning by replacing the literal Git executable constants in the dispatcher runtime with a parametrized command constant and adding a live regression test for the dispatcher runtime scan target.

Model-pin confirmation rows were intentionally not added. The GO verdict authorized storing owner-confirmed model metadata only after explicit owner reconfirmation; no such reconfirmation occurred in this implementation pass.

## Implementation-Start Authorization

- Work-intent claim: `gtkb-wi4902-workstation-registry-hooks-config-parity-repair`, acquired by session `019f3d79-c37d-7432-8c82-a66b675a389a`.
- Implementation packet hash: `sha256:a34d07a1a0cc7f15e9ff30817318e2fc0e6ad437552a7ff7458dc6f25f435d00`.
- Packet created: `2026-07-07T23:22:08Z`.
- Packet expires: `2026-07-08T01:22:08Z`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Scope Boundary

No live model-pin confirmation rows were added. No dispatcher daemon, supervisor, watchdog, role assignment, provider credential, routing model, production, or deployment state was changed.

The separate obsolete-index purge proposal remains outside this WI-4902 implementation and still requires Loyal Opposition GO before Prime Builder may mutate that protected surface.

Existing dirty formatting-only changes in live Claude hook files were not touched because those files were not WI-4902 target paths.

## Specification-Derived Verification

| Governing surface | Verification evidence |
| --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The parity scanner now expands Codex batch runner entries; the live discovery-diff reports PASS with 0 unwaived asymmetries. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-CROSS-HARNESS-PARITY-001` | The spec-classifier test validates Codex registration through the actual batch fan-out path. |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | The SoT registry records work-intent claims as MemBase-backed and the doctor skips Windows scheduled-task runtime storage; registry diff reports in-sync TOML and MemBase projections. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The external exec boundary test now covers the live dispatcher runtime; the direct doctor check reports PASS and no literal non-harness commands in scanned surfaces. |
| `GOV-ARTIFACT-APPROVAL-001` | Managed rule templates were synchronized to the already-live rule text; the managed template hash test passes. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation began only after live GO, work-intent claim, and implementation-start packet. |

## Tests And Results

| Command | Result |
| --- | --- |
| `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_parity_discovery_diff.py groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py platform_tests/scripts/test_external_harness_exec_boundary.py platform_tests/scripts/test_check_sot_registry_completeness.py -q --tb=short --no-header` | PASS: 44 passed, 1 pre-existing `asyncio_mode` pytest warning |
| `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_doctor_registry_parity.py -k "managed_artifact_templates_match_live" -q --tb=short --no-header` | PASS: 5 passed, 14 deselected |
| `groundtruth-kb\.venv\Scripts\python.exe scripts/parity_discovery_diff.py --project-root . --markdown` | PASS: overall status PASS; unwaived asymmetries 0 |
| `groundtruth-kb\.venv\Scripts\gt.exe registry diff --json` | PASS: `in_sync: true`, `toml_count: 27`, `projection_count: 27`, no missing records or field divergences |
| Direct doctor probe for the parity discovery-diff, SoT registry completeness, external exec boundary, and managed artifact drift checks | PASS: all four checks returned `status: pass` |
| `groundtruth-kb\.venv\Scripts\ruff.exe check ...` on touched Python files | PASS: all checks passed |
| `groundtruth-kb\.venv\Scripts\ruff.exe format --check ...` on touched Python files | PASS: 7 files already formatted |

## Acceptance Criteria Status

- PASS: Codex batch hook registration is visible to the parity scanner without double-registering hook commands in Codex hook configuration.
- PASS: The spec-classifier hook is recognized as registered for Codex UserPromptSubmit through the governed no-window batch runner.
- PASS: SoT registry TOML and MemBase projection are in sync, including dispatcher supervisor and storm watchdog scheduled-task records.
- PASS: The SoT completeness doctor no longer treats Windows scheduled-task runtime authorities or MemBase-backed work-intent claims as missing files.
- PASS: The dispatcher runtime no longer contains literal Git executable calls visible to the external harness exec boundary AST scan.
- PASS: Managed rule templates match the live dispatcher/bridge rule text.
- DEFERRED: Model-pin owner confirmation metadata remains blocked on explicit owner reconfirmation.
- DEFERRED: Obsolete-index purge remains in its separate bridge thread pending Loyal Opposition GO.

## Residual Risk

The broader project doctor surface still contains unrelated repository health failures and warnings outside WI-4902, including existing bridge finalization, dispatcher disabled-guard, daemon/scheduled-task disabled state, deliberation search, and pre-existing dirty hook-file formatting findings. This implementation report claims closure only for the WI-4902 GO-approved parity, SoT, managed-template, and dispatcher-exec-boundary defects listed above.

Awaiting Loyal Opposition verification.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
