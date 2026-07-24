# Per-Thread Finalization Repair

This runbook supports `scripts/per_thread_finalization_repair.py`, a report-only
planner for the WI-5116 worktree sprawl repair path.

## Invariant

One thread gets one finalization decision at a time. A finalization commit must
contain exactly the verified implementation/report paths plus the terminal
verdict artifact for that one thread. Do not use `git add -A`, broad sweep
commits, stash/drop cleanup, untracked-file deletion, dispatcher mutation, or
status rewriting to drain the sprawl.

The normal positive finalization actuator remains:

```powershell
python .claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified --slug <slug> --body-file <reviewed-verdict-body> --commit-message "<type(scope): subject>" --include <verified-path>
```

For already-written terminal verdicts, use only the approved project finalizer
or another independently reviewed equivalent path. The planner does not stage,
commit, delete, revert, push, mutate dispatcher state, update PAUTH, or author
bridge statuses.

## Baseline Command

Always use expanded untracked paths. A collapsed `git status --porcelain` count
can hide hundreds of files under untracked directories.

```powershell
python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330
```

Use markdown for operator reading:

```powershell
python scripts/per_thread_finalization_repair.py --format markdown --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330
```

## Classes

- `terminal_verified_repair_candidate`: latest status is `VERIFIED`, the
  verdict points at a readable report, target paths are parseable, and those
  target paths are clean at runtime, and the terminal verdict body is accepted
  by the canonical finalizer's evidence-floor validation. Re-run immediately
  before acting, then use the approved per-thread finalization path.
- `terminal_verified_blocked_invalid_verdict_body`: latest status is
  `VERIFIED`, target paths are parseable and clean, but the terminal verdict
  body fails `write_verdict.validate_verified_body()`. Stop; route through a
  bounded archive/remove repair and have Loyal Opposition reissue `VERIFIED`
  through `write_verdict.py --finalize-verified` with a helper-valid body.
- `terminal_verified_blocked_dirty_targets`: latest status is `VERIFIED`, but
  one or more implementation/report target paths are still dirty or untracked.
  Stop and resolve that thread's source ownership first.
- `terminal_verified_blocked_missing_scope`: latest status is `VERIFIED`, but
  the verdict/report linkage or target paths cannot be proven. Stop; do not
  infer target paths from prose.
- `terminal_withdrawn_or_nonverified_documentation`: latest status is terminal
  but not `VERIFIED`. Treat as documentation/protocol cleanup only after a
  separate review.
- `in_flight_bridge_chain`: latest status is `NEW`, `GO`, `NO-GO`, `REVISED`,
  `NO-ACTION`, `ADVISORY`, or `DEFERRED`. Do not finalize as implementation
  work.
- `excluded_active_program`: the thread matches an explicitly excluded active
  handoff, such as WI-5320/WI-5328/WI-5330.
- `mixed_provenance_stop`: ownership is ambiguous, unsupported, unattributed,
  shared by multiple dirty terminal threads, or attached to a tracked modified
  or deleted terminal `VERIFIED` verdict. Stop and ask for owner or bridge
  disposition.

## STOP Conditions

Stop immediately when:

- More than one thread claims the same dirty source/test/config path.
- A dirty source/test/config path is not attributable to exactly one terminal
  verified thread.
- A latest bridge status is in flight rather than terminal `VERIFIED`.
- A terminal `VERIFIED` body fails the canonical finalizer's validation floor
  (for example missing `Recommended commit type`, `## Spec-to-Test Mapping`, or
  `## Commands Executed` evidence).
- A terminal `VERIFIED` bridge verdict file is tracked and modified or deleted;
  terminal status proves lifecycle state, not ownership of those changed bytes.
- `target_paths` cannot be parsed from the approved/report artifact.
- The thread belongs to a separately active handoff program.
- The finalization helper, finalizer source, or its tests are themselves dirty
  in a way that could affect commit correctness.

## Operator Loop

1. Run the planner with the active handoff exclusions.
2. Pick one thread with `terminal_verified_repair_candidate`.
3. Re-read the full numbered bridge chain for that thread.
4. Confirm the terminal verdict is independent and still latest.
5. Confirm the planned target paths match the reviewed implementation report.
6. Run the approved one-thread finalization actuator.
7. Re-run the planner and continue only from the new report.

If the class is anything other than `terminal_verified_repair_candidate`, do
not commit it from this runbook. File or route the specific ambiguity through
the bridge instead.
