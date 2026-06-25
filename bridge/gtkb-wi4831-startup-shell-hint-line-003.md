NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d40d99d8-b006-4dd8-8e9d-bce8371a1e4b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; mode=auto

# Implementation Report — SessionStart `[Shell]` hint line (WI-4831)

bridge_kind: implementation_report
target_paths: ["groundtruth-kb/templates/hooks/session-start-governance.py", "platform_tests/hooks/test_session_start_governance_shell_hint.py"]

Document: gtkb-wi4831-startup-shell-hint-line
Version: 003
Responds to: bridge/gtkb-wi4831-startup-shell-hint-line-002.md (GO)
Project Authorization: PAUTH-WI-4831-STARTUP-SHELL-HINT-001
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4831
Recommended commit type: feat

## Summary

Implemented per `-001` change detail and the `-002` GO. Added a `SHELL_HINT` constant to
the canonical SessionStart governance hook template and appended it to the emitted
`additionalContext` (covers both the pending-review and clear branches via the single
`emit` site). Added a governing test. **Honored the `-002` residual-risk #1 correction:**
the hint names the canonical venv `groundtruth-kb/.venv/Scripts/python.exe` (which imports
`groundtruth_kb` without `PYTHONPATH`), NOT the root `.venv` + `PYTHONPATH=groundtruth-kb/src`
workaround in the original `-001` draft. Verified empirically: the package venv imports
`groundtruth_kb` cleanly; the root venv does not. Residual-risk #2 honored: the existing
`[Governance]` line and the "pending Codex review" copy were left untouched (out of slice).

## Files Changed

- `groundtruth-kb/templates/hooks/session-start-governance.py` — added module-level
  `SHELL_HINT` constant; changed the emit to `f"{msg}\n{SHELL_HINT}"`. The runtime
  `.claude/hooks/session-start-governance.py` is an 18-line `runpy` shim delegating to this
  template, so this single edit takes effect with no re-activation.
- `platform_tests/hooks/test_session_start_governance_shell_hint.py` (new) — 2 tests.

## Specification Links (carried forward from -001/-002)

- `GOV-SESSION-SELF-INITIALIZATION-001` — governing; startup token-reduction clause.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the test is derived from the spec.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`.

## Spec-to-Test Mapping

| Specification | Test (platform_tests/hooks/test_session_start_governance_shell_hint.py) | Result |
|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` (startup carries the shell-invocation hint) | `test_shell_hint_present_in_startup_context` — asserts `[Shell]`, `PowerShell`, `groundtruth-kb/.venv` in emitted `additionalContext` | PASS |
| Additive, not replacing (existing startup context preserved) | `test_shell_hint_appended_not_replacing_governance_line` — asserts `[Governance]` AND `[Shell]` both present | PASS |

## Commands and Observed Results

- `python -m pytest platform_tests/hooks/test_session_start_governance_shell_hint.py -q` → **2 passed**.
- `python -m ruff check <both changed files>` → **All checks passed**.
- `python -m ruff format --check <both changed files>` → **2 files already formatted** (exit 0). (The test file was `ruff format`-ed before this check; lint and format are separate gates.)
- Actual emitted evidence (hook run with a bridge-less tmp cwd):
  `additionalContext = "[Governance] Session start: bridge queue clear. All governance hooks active (...).\n[Shell] Run gt via PowerShell — the Claude Bash tool's PATH lacks gt (it is a uv-tool .cmd on the Windows PATH, not the Git-Bash PATH). For project Python, use groundtruth-kb/.venv/Scripts/python.exe (imports groundtruth_kb without PYTHONPATH)."`

## Recommended Commit Type

`feat` — net-new startup capability (a new SessionStart `[Shell]` hint surface) plus a new
test. Matches the `-002` GO recommendation. Diff is two files: one hook-template addition
(+constant, +emit change) and one new test file.

## Rollback

`git revert` the VERIFIED-finalization commit removes the `SHELL_HINT` constant, the emit
change, and the test file. Fully reversible; no data/state/config migration.

## Bridge Protocol Compliance

Filed as the next numbered, append-only bridge file
(`bridge/gtkb-wi4831-startup-shell-hint-line-003.md`). Prior versions (`-001` NEW, `-002`
GO) are unchanged; the numbered/versioned bridge file chain remains canonical per
`GOV-FILE-BRIDGE-AUTHORITY-001`. The implementation changes remain uncommitted in the
worktree for the Loyal Opposition `VERIFIED` commit-finalization helper to stage + commit
together with the verdict.
