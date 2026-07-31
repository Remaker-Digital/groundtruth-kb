NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

# WI-5207 Implementation Report - Per-selected-document batch completion

bridge_kind: implementation_report
Document: gtkb-wi5207-per-document-batch-completion
Version: 003 (NEW post-implementation report)
Responds to GO: bridge/gtkb-wi5207-per-document-batch-completion-002.md
Approved proposal: bridge/gtkb-wi5207-per-document-batch-completion-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5207-BATCH-COMPLETION-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5207
Linked Test: TEST-11361
Implementation claim: row 31220, session 019f5474-93a6-7f70-8e54-d6d8b0a31bb4, deadline 2026-07-12T08:20:24Z
Implementation authorization packet: sha256:f5a8f00d2e87bdb7189e231e0d00794ffe3fb15ce21d965bfa8da85a4bc2c81a
Recommended commit type: fix

## Implementation Claim

The dispatcher now records per-document launch signatures and version baselines, snapshots a role-correct verdict outcome for every selected Loyal Opposition document, and declares batch success only when every selected document advances after launch. A multi-document exit-0 batch with any missing verdict is recorded as `selected_documents_incomplete` with exact completed and incomplete document lists. Completed-document signatures are retained, incomplete signatures and aggregate dedupe state are cleared, the next tick selects only incomplete documents, and every document lease is released exactly once.

The incomplete-batch outcome resets stale provider failure/backoff/circuit fields rather than incrementing them. Single-document no-verdict behavior remains the existing `no_verdict_produced` failure. Fully completed batches retain the aggregate signature and all per-document signatures. `VERIFIED` evidence remains subject to atomic commit validation per document. The daemon source remains unchanged and delegates reconciliation to the corrected runtime function.

## Changed Paths

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

All five paths were clean before WI-5207 implementation. No foreign hunk is authorized for the focused commit. The canonical B eligibility transaction regenerated `harness-state/harness-registry.json` after implementation; that unrelated operational projection is explicitly excluded.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`

## Owner Decisions / Input

- `DELIB-202666173` directs genuine six-harness proof and correction of every defect discovered.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5207-BATCH-COMPLETION-20260711` authorizes this bounded implementation through 2026-07-18T23:59:59Z.
- No new owner decision was required; implementation follows the exact GO target set and conditions.

## Prior Deliberations

- `DELIB-202666173` - parent six-harness proof and defect-correction directive.
- `INTAKE-a815f782` - established per-document suppression and lease granularity.
- `INTAKE-fd012ad6` - requires inspection-backed operational evidence.
- WI-5205 / commit `4abb6ed2` - completed the separate canonical `NO-ACTION` consumer semantics repair before WI-5207 implementation.

## Specification-Derived Verification

| Requirement | Executed evidence | Observed result |
| --- | --- | --- |
| Truthful per-selected-document completion | Partial and full two-document runtime tests | Partial records exact completed/missing ids; full retains both signatures |
| Preserve completed work and reoffer only missing work | Partial test persists state, executes the next real dispatcher tick, and captures its LO batch | Only `missing-thread` is selected; `completed-thread` is not reoffered |
| Exact-once lease release | Partial test invokes reconciliation twice with lease-release instrumentation | One release call containing both selected documents |
| `NO-ACTION` requires its own corrected verdict | Mixed `NEW` plus `NO-ACTION` test | Missing `NO-ACTION` response remains incomplete despite sibling `GO` |
| Late-verdict/version race | Verdict is created during the all-document snapshot while recipient state is asserted unchanged | Both outcomes complete before one state mutation; launch version boundaries hold |
| Single-document compatibility | Single selected document exits 0 without a verdict | Existing `no_verdict_produced` failure and failure count retained |
| Distinct nonprovider classification | Runtime health classifier test | WARN contains `selected_documents_incomplete`; no provider or runtime failure classification |
| Daemon delegation | Daemon shadow decision loads exit state and persists runtime reconciliation | Completed/missing lists and retained signature are written through the unchanged daemon delegate |

## Commands And Observed Results

1. Focused acceptance:
   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short -k wi5207`
   Result: `7 passed, 294 deselected`.
2. Approved three-file suite in the implementation worktree:
   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short`
   Result: `290 passed, 11 failed`.
3. The identical suite in detached clean worktree `.gtkb-state/wi5207-baseline` at `4abb6ed2`:
   Result: `283 passed, 11 failed`. The same 11 daemon nodes fail with byte-equivalent causes: nine pre-existing work-intent/provenance fixture failures and two stale 3600/5400 lifetime expectations against the required 29,400-second generous lifetime. WI-5207 adds seven passing tests and zero failures.
4. Ruff lint on all five approved paths:
   `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py`
   Result: `All checks passed!`
5. Ruff format check on all five approved paths:
   `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py`
   Result: `5 files already formatted`.

## GO Conditions

- [x] Every selected `NEW`, `REVISED`, and `NO-ACTION` document receives independent completion evaluation.
- [x] Partial completion is `selected_documents_incomplete`, with exact completed and missing ids.
- [x] Completed signatures are preserved and only incomplete documents reoffer.
- [x] Leases release exactly once for every selected document.
- [x] Partial completion does not increment provider failure, retry backoff, or circuit state.
- [x] Full and single-document compatibility is covered.
- [x] Mixed-status and late-verdict race fixtures are covered.
- [x] Health/report classification is distinct from provider failure.
- [x] Daemon delegation is tested without changing daemon source.
- [x] D/F/H generous allowances remain unchanged.

## Risk And Rollback

Residual risk is limited to legacy multi-document launches created before the new per-document signature map existed. They still receive per-document verdict evaluation and truthful incomplete classification; only per-document signature retention may be unavailable for an old multi-document envelope, in which case clearing the aggregate signature safely favors reoffer. The focused commit is the rollback boundary. Bridge history and runtime telemetry remain append-only.

## Loyal Opposition Asks

1. Inspect the exact five-path diff and confirm no foreign hunk is included.
2. Independently rerun the seven WI-5207 nodes, all passing runtime/config tests, lint, and format checks.
3. Compare the 11 broad failures against clean `4abb6ed2`; do not repair the required generous lifetime constants or unrelated provenance fixtures under WI-5207.
4. Confirm the next-tick partial-batch fixture reoffers only the missing document and lease release remains exact-once.
5. If all evidence holds, write VERIFIED and create one focused commit containing only the five approved paths plus the WI-5207 bridge chain additions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
