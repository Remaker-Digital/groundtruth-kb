NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-10T10-10-00Z-prime-builder-A-alibaba-h-slice4b
author_model: GPT-5.5
author_model_version: GPT-5.5
author_model_configuration: Codex interactive prime-builder; ::init gtkb pb; Alibaba-H priority drive

# Alibaba Cloud Studio Harness Slice 4b: Dispatchable H registration and live adopter proof

bridge_kind: prime_proposal
Document: gtkb-alibaba-harness-slice4b-dispatchable-registration
Version: 001
Date: 2026-07-10 UTC

Work Item: WI-5072
Expedite Work Item: WI-5169
Related Work Items: WI-5167, WI-5073
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708

target_paths: ["scripts/alibaba_cloud_studio_harness.py", ".api-harness/routing.toml", "config/agent-control/harness-capability-registry.toml", "config/dispatcher/rules.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_alibaba_cloud_studio_governance_artifacts.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".groundtruth/formal-artifact-approvals/2026-07-10-canonical-terminology-alibaba-cloud-studio-harness.json", ".groundtruth/formal-artifact-approvals/2026-07-10-operating-model-alibaba-cloud-studio-harness.json", "scripts/goose_harness.py", ".goose/**", "harness-state/harness-identities.json", "harness-state/harness-registry.json"]

implementation_scope: source, tests, config, governed state projection, narrative approval packets
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
state_projection_in_scope: true
commit_exclusions: ["groundtruth.db", "harness-state/harness-registry.json"]

---

## Summary

Implement the budget-critical Alibaba Cloud Studio slice 4b path: make harness identity `H` real, wire it as the `anthropic-messages` / `native-full-hooks` adopter of the verified shared cloud harness runtime, retire the suspended Goose `G` proxy path, and produce the focused tests and read-checks needed for Loyal Opposition to decide whether H is ready to become dispatchable.

This proposal uses WI-5072 for the required PAUTH linkage because `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708` explicitly includes WI-5072/WI-5073. It also services the P0 expedite row WI-5169 and resolves the WI-5167 ownership drift by treating this bridge thread as the single implementation home for Alibaba-H onboarding. It consumes the verified template slices 1/2/3/4a and the verified Alibaba slice-1 ADR. It does not create a second Alibaba implementation thread under the cloud-template project.

The outcome is a thin adopter profile over `scripts/cloud_harness_base.py`: endpoint env name `ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT`, token env-key name `ALIBABA_API_KEY`, dialect `anthropic-messages`, hook tier `native-full-hooks`, author identity `Alibaba Cloud Studio H`, harness id `H`, provider route `alibaba-cloud-studio`, and model route for DeepSeek V4 Pro.

## Current State Evidence

- H is not registered: `gt harness show --harness H` returns unknown harness.
- Goose G exists but is suspended and dispatch-disabled: `gt harness show --harness G` reports suspended status and dispatch `can_receive_dispatch=false`.
- Dispatcher config currently has harness overlays A-F only; H is absent.
- Canonical terminology, operating model, and capability registry currently have no Alibaba Cloud Studio harness entry.
- `scripts/cloud_harness_base.py` already implements `anthropic-messages` and `native-full-hooks`; the remaining work is adopter instantiation plus governed registration/readiness surfaces.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal spec-linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map specs to executed tests/read-checks.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status and implementation-start authorization gate this work.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - establishes H, retires G, and requires Anthropic-endpoint native-full-hook template implementation.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - establishes the shared runtime and five varying axes.
- `SPEC-INTAKE-9ec893` - governs harness identity as integration + model + config and prefers non-GUI maximal-hook integrations.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires identity, registry, capability floor, glossary, operating-model entry, ADR, doctor check, and fail-closed guard-adapter declarations.
- `GOV-ENV-LOCAL-AUTHORITY-001` - live endpoint/key values stay only in `.env.local`; source/config may reference variable names only.
- `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` - native-full-hooks does not bypass the fail-closed guard-adapter floor.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation artifacts stay under `E:\GT-KB`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH plus GO plus implementation-start packet bound the slice.
- `GOV-FORMAL-ARTIFACT-APPROVAL-001`, `GOV-ARTIFACT-APPROVAL-001`, and `DCL-ARTIFACT-APPROVAL-HOOK-001` - narrative/formal edits require approval-packet evidence; implementation must not fabricate owner approval.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - ownership resolution, supersession, and terminal readiness are durable artifact states.

## Prior Deliberations

- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` - owner decision to replace Goose with Alibaba Cloud Studio on the Anthropic endpoint, new identity H, retire G, and obsolete partial Goose work.
- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT` - owner decision splitting slice 4 into 4a native-hook wiring and 4b Alibaba-H onboarding plus live proof.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` - owner decision to build the reusable direct-cloud harness template.
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` - owner direction that harness identity is integration + model + config, preferring non-GUI maximal-hook integrations.
- `DELIB-20260708-GOOSE-GOV-BYPASS-INCIDENT` - governance-bypass history motivating replacement of a hookless GUI proxy with governed full-hook integration.
- `bridge/gtkb-alibaba-cloud-studio-harness-slice1-adr-004.md` - VERIFIED ADR for the H architecture.
- `bridge/gtkb-cloud-harness-template-slice4a-native-hook-wiring-004.md` - VERIFIED native-full-hooks lifecycle wiring that this adopter consumes.

## Owner Decisions / Input

- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` authorizes the replacement direction: new H identity, retire G, Anthropic endpoint, obsolete partial Goose work.
- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT` identifies this work as slice 4b.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` authorizes the shared-template program.
- Active `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708` explicitly includes WI-5072 and WI-5073. WI-5169 is cited as the P0 expedite driver, not as the PAUTH metadata work item.

Implementation remains gated on LO `GO` plus `scripts/implementation_authorization.py begin --bridge-id gtkb-alibaba-harness-slice4b-dispatchable-registration`.

## Requirement Sufficiency

Existing requirements sufficient. The Alibaba ADR, cloud harness template ADR, harness identity principle, onboarding contract, env authority, and slice 4 scope-split collectively specify the implementation target. No new formal requirement is needed before implementation. Narrative/formal edits remain subject to approval-packet gates and must cite existing owner decision evidence; no approval packet may be invented or backdated.

## Proposed Change / Scope

1. Add `scripts/alibaba_cloud_studio_harness.py` as the thin Alibaba adopter wrapper. It mirrors the OpenRouter adopter shape while binding to the shared base with `DIALECT_ANTHROPIC_MESSAGES`, `HOOK_TIER_NATIVE_FULL`, `AUTH_STYLE_AUTHORIZATION_BEARER`, env names `ALIBABA_API_KEY` and `ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT`, route provider `alibaba-cloud-studio`, author identity `Alibaba Cloud Studio H`, and harness id `H`.

2. Update `.api-harness/routing.toml` with an Alibaba model row and `[routing.alibaba-cloud-studio]` skill routes. Remove or obsolete Goose model/route rows if no tracked consumer remains. Preserve OpenRouter and Ollama routing behavior.

3. Update `config/agent-control/harness-capability-registry.toml` with `[harnesses.alibaba-cloud-studio]` declaring the GOV-HARNESS-ONBOARDING-CONTRACT-001 floor plus compact provider envelope metadata analogous to OpenRouter. Do not refresh unrelated managed-skill source hashes.

4. Register H and retire G through canonical harness/dispatcher CLIs, not hand edits. Expected state: H exists with stable id `H`, `harness_name="alibaba-cloud-studio"`, role `['loyal-opposition']` until LO deliberately flips broader dispatchability, headless argv using the project Python interpreter, `scripts/alibaba_cloud_studio_harness.py`, `--prompt {{PROMPT}}`, `--skill bridge-review`, and the Alibaba route. G remains suspended or retired with dispatch disabled. `harness-state/harness-registry.json` is generated projection evidence and must not be included in the final source commit.

5. Update dispatcher config through `gt bridge dispatch config` transaction commands only. H should not be selected for live review until the smoke/readiness proof passes.

6. Add `_check_alibaba_cloud_studio_harness` or equivalent to `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and wire it into the GT-KB profile. It should assert Layer-1/2/3 onboarding for H, routing/model/tool-call capability, env-var-name-only references, and G retirement/dispatch-disabled state. The check must not read or print secret values.

7. Add focused tests for the Alibaba wrapper, routing isolation, missing env classification, env loader behavior, author metadata, anthropic transport binding, native-full-hooks inheritance, capability/governance artifacts, and doctor/readiness behavior. Reuse `test_cloud_harness_base.py` for shared runtime coverage.

8. Update `.claude/rules/canonical-terminology.md` and `.claude/rules/operating-model.md` only with approval-packet evidence for exact proposed narrative content. If packet validation fails, do not mutate these files; file the report as blocked on the single missing owner approval action.

9. Remove or park obsolete Goose artifacts inside target scope: `scripts/goose_harness.py`, `.goose/**`, Goose route rows, and Goose capability/dispatch entries. If a Goose surface is untracked/generated and cannot be finalized in the source commit, report it as cleanup evidence and exclude it from finalization.

10. Run a credential-gated live smoke only if `ALIBABA_API_KEY` and `ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT` are available through the governed env loader. The smoke must not print values. If variables are missing or provider returns credential/backpressure/outage failure, classify the result and do not claim H dispatchable.

## Scope Boundary / Commit Hygiene

- Do not commit `groundtruth.db`.
- Do not commit generated `harness-state/harness-registry.json`; treat it as read-check state unless a later pure-state transaction explicitly authorizes it.
- Do not refresh unrelated registry/source hash fields in `config/agent-control/harness-capability-registry.toml`.
- Do not direct-edit `config/dispatcher/rules.toml`; use the governed dispatcher config transaction CLI.
- Do not expose or copy live `.env.local` values.
- Do not make H dispatchable before the live readiness proof passes.

## Specification-Derived Verification

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | H identity/profile uses Alibaba Cloud Studio + DeepSeek V4 Pro + Anthropic endpoint + native-full-hooks; G is retired/dispatch-disabled | `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`, `gt harness show --harness H`, `gt harness show --harness G` |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Alibaba wrapper delegates to `cloud_harness_base.AdopterProfile` and does not reimplement the loop | wrapper tests plus existing `test_cloud_harness_base.py` |
| `SPEC-INTAKE-9ec893` | routing/provider identity is distinct from OpenRouter/Ollama despite model overlap | routing-isolation tests |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | identity, registry, capability floor, glossary/operating model, ADR, doctor check all present or explicitly blocked by approval packet | governance artifact tests + doctor check |
| `GOV-ENV-LOCAL-AUTHORITY-001` | artifacts reference only env var names; missing env errors never print secret values | missing-env tests and credential scan/preflight evidence |
| `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` | native-full-hooks still inherits the fail-closed floor for mutating tools | existing base tests plus wrapper profile assertion |
| formal approval specs | narrative edits have exact approval-packet validation or are not made | approval packet validation tests/read-checks |
| bridge/project authorization specs | implementation begins only after GO and implementation-start | implementation authorization command evidence |
| dispatcher readiness | H overlay added through transaction CLI and not selected until proof passes | dispatch config/status/health output |
| live proof | if env vars are present, bounded H smoke succeeds without printing secrets; otherwise failure is classified and H is not claimed dispatchable | smoke command output with no-secret evidence |

Minimum focused commands after implementation:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_governance_artifacts.py platform_tests\scripts\test_cloud_harness_base.py -q --tb=short --basetemp .harness-tmp\alibaba-h-slice4b
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_governance_artifacts.py groundtruth-kb\src\groundtruth_kb\project\doctor.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_governance_artifacts.py groundtruth-kb\src\groundtruth_kb\project\doctor.py
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness show --harness H
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness show --harness G
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch config --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch health
```

## Acceptance Criteria

1. H has a concrete Alibaba Cloud Studio adopter wrapper over the shared base; no duplicated hand-rolled cloud harness loop is introduced.
2. H routing is distinct from OpenRouter/Ollama and uses only env variable names for endpoint/key authority.
3. GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer 1/2/3 checks for H are implemented and covered by tests or read-checks.
4. Goose G is not dispatchable after this slice.
5. Dispatcher config contains H only through governed transaction CLI effects; no direct dispatcher config edit is used.
6. The live proof either passes and supports a dispatchability request, or fails/missing-env is classified and the implementation report does not claim H dispatchable.
7. `groundtruth.db` and generated `harness-state/harness-registry.json` are not swept into any final source commit.
8. The post-implementation report includes spec-to-test mapping plus exact verification output.

## Risks / Rollback

- **Risk:** live Alibaba endpoint is missing, invalid, rate-limited, or down. **Mitigation:** classify provider readiness separately; do not claim dispatchability unless smoke passes.
- **Risk:** narrative approval packets are missing or stale. **Mitigation:** fail closed on narrative edits and report the single missing owner action.
- **Risk:** shared state/projection churn contaminates the source commit. **Mitigation:** finalization excludes `groundtruth.db` and generated `harness-state/harness-registry.json`.
- **Risk:** removing Goose artifacts conflicts with another session's untracked work. **Mitigation:** inspect status before deletion and preserve unrelated changes.
- **Rollback:** disable H through dispatcher eligibility and return registry status through the canonical harness CLI.

## Recommended Commit Type

`feat:` - this slice adds a new dispatchable harness capability surface and removes the obsolete Goose proxy path as part of the replacement.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
