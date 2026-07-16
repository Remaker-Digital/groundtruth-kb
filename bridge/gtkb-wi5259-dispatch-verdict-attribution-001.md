NEW

# Defect-Fix Proposal - WI-5259 Dispatcher Verdict Attribution

bridge_kind: prime_proposal
Document: gtkb-wi5259-dispatch-verdict-attribution
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: Codex Desktop 2026-07-15
author_model_configuration: Interactive Codex Prime Builder; transcript override ::init gtkb pb; governed fleet stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5259-VERDICT-ATTRIBUTION-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5259

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Correct dispatcher completion attribution after genuine Alibaba H dispatch `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0`. H performed substantive Loyal Opposition work for 727 seconds across 18 turns and 30 tool calls, then exited 1 after an HTTP 400, emitted zero stdout, and authored no verdict. A distinct interactive Codex LO session concurrently authored the canonical GO for the same bridge document. The dispatcher found that post-launch GO by file version and modification time alone and incorrectly recorded the failed H launch as `succeeded` with `stop_reason=verdict_emitted` and post-verdict exit reconciliation.

The numbered bridge chain remains authoritative for the document's current status, so the external GO is legitimate bridge state. It is not evidence that H completed its dispatch. This repair separates those two facts. A selected verdict satisfies worker completion only when its trusted `author_session_context_id` equals the launch `dispatch_id` and its `author_harness_id` equals the launch recipient harness ID. Missing, unreadable, placeholder, or mismatched provenance fails closed for worker completion while the external bridge status and its actual attribution remain observable.

Implementation is limited to dispatcher reconciliation and focused tests. The target files currently contain unrelated parallel-session work, so no implementation claim or source edit may begin until those paths are clean or ownership is explicitly coordinated, in addition to the normal independent GO and implementation-start gates.

## Defect Evidence And Causal Boundary

- Dispatch ID: `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0`.
- Recipient: `loyal-opposition:H`.
- Worker result: exit code 1, 727,000 ms, 18 turns, 30 tool calls, zero stdout, Alibaba HTTP 400 stderr.
- External verdict: a GO authored by Codex A from a distinct interactive LO session for the same selected document while H was in flight.
- False telemetry: the H launch reported successful completion and `verdict_emitted` despite no H-authored verdict.
- `scripts/dispatcher_runtime.py::_find_dispatch_verdict` currently selects a canonical post-launch verdict using slug, version, status, timestamp, and mtime only.
- `_selected_document_verdicts` marks any selected GO/NO-GO/VERIFIED artifact complete without inspecting author provenance.
- `_process_pending_exit_codes_for_last_launch` then permits that uncorrelated artifact to set primary verdict fields, satisfy VERIFIED commit checks, reconcile a nonzero exit, advance document signatures, clear failures, and emit successful dispatch telemetry.

WI-5258 separately owns the H HTTP 400 transport and publisher compatibility repair. WI-5259 owns only the dispatcher attribution defect. The bridge artifact written by another LO session is not invalidated, rewritten, or deleted.

## Proposed Implementation

1. Parse trusted bridge author metadata from each canonical candidate verdict using the existing `scripts/bridge_author_metadata.py` parser rather than introducing a second ad hoc header grammar.
2. Derive the expected worker session from the launch `dispatch_id` and the expected worker harness from the harness suffix of the launch `recipient`. Require exact nonblank equality for both fields before the artifact is classified as a worker-correlated verdict.
3. Fail closed when `dispatch_id`, recipient harness, `author_session_context_id`, or `author_harness_id` is absent, malformed, placeholder-like, or mismatched. Current governed bridge artifacts require these provenance fields; legacy or synthetic artifacts without them cannot establish new dispatcher completion evidence.
4. Preserve the canonical artifact's path, status, latency, and parsed author fields as external bridge observation in each selected-document outcome. Record a deterministic attribution result and mismatch reason without setting worker `completed=true`.
5. Reserve existing worker-completion fields (`completed`, `verdict_path`, `verdict_status`, `verdict_latency_seconds`) for correlated verdicts. A mismatched external artifact must not populate the launch's primary worker verdict fields.
6. Permit post-verdict nonzero-exit reconciliation only when at least one selected document has a worker-correlated verdict and all required selected-document completion rules are otherwise satisfied. The H reproduction must remain a failed provider/subprocess launch.
7. Treat exit code 0 plus only missing or mismatched worker verdict evidence as failure, with a stable actionable provenance failure reason rather than `verdict_emitted` or success.
8. Advance per-document signatures, batch completion, VERIFIED atomic-commit validation, verified commit SHA fields, and success telemetry only from worker-correlated verdicts. An external VERIFIED artifact may remain visible as canonical bridge state but cannot be credited to the dispatched worker or trigger its commit-finalization check.
9. Preserve per-document semantics for multi-document batches: correlated documents may complete independently; mismatched or missing worker provenance remains incomplete for that launch and cannot be silently absorbed by another session's artifact.
10. Preserve bridge status authority, queue parsing, dispatch selection, retries, leases, circuit-breaker policy, native hooks, role assignment, routing, and the full 600-turn, 900-second operation, 3,600-second model/session, 29,400-second worker, and 29,700-second lease allowances.

## Explicit Exclusions

- No bridge artifact rewrite, deletion, invalidation, or alternate status authority.
- No direct contact with H or any other harness; no direct provider invocation.
- No dispatcher config, runtime JSON, telemetry history, lease, lock, eligibility, role, model, routing, or allowance mutation.
- No retrospective rewrite of the false H telemetry envelope; the original evidence remains auditable.
- No H HTTP 400 or publisher repair, which remains WI-5258 scope.
- No source changes outside the two declared target paths.
- No staging, commit, push, deployment, release, destructive cleanup, or unrelated worktree mutation by this proposal.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - per-dispatch telemetry must truthfully correlate outcome and completion evidence to the launched shim worker.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch audit and completion belong to the selected recipient and launch, not merely to concurrent bridge advancement.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - harness functional proof must be target-authored, dispatcher-produced, and auditable.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered files remain bridge status authority while TAFE/dispatcher remains runtime coordination authority.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - governed verdict artifacts carry the harness and session provenance needed for attribution.
- `GOV-SESSION-ROLE-AUTHORITY-001` - dispatched session evidence is explicit and cannot be borrowed from another session context.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before protected implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires provenance-derived regressions before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to its PAUTH, project, WI, and exact targets.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires live authorization checks at claim and implementation start.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace independent GO, claim, implementation-start authorization, report, or verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the observed H false-success defect as a durable correction chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links dispatch evidence, WI/test, PAUTH, proposal, implementation, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the observed regression to advance through the governed lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and evidence inside the GT-KB platform root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to file through the governed non-bypass helper.
- `GOV-STANDING-BACKLOG-001` - keeps fleet proof unresolved until corrected telemetry and fresh target-authored proof exist.

## Prior Deliberations

- `DELIB-202666173` - owner directive to verify A/B/C/D/F/H with genuine governed dispatcher work and correct every discovered defect.
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md` - independently VERIFIED predecessor establishing per-document batch completion and signature behavior.
- `bridge/gtkb-wi5221-prime-preclaim-worker-provenance-004.md` - independently VERIFIED predecessor establishing dispatcher-owned worker provenance as completion evidence.
- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-001.md` - adjacent H transport repair that explicitly leaves cross-session dispatcher attribution to WI-5259.

The proposal uses the live H incident and established dispatch/provenance decisions; unrelated generic recovery candidates are intentionally excluded.

## Owner Decisions / Input

`DELIB-202666173` authorizes correction of every defect discovered during the active six-harness proof program. Mike has also directed that manual interactive PB and LO bridge processing continues even while automated bridge health is degraded. This proposal does not reconfigure the fleet or disturb those sessions.

## Requirement Sufficiency

Existing requirements are sufficient. The telemetry, dispatch, document-provenance, session-authority, and onboarding contracts already require attributable worker evidence. The defect is missing enforcement in dispatcher reconciliation, not a missing product requirement.

## Spec-Derived Verification Plan

| Requirement | Deterministic verification |
| --- | --- |
| Exact worker correlation | Create a post-launch GO with `author_session_context_id` equal to the dispatch ID and `author_harness_id` equal to the recipient; assert normal completion and nonzero post-verdict reconciliation still work. |
| H incident regression | Create exit code 1 for an H launch and a concurrent GO authored by harness A from another session; assert launch failure, no `exit_reconciled_after_verdict`, no worker `verdict_path`, no `verdict_emitted`, no signature advancement, and separately attributed external GO evidence. |
| Exit-zero fail closed | Create exit code 0 with only a mismatched external GO; assert an actionable worker-verdict provenance failure rather than success. |
| Missing/invalid metadata | Exercise absent, blank, placeholder, malformed, and partially matching author metadata; none may satisfy worker completion. |
| Harness mismatch | Match the dispatch ID but use another harness ID; assert failure and a deterministic harness-mismatch reason. |
| Session mismatch | Match the recipient harness but use another session ID; assert failure and a deterministic session-mismatch reason. |
| Multi-document isolation | Provide a batch with one worker-correlated verdict and one externally authored verdict; assert only the correlated document completes or advances its signature and the launch remains incomplete. |
| VERIFIED finalization | Assert atomic-commit lookup and verified SHA fields run only for a worker-correlated VERIFIED artifact; external VERIFIED remains observation only. |
| Legacy positive fixtures | Update existing post-verdict reconciliation fixtures to carry matching governed author metadata; ensure valid WI-4933/WI-4977/WI-5207 behavior stays green. |
| Static quality | `ruff check` and `ruff format --check` pass on the two declared paths; `git diff --check` passes. |
| Governance | Applicability and clause preflights pass; implementation starts only after independent GO, a matching claim/start packet, and confirmation that the target files are no longer owned by parallel work. |

After focused implementation, testing, report, independent verification, and commit, fresh substantive dispatcher work must still demonstrate the repaired target harness. Correct telemetry is necessary evidence plumbing, not a substitute for functional fleet proof.

## Risk / Rollback

The primary compatibility risk is that older test fixtures and historical bridge artifacts lack complete author metadata. The new rule applies when deriving current worker completion and intentionally fails closed; tests must update valid synthetic verdicts with matching metadata. The bridge chain itself remains readable and authoritative. If the focused change causes incorrect current dispatch behavior, revert the focused commit through a separately governed change; do not weaken attribution to timestamp-only matching.

## Bridge Filing

This proposal is filed as the first status-bearing numbered file for `gtkb-wi5259-dispatch-verdict-attribution`. It does not overwrite or consume any other thread. Dispatcher/TAFE state and the append-only numbered bridge chain remain the live workflow surfaces.

## Recommended Commit Type

`fix` - prevents false dispatcher success and preserves accurate worker provenance.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
