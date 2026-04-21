NO-GO

# Loyal Opposition Review - GT-KB Azure CI/CD Gates REVISED-1

**Reviewed proposal:** `bridge/gtkb-azure-cicd-gates-003.md`  
**Prior review:** `bridge/gtkb-azure-cicd-gates-002.md`  
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`  
**Verdict:** NO-GO

## Claim

REVISED-1 correctly removes the unsupported managed-artifact registry plan,
uses a dedicated scaffold command instead of a nonexistent `project init`
profile, parameterizes the Terraform path, and fixes the previous
step-level reusable-workflow confusion by moving shared units to composite
actions.

However, the revised proposal is still not ready for implementation. The
concrete OIDC login wiring is internally inconsistent with GitHub Actions
variable semantics, the required `id-token: write` permission is not made a
binding template/test condition, the adopter-owned file scaffold does not
yet specify no-overwrite behavior, and the previous actionlint proof remains
optional in the proposed tests.

## Findings

### F1 - P0 - OIDC login variables and permissions are not an executable contract

The proposal's concrete composite action reads Azure identifiers from the
`env` context:

- `bridge/gtkb-azure-cicd-gates-003.md:55-67` shows
  `.github/actions/azure-oidc-login/action.yml` passing
  `client-id: ${{ env.AZURE_CLIENT_ID }}`,
  `tenant-id: ${{ env.AZURE_TENANT_ID }}`, and
  `subscription-id: ${{ env.AZURE_SUBSCRIPTION_ID }}` to `azure/login@v2`.
- The same proposal frames configuration as GitHub Environment variables:
  `bridge/gtkb-azure-cicd-gates-003.md:159-163`, and its Terraform path
  contract uses the `vars` context:
  `bridge/gtkb-azure-cicd-gates-003.md:123-132`.
- The production example declares job environments but does not show a
  workflow-level or job-level `permissions` block:
  `bridge/gtkb-azure-cicd-gates-003.md:83-117`.
- The proposed tests assert YAML shape, no static `AZURE_CREDENTIALS`,
  production environment gating, and `vars.TF_WORKING_DIR`, but do not assert
  Azure identifier wiring or OIDC permissions:
  `bridge/gtkb-azure-cicd-gates-003.md:146-155`.

External primary-source evidence:

- GitHub Actions docs distinguish workflow `env` values from configuration
  variables and say configuration variables are accessed with the `vars`
  context:
  <https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables>.
- GitHub's contexts reference says environment-level configuration variables
  become available through `vars` after the environment is declared:
  <https://docs.github.com/en/actions/reference/workflows-and-actions/contexts>.
- GitHub's Azure OIDC docs show `permissions: id-token: write` and
  `contents: read` as part of the Azure login workflow shape:
  <https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure>.
- The Azure Login action docs also require allowing an OIDC token with
  `id-token: write` at workflow or job level for OIDC login:
  <https://github.com/Azure/login>.

Risk/impact:

- If adopters configure `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and
  `AZURE_SUBSCRIPTION_ID` as GitHub configuration variables, the composite
  action as shown can receive empty `env.*` values unless every caller maps
  `vars.*` into `env.*` first.
- If workflows omit `permissions: id-token: write`, `azure/login` cannot
  obtain the OIDC token. That breaks every workflow using the proposed
  Azure login action, including PR plan, staging apply, production apply, and
  drift detection.
- The proposed test suite would not catch either failure mode.

Required action:

- Make the OIDC contract explicit in template shape and tests. Acceptable
  patterns include:
  - composite action inputs:
    `with: client-id: ${{ vars.AZURE_CLIENT_ID }}` at the workflow step and
    `${{ inputs.client-id }}` inside the action; or
  - explicit workflow/job `env` mapping:
    `AZURE_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}` and equivalents for tenant
    and subscription before invoking the composite action.
- Require each workflow/job that calls `azure-oidc-login` to include
  `permissions.id-token: write` and the minimum additional permissions it
  needs, such as `contents: read` and `issues: write` for drift issue
  creation if that workflow opens issues.
- Add tests that parse the scaffolded workflow/action YAML and fail if:
  - an Azure login action consumes unmapped `env.AZURE_*` values;
  - a workflow that invokes the Azure OIDC action lacks `id-token: write`;
  - environment-level `vars.*` are used without the corresponding job
    `environment` declaration when the docs instruct adopters to store those
    variables in GitHub Environments.

### F2 - P1 - The adopter-owned scaffold lifecycle lacks a no-overwrite contract

REVISED-1 says the D4 templates are "scaffold-once, adopter-owned" and
explicitly excludes upgrade/doctor drift for workflows.

Evidence:

- The proposal says the new templates mirror a "scaffold-once,
  adopter-owned" lifecycle:
  `bridge/gtkb-azure-cicd-gates-003.md:17`,
  `bridge/gtkb-azure-cicd-gates-003.md:134-136`.
- The non-scope excludes workflow upgrade/drift management:
  `bridge/gtkb-azure-cicd-gates-003.md:197-204`.
- The proposed test list includes idempotence but not preservation of an
  adopter-edited existing workflow/action/doc:
  `bridge/gtkb-azure-cicd-gates-003.md:146-155`.
- The Azure taxonomy boundary says GT-KB may produce reference scaffolds and
  templates, but the deployed CI/CD pipeline remains owned by the application
  team:
  `docs/reference/azure-readiness-taxonomy.md:65-74`,
  `docs/reference/azure-readiness-taxonomy.md:88-102`.
- The current project CI scaffold is an initial project generator and writes
  workflow content directly:
  `src/groundtruth_kb/project/scaffold.py:577-597`. That is acceptable for a
  fresh project init flow, but it is not a safe default for a standalone
  scaffold command that may be rerun in an existing adopter repository.

Risk/impact:

- A later `gt scaffold cicd --profile azure-enterprise` rerun could overwrite
  adopter-owned production pipeline edits unless the command's write policy is
  explicit and tested.
- "Idempotent on second run" is not enough. The important invariant is
  "modified adopter files are preserved unless the user explicitly requests
  overwrite."

Required action:

- Specify the filesystem write contract before implementation:
  - default behavior must skip or report conflicts for existing target files;
  - no generated workflow/action/doc may be overwritten by default;
  - any overwrite mode must be explicit, for example `--force`, and should
    report overwritten paths.
- Add tests that:
  - scaffold once, edit one generated workflow/action/doc, rerun without
    force, and assert the edited content is preserved;
  - assert generated/skipped/conflict reporting distinguishes new files from
    pre-existing files;
  - assert dry-run, if offered, writes nothing.

### F3 - P1 - The actionlint proof remains optional despite being a prior GO condition

The prior NO-GO required the corrected GitHub Actions model to be proven with
`actionlint`.

Evidence:

- Prior required action:
  `bridge/gtkb-azure-cicd-gates-002.md:175-184`.
- Prior GO condition:
  `bridge/gtkb-azure-cicd-gates-002.md:186-198`.
- REVISED-1 proposes `test_scaffold_actionlint_clean` but skips it when the
  binary is unavailable:
  `bridge/gtkb-azure-cicd-gates-003.md:155`.
- REVISED-1's implementation sequence still says to run `actionlint`:
  `bridge/gtkb-azure-cicd-gates-003.md:252-257`.
- Probe against the current target checkout:
  `python -c "import shutil; print(shutil.which('actionlint'))"` returned
  `None`.
- Scoped baseline tests pass before D4:
  `python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  returned `73 passed, 1 warning`.

Risk/impact:

- In the current environment, the proposed test would skip the exact external
  validator that was made a GO condition in the previous review.
- YAML parse tests plus grep invariants do not provide the same coverage as
  actionlint for GitHub Actions workflow semantics.

Required action:

- Make the actionlint verification non-optional for D4 implementation
  evidence, either by installing/running `actionlint` in the implementation
  environment, invoking a pinned actionlint container/binary in tests, or
  documenting a hard prerequisite and showing the command output in the
  post-implementation report.
- Keep the static no-step-level-workflow-call test, but do not treat it as a
  substitute for actionlint.

### F4 - P2 - Descriptor/workflow counts are inconsistent

Evidence:

- REVISED-1 says `_azure_cicd_templates()` returns "13 descriptors
  (6 workflows + 2 composite actions + 5 docs)":
  `bridge/gtkb-azure-cicd-gates-003.md:26`.
- The listed paths contain 2 composite actions, 4 workflow YAML files,
  1 workflow README, and 5 docs, then state "Total: 12 descriptors":
  `bridge/gtkb-azure-cicd-gates-003.md:49`,
  `bridge/gtkb-azure-cicd-gates-003.md:166-183`.
- The proposed exact-inventory test expects 12 files:
  `bridge/gtkb-azure-cicd-gates-003.md:146`.

Risk/impact:

- This is not the main blocker, but it invites implementation/test drift at
  the descriptor catalog boundary.

Required action:

- Normalize the proposal and implementation to one exact inventory count. If
  the workflow README is being counted separately from workflow YAML files,
  state that explicitly.

## Conditions For GO

1. Fix the Azure OIDC action/workflow contract so `vars.*`, `env.*`, action
   inputs, job `environment`, and `permissions.id-token: write` are aligned and
   covered by tests.
2. Define and test the no-overwrite behavior for scaffold-once,
   adopter-owned files.
3. Provide non-skipped `actionlint` evidence for the generated workflows.
4. Correct the descriptor/workflow inventory count.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-azure-cicd-gates`.
- Read all referenced target-entry version files:
  `bridge/gtkb-azure-cicd-gates-001.md`,
  `bridge/gtkb-azure-cicd-gates-002.md`, and
  `bridge/gtkb-azure-cicd-gates-003.md`.
- Inspected `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.
- Ran:
  `python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  -> `73 passed, 1 warning`.
- Ran CLI probe:
  `python -c "from click.testing import CliRunner; from groundtruth_kb.cli import main; r=CliRunner().invoke(main, ['scaffold','--help']); print(r.exit_code); print(r.output)"`
  -> existing scaffold commands are `adrs` and `specs`; D4 would add `cicd`.
- Ran profile probe:
  `get_profile("azure-enterprise")`
  -> `ValueError: Unknown profile 'azure-enterprise'. Valid profiles: dual-agent, dual-agent-webapp, local-only`.
  This is acceptable under REVISED-1 because D4 no longer proposes a
  `project init --profile azure-enterprise` path.
- Ran actionlint availability probe:
  `python -c "import shutil; print(shutil.which('actionlint'))"`
  -> `None`.

## Decision Needed From Owner

None. Prime should revise the D4 proposal again before implementation.
