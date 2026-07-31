NEW

# Defect-Fix Proposal - Do not create worker session envelopes for non-spawn dispatcher decisions

bridge_kind: prime_proposal
Document: gtkb-wi5314-nonspawn-session-envelope-suppression
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder A; transcript role ::init gtkb pb


Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5314

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Stop the live dispatcher from creating false open Prime worker session
envelopes on decisions that never spawn. Reorder only the Prime dispatch hot
path so work-intent acquisition succeeds before dispatcher-composed worker
authority is issued, preserving all existing foreign hunks and all Loyal
Opposition document-lease behavior.

## Requirement Sufficiency

Existing requirements are sufficient. Work-tree hygiene, centralized dispatch,
session-role authority, role resolution, and modernization non-impairment
already require this behavior; no new formal requirement is needed.

## Defect / Reproduction

At 2026-07-15T22:37:35Z the health surface reported Prime recipient A with
`last_result=work_intent_acquire_failed`, no live in-flight worker, and no
selected Prime work. Nevertheless `harness-state/codex/session-envelopes/`
received a new open dispatcher-composed Prime envelope about every 32-34
seconds. Source inspection shows `_ensure_dispatch_worker_session(...)` runs at
the dispatch hot path before `_acquire_prime_work_intent_batch(...)`; the
subsequent failure branch returns without closing or removing the authority
document. Repeating the daemon decision therefore creates perpetual untracked
dirt and false live-session evidence.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - prohibits a healthy idle service from generating perpetual repository dirt.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires append-only role-correct proposal, report, and verdict artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the defect, test contract, and independent verdict durably.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete applicability and clause preflights.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent rerun of focused dispatcher tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5314 to the Tree Stabilization PAUTH.
- `SPEC-AUQ-POLICY-ENGINE-001` - preserves owner authority and does not let runtime evidence mint approval.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps tests in disposable in-root synthetic repositories.
- `GOV-STANDING-BACKLOG-001` - WI-5314 is the durable owner for this defect.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires the non-bypass Codex proposal writer.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - binds code, regression, report, and verdict as one lifecycle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - moves the defect only through explicit proposal, report, and verification states.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs selection, claim, worker-authority, and spawn ordering.
- `GOV-SESSION-ROLE-AUTHORITY-001` - a worker session envelope is authority evidence and must represent a real worker session.
- `DCL-SESSION-ROLE-RESOLUTION-001` - dispatcher-composed role evidence must bind the exact selected dispatch and worker.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires preservation of foreign hunks and objective before/after evidence.

## Prior Deliberations

- `DELIB-20266201` - Owner authorization: WI-4855 daemon process-lifecycle hardening
- `DELIB-20260658` - Envelope containment: dispatch tier is OPTIONAL (refines DELIB-20260637 #1)
- `DELIB-202666274` - owner authorizes required modernization blocker repairs while retaining bridge and mechanical gates.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project-scope authority covers WI-5314; operation-time enforcement remains mandatory.
- `DELIB-202666274` - modernization blocker implementation is authorized; no runtime dispatcher/config or Git mechanical operation is requested here.

## Proposed Scope

1. Treat the current pre-start bytes as foreign concurrent work and fail closed
   unless hashes remain `DC67E8ADA02A5CB20243FDF6634222139D23083049AC5FCDA7FCE51428BFB28C`
   for `scripts/dispatcher_runtime.py` and
   `44AF13322CDD9BF3AFC24D5F57CDE65B6BB4933918097A8C542C628BB3A576D0`
   for `platform_tests/scripts/test_dispatcher_runtime.py`.
2. In the Prime non-dry-run path, allocate the session id, acquire the complete
   selected work-intent batch, and only then issue the dispatcher-composed
   worker session envelope. If envelope issuance fails after acquisition,
   release the acquired intents before returning.
3. Preserve Loyal Opposition document-lease ordering, selection, scoring,
   eligibility, caps, dispatch ids, telemetry, and successful worker authority.
4. Add focused regression hunks proving failed acquisition writes no envelope
   and successful acquisition/launch writes exactly one correlated envelope.
5. Do not alter or finalize any pre-existing foreign hunk. Whole-file staging
   or commit is forbidden; any later finalization must use the independently
   verified WI-5314 hunk patch only.
6. Keep the bridge lifecycle append-only by filing only the next numbered
   bridge files and never deleting or rewriting prior versions.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5314; TEST-11457; 2026-07-15 dispatcher health and filesystem observation",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "dispatcher run_dispatch_cycle Prime work-intent path",
  "before_behavior": "A non-spawn Prime decision writes a new open worker session envelope before work-intent acquisition and leaves it behind when acquisition fails.",
  "after_behavior": "A Prime worker session envelope is issued only after the complete work-intent batch is acquired; failed acquisition creates no authority document.",
  "self_descriptive_naming": "The existing work-intent acquisition, worker-session issuance, and spawn helpers continue to name each lifecycle boundary directly.",
  "obsolete_guidance_disposition": "No guidance or public route changes; only incorrect hot-path ordering is repaired.",
  "history_preservation": "Foreign pre-start hunks are preserved byte-for-byte outside the exact WI-5314 patch, and the bridge chain remains append-only.",
  "baseline": {
    "observed_interval_seconds": "32-34",
    "spawned": false,
    "last_result": "work_intent_acquire_failed",
    "new_open_envelope_per_cycle": 1
  },
  "expected_result": {
    "new_envelopes_on_failed_acquisition": 0,
    "new_envelopes_on_successful_launch": 1,
    "foreign_hunks_preserved": true,
    "runtime_configuration_changes": 0
  },
  "rollback": {
    "instructions": "Reverse only the exact WI-5314 ordering and regression-test hunks; never restore either whole file.",
    "test": "Reapply the baseline hashes to a synthetic fixture and rerun the focused acquisition-failure and successful-launch tests."
  },
  "hard_invariants": [
    "No dispatcher-composed worker authority exists for a decision that fails before launch authority is secured.",
    "A successful dispatch retains one exact role envelope correlated to its dispatch and session ids.",
    "All acquired work intents are released if later worker-session issuance or launch fails.",
    "Loyal Opposition document-lease behavior and all foreign pre-start hunks remain unchanged.",
    "No live dispatcher config, daemon runtime, bridge state, harness state, Git history, credential, deployment, or release mutation occurs during implementation."
  ],
  "fail_closed_conditions": [
    "Either pre-start file hash differs before edit.",
    "The new patch overlaps or removes a foreign pre-start hunk.",
    "Any failed-acquisition cycle creates a worker session envelope.",
    "Any successful launch loses or duplicates its correlated worker envelope.",
    "Focused or existing dispatcher regressions fail."
  ],
  "essential_context_preservation": "The repair preserves selected target, dispatch id, session id, role source, work-intent records, telemetry context, document leases, and append-only review evidence."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-WORK-TREE-HYGIENE-001` | Repeat failed-acquisition cycles and prove the worker-envelope file set and hashes stay unchanged. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Verify acquisition, authority issuance, spawn, and cleanup ordering for success and failure. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Prove only a genuine dispatch receives one dispatcher-composed role envelope. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Assert exact target, role, dispatch id, and session id in the successful envelope. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns the focused additions and relevant existing dispatcher tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm role-correct append-only artifacts and distinct PB/LO session contexts. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Resolve WI-5314 and the active Tree Stabilization PAUTH before claim/start. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and clause preflights with zero blocking gaps. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare pre/post foreign-hunk hashes and isolate the exact new patch. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run all mutation checks in synthetic in-root test repositories only. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Confirm runtime outcomes do not mint owner approval. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Link defect, regression, report, and verdict evidence to WI-5314. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-5314 remains the single owner for this defect. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Confirm proposal filing uses the non-bypass Codex writer. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Preserve executable and review evidence as linked artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm explicit NEW, report, and VERIFIED transitions only. |

## Acceptance Criteria

1. A Prime cycle whose work-intent acquisition fails creates zero new worker
   session envelopes across repeated runs.
2. A successful Prime acquisition and launch creates exactly one envelope with
   the exact selected harness, role, dispatch id, and worker session id.
3. Worker-session issuance failure releases every acquired work intent and
   creates no launch.
4. Existing Loyal Opposition document-lease and successful-dispatch tests pass.
5. The implementation report proves the exact WI-5314 patch preserves every
   foreign pre-start hunk and performs no whole-file Git operation.
6. No daemon restart or dispatcher, TAFE, bridge, or harness configuration change,
   `groundtruth.db` mutation, Git stage/commit/push, deploy, or release occurs.

## Risks / Rollback

The main risk is losing a work intent if authority issuance fails after the
reordering, or accidentally absorbing the current foreign WI-5255 and related
hunks. The implementation must release acquired intents on that failure and
record a precise before/new/after hunk separation. Rollback is only the exact
WI-5314 patch; restoring either whole file is prohibited.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix`
