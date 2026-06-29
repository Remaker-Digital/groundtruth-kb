NEW

# gtkb-wi4905-codex-hook-no-window-parity (Slice 1) — Codex Hook No-Window Parity Repair

bridge_kind: prime_proposal
Document: gtkb-wi4905-codex-hook-no-window-parity
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29T08:19:26Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4905

target_paths: [".codex/hooks.json", ".codex/config.toml", ".codex/gtkb-hooks/**", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "scripts/check_harness_parity.py"]

implementation_scope: config | hook_upgrade | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The current release-focused dispatcher test bundle fails
`platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_codex_hook_commands_do_not_use_foreground_console_launchers`.
The failure reports 28 foreground Codex hook commands in `.codex/hooks.json`,
including `python ... active_session_heartbeat.py`, even though there is no
acceptable user experience where routine hook activity opens visible Windows
console windows.

This proposal authorizes a narrow WI-4905 repair: update Codex hook registration
and, if needed, local Codex hook wrapper surfaces so every active Codex hook
launches through a no-window path or an explicit breaker mode. The repair must
preserve hook semantics, avoid production dispatcher routing changes, and keep
the test as a release guard. It is a prerequisite for safely running the
WI-4924 daemon live smoke without reintroducing console bursts.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Requires bridge proposal, LO GO, implementation report, and verification before protected hook/config/test edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires concrete governing links for this implementation proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires the project authorization, project, and work item headers above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Requires implementation-report evidence mapped to the linked requirements.
- `GOV-STANDING-BACKLOG-001` — Requires release-blocking harness parity work to be tracked as durable backlog, not scratch diagnosis.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Requires Windows desktop/background dispatch and hook paths to avoid visible console-window storms.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — Requires harness-surface behavior to be parity-reviewed or explicitly waived.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` — Owner directive creating release-blocking Harness Parity Phase 2 and requiring full feasible harness parity.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-004.md` — Prior VERIFIED console-suppression work; current test failure shows residual or regressed Codex hook configuration.
- `bridge/gtkb-wi4896-daemon-loop-console-residual-004.md` — Prior VERIFIED daemon-loop console residual thread; this proposal handles the remaining hook configuration surface.
- `bridge/gtkb-wi4924-daemon-recipient-state-migration-dedup-repair-001.md` — Current daemon dedupe repair whose live smoke is blocked until Codex hook no-window behavior is restored.

The seeded unrelated deliberations were pruned. This slice builds on the
verified WI-4896 console-suppression program by closing the remaining active
Codex hook registration gap surfaced by the release test.

## Owner Decisions / Input

No new owner decision is required before LO review. The owner has explicitly
stated that no new console window should spawn, and the Phase 2 project
authorization (`DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`) covers
bounded hook/config/test repairs while preserving bridge GO and verification.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4905 explicitly requires expanding
the no-window process-spawn audit to every harness launcher, verifier, benchmark
runner, and recurring worker. This first slice targets the concrete Codex hook
configuration failure currently blocking release smoke.

## Cross-Harness Disposition

Applicable harnesses: Codex A directly; Claude B, Cursor E, Antigravity C,
Ollama D, and OpenRouter F as parity comparison surfaces.

- Codex A is the implementation target because `.codex/hooks.json` currently
  contains foreground commands and the failing test is Codex-specific.
- Claude B is not changed by this slice; Claude-native hook behavior remains a
  parity reference, not a mutation target.
- Cursor E and Antigravity C are not mutated by this slice; their broader
  no-window and readiness work remains under WI-4903/WI-4905 follow-on slices.
- Ollama D and OpenRouter F are not mutated by this slice; provider-wrapper
  no-window/readiness work remains under WI-4904/WI-4905 follow-on slices.

No owner-approved typed waiver is introduced. If any Codex hook cannot be made
no-window without disabling required governance behavior, implementation must
stop and return with the exact owner decision needed.

## Spec-Derived Verification Plan

Implementation report must include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_codex_hook_commands_do_not_use_foreground_console_launchers -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

Expected result: no Codex hook command starts with `python`, `cmd /d /s /c`,
`powershell.exe`, or `pwsh.exe`; active commands either route through
`pythonw.exe` or an explicit breaker mode. The broader focused bundle should no
longer fail on the Codex no-window hook test.

## Risk / Rollback

Risk: changing hook command wrappers can silently disable a governance hook or
break hook argument quoting on Windows. Mitigation: preserve the existing hook
entries and command semantics while changing only the launch surface, then
verify with the existing static test. Rollback is a single commit reverting
`.codex/hooks.json`, any `.codex/gtkb-hooks/**` wrapper changes, and the
associated test adjustments.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4905-codex-hook-no-window-parity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — repairs a release-blocking Codex hook configuration regression that
causes visible Windows console launches and blocks dispatcher smoke testing.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
