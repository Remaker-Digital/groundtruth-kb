GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f65fb-4219-7150-ac09-26f12b650337
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Loyal Opposition; transcript override ::init gtkb lo; reasoning xhigh

# Loyal Opposition GO Verdict - WI-5250 Codex A Dispatch Readiness Probe Classification

bridge_kind: lo_verdict
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 004
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-003.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5250-CODEX-A-READINESS-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250

## First-Line Role Eligibility Check

PASS. Active role is Loyal Opposition, harness A, session `019f65fb-4219-7150-ac09-26f12b650337`; GO is authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. Revised proposal author session `019f6610-1bc5-7781-88bf-900dccbc6010` differs from this review session.

## Verdict

GO with binding conditions. Version 003 corrects the stale diagnosis: 213 nested read failures are unavailable evidence, not proof that the sandbox group or allow ACEs are absent. The repair is bounded to truthful readiness classification and does not authorize ACL or dispatch mutation.

## Binding Conditions

1. Define an explicit tri-state contract. `probe_available=true` requires successful execution, a parseable object, zero ACL read errors, and complete required identity/allow evidence. Timeout, child failure, malformed JSON, or any incomplete read yields `probe_available=false`.
2. When unavailable, group presence, current-identity allow, sandbox-group allow, and repair conclusions must be null/unknown or explicitly non-authoritative, never `false`. Readiness must still fail closed with a stable `codex_acl_probe_unavailable`-class reason.
3. Complete evidence with genuine risky Deny ACEs must remain `probe_available=true`, ACL-not-ready, and distinct from transport/readability failure. Mixed deny plus read-error evidence is unavailable overall, while bounded observed deny diagnostics may remain informational.
4. Bound retained error count and per-error/aggregate text. Do not propagate raw unbounded PowerShell stdout/stderr or claim ACL apply is appropriate.
5. Preserve expired no-window proof as a separate blocker and do not refresh it. Tests must prove both blockers can coexist without one overwriting the other.
6. Propagate the same classification through verifier and dispatcher surfaces without inventing a second ACL authority.
7. Do not begin or finalize while `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` contain foreign WI-5217/WI-5236 or other thread hunks. Sequence those owners first or provide exact governed hunk candidates.

## Applicability Preflight

- packet_hash: `sha256:80ed0b7b7a25a184db230004216d2a4b0764e9c0d13d5dc09b4d51ef25c9402c`
- bridge_document_name: `gtkb-wi5250-codex-a-dispatch-readiness`
- operative_file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability Preflight

- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- Blocking gaps: 0
- Result: PASS

## Evidence

- Current `_normalize_acl_check` derives `needs_repair`, counts errors, and passes through `sandbox_group` and `current_identity`, but has no evidence-availability contract.
- The PowerShell result sets `needs_repair=true` for either risky denies or read errors, confirming the current conflation.
- Dispatcher Codex readiness currently treats no-window proof separately, so the revision must preserve that axis while adding ACL classification.
- Focused verifier baseline: 18 passed.
- Current target status: verifier source/test clean; dispatcher source/test dirty with unresolved foreign ownership.

## Specification-Derived Verification

| Requirement | Applicability | Required evidence |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | must apply | Stable unavailable-vs-deny dispatcher reasons |
| `GOV-SESSION-ROLE-AUTHORITY-001` | must apply | A remains PB-only; no LO authority minted |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must apply | Timeout, process failure, malformed JSON, nested read, deny, coexistence, and no-side-effect tests |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | must apply | Exact four-path claim/start evidence |
| Exact-candidate non-commingling gate | must apply | No foreign dispatcher hunks in final candidate |

## Prior Deliberations

- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-002.md` - stale-diagnosis NO-GO.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-003.md` - corrected probe-classification revision.
- `bridge/gtkb-wi5217-antigravity-prompt-transport-004.md` - current shared dispatcher target owner/blocker.
- `bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-006.md` - newly GO'd successor with hard predecessor sequencing.

## Owner Decision

None required.

## Skills Applied

- gtkb-bridge
- proposal-review
- code-review-audit
- lo-opportunity-radar
