NO-GO

# Loyal Opposition Review - Project VERIFIED-Completion Owner-Confirmed AUQ Trigger

Reviewed: 2026-05-14 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-project-verified-completion-auq-trigger-001.md`
Verdict: NO-GO

## Claim

The project-completion surface is directionally aligned with the owner-selected
Owner-confirmed-via-AUQ variant. The proposal is not ready for GO because its
implementation scope omits files it explicitly says are required, and its
completion/retirement design leaves ambiguous whether project retirement is
mandatory or optional.

## Prior Deliberations

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 WI-3316 project VERIFIED completion AUQ trigger" --limit 8 --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive and the AUQ answer selecting the Owner-confirmed-via-AUQ variant for `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.

No prior deliberation found that waives Codex parity or permits partial project
retirement semantics for this work item.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-verified-completion-auq-trigger
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:62dfbe35f265be3ebb11959a774f29b2b2ec016e783f3c2d3ce4d0986a7be352`
- bridge_document_name: `gtkb-project-verified-completion-auq-trigger`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-verified-completion-auq-trigger-001.md`
- operative_file: `bridge/gtkb-project-verified-completion-auq-trigger-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
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
- Operative file: `bridge\gtkb-project-verified-completion-auq-trigger-001.md`
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

### F1 - The declared implementation scope omits required parity, test, and state paths

Severity: P1

Observation:

- `target_paths` lists `scripts/project_verified_completion_scanner.py`, `.claude/hooks/project-completion-surface.py`, two scanner test paths, `groundtruth-kb/src/groundtruth_kb/db.py`, `groundtruth-kb/tests/test_db.py`, `.claude/settings.json`, and `.codex/hooks.json` (`bridge/gtkb-project-verified-completion-auq-trigger-001.md:16`).
- IP-2 explicitly requires Codex parity: "mirror at `.codex/gtkb-hooks/project-completion-surface.py`" (`bridge/gtkb-project-verified-completion-auq-trigger-001.md:89`).
- IP-2 also writes session idempotency state under `.gtkb-state/project-completion-surface/` (`bridge/gtkb-project-verified-completion-auq-trigger-001.md:87`).
- The verification command runs `tests/hooks/test_project_completion_surface.py` (`bridge/gtkb-project-verified-completion-auq-trigger-001.md:132`).
- None of `.codex/gtkb-hooks/project-completion-surface.py`, `.gtkb-state/project-completion-surface/**`, or `tests/hooks/test_project_completion_surface.py` appears in `target_paths`.

Deficiency rationale:

The proposal cannot both require Codex parity and omit the Codex hook file from
the authorized implementation surface. It also cannot require a hook test file
or persistent idempotency-state path without authorizing and verifying those
paths. A latest GO would create an implementation-start packet that does not
cover files the proposal itself says must be created or exercised.

Impact:

Prime Builder would either be blocked by the implementation-start gate when
creating the missing paths, or would have to implement outside the reviewed
scope. Either outcome breaks the bridge audit trail for this governance hook.

Recommended action:

Revise `target_paths` and the verification plan to include every intended
implementation surface, at minimum:

- `.codex/gtkb-hooks/project-completion-surface.py` and any `.cmd` wrapper if Codex registration uses one.
- `tests/hooks/test_project_completion_surface.py` or the chosen `platform_tests/...` equivalent.
- `.gtkb-state/project-completion-surface/**` if implementation creates durable runtime state there.
- Existing Codex hook parity checks if `.codex/hooks.json` is modified.

Option rationale:

Expanding the reviewed surface is safer than leaving a parity hook implicit.
This project already treats cross-harness hook registration as a tested parity
surface, not as a side effect.

### F2 - Completion and retirement semantics are underspecified

Severity: P1

Observation:

- The proposal's top-level requirement says that on owner approval "the project authorization transitions to `completed` and the project is retired" (`bridge/gtkb-project-verified-completion-auq-trigger-001.md:18`).
- The claim repeats that `transition_project_authorization_to_completed()` transitions the authorization to `completed` and calls project retirement (`bridge/gtkb-project-verified-completion-auq-trigger-001.md:22`).
- The proposed DB method then says retirement is optional: "Optionally call retire_project(project_id) if the authorization was the sole active one" (`bridge/gtkb-project-verified-completion-auq-trigger-001.md:106`).
- The existing retirement API is a project-lifecycle service method, `ProjectLifecycleService.retire_project()`, not a `KnowledgeDB` method (`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:226`).

Deficiency rationale:

The proposal does not settle the load-bearing transition rule. If project
retirement is mandatory when all WIs for the authorization are VERIFIED, the
DB method cannot make retirement optional. If multiple active authorizations
mean the project must remain active, the proposal needs to state that rule and
map it to the source spec before claiming full implementation.

It also needs to define the layering boundary: either the transition lives in a
project lifecycle service that can call both authorization update and project
retirement, or the DB layer must expose primitive writes while the service
orchestrates the policy. A DB method that "calls project retirement" risks a
layer inversion unless the design is made explicit.

Impact:

The implementation could leave a completion-ready project active after owner
approval, retire a project while another active authorization still exists, or
duplicate lifecycle logic in the DB layer. Any of those outcomes weakens the
audit trail for project completion and retirement.

Recommended action:

Revise IP-3 to define the exact state machine:

- What happens when the completed authorization is the only active authorization.
- What happens when other active authorizations remain.
- Whether `project.status` changes to terminal immediately, waits for all active authorizations, or is outside this WI.
- Which layer owns orchestration: `groundtruth_kb.project.lifecycle` service vs `KnowledgeDB` primitives.

Add tests for sole-active authorization completion, multiple-active
authorization handling, missing AUQ evidence, and explicit owner-retire bypass.

## Positive Evidence

- The proposal cites the source governance spec and AUQ-related constraints.
- The owner-decision deliberation supports the Owner-confirmed-via-AUQ variant.
- The cited project authorization is active and includes `WI-3316`.
- The bridge applicability preflight has no missing required specs.
- The mandatory clause preflight reports zero blocking gaps.

## Required Revision

File a revised proposal that:

1. Adds the omitted Codex hook, hook-test, idempotency-state, and parity-check paths to the reviewed implementation surface.
2. Makes project completion and retirement semantics explicit for both single-active and multiple-active-authorization cases.
3. Places the transition orchestration in the correct layer and maps tests to that decision.
4. Keeps `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` at `specified` until the full owner-confirmed completion flow is implemented and tested.

File bridge scan: 1 entry processed.
