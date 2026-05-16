REVISED

# Implementation Proposal - Adopter Packaging + Clean-Adopter Validation (GTKB-ISOLATION-017)

bridge_kind: implementation_proposal
Document: gtkb-isolation-017-adopter-packaging
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-017

target_paths: ["scripts/clean_adopter_validation.py", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py"]

This REVISED proposal implements downstream adopter packaging and clean-adopter validation. Per `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, adopter projects (e.g., the active demos) must be able to consume GT-KB without depending on internal-only paths.

## Revision Notes (-003 vs -001)

This `-003` revises `-001` to address the single finding FINDING-P1-001 in the `-002` NO-GO.

| `-002` finding | How `-003` addresses it |
|----------------|--------------------------|
| FINDING-P1-001 - `target_paths` authorize `groundtruth-kb/src/groundtruth_kb/scaffold/adopter_package.py`, but that directory does not exist; the live `gt project init` scaffold is `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | (a) `target_paths` is repointed: the non-existent `groundtruth-kb/src/groundtruth_kb/scaffold/adopter_package.py` is removed and replaced with the live scaffold module `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`. (b) The non-existent test directory `tests/scripts/` is also corrected: the test file moves to the live adopter test surface `groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py`. (c) `## Proposed Scope` IP-2 is rewritten: there is NO new `adopter_package` helper module; the minimum-file / leakage-check logic is added directly to the live scaffold module `scaffold.py`, reusing its existing `enumerate_scaffold_outputs(...)` function as the canonical scaffold-output enumeration. (d) `## Specification-Derived Verification Plan` is updated so at least one test exercises the live `gt project init` path against the leakage / minimum-file check, using the existing `clean_adopter` fixture in `groundtruth-kb/tests/adopter/conftest.py` (which calls `scaffold_project`). |

Investigation evidence supporting the repoint:
- `Test-Path groundtruth-kb/src/groundtruth_kb/scaffold` is false in the live tree (directory absent).
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` exists; it defines `enumerate_scaffold_outputs(profile_name, *, cloud_provider="none")` (line 124) and `scaffold_project(options)` (line 234).
- `groundtruth-kb/src/groundtruth_kb/cli.py` imports the project scaffold from `groundtruth_kb.project.scaffold` and calls `scaffold_project(options)` for `gt project init`.
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py` already imports and uses `enumerate_scaffold_outputs` for a scaffold-output set comparison (line 202); the leakage / minimum-file check builds on this same enumeration rather than re-implementing the scaffold file list.
- `tests/scripts/` does not exist in the live tree. The live adopter-focused test surface is `groundtruth-kb/tests/adopter/`, which already contains `conftest.py` with the `clean_adopter` fixture and tests such as `test_init_scaffolds_adopter_owned_paths.py` that exercise the live `scaffold_project` path.

No scope change to the substance of the work (clean-adopter validation + minimum-file / leakage check); only the implementation target paths and the helper-module framing are corrected to match the live tree.

## Supersession / Filing Note

`-001` (NEW) and `-002` (NO-GO) are preserved unchanged on disk per the append-only bridge audit-trail invariant. This `-003` is filed as the `REVISED` version; `bridge/INDEX.md` records the latest status as `REVISED`.

## Claim

Two parts: (1) a packaging-validation script that simulates a clean adopter checkout (no GT-KB platform files, only consumed surfaces) and verifies the adopter can run `gt project init`, `gt doctor`, and basic backlog/spec operations; (2) a minimum-file / leakage check added to the live scaffold module that verifies `gt project init` output contains the minimum adopter-side file set and no internal-platform leakage.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`:

- `scripts/clean_adopter_validation.py` - in `E:\GT-KB\scripts\` (existing top-level directory).
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` - the live scaffold module, in-root under `E:\GT-KB\groundtruth-kb\`.
- `groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py` - in the existing `E:\GT-KB\groundtruth-kb\tests\adopter\` directory.

`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - isolation contract; all target paths in-root.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence motivation; adopters must consume GT-KB without internal-only path dependence.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - adoption governance.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping requirement; the verification plan derives tests from these linked specs.
- `GOV-STANDING-BACKLOG-001` - WI tracked in MemBase.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model (advisory; cited per `-002` preflight `missing_advisory_specs`).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers (advisory; cited per `-002` preflight `missing_advisory_specs`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline (advisory; cited per `-002` preflight `missing_advisory_specs`).
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence: owner-approved `PROJECT-GTKB-ISOLATION-CLOSEOUT` authorization including `GTKB-ISOLATION-017`.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization; owner-approved `PROJECT-GTKB-ISOLATION-CLOSEOUT` including `GTKB-ISOLATION-017`.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - foundational lifecycle independence and single-active-application contract.
- `DELIB-1012` - prior GO for the Phase 9 adopter packaging and validation plan.
- `DELIB-1011` - VERIFIED closure of the planning-only adopter packaging thread, explicitly leaving `GTKB-ISOLATION-017` for a later implementation bridge. This proposal is that later implementation bridge.

No prior deliberation reverses the `-002` NO-GO finding; this `-003` revision closes it by repointing `target_paths` to the live scaffold surface.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved `PROJECT-GTKB-ISOLATION-CLOSEOUT` (owner-decision `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`) including this work item.
- `GTKB-ISOLATION-017` is an active member of `PROJECT-GTKB-ISOLATION-CLOSEOUT`, covered by the active project authorization `PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH` (active, unexpired; `included_work_item_ids` explicitly lists `GTKB-ISOLATION-017`). This project authorization provides the owner-approval evidence for the bounded project scope; it does not replace the bridge GO or any formal-artifact-approval packet.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` plus `GOV-GTKB-ADOPTION-ENFORCEMENT-001` specify the requirement: an adopter must be able to consume GT-KB through scaffolded surfaces without internal-platform leakage. No new or revised specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (`GTKB-ISOLATION-017`); an active member of `PROJECT-GTKB-ISOLATION-CLOSEOUT` per the `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. No batch resolve, promote, retire, or reorder of work items or specifications is performed. References to "work item" and "backlog" describe the single work item only. Review-packet inventory: IP-1 (validation script) + IP-2 (scaffold leakage check) + IP-3 (tests), single thread. The applicable evidence is a single-WI implementation proposal with formal-artifact-approval discipline preserved.

## Bridge INDEX Maintenance

`bridge/INDEX.md` remains the canonical bridge workflow state. This `-003` adds a `REVISED:` line at the top of the `gtkb-isolation-017-adopter-packaging` document entry, above the existing `NO-GO:` and `NEW:` lines, preserving newest-first ordering. No other INDEX entry is modified.

## Proposed Scope

### IP-1: clean_adopter_validation.py

New file `scripts/clean_adopter_validation.py`.

CLI: `python scripts/clean_adopter_validation.py [--adopter-name <name>] [--temp-dir <path>]`.

Steps:
1. Create a temp adopter directory; scaffold a clean adopter by importing and calling the live `scaffold_project(...)` from `groundtruth_kb.project.scaffold` (NOT a re-implementation; the script consumes the live scaffold path).
2. Run `gt project doctor` against the scaffolded adopter - must pass.
3. Run smoke ops: `gt backlog add ...`, `gt summary`, etc.
4. Report PASS/FAIL with per-step output.

The script imports the live scaffold function rather than copying file lists, so it cannot drift from the real `gt project init` behavior.

### IP-2: Minimum-file / leakage check in the live scaffold module

In `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` (the live `gt project init` module):

- Add a function (e.g., `validate_scaffold_minimum_and_no_leakage(target, profile_name, *, cloud_provider)`) that:
  - Computes the expected adopter-side minimum file set by calling the existing `enumerate_scaffold_outputs(profile_name, cloud_provider=cloud_provider)` in the same module.
  - Verifies the scaffolded `target` directory contains exactly that minimum set and no internal-platform paths (no `.gtkb-state/`, no `bridge/INDEX.md`-style platform bridge state, no `independent-progress-assessments/`, no platform-only source under `groundtruth-kb/src/`).
  - Returns a structured PASS/FAIL result with the offending leaked or missing paths enumerated.
- There is **no** new `adopter_package` module. The check lives in the live scaffold module so it stays co-located with `enumerate_scaffold_outputs` and `scaffold_project`, and is reachable by the live `gt project init` path and by `scripts/clean_adopter_validation.py`.
- The companion `groundtruth_kb.project.preflight` module already consumes `enumerate_scaffold_outputs` for a scaffold-output set comparison; the new function reuses the same enumeration so there is one source of truth for the scaffold file set.

### IP-3: Tests

New file `groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py`, in the live adopter test directory that already hosts `conftest.py` with the `clean_adopter` fixture.

Tests verify: the validation script returns 0 on a clean adopter and non-zero on an adopter missing required pieces; the leakage / minimum-file check correctly identifies leaked internal paths and a missing minimum-set file; and - critically per the `-002` NO-GO required action - at least one test exercises the **live `gt project init` path** (via the existing `clean_adopter` fixture, which calls `scaffold_project`) and runs the leakage / minimum-file check against that real scaffold output.

## Specification-Derived Verification Plan

| Behavior | Linked spec | Test |
|---|---|---|
| Clean-adopter validation passes on a healthy scaffold (live `scaffold_project`) | `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | `test_clean_adopter_validation_passes` |
| Missing scaffold piece fails validation | `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | `test_clean_adopter_missing_piece_fails` |
| `gt doctor` runs cleanly in a temp adopter | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `test_doctor_runs_in_temp_adopter` |
| Leakage check identifies internal platform paths | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` | `test_scaffold_leakage_check_detects_internal` |
| Minimum-file check on the live `gt project init` output via the `clean_adopter` fixture | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | `test_live_gt_project_init_clean_of_leakage` |
| Backlog smoke ops work in a temp adopter | `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | `test_smoke_backlog_ops_in_temp_adopter` |

Verification commands:

```
python -m pytest groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py -v
python -m ruff check .
python -m ruff format --check .
```

The `test_live_gt_project_init_clean_of_leakage` test directly satisfies the `-002` NO-GO required action item: at least one test exercises the live `gt project init` path against the leakage / minimum-file check.

## Acceptance Criteria

- IP-1, IP-2 landed within the corrected `target_paths`; all six tests in IP-3 PASS.
- At least one test exercises the live `gt project init` / `scaffold_project` path against the leakage / minimum-file check.
- No new `adopter_package` module is created; the leakage / minimum-file logic lives in the live `scaffold.py`.
- Both preflights PASS.

## Risks / Rollback

- Risk: temp-dir cleanup may fail under Windows file locks. Mitigation: the existing `clean_adopter` fixture's `shutil.rmtree(..., ignore_errors=True)` cleanup pattern is reused.
- Risk: scaffold drift between the validation logic and actual `gt project init` paths. Mitigation: both the validation script and the leakage check import / reuse the live `scaffold_project` and `enumerate_scaffold_outputs` functions rather than re-implementing the scaffold file list.
- Rollback: remove `scripts/clean_adopter_validation.py`, revert the added function in `scaffold.py`, and remove the new test file.

## Recommended Commit Type

`feat` - new validation tool + a new minimum-file / leakage-check function on the live scaffold module + tests. Net-new capability surface.

## Applicability Preflight

Run on this `-003` content after the INDEX entry was updated:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-017-adopter-packaging
```

```
## Applicability Preflight

- packet_hash: `sha256:578227eb23699ad6d8c726c23201a62901d6f3db629c6434167468102792850c`
- bridge_document_name: `gtkb-isolation-017-adopter-packaging`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-017-adopter-packaging-003.md`
- operative_file: `bridge/gtkb-isolation-017-adopter-packaging-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

`preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []` (the three advisory specs flagged in the `-002` review are now cited).

## Clause Applicability

```
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-017-adopter-packaging
```

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-isolation-017-adopter-packaging`
- Operative file: `bridge\gtkb-isolation-017-adopter-packaging-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Exit 0; zero blocking gaps. All five `must_apply` clauses report evidence found.

End of proposal.
