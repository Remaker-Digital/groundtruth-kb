NEW

# Implementation Proposal NEW - Doctor `_check_bridge_dispatch_liveness` recipient-key fix (WI-4307)

**Status:** NEW (implementation proposal; awaiting Codex GO/NO-GO)
**Date:** 2026-06-04
**Author:** Prime Builder (Claude Opus 4.7, harness B)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 554d6f54-12a9-4384-b4e4-3b38bba18047
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

bridge_kind: implementation_proposal
Document: gtkb-doctor-dispatch-liveness-recipient-key-fix
Version: 001
Session: S408
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Work Item: WI-4307
work_item_ids: [WI-4307]
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py"]
spec_ids: []

---

## Claim

Repair the recipient-key mapping in `_check_bridge_dispatch_liveness` so it resolves the canonical role labels (`prime-builder`, `loyal-opposition`) that the cross-harness event-driven trigger has been writing into `.gtkb-state/bridge-poller/dispatch-state.json` since Slice 4 of `gtkb-bridge-poller-event-driven-replacement`. Realign the paired test fixture and message-text assertions to the same canonical keys, and add one regression test that asserts the production schema is the accepted form.

## Why Now

The defect produces two false-ALARM FAILs in every `gt platform doctor` run on a healthy GT-KB checkout because the mapping at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2268` is `{"claude": "prime", "codex": "codex"}` but the live dispatch-state file uses canonical role labels (`prime-builder`, `loyal-opposition`). The cross-harness trigger emits canonical labels per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and writes them at `scripts/cross_harness_bridge_trigger.py:1107-1111` (recipient state seed) and `:1769-1770` (legacy→canonical write-side map). The doctor's lookup misses every time, falls through to the "missing 'recipients.<role>' entry" branch, and returns `status="fail"` with ALARM phrasing — indistinguishable from a real liveness alarm.

False ALARMs in the doctor output erode trust in the doctor as a reliability surface (the cited rationale for `GOV-RELIABILITY-FAST-LANE-001`) and silently shadow genuine alarms. Captured under WI-4307 during S406 autonomous /loop, owner-AUQ'd in S408 to use the Reliability-Fixes standing PAUTH path.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 - fast-lane governance for reliability defects with bounded scope; this proposal is one such fix.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority (included in standing PAUTH `included_spec_ids`).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - artifact-oriented governance umbrella (included in standing PAUTH `included_spec_ids`).
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - prefer fresh reads over cached copies; the fix realigns a static helper map with the live cross-harness trigger constant, eliminating a frozen copy.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - triggered by `applies_when_paths_match` glob `groundtruth-kb/src/groundtruth_kb/project/**`; the fix stays within the `groundtruth-kb/` package subtree and does not cross into `applications/`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - artifact-oriented development; the fix produces durable test + source artifacts plus the bridge audit trail.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section satisfies the linkage mandate.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Specification-Derived Verification Plan below maps each cited spec to a test.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lifecycle trigger: defect-class WI (origin=defect) → fix → test → bridge artifact chain.
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - the canonical role-label vocabulary the cross-harness trigger writes (and the doctor must therefore read).

Advisory / cross-cutting:

- `.claude/rules/bridge-essential.md` § "Operational Mode" - documents the cross-harness event-driven trigger as the canonical dispatch mechanism.
- `scripts/cross_harness_bridge_trigger.py:256-270` - the recipient-key migration comment + the legacy→canonical map.
- `.claude/rules/project-root-boundary.md` - the fix stays within `E:\GT-KB` and `groundtruth-kb/src/groundtruth_kb/project/`.

## Prior Deliberations

- DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09 - retirement of the smart-poller substrate; cross-harness trigger became canonical; recipient-key vocabulary canonicalized.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-018.md` (Slice 4 VERIFIED) - the migration that introduced the canonical role-label keys in `dispatch-state.json`.
- `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-008.md` - prior doctor-path bridge thread (renamed `_check_bridge_poller` → `_check_bridge_dispatch_liveness`); the rename preserved the legacy key map and is the proximate source of this defect.
- WI-4307 source-deliberation - S406 autonomous /loop capture (auto-memory file `project_s406_autonomous_loop_drained_bridge_wi4307_capture.md`).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - false-alarm output is a token-tax with negative information dividend; fits the deterministic-services bias.

_No prior bridge proposal exists for this specific recipient-key fix; this is the first._

## Owner Decisions / Input

- 2026-06-04 UTC, S408: owner AUQ "PAUTH path" → "Add WI-4307 to PROJECT-GTKB-RELIABILITY-FIXES (Recommended)". Cover under the standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING envelope; no per-WI PAUTH minting.
- 2026-06-04 UTC, S408: project membership row `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4307` created (version 1, active) via `python -m groundtruth_kb projects add-item PROJECT-GTKB-RELIABILITY-FIXES WI-4307` with explicit AUQ-citing `--change-reason`. This brings WI-4307 under standing PAUTH coverage by active project membership (allowed_mutation_classes: `["source","test_addition","hook_upgrade"]`, forbidden_operations: `["deploy","git_push_force","spec_deletion"]`; no expiration).

No formal-artifact-approval packets are required because the proposal touches only source + test files (no MemBase spec mutation, no protected narrative artifact edit).

## Requirement Sufficiency

Existing requirements sufficient. The fix realigns one helper-level constant with the canonical role-label vocabulary already established by `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and operationalized in `scripts/cross_harness_bridge_trigger.py`. No new requirements; no requirement disambiguation needed.

## Current Implementation Baseline

`groundtruth-kb/src/groundtruth_kb/project/doctor.py:2268` declares:

```python
_BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime", "codex": "codex"}
```

This is then consulted at `:2291` (`role = _BRIDGE_AGENT_TO_RECIPIENT.get(agent, agent)`) and used to index `recipients[role]` at `:2337`. The live `.gtkb-state/bridge-poller/dispatch-state.json` contains:

```json
{
  "recipients": {
    "loyal-opposition": { "updated_at": "...", "last_result": "...", "pending_count": ... },
    "prime-builder":    { "updated_at": "...", "last_result": "...", "pending_count": ... }
  }
}
```

Result: the `recipients.prime` and `recipients.codex` lookups both miss; the fail-branch at `:2338-2347` returns `status="fail"` with message `"... bridge dispatch-state missing 'recipients.prime' entry — ALARM ..."` (and `"... missing 'recipients.codex' entry ..."`). Confirmed against the live file in this session.

The paired test fixture `_write_dispatch_state` at `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py:77-79` writes:

```python
"recipients": {
    "prime": _recipient(prime_updated_at, prime_last_result, prime_pending_count),
    "codex": _recipient(codex_updated_at, codex_last_result, codex_pending_count),
},
```

— the same stale keys the doctor expects, which is why all 7 public-surface tests (TP1-TP7) and 3 helper-edge-case tests currently PASS against a fixture that does not match production. This is a paired test-fixture/production drift.

## Proposed Scope

1. Update the helper map at `doctor.py:2268`:

   ```python
   _BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime-builder", "codex": "loyal-opposition"}
   ```

2. Update the test fixture at `test_doctor_bridge_dispatch_liveness.py:77-79` to write canonical recipient keys (`"prime-builder"`, `"loyal-opposition"`).
3. Update the helper-edge-case docstring at TP7 (`test_run_doctor_distinguishes_claude_from_codex_recipients_in_report`) so the comment reflects the new mapping `(claude → prime-builder, codex → loyal-opposition)`.
4. Update the helper-level edge-case test `TestCheckBridgeDispatchHelperEdgeCases.test_ts2_returns_fail_when_role_key_missing` so the in-fixture single-recipient key is `"loyal-opposition"` (not `"codex"`) and the message-text assertion checks for `"prime-builder"` (not `"prime"`).
5. Update `test_ts3_returns_fail_when_updated_at_unparseable` so its in-fixture keys are canonical (`"prime-builder"`, `"loyal-opposition"`) too.
6. Add ONE new public-surface regression test `test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels` that:
   - reads `scripts/cross_harness_bridge_trigger.py`'s recipient-key write-side constants (`ROLE_STATE_KEYS`) and asserts the doctor's mapping resolves to that same set;
   - rejects the legacy `prime`/`codex` keys with FAIL (so a future regression back to legacy keys is caught).

No production behavior outside the doctor's `_check_bridge_dispatch_liveness` is touched. No source files in `groundtruth-kb/src/groundtruth_kb/project/` other than `doctor.py` are touched. The fix stays entirely within the GT-KB platform subtree (`groundtruth-kb/`) per the root-boundary rule; no `applications/` paths are touched.

Out of scope (logged as candidates for separate WIs, not implemented here):

- Reading `ROLE_STATE_KEYS` from a single shared module (e.g., a `bridge_recipient_keys.py` helper) so doctor + trigger + test share one source of truth. The current proposal hard-codes the canonical labels in doctor.py for surgical scope; the shared-module refactor is a separate hygiene step.
- The deeper canonical-keys reachability question for the legacy `prime`/`codex` keys that may still appear in other consumers (e.g., audit-log readers); not in this proposal's scope.

## Specification-Derived Verification Plan

Test-to-spec mapping for the post-implementation report:

| Test | Spec(s) | What it proves |
|------|---------|----------------|
| `test_run_doctor_reports_pass_for_both_agents_when_fresh` (TP1) - updated fixture | GOV-RELIABILITY-FAST-LANE-001, DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | Canonical recipient keys (`prime-builder`, `loyal-opposition`) are accepted and produce PASS when fresh. |
| `test_run_doctor_reports_warning_when_4_to_10_min_old` (TP2) - updated fixture | GOV-RELIABILITY-FAST-LANE-001 | WARN threshold semantics survive the key migration. |
| `test_run_doctor_reports_fail_when_over_10_min_old` (TP3) - updated fixture | GOV-RELIABILITY-FAST-LANE-001 | ALARM threshold semantics survive the key migration. |
| `test_run_doctor_distinguishes_claude_from_codex_recipients_in_report` (TP7) - updated mapping comment | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | The agent→recipient mapping yields per-agent disjoint verdicts under canonical keys. |
| `test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels` (NEW TP8) | GOV-SOURCE-OF-TRUTH-FRESHNESS-001, DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | Doctor mapping derives from the live cross-harness trigger constant set; regression to legacy keys fails. |
| `TestCheckBridgeDispatchHelperEdgeCases.test_ts2_returns_fail_when_role_key_missing` - updated | (supplemental) | Helper-level missing-key branch still returns FAIL under canonical keys. |
| `TestCheckBridgeDispatchHelperEdgeCases.test_ts3_returns_fail_when_updated_at_unparseable` - updated | (supplemental) | Helper-level unparseable-timestamp branch still returns FAIL under canonical keys. |

Verification commands (will be run before filing the post-implementation report):

```text
ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py
ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py
python -m pytest groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py -v
```

Plus a live-state spot-check against the actual `.gtkb-state/bridge-poller/dispatch-state.json` in the repo: `gt platform doctor` (or its module-form equivalent) must produce PASS / WARN / FAIL based on `updated_at` staleness alone, not a false ALARM driven by missing recipient keys.

## Risk / Rollback

- **Risk:** very low. The change is a 1-character-class string substitution in a private helper map plus a paired test-fixture update; the doctor's downstream logic is untouched. No public API change; no on-disk schema change.
- **Concurrency:** no shared lock or shared mutable state is touched. The dispatch-state file is read-only from the doctor's perspective.
- **Rollback:** revert the doctor.py + test file in one git revert. The fix is fully self-contained inside two files. If the cross-harness trigger ever migrates back to legacy keys, the new TP8 test will catch the regression in the reverse direction.
- **Forward-compatibility:** the change aligns the doctor with the canonical role-label vocabulary that all newer reliability work assumes; aligning is a precondition for future single-shared-module hygiene.

## Recommended Commit Type

`fix:` — repair of broken behavior (false-ALARM doctor output) with no new capability surface. Diff stat: ≤ 20 lines net across 2 files.

## Open Decisions Required From Owner

None. The owner AUQ in S408 already authorized the PAUTH path and project membership; the fix is bounded by the standing PAUTH's allowed_mutation_classes (`source`, `test_addition`).

---

_© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved._
