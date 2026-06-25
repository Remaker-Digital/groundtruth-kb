NEW

# gtkb-run-with-status-worker-lifetime-timeout — Worker-lifetime timeout for run_with_status.py (Phase 0 reliability fix)

bridge_kind: prime_proposal
Document: gtkb-run-with-status-worker-lifetime-timeout
Version: 001
Author: Prime Builder (harness B / claude)
Date: 2026-06-24 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 36bd90f3-6d5f-4f15-8a6f-28e45ada52f0
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: default

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4806

target_paths: ["scripts/run_with_status.py", "platform_tests/scripts/test_run_with_status.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/run_with_status.py` wraps every dispatched harness subprocess and, at line ~82, calls a bare `p.wait()` with no timeout. When a wrapped harness hangs — a cloud provider returning a non-JSON body, an HTTP 502, or a stuck socket — the wrapper blocks forever and the process becomes immortal. These corpses accumulate until they cross the storm-watchdog's non-codex process threshold (15), which asserts the `GTKB_NO_CROSS_HARNESS_TRIGGER` kill-switch and halts dispatch (the WI-4670 root cause, and the cascade behind the kill-switch incident captured in `DELIB-20265877`).

This is the Phase 0 keystone of the dispatcher-completion program (`DELIB-20265882`, stabilize-first): making workers *mortal* is the precondition for safely correcting the watchdog and for reliable dispatch. The fix adds a fixed-default worker-lifetime timeout to the wait. On expiry it terminates the child **process tree** (on Windows `Popen.terminate()`/`kill()` do not reap grandchildren — use `taskkill /T /F` on the pid, or a Job Object), records a distinguishable timeout exit code (124, the coreutils `timeout` convention), and logs the timeout to stderr. The timeout is a fixed module-level default with no new env/config knob, keeping the change a pure defect fix; the Phase 2 daemon makes it configurable later.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — eligibility basis: origin=defect (WI-4806); no new public API/CLI/config surface beyond removing the hang defect (fixed default, no knob); no new/revised requirement; single-concern (~2 files, well under 150 net lines). Filed under `PROJECT-GTKB-RELIABILITY-FIXES`, covered by the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge integrity is the governing reliability mandate; an immortal-worker leak that halts dispatch directly threatens the bridge the protocol depends on.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites its governing specs and maps tests to them below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization / Project / Work Item metadata supplied above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping under the verification heading below.
- `GOV-STANDING-BACKLOG-001` — WI-4806 is the governing standing-backlog work item.

## Prior Deliberations

- `DELIB-20265882` — dispatcher target-architecture grill (2026-06-24): Phase 0 stabilizes the live fleet first; this worker-lifetime timeout is the named Phase 0 keystone that makes hung workers mortal.
- `DELIB-20265877` — kill-switch emergency-only directive: documents the watchdog→kill-switch cascade that immortal corpses trigger; this fix removes the corpse-accumulation cause.
- `DELIB-20264379` — Loyal Opposition review of the Ollama dispatch-stall retry cap: adjacent reliability work on the same dispatch substrate. No prior deliberation governs the `run_with_status.py` worker-lifetime timeout specifically.

## Owner Decisions / Input

No per-fix owner approval is required. This is a fast-lane defect fix authorized by the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` per `GOV-RELIABILITY-FAST-LANE-001`, which removes the per-fix deliberation/PAUTH/approval-packet requirement while preserving Loyal Opposition `GO` and `VERIFIED`. The Phase 0 sequencing was owner-directed ("Proceed to Phase 0") and is recorded in `DELIB-20265882`; no further owner decision gates this fix.

## Requirement Sufficiency

Existing requirements sufficient — the governing requirement is the reliability mandate (`GOV-FILE-BRIDGE-AUTHORITY-001` / bridge-essential.md: bridge integrity is top priority). This is a pure defect fix (an unbounded wait that leaks immortal processes); it introduces no new or revised requirement or specification.

## Spec-Derived Verification Plan

| Linked spec / requirement | Test / command | Expected result |
|---|---|---|
| Reliability mandate — workers must not hang forever (`GOV-FILE-BRIDGE-AUTHORITY-001`) | New pytest in `platform_tests/scripts/test_run_with_status.py`: wrap a child that sleeps well beyond the timeout | Child terminated within timeout + grace; wrapper returns the timeout exit code |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — distinguishable outcome | Same test asserts the status-file content | Status file records the timeout sentinel (124), not 0 or 127 |
| Process-tree reaping (Windows) | Test spawns a child that itself spawns a grandchild, then times out | Both child and grandchild are gone after the timeout (no orphan) |
| No regression | Existing `test_run_with_status.py` cases | All pass (normal exit, redirections, status-file write unchanged) |
| Code quality | `ruff check scripts/run_with_status.py` and `ruff format --check scripts/run_with_status.py` | Both clean |

Reproducible evidence command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py -q --no-header
```

## Risk / Rollback

Low risk — confined to a single wrapper module plus its test. Single-commit rollback = revert the diff; the wrapper returns to the prior bare-`wait()` behavior. The primary risk is Windows process-tree-kill correctness: a bare `Popen.terminate()` orphans grandchildren (a harness's node/python children), so the implementation must use `taskkill /T /F` on the pid (or a Job Object) and the test asserts the *tree* is reaped. A too-aggressive default would prematurely kill a legitimately slow worker; the fixed default is chosen generously (well above observed healthy worker lifetimes) and is revisited when the Phase 2 daemon makes it configurable.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-run-with-status-worker-lifetime-timeout`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs a reliability defect (unbounded wait leaking immortal processes); adds a regression test but no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
