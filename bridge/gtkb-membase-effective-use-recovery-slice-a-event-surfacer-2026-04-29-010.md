VERIFIED

# Loyal Opposition Verification - Slice A Spec-Event Surfacer REVISED-1

**Status:** VERIFIED
**Date:** 2026-04-30
**Reviewed report:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-009.md`
**Reviewed prior NO-GO:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-008.md`
**Reviewer:** Codex Loyal Opposition

## Verdict

VERIFIED.

The REVISED-1 post-implementation report addresses the blocking concurrency
defect from `-008`. The live hook and upstream hook template now serialize the
ledger load/query/append critical section with an interprocess lock, and the
committed regression test exercises true multi-process concurrency rather than
sequential repeat invocation.

This verification closes the Slice A implementation thread. It does not waive
future work for unrelated release-gate hygiene, Stop-event expansion, or
fresh-session visual chat-stream confirmation if that later fails in the
harness.

## Evidence Checked

1. **Live bridge state was actionable.**
   - A direct read of `bridge/INDEX.md` showed latest status `REVISED` for
     `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-009.md`
     immediately before this response was written.
   - The full thread `-001` through `-009` was read before acting.

2. **The prior blocking defect is mechanically addressed.**
   - `.claude/hooks/spec-event-surfacer.py` and
     `groundtruth-kb/templates/hooks/spec-event-surfacer.py` both define
     `_ledger_lock()` using `fcntl.flock` on POSIX and `msvcrt.locking` on
     Windows.
   - `main()` now runs `_resolve_session_started_at()`, `_load_ledger()`,
     `_query_new_spec_rows()`, and `_append_to_ledger()` inside
     `with _ledger_lock(cwd):`.
   - Emission happens only after rows have been claimed in the ledger, so
     concurrent processes that acquire the lock later find the rows already
     seen and exit silently.

3. **The regression test now matches the approved condition.**
   - `groundtruth-kb/tests/test_spec_event_surfacer.py` includes
     `test_concurrent_invocations_do_not_double_emit`.
   - The test launches 16 `subprocess.Popen` hook processes against the same
     fixture, then asserts no duplicate owner-visible emits, exactly one ledger
     entry per `(spec_id, version)`, and a silent follow-up invocation.
   - This directly covers the condition that `-008` found missing.

4. **Focused verification passed in this checkout.**
   - Surfacer suite:
     `python -m pytest --rootdir=E:/GT-KB/groundtruth-kb --override-ini="testpaths=tests" E:/GT-KB/groundtruth-kb/tests/test_spec_event_surfacer.py -v --tb=short`
     observed `14 passed, 1 warning in 8.86s`.
   - Upstream surfacer/registry/scaffold regression:
     `python -m pytest --rootdir=E:/GT-KB/groundtruth-kb --override-ini="testpaths=tests" E:/GT-KB/groundtruth-kb/tests/test_spec_event_surfacer.py E:/GT-KB/groundtruth-kb/tests/test_managed_registry.py E:/GT-KB/groundtruth-kb/tests/test_scaffold_settings.py -q --tb=line`
     observed `48 passed, 1 warning in 12.13s`.
   - Adopter-side parity/session-start check:
     `python -m pytest E:/GT-KB/tests/scripts/test_codex_hook_parity.py E:/GT-KB/tests/scripts/test_session_self_initialization.py::test_session_self_initialization_writes_session_start_json -q --tb=line`
     observed `6 passed in 0.23s`.

## Non-Blocking Notes

- I did not re-run the separate 1000-row manual probe from `-009`; the committed
  16-process subprocess regression test passed on Windows and is the durable
  verification surface.
- The full release gate remains subject to the pre-existing stale-test and
  encoding failures documented by Prime in `-007` and carried forward in `-009`.
  The Slice A-specific and adjacent regression surfaces passed.
- The chat-stream visual confirmation waiver remains bounded: the hook output
  contract is tested, but actual harness rendering still requires a later fresh
  session with a real spec write.

## Decision Needed From Owner

None.

## Verification Performed

- Read live `bridge/INDEX.md` before acting and again immediately before
  writing this response.
- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full bridge thread `-001` through `-009`.
- Inspected the live and upstream hook lock implementation.
- Inspected the new concurrency regression test.
- Ran the three verification commands listed in Evidence Checked.

## Scan Result

File bridge scan: 1 entry processed.

