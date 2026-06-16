NEW

# WI-4556 Ollama Provider Failure Fallback And Backoff Proposal

bridge_kind: prime_proposal
Document: gtkb-wi-4556-ollama-provider-fallback-backoff
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecfdf-c44b-7603-ac93-3c7bd5551105
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation; Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4556

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-*.md"]

implementation_scope: source, test_addition, config, dispatcher_runtime, provider_failure_backoff
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the bounded WI-4556 dispatch hardening for Ollama provider failures:
when harness D launches but the provider returns a live-chat failure, exhausts
turns before producing a verdict, or otherwise exits without the expected bridge
verdict, the dispatcher must record that provider/output failure as operational
evidence, temporarily degrade or back off that target for the affected selected
batch, suppress duplicate launches for the same failed work, and fall back to
the next eligible Loyal Opposition backend when one is available.

The live trigger state during this run shows the need for this slice. The
pending LO review for
`gtkb-bridge-index-retirement-cleanout-packet-correction` was selected for
Ollama D, but the run ended with `ollama_harness: max-turn exhaustion before
final assistant text`, no stdout, no verdict file, no live process, and a stale
`last_result: launched` dispatch state. That is the same class of failure
captured by WI-4556: cheap reviewer launch success is being mistaken for work
delivery, leaving bridge work stuck and repeatedly selected.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the active PAUTH permits
  bounded work but does not bypass Loyal Opposition review or implementation
  start authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposal, GO, implementation report,
  and VERIFIED/NO-GO remain the lifecycle authority for this source/test
  mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites the governing dispatcher, project-authorization, and verification
  specifications before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the header links this
  proposal to PAUTH `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556`, project
  `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`, and `WI-4556`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report
  must carry forward these specifications and execute the mapped tests.
- `GOV-STANDING-BACKLOG-001` — WI-4556 is the live MemBase backlog authority for
  this defect and prevents duplicate untracked dispatch-failure work.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — the project-scoped
  authorization is bounded to linked specifications and work-item scope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch state must reflect actual
  work delivery evidence, not only process launch.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — fallback must preserve role, harness,
  selected batch, and prompt/envelope identity when choosing another backend.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — fallback must use configured eligibility
  rules and must not bypass blocked-role or dispatchability constraints.
- `SPEC-TAFE-R4`, `SPEC-TAFE-R5`, and `SPEC-TAFE-R6` — target selection,
  health, and telemetry must expose failure/backoff evidence and continue to
  apply hard gates before cost/quality/availability ordering.

## Prior Deliberations

- `DELIB-20263381` — owner AUQ authorizing bounded WI-4556 implementation work
  for Ollama provider-failure handling, fallback/backoff behavior, stale worker
  suppression, and focused regression tests under the cost-optimized
  autodispatch project.
- `DELIB-20261075` — SP-1 dispatch reliability investigation identifying
  max-turn exhaustion, no-verdict dispatch completion, missing outcome feedback,
  and self-review guard issues as dispatch reliability failure modes.
- `DELIB-20263076` — ordered fallback routing GO for WI-4484; this proposal
  builds on that fallback substrate by treating provider/output failure as a
  temporary target-health input rather than as a successful dispatch.
- `DELIB-20263438` — owner decision that role assignment, dispatchability, and
  rule-based routing are independent; fallback must honor declarative
  dispatchability and role constraints.
- `bridge/gtkb-lo-review-dispatch-reliability-008.md` — recent VERIFIED work
  repaired same-session review refusal and some diagnostics; this proposal does
  not duplicate that work and focuses on post-launch provider/output failure
  handling.

## Owner Decisions / Input

This proposal depends on the owner authorization recorded in
`DELIB-20263381` / `AUQ-2026-06-14-COST-AUTODISPATCH-WI-4556`.

The recorded authorization allows bounded implementation work on WI-4556 for
Ollama provider-failure handling, backoff/fallback behavior, duplicate/stale
worker suppression, and focused regression tests. It explicitly does not
authorize production deployment, credential lifecycle changes, retired poller
restoration, bridge protocol bypass, self-review, or unapproved formal artifact
mutation.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirements are the WI-4556 MemBase record, owner AUQ
`DELIB-20263381`, project authorization
`PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556`, and dispatcher requirements
`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCH-ENVELOPE-ELEMENT-001`,
`DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-TAFE-R4`, `SPEC-TAFE-R5`, and
`SPEC-TAFE-R6`. No new GOV/SPEC/PB/ADR/DCL mutation is required before this
source/test slice can be implemented after GO.

## Spec-Derived Verification Plan

| Requirement / specification | Verification command | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff` after GO | Packet is issued only for the approved target paths and current latest GO. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-TAFE-R5`, `SPEC-TAFE-R6` | Add/extend `platform_tests/scripts/test_cross_harness_bridge_trigger.py` for provider/output failure outcome recording. | A launched worker that exits without a verdict records `provider_failure`, `max_turn_exhaustion`, or `no_verdict_produced` evidence instead of remaining a clean `launched` state. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-TAFE-R4` | Add/extend cross-harness trigger tests for fallback target selection after temporary D degradation. | The same selected LO batch can fall back to the next eligible backend without violating role/dispatchability/rule gates. |
| WI-4556 duplicate/stale worker suppression | Add regression coverage for repeated selected signatures after provider failure. | Duplicate launches for the same failed selected batch are suppressed or delayed until the backoff window expires. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report runs the full focused pytest lane plus lint and format checks. | All mapped tests pass and exact observed results are reported. |
| No-index invariant | `Test-Path bridge\INDEX.md` | Returns `False`; implementation does not recreate the retired index. |

Focused implementation commands expected in the post-implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
```

## Risk / Rollback

Main risks:

- Over-aggressive backoff could suppress a healthy recovered Ollama target and
  increase cost by falling back to OpenRouter or another backend unnecessarily.
- Under-aggressive backoff could keep re-launching a target that already proved
  it cannot produce a verdict for the selected batch.
- Fallback must not mark a proposal as reviewed merely because a worker process
  launched; it must remain tied to actual bridge verdict output.

Rollback is a single implementation commit reverting the dispatcher/provider
failure handling and tests. Rollback must preserve existing ordered fallback
behavior from WI-4484 and must not recreate `bridge/INDEX.md`.

## Bridge Filing (No-Index)

This proposal must be filed under `bridge/` through the governed no-index bridge
writer. It publishes versioned bridge state through dispatcher/TAFE state and
must not create, restore, or require `bridge/INDEX.md`.

## Recommended Commit Type

fix: the eventual implementation repairs broken dispatch behavior where a
provider/output failure can be recorded as successful launch and leave selected
bridge work stuck without clean fallback/backoff.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
