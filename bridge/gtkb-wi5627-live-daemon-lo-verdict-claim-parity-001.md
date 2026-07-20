NEW
::init gtkb lo
::open build

# WI-5627: Apply LO verdict-claim lifecycle to the live dispatcher daemon path

bridge_kind: prime_proposal
Document: gtkb-wi5627-live-daemon-lo-verdict-claim-parity
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-19 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5627

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5400 correctly added pre-spawn Loyal Opposition verdict-claim acquisition
to `scripts/dispatcher_runtime.py::run_dispatch_cycle`, but the production
daemon uses a separate live-spawn loop in
`scripts/gtkb_dispatcher_daemon.py::_execute_live_spawns`. That loop creates
the LO worker session, then calls `_spawn_harness` without acquiring the
selected document batch's verdict claims or attaching the trusted claim
context. The live path therefore bypasses the verified WI-5400 protection.

Genuine dispatcher-produced OpenRouter F runs
`2026-07-19T03-27-05Z-loyal-opposition-F-64bb72`,
`2026-07-19T03-30-18Z-loyal-opposition-F-7cbd3e`, and
`2026-07-19T03-34-38Z-loyal-opposition-F-a16476` consumed 149,442, 264,687,
and 189,917 tokens respectively before governed publication detected a
peer-held claim and stood down neutrally. This proposal applies the existing
claim lifecycle to the actual daemon path before provider launch. It does not
alter dispatcher configuration, eligibility, routing, selection, allowances,
topology, leases outside the existing API, or any live worker.

Both target files contain substantial foreign dirty changes. Implementation
must begin from the current bytes after GO and use an exact WI-5627 patch.
Whole-file staging is prohibited; unrelated source/test bytes remain
quarantined and unadopted.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the central dispatcher must own the
  pre-launch authority lifecycle used by its production daemon path.
- `ADR-DISPATCHER-ARCHITECTURE-001` — preserves dispatcher-owned selection,
  worker-session authority, provider launch, and exit reconciliation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires independent GO, exact claim, and
  implementation-start authorization before either protected target changes.
- `GOV-RELIABILITY-FAST-LANE-001` — governs this bounded P0 reliability repair
  under the active project standing authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires the observed production
  defect, linked test, implementation evidence, and terminal verdict to remain
  durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserves the defect, linked test,
  proposal, implementation report, verdict, and commit as one traceable graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — keeps this successor defect explicit
  and append-only through candidate, approved, implemented, and verified states.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete
  governing requirements and spec-derived verification before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the exact
  project, PAUTH, work item, and target paths declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent
  verification of the mapped pre-spawn, suppression, and cleanup behaviors.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keeps all implementation and
  evidence in-root under `E:/GT-KB`.
- `GOV-HARNESS-ISOLATION-001` — forbids direct harness contact; the repair is
  confined to dispatcher control-plane behavior.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` established the bounded
  project-level standing authorization used here; normal bridge, claim,
  implementation-start, independent verification, and focused-commit gates
  remain intact.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` requires this proposal
  to depend only on canonical MemBase, Deliberation Archive, dispatcher, and
  numbered bridge evidence. No scratch or retired assessment surface is cited.
- The terminal `gtkb-wi5400-cloud-verdict-claim-lifecycle` numbered bridge
  chain is the direct implementation predecessor. WI-5627 does not reopen or
  rewrite it; it repairs the separately implemented production-daemon path
  that WI-5400's tests did not exercise.
- A bounded Deliberation Archive search for this exact live-daemon parity
  defect found no additional directly governing owner decision. The defect is
  newly observed production evidence, not a competing architecture decision.

## Owner Decisions / Input

No new owner decision is required. The owner-directed active fleet goal
requires every substantive dispatcher-produced harness defect to proceed
through a work item, linked test, PAUTH, bridge GO, implementation, testing,
independent verification, and focused commit. WI-5627 is an eligible bounded
reliability fix under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.

The owner's current dispatcher hold is preserved: no dispatcher configuration,
runtime-state, eligibility, routing, ranking, role, identity, lease-file,
allowance, process, or live-worker mutation is in scope.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and
`ADR-DISPATCHER-ARCHITECTURE-001` already require the dispatcher to own the
production launch and authority lifecycle. WI-5400's terminal implementation
establishes the intended pre-spawn verdict-claim behavior. WI-5627 is a live
path parity defect, not a requirement gap.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Add focused daemon tests around `_execute_live_spawns`: a free exact document batch must be claimed before the fake provider spawn observes control; a peer-held claim must produce a non-launched neutral result and zero provider calls. | Exact batch ownership precedes spawn; peer contention spends no provider budget. |
| `TEST-11672`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Cover partial claim failure, worker-authority failure, launch failure, and incomplete exit using the existing claim and exit-reconciliation APIs. | Only claims owned by the daemon worker session are released; document leases are released on pre-launch suppression; incomplete exits leave no owned claim behind. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run applicability and clause preflights, verify live GO/claim/start for both exact target paths, then require independent LO verification. | All gates pass with zero blocking gaps; no protected edit predates authority. |
| `GOV-RELIABILITY-FAST-LANE-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Produce an exact WI-5627 hunk patch, run reverse/applicability checks, compare it with the focused commit, and preserve each numbered lifecycle transition. | The patch contains only WI-5627 behavior and tests; all foreign dirty bytes remain uncommitted; the durable artifact graph reaches an independent terminal verdict. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-HARNESS-ISOLATION-001` | Inspect the exact diff and run the focused daemon module without provider/network access. | Only the two declared in-root paths change; no direct harness contact or external provider request is added. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
git diff --check -- scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

## Risk / Rollback

The primary risk is duplicating or mis-keying claims across the daemon and
exit-reconciliation paths. The implementation must reuse the existing
`dispatcher_runtime` claim helpers and the exact daemon worker session id; it
must not introduce another registry or direct database transaction. A second
risk is accidentally adopting the substantial foreign dirty bytes already in
both targets. Exact patch hashing, applicability checks, and hunk-only staging
are mandatory.

Rollback is one focused `fix:` commit containing only the WI-5627 patch and
this numbered bridge chain. Revert that commit under normal authority, then
rerun `TEST-11672`, the complete daemon test module, Ruff, compilation, and
whitespace checks. No dispatcher configuration rollback is required because
configuration is outside scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5627-live-daemon-lo-verdict-claim-parity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — this restores already specified and previously verified
verdict-claim behavior in the production daemon path; it adds no new public
capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
