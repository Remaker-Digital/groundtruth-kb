NEW

# Defect-Fix Proposal - WI-5258 Alibaba H HTTP 400 Publisher Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5258-alibaba-http400-publisher-recovery
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: Codex Desktop 2026-07-15
author_model_configuration: Interactive Codex Prime Builder; transcript override ::init gtkb pb; governed fleet stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5258-H-HTTP400-RECOVERY-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5258

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the new Alibaba H publisher-recovery regression exposed by genuine Loyal Opposition dispatch `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0`. H performed substantive review work for 727 seconds across 18 model turns and 30 tool calls, then exited 1 with zero stdout and only the generic error `Alibaba Cloud Studio messages request failed (HTTP 400) after 1 attempt(s): HTTP Error 400: Bad Request`. H authored no bridge verdict.

Two implementation gaps block diagnosis and current H viability. First, the shared HTTP transport discards the `HTTPError` response body, including the provider code, message, and request id needed to distinguish request-shape, model-capability, and transient provider faults. Second, WI-5245 added a named Anthropic `tool_choice` only for publisher recovery. That field is the only request-shape delta immediately preceding the new HTTP 400. Alibaba's current Anthropic-compatible Messages documentation supports both forced named-tool and forced-any selectors for `deepseek-v4-pro`; with publisher recovery already exposing exactly one tool schema, forced-any is semantically equivalent while avoiding a provider-sensitive repeated tool name in the selector.

The repair will retain only bounded allowlisted provider diagnostics and will use `{"type":"any"}` for Anthropic publisher-only recovery while the tools array contains only `PublishBridgeVerdict`. Governed completion will still require a successful publisher result containing a nonblank `verdict_path`. No raw body, prompt, credential, unrelated provider field, direct provider call, alternate bridge writer, or dispatcher bypass is introduced.

## Defect Evidence And Causal Boundary

- Dispatch: `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0`.
- Bridge document: `gtkb-modernization-wi5163-shadow-evaluation`.
- Runtime evidence: 18 turns, 30 tools, 727,000 ms, exit code 1, zero stdout, 135-byte generic HTTP 400 stderr.
- H authored no numbered verdict; the concurrent Codex GO is separately tracked by WI-5259 and cannot count as H output.
- `scripts/cloud_harness_base.py::_post_json_with_bounded_retry` catches `urllib.error.HTTPError` but never reads or sanitizes `exc.read()` before raising a generic `CloudHarnessError`.
- The WI-5245 commit introduced `payload["tool_choice"] = {"type":"tool","name":"PublishBridgeVerdict"}` only when Anthropic publisher-only recovery is active. Earlier H turns and ordinary tool calls succeeded; the new failure appeared on the recovery request.
- Official Alibaba documentation says the Anthropic Messages route supports `deepseek-v4-pro`, tool calling, `{"type":"any"}`, and `{"type":"tool","name":"tool_name"}`. The generic Model Studio error catalog also documents HTTP 400 tool-choice/request-body errors and relies on the detailed provider message for correction.

This proposal corrects the bounded diagnostic and publisher-recovery request shape. WI-5259 separately owns dispatcher cross-session verdict attribution. It does not change H eligibility or dispatch H directly; a fresh governed H proof follows independent verification and commit.

## Proposed Implementation

1. Add a transport-local helper that reads at most a small fixed byte limit from an `HTTPError` body and never retains or emits the unrestricted body.
2. Parse JSON only when possible. Extract and whitespace-normalize only allowlisted scalar fields: provider `code`, `message`, and `request_id`, accepting the common top-level shape and a bounded nested `error` object. Bound every emitted field and the aggregate diagnostic.
3. Ignore authorization data, prompts, request payloads, stack traces, arbitrary nested fields, and non-JSON body text. If no allowlisted field is present, preserve the existing generic HTTP status error.
4. Include the sanitized diagnostic in terminal HTTP errors, including the existing HTTP 429 path where available, without changing retryability, attempt count, backoff, timeout, or wall-clock behavior.
5. For Anthropic publisher-only recovery, expose exactly one schema (`PublishBridgeVerdict`) and set `tool_choice` to `{"type":"any"}`. Because there is exactly one available tool, the provider is still forced to select the governed publisher; final prose, blank output, malformed calls, and missing `verdict_path` remain bounded failures under WI-5224/WI-5245 behavior.
6. Preserve OpenAI-chat payloads, non-recovery Anthropic payloads, native hooks, trusted author/session/model provenance, and the full 600-turn, 900-second operation, 3,600-second model/session, 29,400-second worker, and 29,700-second lease allowances.

## Explicit Exclusions

- No direct Alibaba/provider/harness call outside TAFE/bridge dispatch.
- No dispatcher config, runtime JSON, lease, lock, routing, role, eligibility, model, allowance, or credential mutation.
- No alternate or automatic verdict authoring; H must still invoke `PublishBridgeVerdict` with a valid governed payload.
- No source changes outside the three declared target paths.
- No WI-5259 telemetry-attribution repair in this commit.
- No staging, commit, push, deployment, release, destructive cleanup, or external-system mutation by Prime Builder.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - H must complete governed dispatcher work or fail with actionable attributed evidence.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - the shared cloud transport and Anthropic tool loop are the authoritative implementation surfaces.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - H must satisfy the governed cloud-harness capability floor.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - only the governed publisher may append H verdict artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before source mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires deterministic transport and H-specific regressions before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to its PAUTH, project, work item, and exact paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires the declared source/test boundary at implementation start.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace independent GO, claim, start packet, or verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the fresh production-like H failure as a governed repair chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links the observation, WI/test, PAUTH, proposal, implementation, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires this fleet regression to advance through the governed lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and evidence inside the GT-KB platform root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to use the governed non-bypass bridge helper.
- `GOV-STANDING-BACKLOG-001` - keeps H viability unresolved until independently verified and reproved.

## Prior Deliberations

- `DELIB-202666173` - owner directive to prove A/B/C/D/F/H with genuine governed dispatcher work and correct every discovered defect.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-004.md` - independently VERIFIED predecessor that bounded malformed H publisher recovery; the named selector introduced there is the immediate request-shape delta under investigation.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-005.md` - independently VERIFIED predecessor requiring successful governed verdict publication before provider completion.

The scaffold's generic recovery candidates were pruned because they concern unrelated workflow-recovery and proposal-standard topics rather than H transport compatibility.

## Owner Decisions / Input

`DELIB-202666173` authorizes correction of every defect discovered during the active six-harness proof program. Mike also directed in this task, "You must fix Alibaba and make it work." The active WI-5258 PAUTH narrows that authority to the three declared source/test paths and explicitly forbids direct provider/harness contact and dispatcher mutation.

## Requirement Sufficiency

Existing requirements are sufficient. The onboarding, cloud-template, Alibaba-adoption, file-bridge authority, and spec-derived verification contracts already require truthful bounded failure evidence and governed publisher completion. The observed behavior is an implementation regression, not a missing requirement.

## Spec-Derived Verification Plan

| Requirement | Deterministic verification |
| --- | --- |
| Bounded provider diagnostic | Mock an HTTP 400 JSON body containing `code`, `message`, `request_id`, oversized text, and unrelated credential/prompt/body fields; assert only normalized bounded allowlisted fields appear. |
| No raw-body leakage | Mock non-JSON and JSON bodies containing sentinel secret/prompt fields; assert the raw body and ignored fields never appear in the raised error. |
| Retry preservation | Re-run transient HTTP retry, 429, timeout, and terminal HTTP suites; assert attempt/backoff classifications are unchanged apart from the bounded diagnostic suffix. |
| Provider-compatible forced publisher | In an Anthropic/H publisher-recovery fixture, assert the payload exposes only `PublishBridgeVerdict` and uses `tool_choice={"type":"any"}`; simulate a valid tool response and require nonblank `verdict_path` before completion. |
| Fail-closed recovery | Re-run malformed, mixed-tool, prose, blank, missing-path, and repeated-failure tests; none may complete or execute a non-publisher tool. |
| H inheritance | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short` passes. |
| Shared cloud behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q --tb=short` passes. |
| Static quality | `ruff check` and `ruff format --check` pass on the three declared paths. |
| Governance | Applicability/clause preflights pass; implementation begins only after independent GO plus matching claim/start authorization; a separate LO session verifies and finalizes the focused commit. |

After the focused commit, H remains disabled until one fresh, substantive, target-authored, dispatcher-produced LO verdict succeeds through canonical controls. That proof is fleet acceptance evidence, not a substitute for deterministic tests or independent verification.

## Risk / Rollback

Risk is limited to shared cloud HTTP diagnostics and Anthropic publisher-only recovery. Allowlisting and fixed bounds prevent error-body leakage; the single exposed tool preserves bridge authority. If the selector change regresses valid recovery, revert the one focused commit through a separately governed change and restore the prior named selector while retaining any independently safe diagnostic parsing only if authorized and verified.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5258-alibaba-http400-publisher-recovery`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects an H/cloud-provider regression without adding a new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
