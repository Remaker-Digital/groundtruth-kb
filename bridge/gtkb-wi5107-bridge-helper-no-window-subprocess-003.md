NEW

# GT-KB Bridge Implementation Report - gtkb-wi5107-bridge-helper-no-window-subprocess - 003

bridge_kind: implementation_report
Document: gtkb-wi5107-bridge-helper-no-window-subprocess
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-002.md
Approved proposal: bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5107
Recommended commit type: fix:

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: a7996a03-6874-411a-9c40-cee06222cedd
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

## Implementation Claim

The bridge-filing helper subprocess calls now run headless: each was routed
through the platform's canonical `scripts/windows_subprocess.py`
`no_window_subprocess_kwargs()` helper (the same helper `cloud_harness_base.py`
and `run_with_status.py` already use), so Windows no longer flashes a console
window during interactive bridge filing. Behavior is otherwise unchanged
(`capture_output`/pipes/`cwd`/`input`/`timeout` semantics preserved); only the
`creationflags`/`startupinfo` for window suppression were added.

This report itself was filed through the now-fixed `impl_report_bridge` +
`gtkb_bridge_writer` path (git-existence check + compliance audit), which
exercised the fix live: the internal filing subprocesses ran without console
windows.

## Files Changed

Shared writer (tracked):
- `scripts/gtkb_bridge_writer.py` — import `no_window_subprocess_kwargs`; spread it into the git-existence-check `subprocess.run` (`_bridge_file_committed_in_git`) and the compliance-audit `subprocess.run` (`run_bridge_compliance_audit`).

Canonical templates (tracked):
- `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py` — preflight-runner subprocess.
- `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` — `_git_lines` subprocess.
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` — compliance-audit subprocess.

Activated adapter copies (git-ignored; kept byte-consistent with the templates for cross-harness parity):
- `.claude/skills/bridge/helpers/revise_bridge.py`, `.claude/skills/bridge/helpers/impl_report_bridge.py`, `.claude/skills/bridge-propose/helpers/write_bridge.py`
- `.codex/skills/bridge/helpers/revise_bridge.py`, `.codex/skills/bridge/helpers/impl_report_bridge.py`, `.codex/skills/bridge-propose/helpers/write_bridge.py`
- `.cursor/skills/bridge/helpers/revise_bridge.py`, `.cursor/skills/bridge/helpers/impl_report_bridge.py`, `.cursor/skills/bridge-propose/helpers/write_bridge.py`

Test (tracked):
- `platform_tests/scripts/test_bridge_helper_no_window.py` (new).

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Windows no-window safety, now extended to the interactive bridge-filing helpers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — change to the governed bridge-filing helper path, bridge-gated.
- `GOV-RELIABILITY-FAST-LANE-001` — reliability defect repair under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage carried forward from the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test executed (below).
- `GOV-ENV-LOCAL-AUTHORITY-001` — no credential handling changed; only window-suppression flags added.
- `GOV-STANDING-BACKLOG-001` — WI-5107 backlog record.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` + WI-5107 intent | `platform_tests/scripts/test_bridge_helper_no_window.py` asserts each of the four call sites (git-check, compliance-audit, revise preflight-runner, impl-report `_git_lines`) spreads the no-window kwargs into `subprocess.run` (OS-independent via monkeypatched sentinel). Result: **4 passed**. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest + ruff evidence below. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | The change adds only `creationflags`/`startupinfo`; no credential, header, or payload is emitted; the test asserts unchanged return-value behavior. |

Executed commands and results:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_helper_no_window.py -q --tb=short --no-header
=> 4 passed, 1 warning in 0.14s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_bridge_writer.py groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/scripts/test_bridge_helper_no_window.py
=> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <same five tracked files>
=> 5 files already formatted
```

Import sanity (no regression to critical bridge infrastructure):

```text
scripts.gtkb_bridge_writer imports; no_window_subprocess_kwargs callable => True
revise_bridge (real import context) loads; no_window_subprocess_kwargs callable => True
```

## Owner Decisions / Input

- Owner reported the console-window spawning during bridge filing is disrupting work and directed via `AskUserQuestion` (2026-07-09) to proceed with WI-5107, then to implement it via the normal bridge protocol after the emergency-bootstrap edit was found blocked by the implementation-start-gate. detected_via: ask_user_question.
- Owner selected "All three, WI-5107 first" for the GO'd-fix implementation order. detected_via: ask_user_question.
- No credential, deployment, provider-account, or sandbox change was made.

## Scope Note

The fix covers the bridge-filing helper *internal* subprocesses (the dominant
window source during filing). The *outer* interactive command launch (the
harness spawning `python.exe`/`gt`/`git` for a top-level tool call) is a
separate harness-level surface, out of scope for this WI, and tracked
separately if residual outer-launch windows are observed.

## Recommended Commit Type

`fix:` — repairs an owner-observed reliability defect (console-window flashes disrupting interactive bridge filing) by routing existing subprocess calls through the platform's canonical no-window helper; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
