# Agent Red Customer Experience — Main Terraform Configuration
#
# Provisions the Azure Container Apps environment and all 9 container apps
# with KEDA auto-scaling per Decision #16 (Option B+) and Work Items #47-48.
#
# Architecture:
#   - 7 critical containers at min=2 replicas
#   - 2 non-critical containers at min=1 replica
#   - KEDA scaling: HTTP concurrent (API Gateway), NATS queue depth (agents)
#   - Fail-closed Critic policy (Critic min=2, upgraded to critical)
#
# Usage:
#   cd infrastructure/terraform
#   terraform init
#   terraform plan -var-file="production.tfvars"
#   terraform apply -var-file="production.tfvars"
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
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

  # Prevent replacement when Azure auto-assigns infrastructure_resource_group_name
  lifecycle {
    ignore_changes = [infrastructure_resource_group_name]
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
# Container Apps — 9 services (WI #47-48, Decision #16 Option B+)
# ---------------------------------------------------------------------------

# Shared environment variables for all agent containers
locals {
  shared_env = [
    { name = "ENVIRONMENT", value = var.environment },
    { name = "NATS_URL", value = var.nats_url },
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
      image        = "intent-classifier:v1.1.0-openai"
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
      image        = "knowledge-retrieval:v1.1.1-fix"
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
      image        = "response-generator:v1.1.0-openai"
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
      image        = "critic-supervisor:v1.1.0-openai"
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
      image        = "escalation:v1.1.0-openai"
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
      image        = "analytics:v1.1.0-openai"
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
      port         = 4222
      cpu          = 0.5
      memory       = "1Gi"
      min_replicas = 2
      max_replicas = 2
      critical     = true
      scale_type   = "none"
      scale_rule   = {}
    }
  }
}

# ---------------------------------------------------------------------------
# Container App resources (for_each over the map)
# ---------------------------------------------------------------------------

resource "azurerm_container_app" "apps" {
  for_each = local.container_apps

  name                         = "agent-red-${each.key}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"

  tags = merge(var.tags, {
    component = each.key
    critical  = tostring(each.value.critical)
  })

  # Managed Identity for Key Vault + Cosmos DB access
  identity {
    type = "SystemAssigned"
  }

  # ACR pull
  registry {
    server   = var.container_registry
    identity = "system"
  }

  # Secrets
  secret {
    name  = "appinsights-connection-string"
    value = var.appinsights_connection_string
  }

  template {
    min_replicas = each.value.min_replicas
    max_replicas = each.value.max_replicas

    # WI #59: Connection draining — 60s grace period for zero-downtime deployment
    # Allows in-flight HTTP requests and NATS messages to complete before termination
    revision_suffix = null # Auto-generated by Azure on each deployment

    container {
      name   = each.key
      image  = "${var.container_registry}/${each.value.image}"
      cpu    = each.value.cpu
      memory = each.value.memory

      # Environment variables (shared)
      dynamic "env" {
        for_each = [for e in local.shared_env : e if !contains(keys(e), "secret_name")]
        content {
          name  = env.value.name
          value = env.value.value
        }
      }

      dynamic "env" {
        for_each = [for e in local.shared_env : e if contains(keys(e), "secret_name")]
        content {
          name        = env.value.name
          secret_name = env.value.secret_name
        }
      }

      # Liveness probe (WI #58 — per-container config from dr_security.tf)
      liveness_probe {
        transport = "HTTP"
        port      = lookup(local.health_probes[each.key], "liveness_port", each.value.port)
        path      = lookup(local.health_probes[each.key], "liveness_path", "/health")

        initial_delay           = lookup(local.health_probes[each.key], "initial_delay", 10)
        interval_seconds        = lookup(local.health_probes[each.key], "liveness_period", 30)
        timeout                 = 5
        failure_count_threshold = 3
      }

      # Readiness probe (WI #58 — dependency check, removes from LB on failure)
      readiness_probe {
        transport = "HTTP"
        port      = lookup(local.health_probes[each.key], "readiness_port", each.value.port)
        path      = lookup(local.health_probes[each.key], "readiness_path", "/ready")

        interval_seconds        = lookup(local.health_probes[each.key], "readiness_period", 15)
        timeout                 = 5
        failure_count_threshold = 3
      }
    }

    # ----- KEDA scaling rules (WI #47) -----

    # HTTP concurrent requests trigger (API Gateway only)
    dynamic "http_scale_rule" {
      for_each = each.value.scale_type == "http" ? [1] : []
      content {
        name                = "http-concurrent"
        concurrent_requests = tostring(each.value.scale_rule.concurrent_requests)
      }
    }

    # NATS JetStream queue depth trigger (agent containers)
    dynamic "custom_scale_rule" {
      for_each = each.value.scale_type == "nats" ? [1] : []
      content {
        name             = "nats-queue-depth"
        custom_rule_type = "nats-jetstream"
        metadata = {
          natsServerMonitoringEndpoint = var.nats_monitoring_endpoint
          account                      = "$G"
          stream                       = each.value.scale_rule.consumer_group
          consumer                     = each.value.scale_rule.consumer_group
          lagThreshold                 = tostring(each.value.scale_rule.queue_length)
        }
      }
    }

    # WI #47: Night schedule — scale non-critical to 0 during off-peak hours
    # Enabled only when var.enable_night_scaling is true and container is non-critical
    dynamic "custom_scale_rule" {
      for_each = (
        var.enable_night_scaling &&
        !each.value.critical &&
        each.value.scale_type != "none"
      ) ? [1] : []
      content {
        name             = "night-scale-down"
        custom_rule_type = "cron"
        metadata = {
          timezone        = var.night_scaling_timezone
          start           = var.night_scaling_start
          end             = var.night_scaling_end
          desiredReplicas = "0"
        }
      }
    }
  }

  # Ingress — API Gateway is the only externally exposed container
  dynamic "ingress" {
    for_each = each.key == "api-gateway" ? [1] : []
    content {
      external_enabled = true
      target_port      = each.value.port
      transport        = "auto"

      traffic_weight {
        latest_revision = true
        percentage      = 100
      }
    }
  }

  # Internal TCP ingress for NATS (port 4222) and SLIM Gateway (port 8443)
  dynamic "ingress" {
    for_each = contains(["nats", "slim-gateway"], each.key) ? [1] : []
    content {
      external_enabled = false
      target_port      = each.value.port
      transport        = "tcp"

      traffic_weight {
        latest_revision = true
        percentage      = 100
      }
    }
  }

  # Internal HTTP ingress for agent containers (inter-service communication)
  dynamic "ingress" {
    for_each = !contains(["api-gateway", "slim-gateway", "nats"], each.key) ? [1] : []
    content {
      external_enabled = false
      target_port      = each.value.port

      traffic_weight {
        latest_revision = true
        percentage      = 100
      }
    }
  }
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "container_app_environment_id" {
  description = "Container App Environment ID"
  value       = azurerm_container_app_environment.main.id
}

output "api_gateway_fqdn" {
  description = "API Gateway FQDN (external ingress)"
  value       = try(azurerm_container_app.apps["api-gateway"].ingress[0].fqdn, "not-configured")
}

output "container_app_ids" {
  description = "Map of container app names to their IDs"
  value       = { for k, v in azurerm_container_app.apps : k => v.id }
}

output "managed_identity_principal_ids" {
  description = "System-assigned Managed Identity principal IDs for RBAC assignments"
  value       = { for k, v in azurerm_container_app.apps : k => v.identity[0].principal_id }
}

output "scaling_summary" {
  description = "Scaling configuration summary"
  value = { for k, v in local.container_apps : k => {
    min      = v.min_replicas
    max      = v.max_replicas
    critical = v.critical
    trigger  = v.scale_type
  } }
}
