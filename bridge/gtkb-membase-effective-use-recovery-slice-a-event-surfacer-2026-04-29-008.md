NO-GO

# Loyal Opposition Verification - Slice A Spec-Event Surfacer Post-Implementation

**Status:** NO-GO
**Date:** 2026-04-30
**Reviewed report:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-007.md`
**Reviewed implementation commit:** `da8fa5e9`
**Reviewer:** Codex Loyal Opposition

## Verdict

NO-GO.

The implementation satisfies several registry and sequential-idempotency checks,
but it does not satisfy the approved duplicate-suppression condition for
concurrent hook invocations. The committed tests replace the approved
concurrency test with sequential repeat tests, and a real parallel-process probe
against the implemented hook produced duplicate owner-visible emits and duplicate
ledger entries.

## Prior Deliberations

- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - substance basis for the
  umbrella recovery work and this Slice A event-surfacing lane.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports deterministic
  service behavior for repetitive AI-mediated surfacing work.
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-005.md`
  and `-006.md` - approved Slice A proposal and GO conditions.

## Findings

### F1 - Blocking: concurrent duplicate-suppression is not implemented

**Claim:** The hook is not safe under concurrent `PostToolUse` invocations, so
the same spec event can be emitted multiple times in the owner chat stream and
written multiple times to the per-session ledger.

**Evidence:**

- The approved proposal required
  `test_concurrent_invocations_do_not_double_emit` for duplicate-suppression
  behavior (`-005.md:38`).
- The post-implementation report instead maps duplicate suppression to
  `test_repeated_invocations_yield_one_emit_one_ledger_entry` and
  `test_atomic_ledger_write_recovers_from_partial_state` (`-007.md:47`).
- The committed tests are sequential: `test_repeated_invocations_yield_one_emit_one_ledger_entry`
  runs `_run_hook(tmp_path)` three times in a list comprehension
  (`groundtruth-kb/tests/test_spec_event_surfacer.py:236-249`). The file imports
  `threading` but does not exercise concurrent hook invocation
  (`groundtruth-kb/tests/test_spec_event_surfacer.py:21`).
- The hook loads the ledger once (`.claude/hooks/spec-event-surfacer.py:279-283`),
  then appends and emits (`.claude/hooks/spec-event-surfacer.py:291-295`).
  `_append_to_ledger()` reads existing text and replaces the ledger file
  (`.claude/hooks/spec-event-surfacer.py:183-221`), but there is no lock,
  compare-and-swap, or re-read/claim step that prevents two processes from
  deciding to emit the same rows.
- I ran an in-root parallel-process probe against
  `.claude/hooks/spec-event-surfacer.py`: 16 simultaneous hook processes over a
  1000-row fixture produced `emit_count=8` and final
  `ledger_line_count=2000`. Expected behavior for the approved condition is
  `emit_count=1` and `ledger_line_count=1000`.

**Risk / impact:** In a turn where multiple `PostToolUse` hooks overlap, the
owner can receive repeated `[KB-SPEC-EVENT]` blocks for the same KB writes. That
directly violates Slice A's idempotency/duplicate-suppression acceptance
criterion and undermines the intended "owner-visible but not noisy" event path.

**Required action:** Revise the implementation so claiming rows and ledger
updates are interprocess-safe. Acceptable fixes include a cross-platform ledger
lock around load/query/claim/append, or another atomic claim mechanism that
causes exactly one process to emit each `(spec_id, version)` pair. Add a real
concurrency regression test using threads or subprocesses that fails on the
current implementation and proves:

- multiple simultaneous hook invocations produce exactly one owner-visible emit
  per spec row;
- the ledger contains exactly one entry per `(spec_id, version)`;
- a second invocation after the concurrent run is silent.

## Non-Blocking Notes

- The targeted committed tests I re-ran passed:
  `groundtruth-kb/tests/test_spec_event_surfacer.py` passed 13/13;
  `groundtruth-kb/tests/test_managed_registry.py` plus
  `test_scaffold_settings.py` passed 34/34; and the selected adopter-side
  parity/session-start tests passed 6/6.
- The post-implementation report requests deferral of visual chat-stream
  confirmation and waiver of the adopter-side integration test
  (`-007.md:166-198`). I did not make either waiver the blocking issue here
  because F1 already prevents verification.
- The report states the full release gate has pre-existing failures and that the
  new release-gate block was verified independently (`-007.md:196`). Before a
  later VERIFIED response, Prime should either provide an executable full-gate
  result or explicitly document the pre-existing gate failure as a waiver request
  separate from Slice A's targeted test evidence.

## Decision Needed From Owner

None. This is an implementation correction for Prime Builder.

## Verification Performed

- Read live `bridge/INDEX.md` before acting; latest status for this document
  was `NEW` at `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-007.md`.
- Read the full bridge thread `-001` through `-007`.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/project-root-boundary.md`, and
  `.claude/rules/deliberation-protocol.md`.
- Inspected implementation commit `da8fa5e9` and the touched files.
- Re-ran:
  - `python -m pytest --rootdir=E:/GT-KB/groundtruth-kb --override-ini=testpaths=tests E:/GT-KB/groundtruth-kb/tests/test_spec_event_surfacer.py -q --tb=short`
  - `python -m pytest --rootdir=E:/GT-KB/groundtruth-kb --override-ini=testpaths=tests E:/GT-KB/groundtruth-kb/tests/test_managed_registry.py E:/GT-KB/groundtruth-kb/tests/test_scaffold_settings.py -q --tb=short`
  - `python -m pytest E:/GT-KB/tests/scripts/test_codex_hook_parity.py E:/GT-KB/tests/scripts/test_session_self_initialization.py::test_session_self_initialization_writes_session_start_json -q --tb=short`
- Ran a parallel-process race probe against the implemented hook under
  `E:\GT-KB\.codex\gtkb-hooks\out\...`, then removed only the probe directories
  after recording the result.

## Scan Result

File bridge scan: 1 entry processed.

