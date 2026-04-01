# Agent Red Customer Experience — Infrastructure Terraform Configuration
#
# Manages foundational Azure infrastructure: Container App Environment,
# Log Analytics, Key Vault keys/secrets, CMK, and security RBAC.
#
# Container Apps themselves are managed via Azure CLI / GitHub Actions.
# See git history (commit prior to S251) for the original app resource block.
#
# Usage:
#   cd infrastructure/terraform
#   terraform init
#   terraform plan -var-file="staging.tfvars"
#   terraform apply -var-file="staging.tfvars"
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Remote state — uncomment and configure for team use
  # backend "azurerm" {
  #   resource_group_name  = "agentred-prod-rg"
  #   storage_account_name = "agentredtfstate"
  #   container_name       = "tfstate"
  #   key                  = "agent-red.tfstate"
  # }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# ---------------------------------------------------------------------------
# Data Sources
# ---------------------------------------------------------------------------

data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

data "azurerm_container_registry" "acr" {
  name                = split(".", var.container_registry)[0]
  resource_group_name = var.resource_group_name
}

# ---------------------------------------------------------------------------
# Container Apps Managed Environment
# ---------------------------------------------------------------------------

resource "azurerm_container_app_environment" "main" {
  name                       = var.container_app_environment_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  infrastructure_subnet_id   = var.container_apps_subnet_id != "" ? var.container_apps_subnet_id : null
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = var.tags

  # Prevent forced replacement from ForceNew attributes.
  # - infrastructure_resource_group_name: Azure auto-assigns on creation
  # - log_analytics_workspace_id: state has null (imported without workspace),
  #   config links to managed workspace. Changing null→value forces replacement
  #   which would destroy ALL container apps in this environment. (S251 Codex P1)
  lifecycle {
    ignore_changes = [
      infrastructure_resource_group_name,
      log_analytics_workspace_id,
    ]
  }
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "agent-red-logs"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = var.tags
}

# ---------------------------------------------------------------------------
# Container Apps — REFERENCE CONFIGURATION ONLY
# ---------------------------------------------------------------------------
#
# Container Apps are managed via Azure CLI / GitHub Actions (CI/CD), NOT by
# Terraform. This separation was formalized in S251 after the S248 incident
# where Terraform destroyed agent-red-api-gateway (a stale resource in state)
# which was NOT the active staging gateway (agent-red-staging).
#
# The locals below are preserved as reference documentation for scaling,
# environment variables, and infrastructure configuration. They are consumed
# by scaling_profiles.tf for validation and metrics documentation.
#
# To restore Terraform management of container apps:
#   1. Restore the azurerm_container_app.apps resource block from git history
#      (last present in the commit immediately before S251 Terraform cleanup)
#   2. Import existing apps: terraform import 'azurerm_container_app.apps["api-gateway"]' <resource-id>
#   3. Restore app-scoped monitoring alerts from monitoring.tf git history
#   4. Remove gateway_container_app_name data-source RBAC (replaced by for_each RBAC)
#   5. Run terraform plan to verify no unexpected replacements before apply
#

# Shared environment variables for all agent containers (reference)
locals {
  shared_env = [
    { name = "ENVIRONMENT", value = var.environment },
    { name = "NATS_URL", value = var.nats_url },
    { name = "AGNTCY_SLIM_ENDPOINT", value = var.slim_endpoint },
    { name = "AGNTCY_SLIM_SHARED_SECRET", secret_name = "slim-shared-secret" },
    { name = "COSMOS_DB_ENDPOINT", value = var.cosmos_db_endpoint },
    { name = "COSMOS_DB_DATABASE", value = var.cosmos_db_database },
    { name = "COSMOS_USE_MANAGED_ID", value = "true" },
    { name = "AZURE_KEYVAULT_URL", value = var.key_vault_url },
    { name = "MASTER_KEK_KEY_ID", value = try(azurerm_key_vault_key.cmk[0].versionless_id, "") },
    { name = "USE_AZURE_OPENAI", value = "true" },
    { name = "AZURE_OPENAI_ENDPOINT", value = var.azure_openai_endpoint },
    { name = "APPLICATIONINSIGHTS_CONNECTION_STRING", secret_name = "appinsights-connection-string" },
    # WI #59: Graceful shutdown — containers get 60s to drain connections
    { name = "GRACEFUL_SHUTDOWN_TIMEOUT", value = "60" },
  ]

  # Container app definitions — Decision #16 Option B+
  # Format: name => { image, port, cpu, memory, min, max, critical, scale_trigger }
  container_apps = {
    api-gateway = {
      image        = "api-gateway:v1.0.0"
      port         = 8000
      cpu          = 0.5
      memory       = "1Gi"
      min_replicas = 2
      max_replicas = 8
      critical     = true
      scale_type   = "http"
      scale_rule = {
        concurrent_requests = 50
      }
    }

    intent-classifier = {
      image        = "agent-intent-classifier:v1.0.0"
      port         = 8080
      cpu          = 0.5
      memory       = "1Gi"
      min_replicas = 2
      max_replicas = 6
      critical     = true
      scale_type   = "nats"
      scale_rule = {
        subject        = "*.intent-classifier"
        queue_length   = 20
        consumer_group = "intent-classifier-group"
      }
    }

    knowledge-retrieval = {
      image        = "agent-knowledge-retrieval:v1.0.0"
      port         = 8080
      cpu          = 0.5
      memory       = "1Gi"
      min_replicas = 2
      max_replicas = 6
      critical     = true
      scale_type   = "nats"
      scale_rule = {
        subject        = "*.knowledge-retrieval"
        queue_length   = 15
        consumer_group = "knowledge-retrieval-group"
      }
    }

    response-generator = {
      image        = "agent-response-generator:v1.0.0"
      port         = 8080
      cpu          = 1.0
      memory       = "2Gi"
      min_replicas = 2
      max_replicas = 10
      critical     = true
      scale_type   = "nats"
      scale_rule = {
        subject        = "*.response-generator"
        queue_length   = 10
        consumer_group = "response-generator-group"
      }
    }

    critic-supervisor = {
      image        = "agent-critic-supervisor:v1.0.0"
      port         = 8080
      cpu          = 0.5
      memory       = "1Gi"
      min_replicas = 2
      max_replicas = 4
      critical     = true
      scale_type   = "nats"
      scale_rule = {
        subject        = "*.critic-supervisor"
        queue_length   = 20
        consumer_group = "critic-supervisor-group"
      }
    }

    escalation = {
      image        = "agent-escalation-handler:v1.0.0"
      port         = 8080
      cpu          = 0.25
      memory       = "0.5Gi"
      min_replicas = 1
      max_replicas = 3
      critical     = false
      scale_type   = "nats"
      scale_rule = {
        subject        = "*.escalation-handler"
        queue_length   = 30
        consumer_group = "escalation-group"
      }
    }

    analytics = {
      image        = "agent-analytics-collector:v1.0.0"
      port         = 8080
      cpu          = 0.25
      memory       = "0.5Gi"
      min_replicas = 1
      max_replicas = 2
      critical     = false
      scale_type   = "nats"
      scale_rule = {
        subject        = "*.analytics-collector"
        queue_length   = 50
        consumer_group = "analytics-group"
      }
    }

    slim-gateway = {
      image        = "slim-gateway:latest"
      port         = 8443
      cpu          = 0.5
      memory       = "1Gi"
      min_replicas = 2
      max_replicas = 2
      critical     = true
      scale_type   = "none"
      scale_rule   = {}
    }

    nats = {
      image        = "nats:2.10-alpine"
      port         = 8080 # WebSocket port — Container Apps HTTP ingress requires HTTP/WS, not raw TCP
      cpu          = 0.5
      memory       = "1Gi"
      min_replicas = 2
      max_replicas = 2
      critical     = true
      scale_type   = "none"
      scale_rule   = {}
    }
  }

  # Per-app environment variables (supplements shared_env for specific apps)
  # G1 Lane 2: Langfuse vars scoped to api-gateway only (least privilege)
  per_app_env = {
    api-gateway = var.enable_langfuse ? [
      { name = "LANGFUSE_ENABLED", value = "true" },
      { name = "LANGFUSE_HOST", value = var.langfuse_host },
      { name = "LANGFUSE_HASH_SALT", secret_name = "langfuse-hash-salt" },
      { name = "LANGFUSE_PUBLIC_KEY", secret_name = "langfuse-public-key" },
      { name = "LANGFUSE_SECRET_KEY", secret_name = "langfuse-secret-key" },
    ] : []
  }

  # Langfuse KV secret name → versionless ID mapping (api-gateway only)
  langfuse_secret_map = var.enable_langfuse ? {
    "langfuse-hash-salt"  = azurerm_key_vault_secret.langfuse_hash_salt[0].versionless_id
    "langfuse-public-key" = azurerm_key_vault_secret.langfuse_public_key[0].versionless_id
    "langfuse-secret-key" = azurerm_key_vault_secret.langfuse_secret_key[0].versionless_id
  } : {}
}

# ---------------------------------------------------------------------------
# Container App resource — REMOVED (S251)
# ---------------------------------------------------------------------------
#
# The azurerm_container_app.apps resource block has been removed.
# Container Apps are managed via Azure CLI / GitHub Actions.
#
# The full resource definition is preserved in git history (commit prior to
# S251 Terraform cleanup) and can be restored per the instructions above.
#
# Security RBAC (KEK + Langfuse secrets) remains Terraform-managed via
# data-source lookups of the CI/CD-managed gateway app (S251 Codex P1).
# See dr_security.tf and langfuse.tf for the data-source-backed assignments.
#
# App-scoped monitoring alerts (4 of 5) were removed. Cosmos throttling
# alert was restored standalone in monitoring.tf (S251 Codex P2).

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "container_app_environment_id" {
  description = "Container App Environment ID"
  value       = azurerm_container_app_environment.main.id
}

output "scaling_summary" {
  description = "Scaling configuration summary (reference — apps managed via CI/CD)"
  value = { for k, v in local.container_apps : k => {
    min      = v.min_replicas
    max      = v.max_replicas
    critical = v.critical
    trigger  = v.scale_type
  } }
}
