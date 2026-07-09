NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f38dc-dc71-7af2-a3ba-d3e17ae4f13b
author_model: gpt-5
author_model_version: codex-desktop-2026-07-06
author_model_configuration: codex-desktop; approval_policy=never; sandbox=danger-full-access

# Governance Advisory - WI-5060 Shim Harness Max-Turn Exhaustion Authorization

bridge_kind: governance_advisory
Document: gtkb-wi5060-shim-max-turn-exhaustion-authorization
Version: 001
Date: 2026-07-06 UTC

## Claim

`WI-5060` is owner-requested and implementation-relevant, but targeted MemBase inspection found no active item-specific PAUTH. This is therefore an authorization/scoping proposal, not implementation authority.

## Evidence

- `WI-5060` is open under `PROJECT-GTKB-RELIABILITY-FIXES` and records OpenRouter/F `max-turn exhaustion before final assistant text` plus Ollama/D `failure_class=max_turn_exhaustion`.
- The defect appears shim-class rather than F-specific and blocks trustworthy F Prime Builder activation after SSL connectivity recovered.
- A targeted query of `project_authorizations` found no active row whose `included_work_item_ids` contains `WI-5060`.

## Requested Disposition

- Review whether WI-5060 should receive a bounded implementation authorization.
- If approved, require fresh item-specific PAUTH, independent bridge GO, and implementation-start packet before protected edits.
- Future implementation should investigate max-turn limits, repeated tool-loop termination, and dispatch task decomposition while preserving provider credentials and unrelated harness settings.

## Candidate Target Paths

- `scripts/openrouter_harness.py`
- `scripts/ollama_harness.py`
- `scripts/cross_harness_bridge_trigger.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_verify_openrouter_dispatch.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification linkage on proposals that may lead to implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/authorization linkage or a valid non-implementation exemption.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-gated implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded PAUTH before implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents this proposal from bypassing PAUTH.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - covers dispatcher-mediated harness execution.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - covers dispatcher status and control evidence.

## Prior Deliberations

- `DELIB-202665819` - WI-5048 OpenRouter/F activation review context.
- `DELIB-20265026` - Ollama provider fallback/backoff context.
- `DELIB-20266134` - dispatcher eligibility false-green control-plane ordering.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner requested this work in the current Prime Builder session, then directed Prime Builder to file proposals after the bridge/authorization blocker was surfaced.

## Verification Plan For Future Implementation

| Requirement | Verification |
| --- | --- |
| Shim dispatch finality | Focused unit/smoke coverage must show bounded tasks do not exhaust turns before final assistant text. |
| Status truth | Run dispatcher status/report checks and focused harness readiness tests with credentials redacted. |
| Scope control | Diff A/B/C/D/E/F role, eligibility, and model metadata invariants. |

## Rollback

This proposal changes no protected implementation files. Future rollback must revert only authorized source/test/config changes and preserve bridge, PAUTH, and audit records as append-only evidence.
