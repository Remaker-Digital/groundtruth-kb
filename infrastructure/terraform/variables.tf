# Agent Red Customer Engagement — Terraform Variables
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
  default     = "agntcy-prod-rg"
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "eastus2"
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
  default     = "acragntcycsprodrc6vcp.azurecr.io"
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
  default     = "agntcy-cs-prod-vnet"
}

variable "container_apps_subnet_id" {
  description = "Subnet ID for Container Apps (delegated to Microsoft.App/environments)"
  type        = string
}

# ---------------------------------------------------------------------------
# NATS
# ---------------------------------------------------------------------------

variable "nats_url" {
  description = "NATS JetStream URL (internal VNet address)"
  type        = string
  default     = "nats://10.0.1.5:4222"
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
  default     = "agent-red-prod"
}

variable "cosmos_db_account_name" {
  description = "Cosmos DB account name (for data source lookups)"
  type        = string
  default     = "cosmos-agntcy-cs-prod-rc6vcp"
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
  default     = "https://kv-agntcy-cs-prod-rc6vcp.vault.azure.net/"
}

# ---------------------------------------------------------------------------
# Application Insights
# ---------------------------------------------------------------------------

variable "appinsights_connection_string" {
  description = "Application Insights connection string for OpenTelemetry"
  type        = string
  sensitive   = true
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
