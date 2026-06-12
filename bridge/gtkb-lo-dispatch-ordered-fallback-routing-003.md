NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: corrected by Prime Builder after stale .gtkb-state/bridge-author-metadata/current.json injection

# Implementation Report - Ordered Fallback Routing for Cost-Optimized Loyal Opposition Dispatch

bridge_kind: implementation_report
Document: gtkb-lo-dispatch-ordered-fallback-routing
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: bridge/gtkb-lo-dispatch-ordered-fallback-routing-002.md

Project Authorization: PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4484
Recommended commit type: feature

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

---

## Implementation Claim

Implemented the approved phase-1 ordered fallback routing slice for standard
Loyal Opposition bridge dispatch. The cross-harness trigger now ranks active
Loyal Opposition dispatch candidates by numeric `reviewer_precedence`, attempts
the lowest-precedence ready candidate first, records skipped unavailable
candidates as evidence, and falls through deterministically to the next ready
candidate.

Prime Builder dispatch intentionally keeps the prior singleton-target safety
behavior: multiple active Prime Builder targets still produce a configuration
failure instead of silently selecting one.

This report does not claim full cheapest-backend operational availability.
That remains dependent on WI-4477, which covers Ollama server readiness and
autostart. This implementation only provides the ordered dispatcher behavior
needed once multiple registered Loyal Opposition backends are available.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `bridge/INDEX.md`
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md`

Separate enabling work under `gtkb-fab-14-gate-fp-feedback-loop-008` updated
`scripts/implementation_authorization.py` and
`platform_tests/scripts/test_fab14_requirement_sufficiency.py` to stop treating
the explicit negated sentence "No new or revised requirement is needed" as a
requirement-gap phrase. That gate repair unblocked the WI-4484 authorization
flow, but it is not claimed here as part of the WI-4484 dispatcher
implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Requirement-Derived Verification

### Dispatch Candidate Selection

Approved requirement: standard Loyal Opposition bridge dispatch should prefer
the cheapest suitable registered reviewer, using existing registry precedence,
and fall through when the preferred candidate is unavailable.

Implemented and tested:

- Active Loyal Opposition candidates are sorted by
  `(reviewer_precedence, harness_id)`.
- Missing or invalid `reviewer_precedence` values sort after valid numeric
  precedence values.
- The first ready candidate is selected for dispatch.
- A not-ready preferred candidate is recorded in
  `fallback_skipped_candidates` with readiness evidence, then the dispatcher
  tries the next candidate.
- If every Loyal Opposition candidate is unavailable, dispatch records
  `no_ready_target_for_role`.
- Role-level legacy aliases for `loyal-opposition` point to the selected ready
  target, not to a skipped preferred candidate.

### Prime Builder Safety Boundary

Approved constraint: this slice must not relax Prime Builder dispatch safety.

Implemented and tested:

- Multiple active Prime Builder dispatch targets still produce
  `dispatch_target_resolution_failed`.
- Ordered fallback is scoped to Loyal Opposition dispatch only.

## Verification Commands

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-lo-dispatch-ordered-fallback-routing
```

Observed result: authorization succeeded and produced
`PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484`.

```text
Remove-Item Env:\GTKB_NO_CROSS_HARNESS_TRIGGER -ErrorAction SilentlyContinue
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
```

Observed result: `72 passed in 2.86s`.

```text
Remove-Item Env:\GTKB_NO_CROSS_HARNESS_TRIGGER -ErrorAction SilentlyContinue
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short -k "ordered_fallback or prime_builder_multi_active"
```

Observed result: `4 passed, 68 deselected in 0.89s`.

```text
python -m pytest platform_tests\scripts\test_fab14_requirement_sufficiency.py -q --tb=short
```

Observed result: `8 passed in 0.25s`.

```text
python -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
```

Observed result: `4 files already formatted`.

## Acceptance Criteria Status

- PASS: multiple active Loyal Opposition backends no longer cause a
  multi-active target-resolution failure in the standard LO dispatch path.
- PASS: numeric `reviewer_precedence` determines candidate order.
- PASS: unavailable preferred candidates are skipped with recorded evidence.
- PASS: all-unavailable LO candidates record an explicit no-ready-target result.
- PASS: Prime Builder multi-active dispatch remains a configuration failure.
- PASS: targeted pytest and ruff verification passed.

## Residual Risk And Follow-Up

WI-4477 remains necessary before the lowest-cost Ollama reviewer can be treated
as reliably available. Until WI-4477 is complete, this implementation provides
deterministic fallback behavior but may still select Codex or OpenRouter when
Ollama is not ready.

Rollback is straightforward: revert the dispatcher and test changes listed in
this report, then remove this implementation report entry from the active
bridge chain if Loyal Opposition rejects the slice.
