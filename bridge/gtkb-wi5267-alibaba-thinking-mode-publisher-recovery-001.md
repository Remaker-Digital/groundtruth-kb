NEW

# Defect-Fix Proposal - Alibaba H Thinking-Mode Publisher Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5267-alibaba-thinking-mode-publisher-recovery
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; resumed governed fleet goal

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5267-ALIBABA-THINKING-TOOL-CHOICE-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5267

target_paths: ["scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

## Claim

Alibaba H reached publisher-only recovery after completing a substantive governed review, but the shared Anthropic recovery code forced `tool_choice` to an object form that Alibaba deepseek-v4-pro rejects in thinking mode. Add an explicit provider-profile capability for forced Anthropic publisher selection. Retain the current forced `{"type":"any"}` default for compatible Anthropic profiles, disable that field for Alibaba H, and continue exposing only the `PublishBridgeVerdict` schema during recovery. Existing response validation and bounded retries remain the authority preventing prose or non-publisher output from completing governed work.

## Defect / Reproduction

- Genuine dispatch: `2026-07-15T16-28-16Z-loyal-opposition-H-0dd621`.
- Selected document: `gtkb-wi5255-bc-telemetry-worker-provenance` at `-005 REVISED`.
- Substantive activity: 28 turns, 60 allowlisted read-only tools, 92,334 input tokens, 24,305 output tokens, and exact H worker/session provenance.
- Terminal result: exit code 1, `stop_reason=provider_error`, no H-authored verdict.
- Bounded provider diagnostic: HTTP 400 `InvalidParameter`; Alibaba reported that `tool_choice` cannot be required or object-valued in thinking mode.
- Immediate source: `scripts/cloud_harness_base.py` unconditionally adds `payload["tool_choice"] = {"type": "any"}` for Anthropic publisher-only recovery.
- WI-5258's sanitized HTTP diagnostic behavior worked correctly and must be preserved. Its object forcing strategy is the newly observed incompatibility.

## In-Root Placement Evidence

All four source/test targets and all bridge evidence are inside `E:\GT-KB`. The proposal does not depend on external files, direct provider contact, retained-runtime mutation, or harness-local scratch authority.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - H must complete governed work or fail with actionable attributed evidence.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - the shared cloud loop owns provider-profile variation while preserving common guards.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - H must use its documented provider-compatible Anthropic route and governed verdict publisher.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - only a successful governed publisher call may append the verdict artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before protected edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires provider-specific and shared-loop regressions before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds the proposal to PAUTH, project, WI, and exact targets.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - constrains implementation to the four declared source/test paths.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace GO, claim, implementation start, or independent verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the fresh dispatch failure as a durable repair chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links observation, WI/test, PAUTH, proposal, implementation, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires this regression to advance through the governed lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps implementation and evidence within the platform root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to use the governed helper path and self-enforce gates.
- `GOV-STANDING-BACKLOG-001` - H viability remains unresolved until independently verified and reproved.

## Prior Deliberations

- `DELIB-202666173` - owner directive to prove A/B/C/D/F/H with genuine governed dispatcher work and correct every discovered defect.
- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-001.md` through `-006.md` - predecessor diagnostic repair and object `tool_choice` decision based on the then-available provider contract.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-001.md` through `-004.md` - predecessor publisher-only recovery and malformed-call guard.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-001.md` through `-005.md` - governed completion contract requiring a successful publisher result.
- `TEST-11422` - linked regression requiring a thinking-compatible payload without weakening completion governance.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of defects discovered during the active governed fleet proof.
- The owner directed: "You must fix Alibaba and make it work."
- The owner separately authorized one temporary H dispatch, which was completed fail-closed and H was restored to `can_receive_dispatch=false` before this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The linked cloud-template, Alibaba-adoption, harness-onboarding, bridge-authority, and verification contracts already require a provider-compatible request while forbidding false or alternate verdict completion. WI-5267 changes only the implementation strategy for satisfying those requirements; no new or revised requirement is needed before implementation.

## Proposed Scope

1. Add one explicit, validated `AdopterProfile` capability controlling whether Anthropic publisher-only recovery forces an object `tool_choice`.
2. Preserve the compatible default so other profiles do not change silently.
3. Configure Alibaba H to omit forced `tool_choice` in publisher-only recovery while still sending exactly one tool schema: `PublishBridgeVerdict`.
4. Preserve bounded recovery: prose-only, blank, malformed, or non-publisher output does not complete bridge work and either retries within the existing cap or fails with a classified diagnostic.
5. Update shared and H-specific tests to prove the default and Alibaba branches, successful publication, non-publisher rejection, sanitized HTTP diagnostics, and unchanged allowance behavior.

Explicit non-scope:

- No direct Alibaba/provider/harness invocation outside a future owner-authorized TAFE dispatch.
- No alternate verdict writer, automatic verdict synthesis, or acceptance of prose as governed completion.
- No dispatcher runtime JSON, lease, lock, eligibility, role, route, model, allowance, credential, deployment, push, release, or unrelated worktree mutation.
- No change to WI-5255 or other shared-file candidates.

## Specification-Derived Verification Plan

| Requirement | Deterministic evidence |
| --- | --- |
| Provider-compatible Alibaba request | H-specific recovery tests assert only `PublishBridgeVerdict` is exposed and `tool_choice` is absent on every publisher-only recovery request. |
| Shared-template compatibility | Base/profile tests assert compatible Anthropic profiles retain forced `{"type":"any"}` behavior and invalid capability values fail closed if the representation is not boolean. |
| Governed completion | Existing and updated tool-loop tests prove prose, malformed, and non-publisher outputs remain incomplete; exactly one valid publisher result permits completion. |
| Diagnostic preservation | WI-5258 HTTP 400 sanitization tests remain green and continue to retain only status/code/message/request-id fields. |
| Allowance preservation | H routing/runtime tests retain 600 turns, 900-second operation timeout, full 60-minute model allowance, and the existing worker envelope. |
| Full target regression | Run complete cloud-base and Alibaba harness suites plus Ruff lint and format checks on the four targets. |

## Acceptance Criteria

- [ ] Alibaba publisher-only recovery sends no object or required `tool_choice` in thinking mode.
- [ ] Every Alibaba recovery request exposes only the governed publisher schema.
- [ ] A valid publisher call advances exactly one canonical bridge verdict.
- [ ] Prose, blank, malformed, or non-publisher output cannot create false completion and remains bounded.
- [ ] Compatible Anthropic profiles retain their current forced-selection default.
- [ ] Sanitized HTTP diagnostics and all generous allowances remain unchanged.
- [ ] All four authorized target suites/lint/format checks pass.
- [ ] Independent Loyal Opposition verification precedes any focused commit.

## Risks / Rollback

The principal risk is that omitting forced selection permits another prose-only response. The existing publisher-only prompt, one-tool schema, response parser, and bounded retry contract mitigate that without sending a provider-rejected field. Tests must prove those guards remain active. Rollback is a focused revert of the profile capability, Alibaba setting, and associated tests; the WI/test/bridge evidence remains append-only.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`

## Recommended Commit Type

`fix`
