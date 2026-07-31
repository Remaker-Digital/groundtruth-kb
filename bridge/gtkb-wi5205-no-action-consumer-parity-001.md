NEW

# WI-5205 - Project canonical NO-ACTION semantics across A/B/C/D/F/H

bridge_kind: prime_proposal
Document: gtkb-wi5205-no-action-consumer-parity
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-12 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5205-NO-ACTION-PARITY-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5205

target_paths: ["AGENTS.md", "CLAUDE.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", ".claude/rules/file-bridge-protocol.md", "config/agent-control/system-interface-map.toml", ".claude/rules/codex-standing-priorities.md", ".claude/rules/codex-review-operating-contract.md", ".claude/rules/codex-loyal-opposition-runbook.md", ".claude/rules/prime-bridge-collaboration-protocol.md", "scripts/dispatcher_runtime.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/session_self_initialization.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "scripts/protocol_enforcement_health.py", "scripts/bridge_verified_backlog_reconciler.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py", "scripts/autonomous_dispatch_loop_health.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", ".claude/skills/bridge/SKILL.md", ".codex/skills/bridge/SKILL.md", ".agent/skills/bridge/SKILL.md", ".api-harness/skills/bridge/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/MANIFEST.json", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "groundtruth-kb/templates/skills/bridge/SKILL.md", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py", "platform_tests/scripts/test_protocol_enforcement_health.py", "platform_tests/scripts/test_session_handoff_service.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_dispatcher_envelope_runtime.py", "platform_tests/scripts/test_autonomous_dispatch_loop_health.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_generate_api_skill_adapters.py", "platform_tests/scripts/test_system_interface_map.py", "platform_tests/skills/test_skill_catalog_contract.py", "groundtruth-kb/tests/test_scaffold_bridge_index.py"]

implementation_scope: authoritative contracts, runtime consumers, reporting/health, managed skill projections, scaffold sources, and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`DCL-NO-ACTION-STATUS-SEMANTICS-001`, `groundtruth_kb.bridge.disposition`, `groundtruth_kb.bridge.notify`, and dispatcher rules already agree: latest `NO-ACTION` is nonterminal Loyal-Opposition-actionable work that requires a corrected `GO` or `NO-GO`. Active consumers have drifted. A/B/C startup and rule contracts say `NEW`/`REVISED` only; the shared B/C/D/F/H dispatch prompt and D/F provider prompts omit `NO-ACTION`; state report, handoff, health, scheduler, startup metrics, and terminal reconciliation can hide or suppress it; the canonical bridge skill and A/C/D/F/H projections describe an incomplete review queue.

This is live behavioral failure, not documentation polish. H twice stood down on `gtkb-wi5200-5202-generous-harness-repair-003`; B then issued a GO for WI-5203 whose reasoning repeated the same terminal-stand-down error despite the governing DCL. This proposal projects the canonical status set across every active A/B/C/D/F/H consumer, prevents terminal linked work items from suppressing latest `NO-ACTION`, and keeps `NEW`/`REVISED` no-verdict fail-closed. Historical bridge files, archived reports, Cursor-only projections, and generic proposal-review wording that does not claim a complete status set are excluded.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — defines `NO-ACTION` as Prime-authored, nonterminal, LO-actionable correction work requiring a replacement `GO` or `NO-GO`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — owns status/role authority and the append-only correction chain.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — requires an explicit A/B/C/D/F/H disposition when active rule, prompt, and skill surfaces change.
- `ADR-CROSS-HARNESS-PARITY-001` — requires semantic capability equivalence across applicable harness consumers.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — requires truthful prompt, skill, readiness, and governed-verdict behavior for dispatchable harnesses.
- `GOV-SESSION-SELF-INITIALIZATION-001` — governs startup queue metrics and LO auto-processing text.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — requires every authoritative source, projection, template, test, and verification dependency to remain inside `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete governing links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the project, work item, and PAUTH metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent cross-surface fixture and generation evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5205 and TEST-11359 preserve the horizontal regression and acceptance boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — keeps the owner decision, work item, test, proposal, generated projections, report, and verdict traceable.

## Prior Deliberations

- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` — owner correction establishing the operative status semantics now present in the DCL and code of record.
- `DELIB-20260708-NO-ACTION-CORRECTION-DRIVE-APPROACH` — directs projection of the corrected semantics rather than preserving stale consumer behavior.
- `DELIB-202666173` — directs genuine A/B/C/D/F/H proof and correction of every defect discovered.
- `INTAKE-f92c585f` — asks which corrected LO responses are permitted; the governing DCL resolves this to `GO` or `NO-GO`, so the deferred intake does not override the specified rule.
- `WI-5203` / `bridge/gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown-002.md` — live evidence that both the original proposal and an independent B review applied the stale terminal-stand-down interpretation.

## Owner Decisions / Input

Mike explicitly directed genuine governed proof for A/B/C/D/F/H and correction of every discovered defect, recorded as `DELIB-202666173`. The bounded implementation authorization is `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5205-NO-ACTION-PARITY-20260711`. No new semantic choice is requested; the owner already fixed the meaning in the cited 2026-07-08 decisions.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-NO-ACTION-STATUS-SEMANTICS-001` is explicit about authorship, actionability, nonterminal state, correction response, and forbidden uses. The parity, onboarding, startup, bridge, and verification requirements define the projection and evidence boundaries.

## Spec-Derived Verification Plan

1. `DCL-NO-ACTION-STATUS-SEMANTICS-001`: `NEW -> GO -> NO-ACTION` fixtures remain LO-actionable in dispatcher, state report, startup, handoff, health, scheduler, and reconciler consumers even when the linked work item is terminal; the expected next action is corrected `GO`/`NO-GO`.
2. `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` / `ADR-CROSS-HARNESS-PARITY-001`: A/B/C contracts and shared prompt, D/F provider prompts, H shared prompt, canonical bridge skill, and A/C/D/F/H generated adapters/manifests all carry equivalent status semantics by applicability.
3. `GOV-SESSION-SELF-INITIALIZATION-001`: LO startup counts and auto-process text include `NO-ACTION`; WI-5206 is completed first because both proposals touch `session_self_initialization.py`.
4. Managed-skill generation checks prove canonical `.claude/skills/bridge/SKILL.md`, registry SHA metadata, A/C/D/F/H adapters, and manifests agree. Existing unrelated generated drift is isolated and reported rather than overwritten.
5. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: an independent LO session runs the focused functional suite, adapter checks, and lint/format on changed Python.

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli assert --spec DCL-NO-ACTION-STATUS-SEMANTICS-001
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_session_self_initialization.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py platform_tests/scripts/test_protocol_enforcement_health.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py platform_tests/scripts/test_dispatcher_envelope_runtime.py platform_tests/scripts/test_autonomous_dispatch_loop_health.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_system_interface_map.py groundtruth-kb/tests/test_scaffold_bridge_index.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py platform_tests/skills/test_skill_catalog_contract.py -q --tb=short
```

Expected result: all WI-owned fixtures pass; no latest `NO-ACTION` is hidden, terminal-reconciled, or called successful without a corrected verdict; A/B/C/D/F/H projections agree; unrelated dirty baseline is explicitly isolated.

## Managed Skill Structural Review

- Registry authority: PASS. `.claude/skills/bridge/SKILL.md` is canonical; `config/agent-control/harness-capability-registry.toml` and generated manifests own projections.
- Target completeness: PASS. Canonical skill, A adapter, C adapter, D/F/H shared API adapter, all three manifests, registry SHA, generator tests, and catalog contract are included. Cursor E is intentionally outside the owner-selected harness set and is not generated by these commands.
- Stale assumptions: the worktree already contains unrelated adapter/manifest drift. Implementation must generate or hunk-apply only WI-5205-owned `bridge` skill changes and prove canonical-body SHA agreement without reverting foreign edits.
- Lifecycle/spec linkage: PASS. WI-5205, TEST-11359, PAUTH, owner decision, cross-harness specs, and verification commands are present.

## Cross-Harness Disposition

| Harness | Disposition |
| --- | --- |
| Codex A | Active PB contract learns that latest `NO-ACTION` belongs to LO, while its generated bridge skill describes the complete LO queue. A remains PB and never authors LO verdicts. |
| Claude Code B | Active LO startup/rules, shared dispatch prompt, canonical skill, and native manifest require processing `NO-ACTION` into corrected `GO`/`NO-GO`. |
| Antigravity C | Optimized LO overlay plus generated `.agent` bridge skill receive identical semantics; no extra startup files are loaded. |
| Ollama D | Shared dispatch prompt, D provider prompt, and `.api-harness` bridge skill require corrected review; guard-adapter floor is unchanged. |
| OpenRouter F | Shared dispatch prompt, F provider prompt, and `.api-harness` bridge skill require corrected review; guard-adapter floor is unchanged. |
| Alibaba H | Shared dispatch prompt and `.api-harness` bridge skill require corrected review; H provider system prompt is status-neutral and needs no edit. |

No waiver is requested. Canonical routing remains unchanged because it is already correct.

## Risk / Rollback

The main risks are accidental expansion into historical noise, generated-file overwrite of unrelated dirty edits, and changing canonical routing that is already correct. The target set excludes archives/history/Cursor-only files, uses canonical generators with hunk-scoped reconciliation, and locks routing with existing tests. WI-5206 must reach VERIFIED before the overlapping startup file is edited. Rollback is one scoped commit; generated projections are regenerated from the canonical skill rather than hand-reversed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5205-no-action-consumer-parity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects a live cross-harness role/actionability regression and its generated projections.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
