# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
GroundTruth KB — D2 Azure ADR Instance Templates.

Generates 13 instance ADR skeletons, one per Azure readiness taxonomy category.
Each skeleton carries the 9-question template from taxonomy §5.1 with
<<ADOPTER-ANSWER-REQUIRED>> placeholders in the sections that require owner input.

Paired one-to-one with the D1 category specs in _azure_spec_templates.py.

Authoritative source: bridge/gtkb-azure-adr-template-activation-002.md GO.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


#: Placeholder marker for adopter-owner answers. The D2 harness
#: (`verify_azure_adrs()` in `adr_harness.py`) treats any section containing
#: this string as `unanswered`.
ADR_PLACEHOLDER: str = "<<ADOPTER-ANSWER-REQUIRED>>"


#: The 9 section headings required by the taxonomy §5.1 template shape.
#: Order matches the taxonomy's numbered list.
ADR_REQUIRED_HEADINGS: tuple[str, ...] = (
    "Context",
    "Decision scope",
    "Options considered",
    "Decision",
    "Rationale",
    "Rejected alternatives",
    "Consequences",
    "Assertions",
    "Review trigger",
)


#: The 3 sections whose content must be non-empty AND non-placeholder for
#: an instance ADR to be classified as `answered` by the harness.
#: Per Codex F4 binding condition.
ADR_MANDATORY_OWNER_ANSWER_HEADINGS: tuple[str, ...] = (
    "Decision",
    "Rationale",
    "Rejected alternatives",
)


# ---------------------------------------------------------------------------
# Per-category ADR skeleton builder
# ---------------------------------------------------------------------------


def _instance_adr(
    adr_id: str,
    title: str,
    scope: str,
    category_spec_id: str,
    context_hint: str,
    decision_scope_hint: str,
) -> dict[str, Any]:
    """Build a single instance ADR skeleton with the 9-section template body."""
    lines = [
        f"# {title}",
        "",
        (
            f"Paired with D1 category spec `{category_spec_id}`. Template shape from "
            f"`ADR-TEMPLATE-AZURE-CATEGORY-DECISION` (taxonomy §5)."
        ),
        "",
        "## Context",
        "",
        context_hint,
        "",
        "## Decision scope",
        "",
        decision_scope_hint,
        "",
        "## Options considered",
        "",
        (
            "List at least two concrete options with enough detail to evaluate. "
            "Include cost, operational, and security trade-offs where relevant."
        ),
        "",
        "## Decision",
        "",
        ADR_PLACEHOLDER,
        "",
        "## Rationale",
        "",
        ADR_PLACEHOLDER,
        "",
        "## Rejected alternatives",
        "",
        ADR_PLACEHOLDER,
        "",
        "## Consequences",
        "",
        ("Describe what this decision unlocks, what it constrains, and which downstream ADRs or specs are affected."),
        "",
        "## Assertions",
        "",
        (
            "Name the grep / glob / file-exists / absence assertions that verify this "
            "ADR is still honored. These assertions may be added to the paired "
            f"`{category_spec_id}` spec or to a downstream doctor check."
        ),
        "",
        "## Review trigger",
        "",
        (
            "What would cause this ADR to be reopened? Examples: scale shift, "
            "regulatory change, cost breach, tenancy-model change."
        ),
        "",
    ]
    return {
        "id": adr_id,
        "title": title,
        "type": "architecture_decision",
        "status": "specified",
        "section": "azure-enterprise",
        "scope": scope,
        "handle": f"azure-adr-{scope}",
        "description": "\n".join(lines),
        "tags": ["azure", "azure-enterprise", "adr-instance", scope],
        "assertions": [
            {
                "type": "owner_decision_placeholder",
                "description": (
                    f"Instance ADR for {title} must be answered before the paired "
                    f"{category_spec_id} spec can be promoted past status='specified'."
                ),
            },
        ],
        "testability": "observable",
    }


def _azure_adr_instance_templates() -> list[dict[str, Any]]:
    """13 instance ADR skeletons, one per taxonomy category.

    Each skeleton is ready for adopter-owner to fill in the Decision,
    Rationale, and Rejected alternatives sections (required for the
    D2 harness to classify as `answered`).
    """
    return [
        # §4.1 landing-zone
        _instance_adr(
            adr_id="ADR-AZURE-LANDING-ZONE-001",
            title="Azure Landing Zone / Resource Organization",
            scope="landing-zone",
            category_spec_id="SPEC-AZURE-LANDING-ZONE-001",
            context_hint=(
                "We need to declare how Azure resources are organized (subscriptions, "
                "management groups, naming, tagging, policy, environment topology). "
                "Without this decision, resources can be created anywhere and "
                "governance/cost-attribution/isolation become effectively impossible."
            ),
            decision_scope_hint=(
                "Covers subscription strategy, management group hierarchy, naming "
                "convention, tagging strategy, policy inheritance, and environment "
                "topology (taxonomy §4.1 subtopics)."
            ),
        ),
        # §4.2 identity / RBAC
        _instance_adr(
            adr_id="ADR-AZURE-IDENTITY-001",
            title="Azure Identity / RBAC",
            scope="identity",
            category_spec_id="SPEC-AZURE-IDENTITY-001",
            context_hint=(
                "We need to declare how identity is managed in Azure: OIDC federation "
                "for CI/CD, managed identity for workloads, service-to-service auth, "
                "Entra ID integration, B2B/B2C posture, and RBAC role design."
            ),
            decision_scope_hint=(
                "Covers OIDC federation, managed identity, service-to-service auth, "
                "Entra ID tenant selection, B2B/B2C (if applicable), and RBAC role "
                "assignment (taxonomy §4.2 subtopics)."
            ),
        ),
        # §4.3 tenancy
        _instance_adr(
            adr_id="ADR-AZURE-TENANCY-001",
            title="Azure Tenancy / Isolation",
            scope="tenancy",
            category_spec_id="SPEC-AZURE-TENANCY-001",
            context_hint=(
                "We need to declare what a tenant is for this product, what isolation "
                "model applies, and how cross-tenant boundary is enforced. SaaS "
                "readiness is not only deployment — a tenancy ADR without isolation "
                "tests is not enterprise-ready."
            ),
            decision_scope_hint=(
                "Covers tenant definition, isolation model (pooled / siloed / hybrid), "
                "tenant lifecycle, data partitioning, and cross-tenant authorization "
                "boundary (taxonomy §4.3 subtopics)."
            ),
        ),
        # §4.4 cost
        _instance_adr(
            adr_id="ADR-AZURE-COST-001",
            title="Azure Cost / FinOps",
            scope="cost",
            category_spec_id="SPEC-AZURE-COST-001",
            context_hint=(
                "We need to declare budgets, tag hygiene, per-tenant cost attribution, "
                "FinOps review cadence, and reservation strategy. Enterprise accounts "
                "with a cloud-finance function expect this during procurement."
            ),
            decision_scope_hint=(
                "Covers budgets per subscription/environment/tenant, required tags, "
                "per-tenant cost attribution, FinOps review cadence, and reservation "
                "strategy (taxonomy §4.4 subtopics)."
            ),
        ),
        # §4.5 compliance
        _instance_adr(
            adr_id="ADR-AZURE-COMPLIANCE-001",
            title="Azure Compliance / Audit / Security Posture",
            scope="compliance",
            category_spec_id="SPEC-AZURE-COMPLIANCE-001",
            context_hint=(
                "We need to declare control baseline (SOC 2, HIPAA, PCI-DSS, FedRAMP, "
                "or none with rationale), audit retention, data boundary, threat "
                "modeling cadence, and Defender for Cloud posture."
            ),
            decision_scope_hint=(
                "Covers control baseline, audit retention, data residency, threat "
                "modeling, Defender for Cloud, secret rotation, and vulnerability "
                "management (taxonomy §4.5 subtopics)."
            ),
        ),
        # §4.6 networking
        _instance_adr(
            adr_id="ADR-AZURE-NETWORKING-001",
            title="Azure Networking",
            scope="networking",
            category_spec_id="SPEC-AZURE-NETWORKING-001",
            context_hint=(
                "We need to declare network posture: private endpoints, WAF, DDoS tier, "
                "egress controls, service mesh (or absence), and VNet topology. "
                "Network posture is one of the first items an enterprise security "
                "review raises."
            ),
            decision_scope_hint=(
                "Covers private endpoints, WAF, DDoS tier, egress controls, service "
                "mesh, and VNet topology (taxonomy §4.6 subtopics)."
            ),
        ),
        # §4.7 CI/CD
        _instance_adr(
            adr_id="ADR-AZURE-CICD-001",
            title="Azure CI/CD",
            scope="cicd",
            category_spec_id="SPEC-AZURE-CICD-001",
            context_hint=(
                "We need to declare CI/CD posture: OIDC federation to Azure, IaC "
                "validation gates, environment approval flow, drift detection, and "
                "deploy evidence bundle contents. Auditors routinely ask for this "
                "evidence."
            ),
            decision_scope_hint=(
                "Covers OIDC federation, IaC validation, environment approvals, drift "
                "detection, and deploy evidence artifacts (taxonomy §4.7 subtopics)."
            ),
        ),
        # §4.8 observability
        _instance_adr(
            adr_id="ADR-AZURE-OBSERVABILITY-001",
            title="Azure Observability",
            scope="observability",
            category_spec_id="SPEC-AZURE-OBSERVABILITY-001",
            context_hint=(
                "We need to declare Azure Monitor + App Insights + OpenTelemetry "
                "posture, per-tenant log views, SLO tracking, and alert routing. "
                "Without these, incident response and SLA credits cannot be enforced."
            ),
            decision_scope_hint=(
                "Covers Azure Monitor workspace, App Insights sampling, OpenTelemetry "
                "SDKs, per-tenant log view, SLOs, and alert routing (taxonomy §4.8 "
                "subtopics)."
            ),
        ),
        # §4.9 compute
        _instance_adr(
            adr_id="ADR-AZURE-COMPUTE-001",
            title="Azure Compute",
            scope="compute",
            category_spec_id="SPEC-AZURE-COMPUTE-001",
            context_hint=(
                "We need to declare compute target (Container Apps / AKS / App "
                "Service / Functions), autoscaling rules, health probes, and image "
                "supply chain. Compute target constrains almost every other category."
            ),
            decision_scope_hint=(
                "Covers compute target choice, decision rationale, autoscaling, "
                "health probes, and image supply chain (taxonomy §4.9 subtopics)."
            ),
        ),
        # §4.10 data / storage
        _instance_adr(
            adr_id="ADR-AZURE-DATA-001",
            title="Azure Data / Storage",
            scope="data",
            category_spec_id="SPEC-AZURE-DATA-001",
            context_hint=(
                "We need to declare tenant partitioning in storage, retention policy, "
                "backup/restore cadence, encryption-at-rest strategy, and cross-region "
                "replication."
            ),
            decision_scope_hint=(
                "Covers storage partitioning, retention, backup schedule, encryption "
                "keys, and replication (taxonomy §4.10 subtopics)."
            ),
        ),
        # §4.11 secrets / Key Vault
        _instance_adr(
            adr_id="ADR-AZURE-SECRETS-001",
            title="Azure Secrets / Key Vault",
            scope="secrets",
            category_spec_id="SPEC-AZURE-SECRETS-001",
            context_hint=(
                "We need to declare Key Vault reference pattern, RBAC assignments, "
                "rotation schedule, emergency revoke runbook, and per-environment "
                "vs shared vault topology."
            ),
            decision_scope_hint=(
                "Covers Key Vault reference pattern, RBAC, rotation, emergency "
                "revoke, and vault topology (taxonomy §4.11 subtopics)."
            ),
        ),
        # §4.12 DR / reliability
        _instance_adr(
            adr_id="ADR-AZURE-DR-001",
            title="Azure DR / Reliability",
            scope="dr",
            category_spec_id="SPEC-AZURE-DR-001",
            context_hint=(
                "We need to declare RPO/RTO per critical workflow, backup/restore "
                "evidence cadence, IaC-for-DR commitment, drill schedule, and "
                "incident response runbook."
            ),
            decision_scope_hint=(
                "Covers RPO/RTO, backup/restore, IaC-for-DR, drill schedule, and "
                "incident response runbook (taxonomy §4.12 subtopics)."
            ),
        ),
        # §4.13 doctor / verification
        _instance_adr(
            adr_id="ADR-AZURE-DOCTOR-001",
            title="Azure Doctor / Verification",
            scope="doctor",
            category_spec_id="SPEC-AZURE-DOCTOR-001",
            context_hint=(
                "We need to declare offline doctor scope, live doctor opt-in threshold, "
                "result schema, CI integration, and owner review cadence for doctor "
                "output."
            ),
            decision_scope_hint=(
                "Covers offline doctor scope, live doctor opt-in threshold, result "
                "schema, CI integration, and owner review cadence (taxonomy §4.13 "
                "subtopics)."
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# Public registry
# ---------------------------------------------------------------------------


def azure_adr_instance_templates() -> list[dict[str, Any]]:
    """All 13 Azure-enterprise instance-ADR skeletons (ready for adopter-owner input).

    Paired one-to-one with the 13 D1 category specs in _azure_spec_templates.py.
    """
    return _azure_adr_instance_templates()


AZURE_ADR_INSTANCE_IDS: tuple[str, ...] = (
    "ADR-AZURE-LANDING-ZONE-001",
    "ADR-AZURE-IDENTITY-001",
    "ADR-AZURE-TENANCY-001",
    "ADR-AZURE-COST-001",
    "ADR-AZURE-COMPLIANCE-001",
    "ADR-AZURE-NETWORKING-001",
    "ADR-AZURE-CICD-001",
    "ADR-AZURE-OBSERVABILITY-001",
    "ADR-AZURE-COMPUTE-001",
    "ADR-AZURE-DATA-001",
    "ADR-AZURE-SECRETS-001",
    "ADR-AZURE-DR-001",
    "ADR-AZURE-DOCTOR-001",
)
