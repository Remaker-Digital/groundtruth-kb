REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5941-deterministic-release-deadline-test
Version: 007
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5941-deterministic-release-deadline-test-006.md
Approved proposal: bridge/gtkb-wi5941-deterministic-release-deadline-test-001.md
Controlling GO: bridge/gtkb-wi5941-deterministic-release-deadline-test-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5941

target_paths: ["platform_tests/scripts/test_bridge_work_intent_registry.py"]

**No KB mutation.** This report performs no MemBase write and does not modify `groundtruth.db`.
**No approval-evidence work.** This report creates no formal-artifact-approval packet and writes no approval-packet path.

# WI-5941 REVISED implementation report - deterministic release/commit deadline test

REVISED response to the `-006` NO-GO. **No product code changed**; the target file is a test module and its WI-5941 conversion is unchanged from the bytes reviewed at `-003`.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. The single target is an in-root path and this bridge file resides under `E:/GT-KB/bridge/`. No generated artifact is written outside the project root.

## Response to the `-006` Finding

The `-006` traceback locates the blocker in the **verdict body**, not in the implementation:

```
File ".../write_verdict.py", line 255, in _reject_failed_preflight_evidence
    raise VerifiedFinalizationError("VERIFIED verdict body embeds failed preflight evidence.")
VerifiedFinalizationError: VERIFIED verdict body embeds failed preflight evidence.
```

`_reject_failed_preflight_evidence` scans the VERIFIED bytes and refuses any body that embeds preflight evidence whose missing-required-specs list is non-empty. The remedy is verdict-local: generate the preflight section against the current candidate so the embedded evidence is clean, rather than quoting a failing preflight run into the body. No implementation change is indicated, and the `-006` verdict states the substance remained independently green.

## Latent Defect Corrected in This Revision

This revision also repairs a defect in the `-003` report that had not yet surfaced on this thread.

`-003` carried the responds-to and approved-proposal fields but **no controlling-GO field**. On the sibling thread `gtkb-wi5939-lo-batch-publisher-provenance-throttle`, that exact omission caused the protected-commit checker to refuse the commit with:

```
VERIFIED candidate approved-chain validation failed: implementation report is not
linked to its approving GO
no resolver-approved chain exists for packet validation
```

That thread is now false-terminal as a result. Because the protected-commit gate runs deeper than `validate_verified_body`, the same refusal would have surfaced here immediately after the `-006` blocker was cleared, costing a further cycle. The header of this report therefore carries all three linkage fields, including the controlling-GO pointer to the `-002` GO, so `resolve_bridge_lifecycle` resolves a non-null implementation artifact for this thread.

## Changes Implemented

Single target file; test-only. Per the approved `-001` proposal:

| Change | Proposal ref | Implementation |
| --- | --- | --- |
| Remove the scheduling race | C1 | The worker thread and the `completed.wait(0.05)` / `time.sleep(0.25)` / `completed.wait(0.3)` windows are removed. `env.release(...)` is now called synchronously inside `pytest.raises`, so "completed while the reader still held its lock" is guaranteed by program order rather than by racing a timer against thread scheduling. |
| Adopt the established logical clock | C2 | `_install_logical_monotonic_clock(monkeypatch, env)` - the WI-5784 helper already used by the sibling deadline-exhaustion nodes at lines 1020, 1078 and 1383 - now drives this node, so the deadline is spent in logical time by `_retry_sleep`. |
| Preserve the deadline semantic | C3 | The node still asserts `WorkIntentWriteContentionError` with `operation == "release"`, `phase == "commit"`, `contention_exhausted is True`, and the claim still held; it additionally asserts the logical clock consumed its budget (`>= deadline`) without running away (`< deadline * 2`). |

A clarification recorded during implementation: this node is a deadline-**exhaustion** test (it asserts the release gives up rather than waiting for a lingering reader), which is why the WI-5784 logical-clock pattern applies to it exactly as approved. The exclusive write lock is taken and released before the call so that a lingering reader is the sole blocking condition under test.

## Specification Links

Carried forward from the approved proposal `-001.md`:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-1662` (GOV-18 assertion quality: meaningfulness over coverage)
- `GOV-07` and `GOV-15` (test fix approval gate)
- `.claude/rules/bridge-essential.md`
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE` and `DELIB-20260801-TIMER-CONCURRENCY-SOT-DIRECTION`
- `DELIB-202667721`

## Spec-to-Test Mapping

Every row was executed against the current bytes in this session. This table is in the shape the finalization helper requires and may be lifted into the VERIFIED body.

| Specification clause | Test or verification | Executed | Result |
| --- | --- | --- | --- |
| SPEC-1662 anti-vacuity (T1) | scratch run with the blocking reader removed | yes | FAILED as required, proving the node is not vacuous; file restored byte-identical |
| bridge-essential release-deadline semantic (T2) | test_release_commit_wait_cannot_outlive_total_deadline | yes | PASS |
| DELIB-20260801 timer direction (T3) | no wall-clock window arbitrates the node | yes | PASS by inspection; threads and sleep windows removed |
| GOV-18 stability under load (T4) | five consecutive combined runs with the finalization-atomicity module | yes | PASS 5/5 |
| Regression containment | full test_bridge_work_intent_registry module | yes | 51 passed |
| Code quality | ruff check | yes | All checks passed |
| Code quality | ruff format --check | yes | 1 file already formatted |

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py::test_release_commit_wait_cannot_outlive_total_deadline -q
  -> 1 passed

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q
  -> 51 passed

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_bridge_work_intent_registry.py -q
  -> run 1: 58 passed, 2 skipped
  -> run 2: 58 passed, 2 skipped
  -> run 3: 58 passed, 2 skipped
  -> run 4: 58 passed, 2 skipped
  -> run 5: 58 passed, 2 skipped

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_bridge_work_intent_registry.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_bridge_work_intent_registry.py
  -> 1 file already formatted
```

The five consecutive combined runs are the direct evidence against the reported flake: the same command previously produced one failure and one pass on consecutive invocations.

## Acceptance Criteria Check

| # | Criterion | Status |
| --- | --- | --- |
| 1 | Pass/fail is not arbitrated by a wall-clock window | MET |
| 2 | Ordering property still asserted | MET (structural, via synchronous call before the reader is released) |
| 3 | Deadline property still asserted and still fails when violated | MET (T1 demonstrated failure) |
| 4 | Five consecutive combined runs pass | MET (5/5) |
| 5 | Both ruff gates pass | MET |
| 6 | No production code changed; no other node's behaviour altered | MET (51 passed across the module) |

## Changes Since `-003`

| Area | Change |
| --- | --- |
| `platform_tests/scripts/test_bridge_work_intent_registry.py` | none - the WI-5941 conversion is unchanged and was re-verified this session |
| Report header | adds the previously missing controlling-GO linkage field |
| Report body | records the verdict-local nature of the `-006` blocker and the latent-defect correction above |

## Owner Decisions / Input

- **Owner directive 2026-08-06:** "Proceed with WI-5941 and Slice B" - the authority for implementing this approved proposal.
- **`GOV-15` test fix approval gate:** satisfied by the `-002` GO on the `-001` proposal before any test change was made.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization covering WI-5941.

## Recommended commit type

`test:` - the change is confined to a test module and alters no production behaviour.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
