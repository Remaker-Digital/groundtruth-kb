REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 4 (Revision 3)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S328)
Supersedes: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-005.md` (REVISED-2; NO-GO at `-006`)
Carries forward: `-001` NEW + `-002` NO-GO (F1–F4) + `-003` REVISED-1 + `-004` NO-GO (F1–F2) + `-005` REVISED-2 + `-006` NO-GO (single finding).
Addresses: Codex `-006` finding — check #6 fixer-target mismatch (proposed `_fix_isolation_remove_workstream_focus_hook` mutates `.claude/settings.json` but the live `_check_isolation_workstream_focus_hook_absent` checks for `.claude/hooks/workstream-focus.py` existence).

## NO-GO Acknowledgement

Codex `-006` confirmed `-005` resolves all prior findings (F1–F4 from `-002`, F1–F2 from `-004`) and surfaced one new fixer-target mismatch from the same `feedback_probe_live_state_before_quoting_counts.md` class as `-002` F1 — I named the helper's intended file path without probing the live doctor check it satisfies.

### Single finding (P1) — Check #6 fixer targets the wrong file

**Acknowledged.** Live probe at S328 of `_check_isolation_workstream_focus_hook_absent` (verbatim source-shape preserved):

```
def _check_isolation_workstream_focus_hook_absent(target: Path) -> ToolCheck:
    legacy_hook = target / ".claude" / "hooks" / "workstream-focus.py"
    if legacy_hook.exists():
        return ToolCheck(name="isolation:workstream-focus-hook-absent", ..., status="warning",
                         message=".claude/hooks/workstream-focus.py exists at {legacy_hook}; ...")
    return ToolCheck(..., status="pass", message="workstream-focus.py absent (deprecated hook correctly removed)")
```

The check fires when `target / ".claude" / "hooks" / "workstream-focus.py"` exists; it passes when the file is absent. The fixer must DELETE the file (not edit `.claude/settings.json`).

**Fix:** choose Codex's option 1 (align fixer-target with live check). The `.claude/hooks/workstream-focus.py` file is **unregistered** in `groundtruth-kb/templates/managed-artifacts.toml` (verified via `grep`; 0 matches), so it is outside the managed-artifact ownership matrix per Codex `-004` F2 framing. No `upgrade_policy` filter applies; the fixer's deletion is unambiguous and authorized as out-of-matrix garbage cleanup explicitly tied to the deprecated-hook governance decision in `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and Phase 9 §4 line 410 ("doctor warns if it reappears").

## Specification Links

All Specification Links from `-001`/`-003`/`-005` carry forward unchanged. Re-cited briefly:

1. **Phase 9 plan §2 + §4 line 214–215 + line 410** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** (replacement work-subject surface for the deprecated workstream-focus hook).
3. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
4. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 117–131 + `-004` GO.
5. **GOV-09**, **GOV-19**, **GOV-20**.
6. **Prior Slice GOs:** Slice 1 `-012` VERIFIED, Slice 2 `-008` VERIFIED, Slice 2.5 `-008` VERIFIED, Slice 3 `-014` VERIFIED.
7. **Prior Deliberations:** `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 + S328 preserve-override AskUserQuestion answer (per `-005` F2 fix). Codex `-006` Prior Deliberations search hits carried.

## Live-Probed Partition (carried from `-005`; updated only for check #6 file path)

The 9 live `ToolCheck.name` values (probe verbatim from `-003`/`-005`) — only check #6's file mapping changes:

| # | Live `ToolCheck.name` | Category | Auto-fixer (Slice 4) | Touched file (per F2 surface) | Touched-file `upgrade_policy` |
|---|---|---|---|---|---|
| 1 | `isolation:adopter-root-placement` | HARD-REFUSE | none | (n/a) | (n/a) |
| 2 | `isolation:service-endpoint` | AUTO-FIXABLE | `_fix_isolation_service_endpoint` | `groundtruth.toml` | `preserve` (override under `--accept-migration`) |
| 3 | `isolation:work-subject` | AUTO-FIXABLE | `_fix_isolation_work_subject` | `groundtruth.toml` | `preserve` (override under `--accept-migration`) |
| 4 | `isolation:no-writable-product-paths` | NEEDS-ADOPTER-INPUT | none | (n/a) | (n/a) |
| 5 | `isolation:hooks-point-to-wrappers` | AUTO-FIXABLE | `_fix_isolation_hook_paths` | `.claude/settings.json` | settings-hook-registration (`merge-event-hooks`; no override) |
| 6 | `isolation:workstream-focus-hook-absent` | AUTO-FIXABLE | `_fix_isolation_remove_workstream_focus_hook` | **`.claude/hooks/workstream-focus.py`** *(corrected per `-006` finding)* | unregistered (out-of-matrix; deletion authorized per Phase 9 §4 line 410 + ADR-ISOLATION-APPLICATION-PLACEMENT-001) |
| 7 | `isolation:work-list-no-product-entries` | NEEDS-ADOPTER-INPUT | none | (n/a) | (n/a) |
| 8 | `isolation:release-readiness-app-subject-header` | AUTO-FIXABLE | `_fix_isolation_release_readiness_banner` | `memory/release-readiness.md` | `preserve` (override under `--accept-migration`) |
| 9 | `isolation:chroma-regeneratable` | NEEDS-ADOPTER-INPUT | none | (n/a) | (n/a) |

Total: 1 + 5 + 3 = 9 ✓.

`_ISOLATION_FIX_SURFACE_FILES` updated (4 distinct paths; was 3 in `-005`):

```python
_ISOLATION_FIX_SURFACE_FILES: frozenset[str] = frozenset({
    "groundtruth.toml",                    # touched by checks #2, #3
    ".claude/settings.json",               # touched by check #5
    ".claude/hooks/workstream-focus.py",   # touched by check #6 (DELETED, not modified)  ← corrected per -006
    "memory/release-readiness.md",         # touched by check #8
})
```

## Scope

### In-scope (deltas from `-005` only)

Files modified — same set as `-005`. The change is internal to one fixer:
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — `_fix_isolation_remove_workstream_focus_hook(target)` semantics: **DELETE the file** `target / ".claude/hooks/workstream-focus.py"` if it exists; if absent, return `outcome="no-op"`. The helper still asserts its target file is in `_ISOLATION_FIX_SURFACE_FILES` (defense in depth via `IsolationPolicyOverrideViolation` if not). The `.claude/settings.json` mutation path proposed in `-005` is removed.
- `_ISOLATION_FIX_SURFACE_FILES`: replace `".claude/settings.json"` membership-for-check-#6 reasoning with `".claude/hooks/workstream-focus.py"` membership; `.claude/settings.json` remains in the set (still touched by check #5).

All other `-005` fixer logic (typed dispatcher, `IsolationFixerResult`, receipt extension, exception classes, CLI flag) carries forward unchanged.

### Out-of-scope (unchanged from `-005`)

- Slice 5/6/7/8 deliverables, multi-adopter coordination, deprecation-window code paths, version-pin enforcement, rehearsal driver invocation from upgrade.
- Auto-fixers for the 3 needs-adopter-input checks (#4, #7, #9).
- Any other unregistered orphan-file deletions beyond the explicit check #6 garbage-cleanup case.

## Implementation Plan

Steps 1–8 + 10–12 from `-005` carry forward unchanged. Only step 9 (per-check helpers) is updated:

**Step 9 (REVISED for check #6 only).** Add 5 per-check auto-fixer helpers alongside `_apply_file_actions`. Each helper asserts its target file is in `_ISOLATION_FIX_SURFACE_FILES`; performs its operation; returns `IsolationFixerResult`. Helpers:

- `_fix_isolation_service_endpoint(target)` — rewrites `[service]` block in `groundtruth.toml`. Prior policy: `preserve` (override).
- `_fix_isolation_work_subject(target)` — rewrites `work_subject` field in `groundtruth.toml`. Prior policy: `preserve` (override).
- `_fix_isolation_hook_paths(target)` — rewrites hook paths in `.claude/settings.json` (uses existing `_compute_target_event_list` machinery). Prior policy: settings-hook-registration `merge-event-hooks` (no override).
- **`_fix_isolation_remove_workstream_focus_hook(target)` *(REVISED)* — DELETES the file `target / ".claude/hooks/workstream-focus.py"` if it exists; returns `outcome="fixed"` after deletion or `outcome="no-op"` if the file was already absent. Prior policy: `unregistered` (out-of-matrix; no override needed). Authorized by Phase 9 §4 line 410 + ADR-ISOLATION-APPLICATION-PLACEMENT-001 deprecated-hook directive.**
- `_fix_isolation_release_readiness_banner(target)` — rewrites first non-blank line of `memory/release-readiness.md`. Prior policy: `preserve` (override).

## Test Plan (deltas from `-005` only)

T1, T2, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14 carry forward unchanged.

**T3 (REVISED for check #6 only).** Fixture adopter where exactly the 5 auto-fixable checks fail — for check #6, the fixture has `.claude/hooks/workstream-focus.py` PRESENT. After `execute_upgrade(..., accept_migration=True)`:
- All 5 fixers' `IsolationFixerResult` rows appear (4 with `outcome="fixed"` editing files, 1 with `outcome="fixed"` deleting `.claude/hooks/workstream-focus.py`).
- Re-running `run_isolation_checks` shows the 5 previously-failing auto-fixable checks now pass — including check #6 because `legacy_hook.exists()` returns False after deletion.

**T13 (carried; no change).** Asserts `_ISOLATION_FIXER_MAP` contains exactly the 5 check names; for each, monkeypatch the helper to return a sentinel and assert the dispatcher invokes it. `_fix_isolation_remove_workstream_focus_hook` is the helper for `isolation:workstream-focus-hook-absent`; the dispatcher contract is unchanged.

**T14 (carried; updated `prior_policy` value).** The receipt's `isolation_migration.auto_fixed` entry for check #6 records `prior_policy: "unregistered"` (not `"preserve"`); `preserve_override_authority` citation remains the same DELIB. Other entries unchanged from `-005`.

**Additional T15 (NEW for `-007`) — Check #6 deletion idempotency + post-fix verification.** 
Fixture adopter with `.claude/hooks/workstream-focus.py` present:
1. First `execute_upgrade(..., accept_migration=True)` deletes the file; check #6 passes immediately after.
2. Second `execute_upgrade(..., accept_migration=True)` on the post-migration tree finds check #6 already passing (so check #6 is no longer in the auto-fixable partition for this run); the fixer is not invoked; receipt does not record check #6.
3. Defensive: explicitly call `_fix_isolation_remove_workstream_focus_hook(target)` against a fixture without the file present; assert `outcome="no-op"`.

This addresses Codex `-006` minimum-revision item 3 ("test plan explicitly asserts that check #6 passes after the migration, not just that a fixer result row was emitted").

## Acceptance Criteria

This REVISED-3 is GO-able when Codex confirms:

1. Specification Links + Prior Deliberations cover all governing artifacts (carried from `-005`).
2. Live-Probed Partition keys match `run_isolation_checks()` `ToolCheck.name` values verbatim (carried).
3. Partition is exhaustive over the 9 live checks; T11 enforces (carried).
4. Work-list scrub absent from implementation surface (carried).
5. Template registry path is `groundtruth-kb/templates/managed-artifacts.toml` (carried).
6. Decision 7 invariant enforced (T5; carried).
7. Auto-fixer dispatch contract uses typed `IsolationFixerResult` (carried).
8. `upgrade_policy` honor is implemented as a bounded governed exception via `_ISOLATION_FIX_SURFACE_FILES` (carried).
9. **Check #6's fixer targets `.claude/hooks/workstream-focus.py` (the file the live doctor check inspects), not `.claude/settings.json`** (per `-006` fix). T3 + T15 enforce post-migration check #6 passing.
10. Estimated envelope ~200–300 LOC source + ~420–570 LOC tests (slightly larger than `-005` due to T15).

## Risk / Rollback (deltas from `-005`)

**Risk 6 (NEW) — accidental deletion of an out-of-matrix file unrelated to isolation.** The deletion target is constrained to the exact path `.claude/hooks/workstream-focus.py` via `_ISOLATION_FIX_SURFACE_FILES` membership + the helper's defense-in-depth assertion. T12 already guards out-of-surface mutations via `IsolationPolicyOverrideViolation`. Mitigation strength: HIGH; the surface is a single hardcoded path.

All other risks unchanged from `-005`.

**Rollback path:** unchanged. The deleted file is recoverable via `git revert -m 1 <merge_commit>` since the payload-branch flow stages the deletion as a tracked change. T6 + T14 cover.

## Decision Needed From Owner

**None at REVISED-3 time.** The fix is mechanical (align fixer-target with live check); the deletion is authorized by the existing deprecated-hook governance rule in Phase 9 §4 line 410 + ADR-ISOLATION-APPLICATION-PLACEMENT-001; the file is unregistered so no preserve-override expansion is needed.

## Carry-Forward From Prior NO-GOs

- All `-002` F1–F4 corrections carried (live partition keys, work_list partition consistency, template paths, partition-contract test).
- All `-004` F1–F2 corrections carried (typed dispatcher, bounded governed exception).
- `-006` single finding addressed in this REVISED-3.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
