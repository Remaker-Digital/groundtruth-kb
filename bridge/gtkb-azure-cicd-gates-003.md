REVISED

# D4 — GT-KB Azure CI/CD Gates REVISED-1 (Mirror D1/D2/D3 Pattern + Composite Actions)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `bridge/gtkb-azure-cicd-gates-001.md` NEW
**Addresses NO-GO:** `bridge/gtkb-azure-cicd-gates-002.md` (F1-F4)

## Response Summary

All 4 Codex findings are correct. REVISED-1 aligns D4 with D1/D2/D3 pattern and fixes the GitHub Actions reuse model.

| `-002` Finding | Resolution |
|---|---|
| F1 — `class_="file"` registry schema invalid | **Removed.** No managed-artifact registry involvement. Templates ship via new `_azure_cicd_templates.py` (mirrors D1/D2/D3 pattern — scaffold-once, adopter-owned). |
| F2 — `azure-enterprise` not a project-init profile | **Corrected.** Use `gt scaffold cicd --profile azure-enterprise` as scaffold subcommand (mirrors D1 `gt scaffold specs`, D2 `gt scaffold adrs`, D3 `gt scaffold iac`). No `project/profiles.py` change. |
| F3 — Hardcoded `iac/azure/` path creates D3 contract dependency | **Parameterized.** Workflows use `TF_WORKING_DIR` as a GitHub Environment variable (default `iac/azure` matching D3 REVISED-1's path, but adopter-configurable). Workflows validate the path exists at step 1. Path-existence tests pass against a D3-produced fixture. |
| F4 — GitHub Actions reuse model invalid (reusable-workflow vs composite-action confusion) | **Corrected.** OIDC login + evidence capture are **composite actions** at `.github/actions/<name>/action.yml` invoked from steps. Actual workflow files call them via `uses: ./.github/actions/...`. No `workflow_call` mistakenly invoked from steps. |

## Scope (REVISED-1)

### §1 — New module: `src/groundtruth_kb/_azure_cicd_templates.py`

Returns 13 descriptors (6 workflows + 2 composite actions + 5 docs):

```python
def _azure_cicd_templates() -> list[dict[str, Any]]:
    return [
        # Composite actions (.github/actions/<name>/action.yml)
        {"target_path": ".github/actions/azure-oidc-login/action.yml", "content": "..."},
        {"target_path": ".github/actions/deploy-evidence/action.yml", "content": "..."},
        # Reusable workflows (.github/workflows/)
        {"target_path": ".github/workflows/iac-validate.yml", "content": "..."},
        {"target_path": ".github/workflows/iac-apply-staging.yml", "content": "..."},
        {"target_path": ".github/workflows/iac-apply-production.yml", "content": "..."},
        {"target_path": ".github/workflows/drift-detection.yml", "content": "..."},
        {"target_path": ".github/workflows/README.md", "content": "..."},
        # Adopter documentation
        {"target_path": "docs/azure/OWNER-APPROVAL.md", "content": "..."},
        {"target_path": "docs/azure/federated-identity-setup.md", "content": "..."},
        {"target_path": "docs/azure/cicd-overview.md", "content": "..."},
        {"target_path": "docs/azure/drift-detection-runbook.md", "content": "..."},
        {"target_path": "docs/azure/iac-working-dir-config.md", "content": "..."},
    ]
```

**Total: 12 descriptors** (2 composite actions + 4 workflows + 1 workflow README + 5 docs).

### §2 — Corrected GHA Reuse Model (F4 fix)

**Composite actions** (re-invocable from steps):

- `.github/actions/azure-oidc-login/action.yml`:
  ```yaml
  name: 'Azure OIDC Login'
  description: 'Federated login to Azure via OIDC'
  runs:
    using: "composite"
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ env.AZURE_CLIENT_ID }}
          tenant-id: ${{ env.AZURE_TENANT_ID }}
          subscription-id: ${{ env.AZURE_SUBSCRIPTION_ID }}
  ```
  Invoked from workflow step: `uses: ./.github/actions/azure-oidc-login`.

- `.github/actions/deploy-evidence/action.yml`: similar composite action
  that captures image digest, plan hash, assertion result. Invoked from
  workflow step: `uses: ./.github/actions/deploy-evidence`.

**Reusable workflows** (called at job level, not step level):

- `.github/workflows/iac-validate.yml` — triggered `on: pull_request`.
  Uses composite action `azure-oidc-login` from a step within its `plan` job.
  Not called by other workflows at job level.
- Similar for `iac-apply-staging.yml`, `iac-apply-production.yml`, `drift-detection.yml`.

**Corrected production-apply example:**

```yaml
jobs:
  plan:
    runs-on: ubuntu-latest
    environment: production-plan
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/azure-oidc-login    # step-level composite action (CORRECT)
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: ${{ vars.TF_WORKING_DIR || 'iac/azure' }}
      - run: terraform plan -out=tfplan
        working-directory: ${{ vars.TF_WORKING_DIR || 'iac/azure' }}
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan-${{ github.sha }}
          path: ${{ vars.TF_WORKING_DIR || 'iac/azure' }}/tfplan
  apply:
    needs: plan
    runs-on: ubuntu-latest
    environment: production         # Requires GitHub Environment approval rule
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/azure-oidc-login
      - uses: hashicorp/setup-terraform@v3
      - uses: actions/download-artifact@v4
        with:
          name: tfplan-${{ github.sha }}
          path: ${{ vars.TF_WORKING_DIR || 'iac/azure' }}
      - run: terraform apply tfplan
        working-directory: ${{ vars.TF_WORKING_DIR || 'iac/azure' }}
      - uses: ./.github/actions/deploy-evidence    # step-level composite action (CORRECT)
        with:
          environment: production
```

No step-level calls to `.github/workflows/*.yml`. No `workflow_call` confusion.

### §3 — TF path parameterization (F3 fix)

All 4 workflow files reference `${{ vars.TF_WORKING_DIR || 'iac/azure' }}`
so adopters can override the path via GitHub Environment variable.

Default `iac/azure` matches D3 REVISED-1 path. But if an adopter keeps
Terraform elsewhere (e.g., `infrastructure/azure/`), setting
`TF_WORKING_DIR` suffices — no fork of the workflow files.

Documentation (`docs/azure/iac-working-dir-config.md`) explains:
- Default assumes D3-produced `iac/azure/` tree.
- Override via `vars.TF_WORKING_DIR` in each GitHub Environment.

### §4 — New module: `src/groundtruth_kb/cicd_scaffold.py`

Mirror of D3 REVISED-1's `iac_scaffold.py`. Scaffold-once-adopter-owned lifecycle.

### §5 — New CLI command: `gt scaffold cicd --profile azure-enterprise`

Parallel to D1 specs, D2 adrs, D3 iac.

### §6 — Tests

`tests/test_azure_cicd_scaffold.py`:

- `test_scaffold_writes_expected_12_files` — exact path inventory.
- `test_scaffold_idempotent_on_second_run`.
- `test_scaffold_workflows_are_valid_yaml` — YAML parse all 4 workflows + both action files.
- `test_scaffold_composite_actions_have_correct_shape` — each `action.yml` has `runs.using == "composite"` and `runs.steps` list.
- `test_scaffold_no_step_level_workflow_call` — grep for `uses: ./.github/workflows/*.yml` at step level returns empty (workflow-vs-action-reuse invariant per F4).
- `test_scaffold_no_static_credentials` — grep for `secrets.AZURE_CREDENTIALS` returns empty.
- `test_scaffold_production_workflow_has_environment_gate` — parse `iac-apply-production.yml`, assert `apply` job has `environment: production`.
- `test_scaffold_workflows_use_tf_working_dir_var` — grep for `vars.TF_WORKING_DIR` in all 4 workflows confirms parameterization.
- `test_cli_scaffold_cicd_smoke` — CliRunner invocation exits 0.
- `test_scaffold_actionlint_clean` — run `actionlint` against scaffolded workflow files if the binary is available; skip otherwise.

### §7 — Documentation

New `docs/reference/azure-cicd-templates.md`:
- Overview of scaffold output (12 files).
- OIDC + Azure AD app registration walkthrough.
- GitHub Environment variable configuration.
- Relationship to D3 (default paths assume D3 tree; overridable via `vars.TF_WORKING_DIR`).
- `actionlint` verification recommendation.

## Inventory (exact per F4 discipline applied to D4)

```
.github/actions/azure-oidc-login/action.yml   # Composite action: federated login
.github/actions/deploy-evidence/action.yml    # Composite action: evidence capture
.github/workflows/iac-validate.yml            # On PR: terraform validate + plan + tfsec
.github/workflows/iac-apply-staging.yml       # On develop merge: plan → approval → staging apply
.github/workflows/iac-apply-production.yml    # On tag: plan → approval → production apply
.github/workflows/drift-detection.yml         # Scheduled daily: detect-only plan + issue on drift
.github/workflows/README.md                   # Workflow architecture overview
docs/azure/OWNER-APPROVAL.md                  # GH Environment approval rules template
docs/azure/federated-identity-setup.md        # Azure AD app + federated credential walkthrough
docs/azure/cicd-overview.md                   # Adopter architecture doc
docs/azure/drift-detection-runbook.md         # On-drift procedure
docs/azure/iac-working-dir-config.md          # TF_WORKING_DIR override guidance (F3 fix)
```

**Grand total: 12 files** (2 composite actions + 4 workflows + 1 workflow README + 5 docs).

## Files Touched (REVISED)

| File | Change kind | Est. delta |
|---|---|---|
| `src/groundtruth_kb/_azure_cicd_templates.py` (new) | 12 template descriptors | +~1,000 lines |
| `src/groundtruth_kb/cicd_scaffold.py` (new) | Scaffold orchestrator | +~100 lines |
| `src/groundtruth_kb/cli.py` | `scaffold_cicd` command | +~55 lines |
| `tests/test_azure_cicd_scaffold.py` (new) | 9 tests per §6 | +~300 lines |
| `docs/reference/azure-cicd-templates.md` (new) | Adopter docs | +~220 lines |

**Total: 3 new Python modules + 1 test + 1 doc + 1 CLI extension. Approx +1,675 lines. NO registry TOML changes, NO profile additions.**

## Non-Scope

- Azure DevOps Pipelines (DELIB-0827 GHA-only).
- D3 IaC content (parallel bridge; D4 now path-parameterized so doesn't hard-depend on D3 merge).
- Workflow execution / CI/CD runtime.
- Specific tenant/client IDs.
- Schema extension for registry.
- Upgrade / doctor drift for workflows.

## Verification Plan

```text
# Baseline
$ python -m pytest tests/test_azure_spec_scaffold.py tests/test_azure_adr_scaffold.py -q
# Expect pass.

# New D4 tests
$ python -m pytest tests/test_azure_cicd_scaffold.py -q
# Expect: 9 passed.

# Full suite
$ python -m pytest -q
# Expect: no regressions; +9 pass count.

# mypy strict
$ python -m mypy --strict src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py

# ruff check + format
$ python -m ruff check src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py tests/test_azure_cicd_scaffold.py

# YAML lint
$ yamllint <scaffolded .github/>

# GitHub Actions lint (F4 validation)
$ actionlint <scaffolded .github/workflows/*.yml>
# Expect: no errors. Proves composite-action usage is correct.

# OIDC + path-parameterization assertion
$ grep -r "secrets.AZURE_CREDENTIALS" <scaffolded>
# Expect: empty.

$ grep -c "vars.TF_WORKING_DIR" <scaffolded .github/workflows/*.yml>
# Expect: each workflow uses this variable.

# Step-level workflow-call invariant (F4 fix)
$ grep -r "uses: ./.github/workflows/" <scaffolded>
# Expect: NO matches at step level (only composite actions at step level).
```

## Implementation Sequence

1. Write 12 templates in `_azure_cicd_templates.py`:
   - 2 composite action files (`action.yml`)
   - 4 workflow files with `TF_WORKING_DIR` parameterization
   - 1 workflow README
   - 5 adopter doc files
2. Write `cicd_scaffold.py` orchestrator.
3. Wire CLI command.
4. Write 9 tests (including `actionlint` integration if available).
5. Write `docs/reference/azure-cicd-templates.md`.
6. Run scoped + full pytest; mypy --strict; ruff check + format.
7. Run `yamllint` + `actionlint` on scaffolded fixture.
8. Commit on `groundtruth-kb/main`: `feat(azure): D4 — GitHub Actions CI/CD + composite-action templates via gt scaffold cicd`.
9. Push to `origin/main`.
10. File post-impl report.

## Cross-NO-GO Discipline

| `-002` Finding | Resolution |
|---|---|
| F1 Registry schema | ✅ No registry involvement (mirror D1/D2/D3 scaffold-only) |
| F2 Project-init profile | ✅ `gt scaffold cicd` subcommand only (mirror D1/D2/D3) |
| F3 Hardcoded IaC path | ✅ `vars.TF_WORKING_DIR` parameterization with `iac/azure` default |
| F4 GHA reuse model invalid | ✅ Composite actions at `.github/actions/<name>/action.yml`, invoked from steps; reusable workflows at `.github/workflows/`, not step-invoked |

## Prior Deliberations

- DELIB-0827 (owner: Terraform + GHA + parallel).
- Codex `-002` NO-GO findings (D4).
- Codex `gtkb-azure-iac-skeleton-002.md` (D3 findings with matching structural issues).
- D1/D2/D3 REVISED-1 pattern references.

## Owner Decisions Required

None.

## Requested Verdict

**GO** to implement §1-§7 per the sequence, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
