# Agent Red Customer Engagement — Disaster Recovery & Security Infrastructure
#
# Work Items:
#   #52: Cosmos DB continuous backup (7-day PITR, Decision #18)
#   #55: Customer-Managed Keys for encryption at rest (Decision #20)
#   #58: Health probe configuration for all containers (Decision #19)
#   #59: Rolling deployment with connection draining (Decision #19)
#
# Architecture references:
#   - Decision #18: Cosmos DB continuous 7-day backup (~$4-6/month)
#   - Decision #19: Zero-downtime deployment, 60s draining, health probes
#   - Decision #20: CMK (AES-256) with auto-rotation via Key Vault
#   - Decision #21: Maintenance window Tuesdays 02:00-04:00 UTC
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# ---------------------------------------------------------------------------
# Data sources — existing Key Vault and Cosmos DB
# ---------------------------------------------------------------------------

data "azurerm_key_vault" "main" {
  name                = split(".", split("//", var.key_vault_url)[1])[0]
  resource_group_name = var.resource_group_name
}

data "azurerm_cosmosdb_account" "main" {
  name                = var.cosmos_db_account_name
  resource_group_name = var.resource_group_name
}

data "azurerm_client_config" "current" {}

# ---------------------------------------------------------------------------
# WI #52: Cosmos DB Continuous Backup (Decision #18)
# ---------------------------------------------------------------------------
#
# Enables continuous backup with 7-day point-in-time restore (PITR).
# Self-service restore to any point within the last 7 days.
# Cost: ~$4-6/month on top of serverless RU charges.
#
# NOTE: Continuous backup must be enabled on the Cosmos DB account itself.
# If the account was created with periodic backup, migration to continuous
# requires Azure CLI / portal (one-time, irreversible):
#
#   az cosmosdb update \
#     --name cosmos-agntcy-cs-prod-rc6vcp \
#     --resource-group agntcy-prod-rg \
#     --backup-policy-type Continuous \
#     --continuous-tier Continuous7Days
#
# Once enabled, Terraform manages the account with continuous backup policy.
# The resource below only works if the account already has continuous backup
# or is being created fresh with Terraform.

resource "azurerm_cosmosdb_account" "managed" {
  count = var.manage_cosmos_db_account ? 1 : 0

  name                = var.cosmos_db_account_name
  location            = var.location
  resource_group_name = var.resource_group_name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  # Serverless capacity (existing configuration)
  capacity {
    total_throughput_limit = -1 # Serverless — no provisioned throughput
  }

  # Continuous 7-day backup (WI #52, Decision #18)
  backup {
    type               = "Continuous"
    tier               = "Continuous7Days"
    storage_redundancy = "Local" # LRS — single-region for launch (Decision #21 Option A)
  }

  # Consistency policy — Session (default for multi-tenant SaaS)
  consistency_policy {
    consistency_level = "Session"
  }

  # Single-region geo-location (Decision #21: Option A for launch)
  geo_location {
    location          = var.location
    failover_priority = 0
  }

  # CMK encryption (WI #55, conditional — see below)
  dynamic "identity" {
    for_each = var.enable_cmk ? [1] : []
    content {
      type = "SystemAssigned"
    }
  }

  # Analytics store for Change Feed → Parquet export (Decision #18)
  analytical_storage_enabled = true

  tags = merge(var.tags, {
    backup_type      = "continuous-7day"
    backup_retention = "7d-pitr"
    dr_tier          = "option-a-single-region"
  })

  lifecycle {
    # Prevent accidental deletion of the database account
    prevent_destroy = true
  }
}

# ---------------------------------------------------------------------------
# WI #55: Customer-Managed Keys — Key Vault Key (Decision #20)
# ---------------------------------------------------------------------------
#
# Creates an RSA-2048 key in Key Vault for encrypting Cosmos DB and Blob
# Storage data at rest. Auto-rotation policy rotates the key every 90 days.
#
# CMK provides:
#   - AES-256 encryption at rest (all tiers)
#   - Tenant data isolation at the encryption layer
#   - Key rotation without downtime
#   - Audit trail of key access in Key Vault logs

resource "azurerm_key_vault_key" "cmk" {
  count = var.enable_cmk ? 1 : 0

  name         = "agent-red-cmk"
  key_vault_id = data.azurerm_key_vault.main.id
  key_type     = "RSA"
  key_size     = 2048

  key_opts = [
    "encrypt",
    "decrypt",
    "wrapKey",
    "unwrapKey",
  ]

  # Auto-rotation every 90 days (Decision #20)
  rotation_policy {
    automatic {
      time_before_expiry = "P30D" # Rotate 30 days before expiry
    }

    expire_after         = "P120D" # Key expires after 120 days
    notify_before_expiry = "P14D"  # Notify 14 days before expiry
  }

  tags = merge(var.tags, {
    purpose  = "data-encryption-at-rest"
    rotation = "90-day-auto"
  })
}

# Key Vault access policy for Cosmos DB to use CMK
resource "azurerm_key_vault_access_policy" "cosmos_cmk" {
  count = var.enable_cmk && var.manage_cosmos_db_account ? 1 : 0

  key_vault_id = data.azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_cosmosdb_account.managed[0].identity[0].principal_id

  key_permissions = [
    "Get",
    "UnwrapKey",
    "WrapKey",
  ]
}

# ---------------------------------------------------------------------------
# WI #55: Blob Storage for archival (Decision #18 — Warm + Cold tiers)
# ---------------------------------------------------------------------------
#
# Three-tier data lifecycle:
#   Hot:  Cosmos DB (real-time, 7-day PITR)
#   Warm: Blob Cool tier (90-day retention, Parquet exports)
#   Cold: Blob Archive tier (7+ year retention, compliance)

resource "azurerm_storage_account" "archival" {
  count = var.enable_archival_storage ? 1 : 0

  name                     = var.archival_storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # Single-region for launch (Decision #21)

  # CMK encryption for Blob Storage (WI #55)
  dynamic "identity" {
    for_each = var.enable_cmk ? [1] : []
    content {
      type = "SystemAssigned"
    }
  }

  # Lifecycle management — automatic tiering
  blob_properties {
    delete_retention_policy {
      days = 30 # Soft delete for accidental removal protection
    }

    container_delete_retention_policy {
      days = 30
    }
  }

  tags = merge(var.tags, {
    purpose = "data-archival"
    tiers   = "warm-cool-cold-archive"
  })
}

# CMK encryption for storage account
resource "azurerm_storage_account_customer_managed_key" "archival_cmk" {
  count = var.enable_cmk && var.enable_archival_storage ? 1 : 0

  storage_account_id = azurerm_storage_account.archival[0].id
  key_vault_id       = data.azurerm_key_vault.main.id
  key_name           = azurerm_key_vault_key.cmk[0].name
}

# Warm tier container (90-day retention, Parquet exports from Change Feed)
resource "azurerm_storage_container" "warm" {
  count = var.enable_archival_storage ? 1 : 0

  name                  = "warm-archive"
  storage_account_name  = azurerm_storage_account.archival[0].name
  container_access_type = "private"
}

# Cold tier container (7+ year compliance retention)
resource "azurerm_storage_container" "cold" {
  count = var.enable_archival_storage ? 1 : 0

  name                  = "cold-archive"
  storage_account_name  = azurerm_storage_account.archival[0].name
  container_access_type = "private"
}

# Lifecycle management rules — automatic tier transitions
resource "azurerm_storage_management_policy" "archival_lifecycle" {
  count = var.enable_archival_storage ? 1 : 0

  storage_account_id = azurerm_storage_account.archival[0].id

  # Warm → Cool after 30 days, Cool → Archive after 90 days
  rule {
    name    = "warm-to-cool-to-archive"
    enabled = true

    filters {
      prefix_match = ["warm-archive/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        tier_to_cool_after_days_since_modification_greater_than    = 30
        tier_to_archive_after_days_since_modification_greater_than = 90
        delete_after_days_since_modification_greater_than          = 2555 # ~7 years
      }
    }
  }

  # Cold tier — long-term compliance retention
  rule {
    name    = "cold-compliance-retention"
    enabled = true

    filters {
      prefix_match = ["cold-archive/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        tier_to_archive_after_days_since_modification_greater_than = 0    # Archive immediately
        delete_after_days_since_modification_greater_than          = 2555 # ~7 years
      }
    }
  }
}

# ---------------------------------------------------------------------------
# WI #59: Rolling Deployment with Connection Draining (Decision #19)
# ---------------------------------------------------------------------------
#
# Configures zero-downtime deployment for all container apps:
#   - Single revision mode with rolling update
#   - 60-second connection draining on old revisions
#   - Min replicas maintained during deployment
#   - NATS consumer groups handle message redelivery automatically
#
# NOTE: Azure Container Apps in "Single" revision mode automatically
# replaces old revisions. The connection draining and health probe
# configuration ensures zero-downtime:
#   1. New revision starts and passes readiness probe
#   2. Traffic shifts to new revision
#   3. Old revision enters draining (60s grace period)
#   4. Old revision terminates after draining completes
#
# The revision_mode = "Single" is already set in main.tf.
# Connection draining is configured via the template's
# termination_grace_period_seconds on the container spec.
#
# For Container Apps, the draining behavior is controlled by:
#   - Readiness probe: new revision must pass before receiving traffic
#   - Liveness probe: failed probes trigger container restart
#   - min_replicas: ensures capacity during rolling update

# ---------------------------------------------------------------------------
# WI #58: Health Probe Configuration (Decision #19)
# ---------------------------------------------------------------------------
#
# Health probe design per container type:
#
# | Container            | Liveness Path | Readiness Path | Notes                    |
# |----------------------|---------------|----------------|--------------------------|
# | API Gateway          | /health       | /ready         | Full dependency check    |
# | Intent Classifier    | /health       | /ready         | Includes NATS + OpenAI   |
# | Knowledge Retrieval  | /health       | /ready         | Includes Cosmos + OpenAI |
# | Response Generator   | /health       | /ready         | Includes NATS + OpenAI   |
# | Critic/Supervisor    | /health       | /ready         | Circuit breaker state    |
# | Escalation           | /health       | /ready         | Standard agent probe     |
# | Analytics            | /health       | /ready         | Standard agent probe     |
# | SLIM Gateway         | /healthz      | /healthz       | gRPC health service      |
# | NATS                 | /healthz      | /healthz       | NATS monitoring port     |
#
# Liveness: Lightweight check — process is alive and responsive.
#   - Failure triggers container restart (after failure_count_threshold)
#   - Initial delay allows startup time (10s standard, 15s for Response Generator)
#
# Readiness: Dependency check — service can accept traffic.
#   - Failure removes container from load balancer (no restart)
#   - Checks downstream dependencies (NATS, Cosmos DB, OpenAI, Key Vault)
#
# The health probes are defined inline in main.tf's container app resources.
# The configuration below provides the per-container probe parameters
# that override the defaults in main.tf.

locals {
  # Per-container health probe configuration (WI #58)
  # Overrides the generic /health + /ready defaults in main.tf
  health_probes = {
    api-gateway = {
      liveness_path    = "/health"
      readiness_path   = "/ready"
      liveness_port    = 8080
      readiness_port   = 8080
      initial_delay    = 10
      liveness_period  = 30
      readiness_period = 15
    }

    intent-classifier = {
      liveness_path    = "/health"
      readiness_path   = "/ready"
      liveness_port    = 8080
      readiness_port   = 8080
      initial_delay    = 10
      liveness_period  = 30
      readiness_period = 15
    }

    knowledge-retrieval = {
      liveness_path    = "/health"
      readiness_path   = "/ready"
      liveness_port    = 8080
      readiness_port   = 8080
      initial_delay    = 10
      liveness_period  = 30
      readiness_period = 15
    }

    response-generator = {
      liveness_path    = "/health"
      readiness_path   = "/ready"
      liveness_port    = 8080
      readiness_port   = 8080
      initial_delay    = 15 # Longer startup — GPT-4o connection pooling
      liveness_period  = 30
      readiness_period = 15
    }

    critic-supervisor = {
      liveness_path    = "/health"
      readiness_path   = "/ready"
      liveness_port    = 8080
      readiness_port   = 8080
      initial_delay    = 10
      liveness_period  = 30
      readiness_period = 15
    }

    escalation = {
      liveness_path    = "/health"
      readiness_path   = "/ready"
      liveness_port    = 8080
      readiness_port   = 8080
      initial_delay    = 10
      liveness_period  = 30
      readiness_period = 15
    }

    analytics = {
      liveness_path    = "/health"
      readiness_path   = "/ready"
      liveness_port    = 8080
      readiness_port   = 8080
      initial_delay    = 10
      liveness_period  = 30
      readiness_period = 15
    }

    slim-gateway = {
      liveness_path    = "/healthz"
      readiness_path   = "/healthz"
      liveness_port    = 8443
      readiness_port   = 8443
      initial_delay    = 5 # gRPC — fast startup
      liveness_period  = 30
      readiness_period = 10
    }

    nats = {
      liveness_path    = "/healthz"
      readiness_path   = "/healthz"
      liveness_port    = 8222 # NATS monitoring port (not client port)
      readiness_port   = 8222
      initial_delay    = 5
      liveness_period  = 30
      readiness_period = 10
    }
  }

  # Deployment configuration per container (WI #59)
  deployment_config = {
    # Connection draining grace period in seconds
    # 60s allows in-flight requests and NATS message processing to complete
    termination_grace_period = 60

    # Maintenance window (Decision #21)
    maintenance_day      = "Tuesday"
    maintenance_start    = "02:00"
    maintenance_end      = "04:00"
    maintenance_tz       = "UTC"
    advance_notice_hours = 72
  }
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "backup_configuration" {
  description = "Cosmos DB backup configuration summary"
  value = {
    type           = "Continuous"
    retention      = "7-day PITR"
    storage        = "LRS (single-region)"
    dr_option      = "A — single region + backup"
    estimated_cost = "$4-6/month"
    self_service   = true
    managed_by_tf  = var.manage_cosmos_db_account
  }
}

output "cmk_configuration" {
  description = "Customer-Managed Key configuration"
  value = {
    enabled   = var.enable_cmk
    key_name  = var.enable_cmk ? azurerm_key_vault_key.cmk[0].name : "not-enabled"
    key_vault = data.azurerm_key_vault.main.name
    rotation  = "90-day auto-rotation"
    algorithm = "RSA-2048 / AES-256"
  }
}

output "archival_configuration" {
  description = "Data archival storage configuration"
  value = {
    enabled        = var.enable_archival_storage
    warm_retention = "90 days (Cool tier)"
    cold_retention = "7+ years (Archive tier)"
    format         = "Parquet (Change Feed export)"
    cmk_encrypted  = var.enable_cmk && var.enable_archival_storage
  }
}

output "deployment_configuration" {
  description = "Rolling deployment configuration"
  value = {
    strategy           = "rolling-update"
    revision_mode      = "Single"
    draining_seconds   = local.deployment_config.termination_grace_period
    maintenance_window = "${local.deployment_config.maintenance_day} ${local.deployment_config.maintenance_start}-${local.deployment_config.maintenance_end} ${local.deployment_config.maintenance_tz}"
    advance_notice     = "${local.deployment_config.advance_notice_hours}h"
  }
}
