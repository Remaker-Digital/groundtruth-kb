NO-GO

# Loyal Opposition Review - Core Spec Intake Default

**Status:** NO-GO  
**Reviewer:** Codex Loyal Opposition  
**Date:** 2026-05-15 UTC  
**Reviewed proposal:** `bridge/gtkb-core-spec-intake-default-001.md`  
**Document:** `gtkb-core-spec-intake-default`

## Verdict

NO-GO.

The proposal is directionally aligned with `GTKB-CORE-001`, but it cannot receive GO in this form. It cites a non-current formal spec (`SPEC-CORE-INTAKE-003`), under-scopes the repeated prompt loop promised by the work item, and misses advisory specification links identified by the applicability preflight.

## Prior Deliberations

Deliberation Archive search was run before review.

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - current batch authorization cited by the proposal.
- `DELIB-0875` - Phase 0 governance approval cited by the proposal.
- `DELIB-0898` / `DELIB-1181` - prior `gtkb-core-spec-intake` bridge thread, including the protocol-only closure/withdrawal loop.
- `DELIB-0897` / `DELIB-1182` - prior `gtkb-core-spec-intake-phase1` package-module slice.
- `DELIB-0893` - prior `gtkb-core-spec-intake-phase3a-cli` read-only CLI slice.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:9cf90f60f773a8e88b866ead33b0d5d0499b25f21f2314ebe9db2245d6cb285e`
- bridge_document_name: `gtkb-core-spec-intake-default`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-core-spec-intake-default-001.md`
- operative_file: `bridge/gtkb-core-spec-intake-default-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-core-spec-intake-default`
- Operative file: `bridge\gtkb-core-spec-intake-default-001.md`
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

## Findings

### F1 - Missing cited formal specification blocks requirement sufficiency

**Severity:** P1 governance drift  
**Observation:** The proposal claims the loop is specified by `SPEC-CORE-INTAKE-001..003` and repeats that sufficiency claim in `## Requirement Sufficiency`. Live MemBase query of `current_specifications` found `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and `DCL-CORE-INTAKE-001`, but no `SPEC-CORE-INTAKE-003` row. The work item's current `related_spec_ids_at_creation` likewise lists only `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and `DCL-CORE-INTAKE-001`.

**Evidence:** `bridge/gtkb-core-spec-intake-default-001.md:22`, `:52-54`; command `SELECT id,title,status,type FROM current_specifications WHERE id LIKE 'SPEC-CORE-INTAKE%'` returned only `SPEC-CORE-INTAKE-001` and `SPEC-CORE-INTAKE-002`.

**Impact:** GO would approve implementation against a spec identifier that does not exist in the current MemBase authority surface. That weakens the bridge's specification-linkage gate and makes later verification ambiguous.

**Recommended action:** Revise the proposal to either remove `SPEC-CORE-INTAKE-003` from the sufficiency claim, or create/approve that specification through the governed artifact path before resubmitting. The revised proposal should cite only current authoritative specs.

### F2 - Proposed scope does not implement the repeated prompt loop promised by the claim

**Severity:** P1 governance drift  
**Observation:** The proposal claims that after `gt project init`, GT-KB must repeatedly prompt for missing core specifications until complete. The proposed implementation only adds a module, a default-on project-init enrollment flag, an opt-out, and an initial `MEMORY.md` prompt. It does not include a session-start, doctor, dashboard/startup, CLI answer, or other repeated prompt surface, and its test plan does not prove cross-session prompting or owner-answer capture.

**Evidence:** `bridge/gtkb-core-spec-intake-default-001.md:18`, `:74-83`, `:85-103`. The current work item description requires a persisted loop that asks one missing question at a time, captures answers with owner-stated provenance or confirmation-needed status, continues across sessions, and stops only once every required slot is owner-stated or not applicable. Current `scaffold.py` also documents that `ScaffoldOptions.spec_scaffold` defaults to `None` and that default `gt project init` behavior is unchanged at `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:88-95` and `:323-329`.

**Impact:** Prime could implement the proposed files and pass the listed tests while still not delivering the owner-visible repeated prompt behavior the proposal claims to make default.

**Recommended action:** Revise the proposal to either narrow the claim to a first slice of default enrollment/initial prompt infrastructure, or expand target paths and tests to cover the actual repeated prompt surface. The revised verification plan should include a multi-session or equivalent persisted-state test proving prompt continuation and cessation.

### F3 - Opt-in CLI claim is not authorized by target paths or tests

**Severity:** P2 capability overclaim  
**Observation:** The claim says existing projects opt in via `gt project core-spec-intake enable`, but the target paths include only `scaffold.py`, a new `project/core_spec_intake.py`, and one test file. No CLI target path or test is included for a `gt project core-spec-intake enable` command.

**Evidence:** `bridge/gtkb-core-spec-intake-default-001.md:16`, `:22`, `:85-97`.

**Impact:** The implementation authorization packet derived from a GO would not authorize the CLI file changes needed to make the stated opt-in command real. The proposal therefore overstates its deliverable.

**Recommended action:** Remove the opt-in CLI claim from this slice, or add the concrete CLI target path(s) and specification-derived tests for the command.

### F4 - Applicability preflight found uncited advisory specs

**Severity:** P2 specification-linkage gap  
**Observation:** The mandatory preflight found no missing required specs, but it did find uncited advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

**Evidence:** Applicability Preflight above.

**Impact:** This proposal is explicitly about prompting for owner-stated requirements and preserving specification evidence. The artifact-oriented governance surfaces are relevant review context and should not be omitted.

**Recommended action:** Add these advisory specs to the `Specification Links` section or explain why each is not applicable in the revised proposal.

## Required Action Items

1. Revise and resubmit as `bridge/gtkb-core-spec-intake-default-003.md` with `REVISED` status.
2. Fix the formal-spec sufficiency claim around `SPEC-CORE-INTAKE-003`.
3. Align scope, target paths, and tests with either the claimed default repeated prompt loop or a narrower first slice.
4. Address the applicability preflight's advisory spec omissions.

## Decision Needed From Owner

None.

## Commands Run

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-core-spec-intake-default --format json --preview-lines 20
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-default
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-default
python -m groundtruth_kb deliberations search "GTKB-CORE-001 core spec intake" --limit 5
python -m groundtruth_kb deliberations search "SPEC-CORE-INTAKE ADR-CORE-INTAKE DCL-CORE-INTAKE" --limit 5
SQLite read: current_specifications for SPEC-CORE-INTAKE*, ADR-CORE-INTAKE-001, DCL-CORE-INTAKE-001
SQLite read: current_work_items for GTKB-CORE-001
rg/read-only inspection of scaffold.py and prior core-spec bridge files
```
