NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 Post-Implementation

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice9-007.md`
Scope: post-implementation verification for `scripts/rehearse/_production_effects.py`
Verdict: NO-GO

## Prior Deliberations

- `DELIB-1106` covers the Wave 2 implementation bridge thread and remains relevant umbrella context for Stage B lane behavior.
- `DELIB-0961` covers the earlier Phase 8 rehearsal implementation NO-GO and remains relevant to the production-effects-map requirement.
- No harvested deliberation was found for the exact `gtkb-isolation-016-phase8-wave2-slice9` bridge thread yet; the live bridge thread `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md` through `-007.md` is the operative review record.

## Claim

NO-GO. The implementation satisfies the reported focused tests and preserves the specific `_prod_env_vars*.txt` content-read guard from the GO conditions, but the generated production-effects map is inaccurate against the live checkout in two production-relevant areas:

1. existing directory surfaces are emitted as absent;
2. formal approval packets are classified against a schema that the live approval files do not use.

## Verification Performed

- `python -m pytest tests/scripts/test_rehearse_production_effects.py -q --tb=short --timeout=60` -> `20 passed in 0.47s`.
- `python -m pytest @tmp/rehearse-test-files.txt -q --tb=line --timeout=120` over all `tests/scripts/test_rehearse_*.py` files -> `234 passed in 3.93s`.
- `python -m ruff check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py` -> `All checks passed!`.
- `python -m ruff format --check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py` -> `2 files already formatted`.
- `python scripts/rehearse_isolation.py --phase production --execute --output-dir C:\temp\agent-red-rehearsal-slice9-codex-verify` -> `production ... ok`.

## Finding 1 - P1: Directory Production Surfaces Are Reported As Absent

### Claim

The live production-effects output misrepresents existing directory surfaces as `exists: false`.

### Evidence

- The implementation treats every non-secret surface as existing only when it is a file: `scripts/rehearse/_production_effects.py:621` sets `exists = path.exists() and path.is_file()`.
- The proposal includes directory-like production surfaces such as `.shopify/deploy-bundle`, `.groundtruth/wrap-scan`, and `.groundtruth/session` in the source set.
- Live filesystem probe during this review showed:
  - `.shopify/deploy-bundle exists=True is_file=False is_dir=True`
  - `.groundtruth/wrap-scan exists=True is_file=False is_dir=True`
  - `.groundtruth/session exists=True is_file=False is_dir=True`
- The live smoke output at `C:\temp\agent-red-rehearsal-slice9-codex-verify\production_effects\production_effects.json` emitted:
  - `.shopify/deploy-bundle`: `exists: false`, `size_bytes: 0`
  - `.groundtruth/wrap-scan`: `exists: false`, `size_bytes: 0`
  - `.groundtruth/session`: `exists: false`, `size_bytes: 0`

### Risk / Impact

The production-effects map is intended to drive cutover review. Reporting real production or session-evidence directories as absent creates false-negative evidence and can let cutover planning skip live surfaces that must be reviewed, archived, moved, or explicitly left in place.

### Required Action

- Change non-secret probing to distinguish `exists`, `is_file`, and `is_dir` instead of collapsing existence into `path.is_file()`.
- Preserve safe content scanning only for files; directories should not be content-read.
- Add regression tests with directory fixtures for at least `.shopify/deploy-bundle`, `.groundtruth/wrap-scan`, and `.groundtruth/session`.
- Re-run the live smoke and confirm those rows show `exists: true` with an explicit directory indicator.

### Owner Decision Needed

No.

## Finding 2 - P1: Approval Packet Classification Does Not Match The Live Approval Schema

### Claim

The implementation classifies approval packets using `approved_records[*].id`, but the live approval packets in this checkout use top-level artifact metadata instead. As a result, all live approval packets are emitted as neutral owner-decision rows.

### Evidence

- `scripts/rehearse/_production_effects.py:688` reads `approved_records = data.get("approved_records", [])`.
- The live approval files inspected during this review have no `approved_records`; examples use top-level keys such as `artifact_id`, `artifact_type`, `source_ref`, `full_content`, and `full_content_sha256`.
- Live schema probe found 28 approval JSON files and none had `approved_records`.
- The live smoke output classified all 28 approval-packet rows as `neutral_approval_packet_owner_decision` with `approved_record_id_prefix_counts` all zero.
- The implementation tests cover synthetic packets with `approved_records`, but do not cover the current top-level `artifact_id` schema.

### Risk / Impact

This defeats the proposal's subject-based approval classification. Framework approvals, adopter approvals, and mixed approval evidence can all collapse into neutral owner-decision rows, increasing manual owner burden and weakening the cutover map's ability to separate GT-KB governance evidence from Agent Red application evidence.

### Required Action

- Add support for the live approval packet schema, at minimum using top-level `artifact_id`, `artifact_type`, `source_ref`, and related ID fields where present.
- Keep the existing `approved_records` path only as backward-compatible handling for synthetic or older packet shapes.
- Add fixture tests using current live-schema examples, including a GTKB/GOV/DELIB-style framework packet and an Agent Red/adopter packet if one exists.
- Avoid relying on `full_content` for classification unless the proposal explicitly justifies that content-read boundary; prefer top-level structural metadata where possible.

### Owner Decision Needed

No.

## Verified Good Parts To Preserve

- The `_prod_env_vars*.txt` glob is in `_SECRET_MATERIAL_SURFACES`, including `_prod_env_vars_clean.txt` coverage.
- The focused safety tests for `_prod_env_vars*.txt`, `.env.local`, and `*.tfvars` pass.
- The `content_read` field and `summary.secret_material_with_content_read == 0` safety evidence are useful and should remain.
- The expanded Docker, Shopify, deploy-script, Terraform, and GitHub Actions hardcoded-path categories should be retained.

## Required Revision Summary

Prime should revise Slice 9 with:

1. directory-aware existence metadata for non-secret surfaces;
2. current-schema approval packet classification;
3. tests covering both defects;
4. the same focused and full rehearsal-suite verification already used in `-007`;
5. a fresh live smoke proving the corrected rows against the actual checkout.

## Decision Needed From Owner

None.

