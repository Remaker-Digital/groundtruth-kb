# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
# ruff: noqa: E501
"""
GroundTruth KB - D4 Azure CI/CD Template Catalog.

Defines 12 GitHub Actions CI/CD skeleton file descriptors scaffolded via
``gt scaffold cicd --profile azure-enterprise``. Skeletons are adopter-owned;
after first scaffold the adopter configures GitHub Environments, vars, and
federated-identity credentials per the accompanying docs under ``docs/azure/``.

Authoritative source: bridge/gtkb-azure-cicd-gates-006.md GO.

The catalog is intentionally shaped so the composite action at
``.github/actions/azure-oidc-login/action.yml`` declares typed ``inputs``,
and every workflow invoking it:

1. Passes ``vars.AZURE_*`` through ``with:`` (no ``env.AZURE_*`` anywhere).
2. Declares ``permissions.id-token: write`` at workflow level.
3. Declares a job-level ``environment:`` on every job that calls the
   composite action (so GitHub Environment-scoped ``vars`` resolve).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from typing import Any

__all__ = ["azure_cicd_templates", "AZURE_CICD_EXPECTED_PATHS"]


# ---------------------------------------------------------------------------
# Composite actions
# ---------------------------------------------------------------------------


_ACTION_AZURE_OIDC_LOGIN = """name: 'Azure OIDC Login'
description: >
  Federated login to Azure via OIDC. Caller must declare
  permissions: { id-token: write, contents: read }.
inputs:
  client-id:
    description: 'Azure AD application (client) ID. Pass vars.AZURE_CLIENT_ID.'
    required: true
  tenant-id:
    description: 'Azure AD tenant ID. Pass vars.AZURE_TENANT_ID.'
    required: true
  subscription-id:
    description: 'Azure subscription ID. Pass vars.AZURE_SUBSCRIPTION_ID.'
    required: true
runs:
  using: "composite"
  steps:
    - name: Azure login (OIDC)
      uses: azure/login@v2
      with:
        client-id:       ${{ inputs.client-id }}
        tenant-id:       ${{ inputs.tenant-id }}
        subscription-id: ${{ inputs.subscription-id }}
"""


_ACTION_DEPLOY_EVIDENCE = """name: 'Deploy Evidence'
description: >
  Capture a deployment-evidence artifact for the current job. Caller passes
  the deployment environment name; the action writes a small JSON receipt
  and uploads it as a workflow artifact so downstream auditors can trace
  which commit/tag deployed to which environment.
inputs:
  environment:
    description: 'Deployment environment name (e.g. staging, production).'
    required: true
runs:
  using: "composite"
  steps:
    - name: Write evidence file
      shell: bash
      run: |
        mkdir -p deploy-evidence
        cat > deploy-evidence/receipt.json <<JSON
        {
          "environment": "${{ inputs.environment }}",
          "repository": "${{ github.repository }}",
          "ref":        "${{ github.ref }}",
          "sha":        "${{ github.sha }}",
          "actor":      "${{ github.actor }}",
          "run_id":     "${{ github.run_id }}",
          "run_number": "${{ github.run_number }}",
          "timestamp":  "${{ github.event.head_commit.timestamp }}"
        }
        JSON
    - name: Upload evidence artifact
      uses: actions/upload-artifact@v4
      with:
        name: deploy-evidence-${{ inputs.environment }}-${{ github.run_id }}
        path: deploy-evidence/receipt.json
"""


# ---------------------------------------------------------------------------
# Workflow helpers
# ---------------------------------------------------------------------------


def _oidc_login_step(indent: str = "      ") -> str:
    """Return a standard OIDC-login step block indented at ``indent``.

    Emits the ``uses:`` line for the local composite action, followed by a
    ``with:`` block that passes ``vars.AZURE_*`` through. No ``env.AZURE_*``
    is used anywhere in the generated tree.
    """
    return (
        f"{indent}- uses: ./.github/actions/azure-oidc-login\n"
        f"{indent}  with:\n"
        f"{indent}    client-id:       ${{{{ vars.AZURE_CLIENT_ID }}}}\n"
        f"{indent}    tenant-id:       ${{{{ vars.AZURE_TENANT_ID }}}}\n"
        f"{indent}    subscription-id: ${{{{ vars.AZURE_SUBSCRIPTION_ID }}}}\n"
    )


# ---------------------------------------------------------------------------
# Workflow files
# ---------------------------------------------------------------------------


_WORKFLOW_IAC_VALIDATE = f"""name: IaC Validate

# Runs on pull requests touching the Terraform tree. Validates HCL syntax,
# runs tfsec, and emits a plan against the staging environment so reviewers
# can see the proposed change before merge.

on:
  pull_request:
    paths:
      - 'iac/**'
      - '.github/workflows/iac-validate.yml'
      - '.github/actions/azure-oidc-login/**'

permissions:
  id-token: write    # Required for OIDC federation.
  contents: read     # Required for checkout.

jobs:
  validate:
    runs-on: ubuntu-latest
    environment: staging-plan   # GitHub Environment holding vars.AZURE_*.
    steps:
      - uses: actions/checkout@v4
{_oidc_login_step()}      - uses: hashicorp/setup-terraform@v3
      - name: terraform fmt -check
        run: terraform fmt -check -recursive
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - name: terraform init
        run: terraform init -backend=false
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - name: terraform validate
        run: terraform validate
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - name: terraform plan (informational)
        run: terraform plan -input=false -no-color
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - name: tfsec
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
          soft_fail: false
"""


_WORKFLOW_IAC_APPLY_STAGING = f"""name: IaC Apply (Staging)

# Runs on merges to the staging integration branch. Produces a plan in one
# job, then applies it in a second job gated by the ``staging`` GitHub
# Environment. Keep the plan/apply split so reviewers see what the apply job
# will execute.

on:
  push:
    branches:
      - develop

permissions:
  id-token: write
  contents: read

jobs:
  plan:
    runs-on: ubuntu-latest
    environment: staging-plan
    steps:
      - uses: actions/checkout@v4
{_oidc_login_step()}      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - run: terraform plan -out=tfplan
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan-staging-${{{{ github.sha }}}}
          path: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}/tfplan

  apply:
    needs: plan
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
{_oidc_login_step()}      - uses: hashicorp/setup-terraform@v3
      - uses: actions/download-artifact@v4
        with:
          name: tfplan-staging-${{{{ github.sha }}}}
          path: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - run: terraform init
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - run: terraform apply -input=false tfplan
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - uses: ./.github/actions/deploy-evidence
        with:
          environment: staging
"""


_WORKFLOW_IAC_APPLY_PRODUCTION = f"""name: IaC Apply (Production)

# Runs on release tags (``v*``). Plan job produces the artifact; the apply
# job is gated by the ``production`` GitHub Environment which should require
# explicit reviewer approval (see docs/azure/OWNER-APPROVAL.md).

on:
  push:
    tags:
      - 'v*'

permissions:
  id-token: write
  contents: read

jobs:
  plan:
    runs-on: ubuntu-latest
    environment: production-plan
    steps:
      - uses: actions/checkout@v4
{_oidc_login_step()}      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - run: terraform plan -out=tfplan
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan-production-${{{{ github.sha }}}}
          path: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}/tfplan

  apply:
    needs: plan
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
{_oidc_login_step()}      - uses: hashicorp/setup-terraform@v3
      - uses: actions/download-artifact@v4
        with:
          name: tfplan-production-${{{{ github.sha }}}}
          path: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - run: terraform init
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - run: terraform apply -input=false tfplan
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - uses: ./.github/actions/deploy-evidence
        with:
          environment: production
"""


_WORKFLOW_DRIFT_DETECTION = f"""name: Drift Detection

# Scheduled daily detect-only plan against the production environment. If
# drift is detected, the workflow opens a GitHub issue. This is why this
# workflow needs ``issues: write`` beyond the standard OIDC permissions.

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

permissions:
  id-token: write
  contents: read
  issues: write      # Required so the drift step can open an issue.

jobs:
  detect:
    runs-on: ubuntu-latest
    environment: production-plan
    steps:
      - uses: actions/checkout@v4
{_oidc_login_step()}      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - name: terraform plan -detailed-exitcode
        id: plan
        run: terraform plan -detailed-exitcode -lock=false -input=false
        continue-on-error: true
        working-directory: ${{{{ vars.TF_WORKING_DIR || 'iac/azure' }}}}
      - name: Open drift issue
        if: steps.plan.outcome == 'failure' || steps.plan.outputs.exitcode == '2'
        uses: actions/github-script@v7
        with:
          script: |
            const title = 'Azure IaC drift detected (' + new Date().toISOString().slice(0,10) + ')';
            await github.rest.issues.create({{
              owner: context.repo.owner,
              repo:  context.repo.repo,
              title: title,
              body:  'Automated drift detection run ' + context.runId +
                ' reported differences between code and the production Azure environment. ' +
                'See the attached plan output. Follow docs/azure/drift-detection-runbook.md to triage.',
              labels: ['drift', 'azure', 'priority:high'],
            }});
"""


_WORKFLOW_README = """# GitHub Actions Workflows (Azure Enterprise Profile)

This directory is a skeleton produced by
``gt scaffold cicd --profile azure-enterprise``. It is adopter-owned: the
scaffold never overwrites existing files.

## Files

| Path | Purpose |
|---|---|
| `iac-validate.yml` | Pull-request gate: fmt/validate/plan + tfsec against staging-plan. |
| `iac-apply-staging.yml` | On merge to `develop`: plan + apply to the staging environment. |
| `iac-apply-production.yml` | On release tag (`v*`): plan + apply to production (gated). |
| `drift-detection.yml` | Scheduled daily detect-only plan; opens a GitHub issue on drift. |

Both composite actions live under `../actions/`:

- `actions/azure-oidc-login/action.yml` — federated login via
  `azure/login@v2`. Caller passes `vars.AZURE_*` through `with:`.
- `actions/deploy-evidence/action.yml` — writes a small JSON receipt and
  uploads it as a workflow artifact so downstream auditors can trace which
  commit deployed where.

## GitHub configuration the adopter must supply

Per-environment (`staging-plan`, `staging`, `production-plan`, `production`)
set these GitHub Environment *Variables* (not Secrets):

- `AZURE_CLIENT_ID`        — Azure AD app (client) ID used by the federated credential.
- `AZURE_TENANT_ID`        — Azure AD tenant ID.
- `AZURE_SUBSCRIPTION_ID`  — Azure subscription ID the environment deploys into.
- `TF_WORKING_DIR`         — Optional. Defaults to `iac/azure` when unset.

See `docs/azure/federated-identity-setup.md` for the federated-identity walkthrough
and `docs/azure/OWNER-APPROVAL.md` for the recommended environment-approval rules.

## Why no static credentials?

There is no place in this skeleton that references a static Azure client
secret. All Azure auth flows through OIDC federation. Rotate by
re-scoping the federated credential in Azure AD, not by editing workflow
YAML.
"""


_DOC_OWNER_APPROVAL = """# Owner Approval Rules for GitHub Environments

This is a template for the approval rules an adopter should configure on
the GitHub Environments used by the scaffolded workflows. The scaffold does
not (and cannot) configure these in code — they are GitHub-UI-only
settings per organization.

## Required GitHub Environments

| Environment       | Used by workflow(s)                          | Recommended approval rule                          |
|-------------------|-----------------------------------------------|-----------------------------------------------------|
| `staging-plan`    | `iac-validate.yml`, `iac-apply-staging.yml`   | No required reviewers (plan is read-only).          |
| `staging`         | `iac-apply-staging.yml` (apply job)           | 1 required reviewer from the platform team.         |
| `production-plan` | `iac-apply-production.yml`, `drift-detection` | No required reviewers (plan is read-only).          |
| `production`      | `iac-apply-production.yml` (apply job)        | 2 required reviewers; wait timer ≥ 15 min.          |

## Why split plan and apply?

The apply job downloads the exact plan the preceding plan job uploaded.
Splitting them forces the apply job through an Environment protection rule
that requires human approval AFTER the plan is visible in the run UI. The
reviewer sees what will be applied before clicking approve.

## What reviewers should check before approving production apply

- `terraform plan` output in the plan job shows only expected resources.
- No destroy/replace operations on stateful resources unless the PR
  explicitly authorizes them.
- Cost impact is within the approved budget for the change.
- The commit SHA matches the tagged release that triggered the workflow.

## Rollback

If a production apply creates an incident, revert the tag in git and
re-tag. The apply workflow re-runs with the prior plan. For fast rollback
of resource changes, re-deploy the prior tag rather than attempting to
hand-edit Azure state.
"""


_DOC_FEDERATED_IDENTITY_SETUP = """# Federated Identity Setup for Azure OIDC

Configure federated credentials in Azure AD so the scaffolded workflows can
authenticate to Azure without storing long-lived client secrets.

## Prerequisites

- Azure AD tenant + subscription owner role.
- Azure CLI ≥ 2.50 authenticated (`az login`).
- GitHub repository with the scaffolded workflows merged.

## Step 1: Create an Azure AD application

```bash
az ad app create --display-name "gh-oidc-<repo>"
APP_ID=$(az ad app list --display-name "gh-oidc-<repo>" --query '[0].appId' -o tsv)
az ad sp create --id "$APP_ID"
```

## Step 2: Grant the service principal RBAC

Grant only what the workflow needs. For staging apply, `Contributor` on the
staging resource group is usually sufficient; production should be a
narrower custom role:

```bash
SUB_ID=$(az account show --query id -o tsv)
az role assignment create \\
  --assignee "$APP_ID" \\
  --role "Contributor" \\
  --scope "/subscriptions/$SUB_ID/resourceGroups/<staging-rg>"
```

## Step 3: Add a federated credential per GitHub Environment

Repeat for each of `staging-plan`, `staging`, `production-plan`,
`production`. Example for `staging`:

```bash
az ad app federated-credential create \\
  --id "$APP_ID" \\
  --parameters '{
    "name":      "gh-oidc-staging",
    "issuer":    "https://token.actions.githubusercontent.com",
    "subject":   "repo:<OWNER>/<REPO>:environment:staging",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

The `subject` field must match the GitHub Environment name the workflow
job declares (`environment: staging`). Tag-gated environments use
`subject: repo:<OWNER>/<REPO>:ref:refs/tags/v*` instead.

## Step 4: Set GitHub Environment variables

In GitHub repo Settings → Environments → each environment, add Variables:

- `AZURE_CLIENT_ID`       = `$APP_ID`
- `AZURE_TENANT_ID`       = `az account show --query tenantId -o tsv`
- `AZURE_SUBSCRIPTION_ID` = `$SUB_ID`
- `TF_WORKING_DIR`        = `iac/azure` (optional; default)

These are *Variables*, not *Secrets*. The composite action at
`.github/actions/azure-oidc-login/action.yml` reads them through
`${{ inputs.* }}` after the calling workflow forwards `vars.*`.

## Step 5: Verify

Open a test PR touching `iac/**`. The `IaC Validate` workflow should:

1. Authenticate via `azure/login@v2` without a client secret.
2. Run `terraform fmt -check`, `terraform init -backend=false`,
   `terraform validate`, and an informational `terraform plan`.
3. Run `tfsec`.

If login fails with `AADSTS70021`, double-check that the federated
credential's `subject` matches the environment the job declared.
"""


_DOC_CICD_OVERVIEW = """# CI/CD Overview — Azure Enterprise Profile

The scaffold produces four workflows and two composite actions under
`.github/`. This document explains the overall topology and where to
customize.

## Workflow topology

```
pull_request  ─►  iac-validate.yml          ─►  staging-plan env
                   (fmt, validate, plan, tfsec)

push develop  ─►  iac-apply-staging.yml     ─►  plan → staging env apply
                   (upload tfplan)                (download tfplan + apply)

push tag v*   ─►  iac-apply-production.yml  ─►  plan → production env apply
                   (upload tfplan)                (download tfplan + apply)

cron 06:00Z   ─►  drift-detection.yml       ─►  detect-only plan → issue on drift
```

## Composite actions

- **`actions/azure-oidc-login`** — thin wrapper over `azure/login@v2`. Typed
  inputs force callers to pass values explicitly; no implicit env reads.
- **`actions/deploy-evidence`** — writes a JSON receipt (repo, sha, env,
  timestamp) and uploads it as a workflow artifact.

## Adopter customization points

| Concern                         | Customize in                                                      |
|---------------------------------|-------------------------------------------------------------------|
| Different Terraform tree path   | Set `vars.TF_WORKING_DIR` per environment.                        |
| Extra security scanners         | Add steps to `iac-validate.yml` after `tfsec`.                    |
| Tighter RBAC for production     | Narrow the role assignment in `federated-identity-setup.md` step 2. |
| Slack/Teams notification        | Add a notification step to each `apply` job.                      |
| Additional environments         | Copy an apply workflow and retarget `environment:` + credentials. |

## Relationship to D3 IaC scaffold

These workflows assume a Terraform tree produced by
`gt scaffold iac --profile azure-enterprise` (D3). The default
`TF_WORKING_DIR` is `iac/azure`, which matches D3's top-level. Set
`vars.TF_WORKING_DIR` to override.

## What this scaffold does NOT do

- Provision the Azure AD app, service principal, or federated credentials
  — those are one-shot Azure-side steps (see `federated-identity-setup.md`).
- Configure GitHub Environments or approval rules — those are GitHub-UI
  configuration (see `OWNER-APPROVAL.md`).
- Run the workflows. You need to commit, push, and open a PR.
- Provide a static-client-secret fallback. All auth is OIDC.
"""


_DOC_DRIFT_DETECTION_RUNBOOK = """# Drift Detection Runbook

When `drift-detection.yml` opens an issue, follow this runbook.

## 1. Classify the drift

Open the linked workflow run and read the `terraform plan` output. Drift
falls into one of three categories:

- **Expected** — the adopter changed something in Azure on purpose but
  has not yet reflected it in Terraform. Action: open a PR that brings
  the Terraform tree in line with the observed state. Re-run drift
  detection after merge; the issue should auto-close on the next clean
  run.
- **Unexpected configuration drift** — someone edited the Azure resource
  outside the pipeline. Action: review the diff; either (a) revert the
  manual change in Azure or (b) incorporate it into Terraform as in the
  previous case.
- **Destructive drift** — the plan shows resources being destroyed or
  replaced. Action: treat as an incident; escalate before applying.

## 2. Triage window

Aim to resolve drift within:

- 1 business day for `priority:high` (default label).
- Immediately for drift on stateful resources (databases, storage,
  keyvaults) — escalate to the on-call.

## 3. Re-running detection

Drift detection runs automatically at 06:00Z daily. To re-run manually:

1. Go to Actions → `Drift Detection` → Run workflow.
2. Select the `main` branch.
3. After the run, re-check the linked issue — it will auto-close on a
   clean run.

## 4. Common drift sources

- Azure Portal edits that bypass Terraform.
- `az` CLI one-liners during incident response.
- Auto-remediation from Azure Defender or Azure Policy.
- Managed services (e.g. AKS control-plane upgrades) that rotate
  resource attributes.

For the last two, consider adding a `lifecycle.ignore_changes` block to
the affected resource rather than fighting the drift.

## 5. Permanently closing issues

If the drift is truly expected and cannot be codified (rare), close the
issue with the `wontfix` label AND add a comment explaining the
exception. Without the comment, the next on-call will reopen it.
"""


_DOC_IAC_WORKING_DIR_CONFIG = """# TF_WORKING_DIR Configuration

All four scaffolded workflows read the Terraform tree from
`${{ vars.TF_WORKING_DIR || 'iac/azure' }}`. This document explains when
to override.

## Default: `iac/azure`

If you scaffolded the IaC tree via `gt scaffold iac --profile
azure-enterprise` (D3) at the repository root, the default is correct —
no override needed.

## When to override

| Scenario                                             | Set `TF_WORKING_DIR` to |
|------------------------------------------------------|-------------------------|
| Multiple Terraform roots (monorepo)                  | `infra/azure/platform`  |
| Environment-per-directory layout                     | `iac/azure/envs/prod`   |
| IaC tree moved out of `iac/azure` for unrelated reasons | the new path          |

## How to configure

In GitHub repo Settings → Environments → each of `staging-plan`,
`staging`, `production-plan`, `production`, add a Variable named
`TF_WORKING_DIR` with the correct path.

Variables are per-environment, so you can point different environments at
different Terraform roots (unusual but supported).

## Interaction with the IaC validate workflow

`iac-validate.yml` triggers on pull requests touching `iac/**`. If you
move the Terraform tree out of `iac/`, also update the workflow's
`paths:` trigger. The scaffold uses `iac/**` because that matches the D3
default; a wider trigger like `'**/*.tf'` is reasonable for monorepo
layouts.

## Verifying

After setting the variable, re-run any workflow and confirm the log line
`working-directory:` in each step matches the expected path. A
misconfigured `TF_WORKING_DIR` typically surfaces as a `no *.tf files`
error in the `terraform init` step.
"""


# ---------------------------------------------------------------------------
# Descriptor catalog
# ---------------------------------------------------------------------------


def _azure_cicd_descriptors() -> list[dict[str, Any]]:
    """Return the raw 12-entry descriptor list (module-internal helper).

    Shape mirrors D3 ``azure_iac_templates()``: each entry is a dict with
    ``target_path`` (str, repo-relative) and ``content`` (str, full file
    contents). Downstream consumers should use the public ``azure_cicd_templates()``
    wrapper rather than calling this directly.
    """
    return [
        # 2 composite actions
        {
            "target_path": ".github/actions/azure-oidc-login/action.yml",
            "content": _ACTION_AZURE_OIDC_LOGIN,
        },
        {
            "target_path": ".github/actions/deploy-evidence/action.yml",
            "content": _ACTION_DEPLOY_EVIDENCE,
        },
        # 4 workflows
        {
            "target_path": ".github/workflows/iac-validate.yml",
            "content": _WORKFLOW_IAC_VALIDATE,
        },
        {
            "target_path": ".github/workflows/iac-apply-staging.yml",
            "content": _WORKFLOW_IAC_APPLY_STAGING,
        },
        {
            "target_path": ".github/workflows/iac-apply-production.yml",
            "content": _WORKFLOW_IAC_APPLY_PRODUCTION,
        },
        {
            "target_path": ".github/workflows/drift-detection.yml",
            "content": _WORKFLOW_DRIFT_DETECTION,
        },
        # 1 workflow README
        {
            "target_path": ".github/workflows/README.md",
            "content": _WORKFLOW_README,
        },
        # 5 adopter docs
        {
            "target_path": "docs/azure/OWNER-APPROVAL.md",
            "content": _DOC_OWNER_APPROVAL,
        },
        {
            "target_path": "docs/azure/federated-identity-setup.md",
            "content": _DOC_FEDERATED_IDENTITY_SETUP,
        },
        {
            "target_path": "docs/azure/cicd-overview.md",
            "content": _DOC_CICD_OVERVIEW,
        },
        {
            "target_path": "docs/azure/drift-detection-runbook.md",
            "content": _DOC_DRIFT_DETECTION_RUNBOOK,
        },
        {
            "target_path": "docs/azure/iac-working-dir-config.md",
            "content": _DOC_IAC_WORKING_DIR_CONFIG,
        },
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def azure_cicd_templates() -> list[dict[str, Any]]:
    """Return all 12 Azure CI/CD skeleton templates as path/content descriptors.

    Mirrors the D3 ``azure_iac_templates()`` pattern. Each descriptor has:

    - ``target_path``: path relative to the scaffold root
      (e.g. ``.github/workflows/iac-validate.yml``).
    - ``content``: full file content as a string.

    Total count: 2 composite actions + 4 workflow YAML + 1 workflow README +
    5 adopter docs = 12 descriptors.
    """
    return _azure_cicd_descriptors()


AZURE_CICD_EXPECTED_PATHS: tuple[str, ...] = tuple(d["target_path"] for d in azure_cicd_templates())
"""Authoritative 12-path inventory for the Azure CI/CD scaffold.

Used by both the scaffold orchestrator and the test suite; a single
constant avoids the catalog and the test file drifting out of sync.
"""
