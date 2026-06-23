NEW

bridge_kind: prime_proposal
Document: gtkb-wi4395-uv-cache-command-surface
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a460ee9e-4606-4e64-bd03-cd7eae14bdef
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (resolved via ::init gtkb pb, harness B); explanatory output style; autonomous project-completion loop; model claude-opus-4-8[1m]
Date: 2026-06-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22
Project: PROJECT-GTKB-COMMAND-SURFACE
Work Item: WI-4395
target_paths: ["scripts/command_surface_env.py", "platform_tests/scripts/test_command_surface_env.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4395: Canonical in-root uv command-surface env (UV_CACHE_DIR/TMP/TEMP pin + denied-default-cache regression)

## Summary

WI-4395 (P1, `command-surface`, origin=defect): last-24h Codex transcripts repeatedly showed `uv` failing before GT-KB commands could run — `Failed to initialize cache at C:\Users\micha\AppData\Local\uv\cache; Cannot create a file when that file already exists`. The default user-profile uv cache lives outside the repo, is subject to host/ACL/Drive-sync races, and is denied to the harness for direct inspection.

Per the Loyal Opposition disposition (`DELIB-20263464`, 2026-06-13), the original *outage* is no longer reproducible on the current host, but the work item must NOT be silently closed as "fixed." The durable gap is that **GT-KB still lacks a canonical, tracked command surface that pins `UV_CACHE_DIR`, temp paths, and optional tool dependencies** for automation and verification commands. Without one, agents keep re-deriving the workaround per session (the live repo already shows ad-hoc root-level `.uv-cache/`, `.uv-cache-automation/`, and `.tmp/uv-cache-codex/` cache trees — exactly the HYG-054 sprawl).

This slice delivers that canonical surface as a small, pure, fully-tested helper module plus a regression that simulates a denied/broken default uv cache. It deliberately **reuses the existing `uv-cache` runtime-evidence GC token** so the fix introduces no new cache naming convention (dedup against HYG-054 / WI-4356).

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4395 is the backlog authority for this fix (P1 `command-surface` defect). Single-WI scope (one new helper module + one platform test, no bulk operation); the `CLAUSE-VISIBILITY-BULK-OPS` clause is triggered by the citation but is `not_applicable` here (no inventory artifact, no bulk status mutation).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22` (active; includes WI-4395; allows `source` + `test_addition`; forbids formal-artifact mutation without packet, deploy, force-push, credential lifecycle, broad bulk status mutation).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** + **`.claude/rules/project-root-boundary.md`** — both `target_paths` are in-root under `E:\GT-KB`. The canonical cache/temp surface resolves under `<project_root>/.gtkb-state/` (in-root runtime-evidence location, git-ignored). No out-of-root path is written, read as a dependency, or required. This is the in-root analogue of the DB-snapshot exception's reasoning, but it stays *inside* the root rather than using `%LOCALAPPDATA%`, because uv caches are regenerable runtime evidence already covered by the in-root GC policy.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge (always-applicable bridge-governance trigger). Adds no aggregate-queue artifact and mutates no bridge workflow state beyond this thread.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked above.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the Verification Plan below maps each acceptance criterion (in-root pin, GC-token reuse, path-purity, denied-default-cache handling, idempotent ensure, CLI smoke) to an executed test.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — the helper is the durable, tracked artifact that codifies a previously per-session-rediscovered workaround into a deterministic, testable command surface.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4395 acceptance summary), the LO disposition (`DELIB-20263464`) scoped the durable gap and recommended exactly this "command-surface hardening" shape, the bounded PAUTH authorizes the `source` + `test_addition` work, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / the project-root-boundary rule defines the in-root constraint this slice respects. No new or revised formal specification is required.

## Prior Deliberations

A live semantic deliberation search was run during authoring (`deliberations search "uv cache directory ACL UV_CACHE_DIR command surface harness writable"`, limit 8).

- **`DELIB-20263464` — WI-4395 uv cache command-surface disposition (LO advisory, 2026-06-13).** The authoritative disposition for this work item: the original cache outage is stale, but reproducibility is still under-specified; Prime should "convert WI-4395 from 'repair current uv outage' to a small command-surface hardening bridge" defining one supported wrapper/prelude that sets `UV_CACHE_DIR`/`TMP`/`TEMP` under an approved in-root runtime-evidence location, plus regression coverage simulating a bad default uv cache, deduped against HYG-054 / WI-4356. This proposal implements that recommendation directly.
- **`DELIB-20263239` — WI-4530 gt CLI PATH shim generator (GO, 2026-06-14).** Sibling command-surface-determinism work (the `gt` launcher generator). Distinct concern: WI-4530/WI-4466 is "which `gt` do I invoke"; WI-4395 is "where does `uv` cache when GT-KB commands run." Cited to disambiguate and to keep the two command-surface helpers stylistically aligned (pure module + focused platform test; defer risky wiring).
- **`DELIB-20260809` / `DELIB-20261251` — Work-Tree Hygiene Mechanism Scoping (GO).** Establish that `.gtkb-state/` scratch/cache directories are runtime evidence governed by retention/GC, not canonical state. This proposal's choice of `.gtkb-state/` for the canonical cache + temp surface is consistent with that scoping.
- **`DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` — owner directive (2026-06-22).** Owner directed Prime Builder to complete WI-4395 + WI-4466 and retire PROJECT-GTKB-COMMAND-SURFACE; authorizes this slice.

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622`** — owner directive (interactive session a460ee9e, 2026-06-22): "drive PROJECT-GTKB-COMMAND-SURFACE to VERIFIED (retired) … choose the highest-value PB-actionable work item and complete it … continue until all work items are VERIFIED." This authorizes the bounded `source` + `test_addition` work recorded in `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22`.

The single owner decision deferred to retirement time (disposition of the stale CS-2+ roadmap — drop vs. preserve as fresh backlog) will be surfaced via AskUserQuestion before the project is retired, not in this slice.

## Design

New module `scripts/command_surface_env.py` — pure-Python, stdlib only. It defines the **one** canonical in-root command-surface environment so callers (automation, documented verification preludes) stop re-deriving per-session cache/temp paths.

Public API:

1. **`resolve_command_surface_env(project_root) -> dict[str, str]`** — *path-pure* (no filesystem touch). Returns:
   - `UV_CACHE_DIR` -> `<project_root>/.gtkb-state/uv-cache`
   - `TMP` -> `<project_root>/.gtkb-state/uv-cache-tmp`
   - `TEMP` -> `<project_root>/.gtkb-state/uv-cache-tmp`
   Both subdirectory names contain the substring `uv-cache`, which is one of the runtime-evidence GC `directory_name_tokens` in `config/governance/runtime-evidence-retention.toml` `[gtkb_state_gc]`. That is the deliberate dedup mechanism: the existing 14-day GC + `cross_harness_bridge_trigger._gc_stale_state_dirs` (`scripts/cross_harness_bridge_trigger.py:1365`) already cover these paths, so no new cache convention or retention edit is introduced.
2. **`command_surface_dirs(project_root) -> tuple[Path, ...]`** — the concrete directory set the env points at (for `ensure` + tests).
3. **`ensure_command_surface_env(project_root, base_env=None) -> dict[str, str]`** — the only function that touches the filesystem: idempotently `mkdir(parents=True, exist_ok=True)` each command-surface dir, then return `{**(base_env or os.environ), **resolve_command_surface_env(project_root)}`. The pinned keys always override whatever the inherited/`base_env` cache/temp values were — including a denied or broken default `UV_CACHE_DIR`. Callers merge the result into `subprocess` env; the helper never mutates the live process environment.
4. **`gc_recognized_token(name) -> str | None`** — returns the GC token a directory name matches (substring), or `None`. Used by the dedup self-check and test.
5. **`main(argv=None) -> int`** — self-documenting CLI: prints the resolved env as `KEY=VALUE` lines (default) or JSON (`--format json`); `--project-root` (default: the in-root checkout) and `--ensure` (create the dirs) flags. Mirrors `scripts/install_gt_path_shim.py`'s stdout-only manual-use entrypoint.

The module's `GC_RECOGNIZED_TOKENS` constant mirrors the retention-config token list; a test cross-checks it against the live config so the two cannot silently drift.

**Explicitly out of scope for this slice** (kept minimal and reversible):
- Cleanup/deletion of the pre-existing root-level `.uv-cache*` / `.tmp/uv-cache-codex` sprawl — that is WI-4356's stray-detector / a separate hygiene cleanup, and deletion is a destructive op held out of this additive slice. This helper *prevents new* sprawl by giving a canonical home; it does not remove old sprawl.
- Wiring every existing automation caller to the helper — this slice defines and proves the canonical surface (matching the LO disposition's "define one supported wrapper or documented command prelude"); migrating callers (e.g., the cross-harness trigger's spawn env) is a follow-on with its own blast-radius review.
- Editing `config/governance/runtime-evidence-retention.toml` — deliberately avoided by reusing the existing `uv-cache` token, keeping the slice at `source` + `test_addition` scope.

## Verification Plan (Specification-Derived)

| Acceptance criterion (WI-4395 / DELIB-20263464) | Test (in `platform_tests/scripts/test_command_surface_env.py`) | Method |
|---|---|---|
| `UV_CACHE_DIR` is pinned to an in-root, harness-writable location (not the user-profile default) | `test_resolve_pins_uv_cache_in_root` | `resolve_command_surface_env(root)["UV_CACHE_DIR"] == root/.gtkb-state/uv-cache`; is under `root`; does not contain `AppData` / `.local/uv` default segment |
| `TMP`/`TEMP` pinned in-root | `test_resolve_pins_tmp_temp_in_root` | both equal `root/.gtkb-state/uv-cache-tmp` and are under `root` |
| Fix reuses the existing GC convention (dedup vs HYG-054; no new cache name) | `test_all_dirs_use_gc_recognized_tokens` | every resolved dir name matches a `GC_RECOGNIZED_TOKENS` entry **and** that token set equals the live `[gtkb_state_gc].directory_name_tokens` ∩ used tokens parsed from `config/governance/runtime-evidence-retention.toml` (drift guard) |
| Resolver is path-pure (no I/O) | `test_resolve_is_path_pure_no_io` | call `resolve_command_surface_env` against a fresh tmp root; assert no directory was created; source-inspect that `resolve_*` performs no `mkdir`/`open(...,'w')`/`os.environ` mutation |
| A denied/broken default uv cache is handled by a harness-writable cache location (core acceptance) | `test_ensure_overrides_denied_default_cache` | build `base_env` with `UV_CACHE_DIR` = a denied/bogus path (a path *under a regular file*, i.e. un-creatable); call `ensure_command_surface_env(root, base_env=base_env)`; assert returned `UV_CACHE_DIR == root/.gtkb-state/uv-cache`, the dir exists, and a sentinel file writes+reads successfully |
| `ensure` is idempotent and creates writable dirs | `test_ensure_creates_dirs_idempotent` | two successive `ensure` calls succeed; all `command_surface_dirs` exist and are writable |
| `ensure` preserves unrelated base_env keys | `test_ensure_merges_base_env` | a sentinel `base_env` key survives; only the pinned keys are overridden |
| Self-documenting CLI works | `test_main_prints_env` and `test_main_ensure_creates_dirs` | `main([...])` prints `UV_CACHE_DIR=` line, returns 0; `--ensure` creates the dirs |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_command_surface_env.py -q --tb=short`.

## Risk / Rollback

- **Risk: low.** Net-new pure helper + its tests. `resolve_*` is path-pure; `ensure_*` only `mkdir`s under the git-ignored in-root `.gtkb-state/` and returns a dict — it never mutates the live process env and never deletes anything. No existing caller is rewired in this slice, so existing developer-environment behavior is unchanged until a follow-on opts in.
- **Drift guard:** the GC-token cross-check test fails if `runtime-evidence-retention.toml` later drops the `uv-cache` token, surfacing the coupling instead of letting the canonical cache silently fall out of GC coverage.
- **Rollback:** delete the two new files. No migration, no schema, no config edit, no PATH change, no KB mutation.

## Recommended Commit Type

`feat:` — net-new capability (a canonical command-surface env helper + its regression suite), not a repair of existing in-repo code. Per the Conventional Commits discipline in `.claude/rules/file-bridge-protocol.md`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
