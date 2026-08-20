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
  # Required — provide via .tfvars (do not hardcode personal email)
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
# Alerts — app-scoped alerts removed (S251), infrastructure alerts restored
# ---------------------------------------------------------------------------
#
# App-scoped alerts (1, 2, 3, 5) were removed because they reference
# container apps which are CI/CD-managed, not Terraform-managed.
# Preserved in git history (commit prior to S251).
#
# Cosmos throttling alert (4) restored below — it depends only on the
# Cosmos data source, not on container apps. (S251 Codex P2 remediation)

# ---------------------------------------------------------------------------
# Alert 4: Cosmos DB Throttled Requests (429s) — RESTORED
# ---------------------------------------------------------------------------
#
# Fires when Cosmos DB returns throttled (429) responses, indicating
# RU exhaustion on the serverless account. This causes read/write
# failures across all tenants. Does NOT depend on container apps.

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
# Outputs
# ---------------------------------------------------------------------------

output "monitoring_configuration" {
  description = "Azure Monitor alert configuration summary"
  value = {
    enabled     = var.enable_monitoring_alerts
    alert_email = var.enable_monitoring_alerts ? var.alert_email : "disabled"
    alert_rules = var.enable_monitoring_alerts ? [
      "cosmos-db-throttling (Sev2, standalone — no app dependency)",
    ] : []
    estimated_cost = "$0.10/month"
  }
}
