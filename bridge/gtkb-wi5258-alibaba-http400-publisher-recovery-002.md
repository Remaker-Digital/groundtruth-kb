GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f65fb-4219-7150-ac09-26f12b650337
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Loyal Opposition; transcript override ::init gtkb lo; reasoning xhigh

# Loyal Opposition Proposal Review - WI-5258 Alibaba H HTTP 400 Publisher Recovery

bridge_kind: lo_verdict
Document: gtkb-wi5258-alibaba-http400-publisher-recovery
Version: 002
Responds to: bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-001.md
Date: 2026-07-15 UTC

## Verdict

GO. The proposal addresses a genuine H failure with a bounded three-path repair. Capturing only allowlisted, bounded HTTP error fields is necessary for diagnosis, and switching Anthropic publisher-only recovery to `{"type":"any"}` is an officially supported, governance-equivalent selector while exactly one tool schema is exposed. The implementation must not claim that the named selector caused the observed HTTP 400 until a fresh governed H proof supplies provider evidence.

## First-Line Role Eligibility Check

- Current role: Loyal Opposition under owner transcript `::init gtkb lo`.
- Requested status: `GO`, authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session context: `019f65fb-4219-7150-ac09-26f12b650337`.
- Proposal author session context: `A-2026-07-15T05-27-23Z`.
- Both identifiers are present and distinct; this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:54e7cf2cf41997446eb836d16df5f4616661efacf5a29e60415df49ef6f56adf`
- content_file: `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-001.md`
- operative_file: `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

- Clauses evaluated: `5`.
- must_apply: `3`; may_apply: `2`.
- Must-apply evidence gaps: `0`.
- Blocking gaps: `0`; exit status: `0`.

## Review Findings

No blocking proposal defect was found.

### Provider compatibility finding

Alibaba's current official Anthropic-compatible Messages documentation lists `deepseek-v4-pro` as supported and documents both `{"type":"any"}` and `{"type":"tool","name":"tool_name"}` as valid tool-choice strategies. Its official error catalog confirms that HTTP 400 diagnostics can identify incorrect `tool_choice`, malformed request bodies, unsupported tool calls, input-length limits, and other parameter faults.

Therefore the observed generic HTTP 400 does not by itself establish that the named selector is invalid. That causal statement remains an inference from timing: ordinary H turns succeeded, WI-5245 introduced publisher-only narrowing plus the named selector, and the next genuine recovery request failed. GO is still appropriate because forced-any is documented, the recovery payload exposes only `PublishBridgeVerdict`, and final completion remains gated on a successful nonblank `verdict_path`.

Primary sources reviewed:

- `https://www.alibabacloud.com/help/en/model-studio/anthropic-api-messages`
- `https://www.alibabacloud.com/help/en/model-studio/deepseek-api`
- `https://www.alibabacloud.com/help/en/model-studio/error-code`

### Live implementation and scope finding

Current source confirms `_post_json_with_bounded_retry` discards the `HTTPError` body and emits only status plus the generic exception text. Current publisher-only Anthropic recovery exposes one schema and sets the named `PublishBridgeVerdict` selector. The three proposed targets are clean after the separately VERIFIED WI-5245 commit.

The active PAUTH is version 1, contains only WI-5258, allows only `source` and `test`, and forbids dispatcher mutation, credential lifecycle, destructive cleanup, external-system mutation, Git history rewrite, push, production deployment, and release. Its scope matches the proposal's exact three paths and direct-contact exclusions.

### Related-work finding

WI-5245 is a VERIFIED predecessor, not duplicate work: it bounded malformed publisher recovery and established the publisher-only path. WI-5258 adds transport diagnostics and provider request compatibility after a fresh HTTP 400. WI-5259 separately owns false cross-session verdict attribution in dispatcher telemetry and must not be absorbed here.

## Conditions For Implementation And Verification

1. Read only a fixed, small byte limit from each `HTTPError` body. Do not retain, log, prompt, or serialize the unrestricted body.
2. Parse JSON only; allowlist scalar `code`, `message`, and `request_id` from the documented top level or one bounded `error` object. Ignore arbitrary fields, arrays, nested objects, authorization data, request payloads, prompt text, and non-JSON content.
3. Normalize whitespace, apply conservative per-field and aggregate bounds, and preserve the existing generic status-only error when no safe allowlisted field exists.
4. Preserve retry classification, attempt counts, `Retry-After`, backoff, socket timeout, and wall-clock behavior. Reading diagnostics must not make a retryable response terminal or vice versa.
5. Apply `tool_choice={"type":"any"}` only to Anthropic publisher-only recovery and only when the active schema set is exactly `[PublishBridgeVerdict]`. OpenAI-chat, ordinary Anthropic turns, and all other tool sets remain unchanged.
6. Preserve completion only after the governed publisher returns a nonblank `verdict_path`; prose, blank output, malformed calls, mixed tools, missing paths, and repeated failures remain bounded failures.
7. Add negative leakage tests using secret, prompt, unrelated-field, non-JSON, oversized, and nested-object sentinels. The raised terminal diagnostic must contain none of the ignored values.
8. The implementation report may state that forced-any is a supported compatibility adjustment, but must label the named-selector cause as unproven until fresh H evidence identifies it.
9. H remains non-dispatchable after deterministic VERIFIED. A fresh substantive, target-authored H verdict through canonical dispatch is required before eligibility restoration.
10. Do not absorb WI-5259, alter dispatcher state, contact H directly, or mutate any path outside the three approved targets.

## Prior Deliberations

- `DELIB-202666173` - owner directive to prove A/B/C/D/F/H and correct every discovered defect.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-004.md` - VERIFIED publisher-recovery predecessor.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-005.md` - VERIFIED fail-closed completion predecessor.
- `WI-5259` - separate dispatcher provenance/attribution defect.
- Live deliberation search found no contrary owner decision or competing approved implementation path.

## Baseline And Backlog Evidence

- WI-5258 is open, P1, under `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`.
- Its record explicitly requires provider-response evidence rather than treating the generic HTTP 400 as proof of a named-selector defect.
- The current focused baseline passes: `106 passed, 1 warning in 1.30s`.
- All three target paths are clean, so the eventual finalizer can evaluate an exact WI-5258-only commit candidate.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5258-alibaba-http400-publisher-recovery`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5258-alibaba-http400-publisher-recovery`
- `gt projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5258-H-HTTP400-RECOVERY-20260715 --json`
- `gt backlog show WI-5258 --json`
- `gt backlog show WI-5259 --json`
- `git status --short -- scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- Source inspection of `_post_json_with_bounded_retry` and Anthropic publisher-only recovery in `scripts/cloud_harness_base.py`.
- `python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short --basetemp .pytest-A-lo-wi5258-baseline`
- Official Alibaba Model Studio documentation review for Anthropic Messages, DeepSeek V4, and HTTP error codes.

## Opportunity Radar

The bounded structured-error helper is a useful shared deterministic service within the already-approved transport surface. Keep it transport-local and narrowly allowlisted; no broader abstraction is justified in this slice.

## Owner Action Required

None.

## Loyal Opposition Decision

GO. Prime Builder may implement the exact three-path repair after acquiring the matching work-intent claim and implementation-start authorization, subject to the conditions above.

Recommended commit type: `fix`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, proposal-review, lo-opportunity-radar

