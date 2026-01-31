# Agent Red Customer Engagement — KEDA Scaling Profiles
#
# Work Item #47: Define KEDA scaling profiles for all 9 containers.
# Decision #16: Option B+ — 7 critical at min=2, 2 non-critical at min=1.
#
# This file defines scaling-related locals and scheduled scaling rules
# that complement the container app definitions in main.tf.
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
#
# ---------------------------------------------------------------------------
# Night Schedule (Phase 2.2 — deferred, design placeholder)
# ---------------------------------------------------------------------------
#
# KEDA CronScaler can reduce min replicas during off-peak hours:
#
#   - Non-critical (Escalation, Analytics): scale to 0 from 22:00-06:00 UTC
#   - Critical: remain at min=2 (SLA requires 24/7 availability)
#   - Estimated savings: ~$20-30/mo
#
# Implementation: Add KEDA cron trigger to escalation + analytics container apps.
# Requires KEDA cron scaler support in Azure Container Apps (GA since 2024).
#
# Example (future):
#   custom_scale_rule {
#     name             = "night-scale-down"
#     custom_rule_type = "cron"
#     metadata = {
#       timezone        = "UTC"
#       start           = "0 22 * * *"
#       end             = "0 6 * * *"
#       desiredReplicas = "0"
#     }
#   }
#
# ---------------------------------------------------------------------------

# Scaling validation — ensure critical services have min >= 2
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
