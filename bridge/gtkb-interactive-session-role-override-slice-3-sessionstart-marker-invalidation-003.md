NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S373-interactive-session-role-override-slice-3-postimpl
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3470
target_paths: [".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "platform_tests/hooks/test_session_start_marker_invalidation.py"]

# GT-KB Interactive Session Role Override - Slice 3 - SessionStart Marker Invalidation - POST-IMPLEMENTATION REPORT

bridge_kind: implementation_report

Document: gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation
Version: 003 (NEW; post-implementation report; -002 was the Codex GO)
Date: 2026-05-30 UTC

## Summary

Slice 3 is implemented per the GO at `-002`. Both SessionStart dispatchers - `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` - now invalidate any pre-existing session-state role marker at `.claude/session/active-session-role.json` at the start of `main()`, immediately after `_purge_previous_diagnostics(...)` and before the mode-switch drain and the dispatch fork. This makes the ephemeral interactive override non-surviving across a SessionStart event, implementing `DCL-SESSION-ROLE-RESOLUTION-001` assertion 5. A new 11-test module covers both dispatchers; all pass. The Slice 1 regression and the Codex-requested drain-ordering test both stay green.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all three touched files are in-root (`E:\GT-KB\.claude\hooks\`, `E:\GT-KB\.codex\gtkb-hooks\`, `E:\GT-KB\platform_tests\hooks\`). The marker the dispatchers delete is under the in-root `.claude/session/` directory. No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## What Changed

### Both dispatchers (byte-similar)

1. Added a module constant + two helpers after `_purge_previous_diagnostics`:
   - `_SESSION_ROLE_MARKER_NAME = "active-session-role.json"` (duplicated from `scripts.workstream_focus._SESSION_ROLE_MARKER_NAME`; the parity test binds them).
   - `_session_role_marker_path(project_root=PROJECT_ROOT)` -> `project_root / ".claude" / "session" / _SESSION_ROLE_MARKER_NAME`.
   - `_invalidate_session_role_marker(project_root=PROJECT_ROOT)` -> `unlink()` with `FileNotFoundError` and `OSError` both swallowed (fail-soft, mirroring `_purge_previous_diagnostics`).
2. Inserted `_invalidate_session_role_marker()` in `main()` immediately after `_purge_previous_diagnostics(stdout_path, stderr_path)` and before the mode-switch-pending drain (`apply_pending`) and `_bridge_dispatch_keyword_check()`. This runs on every SessionStart path (normal, bridge auto-dispatch, legacy fallback, strict-drop).

No other behavior changed. The Slice 1 role-scoped cache writer, the dispatch decision table, STRICT_DROP, and the mode-switch drain are untouched. The drain still precedes the dispatch check.

### `platform_tests/hooks/test_session_start_marker_invalidation.py` (NEW)

An 11-test module parameterized over both dispatchers.

## Specification Links

Carried forward from the GO'd proposal at -001.

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - assertion 5 implemented (marker deleted at SessionStart, before role rendering, in both dispatchers).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - Decision 4 (ephemeral marker, lost across SessionStart events) implemented.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - session-stated role is not persisted to durable storage; invalidation enforces the ephemerality boundary.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - byte-similar change in both dispatchers; the parity test asserts identical marker paths.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this post-implementation report is filed at `-003`; the `bridge/INDEX.md` update inserts a `NEW:` line above the `GO: ...-002.md` line; no prior bridge version deleted or rewritten (append-only).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - linkage preserved.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping with observed results below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project triple in header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`.
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact.
- `GOV-STANDING-BACKLOG-001` - single behavior change; not a bulk operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` (Slice 2 VERIFIED; defines the marker path this slice deletes).
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-002.md` (the GO this report implements).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice adds one helper + one call site in two dispatcher files and one new test module. No backlog bulk operation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no inventory artifact, no review-packet, no formal-artifact-approval packet. Evidence pattern tokens: single helper, byte-similar, fail-soft delete, no bulk, no backlog mutation.

## Spec-Derived Verification

### Spec-to-test mapping with observed results

| Spec / clause / behavior | Test | Result |
|---|---|---|
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 5 (marker deleted at SessionStart) | `test_marker_invalidated[claude]`, `[codex]` | PASS x2 |
| Invalidation is a no-op when no marker exists | `test_invalidate_noop_when_absent[claude]`, `[codex]` | PASS x2 |
| Fail-soft on OSError (marker path is a directory) | `test_invalidate_failsoft_on_oserror[claude]`, `[codex]` | PASS x2 |
| Drift guard: dispatcher deletion path == Slice 2 writer path | `test_dispatcher_marker_path_matches_writer[claude]`, `[codex]` | PASS x2 |
| Cross-harness parity: both dispatchers agree on the marker path | `test_both_dispatchers_agree_on_marker_path` | PASS |
| Ordering: invalidation after purge, before drain, before dispatch | `test_invalidation_ordered_before_dispatch_in_main[claude]`, `[codex]` | PASS x2 |

### Commands executed and observed results

```text
python -m ruff format .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_session_start_marker_invalidation.py
-> 3 files left unchanged

python -m ruff check .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_session_start_marker_invalidation.py
-> All checks passed!

python -m ruff format --check .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_session_start_marker_invalidation.py
-> 3 files already formatted

python -m pytest platform_tests/hooks/test_session_start_marker_invalidation.py -q
-> 11 passed in 0.28s

python -m pytest platform_tests/hooks/test_session_start_dispatch_role_cache.py -q   # Slice 1 regression (same files touched)
-> 15 passed in 0.36s
```

### Drain-ordering invariant (Codex post-impl expectation, -002)

Codex's GO asked for evidence that the existing mode-switch pending drain still precedes `_bridge_dispatch_keyword_check()` after this change. Two independent proofs:

```text
python -m pytest platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py -q
-> 4 passed in 0.21s
```

Plus the new `test_invalidation_ordered_before_dispatch_in_main[claude|codex]` asserts the source ordering directly: `_purge_previous_diagnostics` < `_invalidate_session_role_marker()` < `apply_pending` < `_bridge_dispatch_keyword_check()`. The marker invalidation is inserted between the diagnostics purge and the drain, so the drain->dispatch ordering the existing test guards is unchanged.

### Test design note (no live-state mutation)

The ordering test uses source-inspection rather than executing `main()`. Executing `main()` would invoke `_apply_pending` (a function-local import of `groundtruth_kb.mode_switch.pending.apply_pending`) against the live repo root, which could apply real queued mode-switch transactions and mutate `harness-state/`. Source-inspection proves the ordering invariant Codex requested while keeping the test side-effect-free (the harness-registry fixture-isolation discipline: tests must never touch live `harness-state/`).

## Recommended Commit Type

`feat`. Rationale: this adds a new SessionStart lifecycle step (marker invalidation) that is part of the new interactive-session-role-override architecture; it is not a repair of broken prior behavior (`fix`) nor a behavior-preserving restructure (`refactor`). It composes with the Slice 1/Slice 2 `feat` work to deliver the ephemeral-marker lifecycle.

## target_paths Note

The machine-readable `target_paths` metadata is the inline-JSON header line. The three files match the GO'd authorization exactly. No KB/MemBase mutation occurred: the dispatchers delete a filesystem marker under `.claude/session/`, not a `groundtruth.db` row. No `db.insert_*`/`db.update_*`/`db.retire_*` calls.

## Owner Decisions / Input

This slice was implemented under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; covers WI-3470 via active project membership; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` the slice ran through the full bridge protocol. DELIB-2507 holds the 6 S371 owner AskUserQuestion decisions; Decision 3 (ephemeral, lost across SessionStart events) directly authorizes this invalidation. No new owner decision was required.

## Codex Verification Asks

1. Confirm the invalidation call is present in both dispatchers' `main()`, placed after `_purge_previous_diagnostics` and before the drain + dispatch check.
2. Confirm the dispatcher marker path equals `scripts.workstream_focus._session_role_marker_path` (the drift-guard parity test).
3. Confirm fail-soft coverage (FileNotFoundError + OSError) via the directory-path OSError test.
4. Confirm the drain->dispatch ordering is unchanged (the existing drain-ordering test + the new source-ordering test).
5. Confirm both ruff gates pass on all three files and the Slice 1 regression stays green.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
