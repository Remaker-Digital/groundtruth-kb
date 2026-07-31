NEW

# WI-5200..5202 — Generous cloud-harness recovery, runtime envelopes, and truthful H parity

bridge_kind: prime_proposal
Document: gtkb-wi5200-5202-generous-harness-repair
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5200-5202-HARNESS-REPAIR-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5200
Related Work Items: WI-5201, WI-5202

target_paths: [".api-harness/routing.toml", "config/agent-control/harness-capability-registry.toml", "scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_lo_harness_turn_budget.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_check_harness_parity.py", "groundtruth.db", "harness-state/harness-registry.json"]

implementation_scope: source, tests, governed runtime configuration, parity evaluation, and generated registry projection
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

A genuine dispatcher-routed Alibaba H review executed 15 model turns and 31 governed tool calls, then the provider emitted one blank no-tool response. The shared cloud loop treated that response as terminal and exited nonzero even though 25 of its 40 turns remained. The same run exposed an execution-envelope regression: H ignored the `max_turns = 200` routing value and instead used shared defaults of 40 turns and 540 seconds. Fleet inspection then found F's 5,400-second internal session was externally killed at 900 seconds, and D/F were capped at 200 turns despite owner evidence that normally completing DeepSeek/Opus-class work can require 400-plus turns and hundreds of tool actions.

This proposal repairs the complete discovered behavior, not only the first symptom. Blank no-tool responses become recoverable no-progress turns while the same explicit generous turn/session envelope remains; routing obtains distinct operation, session, and turn limits that the cloud adapters actually consume; slow provider harnesses begin at 600 turns, 900 seconds per provider operation, and 28,800 seconds per session; and dispatcher worker lifetimes begin at 29,400 seconds so the outer wrapper cannot pre-empt the inner harness. Active native A/B/C dispatches receive the same conservative 29,400-second outer floor pending sufficient profile telemetry. Semantic fail-closed controls (guard denial, malformed provider data, repeated identical tool loops, per-operation transport bounds, and ultimate overall-envelope exhaustion) remain intact.

WI-5201 is included because the same audit found Phase 1 missing H's shared API managed-skill adapter and Phase 2 hard-coding only D/F provider surfaces. The evaluator will recognize H's actual shared API skill manifest, native-full hook plus guard-floor adapter, bridge helper route, underscore-named runtime, and dispatcher no-window wrapper. Current `can_receive_dispatch` remains reported as current selection state and is not misrepresented as absence of dispatch capability; temporary proof eligibility remains governed by `gt bridge dispatch config` and is restored afterward.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001` — owns the shared provider runtime, routing contract, tool loop, retry behavior, and adopter boundaries.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` — requires H to operate through the shared Anthropic-compatible native-full runtime.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — requires truthful machine-checkable capability, readiness, guard, bridge-write, and projection evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — requires centralized dispatcher-produced execution and truthful lifecycle outcomes.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — governs eligibility changes and generated registry projection through canonical control-plane writers.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — requires mutating provider tools to retain fail-closed guard enforcement.
- `GOV-ENV-LOCAL-AUTHORITY-001` — keeps provider credentials in their existing environment authority; this work does not read or mutate them.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs role-correct append-only proposal, verdict, report, and H-proof artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite its governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the active project and PAUTH linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent execution of the spec-derived checks below before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5200, WI-5201, and WI-5202 are the durable defect records for this implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the authorization, work items, tests, proposal, report, verdict, telemetry, and proof remain one traceable artifact graph.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the discovered defects and owner policy clarification are preserved as governed records before implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — each work item and bridge thread retains explicit proposal, review, implementation, verification, proof, and completion states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all source, tests, config, state projections, and verification evidence remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` — established generous model-aware initial dispatch allowances before telemetry-based tightening; this proposal closes H/F/D coverage gaps left after H onboarding and later runtime changes.
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` — requires elapsed/runtime evidence before declaring a model hung; this proposal aligns the inner and outer bounds so that evidence is meaningful.
- `DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION` — authorized the now-VERIFIED empty-native-hook no-op fix that let H reach real tool execution.
- `DELIB-202666172` — authorized the first genuine H proof dispatch and temporary H/B routing transaction; that run produced the WI-5200/WI-5202 evidence.
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` — authorizes this combined repair, generous initial envelopes, independent verification, and genuine governed H reproof.

## Owner Decisions / Input

Mike explicitly authorized `WI-5200 WI-5201 WI-5202 + H reproof`, then reiterated `Authorize WI-5200 generous H recovery repair`. The authorization permits the exact protected source, tests, routing/parity configuration, canonical registry projection, bridge lifecycle, and temporary proof-routing mutations described here. It forbids direct harness invocation, credential work, deployment, unrelated cleanup, permanent proof routing, and budget reductions without sufficient telemetry.

## Requirement Sufficiency

Existing requirements are sufficient. `ADR-CLOUD-HARNESS-TEMPLATE-001` and `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` define the shared/adopter runtime ownership; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and `SPEC-DISPATCHER-CONTROL-SURFACE-001` define dispatcher and configuration authority; `GOV-HARNESS-ONBOARDING-CONTRACT-001` defines truthful parity/readiness evidence; and the cited bridge, guard, environment, and verification controls define the implementation boundaries. The owner decisions resolve the only policy variable: start generously and tune later from evidence.

## Implementation Plan

1. Extend the shared cloud routing schema with validated optional `timeout_seconds`, `session_timeout_seconds`, and `max_turns`, plus one explicit-CLI-over-config resolver used by H and F. Extend D's existing resolver with the distinct session field.
2. Change the shared no-tool branch so nonblank content returns normally, while blank content appends a corrective user turn and continues. Do not append an empty assistant block. Exhaustion of the overall turn/session envelope remains a nonzero fail-closed result.
3. Configure D/F/H at 600 turns, 900-second provider-operation timeout, and 28,800-second session timeout. Set active A/B/C/D/F/H dispatcher worker defaults to 29,400 seconds and derive D from the distinct session value plus completion margin.
4. Add H to the shared API capability surfaces and make Phase 2 provider/runtime evidence data-driven enough to recognize its underscore-named adapter, shared bridge skills, native-full hook/guard path, and universal dispatcher no-window wrapper.
5. Preserve unrelated pre-existing hunks in `.api-harness/routing.toml`, `config/agent-control/harness-capability-registry.toml`, `groundtruth.db`, and `harness-state/harness-registry.json`. Any invocation-surface projection change uses `gt harness set-invocation-surface`; any eligibility change uses `gt bridge dispatch config set-eligibility`.
6. After independent VERIFIED and focused commit, repeat the WI-5199 H proof only through dispatcher selection. Keep B ineligible until H commits the reserved canonical verdict, then restore B eligible/H ineligible and verify the final state.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | `python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short` | Blank recovery, routing precedence, timeout separation, transport bounds, and eventual fail-closed exhaustion pass. |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | `python -m pytest platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short` | H consumes configured generous limits and retains native-full hooks plus guarded tools. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | `python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_lo_harness_turn_budget.py -q --tb=short` | D uses 600-turn/session configuration while all mutating tools remain guard-gated. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short` with focused lifetime selectors during iteration | Every active dispatch target's outer lifetime exceeds the inner configured session by the completion margin; timeout telemetry retains source/profile evidence. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `python scripts/check_harness_parity.py --all --markdown`; `python scripts/harness_parity_phase2.py --project-root . --format markdown`; focused parity tests | Phase 1 has no unwaived H MISSING row; Phase 2 recognizes H's true runtime surfaces and separates capability from current eligibility; no new regression. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch config/status/health --json` plus transaction tests | All mutations use canonical CLI transactions; final B eligible/H ineligible state is restored; transaction tests pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability/clause preflights, work-intent claim, implementation-start packet, independent verdict, and canonical bridge show | Every write is role-correct, independently reviewed, and append-only. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent reviewer reruns the mapped tests and inspects actual diffs/config projection | VERIFIED is withheld unless all mapped evidence passes. |
| Owner functional-proof requirement | Genuine dispatcher-produced H review of `gtkb-wi5199-fd-evidence-h-functional-proof` | H commits a substantive canonical verdict with `author_harness_id: H`; telemetry shows genuine turns/tool use; no direct invocation occurs. |

Formatting and static verification:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py scripts/alibaba_cloud_studio_harness.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/dispatcher_runtime.py scripts/harness_parity_phase2.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_lo_harness_turn_budget.py platform_tests/scripts/test_harness_parity_phase2.py platform_tests/scripts/test_check_harness_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <same Python paths>
```

## Risk / Rollback

Longer envelopes increase the time a genuinely non-progressing worker can remain alive. The implementation preserves semantic no-progress detection, per-operation transport limits, guard failures, dispatcher concurrency caps, telemetry, and circuit-breaker evidence; it removes only impatience-based false failure. Blank responses can consume the generous overall envelope, but cannot bypass the session deadline or turn cap. A focused single commit permits rollback of source/test/config changes; canonical registry transactions remain separately auditable and can be reversed through the same control surface. No credential or deployment state changes.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5200-5202-generous-harness-repair`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(harness)`: correct false terminal responses, execution-envelope mismatches, and H parity-evaluator false negatives.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
