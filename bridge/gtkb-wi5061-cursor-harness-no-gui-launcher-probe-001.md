NEW

# gtkb-wi5061-cursor-harness-no-gui-launcher-probe — Stop cursor_harness from probing the Cursor GUI launcher (which opens the desktop IDE)

bridge_kind: prime_proposal
Document: gtkb-wi5061-cursor-harness-no-gui-launcher-probe
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
Work Item: WI-5061

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner-reported: the **Cursor desktop IDE launches unexpectedly** (several times;
manually exited each). Root cause: `scripts/cursor_harness.py`
`_cursor_supports_agent_subcommand` (lines 51–68) runs
`subprocess.run([cursor_executable, "agent", "--help"], creationflags=CREATE_NO_WINDOW)`
where `cursor_executable` can be a **GUI launcher** name from
`_CURSOR_GUI_LAUNCHER_NAMES` (`cursor` / `cursor.cmd` / `cursor.exe`). On Windows
`CREATE_NO_WINDOW` suppresses only a **console** window, not a **GUI** window — so
probing `cursor.exe agent --help` opens the Cursor IDE. This is the fallback path
in `_resolve_agent_command` (lines 151–153), reached when the standalone
`cursor-agent` CLI is not found via `_windows_cursor_agent_direct_commands()`
(which hunts a `%LOCALAPPDATA%\cursor-agent\versions\<v>\node.exe` + `index.js`
layout that a Cursor update likely moved). The trigger is any harness-availability
probe that runs cursor command-resolution (`_bootstrap_cursor_harness.py`,
`verify_cursor_dispatch.py`, `harness_parity_phase2.py`) — **not** the dispatcher
(harness E is `can_receive_dispatch=false`; the daemon has no cursor references)
and **not** the storm watchdog.

**Fix (trigger-agnostic).** Restrict cursor-agent-CLI resolution AND the
`agent --help` capability probe to **standalone** `agent` / `cursor-agent`
executables only. `_cursor_supports_agent_subcommand` must refuse to run
`agent --help` against any GUI-launcher name (`cursor` / `cursor.cmd` /
`cursor.exe`); `_resolve_agent_command` must drop the GUI-launcher fallback
(lines 151–153). A missing standalone agent must fail closed with the existing
`CursorHarnessError` guidance (set `CURSOR_AGENT_BIN` to a standalone agent),
never by launching the IDE. (Optionally, broaden `_windows_cursor_agent_direct_commands`
to tolerate current install layouts, but that is secondary — the load-bearing
fix is never invoking a GUI launcher.)

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — small, low-risk reliability defect fix filed
  under the project's standing authorization.
- `GOV-HARNESS-ISOLATION-001` — harnesses are clients confined to bridge + `gt`
  CLI surfaces; a harness shim inadvertently spawning its vendor's GUI IDE is
  an unwanted side-effect outside those surfaces, which this fix removes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority under which this
  proposal is recorded.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item +
  Project Authorization linkage present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives a test from the fixed behavior.
- `GOV-STANDING-BACKLOG-001` — WI-5061 is the governing backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — owner-reported defect
  captured as a durable WI + bridge artifact chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented stance
  for the WI/proposal chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle trigger for the
  owner-reported defect capture.

## Prior Deliberations

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` — the
  owner requirement that Windows launches be headless. The unexpected Cursor IDE
  window is a headless-on-Windows violation of the same class (though a GUI, not
  a console, window — which is precisely why the existing `CREATE_NO_WINDOW` guard
  is insufficient here).
- `INTAKE-c60bf094` — "Prohibit direct harness-to-harness invocation"; related
  harness-discipline lineage now formalized as `GOV-HARNESS-ISOLATION-001` (this
  session). This fix keeps the cursor shim resolving its headless agent CLI
  cleanly instead of spawning the vendor GUI.
- _No prior deliberations specific to the cursor GUI-launcher probe: this is a
  newly-identified defect from a Cursor install-layout change surfaced by the
  owner on 2026-07-06._

## Owner Decisions / Input

This fix is directed by the owner and authorized under the reliability fast-lane:

- **Owner directive (this session, 2026-07-06):** "The Cursor desktop UI has
  recently been launched several times for no reason. I manually exited it each
  time."
- **AskUserQuestion (this session):** owner selected "Suspend cursor/E now + file
  the fix" — cursor/E has been suspended as an interim mitigation, and this
  proposal is the durable fix.
- **Authorization:** `GOV-RELIABILITY-FAST-LANE-001` via
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers WI-5061 by active
  project membership; owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`).

## Requirement Sufficiency

**Existing requirements sufficient.** The headless-on-Windows requirement
(`DELIB-20260702`) and reliability fast-lane eligibility
(`GOV-RELIABILITY-FAST-LANE-001`) already govern this; the fix applies them to a
newly-identified cursor-shim offender. No new or revised requirement is needed.

## Spec-Derived Verification Plan

- `DELIB-20260702` (headless) / `GOV-HARNESS-ISOLATION-001` → add a unit test to
  `platform_tests/scripts/test_cursor_harness.py` asserting that agent-CLI
  resolution never invokes a GUI-launcher executable: with the standalone agent
  absent, `_resolve_agent_command` raises `CursorHarnessError` (fail-closed) and
  `subprocess.run` is **never** called with an argv whose executable is
  `cursor`/`cursor.cmd`/`cursor.exe` and args `["agent","--help"]`. Run:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py -q --no-header` → green.
- Regression → `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_cursor_dispatch.py -q --no-header`
  → green (standalone-agent dispatch path unchanged).
- Code quality → `ruff check` and `ruff format --check` on
  `scripts/cursor_harness.py` and `platform_tests/scripts/test_cursor_harness.py`
  → clean.

## Risk / Rollback

- **Low risk.** The change removes an incorrect fallback (probing a GUI launcher);
  it does not alter the standalone-agent dispatch path that already works. The
  only behavioral change is that a system with no standalone `cursor-agent` now
  fails closed with actionable guidance (`CURSOR_AGENT_BIN`) instead of silently
  opening the IDE — the correct behavior.
- **Rollback.** Single revert of the two-file change. Bridge audit files remain
  append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5061-cursor-harness-no-gui-launcher-probe`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs an unexpected GUI-launch side-effect (the Cursor IDE opening on a
capability probe); no new capability surface is added.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
