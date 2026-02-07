# Agent Red Customer Experience — Azure Monitor Alert Rules
#
# Automated alerting for the sole operator. Sends email notifications
# when critical system conditions are detected.
#
# Alert Rules:
#   1. API Gateway 5xx error rate (> 5 errors in 5 minutes)
#   2. API Gateway P95 latency (> 3,000ms)
#   3. Container App replica restarts (> 3 in 15 minutes)
#   4. Cosmos DB throttled requests (429s — RU exhaustion)
#   5. Container App health probe failures
#
# Cost: ~$0.10/alert rule/month = ~$0.50/month total
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "enable_monitoring_alerts" {
  description = "Enable Azure Monitor alert rules and action group"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
  default     = "mike@remakerdigital.com"
}

# ---------------------------------------------------------------------------
# Action Group — Email notification target
# ---------------------------------------------------------------------------

resource "azurerm_monitor_action_group" "owner_alerts" {
  count = var.enable_monitoring_alerts ? 1 : 0

  name                = "agentred-owner-alerts"
  resource_group_name = var.resource_group_name
  short_name          = "ar-owner"

  email_receiver {
    name                    = "owner"
    email_address           = var.alert_email
    use_common_alert_schema = true
  }

  tags = var.tags
}

# ---------------------------------------------------------------------------
# Alert 1: API Gateway 5xx Errors (> 5 in 5 minutes)
# ---------------------------------------------------------------------------
#
# Fires when the API Gateway returns more than 5 server errors (HTTP 5xx)
# within a 5-minute window. Indicates a code bug, downstream service
# failure, or infrastructure issue requiring immediate attention.

resource "azurerm_monitor_metric_alert" "api_gateway_5xx" {
  count = var.enable_monitoring_alerts ? 1 : 0

  name                = "agentred-api-gateway-5xx-errors"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_container_app.apps["api-gateway"].id]
  description         = "API Gateway is returning server errors (HTTP 5xx). Check application logs for root cause."
  severity            = 1 # Sev1 — requires prompt attention
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "Requests"
    aggregation      = "Count"
    operator         = "GreaterThan"
    threshold        = 5

    dimension {
      name     = "statusCodeCategory"
      operator = "Include"
      values   = ["5xx"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.owner_alerts[0].id
  }

  tags = merge(var.tags, {
    alert_type = "error-rate"
    component  = "api-gateway"
  })
}

# ---------------------------------------------------------------------------
# Alert 2: API Gateway Response Latency P95 > 3,000ms
# ---------------------------------------------------------------------------
#
# Fires when the 95th percentile response time exceeds 3,000ms
# (SLA commitment: P95 < 2,000ms; alert at 3,000ms gives headroom
# before SLA breach). Indicates slow pipeline stages, Azure OpenAI
# throttling, or Cosmos DB contention.

resource "azurerm_monitor_metric_alert" "api_gateway_latency" {
  count = var.enable_monitoring_alerts ? 1 : 0

  name                = "agentred-api-gateway-high-latency"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_container_app.apps["api-gateway"].id]
  description         = "API Gateway P95 latency exceeds 3s. Check Azure OpenAI, Cosmos DB, and pipeline stage timings."
  severity            = 2 # Sev2 — performance degradation
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "RequestDuration"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 3000 # milliseconds
  }

  action {
    action_group_id = azurerm_monitor_action_group.owner_alerts[0].id
  }

  tags = merge(var.tags, {
    alert_type = "latency"
    component  = "api-gateway"
  })
}

# ---------------------------------------------------------------------------
# Alert 3: Container App Replica Restarts (> 3 in 15 minutes)
# ---------------------------------------------------------------------------
#
# Fires when any critical container app restarts more than 3 times in
# 15 minutes. Frequent restarts indicate crash loops (OOM, unhandled
# exceptions, health probe failures).
#
# Note: Only monitors API Gateway — the AGNTCY agent containers have
# ActivationFailed as their expected state (demo mode images restart
# continuously). Adding them would cause constant false positives.

resource "azurerm_monitor_metric_alert" "container_restarts" {
  count = var.enable_monitoring_alerts ? 1 : 0

  name                = "agentred-container-restarts"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_container_app.apps["api-gateway"].id]
  description         = "API Gateway container is restarting frequently. Check application logs for crash cause."
  severity            = 1 # Sev1 — potential outage
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "RestartCount"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 3
  }

  action {
    action_group_id = azurerm_monitor_action_group.owner_alerts[0].id
  }

  tags = merge(var.tags, {
    alert_type = "container-health"
    component  = "api-gateway"
  })
}

# ---------------------------------------------------------------------------
# Alert 4: Cosmos DB Throttled Requests (429s)
# ---------------------------------------------------------------------------
#
# Fires when Cosmos DB returns throttled (429) responses, indicating
# RU exhaustion on the serverless account. This causes read/write
# failures across all tenants.

resource "azurerm_monitor_metric_alert" "cosmos_throttling" {
  count = var.enable_monitoring_alerts ? 1 : 0

  name                = "agentred-cosmos-db-throttling"
  resource_group_name = var.resource_group_name
  scopes              = [data.azurerm_cosmosdb_account.main.id]
  description         = "Cosmos DB is throttling requests (HTTP 429). Review RU consumption and consider query optimization."
  severity            = 2 # Sev2 — degraded performance
  frequency           = "PT5M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.DocumentDB/databaseAccounts"
    metric_name      = "TotalRequests"
    aggregation      = "Count"
    operator         = "GreaterThan"
    threshold        = 0

    dimension {
      name     = "StatusCode"
      operator = "Include"
      values   = ["429"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.owner_alerts[0].id
  }

  tags = merge(var.tags, {
    alert_type = "throttling"
    component  = "cosmos-db"
  })
}

# ---------------------------------------------------------------------------
# Alert 5: API Gateway Replica Count Drops to Zero
# ---------------------------------------------------------------------------
#
# Fires if the API Gateway has zero running replicas — a total outage.
# With min_replicas=2 this should never happen, but monitors for
# platform-level failures (Container App Environment issues, subnet
# exhaustion, ACR pull failures).

resource "azurerm_monitor_metric_alert" "api_gateway_no_replicas" {
  count = var.enable_monitoring_alerts ? 1 : 0

  name                = "agentred-api-gateway-no-replicas"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_container_app.apps["api-gateway"].id]
  description         = "API Gateway has zero running replicas — TOTAL OUTAGE. Check Container App Environment health and ACR image availability."
  severity            = 0 # Sev0 — critical outage
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "Replicas"
    aggregation      = "Maximum"
    operator         = "LessThan"
    threshold        = 1
  }

  action {
    action_group_id = azurerm_monitor_action_group.owner_alerts[0].id
  }

  tags = merge(var.tags, {
    alert_type = "outage"
    component  = "api-gateway"
  })
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "monitoring_configuration" {
  description = "Azure Monitor alert configuration summary"
  value = {
    enabled     = var.enable_monitoring_alerts
    alert_email = var.enable_monitoring_alerts ? var.alert_email : "disabled"
    alert_rules = var.enable_monitoring_alerts ? [
      "api-gateway-5xx-errors (Sev1)",
      "api-gateway-high-latency (Sev2)",
      "container-restarts (Sev1)",
      "cosmos-db-throttling (Sev2)",
      "api-gateway-no-replicas (Sev0)",
    ] : []
    estimated_cost = "$0.50/month"
  }
}
