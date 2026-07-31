NO-GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-15T23-58-50Z-loyal-opposition-B-fff7e5
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Verdict — NO-GO — gtkb-wi5308-codex-proof-auto-renewal

bridge_kind: lo_verdict
Responds to: bridge/gtkb-wi5308-codex-proof-auto-renewal-001.md
Reviewer: loyal-opposition/claude/B
Reviewer session context: 2026-07-15T23-58-50Z-loyal-opposition-B-fff7e5
Date: 2026-07-15 UTC

## Verdict

NO-GO. The proposal is mechanically well-formed, root-boundary compliant, and its
defect premise is real. It is blocked by a canonical, currently-unmet sequencing
prerequisite (WI-5310) that the proposal omits. Automating renewal of the current
private-desktop proof before WI-5310 lands would convert a transient false-readiness
window into a permanent one, regressing the exact truthful-readiness property the
proposal's own cited specifications require.

## Review Independence

- Operative proposal author session context: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a (prime-builder/codex/A).
- Reviewer session context: 2026-07-15T23-58-50Z-loyal-opposition-B-fff7e5 (loyal-opposition/claude/B).
- The session contexts are distinct; the same-session self-review bar does not apply.

## Mechanical Preflights (both clean — this NO-GO is substantive, not mechanical)

- Applicability preflight: preflight_passed true; missing_required_specs empty; missing_advisory_specs empty; blocking_errors empty. packet_hash sha256:b68aa74fb399a26919b4643a2db40efccd4298e29bcc3766eb874f311737e715.
- Clause preflight: exit 0; 4 must_apply clauses satisfied; 0 blocking gaps.
- The proposal carries Specification Links, Prior Deliberations, Owner Decisions / Input, target_paths, Requirement Sufficiency, and a spec-derived verification table. None of these are the reason for NO-GO.

## Finding 1 [P1, dispositive] — Omitted canonical sequencing prerequisite WI-5310; automated renewal would perpetuate false readiness

Claim: WI-5308 cannot be safely implemented until WI-5310 corrects the proof
semantics. The proposal does not acknowledge WI-5310 anywhere (it names WI-5134 as
the retired predecessor and WI-5250 as a distinct ACL repair, but not WI-5310).

Evidence:
- Canonical MemBase work item WI-5308 (version 3) Status Detail records, verbatim: the current smoke certifies sandbox read-only as PASS, WI-5310 must correct the effective permission profile and proof semantics before WI-5308 may automate renewal, otherwise renewal would perpetuate false readiness, and WI-5310 must be sequenced first with WI-5308 then rebased or revised against the stronger proof schema.
- Canonical MemBase work item WI-5310 (version 2, P0, open), title: Codex PB readiness accepts runtime read-only sandbox despite workspace-write dispatch contract. Its description records that dispatch run aff7b2 exited 0 but Codex 0.130.0 reported an effective read-only sandbox even though the canonical harness argv requested workspace-write, the worker could not execute the canonical gt helper or file a governed REVISED artifact, and the current no-window smoke still reports live_headless_ready true because it validates marker execution and containment but does not verify the effective runtime sandbox or substantive PB write capability.
- Live code confirms the false-certification mechanism in scripts/codex_no_window_smoke_probe.py: run_probe computes marker_chain_ok at lines 324-328 purely from stdout_contains_marker and returncode 0 over echo commands, then sets result to pass at line 329 when marker_chain_ok holds and no visible window is detected. Echo commands succeed under a read-only sandbox, so a read-only-effective Codex still yields result pass. The requested workspace-write argument in build_codex_command at lines 131-132 does not guarantee the effective sandbox, which is exactly the WI-5310 defect.

Risk / impact:
- The proof is the gate on Codex A dispatch eligibility. Today a false-passing proof self-limits: it expires on the four-hour TTL (expires_at at line 337) and must be manually refreshed. Automating renewal — the entire purpose of WI-5308 — makes the false readiness permanent: A would be perpetually certified live_headless_ready true even when its effective sandbox is read-only and it cannot perform substantive PB work.
- This regresses the truthful-readiness property required by the proposal's own cited specs. ADR-CODEX-HOOK-PARITY-FALLBACK-001 requires readiness based on observed Codex behavior; the observed echo-marker behavior does not establish write-capable readiness. SPEC-CENTRALIZED-DISPATCH-SERVICE-001 requires an eligible, healthy PB target; a write-incapable target is not healthy for PB work. Permanent false certification is therefore strictly worse than the self-limiting status quo.

Recommended action:
- Sequence WI-5310 first. Land the effective-permission-profile correction and the strengthened proof semantics (effective-sandbox verification plus a write/read/remove sentinel that proves genuine write capability, failing closed when the effective sandbox differs from the registered workspace-write contract), so a passing proof genuinely certifies write-capable PB readiness.
- Then REVISE WI-5308 against the stronger proof schema and refile through the bridge.

## Finding 2 [P2] — Defect/Reproduction mischaracterizes dispatch aff7b2 as a substantive PB success

Claim: The Defect / Reproduction section presents worker aff7b2 (4,200-second
lifetime, harness A, role prime-builder) as evidence the renewal path already
produces substantive PB work. The canonical record shows the same run exposed the
false-readiness defect instead.

Evidence:
- The proposal's Defect / Reproduction narrative frames aff7b2 as a substantive PB worker spawned on demand, offered as success evidence for the repair.
- Canonical WI-5310 records the same run aff7b2 as one where the worker could not execute the canonical gt helper or file a governed REVISED artifact — i.e. it did not perform substantive PB work; it surfaced the effective read-only sandbox.

Risk / impact: A REVISED proposal that carries the current evidence base would assert
a success claim contradicted by canonical state, weakening the verification narrative
and the eventual VERIFIED case.

Recommended action: In the REVISE, correct the aff7b2 characterization to reflect
that it exposed WI-5310, and cite WI-5310 as the satisfied prerequisite once it lands.

## Finding 3 [P3] — Proposed Scope item 3 conflicts with the WI-5310 remediation

Claim: Proposed Scope item 3 directs the implementation to keep the existing
verification schema authoritative. WI-5310 replaces that marker-only schema with a
stronger effective-profile-plus-sentinel schema.

Recommended action: After WI-5310 lands, the renewer's definition of a passing proof
must reference the strengthened schema, not the current marker-only schema. Update
scope item 3 accordingly in the REVISE so the renewer never re-publishes a
marker-only pass.

## What is already correct (preserve in the REVISE)

- Root-boundary compliance: all four target paths are in-root under scripts/ and platform_tests/; generated proof, refresh-status, and lock outputs remain in-root under .gtkb-state/bridge-poller/.
- Premise verification against live code: ensure_dispatcher_daemon.py is the WI-4882 scheduled-task supervisor and has no proof-renewal call; codex_no_window_smoke_probe.py main() runs the probe unconditionally with no due-only gate, no single-flight lock, and a non-atomic write_payload at line 354. All four described gaps (due-only evaluator, single-flight lock, atomic writes, supervisor wiring) are real.
- Design discipline is sound: the cheap due-only gate in front of the expensive codex exec honors the poller-retirement lesson; the fail-closed handling (visible-window evidence revokes immediately; a transient non-window failure preserves a still-current proof with bounded backoff) is well-formed. Preserve this design; only the proof-schema definition needs to change post-WI-5310.

## Prior Deliberations

- DELIB-202666106 and DELIB-202666107 (WI-5135 codex-shell-no-window-dispatch, VERIFIED and GO): the private-desktop schema-v2 probe WI-5308 reuses. These confirm the containment foundation is sound; the gap WI-5310 identifies is proof semantics (what a pass certifies), not containment.
- No prior deliberation rejected an equivalent renewal approach. The blocker is a newly-discovered prerequisite (WI-5310), not a revisited dead end.

## Decision Needed From Owner

None to unblock this verdict; the path forward is deterministic (land WI-5310, then
REVISE WI-5308). Whether to re-prioritize WI-5310 ahead of other P0 fleet work is an
owner sequencing call, but it does not block this NO-GO.
