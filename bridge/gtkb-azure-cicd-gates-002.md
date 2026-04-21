NO-GO

# Loyal Opposition Review - GT-KB Azure CI/CD Gates

**Reviewed proposal:** `bridge/gtkb-azure-cicd-gates-001.md`  
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`  
**Verdict:** NO-GO

## Claim

The D4 objective is directionally aligned with the verified Azure taxonomy:
CI/CD readiness includes OIDC federation, IaC validation, environment approval
gates, drift detection, and deploy evidence artifacts. However, the proposal is
not yet executable against the current GT-KB project scaffold and managed
artifact contracts. It relies on an unsupported project profile, an unsupported
registry class, an unresolved IaC path dependency, and invalid GitHub Actions
reuse syntax.

## Findings

### F1 - P0 - Proposed managed-artifact records are invalid under the current registry schema

The proposal says all 11 D4 files will be added to
`templates/managed-artifacts.toml` as `class_="file"` artifacts with
`initial_profiles = ["azure-enterprise"]`, `managed_profiles =
["azure-enterprise"]`, and `upgrade_policy = "structured-merge"`.

Evidence:
- Proposal registry contract: `bridge/gtkb-azure-cicd-gates-001.md:131-139`.
- Current managed registry only accepts these artifact classes:
  `hook`, `rule`, `skill`, `settings-hook-registration`,
  `gitignore-pattern`, and `ownership-glob`:
  `src/groundtruth_kb/project/managed_registry.py:75-83`.
- Current file-backed artifact rows are narrowed to `hook`, `rule`, and
  `skill`, not generic `file`: `src/groundtruth_kb/project/managed_registry.py:88`,
  `src/groundtruth_kb/project/managed_registry.py:136-149`,
  `src/groundtruth_kb/project/managed_registry.py:466-496`.
- Parser dispatch rejects unknown classes before scaffold/upgrade can run:
  `src/groundtruth_kb/project/managed_registry.py:601-620`.
- Probe command against the target checkout:
  `python` synthetic `_parse_record({"class": "file", ...})` returned
  `UnknownArtifactClass: record 'file.azure-ci': unknown class 'file'`.
- Baseline registry/CI tests pass before D4:
  `python -m pytest tests/test_managed_registry.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  returned `49 passed, 1 warning`.

Risk/impact:
- Adding the proposed TOML rows literally will break registry loading before
  the new templates can be scaffolded, upgraded, or tested.
- Updating `tests/test_managed_registry.py` counts without changing the schema
  will not make the rows valid.

Required action:
- Either add a complete generic `file` artifact class to
  `managed_registry.py`, scaffold, upgrade, doctor, tests, and docs; or do not
  route these CI templates through `managed-artifacts.toml`.
- If D4 should use the existing CI scaffold tier system instead, revise the
  proposal to integrate with `_copy_ci_templates()` and the existing
  `templates/ci/{minimal,standard,full}` contract instead of declaring
  unsupported registry rows.

### F2 - P0 - `azure-enterprise` is not a `gt project init` profile

The proposal frames D4 as GitHub Actions templates for the `azure-enterprise`
profile and its end-to-end verification plan expects
`gt project init test-proj --profile azure-enterprise` to produce six workflow
files.

Evidence:
- Proposal scope and verification plan:
  `bridge/gtkb-azure-cicd-gates-001.md:15-21`,
  `bridge/gtkb-azure-cicd-gates-001.md:207-210`.
- Current `gt project init --profile` choices are only `local-only`,
  `dual-agent`, and `dual-agent-webapp`: `src/groundtruth_kb/cli.py:565-572`.
- Current project profile registry defines only those same three profiles:
  `src/groundtruth_kb/project/profiles.py:23-61`.
- Unknown project profiles are rejected by `get_profile()`:
  `src/groundtruth_kb/project/profiles.py:64-69`.
- Probe command against the target checkout:
  `get_profile("azure-enterprise")` returned
  `ValueError: Unknown profile 'azure-enterprise'. Valid profiles: dual-agent, dual-agent-webapp, local-only`.
- `azure-enterprise` currently exists as a spec scaffold and ADR scaffold
  profile, not as a project scaffold profile:
  `src/groundtruth_kb/cli.py:1779-1788`,
  `src/groundtruth_kb/cli.py:1863-1868`.
- The taxonomy explicitly says reference scaffolds must be starter defaults or
  gated by an explicit profile selection:
  `docs/reference/azure-readiness-taxonomy.md:90-102`.

Risk/impact:
- Prime could implement the templates and tests but leave no valid adopter
  entry point for `gt project init --profile azure-enterprise`.
- If `azure-enterprise` is added only to registry row profiles, those rows will
  not become reachable from project scaffold code because `get_profile()` still
  rejects the profile.

Required action:
- Choose and specify the delivery surface:
  1. add a real `azure-enterprise` project profile with CLI choice, manifest,
     scaffold, upgrade, doctor, docs, and tests; or
  2. add a separate command such as `gt scaffold ci --profile azure-enterprise`;
     or
  3. gate Azure CI templates behind an existing project profile plus
     `cloud_provider="azure"`.
- Update the verification plan to exercise the selected reachable command.

### F3 - P0 - The proposed workflows depend on an unresolved IaC path contract

The production example runs Terraform from `iac/azure`, uploads
`iac/azure/tfplan`, and applies `iac/azure/tfplan`. The proposal explicitly
keeps D3 IaC template content out of D4 scope while saying D3 is a parallel
sibling.

Evidence:
- D4 production example uses `working-directory: iac/azure` and artifact path
  `iac/azure/tfplan`: `bridge/gtkb-azure-cicd-gates-001.md:79-86`,
  `bridge/gtkb-azure-cicd-gates-001.md:102-113`.
- D4 non-scope excludes D3 IaC content:
  `bridge/gtkb-azure-cicd-gates-001.md:168-170`.
- The current Agent Red bridge state does not show D3
  `gtkb-azure-iac-skeleton` as GO-approved/resolved. During this review it
  moved from `NO-GO` to a newer `REVISED` line, which is still an actionable
  review state rather than an approved path contract:
  `bridge/INDEX.md:179-182`.
- Current GT-KB project scaffold's existing cloud stub path is
  `infrastructure/terraform`, not `iac/azure`:
  `src/groundtruth_kb/project/scaffold.py:538-547`,
  `src/groundtruth_kb/project/scaffold.py:820-835`.
- Current checkout has no `templates/ci/azure`, no `iac/azure`, and no
  `templates/infrastructure/terraform` directory:
  `Test-Path templates/ci/azure; Test-Path iac/azure; Test-Path templates/infrastructure/terraform`
  returned `False`, `False`, `False`.

Risk/impact:
- D4 could generate workflows that fail immediately for current adopters
  because their scaffolded Terraform tree is elsewhere or absent.
- Parallelizing D3 and D4 is reasonable only if D4 does not hard-code D3 paths
  before D3's approved contract exists.

Required action:
- Either make D4 conditional on an approved D3 path contract, or parameterize
  the Terraform working directory in the workflow templates and tests.
- Add a scaffold integration test that creates the selected Azure project shape
  and proves every workflow's Terraform paths exist in that scaffold.

### F4 - P1 - The GitHub Actions reuse model in the proposal is invalid

The proposal says `deploy-evidence.yml` is a reusable workflow using
`workflow_call`, but the example invokes it inside a step with
`uses: ./.github/workflows/deploy-evidence.yml`. It also describes
`azure-oidc-login.yml` under `templates/ci/azure/workflows/` as a "Reusable
composite action."

Evidence:
- Proposal tree describes `workflows/azure-oidc-login.yml` as a reusable
  composite action: `bridge/gtkb-azure-cicd-gates-001.md:26-34`.
- Proposal example invokes `deploy-evidence.yml` from within a job step:
  `bridge/gtkb-azure-cicd-gates-001.md:108-113`.
- Proposal states `deploy-evidence.yml` is a reusable workflow:
  `bridge/gtkb-azure-cicd-gates-001.md:116-119`.
- GitHub Actions documentation says reusable workflows are called directly
  within a job with `jobs.<job_id>.uses`, not from job steps:
  <https://docs.github.com/en/actions/sharing-automations/reusing-workflows>.
- GitHub Actions documentation says composite/custom actions require an
  action metadata file named `action.yml` or `action.yaml`, and local
  composite actions are referenced by the folder containing that metadata:
  <https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax>,
  <https://docs.github.com/actions/creating-actions/creating-a-composite-action>.

Risk/impact:
- `actionlint` should reject the example shape once implemented.
- Even if the YAML parses, the reusable workflow/composite action split is
  wrong and adopters will get broken automation.

Required action:
- Decide for each shared unit whether it is a reusable workflow or a composite
  action.
- If reusable workflow: place it under `.github/workflows/*.yml` and invoke it
  at job level with `jobs.<job_id>.uses`.
- If composite action: place it under `.github/actions/<name>/action.yml` and
  invoke the action directory from a step.
- Keep `actionlint templates/ci/azure/workflows/*.yml` in the verification
  plan and add a test/assertion that catches step-level calls to
  `.github/workflows/*.yml`.

## Conditions For GO

1. Revise the registry plan so it uses a supported schema or proposes the full
   schema expansion required for generic file artifacts.
2. Define a reachable D4 adopter entry point and update CLI/profile/docs/tests
   accordingly.
3. Resolve the Terraform path dependency with D3 before hard-coding
   `iac/azure`, or make D4 path-configurable and test it against the current
   scaffold.
4. Correct the GitHub Actions reuse model and prove it with `actionlint`.
5. Preserve the taxonomy boundary: GT-KB may ship reference templates, but the
   customer's deployed pipeline remains adopter-owned per
   `docs/reference/azure-readiness-taxonomy.md:65-74`.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-azure-cicd-gates` and the
  referenced version file `bridge/gtkb-azure-cicd-gates-001.md`.
- Inspected `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.
- Ran:
  `python -m pytest tests/test_managed_registry.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  -> `49 passed, 1 warning`.
- Ran probe:
  `get_profile("azure-enterprise")`
  -> `ValueError: Unknown profile 'azure-enterprise'. Valid profiles: dual-agent, dual-agent-webapp, local-only`.
- Ran probe:
  synthetic `_parse_record({"class": "file", ...})`
  -> `UnknownArtifactClass: record 'file.azure-ci': unknown class 'file'`.

## Decision Needed From Owner

None for this review. Prime needs to revise the D4 proposal before
implementation.
