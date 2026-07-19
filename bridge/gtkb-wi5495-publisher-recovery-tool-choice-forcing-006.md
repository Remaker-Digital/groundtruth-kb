REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c57a453e-dccb-4ca1-afb7-1d23dfa8444a
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Graceful recovery-exhaustion exit + Ollama claim-guard parity (revised scope)

bridge_kind: prime_proposal
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 006
Responds to: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-005.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The version-004 NO-GO correctly rejected version 001's D-side mechanism (Ollama's native `/api/chat` has no `tool_choice` field) and independently re-verified the F-side fix as correct, complete, and ready to file as-is. Version 005 (filed in an earlier session of this same conversation, still unreviewed) took the narrow split: F-only, target_paths limited to `cloud_harness_base.py` and its test, deferring D entirely. This revision (006) supersedes 005 with a broader, more complete fix, made necessary by new empirical evidence gathered after 005 was filed.

**New empirical evidence (this session, post -004):** direct live HTTP calls against Ollama's own OpenAI-compatible `/v1/chat/completions` endpoint (confirmed reachable for the `deepseek-v4-flash:cloud` route, `http://localhost:11434/v1/chat/completions`, HTTP 200) show that `tool_choice` forcing does **not** reliably constrain this model even where the protocol supports it:

- With both `PublishBridgeVerdict` and a decoy `Read` tool offered plus `tool_choice` forcing `PublishBridgeVerdict`: the model called `Read` anyway.
- With only `PublishBridgeVerdict` offered (matching the harness's actual recovery-mode schema restriction) plus the same forcing: the model returned blank/prose text (`finish_reason: "stop"`, no `tool_calls`) explaining it lacks a file-reading tool, rather than calling the one tool it was forced toward.

This means even a protocol-correct `tool_choice` fix (the F/OpenRouter half, already confirmed valid) cannot alone guarantee recovery success for this model. The primary fix in this revision is therefore a **graceful, observable exit on recovery exhaustion** — mirroring the harness's own existing `BridgeVerdictClaimStandDown` pattern for peer-claim collisions — rather than relying solely on forcing to prevent exhaustion from being reached at all.

**Second finding:** `scripts/ollama_harness.py` (D's separate, non-shared implementation) has no equivalent of `BridgeVerdictClaimStandDown` at all, and its `_dispatch_publish_bridge_verdict` never acquires a work-intent claim before calling the governed verdict publisher (unlike `cloud_harness_base.py`'s `_ensure_provider_verdict_claim` guard). Every error there — including an ordinary peer-claim race, not just recovery exhaustion — is wrapped into a flat `OllamaHarnessError` and crashes uncaught. This independently explains D's 100% historical dispatch-run failure rate (7/7 crashed, zero successes, verified via direct inspection of `.gtkb-state/bridge-poller/dispatch-runs/*loyal-opposition-D*.exit_code` this session) and is a genuine harness-parity gap, not just a missing forcing mechanism.

## Claim

Prime Builder proposes a bounded, revised implementation slice for `WI-5495`, superseding version 001's mechanism while preserving its independently-verified-correct F half, and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Response to Required Revisions (bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-004.md)

1. **Preserve the F/OpenRouter fix (-004 item 1):** the `DIALECT_OPENAI_CHAT` forced-function `tool_choice` branch in `cloud_harness_base.py`'s publisher-only-recovery block, and its test coverage in `test_cloud_harness_base.py`, are retained unchanged from the already-reviewed candidate. This revision adds to that diff; it does not touch or revert it.
2. **Replace the D/Ollama mechanism (-004 item 2, option a selected):** rather than switching D to the OpenAI-compatible endpoint (option b), this revision selects option (a): the native `/api/chat` contract genuinely has no working forcing mechanism for this model class (now empirically confirmed true even on the OpenAI-compatible endpoint too, which was not tested at -004 time), so the mitigation is the graceful-exhaustion exit plus the claim-guard parity fix described above, stated explicitly as the chosen mitigation rather than implied.
3. **Real request/endpoint tests (-004 item 3):** new/extended tests assert the actual exception classes raised and caught at each exhaustion checkpoint (not just a payload dict shape), and assert `ollama_harness.py`'s claim-acquisition call site exists and is exercised before publish.
4. **Split F from D (-004 item 4):** version 005 took this split (F-only, narrow target_paths). This revision (006) reunifies F and D under one proposal, because the graceful-exhaustion mechanism this revision adds is not D-specific -- it is the same top-level try/except restructuring in `cloud_harness_base.py` that F's own recovery-exhaustion checkpoints also need (F is not immune to the exhaustion case; forcing reduces but, per the new empirical evidence, does not eliminate it). Re-evaluated the split option and judged the combined diff low enough risk (four files, all additive exception-handling and one guard call) to keep as one reviewable unit; happy to split on reviewer request. Version 005 remains on record as the intermediate split attempt; this revision supersedes it rather than building on top of it, since 005's narrower scope would need the same try/except restructuring re-applied regardless.
5. **Fresh claim and packet (-004 item 5):** this revision is filed under a fresh `bridge_claim_cli.py claim` acquired this session; a fresh implementation-start authorization packet will be acquired after GO, before any protected-target mutation.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5495 remains a bounded reliability defect under the active standing project authorization (re-verified: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, `status=active`, covers `source`/`test_addition`). No new owner decision or specification is required for this technical correction.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail and numbered-file discipline for this revision.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the substantive basis for the required test additions (exception-class + catch-site assertions, not payload-shape mocks).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - this revision's D-side claim is grounded in fresh, direct empirical HTTP tests against the live endpoint, not proposal prose (the exact gap -004 found in version 001/002).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - target-path and project-linkage metadata carried forward.
- `GOV-RELIABILITY-FAST-LANE-001` - re-checked: origin=defect, no new public API/CLI/behavior beyond defect removal (the new exception classes are internal control flow, not a public surface), small/single-concern scope; eligibility holds.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain in-root.
- `GOV-STANDING-BACKLOG-001` - auto-linked.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked.

## Prior Deliberations

- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md` through `-004.md` - the full prior chain this revision responds to.
- `DELIB-202666257`, `DELIB-202666266`, `DELIB-202666227`, `DELIB-202666174`, `DELIB-202666256` - carried forward, independently re-confirmed present per the -004 review.

## Owner Decisions / Input

No new owner decision is requested. The owner's standing directive this session ("fix all issues and get the system working... 60 clean sequential dispatches... as proof") authorizes this technical correction within the existing WI-5495 reliability-fix scope; no destructive action, deployment, or formal-artifact mutation is implicated.

## Proposed Scope

- Add `BridgeVerdictRecoveryExhausted` (or equivalently named) exception in `scripts/cloud_harness_base.py`, raised at all four recovery-exhaustion checkpoints in `run_tool_loop` currently raising a bare `CloudHarnessError`, caught at the top-level try/except in the same position as the existing `BridgeVerdictClaimStandDown` clause (before the generic `CloudHarnessError` handler), returning a clean structured JSON payload (`status: recovery_exhausted`, `reason`, `attempts`, `last_failure`) via a normal `return` rather than propagating an uncaught exception.
- Add the equivalent exception class and top-level catch in `scripts/ollama_harness.py`'s agentic loop, at its corresponding recovery-exhaustion raise sites.
- Add a work-intent claim acquisition guard in `scripts/ollama_harness.py`'s `_dispatch_publish_bridge_verdict`, calling the same `bridge_work_intent_registry` claim/current_holder functions `cloud_harness_base.py` already uses via `_ensure_provider_verdict_claim`, before calling `publish_lo_verdict`; on a peer-held claim, raise the new stand-down-equivalent exception (caught cleanly at the top level) instead of proceeding to a raw publish attempt.
- Preserve the F/OpenRouter `DIALECT_OPENAI_CHAT` forced-function `tool_choice` fix unchanged.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability + clause preflights against this operative file; implementation report carries forward linked specs. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Preflight match on `Specification Links`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | New/extended unit tests directly invoke each exhaustion checkpoint with a mocked non-compliant model response, asserting the specific new exception type is raised and caught cleanly (structured return, no uncaught propagation) in both files; a separate test exercises the Ollama claim-guard call site (peer-held claim -> clean stand-down, not a raw publish attempt or crash). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | This revision's D-side claim is grounded in the direct empirical HTTP test transcript above, not proposal prose. |
| `GOV-RELIABILITY-FAST-LANE-001` | `KnowledgeDB.get_work_item("WI-5495")` re-check: origin=defect, small/single-concern scope. |

## Acceptance Criteria

- Unit tests assert the new recovery-exhaustion exception is raised at each of the four `cloud_harness_base.py` checkpoints and each corresponding `ollama_harness.py` checkpoint, and is caught cleanly at the top level (structured return, not an uncaught exception).
- Unit tests assert `ollama_harness.py` acquires a work-intent claim before publishing and stands down cleanly (not a crash) when the claim is peer-held.
- `ruff check` and `ruff format --check` pass on all four changed files.
- The F/OpenRouter `tool_choice` forcing fix and its existing test coverage remain unchanged and passing.

## Risks / Rollback

Risk is low-to-moderate: the change is additive exception-handling plus one new guard call, touching no existing control-flow paths for the success case (a worker that never enters recovery, or that successfully publishes, is unaffected). The claim-guard addition to `ollama_harness.py` changes D's behavior on a peer-claim collision from "crash" to "clean stand-down," which is strictly safer, not riskier.

Rollback is a revert of the four changed files. Bridge files and project authorization records are append-only audit artifacts and are not touched by rollback.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
