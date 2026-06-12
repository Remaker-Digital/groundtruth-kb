GO

bridge_kind: loyal_opposition_review
Document: gtkb-lo-dispatch-ordered-fallback-routing
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md

# Loyal Opposition Review - Ordered Fallback Routing

## Review Scope

Reviewed `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md` for
WI-4484 / PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH, including live bridge state,
the current dispatcher implementation, harness registry precedence data,
project authorization, backlog dependencies, and mandatory bridge preflights.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review.
The proposal records `author_session_context_id:
hygiene-sweep-automation-2026-06-12`; this review is running in Codex thread
`019ebc90-8c96-7b30-8669-cf3cbea03bc5`.

## Dependency And Precedence Check

The cost-optimized autodispatch project is currently rank-1 / top-priority.
`WI-4484` is P1 and depends on `WI-4477`; `WI-4477` is also P1 and depends on
`WI-4473`. Live backlog state shows `WI-4473` is resolved / VERIFIED, while
`WI-4477` remains open for Ollama server readiness and autostart.

That open dependency does not block this bounded phase-1 proposal because the
proposal explicitly excludes Ollama autostart/readiness and implements only
dispatcher fallback behavior when a preferred backend is unavailable. Prime
Builder must not claim the cheapest reviewer is reliably available until
`WI-4477` is completed; this GO authorizes only the fallback-selection slice.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:4c34cef4249058c0078a0f657fb7d0e7be73b547d2283a9bd4d0695034fbb3b3`
- bridge_document_name: `gtkb-lo-dispatch-ordered-fallback-routing`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md`
- operative_file: `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-dispatch-ordered-fallback-routing`
- Operative file: `bridge\gtkb-lo-dispatch-ordered-fallback-routing-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` is cited by the
  proposal and is the owner-decision basis for cost-optimized automatic
  dispatch.
- `bridge/gtkb-fab-01-dispatch-substrate-revival-004.md` is VERIFIED and
  provides the active multi-harness dispatch launchability foundation.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-002.md` is GO and
  remains the telemetry/claim-contract follow-on foundation.
- `WI-4477` remains open and is deliberately excluded from this slice.
- Deliberation search for `cost optimized autodispatch reviewer_precedence
  ordered fallback` returned no additional hits.

## Evidence Checks

- `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-lo-dispatch-ordered-fallback-routing --format json --preview-lines 120`
  reported the live thread as `NEW: bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md`
  with `drift: []` before this verdict.
- `python -m groundtruth_kb backlog show WI-4484 --json` shows the P1 work item
  belongs to PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH and carries the phase-1
  fallback-routing acceptance summary.
- `python -m groundtruth_kb backlog show WI-4477 --json` shows the open Ollama
  readiness/autostart dependency and confirms the implementation report for
  this slice must not claim Ollama is reliably dispatch-ready.
- `python -m groundtruth_kb projects authorizations PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH --json`
  shows active `PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484`,
  scoped to WI-4484 with `source`, `test_addition`, and `config` mutation
  classes.
- Live `harness-state/harness-registry.json` records active LO recipients
  `ollama` D precedence 10, `codex` A precedence 20, and `openrouter` F
  precedence 30.
- Live `scripts/cross_harness_bridge_trigger.py` already has a plural
  `_resolve_dispatch_targets` path, but it returns active matching targets in
  registry order and the dispatch loop appends every ready LO target to
  `pending_by_target`. The requested implementation must therefore select the
  first ready candidate by `reviewer_precedence`, not merely add plural-target
  support.

## Review Findings

No blocking findings.

## Implementation Constraints

- Keep this slice limited to ordered fallback selection for standard Loyal
  Opposition dispatch. Do not implement Ollama autostart/readiness or active
  orchestrator scoring under this GO.
- Sort LO candidates by numeric `reviewer_precedence`, then dispatch only the
  first ready candidate for a given LO actionable batch.
- Record skipped preferred-candidate readiness reasons without erasing the
  existing readiness diagnostics.
- Preserve Prime Builder dispatch behavior, single-harness inertness, substrate
  mismatch handling, and the existing implementation-start / bridge authority
  gates.
- The implementation report must explicitly state that full cheapest-backend
  availability remains dependent on WI-4477.

## Opportunity Radar

No separate advisory is needed. The deterministic-service opportunity is the
work itself: route selection should be a small dispatcher policy with focused
tests, not session-time manual backend choice.

## Verdict

GO for implementation within `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md`
scope and the constraints above.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
