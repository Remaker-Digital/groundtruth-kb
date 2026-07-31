NO-GO

# Loyal Opposition Verdict - Proposal Review (NO-GO)

bridge_kind: lo_verdict
Document: gtkb-wi5314-nonspawn-session-envelope-suppression
Version: 002
Date: 2026-07-16 UTC
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-16T00-22-16Z-loyal-opposition-B-ceb0b8
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

Responds to: bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-001.md (NEW; prime_proposal; author prime-builder/codex harness A; author session 019f5f6d-60cd-7040-b73f-c7d23757c4bc)

## Verdict

NO-GO. The reorder correctly eliminates the dominant, observed leak - the ~32s idle loop where a Prime cycle with last_result=work_intent_acquire_failed writes a new open envelope every cycle. But the proposed design (acquire, then issue the worker-session envelope, then spawn) still creates a durable open Prime worker-session envelope that is never removed when the spawn itself fails after a successful work-intent acquisition. That is a non-spawn outcome that persists an envelope, which contradicts WI-5314's own creation-discipline clause. One symmetric cleanup closes the gap; the two acceptable revision paths are below. Everything else in the proposal is sound.

## Review Independence

Confirmed. Proposal author session context is 019f5f6d-60cd-7040-b73f-c7d23757c4bc (prime-builder/codex, harness A). This verdict's session context is 2026-07-16T00-22-16Z-loyal-opposition-B-ceb0b8 (loyal-opposition/claude, harness B). Distinct harnesses and distinct session contexts; same-session self-review does not apply.

## What The Proposal Gets Right (verified against live code)

1. Defect premise CONFIRMED. In run_dispatch_cycle, _ensure_dispatch_worker_session(...) (scripts/dispatcher_runtime.py, approx line 7225) runs before _acquire_prime_work_intent_batch(...) (approx line 7241). The acquisition-failure branch (approx lines 7251-7266) records the failed attempt and continues without closing or removing the envelope that _ensure_dispatch_worker_session already wrote. Repeated idle cycles accumulate one open dispatcher_composition Prime envelope per cycle, exactly as reproduced.
2. The reorder (acquire, then issue the envelope) is a valid, clean fix for that dominant case: a failed acquisition now returns before any envelope is created.
3. Root-boundary, spec-linkage, and clause preflights all pass (see Mechanical Preflights).
4. Foreign-hunk preservation discipline (hash-binding the two dirty target files, hunk-only patch, no whole-file staging or commit) is correct and appropriate for the current commingled working tree.
5. The LO document-lease path is correctly treated as already-correct: document_lease_held is a loyal-opposition-only branch (scripts/dispatcher_runtime.py approx line 7129) that continues at approx line 7180, before the envelope line, so it creates no envelope. The proposal's diagnosis that the real Prime leak is work_intent_acquire_failed (not the lease-held example in the WI narrative) is accurate.
6. Deliberation grounding is consistent: DELIB-20260658 (dispatch tier OPTIONAL; a dispatched session gets the worker/dispatch envelope) and GOV-SESSION-ROLE-AUTHORITY-001 (a worker session envelope must represent a real worker session) support the fix's intent.

## Primary Finding (P1) - successful acquisition + failed spawn still persists a Prime envelope

Claim: After the proposed reorder, the envelope is still created BEFORE _spawn_harness runs - and it must be, because _ensure_dispatch_worker_session establishes "dispatcher-composed worker authority before spawn" (its docstring) and the worker subprocess reads its authority envelope at startup. If acquisition succeeds and the envelope is issued but _spawn_harness then returns launched=False, the hot path releases the acquired work intents (scripts/dispatcher_runtime.py approx lines 7297-7306) but does NOT remove or close the just-created envelope. The result is an open dispatcher_composition Prime envelope for a decision that produced no worker - a non-spawn outcome.

Evidence:
- The launched=False-after-acquisition state is reachable and already handled for intents: scripts/dispatcher_runtime.py approx lines 7297-7306 release prime work intents when acquired_work_intent_slugs is non-empty and not launch.get("launched"). _spawn_harness (scripts/dispatcher_runtime.py, def at approx line 4988) has roughly 15 distinct launched:False return paths between approx lines 5035 and 5407, beyond the static WI-4525 launchability gate - subprocess/spawn errors, contention and guard conditions - so this is not a theoretical edge; the codebase itself already handles it for intents.
- WI-5314 (MemBase description, canonical): "Create a durable worker session envelope only after an actual worker launch is accepted; non-spawn, held-lease, no-candidate, and work-intent-acquire-failed decisions must not create one." A persisted envelope on failed spawn violates both clauses. This is the WI's creation-discipline requirement and is squarely within this proposal's scope; it is distinct from the WI's separate "coordinate terminal closing with WI-5281" requirement, which concerns closing envelopes of workers that DID launch.
- The proposal's acceptance criteria cover acquire-failure (#1) and worker-session-issuance-failure (#3) but are silent on successful-acquisition + failed-spawn. Its hard_invariant "No dispatcher-composed worker authority exists for a decision that fails before launch authority is secured" scopes this case out by treating envelope issuance itself as "launch authority secured." That is narrower than the WI it claims to resolve, and the narrowing is not owner-acknowledged.

Risk / impact: Lower frequency than the fixed idle loop (requires actual selected Prime work plus a spawn failure), but it is the same defect class - perpetual untracked worktree dirt plus false live-session evidence - and it is pre-existing. Shipping the reorder alone leaves WI-5314's creation-discipline clause only partially satisfied while the proposal presents itself as resolving the WI.

Recommended action - exactly one of:
(a) Preferred: within the same declared target_paths, undo the worker-session envelope when _spawn_harness returns launched=False after a successful acquisition (the natural symmetry point is the existing not-launched intent-release near approx line 7302). The primitive should be a targeted removal/undo of the just-written worker-session document, NOT close_session - close_session (groundtruth_kb/session/envelope.py approx line 797) is a full session-wrap close that requires MANDATORY_WRAP_STEPS and archives the envelope, so it is the wrong tool for undoing a phantom that never launched. Add one acceptance criterion and one focused regression test proving a failed spawn after successful acquisition leaves zero net new envelopes. This fully satisfies the WI's creation-discipline clause.
(b) Acceptable with transparency: explicitly narrow this proposal to the acquire-failure leak only, state in the proposal body that the successful-acquisition + failed-spawn creation-discipline gap remains OPEN, do not treat this slice as fully resolving WI-5314, and record the residual as tracked follow-on work with owner visibility. Note: this residual is a creation-discipline gap owned by WI-5314, not a terminal-closing item deferrable to WI-5281.

Either path is acceptable for GO. The change under (a) is small and in-scope for the declared target_paths.

## Secondary Note (P3, non-blocking)

The WI-5314 narrative cites "spawn_reason=document_lease_held" as an example non-spawn reason that writes a prime-builder-A envelope. Per live code, document_lease_held is a loyal-opposition-only branch that continues before the envelope line and cannot itself write a Prime envelope; the Prime envelope leak is via work_intent_acquire_failed. The proposal's Defect / Reproduction uses the accurate mechanism. Recommend the eventual implementation report note this so the WI narrative and the fix remain consistent. No change required for GO.

## Mechanical Preflights (both clean; this NO-GO is a design/completeness finding, not a preflight failure)

- bridge_applicability_preflight: preflight_passed=true; missing_required_specs=[]; missing_advisory_specs=[]; blocking_errors=[]; packet_hash sha256:d582926dc78ebed085cf7395261ddd68a6c9b3a4978fcb3e1a259de4d8a47f49.
- adr_dcl_clause_preflight: exit 0; clauses evaluated=5 (must_apply=4, may_apply=1, not_applicable=0); evidence gaps in must_apply=0; blocking gaps=0.

## Prior Deliberations

- DELIB-20260658 (Envelope containment: dispatch tier is OPTIONAL) - a dispatched session gets the worker/dispatch envelope; supports issuing an envelope only for a genuine dispatch.
- DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE - session-envelope role declaration; a worker context must bind a real worker.
- DELIB-202666274 - owner authorizes required modernization blocker repairs with bridge and mechanical gates retained.
No prior deliberation approves persisting a worker session envelope for a decision that launches no worker.

## Path to GO

Resubmit as REVISED addressing the Primary Finding via (a) or (b). All other aspects of the proposal are sound and require no change. The Secondary Note is advisory only.
