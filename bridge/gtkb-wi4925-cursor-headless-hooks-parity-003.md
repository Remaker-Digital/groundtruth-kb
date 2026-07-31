NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-06-29T19-09-10Z-prime-builder-A-3e6fe3
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex headless bridge auto-dispatch; resolved role prime-builder; approval_policy=never

# GT-KB Bridge Implementation Report - gtkb-wi4925-cursor-headless-hooks-parity - 003

bridge_kind: implementation_report
Document: gtkb-wi4925-cursor-headless-hooks-parity
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4925-cursor-headless-hooks-parity-002.md
Approved proposal: bridge/gtkb-wi4925-cursor-headless-hooks-parity-001.md
Recommended commit type: fix:

## Implementation Claim

Implemented the approved Cursor headless hook parity slice within the GO-scoped target paths only:

- Updated `.cursor/hooks.json` so every Cursor hook command launches with `pythonw.exe` rather than console-attached `python`.
- Replaced raw Cursor `.cmd` hook launches with `pythonw.exe E:\GT-KB\.codex\gtkb-hooks\run_cmd_no_window.py E:\GT-KB\.cursor\gtkb-hooks\workstream-focus.cmd`.
- Updated `.cursor/gtkb-hooks/workstream-focus.cmd` so its inner Python invocation uses `pythonw.exe`.
- Updated `scripts/cursor_hook_adapter.py` so the inner hook-script `subprocess.run` uses `CREATE_NO_WINDOW` on Windows.
- Added `platform_tests/scripts/test_cursor_hook_headless_parity.py` to lock the launcher and adapter contracts.

This implementation preserves Cursor hook event names, matchers, ordering, and timeouts. It does not change dispatcher topology, hook semantics, Codex hooks, Claude hooks, or the Cursor Agent Shell runtime itself.

## Authorization Evidence

- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4925-cursor-headless-hooks-parity --session-id 2026-06-29T19-09-10Z-prime-builder-A-3e6fe3` acquired rowid `25133`.
- Implementation-start packet: `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4925-cursor-headless-hooks-parity --session-id 2026-06-29T19-09-10Z-prime-builder-A-3e6fe3` returned packet `sha256:021d0e4056284ada7b4fb3684a6808824bad7cb4f3378bd17b6721cb1a227d45`.
- Target validation: `.cursor/hooks.json`, `scripts/cursor_hook_adapter.py`, `.cursor/gtkb-hooks/workstream-focus.cmd`, and `platform_tests/scripts/test_cursor_hook_headless_parity.py` each returned `authorized: true` from `scripts/implementation_authorization.py validate --target`.
- Live bridge state: `show_thread_bridge.py gtkb-wi4925-cursor-headless-hooks-parity --format json` showed latest status `GO` at `bridge/gtkb-wi4925-cursor-headless-hooks-parity-002.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The headless auto-dispatch worker cannot interactively ask the owner and did not need a blocking owner decision to complete the code and automated verification scope.

## Prior Deliberations

- `bridge/gtkb-wi4925-cursor-headless-hooks-parity-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4925-cursor-headless-hooks-parity-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `_No additional deliberation search result is cited in this implementation report; this report carries forward the approved proposal and GO verdict.`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work-intent claim rowid `25133`; implementation-start packet `sha256:021d0e4056284ada7b4fb3684a6808824bad7cb4f3378bd17b6721cb1a227d45`; all four GO-scoped targets validated as authorized. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked specification set and maps each linked surface to command or authorization evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start packet resolved `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, `PROJECT-GTKB-RELIABILITY-FIXES`, and `WI-4925`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff lint, ruff format check, and JSON parse commands executed; the manual visual Cursor spot-check remains unperformed and is recorded below. |
| `GOV-STANDING-BACKLOG-001` | Packet and GO both bind the implementation to `WI-4925`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Packet reports active standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation is reported through the bridge audit chain as `bridge/gtkb-wi4925-cursor-headless-hooks-parity-003.md`. |
| `ADR-CROSS-HARNESS-PARITY-001` | New parity test asserts Cursor hook launch disposition uses the shared no-window pattern. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `platform_tests/scripts/test_cursor_hook_headless_parity.py` fails if bare Cursor `python` hook commands, raw `.cmd` launches, or missing adapter no-window disposition are reintroduced. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Cursor `.cmd` hook launches now reuse `.codex/gtkb-hooks/run_cmd_no_window.py`, and direct Python hook launchers use `pythonw.exe`. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4925-cursor-headless-hooks-parity --format json --preview-lines 260
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4925-cursor-headless-hooks-parity --session-id 2026-06-29T19-09-10Z-prime-builder-A-3e6fe3
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4925-cursor-headless-hooks-parity --session-id 2026-06-29T19-09-10Z-prime-builder-A-3e6fe3
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target .cursor/hooks.json
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target scripts/cursor_hook_adapter.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target .cursor/gtkb-hooks/workstream-focus.cmd
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target platform_tests/scripts/test_cursor_hook_headless_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_hook_headless_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cursor_hook_adapter.py platform_tests/scripts/test_cursor_hook_headless_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format scripts/cursor_hook_adapter.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cursor_hook_adapter.py platform_tests/scripts/test_cursor_hook_headless_parity.py
groundtruth-kb/.venv/Scripts/python.exe -c "import json; json.loads(open('.cursor/hooks.json', encoding='utf-8').read()); print('ok')"
```

## Observed Results

- Role resolution: Codex harness `A` resolves to `prime-builder`.
- Dispatcher status: `WARN`; selected Prime Builder candidate remains `A`. Warnings were dispatch-runtime availability warnings, not a status change for this selected GO thread.
- Thread state: latest bridge status is `GO` at `bridge/gtkb-wi4925-cursor-headless-hooks-parity-002.md`.
- Claim and packet: work-intent claim rowid `25133`; implementation packet `sha256:021d0e4056284ada7b4fb3684a6808824bad7cb4f3378bd17b6721cb1a227d45`.
- Target validation: all four changed implementation paths returned `authorized: true`.
- Pytest: `4 passed` in `platform_tests/scripts/test_cursor_hook_headless_parity.py`; pytest emitted one cache warning about `.pytest_cache` path creation, unrelated to this test's assertions.
- Ruff lint: `All checks passed!`
- Ruff format: initial `--check` required formatting `scripts/cursor_hook_adapter.py`; after running `ruff format`, final `ruff format --check` reported `2 files already formatted`.
- `.cursor/hooks.json` parse: `ok`.

## Files Changed

Implementation changes claimed for this bridge item:

- `.cursor/hooks.json`
- `.cursor/gtkb-hooks/workstream-focus.cmd`
- `scripts/cursor_hook_adapter.py`
- `platform_tests/scripts/test_cursor_hook_headless_parity.py`

The worktree contained many unrelated dirty files before this auto-dispatch. They are not claimed by this implementation report and were not intentionally modified for `WI-4925`.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: this is a defect-class reliability fix for Cursor hook launcher disposition, with a focused regression test.

## Scoped Diff Summary

```text
.cursor/hooks.json
- Replaced console-attached Python hook launchers with pythonw.exe.
- Routed Cursor .cmd hook invocations through .codex/gtkb-hooks/run_cmd_no_window.py.

.cursor/gtkb-hooks/workstream-focus.cmd
- Replaced the inner bare python launcher with pythonw.exe.

scripts/cursor_hook_adapter.py
- Added Windows CREATE_NO_WINDOW disposition for the inner hook subprocess.

platform_tests/scripts/test_cursor_hook_headless_parity.py
- Added regression tests for Python launcher choice, .cmd wrapper routing, workstream-focus.cmd, and adapter CREATE_NO_WINDOW use.
```

## Acceptance Criteria Status

- [x] `.cursor/hooks.json` uses `pythonw.exe` for all Python hook commands; no bare `python ` launcher remains.
- [x] All Cursor `.cmd` hook invocations route through `run_cmd_no_window.py`.
- [x] `.cursor/gtkb-hooks/workstream-focus.cmd` does not spawn a console-attached Python interpreter.
- [x] `cursor_hook_adapter.py` passes `CREATE_NO_WINDOW` for inner hook subprocesses on Windows.
- [x] `platform_tests/scripts/test_cursor_hook_headless_parity.py` passes and fails if regression reintroduces bare `python` hook commands.
- [ ] Manual spot-check: representative Cursor agent Write + Shell produces zero hook-origin console windows.

## Manual Verification Gap

The manual visual Cursor Write + Shell no-console spot-check was not performed. This run is a headless auto-dispatch worker and cannot honestly observe the user's Cursor GUI console-window behavior. The implementation therefore does not claim the final visual acceptance item. Loyal Opposition should treat this as a residual verification gap if manual observation is mandatory for `VERIFIED`.

## Risk And Rollback

Residual risk is limited to runtime behavior of Cursor hook process launch under Cursor's host environment. The source and configuration now use Windows no-window launchers, and automated checks lock that contract, but a GUI observation pass is still needed to prove end-to-end absence of hook-origin console windows.

Rollback is a scoped revert of:

- `.cursor/hooks.json`
- `.cursor/gtkb-hooks/workstream-focus.cmd`
- `scripts/cursor_hook_adapter.py`
- `platform_tests/scripts/test_cursor_hook_headless_parity.py`

Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed automated evidence.
2. If the manual visual spot-check is mandatory before closure, return `NO-GO` with that single remaining verification gap.
3. If automated launcher-disposition evidence is sufficient for this headless dispatch slice, return `VERIFIED`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
