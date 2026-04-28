# Azure CI/CD Templates (`gt scaffold cicd --profile azure-enterprise`)

This reference documents the 12 GitHub Actions CI/CD skeleton files that
`gt scaffold cicd --profile azure-enterprise` produces. Skeletons are
**adopter-owned**: the scaffold never overwrites existing files. After the
first successful `--apply`, the adopter is free to edit every file and the
scaffold will skip them on subsequent runs.

## What the scaffold produces

Twelve files, all under `.github/` or `docs/azure/`:

| # | Target path | Kind | Purpose |
|---|---|---|---|
| 1 | `.github/actions/azure-oidc-login/action.yml` | Composite action | Federated login via `azure/login@v2`. Typed inputs only. |
| 2 | `.github/actions/deploy-evidence/action.yml` | Composite action | Writes a JSON deployment receipt, uploads as artifact. |
| 3 | `.github/workflows/iac-validate.yml` | Workflow | PR gate: fmt, validate, plan, tfsec against staging-plan. |
| 4 | `.github/workflows/iac-apply-staging.yml` | Workflow | Merge-to-`develop` gate: plan + gated apply to staging. |
| 5 | `.github/workflows/iac-apply-production.yml` | Workflow | Tag (`v*`) gate: plan + gated apply to production. |
| 6 | `.github/workflows/drift-detection.yml` | Workflow | Daily detect-only plan; opens a GitHub issue on drift. |
| 7 | `.github/workflows/README.md` | Docs | Workflow architecture overview for repo browsers. |
| 8 | `docs/azure/OWNER-APPROVAL.md` | Docs | Recommended Environment-approval rules template. |
| 9 | `docs/azure/federated-identity-setup.md` | Docs | Azure AD federated-credential walkthrough. |
| 10 | `docs/azure/cicd-overview.md` | Docs | Overall CI/CD topology + customization points. |
| 11 | `docs/azure/drift-detection-runbook.md` | Docs | Response procedure for drift-detection issues. |
| 12 | `docs/azure/iac-working-dir-config.md` | Docs | When and how to override `TF_WORKING_DIR`. |

## Usage

```bash
# Dry run (default) - no files written; the report shows what would be generated.
gt scaffold cicd --profile azure-enterprise

# Apply - writes the 12 files under the current directory.
gt scaffold cicd --profile azure-enterprise --apply

# Apply into a different root (useful for testing or monorepo layouts).
gt scaffold cicd --profile azure-enterprise --apply --target-dir infra/azure-cicd
```

Re-running `--apply` after any files already exist reports each of them as
*skipped*; nothing is overwritten. To reset a scaffolded file to its
skeleton contents, delete it first.

## OIDC contract

All Azure authentication flows through OpenID Connect federation. There is
no place in the scaffold that reads `secrets.AZURE_CREDENTIALS` or any
static client secret. The composite action at
`.github/actions/azure-oidc-login/action.yml` declares three typed inputs:

- `client-id` (required) — pass `${{ vars.AZURE_CLIENT_ID }}`.
- `tenant-id` (required) — pass `${{ vars.AZURE_TENANT_ID }}`.
- `subscription-id` (required) — pass `${{ vars.AZURE_SUBSCRIPTION_ID }}`.

Every workflow that calls this composite action:

1. Declares `permissions: { id-token: write, contents: read }` at the
   workflow level. Without `id-token: write`, GitHub will not mint the
   OIDC token required by `azure/login@v2`.
2. Declares a job-level `environment:` on every job that invokes the
   composite action. GitHub Environment-scoped `vars.*` only resolve when
   the job declares the owning environment.
3. Passes the three `vars.AZURE_*` values through the composite action's
   `with:` block. The composite action never reads them from
   `env.AZURE_*`.

`drift-detection.yml` additionally declares `permissions: { issues:
write }` so the detection step can open an issue when drift is reported.

## Azure AD application and federated credentials

The scaffold does not (and cannot) create the Azure AD application or the
federated credentials. Those steps are one-shot Azure-side configuration.
See `docs/azure/federated-identity-setup.md` (produced by the scaffold) for
the full CLI walkthrough. Summary:

1. `az ad app create --display-name "gh-oidc-<repo>"`, then
   `az ad sp create --id $APP_ID`.
2. `az role assignment create` to grant the service principal the minimum
   RBAC required (`Contributor` on the staging resource group; a narrower
   custom role on production).
3. `az ad app federated-credential create` per GitHub Environment
   (`staging-plan`, `staging`, `production-plan`, `production`). The
   federated credential's `subject` field must match the Environment name
   the workflow job declares.

## GitHub Environment configuration

In GitHub repo Settings → Environments, create these four environments
and add the listed variables (not secrets):

| Environment | Reviewer rule | Variables |
|---|---|---|
| `staging-plan` | None | `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, optional `TF_WORKING_DIR`. |
| `staging` | 1 platform reviewer | same |
| `production-plan` | None | same (usually staging's values or a separate read-only SP) |
| `production` | 2 reviewers + ≥ 15 min wait | Same, with production subscription scope. |

The scaffolded `docs/azure/OWNER-APPROVAL.md` carries a detailed template
the adopter can adapt.

## Relationship to D3 (`gt scaffold iac`)

All four scaffolded workflows read the Terraform tree from
`${{ vars.TF_WORKING_DIR || 'iac/azure' }}`. The default `iac/azure`
matches the top-level directory produced by
`gt scaffold iac --profile azure-enterprise` (D3). If your Terraform tree
lives elsewhere, set `vars.TF_WORKING_DIR` per environment; see
`docs/azure/iac-working-dir-config.md` for overrides.

## Recommended post-scaffold verification

### actionlint (strongly recommended)

Run actionlint against the scaffolded workflow files to catch typos,
unknown action refs, and context-misuse:

```bash
actionlint --version
actionlint .github/workflows/*.yml
```

A clean run produces no output and exits 0. The GroundTruth-KB internal
test suite includes `test_scaffolded_workflows_actionlint_clean` (gated on
actionlint being on PATH) as an extra defense. If you install actionlint
on your CI runner, consider adding the same invocation as a job step in
`iac-validate.yml`.

### Dry-run verification before `--apply`

Always run without `--apply` first. The dry-run report lists every target
path, and distinguishes paths that would be generated from paths that
would be skipped (because they already exist). No file is written until
you explicitly pass `--apply`.

### Manual smoke of the generated tree

After `--apply`:

- Confirm all 12 files are present with `find .github docs/azure -type f`.
- Parse each `.yml` with your language's YAML library to rule out copy
  errors.
- `grep -R "secrets.AZURE_CREDENTIALS" .github` should return no matches
  (OIDC-only contract).
- `grep -R "env.AZURE_CLIENT_ID" .github` should return no matches (typed
  inputs only).

## Non-scope

The scaffold does NOT do any of the following:

- Create or configure Azure AD applications, service principals, or
  federated credentials (Azure-side; see the scaffolded walkthrough).
- Create or configure GitHub Environments, required reviewers, or wait
  timers (GitHub-UI-only).
- Execute or schedule the workflows — you must commit, push, and open a PR.
- Provision a Terraform tree (that's D3, `gt scaffold iac`).
- Support a `--force` overwrite mode. This is intentional: scaffold-once
  adopter-owned lifecycle matches the D1/D2/D3 pattern. Delete a file and
  re-run `--apply` if you want to regenerate it.
- Provide any Azure DevOps Pipelines templates (DELIB-0827 GHA-only).

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `AADSTS70021: No matching federated identity record found` | The federated credential's `subject` does not match the Environment name the job declares. See federated-identity-setup.md. |
| `terraform init` fails with `no *.tf files` | `TF_WORKING_DIR` points to a directory that does not contain Terraform configuration. |
| `permission denied: id-token` | Workflow is missing `permissions: id-token: write` at workflow level, or the calling repo disables OIDC on forked PRs. |
| `vars.AZURE_CLIENT_ID` resolves to empty string | The job does not declare a matching `environment:`, or the Environment does not have the variable set. |
| `terraform plan` drift on resources the adopter never changed | Managed services (e.g. AKS upgrades, Azure Policy remediation) are rotating fields; consider a `lifecycle.ignore_changes` block. |

## Authoritative sources

- Proposal: `bridge/gtkb-azure-cicd-gates-005.md` (REVISED-2).
- Review (GO): `bridge/gtkb-azure-cicd-gates-006.md`.
- Parent track: D3 `bridge/gtkb-azure-iac-skeleton-006.md` VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
