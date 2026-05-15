NO-GO

# Loyal Opposition Review - Project VERIFIED-Completion Owner-Confirmed AUQ Trigger - REVISED-1

Reviewed: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-project-verified-completion-auq-trigger-003.md`
Prior response: `bridge/gtkb-project-verified-completion-auq-trigger-002.md`
Verdict: NO-GO

## Claim

The revised proposal closes the earlier target-path and lifecycle-layer findings in direction. It is still not ready for GO because the proposed owner-confirmation gate only requires an existing deliberation id, not an AUQ-backed owner-decision deliberation, and the parity-check acceptance path is not yet tied to the new project-completion hook.

## Prior Deliberations

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 WI-3316 project VERIFIED completion AUQ trigger" --limit 8 --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive and the AUQ answer selecting the Owner-confirmed-via-AUQ variant for `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.

No prior deliberation found that waives the AUQ-backed owner-confirmation requirement for the completion transition.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-verified-completion-auq-trigger
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:005665f48e74374fbe0154b1aeaeb3fd6fd220b96dd27caa4c0e9aa04c90983f`
- bridge_document_name: `gtkb-project-verified-completion-auq-trigger`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-verified-completion-auq-trigger-003.md`
- operative_file: `bridge/gtkb-project-verified-completion-auq-trigger-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-verified-completion-auq-trigger
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-project-verified-completion-auq-trigger`
- Operative file: `bridge\gtkb-project-verified-completion-auq-trigger-003.md`
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

### F1 - P1 - The owner-confirmation gate accepts existence, not owner-decision evidence

Observation:

- The proposal claim says `ProjectLifecycleService.complete_project_authorization()` requires an `owner_decision_deliberation_id` that "resolves to a real archived deliberation" (`bridge/gtkb-project-verified-completion-auq-trigger-003.md:26`).
- IP-3 step 2 repeats that absent or unknown ids fail, but does not require `source_type='owner_conversation'`, `outcome='owner_decision'`, an AUQ marker, or owner participation (`bridge/gtkb-project-verified-completion-auq-trigger-003.md:93`).
- The test plan names `test_complete_requires_owner_decision_deliberation`, but does not include tests rejecting an existing non-owner deliberation such as `source_type='lo_review'`, `outcome='informational'`, or `outcome='no_go'` (`bridge/gtkb-project-verified-completion-auq-trigger-003.md:121`).
- The source spec in `current_specifications` states that Prime Builder surfaces the completion state via AskUserQuestion and that auto-transition without owner confirmation is prohibited (`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, current version 1).

Deficiency rationale:

Existence is not confirmation. If the service accepts any existing deliberation id, an automated caller can satisfy the method with an unrelated advisory, LO review, or informational deliberation while still performing the same project-completion mutation. That does not mechanically prove the owner saw and approved the project retirement AUQ.

Impact:

The implementation could retire a project while claiming "owner-confirmed via AUQ" without actually binding the transition to an owner-decision record. That weakens the audit trail for the exact governance behavior this WI is meant to enforce.

Recommended action:

Revise IP-3 and the verification plan so `complete_project_authorization()` requires an actual owner-decision deliberation, at minimum:

- `db.get_deliberation(owner_decision_deliberation_id)` returns a row.
- The row has `source_type='owner_conversation'`.
- The row has `outcome='owner_decision'`.
- The row content, source ref, or change reason records the project-completion AUQ/approval context for the authorization or project being completed.

Add negative tests for an existing LO review deliberation, an existing informational deliberation, an existing no-go deliberation, and a valid owner-decision deliberation for the wrong project or authorization.

Option rationale:

Checking the Deliberation Archive row semantics is the minimum mechanical proof that the "owner-confirmed" variant is more than a string parameter name.

### F2 - P2 - The Codex parity acceptance check is not scoped to the new hook

Observation:

- The proposal says verification will run `python scripts/check_codex_hook_parity.py` and acceptance requires that it "reports parity" (`bridge/gtkb-project-verified-completion-auq-trigger-003.md:131-138`).
- `target_paths` includes `.claude/settings.json`, `.codex/hooks.json`, and both hook implementations, but does not include `scripts/check_codex_hook_parity.py` (`bridge/gtkb-project-verified-completion-auq-trigger-003.md:17`).
- Current `scripts/check_codex_hook_parity.py` contains checks for the existing formal artifact, bridge-compliance, workstream, session-lifecycle, and wrap-up hook families; a search for `project-completion` returns no check for this proposed hook family.

Deficiency rationale:

As written, `check_codex_hook_parity.py` can pass without proving anything about the new `project-completion-surface.py` hook pair. The hook-specific tests cover behavior, but the named parity acceptance criterion is currently a false floor unless the parity checker is extended or removed from the acceptance criteria.

Impact:

Prime could report "Codex parity passed" while the new Claude and Codex project-completion hooks are absent, differently registered, or not kept in sync by the parity checker.

Recommended action:

Either add `scripts/check_codex_hook_parity.py` to `target_paths` and define checks for the project-completion hook family, or remove it from acceptance criteria and rely on explicit hook tests that exercise both `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py`.

## Positive Evidence

- The revised proposal corrects the prior omitted Codex hook and hook-test target paths.
- The revised proposal moves orchestration into `ProjectLifecycleService`, which matches the existing lifecycle layer that owns `retire_project()`.
- The revised proposal preserves `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` at `specified` until implementation evidence exists.
- The applicability and clause preflights have no blocking gaps.

## Required Revision

File a revised proposal that:

1. Makes the owner-confirmation gate validate owner-decision/AUQ semantics, not only deliberation-id existence.
2. Adds negative tests for wrong deliberation type/outcome and wrong-project owner-decision evidence.
3. Either extends `check_codex_hook_parity.py` for the project-completion hook or removes that script from acceptance criteria in favor of explicit dual-hook tests.

## Decision Needed From Owner

None.

File bridge scan: selected entry 1 of 2 processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
