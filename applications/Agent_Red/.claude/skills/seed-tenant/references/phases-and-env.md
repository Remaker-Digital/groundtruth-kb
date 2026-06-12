# Seed Tenant: Phases & Environment Variables

## 9-Phase Process

| Phase | Name | What It Does |
|-------|------|-------------|
| 0 | Clean Partition | Delete ALL documents for tenant from 9 containers |
| 1 | Containers | Create/verify 10 Cosmos DB containers with indexes |
| 2 | Tenant | Create TenantDocument (status=active, tier=professional) |
| 3 | Preferences | Create PreferencesDocument v1 (config_state=draft) |
| 4 | Team | Create 1 TeamMemberDocument (superadmin) with API key |
| 5 | Knowledge Base | Seed zero KB articles (optionally embed with --embed) |
| 6 | Platform Config | Create 4 tier_defaults documents |
| 7 | Demo Data | Seed conversations/profiles (only with --demo) |
| 8 | Summary | Print all credentials, URLs, and phase results |

## Environment Variables

Required in `.env.local`:
- `COSMOS_DB_ENDPOINT` -- Azure Cosmos DB endpoint URL
- `COSMOS_DB_KEY` -- Azure Cosmos DB primary key
- `COSMOS_DB_DATABASE` -- Database name (default: `agentred`)

Optional overrides:
- `SEED_TENANT_ID` (default: `remaker-digital-001`)
- `SEED_SHOP_DOMAIN` (default: `blanco-9939.myshopify.com`)
- `SEED_CUSTOMER_EMAIL` (default: `mike@remakerdigital.com`)
- `SEED_TIER` (default: `professional`)

## Post-Seed Steps (MANDATORY after --execute)

1. **Update Azure Key Vault** with the new API key from Phase 8 output:
   ```bash
   az keyvault secret set --vault-name kv-agentred-eastus --name ADMIN-PREVIEW-API-KEY --value "<NEW_KEY>"
   ```

2. **Restart Container App** to pick up new credentials:
   ```bash
   az containerapp revision restart --name agent-red-api-gateway --resource-group Agent-Red --revision <ACTIVE_REVISION>
   ```

3. **Verify admin UI auth:**
   ```bash
   curl -s https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/api/tenants/lookup -H "X-API-Key: <NEW_KEY>"
   ```

4. **Update `.env.local`** with new `SUPERADMIN_PREVIEW_API_KEY` and `PREVIEW_WIDGET_KEY` from Phase 8 output.

5. **Update `memory/MEMORY.md`** if tenant credentials changed.
