NEW

# GTKB-STARTUP-REFRACTOR-001 Slice D — SessionStart Hook De-Duplication (post-implementation report)

bridge_kind: implementation_report
Document: gtkb-startup-refractor-slice-d-sessionstart-hook-dedup
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004.md (GO)

author_identity: Claude Code Prime Builder (PAUTH-authorized implementation)
author_harness_id: B
author_session_context_id: 60847c87-b6de-48c1-a2bb-1e2e51c7a7b9
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4272

target_paths: [".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "scripts/session_start_dispatch_core.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_*session_start*.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py", "platform_tests/hooks/test_session_start_marker_invalidation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Recommended Commit Type

`refactor` — extracts shared SessionStart dispatch logic into one module with
thin delegating wrappers and relocates the parity assertions to the single
source; no behavior change, no new capability.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — governs the SessionStart dispatch behavior preserved here. PAUTH-linked.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — de-duplication reduces the maintained startup surface; stdlib-light invariant.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Claude/Codex hook parity; the parity tool is the mechanical drift gate relocated here.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the resolution-table contract the parity tool enforces; behavior unchanged.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — init-keyword syntax the dispatchers parse; unchanged.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — init-keyword assertion; unchanged.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + WI + PAUTH linkage.
- `GOV-STANDING-BACKLOG-001` — WI-4272 linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all target paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Summary

Implemented the GO'd (`-004`) scope-corrected Slice D. The two SessionStart
dispatchers were character-identical across ~645 lines except module docstring,
`OUT_DIR`, `HARNESS_NAME`, and one comment. Changes:

1. **`scripts/session_start_dispatch_core.py` (new)** — the shared dispatch
   core: all primitives (the `StartupDecision` enum, the canonical init-keyword
   regex, the `_LABEL_TO_CANONICAL_MODE`/`_MODE_TO_ROLE_PROFILE` dicts, the
   marker constant, `main()`, and the dispatch/relay/audit/marker functions),
   seeded from the monolith. `HARNESS_NAME`/`OUT_DIR` are `None` placeholders
   (a wrapper that forgets to override fails fast rather than silently inheriting
   another harness's identity); the `__main__` block is removed (it is a library).
2. **`.claude/hooks/session_start_dispatch.py` / `.codex/gtkb-hooks/session_start_dispatch.py`**
   — thin wrappers: import the core, copy its namespace, set their own
   `HARNESS_NAME`/`OUT_DIR`, then **rebind** every shared function onto the
   wrapper's globals via `types.FunctionType(...)`. The rebind copies
   `__kwdefaults__`/`__annotations__`/`__qualname__`/`__doc__`/`__dict__` (not
   just `__defaults__`), so keyword-only-default functions
   (`_bridge_dispatch_keyword_check`, `_write_startup_relay_cache`,
   `_audit_log_misdirected_dispatch`) keep their defaults. The rebind makes the
   functions execute against wrapper globals, preserving the existing dispatcher
   tests' `monkeypatch.setattr(module, "OUT_DIR"/helper, ...)` contract.
3. **`scripts/check_codex_hook_parity.py`** — relocated the drift gate:
   `_resolution_table_parity_errors` now asserts the primitives in the **core**
   (single source), keeps the intentional-difference guard (Assertion 8) on the
   wrappers, replaces the now-moot "two dispatchers ast-equivalent" Assertion 4
   with a core dict **content** check against canonical mappings, and adds
   **Assertion 10** (each wrapper imports the core + rebinds). The `check_project`
   claude/codex dispatcher blocks and `_start_wrapper_errors` (which also read
   the wrapper source for behavioral tokens that moved to the core) were
   retargeted to verify wrapper delegation + check the core for the behavioral
   contract. All within `target_paths`.
4. **Tests** — `test_check_codex_hook_parity_resolution_table.py` and
   `test_codex_hook_parity_resolution_table_drift.py` rewritten to mutate the
   core for primitive drift classes (Assertion 8 still mutates wrappers; new
   delegation tests added); `test_codex_hook_parity.py`,
   `test_session_start_dispatch_drains_pending_before_role_resolution.py`, and
   `test_session_start_marker_invalidation.py` retargeted source-reads to the
   core; new `test_session_start_dispatch_core_stdlib_light.py` asserts the core
   has no heavy module-level imports.

Behavior-preserving: no change to SessionStart decision logic, role resolution,
init-keyword dispatch, disclosure-relay, strict-drop, or marker invalidation.

## Implementation-Start Conditions (from GO -004)

1. **Pre-edit dirty-state recorded.** `git status --short` of all target files
   was clean before editing (no unrelated in-flight hook/test edits to bundle).
2. **No unrelated bundling.** Only the 10 files above are staged; the
   projects-remove-item and Slice E worktree changes are excluded.
3. **Behavior-preserving + stdlib-light.** The shared module's module-level
   imports remain stdlib + `scripts.harness_*` (the `groundtruth_kb` mode-switch
   import stays lazy inside `main()`); asserted by the new stdlib-light test.

## Spec-to-Test Mapping

| Specification / Invariant | Test(s) | Result |
|---|---|---|
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (parity drift gate) | `test_check_codex_hook_parity_resolution_table.py` (30), `test_codex_hook_parity_resolution_table_drift.py` (5), `test_codex_hook_parity.py` (11) | PASS |
| `DCL-SESSION-ROLE-RESOLUTION-001` + `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` + `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (role resolution, init-keyword, STRICT_DROP, marker lifecycle — behavior unchanged) | `test_claude_session_start_dispatcher.py`, `test_codex_session_start_dispatcher.py`, `test_strict_drop_misdirected_headless_dispatch.py`, `test_session_role_marker_invalidation_both_harnesses.py`, `test_session_start_dispatch_role_cache.py`, `test_session_start_marker_invalidation.py`, `test_session_start_dispatch_drains_pending_before_role_resolution.py`, `test_session_start_dispatch_drains_bridge_substrate_pending.py`, `test_session_startup_control_map.py` | PASS |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (stdlib-light) | `test_session_start_dispatch_core_stdlib_light.py` (2) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lint + format) | `ruff check` / `ruff format --check` | clean |

## Commands Executed + Observed Results

```text
# Parity + structural subset
groundtruth-kb\.venv\Scripts\python.exe -m pytest \
  test_check_codex_hook_parity_resolution_table.py test_codex_hook_parity_resolution_table_drift.py \
  test_codex_hook_parity.py test_session_start_dispatch_drains_pending_before_role_resolution.py \
  test_session_start_dispatch_core_stdlib_light.py test_session_start_marker_invalidation.py \
  test_session_start_dispatch_role_cache.py -p no:cacheprovider
=> 75 passed

# Dispatcher behavioral suite
groundtruth-kb\.venv\Scripts\python.exe -m pytest \
  test_claude_session_start_dispatcher.py test_codex_session_start_dispatcher.py \
  test_strict_drop_misdirected_headless_dispatch.py test_session_role_marker_invalidation_both_harnesses.py \
  test_session_start_dispatch_drains_bridge_substrate_pending.py test_session_startup_control_map.py
=> 54 passed in 149.73s

# Code quality (both gates)
ruff check <10 changed files>           => All checks passed!
ruff format --check <10 changed files>  => 10 files already formatted
```

`_resolution_table_parity_errors(REPO_ROOT)` and `check_project(REPO_ROOT)` both
return `[]` on the migrated tree.

## Owner Decisions / Input

- Implementation authority: project PAUTH (active), owner decision `DELIB-20260622`,
  allowed mutation classes `source`, `test`, `config`, `hook`. The expanded
  `target_paths` (parity tool + its tests) remain within the PAUTH mutation
  classes and project scope. No new owner content decision; behavior-preserving
  refactor.

## Risk / Rollback

Highest blast radius in the umbrella (every session start). Mitigated by: the
behavioral dispatcher tests passing unchanged (monkeypatch contract preserved via
the rebind), the relocated drift-class tests proving each parity assertion still
fires at the new source, the stdlib-light assertion, and `check_project`/
`_resolution_table_parity_errors` returning `[]` on the migrated tree. Rollback is
a single-commit revert restoring the two self-contained hooks + the original
parity tool.

## Verification Note for Loyal Opposition

This report and its proposal (`-003`) were authored by Prime Builder (harness B),
not by the reviewing session. The implementation extended the parity-tool work
beyond `_resolution_table_parity_errors` to also retarget `_start_wrapper_errors`
and the `check_project` dispatcher blocks (both read wrapper source for behavioral
tokens that moved to the core); both are within the GO'd `scripts/check_codex_hook_parity.py`
target path.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
