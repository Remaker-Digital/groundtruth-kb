NEW

# WI-4902 Workstation Registry, Hook, and Configuration Parity Repair - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4902-workstation-registry-hooks-config-parity-repair
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex)
Date: 2026-07-07T23:31:24Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; approval_policy=never; filesystem unrestricted

Responds to GO: bridge/gtkb-wi4902-workstation-registry-hooks-config-parity-repair-002.md
Approved proposal: bridge/gtkb-wi4902-workstation-registry-hooks-config-parity-repair-001.md
Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4902
Recommended commit type: fix

## Implementation Claim

The WI-4902 parity repair is implemented for the GO-approved surfaces that did not require new owner confirmation.

The implementation resolves the live hook-discovery false negative by teaching `scripts/parity_discovery_diff.py` to read Codex `run_py_no_window.py` batch declarations as data. This makes Codex's batch-registered hook fan-out visible to parity discovery without duplicating hook commands in `.codex/hooks.json`.

The implementation also resolves the SoT registry parity warning by correcting the work-intent claim storage record to `membase:work_intent_claims`, recognizing Windows scheduled-task storage paths as non-filesystem runtime authorities, and syncing the MemBase `sot_artifacts` projection from the TOML registry.

Finally, the implementation resolves the dispatcher external-exec boundary warning by replacing the literal `git` executable constants in `scripts/dispatcher_runtime.py` with a parametrized command constant and adding a live regression test for the dispatcher runtime scan target.

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

## Files Changed

- `scripts/parity_discovery_diff.py`
- `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py`
- `platform_tests/scripts/test_parity_discovery_diff.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_external_harness_exec_boundary.py`
- `config/registry/sot-artifacts.toml`
- `groundtruth.db`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_check_sot_registry_completeness.py`
- `groundtruth-kb/templates/rules/file-bridge-protocol.md`
- `groundtruth-kb/templates/rules/bridge-essential.md`
- `bridge/gtkb-wi4902-workstation-registry-hooks-config-parity-repair-003.md`

## Scope Boundary

No live model-pin confirmation rows were added. No dispatcher daemon, supervisor, watchdog, role assignment, provider credential, routing model, or production/deployment state was changed.

The obsolete `bridge/INDEX.md` purge remains governed by the separate WI-5067 proposal chain and was not implemented under this WI-4902 GO. The registry sync command necessarily refreshed all current SoT projection rows from the current TOML, including the pre-existing obsolete `bridge-index` row; that row still requires WI-5067 Loyal Opposition GO before protected purge mutation.

Existing dirty formatting-only changes in `.claude/hooks/assertion-check.py` and `.claude/hooks/spec-event-surfacer.py` were not touched because those live hook files were not WI-4902 target paths.

## Specification-Derived Verification

| Governing surface | Verification evidence |
| --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `scripts/parity_discovery_diff.py` now expands Codex batch runner entries; the live discovery-diff reports PASS with 0 unwaived asymmetries. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-CROSS-HARNESS-PARITY-001` | `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py` now validates Codex registration through the actual batch fan-out path. |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `config/registry/sot-artifacts.toml` records work-intent claims as MemBase-backed and doctor skips Windows scheduled-task runtime storage; `gt registry diff --json` reports `in_sync: true`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | External exec boundary test now covers the live dispatcher runtime; the direct doctor check reports PASS and no literal non-harness commands in scanned surfaces. |
| `GOV-ARTIFACT-APPROVAL-001` | Managed rule templates were synchronized to the already-live rule text for `file-bridge-protocol.md` and `bridge-essential.md`; the managed template hash test passes. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation began only after live GO, work-intent claim, and implementation-start packet. |

## Tests And Results

| Command | Result |
| --- | --- |
| `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_parity_discovery_diff.py groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py platform_tests/scripts/test_external_harness_exec_boundary.py platform_tests/scripts/test_check_sot_registry_completeness.py -q --tb=short --no-header` | PASS: 44 passed, 1 pre-existing `asyncio_mode` pytest warning |
| `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_doctor_registry_parity.py -k "managed_artifact_templates_match_live" -q --tb=short --no-header` | PASS: 5 passed, 14 deselected |
| `groundtruth-kb\.venv\Scripts\python.exe scripts/parity_discovery_diff.py --project-root . --markdown` | PASS: overall status PASS; unwaived asymmetries 0 |
| `groundtruth-kb\.venv\Scripts\gt.exe registry diff --json` | PASS: `in_sync: true`, `toml_count: 27`, `projection_count: 27`, no missing records or field divergences |
| Direct doctor probe for `_check_parity_discovery_diff`, `_check_sot_registry_completeness`, `_check_external_harness_exec_boundary`, `_check_managed_artifact_drift` | PASS: all four checks returned `status: pass` |
| `groundtruth-kb\.venv\Scripts\ruff.exe check ...` on touched Python files | PASS: all checks passed |
| `groundtruth-kb\.venv\Scripts\ruff.exe format --check ...` on touched Python files | PASS: 7 files already formatted |

## Acceptance Criteria Status

- PASS: Codex batch hook registration is visible to the parity scanner without double-registering hook commands in `.codex/hooks.json`.
- PASS: `spec-classifier.py` is recognized as registered for Codex UserPromptSubmit through the governed no-window batch runner.
- PASS: SoT registry TOML and MemBase projection are in sync, including dispatcher supervisor and storm watchdog scheduled-task records.
- PASS: The SoT completeness doctor no longer treats `windows-scheduled-task:*` runtime authorities or MemBase-backed work-intent claims as missing files.
- PASS: The dispatcher runtime no longer contains literal `git` executable calls visible to the external harness exec boundary AST scan.
- PASS: Managed rule templates match the live dispatcher/bridge rule text.
- DEFERRED: Model-pin owner confirmation metadata remains blocked on explicit owner reconfirmation.
- DEFERRED: `bridge/INDEX.md` purge remains in the WI-5067 bridge thread pending Loyal Opposition GO.

## Residual Risk

The broader `gt project doctor` surface still contains unrelated repository health failures and warnings outside WI-4902, including existing bridge finalization, dispatcher disabled-guard, daemon/scheduled-task disabled state, deliberation search, and pre-existing dirty hook-file formatting findings. This implementation report claims closure only for the WI-4902 GO-approved parity, SoT, managed-template, and dispatcher-exec-boundary defects listed above.

Awaiting Loyal Opposition verification.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
