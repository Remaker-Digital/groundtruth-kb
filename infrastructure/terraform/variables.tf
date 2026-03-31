# Agent Red Customer Experience — Terraform Variables
#
# Shared variables for all modules. Override via terraform.tfvars
# or environment variables (TF_VAR_*).
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# ---------------------------------------------------------------------------
# Azure
# ---------------------------------------------------------------------------

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  # Required — provide via .tfvars (e.g. "Agent-Red")
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  # Required — provide via .tfvars (e.g. "eastus")
}

variable "environment" {
  description = "Deployment environment (production, staging, development)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

# ---------------------------------------------------------------------------
# Container Registry
# ---------------------------------------------------------------------------

variable "container_registry" {
  description = "Azure Container Registry login server"
  type        = string
  # Required — provide via .tfvars (e.g. "acragentredeastus.azurecr.io")
}

# ---------------------------------------------------------------------------
# Container App Environment
# ---------------------------------------------------------------------------

variable "container_app_environment_name" {
  description = "Name of the Container Apps managed environment"
  type        = string
  default     = "agent-red-cae"
}

variable "vnet_name" {
  description = "Virtual network name"
  type        = string
  default     = "agentred-prod-vnet"
}

variable "container_apps_subnet_id" {
  description = "Subnet ID for Container Apps (delegated to Microsoft.App/environments)"
  type        = string
}

# ---------------------------------------------------------------------------
# NATS
# ---------------------------------------------------------------------------

variable "nats_url" {
  description = "NATS JetStream URL via secure WebSocket (Container Apps TLS ingress requires wss://)"
  type        = string
  default     = "wss://agent-red-nats.internal:8080"
}

variable "slim_endpoint" {
  description = "SLIM routing endpoint via plain HTTP/2 (allowInsecure=true for gRPC compatibility)"
  type        = string
  default     = "http://agent-red-slim.internal"
}

variable "nats_monitoring_endpoint" {
  description = "NATS monitoring endpoint for KEDA scaler (host:port format)"
  type        = string
  default     = "agent-red-nats.internal:8222"
}

# ---------------------------------------------------------------------------
# Azure OpenAI
# ---------------------------------------------------------------------------

variable "azure_openai_endpoint" {
  description = "Azure OpenAI Service endpoint URL"
  type        = string
  # Required — provide via .tfvars (e.g. "https://agent-red-openai.openai.azure.com/")
}

# ---------------------------------------------------------------------------
# Cosmos DB
# ---------------------------------------------------------------------------

variable "cosmos_db_endpoint" {
  description = "Cosmos DB account endpoint URL"
  type        = string
}

variable "cosmos_db_database" {
  description = "Cosmos DB database name"
  type        = string
  default     = "agentred"
}

variable "cosmos_db_account_name" {
  description = "Cosmos DB account name (for data source lookups)"
  type        = string
  # Required — provide via .tfvars (e.g. "cosmos-agentred-eastus")
}

variable "manage_cosmos_db_account" {
  description = "Whether Terraform manages the Cosmos DB account (set true for new deployments, false for existing accounts)"
  type        = bool
  default     = false
}

# ---------------------------------------------------------------------------
# Customer-Managed Keys (WI #55, Decision #20)
# ---------------------------------------------------------------------------

variable "enable_cmk" {
  description = "Enable Customer-Managed Keys for encryption at rest (Cosmos DB + Blob Storage)"
  type        = bool
  default     = false
}

# ---------------------------------------------------------------------------
# Archival Storage (WI #52, Decision #18)
# ---------------------------------------------------------------------------

variable "enable_archival_storage" {
  description = "Enable Blob Storage for warm/cold data archival"
  type        = bool
  default     = false
}

variable "archival_storage_account_name" {
  description = "Storage account name for data archival (3-24 chars, lowercase alphanumeric)"
  type        = string
  default     = "agentredarchival"
}

# ---------------------------------------------------------------------------
# Key Vault
# ---------------------------------------------------------------------------

variable "key_vault_url" {
  description = "Azure Key Vault endpoint URL"
  type        = string
  # Required — provide via .tfvars (e.g. "https://kv-agentred-eastus.vault.azure.net/")
}

# ---------------------------------------------------------------------------
# Application Insights
# ---------------------------------------------------------------------------

variable "appinsights_connection_string" {
  description = "Application Insights connection string for OpenTelemetry"
  type        = string
  sensitive   = true
  default     = ""
}

# ---------------------------------------------------------------------------
# KEDA Night Scaling (WI #47)
# ---------------------------------------------------------------------------

variable "enable_night_scaling" {
  description = "Enable KEDA cron-based night scaling for non-critical containers (Escalation, Analytics)"
  type        = bool
  default     = false
}

variable "night_scaling_timezone" {
  description = "Timezone for night scaling schedule (IANA format)"
  type        = string
  default     = "UTC"
}

variable "night_scaling_start" {
  description = "Cron expression for night scaling start (scale to 0)"
  type        = string
  default     = "0 22 * * *"
}

variable "night_scaling_end" {
  description = "Cron expression for night scaling end (restore min replicas)"
  type        = string
  default     = "0 6 * * *"
}

# ---------------------------------------------------------------------------
# Scheduled Jobs — Data Retention + Archival (WI #190)
# ---------------------------------------------------------------------------

variable "enable_scheduled_jobs" {
  description = "Enable scheduled Container App Jobs for data retention and archival"
  type        = bool
  default     = false
}

variable "retention_schedule" {
  description = "Cron expression for data retention job (default: daily at 03:00 UTC)"
  type        = string
  default     = "0 3 * * *"
}

variable "archival_schedule" {
  description = "Cron expression for archival pipeline job (default: daily at 04:00 UTC)"
  type        = string
  default     = "0 4 * * *"
}

variable "job_image_tag" {
  description = "Docker image tag for scheduled job container"
  type        = string
  default     = "latest"
}

# ---------------------------------------------------------------------------
# Langfuse Observability (G1 Lane 2, SPEC-1874)
# ---------------------------------------------------------------------------

variable "enable_langfuse" {
  description = "Enable Langfuse observability (Lane 1 structural export, api-gateway only)"
  type        = bool
  default     = false
}

variable "langfuse_host" {
  description = "Langfuse Cloud host URL"
  type        = string
  default     = "https://us.cloud.langfuse.com"
}

variable "langfuse_public_key" {
  description = "Langfuse project public key (from Cloud dashboard, required when enable_langfuse=true)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "langfuse_secret_key" {
  description = "Langfuse project secret key (from Cloud dashboard, required when enable_langfuse=true)"
  type        = string
  sensitive   = true
  default     = ""
}

# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default = {
    project     = "agent-red"
    owner       = "remaker-digital"
    environment = "production"
    managed_by  = "terraform"
  }
}
