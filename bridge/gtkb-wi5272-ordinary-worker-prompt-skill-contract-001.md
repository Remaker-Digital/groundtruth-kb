NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope active; WI-5272 implementation requires ops envelope for configuration-like prompt/skill mutation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Ordinary-worker prompt and skill contract rewrite

bridge_kind: prime_proposal
Document: gtkb-wi5272-ordinary-worker-prompt-skill-contract
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5272-ORDINARY-WORKER-PROMPT-SKILL-CONTRACT-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5272

target_paths: ["config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/activity-disposition-profiles.toml", ".claude/rules/codex-session-bootstrap.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/codex-loyal-opposition-runbook.md", ".claude/skills/bridge/SKILL.md", ".claude/skills/verify/SKILL.md", ".claude/skills/dispatcher-control/SKILL.md", ".claude/skills/bridge-config/SKILL.md", ".claude/skills/bridge-reconciliation/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/verify/SKILL.md", ".codex/skills/dispatcher-control/SKILL.md", ".codex/skills/bridge-config/SKILL.md", ".codex/skills/bridge-reconciliation/SKILL.md", ".codex/skills/MANIFEST.json", "platform_tests/skills/test_skill_catalog_contract.py", "platform_tests/scripts/test_session_startup_control_map.py", "platform_tests/scripts/test_benchmark_activity_envelope_load.py", "platform_tests/scripts/test_wi5266_envelope_resource_routing.py"]

implementation_scope: configuration/source/test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5272 proposes the ordinary-worker prompt and skill rewrite. PB/LO ordinary sessions keep role-adapted baseline knowledge, but assigned bridge/dispatcher content must come through worker-context and mediated packet facades. Configuration-like prompt/skill mutations require an ops activity envelope after GO.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5272` and keeps the bridge, PAUTH, ops-envelope, and verification gates intact.

## Requirement Sufficiency

Existing requirements sufficient.

The work item, owner decisions, and active PAUTH define the implementation boundary. Implementation that mutates prompt, skill, rule, adapter, or startup guidance files must occur only after LO GO, work-intent claim, implementation-start authorization, and an ops activity envelope for the configuration-like mutations.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB` and no adopter application path is targeted.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher remains a GT-KB-owned black-box service surface.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - ordinary workers must not depend on raw bridge/dispatcher/TAFE/harness internals.
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` - ordinary workers receive full assigned content through safe packet facades.
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - protected access requires the correct activity envelope and case authority.
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` - ordinary dispatcher work should use a worker-context facade.
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` - child work remains tied to the approved black-box foundation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms this platform prompt/skill work stays outside adopter application scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses helper-mediated bridge filing and explicit compliance evidence.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-surface behavior changes require parity disposition or typed waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - target paths touching harness surfaces require cross-harness disposition.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` - ordinary worker means a session envelope without an initialized activity envelope; PB and LO ordinary workers retain role-adapted baseline behavior/constraints/knowledge.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` - safe packet must contain full assigned proposal/verdict/report/review content and omit black-box internals.
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE` - raw bridge files and bridge index are protected ordinary-worker surfaces; workers should use mediated CLI/views.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - ops controls black-box configuration mutation; build controls direct internals mutation only with case authorization.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` - worker-safe facades and prompt/skill alignment precede audit/soft-deny and hard gates.

## Owner Decisions / Input

- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` - owner-decision evidence for ordinary-worker baseline semantics.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - owner correction requiring ops envelope for black-box configuration mutation and case-specific build authorization for internals.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5272-ORDINARY-WORKER-PROMPT-SKILL-CONTRACT-20260717` - active project authorization covering `WI-5272`.

## Cross-Harness Disposition

| Harness | Disposition | Evidence / Required Follow-up |
| --- | --- | --- |
| Claude Code | Behavioral parity required and in scope. Canonical `.claude/skills/*`, startup overlays, and rule files are target paths. | Update canonical Claude skill/rule/startup surfaces so ordinary workers use worker-context and mediated packet commands instead of raw internals. |
| Codex | Behavioral parity required and in scope. Generated `.codex/skills/*` adapters and `.codex/skills/MANIFEST.json` are target paths. | Regenerate/update Codex adapters from canonical skill sources and prove adapter/catalog consistency. |
| Cursor | Not an applicable target in this WI; no Cursor-specific hook, prompt, or adapter file is changed. | Cursor parity or typed waivers belong to WI-5275 unless LO requires narrower follow-up before GO. |
| Antigravity | Not an applicable target in this WI; no Antigravity-specific adapter/config target is changed. | Antigravity parity or typed waivers belong to WI-5275 unless LO requires narrower follow-up before GO. |
| Ollama / OpenRouter / other headless providers | Not applicable to this prompt/skill rewrite target set. Provider dispatch packet semantics remain mediated by worker-context/bridge packet surfaces. | Provider-specific enforcement or unsupported-surface waivers belong to WI-5275 and the WI-5276 closure scanner. |

## Proposed Scope

- Rewrite ordinary-worker startup, role, bridge, verification, dispatcher-control, bridge-config, and bridge-reconciliation guidance so ordinary PB and LO sessions use worker-context and mediated packet surfaces for assigned work.
- Remove ordinary-worker instructions that require direct raw bridge-file, TAFE, dispatcher-runtime, harness-registry, queue-ranking, or configuration-internal inspection as live dependencies.
- Treat prompt/skill/rule updates as configuration-like black-box work requiring LO GO, claim, implementation-start authorization, and an ops activity envelope.
- Preserve role-adapted baseline behavior while making activity-envelope escalation explicit for ops/build/case-authorized internals access.
- Do not mutate dispatcher topology, TAFE/runtime state, harness registry state, hook registrations, credentials, release/deployment surfaces, adopter application files, or Git remote state.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run startup/control-map and skill catalog tests to prove dispatcher internals remain service-owned and ordinary prompts use facades. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Run deterministic scans over target prompts/skills to reject ordinary-worker raw bridge/dispatcher/TAFE/harness-state dependency language. |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Verify ordinary guidance points to worker-context and mediated packet commands for full assigned content. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Verify ops/build/case-authorized exception language remains explicit and does not grant ordinary access. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Verify prompt and skill guidance references the facade commands introduced by WI-5270/WI-5271 and does not create competing ad hoc read paths. |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | Verify implementation remains sequenced behind active foundation specs and uses the active WI-5272 PAUTH. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify target paths remain GT-KB platform prompt/skill/test files and do not touch adopter application files. |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify Claude canonical skill/rule changes and Codex generated adapter/manifest changes preserve equivalent ordinary-worker instructions. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run the proposal/bridge compliance gate and targeted skill catalog tests proving this Cross-Harness Disposition remains present and accurate. |

## Acceptance Criteria

- Ordinary-worker instructions name worker-context and mediated bridge packet views as the default source for assigned proposal/verdict/report/verification content.
- No ordinary-worker prompt, startup overlay, or governed skill instructs workers to inspect raw bridge files, bridge index/state, dispatcher runtime/config, TAFE internals, harness registry files, or queue-ranking data as ordinary live dependencies.
- Canonical Claude skill changes are regenerated into Codex adapters and manifest state, with tests proving adapter/catalog consistency.
- The implementation report lists any remaining explicit break-glass/ops/build/internal references and proves they are scoped to maintenance, ops, build, or case-authorized paths rather than ordinary worker flow.
- Implementation proves it ran under an ops activity envelope for configuration-like prompt/skill mutations; this current build-envelope proposal is not an implementation authorization for those mutations.

## Risks / Rollback

Risk is moderate because this touches behavior-defining prompt, rule, skill, and adapter surfaces. The largest risk is over-redacting operator diagnostics or leaving an ordinary-worker raw-internal instruction behind.

Rollback is a revert of the prompt/skill/rule/adapter/test changes under the approved target paths. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `config/agent-control/activity-disposition-profiles.toml`
- `.claude/rules/codex-session-bootstrap.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-loyal-opposition-runbook.md`
- `.claude/skills/bridge/SKILL.md`
- `.claude/skills/verify/SKILL.md`
- `.claude/skills/dispatcher-control/SKILL.md`
- `.claude/skills/bridge-config/SKILL.md`
- `.claude/skills/bridge-reconciliation/SKILL.md`
- `.codex/skills/bridge/SKILL.md`
- `.codex/skills/verify/SKILL.md`
- `.codex/skills/dispatcher-control/SKILL.md`
- `.codex/skills/bridge-config/SKILL.md`
- `.codex/skills/bridge-reconciliation/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `platform_tests/skills/test_skill_catalog_contract.py`
- `platform_tests/scripts/test_session_startup_control_map.py`
- `platform_tests/scripts/test_benchmark_activity_envelope_load.py`
- `platform_tests/scripts/test_wi5266_envelope_resource_routing.py`

## Recommended Commit Type

`docs`
