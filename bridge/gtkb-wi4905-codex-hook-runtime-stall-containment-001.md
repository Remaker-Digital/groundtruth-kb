NEW

# gtkb-wi4905-codex-hook-runtime-stall-containment â€” Codex Hook Runtime Stall Containment

bridge_kind: prime_proposal
Document: gtkb-wi4905-codex-hook-runtime-stall-containment
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-30T00:00:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4905

target_paths: [".codex/hooks.json", ".codex/gtkb-hooks/run_cmd_no_window.py", ".codex/gtkb-hooks/run_py_no_window.py", ".codex/gtkb-hooks/workstream-focus.cmd", ".codex/gtkb-hooks/formal-artifact-approval.cmd", "platform_tests/scripts/test_codex_hook_runtime_containment.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_cursor_hook_headless_parity.py"]

implementation_scope: config | hook_upgrade | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4905 static no-window parity was previously VERIFIED at `bridge/gtkb-wi4905-codex-hook-no-window-parity-004.md`: active Codex hook commands used `pythonw.exe` and `.cmd` hooks routed through `.codex/gtkb-hooks/run_cmd_no_window.py`. The 2026-06-29 incident revealed a second release-blocking runtime defect inside that verified surface: the wrapper suppressed visible windows but inherited hook stdin and did not impose an internal child timeout, allowing hook subprocess trees to accumulate and stall Codex tool execution.

Observed evidence after the user restarted Codex and disabled hooks: thousands of live hook subprocesses existed under `.codex/gtkb-hooks/run_cmd_no_window.py`, including `workstream-focus.cmd`, `bridge-compliance-gate.cmd`, `bridge-compliance-audit.cmd`, `formal-artifact-approval.cmd`, and `implementation-start-gate.cmd`. The release-safe fix is to treat `.codex/hooks.json` as temporarily empty until hook runtime containment is regression-tested, and to harden the shared wrapper so re-enabled hooks cannot orphan child processes or wait indefinitely on inherited stdin.

This proposal authorizes a bounded follow-up to WI-4905: keep Codex project hooks unregistered for the current release repair window, harden no-window hook wrappers with finite stdin/timeout semantics, normalize BOM-bearing `.cmd` wrappers, and add focused regression tests proving that wrapper-launched hooks exit, preserve output/exit status, time out stalled children, and leave no matching orphan hook processes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` â€” Requires bridge proposal, GO, implementation report, and verification before protected hook/config/test edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` â€” Requires concrete governing links for implementation proposals.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` â€” Requires project authorization, project, and work item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` â€” Requires report evidence mapped to cited requirements.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` â€” Requires Windows desktop/background dispatch and hook paths to avoid visible console storms and unattended process accumulation.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` â€” Requires harness-surface parity behavior to be tested or explicitly waived.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` â€” Owner directive creating release-blocking Harness Parity Phase 2 and requiring full feasible harness parity.
- `bridge/gtkb-wi4905-codex-hook-no-window-parity-001.md` through `bridge/gtkb-wi4905-codex-hook-no-window-parity-004.md` â€” prior WI-4905 static no-window hook parity implementation and verification.
- `bridge/gtkb-wi4925-cursor-headless-hooks-parity-001.md` through latest â€” Cursor parity work that reuses the Codex no-window wrapper and therefore depends on this wrapper being runtime-safe.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-004.md` â€” prior VERIFIED console-suppression work; current follow-up handles hook runtime orphaning, not dispatcher launch windows.

## Owner Decisions / Input

No new owner decision is required before LO review. The owner explicitly stated that no new console window should spawn, that the hook storm is a release showstopper, and that GT-KB must be repaired before release. The active Harness Parity Phase 2 authorization covers bounded hook/config/test repair while preserving bridge GO and verification.

## Requirement Sufficiency

Existing requirements are sufficient. The prior WI-4905 acceptance criteria proved static launcher shape only. This follow-up adds runtime safety criteria that are necessary for the same no-window goal to be release-safe in practice: finite stdin handling, bounded child execution, output/exit-code preservation, and no orphan process accumulation.

## Cross-Harness Disposition

Codex A is the implementation target because the observed stall came from Codex project hooks. Cursor E is affected indirectly because Cursor hook parity work reuses `.codex/gtkb-hooks/run_cmd_no_window.py`. Claude B, Antigravity C, Ollama D, and OpenRouter F are not mutated by this slice.

This proposal does not retire or waive any harness. It temporarily keeps Codex project hooks unregistered until the wrapper runtime is proven safe and a later governed slice deliberately re-enables a minimal hook set.

## Spec-Derived Verification Plan

Implementation report must include:

```text
python -m json.tool .codex/hooks.json
python -m py_compile .codex/gtkb-hooks/run_cmd_no_window.py .codex/gtkb-hooks/run_py_no_window.py
python -m pytest platform_tests/scripts/test_codex_hook_runtime_containment.py -q --tb=short
python -m pytest platform_tests/scripts/test_cursor_hook_headless_parity.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m ruff check .codex/gtkb-hooks/run_cmd_no_window.py .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_hook_runtime_containment.py
python -m ruff format --check .codex/gtkb-hooks/run_cmd_no_window.py .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_hook_runtime_containment.py
```

Expected runtime evidence:

- `.codex/hooks.json` remains valid JSON and intentionally contains no active hooks during containment.
- Wrapper-launched `.cmd` and `.py` hook fixtures receive finite stdin, return promptly, preserve child stdout/stderr and exit code, and enforce timeout exit `124` for stalled children.
- The two known BOM-bearing `.cmd` wrappers no longer begin with UTF-8 BOM bytes.
- A post-probe process scan finds no live hook processes matching the Codex wrapper/hook command patterns.

## Risk / Rollback

Risk: emptying `.codex/hooks.json` temporarily removes Codex-side project hook enforcement. Mitigation: this is deliberate containment during a release-blocking hook storm; Prime Builder self-enforces bridge and implementation-start rules while hooks are offline. Re-enable hooks only in a later governed slice after the runtime containment tests pass.

Rollback: restore the prior `.codex/hooks.json` and wrapper versions from git after terminating any orphaned hook process trees. Do not re-enable project hooks without first proving no-window/no-orphan behavior.

## Implementation Notes

Emergency containment has already been applied interactively to restore Codex usability after the storm. This proposal brings that containment under the bridge for verification and any additional regression-test work. If LO rejects this proposal, Prime Builder must stop further protected edits and either revert or revise per the NO-GO findings.

## Acceptance Criteria

- [ ] `.codex/hooks.json` is valid and intentionally empty for containment.
- [ ] `run_cmd_no_window.py` and `run_py_no_window.py` pass finite hook payloads to children instead of inheriting open stdin.
- [ ] Both wrappers enforce an internal timeout and return `124` on child timeout.
- [ ] Both wrappers preserve child stdout/stderr and exit status.
- [ ] BOM-bearing Codex `.cmd` wrappers are normalized to plain ASCII/UTF-8 without BOM.
- [ ] Focused regression tests and lint/format checks pass.
- [ ] A process scan after probes finds no live orphan hook processes.

## Recommended Commit Type

fix: contain Codex hook runtime stalls
