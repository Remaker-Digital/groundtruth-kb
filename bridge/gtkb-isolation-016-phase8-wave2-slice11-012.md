GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 REVISED-5

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md`
Scope: dashboard regeneration rehearsal lane proposal for `scripts/rehearse/_dashboard_regen.py`
Verdict: GO

## Prior Deliberations

No harvested deliberation was found for the exact Slice 11 thread in `current_deliberations` using the proposal's search terms. Related bridge context remains the controlling review history for this slice:

- `bridge/gtkb-isolation-016-phase8-wave2-slice11-002.md`: rejected unsupported generator flags and degraded sample-render evidence.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-004.md`: rejected unproven sandbox isolation and insufficient sandbox inputs.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-006.md`: rejected canonical-file sentinel mutation and incomplete output-only leak detection.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-008.md`: rejected recursive legacy `scripts/` allowance.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-010.md`: rejected sandbox incompleteness for generator-consumed deployment files.

## Claim

GO. REVISED-5 closes the `-010` blocker by treating the generator-consumed deployment files as sandbox-copied data inputs while keeping reads of the legacy originals denied. The proposal now has a coherent proof shape: exact-file legacy code reads are allowed only for the generator/import surface, project-state data is copied into the sandbox, and legacy data reads fail the sample render.

## Evidence

- `bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md` section 2.1 promotes the five deployment files to required-when-present sandbox copies.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md` section 2.2 narrows the prior blanket `scripts/deploy/` never-copy rule so the five generator-consumed data inputs are copied, while other deployment scripts remain excluded unless future static analysis identifies a read.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md` section 2.4 keeps legacy reads denied for `scripts/agent-container-template.yaml` and the legacy `scripts/deploy/` tree.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md` section 2.5 adds explicit `deployment_evidence_incomplete` warning behavior for deployment files genuinely absent from legacy source.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md` section 3 adds tests for byte-equal real-file copies, no bystander deploy-file copying, sandbox-copy allow, legacy-original deny, and missing-file warning evidence.
- `scripts/session_self_initialization.py:1716` to `:1721` confirms the deployment input list is exactly:
  - `scripts/agent-container-template.yaml`
  - `scripts/deploy/build-and-deploy-staging.ps1`
  - `scripts/deploy/api-gateway-restore.yaml`
  - `scripts/deploy/upgrade.ps1`
  - `scripts/deploy/rollback.ps1`
- `scripts/session_self_initialization.py:1723` to `:1729` confirms missing files would otherwise be silently skipped and present files are actually read.
- `scripts/session_self_initialization.py:4` to `:19` plus `:3270` confirm the generator's local import surface remains `_wrap_io.py`; no additional local helpers need legacy-code allowlisting.
- Live file inspection confirmed the five deployment files are present in this checkout.

## Risk / Impact

Residual risk is implementation drift: if the implementation copies a broader `scripts/deploy/` tree, reintroduces recursive legacy `scripts/` reads, or treats present-but-failed deployment copies as warnings instead of errors, the proof becomes weak again. The proposed tests are sufficient to catch that drift if implemented as described.

The `status="ok"` plus `deployment_evidence_incomplete` warning for deployment files absent from legacy source is acceptable for this proposal because it distinguishes true source absence from failed sandbox copy. In the current checkout all five files exist, so the live implementation path should copy all five and emit no such warning.

## Implementation Constraints

- Do not restore recursive `legacy_root/scripts` allowance.
- Keep legacy originals of the five deployment files denied.
- Copy the five deployment files into the sandbox as real files, not symlinks, preserving relative paths.
- If a deployment file exists in legacy source but is not copied byte-equally into the sandbox, return `status="error"`.
- Preserve the tests proposed in REVISED-5 sections 3.1 and 3.2, including a guard that bystander files under `scripts/deploy/` are not copied.
- Advance the driver missing-lane fixture from `dashboard` to `rollback` when `_dashboard_regen.py` lands.

## Recommended Action

Proceed to implementation under the REVISED-5 constraints. Post-implementation verification should run the new `tests/scripts/test_rehearse_dashboard_regen.py`, the driver regression, focused Ruff checks for the new files, and a live dashboard-regeneration rehearsal smoke.

## Decision Needed From Owner

None.
