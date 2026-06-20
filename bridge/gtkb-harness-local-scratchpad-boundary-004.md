GO

# gtkb-harness-local-scratchpad-boundary - Harness-Local Scratchpads Are Non-Authoritative

bridge_kind: lo_verdict
Document: gtkb-harness-local-scratchpad-boundary
Version: 004
Author: Loyal Opposition (Ollama, harness D)
Reviewer: Loyal Opposition
Date: 2026-06-19 UTC
Responds to: bridge/gtkb-harness-local-scratchpad-boundary-003.md

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: ollama-harness-d
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Verdict

GO. The role/status defect identified in `bridge/gtkb-harness-local-scratchpad-boundary-002.md` has been corrected in `bridge/gtkb-harness-local-scratchpad-boundary-003.md`. The artifact is now filed as a Prime Builder-authored `REVISED` prime proposal, with correct author metadata and the same substantive implementation intent preserved from `-001`.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:d53a787a57ab9488e93a3eb4f42e86eb47ccd4bd1a272ea107eab70c1c74462e`
- bridge_document_name: `gtkb-harness-local-scratchpad-boundary`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-harness-local-scratchpad-boundary-003.md`
- operative_file: `bridge/gtkb-harness-local-scratchpad-boundary-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-local-scratchpad-boundary`
- Operative file: `bridge\gtkb-harness-local-scratchpad-boundary-004.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | may_apply | — | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
```

## Positive Confirmations

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-local-scratchpad-boundary` passes with no missing required specs.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-local-scratchpad-boundary` passes with no blocking gaps.
- Bridge role/status correctness: `bridge/gtkb-harness-local-scratchpad-boundary-003.md` is filed as `REVISED` by a Prime Builder session (`author_identity: codex-prime-builder`, `author_harness_id: A`) and responds to the prior LO NO-GO (`bridge/gtkb-harness-local-scratchpad-boundary-002.md`).
- Project authorization is preserved: `PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-WI-4681-HARNESS-SCRATCHPAD-BOUNDARY`, project `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION`, work item `WI-4681`.
- The proposal includes owner decision evidence (`DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY`), target paths, requirement sufficiency, acceptance criteria, and a spec-derived verification plan.
- The target paths are in-root and consistent with the ADR-ISOLATION-APPLICATION-PLACEMENT-001 IN-ROOT clause: `AGENTS.md`, `.claude/rules/project-root-boundary.md`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, and the proposed new test at `platform_tests/scripts/test_harness_local_scratchpad_boundary.py`.

## Findings

### F1 - Role/status defect resolved

**Observation.** The previous LO NO-GO (`-002`) found that the proposal was authored by Loyal Opposition metadata while carrying a Prime-actionable `NEW` implementation proposal. In `-003`, the artifact status is `REVISED`, the author metadata reads `codex-prime-builder`, and the `bridge_kind` remains `prime_proposal`.

**Assessment.** The corrected ownership path satisfies the LO objection. The substantive policy clarification — that harness-local scratchpads and the `MEMORY.md` hierarchy are non-authoritative and cannot become formal GT-KB artifacts, evidence, or dependencies — remains unchanged and is aligned with the owner decision `DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY`.

### F2 - Scope and exclusion clarity preserved

**Observation.** The proposal explicitly excludes disabling harness memory systems, deleting the existing `MEMORY.md` hierarchy, changing credential handling, restoring retired pollers, or creating new out-of-root dependencies. The implementation scope is governance (rules/doctor/test), with `kb_mutation_in_scope: false`.

**Assessment.** The bounded scope is appropriate for a clarification slice under WI-4681 and consistent with `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` constraints.

### F3 - Target-path verification note

**Observation.** The test target path `platform_tests/scripts/test_harness_local_scratchpad_boundary.py` does not currently exist; it is a planned artifact for the implementation phase.

**Assessment.** This is acceptable for a proposal. The eventual implementation report must create and verify that test under `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

### F4 - Optional pre-existing wording in rule files

**Observation.** `AGENTS.md` already contains language classifying `MEMORY.md` as an operational notepad tier and referencing the doctor's `harness-memory` profile. `.claude/rules/project-root-boundary.md` does not yet explicitly call out harness-local scratchpads as non-authoritative.

**Assessment.** The proposal's target-path plan is to add that explicit classification to `.claude/rules/project-root-boundary.md` and to update the doctor's checks and tests. This is consistent with the stated objective.

## Required Revisions

None for the proposal phase. The implementation phase must:

1. Add explicit non-authoritative scratchpad boundary wording to `.claude/rules/project-root-boundary.md` covering Antigravity planning/brain files, Codex automation memory, Claude Code auto-memory, and the `MEMORY.md` hierarchy.
2. Update or add doctor checks in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` to enforce that formal GT-KB artifacts, implementation reports, verification verdicts, tests, bridge evidence, governed decisions, release evidence, and dependency closure do not read from or depend on harness-local scratch/memory surfaces.
3. Create `platform_tests/scripts/test_harness_local_scratchpad_boundary.py` with spec-derived tests that verify the new rule text and doctor behavior.
4. Run the applicable preflight checks and any changed-source lint/tests (e.g., `ruff`, `pytest platform_tests/scripts/test_harness_local_scratchpad_boundary.py`) and include the clean results in the implementation report.

## Prime Builder Implementation Context

- **Objective:** implement the harness-local scratchpad non-authority clarification in the stated target files and tests.
- **Preconditions:** latest bridge status is this GO (`-004`).
- **Recommended next step:** Prime Builder performs the implementation, updates the target paths, and files an implementation report (`REVISED`/`NEW` as appropriate) with spec-derived verification evidence.
- **Verification to preserve:** applicability preflight pass, clause preflight pass, focused pytest for the new boundary wording and doctor checks, and ruff checks for any changed Python files.
- **Rollback:** bridge is append-only; any defects should be addressed by a further revision rather than overwriting prior files.

## Specifications Carried Forward

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY` - owner directive for this slice: harness-local scratchpads, auto-memory systems, and the `MEMORY.md` hierarchy are non-authoritative and cannot be reliable change-control surfaces.
- `DELIB-20260670` - empirical SoT-fragmentation survey that found agents using non-SoT files as current-state substitutes.
- `DELIB-20260671` / `DELIB-20260672` / `DELIB-20260673` - Platform SoT Consolidation authority chain that absorbed the Agent SoT Read Discipline work and established the read-discipline umbrella.
- `DELIB-20260879` - owner authorization for the existing Slice 2A read-discipline implementation envelope; WI-4681 is a narrower follow-on because the existing envelope did not explicitly cover harness-local scratchpad authority.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - existing root-boundary exception for invoking external harness executables; this proposal preserves that narrow executable-only exception and does not extend it to harness-local files, memory, planning documents, or evidence.
- `bridge/gtkb-harness-local-scratchpad-boundary-001.md` - original proposal under review.
- `bridge/gtkb-harness-local-scratchpad-boundary-002.md` - Loyal Opposition NO-GO requiring the proposal to be refiled by a valid Prime Builder session.
- `bridge/gtkb-harness-local-scratchpad-boundary-003.md` - Prime Builder REVISED proposal that corrects the role/status defect.
