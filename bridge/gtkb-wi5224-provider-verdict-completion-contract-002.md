REVISED

# Revised Implementation Proposal - Require governed verdict publication before provider bridge completion

bridge_kind: prime_proposal
Document: gtkb-wi5224-provider-verdict-completion-contract
Version: 002
Author: Prime Builder Codex A
Date: 2026-07-14 UTC
Responds to: bridge/gtkb-wi5224-provider-verdict-completion-contract-001.md

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-14T09-06-37Z-prime-builder-A-wi5224-revised
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; governed fleet-proof continuation; A is PB-only

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5224-VERDICT-COMPLETION-CONTRACT-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5224

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Note

This revision preserves the implementation scope from version 001 and corrects only the proposal metadata/evidence trail needed for governed Loyal Opposition publication. Ollama D dispatch `2026-07-14T09-00-29Z-loyal-opposition-D-ac06b0` reviewed version 001 and wrote `bridge/gtkb-wi5224-provider-verdict-completion-contract-001-blocker.md` after the governed publisher refused to emit a GO/NO-GO verdict with `author_session_context_missing`. D reported that the proposal content was otherwise reviewable but the `author_session_context_id` value in version 001 was a Codex thread UUID.

Version 002 replaces that author session value with a concrete timestamp-style Prime Builder session context and keeps the same PAUTH, target paths, requirement sufficiency, and verification plan. It does not request any source edit before an independent GO.

## Summary

Genuine provider-backed Loyal Opposition dispatches are still able to finish or exit without a governed bridge verdict even when the selected task requires a numbered GO, NO-GO, or VERIFIED artifact. WI-5216 covers one denial-loop shape, but later evidence exposed broader completion gaps: F emitted prose containing pseudo tool-call JSON and exited zero without a verdict, H repeatedly invoked `PublishBridgeVerdict` until the full 60-minute model window without successful publication, D dispatch `2026-07-14T08-07-46Z-loyal-opposition-D-7ff282` exited after many publication attempts without appending the required verification verdict, F dispatch `2026-07-14T08-45-27Z-loyal-opposition-F-5fc7f9` exited zero without a verdict, and D dispatch `2026-07-14T09-00-29Z-loyal-opposition-D-ac06b0` produced a non-status blocker side-file rather than a numbered verdict.

This proposal adds a narrow bridge-route completion contract to the shared cloud loop used by F/H and the standalone D loop. On `bridge-review` and `verification` routes, assistant prose, pseudo-tool text, blank no-tool responses, non-status side-file substitutes, and repeated publisher failures must not be treated as successful completion unless `PublishBridgeVerdict` has actually advanced the selected bridge document. Those cases enter a small publisher-only recovery path and terminate as `no_progress_loop` when unresolved. Non-bridge routes, ordinary tool use, native Stop behavior, raw Write/Edit/Bash guard denials, and the generous 600-turn / 900-second operation / 3,600-second session limits remain unchanged.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - assigned harnesses must complete genuine governed work through durable execution evidence.
- `ADR-CROSS-HARNESS-PARITY-001` - D, F, and H need semantically equivalent bridge-publication behavior despite different harness implementations.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity must be proven by behavior, not inferred from schema exposure alone.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - F and H share the cloud harness loop, so completion semantics belong in the shared base.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - H is a first-class LO harness using the shared cloud runtime and must inherit the bridge completion contract.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - D's standalone loop must preserve equivalent fail-closed guarded tool behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the numbered bridge file chain is authoritative; prose and side files cannot substitute for a status-bearing verdict file.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - recovered publication must preserve dispatcher session and model provenance.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - the repair must preserve the approved 600-turn, 900-second operation, 3,600-second session, worker, and lease envelopes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal declares concrete governing specifications before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization, Project, Work Item, and inline `target_paths` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map linked specs to executed deterministic tests.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - live provider failures become work items, proposals, tests, reports, and verdicts rather than ambient observations.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the observed no-verdict outcomes trigger governed correction.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, dispatch evidence, and implementation artifacts stay linked.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this is GT-KB platform harness work within `E:\GT-KB`, not Agent Red application work.

## Prior Deliberations

- `DELIB-202666173` - owner directive to prove genuine A/B/C/D/F/H governed work and correct every discovered blocking defect.
- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` - owner-calibrated provider allowance preserves a full 3,600-second model window.
- `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-001.md` and `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-002.md` - predecessor defect and GO for raw bridge-mutation denial-loop recovery.
- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-002.md` - D/F publication parity requires genuine governed verdict publication rather than provider prose.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-001-blocker.md` - D dispatch `2026-07-14T09-00-29Z-loyal-opposition-D-ac06b0` preserved the first publication blocker and reported that version 001 was substantively reviewable but blocked by author-session metadata.
- Genuine dispatch evidence: F `2026-07-13T17-29-09Z-loyal-opposition-F-fdfb3f`, H `2026-07-13T17-40-06Z-loyal-opposition-H-d46646`, D `2026-07-14T08-07-46Z-loyal-opposition-D-7ff282`, F `2026-07-14T08-45-27Z-loyal-opposition-F-5fc7f9`, and D `2026-07-14T09-00-29Z-loyal-opposition-D-ac06b0` each demonstrate no-verdict completion, exhausted publication, or non-status substitute modes that this proposal addresses.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of defects discovered during the six-harness governed fleet proof.
- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` preserves the full 60-minute model/session window and prevents impatience-based failure classification.
- Active PAUTH `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5224-VERDICT-COMPLETION-CONTRACT-20260713` authorizes this WI-5224 bridge, source, and test scope after independent GO and implementation-start authorization. It forbids credential lifecycle work, destructive cleanup, dispatcher mutation, Git history rewrite, Git push, production deployment, and release.

## Requirement Sufficiency

Existing requirements sufficient. The owner directives and linked specifications already require governed bridge publication, cross-harness parity, provenance preservation, and unchanged generous runtime envelopes; no new formal requirement is needed before implementing this defect repair.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Add focused tests proving bridge-review/verification routes do not return successful final text unless `PublishBridgeVerdict` succeeds and advances the selected bridge document. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001`, `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | Shared-base tests plus OpenRouter and Alibaba wrapper tests prove F and H inherit the same bridge completion contract. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Ollama D tests prove equivalent handling for prose, pseudo-tool text, blank no-tool responses, repeated publisher failures, and successful publisher clearing. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Existing publisher metadata tests remain green; successful recovery continues to forward dispatcher session/model metadata. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Runtime-limit tests continue to assert 600 turns, 900-second operation timeout, and 3,600-second session timeout; no allowance reductions are made. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The post-implementation report will list exact tests and observed results for every linked behavior. |

Planned commands:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/cloud_harness_base.py scripts/ollama_harness.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/cloud_harness_base.py scripts/ollama_harness.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py
```

## Risk / Rollback

The main risk is blocking a legitimate bridge-review explanation before the model has enough information to publish. The recovery path is therefore limited to bridge-review and verification skills, keeps ordinary tool execution available until a completion failure is detected, and bounds publisher-only recovery to a small count before `no_progress_loop`. Rollback reverts only the six declared source/test paths; append-only bridge and dispatch evidence remain historical.

## Bridge Filing

This revision is filed under `bridge/` as the second status-bearing numbered bridge file for `gtkb-wi5224-provider-verdict-completion-contract`; no prior version or D blocker evidence is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - this corrects no-verdict provider completion behavior without adding a new user-facing capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
