NEW

# gtkb-wi5049-headless-sweep-git-and-audit-guard-repair — Headless the auto_finalize_sweep git spawns and repair the crashed no-window audit guard

bridge_kind: prime_proposal
Document: gtkb-wi5049-headless-sweep-git-and-audit-guard-repair
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-06 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 66422d1e-3091-47fa-a848-f5468485ec45
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5049

target_paths: ["scripts/auto_finalize_sweep.py", "scripts/windows_no_window_spawn_audit.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner-reported (2026-07-06, screenshot): a visible console window
`git -C E:\GT-KB ls-files --others --exclude-standard bridge` flashes on Windows.
Root cause: `scripts/auto_finalize_sweep.py._git` spawns git via a **raw**
`subprocess.run(...)` with no Windows no-window `creationflags`. Because the
sweep is registered as a `Stop` hook (`.claude/settings.json` / `.codex/hooks.json`),
it runs on every turn-end and the WI-4871 enumeration
(`git ls-files --others --exclude-standard bridge`) pops a console window each time.

The repo already has the fix pattern — `scripts/windows_subprocess.no_window_subprocess_kwargs()`
returns `{creationflags: CREATE_NO_WINDOW}` on Windows (no-op elsewhere) — and an
established owner requirement that Windows hook launches be headless
(`DELIB-20260702`). The reason this offender slipped through is a **second
defect**: the enforcing audit `scripts/windows_no_window_spawn_audit.py` crashes
with `FileNotFoundError` in `scan_file` when `git ls-files *.py` returns a
tracked-but-missing path (`platform_tests/scripts/test_doctor_kill_switch_staleness.py`),
so the mechanical guard that would have caught the raw spawn is not running.

**Fix (two small source changes):**

1. `auto_finalize_sweep.py._git` — import `no_window_subprocess_kwargs` from the
   sibling `windows_subprocess` module (adding the `scripts` dir to `sys.path`
   consistent with the module's existing sibling-import convention) and pass
   `**no_window_subprocess_kwargs()` into the `subprocess.run(...)` call, so all
   sweep git invocations spawn headless on Windows.
2. `windows_no_window_spawn_audit.py.scan_file` — treat a missing path as a
   skip (return no findings on `FileNotFoundError`) so the audit completes and
   mechanically enforces no-window compliance across the tracked Python surface,
   catching this offender and preventing recurrence.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — this is a small, low-risk reliability defect
  fix eligible for the reliability fast-lane; filed under the project's standing
  authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `auto_finalize_sweep.py` is bridge
  finalization infrastructure; the fix preserves its audit-trail behavior while
  only changing subprocess window visibility.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries
  Project + Work Item + Project Authorization linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives checks from the fixed behavior.
- `GOV-STANDING-BACKLOG-001` — WI-5049 is the governing backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — owner directive captured as
  a durable WI + bridge artifact chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented stance
  for the WI/proposal chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle trigger for the
  owner-reported defect capture.

## Prior Deliberations

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` — the
  governing owner requirement: AUQ-adjacent and hook launches must be headless on
  Windows. This proposal extends that requirement's coverage to the
  auto_finalize_sweep `Stop` hook, which was not headless.
- `DELIB-20263477` (WI-4529 Windows Dispatch Console Window Bridge Gap) — prior
  work on the same Windows console-window class for dispatch subprocesses; this
  is the sweep-hook analogue.
- `DELIB-20263310` (Windows Spawn No-Window Flag for Bridge-Dispatch Subprocesses)
  — establishes the `CREATE_NO_WINDOW` remedy pattern reused here via the shared
  `windows_subprocess` helper.
- WI-4959 (Suppress AUQ-adjacent hook console windows on Windows) — the sibling
  precedent fix; WI-5049 is the same fix class applied to a hook the earlier work
  did not cover, plus repair of the audit guard that should have flagged it.

## Owner Decisions / Input

This fix is directed by the owner and authorized under the reliability fast-lane:

- **Owner directive (this session, 2026-07-06):** "We want all console windows to
  be headless. Please find and fix this issue." (with a screenshot of the
  `git ls-files ... bridge` console window).
- **Standing owner requirement:** `DELIB-20260702` — AUQ-adjacent/hook launches
  must be headless on Windows.
- **Authorization:** `GOV-RELIABILITY-FAST-LANE-001` via
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers WI-5049 by active
  project membership; owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`).

No further owner decision is required to review this proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** The headless-on-Windows requirement already
exists (`DELIB-20260702`) and reliability fast-lane eligibility is governed by
`GOV-RELIABILITY-FAST-LANE-001`. This proposal applies those existing
requirements to a newly-identified offender and repairs the guard that enforces
them; no new or revised requirement is needed.

## Spec-Derived Verification Plan

- `DELIB-20260702` headless requirement → after the fix, run the repaired audit
  and confirm `auto_finalize_sweep.py` is clean:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py`
  → completes without `FileNotFoundError`; summary `violation_count: 0`,
  `release_ready: true`.
- Audit-guard repair → add/confirm a unit test that `scan_file` returns no
  findings for a missing path, then run the audit test suite:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py -q --no-header`
  (create the test if absent) → green.
- Sweep behavior unchanged (regression) →
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_auto_finalize_verified_verdicts.py -q --no-header`
  → green (headless spawn does not alter enumeration/finalization semantics).
- Shared helper unchanged →
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_windows_subprocess.py -q --no-header`
  → green.
- Code quality on changed files → `ruff check` and `ruff format --check` on
  `scripts/auto_finalize_sweep.py` and `scripts/windows_no_window_spawn_audit.py`
  → clean.

## Risk / Rollback

- **Low risk.** (1) `no_window_subprocess_kwargs()` adds `creationflags` only on
  Windows (`os.name == "nt"`) and is a no-op elsewhere; it changes window
  visibility only, not git behavior, output capture, or exit handling. (2) The
  audit `scan_file` change only skips paths that are not on disk (a
  tracked-but-missing file cannot be scanned anyway), so it removes a crash
  without weakening coverage of real files.
- **Rollback.** Single revert of the two-file change restores prior behavior; no
  data or state migration is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5049-headless-sweep-git-and-audit-guard-repair`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs broken behavior (a visible console window on every turn-end and a
crashing enforcement audit). No new capability surface is added; both changes are
defect repairs to existing scripts.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
