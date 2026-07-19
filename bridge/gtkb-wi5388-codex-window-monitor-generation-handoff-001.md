NEW

# WI-5388 - Roll forward the Codex window monitor without termination

bridge_kind: prime_proposal
Document: gtkb-wi5388-codex-window-monitor-generation-handoff
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5388

target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]

implementation_scope: versioned singleton generation handoff only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make the independently reviewed WI-5368 matcher take effect without stopping
or impairing the currently running WI-5298 monitor. The active process began on
2026-07-15 and retains the old exact `add -u` matcher in memory. The scheduled
launcher starts the script repeatedly, but every new instance exits because the
active process owns the v1 named mutex. A source-only matcher edit therefore
cannot repair the live window storm until a host restart.

After WI-5368 is VERIFIED and mechanically finalized, change only the monitor's
singleton generation from v1 to v2 and update its exact static test. The next
ordinary scheduled launch then starts one v2 process alongside the still-live
v1 process. Both remain hide-only observers and exit only through their natural
host lifecycle. Repeated launches remain idempotent behind the v2 mutex. After
the next natural host restart, only v2 returns.

This proposal is hard-sequenced after WI-5368 and may not implement against the
old matcher. It performs no process termination, suspension, priority change,
Git interception, dispatcher change, or harness eligibility change.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - runtime rollout must preserve
  every harness's operation and dispatchability.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Windows fallback must be explicit,
  testable, and effective in the live Codex environment.
- `ADR-CROSS-HARNESS-PARITY-001` - the Codex-specific monitor must not alter
  other harnesses or shared routing.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - singleton and provenance behavior
  require deterministic enforcement.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization does
  not waive GO, claim, start, verification, or Git-operation gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live authority
  is rechecked before the protected effect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing
  requirements are explicitly linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI,
  and exact targets are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification includes
  static generation and live coexistence evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5388 durably owns the rollout omission.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - runtime finding, work item,
  proposal, implementation, report, verdict, and finalization remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5368 completion is an explicit
  predecessor and WI-5388 remains active through verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live deployment gap is fixed as
  governed work rather than hidden by source-only evidence.

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - background automation must not
  surface visible consoles.
- `DELIB-202666274` - supplies project-scoped modernization authority while
  preserving bridge and mechanical Git gates.
- Owner directive, 2026-07-16 - fix the console-window defect without making
  any harness less dispatchable; disabling a harness is unacceptable.
- WI-5298 - establishes the v1 hide-only monitor and forbids process or
  dispatch interference.
- WI-5368 - owns the full internal Git command matcher that must be present
  before this runtime handoff.

## Owner Decisions / Input

No new owner decision is required. The owner has explicitly required a
nonimpairing fix. Git staging, commit, push, deployment, release, cleanup,
credentials, dispatcher, TAFE, routing, harness role, and eligibility changes
remain excluded.

## Requirement Sufficiency

Existing requirements are sufficient. This is a rollout omission in an already
selected hide-only design, not a new behavioral policy.

## Proposed Scope

1. Fail closed unless the exact WI-5368 matcher is already present in the
   committed parent.
2. Change only the named mutex generation from v1 to v2.
3. Update the focused static assertion to require the v2 name and add a
   regression explaining why the generation change is intentional.
4. Permit the existing scheduler/launcher to start v2 naturally; do not stop,
   signal, replace, or otherwise manipulate v1.
5. Verify v1 and v2 coexist, subsequent v2 launches exit idempotently, and all
   qualifying commands finish naturally.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run the focused monitor test module after confirming the committed parent contains WI-5368. | The full command matcher remains green and the v2 singleton name is exact. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Start the monitor normally while v1 is live, then observe process and window state without stopping either process. | Exactly one v2 generation remains live, v1 continues naturally, qualifying windows are hidden, and unrelated windows remain untouched. |
| Idempotence | Allow at least two later scheduler launches and inspect the v2 population. | No second persistent v2 monitor appears; launcher attempts exit naturally behind the v2 mutex. |
| Scope and lifecycle | Inspect exact two-path diff and diff-check output; require independent implementation review. | Only generation-name and focused-test hunks exist; VERIFIED precedes finalization. |
| Harness continuity | Use the governed read-only health surface before and after live proof. | No role, eligibility, routing, or dispatchability value changes because of the handoff. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5388; live v1 process observation on 2026-07-16; WI-5368 predecessor","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; ADR-CODEX-HOOK-PARITY-FALLBACK-001","primary_route":"versioned named-mutex generation handoff through the existing scheduled launcher","before_behavior":"The active v1 process retains the old matcher indefinitely and rejects every newly launched source version behind its mutex.","after_behavior":"One v2 monitor starts naturally alongside v1, repeated v2 launches are idempotent, and only v2 returns after a natural host restart.","self_descriptive_naming":"GTKB-CodexSnapshotWindowHider-v2 identifies the operative generation explicitly.","obsolete_guidance_disposition":"The v1 name remains only as historical evidence; runtime and focused tests identify v2 as current after the handoff.","history_preservation":"WI-5298 v1, WI-5368 matcher repair, WI-5388 generation change, live coexistence evidence, and append-only verdict history remain distinct.","baseline":{"active_generation":"v1 started 2026-07-15","behavior":"exact add-u matcher remains loaded despite later source changes"},"expected_result":{"active_generations_before_restart":"one v1 and one v2 monitor","active_generations_after_natural_restart":"one v2 monitor","process_effect":"no termination, suspension, reprioritization, replacement, or dispatch mutation"},"rollback":{"instructions":"A rollback requires a governed successor generation; do not terminate either live process or reuse an occupied mutex name.","verification":"focused singleton tests plus live idempotence observation"},"hard_invariants":["WI-5368 committed predecessor","hide-only behavior","no process lifecycle action","no Git interception","no dispatcher, routing, role, or eligibility mutation","all harnesses remain dispatchable"],"fail_closed_conditions":["WI-5368 matcher absent","v1 is stopped or signaled","more than one persistent v2 process","arbitrary Git windows are affected","any harness or dispatch state changes","GO, claim, start, or independent verification is absent"],"essential_context_preservation":"Retain v1 provenance, WI-5368 matcher evidence, v2 singleton idempotence, natural-restart convergence, and full nonimpairment proof."}
```

## Acceptance Criteria

1. WI-5368 is the committed parent of the v2 generation change.
2. One v2 monitor starts while v1 continues naturally.
3. Repeated launches do not create more than one persistent v2 monitor.
4. The full WI-5368 command family is hidden without altering any command or
   unrelated window.
5. No process or harness is terminated, disabled, suspended, deprioritized, or
   made ineligible.
6. Independent VERIFIED precedes exact mechanical finalization.

## Risk / Rollback

The bounded risk is temporary duplicate hide calls for the old `add -u` shape.
Both monitors invoke only asynchronous `SW_HIDE`, so the duplicate is
idempotent and does not alter command execution. Reusing v1 would leave the fix
inactive; terminating v1 would violate the owner directive. Rollback therefore
uses a separately governed successor generation and natural lifecycle only.

## Bridge Filing

File through the governed Codex non-bypass helper. The numbered bridge file
chain is append-only. Deterministic TAFE routing remains external; this filing
does not contact or configure any harness.

## Recommended Commit Type

`fix` - activate the corrected hide-only monitor without process termination.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
