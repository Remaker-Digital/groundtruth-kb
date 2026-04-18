# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
GroundTruth KB — D1 Azure Spec Scaffold Templates.

Generates 13 per-category spec skeletons + 1 ADR template spec + 1 verification
plan spec + 1 taxonomy document entry, per the Azure readiness taxonomy at
``docs/reference/azure-readiness-taxonomy.md``.

All specs persist their template markdown in the ``description`` field
(already-accepted kwarg of ``db.insert_spec()``). The taxonomy document uses
``db.insert_document()`` separately, via the mixed-artifact path in
``scaffold_specs()``.

Authoritative source: bridge/gtkb-azure-spec-scaffold-004.md GO.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# 13 per-category spec skeletons (from taxonomy §4)
# ---------------------------------------------------------------------------


def _category_spec(
    category_id: str,
    title: str,
    scope: str,
    taxonomy_section: str,
    subtopics: list[str],
    owner_decisions: list[str],
    assertions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a single category spec dict with taxonomy-aligned description."""
    description_lines = [
        f"# {title}",
        "",
        f"Source: `docs/reference/azure-readiness-taxonomy.md` §{taxonomy_section}",
        "",
        "## Subtopics",
        "",
    ]
    description_lines.extend(f"- {s}" for s in subtopics)
    description_lines.extend(["", "## Owner decisions required", ""])
    description_lines.extend(f"- [ ] {d}" for d in owner_decisions)
    description_lines.extend(["", "## Automatable assertions", ""])
    description_lines.append(
        "See the `assertions` field on this spec for machine-checkable "
        "conditions. An assertion of kind `owner_decision_placeholder` means "
        "the adopter must answer the decision before promoting the spec past "
        "`status='specified'`."
    )
    return {
        "id": category_id,
        "title": title,
        "type": "requirement",
        "status": "specified",
        "section": "azure-enterprise",
        "scope": scope,
        "handle": f"azure-{scope}",
        "description": "\n".join(description_lines),
        "tags": ["azure", "azure-enterprise", scope],
        "assertions": assertions,
        "testability": "automatable",
    }


def _azure_category_templates() -> list[dict[str, Any]]:
    """13 category spec skeletons from taxonomy §4.

    Order matches the taxonomy §4 enumeration. Each spec has:
    - A multi-line markdown description with section headings + subtopics +
      owner decision placeholders + assertion pointers (persists in the
      `description` field).
    - At least one `owner_decision_placeholder` assertion OR one automatable
      assertion, per INSIGHTS Phase 2 verification clause #2.
    """
    return [
        # §4.1 landing-zone / resource-organization
        _category_spec(
            category_id="SPEC-AZURE-LANDING-ZONE-001",
            title="Azure Landing Zone / Resource Organization",
            scope="landing-zone",
            taxonomy_section="4.1",
            subtopics=[
                "Subscription strategy (single, per-environment, per-workload, platform + application)",
                "Management group hierarchy (including 'no hierarchy, documented')",
                "Resource naming convention (prefix/suffix format, abbreviations, casing)",
                "Tagging strategy (required tags, allowed values, enforcement mechanism)",
                "Policy inheritance (Azure Policy baseline, exemption process)",
                "Environment topology (dev / test / stage / prod; count, separation, promotion flow)",
            ],
            owner_decisions=[
                "Choose subscription strategy",
                "Choose management group hierarchy (or document 'no hierarchy')",
                "Define resource naming convention",
                "Define required tags and enforcement mechanism",
                "Define policy baseline and exemption process",
                "Define environment topology and promotion flow",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": (
                        "Landing zone ADR answered "
                        "(subscriptions, management groups, naming, tags, policy, environments)"
                    ),
                },
            ],
        ),
        # §4.2 identity / RBAC
        _category_spec(
            category_id="SPEC-AZURE-IDENTITY-001",
            title="Azure Identity / RBAC",
            scope="identity",
            taxonomy_section="4.2",
            subtopics=[
                "OIDC federated identity for CI/CD (no static AZURE_CREDENTIALS)",
                "Managed identity for workload-to-service authentication",
                "Service-to-service auth model (system-assigned, user-assigned, workload identity, service principal)",
                "Entra ID (Azure AD) integration: tenant selection, directory roles",
                "B2B / B2C model if external users are surfaced",
                "RBAC role design: built-in vs custom roles, least-privilege patterns",
            ],
            owner_decisions=[
                "Confirm OIDC federation for CI/CD (no static secrets)",
                "Choose managed identity strategy",
                "Define service-to-service auth model",
                "Confirm Entra ID tenant and directory roles",
                "Choose B2B vs B2C (or document 'neither applicable')",
                "Define RBAC role assignment pattern",
            ],
            assertions=[
                {
                    "type": "grep_absent",
                    "description": "No static AZURE_CREDENTIALS JSON secret in recommended CI/CD path",
                    "pattern": r"AZURE_CREDENTIALS",
                    "file": ".github/workflows/*.yml",
                },
                {
                    "type": "owner_decision_placeholder",
                    "description": (
                        "Identity/RBAC ADR answered (OIDC, managed identity, service-to-service, Entra, RBAC roles)"
                    ),
                },
            ],
        ),
        # §4.3 tenancy
        _category_spec(
            category_id="SPEC-AZURE-TENANCY-001",
            title="Azure Tenancy / Isolation",
            scope="tenancy",
            taxonomy_section="4.3",
            subtopics=[
                "Tenant definition (what constitutes a tenant for this product)",
                "Isolation model: pooled, siloed, or hybrid",
                "Tenant lifecycle: onboarding, suspension, offboarding, data export, deletion",
                "Data partitioning: schema, table, row, container, database",
                "Cross-tenant authorization boundary (how A cannot access B)",
            ],
            owner_decisions=[
                "Define what a 'tenant' is for this product",
                "Choose isolation model (pooled / siloed / hybrid)",
                "Document tenant lifecycle flows",
                "Define data partitioning pattern",
                "Define cross-tenant authorization test strategy",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": "Tenancy ADR answered with cross-tenant isolation test referenced",
                },
            ],
        ),
        # §4.4 cost
        _category_spec(
            category_id="SPEC-AZURE-COST-001",
            title="Azure Cost / FinOps",
            scope="cost",
            taxonomy_section="4.4",
            subtopics=[
                "Budgets per subscription / environment / tenant",
                "Tag hygiene (required tags enforced by policy or equivalent assertion)",
                "Per-tenant cost attribution",
                "FinOps review cadence (who reviews, how often, budget-breach response)",
                "Reservation / savings plan strategy (or documented decision not to)",
            ],
            owner_decisions=[
                "Define budget per subscription / environment / tenant",
                "Define required cost tags + enforcement mechanism",
                "Define per-tenant cost attribution approach",
                "Define FinOps review cadence + breach response owner",
                "Choose reservation/savings strategy (or document decision not to)",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": "Cost/FinOps ADR answered (budgets, tags, attribution, review cadence)",
                },
            ],
        ),
        # §4.5 compliance / audit / security posture
        _category_spec(
            category_id="SPEC-AZURE-COMPLIANCE-001",
            title="Azure Compliance / Audit / Security Posture",
            scope="compliance",
            taxonomy_section="4.5",
            subtopics=[
                "SOC 2-aligned control baseline (access reviews, logging, change management)",
                "Audit trail retention and export",
                "Data boundary: residency, cross-border transfer controls, subprocessor list",
                "Threat modeling per major component",
                "Defender for Cloud enablement (or explicit waiver ADR)",
                "Secret rotation schedule and exception process",
                "Vulnerability management (scans, patch SLAs, CVE response)",
            ],
            owner_decisions=[
                "Choose control baseline (SOC 2, HIPAA, PCI-DSS, FedRAMP, or none with rationale)",
                "Define audit trail retention period",
                "Define data residency + cross-border transfer policy",
                "Commit to per-component threat model documents",
                "Choose Defender for Cloud enablement (or waiver)",
                "Define secret rotation schedule",
                "Define vulnerability management process",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": "Compliance baseline ADR answered + audit retention + threat model linked",
                },
            ],
        ),
        # §4.6 networking
        _category_spec(
            category_id="SPEC-AZURE-NETWORKING-001",
            title="Azure Networking",
            scope="networking",
            taxonomy_section="4.6",
            subtopics=[
                "Private endpoints for data-plane services (Storage, Cosmos, Key Vault, ACR)",
                "WAF in front of public endpoints",
                "DDoS protection tier (basic vs standard)",
                "Egress controls (firewall, NAT gateway, UDRs)",
                "Service-mesh (if applicable) or documented decision not to use one",
                "VNet topology (hub-and-spoke, single VNet with subnets, etc.)",
            ],
            owner_decisions=[
                "Choose private-endpoint strategy for data-plane services",
                "Choose WAF policy for public endpoints",
                "Choose DDoS protection tier",
                "Choose egress control mechanism",
                "Choose service mesh posture (or document none)",
                "Choose VNet topology",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": "Networking ADR answered (private endpoints, WAF, DDoS, egress, topology)",
                },
            ],
        ),
        # §4.7 CI/CD
        _category_spec(
            category_id="SPEC-AZURE-CICD-001",
            title="Azure CI/CD",
            scope="cicd",
            taxonomy_section="4.7",
            subtopics=[
                "OIDC federation to Azure (no AZURE_CREDENTIALS JSON secret)",
                "IaC validation (Terraform / Bicep plan, format, security scan)",
                "Environment approval gates (staging → production requires human approval)",
                "Drift detection (periodic plan vs deployed state)",
                "Deploy evidence artifacts (image digest, IaC plan hash, assertion result, owner approval link)",
            ],
            owner_decisions=[
                "Confirm OIDC federation configured (or plan for it)",
                "Define IaC validation gates in CI",
                "Define environment approval flow",
                "Define drift detection schedule",
                "Define deploy evidence bundle contents",
            ],
            assertions=[
                {
                    "type": "grep_absent",
                    "description": "No AZURE_CREDENTIALS secret reference in workflows",
                    "pattern": r"AZURE_CREDENTIALS",
                    "file": ".github/workflows/*.yml",
                },
                {
                    "type": "owner_decision_placeholder",
                    "description": "CI/CD ADR answered (OIDC, IaC validation, approvals, drift, evidence)",
                },
            ],
        ),
        # §4.8 observability
        _category_spec(
            category_id="SPEC-AZURE-OBSERVABILITY-001",
            title="Azure Observability",
            scope="observability",
            taxonomy_section="4.8",
            subtopics=[
                "Azure Monitor workspace + retention",
                "Application Insights (connection string, sampling policy)",
                "OpenTelemetry traces (SDKs, exporters, context propagation)",
                "Per-tenant log view (security team can answer 'show me tenant X activity')",
                "SLO tracking (availability, latency, error budget)",
                "Alert routing (on-call schedule, paging integration)",
            ],
            owner_decisions=[
                "Choose Azure Monitor workspace + retention period",
                "Choose Application Insights sampling policy",
                "Choose OpenTelemetry SDK + exporter set",
                "Define per-tenant log view query",
                "Define SLO set and error-budget policy",
                "Define alert routing + on-call paging integration",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": "Observability ADR answered (monitor, App Insights, OTel, SLOs, alerts)",
                },
            ],
        ),
        # §4.9 compute
        _category_spec(
            category_id="SPEC-AZURE-COMPUTE-001",
            title="Azure Compute",
            scope="compute",
            taxonomy_section="4.9",
            subtopics=[
                "Compute target decision: Azure Container Apps, AKS, App Service, or Functions",
                "Decision criteria: expected scale, stateful vs stateless, multi-region, team experience",
                "Autoscaling model (replicas, rules, scale-to-zero)",
                "Health probes (readiness, liveness)",
                "Image supply chain (ACR vs GHCR; signing; scanning)",
            ],
            owner_decisions=[
                "Choose compute target (Container Apps / AKS / App Service / Functions)",
                "Document decision rationale (scale, state, region, ops experience)",
                "Define autoscaling rules",
                "Define health probe pattern",
                "Define image supply chain",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": (
                        "Compute target ADR answered + autoscaling + health probes + image supply chain documented"
                    ),
                },
            ],
        ),
        # §4.10 data / storage
        _category_spec(
            category_id="SPEC-AZURE-DATA-001",
            title="Azure Data / Storage",
            scope="data",
            taxonomy_section="4.10",
            subtopics=[
                "Tenant partitioning model in storage (schema, table, row, container, database)",
                "Retention policy per data class",
                "Backup schedule + restore test cadence",
                "Encryption at rest (Microsoft-managed vs customer-managed keys)",
                "Cross-region replication (or documented single-region decision)",
            ],
            owner_decisions=[
                "Choose tenant partitioning pattern in storage",
                "Define retention policy per data class",
                "Define backup schedule + restore test cadence",
                "Choose encryption-at-rest key strategy",
                "Choose cross-region replication (or document single-region)",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": (
                        "Data/storage ADR answered (partitioning, retention, backups, encryption, replication)"
                    ),
                },
            ],
        ),
        # §4.11 secrets / Key Vault
        _category_spec(
            category_id="SPEC-AZURE-SECRETS-001",
            title="Azure Secrets / Key Vault",
            scope="secrets",
            taxonomy_section="4.11",
            subtopics=[
                "Key Vault reference pattern (app reads from KV via managed identity)",
                "Key Vault RBAC (Key Vault Secrets User for workload identity)",
                "Secret rotation schedule + automation",
                "Emergency secret-revoke runbook",
                "Separation: per-environment vs shared vaults",
            ],
            owner_decisions=[
                "Confirm Key Vault reference pattern (no plaintext in app config)",
                "Define Key Vault RBAC assignments",
                "Define secret rotation schedule and automation",
                "Document emergency secret-revoke runbook",
                "Choose per-environment or shared Key Vault topology",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": "Secrets ADR answered (KV reference pattern, RBAC, rotation, revoke, topology)",
                },
            ],
        ),
        # §4.12 DR / reliability
        _category_spec(
            category_id="SPEC-AZURE-DR-001",
            title="Azure DR / Reliability",
            scope="dr",
            taxonomy_section="4.12",
            subtopics=[
                "RPO/RTO per critical workflow",
                "Backup + restore evidence cadence",
                "IaC-for-DR (infrastructure defined in code so DR rebuild is reproducible)",
                "DR drill schedule + owner",
                "Incident response runbook",
            ],
            owner_decisions=[
                "Define RPO/RTO per critical workflow",
                "Define backup/restore evidence cadence",
                "Commit to IaC-for-DR (all infra defined in code)",
                "Define DR drill schedule and responsible owner",
                "Document incident response runbook",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": (
                        "DR/reliability ADR answered (RPO/RTO, backups, IaC-for-DR, drill schedule, runbook)"
                    ),
                },
            ],
        ),
        # §4.13 doctor / verification
        _category_spec(
            category_id="SPEC-AZURE-DOCTOR-001",
            title="Azure Doctor / Verification",
            scope="doctor",
            taxonomy_section="4.13",
            subtopics=[
                "Offline doctor: runs without Azure API calls; checks specs, ADRs, CI workflows, assertions",
                "Live doctor: explicit --live opt-in; calls Azure APIs to compare declared vs deployed",
                "Result schema (per-check status, evidence pointers, timestamp)",
                "Integration with CI (fail-build on critical-check regression)",
                "Owner review cadence for offline + live results",
            ],
            owner_decisions=[
                "Confirm offline doctor scope (which categories covered)",
                "Confirm live doctor opt-in threshold (when --live is required)",
                "Define result schema and retention",
                "Define CI integration + fail-build policy",
                "Define owner review cadence for doctor output",
            ],
            assertions=[
                {
                    "type": "owner_decision_placeholder",
                    "description": (
                        "Doctor/verification ADR answered (offline/live scope, schema, CI integration, review cadence)"
                    ),
                },
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# ADR template spec (reusable template shape per taxonomy §5)
# ---------------------------------------------------------------------------


def _azure_adr_template_spec() -> dict[str, Any]:
    """The reusable ADR template for per-category Azure decisions.

    Registered as type='architecture_decision' per taxonomy §5.
    Instance ADRs (actual owner decisions) are deferred to D2.
    """
    description_lines = [
        "# Azure Category ADR — Reusable Template Shape",
        "",
        "Source: `docs/reference/azure-readiness-taxonomy.md` §5",
        "",
        "Reusable template for per-category Azure architecture decisions.",
        "Adopters copy this shape when answering any of the 13 category ADRs",
        "required by the `enterprise-ready` readiness tier.",
        "",
        "## Template structure",
        "",
        "Every instance ADR derived from this template MUST include the",
        "following sections:",
        "",
        "### Context",
        "- What problem is this decision resolving?",
        "- Which readiness tier requires it (production-candidate / enterprise-ready / regulated-enterprise)?",
        "- Which taxonomy category (one of the 13 §4.N categories)?",
        "",
        "### Decision",
        "- The single named choice (e.g., 'Container Apps', 'pooled multi-tenant').",
        "- Not a menu of options — the actual pick.",
        "",
        "### Alternatives considered",
        "- At least one explicitly rejected alternative + why rejected.",
        "- Empty 'none considered' is acceptable only for trivial decisions;",
        "  otherwise the review gate should fail.",
        "",
        "### Consequences",
        "- Positive (what this unlocks or simplifies).",
        "- Negative (what this constrains, costs, or makes harder).",
        "- Reversibility note (easy to change later? what would trigger revisit?).",
        "",
        "### Verification method",
        "- How the instance ADR is machine-verifiable (assertion, file presence, doctor check).",
        "- Link to the category's `SPEC-AZURE-*-001` spec if applicable.",
        "",
        "### Owner decision placeholder",
        "- `- [ ] Decision recorded by: <owner>`",
        "- `- [ ] Decision date: <YYYY-MM-DD>`",
        "- `- [ ] Verification passes: <offline-doctor-result-link>`",
        "",
        "## Usage",
        "",
        "D2 (`gtkb-azure-adr-template-activation`) will provide the workflow",
        "that materializes instance ADRs from this template + the assertion",
        "harness that verifies answers.",
    ]
    return {
        "id": "ADR-TEMPLATE-AZURE-CATEGORY-DECISION",
        "title": "Azure Category ADR — Reusable Template Shape",
        "type": "architecture_decision",
        "status": "specified",
        "section": "azure-enterprise",
        "scope": "adr-template",
        "handle": "azure-adr-category-template",
        "description": "\n".join(description_lines),
        "tags": ["azure", "azure-enterprise", "adr-template"],
        "assertions": [
            {
                "type": "template",
                "description": (
                    "This spec is a TEMPLATE; instance ADRs per category are answered separately (D2 scope)."
                ),
            },
        ],
        "testability": "automatable",
    }


# ---------------------------------------------------------------------------
# Verification plan spec (from taxonomy §6 doctor skeleton)
# ---------------------------------------------------------------------------


def _azure_verification_plan_spec() -> dict[str, Any]:
    """The verification plan spec (offline/live doctor skeleton)."""
    description_lines = [
        "# Azure Readiness Verification Plan",
        "",
        "Source: `docs/reference/azure-readiness-taxonomy.md` §6",
        "",
        "Defines the shape of `gt project doctor --readiness azure-enterprise`",
        "output + the category-to-verification-mode mapping. Implementation",
        "deferred to D5 (`gtkb-azure-doctor-offline`) and D6",
        "(`gtkb-azure-doctor-live`); this spec documents the target contract.",
        "",
        "## Offline mode",
        "",
        "Runs without calling Azure APIs. Checks:",
        "- Spec coverage: all 13 category specs exist (this D1 bridge populates them).",
        "- Assertion presence: every spec has at least one assertion or owner-decision placeholder.",
        "- ADR coverage: per-category instance ADRs recorded (D2 activates the workflow).",
        "- Workflow scan: no `AZURE_CREDENTIALS` JSON secret in CI; OIDC configured.",
        "- IaC text scan: references Key Vault for secret reads; no plaintext in app config.",
        "",
        "## Live mode (explicit --live opt-in)",
        "",
        "Calls Azure APIs (via the adopter's own configured credentials). Checks:",
        "- Tags present on resources per landing zone spec.",
        "- Role assignments match RBAC spec.",
        "- Private endpoints deployed per networking spec.",
        "- Diagnostic settings configured per observability spec.",
        "",
        "## Category to verification mode mapping",
        "",
        "(from taxonomy §4.0.1 Category-to-Evidence matrix)",
        "",
        "| Category | Offline evidence | Live evidence |",
        "|----------|------------------|----------------|",
        "| landing-zone | file/assertion scan | tag/policy check |",
        "| identity | workflow scan | Azure role assignment check |",
        "| tenancy | test/spec linkage | cross-tenant assertion results |",
        "| cost | tag assertion | budget check |",
        "| compliance | spec coverage | audit artifact presence |",
        "| networking | IaC scan | live resource check |",
        "| cicd | workflow parse + forbidden-secret scan | — |",
        "| observability | config scan | App Insights/Log Analytics check |",
        "| compute | IaC/workflow scan | deployment health check |",
        "| data | spec/assertion scan | backup setting check |",
        "| secrets | IaC scan | Key Vault RBAC check |",
        "| dr | artifact scan | restore evidence check |",
        "| doctor | unit tests + output validation | — |",
        "",
        "## Result schema (to be finalized by D5/D6)",
        "",
        "Each check returns: `{ check_id, category, status (pass/fail/warn), evidence, timestamp }`.",
        "",
        "## Owner decisions required",
        "",
        "- [ ] Confirm offline scope covers all 13 categories (yes, per taxonomy; this spec).",
        "- [ ] Confirm live opt-in threshold (explicit --live flag; no implicit API calls).",
        "- [ ] Define result retention + owner review cadence.",
    ]
    return {
        "id": "SPEC-AZURE-READINESS-VERIFICATION",
        "title": "Azure Readiness Verification Plan",
        "type": "requirement",
        "status": "specified",
        "section": "azure-enterprise",
        "scope": "verification",
        "handle": "azure-verification",
        "description": "\n".join(description_lines),
        "tags": ["azure", "azure-enterprise", "verification", "doctor"],
        "assertions": [
            {
                "type": "owner_decision_placeholder",
                "description": "Verification scope confirmed + result retention policy defined",
            },
        ],
        "testability": "automatable",
    }


# ---------------------------------------------------------------------------
# Taxonomy document entry (consumed via db.insert_document())
# ---------------------------------------------------------------------------


def _azure_taxonomy_document() -> dict[str, Any]:
    """The taxonomy document registration.

    Fields match ``db.insert_document()`` signature:
        id, title, category, status, content (optional), tags (optional),
        source_path (optional)

    This dict is consumed via a DIFFERENT code path than spec templates
    (see scaffold_specs() mixed-artifact branch). Do not pass this to
    db.insert_spec().
    """
    return {
        "id": "DOC-AZURE-READINESS-TAXONOMY",
        "title": "Azure Enterprise Readiness Taxonomy",
        "category": "taxonomy",
        "status": "current",
        "source_path": "docs/reference/azure-readiness-taxonomy.md",
        "tags": ["azure", "azure-enterprise", "taxonomy", "readiness"],
    }


# ---------------------------------------------------------------------------
# Public registry (consumed by spec_scaffold.scaffold_specs())
# ---------------------------------------------------------------------------


def azure_spec_templates() -> list[dict[str, Any]]:
    """All 15 Azure-enterprise SPEC templates: 13 categories + 1 ADR + 1 verification.

    Returns dicts shaped for ``db.insert_spec()``. Does NOT include the
    taxonomy document (that's a DIFFERENT artifact type; see
    ``azure_taxonomy_document()``).
    """
    specs: list[dict[str, Any]] = []
    specs.extend(_azure_category_templates())
    specs.append(_azure_adr_template_spec())
    specs.append(_azure_verification_plan_spec())
    return specs


def azure_taxonomy_document() -> dict[str, Any]:
    """The single Azure-enterprise DOCUMENT template (consumed via insert_document())."""
    return _azure_taxonomy_document()


# ---------------------------------------------------------------------------
# Stable golden IDs (for regression tests)
# ---------------------------------------------------------------------------


AZURE_CATEGORY_SPEC_IDS: tuple[str, ...] = (
    "SPEC-AZURE-LANDING-ZONE-001",
    "SPEC-AZURE-IDENTITY-001",
    "SPEC-AZURE-TENANCY-001",
    "SPEC-AZURE-COST-001",
    "SPEC-AZURE-COMPLIANCE-001",
    "SPEC-AZURE-NETWORKING-001",
    "SPEC-AZURE-CICD-001",
    "SPEC-AZURE-OBSERVABILITY-001",
    "SPEC-AZURE-COMPUTE-001",
    "SPEC-AZURE-DATA-001",
    "SPEC-AZURE-SECRETS-001",
    "SPEC-AZURE-DR-001",
    "SPEC-AZURE-DOCTOR-001",
)


AZURE_ADR_TEMPLATE_SPEC_ID: str = "ADR-TEMPLATE-AZURE-CATEGORY-DECISION"


AZURE_VERIFICATION_SPEC_ID: str = "SPEC-AZURE-READINESS-VERIFICATION"


AZURE_TAXONOMY_DOC_ID: str = "DOC-AZURE-READINESS-TAXONOMY"


AZURE_ALL_SPEC_IDS: tuple[str, ...] = AZURE_CATEGORY_SPEC_IDS + (AZURE_ADR_TEMPLATE_SPEC_ID, AZURE_VERIFICATION_SPEC_ID)
