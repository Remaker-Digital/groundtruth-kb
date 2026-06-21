REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eead2-9d95-7ad1-b7e3-e9fc33cb8dbe
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder override via ::init gtkb pb

# Revised Defect-Fix Proposal - Loyal Opposition reviewer pool governance-grade routing

bridge_kind: prime_proposal
Document: gtkb-lo-reviewer-pool-governance-grade-routing
Version: 003
Date: 2026-06-21 UTC
Responds to: bridge/gtkb-lo-reviewer-pool-governance-grade-routing-002.md
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4698

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py"]

## Revision Summary

This revision answers the NO-GO at `bridge/gtkb-lo-reviewer-pool-governance-grade-routing-002.md` by removing all dispatcher configuration mutation from scope. The revised implementation request is source plus test-addition only:

- Removed the dispatcher TOML rule-file target from scope.
- Removed the dispatch rule-schema module target from scope.
- Removed the proposed rule-schema/config quality-floor field from this fast-lane slice.
- Replaced the config mutation with a source-level default governance-grade Loyal Opposition quality floor in the centralized selector.
- Replaced the existing-test-file target with a new focused regression file so the test work is `test_addition`, matching the cited standing PAUTH.
- Cleaned the live bridge status wording: this is a dispatchable `REVISED` proposal, not a draft.

No production deployment, credential lifecycle action, KB bulk mutation, formal spec mutation, or dispatcher TOML mutation is requested.

## First-Line Role Eligibility Check

- Owner session init: `::init gtkb pb`.
- Resolved interactive role for this session: Prime Builder.
- Durable registry note: harness `A` remains durably assigned Loyal Opposition; this filing uses the transcript-defined interactive Prime Builder override allowed by the session-role authority rules and does not change the durable registry.
- Latest bridge state before this revision: `NO-GO` at `bridge/gtkb-lo-reviewer-pool-governance-grade-routing-002.md`.
- Status authored here: `REVISED`.
- Eligibility result: Prime Builder is authorized to respond to a latest `NO-GO` proposal thread with `REVISED`.

## Claim

The current bridge dispatcher can select a low-cost Loyal Opposition harness for governance-grade bridge review even when that harness quality score is below the level needed to complete the review. The canary performed on 2026-06-21 confirmed the architectural route works: the dispatcher selected low-cost OpenRouter harness `F` for one LO item after temporary resume. The same canary also confirmed WI-4698 remains a blocker: `F` produced no verdict after more than five minutes and had to be killed, while Ollama harness `D` could not be contacted locally. This matches WI-4698's stored defect description: C/D/F are not reliable governance-grade reviewers, while the capable scores are A q88 and B q95.

Because the trigger currently calls the selector with a role-only `DispatchContext(required_role="loyal-opposition")`, a fix that depends on per-item TOML rule metadata is not needed for this immediate fast-lane repair. The selector itself should apply a conservative default quality floor for LO dispatch candidates so sub-floor reviewers are excluded before cost-first ranking can choose them.

## Defect / Reproduction

Reproduce the defect without launching any harness:

1. Build dispatch records with active LO candidates at q62, q72, q78, and q88.
2. Give the lower-quality candidates lower `dispatch_cost` so the existing cost-first ordering prefers them.
3. Call `select_dispatch_candidates(records, config, DispatchContext(required_role="loyal-opposition"))`.
4. Current behavior: the cheapest active LO candidates remain eligible and can sort ahead of the capable q88 reviewer.
5. Expected behavior: candidates below the governance-grade LO floor are removed before ranking. If no LO candidate clears the floor, the selector returns an empty list so dispatch fails closed and health reports the absence of an eligible LO target.

## In-Root Placement Evidence

All target paths are inside the GT-KB project root:

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py`

No application/adopter path is touched. No out-of-root artifact is read as authority or written as a GT-KB artifact.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the dispatcher is bridge infrastructure; this source/test-only repair is intended to restore bridge-review routing without bypassing the bridge.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the centralized dispatch service owns candidate eligibility and ranking semantics; the floor is an eligibility refinement applied before ranking.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - the dispatch envelope remains intact; this revision does not alter TOML rule shape or envelope parsing.
- `REQ-HARNESS-REGISTRY-001` - the selector uses existing `dispatch_quality` harness metadata as the quality signal.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch element precedence and role-default behavior remain unchanged; only the candidate set is narrowed for LO selection.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-4698 is a small, single-concern reliability defect fix under the standing reliability fast-lane.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps cited specifications to tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to GT-KB platform source and platform tests; no Agent Red or adopter boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4698 is an open standing-backlog work item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness fallback discipline is preserved; this repair ensures fallback does not land on known sub-floor LO harnesses.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect and acceptance criteria remain preserved in WI-4698 and this bridge thread.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this revision records the routing decision as a bridge proposal before implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the defect evidence, proposal revision, and later verification remain in governed artifacts rather than harness-local scratch.

## Prior Deliberations

- `DELIB-2780` - Bridge thread gtkb-headless-gemini-lo-dispatch-verification; prior context for C/Gemini LO dispatch and why quality-based routing matters.
- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - Bridge Dispatcher Redesign as Optimizing Multi-Harness Fabric; strategic context for capability-aware dispatch. This revision is a bounded immediate floor, not the full fabric redesign.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-ADVISORY-REVIEW-ROUTING-20260612` - prior advisory context on routing degraded LO work.
- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-4698 is P1 and pipeline-repair-adjacent.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization context for small defect/reliability fixes.

Sibling bridge thread: `bridge/gtkb-lo-dispatch-pipeline-repair-001.md` / WI-4679 repairs trigger-side retry and fall-through defects. WI-4698 is selector-side candidate eligibility: it prevents the dispatcher from choosing a known sub-floor LO reviewer in the first place.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) authorizes source, test_addition, and hook_upgrade classes for eligible reliability fast-lane work in this project. This revision is source plus test-addition only.
- `DELIB-20265457` authorized authoring reliability-fix bridge proposals for the project batch; WI-4698 is a P1 dispatch defect in that project.
- Current owner directive in this session: "Please proceed with WI-4698."
- No additional owner decision is needed for this revision because the NO-GO's config-mutation concern is resolved by removing all config mutation from scope.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` already places candidate eligibility and ranking in the centralized dispatch service, and `REQ-HARNESS-REGISTRY-001` already defines `dispatch_quality` as harness metadata. WI-4698's acceptance summary explicitly allows "capability-aware routing or quality floor"; this revision implements the quality-floor path without adding a new public API, CLI surface, config schema, or owner-facing workflow.

## Proposed Scope

1. In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, add a small default constant for governance-grade LO dispatch quality, proposed value `80.0`. This excludes the known q62/q72/q78 pool and admits the q88 LO-capable Codex record when active in the LO registry role.
2. Apply that floor inside `select_dispatch_candidates` after config overlay, active-role checks, dispatchability checks, and rule-context eligibility, but before ranking by `selection_order_for(context)`.
3. Scope the floor to `DispatchContext(required_role="loyal-opposition")` so Prime Builder selection is unchanged.
4. Use the same effective quality semantics as ranking: if `dispatch_quality` is missing or nonnumeric, compare with the existing default-quality behavior rather than raising.
5. Preserve fail-closed behavior: if no active dispatchable LO candidate meets the floor, return an empty candidate list. `collect_bridge_dispatch_status` already reports that as a FAIL finding for the role.
6. Add a new test file, `platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py`, with focused source/test-addition coverage. Do not edit the dispatcher TOML rule file or the dispatch rule-schema module in this slice.

This proposal intentionally leaves the richer capability-aware dispatcher fabric from `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` to future work. The goal here is the least risky fast-lane repair that makes low-cost harness reactivation safe only after they can meet the governance-grade quality floor.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_lo_quality_floor_excludes_subfloor_candidates_before_cost_ranking` | With q72 cheaper than q88, LO selection returns q88 and excludes q72 before ranking. |
| `REQ-HARNESS-REGISTRY-001` | `test_lo_quality_floor_uses_overlayed_dispatch_quality` | A temporary dispatch overlay quality value is applied before the floor comparison. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` / `DCL-DISPATCH-ENVELOPE-RULES-001` | `test_prime_builder_selection_is_not_affected_by_lo_floor` | Prime Builder role selection preserves existing cost/ranking behavior and does not apply the LO floor. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_lo_quality_floor_fails_closed_when_no_candidate_qualifies` | If all active LO candidates are q62/q72/q78, `select_dispatch_candidates` returns empty and status collection reports FAIL rather than dispatching to a sub-floor reviewer. |

Execution commands:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py
```

## Acceptance Criteria

1. LO dispatch candidates below the default governance-grade quality floor are excluded before ranking.
2. Prime Builder dispatch selection and non-LO roles are unaffected.
3. Config overlays are applied before quality-floor comparison.
4. If no active dispatchable LO candidate meets the floor, selection fails closed with no candidate and health reports a role eligibility failure.
5. No dispatcher TOML mutation is made.
6. No dispatch rule-schema module mutation is made.
7. Focused tests and existing dispatch-config regressions pass.

## Risks / Rollback

- Risk: the default floor is too high and leaves no LO candidate. Mitigation: fail-closed health output makes this visible immediately, and the current active q88 Codex LO record clears the proposed floor.
- Risk: source-level default logic is less expressive than future capability-aware routing. Mitigation: this is a narrow fast-lane repair; later dispatcher-fabric work can replace or generalize the constant through a separately authorized capability design.
- Risk: a low-cost harness improves but remains below the floor. Mitigation: its `dispatch_quality` metadata can be updated through the appropriate governed harness registry path after evidence exists; until then, it should not receive governance-grade LO work.
- Rollback: remove the floor helper/constant and its call from `select_dispatch_candidates`, then remove the new test file. No schema migration, config mutation, or durable dispatch state migration is involved.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py`

## Owner Action Required

None.
