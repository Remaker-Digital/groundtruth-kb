NEW

# gtkb-wi5107-bridge-helper-no-window-subprocess — Route bridge-filing helper subprocesses through the canonical no-window helper to stop console-window flashes during interactive filing

bridge_kind: prime_proposal
Document: gtkb-wi5107-bridge-helper-no-window-subprocess
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: a7996a03-6874-411a-9c40-cee06222cedd
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5107

target_paths: ["scripts/gtkb_bridge_writer.py", "groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", ".codex/skills/bridge/helpers/revise_bridge.py", ".codex/skills/bridge/helpers/impl_report_bridge.py", ".codex/skills/bridge-propose/helpers/write_bridge.py", ".cursor/skills/bridge/helpers/revise_bridge.py", ".cursor/skills/bridge/helpers/impl_report_bridge.py", ".cursor/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_bridge_helper_no_window.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Interactive bridge filing (propose / revise / implementation-report helpers) spawns Windows console windows because the helper path's internal `subprocess.run(...)` calls do not pass the Windows no-window creation flags. During this session (S-2026-07-09), filing three P1 bridge entries in quick succession flashed console windows rapidly enough to disrupt the owner's work (owner-reported). The platform already ships a canonical no-window helper — `scripts/windows_subprocess.py` `no_window_subprocess_kwargs()` — which the harness runtime (`scripts/cloud_harness_base.py`) and the status wrapper (`scripts/run_with_status.py`) already use; the bridge-filing helpers were simply never routed through it. This proposal closes that gap so interactive bridge filing runs headless, matching the rest of the platform's Windows no-window discipline.

## Root Cause

Bridge-filing subprocess calls launched WITHOUT `creationflags=CREATE_NO_WINDOW` (each pops a brief console window on Windows):

- `scripts/gtkb_bridge_writer.py`: `_bridge_file_committed_in_git` (L41) runs `subprocess.run(["git", "log", ...])`; `run_bridge_compliance_audit` (L123) runs `subprocess.run([python, bridge-compliance-gate.py, --audit-only])`. Neither passes no-window flags.
- The bridge skill helpers' preflight/credential subprocess runners: `revise_bridge.py` `_run_preflight_command` (L281), `bridge-propose/helpers/write_bridge.py` (L379), `bridge/helpers/impl_report_bridge.py` (L246). None pass no-window flags. These exist as one canonical copy under `groundtruth-kb/templates/skills/…` plus generated adopter copies under `.claude/`, `.codex/`, `.cursor/`.

By contrast, `scripts/cloud_harness_base.py` (L992) sets `CREATE_NO_WINDOW` for its subprocess calls, and `scripts/windows_subprocess.py` provides the reusable `no_window_subprocess_kwargs()` / `hidden_startupinfo()` helpers. The bridge-filing path predates or missed that routing.

## Proposed Scope

- IP-1 (`scripts/gtkb_bridge_writer.py`): import `no_window_subprocess_kwargs` from `scripts.windows_subprocess`; spread `**no_window_subprocess_kwargs()` into the two `subprocess.run(...)` calls (git-existence check L41, compliance-audit L123). Behavior is unchanged (`capture_output`/pipes still work); only the console window is suppressed.
- IP-2 (canonical templates): apply the same routing to the three template helper subprocess runners — `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py`, `.../bridge/helpers/impl_report_bridge.py`, `.../bridge-propose/helpers/write_bridge.py` — importing the helper via the existing `scripts.*` sys.path setup those modules already use.
- IP-3 (activated adapter copies): apply the identical routing to the generated `.claude/`, `.codex/`, and `.cursor/` copies of those three helpers so the fix is live for every harness's interactive filing (kept byte-consistent with the templates per the cross-harness parity discipline).
- IP-4 (tests): add `platform_tests/scripts/test_bridge_helper_no_window.py` asserting that the bridge-filing subprocess call sites pass the no-window creation flags (patch `subprocess.run`, invoke the audit/preflight path with `force_windows`, assert `creationflags` / `startupinfo` present in the recorded call kwargs).

Out of scope: how the OUTER interactive command (the harness launching `python.exe`/`gt`/`git` for a top-level tool call) is spawned — that is a separate harness-level surface; this proposal covers the bridge-helper INTERNAL subprocesses, the dominant window source during filing.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — requires GT-KB dispatcher/background work to remain headless/no-window safe on Windows; this fix extends that discipline to the interactive bridge-filing helpers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the change is to the governed bridge-filing helper path and is bridge-gated.
- `GOV-RELIABILITY-FAST-LANE-001` — a reliability defect repair under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives a focused test from the linked no-window requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the PAUTH/project/work-item metadata above.
- `GOV-STANDING-BACKLOG-001` — WI-5107 is the backlog record for this defect.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are GT-KB platform files inside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the owner-observed defect and its fix are preserved as durable bridge/work-item evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — defect, proposal, verification, and report stay linked through governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-5107 advances through the standard defect-fix lifecycle triggers.

## Prior Deliberations

- `bridge/gtkb-wi5049-headless-spawn-guardrails-008.md` — the WI-5049 headless-spawn / no-window guardrails (auto_finalize_sweep console window) — same Windows no-window-hygiene family this fix extends to the filing helpers.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` — dispatcher no-window containment; adjacent no-window discipline precedent.
- `bridge/gtkb-wi5066-openrouter-silent-stall-timeout-005.md` — the sibling reliability thread; both are Windows-headless robustness fixes in the same session's program.

## Owner Decisions / Input

- Owner reported (2026-07-09) that the bridge-filing console-window spawning is disrupting work — more than a nuisance — and directed via `AskUserQuestion` to **"proceed with WI-5107 (the no-window helper gap)"**. detected_via: ask_user_question.
- Owner selected **"Normal protocol, I file"** after the emergency-bootstrap direct edit was found to be blocked by the implementation-start-gate (the `GTKB_EMERGENCY_BRIDGE_REPAIR` exemption is scoped to the bridge-control surface and does not cover the bridge writer / skill helpers). detected_via: ask_user_question.
- No credential, deployment, provider-account, or sandbox-weakening action is requested or authorized.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (Windows no-window safety), WI-5107's acceptance intent, and `GOV-RELIABILITY-FAST-LANE-001` govern this bounded defect repair. No new or revised requirement is required before implementation.

## Spec-Derived Verification Plan

Focused test lands in `platform_tests/scripts/test_bridge_helper_no_window.py`. Reproducible evidence via the repo venv:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_helper_no_window.py -q --no-header
```

Spec-to-test mapping:

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` + WI-5107 intent →
  - **T1:** patch `subprocess.run` in `gtkb_bridge_writer`; invoke `run_bridge_compliance_audit` and `_bridge_file_committed_in_git`; assert the recorded call kwargs carry the no-window creation flags (via `no_window_subprocess_kwargs(force_windows=True)`), and that behavior (return value / capture) is unchanged.
  - **T2:** patch `subprocess.run` in the bridge helper preflight runner; invoke it; assert the recorded call kwargs carry the no-window creation flags.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → the implementation report runs the focused pytest plus `ruff check` / `ruff format --check` on the changed Python and cites exact results.

Post-fix confirmation: filing the WI-5107 implementation report itself runs through the now-fixed helpers and MUST not flash console windows (a live no-regression signal recorded in the report).

## Risk / Rollback

- Risk: passing `startupinfo`/`creationflags` could interact with existing `subprocess.run` kwargs. Mitigation: `no_window_subprocess_kwargs()` returns only `creationflags` + `startupinfo` (both additive, non-conflicting with `capture_output`/`cwd`/`input`/`timeout`); T1/T2 assert unchanged behavior; the helper is already proven in `run_with_status.py` and `cloud_harness_base.py`.
- Risk: adapter-copy drift between templates and the generated `.claude`/`.codex`/`.cursor` copies. Mitigation: apply the identical edit to all copies (or regenerate) and keep them byte-consistent per the cross-harness parity discipline.
- Rollback: single-commit revert of the changed lines restores prior (window-spawning) behavior; no data, credential, or KB change is involved.

## Recommended Commit Type

`fix:` — repairs an owner-observed reliability defect (console-window flashes disrupting interactive bridge filing) by routing existing subprocess calls through the platform's canonical no-window helper; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
