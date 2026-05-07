# Implementation Proposal: Encryption P0 Verification + Remediation

**Session:** S264
**Date:** 2026-04-07
**Author:** Prime Builder (Opus 4.6)

## Updated Root Cause Analysis

The earlier hypothesis (dev-mode KEK mismatch) was **incorrect**. Investigation reveals:

- Production KV DEK: 256 bytes (RSA-OAEP wrapped with production KEK)
- Staging KV DEK: 256 bytes (also RSA-OAEP wrapped)
- Both DEKs were wrapped with the production RSA KEK, meaning `MASTER_KEK_KEY_ID`
  was available during the S263 migration

The `InvalidTag` error from ad-hoc container exec tests was caused by **incomplete
singleton initialization** — the TenantSecretService singleton wasn't wired into
the global reference used by the repository's `_fetch_tenant_dek`. This is NOT
a production runtime issue.

## Verification Plan

1. Attempt container exec with FULL lifecycle startup (including `_startup_secret_service`)
2. If exec WebSocket is flaky, use an alternative: deploy a one-shot verification
   container job that reads one encrypted record and reports result
3. Check production container logs for any decryption failures over last 24h

## Remediation (if needed)

If verification proves decryption fails in the running application:
- The `fix_devmode_encryption.py` script is NOT appropriate (DEKs are RSA-wrapped, not dev-wrapped)
- Instead: re-run migration with `--force` against production from inside the container
  where both `MASTER_KEK_KEY_ID` and `AZURE_KEYVAULT_URL` are set

## Expected Outcome

Decryption should work correctly. The migration used the production KEK to wrap DEKs,
and the production container has the same KEK configured.

---
*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
