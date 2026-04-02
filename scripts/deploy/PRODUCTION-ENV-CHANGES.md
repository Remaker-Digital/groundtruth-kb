# Production Gateway Env Var Changes from Staging Base

When using the staging YAML export as a base for production, change these values:

## Must Change (environment-specific)

| Env Var | Staging Value | Production Value |
|---------|---------------|------------------|
| `ENVIRONMENT` | `staging` | `production` |
| `COSMOS_DB_DATABASE` | `agentred-staging` | `agentred` |
| `KEY_VAULT_URL` | `https://kv-agentred-staging.vault.azure.net/` | `https://kv-agentred-eastus.vault.azure.net/` |
| `AZURE_KEYVAULT_URL` | `https://kv-agentred-staging.vault.azure.net/` | `https://kv-agentred-eastus.vault.azure.net/` |
| `CONTAINER_APP_FQDN` | `agent-red-staging.orangeglacier...` | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `TEST_HOST_URL` | `https://agent-red-test-host.internal...` | `https://agent-red-test-host-prod.internal.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `APP_CORS_ORIGINS` | staging URLs | `https://blanco-9939.myshopify.com,https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |

## Must Change (secrets — get from Key Vault)

| Env Var | Source |
|---------|--------|
| `ADMIN_PREVIEW_API_KEY` | Key Vault `admin-preview-api-key` |
| `SUPERADMIN_PREVIEW_API_KEY` | Key Vault `superadmin-preview-api-key` |
| `STRIPE_SECRET_KEY` | Key Vault (production Stripe key, `sk_live_*` not `sk_test_*`) |
| `STRIPE_WEBHOOK_SECRET` | Key Vault (production webhook secret) |

## Must Change (scaling)

| Property | Staging | Production |
|----------|---------|------------|
| `minReplicas` | `0` | `2` |
| `maxReplicas` | `3` | `8` |

## Remove (staging-only)

| Env Var | Reason |
|---------|--------|
| `DISABLE_RATE_LIMITING` | Production must enforce rate limits |
| `PRE_AUTH_RATE_LIMIT_EXEMPT_IPS` | Staging developer IP only |
| `LOG_LEVEL` | Use production default (INFO) |

## Keep Same

All other env vars (AZURE_OPENAI_*, COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, NATS_URL,
SHOPIFY_*, SMTP_*, MASTER_KEK_KEY_ID, LANGFUSE_*, etc.) are shared infrastructure
and should remain the same between staging and production.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
