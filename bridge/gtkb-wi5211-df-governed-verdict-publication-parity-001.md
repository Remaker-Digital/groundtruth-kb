NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Implementation Proposal - Project governed LO verdict publication to D and F provider routes

bridge_kind: prime_proposal
Document: gtkb-wi5211-df-governed-verdict-publication-parity
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5211-DF-VERDICT-PARITY-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5211

target_paths: ["scripts/openrouter_harness.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Project WI-5210's governed PublishBridgeVerdict capability to OpenRouter F and Ollama D without weakening raw mutator guards. F receives only profile enablement and skill threading over the shared implementation; D receives a thin standalone adapter to the same canonical writer. Routing and generous allowances remain unchanged.

Work item description: WI-5210 repairs the live Alibaba H publication failure with a dedicated governed PublishBridgeVerdict route, but independent B review found the same controlled-artifact boundary is latent for OpenRouter F and Ollama D. F uses the shared cloud runtime but its prior committed verdicts predate the direct-write hard block; D has a separate provider runtime and is already DEGRADED. After WI-5210 is VERIFIED, project equivalent high-level verdict publication to F and D bridge-review/verification routes without weakening raw Write/Edit/Bash, preserve all 600-turn/900-second/28800-second/29400-second allowances, and prove each through fresh genuine dispatcher work.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5211` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/openrouter_harness.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_openrouter_harness.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - auto-linked governing or work-item specification.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666172` - Authorize WI-5199 plus H functional proof
- `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION` - Owner authorization to implement WI-4516 bridge Bash hardening
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - Owner decision: WI-5210 hunk-scoped finalization waiver
- `DELIB-20260712-WI5205-HUNK-SCOPED-FINALIZATION-WAIVER` - Owner decision: WI-5205 hunk-scoped finalization waiver
- `DELIB-20263410` - Lift WI-4510 cutover hold; authorize cutover readiness + proposal drafting

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5211-DF-VERDICT-PARITY-20260712` - active project authorization covering `WI-5211`.

## Proposed Scope

- Enable PublishBridgeVerdict in the OpenRouter profile, thread the selected bridge-review/verification skill through its shared tool loop, and update its LO prompt; do not alter shared cloud source.
- Add Ollama schema filtering, worker-role-document establishment, trusted publisher delegation, skill threading, and LO prompt parity while leaving raw Write/Edit/Bash guards unchanged.
- Grant neither provider a numbered path nor version; the canonical publisher remains sole authority for role, same-thread claim, transition, provenance, exclusive append, and VERIFIED atomic finalization.
- Run focused and unchanged guard/writer/atomicity/lifetime regressions, then route fresh genuine dispatcher-produced review work separately through F and D before the WI-5211 implementation report.
- Preserve 600 turns, 900-second operations, 28,800-second sessions, 29,400-second worker lifetimes, and 29,700-second document leases.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Adapter tests and fresh F/D dispatcher runs prove equivalent governed publication capability on both provider routes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run both focused adapter suites, unchanged writer/guard/atomicity/lifetime regressions, Ruff gates, and inspect both genuine run envelopes before requesting VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | No routing or config waiver substitutes for matching tool exposure, guard behavior, and genuine work evidence. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Publisher delegation tests assert trusted harness ID, session ID, model ID/version/configuration and reject conflicts or missing session evidence. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Each harness receives fresh real review work and must publish a substantive canonical verdict or expose a separately tracked defect. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | F reuses the shared cloud publisher implementation via profile enablement and explicit skill threading. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | D schema, filtering, document authority, delegation, prompts, and raw guard regressions match the shared contract. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Tests prove document-authoritative LO role establishment and preserved 600/900/28800/29400/29700 bounds. |

## Acceptance Criteria

- F exposes the governed tool only for bridge-review and verification and forwards the real skill/session/model metadata; non-LO skills and raw numbered bridge mutation remain denied.
- D implements the same high-level contract and fail-closed role/session/list validation while delegating governance to scripts.gtkb_bridge_writer; no path/version authority or raw guard exemption is added.
- Focused adapter tests plus unchanged canonical writer, implementation-start denial, VERIFIED atomicity, and dispatcher lifetime suites pass.
- Fresh separately assigned dispatcher work for both F and D produces substantive canonical verdicts or separately governed root-cause defects, with no impatience-based failure classification.
- Independent Loyal Opposition returns VERIFIED and one focused four-path source/test commit is created after the proof evidence is complete.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/openrouter_harness.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
