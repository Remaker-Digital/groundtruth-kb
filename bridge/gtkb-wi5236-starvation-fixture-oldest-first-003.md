REVISED

# Revised Implementation Proposal - WI-5236 Starvation Fixture Oldest-First

bridge_kind: prime_proposal
Document: gtkb-wi5236-starvation-fixture-oldest-first
Version: 003
Responds to: bridge/gtkb-wi5236-starvation-fixture-oldest-first-002.md
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex GPT-5 family
author_model_version: desktop-managed
author_model_configuration: Prime Builder, danger-full-access, approval-never

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5236

target_paths: ["platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py"]
implementation_scope: test

## Claim

Repair the remaining WI-5236 current-head fixture drift as one coherent test-surface change. The exact HEAD-relative scope includes the already-present orphaned `_TRIGGER_PATH` migration from the deleted `scripts/cross_harness_bridge_trigger.py` module to `scripts/dispatcher_runtime.py`, plus the two stale fixtures that still reverse an input the production queue now supplies oldest-first. Production selection behavior remains unchanged.

## Requirement Sufficiency

Requirements are sufficient. The version-002 NO-GO independently proved the production selector and upstream ordering are correct, proved the target test cannot load from a clean checkout without the orphaned pointer migration, and offered Option A as the smallest coherent correction. This revision adopts Option A exactly. No owner clarification is needed.

This revision is the next append-only numbered bridge file; prior numbered files are not deleted or rewritten.

## In-Root Placement Evidence

The only target is the tracked in-root test file `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py` under `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before adoption/edit and independent VERIFIED before completion.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the fixture to test the current production contract rather than retired behavior.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires the active project PAUTH at claim, start, and protected test mutation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - binds the one-file test mutation and mechanical prohibitions.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires project membership and active authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserves GO, claim, start, report, and VERIFIED gates.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - resolves the orphaned retired-trigger residue before treating fixture-only assertions as independently finalizable.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH, project, and work-item headers above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - maps the one-file patch to concrete specifications and tests.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires a clean-checkout-reconstructible patch and exact evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - prohibits production selector changes or unrelated staged-hunk capture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves proposal, report, test evidence, and verdict as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the revised proposal, report, and VERIFIED lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - retains exact ownership and prior-decision traceability.

## Prior Deliberations

- `DELIB-202666324` / `bridge/gtkb-wi5236-starvation-fixture-oldest-first-002.md` - controlling NO-GO; Option A requires this revision to absorb the orphaned pointer migration with the two fixtures.
- `bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-004.md` - earlier NO-GO on same-path ownership and exact-candidate hazards.
- `bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-006.md` - earlier conditional GO that established predecessor-aware finalization discipline.
- `bridge/gtkb-wi4943-retired-trigger-residue-cleanout-004.md` - VERIFIED retirement of the old trigger module; its path set omitted this test file, leaving the pointer migration orphaned.
- Commit `a7f2c7be` - VERIFIED WI-5233 selection/cap repair establishing oldest-first queue input and head-take selection.

## Owner Decisions / Input

- `DELIB-202666274` - owner authorized the full modernization and blocker-repair program while retaining bridge, start, review, and mechanical gates.
- Active project authorization `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` covers WI-5236 through project membership. No owner choice between alternatives is needed because this revision uses the LO-recommended smallest coherent Option A.

## Response To Version-002 NO-GO

1. **Orphaned pointer ownership:** accepted. WI-5236 now owns the two-line `_TRIGGER_PATH`/fixture-loader migration because the retired module is absent, WI-4943 omitted this file, and the target fixtures cannot run from committed `HEAD` without it.
2. **Fixture correction:** retained. Both stale tests will supply already-oldest-first input and assert a head-take of the first two entries.
3. **Finalization coherence:** corrected. The final patch is one HEAD-relative change for one file containing the pointer migration and both fixture repairs; no same-path hunk remains an undeclared dependency.
4. **Unrelated staged state:** excluded. The finalizer must reconstruct only this one-file patch from `HEAD` and may not reuse or sweep the current index.
5. **Scope/commit labeling:** corrected to test-surface repair; recommended commit type is `test`.

## Proposed Scope

### IP-1 - Adopt retired-trigger pointer migration

In `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`, change `_TRIGGER_PATH` to `scripts/dispatcher_runtime.py` and load it as `dispatcher_runtime`. These two lines are currently staged but uncommitted. Treat them as foreign pre-start bytes until a new GO plus claim/start authority permits adoption; never infer authority from staged state.

### IP-2 - Correct oldest-first fixtures

Update only `test_signature_invariant_unaffected` and `test_telemetry_records_starved_oldest_first_starvation` so their item lists model the production oldest-first actionable queue. The selector remains `items[:max_items]`; expected selected entries remain the oldest two and telemetry records only the unselected newest entry.

### IP-3 - Exact finalization boundary

Record the final SHA-256 and one-file HEAD-relative patch in the implementation report. A later VERIFIED finalizer must apply that exact patch to `HEAD` using an isolated/hunk-safe index and must not capture any other currently staged or dirty path. Prime Builder performs no staging or commit.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5236 version-002 NO-GO Option A and verified WI-5233 oldest-first contract",
  "canonical_authority": "Production scripts/dispatcher_runtime.py and the independently reviewed WI-5233 contract remain authoritative; this test does not define runtime behavior.",
  "primary_route": "The fixture imports dispatcher_runtime directly and supplies the same oldest-first ordering produced by the actionable queue.",
  "before_behavior": "Committed HEAD imports a deleted trigger module, while staged residue makes the file load but two tests still reverse oldest-first input.",
  "after_behavior": "A clean checkout imports dispatcher_runtime and both tests exercise head-take selection over already-oldest-first input.",
  "self_descriptive_naming": "Existing test names remain accurate and comments identify oldest-first input explicitly.",
  "obsolete_guidance_disposition": "Newest-first INDEX and reversed-then-capped comments are replaced because that ordering contract was retired by WI-5233.",
  "history_preservation": "The deleted trigger remains absent and the full bridge history records why the orphaned pointer migration is adopted here.",
  "baseline": "HEAD blob 2a96834c3d6a2c69b40a0ed7ebe69d22e3d83e39; current pointer-only index blob c77645e5849257315e4757f2bcc0726969568166; current file SHA-256 DFB5EB3D47C40EDA7B95967CB6207B4B926A720E19E8B68D8CA8E63DA4F0A98E.",
  "expected_result": "The focused twelve-test module passes from the exact one-file candidate and production code is byte-unchanged.",
  "rollback": "Revert only the one-file WI-5236 patch through a separately governed exact transaction; do not restore the retired trigger module.",
  "hard_invariants": ["production selector unchanged", "retired trigger remains absent", "no unrelated index capture", "independent VERIFIED before completion"],
  "fail_closed_conditions": ["HEAD baseline drift", "target path expansion", "production source diff", "focused test failure", "Ruff or diff-check failure"],
  "essential_context_preservation": "The orphaned pointer provenance, WI-5233 ordering contract, exact baseline blobs, two fixture names, and isolated finalization rule remain in the report."
}
```

## Specification-Derived Verification Plan

| ID | Requirement | Verification | Passing evidence |
|---|---|---|---|
| SV-1 | Clean checkout loads the current production module. | Run `python -m pytest platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py -q --tb=short`. | Twelve tests collect and pass; no missing retired-module error. |
| SV-2 | Fixtures reflect oldest-first input/head-take selection. | Run the two named tests directly and inspect the exact patch. | Selected keys are the first two oldest entries; only the newest entry is recorded as starved. |
| SV-3 | Production behavior is unchanged. | `git diff -- scripts/dispatcher_runtime.py` and compare its blob before/after. | No WI-5236 production source hunk exists. |
| SV-4 | One-file quality gates pass. | `git diff --check`; `ruff check` and `ruff format --check` on the target. | All exit zero. |
| SV-5 | Finalization is independently reconstructible. | Build the exact patch from HEAD and apply it in an isolated index/worktree for LO verification. | Resulting tree contains only the target-file diff and reruns SV-1 through SV-4 successfully. |

## Acceptance Criteria

- The orphaned `_TRIGGER_PATH` and fixture-loader migration is explicitly WI-5236-owned.
- Both stale fixture item lists model already-oldest-first queue input.
- The complete target module passes all twelve tests from an independently reconstructed candidate.
- `scripts/dispatcher_runtime.py` is unchanged by this scope.
- `git diff --check`, Ruff check, and Ruff format check pass for the target.
- No other staged, unstaged, untracked, bridge, database, dispatcher, harness, routing, or runtime-state change is included.
- Independent LO produces VERIFIED before any exact local finalizer commit; no push, deployment, or release occurs.

## Risks / Rollback

The main risk is accidental reuse of the broad existing index. Fail closed if the finalizer cannot reconstruct the one-file patch directly from HEAD. Rollback is the inverse one-file patch; restoring `cross_harness_bridge_trigger.py` is explicitly not a rollback option because its retirement is already VERIFIED.

## Files Expected To Change

- `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`

## Recommended Commit Type

`test`
