REVISED

# GT-KB Bridge Implementation Report (REVISED) - gtkb-wi5071-no-window-source-fixes-reintroduction-guard - 005

bridge_kind: implementation_report
Document: gtkb-wi5071-no-window-source-fixes-reintroduction-guard
Version: 005 (REVISED post-implementation report; responds to NO-GO -004)
Responds to NO-GO: bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-004.md
Responds to GO: bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-002.md
Approved proposal: bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-001.md
Supersedes: bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-003.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fea7dd14-2033-476e-8618-748d76c6fda2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; resolved_role=prime-builder (session-stated ::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5071

Recommended commit type: fix:

## Response To NO-GO -004

The independent LO NO-GO (-004, session 85e78bc0) confirmed the substance is VERIFIED-worthy and raised one blocker: the -003 report listed the goose path token inside `## Files Changed` (under "NOT committed"), so the VERIFIED-finalize covers-check (`_claimed_paths_from_report`) treated it as a required-include path, deadlocking the finalize. This REVISED report addresses that: `## Files Changed` below lists ONLY the six committed tracked files; all goose discussion is confined to `## Deviations / Scope Notes` (a section the covers-check does not scan).

This REVISED report ALSO carries a small implementation delta beyond the LO's report-only ask, driven by a separate owner decision the -004 reviewer did not have: per `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` (owner, 2026-07-08) Goose harness `G` is being retired and its artifacts obsoleted, and the owner directed (AUQ, this session) dropping goose from WI-5071-B. So the `scripts/goose_harness.py` entry has been **removed** from `RELEASE_RUNTIME_FILES` in `scripts/windows_no_window_spawn_audit.py` (that file is now +4 rather than +5). Nothing else in the implementation changed; the audit/tests/ruff were fully re-run clean.

## Implementation Claim

Slice 1 of WI-5071 stops the concrete automated console-window spawn sources found by the inventory and wires the previously-unenforced static audit into the release gate plus a real-tree CI test. All changes are additive no-window flags / allowlist data / one gate check / one test; no control-flow or argv change; no global window suppressor (honoring the owner constraint that the fix must never block manual window/GUI launches).

Three committed source fixes (all confirmed `compliant_no_window` by the audit):

- `scripts/verify_codex_dispatch.py:143` - the `.codex` ACL-repair powershell runner now passes `**no_window_subprocess_kwargs()` (layered cleanly on WI-5065's committed repair logic, commit `00b76b29`).
- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py:784` - the scheduled-task installer runner now mirrors this module's own compliant `_run_powershell` idiom (inline `creationflags = CREATE_NO_WINDOW` on `os.name == "nt"`); no cross-module import.
- `scripts/ops/install_ollama_autostart_task.ps1:52` - `New-ScheduledTaskSettingsSet` now passes `-Hidden`.

Reintroduction guard (committed):

- `scripts/windows_no_window_spawn_audit.py` - `RELEASE_RUNTIME_FILES` extended with `scripts/verify_codex_dispatch.py`, `scripts/verify_cursor_dispatch.py`, `scripts/verify_claude_dispatch.py`; `RELEASE_RUNTIME_PREFIXES` extended with `groundtruth-kb/src/groundtruth_kb/watchdog/`. (The goose entry from -003 has been removed per the owner goose-retirement decision.)
- `scripts/release_candidate_gate.py` - new `_check_no_window_spawn_audit()` gate (exit-1 on `violation_count > 0`), registered in `main()`.
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py` - new `test_real_tree_has_no_no_window_violations()` scanning the git-tracked tree, asserting `violation_count == 0` (runs in CI).

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- **Standing owner directive `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`** (owner_decision): no visible console windows may spawn; dispatcher may remain quiesced during repair; acceptance is a 120-consecutive-minute clean interval. WI-5071's `source_owner_directive`.
- **Owner AUQ (scope), 2026-07-09:** WI-5071 scope -> "+ Consolidate inline helpers" (comprehensive scope); Slice 1 is the first slice. `detected_via: ask_user_question`.
- **Owner directive (source-level, no global suppressor):** stop the spawns at the source, guard against reintroduction, but never block manual window/GUI launches. `detected_via: owner_directive`.
- **Owner decision `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS`** (owner_decision, 2026-07-08): retire Goose harness `G`, replace with an "Alibaba Cloud Studio" harness (identity `H`), and obsolete Goose artifacts including `scripts/goose_harness.py`.
- **Owner AUQ (this session), 2026-07-09:** "How should I handle goose in WI-5071-B?" -> "Drop goose from WI-5071-B" (remove the allowlist entry; leave the doomed on-disk goose edit). `detected_via: ask_user_question`. This authorizes the goose-drop implementation delta in this REVISED report.

Project-scope owner-approval evidence is `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers WI-5071 by active project membership).

## Prior Deliberations

- `bridge/gtkb-wi5071-...-001.md` - approved proposal.
- `bridge/gtkb-wi5071-...-002.md` - LO GO (Antigravity C, session `0072210b`).
- `bridge/gtkb-wi5071-...-004.md` - LO NO-GO (Claude B, session `85e78bc0`) - the report-structure finding this revision addresses.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - governing owner directive.
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` - goose-retirement owner decision motivating the goose drop.
- `DELIB-20266297` (WI-4896), `DELIB-20266506` (WI-4932) - prior no-window slices.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` (WI-5052 VERIFIED) - related containment.

## Specification-Derived Verification Plan

Interpreter: `groundtruth-kb/.venv/Scripts/python.exe`.

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DELIB-20260707` + `GOV-RELIABILITY-FAST-LANE-001` + `ADR-CROSS-HARNESS-PARITY-001` | Full-tree audit `violation_count: 0`, `release_ready: true` (exit 0); the three committed fixed sites confirmed `compliant_no_window`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (guard enforced) | Real-tree pytest `test_real_tree_has_no_no_window_violations` PASSES; `_check_no_window_spawn_audit()` converts audit exit-1 into a `GateFailure`. |
| No-regression on touched modules | 72 tests PASS across the 5 touched-module test files. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | REVISED report filed append-only via the governed revise helper; `## Files Changed` lists exactly the committed set so the finalize covers-check is unambiguous. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py` (full-tree audit)
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest <5 touched-module test files> -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <5 tracked changed .py>`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <5 tracked changed .py>`

## Observed Results

- Full-tree audit (post goose-drop): `{"counts": {"compliant_no_window": 89, "interactive_allowlist": 115, "non_release_runtime": 469}, "release_ready": true, "total_findings": 673, "violation_count": 0}` (exit 0).
- Audit test file: **11 passed**.
- Touched-module regression: **72 passed**.
- `ruff check`: **All checks passed!**
- `ruff format --check`: **5 files already formatted.**

## Files Changed

The complete committed set for WI-5071 (6 tracked files; `git diff --stat HEAD`):

- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `scripts/ops/install_ollama_autostart_task.ps1`
- `scripts/release_candidate_gate.py`
- `scripts/verify_codex_dispatch.py`
- `scripts/windows_no_window_spawn_audit.py`

## Deviations / Scope Notes

1. **Goose DROPPED entirely from WI-5071-B (owner decision).** Per `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` and the owner AUQ this session, the goose harness file (an untracked WI-5072 artifact slated for retirement) is out of scope: the `RELEASE_RUNTIME_FILES` entry for it has been removed, and it is not committed. The on-disk no-window edit to that untracked file is left in place (harmless; it dies with the file at retirement). Nothing about goose is codified by WI-5071-B, so the retirement work has nothing here to clean up. (This is the fix for NO-GO -004 Finding 1 AND the owner's goose-drop directive.)
2. **`verify_antigravity_dispatch.py` deliberately NOT allowlisted.** Its `:462` spawn is non-compliant and out of `target_paths`; allowlisting it would break `violation_count == 0`. Deferred to the Antigravity console-window track (WI-5113). `verify_cursor_dispatch.py` / `verify_claude_dispatch.py` have no spawn sites and are added as forward-guards.
3. **Incidental ruff cleanup of the (uncommitted, untracked) goose file** from -003 remains on-disk only; not committed.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: repairs a reliability regression (visible console windows) and closes the enforcement gap that let it recur; the net-new lines are the protective guard test and release-gate check.

## Acceptance Criteria Status

- [x] Audit `violation_count == 0` (full tree, post goose-drop).
- [x] Real-tree test passes.
- [x] `ruff check` and `ruff format --check` pass on the changed tracked `.py`.
- [x] Release-gate check registered and green.
- [x] NO-GO -004 Finding 1 resolved: `## Files Changed` lists only the 6 committed files; goose confined to `## Deviations`.
- [ ] `DELIB-20260707` 120-minute clean-interval soak - post-implementation owner-facing acceptance across ALL slices; dispatch remains quiesced.

## Risk And Rollback

Blast radius: three committed no-window edits, one allowlist data extension (goose entry removed), one additive release-gate check, one new test. Additive `creationflags`/`startupinfo` are no-ops off-Windows. The guard is a CI/gate check plus a pytest - no local pre-commit hook, no runtime window suppression - so it cannot block the owner's local commits or manual launches. Rollback: revert the 6 committed files; no data migration, no persisted state.

## Loyal Opposition Asks

1. Confirm `## Files Changed` lists exactly the 6 committed tracked files and the finalize covers-check now demands only that set (goose is absent from every scanned heading).
2. Confirm the goose-drop implementation delta (removed `scripts/goose_harness.py` from `RELEASE_RUNTIME_FILES`) leaves the audit at `violation_count == 0` and is authorized by the cited owner decisions.
3. Confirm the three committed source fixes carry real no-window dispositions and the guard is enforced (not advisory).
4. Return VERIFIED if satisfied, committing the 6 tracked files + the bridge chain (`-001` through `-005`); otherwise NO-GO with findings.
