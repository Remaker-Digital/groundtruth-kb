NEW

# GT-KB Bridge Implementation Report - gtkb-wi5071-no-window-source-fixes-reintroduction-guard - 003

bridge_kind: implementation_report
Document: gtkb-wi5071-no-window-source-fixes-reintroduction-guard
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-002.md
Approved proposal: bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-001.md

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

## Implementation Claim

Slice 1 of WI-5071 is implemented: the concrete automated console-window spawn sources found by the inventory now carry a Windows no-window disposition, and the previously-unenforced static audit is wired into the release gate plus a real-tree CI test so a regression is caught rather than silently shipped. All changes are strictly additive no-window flags / allowlist data / one gate check / one test; none change harness argv or control flow, and no global window suppressor is introduced (honoring the owner constraint that the fix must never block manual window/GUI launches).

Concrete source fixes (all confirmed `compliant_no_window` by `scripts/windows_no_window_spawn_audit.py`):

- `scripts/verify_codex_dispatch.py:143` - the `.codex` ACL-repair `powershell -File repair_codex_dotdir_acl.ps1` runner now passes `**no_window_subprocess_kwargs()`. (Layered on top of WI-5065's just-VERIFIED repair logic in the same `_run` closure; commit `00b76b29`.)
- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py:784` - the scheduled-task installer runner now mirrors this module's own compliant `_run_powershell` idiom (inline `creationflags = CREATE_NO_WINDOW` on `os.name == "nt"`); no cross-module import added.
- `scripts/ops/install_ollama_autostart_task.ps1:52` - `New-ScheduledTaskSettingsSet` now passes `-Hidden`, matching every other GT-KB task installer.
- `scripts/goose_harness.py:144` - the goose CLI launch now passes `**no_window_subprocess_kwargs()`. **See "Deviations / Scope Notes" below: this file is UNTRACKED (WI-5072 in-progress) and is deliberately not committed by this WI.**

Reintroduction guard:

- `scripts/windows_no_window_spawn_audit.py` - `RELEASE_RUNTIME_FILES` extended with `scripts/goose_harness.py`, `scripts/verify_codex_dispatch.py`, `scripts/verify_cursor_dispatch.py`, `scripts/verify_claude_dispatch.py`; `RELEASE_RUNTIME_PREFIXES` extended with `groundtruth-kb/src/groundtruth_kb/watchdog/`.
- `scripts/release_candidate_gate.py` - new `_check_no_window_spawn_audit()` gate (exit-1 on `violation_count > 0`), registered in `main()` after the app-root-minimization check.
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py` - new `test_real_tree_has_no_no_window_violations()` scanning the git-tracked tree and asserting `violation_count == 0` (runs in CI via the platform_tests suites).

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

This work is authorized by owner evidence carried forward from the approved proposal (`-001`):

- **Standing owner directive `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`** (owner_decision): "no visible console windows may spawn on this workstation... no exception"; the dispatcher may remain quiesced during repair; acceptance is a 120-consecutive-minute clean interval. This is WI-5071's `source_owner_directive`.
- **Owner AUQ (scope), 2026-07-09:** "How should I scope the WI-5071 no-window-containment fix?" -> "+ Consolidate inline helpers" (the comprehensive scope). Slice 1 is the first slice of that scope. `detected_via: ask_user_question`.
- **Owner directive (source-level, no global suppressor):** "stop the spawns at the source(s)... find a way to stop them from being reintroduced. DO NOT block me from manually launching any window or GUI." Constrains the design to source-level flags + CI/gate enforcement only - no local pre-commit hook, no runtime window-killer, no global hider. `detected_via: owner_directive`.

Project-scope owner-approval evidence is `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers WI-5071 by active project membership). No new owner decision is required to verify this report; the LO commit-scope decision below is surfaced for reviewer awareness, not owner approval.

## Prior Deliberations

- `bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-001.md` - approved implementation proposal, carried forward.
- `bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-002.md` - Loyal Opposition GO (Antigravity harness C, session `0072210b-cb63-4414-9a5f-80aa3188ed19`) authorizing implementation.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - governing owner directive.
- `DELIB-20266297` (WI-4896) and `DELIB-20266506` (WI-4932) - prior no-window slices; this slice extends coverage to the remaining outliers and adds the missing enforcement.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` (WI-5052 VERIFIED) - related dispatcher no-window containment; this slice closes the audit-enforcement gap that let post-VERIFIED regressions recur.

## Specification-Derived Verification Plan

Interpreter: `groundtruth-kb/.venv/Scripts/python.exe` (project venv).

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DELIB-20260707` + `GOV-RELIABILITY-FAST-LANE-001` + `ADR-CROSS-HARNESS-PARITY-001` (no automated spawn site lacks a no-window disposition) | Full-tree audit `scripts/windows_no_window_spawn_audit.py` reports `violation_count: 0`, `release_ready: true`. Explicit per-file audit confirms the three fixed sites are `compliant_no_window` (goose:144, verify_codex:143, service_sot:784). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (guard enforced, not advisory) | New real-tree pytest `test_real_tree_has_no_no_window_violations` PASSES (scans git-tracked tree, asserts `violation_count == 0`); the `_check_no_window_spawn_audit()` release-gate check runs the audit and converts exit-1 into a `GateFailure`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge discipline) | Report filed append-only as `-003` via the governed `impl_report_bridge.py file` helper; GO/NO-GO discipline preserved. |
| No-regression on touched modules | 72 existing tests PASS across `test_verify_codex_dispatch.py`, `test_codex_dotdir_acl_repair.py`, `test_gtkb_service_sot_watchdog.py`, `test_release_candidate_gate.py`, `test_release_candidate_gate_template.py`. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py` (full-tree audit)
- `groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py --json scripts/goose_harness.py scripts/verify_codex_dispatch.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py` (per-file confirmation of fixed sites)
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py platform_tests/scripts/test_release_candidate_gate.py groundtruth-kb/tests/test_release_candidate_gate_template.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <6 changed .py>`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <6 changed .py>`

## Observed Results

- Full-tree audit: `{"counts": {"compliant_no_window": 89, "interactive_allowlist": 115, "non_release_runtime": 469}, "release_ready": true, "total_findings": 673, "violation_count": 0}` (exit 0).
- Per-file audit of fixed sites: 4 findings, all `compliant_no_window`, `violation_count: 0`.
- Audit test file: **11 passed** (10 existing + the new real-tree test).
- Touched-module regression: **72 passed**.
- `ruff check`: **All checks passed!**
- `ruff format --check`: **6 files already formatted.**

## Files Changed

Committed by this WI (6 tracked files; `git diff --stat HEAD`, 53 insertions / 2 deletions):

- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `scripts/ops/install_ollama_autostart_task.ps1`
- `scripts/release_candidate_gate.py`
- `scripts/verify_codex_dispatch.py`
- `scripts/windows_no_window_spawn_audit.py`

NOT committed by this WI (see Deviations / Scope Notes):

- `scripts/goose_harness.py` - untracked WI-5072 file; the no-window fix is applied on-disk but left uncommitted.

## Deviations / Scope Notes

1. **`scripts/goose_harness.py` is UNTRACKED (WI-5072 in-progress) - descoped from the commit.** The proposal listed goose as a target (item 1, "the lone outlier"). On implementation, `git ls-files` confirms goose is untracked (not gitignored; `git check-ignore` exit 1) and no active work-intent claim holds it. To avoid capturing WI-5072's untracked file under a WI-5071 commit (attribution + commingling hazard, cf. WI-5105/WI-5112), this WI commits only the 6 tracked files. The no-window fix (`**no_window_subprocess_kwargs()`) IS applied on-disk, so goose runs headless the instant it is dispatched (and goose is currently `active=False` with dispatch quiesced, so there is no interim window risk). The `RELEASE_RUNTIME_FILES` entry for goose is committed and **pre-positions the reintroduction guard**: the moment WI-5072 tracks goose_harness.py, the audit REQUIRES it to be headless or the real-tree test / release gate fails. Coordination note for WI-5072: goose_harness.py currently carries this no-window fix plus an incidental ruff cleanup (below); its first commit will land both.

2. **`verify_antigravity_dispatch.py` deliberately NOT added to the allowlist.** The proposal (item 5) said add the "cursor/claude/antigravity verifiers for completeness." Audit shows `verify_antigravity_dispatch.py:462` has a non-compliant spawn, and that file is NOT in this WI's `target_paths`. Adding it to `RELEASE_RUNTIME_FILES` would promote its unfixed spawn to a hard `violation`, breaking the `violation_count == 0` acceptance. `verify_cursor_dispatch.py` and `verify_claude_dispatch.py` have no spawn sites (safe forward-guards) and ARE added. The antigravity verifier spawn belongs to the Antigravity console-window track (WI-5113); it is left for that WI and flagged as a follow-on.

3. **Incidental ruff cleanup of `scripts/goose_harness.py`.** The file carried pre-existing ruff debt (F401 unused `os`, UP035 `typing.Sequence`, formatting) that predates this change. Because the ruff gate must pass on changed `.py` and goose is in `target_paths`, `ruff check --fix` + `ruff format` were applied to it. These changes are on-disk only (goose is uncommitted per note 1).

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: repairs a reliability regression (visible console windows) and closes the enforcement gap that let it recur. The net-new lines are the guard test and the release-gate check that protect the repaired behavior; per the Conventional Commits type discipline a reliability-repair with protective tests remains `fix:`.

## Acceptance Criteria Status

- [x] Audit reports `violation_count == 0` (full tree) - confirmed.
- [x] Real-tree test passes - `test_real_tree_has_no_no_window_violations` PASS.
- [x] `ruff check` and `ruff format --check` both pass on changed `.py` - confirmed.
- [x] Release-gate check registered and green - `_check_no_window_spawn_audit()` added to `main()`; runs the audit (exit 0).
- [ ] `DELIB-20260707` 120-consecutive-minute clean-interval soak - owner-facing live acceptance that follows re-enabling dispatch headless across ALL slices (post-implementation); NOT a per-slice unit test. Dispatch remains quiesced per the sanctioned safe state.

## Risk And Rollback

Blast radius: four narrow no-window edits (three committed + goose on-disk), one allowlist data extension, one additive release-gate check, one new test. Additive `creationflags`/`startupinfo` are no-ops on non-Windows. No control-flow or argv change; a Windows child that previously popped a console now runs hidden. The guard is a CI/gate check plus a pytest - no local pre-commit hook, no runtime window suppression - so it cannot block the owner's local commits or manual window/GUI launches. Rollback: revert the 6 committed files; goose_harness.py is uncommitted so its on-disk edit is discarded on `git checkout`/revert of that file. No data migration, no persisted state.

## Loyal Opposition Asks

1. Verify the three committed source fixes carry a real no-window disposition and the audit classifies them `compliant_no_window`.
2. Confirm the reintroduction guard is genuinely enforced (real-tree test + release-gate check), not advisory.
3. Assess the three documented deviations (goose untracked/descoped; antigravity verifier excluded; goose ruff cleanup) - confirm they preserve the GO'd acceptance criteria and are the correct scope calls.
4. Return VERIFIED if the report and implementation satisfy the approved proposal, committing the 6 tracked files + the bridge chain; otherwise NO-GO with findings.
