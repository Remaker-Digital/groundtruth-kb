NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop Prime Builder interactive session

# GT-KB Bridge Implementation Proposal - gtkb-wi4552-declarative-agent-role-manifest-slice-1 - 001

bridge_kind: prime_proposal
Document: gtkb-wi4552-declarative-agent-role-manifest-slice-1
Version: 001
Project Authorization: PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-OMNIGENT-ALIGNMENT
Work Item: WI-4552
Recommended commit type: feat:

target_paths: ["config/agent-control/declarative-agent-role-manifest.yaml", "groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py", "groundtruth-kb/tests/test_agent_role_manifest.py"]

implementation_scope: source_config_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Implement WI-4552 Slice 1 by adding a GT-KB-native declarative agent/role manifest that inventories role intent, prompt/rule surfaces, tool/capability expectations, reviewer/counterpart expectations, and harness applicability in one YAML document, plus a deterministic loader/validator and focused tests.

This first slice is inventory and validation only. It does not change durable role assignment, dispatch routing, SessionStart role resolution, hook registration, harness-state projection generation, or mode-switch transactions. The live authority remains the existing harness-state source-of-truth stack and its canonical reader APIs until a later bridge proposal explicitly migrates one behavior at a time.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the governing role, harness, reader-entrypoint, and parity specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to linked requirements.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected config/source/test implementation requires a live bridge `GO`, a work-intent claim, and an implementation-start packet.
- `GOV-STANDING-BACKLOG-001` - WI-4552 is the MemBase-backed Omnigent Alignment backlog item being processed.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - roles are portable harness assignments rather than vendor-bound identities.
- `GOV-SESSION-ROLE-AUTHORITY-001` - durable role authority and transcript-defined interactive role authority remain distinct.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - harness state authority remains the three existing SoT files and canonical entrypoints.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - any live harness-state reads must go through `groundtruth_kb.harness_projection` reader APIs, not direct JSON/TOML reads.
- `DCL-HARNESS-STATE-SOT-ASSERTION-001` - existing harness-state SoT assertions must keep passing.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - any future harness represented by the manifest must preserve onboarding/capability-floor obligations.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook capability remains per-harness and must be represented without assuming identical live surfaces.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-observable role/capability surfaces require behavioral parity or declared typed waiver.

## Requirement Sufficiency

Existing requirements are sufficient for this first slice.

WI-4552 asks for an Omnigent-shaped declarative agent definition: prompt, tools, sub-agents, reviewers, and harness in one YAML. The current GT-KB specs already define the authority boundaries this slice must preserve: roles are portable, durable and interactive role authority are distinct, harness SoTs must be read through canonical entrypoints, and cross-harness observable behavior needs parity disposition. A first-slice sidecar manifest and validator can make the shape concrete without asking the owner to bless a runtime migration yet.

No new owner input is requested. Any later slice that makes the YAML manifest authoritative for SessionStart, dispatch routing, mode switching, or hook behavior should be separately proposed and reviewed.

## Target Paths

The implementation is limited to:

- `config/agent-control/declarative-agent-role-manifest.yaml`
- `groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py`
- `groundtruth-kb/tests/test_agent_role_manifest.py`

No edit to harness registry JSON configurations, capability registry TOML configs, settings/hooks JSONs, hook implementations, mode-switch code, dispatcher code, MemBase, or formal artifacts is in scope.

## Implementation Plan

1. Add `config/agent-control/declarative-agent-role-manifest.yaml` with `schema_version`, `manifest_id`, `authority_status = inventory_only`, canonical role declarations, prompt/rule surface references, capability/tool expectations, reviewer/counterpart expectations, allowed harness applicability, and explicit source-of-truth references back to the existing harness-state stack.
2. Add `groundtruth_kb.agent_role_manifest` with a deterministic PyYAML loader, typed dataclasses or structured dictionaries, schema-version validation, allowed-role validation, non-empty required-field validation, duplicate role/harness entry rejection, relative-path/root-boundary checks, and a stable content hash.
3. Keep live role and harness behavior unchanged. If the loader needs to compare against live harness state, it must call `groundtruth_kb.harness_projection.read_roles` rather than directly reading `harness-state/harness-registry.json`.
4. Add tests that parse the YAML manifest, validate role declarations for `prime-builder` and `loyal-opposition`, reject unknown role tokens, reject duplicate role or harness ids, verify source-of-truth references point to canonical reader surfaces, verify no direct harness-state file reads are introduced, and verify no network/LLM/subprocess dependency exists.
5. Add cross-harness parity test expectations for role-specific capability declarations: active PB/LO harnesses can be represented by harness name/id and any harness-specific gaps must be encoded as an explicit inventory note or typed waiver reference rather than implied by omission.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Manifest contains role ids, file paths, capability ids, and prose only; no credentials, tokens, endpoint secrets, or key-shaped values. | Bridge helper credential scan and focused source review. | |
| CQ-PATHS-001 | Yes | Limit implementation to the three declared target paths and do not touch live harness SoTs or hook registrations. | Implementation-start target validation and `git status --short -- <target paths>`. | |
| CQ-COMPLEXITY-001 | Yes | Keep schema validation deterministic and table-driven; do not build a runtime dispatcher or mode-switch layer in this slice. | Ruff check and focused tests. | |
| CQ-CONSTANTS-001 | Yes | Name schema version, role tokens, authority status, and required fields as constants in the loader. | Tests for accepted/rejected role and authority tokens. | |
| CQ-SECURITY-001 | Yes | Loader is local/read-only; it must not call LLM, network, subprocess, shell, or provider APIs. | Source-inspection test for forbidden dependency strings. | |
| CQ-DOCS-001 | Yes | YAML comments or fields must distinguish inventory-only status from live authority. | Test/source review confirms `authority_status` and SoT references. | |
| CQ-TESTS-001 | Yes | Add tests for parsing, required fields, duplicate ids, unknown role rejection, SoT reader discipline, path-boundary behavior, and no hidden runtime migration. | `python -m pytest groundtruth-kb/tests/test_agent_role_manifest.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | The loader does not add runtime logging. | Diff review confirms no logging surface. | No runtime behavior is introduced. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge applicability preflight, ADR/DCL clause preflight, and target-path coverage preflight before reporting implementation. | Command output included in the post-implementation report. | |

## Cross-Harness Disposition

This slice touches a harness-observable configuration surface by adding `config/agent-control/declarative-agent-role-manifest.yaml` and a loader that describes role/capability expectations. It does not install harness-specific hooks or change behavior on any harness.

| Harness / role surface | Disposition |
| --- | --- |
| Codex / Prime Builder | Represented in inventory; no behavior change; parity impact is documentation/validation only. |
| Claude / Prime Builder | Represented in inventory; no behavior change; suspended status remains governed by existing harness registry. |
| Ollama / Loyal Opposition | Represented as dispatch-capable LO where applicable; no behavior change. |
| OpenRouter / Loyal Opposition | Represented as dispatch-capable LO where applicable; no behavior change. |
| Antigravity / Loyal Opposition | Represented with hook-capability caveat per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; no behavior change and retired status remains authoritative in harness registry. |
| Cursor / Prime Builder | Represented where present in the harness registry; no behavior change. |

No typed waiver is requested because this slice does not require behavioral equivalence beyond manifest parse/validation. Later behavior migration proposals that touch harness-specific surfaces must include a fresh cross-harness disposition and any typed waivers needed under `ADR-CROSS-HARNESS-PARITY-001`.

## Out Of Scope

- Making the YAML manifest authoritative for durable role assignment, SessionStart role resolution, dispatcher target selection, mode switching, AUQ routing, or hook registration.
- Editing harness registry config files or harness capability registry TOML configs.
- Adding new role tokens or reviving `acting-prime-builder` as a settable role.
- Migrating existing rule files, startup overlays, hooks, skills, or dispatcher config into YAML.
- Adding phone/web approval surfaces; that is WI-4553.
- Adding cost/token budget enforcement; that is WI-4550.
- Mutating MemBase or formal GOV/ADR/DCL/SPEC records.

## Owner Decisions / Input

No new owner input is requested.

Relevant existing decisions:

- `DELIB-OMNIGENT-ADVISORY-20260614` - owner accepted Omnigent Alignment work items including WI-4552.
- `DELIB-20263229` - owner selected patterns-only Omnigent emulation: borrow design shape without importing Omnigent or creating runtime dependency.
- `DELIB-20265586` - owner-approved project authorization snapshot covering the Omnigent Alignment bounded implementation scope.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - central deterministic services with thin adapters are preferred for repeatable policy decisions.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - owner determined cross-harness parity is required and enforced.

## Prior Deliberations

- `DELIB-OMNIGENT-ADVISORY-20260614` - established Omnigent Alignment work items including WI-4552.
- `DELIB-20263229` - patterns-only emulation decision for Omnigent-derived ideas.
- `DELIB-20265586` - project authorization snapshot for Omnigent Alignment.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic service plus thin-adapter architecture.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - cross-harness parity enforcement gap owner determination.
- `bridge/gtkb-wi4551-unified-policy-registry-slice-1-003.md` - adjacent Omnigent Alignment policy-registry slice; WI-4552 should follow the same inventory-first, no-hidden-migration pattern.

## Spec-Derived Verification Plan

| Spec / governing surface | Verification obligation |
| --- | --- |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge preflight sees Project Authorization, Project, Work Item, and concrete `target_paths`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight has no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests map to role portability, reader-entrypoint discipline, no live behavior migration, and cross-harness inventory semantics. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | PB obtains GO, work-intent claim, and implementation-start packet before touching config/source/test files. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Manifest accepts only canonical role tokens and keeps role assignment portable across harnesses. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Manifest status remains `inventory_only` and tests prove it does not mutate or override durable/transcript role authority. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | YAML references the existing SoT stack and does not declare itself authoritative. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | Loader does not directly read harness-state JSON/TOML; any live comparison uses canonical reader APIs. |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | Existing harness-state SoT tests remain green. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Manifest shape preserves onboarding artifact/capability-floor references for future harnesses. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Manifest represents per-harness hook capability without assuming universal event hooks. |
| `ADR-CROSS-HARNESS-PARITY-001` | Proposal includes this Cross-Harness Disposition and tests check explicit harness applicability/gap representation. |

## Acceptance Criteria

- [ ] `config/agent-control/declarative-agent-role-manifest.yaml` exists and declares schema version, manifest id, inventory-only authority status, canonical roles, prompt/rule surfaces, tool/capability expectations, reviewer/counterpart expectations, harness applicability, and SoT references.
- [ ] `groundtruth_kb.agent_role_manifest` loads and validates the YAML deterministically, rejects duplicate role/harness ids, rejects unknown role tokens, rejects unsupported authority status, and returns a stable content hash.
- [ ] The loader does not directly read or mutate `harness-state/harness-registry.json`, `harness-state/harness-identities.json`, or `config/agent-control/harness-capability-registry.toml`; any live harness-state comparison uses canonical `harness_projection` reader APIs.
- [ ] Existing role/harness behavior remains unchanged: no mode-switch, dispatcher, SessionStart, hook, AUQ, or harness projection code is modified in this slice.
- [ ] Focused tests cover the manifest parse path, validation failures, source-of-truth reader discipline, cross-harness applicability inventory, and deterministic/no-network/no-LLM/no-subprocess behavior.
- [ ] Verification commands include focused pytest, Ruff check, Ruff format-check, bridge applicability preflight, ADR/DCL clause preflight, and proposal target-path coverage preflight.

## Risk And Rollback

Risk is low because the slice adds sidecar inventory/config and a read-only loader only. The main risk is schema drift with the existing harness-state SoTs; tests mitigate this by requiring explicit source-of-truth references and by keeping the manifest non-authoritative. Rollback is to remove the three target files; no live role, dispatch, hook, or MemBase state should require rollback.

## Loyal Opposition Asks

1. Verify that the slice is narrow enough to avoid hidden role/harness behavior migration.
2. Confirm the linked specs are sufficient for a sidecar declarative manifest and loader.
3. Return `GO` if the scope is acceptable; otherwise return `NO-GO` with concrete required changes.
