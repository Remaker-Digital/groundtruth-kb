# Agent Red Customer Experience — Langfuse Observability (G1 Lane 2)
#
# Provisions Key Vault secrets and api-gateway-only RBAC for Langfuse Cloud
# integration. All resources gated behind var.enable_langfuse.
#
# Scope: api-gateway only (least privilege per Codex review S248).
# No self-hosted infrastructure — uses Langfuse Cloud SaaS.
#
# SPEC-1874 (Lane 1 structural export)
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# ---------------------------------------------------------------------------
# Hash salt — generated per-environment, never leaves Key Vault
# ---------------------------------------------------------------------------

resource "random_password" "langfuse_hash_salt" {
  count   = var.enable_langfuse ? 1 : 0
  length  = 32
  special = true
}

# ---------------------------------------------------------------------------
# Key Vault secrets — Langfuse credentials
# ---------------------------------------------------------------------------

resource "azurerm_key_vault_secret" "langfuse_hash_salt" {
  count        = var.enable_langfuse ? 1 : 0
  name         = "langfuse-hash-salt"
  value        = random_password.langfuse_hash_salt[0].result
  key_vault_id = data.azurerm_key_vault.main.id

  tags = merge(var.tags, {
    purpose = "langfuse-observability"
  })
}

resource "azurerm_key_vault_secret" "langfuse_public_key" {
  count        = var.enable_langfuse ? 1 : 0
  name         = "langfuse-public-key"
  value        = var.langfuse_public_key
  key_vault_id = data.azurerm_key_vault.main.id

  tags = merge(var.tags, {
    purpose = "langfuse-observability"
  })

  # Codex guardrail: prevent deploy with enable_langfuse=true but empty keys
  lifecycle {
    precondition {
      condition     = length(var.langfuse_public_key) > 0
      error_message = "langfuse_public_key must be non-empty when enable_langfuse is true."
    }
  }
}

resource "azurerm_key_vault_secret" "langfuse_secret_key" {
  count        = var.enable_langfuse ? 1 : 0
  name         = "langfuse-secret-key"
  value        = var.langfuse_secret_key
  key_vault_id = data.azurerm_key_vault.main.id

  tags = merge(var.tags, {
    purpose = "langfuse-observability"
  })

  # Codex guardrail: prevent deploy with enable_langfuse=true but empty keys
  lifecycle {
    precondition {
      condition     = length(var.langfuse_secret_key) > 0
      error_message = "langfuse_secret_key must be non-empty when enable_langfuse is true."
    }
  }
}

# ---------------------------------------------------------------------------
# RBAC — Key Vault Secrets User for api-gateway ONLY (least privilege)
# ---------------------------------------------------------------------------
#
# S251 Codex P1 remediation: Security RBAC stays in Terraform even though
# the container app itself is CI/CD-managed. Uses data source lookup.

resource "azurerm_role_assignment" "gateway_langfuse_secrets" {
  count = var.enable_langfuse && local.gateway_principal_id != "" ? 1 : 0

  scope                = data.azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = local.gateway_principal_id
}
