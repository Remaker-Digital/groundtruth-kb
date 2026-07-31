NEW

# gtkb-wi5071-no-window-source-fixes-reintroduction-guard — Slice 1: fix the found console-window spawn sources + enforce the reintroduction guard

bridge_kind: prime_proposal
Document: gtkb-wi5071-no-window-source-fixes-reintroduction-guard
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 054bb30f-56ef-436b-a5d6-ad07f7b29dd6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; resolved_role=prime-builder (session-stated ::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5071

target_paths: ["scripts/goose_harness.py", "scripts/verify_codex_dispatch.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py", "scripts/ops/install_ollama_autostart_task.ps1", "scripts/windows_no_window_spawn_audit.py", "scripts/release_candidate_gate.py", "platform_tests/scripts/test_windows_no_window_spawn_audit.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5071 is the open P1 reliability regression under `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`: "no visible console windows may spawn on this workstation. There is no exception." The owner directed (this session, 2026-07-09) that the spawns be stopped at the source(s), without halting work, with a mechanism that prevents reintroduction, and — critically — WITHOUT any global suppressor that would also block the owner's own manual window/GUI launches.

An exhaustive inventory (structured investigation, this session) found the automated dispatcher-to-worker chain is already centrally headless: the daemon launches each worker through `scripts/run_with_status.py`, which applies `CREATE_NO_WINDOW | DETACHED_PROCESS` plus a hidden `STARTUPINFO` (`SW_HIDE`), and the static audit `scripts/windows_no_window_spawn_audit.py` currently reports `violation_count: 0`. There is NO repo-level global window suppressor — the only global hider is a host-local `.pyw` outside the repo (`CodexConsoleWindowHider`, currently Disabled) — so a source-level fix plus a source-level lint honors the "do not block my manual launches" constraint by construction.

This Slice 1 fixes the concrete automated spawn-source gaps the inventory found and, most importantly, closes the reintroduction hole: the audit tool exists but is wired into NO enforcement path (not CI, not the release gate, not a pre-commit) and its allowlist under-covers the automated surface, so a newly-introduced console spawn would not be caught.

Scope of Slice 1 (of the owner-approved comprehensive program; scope AUQ answer "+ Consolidate inline helpers" this session — later slices cover the inline-helper consolidation and the `.claude`-hook headless parity):

1. `scripts/goose_harness.py` — the goose CLI launch (`subprocess.run`, near line 154) has no `creationflags`; goose (harness G) is a registered dispatch target, so when dispatched it runs as a console-less grandchild and the console child gets a NEW visible console. Every sibling harness applies the no-window disposition; goose is the lone outlier. Add `**no_window_subprocess_kwargs()` (import from `scripts/windows_subprocess.py`).
2. `scripts/verify_codex_dispatch.py` — the `powershell -File repair_codex_dotdir_acl.ps1` runner (near line 140) skips the window suppression that every peer verifier applies. Add the hidden-process kwargs (mirror the sibling verifiers).
3. `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py` — the installer runner (`subprocess.run` of `powershell.exe … install_service_sot_watchdog_task.ps1`, near line 778) omits `CREATE_NO_WINDOW` even though the module's own `_run_powershell` probe helper (near line 553) sets it. Mirror the helper's disposition.
4. `scripts/ops/install_ollama_autostart_task.ps1` — the registered logon task (`New-ScheduledTaskSettingsSet`, near line 50) has no `-Hidden` and uses `-LogonType Interactive` with `ollama.exe serve` (a console process), so it can surface a console at logon. Add `-Hidden` to match every other GT-KB task installer.
5. `scripts/windows_no_window_spawn_audit.py` — extend the allowlist so the automated files above are actually checked: add `scripts/goose_harness.py` and the dispatch verifiers (`verify_codex_dispatch.py`, plus the cursor/claude/antigravity verifiers for completeness) to `RELEASE_RUNTIME_FILES`, and add `groundtruth-kb/src/groundtruth_kb/watchdog/` to `RELEASE_RUNTIME_PREFIXES`.
6. `scripts/release_candidate_gate.py` — add a `_check_no_window_spawn_audit()` gate that runs the audit and fails the gate when `violation_count > 0`; register it in `main()`.
7. `platform_tests/scripts/test_windows_no_window_spawn_audit.py` — add a real-tree test that runs `scan_paths` over the git-tracked tree and asserts `violation_count == 0`. Because `platform_tests` runs in CI (`groundtruth-kb-tests.yml`, `python-tests.yml`), this makes the guard self-enforcing in CI. It is a CI/gate check, NOT a local pre-commit hook and NOT a runtime window-killer, so it never blocks the owner's local commits or manual launches.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — reliability fast-lane; WI-5071's home (PROJECT-GTKB-RELIABILITY-FIXES) and the authority for this bounded defect fix.
- `ADR-CROSS-HARNESS-PARITY-001` — the goose_harness fix brings goose to no-window parity with every sibling harness launcher; the allowlist extension covers the per-harness verifiers uniformly.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline governing this proposal and its verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing spec.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/WI linkage metadata present (WI-5071 / PROJECT-GTKB-RELIABILITY-FIXES / PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the verification plan maps the fix to the real-tree audit test.
- `GOV-STANDING-BACKLOG-001` — MemBase work_items is the canonical backlog authority; WI-5071 is tracked there under PROJECT-GTKB-RELIABILITY-FIXES.

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — the governing owner directive ("no visible console windows… no exception"; 120-consecutive-minute clean acceptance; dispatcher may remain quiesced during repair). WI-5071's `source_owner_directive`. This slice implements the durable source-level suppression plus reintroduction guard that directive requires.
- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` — AUQ-adjacent / UserPromptSubmit hook children must be headless; motivates the later `.claude`-hook parity slice (out of Slice 1 scope, tracked as a follow-on).
- `DELIB-20266297` (WI-4896 dispatcher console-window suppression) and `DELIB-20266506` (WI-4932 Cursor no-window launcher) — prior no-window slices that made the daemon/stop-hook/bridge-launcher/Cursor surfaces headless; this slice extends that coverage to the remaining outliers (goose, service_sot installer, codex-dotdir verifier, ollama task) and adds the missing enforcement.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` (WI-5052 VERIFIED) — the dispatcher_runtime Popen no-window containment; WI-5071's `related_bridge_thread`. This slice complements it by closing the audit-enforcement gap that let post-VERIFIED regressions recur.

## Owner Decisions / Input

This proposal depends on owner approval. Authorizing evidence (all this session, 2026-07-09, interactive Prime Builder, harness B):

- **Owner directive:** "I want the spawns to be stopped, at the source(s), without halting work. Find them all and fix them and find a way to stop them from being reintroduced. DO NOT block me from manually launching any window or GUI if I choose." Authorizes this source-level fix plus reintroduction guard and constrains the design to exclude any global window suppressor. `detected_via: owner_directive`.
- **Owner AUQ (scope):** "How should I scope the WI-5071 no-window-containment fix?" -> "+ Consolidate inline helpers" — the comprehensive scope (concrete spawn fixes + guard + `.claude` parity + inline-helper consolidation). Slice 1 is the first slice of that comprehensive scope; consolidation and `.claude`-hook parity follow as later slices. `detected_via: ask_user_question`.
- **Owner AUQ (host-local cleanup):** per the chosen option, the owner authorized purging the leaked `GTKB-SingleHarness-E2E-Test-*` scheduled tasks (done this session) and will delete the external `CodexConsoleWindowHider`. `detected_via: ask_user_question`.
- **Standing directive:** `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` (owner_decision).

Project-scope owner-approval evidence is `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, which covers WI-5071 by active project membership. Implementation authority remains gated by Loyal Opposition GO plus the implementation-start authorization packet.

## Requirement Sufficiency

Existing requirements sufficient. This is a defect/regression fix under `GOV-RELIABILITY-FAST-LANE-001` (WI-5071) implementing the standing owner directive `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`. No new requirement is needed to authorize it.

## Spec-Derived Verification Plan

Interpreter: the project venv (`groundtruth-kb/.venv/Scripts/python.exe`).

Spec-to-test mapping:

- `DELIB-20260707` + `GOV-RELIABILITY-FAST-LANE-001` + `ADR-CROSS-HARNESS-PARITY-001` (no automated spawn site lacks a no-window disposition) -> the new real-tree test in `platform_tests/scripts/test_windows_no_window_spawn_audit.py` asserting `scan_paths` over the git-tracked tree returns `violation_count == 0` with the extended allowlist in force. This test fails if any of the four fixed sites (or a future regression) reintroduces an unguarded spawn.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (guard is enforced, not advisory) -> the `_check_no_window_spawn_audit()` gate in `release_candidate_gate.py` is exercised by the existing gate test surface; the real-tree audit test proves the guard's scan classifies the newly-allowlisted files as release-runtime.

Verification commands (run in a gate-satisfied environment after implementation):

- Run the audit directly and confirm zero violations with the extended allowlist: `groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py`.
- pytest the audit test file (`platform_tests/scripts/test_windows_no_window_spawn_audit.py`) — includes the classification-logic tests plus the new real-tree zero-violation test.
- Code quality, BOTH separate gates on the changed .py: `python -m ruff check <changed>` AND `python -m ruff format --check <changed>`.
- Confirm the release gate registers and passes the new check.

Acceptance: audit reports `violation_count == 0`; the real-tree test passes; ruff check and ruff format --check both pass; the release-gate check is registered and green. The `DELIB-20260707` 120-consecutive-minute clean-interval soak is the owner-facing live acceptance that follows re-enabling dispatch headless (post-implementation, across all slices), not a per-slice unit test.

## Risk / Rollback

Blast radius: four narrow spawn-disposition edits (adding no-window flags — strictly additive; on non-Windows the flags are no-ops), one allowlist extension (data-only), one release-gate check (additive), one new test. None changes control flow or the harness argv; a Windows child that previously popped a console now runs hidden. The guard is a CI/gate check and a pytest — no local pre-commit hook and no runtime window suppression, so it cannot block the owner's local commits or manual window/GUI launches. Rollback: revert the seven files; no data migration, no persisted state.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5071-no-window-source-fixes-reintroduction-guard`; append-only. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: — repairs a reliability regression (visible console windows) and closes the enforcement gap that let it recur. The net-new lines are the guard test and the release-gate check that protect the repaired behavior; per the Conventional Commits type discipline a reliability-repair with protective tests remains `fix:`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
