GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 REVISED-2

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice9-005.md`
Scope: Production effects rehearsal lane proposal for `scripts/rehearse/_production_effects.py`

## Claim

GO. The revised proposal resolves the `-004` credential-safety blocker by moving `scripts/deploy/_prod_env_vars*.txt` from content-scanned deploy scripts to secret-adjacent, presence-only, `DO_NOT_MOVE` handling.

## Evidence

- The revision explicitly removes `_prod_env_vars*.txt` from the content-scanned deploy-script section and adds it to the secret-material section.
- The proposed row records `disposition: DO_NOT_MOVE`, `signal: production_env_vars_secret_adjacent_per_codex_s9_004`, `deploy_safety: deploy-blocking`, and `content_read: false`.
- Live repo contains `scripts/deploy/_prod_env_vars.txt` and `scripts/deploy/_prod_env_vars_clean.txt`, so this is a real safety surface.
- The proposed regression test monkeypatches both `Path.read_text` and `Path.read_bytes` for `_prod_env_vars*` files and asserts no forbidden read occurs while still producing the expected surface row.

## Required Implementation Constraints

- Apply the same secret-adjacent treatment to every file matching `scripts/deploy/_prod_env_vars*.txt`, including `_prod_env_vars_clean.txt`.
- Keep content scanning for non-secret deploy scripts/configs only.
- Preserve the `content_read` boolean in output so review can distinguish presence-only probes from content-scanned surfaces.
- Include at least one fixture with multiple `_prod_env_vars*.txt` matches to prevent only the exact `_prod_env_vars.txt` filename from being protected.

## Risk / Impact

Low after the constraints. The design preserves the useful production-effects source expansion while restoring the sensitive-content boundary.

## Decision Needed From Owner

None.
