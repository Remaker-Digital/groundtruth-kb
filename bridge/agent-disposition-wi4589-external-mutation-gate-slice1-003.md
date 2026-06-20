NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ee2c3-1add-7ef1-bc05-9b0e8c21b5c9
author_model: gpt-5-codex
author_model_version: 2026-06-19
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# WI-4589 External Mutation Authorization Gate - Slice 1 Implementation Report

bridge_kind: implementation_report
Document: agent-disposition-wi4589-external-mutation-gate-slice1
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/agent-disposition-wi4589-external-mutation-gate-slice1-002.md
Approved proposal: bridge/agent-disposition-wi4589-external-mutation-gate-slice1-001.md
Implementation commit: 20f5dd2ba
Recommended commit type: feat:

## Implementation Claim

Implemented the approved additive external-mutation decision module and focused tests under the exact GO target paths:

- `scripts/external_mutation_guard.py`
- `platform_tests/scripts/test_external_mutation_guard.py`

The module is a pure preflight decision layer. It classifies external action attempts, requires owner-visible authority, bridge GO evidence when required, harness/session/model provenance, and a compatible post-action receipt plan before returning an allowed decision. It does not execute network calls, deployment commands, credential reads or writes, filesystem writes, bridge writes, MemBase writes, or receipt writes.

This slice does not claim full `WI-4589` closure. Follow-on slices still need hook, connector, deployment-helper, harness, and status-surface integration.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `.claude/rules/file-bridge-protocol.md`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `REQ-HARNESS-REGISTRY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `WI-4589`

## Owner Decisions / Input

No new owner decision was required for this implementation report. The implementation stayed inside the existing owner-approved project authorization and Loyal Opposition GO scope:

- `DELIB-20263455`
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA`
- `bridge/agent-disposition-wi4589-external-mutation-gate-slice1-002.md`

## Prior Deliberations

- `DELIB-20263455` - owner-approved Agent Disposition and Protocol Enforcement planning and ranked child work items.
- `DELIB-0862` - bridge-first governance.
- `DELIB-20260872` - project authorization grants bridge-cycle eligibility, not blanket implementation authority.
- `DELIB-2258` - implementation-start and work-intent gating are durable safety controls.
- `DELIB-20261178` - live versioned bridge and dispatcher state are authority, not stale summaries.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - planning-only GO for the umbrella child sequence.
- `bridge/agent-disposition-wi4588-protected-mutation-guard-slice1-004.md` - VERIFIED protected mutation guard predecessor.
- `bridge/agent-disposition-wi4590-post-action-receipts-slice1-004.md` - VERIFIED post-action receipt contract reused for receipt vocabulary compatibility.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `.claude/rules/file-bridge-protocol.md`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Focused pytest covers fail-closed behavior when current GO evidence is missing and no bridge-bypass allow path exists. Applicability preflight passed with no missing required specs. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Focused pytest covers `missing_authority`; allowed decisions require structured owner-visible authority. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, `REQ-HARNESS-REGISTRY-001` | Focused pytest covers `missing_harness_provenance`; allowed decisions carry bridge thread, bridge version, and work item evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Focused pytest covers production deployment and credential lifecycle denial, including explicit approval still denied when active PAUTH forbids the class. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries project metadata, linked specs, spec-to-test mapping, command evidence, and observed results. Clause preflight passed with zero blocking gaps. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Focused pytest covers missing/incomplete receipt plans and incompatible receipt mutation classes before any allow result. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation and tests are in-root approved target paths; `Test-Path bridge/INDEX.md` returned `False`. |
| `GOV-STANDING-BACKLOG-001`, `WI-4589` | Work stayed scoped to the ranked `WI-4589` child slice and does not silently claim full WI completion. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_external_mutation_guard.py -q --tb=short`
- `python -m ruff check scripts/external_mutation_guard.py platform_tests/scripts/test_external_mutation_guard.py`
- `python -m ruff format --check scripts/external_mutation_guard.py platform_tests/scripts/test_external_mutation_guard.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4589-external-mutation-gate-slice1`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4589-external-mutation-gate-slice1`
- `Test-Path -LiteralPath bridge/INDEX.md`
- `git commit -m "feat: add external mutation guard"`

## Observed Results

- Pytest: 13 passed in 1.29s.
- Ruff check: `All checks passed!`
- Ruff format check: `2 files already formatted`.
- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; packet hash `sha256:13b5595f215896f300baeb6f08e726efa18489afdb5d0803fddeaa241c775006`.
- ADR/DCL clause preflight: mandatory mode; clauses evaluated 5; must_apply 1; evidence gaps in must_apply clauses 0; blocking gaps 0; exit 0.
- Retired bridge index check: `False`.
- Commit: `[develop 20f5dd2ba] feat: add external mutation guard`; 2 files changed, 474 insertions.

## Files Changed

- `scripts/external_mutation_guard.py` - new pure external-action guard with stable decision classes, authority/provenance checks, receipt-plan compatibility, and fail-closed reason codes.
- `platform_tests/scripts/test_external_mutation_guard.py` - new focused tests for deny/allow behavior and no filesystem mutation during decision evaluation.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: this adds a new deterministic guard capability plus tests.

```text
 platform_tests/scripts/test_external_mutation_guard.py | 188 ++++++++++++++
 scripts/external_mutation_guard.py                    | 286 +++++++++++++++++++++
 2 files changed, 474 insertions(+)
```

## Acceptance Criteria Status

- [x] A reusable external-mutation guard module returns structured allow/deny results before any external side effect.
- [x] The module fails closed for unsupported action classes, missing owner-visible authority, missing bridge GO when required, missing harness/session provenance, missing receipt plans, production deployment without explicit owner approval, and credential lifecycle actions.
- [x] Tests demonstrate allow and deny cases without network access, cloud-provider calls, deployment commands, credential mutation, MemBase mutation, or bridge mutation.
- [x] The implementation report identifies follow-on hook, connector, deployment-helper, and harness integrations instead of claiming full `WI-4589` closure.

## Risk And Rollback

Residual risk is integration drift: this slice only creates the decision module and tests. Follow-on slices must wire callers to the guard and ensure post-action receipts are actually emitted after allowed external actions.

Rollback before follow-on integration is path-local: revert commit `20f5dd2ba`, removing `scripts/external_mutation_guard.py` and `platform_tests/scripts/test_external_mutation_guard.py`. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that commit `20f5dd2ba` satisfies the approved slice scope and target paths.
2. Confirm the tests derive from the linked specifications and the GO conditions.
3. Return `VERIFIED` if satisfied, otherwise return `NO-GO` with findings.
