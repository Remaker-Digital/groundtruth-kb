GO

# Loyal Opposition Review - Smart-Poller Auto-Trigger Spec + Incident Remediation

**Document:** `spec-smart-poller-auto-trigger-2026-04-29`
**Reviewed version:** `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md`
**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-29

## Claim

The proposal is narrow enough to proceed. It files the missing auto-trigger contract, wires already-existing dispatch tests into an executed lane, and extends the smart-poller doctor check to cover the incident class that actually escaped: a live daemon running without dispatch.

## Evidence

- The live bridge index still listed this thread as latest `NEW` before review.
- The proposal includes a `Specification Links` section and maps tests to the proposed DCL assertions: `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md:8`, `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md:24`.
- Existing dispatch tests cover no-work/no-spawn and pending-work/single-spawn behavior: `groundtruth-kb/tests/test_bridge_poller_runner.py:91`, `groundtruth-kb/tests/test_bridge_poller_runner.py:106`.
- Existing doctor coverage already exercises the smart-poller activation surface: `groundtruth-kb/tests/test_doctor_smart_poller.py:99`, `groundtruth-kb/tests/test_doctor_smart_poller.py:304`.
- Current doctor implementation verifies runner, PS1 helper, VBS launcher, scheduled-task target, audit freshness, duplicate runner state, and notification freshness, but it does not inspect `--no-dispatch` or `dispatch-state.json`: `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1381`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1551`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1684`.

## Verification Performed

- `python -m pytest groundtruth-kb/tests/test_bridge_poller_runner.py -q --tb=short` -> 15 passed.
- `python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short` -> 14 passed.

## GO Conditions

1. Do not mutate the live GT-KB scheduled task as the primary regression test for `--no-dispatch`. Cover that assertion with a mocked/synthetic scheduled-task action or a disposable test task. If a live-task smoke check is still needed, it must be scripted with deterministic restore and the post-implementation report must show the restore verification.
2. The post-implementation report must carry forward the linked specs, the DCL assertion-to-test mapping, exact commands, and observed results. The new doctor tests must explicitly cover both `--no-dispatch` detection and stale/missing dispatch-state evidence with pending work.
3. Treat `DCL-TEST-SPEC-DERIVATION-001` as provisional until the platform-level bridge actually files it. The docstring citation format proposed here is acceptable as a local convention, but it must not be claimed as enforcement from a not-yet-filed DCL.
4. When adding `groundtruth-kb/tests/test_bridge_poller_runner.py` to `scripts/release_candidate_gate.py`, verify the release gate invokes it from a context where its imports/path loading work. The post-implementation report must show either the full release gate result or a targeted command plus evidence that the file is included in the gate list.

## Risk / Impact

The core risk is real and high: a running poller that never dispatches can make the bridge look operational while requiring owner intervention. The proposed DCL plus doctor checks are the right incident-narrow control. The only substantial risk in the proposal is live-task validation; the GO conditions above keep the regression test from becoming a second outage vector.

## Decision Needed From Owner

None.

