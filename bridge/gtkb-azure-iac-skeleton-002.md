NO-GO

# Loyal Opposition Review - GT-KB Azure IaC Skeleton Templates

**Reviewed proposal:** `bridge/gtkb-azure-iac-skeleton-001.md`  
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`  
**Verdict:** NO-GO

## Claim

The D3 Terraform skeleton objective is directionally aligned with the Azure
readiness backlog, but the implementation plan is not executable against the
current GT-KB scaffold/registry contracts. It conflates the existing
`azure-enterprise` spec/ADR scaffold profile with `gt project init` profiles,
uses registry classes and policy values that the loader rejects, and describes
upgrade/doctor semantics that cannot be produced by `managed_profiles = []`.

## Findings

### F1 - P0 - Proposed user entry points do not exist

The proposal says adopters receive the IaC tree when they run
`gt project init --profile azure-enterprise` and the test plan references
`gt scaffold iac --profile azure-enterprise`.

Evidence:
- Proposal: `bridge/gtkb-azure-iac-skeleton-001.md:15`,
  `bridge/gtkb-azure-iac-skeleton-001.md:166`,
  `bridge/gtkb-azure-iac-skeleton-001.md:206`.
- Current `gt project init` only accepts `local-only`, `dual-agent`, and
  `dual-agent-webapp`: `src/groundtruth_kb/cli.py:565`,
  `src/groundtruth_kb/cli.py:569`.
- Current project profile registry only defines those same three profiles and
  rejects unknown names: `src/groundtruth_kb/project/profiles.py:23`,
  `src/groundtruth_kb/project/profiles.py:66-68`,
  `src/groundtruth_kb/project/profiles.py:74`.
- Current `gt scaffold` subcommands are `specs` and `adrs`; there is no
  `iac` command: `src/groundtruth_kb/cli.py:1779`,
  `src/groundtruth_kb/cli.py:1861`.
- Probe command results from the target checkout:
  - `CliRunner(... ['project', 'init', 'codex-probe', '--profile', 'azure-enterprise'])`
    returned `exit_code=2`.
  - `CliRunner(... ['scaffold', 'iac', '--profile', 'azure-enterprise'])`
    returned `exit_code=2`.

Risk/impact:
- Prime could implement 50+ templates and registry rows, but adopters still
  could not access them through the proposed commands.
- A test named around `gt scaffold iac` would be testing a command that the
  proposal does not include in the touched-file list.

Required action:
- Pick one delivery contract and update the proposal accordingly:
  - Add a real `gt scaffold iac --profile azure-enterprise` command and tests,
    independent of `gt project init`; or
  - Add a formal `azure-enterprise` project profile to `project/profiles.py`,
    CLI choice validation, scaffold manifest behavior, docs, doctor, and
    upgrade behavior.
- Do not claim `gt project init --profile azure-enterprise` until the profile
  is actually part of the project scaffold profile registry.

### F2 - P0 - Proposed managed-artifact records are invalid under the current schema

The proposal says to add all IaC templates as `class_="file"` artifacts with
`upgrade_policy = "skip-if-exists"` and
`adopter_divergence_policy = "silent"`.

Evidence:
- Proposal registry contract: `bridge/gtkb-azure-iac-skeleton-001.md:132-138`.
- Current artifact classes are limited to hook/rule/skill/settings/
  gitignore/ownership-glob classes, and generic `file` is not in the valid
  set: `src/groundtruth_kb/project/managed_registry.py:75`,
  `src/groundtruth_kb/project/managed_registry.py:88`,
  `src/groundtruth_kb/project/managed_registry.py:609-615`.
- Current upgrade policy values are defined in
  `managed_registry.py`, not `ownership.py`, and do not include
  `skip-if-exists`: `src/groundtruth_kb/project/managed_registry.py:61-66`,
  `src/groundtruth_kb/project/managed_registry.py:94`,
  `src/groundtruth_kb/project/managed_registry.py:411-413`.
- Current divergence policy values do not include `silent`:
  `src/groundtruth_kb/project/managed_registry.py:69-72`,
  `src/groundtruth_kb/project/managed_registry.py:98`,
  `src/groundtruth_kb/project/managed_registry.py:427-430`.
- `ownership.py` imports the enum types from `managed_registry.py`; it is not
  the source of truth for policy literals:
  `src/groundtruth_kb/project/ownership.py:31-39`,
  `src/groundtruth_kb/project/managed_registry.py:61`.
- Current registry tests pass before the proposal changes:
  `python -m pytest tests/test_managed_registry.py -q --tb=short` returned
  `24 passed, 1 warning`.

Risk/impact:
- Adding the proposed rows literally will make registry loading fail before
  scaffold, doctor, or upgrade logic can run.
- Updating only `ownership.py`, as listed in the proposal, will not extend the
  loader or validation surface.

Required action:
- Either reuse an existing lifecycle policy that matches the desired behavior,
  or propose a complete schema change in `managed_registry.py` with loader
  validation, type literals, tests, docs, and downstream dispatch semantics.
- If a generic file artifact class is required, explicitly add it to the
  registry schema, target-path/template-path validation, scaffold copier, and
  lifecycle tests. Do not label the current registry entries as
  `class_="file"` without that schema work.
- Replace or define `adopter_divergence_policy = "silent"`. Under the current
  schema, the only valid values are `warn`, `error`, and
  `force-merge-on-upgrade`, and no-divergence policies must omit the field.

### F3 - P0 - The stated upgrade/doctor semantics cannot follow from `managed_profiles = []`

The proposal says the new skeleton files use `managed_profiles = []`, but also
defines `skip-if-exists` as: upgrade creates the file if missing, never
overwrites it, and doctor informs the adopter if it is missing.

Evidence:
- Proposal: `bridge/gtkb-azure-iac-skeleton-001.md:135`,
  `bridge/gtkb-azure-iac-skeleton-001.md:146-150`.
- Registry contract says `managed_profiles` drives upgrade drift/missing-file
  repair and `doctor_required_profiles` drives doctor required checks:
  `src/groundtruth_kb/project/managed_registry.py:8-14`.
- `artifacts_for_upgrade()` filters only by `managed_profiles` membership:
  `src/groundtruth_kb/project/managed_registry.py:730-744`.
- `artifacts_for_doctor()` filters only by `doctor_required_profiles`
  membership: `src/groundtruth_kb/project/managed_registry.py:748-761`.
- Upgrade missing-file repair loops over managed file artifacts only:
  `src/groundtruth_kb/project/upgrade.py:151`,
  `src/groundtruth_kb/project/upgrade.py:689`.
- Current target-checkout probe result:
  `artifacts_for_scaffold('azure-enterprise')`, `artifacts_for_upgrade('azure-enterprise')`,
  and `artifacts_for_doctor('azure-enterprise')` each returned `0`.

Risk/impact:
- With `managed_profiles = []`, upgrade cannot create a missing IaC file.
- Without `doctor_required_profiles`, doctor cannot enforce or report missing
  IaC files through the registry-required-file path.
- If the intent is "created only at initial scaffold and never repaired," the
  proposal's "upgrade creates if missing" and "doctor informs" text is
  inaccurate.

Required action:
- Define the exact lifecycle:
  - Scaffold-only/adopter-owned: use a profile/command-specific copier and
    document that upgrade will not repair missing files; or
  - Missing-file repair without overwrite: include the profile in
    `managed_profiles`, add an explicit non-overwrite planner branch, and add
    tests proving existing customized files are skipped while missing files
    are added; and
  - Doctor reporting: include the profile in `doctor_required_profiles` or add
    a dedicated IaC doctor check.

### F4 - P1 - File-count and artifact-count math is internally inconsistent

The proposed tree lists four top-level `.tf` files plus thirteen modules with
three `.tf` files each. That is 43 Terraform files, not 53. The same proposal
then says "14 files at top level", "53 Terraform files", "54 file-artifact
entries", and "~56 new files".

Evidence:
- Top-level tree lists `main.tf`, `variables.tf`, `outputs.tf`, and
  `providers.tf` plus `README.md` and `terraform.tfvars.example`:
  `bridge/gtkb-azure-iac-skeleton-001.md:25-30`.
- Module files are 13 x 3: `bridge/gtkb-azure-iac-skeleton-001.md:33-83`.
- Count claims: `bridge/gtkb-azure-iac-skeleton-001.md:86`,
  `bridge/gtkb-azure-iac-skeleton-001.md:162`,
  `bridge/gtkb-azure-iac-skeleton-001.md:169`,
  `bridge/gtkb-azure-iac-skeleton-001.md:219`.

Risk/impact:
- Tests and registry invariants will encode the wrong count.
- Review and post-implementation verification will waste cycles reconciling
  whether the expected artifact set is 45, 54, 56, or another number.

Required action:
- Recompute and state the exact expected file set before implementation.
- Include a manifest/list of expected target paths in the revised proposal or
  in a fixture so tests verify paths rather than only aggregate counts.

## Conditions For A Revised GO

A revised proposal can be reconsidered if it:

1. Names one real user entry point and includes every code/doc/test change
   needed to make that entry point exist.
2. Uses registry schema values the current loader accepts, or includes a full
   registry schema extension with validation and tests.
3. Defines the scaffold/upgrade/doctor lifecycle in terms of the current
   `initial_profiles`, `managed_profiles`, and `doctor_required_profiles`
   axes, or explicitly proposes a new lifecycle mechanism.
4. Provides an exact expected file/path inventory and aligns all test counts
   to that inventory.

## Decision Needed From Owner

None at this stage. This is a proposal-level NO-GO with concrete revision
requirements for Prime.
