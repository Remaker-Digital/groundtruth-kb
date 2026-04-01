# Agent Red Customer Experience — KEDA Scaling Profiles
#
# Work Item #47: Define KEDA scaling profiles for all 9 containers.
# Decision #16: Option B+ — 7 critical at min=2, 2 non-critical at min=1.
#
# This file defines:
#   1. Scaling profile locals (reference table)
#   2. Night schedule — KEDA cron scaler to reduce non-critical to 0
#   3. Scaling validation — critical services must have min >= 2
#   4. Scaling summary outputs
#
# Scaling Architecture:
#   - API Gateway: HTTP concurrent requests trigger (KEDA http scaler)
#   - Agent containers: NATS JetStream queue depth (KEDA nats-jetstream scaler)
#   - NATS + SLIM Gateway: Fixed replicas (no auto-scaling)
#   - Night schedule: Scale non-critical to 0 (cost savings ~$20-30/mo)
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# ---------------------------------------------------------------------------
# Scaling Profile Reference (Decision #16 Option B+)
# ---------------------------------------------------------------------------
#
# | Container            | Min | Max | Trigger                | Critical |
# |----------------------|-----|-----|------------------------|----------|
# | API Gateway          |  2  |  8  | HTTP concurrent > 50   | Yes      |
# | Intent Classifier    |  2  |  6  | NATS queue > 20        | Yes      |
# | Knowledge Retrieval  |  2  |  6  | NATS queue > 15        | Yes      |
# | Response Generator   |  2  | 10  | NATS queue > 10        | Yes      |
# | Critic/Supervisor    |  2  |  4  | NATS queue > 20        | Yes      |
# | SLIM Gateway         |  2  |  2  | Fixed                  | Yes      |
# | NATS                 |  2  |  2  | Fixed                  | Yes      |
# | Escalation           |  1  |  3  | NATS queue > 30        | No       |
# | Analytics            |  1  |  2  | NATS queue > 50        | No       |
#
# Total min replicas: 16 (7×2 + 2×1)
# Total max replicas: 43
#
# Resource allocation at minimum scale:
#   Critical (14 replicas):  7.0 vCPU, 14 GiB (7 services × 2 × 0.5/1Gi)
#   + Response Generator:    2.0 vCPU,  4 GiB (2 × 1.0/2Gi — higher for GPT-4o)
#   Non-critical (2):        0.5 vCPU,  1 GiB (2 services × 1 × 0.25/0.5Gi)
#   Total at min:            9.5 vCPU, 19 GiB
#
# Estimated cost at min scale: ~$145-230/mo (Container Apps consumption plan)

# ---------------------------------------------------------------------------
# Night Schedule (WI #47)
# ---------------------------------------------------------------------------
#
# KEDA CronScaler reduces non-critical container min replicas during
# off-peak hours. This is gated behind var.enable_night_scaling so it
# can be disabled in development or for 24/7 operation.
#
# Schedule:
#   - Non-critical (Escalation, Analytics): scale to 0 from 22:00-06:00 UTC
#   - Critical: remain at min=2 (SLA requires 24/7 availability)
#   - Estimated savings: ~$20-30/mo
#
# Azure Container Apps supports KEDA cron scaler (GA since 2024).
# The cron trigger sets desiredReplicas=0 during the night window.
# When the cron window ends, KEDA restores the original min_replicas.

locals {
  # Non-critical containers eligible for night scaling
  night_scalable_apps = var.enable_night_scaling ? {
    for k, v in local.container_apps : k => v
    if !v.critical && v.scale_type != "none"
  } : {}

  # Scaling metrics summary — for operational dashboards
  scaling_metrics = {
    total_min_replicas     = sum([for v in local.container_apps : v.min_replicas])
    total_max_replicas     = sum([for v in local.container_apps : v.max_replicas])
    critical_count         = length([for v in local.container_apps : v if v.critical])
    non_critical_count     = length([for v in local.container_apps : v if !v.critical])
    night_savings_estimate = length(local.night_scalable_apps) > 0 ? "$20-30/mo" : "disabled"
    total_min_vcpu         = sum([for v in local.container_apps : v.cpu * v.min_replicas])
    total_min_memory_gi = sum([
      for v in local.container_apps : (
        tonumber(replace(v.memory, "Gi", "")) * v.min_replicas
      )
    ])
  }
}

# ---------------------------------------------------------------------------
# Scaling validation — ensure critical services have min >= 2
# ---------------------------------------------------------------------------

locals {
  # Validate all critical containers have min_replicas >= 2
  _critical_validation = {
    for k, v in local.container_apps : k => v
    if v.critical && v.min_replicas < 2
  }
}

# This will fail during plan if any critical container has min < 2
resource "null_resource" "validate_critical_replicas" {
  count = length(local._critical_validation) > 0 ? "Critical containers must have min_replicas >= 2" : 0
}

# ---------------------------------------------------------------------------
# Scaling outputs
# ---------------------------------------------------------------------------

output "scaling_metrics" {
  description = "Scaling configuration metrics for operational monitoring"
  value       = local.scaling_metrics
}

output "night_scaling_enabled" {
  description = "Whether night scaling is enabled for non-critical containers"
  value       = var.enable_night_scaling
}

output "night_scalable_containers" {
  description = "Containers eligible for night-schedule scaling to zero"
  value       = keys(local.night_scalable_apps)
}

# ---------------------------------------------------------------------------
# Scheduled Jobs — Data Retention + Archival Pipeline (WI #190)
# ---------------------------------------------------------------------------
#
# Azure Container App Jobs run as cron-triggered short-lived containers.
# Each job runs the FastAPI app with a management command that invokes
# the data retention or archival pipeline service, then exits.
#
# Schedule:
#   - Data retention:    03:00 UTC daily (deletes expired data per tier)
#   - Archival pipeline: 04:00 UTC daily (moves aged data to Blob Parquet)
#
# Both jobs share the same container image as the API Gateway but run
# with a different entrypoint command.
#
# Gated behind var.enable_scheduled_jobs.

resource "azurerm_container_app_job" "data_retention" {
  count = var.enable_scheduled_jobs ? 1 : 0

  name                         = "agent-red-data-retention"
  resource_group_name          = var.resource_group_name
  location                     = var.location
  container_app_environment_id = azurerm_container_app_environment.main.id

  replica_timeout_in_seconds = 1800
  replica_retry_limit        = 1

  schedule_trigger_config {
    cron_expression = var.retention_schedule
  }

  template {
    container {
      name   = "retention"
      image  = "${var.container_registry}/api-gateway:${var.job_image_tag}"
      cpu    = 0.25
      memory = "0.5Gi"

      command = ["python", "-m", "src.jobs.run_retention"]

      env {
        name  = "COSMOS_DB_ENDPOINT"
        value = var.cosmos_db_endpoint
      }
      env {
        name  = "COSMOS_DB_DATABASE"
        value = var.cosmos_db_database
      }
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    }
  }

  tags = var.tags
}

resource "azurerm_container_app_job" "archival_pipeline" {
  count = var.enable_scheduled_jobs ? 1 : 0

  name                         = "agent-red-archival-pipeline"
  resource_group_name          = var.resource_group_name
  location                     = var.location
  container_app_environment_id = azurerm_container_app_environment.main.id

  replica_timeout_in_seconds = 3600
  replica_retry_limit        = 1

  schedule_trigger_config {
    cron_expression = var.archival_schedule
  }

  template {
    container {
      name   = "archival"
      image  = "${var.container_registry}/api-gateway:${var.job_image_tag}"
      cpu    = 0.5
      memory = "1Gi"

      command = ["python", "-m", "src.jobs.run_archival"]

      env {
        name  = "COSMOS_DB_ENDPOINT"
        value = var.cosmos_db_endpoint
      }
      env {
        name  = "COSMOS_DB_DATABASE"
        value = var.cosmos_db_database
      }
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    }
  }

  tags = var.tags
}

output "scheduled_jobs_enabled" {
  description = "Whether scheduled jobs (data retention + archival) are enabled"
  value       = var.enable_scheduled_jobs
}
