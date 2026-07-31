NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=unspecified-by-host; thread_source=CODEX_THREAD_ID
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5784-work-intent-claim-lock-retry - 003

bridge_kind: implementation_report
Document: gtkb-wi5784-work-intent-claim-lock-retry
Version: 003
Responds to: bridge/gtkb-wi5784-work-intent-claim-lock-retry-002.md
Approved proposal: bridge/gtkb-wi5784-work-intent-claim-lock-retry-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5784
Recommended commit type: fix:

## Implementation Claim

Implemented the approved WI-5784 acquire/release repair in the shared work-intent registry. Transient transaction-phase `SQLITE_BUSY`/`SQLITE_LOCKED` failures now retry through fresh connections under one monotonic total deadline and capped backoff. Every attempt re-reads the exact claim row, revalidates the operation and project-authorization bootstrap metadata, preserves changed or foreign holders, and treats a missing release row as idempotent success. The remaining SQLite busy timeout is re-clamped before `BEGIN IMMEDIATE`, the transactional action, and `COMMIT`, so a late commit cannot consume a new full per-attempt wait budget.

The implementation also replaces global `SCHEMA_SQL` execution on this narrow hot path with an idempotent `work_intent_claims`-only table/additive-column/index migration, and exposes typed operation/phase/attempt/elapsed/SQLite-code/path diagnostics without claiming lock-holder identity. Open/schema/corruption and other non-contention failures remain immediate; retry behavior is limited to acquire and release, as approved.

Implementation authority evidence:

- live `go_implementation` claim row `34991`, held by Prime Builder session `019fb1f2-2f91-7b82-ac15-acdd56e13d1e` for this exact bridge thread and project;
- schema-v3 implementation-start packet `sha256:a37586c7debbe850be37694dbbcb729820eb1198838d69685b0395d18e436784` with the same two target paths;
- PAUTH `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` v5 and owner decision `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-10`
- `GOV-12`
- `SPEC-1662`
- `GOV-15`

## Owner Decisions / Input

No new owner decision is required by this implementation report. Mike approved governed processing of `WI-5784` in `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL`; the work item inherits implementation approval from its active parent project and the selected whole-project PAUTH. No dispatcher/TAFE, deployment, credential, external-system, destructive-cleanup, push, release, or history-rewrite authority was requested or exercised.

## Prior Deliberations

- `bridge/gtkb-wi5784-work-intent-claim-lock-retry-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5784-work-intent-claim-lock-retry-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This Prime `NEW` report carries forward every proposal specification, project/WI/PAUTH metadata, the exact claim and implementation-start packet, executed commands, and observed results. Candidate applicability preflight is executed before filing; independent Loyal Opposition verification remains required. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-STANDING-BACKLOG-001` | The numbered proposal/GO/report chain, linked owner decision, work item, source, tests, and residual advisory evidence preserve the change as governed artifacts without claiming verification. |
| `SPEC-AUQ-POLICY-ENGINE-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL`, active project membership, PROGRAM PAUTH v5, live claim row 34991, and packet `sha256:a37586...784` were checked before protected mutation. The exact authorized two-path cohort is unchanged. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `git diff --stat` and the report file list show only the shared platform registry and shared platform test changed; no adopter or harness-local authority surface was introduced. The adjacent role/claim/hook green cohorts passed 85 and 39 tests respectively. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_acquire_retry_preserves_foreign_holder_published_during_contention`, `test_acquire_retry_revalidates_bootstrap_authority_metadata`, and `test_release_retry_revalidates_and_preserves_replacement_holder` prove each retry re-observes exact transactional ownership/authority and preserves replacements. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`; `GOV-10`; `SPEC-1662` | Real two-connection SQLite tests exercise unlock success, acquire exhaustion/no partial claim, release success, replacement preservation, commit-phase deadline exhaustion/rollback, idempotence, typed non-busy failure, and narrow schema behavior through public acquire/release interfaces. Focused result: 44 passed. |
| `GOV-12` | Ten focused WI-5784 regression tests were added in the same two-path change and the complete focused module passes 44 tests. |
| `GOV-15` | `git diff --check`, exact-path file hashes, and the two-file diff prove the implementation stayed local and bounded. Dispatcher/TAFE remained disabled and untouched; no external mutation or compensating cleanup occurred. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short --timeout=300`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/skills/test_bridge_propose_helper_work_intent.py groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short --timeout=300 -k "not gate_does_not_auto_extend_an_allowed_mutation and not helper_failsoft_fallback_equals_canonical"`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_go_impl_claim_timebox.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py platform_tests/hooks/test_bridge_compliance_gate_work_intent.py -q --tb=short --timeout=300 -k "not post_go_no_go_remains_an_implementation_claim and not axis2_failsoft_fallback_equals_canonical and not work_intent_failsoft_fallback_equals_canonical"`
- `git diff --check -- scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi5784-work-intent-claim-lock-retry-003.md --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi5784-work-intent-claim-lock-retry-003.md`

## Observed Results

- Focused registry module: **44 passed**, 5 pre-existing warnings, in 4.32 seconds.
- Ruff lint: **All checks passed**.
- Ruff format: **2 files already formatted**.
- Adjacent claim/role/auto-extend/proposal-helper/control-plane green cohort: **85 passed, 2 deliberately deselected**, 1 warning, in 42.70 seconds.
- Adjacent timebox/Axis-2/compliance-gate green cohort: **39 passed, 4 deliberately deselected**, 1 warning, in 2.76 seconds.
- Diff whitespace check: passed. Final file SHA-256 values: source `F26E10DC6E0B10CAB524D9BDED3DF4AEE8BF821907D9043571739B3E2829D5D4`; test `F886F15E229BA1BC56E7C2513F67772031459B14A5C49A7C8A258CA23158A5AB`.
- Candidate applicability preflight: passed with `blocking_errors: []`, `missing_required_specs: []`, and `missing_advisory_specs: []`. Mandatory clause preflight: 5 clauses evaluated, 3 `must_apply`, 0 evidence gaps, 0 blocking gaps.
- Independent read-only code review initially found bootstrap-authority and commit-deadline gaps; both were corrected. Final re-review found no actionable source defect and its five concurrency/revalidation cases passed (`5 passed, 39 deselected`).
- Full adjacent discovery runs exposed unrelated existing failures rather than hiding them: a repeated 30-second `.gtkb-state/sot-registry/control-plane.lock` timeout, staged foreign `CURSOR_CONVERSATION_ID` fallback drift in `scripts/gtkb_session_id.py`, and a stale latest-NO-GO expectation. Excluding only those specifically attributed cases yielded the green cohorts above. These observations are being preserved in the separate concurrency/SoT advisory packet; none is in either WI-5784 target.

## Files Changed

- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `scripts/bridge_work_intent_registry.py`

Excluded out-of-scope dirty paths: 299.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: This repairs a reproduced acquire/release lock-contention defect and adds its regression coverage.

```text
     .../scripts/test_bridge_work_intent_registry.py    | 342 ++++++++++++++++
     scripts/bridge_work_intent_registry.py             | 447 +++++++++++++++++----
     2 files changed, 708 insertions(+), 81 deletions(-)
```

## Acceptance Criteria Status

- [x] Acquire succeeds when a real two-connection lock clears inside the total deadline and leaves no partial claim when the deadline expires.
- [x] Every acquire retry revalidates the transactional holder, bootstrap authority metadata, and operation; changed or foreign ownership is never overwritten.
- [x] Release succeeds idempotently for an absent row, deletes only the exact slug-plus-session holder after retry, and preserves a replacement or foreign holder.
- [x] Only transaction-phase `SQLITE_BUSY` and `SQLITE_LOCKED` are retried; schema, corruption, open, and other failures surface immediately with typed phase/attempt/elapsed/code diagnostics and all connections closed.
- [x] The uncontended acquire/release hot path avoids global `SCHEMA_SQL` while retaining narrow idempotent schema compatibility; the focused suite stays green at 44 tests.

## Risk And Rollback

Residual risk is bounded. The retry window can add up to ten seconds of deliberate fail-closed latency during real write contention. Open/schema contention remains an immediate typed failure by approved design, and `extend` semantics, caller compensation, dispatcher durability, process ownership, and lock-file policy remain out of scope. The real timing tests use conservative Windows margins, but scheduler and SQLite timing variation remain a verification consideration. Unrelated foreign worktree drift and the independent control-plane lock timeout are disclosed above and are not attributed to this implementation.

Rollback requires separate authority to revert only `scripts/bridge_work_intent_registry.py` and `platform_tests/scripts/test_bridge_work_intent_registry.py`, then rerun the focused and adjacent commands. The proposal, GO, report, project authorization, owner decision, and later verdict remain append-only audit artifacts and must not be deleted.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
