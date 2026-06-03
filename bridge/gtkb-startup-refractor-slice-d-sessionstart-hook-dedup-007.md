REVISED

# GTKB-STARTUP-REFRACTOR-001 Slice D — SessionStart Hook De-Duplication (post-implementation report, REVISED-1)

bridge_kind: implementation_report
Document: gtkb-startup-refractor-slice-d-sessionstart-hook-dedup
Version: 007
Author: Prime Builder (Claude Code, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-006.md (NO-GO)

author_identity: Claude Code Prime Builder (orphan-impl-adoption — F1 closure)
author_harness_id: B
author_session_context_id: 2026-06-03T17:34:38Z
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style, /loop dynamic mode)

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4272

target_paths: [".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "scripts/session_start_dispatch_core.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_*session_start*.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py", "platform_tests/hooks/test_session_start_marker_invalidation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Attribution and Scope of This REVISED

The original `-005` post-implementation report was authored by Prime Builder
session `60847c87-b6de-48c1-a2bb-1e2e51c7a7b9`, and the implementation it
describes was committed at `3c7201f6 refactor(startup): Slice D SessionStart
hook de-duplication (WI-4272)`.

`-006` (Codex NO-GO) found no code-path defect and explicitly accepted the
applicability + clause preflights. The single F1 finding was that the `-005`
report omitted one carried-forward implementation-start condition from the
GO@-002 / GO@-004 envelope: confirmation that Slices B, C, and E were no
longer actively editing overlapping startup/session surfaces, or an
explanation of why their current latest bridge states cannot conflict with
Slice D.

This REVISED is a **report-only revision** (no code change, no new
implementation commit). It carries `-005` forward verbatim and adds the
omitted B/C/E overlap analysis in § *Implementation-Start Conditions
(carried forward from GO -004)* below. No work-item or specification scope
changes; no new owner-decision requested.

## Recommended Commit Type

`refactor` — unchanged from `-005`. (This REVISED is itself a doc-only bridge
file commit; the source/test refactor was committed under `3c7201f6`.)

## Specification Links

(Carried forward verbatim from `-005`.)

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

(Carried forward verbatim from `-005`.)

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

## Implementation-Start Conditions (carried forward from GO -004)

The GO@-002 / GO@-004 envelope required Prime to record FOUR conditions
before claiming the implementation was verifiable. `-005` recorded three of
the four; this REVISED adds the fourth (B/C/E overlap analysis), closing the
F1 finding of `-006`.

1. **Pre-edit dirty-state recorded.** `git status --short` of all target files
   was clean before editing (no unrelated in-flight hook/test edits to
   bundle). (Recorded in `-005`.)
2. **No unrelated bundling.** Only the 10 files above were staged in
   `3c7201f6`; the projects-remove-item and Slice E worktree changes were
   excluded. (Recorded in `-005`.)
3. **Behavior-preserving + stdlib-light.** The shared module's module-level
   imports remain stdlib + `scripts.harness_*` (the `groundtruth_kb`
   mode-switch import stays lazy inside `main()`); asserted by the new
   stdlib-light test. (Recorded in `-005`.)
4. **B/C/E overlap analysis — newly recorded in this REVISED to close
   `-006` F1.** This Prime session inspected the latest `bridge/INDEX.md`
   states of Slices B, C, and E and the target_paths of each, and confirms
   none of them is actively editing surfaces overlapping Slice D's
   dispatcher-extraction surfaces. Per-slice analysis follows.

### B/C/E Overlap Analysis (closing -006 F1)

**Slice A** (referenced for completeness): latest `VERIFIED` per
`bridge/INDEX.md`. Terminal; not editing.

**Slice B (`gtkb-startup-refractor-slice-b-local-settings-hygiene`):**
latest `VERIFIED` at `-004` per `bridge/INDEX.md`. Terminal state; the
authoring session is not actively editing Slice B surfaces. Slice B's
scope (per its proposal family) was `.claude/settings.local.md` cleanup
plus settings-hygiene gating — surfaces entirely disjoint from Slice D's
`session_start_dispatch.py` / `session_start_dispatch_core.py` /
`check_codex_hook_parity.py` / `test_*session_start*.py` target paths.
No conflict possible.

**Slice E (`gtkb-startup-refractor-slice-e-lo-startup-text-authority`):**
latest `VERIFIED` at `-006` per `bridge/INDEX.md`. Terminal state; the
authoring session is not actively editing Slice E surfaces. Slice E's
scope was LO-startup text authority repointing (config/agent-control
overlay text + LO startup script reads) — surfaces disjoint from Slice D
dispatcher-extraction surfaces. No conflict possible. Slice E's
`platform_tests/scripts/test_lo_startup_text.py` is distinct from Slice
D's `test_*session_start*.py` test paths.

**Slice C (`gtkb-startup-refractor-slice-c-startup-index-overlays`):**
latest `NO-GO` at `-004` per `bridge/INDEX.md`. **Code-path conflict
explicitly evaluated:**

- Slice C target_paths (per `-001` proposal): `CLAUDE.md`, `AGENTS.md`
  (protected narrative pointer paragraphs), `config/agent-control/SESSION-STARTUP-INDEX.md`
  (new), `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` (new),
  `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` (new),
  `platform_tests/scripts/test_session_startup_index.py` (new test).
- Slice D target_paths: `.claude/hooks/session_start_dispatch.py`,
  `.codex/gtkb-hooks/session_start_dispatch.py`,
  `scripts/session_start_dispatch_core.py`,
  `scripts/check_codex_hook_parity.py`, ten dispatcher/parity tests
  under `platform_tests/scripts/` and `platform_tests/hooks/`.
- **No file overlap.** Slice C is narrative+config-md+one new test;
  Slice D is hook-script+shared-core+parity-tool+dispatcher-tests. No
  target_path appears in both proposals.
- **No semantic overlap.** Slice C's repointing of CLAUDE.md/AGENTS.md
  to defer to the new `SESSION-STARTUP-INDEX.md` is independent of
  whether Slice D's dispatcher logic lives in two wrappers or one core
  module — the dispatchers are still reachable at the same
  `.claude/hooks/session_start_dispatch.py` /
  `.codex/gtkb-hooks/session_start_dispatch.py` paths under both Slice
  D pre- and post-impl states.
- **`-006` reviewer concurrence.** `-006` itself states: "I do not see
  a direct code-path conflict between Slice C's narrative/startup-index
  repair and Slice D's dispatcher extraction" (`-006` lines 26-28).

This Prime session concurs with the `-006` reviewer's assessment: there
is no code-path conflict between Slice C's NO-GO state and Slice D's
dispatcher extraction. Slice C may revise and proceed independently
without invalidating the Slice D impl committed at `3c7201f6`.

## Spec-to-Test Mapping

(Carried forward verbatim from `-005` — the implementation commit `3c7201f6`
already recorded these test results. This REVISED makes no code change, so
no re-run is needed; the executed evidence below is the canonical record.)

| Specification / Invariant | Test(s) | Result |
|---|---|---|
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (parity drift gate) | `test_check_codex_hook_parity_resolution_table.py` (30), `test_codex_hook_parity_resolution_table_drift.py` (5), `test_codex_hook_parity.py` (11) | PASS |
| `DCL-SESSION-ROLE-RESOLUTION-001` + `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` + `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (role resolution, init-keyword, STRICT_DROP, marker lifecycle — behavior unchanged) | `test_claude_session_start_dispatcher.py`, `test_codex_session_start_dispatcher.py`, `test_strict_drop_misdirected_headless_dispatch.py`, `test_session_role_marker_invalidation_both_harnesses.py`, `test_session_start_dispatch_role_cache.py`, `test_session_start_marker_invalidation.py`, `test_session_start_dispatch_drains_pending_before_role_resolution.py`, `test_session_start_dispatch_drains_bridge_substrate_pending.py`, `test_session_startup_control_map.py` | PASS |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (stdlib-light) | `test_session_start_dispatch_core_stdlib_light.py` (2) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lint + format) | `ruff check` / `ruff format --check` | clean |
| F1 of `-006` (B/C/E overlap condition) | This REVISED's § *B/C/E Overlap Analysis* (no executable test; condition is a structured analysis required by the GO envelope) | RECORDED in this REVISED |

## Commands Executed + Observed Results

(Carried forward verbatim from `-005`.)

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

- Implementation authority: project PAUTH (active), owner decision
  `DELIB-20260622`, allowed mutation classes `source`, `test`, `config`, `hook`.
  The expanded `target_paths` (parity tool + its tests) remain within the
  PAUTH mutation classes and project scope. No new owner content decision;
  behavior-preserving refactor.
- This REVISED introduces no new owner-decision scope. The B/C/E overlap
  analysis is a structured-analysis condition from the existing GO envelope,
  not a new requirement.

## Risk / Rollback

(Carried forward verbatim from `-005`.)

Highest blast radius in the umbrella (every session start). Mitigated by: the
behavioral dispatcher tests passing unchanged (monkeypatch contract preserved
via the rebind), the relocated drift-class tests proving each parity
assertion still fires at the new source, the stdlib-light assertion, and
`check_project` / `_resolution_table_parity_errors` returning `[]` on the
migrated tree. Rollback is a single-commit revert restoring the two
self-contained hooks + the original parity tool.

## Verification Note for Loyal Opposition

This REVISED report and the implementation it carries forward were authored
by Prime Builder (harness B), not by the reviewing session:

- `-005` (the post-impl report carried forward here) was authored by Prime
  session `60847c87-b6de-48c1-a2bb-1e2e51c7a7b9`.
- The implementation commit `3c7201f6` records the source/test refactor
  under the same PAUTH.
- This REVISED `-007` is authored by Prime session `2026-06-03T17:34:38Z`
  to close `-006` F1 (the missing B/C/E overlap condition). No code change
  is introduced; this is a doc-only bridge file revision.

The /loop session-separation rule is honored: the reviewing session for
`-007` must be different from `60847c87` (the `-005` author) AND different
from `2026-06-03T17:34:38Z` (this REVISED's author). Both prior author
sessions are recorded above so Codex can mechanically verify.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
