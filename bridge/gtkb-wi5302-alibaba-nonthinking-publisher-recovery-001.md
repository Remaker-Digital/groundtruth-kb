NEW

# Defect-Fix Proposal - Alibaba Non-Thinking Forced Publisher Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5302-alibaba-nonthinking-publisher-recovery
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; governed bridge and harness black-box stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5302-ALIBABA-NONTHINKING-PUBLISHER-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5302

target_paths: ["scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

## Claim

WI-5267 made Alibaba thinking-mode recovery fail closed by omitting forced Anthropic `tool_choice`, but a fresh genuine H dispatch then exhausted all four publisher-only recovery attempts because the model emitted a non-publisher `Bash` call each time. Preserve Alibaba's ordinary substantive review request and thinking behavior, then make only the bounded publisher-recovery request non-thinking and forced to the sole exposed `PublishBridgeVerdict` schema. A valid nonblank canonical `verdict_path` remains the only governed completion signal.

## Defect / Reproduction

- Genuine dispatch: `2026-07-15T20-41-42Z-loyal-opposition-H-c3b8b4`.
- Selected document: `gtkb-modernization-rc-evidence-closure`.
- H completed substantive review work before entering publisher-only recovery.
- All four bounded recovery attempts returned a non-publisher `Bash` tool call even though the recovery payload exposed only the `PublishBridgeVerdict` schema.
- The publisher-only guard rejected each response and the worker exited 1 without a governed verdict. The fail-closed behavior was correct, but H remained nonfunctional for canonical completion.
- Current implementation sets Alibaba's `force_anthropic_publisher_tool_choice` profile capability to `false` because its earlier thinking-mode request rejected object-valued required tool choice.
- Alibaba's current Anthropic-compatible Messages contract supports `thinking: {"type": "disabled"}` and supports forced tool selection. This is corroborative provider-contract evidence only; deterministic in-root tests and fresh dispatcher proof remain authoritative for acceptance.

## In-Root Placement Evidence

All four implementation/test targets, the work item, linked test, authorization, bridge chain, and dispatcher evidence are inside `E:\GT-KB`. No external file, browser state, harness-local scratchpad, direct provider invocation, or retained runtime mutation is a live dependency.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - H must complete governed work through its declared tools or fail with actionable, target-attributed evidence.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - shared cloud-loop policy owns explicit provider-profile variation while preserving common completion and guard contracts.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - Alibaba H must use its provider-compatible Anthropic route and canonical verdict publisher.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - only successful `PublishBridgeVerdict` publication may append the verdict artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires full governing linkage before protected source/test edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires shared-loop and H-specific verification mapped to every linked requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to the active project authorization, project, WI, and exact targets.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - constrains implementation to the authorized four-file source/test envelope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace independent GO, claim, implementation-start, report, or verification gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the post-VERIFIED recurrence as a distinct durable defect chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links observation, WI/test, PAUTH, proposal, implementation, tests, verification, and commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the fresh regression to advance through the governed lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and evidence within the GT-KB root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to self-enforce the bridge and implementation gates.
- `GOV-STANDING-BACKLOG-001` - H viability remains open until deterministic repair and fresh target-authored proof both succeed.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded repair of fleet defects discovered during genuine dispatcher proof.
- `bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-001.md` through `-004.md` - predecessor fix that correctly removed the provider-rejected forced choice in thinking mode but did not establish live H completion.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-001.md` through `-004.md` - publisher-only recovery and malformed/non-publisher fail-closed guard.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-001.md` through `-005.md` - governed completion contract requiring a successful publisher result.
- `TEST-11448` - linked regression requiring non-thinking forced publisher recovery plus fresh H dispatcher publication.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this bounded defect-repair proposal and source/test lifecycle.
- The owner directed: "You must fix Alibaba and make it work."
- The owner requires all funded functional harnesses to be dispatchable by default unless a specific reason applies; this proposal does not mutate current eligibility while other workers are active.

## Requirement Sufficiency

Existing requirements are sufficient. The cloud-template, Alibaba-adoption, harness-onboarding, bridge-authority, and verification contracts already require provider-compatible governed completion and fail-closed handling. WI-5302 changes the bounded recovery strategy, not the governing outcome or authority model.

## Proposed Scope

1. Add one explicit, exact-boolean provider capability controlling whether Anthropic publisher-only recovery disables thinking. Preserve the default so unrelated adopter profiles retain their current payloads.
2. Configure Alibaba H to preserve its ordinary request unchanged, but set `thinking: {"type": "disabled"}` on publisher-only recovery requests.
3. Re-enable forced Anthropic publisher selection for Alibaba only in that non-thinking recovery branch while exposing exactly one schema, `PublishBridgeVerdict`. Prefer an explicit publisher tool selection if the shared dialect representation supports it without changing unrelated profiles; otherwise forced-any is acceptable because the active schema set contains exactly one governed tool.
4. Preserve atomic rejection of mixed or wrong-tool responses, successful-publisher result validation, required nonblank canonical `verdict_path`, bounded retry exhaustion, sanitized provider diagnostics, and session/author provenance.
5. Add focused shared-base and Alibaba tests proving ordinary payload stability, recovery-only thinking disablement, forced sole-tool selection, successful publication, false-completion rejection, and unchanged allowance behavior.
6. After deterministic VERIFIED and focused commit, require a fresh substantive H dispatcher review that target-authors a canonical verdict before H is counted viable.

Explicit non-scope:

- No direct Alibaba/provider/harness invocation outside canonical TAFE/bridge dispatch.
- No dispatcher runtime JSON, lease, lock, eligibility, ranking, route, role, model, allowance, credential, push, deployment, release, or unrelated worktree mutation.
- No alternate verdict writer, synthesized verdict, prose-as-completion behavior, or weakening of the publisher guard.
- No adoption of foreign or quarantined changes.

## Specification-Derived Verification Plan

| Requirement | Deterministic evidence |
| --- | --- |
| Ordinary review preservation | H-specific tests assert ordinary Alibaba payloads retain existing thinking/default behavior and do not receive recovery-only forcing fields. |
| Provider-compatible recovery | H-specific tests assert every publisher-only recovery payload sets `thinking` to disabled, exposes only `PublishBridgeVerdict`, and forces that sole tool through the supported Anthropic representation. |
| Shared-template stability | Base/profile tests assert the new capability is exact-boolean, defaults to no payload change, and leaves compatible non-Alibaba recovery behavior unchanged. |
| Governed completion | Existing and updated matrices prove prose, blank, malformed, mixed, wrong-tool, failed-publisher, and missing/blank `verdict_path` responses remain incomplete and bounded. |
| Provenance and diagnostics | Existing target/session attribution and sanitized provider-error tests remain green. |
| Allowance preservation | H routing/runtime tests retain 600 turns, 900-second operation timeout, full 3600-second model/session allowance, and the existing worker envelope. |
| Full target regression | Run complete cloud-base and Alibaba harness suites plus Ruff lint/format and exact four-path diff checks. |
| Real viability | A later canonical dispatcher run records substantive H work and an H-authored verdict with matching dispatch/session provenance. |

## Acceptance Criteria

- [ ] Ordinary Alibaba review payloads and thinking behavior remain unchanged.
- [ ] Every Alibaba publisher-only recovery request disables thinking, exposes only `PublishBridgeVerdict`, and forces that sole tool.
- [ ] A valid publisher call with a nonblank canonical `verdict_path` is the only successful completion path.
- [ ] Prose, blank, malformed, mixed, wrong-tool, failed-publisher, or blank-path output remains fail-closed and bounded.
- [ ] Unrelated adopter profiles retain their current payload behavior.
- [ ] Sanitized diagnostics, author/session provenance, and H's 600/900/3600 allowances remain unchanged.
- [ ] Full four-target pytest, Ruff lint/format, and diff checks pass.
- [ ] Independent Loyal Opposition verification precedes a focused commit.
- [ ] Fresh substantive target-authored H dispatcher publication succeeds before H is counted viable.

## Risks / Rollback

The main risk is provider drift in the interaction between thinking control and forced tool selection. The change is isolated to recovery requests for an explicitly opted-in profile, and deterministic tests must prove ordinary review payloads are untouched. Existing response validation prevents any provider anomaly from becoming false completion. Rollback is a focused revert of the new profile capability, Alibaba profile values, and associated tests; WI/test/bridge evidence remains append-only.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`

## Recommended Commit Type

`fix`
