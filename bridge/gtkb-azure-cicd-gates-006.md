GO

# Loyal Opposition Review - GT-KB Azure CI/CD Gates REVISED-2

**Reviewed proposal:** `bridge/gtkb-azure-cicd-gates-005.md`  
**Prior reviews:** `bridge/gtkb-azure-cicd-gates-002.md`, `bridge/gtkb-azure-cicd-gates-004.md`  
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`  
**Verdict:** GO, with implementation/verification conditions below.

## Claim

REVISED-2 resolves the blocking findings from the prior two NO-GO reviews and
is ready for implementation as a scaffold-only, adopter-owned Azure CI/CD
template track.

The proposal now avoids the unsupported managed-artifact registry path, avoids
adding `azure-enterprise` to `gt project init`, aligns the CI/CD default
Terraform path with the now-verified D3 `iac/azure` scaffold while keeping it
overridable, uses composite actions correctly, defines no-overwrite behavior,
and makes actionlint evidence a binding post-implementation condition.

## Evidence

### Prior blocking issues are addressed

- Registry/schema issue from `-002` is removed. REVISED-2 lists only a Python
  template catalog, a scaffold orchestrator, a CLI command, tests, and docs:
  `bridge/gtkb-azure-cicd-gates-005.md:184-197`,
  `bridge/gtkb-azure-cicd-gates-005.md:345-355`.
- Project profile issue from `-002` is removed. REVISED-2 proposes
  `gt scaffold cicd --profile azure-enterprise`, parallel to existing
  `gt scaffold specs`, `gt scaffold adrs`, and `gt scaffold iac`:
  `bridge/gtkb-azure-cicd-gates-005.md:191-196`.
- The current target checkout already has the D3 scaffold command pattern that
  D4 intends to mirror:
  `src/groundtruth_kb/cli.py:1923`,
  `src/groundtruth_kb/cli.py:1934`,
  `src/groundtruth_kb/cli.py:1944`.
- D3's verified target tree is `iac/azure`, matching D4's default
  `TF_WORKING_DIR` fallback:
  `src/groundtruth_kb/_azure_iac_templates.py:426`,
  `src/groundtruth_kb/_azure_iac_templates.py:440-445`,
  `src/groundtruth_kb/_azure_iac_templates.py:459`.
- Current scoped baseline in the target checkout passed:
  `python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py tests/test_azure_iac_scaffold.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  -> `89 passed, 1 warning`.

### OIDC contract is now coherent enough to implement

- The composite action now accepts typed inputs rather than reading unmapped
  `env.AZURE_*` values:
  `bridge/gtkb-azure-cicd-gates-005.md:68-94`.
- Workflows pass GitHub configuration variables through `with:`:
  `bridge/gtkb-azure-cicd-gates-005.md:116-120`,
  `bridge/gtkb-azure-cicd-gates-005.md:137-141`.
- Workflows declare the required OIDC permission at workflow level:
  `bridge/gtkb-azure-cicd-gates-005.md:106-108`.
- The drift workflow is required to add `issues: write` for issue creation:
  `bridge/gtkb-azure-cicd-gates-005.md:154-156`.
- Proposed tests now cover typed inputs, no `env.AZURE_*` consumption,
  `vars.AZURE_*` forwarding, `permissions.id-token: write`, and
  `issues: write` for drift detection:
  `bridge/gtkb-azure-cicd-gates-005.md:226-230`.

### No-overwrite lifecycle now matches the verified D3 pattern

- REVISED-2 explicitly states default dry-run, `--apply` writes, and existing
  files are never overwritten:
  `bridge/gtkb-azure-cicd-gates-005.md:167-180`.
- The current D3 implementation checks `full_path.exists()` before any write
  and skips existing files:
  `src/groundtruth_kb/iac_scaffold.py:97-111`.
- D3 tests already verify a modified adopter file survives re-apply:
  `tests/test_azure_iac_scaffold.py:127-143`.
- REVISED-2 adds the equivalent D4 test:
  `bridge/gtkb-azure-cicd-gates-005.md:212-217`.

### Actionlint is correctly made a binding verification condition, but use a supported invocation

- REVISED-2 makes clean actionlint output a required condition for VERIFIED:
  `bridge/gtkb-azure-cicd-gates-005.md:244-263`,
  `bridge/gtkb-azure-cicd-gates-005.md:291-296`.
- On this verification machine, `python -c "import shutil; print(shutil.which('actionlint'))"`
  returned `None`.
- `go version` failed because Go is not installed.
- `docker --version` returned `Docker version 29.2.1, build a5c7197`, but
  `docker run --rm rhysd/actionlint:latest -version` failed because the Docker
  daemon is not running.
- Current actionlint usage documentation says no-argument actionlint detects
  workflow files, and positional file arguments are YAML workflow files:
  <https://raw.githubusercontent.com/rhysd/actionlint/main/docs/usage.md>.
- Current actionlint release notes show action metadata support exists, but it
  is tied to actionlint's workflow/local-action analysis rather than treating
  composite action metadata as ordinary workflow files:
  <https://github.com/rhysd/actionlint/releases>.

Risk/impact:
- The proposal's literal command
  `actionlint .github/workflows/*.yml .github/actions/*/action.yml` may ask
  actionlint to parse composite action metadata as workflow YAML. That is not
  the supported usage shape.

Required implementation condition:
- Keep actionlint as non-optional post-implementation evidence, but run it in
  a supported form: either `actionlint` from the scaffolded repo root or
  `actionlint .github/workflows/*.yml`. Local composite action metadata should
  be validated through workflows that reference those local actions, plus the
  proposed PyYAML/action-shape tests for `action.yml`.

## GO Conditions

1. Keep D4 scaffold-only: no `templates/managed-artifacts.toml`, no
   `project/profiles.py`, no upgrade/doctor lifecycle, and no `--force`
   overwrite mode.
2. Preserve the exact 12-path inventory from REVISED-2 and test path equality
   against `AZURE_CICD_EXPECTED_PATHS`.
3. Implement skip-if-exists semantics exactly: default dry-run writes nothing;
   `--apply` writes only missing files; existing adopter-edited files are
   reported as skipped and preserved byte-for-byte.
4. Keep the OIDC contract explicit: composite action inputs only, workflows
   pass `vars.AZURE_*`, no `env.AZURE_*` consumption, each workflow invoking
   Azure OIDC has `permissions.id-token: write`, and drift detection has
   `issues: write`.
5. For jobs that consume GitHub Environment-level `vars.*`, declare the
   corresponding job `environment` and add a test that every job invoking
   `.github/actions/azure-oidc-login` has an environment when the docs instruct
   adopters to configure those variables in GitHub Environments.
6. Post-implementation verification must include non-skipped actionlint
   evidence with `actionlint --version` and a supported actionlint invocation
   (`actionlint` from repo root or workflow-file arguments only).
7. Run and report the proposed pytest, mypy, ruff check, and ruff format
   commands. A skipped in-suite actionlint test is acceptable only if the
   separate post-implementation actionlint command output is present.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-azure-cicd-gates`.
- Read all referenced target-entry version files:
  `bridge/gtkb-azure-cicd-gates-001.md`,
  `bridge/gtkb-azure-cicd-gates-002.md`,
  `bridge/gtkb-azure-cicd-gates-003.md`,
  `bridge/gtkb-azure-cicd-gates-004.md`, and
  `bridge/gtkb-azure-cicd-gates-005.md`.
- Inspected `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.
- Ran:
  `python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py tests/test_azure_iac_scaffold.py tests/test_scaffold_ci_tiers.py -q --tb=short`
  -> `89 passed, 1 warning`.
- Ran CLI probe:
  `python -c "from click.testing import CliRunner; from groundtruth_kb.cli import main; r=CliRunner().invoke(main, ['scaffold','--help']); print(r.exit_code); print(r.output)"`
  -> exit `0`; current scaffold commands are `adrs`, `iac`, and `specs`.
- Ran D3 path probe:
  `python -c "from groundtruth_kb._azure_iac_templates import AZURE_IAC_EXPECTED_PATHS; print(len(AZURE_IAC_EXPECTED_PATHS)); print(AZURE_IAC_EXPECTED_PATHS[:6])"`
  -> `45` and top-level paths under `iac/azure/`.
- Ran actionlint availability probe:
  `python -c "import shutil; print(shutil.which('actionlint'))"`
  -> `None`.
- Ran `go version`
  -> Go is not installed.
- Ran `docker --version`
  -> Docker CLI is installed.
- Ran `docker run --rm rhysd/actionlint:latest -version`
  -> failed because the Docker daemon is not running.

## Decision Needed From Owner

None. Prime may implement D4 under the GO conditions above.
