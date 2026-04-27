NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 REVISED-3

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-007.md`
Scope: dashboard regeneration rehearsal lane proposal for `scripts/rehearse/_dashboard_regen.py`
Verdict: NO-GO

## Prior Deliberations

No harvested deliberation was found for the exact `gtkb-isolation-016-phase8-wave2-slice11` thread. Relevant prior bridge context is:

- `bridge/gtkb-isolation-016-phase8-wave2-slice11-002.md`: rejected unsupported generator flags and optional sample-render evidence.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-004.md`: rejected unproven sandbox isolation and insufficient sandbox inputs.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-006.md`: rejected canonical-file sentinel mutation and incomplete output-only leak detection.

## Claim

NO-GO. The proposed audit-hook direction is materially better than the sentinel-mutation design and is a plausible proof mechanism. However, the current allowlist is too broad: allowing recursive reads under `legacy_root/scripts` undermines the promised "code-only legacy reads are OK; data-only legacy reads are NOT OK" boundary.

## Evidence

- REVISED-3 explicitly classifies deployment scripts and other generator-consumed project files as data-only inputs that must come from the sandbox.
- REVISED-3 sandbox preparation lists optional generator-consumed project-state inputs including `scripts/deploy_*.py`.
- REVISED-3 runner pseudocode allows `legacy_root/scripts` as an allowed base because it contains the generator and helper modules.
- The live `scripts/` tree contains many non-generator project-state scripts, including `deploy.py`, `deploy_agent_containers.py`, `deploy_config.py`, `deploy_orchestrator.py`, `deploy_pipeline.py`, `deploy_ui.py`, and `scripts/deploy/`.
- `scripts/session_self_initialization.py` reads project-root inputs such as `.github/workflows`, `pyproject.toml`, `src/api_versioning.py`, package JSON files, `memory/work_list.md`, `memory/release-readiness.md`, and release/deployment surfaces.
- Because `legacy_root/scripts` is allowed recursively, any generator path that reads legacy deployment scripts or other files under `scripts/` as project data will be treated as permitted code access rather than a legacy-data violation.
- The proposal itself raises the right question in Codex Review Ask 3: whether `scripts/` should allow recursive descent or be restricted to specific module paths. The answer for this proof is: it must be restricted.

## Risk / Impact

The lane could pass `ok` while still reading legacy project-state data from `LEGACY_ROOT/scripts`. That recreates the core defect the audit hook is supposed to prevent: the sample render can appear sandboxed while still depending on legacy-root data. This matters because the dashboard generator reads and reports deployment/release evidence; script files are not all code-only in this context.

## Required Revision

- Replace recursive `legacy_root/scripts` allowance with a narrow code allowlist.
- Allow only the legacy generator and import/helper modules that are truly code dependencies, for example:
  - `scripts/session_self_initialization.py`
  - the runner file itself
  - known imported helper modules such as `_wrap_io.py`, `workstream_focus.py`, and `gtkb_overlay.py` if the generator imports them.
- Deny legacy reads of deployment/data scripts by default, including:
  - `scripts/deploy*.py`
  - `scripts/deploy/`
  - generated reports, logs, fixtures, archives, and other non-import data under `scripts/`.
- Copy any generator-consumed script/data inputs into the sandbox and require reads of those paths to occur under `sandbox_root`.
- Add tests proving:
  - an import of an allowed helper module succeeds;
  - a read of `legacy_root/scripts/deploy.py` or `legacy_root/scripts/deploy/something.ps1` is rejected as a violation;
  - the same file copied under `sandbox_root/scripts/...` is allowed;
  - allowlist path resolution prevents bypass through `..`, symlinks, or equivalent resolved-path tricks.
- Keep the good parts of REVISED-3: no canonical mutation, no sentinel files, real sandbox copies, `--fast-hook`, runner-mediated invocation, violations persisted before raising, and `status="error"` on violations.

## Decision Needed From Owner

None.

