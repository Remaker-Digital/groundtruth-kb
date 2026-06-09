"""Container App scaling baseline taxonomy and configuration.

This module is the single source of truth for which Azure Container Apps
require scaling enforcement and what their min/max replica baselines are.
Both the smoke deploy path (`scripts/deploy.py`) and the canonical
production deploy path (`scripts/deploy_pipeline.py`) import from here.

Source of truth for production SCALING_CONFIG values:
`infrastructure/terraform/main.tf` container_apps block (Decision #16
Option B+). When Terraform changes, update SCALING_CONFIG in the same
PR — `tests/unit/test_deploy_scaling.py` reconciles against `main.tf`.

Created 2026-04-25 (S308) per
`bridge/canonical-deploy-pipeline-scaling-enforcement-007.md` to close
the WI-3031 canonical-path scaling-enforcement gap. Symbols here were
moved from `scripts/deploy.py` lines 35-100 (pre-S308). The smoke path
re-exports them so existing in-tree callers keep working byte-identically.

Excluded from SCALING_CONFIG:
- NATS — Terraform-managed, not deploy-managed.
- Test host containers — no Decision #16 baseline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

# Azure resource group for all Agent Red container apps.
RESOURCE_GROUP = "Agent-Red"

# Environment-specific gateway container app names. Staging and production
# share most apps (per ADR-002); only the gateway differs by environment.
CONTAINER_APPS: dict[str, str] = {
    "staging": "agent-red-staging",
    "production": "agent-red-api-gateway",
}

# Per-agent containers (ADR-002). Deployed alongside the gateway in both
# environments. Maps ACR repo name → Azure Container App name.
AGENT_CONTAINER_APPS: dict[str, str] = {
    "agent-intent-classifier": "agent-red-intent-classifier",
    "agent-knowledge-retrieval": "agent-red-knowledge-retrieval",
    "agent-response-generator": "agent-red-response-generator",
    "agent-escalation-handler": "agent-red-escalation-handler",
    "agent-analytics-collector": "agent-red-analytics-collector",
    "agent-critic-supervisor": "agent-red-critic-supervisor",
}

# Infrastructure containers (non-agent services supporting transport).
# NATS uses a public image and is managed by Terraform, not deploy code.
INFRA_CONTAINER_APPS: dict[str, str] = {
    "slim-gateway": "agent-red-slim",
}

# Scaling baseline per Container App (WI-3171, extends WI-3156).
# Production values mirror infrastructure/terraform/main.tf.
SCALING_CONFIG: dict[str, dict[str, int]] = {
    # --- Gateways (environment-specific) -----------------------------------
    "agent-red-api-gateway": {"min_replicas": 2, "max_replicas": 8},
    "agent-red-staging": {"min_replicas": 1, "max_replicas": 5},
    # --- Critical agent containers -----------------------------------------
    "agent-red-intent-classifier": {"min_replicas": 2, "max_replicas": 6},
    "agent-red-knowledge-retrieval": {"min_replicas": 2, "max_replicas": 6},
    "agent-red-response-generator": {"min_replicas": 2, "max_replicas": 10},
    "agent-red-critic-supervisor": {"min_replicas": 2, "max_replicas": 4},
    # --- Non-critical agent containers -------------------------------------
    "agent-red-escalation-handler": {"min_replicas": 1, "max_replicas": 3},
    "agent-red-analytics-collector": {"min_replicas": 1, "max_replicas": 2},
    # --- Critical infrastructure -------------------------------------------
    "agent-red-slim": {"min_replicas": 2, "max_replicas": 2},
}


def get_scaling_targets(environment: str) -> list[str]:
    """Return the ordered list of container-app names requiring scaling enforcement.

    The list is the env-specific gateway followed by every shared agent
    container, then every shared infra container. NATS and test-host
    containers are intentionally excluded (NATS is Terraform-managed; the
    test host has no Decision #16 baseline).

    Used by both the smoke deploy path and the canonical production path
    so they enforce scaling against the identical target set.
    """
    return [
        CONTAINER_APPS[environment],
        *AGENT_CONTAINER_APPS.values(),
        *INFRA_CONTAINER_APPS.values(),
    ]
