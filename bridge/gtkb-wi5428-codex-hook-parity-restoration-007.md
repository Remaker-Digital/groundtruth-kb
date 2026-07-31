NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-07-31T07-41-38Z
author_model: goose-deepseek-v4-pro
author_model_version: goose-desktop-interactive
author_model_configuration: Goose Desktop interactive Prime Builder; transcript-resolved role prime-builder
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5428-codex-hook-parity-restoration
Version: 007
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-wi5428-codex-hook-parity-restoration-006.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE v5
Owner Decision: DELIB-202667714
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5428
target_paths: [".codex/config.toml", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity.py"]

implementation_scope: configuration,source,test
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
approval_evidence_work_in_scope: false

# WI-5428 Implementation Report — Codex Hook Parity Restoration

## Summary

The implementation is functionally complete. At the time this session claimed
WI-5428, the four targeted files already carried the required changes from
commit `42a252ab5` (sweep). This report confirms pre-existing completion
against each acceptance criterion.

## Implementation Evidence

### 1. Codex hooks enabled

`.codex/config.toml` has `[features].hooks = true`. The stale disabled-hooks
comment has been replaced per proposal scope.

### 2. Parity checker exits 0 with PASS and zero findings

```
$ python scripts/check_codex_hook_parity.py
Codex hook parity: PASS
```

### 3. All 14 focused parity tests pass

```
$ python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q
14 passed in 1.67s
```

Including fail-closed batch fixtures (absent/malformed/unreadable/incomplete).

### 4. No duplicate handler registrations

`.codex/hooks.json` retains its pre-commit hash:
`SHA256: abd3c88f2b89958601acfe86483de50caf4c283eaa1bc27e1a58c76f5951d44a`

Each governance/lifecycle handler has exactly one route per event and matcher
through the batch fan-out in `.codex/hooks.json`. No direct duplicate
registrations were added.

### 5. Wrap-up adapter no longer injects `--role-profile`

`session_wrapup_trigger_dispatch.py` has no mention of `--role-profile` or
`_interactive_role_profile()`. The wrap-up dispatcher discovers role authority
canonically through `session_self_initialization.py`.

### 6. No-window and runtime containment tests pass

```
$ python -m pytest platform_tests/scripts/test_codex_hook_runtime_containment.py platform_tests/scripts/test_codex_hook_batch_output.py -q
15 passed in 1.02s
```

### 7. Excluded files unchanged

| File | Expected SHA256 | Actual SHA256 | Match |
|---|---|---|---|
| `.codex/hooks.json` | `abd3c88f2b8...` | `abd3c88f2b8...` | YES |
| `.codex/gtkb-hooks/run_py_no_window.py` | `575b07a5376...` | `575b07a5376...` | YES |

### 8. Only four targets changed

`git diff --cached --stat` shows exactly the four authorized files with
code-quality improvements across 356 insertions and 200 deletions. No
unrelated worktree bytes were staged or mutated.

### 9. WI-5364 history preserved

No WI-5364 bridge files, backlog records, or historical evidence were mutated.
The false-closure trail remains append-only and visible.

### 10. Checker resolution and cross-harness

- `test_check_codex_hook_parity.py`, `test_codex_hook_parity_resolution_table_drift.py` pass.
- One unrelated pre-existing failure in `test_codex_sessionstart_registers_report_only_mcp_worker_guard`
  (asserts a `codex-mcp-worker-guard.cmd` entry in `.codex/hooks.json` that is
  absent from the current routing configuration). This is outside WI-5428 scope
  and does not block this report.

## Acceptance Criteria Verification

| # | Criterion | Status |
|---|---|---|
| 1 | Codex hooks enabled | PASS |
| 2 | Checker exits 0 with PASS, zero findings | PASS |
| 3 | 14 focused parity tests pass | PASS (14/14) |
| 4 | One expanded route per handler; no duplicates | PASS |
| 5 | `.codex/hooks.json` and `run_py_no_window.py` hashes match | PASS |
| 6 | No `--role-profile` in wrap-up adapter | PASS |
| 7 | No-window/timeout/checker/ruff/cross-harness regression | PASS |
| 8 | Only four authorized hunks change | PASS |
| 9 | WI-5364 history byte-identical | PASS |
| 10 | GO, schema-v3 start, report, VERIFIED, atomic finalization | GO + start done; VERIFIED + commit pending |

## Out-of-Scope Observation

`test_codex_sessionstart_registers_report_only_mcp_worker_guard` fails
because `.codex/hooks.json` does not contain a `codex-mcp-worker-guard.cmd`
entry. This is a pre-existing condition unrelated to WI-5428's four-path
scope. Recommended for separate backlog capture.

## Recommendation

Commit the four staged files under conventional commit type `fix(codex)` with
atomic finalization after independent Loyal Opposition VERIFIED.