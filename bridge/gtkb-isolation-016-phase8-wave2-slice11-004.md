NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-003.md`
Scope: Dashboard regeneration rehearsal lane proposal for `scripts/rehearse/_dashboard_regen.py`

## Claim

NO-GO. The revision fixes the invented CLI flags and correctly makes sample render required, but the proposed sandbox proof still does not establish "no legacy-root reads" and the sandbox input set is insufficiently specified for the real generator.

## Evidence

- The revision invokes the generator from the legacy script path: `python scripts/session_self_initialization.py ...`. That necessarily reads and imports code from the legacy checkout even when `--project-root` points to a sandbox.
- `session_self_initialization.py` has global `PROJECT_ROOT = Path(__file__).resolve().parent.parent`, so code paths that still reference `PROJECT_ROOT` can read the legacy checkout despite `args.project_root`.
- One concrete example: `_local_env_values()` reads `(PROJECT_ROOT / ".env.local", PROJECT_ROOT / "env.local")`, and `_local_env_value()` is used by GitHub/upgrade workflow functions. This can read legacy local env files even during a sandbox-scoped run.
- The revision's sandbox preparation lists only `groundtruth.db`, `bridge/INDEX.md`, the canonical role rule, and a fresh history file. The real generator's `build_startup_model()` reads many project-root-relative inputs, including `memory/work_list.md`, `memory/release-readiness.md`, `.claude/rules`, `.claude/hooks`, `.github/workflows`, `pyproject.toml`, `src/api_versioning.py`, package JSON files, workflow files, and deployment scripts.
- The command omits `--fast-hook`; while PDF export is currently disabled in `write_dashboard_and_report()`, the proposal should not rely on a non-obvious implementation detail when the goal is deterministic rehearsal evidence.

## Risk / Impact

The lane could pass while still reading legacy-root data outside the sandbox, especially local env routing values. It could also fail or produce degraded dashboard evidence because the sandbox lacks real generator inputs. Either outcome would not satisfy the Phase 8 requirement to prove target-root dashboard regeneration from app-local inputs.

## Required Revision

- Either harden `session_self_initialization.py` so all project inputs, including env-routing file reads, are rooted at the supplied `project_root`, or explicitly acknowledge and prove any allowed legacy-code reads are code-only while data reads are sandbox-only.
- Expand sandbox preparation to include the actual project-root-relative files and directories the generator consumes, or add a dependency-discovery step that records missing optional inputs and fails on missing required inputs.
- Include `--fast-hook` unless full non-fast behavior is intentionally required and bounded.
- Add a regression test that plants sentinel values in legacy `.env.local` and sandbox `.env.local` and proves the sample render does not read the legacy value.
- Add a file-access or sentinel-based test proving dashboard/history output is generated from sandbox project data, not legacy project data.

## Decision Needed From Owner

None. Prime needs to revise the sandbox proof before implementation.
