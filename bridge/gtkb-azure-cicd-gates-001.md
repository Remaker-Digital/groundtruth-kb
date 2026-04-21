NEW

# D4 — GT-KB Azure CI/CD Gates (GitHub Actions)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Backlog Slot:** D4 per `bridge/post-phase-a-prioritization-003.md:179-180` and owner work-through
**Owner decision:** DELIB-0827 — GitHub Actions only (Azure DevOps out of scope), parallel with D3
**Dependencies satisfied:** Azure taxonomy VERIFIED ✅; D1 + D2 VERIFIED ✅.
**Parallel sibling:** D3 `gtkb-azure-iac-skeleton` (same owner decision DELIB, runs concurrently).

## Scope

Add GitHub Actions workflow templates for the `azure-enterprise` profile
covering the CI/CD category (4.7 in the Azure taxonomy):
- OIDC federated identity (no `AZURE_CREDENTIALS` JSON secret)
- IaC validation (terraform fmt/validate/plan + security scan)
- Environment approval gates (staging → production requires human approval)
- Drift detection (periodic plan vs deployed state)
- Deploy evidence artifacts (image digest, IaC plan hash, assertion result, owner approval link)

## Template Tree (proposed)

```
templates/ci/azure/
├── README.md                          # Explains OIDC setup, required secrets/variables, approval gates
├── workflows/
│   ├── azure-oidc-login.yml           # Reusable composite action for federated login
│   ├── iac-validate.yml               # On PR: terraform fmt/init/validate/plan + tfsec security scan
│   ├── iac-apply-staging.yml          # On merge to develop: plan, await approval, apply to staging
│   ├── iac-apply-production.yml       # On release tag: plan, require manual approval, apply to production
│   ├── drift-detection.yml            # Scheduled daily: terraform plan in detect-only mode, alert on drift
│   └── deploy-evidence.yml            # Reusable: capture image digest, plan hash, assertion result, owner approval URL
└── integrations/
    ├── OWNER-APPROVAL.md              # Template for GitHub Environment approval rules setup
    └── federated-identity-setup.md    # Walkthrough: creating Azure AD app registration + federated credential for the repo
```

**Total: 11 new files (1 README + 6 workflows + 2 integration docs + structure).**

## Content Shape (per workflow)

Each workflow is adopter-ready with `AZURE_TENANT_ID`,
`AZURE_CLIENT_ID`, `AZURE_SUBSCRIPTION_ID` as GitHub Environment variables
(non-secret — the OIDC protocol authenticates, no secret values needed).

Example: `workflows/iac-apply-production.yml`:

```yaml
name: IaC Apply (Production)

on:
  push:
    tags:
      - 'v*'

permissions:
  id-token: write       # Required for OIDC federation
  contents: read

env:
  TF_VERSION: "1.9.x"

jobs:
  plan:
    runs-on: ubuntu-latest
    environment: production-plan   # Non-approval env
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - run: terraform init
        working-directory: iac/azure
      - run: terraform plan -out=tfplan
        working-directory: iac/azure
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan-${{ github.sha }}
          path: iac/azure/tfplan

  apply:
    needs: plan
    runs-on: ubuntu-latest
    environment: production        # REQUIRES approval per GitHub Environment rules
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: actions/download-artifact@v4
        with:
          name: tfplan-${{ github.sha }}
          path: iac/azure
      - run: terraform apply tfplan
        working-directory: iac/azure
      # Evidence capture (references deploy-evidence.yml reusable)
      - name: Capture deploy evidence
        uses: ./.github/workflows/deploy-evidence.yml
        with:
          plan_path: iac/azure/tfplan
          environment: production
```

Other workflows follow similar patterns:
- `iac-validate.yml` runs on PR with `terraform fmt -check`, `validate`, `plan`, and `tfsec` security scan. Blocks merge on any failure.
- `drift-detection.yml` runs on schedule (daily 09:00 UTC), executes `terraform plan -detailed-exitcode`, creates GitHub Issue if exit code == 2 (drift detected).
- `deploy-evidence.yml` is a reusable workflow (`workflow_call`) that other workflows invoke to capture evidence artifacts.

## Assertions + Security Posture

Per taxonomy §4.7 "OIDC federation to Azure (no `AZURE_CREDENTIALS` JSON secret)" and §4.11 "No-static-credentials-in-CI assertion (the forbidden-pattern scan)":

Assertion to be added to the azure-enterprise profile (via D3 registry or D5 doctor):
- `ci_workflows_use_oidc`: `grep -L "secrets.AZURE_CREDENTIALS" templates/ci/azure/workflows/*.yml` returns all workflow files (none use the JSON secret).
- `ci_workflows_have_approval_gates`: `yq '.jobs[].environment' templates/ci/azure/workflows/iac-apply-production.yml` returns `"production"` (environment gated).

These assertions enforce the forbidden-pattern scan at template-write time, not just adopter-apply time.

## Registry Integration

All 11 files added as `class_="file"` artifacts in
`templates/managed-artifacts.toml` with:
- `initial_profiles = ["azure-enterprise"]`
- `managed_profiles = ["azure-enterprise"]` (workflow files ARE managed — GT-KB updates the workflow skeleton across releases)
- `ownership = "gt-kb-managed"`
- `upgrade_policy = "structured-merge"` for workflow YAML (preserves adopter customizations; applies skeleton updates)
- `adopter_divergence_policy = "warn"`

Subtle: workflow files are differently-handled than IaC skeletons (D3).
- D3 IaC: `skip-if-exists` (heavily customized, never overwrite).
- D4 CI/CD: `structured-merge` (templated values adopters change are `vars.*` references; workflow structure stays stable and benefits from GT-KB updates).

If this distinction proves fragile, a future revision can downgrade D4 workflows to `skip-if-exists` too.

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `templates/ci/azure/workflows/*.yml` (6 new workflow files) | OIDC + IaC validate + staging apply + production apply + drift detection + evidence capture | +~500 lines |
| `templates/ci/azure/README.md` (new) | OIDC setup walkthrough + required GitHub Environment variables + approval rule config | +~200 lines |
| `templates/ci/azure/integrations/OWNER-APPROVAL.md` (new) | GitHub Environment approval rules template | +~80 lines |
| `templates/ci/azure/integrations/federated-identity-setup.md` (new) | Azure AD app registration + federated credential walkthrough | +~120 lines |
| `templates/managed-artifacts.toml` | Add 11 new file-artifact entries | +~150 lines |
| `src/groundtruth_kb/project/scaffold.py` | Extend to copy `templates/ci/azure/` when `profile=azure-enterprise` | +~15 lines |
| `tests/test_managed_registry.py` | Update invariants: new ci file count | +~8 / -~3 lines |
| `tests/test_azure_cicd_scaffold.py` (new) | Integration test: scaffold writes all 11 files with correct OIDC assertions | +~180 lines |
| `docs/reference/azure-cicd-templates.md` (new) | Adopter-facing documentation | +~150 lines |

**Total: ~11 new template files + 5 modified/new support files. Approx +1,400 lines, -3 lines.**

## Non-Scope (explicit exclusions)

- **Azure DevOps Pipelines** — owner explicitly chose GitHub Actions-only (DELIB-0827).
- **Workflow execution / deployment** — templates only; GT-KB doesn't run CI/CD.
- **Specific secret values / tenant IDs / client IDs** — adopters fill these in via GitHub Environment vars.
- **Integration with non-Azure deploy targets** — D4 targets Azure only.
- **D3 IaC template content** — separate parallel bridge; D4 references but doesn't duplicate.
- **D5 Azure doctor checks** — depends on D3 + D4 completion.

## Verification Plan

```text
# Pre-apply: confirm current azure-enterprise ci scaffold is empty
$ ls templates/ci/azure/ 2>&1
ls: cannot access ...: No such file or directory

# Run scoped + registry tests
$ python -m pytest tests/test_managed_registry.py tests/test_azure_cicd_scaffold.py -q
# Expect: registry invariants updated; new scaffold test 5-10 passes

# Run full suite
$ python -m pytest -q
# Expect: no regressions, net-new test adds pass count

# mypy strict on modified scaffold.py
$ python -m mypy --strict src/groundtruth_kb/project/scaffold.py
Success: no issues found in 1 source file

# ruff check + format
$ python -m ruff check src/groundtruth_kb/project/scaffold.py tests/test_azure_cicd_scaffold.py
All checks passed!

# YAML lint (workflows valid)
$ yamllint templates/ci/azure/workflows/
(no errors)

# GitHub Actions workflow lint (actionlint)
$ actionlint templates/ci/azure/workflows/*.yml
(no errors)

# OIDC assertion check (no AZURE_CREDENTIALS JSON secret)
$ grep -r "secrets.AZURE_CREDENTIALS" templates/ci/azure/
(empty — no hits)

# End-to-end scaffold test
$ cd /tmp/scratch && gt project init test-proj --profile azure-enterprise
$ ls test-proj/.github/workflows/
# Expect: 6 azure-* workflow files
```

## Implementation Sequence

1. Design + write the 6 workflow templates + 3 integration docs + 1 README.
2. Extend `scaffold.py` to copy `templates/ci/azure/` when profile matches.
3. Add 11 new file-artifact registry entries in `templates/managed-artifacts.toml`.
4. Update test_managed_registry.py invariants.
5. Write `tests/test_azure_cicd_scaffold.py` — scaffold + OIDC-assertion test.
6. Write `docs/reference/azure-cicd-templates.md`.
7. Run scoped + full pytest; mypy --strict; ruff check + format.
8. Run `actionlint` against the workflow templates (catches invalid syntax early).
9. Commit on `groundtruth-kb/main`: `feat(azure): D4 — GitHub Actions CI/CD templates for azure-enterprise profile`.
10. Push to `origin/main`.
11. File post-impl report.

## Prior Deliberations

- DELIB-0827 (owner_conversation, 2026-04-18): D3=Terraform-only + D4=GHA-only + parallel.
- `docs/reference/azure-readiness-taxonomy.md` §4.7 (CI/CD category subtopics).
- Agent Red's own `.github/workflows/` as pattern reference (existing Agent Red workflows use GHA).

## Owner Decisions Required

None. DELIB-0827 + taxonomy doc pin all choices.

## Requested Verdict

**GO** to implement §1-§11 per the sequence, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
