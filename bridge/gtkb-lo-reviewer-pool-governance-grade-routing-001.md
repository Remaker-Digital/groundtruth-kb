NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Loyal Opposition reviewer pool cannot complete governance-grade bridge reviews

bridge_kind: prime_proposal
Document: gtkb-lo-reviewer-pool-governance-grade-routing
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4698

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "config/dispatcher/rules.toml", "platform_tests/scripts/test_bridge_dispatch_config.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The bridge LO dispatch ranking in `config/dispatcher/rules.toml` + `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` ranks Loyal Opposition candidates `cost`-first (rule `bridge-loyal-opposition-cheap-fast-default`: `prefer = ["cost", "availability", "quality", ...]`), which deterministically routes every NEW/REVISED review to the cheapest LO harness regardless of its quality score. The cheapest LO targets (D ollama q62, F openrouter q72) cannot complete governance-grade reviews: ollama exhausts its turn budget (`max_turn_exhaustion`) and openrouter returns no verdict (`no_verdict_produced`) — both recognized runtime-failure classes in `bridge_dispatch_config.py` — so their circuit breakers trip and the higher-quality LO targets are never tried. The selector has no quality-floor concept, so a rule cannot express "route reviews only to LO harnesses at or above quality N." That missing filter is the defect: a known-incapable harness is selected ahead of capable ones and the review pipeline stalls.

## Defect / Reproduction

Observed incident (origin of WI-4698): configured LO reviewer harnesses (C antigravity/gemini-2.5-flash q78, D ollama q62, F openrouter q72) fail governance-grade reviews — ollama `max_turn_exhaustion`, openrouter `no_verdict_produced` — and all their circuit breakers tripped, leaving ~8-9 bridge items (including the session-start queue) stuck. The only harnesses scored capable of governance-grade review (A Codex q88, B Claude q95) are both Prime Builder, so they are not LO dispatch targets.

Reproduction (logical, deterministic, no live harness needed): build a dispatcher config with two active LO targets — a cheap low-quality one (e.g. `dispatch_cost = 20`, `dispatch_quality = 62`) and a costlier high-quality one (e.g. `dispatch_cost = 70`, `dispatch_quality = 90`) — and the current `bridge-loyal-opposition-cheap-fast-default` rule (`prefer = ["cost", ...]`). Call `select_dispatch_candidates(records, config, DispatchContext(required_role="loyal-opposition"))`. The current code returns the cheap low-quality harness first; there is no way to express a quality floor, so the high-quality harness can never be preferred for a governance-grade review. Expected: a rule may declare a `min_quality` floor that filters out LO candidates below the floor so the capable harness is selected (and, when no candidate clears the floor, the selector surfaces an empty, fail-closed result rather than silently dispatching an incapable harness).

## Pre-Filing Preflight Evidence

- Applicability preflight (`scripts/bridge_applicability_preflight.py --content-file ...`): `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. (The content-derived `packet_hash` is emitted by the preflight at file/review time; it is intentionally not pinned here because any subsequent edit recomputes it. Re-run the preflight at filing time and cite the then-current hash in the GO verdict.)
- Clause preflight (`scripts/adr_dcl_clause_preflight.py --content-file ...`): exit 0; 4/4 `must_apply` clauses have evidence; 0 blocking gaps.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py`, `config/dispatcher/rules.toml`, `platform_tests/scripts/test_bridge_dispatch_config.py`. No application/adopter surface is touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the dispatch selector is bridge infrastructure; this fix restores correct bridge-review routing so NEW/REVISED reports reach a reviewer capable of completing them, which is core bridge-function authority.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governing spec for the centralized dispatch service's eligibility/ranking semantics; the `min_quality` filter is an additive eligibility refinement within that service's contract.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch-envelope routing/eligibility conformance constraints the new quality-floor rule must honor (the filter narrows eligibility; it does not alter envelope shape).
- `REQ-HARNESS-REGISTRY-001` - harness eligibility/availability and the `dispatch_quality` axis the floor compares against; the fix prevents a known-incapable harness from being selected ahead of capable ones.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch-envelope element semantics; the quality floor is applied during candidate selection and does not change the routing-override/role-default precedence of the envelope.
- `GOV-RELIABILITY-FAST-LANE-001` - this is a small, single-concern reliability defect fix routed under the standing reliability fast-lane.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix keeps the durable dispatch-routing rule (a tracked config artifact) consistent with the harness quality metadata, preserving the artifact-network rather than burying routing logic in code.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives every test from the cited specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - confirmed NOT applicable: this defect fix changes dispatch candidate ranking only and introduces no owner-decision/AUQ policy surface; cited for completeness because the scaffold seeded it.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform dispatch module (`groundtruth-kb/src/...`), platform config, and platform tests; no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4698 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness dispatch fallback discipline; this fix complements the sibling fall-through repair (WI-4679) by ensuring the candidate the fallback lands on actually meets the governance-grade quality floor.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the routing decision remains artifact-backed (a declarative `min_quality` field in the tracked rules config) rather than inferred or hard-coded.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the dispatch-config selector triggers updating its governing config artifact and its test, keeping the lifecycle of the routing rule consistent.

## Prior Deliberations

- `DELIB-2780` - Bridge thread gtkb-headless-gemini-lo-dispatch-verification: prior verification of headless gemini (C) LO dispatch; the WI-4698 incident notes the gemini-tier regression that contributes to the stalled pool, so this is the directly-relevant routing precedent.
- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - Bridge Dispatcher Redesign as Optimizing Multi-Harness Fabric (owner deliberation 2026-06-20): the strategic framing for capability-aware multi-harness dispatch; this fast-lane fix is a bounded, immediate increment toward that fabric (a quality floor), not the full redesign.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-ADVISORY-REVIEW-ROUTING-20260612` - Bridge dispatch overhaul: Claude Code manual advisory review routing — prior context on routing degraded LO work, establishing that routing quality (not just availability/cost) is a recognized dispatch concern.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope, P1, pipeline-repair-adjacent).

Sibling bridge thread (live, related, not yet a DELIB): `bridge/gtkb-lo-dispatch-pipeline-repair-001.md` (WI-4679) repairs two trigger-side dispatch defects (F sticky-signature backoff, C tier fall-through). WI-4698 is complementary and at the selector/config layer: WI-4679 makes the pipeline retry/fall-through correctly; WI-4698 ensures the candidate it falls through to clears a governance-grade quality floor. The two do not overlap in target paths (WI-4679: `scripts/cross_harness_bridge_trigger.py`; WI-4698: `bridge_dispatch_config.py` + `rules.toml`).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing reliability fast-lane authorization, `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4698 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the routing defect, and is bounded to a small additive config-field + selector filter plus tests, so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the owner direction establishing the standing reliability fast-lane for small defect fixes; this WI fits the fast-lane criteria (defect origin, single concern, no new requirement).
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items, pipeline-repair and P1/P2 first; WI-4698 is P1 and directly pipeline-repair-related.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and `DCL-DISPATCH-ENVELOPE-RULES-001` already establish that the dispatch service selects eligible candidates and ranks them by declarative rule preference, and `REQ-HARNESS-REGISTRY-001` already defines `dispatch_quality` per harness. This fix adds an optional, declarative `min_quality` eligibility filter to the existing rule schema so the existing quality metadata can gate selection; it does not introduce a new capability contract or new owner-facing behavior. No new or revised requirement/specification is introduced. (The WI's broader suggestion of "an LO quality floor or routing governance-grade proposals to a higher-quality LO" is satisfied by this additive config filter; the full capability-aware fabric in `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` is a separate, larger, requirement-bearing project and is explicitly out of scope here.)

## Proposed Scope

1. Extend the dispatch rule schema in `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py`'s `DispatchRule` with an optional `min_quality: float | None = None` field, parsed in `DispatchRule.from_mapping` (tolerant numeric parse; absent/invalid → `None` = no floor). This is an additive field; existing rules without it are unchanged.
   - Note: `DispatchRule` lives in `bridge_dispatch_rules.py` (an authorized target path), which is imported by `bridge_dispatch_config.py`. The schema field is small; the behavioral application is in the selector (step 2).
2. In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` `select_dispatch_candidates`, after role/dispatchability admission and before ranking, apply the active rule's `min_quality` floor (resolved via the same `matching_rules`/`selection_order_for` path already used for `prefer`): drop any candidate whose `dispatch_quality` is below the floor. Resolve the candidate's quality through the existing overlay (`apply_dispatch_config_to_record`) with the established default. A candidate with no quality value uses the existing default (50.0) for comparison, matching `_rank_key`'s default semantics. When no rule declares a floor, behavior is byte-identical to today.
   - Fail-closed posture: if the floor filters out all candidates, the selector returns an empty list (the existing `collect_bridge_dispatch_status` already surfaces "no active dispatchable harness is eligible for role" as a FAIL finding), so the dispatcher does not silently fall back to a sub-floor harness. This is the conservative/correct posture for the defect.
3. In `config/dispatcher/rules.toml`, add a `min_quality` floor to the `bridge-loyal-opposition-cheap-fast-default` rule (or a new governance-grade LO rule) set to a value that admits the capable LO target(s) and excludes the known-incapable ones (the exact floor value is a one-line config decision; e.g. a floor at the antigravity/gemini quality band so q62/q72 are excluded while a ≥78 LO is admitted). Keep the rule's existing `prefer` ordering for tie-break among the surviving candidates. Document the floor's intent inline.
4. Add regression tests in `platform_tests/scripts/test_bridge_dispatch_config.py` (see verification plan).

This is the defect-removal path. The WI's alternative framing ("capability-aware dispatch routing" as a full subsystem) is a larger, requirement-bearing redesign (`DELIB-20260620...`) and is explicitly out of scope for this fast-lane defect fix; this fix is the minimal additive filter that stops a known-incapable harness from being selected ahead of a capable one.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (rule-declared eligibility filters the candidate set) | `test_min_quality_floor_excludes_subfloor_lo_candidate` | With a rule declaring `min_quality` above a cheap low-quality LO's score, `select_dispatch_candidates` excludes that candidate and returns the higher-quality LO first. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` (eligibility narrowing must not alter unfloored behavior) | `test_no_min_quality_preserves_existing_ranking` | A config with no `min_quality` on any rule produces byte-identical candidate ordering to the pre-change `cost`-first behavior (no regression). |
| `REQ-HARNESS-REGISTRY-001` (`dispatch_quality` metadata gates selection; fail-closed when none qualify) | `test_min_quality_floor_fail_closed_when_no_candidate_qualifies` | When the floor exceeds every active LO candidate's quality, `select_dispatch_candidates` returns an empty list and `collect_bridge_dispatch_status` reports FAIL ("no active dispatchable harness is eligible for role 'loyal-opposition'") rather than selecting a sub-floor harness. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (governance-grade reviews route to a capable reviewer) | `test_rules_toml_lo_rule_declares_governance_grade_floor` | The shipped `config/dispatcher/rules.toml` LO rule declares a `min_quality` floor that excludes the q62/q72 LO targets and admits the ≥78 LO target (config-level acceptance assertion). |

Execution commands:
- `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py config/dispatcher/rules.toml platform_tests/scripts/test_bridge_dispatch_config.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py platform_tests/scripts/test_bridge_dispatch_config.py`

(Note: `ruff format --check` is applied to the `.py` files only; `rules.toml` is excluded from the Python formatter and validated by `tomllib` parse within the config loader and tests.)

## Acceptance Criteria

1. `select_dispatch_candidates` honors an optional rule-declared `min_quality` floor: candidates below the floor are excluded before ranking; surviving candidates keep the rule's existing `prefer` ordering.
2. With no `min_quality` declared, candidate selection is byte-identical to current behavior (no regression for any existing rule).
3. When the floor excludes all LO candidates, the selector returns empty and the status collector reports FAIL (fail-closed; no silent sub-floor dispatch).
4. The shipped `config/dispatcher/rules.toml` LO rule declares a governance-grade `min_quality` floor that excludes q62/q72 and admits the capable LO target.
5. The four derived tests pass; `ruff check` and `ruff format --check` are clean on the changed `.py` files; `rules.toml` parses cleanly.

## Risks / Rollback

- Risk: setting the floor too high strands LO dispatch entirely (no candidate qualifies) → pipeline stalls in a fail-closed state. Mitigation: the chosen floor admits at least one active LO target (the ≥78 harness); the fail-closed FAIL finding makes the condition loud and immediately diagnosable via `gt bridge dispatch status`/`health`, rather than silent mis-routing.
- Risk: over-tightening could change selection for unrelated roles. Mitigation: `min_quality` is rule-scoped; only the LO rule(s) that declare it are affected; the Prime Builder rule is untouched.
- Risk: the quality scores are coarse heuristics, so the floor is a blunt instrument. Mitigation: this fix is the bounded fast-lane increment; the WI explicitly leaves richer capability-aware routing to the dispatcher-fabric project (`DELIB-20260620...`).
- Rollback: remove the `min_quality` field application in `select_dispatch_candidates` and the `min_quality` line from `rules.toml`; the schema field is additive and inert without the config line. Fully reversible with no migration and no state change.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` (apply the floor in `select_dispatch_candidates`)
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py` (additive `min_quality` field on `DispatchRule` + `from_mapping` parse)
- `config/dispatcher/rules.toml` (declare the governance-grade LO `min_quality` floor)
- `platform_tests/scripts/test_bridge_dispatch_config.py` (four derived regression tests)

## Recommended Commit Type

`fix`
