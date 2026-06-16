REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Dispatcher Trigger And Automation Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-dispatcher-trigger-cleanout
Version: 002
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/single_harness_bridge_automation.py", "scripts/install_single_harness_dispatcher_task.ps1", "scripts/uninstall_single_harness_dispatcher_task.ps1", "scripts/bridge_work_intent_registry.py", ".claude/settings.json", ".codex/hooks.json", "config/agent-control/system-interface-map.toml", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_work_intent_auto_extend.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_single_harness_bridge_automation.py", "platform_tests/scripts/test_single_harness_dispatcher_task_installer.py", "platform_tests/scripts/test_slice_3_hook_registrations.py", ".claude/skills/bridge/SKILL.md", ".codex/skills/bridge/SKILL.md", ".claude/skills/bridge-config/SKILL.md", ".codex/skills/bridge-config/SKILL.md", "bridge/gtkb-no-index-dispatcher-trigger-cleanout-*.md"]

implementation_scope: dispatcher_trigger_no_index_cleanup, single_harness_automation_cleanup, skill_instruction_cleanup, hook_registration_cleanup, work_intent_fixture_cleanup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note

This REVISED version expands the target set beyond
`cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` to
include the single-harness automation activation layer and hook registrations.
The owner-provided Codex LO screenshot showed a fresh session honoring an
automation rule that still selected `bridge/INDEX.md`; the local sweep confirmed
that `.claude/settings.json` and `.codex/hooks.json` still invoke
`scripts/single_harness_bridge_automation.py`, while the activation path
delegates to the index-era dispatcher.

## Summary

The bootstrap repair in
`bridge/gtkb-no-index-implementation-authorization-bootstrap-003.md` restored
implementation-start authorization without the retired bridge index. The next
active defect is that dispatch/runtime surfaces, hook registrations, automation
activation, and work-intent tests still preserve index-only language or
fixtures:

- `scripts/cross_harness_bridge_trigger.py` still advertises and reads live `bridge/INDEX.md`.
- `scripts/single_harness_bridge_dispatcher.py` still advertises and prompts workers to read live `bridge/INDEX.md`.
- `scripts/single_harness_bridge_automation.py` is still registered from both `.claude/settings.json` and `.codex/hooks.json`; it activates or invokes the dispatcher path that still reads the retired index.
- `.codex/hooks.json` still has status messages for guarding `bridge/INDEX.md` atomic writes.
- `config/agent-control/system-interface-map.toml` still describes Codex app thread automations and Axis 2 surfaces as reading live `bridge/INDEX.md`.
- `platform_tests/scripts/test_bridge_work_intent_registry.py`, `test_work_intent_role_eligibility.py`, `test_work_intent_auto_extend.py`, `test_single_harness_bridge_dispatcher.py`, `test_single_harness_bridge_automation.py`, and `test_single_harness_dispatcher_task_installer.py` still build `bridge/INDEX.md` fixtures instead of status-bearing versioned bridge files.
- `.claude/skills/bridge/SKILL.md` and `.codex/skills/bridge/SKILL.md` still contain compatibility-view instructions that tell agents to update or read the retired index.
- The `bridge-config` skill correctly says not to summarize the retired index, but still calls it a deprecated generated compatibility view; that wording must be hardened to say the file must not exist and that breaks are defects.

This proposal covers the dispatcher/automation slice only. Startup payload
generation is covered by sibling proposal
`bridge/gtkb-no-index-startup-control-cleanout-002.md`; broader runtime tools
are covered by `bridge/gtkb-no-index-runtime-tooling-cleanout-001.md`.

## Prior Deliberations

- `DELIB-20263438` - Owner requirement: corrected bridge-dispatch architecture and rule-based dispatch.
- `DELIB-20263447` - Dispatcher/Bridge CLI-first operation benchmark; relevant to using CLI status/config/health rather than prompt-only conventions.
- `bridge/gtkb-no-index-implementation-authorization-bootstrap-003.md` - Bootstrap implementation report that fixed no-index implementation authorization and exposed remaining dispatcher/tooling defects.
- `bridge/gtkb-no-index-startup-control-cleanout-002.md` - Sibling proposal capturing the Codex LO screenshot and generated startup-payload contradiction.
- `bridge/gtkb-cli-mediated-agent-mutation-boundary-002.md` - Related design constraint: skills should sit over CLI-backed mutation surfaces where practical.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim; the prior broad cleanout GO could not mint a packet, so this compliant proposal is required.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge proposals, implementation reports, and verification verdicts remain the governed work lifecycle.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and machine-readable target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links the governing requirements for the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification will include spec-to-test mapping and observed commands.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the dispatcher/status/health CLI and harness registry are the dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - routing decisions must be based on role, subject, and activity rules, independent of a retired index file.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - hook and skill behavior must be corrected across Claude Code, Codex, Antigravity, OpenRouter, and Ollama surfaces instead of only one harness.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped cleanup. Mike's directives
are explicit: do not preserve backward compatibility for the retired index;
every break caused by its absence is a defect to fix; and agents must use the
dispatcher CLI/skills and versioned bridge files rather than `bridge/INDEX.md`.

The owner also stated that mutating GT-KB operations should be captured by the
CLI as the internal AI/agent system UI. This proposal should therefore prefer
`gt bridge dispatch config|status|health` and shared no-index resolver services
over prompt-only cleanup.

## Proposed Implementation

1. Replace trigger/dispatcher bridge-state discovery with versioned bridge-file scanning or existing dispatcher/TAFE state surfaces. Do not recreate or require `bridge/INDEX.md`.
2. Update trigger, dispatcher, and automation help text, worker prompts, diagnostics, dedupe signatures, and health evidence so they describe the no-index dispatcher model.
3. Update `.claude/settings.json` and `.codex/hooks.json` so active hook registrations do not invoke or advertise index-era automation. If single-harness automation remains, it must operate through no-index dispatcher state and CLI status/health.
4. Rewrite focused work-intent and single-harness automation tests to create status-bearing bridge files (`bridge/<slug>-NNN.md`) instead of index-only fixtures.
5. Harden the bridge and bridge-config skills so active instructions say:
   - `bridge/INDEX.md` must not exist.
   - Dispatcher topology/health comes from `gt bridge dispatch config|status|health`.
   - Thread state for proposal/report chains comes from versioned bridge files or dispatcher/TAFE state, not a compatibility view.
   - Any helper or automation that requires the retired index is defective and must be fixed or retired.
6. Preserve only clearly historical/audit references outside this target set.

## Specification-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
rg -n "bridge/INDEX\.md|bridge\\INDEX\.md|reads live bridge/INDEX|Read bridge/INDEX|sole authoritative|compatibility view|generated compatibility|single_harness_bridge_automation|Guarding bridge/INDEX" scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py scripts\single_harness_bridge_automation.py .claude\settings.json .codex\hooks.json config\agent-control\system-interface-map.toml .claude\skills\bridge\SKILL.md .codex\skills\bridge\SKILL.md .claude\skills\bridge-config\SKILL.md .codex\skills\bridge-config\SKILL.md platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_single_harness_bridge_automation.py platform_tests\scripts\test_single_harness_dispatcher_task_installer.py
python -m pytest platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_single_harness_bridge_automation.py platform_tests\scripts\test_single_harness_dispatcher_task_installer.py platform_tests\scripts\test_slice_3_hook_registrations.py -q --tb=short
python -m ruff check scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py scripts\single_harness_bridge_automation.py scripts\bridge_work_intent_registry.py platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_single_harness_bridge_automation.py platform_tests\scripts\test_single_harness_dispatcher_task_installer.py platform_tests\scripts\test_slice_3_hook_registrations.py
python -m ruff format --check scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py scripts\single_harness_bridge_automation.py scripts\bridge_work_intent_registry.py platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_single_harness_bridge_automation.py platform_tests\scripts\test_single_harness_dispatcher_task_installer.py platform_tests\scripts\test_slice_3_hook_registrations.py
gt bridge dispatch config
gt bridge dispatch status --json
gt bridge dispatch health --json
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- No active target in this proposal instructs agents or code to read, write, require, or guard the retired index. Historical mentions must be explicitly marked as historical.
- Work-intent and automation tests pass using versioned bridge files or dispatcher/TAFE state.
- Hook registration tests confirm no active hook invokes an index-era bridge automation path.
- Ruff checks pass.
- Dispatcher config/status/health remain PASS and report the eligible LO targets.

## Risks

- The trigger and automation scripts are large and may still have index assumptions in prompt construction, diagnostics, dedupe signatures, scheduled-task arguments, or tests. The implementation must avoid a superficial docstring-only fix.
- Existing dispatch state may contain historical index-derived signatures. The implementation should treat stale state as diagnostic history, not live authority.
- Removing old single-harness automation hooks without replacement could temporarily reduce automatic surfacing of interactive/AUQ-heavy work. The implementation should either route that behavior through dispatcher/TAFE state or explicitly preserve it as a separate follow-up if it cannot be safely migrated in this slice.
- LO review quality is still uneven: Antigravity wrote a terminal VERIFIED for the bootstrap but Ollama correctly found that verdict too generic. Verification for this proposal should require focused evidence and may need a headless Codex LO fallback.

## Rollback

Revert changes in the target paths. Do not recreate `bridge/INDEX.md`; a
rollback that depends on that file violates the owner directive and would mask
the defect.
