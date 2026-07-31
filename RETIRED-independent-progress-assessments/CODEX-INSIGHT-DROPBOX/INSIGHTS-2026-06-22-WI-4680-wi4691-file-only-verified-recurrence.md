# WI-4680 Recurrence: WI-4691 VERIFIED Commit Contains Only Verdict

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-4680, WI-4691

## Claim

The WI-4691 bridge thread now has a terminal `VERIFIED` verdict, but the commit that recorded that verdict contains only the verdict file. The verified implementation report and dirty implementation paths remain outside that commit in the current worktree. This is a fresh recurrence of open P0 `WI-4680` ("Make LO VERIFIED verdict recording atomic with final commit").

## Evidence

- `git show --name-status --oneline ca5f24774` reports only:
  - `A bridge/gtkb-wi4691-quality-first-spillover-dispatch-004.md`
- `bridge/gtkb-wi4691-quality-first-spillover-dispatch-004.md` line 1 is `VERIFIED`, line 7 says it reviewed `bridge/gtkb-wi4691-quality-first-spillover-dispatch-003.md`, and lines 14-16 claim the implementation and tests passed.
- Current worktree state still shows WI-4691 implementation/report artifacts outside that verdict commit:
  - `M groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
  - `M platform_tests/scripts/test_bridge_dispatch_config.py`
  - `M scripts/cross_harness_bridge_trigger.py`
  - `?? bridge/gtkb-wi4691-quality-first-spillover-dispatch-003.md`
- Live backlog already contains `WI-4680` as open P0 with the exact defect statement: VERIFIED should be valid only when verified work and verdict are finalized by the same verification transaction.

## Risk / Impact

This leaves the bridge thread terminal while the implementation evidence is still not atomically tied to that terminal verdict. A later sweep, conflict, or checkout could preserve the verdict without the implementation report/source changes it claims to verify. That weakens the bridge audit trail and can make backlog reconciliation trust a terminal state that does not actually identify a complete implementation commit.

## Recommended Action

Do not create a duplicate work item. Keep `WI-4680` as the owning P0 repair and use this WI-4691 event as regression evidence for its implementation proposal and tests.

Prime Builder should ensure the eventual WI-4680 fix rejects or quarantines any `VERIFIED` bridge file when the committing transaction does not include the reviewed implementation report and dirty verified paths, including verdicts authored outside the Codex helper path.

## Decision Needed From Owner

None. This is already covered by open P0 backlog work.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
