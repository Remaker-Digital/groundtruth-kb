NEW

# Ordered Fallback Routing for Cost-Optimized Loyal Opposition Dispatch (WI-4484)

bridge_kind: prime_proposal
Document: gtkb-lo-dispatch-ordered-fallback-routing
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: hygiene-sweep-automation-2026-06-12
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; workspace-write; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4484
Program: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH (top-priority program; priority grouping)

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: dispatcher
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

The cross-harness bridge trigger already knows about multiple dispatchable
Loyal Opposition backends and already records a numeric
`reviewer_precedence` for each active harness in
`harness-state/harness-registry.json` (`ollama` D = 10, `codex` A = 20,
`openrouter` F = 30). However,
`scripts/cross_harness_bridge_trigger.py` still treats dispatch
resolution as a single-target role lookup, so standard Loyal Opposition
review cannot deliberately prefer the cheapest suitable backend first and
fall through deterministically when the preferred backend is unavailable
or not ready.

This proposal implements a narrow phase-1 routing policy for standard
Loyal Opposition bridge review: rank all active LO-capable targets by
existing `reviewer_precedence`, try the preferred candidate first, and
fall through to the next candidate when readiness or launchability
blocks the preferred one. The dispatcher must preserve current bridge
governance, current readiness checks, and current dispatch-state
auditing. It must not introduce active-orchestrator scoring, dynamic
quality optimization, or a new management agent; it only adds
deterministic ordered fallback across already-registered backends.

## Requirement Sufficiency

Existing requirements sufficient.

The current dispatch substrate plus existing owner decision already
constrain this change sufficiently: the cross-harness trigger remains
the canonical AXIS-1 dispatch surface; `harness-state/harness-registry.json`
remains the generated source for active harness topology and
`reviewer_precedence`; and bridge governance plus spec-derived
verification remain unchanged. No new or revised requirement is needed
before implementing deterministic ordered fallback routing.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
`scripts/cross_harness_bridge_trigger.py` and
`platform_tests/scripts/test_cross_harness_bridge_trigger.py`. This
slice uses the already-generated in-root `harness-state/harness-registry.json`
as read-only routing input and does not hand-edit generated registry
artifacts.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal changes the AXIS-1 dispatcher that consumes canonical bridge state; bridge governance and `bridge/INDEX.md` authority must remain unchanged.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant governing specs for the dispatcher and bridge workflow are linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove fallback routing behavior with executed regression tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project / Work Item / Project Authorization metadata are present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all edited files remain in-root platform artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-4484 is the standing-backlog work item governing this slice.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - the cross-harness trigger remains the canonical auto-trigger dispatch surface for dispatchable work; this slice adjusts target selection only.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - the existing single-harness coexistence/inertness contract must remain intact; this slice applies only to the normal multi-harness dispatch path.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - topology separation between single-harness and cross-harness modes must remain intact.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the dispatcher should read existing generated precedence/topology data, not create a hand-maintained shadow routing authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner-directed architecture preference is captured as a governed work item and bridge proposal rather than an ad hoc code edit.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this change follows the artifact-first implementation cycle rather than bypassing bridge governance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner directive and dispatch design preference are captured as durable lifecycle artifacts before code mutation.

## Prior Deliberations

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - owner directive making cost-optimized automatic dispatch top-priority, including the explicit precedence posture `ollama` preferred, `codex` backstop, `openrouter` fallback.
- `bridge/gtkb-fab-01-dispatch-substrate-revival-004.md` - VERIFIED foundation for active multi-harness dispatch launchability and honest event-source modeling.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-002.md` - GO thread establishing the telemetry and measurement foundation the later orchestrator direction will consume.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-11-06-58-dispatch-precedence-review.md` - Loyal Opposition advisory establishing that dispatch-cluster changes should be staged on top of FAB-01 and FAB-10 rather than as a parallel substrate.
- `WI-4477` - adjacent work item for Ollama readiness and autostart; explicitly excluded from this proposal's code scope.

## Owner Decisions / Input

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` records the owner directive that cost-optimized automatic dispatch is top-priority and that the dispatcher should prefer the cheapest viable reviewer first.
- 2026-06-12 owner directive in this session: implement logic in the dispatcher so work routes to the lowest-cost model believed able to do the job well, with fallback to the next best or cheapest available target when the first is unavailable.
- `PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484` is active for this work item with `source`, `test_addition`, and `config` mutation classes; forbidden operations include deploy, retired-poller restoration, and orchestrator-scope expansion.
- No further owner decision is required for this bounded phase-1 implementation. The dedicated Dispatch Manager idea remains out of scope here and is deferred to the broader orchestrator investigation under `WI-4438`.

## Proposed Scope

### IP-1 - Ordered candidate ranking for Loyal Opposition dispatch

Update `scripts/cross_harness_bridge_trigger.py` so the normal
multi-harness dispatch path resolves all active LO-capable targets,
sorts them by `reviewer_precedence` ascending, and attempts dispatch in
that order for standard Loyal Opposition review work.

- Reuse the existing `reviewer_precedence` field already present in `harness-state/harness-registry.json`; do not introduce a second routing authority.
- Preserve current `DispatchTarget` construction, current invocation surfaces, and current prompt generation.
- Preserve single-harness inertness and substrate mismatch behavior exactly.

### IP-2 - Readiness-gated fallback without configuration failure on multiple active LO backends

Change the resolver and dispatch flow so multiple active LO backends are
no longer treated as a fail-closed configuration error for this path.

- Preferred candidate ready -> dispatch to that candidate only.
- Preferred candidate not ready (`ollama_dispatch_not_ready`, `openrouter_dispatch_not_ready`, and similar) -> record the skip reason and try the next ranked candidate.
- Exhausted candidate set -> record a deterministic no-ready-target result rather than crashing the cycle.
- Prime Builder dispatch behavior remains single-target and unchanged in this slice.

### IP-3 - Durable selection evidence in dispatch-state and failure logs

Extend the per-run evidence so the chosen target and fallback reasons are
visible after the fact.

- Record the selected candidate harness id or recipient key when dispatch launches.
- Record skipped candidate reasons when fallback occurs.
- Keep the existing dispatch-failures and dispatch-state surfaces authoritative for diagnosis; do not add a new telemetry store in this slice.

### IP-4 - Focused regression coverage

Augment `platform_tests/scripts/test_cross_harness_bridge_trigger.py` to
cover:

- multiple active LO targets ranked by precedence;
- preferred ready target wins;
- preferred not-ready target falls through to next candidate;
- all candidates unavailable -> deterministic no-ready-target outcome;
- Prime Builder single-target resolution unchanged.

## Specification-Derived Verification Plan

| Spec / requirement | Derived test / evidence | Command |
|---|---|---|
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` (cross-harness trigger remains canonical dispatch surface) | focused trigger tests covering ranked LO fallback without changing the dispatch substrate | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` + `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | existing single-harness topology tests still pass unchanged | same pytest command above |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | tests prove precedence is read from generated registry data, not a second hard-coded authority | same pytest command above |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | repo-native lint and format checks on changed Python | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py`; `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` |

## Acceptance Criteria

1. Standard LO dispatch can operate with multiple active LO-capable backends without raising a multiple-active-target configuration error.
2. The dispatcher prefers the lowest `reviewer_precedence` ready candidate and falls through deterministically when a preferred candidate is unavailable or not ready.
3. Exhausting all LO candidates records a deterministic no-ready-target outcome in existing diagnostic surfaces.
4. Prime Builder target resolution and single-harness or substrate-mismatch behavior remain unchanged.
5. Focused pytest coverage passes, and changed Python is `ruff check` and `ruff format --check` clean.

## Risks / Rollback

- **Risk - broadening LO multi-target resolution could accidentally relax Prime behavior.** Mitigation: keep the fallback logic scoped to standard Loyal Opposition dispatch only; preserve Prime Builder resolution semantics and existing tests.
- **Risk - precedence-only routing could hide backend-specific readiness problems.** Mitigation: each skipped candidate must still record its existing readiness reason so fallback does not erase diagnosis.
- **Risk - owner expectation could drift toward active orchestrator behavior.** Mitigation: explicitly keep scoring, quality optimization, staged pipelines, and a dedicated dispatch-manager agent out of scope for this slice.
- **Rollback:** revert the dispatcher and focused test changes; dispatch returns to the current single-target-per-role behavior.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Recommended Commit Type

`feat` - adds deterministic cost-optimized fallback routing behavior to
the existing Loyal Opposition dispatcher without introducing a new
orchestration subsystem.

## Bridge Protocol Compliance

This proposal is filed at `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md`
with a matching `Document: gtkb-lo-dispatch-ordered-fallback-routing`
entry and `NEW: bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md`
status line inserted at the top of `bridge/INDEX.md`. It is append-only
and rewrites no prior bridge version. `bridge/INDEX.md` remains the
canonical workflow queue. This proposal changes only the target-selection
behavior of the existing AXIS-1 dispatcher and does not restore the
retired OS poller or retired smart poller.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
