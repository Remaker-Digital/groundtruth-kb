NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 2026-06-07T01-02-49Z-prime-builder-transcript-scan-p1
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop Prime Builder; owner-directed PROJECT-GTKB-RELIABILITY-FIXES P1 chase-through
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Active Session Heartbeat Retries Transient Windows Replace Access Denied (WI-4392)

bridge_kind: implementation_proposal
Document: gtkb-heartbeat-replace-access-denied-retry
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Codex Prime Builder
Date: 2026-06-07 UTC
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4392
target_paths: ["scripts/active_session_heartbeat.py", "platform_tests/scripts/test_active_session_heartbeat.py"]
Recommended commit type: fix:

## Claim

The active-session heartbeat hook writes a temp file and calls os.replace once. On Windows, the last-24h transcript scan found 9 Access denied errors during tmp-to-lock replacement. The script exits 0 by fire-and-forget contract, so tool calls are not hard-blocked, but hook stderr noise recurs and the active-session suppression lock can remain stale or absent.

Existing WI-3360 fixed non-atomic writes and stale collision files. This proposal handles the remaining post-atomic Windows replace race with a bounded retry/backoff around os.replace.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-RELIABILITY-FAST-LANE-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-SMART-POLLER-AUTO-TRIGGER-001
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001

## Reliability Fast-Lane Eligibility

1. Origin defect/regression: met. WI-4392 is a transcript-observed hook reliability defect.
2. No new public API/CLI: met. The implementation changes internal retry behavior and tests only.
3. No forbidden operations: met. No deploy, force-push, spec deletion, or data migration.
4. Small single-concern scope: met. One heartbeat write path and one focused regression test.

## Prior Deliberations

- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: standing reliability fast-lane direction and PAUTH basis.
- bridge/gtkb-cross-harness-trigger-import-repair was the prior resolved thread for import/bootstrap and non-atomic lock-write issues; this proposal explicitly handles the remaining post-atomic Windows replace race.
- WI-4392 transcript-scan evidence: owner-requested scan on 2026-06-06 captured 9 Access denied heartbeat errors.

## Owner Decisions / Input

No new owner decision required. Mike explicitly directed this session to elevate these PROJECT-GTKB-RELIABILITY-FIXES items and chase them through to completion. The standing PAUTH covers small source/test reliability fixes by active project membership.

## Scope

IP-1: Add bounded retry/backoff around the os.replace call in scripts/active_session_heartbeat.py:_atomic_write_json, catching transient PermissionError and preserving the existing fire-and-forget behavior if all attempts fail.

IP-2: Add a focused test that monkeypatches os.replace to raise PermissionError once, verifies the retry path succeeds, and confirms the lock file is written.

## Out Of Scope

- Changing heartbeat file names, state-dir registration, active-session suppression semantics, or cross-harness trigger dispatch selection.
- Adding CLI flags or new public behavior.
- Weakening the fire-and-forget contract.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 / ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Heartbeat write remains reliable enough for active-session suppression; transient Windows replace failures are retried. |
| GOV-RELIABILITY-FAST-LANE-001 | Manual target-path inspection confirms source + test-only, one-concern fast-lane scope. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Post-implementation report will carry executed pytest/ruff evidence. |

Implementation verification will run:

- python -m pytest platform_tests/scripts/test_active_session_heartbeat.py -q --tb=short
- python -m ruff check scripts/active_session_heartbeat.py platform_tests/scripts/test_active_session_heartbeat.py
- python -m ruff format --check scripts/active_session_heartbeat.py platform_tests/scripts/test_active_session_heartbeat.py

## Acceptance Criteria

- [ ] Loyal Opposition returns GO.
- [ ] _atomic_write_json retries transient PermissionError from os.replace with bounded backoff.
- [ ] The existing fire-and-forget main() behavior remains intact when writes ultimately fail.
- [ ] Focused regression test simulates a transient PermissionError and passes after retry succeeds.
- [ ] Post-implementation report carries observed verification commands and results.
- [ ] Loyal Opposition returns VERIFIED before WI-4392 is closed.

## Risk And Rollback

Risk is low: the change only retries the existing atomic replacement path. Rollback is file-level revert of the retry loop and test. If all retry attempts fail, the existing fire-and-forget top-level behavior still reports stderr and exits 0.
