NO-GO

# Loyal Opposition Verification - GT-KB Azure CI/CD Gates Post-Implementation

**Reviewed post-implementation report:** `bridge/gtkb-azure-cicd-gates-007.md`
**Reviewed GO:** `bridge/gtkb-azure-cicd-gates-006.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Verdict:** NO-GO

## Role Authority

- Effective role: Loyal Opposition
- Authority source path: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\.claude\rules\operating-role.md`
- Required durable role: `active_role: loyal-opposition`
- Observed durable role: `active_role: loyal-opposition`
- Scanner name: Codex automated Loyal Opposition bridge review scan

## Claim

The D4 Azure CI/CD scaffold implementation satisfies the mechanical scaffold,
test, type-check, lint, and actionlint conditions from the prior GO. However,
post-implementation verification cannot pass while the generated Azure
federated-identity setup guide gives a tag-ref subject for tag-gated
environment jobs. The generated production jobs declare GitHub environments, so
their Azure federated credential subjects must be environment subjects, not tag
subjects.

## Blocking Finding

### F1 - P1 - Scaffolded federated-identity docs can make production OIDC fail

The implementation correctly makes every OIDC-consuming job declare a GitHub
Environment, including the production tag workflow. The scaffolded
`docs/azure/federated-identity-setup.md` content then contradicts that contract
by saying tag-gated environments use `subject:
repo:<OWNER>/<REPO>:ref:refs/tags/v*` instead.

Evidence:
- Prior GO condition 5 required every job consuming GitHub Environment-level
  `vars.*` to declare a corresponding job `environment`:
  `bridge/gtkb-azure-cicd-gates-006.md:124-130`.
- The generated production workflow declares environment-gated plan/apply jobs:
  `src/groundtruth_kb/_azure_cicd_templates.py:224-273`.
- The generated drift workflow also declares `environment: production-plan`:
  `src/groundtruth_kb/_azure_cicd_templates.py:276-320`.
- The test suite enforces that every OIDC job has an environment:
  `tests/test_azure_cicd_scaffold.py:306-330`.
- The generated federated-identity setup doc first says the subject must match
  the workflow job environment, then tells tag-gated environments to use a tag
  ref subject: `src/groundtruth_kb/_azure_cicd_templates.py:442-460`.
- GitHub's OIDC reference states that an environment subject is used when a job
  references an environment, and that tag subjects apply only when the job does
  not reference an environment:
  <https://docs.github.com/en/actions/reference/security/oidc>.
- Microsoft Entra workload identity federation docs make the same split: jobs
  tied to an environment use `repo:<Organization/Repository>:environment:<Name>`;
  jobs not tied to an environment use branch/tag `ref` subjects:
  <https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-create-trust>.

Risk/impact:
- An adopter following the generated setup guide for the tag-triggered
  production workflow can create a federated credential that does not match the
  actual GitHub OIDC `sub` claim for jobs declaring `environment: production` or
  `environment: production-plan`.
- The resulting production plan/apply login can fail with "no matching
  federated identity record" even though the generated workflow syntax,
  environment gates, and actionlint checks pass.
- The `refs/tags/v*` example is also unsafe as default Entra federated identity
  guidance because ordinary explicit federated identity credential subjects are
  exact subject strings; wildcard-style matching belongs only in a separately
  documented flexible federated identity credential path.

Required action:
1. Update the generated `docs/azure/federated-identity-setup.md` content in
   `src/groundtruth_kb/_azure_cicd_templates.py` so all four generated
   environments (`staging-plan`, `staging`, `production-plan`, `production`)
   instruct adopters to create environment-subject credentials:
   `repo:<OWNER>/<REPO>:environment:<ENVIRONMENT_NAME>`.
2. If tag-ref credentials are documented at all, explicitly say they apply only
   to jobs that do not declare a GitHub `environment`, and do not use
   `refs/tags/v*` as an explicit federated credential subject.
3. Add a regression test in `tests/test_azure_cicd_scaffold.py` that scaffolds
   the docs and asserts the federated-identity guide does not contain
   `refs/tags/v*`, while it does contain the production environment subject
   pattern.
4. Re-run the same scoped verification commands and file a revised
   post-implementation report.

## Passing Evidence

The blocking finding is limited to generated setup documentation. The core
scaffold implementation and verification commands otherwise passed.

- D4 scaffold-only surface is present:
  `src/groundtruth_kb/_azure_cicd_templates.py`,
  `src/groundtruth_kb/cicd_scaffold.py`,
  `src/groundtruth_kb/cli.py`, and
  `tests/test_azure_cicd_scaffold.py`.
- The scaffold writer implements default dry-run and skip-if-exists semantics:
  `src/groundtruth_kb/cicd_scaffold.py:61-118`.
- The CLI exposes `gt scaffold cicd --profile azure-enterprise` without
  `--force`: `src/groundtruth_kb/cli.py:2594-2658`.
- The template catalog preserves the 12-path inventory:
  `src/groundtruth_kb/_azure_cicd_templates.py:653-737`.
- Direct inventory probe returned 12 paths and catalog equality `True`.
- Scoped D4 tests:
  `python -m pytest tests/test_azure_cicd_scaffold.py -q --tb=short`
  -> `26 passed, 1 skipped, 1 warning`.
- Azure scaffold baseline:
  `python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py tests/test_azure_iac_scaffold.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  -> `89 passed, 1 warning`.
- Type check:
  `python -m mypy --strict src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py`
  -> `Success: no issues found in 3 source files`.
- Lint:
  `python -m ruff check src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py tests/test_azure_cicd_scaffold.py`
  -> `All checks passed!`.
- Format check:
  `python -m ruff format --check src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py tests/test_azure_cicd_scaffold.py`
  -> `4 files already formatted`.
- Actionlint binary:
  `C:\Users\micha\AppData\Local\Temp\actionlint-1.7.12\actionlint.exe -version`
  -> `1.7.12`.
- Fresh temporary scaffold actionlint and probes:
  `python -m groundtruth_kb scaffold cicd --profile azure-enterprise --apply --target-dir <tmp>`;
  `git -C <tmp> init`;
  actionlint repo-root invocation `actionlint -no-color -shellcheck=`
  -> `actionlint_exit=0`,
  `env_azure_refs=0`,
  `id_token_files=4`,
  `inputs_client_id_count=1`,
  `workflow_step_calls=0`,
  `tf_working_dir_files=4`.
- Full suite:
  `python -m pytest -q --tb=short`
  -> `1618 passed, 1 skipped, 1 warning in 396.09s`.
- Scope guard:
  `rg -n 'class = "file"|azure-enterprise|azure_cicd|cicd' templates/managed-artifacts.toml src/groundtruth_kb/project/profiles.py src/groundtruth_kb/project/doctor.py src/groundtruth_kb/project/preflight.py`
  -> `NO_HITS`.

## Required Action Items

- Fix the generated federated-identity setup docs as described in F1.
- Add the proposed docs regression test.
- Re-run the scoped D4 tests, baseline scaffold tests, mypy, ruff check, ruff
  format check, actionlint, and full suite or an explicitly justified full-suite
  substitute.
- File a revised post-implementation bridge report.

## Decision Needed From Owner

None.
