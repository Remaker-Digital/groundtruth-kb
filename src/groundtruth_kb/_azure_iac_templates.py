# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
GroundTruth KB - D3 Azure IaC Template Catalog.

Defines 45 Terraform skeleton file descriptors scaffolded via
``gt scaffold iac --profile azure-enterprise``. Skeletons are adopter-owned;
after first scaffold the adopter uncomments resources and fills in values
per the corresponding ADR-Azure-* instance (from D2).

Authoritative source: bridge/gtkb-azure-iac-skeleton-004.md GO.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from typing import Any

__all__ = ["azure_iac_templates", "AZURE_IAC_EXPECTED_PATHS"]


# ---------------------------------------------------------------------------
# Module catalog — 13 modules, one per Azure readiness taxonomy category
# ---------------------------------------------------------------------------

_MODULE_CATALOG: list[dict[str, str]] = [
    {
        "name": "landing-zone",
        "category": "4.1",
        "adr_handle": "adr-azure-landing-zone",
        "title": "Resource Organization / Landing Zone",
        "purpose": "Resource group hierarchy, naming conventions, and required tags.",
        "example_resource": "azurerm_resource_group",
    },
    {
        "name": "identity",
        "category": "4.2",
        "adr_handle": "adr-azure-identity",
        "title": "Identity / RBAC",
        "purpose": "Managed identities, role assignments, and service principal federation.",
        "example_resource": "azurerm_user_assigned_identity",
    },
    {
        "name": "tenancy",
        "category": "4.3",
        "adr_handle": "adr-azure-tenancy",
        "title": "Tenancy Model",
        "purpose": "Per-tenant isolation boundary (partition-key, container-per-tenant, DB-per-tenant).",
        "example_resource": "azurerm_cosmosdb_sql_container",
    },
    {
        "name": "cost",
        "category": "4.4",
        "adr_handle": "adr-azure-cost",
        "title": "Cost Governance",
        "purpose": "Budgets, cost alerts, and tag-based cost attribution.",
        "example_resource": "azurerm_consumption_budget_subscription",
    },
    {
        "name": "compliance",
        "category": "4.5",
        "adr_handle": "adr-azure-compliance",
        "title": "Compliance / Security Posture",
        "purpose": "Defender for Cloud, Azure Policy, audit log retention.",
        "example_resource": "azurerm_security_center_subscription_pricing",
    },
    {
        "name": "networking",
        "category": "4.6",
        "adr_handle": "adr-azure-networking",
        "title": "Networking",
        "purpose": "VNet, NSG, private endpoints, public/private routing decisions.",
        "example_resource": "azurerm_virtual_network",
    },
    {
        "name": "cicd",
        "category": "4.7",
        "adr_handle": "adr-azure-cicd",
        "title": "CI/CD",
        "purpose": "Federated-identity app registration placeholder (workflows are scaffolded by D4).",
        "example_resource": "azuread_application_federated_identity_credential",
    },
    {
        "name": "observability",
        "category": "4.8",
        "adr_handle": "adr-azure-observability",
        "title": "Observability",
        "purpose": "Log Analytics workspace, Application Insights, diagnostic settings, alerts.",
        "example_resource": "azurerm_log_analytics_workspace",
    },
    {
        "name": "compute",
        "category": "4.9",
        "adr_handle": "adr-azure-compute",
        "title": "Compute",
        "purpose": "Container Apps / AKS / App Service / Functions (adopter picks per ADR).",
        "example_resource": "azurerm_container_app_environment",
    },
    {
        "name": "data",
        "category": "4.10",
        "adr_handle": "adr-azure-data",
        "title": "Data / Storage",
        "purpose": "Cosmos / SQL / Storage with backup + geo-replication + retention.",
        "example_resource": "azurerm_cosmosdb_account",
    },
    {
        "name": "secrets",
        "category": "4.11",
        "adr_handle": "adr-azure-secrets",
        "title": "Secrets / Key Vault",
        "purpose": "Key Vault, access policies, customer-managed keys vs Microsoft-managed.",
        "example_resource": "azurerm_key_vault",
    },
    {
        "name": "dr",
        "category": "4.12",
        "adr_handle": "adr-azure-dr",
        "title": "DR / Reliability",
        "purpose": "Backup vaults, geo-redundancy, tested restore cadence, RPO/RTO.",
        "example_resource": "azurerm_recovery_services_vault",
    },
    {
        "name": "doctor",
        "category": "4.13",
        "adr_handle": "adr-azure-doctor",
        "title": "Doctor / Verification",
        "purpose": "Stubs for post-deployment verification hooks (detailed implementation is D5).",
        "example_resource": "# No Azure resources; doctor logic lives in Python",
    },
]


_COPYRIGHT_HEADER = (
    "# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.\n"
    "# Scaffolded by gt scaffold iac --profile azure-enterprise (D3 skeleton).\n"
    "# Adopter-owned; customize per the corresponding ADR-Azure-* instance from D2.\n"
)


# ---------------------------------------------------------------------------
# Template body generators (per-module)
# ---------------------------------------------------------------------------


def _module_main_tf(mod: dict[str, str]) -> str:
    """Build content for modules/<name>/main.tf (Terraform skeleton)."""
    return (
        f"{_COPYRIGHT_HEADER}"
        f"# Module: {mod['title']} (taxonomy category {mod['category']})\n"
        f"# ADR reference: {mod['adr_handle']} (scaffolded by D2)\n"
        f"#\n"
        f"# Purpose: {mod['purpose']}\n"
        f"#\n"
        f"# Required adopter decisions (answered in {mod['adr_handle']}):\n"
        f"#   1. Decision (see ADR \u00a7Decision) - commit to a concrete choice.\n"
        f"#   2. Rationale (see ADR \u00a7Rationale) - document why.\n"
        f"#   3. Rejected alternatives (see ADR \u00a7Rejected alternatives) - record what was weighed.\n"
        f"#\n"
        f"# -----------------------------------------------------------------------------\n"
        f"# Primary resource block (commented-out; uncomment and fill in per ADR)\n"
        f"# -----------------------------------------------------------------------------\n"
        f"# TODO: adopter - uncomment and configure per {mod['adr_handle']} \u00a7Decision.\n"
        f'# resource "{mod["example_resource"]}" "main" {{\n'
        f"#   name                = var.name\n"
        f"#   resource_group_name = var.resource_group_name\n"
        f"#   location            = var.location\n"
        f"#   tags                = var.tags\n"
        f"# }}\n"
    )


def _module_variables_tf(mod: dict[str, str]) -> str:
    """Build content for modules/<name>/variables.tf."""
    return (
        f"{_COPYRIGHT_HEADER}"
        f"# Variables for the {mod['title']} module (taxonomy category {mod['category']}).\n"
        f"# See {mod['adr_handle']} for the adopter decisions that set these values.\n"
        f"\n"
        f'variable "name" {{\n'
        f'  description = "Name for the primary resource. See {mod["adr_handle"]} \u00a7Decision."\n'
        f"  type        = string\n"
        f"}}\n"
        f"\n"
        f'variable "resource_group_name" {{\n'
        f'  description = "Resource group for this module\'s resources. Typically from the landing-zone module."\n'
        f"  type        = string\n"
        f"}}\n"
        f"\n"
        f'variable "location" {{\n'
        f'  description = "Azure region. See adr-azure-landing-zone for region strategy."\n'
        f"  type        = string\n"
        f"}}\n"
        f"\n"
        f'variable "tags" {{\n'
        f'  description = "Required tags per adr-azure-landing-zone tag taxonomy."\n'
        f"  type        = map(string)\n"
        f"  default     = {{}}\n"
        f"}}\n"
    )


def _module_outputs_tf(mod: dict[str, str]) -> str:
    """Build content for modules/<name>/outputs.tf."""
    return (
        f"{_COPYRIGHT_HEADER}"
        f"# Outputs for the {mod['title']} module (taxonomy category {mod['category']}).\n"
        f"# Uncomment matching outputs as resources are provisioned.\n"
        f"\n"
        f"# TODO: adopter - uncomment when primary resource is configured.\n"
        f'# output "id" {{\n'
        f'#   description = "Resource ID of the primary {mod["title"]} resource."\n'
        f"#   value       = {mod['example_resource']}.main.id\n"
        f"# }}\n"
        f"\n"
        f'# output "name" {{\n'
        f'#   description = "Name of the primary resource (for cross-module references)."\n'
        f"#   value       = {mod['example_resource']}.main.name\n"
        f"# }}\n"
    )


# ---------------------------------------------------------------------------
# Top-level file contents
# ---------------------------------------------------------------------------


_TOP_MAIN_TF = f"""{_COPYRIGHT_HEADER}# Top-level Terraform configuration for the Azure-enterprise profile.
# Wires together 13 per-category modules (one per taxonomy category).
# Adopters uncomment and fill in module calls as they configure each category
# per the corresponding ADR-Azure-* instance.

# -----------------------------------------------------------------------------
# Landing zone (Category 4.1) - the root resource group + tags + region.
# -----------------------------------------------------------------------------
# module "landing_zone" {{
#   source              = "./modules/landing-zone"
#   name                = "rg-app-prod"      # Set per adr-azure-landing-zone \u00a7Decision.
#   resource_group_name = "rg-app-prod"
#   location            = "eastus2"
#   tags                = var.required_tags
# }}

# Other modules follow the same shape. Uncomment and configure per ADR:
# - modules/identity         (Category 4.2)
# - modules/tenancy          (Category 4.3)
# - modules/cost             (Category 4.4)
# - modules/compliance       (Category 4.5)
# - modules/networking       (Category 4.6)
# - modules/cicd             (Category 4.7; D4 provides workflows)
# - modules/observability    (Category 4.8)
# - modules/compute          (Category 4.9)
# - modules/data             (Category 4.10)
# - modules/secrets          (Category 4.11)
# - modules/dr               (Category 4.12)
# - modules/doctor           (Category 4.13; D5 provides verification logic)
"""


_TOP_VARIABLES_TF = f"""{_COPYRIGHT_HEADER}# Top-level variables shared across modules.
# Set via terraform.tfvars (see terraform.tfvars.example) or environment variables.

variable "subscription_id" {{
  description = "Azure subscription ID to deploy into."
  type        = string
}}

variable "tenant_id" {{
  description = "Azure AD tenant ID."
  type        = string
}}

variable "location" {{
  description = "Default Azure region. See adr-azure-landing-zone for region strategy."
  type        = string
  default     = "eastus2"
}}

variable "environment" {{
  description = "Deployment environment (dev, staging, prod, etc.)."
  type        = string
}}

variable "required_tags" {{
  description = "Required tags per adr-azure-landing-zone tag taxonomy."
  type        = map(string)
  default     = {{}}
}}
"""


_TOP_OUTPUTS_TF = f"""{_COPYRIGHT_HEADER}# Top-level outputs expose key module outputs for downstream tooling.
# Uncomment matching outputs as modules are provisioned.

# output "resource_group_id" {{
#   description = "ID of the root resource group from landing-zone module."
#   value       = module.landing_zone.id
# }}

# output "key_vault_uri" {{
#   description = "Key Vault URI for secret references."
#   value       = module.secrets.vault_uri
# }}
"""


_TOP_PROVIDERS_TF = f"""{_COPYRIGHT_HEADER}# Provider pins and backend configuration stub.
# Adopters configure their Terraform state backend (azurerm, remote state, etc.).

terraform {{
  required_version = ">= 1.9.0"

  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }}
    azuread = {{
      source  = "hashicorp/azuread"
      version = "~> 2.50"
    }}
  }}

  # TODO: adopter - configure Terraform backend per adr-azure-landing-zone.
  # Example (Azure Storage backend):
  # backend "azurerm" {{
  #   resource_group_name  = "rg-tfstate-prod"
  #   storage_account_name = "tfstateprod"
  #   container_name       = "tfstate"
  #   key                  = "app.tfstate"
  # }}
}}

provider "azurerm" {{
  features {{}}
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}}

provider "azuread" {{
  tenant_id = var.tenant_id
}}
"""


_TOP_README_MD = """# Azure Enterprise - Terraform Skeleton

Scaffolded by `gt scaffold iac --profile azure-enterprise` (D3).

## Overview

This tree contains Terraform skeleton files for the 13 Azure readiness
taxonomy categories. Each `modules/<name>/` directory corresponds to a
category in `docs/reference/azure-readiness-taxonomy.md` \u00a74 and pairs
one-to-one with an ADR-Azure-* instance scaffolded by
`gt scaffold adrs --profile azure-enterprise` (D2).

## Adopter workflow

1. Complete the ADR-Azure-* instances (from D2): answer the Decision,
   Rationale, and Rejected alternatives sections.
2. Copy `terraform.tfvars.example` to `terraform.tfvars` and fill in values.
3. Configure the Terraform backend in `providers.tf` (see TODO marker).
4. For each module you need: uncomment the resource blocks in
   `modules/<name>/main.tf`, fill in values per the corresponding ADR,
   uncomment outputs in `modules/<name>/outputs.tf`, and wire the module
   call in the top-level `main.tf`.
5. Run `terraform init` then `terraform plan` and `terraform apply`.

## Adopter-owned files

After scaffolding, these files belong to the adopter. Re-running
`gt scaffold iac` skips any file that already exists (never overwrites).
If you want to reset a module to skeleton state, delete the file first
and re-run scaffold.

## Relationship to other tracks

- **D2 ADR instances** (`gt scaffold adrs`): capture the decisions these
  skeletons codify.
- **D4 CI/CD workflows** (`gt scaffold cicd`): GitHub Actions that validate,
  plan, and apply this Terraform tree.
- **D5 doctor** (future): runs offline and live checks against this
  configuration.

## Validation

Skeleton files are valid Terraform syntax (all resources are commented
out). After copying:

    terraform init -backend=false
    terraform validate

should succeed. Once you uncomment resources, `terraform plan` will show
what will be created against your subscription.
"""


_TOP_TFVARS_EXAMPLE = """# Example values - copy to terraform.tfvars and fill in real values.
# Never commit terraform.tfvars (it will contain subscription/tenant IDs).

# Adopter: replace each <PLACEHOLDER> with the real value from the Azure
# Portal (Subscription blade > Overview, and Azure AD tenant properties).
# Values are strings; the file is a Terraform .tfvars file.

# subscription_id = "<YOUR-SUBSCRIPTION-ID-FROM-AZURE-PORTAL>"
# tenant_id       = "<YOUR-TENANT-ID-FROM-AZURE-AD-PROPERTIES>"
# location        = "eastus2"
# environment     = "prod"

# required_tags = {
#   Environment        = "prod"
#   Owner              = "platform@example.com"
#   CostCenter         = "0000"
#   DataClassification = "internal"
# }
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def azure_iac_templates() -> list[dict[str, Any]]:
    """Return all 45 Azure IaC skeleton templates as path/content descriptors.

    Mirrors the D1 `_azure_spec_templates()` / D2 `azure_adr_instance_templates()`
    pattern. Each descriptor has:
        - target_path: path relative to the scaffold root (e.g. "iac/azure/main.tf")
        - content: full file content as a string

    Total count: 6 top-level files + 13 modules x 3 files = 45 descriptors.
    """
    descriptors: list[dict[str, Any]] = []

    # 6 top-level files
    top = [
        ("iac/azure/main.tf", _TOP_MAIN_TF),
        ("iac/azure/variables.tf", _TOP_VARIABLES_TF),
        ("iac/azure/outputs.tf", _TOP_OUTPUTS_TF),
        ("iac/azure/providers.tf", _TOP_PROVIDERS_TF),
        ("iac/azure/README.md", _TOP_README_MD),
        ("iac/azure/terraform.tfvars.example", _TOP_TFVARS_EXAMPLE),
    ]
    descriptors.extend({"target_path": path, "content": content} for path, content in top)

    # 13 modules x 3 files each = 39 files
    for mod in _MODULE_CATALOG:
        base = f"iac/azure/modules/{mod['name']}"
        descriptors.append({"target_path": f"{base}/main.tf", "content": _module_main_tf(mod)})
        descriptors.append({"target_path": f"{base}/variables.tf", "content": _module_variables_tf(mod)})
        descriptors.append({"target_path": f"{base}/outputs.tf", "content": _module_outputs_tf(mod)})

    return descriptors


AZURE_IAC_EXPECTED_PATHS: tuple[str, ...] = tuple(d["target_path"] for d in azure_iac_templates())
"""Authoritative 45-path inventory for the Azure IaC scaffold.

Used by both the scaffold orchestrator and the test suite; a single
source prevents count drift between runtime and invariants."""
