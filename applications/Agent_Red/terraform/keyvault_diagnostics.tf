# Agent Red Customer Experience — Key Vault Diagnostic Logging
#
# S254 hardening: enables audit logging on the Key Vault so that
# key/secret CRUD operations (create, delete, purge, recover) are
# traceable. Added after a CMK purge incident where the deletion
# could not be attributed because no diagnostic logs existed.
#
# Logs are sent to the existing Log Analytics workspace.
# Cost: minimal — Key Vault audit events are low-volume.
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

resource "azurerm_monitor_diagnostic_setting" "keyvault_audit" {
  name                       = "keyvault-audit-logs"
  target_resource_id         = data.azurerm_key_vault.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "AuditEvent"
  }

  metric {
    category = "AllMetrics"
    enabled  = false
  }
}
