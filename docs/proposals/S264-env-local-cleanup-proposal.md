# Implementation Proposal: .env.local Cleanup & Reorganization

**Session:** S264
**Date:** 2026-04-07
**Author:** Prime Builder (Opus 4.6)

## Problem Statement

The current `.env.local` has caused multiple incidents:
1. Encryption migration accidentally ran against production (S263)
2. Ongoing confusion about which keys belong to which environment
3. `COSMOS_DB_DATABASE=agentred` (production) as the default is dangerous
4. `KEY_VAULT_URL` vs `AZURE_KEYVAULT_URL` env var contract split
5. Production keys have inconsistent naming (`PRODUCTION_TEST-CUSTOMER@REMAKERDIGITAL.COM_API-KEY`)

## Proposed Changes

### 1. Change default database to staging
- `COSMOS_DB_DATABASE=agentred-staging` (was `agentred`)
- Add comment warning that production DB name is `agentred`

### 2. Add AZURE_KEYVAULT_URL alongside KEY_VAULT_URL
- Add `AZURE_KEYVAULT_URL` pointing to production KV (same value as `KEY_VAULT_URL`)
- Add `STAGING_AZURE_KEYVAULT_URL` pointing to staging KV
- Keep `KEY_VAULT_URL` for backward compat but add deprecation note

### 3. Reorganize into clear sections
- Section 1: Azure Infrastructure (shared)
- Section 2: External Services (shared)
- Section 3: STAGING keys (clearly labeled)
- Section 4: PRODUCTION keys (clearly labeled, with WARNING banner)
- Section 5: Backward-compatible aliases (default to staging)

### 4. Rename production keys
- `PRODUCTION_REMAKER_USER_KEY` (was missing)
- `PRODUCTION_REMAKER_TENANT_KEY` (was `ar_live_test-...`)
- `PRODUCTION_REMAKER_WIDGET_KEY` (was missing)
- Remove stale `PRODUCTION_TEST-CUSTOMER@REMAKERDIGITAL.COM_API-KEY`

### 5. Add MASTER_KEK_KEY_ID entries
- `STAGING_MASTER_KEK_KEY_ID` for staging
- `PRODUCTION_MASTER_KEK_KEY_ID` for production
- Default `MASTER_KEK_KEY_ID` not set (forces explicit choice)

## Risk Assessment

**LOW.** This is a local-only file. No runtime impact. The key change (COSMOS_DB_DATABASE defaulting to staging) prevents future production accidents.

## Verification

After cleanup, run `python -c "import dotenv; ..."` to confirm all keys parse correctly.

---
*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
