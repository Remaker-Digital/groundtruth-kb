NEW

# Implementation Proposal - Flatten dispatch ranking values to a single Codex baseline

bridge_kind: prime_proposal
Document: gtkb-wi5033-dispatch-ranking-flatten
Version: 001 (NEW; implementation proposal)
Date: 2026-07-07 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; Codex desktop execution

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5033-RANKING-FLATTEN-20260707
Project: PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION
Work Item: WI-5033

target_paths: ["groundtruth.db", "harness-state/harness-registry.json", ".gtkb-state/bridge-dispatch-config-transactions/audit.jsonl"]

## Claim

Implement WI-5033 by flattening dispatcher ranking values to the Codex/A baseline after WI-5032's uniform-random terminal tiebreak reached VERIFIED.

The implementation will update only dispatch ranking values for harnesses `B`, `C`, `D`, `E`, and `F`:

- `dispatch_quality = 90`
- `dispatch_cost = 60`
- `dispatch_availability = 90`
- `reviewer_precedence = 20`

Harness `A` already reports this baseline and will be used as the comparison value, not modified. Roles, lifecycle statuses, `can_receive_dispatch`, `can_fire_events`, max-items caps, invocation surfaces, model configuration, and capability flags are explicitly out of scope.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5033 is a bounded owner-approved configuration/registry normalization after WI-5032. The live authorizations and specs already cover the dispatcher control surface, harness registry authority, project authorization, bridge gating, and post-implementation verification.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `E:\GT-KB\groundtruth.db`
- `E:\GT-KB\harness-state\harness-registry.json`
- `E:\GT-KB\.gtkb-state\bridge-dispatch-config-transactions\audit.jsonl`

No files outside `E:\GT-KB` are required or authorized.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected/governed implementation work must proceed through the numbered bridge file chain and latest `GO` before mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Owner decisions, PAUTH, work item state, bridge proposal, and implementation report remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The work preserves traceability across MemBase, bridge, project authorization, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5033 moves through explicit backlog, proposal, implementation report, and verification lifecycle states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All live GT-KB mutation targets stay under the `E:\GT-KB` root boundary.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - WI-5033 is covered by bounded PAUTH `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5033-RANKING-FLATTEN-20260707`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - The PAUTH authorizes proposal/report pursuit but does not bypass bridge `GO` or implementation-start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal includes machine-readable PAUTH, project, and work item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the governing specs for the intended implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must map each linked requirement to executed tests/status checks.
- `GOV-STANDING-BACKLOG-001` - WI-5033 remains governed backlog work in the dispatch-selection self-optimization project.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Dispatch selection uses centralized dispatcher status/configuration surfaces rather than ad hoc edits.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Dispatcher architecture remains intact; this changes ranking attributes only, not topology or runtime substrate.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - Single-harness dispatcher behavior must remain compatible with the governed dispatcher status and selection surfaces.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - Harness-state authority remains consolidated through MemBase plus generated projection.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Verification must prove the generated projection and status surfaces are fresh after the mutation.
- `REQ-HARNESS-REGISTRY-001` - Harness ranking and reviewer-precedence fields are append-only MemBase harness registry attributes with a generated flat projection.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - Verification reads harness-state through `gt harness` / `gt bridge dispatch status`, not direct projection reads.

## Prior Deliberations

- `DELIB-202665871` - Owner approved WI-5033 implementation authorization after WI-5032 reached VERIFIED.
- `DELIB-DISPATCH-RANKING-NORMALIZATION-20260705` - Owner directive to flatten ranking values to the Codex baseline after the tiebreak fix.
- `DELIB-202665442` - Dispatch-field source-of-truth home is the registry/MemBase path for this project.
- `DELIB-202665447` - Selection model uses per-lane objective/ranking with median/tail floors; WI-5033 is the value-normalization follow-on.
- `bridge/gtkb-wi5032-uniform-random-dispatch-tiebreak-004.md` - WI-5032 reached VERIFIED and unblocks WI-5033.

## Owner Decisions / Input

- `DELIB-202665871` - Owner authorized WI-5033 on 2026-07-07.
- `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5033-RANKING-FLATTEN-20260707` - Active bounded project authorization for this proposal and later GO-gated implementation.

## Proposed Scope

After Loyal Opposition returns `GO`, Prime Builder will:

1. Open a live GO implementation claim for `gtkb-wi5033-dispatch-ranking-flatten`.
2. Open an implementation-start packet with `scripts/implementation_authorization.py begin`.
3. Validate all proposed mutation targets before writing.
4. Run the governed dispatcher writer for each non-baseline harness:
   - `gt bridge dispatch config set-weights B --quality 90 --cost 60 --availability 90 --json`
   - `gt bridge dispatch config set-weights C --quality 90 --cost 60 --availability 90 --json`
   - `gt bridge dispatch config set-weights D --quality 90 --cost 60 --availability 90 --json`
   - `gt bridge dispatch config set-weights E --quality 90 --cost 60 --availability 90 --json`
   - `gt bridge dispatch config set-weights F --quality 90 --cost 60 --availability 90 --json`
5. Run the governed harness registry writer for reviewer precedence:
   - `gt harness set-precedence --harness B --precedence 20 --reason "WI-5033 flatten dispatch ranking values to Codex baseline"`
   - `gt harness set-precedence --harness C --precedence 20 --reason "WI-5033 flatten dispatch ranking values to Codex baseline"`
   - `gt harness set-precedence --harness D --precedence 20 --reason "WI-5033 flatten dispatch ranking values to Codex baseline"`
   - `gt harness set-precedence --harness E --precedence 20 --reason "WI-5033 flatten dispatch ranking values to Codex baseline"`
   - `gt harness set-precedence --harness F --precedence 20 --reason "WI-5033 flatten dispatch ranking values to Codex baseline"`
6. Verify via dispatcher status and harness registry CLI reads.
7. File a post-implementation report as the next bridge version.

## Explicit Non-Scope

- No role assignment changes.
- No harness lifecycle status changes.
- No `can_receive_dispatch` or `can_fire_events` changes.
- No max-items cap changes.
- No model/provider/invocation-surface changes.
- No dispatcher daemon restart, topology activation, production deployment, credential lifecycle work, destructive cleanup, or sweep commit.

## Current-State Evidence

`gt bridge dispatch status --json` currently reports:

- `A`: quality 90, cost 60, availability 90, reviewer_precedence 20.
- `B`: quality 95, cost 60, availability 75, reviewer_precedence 10.
- `C`: quality 80, cost 30, availability 80, reviewer_precedence 30.
- `D`: quality 92, cost 25, availability 95, reviewer_precedence 10.
- `E`: quality 80, cost 20, availability 90, reviewer_precedence 15.
- `F`: quality 80, cost 20, availability 90, reviewer_precedence 20.

`gt bridge dispatch config set-weights B --quality 90 --cost 60 --availability 90 --dry-run --json` returned dry-run status and identified `harness-state/harness-registry.json` as the generated projection write surface. Source inspection of `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py` shows the real write path appends MemBase harness registry rows in `groundtruth.db`, regenerates `harness-state/harness-registry.json`, and appends `.gtkb-state/bridge-dispatch-config-transactions/audit.jsonl`.

## Specification-Derived Verification Plan

| Spec / governing surface | Required verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Latest bridge status is `GO` before implementation; claim and implementation-start packet are recorded; implementation report is filed as the next `NEW`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `scripts/implementation_authorization.py validate` succeeds for each target path under the WI-5033 PAUTH. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight passes with no missing required specs before filing and in the implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward with actual executed command results. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5033 --json` reflects the bridge thread and remains scoped to the active project/PAUTH. |
| `REQ-HARNESS-REGISTRY-001` / `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` / `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `gt bridge dispatch status --json` and `gt harness show --harness <id>` show fresh values after MemBase append and projection regeneration. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | Verification uses `gt harness` / `gt bridge dispatch status` CLI readers rather than direct JSON reads. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Dispatcher health/status remains `PASS`; no role, lifecycle, dispatchability, or topology fields change. |
| WI-5032 dependency | `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_wi5032_runtime_fallback_randomizes_equal_precedence_ties -q --tb=short` passes after values are flattened. |

## Acceptance Criteria

- Harnesses `A`, `B`, `C`, `D`, `E`, and `F` all report `dispatch_quality = 90`, `dispatch_cost = 60`, `dispatch_availability = 90`, and `reviewer_precedence = 20` through `gt bridge dispatch status --json`.
- Roles, lifecycle statuses, `can_receive_dispatch`, `can_fire_events`, max-items caps, invocation surfaces, model/provider config, and capability flags are unchanged except for harness-version provenance fields created by the governed writers.
- `gt bridge dispatch status --json` reports dispatcher health/status without new findings.
- The WI-5032 fully-tied uniform-random selector regression test remains passing.
- The implementation report contains exact command output summaries and a scoped diff/DB/projection mutation note.

## Risks / Rollback

Risk is medium because this deliberately flattens dispatcher ranking values and can change which headless harness is selected. The risk is bounded by WI-5032's VERIFIED uniform-random full-tie behavior and by explicit non-scope for dispatchability/status/role changes.

Rollback is to append new harness registry versions restoring the prior values for `B`, `C`, `D`, `E`, and `F` through the same governed CLI writers, regenerate the projection, and file a bridge report. Do not edit historical MemBase harness versions or bridge files.

## Files Expected To Change

- `groundtruth.db`
- `harness-state/harness-registry.json`
- `.gtkb-state/bridge-dispatch-config-transactions/audit.jsonl`

## Recommended Commit Type

`chore`
