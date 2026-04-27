NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice9-003.md`
Scope: Production effects rehearsal lane proposal for `scripts/rehearse/_production_effects.py`

## Claim

NO-GO. The revised source set and deploy-safety field address the previous coverage defect, but the proposal now creates a credential-safety contradiction around production environment variable files.

## Evidence

- The original Slice 9 safety property remains in force: sensitive content must not be read; `.env.local`, `.env`, secrets, and credential fields are presence/size only.
- The revision adds `scripts/deploy/_prod_env_vars*.txt` as deploy surfaces with disposition `MOVE` and `deploy-blocking`.
- The revision also says deploy-script surfaces receive per-file content scans for hardcoded legacy-root references.
- Files named `_prod_env_vars*.txt` are production environment variable material and should be treated as secret-adjacent at minimum. The revised proposal does not explicitly exempt those files from content scanning.
- By contrast, the revision correctly treats Terraform `*.tfvars` as presence-only and `DO_NOT_MOVE` because they are secret-adjacent.

## Risk / Impact

As written, the lane could read and relocate production environment variable material during a rehearsal review. That violates the credential-safety posture and the original Slice 9 safety property.

## Required Revision

- Treat `scripts/deploy/_prod_env_vars*.txt` as secret-adjacent:
  - presence, size, and path only;
  - no content scan;
  - `DO_NOT_MOVE` or `OWNER_DECISION_REQUIRED`, not automatic `MOVE`.
- Add a regression test proving `_prod_env_vars*.txt` files are not opened/read.
- Keep hardcoded-path content scanning for non-secret deploy scripts and configs only.
- Preserve the useful revised additions: Docker, Shopify, deploy scripts, Terraform, GitHub Actions working-directory scan, and first-class `deploy_safety`.

## Decision Needed From Owner

None. Prime needs to revise the sensitive-file handling before implementation.
