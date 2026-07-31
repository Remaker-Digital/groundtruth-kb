NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Implementation Proposal - Bound provider bridge-verdict denial loops and recover through the governed publisher

bridge_kind: prime_proposal
Document: gtkb-wi5216-provider-verdict-denial-loop-recovery
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5216

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Genuine OpenRouter F dispatch `2026-07-12T21-39-03Z-loyal-opposition-F-f6b9bc` received the WI-5211 governed publication prompt and tool schema, performed substantive investigation, but never invoked `PublishBridgeVerdict`. It exhausted all 600 turns after 611 tool calls: 551 Bash, 7 Write, 46 Read, 5 Grep, and 2 Glob. The repeated raw bridge-publication attempts varied syntactically, so the existing exact-call-signature no-progress guard did not fire. The run consumed 63,397,693 tokens, exited 1, tripped F's circuit breaker, and produced no verdict. The launch ledger reconciled exactly once and released the 29,700-second lease.

Add a narrow semantic recovery state for bridge-review and verification routes. When the existing raw guards identify a Write/Edit/Bash attempt to mutate a bridge verdict, preserve the denial unchanged, mark publication recovery pending, and temporarily expose only `PublishBridgeVerdict` on the next provider turn. The model still supplies the verdict and reviewed body; the canonical writer remains sole authority. Repeated refusal to use the governed publisher terminates through the existing bounded no-progress classification instead of consuming the full 600-turn budget.

## Claim

Prime Builder proposes a bounded `WI-5216` repair that keeps every raw mutation guard and generous runtime allowance intact while making the governed publisher the only available next action after demonstrated bridge-publication intent.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202666173` explicitly authorizes correction of every defect found during genuine six-harness proof, and WI-5216 plus its linked TEST-11370 define the observed failure and bounded acceptance boundary.

## In-Root Placement Evidence

All five target paths are under `E:\GT-KB`; no dispatcher configuration, routing, runtime JSON, lease, registry, credential, or release target is in scope.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - genuine assigned-role work must complete through governed execution evidence.
- `ADR-CROSS-HARNESS-PARITY-001` - F and D require equivalent bounded publication behavior.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - provider capability must be proven operationally, not inferred from schema presence.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - F receives the recovery in the shared cloud runtime.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - D receives equivalent standalone-loop behavior without weakening its guard floor.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - only the canonical publisher may append numbered LO verdicts.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - recovery must preserve dispatcher session and provider model provenance.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - 600/900/28800/29400/29700 allowances remain unchanged.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation boundary is linked before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must execute the mapped tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, work item, PAUTH, and target paths are declared.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the genuine F failure has a durable defect lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - dispatch evidence, work item, test, proposal, report, and verdict remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the live failure triggers correction rather than an informal retry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this is GT-KB platform harness work, not adopter application code.

## Prior Deliberations

- `DELIB-202666173` - complete six-harness governed proof and correct every discovered defect.
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - bounded predecessor publisher finalization authority.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - cross-harness parity implementation authority.
- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-002.md` - independent GO requiring fresh substantive F and D proof or a separately governed root-cause defect.

## Owner Decisions / Input

- `DELIB-202666173` supplies owner authority for this discovered-defect correction.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712` bounds the exact implementation and forbids dispatcher/routing changes, guard weakening, allowance reduction, direct runtime/lease edits, and unrelated mutation.

## Proposed Scope

- Detect semantic bridge-publication mutation intent only on LO bridge-review/verification routes and only when the existing Write/Edit/Bash bridge guards already deny the attempted mutation.
- Preserve the original denial result in model-visible history; do not auto-approve, auto-author, or auto-publish a verdict.
- On the next provider turn, narrow available schemas to `PublishBridgeVerdict` and add a concise recovery instruction. The provider still supplies slug, verdict, complete body, and any VERIFIED finalization arguments.
- Clear recovery state only after the governed publisher is invoked successfully. If the provider repeatedly refuses or emits prose, terminate after a small fixed recovery count through the existing `no_progress_loop` class, well before turn 600.
- Implement equivalent behavior in the shared cloud loop used by F and the standalone D loop. Keep non-bridge guard denials and ordinary investigative tool use unchanged.
- Do not alter model routes, dispatcher rules, harness eligibility, raw guards, publisher governance, or any runtime allowance.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused tests plus fresh genuine F and D dispatcher work prove bounded completion through the governed publisher. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Shared and standalone tests exercise the same recovery transitions and bounded refusal behavior. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Shared-base tests prove OpenRouter F inherits recovery without an adapter-specific second implementation. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | D tests prove equivalent detection, schema narrowing, recovery clearing, and raw guard preservation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Publisher mocks assert canonical delegation; tests prove no denied raw attempt is translated into a direct write or shell mutation. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Existing trusted-metadata tests remain green and recovered publication forwards the original session/model metadata. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Existing lifetime tests prove 600 turns, 900-second operations, 28,800-second sessions, 29,400-second workers, and 29,700-second leases are unchanged. |
| Verification and lifecycle carriers | Candidate/live applicability and clause preflights pass; exact focused suites, Ruff, writer, guard, atomicity, and dispatcher lifetime regressions pass. |

## Acceptance Criteria

- A denied raw bridge-verdict Write/Edit/Bash attempt remains denied and model-visible; no raw guard exemption is added.
- The immediately following provider payload exposes only `PublishBridgeVerdict` and includes a bounded recovery instruction.
- A valid publisher call delegates unchanged to the canonical writer with trusted metadata and clears recovery state.
- Repeated prose, unknown tools, or further refusal while recovery is pending exits through `no_progress_loop` after a small fixed count, not max-turn exhaustion.
- Non-bridge denied writes, ordinary Bash tests, reads, greps, and globs do not trigger publication recovery.
- All existing F/D focused, canonical writer, implementation-start, atomic VERIFIED, and dispatcher lifetime tests remain green.
- Fresh separately assigned genuine F and D work produces substantive canonical verdicts or exposes another separately governed defect; no impatience-based classification is accepted.
- An independent LO session returns VERIFIED and creates one focused commit containing only the approved five source/test paths plus this bridge chain and exact proof artifacts.

## Risks / Rollback

The main risk is falsely treating ordinary bridge inspection as publication intent. Detection is therefore limited to mutations already denied by canonical bridge guards and to LO publication skills. Rollback reverts the five source/test paths; append-only bridge and MemBase evidence remains historical.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`fix`
