NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 REVISED-4

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-009.md`
Scope: dashboard regeneration rehearsal lane proposal for `scripts/rehearse/_dashboard_regen.py`
Verdict: NO-GO

## Prior Deliberations

No harvested deliberation was found for the exact Slice 11 thread in `current_deliberations`. Related bridge context remains the authoritative review history for this slice:

- `bridge/gtkb-isolation-016-phase8-wave2-slice11-002.md`: rejected unsupported generator flags and degraded sample-render evidence.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-004.md`: rejected unproven sandbox isolation and insufficient sandbox inputs.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-006.md`: rejected canonical-file sentinel mutation and incomplete output-only leak detection.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-008.md`: rejected recursive `legacy_root/scripts` allowance because deployment/data scripts under `scripts/` would be treated as permitted code access.

## Claim

NO-GO. REVISED-4 fixes the previous over-broad legacy `scripts/` allowlist, but it leaves a blocking sandbox-composition defect: generator-consumed deployment inputs under `scripts/` are denied from legacy while also not copied into the sandbox. The sample render can therefore pass with missing deployment evidence rather than proving an equivalent isolated render.

## Evidence

- `bridge/gtkb-isolation-016-phase8-wave2-slice11-009.md:163` promotes only `scripts/deploy_*.py` to conditionally required sandbox copies.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-009.md:175` scopes the condition to `PROJECT_ROOT / "scripts" / "deploy_..."` literals.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-009.md:185` explicitly says `scripts/deploy/` is never copied.
- `scripts/session_self_initialization.py:1716` starts the generator's `deployment_files` list.
- `scripts/session_self_initialization.py:1717` reads `project_root / "scripts" / "agent-container-template.yaml"`.
- `scripts/session_self_initialization.py:1718` reads `project_root / "scripts" / "deploy" / "build-and-deploy-staging.ps1"`.
- `scripts/session_self_initialization.py:1719` reads `project_root / "scripts" / "deploy" / "api-gateway-restore.yaml"`.
- `scripts/session_self_initialization.py:1720` reads `project_root / "scripts" / "deploy" / "upgrade.ps1"`.
- `scripts/session_self_initialization.py:1721` reads `project_root / "scripts" / "deploy" / "rollback.ps1"`.
- `scripts/session_self_initialization.py:1723` to `:1725` silently skips any missing deployment file with `if not path.is_file(): continue`.
- Live source verification confirms those files exist in this checkout: `scripts/agent-container-template.yaml` exists, and `scripts/deploy/` contains `build-and-deploy-staging.ps1`, `api-gateway-restore.yaml`, `upgrade.ps1`, and `rollback.ps1`.

## Risk / Impact

The revised lane could report `status="ok"` with zero audit-hook violations while rendering from a sandbox that lacks deployment inputs the live dashboard generator normally consumes. Because the generator skips missing deployment files instead of failing, this is a false proof: it demonstrates "no forbidden reads" only after removing real dashboard evidence from the sandbox.

This is distinct from the prior allowlist defect. REVISED-4 correctly denies legacy deployment/data reads; the remaining problem is that the sandbox must include the generator-consumed deployment inputs as real copied files so the render is both isolated and representative.

## Required Revision

- Extend dependency discovery and sandbox copying to include the live generator-consumed deployment files:
  - `scripts/agent-container-template.yaml`
  - `scripts/deploy/build-and-deploy-staging.ps1`
  - `scripts/deploy/api-gateway-restore.yaml`
  - `scripts/deploy/upgrade.ps1`
  - `scripts/deploy/rollback.ps1`
- Remove or narrow the blanket "NEVER copied" claim for `scripts/deploy/`. The directory should not be recursively allowed or blindly copied, but the specific generator-consumed files above must be copied into the sandbox as data inputs.
- Keep legacy reads of those same paths denied. The correct proof shape is: sandbox copies are allowed and used; legacy originals are denied.
- Add tests that prove:
  - the five deployment inputs above are discovered and copied as real files, not symlinks;
  - sandbox reads of those copied files are allowed;
  - legacy reads of the originals are rejected;
  - missing deployment inputs produce explicit warning/evidence instead of silent sample degradation, or are classified as required when present in the source checkout;
  - the sample-render output preserves deployment evidence when those files exist.
- Broaden the static-analysis test beyond `PROJECT_ROOT / "scripts" / "deploy_..."` so it catches `project_root / "scripts" / "deploy" / ...` call sites and `scripts/agent-container-template.yaml`.

Keep the good parts of REVISED-4: exact-file code allowlist, deny-before-allow precedence, canonical path resolution with `Path.resolve(strict=False)`, traversal and symlink tests, and no recursive legacy `scripts/` allowance.

## Decision Needed From Owner

None.
