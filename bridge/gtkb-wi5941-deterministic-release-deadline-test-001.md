NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5941-deterministic-release-deadline-test
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5941

target_paths: ["platform_tests/scripts/test_bridge_work_intent_registry.py"]

# WI-5941 - Make the release/commit deadline test deterministic under suite load

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. The single target
`platform_tests/scripts/test_bridge_work_intent_registry.py` is an in-root path,
and this bridge file resides under `E:/GT-KB/bridge/`. No generated artifact is
written outside the project root.

## Problem Statement

`platform_tests/scripts/test_bridge_work_intent_registry.py::test_release_commit_wait_cannot_outlive_total_deadline`
is order- and load-dependent. Observed 2026-08-05 during the WI-5939 regression
run:

| Invocation | Result | Elapsed |
| --- | --- | --- |
| Combined with `test_bridge_publication_finalization_atomicity.py` | **1 failed**, 57 passed, 2 skipped | 13.15s |
| Same test in isolation | 1 passed | 1.32s |
| Identical combined command, immediately re-run | 58 passed, 2 skipped | 9.45s |

The test (line 1183) drives a real worker thread against a real SQLite write
lock and arbitrates the outcome with wall-clock windows:

```
assert not completed.wait(0.05)
time.sleep(0.25)
blocker.rollback()
completed_before_reader_release = completed.wait(0.3)
...
assert completed_before_reader_release
```

The load-bearing assertion is `completed_before_reader_release`: the release must
finish while the reader still holds its lock, proving the release did not simply
wait for the reader to go away. But the evidence for that ordering is a **0.3s
race against thread scheduling**. Under suite load the worker can miss that
window without any behavioural defect, so the test reports a false failure.

An intermittently red suite is worse than a slow one: it trains reviewers to
discount regression failures, which is precisely the condition under which a real
regression passes unnoticed.

## Why This Is a Gap, Not a New Idea

WI-5784 (commit `277630edb`, "deterministic deadline-exhaustion test nodes
(logical monotonic clock)") already established the remedy **inside this same
module**. It added:

```
def _install_logical_monotonic_clock(monkeypatch, env) -> list[float]:
    """Install a controllable logical monotonic clock for deterministic deadline tests.

    WI-5784: replace the wall-clock ``_monotonic``/``_retry_sleep`` with a
    logical clock the fixture advances explicitly, so deadline exhaustion is
    ...
```

at line 805, and converted several deadline tests to it (lines 1020, 1078,
1383). `test_release_commit_wait_cannot_outlive_total_deadline` was **not**
converted and still arbitrates on wall-clock windows. This proposal closes that
remaining gap using the pattern already accepted in this module, rather than
introducing a new testing approach.

This also aligns with the owner timer/concurrency direction: hard-coded timing
constants in tests should give way to deterministic, governed control
(`DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE`,
`DELIB-20260801-TIMER-CONCURRENCY-SOT-DIRECTION`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files are the canonical append-only
  audit trail governing this proposal artifact and its thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section
  discharges the proposal spec-linkage obligation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan below maps
  each preserved behavioural clause to a concrete executed test.
- `SPEC-1662` (GOV-18 Assertion Quality Standard: meaningfulness over coverage) -
  the repair must preserve the assertion's meaning, not weaken it into a test
  that passes vacuously.
- `GOV-07` (no bug fixes during testing procedures) and `GOV-15` (test fix
  approval gate) - this test change is proposed through the governed cycle with
  owner authorization rather than applied opportunistically mid-run.
- `.claude/rules/bridge-essential.md` - work-intent claim/release is
  bridge-critical infrastructure; its regression coverage must stay trustworthy.
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE` and
  `DELIB-20260801-TIMER-CONCURRENCY-SOT-DIRECTION` - owner direction to remove
  hard-coded timing and converge on deterministic governed control.
- `DELIB-202667721` - owner decision behind the whole-project authorization.

## Prior Deliberations

- WI-5784 / commit `277630edb` - the in-module precedent
  (`_install_logical_monotonic_clock`) this proposal extends to the remaining
  wall-clock test.
- `DELIB-20260801-TIMER-CONCURRENCY-SOT-DIRECTION` - "When inspection establishes
  a timer as too short, capture a corrective work item; converge hard-coded
  timing." WI-5941 is that corrective work item for this test.
- `DELIB-202666540` (WI-5336 fresh-worker built-wheel timeout, GO) - prior
  accepted treatment of a timeout-sensitive test surface.
- WI-5939 thread (`bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-003.md`
  and `-005.md`) - where this flake was observed and disclosed rather than
  absorbed.

## Requirement Sufficiency

Existing requirements sufficient. The assertion-quality standard (`SPEC-1662`),
the test-fix approval gate (`GOV-15`), and the owner timer/concurrency direction
already govern this change. No new requirement is implied.

## Proposed Change

Single target file; test-only change. No production code is touched.

### C1 - Remove the scheduling race from the ordering assertion

Restructure the test so the ordering claim ("release completed while the reader
still held its lock") is guaranteed by program structure rather than by a
wall-clock window: wait for worker completion with a generous bound while the
reader lock is still held, and only release the reader afterwards. The assertion
then proves the same property without depending on the worker being scheduled
within 0.3s.

### C2 - Adopt the established logical monotonic clock

Apply `_install_logical_monotonic_clock` (the WI-5784 helper already in this
module) so the release path's deadline arithmetic advances logically rather than
by wall-clock sleeping, matching the sibling deadline tests at lines 1020, 1078,
and 1383.

### C3 - Preserve the deadline semantic explicitly

Keep an explicit assertion that the release respected the total deadline budget,
expressed against the injected logical clock rather than measured wall time, so
the test still fails if the release is allowed to outlive its deadline. This is
the anti-vacuity requirement: the repaired test must still fail on the defect it
was written to catch.

## Test Plan (specification-derived)

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | SPEC-1662 (meaningfulness) | the repaired test still FAILS when the release is permitted to outlive the total deadline (demonstrated in a scratch run by relaxing the deadline bound; evidence reported, no committed change) |
| T2 | bridge-essential (release must not depend on the blocker clearing) | release completes while the reader still holds its lock, asserted by structural ordering rather than a timing window |
| T3 | DELIB-20260801 timer direction | no wall-clock sleep/wait window arbitrates the pass/fail outcome of this test node |
| T4 | GOV-18/SPEC-1662 stability | the test passes in isolation and in combination, repeatedly |

Commands to be executed and reported in the implementation report:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest "platform_tests/scripts/test_bridge_work_intent_registry.py::test_release_commit_wait_cannot_outlive_total_deadline" -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_bridge_work_intent_registry.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_bridge_work_intent_registry.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_bridge_work_intent_registry.py
```

The combined-suite command will be executed **at least five consecutive times**
and all five results reported, since a single green run is not evidence that an
intermittent failure is resolved.

## Acceptance Criteria

1. The pass/fail outcome of this test node is not arbitrated by a wall-clock
   window.
2. The ordering property (release completes while the reader holds its lock) is
   still asserted.
3. The deadline property is still asserted and still fails when violated (T1).
4. Five consecutive combined-suite runs pass.
5. `ruff check` and `ruff format --check` pass on the target file.
6. No production code changed; no other test node's behaviour altered.

## Risk and Rollback

- **Risk: weakening the assertion into vacuity.** This is the main hazard of
  "fixing" a flaky test. Mitigated by T1, which requires demonstrating the
  repaired test still fails on the defect it guards.
- **Risk: the flake is a real intermittent defect in release/commit, not a test
  artifact.** Evidence against: the test passes in isolation and on immediate
  re-run of the identical command, and the failure correlates with suite elapsed
  time. If T1 or the repeated runs surface a genuine intermittent product defect,
  this proposal stops and a separate defect work item is filed rather than
  masking it.
- **Rollback:** single test file; revert the file.

## Owner Decisions / Input

- **Owner directive 2026-08-06 (this session):** "Proceed with WI-5941 and Slice
  B" - authorizes preparing this proposal now, in parallel with the WI-5939
  verification cycle.
- **AUQ 2026-08-05 (close-out path):** owner selected "One more cycle with the
  checklist" for WI-5939, leaving WI-5941 and Slice B free to advance
  independently.
- **`GOV-15` test fix approval gate:** this proposal is the governed request for
  approval to modify a failing test; the change is not applied until GO.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization
  covering WI-5941 as an active member work item.

## Recommended Commit Type

`test:` - the change is confined to a test module and alters no production
behaviour.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
