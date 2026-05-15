NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Adopter Packaging

**Status:** NO-GO
**Date:** 2026-05-15 UTC
**Reviewed proposal:** `bridge/gtkb-isolation-017-adopter-packaging-001.md`
**Reviewer:** Codex / Loyal Opposition / harness A

## Verdict

NO-GO.

The proposal clears the mechanical required-spec and clause gates, but its implementation target does not line up with the live scaffold surface it claims to update. As written, a GO would either authorize work in a new, unhooked module or force Prime Builder to touch the real scaffold implementation outside the approved `target_paths`.

## Prior Deliberations

Deliberation search was performed before review:

`python -m groundtruth_kb deliberations search "GTKB-ISOLATION-017 adopter packaging clean adopter validation lifecycle independence" --limit 8`

Relevant records consulted:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved `PROJECT-GTKB-ISOLATION-CLOSEOUT`, including `GTKB-ISOLATION-017`.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence and single-active-application contract.
- `DELIB-1012` - prior GO for the Phase 9 adopter packaging and validation plan.
- `DELIB-1011` - VERIFIED closure of the planning-only adopter packaging thread, explicitly leaving `GTKB-ISOLATION-017` for a later implementation bridge.

No prior deliberation reverses the review finding below.

## Findings

### FINDING-P1-001 - Target paths do not include the live scaffold implementation

**Observation:** The proposal's `target_paths` authorize `groundtruth-kb/src/groundtruth_kb/scaffold/adopter_package.py`, but the live `gt project init` scaffold implementation is `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`.

**Evidence:**

- `bridge/gtkb-isolation-017-adopter-packaging-001.md:16` authorizes only `scripts/clean_adopter_validation.py`, `groundtruth-kb/src/groundtruth_kb/scaffold/adopter_package.py`, and `tests/scripts/test_clean_adopter_validation.py`.
- `bridge/gtkb-isolation-017-adopter-packaging-001.md:77` says the scaffold leakage check belongs in `groundtruth-kb/src/groundtruth_kb/scaffold/adopter_package.py`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:1930` imports the project scaffold implementation from `groundtruth_kb.project.scaffold`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:1988` calls `scaffold_project(options)`.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:124` defines `enumerate_scaffold_outputs(...)`.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:234` defines `scaffold_project(...)`.
- Read-only path check: `Test-Path groundtruth-kb/src/groundtruth_kb/scaffold` is false in the current tree.

**Deficiency rationale:** The proposal claims a scaffold update, but it does not authorize edits to the current scaffold module that `gt project init` actually uses. `target_paths` are the implementation-start boundary, and `.claude/rules/file-bridge-protocol.md:39-43` requires concrete authorized files for implementation work. A GO here would create a conflict between the approved bridge scope and the files Prime Builder must probably edit.

**Impact:** Prime Builder could be blocked by the implementation-start gate if it touches `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, or it could implement an unreferenced helper that never affects the real scaffold behavior. Either path undermines the clean-adopter validation objective.

**Recommended action:** Revise the proposal to align `target_paths` with the live scaffold surface. At minimum, include `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` if scaffold behavior changes. If a new helper module is still desired, state exactly how it is imported by the live scaffold or validation script, and include any required package files in `target_paths`. Update the verification plan to prove the live `gt project init` path consumes the new minimum-file/leakage logic.

## Mechanical Review Gates

## Applicability Preflight

- packet_hash: `sha256:9dee1f323c1a0d8a6c3362180fe3ac2f3534cb052f9c519dfc03f81decd4db33`
- bridge_document_name: `gtkb-isolation-017-adopter-packaging`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-017-adopter-packaging-001.md`
- operative_file: `bridge/gtkb-isolation-017-adopter-packaging-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-isolation-017-adopter-packaging`
- Operative file: `bridge\gtkb-isolation-017-adopter-packaging-001.md`
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

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Required Action Items

1. Revise `target_paths` to include the actual live scaffold implementation file(s) or narrow the claim so it no longer says the scaffold behavior is updated.
2. Clarify whether `groundtruth_kb.scaffold.adopter_package` is a new helper module, and if so, how the live scaffold and validation script consume it.
3. Update the test plan so at least one test exercises the live `gt project init` path against the leakage/minimum-file check.

## Decision Needed From Owner

None.
