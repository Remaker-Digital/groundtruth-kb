NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06-codex-pb-ollama-kimi-switch
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive; ::init gtkb pb; approval_policy=never

# Implementation Proposal - WI-5047: Switch Ollama/D headless dispatch to Kimi K2.7 Code cloud

bridge_kind: prime_proposal
Document: gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-5047

target_paths: [".api-harness/routing.toml", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "groundtruth.db", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth-kb/tests/test_doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py"]

implementation_scope: config
authority_check: Prime Builder status-write eligibility checked before filing; Codex harness A is Prime Builder by durable registry and explicit `::init gtkb pb`.
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Prime Builder proposes a bounded follow-on change for `WI-5047`: switch Ollama/D headless dispatch from the currently pinned `deepseek-v4-pro-cloud` / `deepseek-v4-pro:cloud` route back to the existing Kimi route key `kimi-k2-7-code-cloud`, whose model id is `kimi-k2.7-code:cloud`.

This is a model-selection reversal of the completed `WI-4964` A/B/D headless model-pinning slice. It must therefore proceed through a new work item, new owner-decision deliberation, new PAUTH, and independent Loyal Opposition review rather than editing the current config directly.

## Claim

The owner has made a new forward model-selection decision for Ollama/D. The implementation should update only the necessary Ollama route selection, D headless argv, dispatcher model-label/status metadata, and focused verification surfaces while preserving provider credentials, durable roles, reviewer precedence, dispatch eligibility, OpenRouter/F routing, and unrelated harness settings.

## Requirement Sufficiency

Requirements are sufficient for a bridge proposal.

- Owner decision `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` explicitly confirms: "switch Ollama/D to kimi-k2.7-code:cloud and create the governed follow-on proposal."
- `WI-5047` records the follow-on work item and `TEST-11290` records the linked verification obligation.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706` is active and includes `WI-5047`.
- The target route key already exists in `.api-harness/routing.toml`: `[models.kimi-k2-7-code-cloud]` with `model_id = "kimi-k2.7-code:cloud"` and provider `ollama`.
- The prior DeepSeek decision remains historical evidence but is superseded for future Ollama/D headless dispatch by the 2026-07-06 owner decision.

## Current State Evidence

- `.api-harness/routing.toml` currently defines both route keys: `kimi-k2-7-code-cloud` -> `kimi-k2.7-code:cloud`, and `deepseek-v4-pro-cloud` -> `deepseek-v4-pro:cloud`.
- `[routing.ollama].default_model` currently points to `deepseek-v4-pro-cloud`.
- `[routing.ollama.skills]` currently points `bridge-review`, `verification`, and `implementation` to `deepseek-v4-pro-cloud`.
- `harness-state/harness-registry.json` currently records Ollama/D headless argv with `--model deepseek-v4-pro-cloud`.
- `config/dispatcher/rules.toml` currently records dispatcher budget/status metadata for harness D as `model = "deepseek-v4-pro-cloud"`.
- `gt harness roles` shows Codex/A as Prime Builder and Ollama/D as Loyal Opposition with the DeepSeek route in headless argv.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.api-harness/routing.toml`, `harness-state/harness-registry.json`, `config/dispatcher/rules.toml`, `groundtruth.db`, `platform_tests/scripts/test_verify_ollama_dispatch.py`, `groundtruth-kb/tests/test_doctor.py`, and `groundtruth-kb/tests/test_doctor_ollama.py`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - harness behavior and owner-visible model identity must remain truthful and comparable across dispatch surfaces.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs centralized headless bridge dispatch and selected target behavior.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher state/config must be inspected through governed control/status surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded project authorization before implementation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct bridge filing and independent review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before terminal VERIFIED.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - keeps Codex helper-mediated bridge filing and hook fallback evidence explicit.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - captures the owner decision and follow-on work as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - classifies model-selection decisions and supersession as artifact lifecycle triggers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the decision/work-item/proposal chain rather than treating the model switch as transient chat.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform harness configuration work out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - ensures the follow-on work is represented in the MemBase backlog.

## Prior Deliberations

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - owner decision superseding the prior DeepSeek route for future Ollama/D headless dispatch and requesting this governed proposal.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - prior owner decision that pinned Ollama/D to DeepSeek V4 Pro cloud; retained as historical context and explicitly superseded by the new decision.
- `DELIB-202665282` - Loyal Opposition VERIFIED record for the WI-4964 headless model-pinning implementation.
- `DELIB-202665283` - Loyal Opposition GO record for the WI-4964 model-pinning proposal.
- `bridge/gtkb-headless-dispatch-model-pinning-003.md` - prior REVISED proposal whose current-state evidence showed Kimi as the earlier route before DeepSeek pinning.
- `bridge/gtkb-headless-dispatch-model-pinning-006.md` - prior VERIFIED verdict documenting the completed DeepSeek pin and noting provider availability was separate from model identity.

## Owner Decisions / Input

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - new owner decision and implementation-proposal trigger.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706` - active bounded project authorization for `WI-5047`.

## Proposed Scope

1. Update `.api-harness/routing.toml` so `[routing.ollama].default_model` is `kimi-k2-7-code-cloud`.
2. Update `[routing.ollama.skills]` so `bridge-review`, `verification`, and `implementation` route to `kimi-k2-7-code-cloud` unless implementation evidence proves an explicit D argv selector fully overrides skill routing and no default/skill change is needed. The preferred implementation is to align all Ollama defaults/skills to Kimi for clarity.
3. Use the canonical harness writer/projection path to update Ollama/D headless argv from `--model deepseek-v4-pro-cloud` to `--model kimi-k2-7-code-cloud` without changing roles, lifecycle status, reviewer precedence, dispatch eligibility, prompt transport, or unrelated invocation surfaces.
4. Update dispatcher model-label/status metadata for harness D from `deepseek-v4-pro-cloud` to `kimi-k2-7-code-cloud` through the governed dispatcher-control path or an equivalent already-governed configuration transaction.
5. Update focused tests and fixtures that assert Ollama/D route identity so they expect `kimi-k2-7-code-cloud` / `kimi-k2.7-code:cloud` and still guard against provider/route confusion.
6. Do not remove the `deepseek-v4-pro-cloud` route definition unless a separate review determines it is obsolete; this proposal only changes the active Ollama/D route selection.
7. Do not change OpenRouter/F, provider credentials, Ollama account settings, external model access, durable role assignments, reviewer precedence, or dispatch eligibility.

## Out Of Scope

- Credential lifecycle, key rotation, external provider account configuration, production deployment, GitHub/settings mutation, or model availability purchase/access changes.
- Any change to Agent Red or other adopter application files.
- Re-enabling or disabling dispatch for any harness.
- Changing OpenRouter/F route identity.
- Deleting historical DeepSeek bridge, deliberation, or route evidence.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Assert D headless argv, route resolver output, and dispatcher status all name `kimi-k2-7-code-cloud` / `kimi-k2.7-code:cloud` consistently. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run `gt bridge dispatch config --json`, `gt bridge dispatch status --json`, and `gt bridge dispatch health --json`; verify D metadata updates without topology drift. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Use governed `gt bridge dispatch` / `gt harness` surfaces for status evidence rather than cached reports or aggregate queue artifacts. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Acquire implementation-start authorization for `WI-5047` and keep changes within PAUTH target classes and listed target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability and clause preflights before implementation report; cite GO and work-intent claim. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm PAUTH, project, work item, target_paths, and numbered bridge chain remain valid. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Confirm cited governing specs exist and are relevant before report filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute focused tests plus resolver/status checks and include command output in the implementation report. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Use Codex helper-mediated bridge writing and audit-only compliance evidence for this proposal. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify decision `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD`, work item `WI-5047`, test `TEST-11290`, PAUTH, and bridge proposal all exist and link coherently. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm no `applications/` or Agent Red files are changed. |
| `GOV-STANDING-BACKLOG-001` | Confirm `WI-5047` remains the backlog authority for this follow-on change. |

## Acceptance Criteria

- `scripts.ollama_harness.load_routing_config` plus `resolve_model(..., requested_model="kimi-k2-7-code-cloud", skill="bridge-review")` returns route key `kimi-k2-7-code-cloud`, model id `kimi-k2.7-code:cloud`, provider `ollama`, and the expected bridge tool set.
- Resolving the default Ollama bridge-review route without a requested model returns `kimi-k2-7-code-cloud` / `kimi-k2.7-code:cloud`.
- `harness-state/harness-registry.json` projection for harness D headless argv contains `--model kimi-k2-7-code-cloud` and no longer contains `--model deepseek-v4-pro-cloud`.
- `config/dispatcher/rules.toml` / `gt bridge dispatch config --json` reports harness D model label as `kimi-k2-7-code-cloud`.
- D durable role, status, reviewer precedence, dispatch tags, `can_receive_dispatch`, prompt placeholder, `--skill bridge-review`, and `max_items` are unchanged except for the model selector.
- Focused tests pass, including the linked `TEST-11290` assertion coverage and existing Ollama doctor/dispatch route tests adjusted for Kimi.
- Bridge applicability and clause preflights pass on the implementation report before requesting VERIFIED.

## Risks / Rollback

Risk is moderate because the change mutates live harness routing and owner-visible dispatcher metadata. The main risk is mixing provider identities: Ollama cloud route `kimi-k2.7-code:cloud` is not an OpenRouter route, and OpenRouter/F must remain untouched.

Rollback is to restore D active route selection, D headless argv, and D dispatcher label to the prior `deepseek-v4-pro-cloud` / `deepseek-v4-pro:cloud` values through the same governed config and harness writer paths. Bridge files, deliberations, work items, and PAUTH records are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `.api-harness/routing.toml`
- `harness-state/harness-registry.json`
- `config/dispatcher/rules.toml`
- `groundtruth.db`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `groundtruth-kb/tests/test_doctor.py`
- `groundtruth-kb/tests/test_doctor_ollama.py`

## Recommended Commit Type

`chore`
