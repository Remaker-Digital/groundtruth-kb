NEW

bridge_kind: implementation_report
Document: gtkb-wi4530-gt-cli-path-install-shim
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f85ed01a-e9b0-4f44-9d72-4175a3d0b5b0
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch session (dispatch id 2026-06-14T15-12-05Z-prime-builder-B-8ddebf); Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC
Responds to: bridge/gtkb-wi4530-gt-cli-path-install-shim-002.md (Codex GO)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4530
target_paths: ["scripts/install_gt_path_shim.py", "platform_tests/scripts/test_install_gt_path_shim.py"]
implementation_scope: source, test
Recommended commit type: feat:

# WI-4530 Implementation Report — In-root `gt` PATH-shim content/path generator

## Summary

Implemented WI-4530 exactly as approved in the `-001` proposal and the Codex `GO`
at `-002`: a pure, in-root, deterministic generator that (1) resolves the venv
`gt` executable path from a `project_root` and (2) renders the launcher script's
text content (Windows `.cmd` / POSIX shell) forwarding all arguments to the venv
exe. The module performs **no I/O** — no file write, no PATH/env mutation, no
subprocess — in any public function; the `__main__` entrypoint only prints the
rendered content to stdout. The out-of-root user-PATH placement and the
install/bootstrap wiring remain deferred to a follow-on slice with its own
authorization (GO condition #4, confirmed below).

Two files were created (net-new, 320 LOC total):

- `scripts/install_gt_path_shim.py` (169 lines) — the generator module.
- `platform_tests/scripts/test_install_gt_path_shim.py` (151 lines) — 14 tests.

## Specification Links (carried forward from -001)

- **GOV-STANDING-BACKLOG-001** — WI-4530 backlog authority (P3 developer-environment improvement); single-WI scope (`CLAUSE-VISIBILITY-BULK-OPS` `not_applicable`).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implemented under active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4530; allows `source` + `test_addition`).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** + **`.claude/rules/project-root-boundary.md`** — both files are in-root under `E:\GT-KB`; the helper is path-pure and string-pure and places nothing out-of-root (asserted by `test_helper_does_no_io`).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — report filed through the live file bridge; no bridge workflow-state mutation beyond this thread's own version chain.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata concretely carried forward.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (mapping + execution evidence below).
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**, **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — the durable tracked generator codifies the 2026-06-13 manual workaround.

## Owner Decisions / Input

This implementation is authorized by durable owner-decision evidence; no new owner AskUserQuestion was required.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4530 under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (allowed: `source`, `test_addition`; forbids formal-artifact mutation without packet, deploy, force-push, credential lifecycle, broad bulk status mutation). This durable PAUTH row is the authority record (per the LO `-002` note that the cycle-13 AUQ is contextual, not sole approval evidence).
- **Cycle-13 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Seed both as scripts/ helpers", authorizing this scripts/-helper slice; install/PATH-setup follow-on slice declares its own authorization.

## GO Conditions Compliance (from -002 §Implementation Conditions)

1. **Slice kept pure** — no rendered-launcher file creation, no PATH mutation, no subprocess, no out-of-root placement, no KB mutation, no install/bootstrap wiring. Mechanically asserted by `test_helper_does_no_io` (AST inspection of the whole module: no `subprocess` import/use, no `open(...)`, no `Path.write_text`/`write_bytes`, no `os.environ` access). **PASS.**
2. **CLI/stdout entrypoint covered** — the `__main__` path is exercised by `test_main_emits_windows_content_to_stdout` (stdout == rendered content, rc 0) and `test_main_unsupported_platform_returns_2` (rc 2, stderr message, empty stdout), beyond the public-function tests. **PASS.**
3. **Report cites active PAUTH + verification output** — PAUTH row cited above; pytest / ruff check / ruff format output below. **PASS.**
4. **Follow-on install/PATH slice out of scope** — explicitly confirmed in §Follow-on Scope below. **PASS.**

## Implementation Detail

`scripts/install_gt_path_shim.py` public API (stdlib only, pure):

- `resolve_venv_gt_exe(project_root, platform) -> Path` — Windows → `<root>/groundtruth-kb/.venv/Scripts/gt.exe`; POSIX (`linux`/`darwin`) → `<root>/groundtruth-kb/.venv/bin/gt`; `ValueError` for unsupported platform.
- `render_windows_cmd_shim(venv_exe_path) -> str` — `@echo off`, WI-4530 doc header, `"<venv_exe>" %*` (double-quoted for spaces).
- `render_posix_shell_shim(venv_exe_path) -> str` — `#!/usr/bin/env bash` shebang, WI-4530 doc header, `exec "<venv_exe>" "$@"`.
- `render_for_platform(project_root, platform) -> dict[str, str]` — `{"filename", "content", "venv_exe"}` convenience wrapper.
- `main(argv=None) -> int` — argparse (`--platform` default `sys.platform`, `--project-root` default in-root checkout); prints content to stdout; rc 0 / rc 2 on unsupported platform.

**Host-flavour note (not a defect):** `pathlib` uses the host's path flavour, so a `--platform linux` render on a Windows host shows backslashes. This is correct path-pure behavior — the generator is intended to run on the host where the launcher will be placed (a POSIX host produces forward slashes). Tests build expected paths with the same `Path` joins, so assertions are host-agnostic.

## Spec-to-Test Mapping

| Acceptance criterion | Test | Result |
|---|---|---|
| Windows venv-exe path resolution (WI-4530 root) | `test_resolve_venv_gt_exe_windows` | PASS |
| POSIX venv-exe path resolution (linux + darwin) | `test_resolve_venv_gt_exe_posix` (parametrized) | PASS |
| Unsupported platform raises ValueError | `test_resolve_venv_gt_exe_unsupported_platform` | PASS |
| Windows .cmd forwards all args to quoted venv exe | `test_windows_cmd_shim_forwards_args` | PASS |
| POSIX shim has shebang, uses exec, forwards "$@" | `test_posix_shell_shim_uses_exec_and_quoted_args` | PASS |
| Path with spaces is quoted intact (both platforms) | `test_shim_quotes_path_with_spaces` (parametrized) | PASS |
| Wrapper returns filename + content + venv_exe | `test_render_for_platform_shape` | PASS |
| Wrapper rejects unsupported platform | `test_render_for_platform_unsupported_platform` | PASS |
| Helper does NO I/O (in-root constraint) | `test_helper_does_no_io` (AST) | PASS |
| `__main__` prints content / rc 0 (GO cond #2) | `test_main_emits_windows_content_to_stdout` | PASS |
| `__main__` rc 2 + stderr on unsupported (GO cond #2) | `test_main_unsupported_platform_returns_2` | PASS |

## Verification Evidence

Interpreter: `groundtruth-kb/.venv/Scripts/python.exe` (ruff- and pytest-capable; the root `.venv` has neither). Repo `pyproject.toml` addopts include `--timeout=30` (pytest-timeout absent in the venv), so pytest was run with `-o addopts=""` to clear it; this affects only the timeout plugin, not test execution.

```
# pytest
$ python -m pytest platform_tests/scripts/test_install_gt_path_shim.py -q -o addopts=""
14 passed, 1 warning in 0.31s

# ruff check (lint)
$ python -m ruff check scripts/install_gt_path_shim.py platform_tests/scripts/test_install_gt_path_shim.py
All checks passed!

# ruff format --check (formatting gate — separate from lint)
$ python -m ruff format --check scripts/install_gt_path_shim.py platform_tests/scripts/test_install_gt_path_shim.py
2 files already formatted
```

CLI smoke (real `__main__` invocation):

```
$ python scripts/install_gt_path_shim.py --platform win32 --project-root E:/GT-KB
@echo off
REM gt CLI launcher shim (WI-4530) -- generated by scripts/install_gt_path_shim.py
REM Forwards all arguments to the GT-KB venv console script.
"E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe" %*

$ python scripts/install_gt_path_shim.py --platform freebsd ; echo RC=$?
Unsupported platform 'freebsd'; supported platforms: darwin, linux, win32.
RC=2
```

## Follow-on Scope (GO condition #4)

The follow-on install / PATH-placement slice remains **out of scope** for this
implementation. This slice stops at pure content/path generation. Wiring the
generator into the install/bootstrap path, choosing the per-OS user-PATH
deployment target, performing the out-of-root placement, and communicating PATH
setup to the user are all deferred to that follow-on slice, which will declare
its own authorization and undergo its own project-root-boundary review for the
specific out-of-root placement decision.

## Recommended Commit Type

`feat:` — net-new capability (a deterministic launcher-shim content/path
generator + its 14-test suite); not a repair of existing broken behavior. The
diffstat is two net-new files (320 LOC), consistent with `feat:` per the
Conventional Commits discipline in `.claude/rules/file-bridge-protocol.md`.

## Risk / Rollback

- **Risk: very low.** Pure-Python content/path generator + unit tests; no file write, no PATH mutation, no subprocess, no install-process change. No caller wires the helper yet, so it cannot affect existing developer-environment behavior until the follow-on install slice lands.
- **Rollback:** delete the two new files. No migration, no schema, no install-process change, no PATH change, no KB mutation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
