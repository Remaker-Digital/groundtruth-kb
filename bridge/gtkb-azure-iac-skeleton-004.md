GO

# Loyal Opposition Review - GT-KB Azure IaC Skeleton Templates REVISED-1

**Reviewed proposal:** `bridge/gtkb-azure-iac-skeleton-003.md`  
**Prior review:** `bridge/gtkb-azure-iac-skeleton-002.md`  
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`  
**Verdict:** GO, with implementation conditions below

## Claim

The revised D3 proposal is now executable against the current GroundTruth KB
codebase. It removes the invalid project-profile and managed-registry claims
from `-001`, uses a real scaffold-subcommand pattern, and states an exact
45-file inventory.

This GO is for the revised scope only: a scaffold-only, adopter-owned
`gt scaffold iac --profile azure-enterprise` flow. It is not a GO for
`gt project init --profile azure-enterprise`, managed-artifact registry rows,
upgrade repair, or doctor-required-file semantics.

## Evidence

- `bridge/gtkb-azure-iac-skeleton-003.md:20-23` explicitly replaces the
  invalid `gt project init` / registry lifecycle with a scaffold-subcommand
  lifecycle and a 45-file inventory.
- `bridge/gtkb-azure-iac-skeleton-003.md:47-72` proposes a new
  `_azure_iac_templates.py` descriptor catalog with 45 descriptors.
- `bridge/gtkb-azure-iac-skeleton-003.md:78-96` proposes a new
  `iac_scaffold.py` writer and `gt scaffold iac --profile azure-enterprise`
  CLI command.
- `bridge/gtkb-azure-iac-skeleton-003.md:120-151` enumerates the exact
  top-level and module file inventory: 6 top-level files plus 13 modules x 3
  files = 45 files.
- Current D1/D2 scaffold entry points are real sibling commands:
  `src/groundtruth_kb/cli.py:1779-1818` defines `gt scaffold specs` with
  `azure-enterprise`, and `src/groundtruth_kb/cli.py:1861-1900` defines
  `gt scaffold adrs --profile azure-enterprise`.
- Current D1/D2 implementation pattern uses Python template catalogs and
  scaffold orchestrators, not the managed-artifact registry:
  `src/groundtruth_kb/_azure_spec_templates.py:1-14`,
  `src/groundtruth_kb/spec_scaffold.py:236-278`,
  `src/groundtruth_kb/_azure_adr_instance_templates.py:1-14`, and
  `src/groundtruth_kb/adr_scaffold.py:69-146`.
- Current D1/D2 tests validate template count, idempotence, and persisted
  output: `tests/test_spec_scaffold_azure.py:59-69`,
  `tests/test_spec_scaffold_azure.py:147-167`,
  `tests/test_spec_scaffold_azure.py:239-257`,
  `tests/test_adr_scaffold_azure.py:59-68`,
  `tests/test_adr_scaffold_azure.py:113-139`, and
  `tests/test_adr_scaffold_azure.py:188-206`.
- Verification command in the target checkout:
  `python -m pytest tests/test_spec_scaffold_azure.py tests/test_adr_scaffold_azure.py -q --tb=short`
  returned `48 passed, 1 warning`.
- Probe command `rg -n "iac_scaffold|_azure_iac|scaffold_azure_iac|terraform validate|setup-terraform" src tests docs .github`
  returned no matches, confirming D3 is not already present and there is no
  existing Terraform-validation test or CI setup in the inspected checkout.

## Findings

### F1 - Prior P0 entry-point blocker is resolved

The revised proposal now names one real delivery contract:
`gt scaffold iac --profile azure-enterprise`.

Evidence:
- Revised entry point: `bridge/gtkb-azure-iac-skeleton-003.md:20`,
  `bridge/gtkb-azure-iac-skeleton-003.md:93-96`.
- Existing scaffold command pattern: `src/groundtruth_kb/cli.py:1779-1818`,
  `src/groundtruth_kb/cli.py:1861-1900`.

Risk/impact:
- Low, if implementation stays inside the proposed sibling scaffold-command
  surface.

Required action:
- Do not add `azure-enterprise` to `project/profiles.py`.
- Do not document `gt project init --profile azure-enterprise`.
- Implement the command as a sibling under the existing `scaffold` group.

### F2 - Prior P0 registry-schema blocker is resolved

The revised proposal removes `class_="file"`, `skip-if-exists`, and
`adopter_divergence_policy="silent"` from the implementation plan.

Evidence:
- Removal summary: `bridge/gtkb-azure-iac-skeleton-003.md:21-22`.
- Revised files touched omit `templates/managed-artifacts.toml`,
  `managed_registry.py`, `ownership.py`, and `upgrade.py`:
  `bridge/gtkb-azure-iac-skeleton-003.md:153-162`.

Risk/impact:
- Low, as long as implementation does not reintroduce registry rows or managed
  lifecycle semantics.

Required action:
- Keep D3 scaffold-only and adopter-owned.
- If registry integration is desired later, file a separate bridge proposal.

### F3 - Prior P1 inventory blocker is resolved

The revised proposal gives an exact path inventory and aligns the intended test
surface to that inventory.

Evidence:
- Exact top-level paths: `bridge/gtkb-azure-iac-skeleton-003.md:122-130`.
- Exact module path groups: `bridge/gtkb-azure-iac-skeleton-003.md:133-149`.
- Grand total: `bridge/gtkb-azure-iac-skeleton-003.md:151`.
- Test intent to assert exact inventory: `bridge/gtkb-azure-iac-skeleton-003.md:104-107`.

Risk/impact:
- Low.

Required action:
- Implement a single expected-path constant or fixture and use it in both the
  template-catalog test and scaffold-output test so counts cannot drift apart.

### F4 - P1 condition: Terraform validation must not become an undeclared CI dependency

The revised proposal includes a `test_scaffold_terraform_valid` test and a
verification step running `terraform init -backend=false && terraform validate`.
That is useful as a smoke check, but it must not make the main Python test suite
depend on an unprovisioned Terraform binary or a network provider download.

Evidence:
- Proposed test: `bridge/gtkb-azure-iac-skeleton-003.md:109`.
- Proposed verification command: `bridge/gtkb-azure-iac-skeleton-003.md:204-206`,
  `bridge/gtkb-azure-iac-skeleton-003.md:216-217`.
- Current CI installs Python package dependencies and runs full pytest, but
  does not install Terraform: `.github/workflows/ci.yml:40-48`,
  `.github/workflows/ci.yml:85-91`.
- Current desktop setup lists Terraform CLI as optional:
  `docs/desktop-setup.md:42-46`.
- Local probe found Terraform installed on this machine at
  `C:\ProgramData\chocolatey\bin\terraform.exe`, but that does not establish
  CI availability.

Risk/impact:
- If the new test unconditionally shells out to Terraform, CI can fail on
  runners without Terraform.
- If `providers.tf` declares required providers, `terraform init` may download
  provider packages, adding network/flakiness risk to the core pytest suite.

Required action:
- Either provision Terraform explicitly in every CI job that runs the test, or
  mark the Terraform validation test as an environment-gated smoke test that
  skips when `shutil.which("terraform") is None`.
- Do not make provider download a hard requirement of the default pytest suite.
  Keep pure-Python tests as the binding checks for the 45-path inventory,
  idempotence, target-path confinement, and adopter markers.

### F5 - P2 condition: lock down CLI write semantics

The revised proposal says `scaffold_azure_iac()` writes missing files and skips
existing files, while saying the command mirrors D1/D2. Existing D1/D2 commands
default to dry-run and require `--apply` for writes. D3 may intentionally differ
because it writes files, not KB rows, but the implementation must make that
choice explicit.

Evidence:
- Proposed writer semantics: `bridge/gtkb-azure-iac-skeleton-003.md:82-90`.
- Existing scaffold specs dry-run/apply option:
  `src/groundtruth_kb/cli.py:1790-1794`.
- Existing scaffold adrs dry-run/apply option:
  `src/groundtruth_kb/cli.py:1871-1874`.

Risk/impact:
- Ambiguous default write behavior can surprise adopters and make CLI tests
  assert only exit code while missing the actual lifecycle contract.

Required action:
- If `gt scaffold iac` writes by default, say so in command help/docs and test
  that the command writes under the intended target root while preserving
  existing files.
- If D3 should mirror D1/D2 dry-run/apply behavior exactly, add
  `--apply/--dry-run` to the command and test both modes.

## GO Conditions

1. Implement only the revised scaffold-only scope from `-003`.
2. Keep the 45-file inventory exact and test it by full path, not count alone.
3. Keep existing files adopter-owned: skip existing paths and never overwrite
   them during scaffold.
4. Make Terraform validation optional or explicitly provisioned; do not add an
   undeclared external dependency to default pytest.
5. Make CLI write/default behavior explicit in help, docs, and tests.

## Decision Needed From Owner

None. This is a Prime implementation GO with the conditions above.

