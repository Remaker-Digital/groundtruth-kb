NEW

# D3 — GT-KB Azure IaC Skeleton Templates (Terraform)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Backlog Slot:** D3 per `bridge/post-phase-a-prioritization-003.md:179-180` and owner work-through
**Owner decision:** DELIB-0827 — Terraform only (Bicep out of scope), parallel with D4
**Dependencies satisfied:** Azure taxonomy VERIFIED ✅; D1 (gtkb-azure-spec-scaffold) VERIFIED ✅ `c561da8`; D2 (gtkb-azure-adr-template-activation) VERIFIED ✅ `92615e8`.

## Scope

Add Terraform skeleton templates for the `azure-enterprise` profile that
adopters receive when they run `gt project init --profile azure-enterprise`
(or upgrade to that profile). Templates cover the 13 taxonomy categories
from D1 at the **skeleton** level — structure + commented-out placeholders +
adopter-decision markers. Templates do NOT encode a specific Azure
subscription, tenant, or customer-specific values.

## Template Tree (proposed)

```
templates/iac/azure/
├── README.md                      # Explains structure + adopter workflow
├── main.tf                        # Top-level module wiring (resource_group + 13 module calls)
├── variables.tf                   # Top-level variables (subscription_id, location, environment, tags)
├── outputs.tf                     # Top-level outputs (resource_group name, key outputs per module)
├── terraform.tfvars.example       # Example values; adopter copies to terraform.tfvars
├── providers.tf                   # azurerm + azuread provider version pins + backend config stub
└── modules/
    ├── landing-zone/              # Category 4.1 — resource-organization (RG, naming, tags)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── identity/                  # Category 4.2 — RBAC (managed identities, role assignments)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── tenancy/                   # Category 4.3 — (tenant isolation model placeholder)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── cost/                      # Category 4.4 — budgets + cost alerts
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── compliance/                # Category 4.5 — audit/security posture (Defender, Policy)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── networking/                # Category 4.6 — VNet, NSG, private endpoints
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── cicd/                      # Category 4.7 — (OIDC federated-identity placeholder; wiring is D4 scope)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── observability/             # Category 4.8 — Log Analytics, App Insights, alerts
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── compute/                   # Category 4.9 — Container Apps / AKS / App Service (adopter picks)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── data/                      # Category 4.10 — Cosmos / SQL / Storage
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── secrets/                   # Category 4.11 — Key Vault + access policies
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── dr/                        # Category 4.12 — DR / reliability (backup vaults, geo-redundancy)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── doctor/                    # Category 4.13 — verification hooks (stubs; detailed in D5)
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

**Total: 14 files at top level + 13 × 3 = 39 module files = 53 Terraform files.**

## Content Shape (per module)

Each module's `main.tf` is a **skeleton** — structure + commented-out
example blocks + explicit `TODO: <adopter-decision>` markers referencing
the corresponding ADR-Azure-NN from D2. Adopters uncomment + fill in values.

Example: `modules/landing-zone/main.tf`:

```hcl
# landing-zone module — Category 4.1 per docs/reference/azure-readiness-taxonomy.md
#
# ADR reference: ADR-Azure-landing-zone (from D2 templates)
#
# Required adopter decisions (answered in ADR-Azure-landing-zone):
# 1. Resource group naming convention (rg-{app}-{env}-{region} or other)
# 2. Region strategy (single-region, multi-region active-passive, active-active)
# 3. Tag taxonomy (required tags: Environment, Owner, CostCenter, DataClassification)
# 4. Subscription model (single prod, prod+nonprod, hub-spoke)

# -----------------------------------------------------------------------------
# Resource Group (REQUIRED)
# -----------------------------------------------------------------------------
# TODO: adopter — set name + location per ADR-Azure-landing-zone §Decision.
# resource "azurerm_resource_group" "main" {
#   name     = var.resource_group_name
#   location = var.location
#   tags     = var.required_tags
# }

# -----------------------------------------------------------------------------
# Management group assignment (OPTIONAL — enterprise-ready tier)
# -----------------------------------------------------------------------------
# TODO: adopter — if using management groups, assign RG under the correct MG.
# data "azurerm_management_group" "parent" { name = var.management_group_id }
```

Other modules follow the same skeleton pattern:
- Commented-out resource blocks with example arguments
- Clear TODO markers tied to ADR instance answers
- Required vs Optional annotation per tier (`production-candidate`, `enterprise-ready`, `regulated-enterprise`)
- No hardcoded subscription/tenant IDs

## Registry Integration

All 53 files added as `class_="file"` artifacts in
`templates/managed-artifacts.toml` with:
- `initial_profiles = ["azure-enterprise"]`
- `managed_profiles = []` (skeletons — adopter-customized once landed; upgrade should NOT overwrite)
- `ownership = "gt-kb-managed"`
- `upgrade_policy = "skip-if-exists"` (new schema value — see §Schema extension below)
- `adopter_divergence_policy = "silent"` (adopter changes are expected)

### Schema extension: new `upgrade_policy = "skip-if-exists"` value

Current `upgrade_policy` values (from ownership.py): `overwrite`,
`structured-merge`, `scaffold-only`. None fits "skeleton file the adopter
will heavily customize."

New value: `skip-if-exists`. Semantics:
- Scaffold: copy file from template if target doesn't exist.
- Upgrade: NO-OP if file exists; only creates if missing (e.g., adopter
  deleted it). Never overwrites.
- Doctor: informs adopter if file is missing.

This mirrors the existing `scaffold-only` policy but with a clearer
intent marker for "IaC adopter-owned" files.

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `templates/iac/azure/*.tf` (53 new files across 14 directories) | New skeleton content | +~2,000 lines |
| `templates/iac/azure/README.md` (new) | Adopter-facing documentation | +~150 lines |
| `templates/iac/azure/terraform.tfvars.example` (new) | Example variables | +~50 lines |
| `templates/managed-artifacts.toml` | Add 54 new file-artifact entries | +~750 lines |
| `src/groundtruth_kb/project/ownership.py` | Add `"skip-if-exists"` to `upgrade_policy` literal type | +~3 lines |
| `src/groundtruth_kb/project/upgrade.py` | Handle `skip-if-exists` in `_plan_file_actions` | +~20 lines |
| `tests/test_managed_registry.py` | Update invariants: new iac file count + new upgrade_policy value | +~10 / -~5 lines |
| `tests/test_azure_iac_scaffold.py` (new) | Integration test: `gt scaffold iac --profile azure-enterprise` produces full tree, correct file-paths, correct content markers | +~200 lines |
| `docs/reference/azure-iac-templates.md` (new) | Adopter documentation for how to consume the templates | +~200 lines |

**Total: ~56 new files + 4 modified files. Approx +3,400 lines, -5 lines.**

## Non-Scope (explicit exclusions)

- **Bicep templates** — owner explicitly chose Terraform-only (DELIB-0827).
- **Azure DevOps pipelines** — D4 scope (GitHub Actions only per DELIB-0827).
- **Specific subscription/tenant/customer values** — adopters fill these in.
- **Runtime Terraform execution / `terraform apply` tooling** — GT-KB doesn't execute IaC; adopters do.
- **Terraform backend configuration beyond stub** — adopters choose their backend (azurerm, remote state, etc.).
- **Bicep-compat or multi-tool interop shims** — owner decision is Terraform-only.
- **D4 CI/CD workflow templates** — separate bridge (parallel).
- **D5 Azure doctor offline/live checks** — depends on D3+D4 completion.

## Verification Plan

```text
# Pre-apply: confirm current azure-enterprise scaffold is empty
$ python -c "from groundtruth_kb.project.managed_registry import artifacts_for_scaffold; print(len(list(artifacts_for_scaffold('azure-enterprise'))))"
0

# Run scoped + registry tests
$ python -m pytest tests/test_managed_registry.py tests/test_azure_iac_scaffold.py -q
# Expect: registry invariants updated (class counts + 54 new file artifacts); new scaffold test 5-10 passes

# Run full suite
$ python -m pytest -q
# Expect: 1515 → 1525+ (+10 from new test file). No regressions.

# mypy strict (ownership + upgrade changes)
$ python -m mypy --strict src/groundtruth_kb/project/ownership.py src/groundtruth_kb/project/upgrade.py
Success: no issues found in 2 source files

# ruff check + format
$ python -m ruff check src/groundtruth_kb/project/ownership.py src/groundtruth_kb/project/upgrade.py tests/test_azure_iac_scaffold.py
All checks passed!

# End-to-end scaffold test
$ cd /tmp/scratch && gt project init test-project --profile azure-enterprise
$ ls test-project/iac/azure/
# Expect: full 14-dir tree with 53 .tf files

# Terraform validate (should pass because skeletons are syntactically valid, even with all resources commented)
$ cd test-project/iac/azure && terraform init -backend=false && terraform validate
Success! The configuration is valid.
```

## Implementation Sequence

1. Design + write the 14-directory template tree (53 .tf files + README + tfvars example).
2. Add `skip-if-exists` upgrade-policy value to `ownership.py` and handler in `upgrade.py`.
3. Add 54 new file-artifact registry entries in `templates/managed-artifacts.toml` (profile=azure-enterprise).
4. Update test_managed_registry.py invariants.
5. Write `tests/test_azure_iac_scaffold.py` — end-to-end scaffold test.
6. Write `docs/reference/azure-iac-templates.md`.
7. Run scoped + full pytest; mypy --strict; ruff check + format.
8. `terraform init -backend=false && terraform validate` against the generated scaffold tree.
9. Commit on `groundtruth-kb/main`: `feat(azure): D3 — Terraform IaC skeleton templates for azure-enterprise profile`.
10. Push to `origin/main` (GT-KB fast-iterate pattern per `feedback_iterate_fast_on_main.md`).
11. File post-impl report.

## Prior Deliberations

- DELIB-0827 (owner_conversation, 2026-04-18): D3=Terraform-only + D4=GHA-only + parallel.
- `bridge/gtkb-azure-spec-scaffold-006.md` (D1 VERIFIED): 13 category specs.
- `bridge/gtkb-azure-adr-template-activation-004.md` (D2 VERIFIED): 13 ADR instance skeletons.
- `docs/reference/azure-readiness-taxonomy.md` §4 (category catalog 4.1-4.13).

## Owner Decisions Required

None. Defaults from DELIB-0827 + taxonomy doc + D1/D2 patterns pin all choices.

## Requested Verdict

**GO** to implement §1-§6 per the sequence, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
