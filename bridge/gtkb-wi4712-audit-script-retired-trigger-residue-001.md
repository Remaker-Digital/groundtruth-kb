NEW

# WI-4712 Audit Script Retired-Trigger Residue Scope Repair

bridge_kind: prime_proposal
Document: gtkb-wi4712-audit-script-retired-trigger-residue
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07T20:52:21Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Codex desktop session; role override `::init gtkb pb`; WI-5033 dispatcher/bridge auto-build goal

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4712-BATCH-B-20260705
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4712

target_paths: ["scripts/windows_no_window_spawn_audit.py", "platform_tests/scripts/test_windows_no_window_spawn_audit.py", "platform_tests/scripts/test_retired_dispatch_substrate_residue.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

While implementing `bridge/gtkb-wi4712-retired-trigger-suite-disposition-002.md`, the retired-substrate guard exposed a real live-surface residue outside the approved WI-4712 target paths: `scripts/windows_no_window_spawn_audit.py` still lists the deleted retired trigger script in `RELEASE_RUNTIME_FILES`. The initial WI-4712 GO only authorizes `groundtruth.db`, `platform_tests/scripts/test_retired_dispatch_substrate_residue.py`, and `platform_tests/scripts/test_dispatcher_runtime.py`, so Prime Builder cannot repair the audit script under that thread without widening scope through a new bridge review.

This proposal authorizes the narrow source/test repair needed to make the existing WI-4712 disposition verifiable: remove the retired trigger script from the no-window audit release-runtime inventory, preserve the audit's no-visible-window contract, and keep the retired-substrate guard green without restoring any retired dispatch substrate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected script/test mutation requires an append-only proposal, Loyal Opposition GO, implementation-start authorization, and post-implementation verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the Batch B PAUTH authorizes WI-4712 dispatcher-modernization disposition work through the bridge path.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the PAUTH does not allow Prime Builder to bypass target-path review; this proposal exists because the new source file is outside the earlier GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal links the governance, dispatcher, and release-testing specifications that constrain the repair.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the header binds the proposal to the active PAUTH, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must carry forward spec-to-test mapping and observed command output.
- `GOV-STANDING-BACKLOG-001` — WI-4712 cannot be resolved while live release surfaces still contradict the retired-substrate disposition.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — current dispatch behavior must remain on the migrated dispatcher runtime rather than the retired trigger suite.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — automated bridge work remains centralized in the dispatcher daemon/runtime surfaces.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — dispatcher status and readiness audits must describe current supported dispatcher surfaces only.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the repair must not restore hook-driven or retired trigger automation.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Windows dispatcher release-runtime auditing must preserve no-visible-window guarantees while removing stale retired-substrate inventory.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — release readiness requires audit/test surfaces to match the supported operating state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the scope gap discovered during implementation is preserved as a governed follow-on proposal instead of an unreviewed workspace edit.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the proposal, GO, implementation evidence, and backlog disposition form one durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — previously bounded retired-trigger residue triggers follow-on work when current scans classify it as active release residue.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` — owner-approved Batch B continuation created the active WI-4712 project authorization.
- `bridge/gtkb-wi4712-retired-trigger-suite-disposition-001.md` — original WI-4712 current-state disposition proposal; target paths did not include the no-window audit script.
- `bridge/gtkb-wi4712-retired-trigger-suite-disposition-002.md` — Loyal Opposition GO that allowed implementation but required passing retired-substrate guard evidence.
- `bridge/gtkb-wi4943-retired-trigger-residue-cleanout-004.md` — VERIFIED retired-trigger residue cleanout; it explicitly treated later release-health classification of out-of-scope residue as a trigger for follow-on source-scope work.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` — VERIFIED no-window containment thread that established the audit script as an active release-readiness surface.
- `INTAKE-b8875adc` — OPS proposals need explicit trigger/evidence fields; this proposal is triggered by a concrete failed guard run and names the exact evidence path.
- `INTAKE-8301153b` — diagnostic audit references are references by default; here the audit reference is not merely historical because it lives in the release-runtime inventory set.

## Owner Decisions / Input

No new owner decision is required. The active Batch B owner approval (`DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`) already authorizes WI-4712 dispatcher-modernization disposition work through the bridge, and this proposal narrows the newly discovered scope gap to the audit script and focused tests needed to complete that disposition.

## Requirement Sufficiency

Existing requirements sufficient — the linked bridge authority, project-authorization, standing-backlog, dispatcher architecture, centralized dispatcher, no-window audit, and release-readiness requirements fully determine the intended behavior. No new requirement is needed to remove a deleted retired script from an active release-runtime inventory.

## Spec-Derived Verification Plan

Specification-to-evidence mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: after GO, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4712-audit-script-retired-trigger-residue`; expected result is an implementation-start packet scoped to the declared target paths.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and `ADR-DISPATCHER-ARCHITECTURE-001`: run `python -m pytest platform_tests/scripts/test_retired_dispatch_substrate_residue.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`; expected result is passing dispatcher runtime and retired-substrate guard coverage with no restoration of retired trigger files.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` and `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`: run `python -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py -q --tb=short` and `python scripts/windows_no_window_spawn_audit.py --json`; expected result is passing no-window audit tests and `release_ready: true` / `violation_count: 0`.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: rerun the WI-4712 backlog-resolution dry run after the guard is clean; expected result is a valid dry-run payload before any single-row terminal update is applied under the original WI-4712 disposition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report must carry forward the linked specs, the initial guard failure, the fix, and observed verification results.

Expected focused commands:

```text
python -m pytest platform_tests/scripts/test_retired_dispatch_substrate_residue.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_windows_no_window_spawn_audit.py -q --tb=short
python scripts/windows_no_window_spawn_audit.py --json
python -m ruff check scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_retired_dispatch_substrate_residue.py platform_tests/scripts/test_dispatcher_runtime.py
python -m ruff format --check scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_retired_dispatch_substrate_residue.py platform_tests/scripts/test_dispatcher_runtime.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4712-audit-script-retired-trigger-residue --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4712-audit-script-retired-trigger-residue
```

## Risk / Rollback

Primary risk is weakening the no-window audit by removing too much release-runtime coverage. Mitigation: delete only the nonexistent retired trigger script from `RELEASE_RUNTIME_FILES`, preserve current dispatcher/runtime launch audit coverage, and run the audit's focused tests plus JSON audit command. Rollback is a scoped revert of the source/test changes; rollback must not restore the deleted retired trigger script as a supported release runtime.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4712-audit-script-retired-trigger-residue`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — this removes stale release-runtime audit residue that currently blocks WI-4712 verification and release-readiness guard evidence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
