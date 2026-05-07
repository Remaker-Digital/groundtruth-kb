# Implementation Proposal: Production Encryption Remediation (P0)

**Session:** S264
**Date:** 2026-04-07
**Author:** Prime Builder (Opus 4.6)
**Severity:** P0 — Production data currently unreadable through application

## Root Cause

The S263 encryption migration ran from the local machine against the production
database (`agentred`). The migration script reads `MASTER_KEK_KEY_ID` and
`AZURE_KEYVAULT_URL` to determine encryption mode. Neither was set in `.env.local`
(only `KEY_VAULT_URL` existed), so the migration ran in **dev-mode** — encrypting
all data with an in-memory test key instead of the production KEK.

The production container has `MASTER_KEK_KEY_ID` set via Azure Container App
environment variables, so it attempts to decrypt with the production KEK, which
fails with `cryptography.exceptions.InvalidTag`.

### Evidence Chain

1. `.env.local` (pre-cleanup): `MASTER_KEK_KEY_ID` absent, `AZURE_KEYVAULT_URL` absent
2. `run_data_encryption_migration.py:282-284`: `dev_mode = not kek_key_id` (True when missing)
3. `envelope_encryption.py:77-89`: dev-mode uses in-memory test key
4. Production container exec: `InvalidTag` on decrypt attempt
5. Raw Cosmos query: `customer_email` and `shopify_shop_domain` are ciphertext

### Affected Data

- **Tenants:** remaker-digital-001, test-customer-001 (both had DEKs provisioned)
- **Fields:** customer_email, shopify_shop_domain, brand_name (per _encryption_fields)
- **Collections:** tenants, team_members (per migration script)
- **Scope:** 37 fields across 2 tenants (per S263 memory)

## Remediation Plan

### Step 1: Write a decrypt-reencrypt script

Create `scripts/fix_encryption_key_mismatch.py` that:
1. Reads each affected document directly from Cosmos (bypass repository)
2. Decrypts each field using dev-mode key (same algorithm, in-memory test KEK)
3. Re-encrypts each field using the production KEK via Key Vault
4. Writes the corrected ciphertext back to Cosmos
5. Supports `--dry-run` for preview

### Step 2: Run against production with explicit environment

```bash
AZURE_KEYVAULT_URL=https://kv-agentred-eastus.vault.azure.net/ \
MASTER_KEK_KEY_ID=https://kv-agentred-eastus.vault.azure.net/keys/agent-red-cmk \
COSMOS_DB_DATABASE=agentred \
python scripts/fix_encryption_key_mismatch.py --force
```

### Step 3: Verify via container exec

Re-run the repository read test in the production container to confirm
fields decrypt to plaintext.

### Step 4: Post-mortem updates

- Update Codex with remediation evidence
- Prevent recurrence: migration script should reject dev-mode for non-dev databases

## Risk Assessment

**MEDIUM.** The script must handle the dev-mode decryption correctly. If the
dev-mode key derivation changed between versions, decryption may fail. Mitigation:
use `--dry-run` first to verify one field decrypts correctly before writing.

## Alternative: Revert to plaintext

If re-encryption is problematic, we could decrypt all fields back to plaintext
and re-run the migration properly. This is simpler but means production data
is temporarily unencrypted.

---
*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
