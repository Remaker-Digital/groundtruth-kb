NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S373-interactive-session-role-override-slice-3
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3470
target_paths: [".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "platform_tests/hooks/test_session_start_marker_invalidation.py"]

# GT-KB Interactive Session Role Override - Slice 3 - SessionStart Marker Invalidation

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation
Version: 001 (NEW)
Date: 2026-05-30 UTC

## Summary

Slice 3 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE (parent GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md`; Slice 2 VERIFIED at `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`). Both SessionStart dispatchers - `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` - delete any pre-existing session-state role marker at `.claude/session/active-session-role.json` at the very start of `main()`, before the dispatch-decision fork and before any role rendering. This makes the ephemeral interactive override non-surviving across a SessionStart event (new session, compaction, resume), implementing `DCL-SESSION-ROLE-RESOLUTION-001` assertion 5.

The change is byte-similar across both dispatchers (the Slice 1 + Slice 2 pattern). A new test module asserts: (a) a pre-written marker is absent after invalidation in both harnesses; (b) the dispatchers' marker path equals the Slice 2 writer's path (`scripts.workstream_focus._session_role_marker_path`), so the deletion target cannot drift away from the write target; (c) invalidation is fail-soft.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all three touched files are in-root (`E:\GT-KB\.claude\hooks\`, `E:\GT-KB\.codex\gtkb-hooks\`, `E:\GT-KB\platform_tests\hooks\`). The marker the dispatchers delete is under the in-root `.claude/session/` directory. No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## Problem Statement

Slice 2 (VERIFIED) writes an ephemeral marker at `.claude/session/active-session-role.json` on the interactive init-keyword path. Per the owner's S371 Decision 3 and `DCL-SESSION-ROLE-RESOLUTION-001` assertion 5, that marker MUST NOT survive a SessionStart event: a fresh session (or compaction/resume) must revert to the durable role until the owner re-declares. Today nothing deletes the marker at SessionStart, so a marker written in session N would persist into session N+1's filesystem and be mistaken for an active declaration by the marker-consuming slices (4-7). Slice 3 closes that gap.

The marker is harness-agnostic: Slice 2's `_session_role_marker_path` resolves to `.claude/session/active-session-role.json` regardless of harness, so both dispatchers target the same path.

## Proposed Change

### Both dispatchers (`.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`)

1. Add a module constant and two helpers (byte-similar in both files):

```python
# Slice 3: the ephemeral session-state role marker written by the
# UserPromptSubmit init-keyword path (scripts/workstream_focus.py Slice 2).
# Per DCL-SESSION-ROLE-RESOLUTION-001 assertion 5, SessionStart must invalidate
# it so the interactive override does not survive a SessionStart event. The
# constant is duplicated from scripts.workstream_focus._SESSION_ROLE_MARKER_NAME
# rather than imported, to keep the SessionStart hot path stdlib-light; the
# parity test asserts the two paths stay equal.
_SESSION_ROLE_MARKER_NAME = "active-session-role.json"


def _session_role_marker_path(project_root: Path = PROJECT_ROOT) -> Path:
    return project_root / ".claude" / "session" / _SESSION_ROLE_MARKER_NAME


def _invalidate_session_role_marker(project_root: Path = PROJECT_ROOT) -> None:
    """Delete any pre-existing session-state role marker before SessionStart
    renders. Fail-soft: a missing marker or an OSError must not abort startup."""
    try:
        _session_role_marker_path(project_root).unlink()
    except FileNotFoundError:
        return
    except OSError:
        return
```

2. Call `_invalidate_session_role_marker()` in `main()` immediately after the existing `_purge_previous_diagnostics(stdout_path, stderr_path)` call (Claude line 532; Codex line 526), before the mode-switch-pending drain and before `_bridge_dispatch_keyword_check()`. Placing it before the dispatch fork guarantees the marker is cleared on every SessionStart path (normal startup, bridge auto-dispatch, strict-drop), satisfying "before SessionStart-time role rendering" unconditionally.

No other behavior changes. The dispatch decision table, STRICT_DROP, the role-scoped cache writer (Slice 1), and the startup-service subprocess flow are all untouched.

### `platform_tests/hooks/test_session_start_marker_invalidation.py` (NEW)

A parameterized module loading both dispatchers under distinct synthetic names, asserting the invalidation behavior and the path-parity contract.

## Design Note - Duplicate Constant vs Import (Codex Review Ask)

The dispatchers duplicate `_SESSION_ROLE_MARKER_NAME` / `_session_role_marker_path` rather than importing them from `scripts.workstream_focus`, to keep the reliability-sensitive SessionStart path stdlib-light and avoid a runtime dependency on the heavier UserPromptSubmit module. Drift is prevented mechanically by a parity test (`test_dispatcher_marker_path_matches_writer`) asserting the dispatcher path equals `scripts.workstream_focus._session_role_marker_path(root)`. The alternative - importing the helper - guarantees zero drift by construction but couples the hot path to `workstream_focus` import success. This proposal picks the duplicate-constant + parity-test pattern (codebase precedent: the rehearsal allowlist desc parity test); Codex Review Ask 4 invites a different call.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - assertion 5 (marker MUST NOT survive a SessionStart event; SessionStart MUST delete/invalidate it before role rendering) is the operative requirement.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - Decision 4 (ephemeral marker, lost across SessionStart events) is the architectural source.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - session-stated role is not persisted to durable storage; invalidation enforces the ephemerality half of the boundary.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - both dispatchers receive the byte-similar change; the test asserts path parity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed at `-001` NEW; the `bridge/INDEX.md` update inserts a `NEW:` entry at the top of a new document block; no bridge file deletion or in-place rewrite of prior versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test plan below maps each acceptance criterion to executable verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; includes WI-3470 via active project membership).
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact.
- `GOV-STANDING-BACKLOG-001` - single behavior change; not a bulk operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` (Slice 2 VERIFIED dependency; defines the marker path this slice deletes).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice adds one helper + one call site in two dispatcher files and one new test module. No backlog bulk operation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no inventory artifact, no review-packet, no formal-artifact-approval packet. Evidence pattern tokens: single helper, byte-similar, fail-soft delete, no bulk, no backlog mutation.

## Prior Deliberations

- `DELIB-2507` - S371 owner directive + 6 AUQ architecture decisions; Decision 3/4 authorize the ephemeral-marker lifecycle that this slice's invalidation enforces.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent GO for the 10-slice plan; Slice 3 is the third slice.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` - Slice 2 VERIFIED; established the marker path and writer that this slice's deletion target must match.
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` - Slice 1 VERIFIED; established the byte-similar dual-dispatcher change pattern this slice follows.
- No prior deliberation has touched SessionStart marker deletion; this is the first slice to add a marker-invalidation step to `main()`.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ROLE-RESOLUTION-001` assertion 5 + `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Decision 4 + the parent GO fully specify the invalidation behavior. No new owner clarification required for Slice 3.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each acceptance criterion maps to an executable test in the new module:

| Acceptance criterion | Test | Expected |
|---|---|---|
| Pre-written marker is absent after invalidation (Claude + Codex) | `test_marker_invalidated[claude]`, `[codex]` | marker file removed |
| Invalidation is a no-op (no raise) when no marker exists | `test_invalidate_noop_when_absent[claude]`, `[codex]` | no exception; returns None |
| Fail-soft on OSError (e.g., path is a non-empty directory / locked) | `test_invalidate_failsoft_on_oserror[claude]`, `[codex]` | no exception propagates |
| Dispatcher marker path equals the Slice 2 writer's path (no drift) | `test_dispatcher_marker_path_matches_writer[claude]`, `[codex]` | `dispatcher._session_role_marker_path(root) == workstream_focus._session_role_marker_path(root)` |
| Both dispatchers resolve the same marker path (cross-harness parity) | `test_both_dispatchers_agree_on_marker_path` | claude path == codex path |
| `main()` calls the invalidation before the dispatch fork | `test_main_invokes_invalidation_before_dispatch` (monkeypatch `_invalidate_session_role_marker` + `_bridge_dispatch_keyword_check` to record call order; assert invalidation called and ordered first) | invalidation recorded before dispatch check |

### Required verification commands (post-implementation report will show observed results)

```text
python -m ruff check .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_session_start_marker_invalidation.py
python -m ruff format --check .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_session_start_marker_invalidation.py
python -m pytest platform_tests/hooks/test_session_start_marker_invalidation.py -q
python -m pytest platform_tests/hooks/test_session_start_dispatch_role_cache.py -q   # Slice 1 regression (same files touched)
```

Both `ruff check` (lint) and `ruff format --check` (formatter) are run, per the Slice 2 NO-GO -006 lesson that they are distinct gates.

## Acceptance Criteria

- Codex issues GO with explicit confirmation that:
  - The invalidation is byte-similar across both dispatchers and placed before the dispatch fork.
  - The marker path the dispatchers delete matches the Slice 2 writer's path (the parity test covers this).
  - The duplicate-constant choice (vs import) is acceptable, or a NO-GO names the import alternative.
  - No other dispatcher behavior changes (Slice 1 cache writer + STRICT_DROP untouched).
- If GO, implement and file the post-implementation report carrying forward Spec Links + spec-to-test mapping + observed results for both ruff gates and both test modules + recommended Conventional Commits type.
- If NO-GO, revise via `-002 REVISED` (no in-place edit of `-001`).

## Risk and Rollback

- **Risk:** the dispatcher constant drifts from the Slice 2 writer's marker path, so SessionStart deletes the wrong (or no) file. **Mitigation:** `test_dispatcher_marker_path_matches_writer` asserts equality against `scripts.workstream_focus._session_role_marker_path`; the test fails on drift.
- **Risk:** invalidation raises and aborts SessionStart. **Mitigation:** fail-soft try/except (FileNotFoundError + OSError swallowed), mirroring `_purge_previous_diagnostics`. Tested by `test_invalidate_failsoft_on_oserror`.
- **Risk:** invalidation runs too late (after a marker-consuming step). **Mitigation:** the call is placed before the dispatch fork and before any rendering; `test_main_invokes_invalidation_before_dispatch` asserts ordering.
- **Risk:** a legitimately active same-session marker is deleted on a mid-session SessionStart (compaction). **Accepted by design:** per Decision 3/4 the override is explicitly lost across SessionStart events; the owner re-declares with the init keyword. This is the intended contract, not a defect.
- **Rollback:** remove the `_invalidate_session_role_marker()` call and the helper from both dispatchers; delete the test module. No state to unwind (the marker is ephemeral; Slices 4-7 are not yet landed).

## Owner Decisions / Input

This slice proceeds under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; covers WI-3470 via active project membership; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` the slice still runs through the full bridge protocol (this NEW -> Codex GO -> implement -> post-implementation report -> VERIFIED). DELIB-2507 holds the 6 S371 owner AskUserQuestion decisions; Decision 3 (ephemeral, lost across SessionStart events) directly authorizes this invalidation. No new owner decision is required.

## Codex Review Asks

1. Confirm the invalidation call placement (before the dispatch fork, after `_purge_previous_diagnostics`) satisfies "before SessionStart-time role rendering" on every path.
2. Confirm the byte-similar change across both dispatchers and the parity test adequately prevent path drift.
3. Confirm fail-soft coverage (FileNotFoundError + OSError) is sufficient.
4. Confirm the duplicate-constant choice, or NO-GO in favor of importing `scripts.workstream_focus._session_role_marker_path` into the dispatchers.
5. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
