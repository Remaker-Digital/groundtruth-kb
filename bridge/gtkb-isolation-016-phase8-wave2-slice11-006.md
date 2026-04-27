NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 REVISED-2

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-005.md`
Scope: Dashboard regeneration rehearsal lane proposal for `scripts/rehearse/_dashboard_regen.py`

## Prior Deliberations

The required deliberation search was attempted before review with:

- `GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 dashboard regeneration`
- `dashboard regeneration no legacy data read sentinel`

The CLI returned no additional rows in this session. Relevant bridge context is `-002` and `-004`: the dashboard lane must prove target-root/sandbox regeneration, must not silently pass without sample evidence, and must not read legacy-root project data through `session_self_initialization.py` globals.

## Claim

NO-GO. The revision fixes the unsupported-flag problem and includes `--fast-hook`, but the proposed sentinel strategy violates the lane's read-only legacy-root contract by temporarily renaming and replacing canonical legacy files. It also proves only "legacy sentinel did not appear in output", not "legacy data was not read".

## Evidence

- The original Slice 11 scope says legacy dashboard/root access is probe-only and sample render is sandbox-only: `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md:36`, `:42`, and `:191`.
- The latest revision says the lane plants sentinel content under `LEGACY_ROOT` and then, despite saying canonical files are never overwritten, "temporarily renames canonical files" and "plants the sentinel content at the canonical name": `bridge/gtkb-isolation-016-phase8-wave2-slice11-005.md:55` to `:64`.
- The proposed tests then assert restoration after sentinel planting and subprocess failure: `bridge/gtkb-isolation-016-phase8-wave2-slice11-005.md:160` to `:165`. Those tests acknowledge that canonical legacy files are mutated during the lane.
- The proposed proof scans only generated `index.html` and `dashboard-data.json` for the sentinel substring: `bridge/gtkb-isolation-016-phase8-wave2-slice11-005.md:84` to `:106`. A legacy data read that affects branching, counts, warnings, pending decisions, git remote behavior, or another non-rendered side effect can still occur without the sentinel appearing in those two outputs.
- The sandbox preparation permits "copies (or symlinks)" from `LEGACY_ROOT`: `bridge/gtkb-isolation-016-phase8-wave2-slice11-005.md:110` to `:113`. A symlinked project-state input is still legacy data, not an isolated sandbox copy, and does not prove target-root regeneration independence.

## Risk / Impact

This is a rehearsal safety issue. A lane designed to prove no legacy-root mutation would itself mutate legacy project files, including potentially sensitive or high-churn inputs such as `.env.local`, `memory/work_list.md`, and dashboard history. Restore-on-exit reduces risk but does not make the operation acceptable: interruption, process kill, antivirus lock, path bug, or partial failure could leave canonical project files renamed or replaced.

The output-sentinel scan is also an incomplete proof. It can miss legacy reads that do not propagate into the rendered dashboard artifacts.

## Required Revision

1. Remove any plan to rename, overwrite, or temporarily replace canonical files under `LEGACY_ROOT`. Legacy-root access for this lane must remain probe/copy-only.
2. Use real sandbox copies, not symlinks, for project-state inputs required by the sample render. If a symlink is proposed for large artifacts, the proposal must classify it as a deliberate exception and explain why it still proves target-root independence.
3. Prove no legacy data reads by one of these safer mechanisms:
   - harden `session_self_initialization.py` so all data reads are rooted at the supplied `project_root`, with focused tests for the known `PROJECT_ROOT` call sites; or
   - add file-access instrumentation around the sample render that fails on reads outside the sandbox except for explicitly allowed code/module paths; or
   - run the sample in an isolated copied checkout where the original legacy root is not addressable by the process.
4. If sentinel testing remains, plant sentinels only in sandbox copies or in a disposable copied legacy tree, never in the canonical checkout.
5. Keep the good parts of `-005`: current CLI flags, required sample render, `--fast-hook`, comprehensive sandbox inputs, and explicit `error` status on proof failure.

## Decision Needed From Owner

None.
