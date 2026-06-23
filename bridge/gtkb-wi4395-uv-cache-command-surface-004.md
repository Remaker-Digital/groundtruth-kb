NEW

bridge_kind: implementation_report
Document: gtkb-wi4395-uv-cache-command-surface
Version: 004
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 019eecf8-f9c0-7652-a2ab-d36df80757a8
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (resolved via ::init gtkb pb, harness B); explanatory output style; autonomous project-completion loop; model claude-opus-4-8[1m]
Date: 2026-06-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22
Project: PROJECT-GTKB-COMMAND-SURFACE
Work Item: WI-4395
target_paths: ["scripts/command_surface_env.py", "platform_tests/scripts/test_command_surface_env.py"]
implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4395 Implementation Report: canonical in-root uv command-surface env

Post-implementation report for the GO at `bridge/gtkb-wi4395-uv-cache-command-surface-003.md`. Implements the v002 (REVISED) proposal exactly as approved — no scope change.

## Summary of work performed

Added the canonical in-root command-surface environment helper and its regression suite. Implementation-start authorization packet `sha256:7f215cde755687246752649f31aa05e6b6042e02aac0b9f1e151004cc556ccf1` was created from the GO (`begin --bridge-id gtkb-wi4395-uv-cache-command-surface`) before any source write; all writes were confined to the two approved `target_paths`.

The helper pins `UV_CACHE_DIR` to `<root>/.gtkb-state/uv-cache` and `TMP`/`TEMP` to `<root>/.gtkb-state/uv-cache-tmp`. Both subdirectory names contain the `uv-cache` substring, which is one of the runtime-evidence GC `directory_name_tokens` in `config/governance/runtime-evidence-retention.toml` `[gtkb_state_gc]`, so the existing 14-day GC already covers them — no new cache convention is introduced (dedup vs HYG-054 / WI-4356). `resolve_command_surface_env` is path-pure; `ensure_command_surface_env` is the only filesystem-touching function (idempotent `mkdir`), returns a merged env, and never mutates the live process environment.

## Files Changed

- `scripts/command_surface_env.py` — NEW. Pure-Python/stdlib helper: `resolve_command_surface_env` (path-pure), `command_surface_dirs`, `gc_recognized_token`, `ensure_command_surface_env` (idempotent dir creation + merged env), and a self-documenting `main` CLI (`--project-root` / `--ensure` / `--format env|json`).
- `platform_tests/scripts/test_command_surface_env.py` — NEW. 13 tests covering the Verification Plan.

No other files were modified. No KB mutation, no config edit, no deletion of the pre-existing root-level `.uv-cache*` sprawl (explicitly out of scope per the proposal).

## Specification Links (carried forward from -002)

- **GOV-STANDING-BACKLOG-001** — WI-4395 backlog authority; single-WI scope (the `CLAUSE-VISIBILITY-BULK-OPS` clause is `not_applicable`: no bulk op).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implemented under active `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22` (`source` + `test_addition`); the begin packet validated PAUTH coverage of WI-4395.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** + `.claude/rules/project-root-boundary.md` — both files in-root; the canonical cache/temp paths resolve under the in-root, git-ignored `.gtkb-state/`. No out-of-root path is written, read as a dependency, or required.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge numbered chain.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — links carried forward concretely.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — spec-to-test mapping + executed evidence below.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory).

## Spec-to-Test Mapping (all executed; all PASS)

| Acceptance criterion (WI-4395 / DELIB-20263464) | Test | Result |
|---|---|---|
| `UV_CACHE_DIR` pinned to in-root `.gtkb-state/uv-cache` (not the uv default) | `test_resolve_pins_uv_cache_in_root` | PASS |
| `TMP`/`TEMP` pinned in-root | `test_resolve_pins_tmp_temp_in_root` | PASS |
| `TMP`/`TEMP` share one dir; canonical dir set | `test_tmp_temp_share_one_dir` | PASS |
| Every pinned dir name uses a GC-recognized token (dedup vs HYG-054) | `test_all_dirs_use_gc_recognized_tokens` | PASS |
| Drift guard: helper tokens equal the live retention config tokens | `test_gc_tokens_match_live_retention_config` | PASS |
| Resolver is path-pure (no I/O) | `test_resolve_is_path_pure_no_io` | PASS |
| `ensure` creates dirs idempotently | `test_ensure_creates_dirs_idempotent` | PASS |
| **Denied/broken default uv cache handled by an in-root writable location** (core) | `test_ensure_overrides_denied_default_cache` | PASS |
| `ensure` merges/preserves unrelated base_env keys | `test_ensure_merges_base_env` | PASS |
| `ensure` never mutates the live process env | `test_ensure_does_not_mutate_process_env` | PASS |
| Self-documenting CLI prints env, read-only by default | `test_main_prints_env` | PASS |
| CLI `--ensure` creates dirs | `test_main_ensure_creates_dirs` | PASS |
| CLI `--format json` emits the three pinned keys | `test_main_json_format` | PASS |

## Verification Evidence (exact commands + observed results)

Run with the canonical venv interpreter (`groundtruth-kb/.venv/Scripts/python.exe`), per the GO's spec-derived verification expectations:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_command_surface_env.py -q --tb=short
  => 13 passed, 1 warning in 0.88s
     (the single warning is the pre-existing repo-wide "Unknown config option: asyncio_mode"
      pytest warning, unrelated to this change)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/command_surface_env.py platform_tests/scripts/test_command_surface_env.py
  => All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/command_surface_env.py platform_tests/scripts/test_command_surface_env.py
  => 2 files already formatted
```

Implementation note (transparency): the first pytest run had one failure in `test_resolve_pins_uv_cache_in_root`. The failure was a **test-assertion defect, not a source defect**: the assertion used an environment-dependent substring proxy to assert the cache was not the user-profile default, and that proxy spuriously matched the location of pytest's own temporary directory. Per GOV-06 (fix the spec/test when the test is wrong, not the correct code), the assertion was replaced with a precise, location-independent relative-path check (`relative_to(root) == .gtkb-state/uv-cache`). The source helper was not changed. Re-run is the clean 13/13 above.

## Advisory Note Response (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001)

The GO's advisory note asked the report to cite or explain the applicability-preflight's missing advisory spec `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`. It is **not citable because the spec row is genuinely absent from MemBase** — the applicability registry references the ID, but no `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` artifact exists to link. It is advisory-only and does not gate. The artifact-oriented-governance intent it represents is satisfied here by the two cited present specs: **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** and **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** — this slice codifies a previously per-session-rediscovered workaround into a durable, tracked, tested artifact.

## Prior Deliberations (carried forward)

- `DELIB-20263464` — WI-4395 LO disposition (the command-surface-hardening recommendation this implements).
- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` — owner directive authorizing the work.
- `DELIB-20263239` — sibling WI-4530 command-surface determinism (style/scope separation).
- `DELIB-20260809` / `DELIB-20261251` — work-tree hygiene scoping (`.gtkb-state` is runtime evidence under retention/GC).

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no new AskUserQuestion required.

- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` — owner directive (session a460ee9e, 2026-06-22) to drive PROJECT-GTKB-COMMAND-SURFACE to VERIFIED/retired, recorded in `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22`.

## Recommended Commit Type

`feat:` — net-new capability (canonical command-surface env helper + regression suite). Matches the diff (two new files, no repair of existing in-repo code).

## Risk / Rollback

- **Risk: low.** Net-new pure helper + tests; no caller rewired, no PATH/env mutation, no deletion, no KB/config mutation. Existing developer-environment behavior is unchanged until a follow-on opts in.
- **Rollback:** delete the two new files.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
