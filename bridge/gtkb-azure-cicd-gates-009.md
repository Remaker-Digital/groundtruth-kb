REVISED

# GT-KB Azure CI/CD Gates Post-Implementation Revision

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Reviewed GO:** `bridge/gtkb-azure-cicd-gates-006.md`
**NO-GO addressed:** `bridge/gtkb-azure-cicd-gates-008.md`
**Target checkout updated:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

Prime Builder corrected the generated Azure federated-identity setup guide so
the scaffolded docs match the environment-declaring production workflows.

The generated guide now instructs adopters to create environment-subject
federated credentials for all four generated GitHub Environments:
`staging-plan`, `staging`, `production-plan`, and `production`. It no longer
uses `refs/tags/v*` as an explicit federated credential subject.

## Changes Made

- Updated `src/groundtruth_kb/_azure_cicd_templates.py` so
  `docs/azure/federated-identity-setup.md` lists:
  - `repo:<OWNER>/<REPO>:environment:staging-plan`
  - `repo:<OWNER>/<REPO>:environment:staging`
  - `repo:<OWNER>/<REPO>:environment:production-plan`
  - `repo:<OWNER>/<REPO>:environment:production`
- Kept tag-ref guidance only as a boundary note: tag-ref subjects apply only
  to jobs that do not declare a GitHub Environment.
- Added `tests/test_azure_cicd_scaffold.py::TestWorkflowSemantics::test_federated_identity_docs_use_environment_subjects`
  to scaffold the docs and assert:
  - `refs/tags/v*` is absent
  - all four environment subjects are present
  - the tag-ref boundary note is present

## NO-GO Finding Addressed

### F1 - Scaffolded federated-identity docs can make production OIDC fail

Addressed.

The generated production plan/apply jobs and drift detection jobs already
declare GitHub Environments. The generated setup guide now aligns with that
contract by requiring `repo:<OWNER>/<REPO>:environment:<ENVIRONMENT_NAME>`
subjects for the generated environments.

## Verification

- `python -m pytest tests/test_azure_cicd_scaffold.py -q --tb=short`
  -> 27 passed, 1 skipped, 1 warning.
- `python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py tests/test_azure_iac_scaffold.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  -> 89 passed, 1 warning.
- `python -m mypy --strict src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py`
  -> Success: no issues found in 3 source files.
- `python -m ruff check src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py tests/test_azure_cicd_scaffold.py`
  -> All checks passed.
- `python -m ruff format --check src/groundtruth_kb/_azure_cicd_templates.py src/groundtruth_kb/cicd_scaffold.py src/groundtruth_kb/cli.py tests/test_azure_cicd_scaffold.py`
  -> 4 files already formatted.
- Fresh temporary scaffold/actionlint/probe:
  `python -m groundtruth_kb scaffold cicd --profile azure-enterprise --apply --target-dir <tmp>`;
  `git init`; `actionlint -no-color -shellcheck=`
  -> `actionlint_exit=0`, `refs_tags_count=0`, `missing_subjects=0`,
  `id_token_files=4`, `env_azure_refs=0`.
- Full suite:
  `python -m pytest -q --tb=short`
  -> 1619 passed, 1 skipped, 1 warning in 434.59s.
- Scope guard:
  `rg -n 'class = "file"|azure-enterprise|azure_cicd|cicd' templates/managed-artifacts.toml src/groundtruth_kb/project/profiles.py src/groundtruth_kb/project/doctor.py src/groundtruth_kb/project/preflight.py`
  -> no hits.

Additional probe:

- A test-inclusive strict mypy command was tried and failed only on the known
  missing `types-PyYAML` stub for `yaml` in `tests/test_azure_cicd_scaffold.py`.
  The previously accepted D4 source-only strict mypy command passed.

## Decision Needed From Owner

None for this verification request.

File bridge scan: 0 entries processed.
