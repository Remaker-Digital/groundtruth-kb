NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Pre-existing failures in platform_tests/hooks/test_workstream_focus.py: stale relay-cache fixtures + counterpart-state path resolution

bridge_kind: prime_proposal
Document: gtkb-test-workstream-focus-stale-relay-cache-fixtures
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3460

target_paths: ["platform_tests/hooks/test_workstream_focus.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

WI-3460 reported three pre-existing failures in `platform_tests/hooks/test_workstream_focus.py` (as observed during Slice 2 / WI-3458 at bridge `-002`: 47 passed / 3 failed / 3 skipped / 2 xfailed): (1) `test_startup_gate_emits_bounded_pointer_not_inlined_disclosure` and (2) `test_startup_gate_message_authorizes_one_read_only_read` failed because the relay-cache fixture (`_write_relay_cache`) baked a hardcoded `generated_at` date (`2026-05-15T00:00:00Z`) that aged out of the freshness window; (3) `test_detect_counterpart_state_uses_project_root_paths_when_provided` failed for a separate root cause (the WI-3342 IP-3 `load_role_assignments` migration dropped `harness_type`, so `detect_counterpart_state` keyed its role-set map by harness ID and `counterpart_present` never matched). Interrogative-default verification at the current commit (HEAD `19238f359`) shows **all three named failures are already resolved by intervening reliability work**, and the test suite is green. The correct fast-lane defect closure is therefore (a) a verification gate confirming resolution and (b) removal of the now-dead xfail scaffolding (a stale comment block + an unreferenced module constant) that still describes the fixed regression as if active.

## Defect / Reproduction

Reproduction (as originally reported, against the pre-fix tree): with `_write_relay_cache` writing a fixed `generated_at` of `2026-05-15T00:00:00Z`, running the suite on/after the freshness cutoff made the cache stale, so the two startup-gate relay tests asserted on a `STARTUP RELAY FAILURE` context they did not expect → FAIL. Separately, after the WI-3342 IP-3 migration `scripts/harness_roles.py::load_role_assignments` returned a minimal `{"role": [...]}` record (dropping `harness_type`); `scripts/workstream_focus.py::detect_counterpart_state` keyed `per_harness_role_sets` by `record.get("harness_type")` (now `None` → falls back to the harness ID), and `counterpart_present` compared against `DEFAULT_HARNESS_IDS` (harness names), so it was always `False` → the project-root-path test (and the two counterpart-role-collision tests) failed/xfailed.

Current state (verified read-only at HEAD `19238f359`, this session):
- `python -m pytest platform_tests/hooks/test_workstream_focus.py -q` → **59 passed, 3 skipped, 0 failed, 0 xfailed/xpassed**.
- The two startup-gate tests pass: `_write_relay_cache` (lines 459-490) now computes `generated_at` via `datetime.now(UTC).strftime(...)` — the hardcoded-date bitrot is gone.
- `test_detect_counterpart_state_uses_project_root_paths_when_provided`, `test_detect_counterpart_state_same_role_warns`, and `test_detect_counterpart_state_different_role_warns` all pass: `detect_counterpart_state` (source lines 900-916) now normalizes role-sets via `_normalize_role_field` and the harness-type-vs-id regression is fixed (the `@pytest.mark.xfail` decorators have been removed).
- Residual hygiene defect: `platform_tests/hooks/test_workstream_focus.py` lines 1213-1243 still carry an explanatory comment block describing the *fixed* WI-3342 IP-3 regression as a live "KNOWN PRODUCTION REGRESSION (reported, not fixed here)" and declaring "xfail keeps the correct test in place," plus the module-level string constant `_COUNTERPART_HARNESS_TYPE_REGRESSION` (defined at line 1237) that is now **unreferenced** (no `@pytest.mark.xfail(reason=...)` consumes it; `grep -rn _COUNTERPART_HARNESS_TYPE_REGRESSION scripts/ platform_tests/` returns only the definition site). This dead scaffolding misleads future readers/audits into believing a production regression is still active.

This proposal removes that stale scaffolding (the WI's "standing fix" of de-bitrotting the fixtures already landed) and pins resolution behind durable regression assertions, so WI-3460 closes with evidence rather than silent drift.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/hooks/test_workstream_focus.py`. The source module `scripts/workstream_focus.py` was inspected read-only and requires **no change** (its production regression is already fixed); it is therefore not a target path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `VERIFIED` is the authoritative terminal signal; this defect is closed only when the regression assertions are re-run as the verification evidence under the bridge gate, not by a bare "tests look green" claim.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - removing the dead xfail comment/constant keeps the durable test artifact honest about lifecycle state (a fixed regression must not be documented as still active), preserving the artifact network's truthfulness.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs that constrain the change (mandatory proposal linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives its checks from the named specs and executes the affected tests, satisfying the mandatory spec-derived-testing gate for the eventual VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries the mandatory `Project Authorization` / `Project` / `Work Item` linkage lines (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / PROJECT-GTKB-RELIABILITY-FIXES / WI-3460).
- `SPEC-AUQ-POLICY-ENGINE-001` - no owner-decision AUQ is introduced by this fast-lane test-hygiene fix; the change is covered by standing authorization, so the AUQ policy surface is not engaged (relevance: confirms this change does not require a fresh owner decision under the AUQ policy engine).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to a GT-KB platform test (`platform_tests/...`); no application/adopter surface under `applications/` is touched, so the platform/application isolation boundary is respected.
- `GOV-STANDING-BACKLOG-001` - WI-3460 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES; this proposal advances and closes that tracked item.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the affected tests exercise the workstream-focus UserPromptSubmit hook (startup-gate relay + counterpart-state), which is part of the Claude/Codex hook-parity surface; this change does not alter hook behavior or parity, only the test fixtures/scaffolding (relevance: confirms hook-parity behavior is unchanged).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix keeps test scaffolding artifact-backed and consistent with the now-fixed production state rather than leaving inferred/stale narrative in the test module.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the test module to remove dead regression scaffolding is the lifecycle-trigger-appropriate action for a "fixed regression whose xfail/comment scaffolding is now stale" condition.

## Prior Deliberations

- `DELIB-20264935` - GO - Startup Relay Cache TTL Self-Heal: the GO for the startup-relay-cache self-healing work (WI-3486) whose landing made the relay-cache freshness path robust; directly relevant because it is part of why T1/T2 now pass.
- `DELIB-20264942` - Loyal Opposition Verification - Startup Relay Truncation Fix Refile: verification of the startup-relay fix family that overlaps the same `_write_relay_cache`/startup-gate surface these tests exercise.
- `DELIB-20264943` - Loyal Opposition Verification - Startup Relay Truncation Fix Refile: companion verification record for the same startup-relay corrective family (confirms the relay surface was verified, supporting the "already resolved" claim).
- `DELIB-20264235` - Loyal Opposition Review - Interactive Session Role Override Slice 2: role-resolution / registry-projection context relevant to the `detect_counterpart_state` role-set reading path that was the third failure's root cause.
- `DELIB-20264794` - Loyal Opposition Verification - SessionStart Formalization Corrective Implementation: SessionStart/startup-gate verification context adjacent to the startup-disclosure relay tests in this module.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - the reliability fast-lane standing authorization; WI-3460 is origin=defect, single-concern, touches one test file, introduces no new public API/CLI/behavior and no new/revised requirement or spec, so it is covered by the standing project authorization through active project membership without a fresh owner approval.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3460 is one of the open reliability work items in scope for that batch (P3 defect).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane direction that PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING operationalizes; this WI meets every fast-lane criterion (see Requirement Sufficiency + the fast-lane checklist), so it proceeds on the fast lane.

## Requirement Sufficiency

Existing requirements sufficient. The governing authority is `GOV-FILE-BRIDGE-AUTHORITY-001` (VERIFIED is the terminal evidence signal) together with `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (durable artifacts must reflect true lifecycle state). These already require that a fixed regression's stale test scaffolding be cleaned up and that closure rest on executed regression evidence. No new or revised requirement/specification is introduced; this is a defect-removal (test-hygiene) change.

## Proposed Scope

This is the defect-removal path. The WI's original "standing fix" (de-bitrot the relay-cache fixture to use a relative/`now`-based timestamp) has already landed; the remaining work removes dead scaffolding and pins resolution.

1. **Remove the stale regression scaffolding in `platform_tests/hooks/test_workstream_focus.py`** (the only file that changes):
   - Delete the now-inaccurate comment block at lines ~1213-1243 (the "WI-3342 IP-6 — KNOWN PRODUCTION REGRESSION (reported, not fixed here)" narrative that describes a regression which is now fixed and states "xfail keeps the correct test in place").
   - Delete the unreferenced module-level constant `_COUNTERPART_HARNESS_TYPE_REGRESSION` (defined at line ~1237, consumed by no `@pytest.mark.xfail` decorator anywhere — confirmed by `grep -rn _COUNTERPART_HARNESS_TYPE_REGRESSION scripts/ platform_tests/` returning only the definition site).
   - Optionally replace the deleted block with a one-line note recording that the WI-3342 IP-3 `harness_type` regression and the relay-cache freshness bitrot are both resolved (so the audit trail in-file points forward, not backward). This keeps the two `detect_counterpart_state` tests in place as live (non-xfail) regression coverage.
2. **No change to `scripts/workstream_focus.py`** — the production `detect_counterpart_state` role-set/`_normalize_role_field` path and the `_write_relay_cache` freshness path are already correct; the source is cited in this proposal as inspected-no-change-required, not as a target path.
3. The contract/behavior-change alternative named in the WI ("model/display that automatic startup behavior can precede X") does not apply here; nothing in this fix changes runtime behavior, only test scaffolding.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (closure rests on executed evidence) | `test_startup_gate_emits_bounded_pointer_not_inlined_disclosure` | The startup-gate relay emits a bounded pointer and does not surface a `STARTUP RELAY FAILURE` for a freshly-written cache — passes (no hardcoded-date bitrot). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (closure rests on executed evidence) | `test_startup_gate_message_authorizes_one_read_only_read` | The relay gate wording authorizes the one read-only recovery read (`read-only` / `verbatim` / `acknowledgement` present) — passes. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (no stale lifecycle narrative) | `test_detect_counterpart_state_uses_project_root_paths_when_provided` | `detect_counterpart_state(sandbox)` loads the sandbox role map (paths under sandbox, never under canonical `PROJECT_ROOT`) — passes as a live, non-xfail test after scaffolding removal. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (regression coverage retained) | `test_detect_counterpart_state_same_role_warns` | Two harnesses sharing a role-set produce a `counterpart_present=True` + collision warning — passes (harness-type regression fixed; the xfail formerly guarding this is removed). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (regression coverage retained) | `test_detect_counterpart_state_different_role_warns` | Distinct role-sets produce `same_role_slot=False` + a role-divergence warning — passes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (dead scaffolding removed) | Static check (grep) | `_COUNTERPART_HARNESS_TYPE_REGRESSION` no longer appears in `platform_tests/hooks/test_workstream_focus.py`, and no `@pytest.mark.xfail` referencing the WI-3342 IP-3 counterpart regression remains. |

Execution commands:
- `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`
- `python -m ruff check platform_tests/hooks/test_workstream_focus.py`
- `python -m ruff format --check platform_tests/hooks/test_workstream_focus.py`

## Acceptance Criteria

1. `platform_tests/hooks/test_workstream_focus.py` passes in full with **no xfail/xpass** and no skips beyond the three intentional `@pytest.mark.skip` (S304/S305 retirement) cases — i.e. the green baseline (59 passed, 3 skipped) is preserved.
2. The dead `_COUNTERPART_HARNESS_TYPE_REGRESSION` constant and the stale "KNOWN PRODUCTION REGRESSION (reported, not fixed here)" comment block are removed; `grep -rn _COUNTERPART_HARNESS_TYPE_REGRESSION scripts/ platform_tests/` returns nothing.
3. `python -m ruff check` and `python -m ruff format --check` are clean on the changed file.
4. `scripts/workstream_focus.py` is unchanged (no source regression introduced).

## Risks / Rollback

- Risk: deleting the comment block also deletes useful provenance about the historical WI-3342 IP-3 regression. Mitigation: replace it with a concise one-line "resolved" note (step 1, optional sub-bullet) so the provenance is retained without falsely implying the regression is live.
- Risk: a future regression of the `harness_type`/role-set reading path would now fail (rather than xfail) loudly. This is the intended, correct posture — the two `detect_counterpart_state` tests become live guards; no mitigation needed beyond awareness.
- Risk (low): the relay-cache tests are time-sensitive by nature. Mitigation: the fixtures already use `datetime.now(UTC)`; this proposal does not reintroduce any hardcoded date.
- Rollback: revert the single test-file edit. The change is comment/dead-constant removal plus an optional one-line note, fully reversible with no migration and no source or KB impact.

## Files Expected To Change

- `platform_tests/hooks/test_workstream_focus.py` (only file changed)
- `scripts/workstream_focus.py` — inspected, NO change required (production regression already fixed); listed here for traceability, not as a target path.

## Recommended Commit Type

`fix`

Rationale: WI-3460 origin is `defect`; the change removes defect-era dead scaffolding from a test module with no new capability. (`test:` would also be defensible since only a test file changes; `fix:` is used per the defect origin and the reliability-fast-lane convention.)
