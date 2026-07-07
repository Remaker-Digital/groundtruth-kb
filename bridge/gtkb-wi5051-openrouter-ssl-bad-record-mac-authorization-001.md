NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f38dc-dc71-7af2-a3ba-d3e17ae4f13b
author_model: gpt-5
author_model_version: codex-desktop-2026-07-06
author_model_configuration: codex-desktop; approval_policy=never; sandbox=danger-full-access

# Governance Advisory - WI-5051 OpenRouter SSL Dispatch Authorization

bridge_kind: governance_advisory
Document: gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization
Version: 001
Date: 2026-07-06 UTC

## Claim

`WI-5051` records an OpenRouter/F SSL failure but lacks active item-specific PAUTH. Because later evidence says SSL is now connecting, this proposal asks LO to choose repair, verification-only closure, or supersession rather than assuming implementation authority.

## Evidence

- `WI-5051` is open under `PROJECT-GTKB-RELIABILITY-FIXES` and cites dispatch `2026-07-06T17-51-05Z-prime-builder-F-630250` failing with `ssl.SSLError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC]`.
- `WI-5060` later reports SSL now connects, which may make WI-5051 a verification/closure item rather than a code repair.
- A targeted query of `project_authorizations` found no active row whose `included_work_item_ids` contains `WI-5051`.

## Requested Disposition

- Review whether WI-5051 needs implementation, verification-only closure, or retirement/supersession by WI-5060 evidence.
- If implementation remains needed, require fresh item-specific PAUTH, independent bridge GO, and implementation-start packet.
- Keep provider credentials, account settings, and unrelated F eligibility/config outside scope unless separately authorized.

## Candidate Target Paths

- `scripts/openrouter_harness.py`
- `scripts/verify_openrouter_dispatch.py`
- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_verify_openrouter_dispatch.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification linkage on proposals that may lead to implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/authorization linkage or a valid non-implementation exemption.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-gated implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded PAUTH before implementation.
- `GOV-ENV-LOCAL-AUTHORITY-001` - keeps credentials anchored to `.env.local` without disclosure.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - covers provider-backed dispatch execution.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - covers dispatcher health/status classification evidence.

## Prior Deliberations

- `DELIB-202665819` - WI-5048 OpenRouter/F activation review context.
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - nearby model/route truth context for provider-backed harnesses.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner requested this work in the current Prime Builder session, then directed Prime Builder to file proposals after the bridge/authorization blocker was surfaced.

## Verification Plan For Future Implementation

| Requirement | Verification |
| --- | --- |
| SSL classification | Focused tests must classify TLS/provider failures truthfully without false-green dispatch status. |
| Credential safety | Credential scans and stderr/stdout review must show no secret disclosure. |
| Closure path | If no code change is needed, record readiness/smoke evidence and reconcile through governed status change. |

## Rollback

This proposal changes no protected implementation files. Future rollback must revert only authorized source/test/config changes and preserve bridge, PAUTH, and audit records as append-only evidence.
