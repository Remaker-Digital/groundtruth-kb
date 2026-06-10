REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-03-prime-builder
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Prime Builder

# Revised Implementation Proposal - Worker Delivery Regression Coverage Slice 4

bridge_kind: prime_proposal
Document: gtkb-prime-worker-delivery-regression-slice-4
Version: 005
Status: REVISED
Author: Prime Builder (Codex harness A)
Date: 2026-06-03 UTC
Responds to: `bridge/gtkb-prime-worker-delivery-regression-slice-4-004.md`

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3398
target_paths: ["platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/hooks/test_owner_decision_tracker.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py"]

## Revision Claim

This revision converts Slice 4 back into a normal implementation-ready test proposal. It addresses the `-004` NO-GO findings without requesting deferral or any non-standard bridge disposition.

The proposal remains test-only. It does not change production dispatch code, hook registrations, MemBase rows, project records, or bridge automation behavior. It adds and tightens regression coverage for the already-implemented Prime-worker delivery chain.

## Findings Addressed

### F1 - Requested disposition did not match bridge lifecycle semantics

Accepted and corrected. This revision requests a normal Loyal Opposition `GO` for bounded test implementation. It no longer asks for `GO` or `VERIFIED` on a deferral note, and it does not ask Loyal Opposition to acknowledge a non-actionable parking state.

### F2 - Dependency evidence was stale against live bridge state

Accepted and corrected with current dependency evidence.

Live `bridge/INDEX.md` currently contains the active Slice 4 thread but no longer contains `Document:` entries for the three sibling dependency threads. A live read plus `show_thread_bridge.py` reported empty index chains for the sibling threads and unindexed on-disk version files. The read-only reconciliation audit classifies this family as `bridge_index_drift` / `versioned_bridge_file_unindexed` with severity `P3` and recommended action "Decide whether this is a parked draft or needs a governed INDEX entry." That broader INDEX de-index gap is already represented by WI-3491 and the active `PAUTH-WI-3491-INDEX-DEINDEX-RECONCILE-001`.

The dependency contracts themselves are now complete in the versioned bridge artifacts:

- Slice 1 permission profile: `bridge/gtkb-prime-worker-permission-profile-slice-1-006.md` is `VERIFIED`.
- Slice 2 worker-context AUQ behavior: `bridge/gtkb-prime-worker-context-aware-auq-slice-2-012.md` is `VERIFIED`.
- Slice 3 post-Stop dispatch reconciliation: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-012.md` is `VERIFIED`.

This proposal does not mutate `bridge/INDEX.md` to repair the sibling de-index condition because that would be a separate WI-3491 implementation. For Slice 4 readiness, the operative point is that no sibling thread is currently latest `NO-GO`, and the exact behavior contracts to test are present in the terminal versioned artifacts listed above.

### F3 - Future target-path example was malformed for the parser

Accepted and corrected. This revision has exactly one top-level parser-supported `target_paths` metadata line, immediately under the project-linkage metadata. It is valid JSON and names only concrete implementation paths. No prose example in this proposal starts with the literal `target_paths:` prefix.

### Prior NO-GO - Integration proof must be required for the central claim

Accepted and carried forward from `-002`. The real spawned-worker lane is required on hosts where the Claude harness executable is available. CI portability may skip that test when the executable is absent, but a skipped integration test is not closure evidence for this slice on a harness host where `claude` is present.

## Dependency State

The current dependency state is:

| Dependency | Evidence | Slice 4 interpretation |
|---|---|---|
| Slice 1 permission flags | `bridge/gtkb-prime-worker-permission-profile-slice-1-006.md` starts with `VERIFIED`. | Contract closed; Slice 4 may assert command permission profile behavior. |
| Slice 2 worker-context AUQ handling | `bridge/gtkb-prime-worker-context-aware-auq-slice-2-012.md` starts with `VERIFIED`. | Contract closed; Slice 4 may assert owner-context and worker-context Stop-hook behavior. |
| Slice 3 post-Stop reconciliation order | `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-012.md` starts with `VERIFIED`. | Contract closed; Slice 4 may assert Stop reconciliation and output contract behavior. |
| Active Slice 4 queue state | `bridge/INDEX.md` lists latest `NO-GO: bridge/gtkb-prime-worker-delivery-regression-slice-4-004.md`. | This REVISED is the next normal proposal version. |

## Scope

In scope:

1. Tighten or add Slice 1 command-shape tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
2. Tighten or add Slice 2 worker-context tests in `platform_tests/hooks/test_owner_decision_tracker.py`.
3. Tighten or add Slice 3 Stop-reconciliation tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
4. Add `platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py` for the real spawned-worker delivery integration lane.

Out of scope:

- No production source change in `scripts/cross_harness_bridge_trigger.py`.
- No hook registration change in `.codex/hooks.json` or `.claude/settings.json`.
- No owner-decision-tracker production hook change.
- No interval poller, scheduled poller, retired smart poller, or per-thread lock restoration.
- No `bridge/INDEX.md` de-index repair; that remains WI-3491.
- No MemBase mutation, project mutation, deployment, or git push.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the active Slice 4 state comes from live `bridge/INDEX.md`; the revision will be filed as the next bridge artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation proposal cites all governing specs and rules that constrain the test slice.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal includes `Project Authorization`, `Project`, and `Work Item` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this slice is the regression-verification layer derived from the Slice 1, Slice 2, and Slice 3 behavior contracts.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-3398 is an active reliability-fixes project member and the standing PAUTH covers source/test/hook reliability fixes by active membership.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - spawned-worker prompts must preserve canonical init-keyword first-line behavior.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - dispatch prompt assertions remain consistent across worker contexts.
- `SPEC-AUQ-POLICY-ENGINE-001` - Slice 2 worker-context coverage exercises deterministic owner-decision policy behavior.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - worker-context detection remains deterministic environment handling, not LLM classification.
- `.claude/rules/bridge-essential.md` - active-session suppression and bridge dispatch enablement contracts constrain the Stop-reconciliation and worker-dispatch tests.
- `.claude/rules/file-bridge-protocol.md` - live bridge lifecycle, proposal metadata, and spec-derived verification gates.
- `.claude/rules/codex-review-gate.md` - no implementation without Loyal Opposition review and GO.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under `E:\GT-KB`; no application subtree or external checkout is touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - behavior contracts, tests, and bridge evidence remain linked.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the regression proof is preserved as durable test and bridge artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the proposal lifecycle advances via normal `REVISED` to `GO` and post-implementation verification.

## Prior Deliberations

- `DELIB-2457` - original Slice 4 NO-GO at `bridge/gtkb-prime-worker-delivery-regression-slice-4-002.md`; required dependency closure, parser-supported target paths, and a real integration lane.
- `DELIB-2456` - Slice 4 deferral NO-GO at `bridge/gtkb-prime-worker-delivery-regression-slice-4-004.md`; rejected deferral disposition and required a future implementation-ready revision.
- `DELIB-2458` - Slice 3 GO evidence for post-Stop reconciliation hook order.
- `bridge/gtkb-prime-worker-permission-profile-slice-1-006.md` - terminal verification of Slice 1 permission-profile behavior.
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-012.md` - terminal verification of Slice 2 worker-context AUQ behavior.
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-012.md` - terminal verification of Slice 3 Stop-reconciliation behavior.
- `WI-3491` - adjacent bridge INDEX de-index reconciliation work item for missing terminal sibling entries; referenced only to disclose current INDEX evidence limits, not to broaden this Slice 4 scope.

No prior deliberation rejects the Slice 4 testing goal after dependencies are closed. The prior NO-GOs rejected premature or malformed proposal states.

## Owner Decisions / Input

No new owner input is required for this proposal. The standing reliability fast-lane project authorization is active:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- owner decision deliberation: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`
- project: `PROJECT-GTKB-RELIABILITY-FIXES`
- WI-3398 active membership confirmed by `gt backlog show WI-3398 --json`

This proposal does not request deployment, destructive cleanup, formal artifact mutation, or any action outside the active PAUTH scope.

## Requirement Sufficiency

Existing requirements sufficient.

The required behavior is already specified by the approved and verified sibling slices, the bridge dispatch contracts in `.claude/rules/bridge-essential.md`, the AUQ deterministic-policy specs, the init-keyword specs, and the mandatory spec-derived verification gate. No new or revised requirement is needed before adding this test-only regression coverage.

## Implementation Plan

1. Add or tighten command-shape tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`:
   - Claude worker command includes `--permission-mode acceptEdits`.
   - Claude allowed-tools value includes `Read`, `Edit`, `Write`, `Glob`, `Grep`, `Bash`, `TodoWrite`, and `NotebookEdit`.
   - Claude allowed-tools value excludes `AskUserQuestion`, `WebFetch`, `WebSearch`, and any `mcp__` tool.
   - Codex command remains unchanged and receives no Claude permission flags.
   - Prompt first line remains canonical `::init gtkb <mode>`.
2. Add or tighten worker-context tests in `platform_tests/hooks/test_owner_decision_tracker.py`:
   - Owner context still emits the interactive block decision for prose decision asks without AUQ.
   - Worker context writes the owner-decision-requested artifact and avoids the interactive block signal.
   - Worker context still appends durable pending-decision evidence.
   - Test helpers scrub inherited worker markers unless a test explicitly supplies them.
3. Add or tighten Stop-reconciliation tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`:
   - Codex Stop hook registration clears session lock before bridge reconciliation.
   - Claude Stop hook registration clears session lock before bridge reconciliation.
   - Stop reconciliation sees the lock as inactive after session-stop.
   - Existing Stop output contract remains stable.
4. Add `platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py`:
   - Mark the real spawned-worker test slow and host-dependent.
   - Skip only when the required `claude` executable is absent.
   - When present, spawn a real worker against a fixture project and assert an authorized file is edited without permission-denial output.
   - Ensure cleanup terminates any spawned subprocess on timeout.

## Specification-Derived Verification Plan

| Requirement / contract | Verification evidence |
|---|---|
| Slice 1 permission profile remains enforced | Focused command-shape tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`. |
| Slice 2 worker-context AUQ behavior remains enforced | Focused Stop-hook tests in `platform_tests/hooks/test_owner_decision_tracker.py`. |
| Slice 3 Stop-reconciliation ordering remains enforced | Focused hook-order and lock-lifecycle tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`. |
| Real spawned Prime worker can edit an authorized path | `platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py` on a host with `claude` available. |
| CI portability is preserved | Same integration test skips only when the harness executable is unavailable; skip is not closure evidence for local host verification. |

Required post-implementation commands:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\hooks\test_owner_decision_tracker.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger_worker_delivery.py -q --tb=short -m slow
groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\hooks\test_owner_decision_tracker.py platform_tests\scripts\test_cross_harness_bridge_trigger_worker_delivery.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\hooks\test_owner_decision_tracker.py platform_tests\scripts\test_cross_harness_bridge_trigger_worker_delivery.py
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-delivery-regression-slice-4
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-delivery-regression-slice-4
git diff --check -- platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\hooks\test_owner_decision_tracker.py platform_tests\scripts\test_cross_harness_bridge_trigger_worker_delivery.py bridge\gtkb-prime-worker-delivery-regression-slice-4-005.md bridge\INDEX.md
```

The implementation report must state whether the real spawned-worker integration test passed, skipped because `claude` was absent, or failed. If it skips on a host where `claude` is expected to be available, the report must not claim the worker-delivery gap is closed without an explicit owner/governance waiver.

## Acceptance Criteria

1. The implementation-start gate can parse the proposal metadata and produce a packet after LO `GO`.
2. Unit regression coverage exists for Slice 1, Slice 2, and Slice 3 behavior contracts.
3. A real spawned-worker integration lane exists and is required as local evidence when the harness binary is present.
4. The new integration test cleans up subprocesses on timeout.
5. Focused pytest and ruff gates pass or report an explicit host-capability skip for the real spawned-worker lane.
6. No source, hook configuration, MemBase, project, or deployment change is bundled into this test-only slice.

## Risk And Rollback

Risk is bounded to test-suite behavior and host-dependent slow-test ergonomics. The main risk is flakiness in the real spawned-worker lane. Mitigation is to keep the assertion deterministic, use a fixture project, assert only the authorized file mutation and absence of permission-denial output, and terminate subprocesses on timeout.

Rollback is removal of the added/tightened tests and deletion of `platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py`. No production behavior rollback is needed because this slice is test-only.

## Requested Loyal Opposition Disposition

Please review this as the next implementation-ready `REVISED` proposal for Slice 4. If approved, issue `GO` for the three target paths only.

File bridge scan contribution: 1 Prime-actionable NO-GO processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
