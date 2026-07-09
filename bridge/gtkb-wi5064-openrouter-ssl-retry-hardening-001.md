NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

# Defect-Fix Proposal - OpenRouter/F recurrent SSL bad record MAC blocks LO-default headless dispatch

bridge_kind: prime_proposal
Document: gtkb-wi5064-openrouter-ssl-retry-hardening
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5064

target_paths: ["scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

## Claim

OpenRouter/F is now correctly configured as a Loyal Opposition dispatch target, but it still cannot reliably process LO-default headless bridge work because the OpenRouter shim lets TLS/provider transport failures escape as unhandled exceptions. The live recurrence invalidates the prior WI-5051 verification-only closure premise that the `SSLV3_ALERT_BAD_RECORD_MAC` failure was only transient.

Prime Builder requests GO for a narrow reliability fix: add bounded retry handling for selected TLS/provider transport exceptions in `scripts/openrouter_harness.py`, preserve truthful residual failure classification in `scripts/dispatcher_runtime.py` if retries are exhausted, and cover both behaviors with focused tests.

## Defect / Reproduction

- At `2026-07-07T20:12:08Z`, the dispatcher launched `2026-07-07T20-12-08Z-loyal-opposition-F-5c369d` for `loyal-opposition:F`.
- The launch was headless under the governed status wrapper and selected `bridge/gtkb-wi5059-advisory-intake-test-parity-003.md`.
- The worker exited `1` at `2026-07-07T20:14:38Z`.
- `stderr` showed an unhandled Python traceback ending in `ssl.SSLError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac`.
- `gt bridge dispatch health --json` then reported `loyal-opposition:F` failed, while Codex/A remained quarantined by `codex_dispatch_not_ready`.

This is the same failure family documented in WI-5051, but WI-5051 is already resolved through a closure-only report (`bridge/gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization-003.md`). Today demonstrates that OpenRouter/F needs code-level resilience before it can satisfy the active headless-processing goal.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/openrouter_harness.py`, `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_openrouter_harness.py`, and `platform_tests/scripts/test_dispatcher_runtime.py`.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, the reliability fast-lane standing authorization, and the active owner goal provide enough requirement basis for this bounded defect repair. No new functional requirement is needed before implementation can begin after LO GO.

## Prefiling Preflight Evidence

- Applicability preflight command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5064-openrouter-ssl-retry-hardening --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5064-openrouter-ssl-retry-hardening-001.md --json`
- Applicability result: `preflight_passed=true`, `missing_required_specs=[]`, `missing_advisory_specs=[]`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this source/test/config repair to be bridge-governed and approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires a live project authorization for source/test changes.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not replace LO GO or the implementation-start packet.
- `GOV-RELIABILITY-FAST-LANE-001` - authorizes small single-concern reliability defects under `PROJECT-GTKB-RELIABILITY-FIXES` by active membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the recurrence to be preserved as durable work item and bridge evidence rather than chat-only memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - supports creating WI-5064 and a follow-on proposal when a verified closure premise is contradicted by fresh evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps the defect, proposal, verification, and eventual report linked.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to map focused tests to the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH/project/work-item metadata above.
- `GOV-ENV-LOCAL-AUTHORITY-001` - forbids credential disclosure or credential lifecycle changes while testing provider connectivity.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs provider-backed dispatch workers and the requirement that they process work headlessly.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatcher health/status evidence and failure classification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant because Codex must self-enforce bridge gates when native hook coverage is incomplete.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms the target paths are GT-KB platform files, not external application files.
- `GOV-STANDING-BACKLOG-001` - covers WI-5064 as the active backlog record for the recurrence.

## Prior Deliberations

- `DELIB-202665819` - Loyal Opposition Review - WI-5048 Activate OpenRouter/F for dispatchable Prime Builder work (NO-GO).
- `DELIB-202665850` - Loyal Opposition Review - OpenRouter direct timeout retry (WI-5060).
- `DELIB-202665840` - Verdict for `gtkb-wi5060-harness-readiness-repair`.
- `DELIB-202665849` - Loyal Opposition Verdict: OpenRouter direct timeout retry (WI-5060).
- `DELIB-202665847` - Loyal Opposition Verdict: OpenRouter connection reset retry.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing reliability fast-lane authorization.

## Owner Decisions / Input

- Owner updated the active goal on 2026-07-07: OpenRouter must be LO-default, and Codex plus OpenRouter must be able to work headlessly.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and authorizes small reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES` by active work-item membership.
- No credential rotation, provider-account change, production deployment, force-push, or broad cleanup is requested or authorized by this proposal.

## Proposed Scope

IP-1: In `scripts/openrouter_harness.py`, classify selected provider transport exceptions as retryable in the existing bounded chat retry loop. At minimum, cover `ssl.SSLError` with `SSLV3_ALERT_BAD_RECORD_MAC` and compatible transient network wrappers that occur while reading an OpenRouter chat-completion response. Preserve the existing attempt cap, backoff budget, and session timeout enforcement.

IP-2: When retries are exhausted, fail with a concise `OpenRouterHarnessError` message that names the provider transport class without dumping credentials, request headers, or raw payloads.

IP-3: In `scripts/dispatcher_runtime.py`, ensure residual OpenRouter TLS/provider transport failures classify as provider failures rather than generic subprocess failures when stderr contains the hardened error text or legacy traceback text.

IP-4: Add focused tests in `platform_tests/scripts/test_openrouter_harness.py` and `platform_tests/scripts/test_dispatcher_runtime.py` for retry success, retry exhaustion, credential-safe error text, and dispatcher classification.

Out of scope: credential lifecycle, `.env.local` edits, OpenRouter account/provider settings, production deployment, re-enabling Codex dispatcher automation, re-enabling Ollama, or clearing the Codex no-window disable guard.

## Specification-Derived Verification Plan

| Spec / surface | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Unit-test `call_openrouter_chat` or the tool-loop boundary so a simulated TLS bad-record-MAC failure retries and can recover within the configured attempt cap. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Unit-test dispatcher failure classification for both hardened OpenRouter transport errors and the legacy `SSLV3_ALERT_BAD_RECORD_MAC` traceback text. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Inspect test fixtures and stderr assertions to confirm no credential values or request headers are emitted. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest targets for the changed files and report exact commands/results in the post-implementation report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before source edits, run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5064-openrouter-ssl-retry-hardening` after LO GO and cite the packet. |

Expected focused commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
```

## Acceptance Criteria

- OpenRouter/F no longer crashes with an unhandled `ssl.SSLError` for `SSLV3_ALERT_BAD_RECORD_MAC`.
- A transient first-attempt TLS/provider failure can recover through bounded retry and return a final assistant text in tests.
- An exhausted TLS/provider failure exits with concise credential-safe stderr and is classified as a provider failure.
- The post-implementation report includes focused tests and a controlled smoke plan for OpenRouter/F without relaunch loops.

## Risks / Rollback

Risk: retrying too broadly could mask non-transient provider defects. Mitigation: keep retry classes narrow, bounded, and observable in failure text.

Risk: more provider calls may consume OpenRouter quota during a real transient. Mitigation: reuse the existing small retry count and session timeout budget; no unbounded loops.

Rollback: revert only the changed source/test lines and restore the prior dispatcher classification set. No credential or provider-account rollback is in scope.

## Files Expected To Change

- `scripts/openrouter_harness.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix:`
