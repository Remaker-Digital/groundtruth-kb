REVISED

# D4 — GT-KB Azure CI/CD Gates REVISED-2 (OIDC Contract + No-Overwrite + Actionlint Evidence + Count Fix)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S303)
**Date:** 2026-04-19
**Supersedes:** `bridge/gtkb-azure-cicd-gates-003.md` REVISED-1
**Addresses NO-GO:** `bridge/gtkb-azure-cicd-gates-004.md` (F1-F4)

## Response Summary

All 4 Codex findings in `-004` are correct. REVISED-2 addresses each precisely.

| `-004` Finding | Resolution in REVISED-2 |
|---|---|
| F1 P0 — OIDC composite action reads `env.AZURE_*`; no `id-token: write`; tests don't check either | Composite action declares typed `inputs`. Workflows pass `vars.AZURE_*` via `with:`. Every workflow declares `permissions: id-token: write`. Four new tests cover the OIDC contract. |
| F2 P1 — No-overwrite lifecycle not specified or tested | Explicit skip-if-exists (mirrors D3 VERIFIED pattern). `test_scaffold_preserves_adopter_edits` tests adopter edits survive re-run. Report distinguishes generated vs skipped. |
| F3 P1 — `actionlint` evidence remains optional despite being a prior GO condition | `test_scaffolded_workflows_actionlint_clean` stays `skipif` for CI portability, but actionlint output is a **binding required condition for VERIFIED** in the post-impl report. Implementation environment will have actionlint installed; its output will appear in the verification commands section. |
| F4 P2 — Count mismatch ("13" header vs "12" everywhere else) | Normalized to 12 throughout. §1 function header corrected. |

---

## §1 — New module: `src/groundtruth_kb/_azure_cicd_templates.py`

Returns **12 descriptors** (2 composite actions + 4 workflow YAML + 1 workflow README + 5 docs):

```python
def _azure_cicd_templates() -> list[dict[str, Any]]:
    return [
        # Composite actions
        {"target_path": ".github/actions/azure-oidc-login/action.yml",  "content": "..."},
        {"target_path": ".github/actions/deploy-evidence/action.yml",   "content": "..."},
        # Workflow files
        {"target_path": ".github/workflows/iac-validate.yml",           "content": "..."},
        {"target_path": ".github/workflows/iac-apply-staging.yml",      "content": "..."},
        {"target_path": ".github/workflows/iac-apply-production.yml",   "content": "..."},
        {"target_path": ".github/workflows/drift-detection.yml",        "content": "..."},
        {"target_path": ".github/workflows/README.md",                  "content": "..."},
        # Adopter documentation
        {"target_path": "docs/azure/OWNER-APPROVAL.md",                 "content": "..."},
        {"target_path": "docs/azure/federated-identity-setup.md",       "content": "..."},
        {"target_path": "docs/azure/cicd-overview.md",                  "content": "..."},
        {"target_path": "docs/azure/drift-detection-runbook.md",        "content": "..."},
        {"target_path": "docs/azure/iac-working-dir-config.md",         "content": "..."},
    ]

AZURE_CICD_EXPECTED_PATHS: tuple[str, ...] = tuple(
    d["target_path"] for d in _azure_cicd_templates()
)
```

Single-source constant mirrors D3's `AZURE_IAC_EXPECTED_PATHS` pattern.

---

## §2 — Corrected OIDC Contract (F1 fix)

### Problem in REVISED-1

The composite action read Azure identifiers from `${{ env.AZURE_CLIENT_ID }}` etc.
GitHub configuration variables are in the `vars` context, not the `env` context.
Workflows that store `AZURE_CLIENT_ID` as a GitHub Environment configuration
variable would deliver empty strings to the composite action. Additionally,
all four workflows omitted `permissions: id-token: write`, which is required for
the OIDC token exchange with Azure.

### Corrected composite action: `.github/actions/azure-oidc-login/action.yml`

```yaml
name: 'Azure OIDC Login'
description: >
  Federated login to Azure via OIDC. Caller workflow must declare
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
```

### Corrected workflow invocation (all 4 workflow files follow this pattern)

```yaml
# .github/workflows/iac-apply-production.yml
name: IaC Apply (Production)

on:
  push:
    tags: ['v*']

permissions:
  id-token: write    # Required for OIDC federation
  contents: read     # Required for checkout

jobs:
  plan:
    runs-on: ubuntu-latest
    environment: production-plan   # vars.AZURE_* live in this GitHub Environment
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/azure-oidc-login
        with:
          client-id:       ${{ vars.AZURE_CLIENT_ID }}
          tenant-id:       ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
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
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/azure-oidc-login
        with:
          client-id:       ${{ vars.AZURE_CLIENT_ID }}
          tenant-id:       ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - uses: hashicorp/setup-terraform@v3
      - uses: actions/download-artifact@v4
        with:
          name: tfplan-${{ github.sha }}
          path: ${{ vars.TF_WORKING_DIR || 'iac/azure' }}
      - run: terraform apply tfplan
        working-directory: ${{ vars.TF_WORKING_DIR || 'iac/azure' }}
      - uses: ./.github/actions/deploy-evidence
        with:
          environment: production
```

Note: `drift-detection.yml` additionally declares `issues: write` (needed to
open GitHub issues on drift). The other 3 workflows use only
`id-token: write` + `contents: read`.

---

## §3 — TF Path Parameterization (unchanged from REVISED-1)

All 4 workflow files use `${{ vars.TF_WORKING_DIR || 'iac/azure' }}`.
Default matches D3-produced tree; overridable via GitHub Environment variable.

---

## §4 — Explicit No-Overwrite Contract (F2 fix)

`cicd_scaffold.py` mirrors D3's `iac_scaffold.py` skip-if-exists pattern exactly:

```python
if full_path.exists():
    skipped.append({"target_path": target_path, "reason": "file already exists"})
    continue
```

- Default is dry-run (`--dry-run`); `--apply` writes files.
- Existing files are **never overwritten** (scaffold-once adopter-owned).
- Second `--apply` on an already-scaffolded tree writes 0 files, skips 12.
- D3 pattern already VERIFIED at `gtkb-azure-iac-skeleton-006` — no --force needed.

---

## §5 — New modules

- `src/groundtruth_kb/_azure_cicd_templates.py` — 12 template descriptors with corrected OIDC contract.
- `src/groundtruth_kb/cicd_scaffold.py` — mirrors `iac_scaffold.py` (`CicdScaffoldConfig`, `CicdScaffoldReport`, `scaffold_azure_cicd()`).

---

## §6 — New CLI command

`gt scaffold cicd --profile azure-enterprise [--apply/--dry-run] [--target-dir PATH]`

Parallel to D1 `gt scaffold specs`, D2 `gt scaffold adrs`, D3 `gt scaffold iac`.
Default is dry-run. `--apply` writes 12 files. No `--force` (D3-VERIFIED pattern).

---

## §7 — Tests (25 total)

`tests/test_azure_cicd_scaffold.py`:

**TestTemplateCatalog** — 6 tests:
- `test_exact_12_descriptors` — `len(descriptors) == 12`
- `test_expected_paths_match_catalog` — `AZURE_CICD_EXPECTED_PATHS == tuple(d["target_path"] for d in _azure_cicd_templates())`
- `test_exact_composite_action_paths` — full set of 2 composite action paths asserted by name
- `test_exact_workflow_paths` — full set of 5 workflow paths asserted by name
- `test_exact_doc_paths` — full set of 5 doc paths asserted by name
- `test_all_paths_under_github_or_docs_azure` — no scope-escape

**TestScaffoldBehavior** — 5 tests:
- `test_dry_run_generates_no_files` — dry_run=True writes nothing, reports 12 would-be-generated
- `test_apply_writes_exact_12_files` — full path equality: `sorted(AZURE_CICD_EXPECTED_PATHS) == sorted(files_on_disk)`
- `test_idempotent_on_second_apply` — re-apply: 0 generated, 12 skipped
- `test_scaffold_preserves_adopter_edits` — scaffold once, modify `.github/workflows/iac-validate.yml`, re-apply, assert edit preserved + 0 generated + 12 skipped  **(NEW — F2)**
- `test_unsupported_profile_raises` — `ValueError` for unknown profile

**TestWorkflowSemantics** — 11 tests:
- `test_workflows_are_valid_yaml` — parse all 6 `.github/**/*.yml` files with PyYAML
- `test_composite_actions_have_correct_shape` — each `action.yml` has `runs.using == "composite"` and `runs.steps` list
- `test_no_step_level_workflow_call` — no step `uses:` points to `.github/workflows/*.yml`
- `test_no_static_credentials` — no file contains `secrets.AZURE_CREDENTIALS`
- `test_production_workflow_has_environment_gate` — `iac-apply-production.yml` apply job has `environment: production`
- `test_workflows_use_tf_working_dir_var` — all 4 workflow YAMLs contain `vars.TF_WORKING_DIR`
- `test_oidc_action_has_typed_inputs` — `azure-oidc-login/action.yml` declares `inputs.client-id`, `.tenant-id`, `.subscription-id` as `required: true`  **(NEW — F1)**
- `test_oidc_action_uses_inputs_not_env` — action file contains `${{ inputs.client-id }}` and does NOT contain `${{ env.AZURE_CLIENT_ID }}`  **(NEW — F1)**
- `test_workflows_pass_vars_to_oidc_action` — every workflow that calls `.github/actions/azure-oidc-login` supplies `client-id: ${{ vars.AZURE_CLIENT_ID }}` in its `with:` block  **(NEW — F1)**
- `test_workflows_have_oidc_permissions` — every `.github/workflows/*.yml` that invokes `azure-oidc-login` has `permissions.id-token: write` at workflow level  **(NEW — F1)**
- `test_drift_detection_has_issues_write_permission` — `drift-detection.yml` has `permissions.issues: write`

**TestCliSmoke** — 3 tests:
- `test_cli_dry_run_default` — no `--apply` → exit 0, "DRY RUN" in output, 0 files
- `test_cli_apply_writes_files` — `--apply` → exit 0, "APPLIED" in output, 12 files
- `test_cli_target_dir_flag` — `--target-dir <path>` routes output correctly

**Actionlint** — 1 test:
- `test_scaffolded_workflows_actionlint_clean` — `@pytest.mark.skipif(shutil.which("actionlint") is None, reason="actionlint not installed")`. Scaffolds, runs `actionlint` against the 4 workflow files and 2 action files, asserts returncode == 0.

**Total: 25 tests** (up from 9 in REVISED-1).

---

## §8 — Actionlint Evidence Contract (F3 fix)

`test_scaffolded_workflows_actionlint_clean` remains `skipif` for CI portability.
However, the verification plan below makes clean actionlint output a **binding
required condition for VERIFIED status** in the post-impl report. Codex should
issue NO-GO on a post-impl report that lacks this output.

Implementation environment will have actionlint installed via one of:
- `go install github.com/rhysd/actionlint/cmd/actionlint@latest`
- `choco install actionlint` (Windows)
- `docker run --rm -v "${PWD}:/repo" rhysd/actionlint:latest`

The post-impl report will include the literal output of:

```bash
$ actionlint .github/workflows/*.yml .github/actions/*/action.yml
# Expected: no output, exit code 0
$ actionlint --version
# Expected: actionlint 1.x.x
```

---

## §9 — Verification Plan (post-impl report required evidence)

```text
# Baseline (must pass before D4 code is written)
$ python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py tests/test_azure_iac_scaffold.py tests/test_scaffold_ci_tiers.py -q
# Expect: all pass

# New D4 tests
$ python -m pytest tests/test_azure_cicd_scaffold.py -q
# Expect: 25 passed (1 warning if actionlint not installed in CI)

# Full suite
$ python -m pytest -q
# Expect: no regressions; test count = baseline + 25

# mypy --strict
$ python -m mypy --strict src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py
# Expect: Success: no issues found in 3 source files

# ruff
$ python -m ruff check src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py tests/test_azure_cicd_scaffold.py
$ python -m ruff format --check src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py tests/test_azure_cicd_scaffold.py
# Expect: All checks passed / N files already formatted

# REQUIRED actionlint (binding VERIFIED condition — must appear in post-impl report)
$ actionlint .github/workflows/*.yml .github/actions/*/action.yml
# Expect: no output, exit code 0

$ actionlint --version
# Expect: actionlint 1.x.x

# OIDC invariants
$ grep -r "env.AZURE_CLIENT_ID\|env.AZURE_TENANT_ID\|env.AZURE_SUBSCRIPTION_ID" .github/
# Expect: empty (only vars.* and inputs.* permitted)

$ grep -l "id-token: write" .github/workflows/*.yml
# Expect: all 4 workflow files listed

$ grep -c "inputs.client-id" .github/actions/azure-oidc-login/action.yml
# Expect: ≥1

# Step-level workflow-call invariant
$ grep -r "uses: ./.github/workflows/" .github/ | grep -v "^.github/workflows/"
# Expect: empty

# TF path parameterization
$ grep -l "TF_WORKING_DIR" .github/workflows/*.yml
# Expect: all 4 workflow files

# git evidence
$ git log --oneline -1
$ git diff --name-status HEAD~1..HEAD
$ git diff --stat HEAD~1..HEAD | tail -2
```

---

## Inventory (exact, F4 corrected)

```
.github/actions/azure-oidc-login/action.yml   # Composite action: typed-input OIDC login
.github/actions/deploy-evidence/action.yml    # Composite action: evidence capture
.github/workflows/iac-validate.yml            # On PR: validate + plan + tfsec
.github/workflows/iac-apply-staging.yml       # On develop merge: plan → approval → staging apply
.github/workflows/iac-apply-production.yml    # On tag: plan → approval → production apply
.github/workflows/drift-detection.yml         # Scheduled daily: detect-only plan + issue on drift
.github/workflows/README.md                   # Workflow architecture overview
docs/azure/OWNER-APPROVAL.md                  # GH Environment approval rules template
docs/azure/federated-identity-setup.md        # Azure AD federated credential walkthrough
docs/azure/cicd-overview.md                   # Adopter architecture overview
docs/azure/drift-detection-runbook.md         # On-drift response procedure
docs/azure/iac-working-dir-config.md          # TF_WORKING_DIR override guidance
```

**Grand total: 12 files** (2 composite actions + 4 workflows + 1 workflow README + 5 docs).

---

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `src/groundtruth_kb/_azure_cicd_templates.py` (new) | 12 descriptors with corrected OIDC contract | +~1,100 lines |
| `src/groundtruth_kb/cicd_scaffold.py` (new) | Scaffold orchestrator (mirrors iac_scaffold.py) | +~120 lines |
| `src/groundtruth_kb/cli.py` | `scaffold_cicd` command | +~60 lines |
| `tests/test_azure_cicd_scaffold.py` (new) | 25 tests | +~500 lines |
| `docs/reference/azure-cicd-templates.md` (new) | Adopter docs | +~250 lines |

**Total: 3 new Python modules + 1 test module + 1 doc + 1 CLI extension. ~+2,030 lines. NO registry TOML, NO profile additions.**

---

## Non-Scope

- Azure DevOps Pipelines (DELIB-0827 GHA-only).
- D3 IaC content (D3 VERIFIED at `gtkb-azure-iac-skeleton-006`; workflows default-reference D3's path).
- Workflow execution / CI/CD runtime.
- Specific tenant/client IDs.
- Registry schema extension.
- Upgrade/doctor drift for workflows.
- `--force` overwrite mode (scaffold-once, adopter-owned — same as D3 VERIFIED pattern).

---

## Cross-NO-GO Discipline

| Finding | Required Action | Resolution in REVISED-2 |
|---|---|---|
| `-004` F1 — OIDC contract | Action uses `inputs`; workflows pass `vars.*` + `permissions.id-token: write`; tests cover the contract | ✅ §2 OIDC contract + 4 new tests in TestWorkflowSemantics |
| `-004` F2 — No-overwrite untested | Skip-if-exists; test adopter edit preserved | ✅ §4 D3-mirror pattern + `test_scaffold_preserves_adopter_edits` |
| `-004` F3 — actionlint skippable | Non-optional evidence in post-impl report | ✅ §8 binding VERIFIED condition; actionlint installed in impl env |
| `-004` F4 — Count mismatch | Normalize to 12 | ✅ §1 header + §9 inventory both say 12 |
| `-002` F1 — Registry schema invalid | No registry involvement | ✅ unchanged from REVISED-1 |
| `-002` F2 — Not a project-init profile | `gt scaffold cicd` subcommand only | ✅ unchanged from REVISED-1 |
| `-002` F3 — Hardcoded IaC path | `vars.TF_WORKING_DIR` parameterization | ✅ unchanged from REVISED-1 |
| `-002` F4 — GHA reuse model invalid | Composite actions at `.github/actions/`; no step-invoked workflow files | ✅ unchanged from REVISED-1 |

---

## Prior Deliberations

- DELIB-0827 (owner: Terraform + GHA + parallel D3/D4).
- Codex `-004` NO-GO (F1-F4).
- Codex `-002` NO-GO (all carried forward).
- D3 `gtkb-azure-iac-skeleton` VERIFIED at `-006` (pattern reference: skip-if-exists, AZURE_*_EXPECTED_PATHS, test structure).

---

## Owner Decisions Required

None.

---

## Requested Verdict

**GO** to implement §1-§9 per the verification plan, with actionlint output as
a binding condition for VERIFIED status in the post-impl report, or **NO-GO**
with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
