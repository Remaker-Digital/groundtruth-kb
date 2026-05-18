GO

# Loyal Opposition Review: gtkb-harness-data-driven-dispatch-003

Document: gtkb-harness-data-driven-dispatch
Reviewed proposal: bridge/gtkb-harness-data-driven-dispatch-003.md
Verdict: GO
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-17 UTC

## Applicability Preflight

- packet_hash: `sha256:d4122fb70df4cb1df37252253f56e6e17da5dadce2e2e071f5ae2901e36aaca2`
- bridge_document_name: `gtkb-harness-data-driven-dispatch`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-data-driven-dispatch-003.md`
- operative_file: `bridge/gtkb-harness-data-driven-dispatch-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-data-driven-dispatch`
- Operative file: `bridge\gtkb-harness-data-driven-dispatch-003.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-2079` directly controls this proposal. Q9 decided that the cross-harness trigger dispatches harnesses data-driven from the registry `invocation_surfaces` column and rejected a hard-coded per-harness branch. Direct read command: `python -m groundtruth_kb deliberations get DELIB-2079 --json`.
- `DELIB-2080` is directly relevant. It amends the same Antigravity Integration design with full role portability and records the Gemini CLI headless invocation form for the Antigravity harness. Direct read command: `python -m groundtruth_kb deliberations get DELIB-2080 --json`.
- Deliberation semantic searches for harness-registry data-driven dispatch and role-portable invocation surfaces returned no additional matches; direct ID reads supplied the controlling owner decisions cited above.

## Review Findings

No blocking findings.

### F1 Resolution Accepted - P1 Governance Drift Cleared

Observation:
The `-002` NO-GO identified that the `-001` proposal retained a hard-coded `codex`/`claude` fallback switch after claiming FR8 compliance. The `-003` revision removes that fallback from the requested implementation and makes registry-supplied `invocation_surfaces` the sole command-construction path.

Evidence:
- Prior NO-GO: `bridge/gtkb-harness-data-driven-dispatch-002.md:57-87`.
- Revision response: `bridge/gtkb-harness-data-driven-dispatch-003.md:21-30`.
- Revised scope: `bridge/gtkb-harness-data-driven-dispatch-003.md:72-89`.
- Revised acceptance criteria: `bridge/gtkb-harness-data-driven-dispatch-003.md:132-136`.
- Current code still contains the switch at `scripts/cross_harness_bridge_trigger.py:456-479`, so the proposal is correctly scoped as implementation work rather than a false claim that the change already exists.

Deficiency rationale:
The blocking deficiency in `-001` was the conflict between a retained fallback and the governing requirement. The `-003` revision now aligns the requested implementation with `REQ-HARNESS-REGISTRY-001` FR8, whose current v2 text requires cross-harness bridge dispatch to resolve invocation commands from `invocation_surfaces` with no per-harness branch hard-coded into the trigger.

Recommended action:
Prime Builder may implement the revised scope. The post-implementation report must demonstrate that `_harness_command()` has no surviving `codex`/`claude` command branch and that missing, absent-`headless`, and malformed `invocation_surfaces` fail closed to `None` for every harness, including Claude and Codex records.

### Scope And Test Mapping Accepted

Observation:
The proposal carries the required metadata, cites the active project authorization, and maps the relevant specifications to concrete unit and integration tests.

Evidence:
- Project metadata: `bridge/gtkb-harness-data-driven-dispatch-003.md:9-13`.
- Project authorization check: `python -m groundtruth_kb projects show PROJECT-HARNESS-REGISTRY-REFACTOR --json` reports authorization `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION` as `active`, scoped to REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344; the project work-item list includes WI-3344.
- Specification links: `bridge/gtkb-harness-data-driven-dispatch-003.md:38-49`.
- Spec-to-test mapping: `bridge/gtkb-harness-data-driven-dispatch-003.md:115-123`.
- Current harness projection and DB rows have `invocation_surfaces: null` for harnesses A and B, matching the proposal's claim that IP-2 is load-bearing.

Deficiency rationale:
No deficiency found. The proposal now treats existing Claude/Codex `invocation_surfaces` population as mandatory, adds seed-path consistency, and adds both unit tests for command construction and an integration test for `_resolve_dispatch_target()` projection attachment. That covers the previous governance failure and the main operational regression risk.

Recommended action:
Prime Builder should preserve the implementation order implied by the proposal: append the Claude/Codex harness record versions with structured `headless.argv` templates, regenerate `harness-state/harness-registry.json`, then land the trigger code path and regression tests in the same implementation thread.

## Loyal Opposition Responses To Proposal Asks

1. Structured `invocation_surfaces.headless.argv` is accepted. The ordered argv list with `{{PROMPT}}` and `{{PROJECT_ROOT}}` placeholders substituted as individual argv elements is the right encoding because it avoids shell-parsing arbitrary bridge text.
2. Splitting Antigravity harness-record registration and its concrete `invocation_surfaces` value into WI-3348 remains the correct boundary. This thread should make the trigger consume registry invocation data; the later thread can register Antigravity's actual record.
3. Uniform fail-closed `None` / `unknown_recipient` behavior for missing, malformed, or unsupported `invocation_surfaces` is accepted, including for Claude and Codex. Because this removes the legacy safety fallback, the implementation report must include observed evidence that Claude and Codex dispatch work through populated registry data.

## Verification Expectations For Post-Implementation Report

The implementation report must carry forward the linked specifications and include observed results for at least:

- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-data-driven-dispatch`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-data-driven-dispatch`

It should also cite the resulting current `harnesses` versions for A and B, the regenerated `harness-state/harness-registry.json` `invocation_surfaces.headless.argv` values, and source evidence that `_harness_command()` no longer contains a per-harness command switch.

## Decision Needed From Owner

None.
