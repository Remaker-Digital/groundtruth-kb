REVISED

# Revised Proposal - Orphaned Bridge Authority Direction Switch Cleanup

author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ef094-6d42-7541-a32f-0ae73d233921
author_model: gpt-5-codex
author_model_version: 2026-06-22
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

bridge_kind: prime_revision
Document: gtkb-remove-orphaned-bridge-authority-direction-switch
Version: 003
Responds-To: bridge/gtkb-remove-orphaned-bridge-authority-direction-switch-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4629

target_paths: ["harness-state/bridge-authority-direction.json", "groundtruth-kb/tests/test_bridge_authority_direction.py"]

## Revision Claim

This revision preserves the original defect-removal scope: delete the orphaned tracked authority-direction switch file and delete its dangling test for the already-deleted `scripts/bridge_authority_cutover.py` consumer.

The only change from version 001 is the verification plan. Version 002 correctly found that the prior plan named deleted paths in direct `ruff check` and `ruff format --check` commands, which would make the approval packet's own evidence impossible to execute after implementation. This revision replaces those missing-path ruff commands with executable post-delete evidence:

- absence checks for both deleted targets;
- repo-wide grep proving no live Python references to the retired consumer remain;
- a target-set diff/status check proving the implementation is deletion-only;
- a conditional ruff gate that runs only if any surviving modified Python path remains in the approved target set; and
- the existing full `groundtruth-kb/tests` regression run.

No source/config/test target path is added. No public behavior, schema, bridge state, MemBase data, application subtree, or formal artifact mutation is added to scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the stale switch file is a dead authority artifact from the retired bridge-index cutover path; removing it keeps live bridge authority surfaces consistent with consumed runtime state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the retirement is preserved as a bridge-reviewed artifact lifecycle change rather than an untracked cleanup.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites the governing specs constraining the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the revised verification plan maps the deletion to executable absence, reference, and regression checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths remain machine-readable in this revision.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both target paths are under `E:\GT-KB`; no adopter/application path is touched.
- `GOV-STANDING-BACKLOG-001` - `WI-4629` remains the standing-backlog source for this defect.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the orphan cleanup remains tied to durable bridge, work-item, and test evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the deleted switch file and deleted dangling test are treated as retired artifacts, not live configuration.

## Prior Deliberations

- `DELIB-20264698` - retired bridge artifact runtime source cleanout context.
- `DELIB-20263786` - bridge index retirement cleanout packet correction review.
- `DELIB-20263285` - TAFE live implementation-flow pilot proposal review, predecessor context for the authority-direction cutover.
- `DELIB-20263275` - TAFE Slice C bridge-thread ingestion verdict, sibling cutover context.
- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` / `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization for small defect fixes under active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ directing proposal authoring for open PROJECT-GTKB-RELIABILITY-FIXES work items; `WI-4629` is in that batch.

No new owner decision is required. This revision narrows no owner choice and adds no new mutation class; it only corrects an executable verification defect in the already-filed proposal.

## Findings Addressed

### FINDING-P1-001: Ruff commands name files that the proposal deletes

Response: resolved. The revised verification plan no longer invokes `ruff` directly on `harness-state/bridge-authority-direction.json` or `groundtruth-kb/tests/test_bridge_authority_direction.py` after those paths are deleted.

The post-delete code-quality evidence is now executable:

1. Confirm the approved target diff is deletion-only.
2. Build the surviving modified Python path list from the approved target set using `git diff --diff-filter=ACMR --name-only -- <target_paths>`.
3. If that list is empty, record `no surviving Python targets to lint`; this is the expected outcome for this deletion-only implementation.
4. If any surviving Python path unexpectedly remains modified, run `python -m ruff check` and `python -m ruff format --check` on that list before filing the implementation report.

This keeps the mandatory Python quality gate meaningful without requiring commands that are guaranteed to fail on intentionally deleted files.

## Scope Changes

No implementation scope change.

Target paths remain:

- `harness-state/bridge-authority-direction.json` (delete)
- `groundtruth-kb/tests/test_bridge_authority_direction.py` (delete)

The proposal still excludes live source changes, schema changes, MemBase writes, `bridge/INDEX.md` recreation, application/adopter paths, and tracked changes to ignored `__pycache__` cache files.

## Pre-Filing Preflight Subsection

Before live filing, this completed revision content is checked with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-remove-orphaned-bridge-authority-direction-switch --content-file .gtkb-state/bridge-revisions/drafts/gtkb-remove-orphaned-bridge-authority-direction-switch-003.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-remove-orphaned-bridge-authority-direction-switch --content-file .gtkb-state/bridge-revisions/drafts/gtkb-remove-orphaned-bridge-authority-direction-switch-003.md
```

The governed revision helper reruns these checks before publishing the live `REVISED` bridge file.

## Revised Verification Plan

| Spec / obligation | Executable verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` - no live consumer-less authority toggle remains | `Test-Path -LiteralPath harness-state/bridge-authority-direction.json` | `False` after implementation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - dangling test for retired consumer is removed | `Test-Path -LiteralPath groundtruth-kb/tests/test_bridge_authority_direction.py` | `False` after implementation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - no live Python references to retired cutover API remain | `rg -n "bridge_authority_cutover|read_authority_direction|direction_state_path" groundtruth-kb scripts .claude config --glob "*.py"` | no matches |
| Python quality gate for deletion-only target set | PowerShell conditional ruff gate over surviving modified Python targets in the approved target set | expected output: `no surviving Python targets to lint`; otherwise both ruff commands pass on any surviving modified Python targets |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - no test-suite regression from deletion | `python -m pytest groundtruth-kb/tests -q --tb=short` | pass; no import/load error from the deleted test |
| Target scope discipline | `git diff --name-status -- harness-state/bridge-authority-direction.json groundtruth-kb/tests/test_bridge_authority_direction.py` | only deletion entries for the two approved target paths |

Concrete post-implementation command set:

```powershell
Test-Path -LiteralPath harness-state\bridge-authority-direction.json
Test-Path -LiteralPath groundtruth-kb\tests\test_bridge_authority_direction.py
rg -n "bridge_authority_cutover|read_authority_direction|direction_state_path" groundtruth-kb scripts .claude config --glob "*.py"
git diff --name-status -- harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py
$survivingPy = @(git diff --diff-filter=ACMR --name-only -- harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py | Where-Object { $_ -like "*.py" })
if ($survivingPy.Count -gt 0) {
  python -m ruff check @survivingPy
  python -m ruff format --check @survivingPy
} else {
  "no surviving Python targets to lint"
}
python -m pytest groundtruth-kb\tests -q --tb=short
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-remove-orphaned-bridge-authority-direction-switch
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-remove-orphaned-bridge-authority-direction-switch
```

The pre-fix proof command remains optional diagnostic evidence only:

```powershell
python -m pytest groundtruth-kb\tests\test_bridge_authority_direction.py -q --tb=short
```

It is expected to error before deletion because the test imports deleted `scripts/bridge_authority_cutover.py`. It must not be required after deletion because the file no longer exists.

## Acceptance Criteria

1. `harness-state/bridge-authority-direction.json` is deleted from the working tree and staged as a tracked deletion.
2. `groundtruth-kb/tests/test_bridge_authority_direction.py` is deleted from the working tree and staged as a tracked deletion.
3. Repo-wide Python grep over `groundtruth-kb`, `scripts`, `.claude`, and `config` finds no live references to `bridge_authority_cutover`, `read_authority_direction`, or `direction_state_path`.
4. The deletion-only target set produces no surviving modified Python target paths; if any surviving modified Python path exists, `ruff check` and `ruff format --check` pass on that exact path list.
5. `python -m pytest groundtruth-kb/tests -q --tb=short` passes with no import/load error caused by the retired cutover module.

## Risk And Rollback

Risk: a non-Python or documentation reference to `bridge-authority-direction` remains. Mitigation: the load-bearing runtime risk is Python consumption of the retired cutover surface; the implementation report may additionally include an advisory `rg` over docs/config if desired, but the executable gate is the Python live-consumer grep above.

Risk: full `groundtruth-kb/tests` may expose unrelated pre-existing failures. Mitigation: any out-of-scope failures must be reported distinctly; the deletion-specific acceptance remains absence plus no live Python references. A deletion-caused import/load error is in scope and must be fixed before reporting.

Rollback is simple and path-local:

```powershell
git restore --staged --worktree harness-state\bridge-authority-direction.json groundtruth-kb\tests\test_bridge_authority_direction.py
```

After commit, rollback is a normal `git revert` of the implementing commit. Bridge files remain append-only.
