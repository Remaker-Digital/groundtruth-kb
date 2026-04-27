VERIFIED

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 Post-Implementation REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice9-009.md`
Scope: verification of the revised Slice 9 production-effects implementation after `-008` NO-GO
Verdict: VERIFIED

## Prior Deliberations

- `DELIB-1106` covers the Wave 2 implementation bridge thread and remains relevant umbrella context for Stage B lane behavior.
- `DELIB-0961` covers the earlier Phase 8 rehearsal implementation NO-GO and remains relevant to the production-effects-map requirement.
- No harvested deliberation was found for the exact `gtkb-isolation-016-phase8-wave2-slice9` bridge thread yet; the live bridge thread remains the operative review record.

## Claim

VERIFIED. The `-009` revision resolves both `-008` P1 findings:

1. directory production surfaces are now reported as existing directories instead of absent files;
2. live approval packets are now classified through top-level artifact metadata rather than the synthetic `approved_records` fixture shape.

The original `-006` GO constraints around `_prod_env_vars*.txt` secret-adjacent handling also remain covered by tests and output evidence.

## Verification Performed

- `python -m pytest tests/scripts/test_rehearse_production_effects.py -q --tb=short --timeout=60`
  - Result: `28 passed in 0.63s`.
- `python -m pytest @tmp/rehearse-test-files.txt -q --tb=line --timeout=120`
  - Explicit file list over all `tests/scripts/test_rehearse_*.py`.
  - Result: `242 passed in 4.13s`.
- `python -m ruff check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py`
  - Result: `All checks passed!`.
- `python -m ruff format --check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py`
  - Result: `2 files already formatted`.
- `python scripts/rehearse_isolation.py --phase production --execute --output-dir C:\temp\agent-red-rehearsal-slice9-revised1-codex-verify`
  - Result: `production ... ok`.

## Finding 1 Closure - Directory Surfaces

### Evidence

The revised live smoke output at `C:\temp\agent-red-rehearsal-slice9-revised1-codex-verify\production_effects\production_effects.json` now reports:

- `.shopify/deploy-bundle`: `exists=True`, `is_file=False`, `is_directory=True`, `content_read=False`.
- `.groundtruth/wrap-scan`: `exists=True`, `is_file=False`, `is_directory=True`, `content_read=False`.
- `.groundtruth/session`: `exists=True`, `is_file=False`, `is_directory=True`, `content_read=False`.

The test suite includes `test_run_reports_directory_surfaces_as_existing` and `test_run_reports_file_surfaces_with_is_file_true`, which cover the file/directory distinction directly.

### Risk / Impact

Closed. The production-effects map no longer emits false-negative absence evidence for those live directory surfaces.

### Recommended Action

None for this slice.

### Owner Decision Needed

No.

## Finding 2 Closure - Approval Packet Schema

### Evidence

The revised live smoke output now shows all 28 approval-packet rows using `classification_basis: live_schema_top_level_artifact`.

Observed live classification signals included:

- `framework_approval_packet_gtkb_prefix`: 1 row.
- `framework_approval_packet_artifact_type_governance`: 8 rows.
- `framework_approval_packet_artifact_type_architecture_decision`: 1 row.
- `deliberation_approval_packet_subject_ambiguous`: 17 rows.
- `approval_packet_unclassified_owner_decision`: 1 row.

The prior failure mode, where all 28 packets collapsed to `neutral_approval_packet_owner_decision` with zero `approved_record_id_prefix_counts`, is gone.

The tests now include live-schema fixtures for:

- GTKB-prefixed artifact IDs.
- governance artifact type.
- framework-source deliberations.
- adopter-source deliberations.
- ambiguous deliberations.
- AR-prefixed artifact IDs.

### Risk / Impact

Closed for the `-008` blocker. Some live `DELIB-*` packets remain intentionally owner-decision because top-level metadata is not enough to determine subject safely. That is acceptable for this slice because the revised classifier now distinguishes current-schema packets instead of treating them as unsupported.

### Recommended Action

None for this slice.

### Owner Decision Needed

No.

## Preserved Safety Evidence

- `_prod_env_vars*.txt` remains secret-adjacent and presence-only.
- `.env.local` remains presence-only.
- `*.tfvars` remains presence-only.
- The live smoke summary reports `secret_material_with_content_read: 0`.
- Schema consistency check found zero rows missing `exists`, `is_file`, `is_directory`, `content_read`, or `deploy_safety`.

## Decision Needed From Owner

None.

