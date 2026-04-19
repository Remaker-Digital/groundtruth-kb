# Azure IaC Templates (D3)

Reference for the Terraform skeleton tree scaffolded by
`gt scaffold iac --profile azure-enterprise`.

## What it produces

45 Terraform skeleton files under `iac/azure/`:

- **Top-level (6 files):**
  - `main.tf` — module-call wiring (commented-out; adopter uncomments per ADR)
  - `variables.tf` — shared input variables (subscription_id, tenant_id, location, environment, required_tags)
  - `outputs.tf` — top-level outputs (commented; adopter uncomments as modules provision)
  - `providers.tf` — provider pins (azurerm ~> 3.110, azuread ~> 2.50) + backend stub
  - `README.md` — adopter workflow overview
  - `terraform.tfvars.example` — example values (never commit the non-example version)

- **Modules (13 × 3 = 39 files):**
  one directory per Azure readiness taxonomy category (§4 of
  `azure-readiness-taxonomy.md`), each with `main.tf` / `variables.tf`
  / `outputs.tf`.

| Module | Category | ADR handle (from D2) |
|---|---|---|
| `landing-zone` | 4.1 | `adr-azure-landing-zone` |
| `identity` | 4.2 | `adr-azure-identity` |
| `tenancy` | 4.3 | `adr-azure-tenancy` |
| `cost` | 4.4 | `adr-azure-cost` |
| `compliance` | 4.5 | `adr-azure-compliance` |
| `networking` | 4.6 | `adr-azure-networking` |
| `cicd` | 4.7 | `adr-azure-cicd` |
| `observability` | 4.8 | `adr-azure-observability` |
| `compute` | 4.9 | `adr-azure-compute` |
| `data` | 4.10 | `adr-azure-data` |
| `secrets` | 4.11 | `adr-azure-secrets` |
| `dr` | 4.12 | `adr-azure-dr` |
| `doctor` | 4.13 | `adr-azure-doctor` |

## Lifecycle: scaffold-once, adopter-owned

Scaffold is one-shot. Existing files are **skipped, never overwritten**.
If you want to reset a file to skeleton state:

    rm iac/azure/main.tf
    gt scaffold iac --profile azure-enterprise --apply

This makes adopter customizations safe. Re-running the command after
every GT-KB release is safe — your customizations survive.

## Usage

### Dry run (default)

    gt scaffold iac --profile azure-enterprise

Reports what would be generated or skipped. No files written.

### Apply

    gt scaffold iac --profile azure-enterprise --apply

Writes the 45-file tree under the current directory (or use
`--target-dir <path>`).

### Target elsewhere

    gt scaffold iac --profile azure-enterprise --apply --target-dir /path/to/project-root

## Adopter workflow

1. Scaffold the tree: `gt scaffold iac --profile azure-enterprise --apply`.
2. Complete the ADR-Azure-* instances via `gt scaffold adrs --profile
   azure-enterprise` (D2): answer the `<<ADOPTER-ANSWER-REQUIRED>>`
   placeholders for Decision, Rationale, and Rejected alternatives.
3. Copy `iac/azure/terraform.tfvars.example` to `iac/azure/terraform.tfvars`
   and fill in `<YOUR-SUBSCRIPTION-ID>` and `<YOUR-TENANT-ID>` placeholders.
4. Configure the Terraform backend in `iac/azure/providers.tf` (TODO marker
   points to adr-azure-landing-zone for the state-storage decision).
5. For each module you need:
   - Uncomment the resource block in `modules/<name>/main.tf`.
   - Adjust inputs per the corresponding ADR's `§Decision`.
   - Uncomment matching outputs in `modules/<name>/outputs.tf`.
   - Uncomment the `module "X"` call in the top-level `main.tf` and wire inputs.
6. Validate locally: `terraform init && terraform plan`.
7. Commit the customized tree + terraform.tfvars (never commit
   terraform.tfvars — contains subscription IDs; use .gitignore).

## Validation

All 45 skeleton files are valid Terraform HCL (resources commented out).
After scaffolding:

    cd iac/azure
    terraform init -backend=false
    terraform validate

both succeed. Once you uncomment resources, `terraform plan` will show
what will be created against your configured subscription.

## Relationship to other tracks

- **D1 spec scaffold** (`gt scaffold specs --profile azure-enterprise`):
  13 category specs + ADR template spec + verification-plan spec. The
  IaC modules here pair one-to-one with those category specs.
- **D2 ADR instance scaffold** (`gt scaffold adrs --profile
  azure-enterprise`): 13 ADR skeletons with the 9-section template.
  Each IaC module references its ADR handle via `TODO: adopter` marker.
- **D4 CI/CD templates** (future): GitHub Actions workflows that run
  `terraform validate`/`plan`/`apply` against this tree with OIDC
  federation + environment approval gates + drift detection.
- **D5 doctor** (future): offline + live verification checks against
  this Terraform configuration and the deployed Azure resources.

## Non-scope

- **Bicep templates** — D3 is Terraform-only per owner decision.
- **Specific Azure subscription/tenant values** — adopter-owned.
- **Running Terraform for you** — GT-KB doesn't execute `terraform apply`;
  adopters do (or their CI does via D4 workflows).
- **Upgrade/drift repair** — scaffold is one-shot; adopter owns after
  first write. Future GT-KB releases will not overwrite your files.

## Implementation

- Template catalog: `src/groundtruth_kb/_azure_iac_templates.py`
- Scaffold orchestrator: `src/groundtruth_kb/iac_scaffold.py`
- CLI command: `src/groundtruth_kb/cli.py::scaffold_iac_cmd`
- Tests: `tests/test_azure_iac_scaffold.py` (16 tests)
- Bridge: `bridge/gtkb-azure-iac-skeleton-004.md` (GO) and `-003.md` (REVISED-1)
