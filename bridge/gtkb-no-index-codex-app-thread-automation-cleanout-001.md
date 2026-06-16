NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Codex App-Thread Automation Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-codex-app-thread-automation-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["config/agent-control/system-interface-map.toml", ".claude/rules/bridge-essential.md", "scripts/session_self_initialization.py", "scripts/cross_harness_bridge_trigger.py", ".codex/gtkb-hooks/last-wi-id-collision-skipped.json", ".codex/gtkb-hooks/last-bridge-audit-skipped.json", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_system_interface_map.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "bridge/gtkb-no-index-codex-app-thread-automation-cleanout-*.md"]

implementation_scope: codex_app_thread_automation_no_index_cleanup, external_automation_inventory_quarantine, root_boundary_enforcement
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The owner-provided Codex LO startup screenshot mentioned "automation memory"
and showed Codex honoring an automation rule that still required
`bridge/INDEX.md` as queue authority. A local root-only sweep found the likely
source: generated Codex hook-cache files inside `E:\GT-KB` contain a command
that writes and reads `$env:CODEX_HOME\automations\keep-working-lo\memory.md`.
That external memory is outside the GT-KB root and must not be treated as a
live GT-KB dependency or authority.

Representative evidence:

- `.codex/gtkb-hooks/last-wi-id-collision-skipped.json` and `.codex/gtkb-hooks/last-bridge-audit-skipped.json` contain a skipped command that creates `$env:CODEX_HOME\automations\keep-working-lo\memory.md`, appends "Loaded automation memory and relevant GT-KB bridge/backlog/dispatch rules", and reads its tail back into the Codex session.
- The same cached command says `bridge/INDEX.md` is absent, that legacy scan helpers fail, and that visible no-index proposals are not safe Codex-A LO work because Codex A is the Prime author.
- `config/agent-control/system-interface-map.toml` inventories `monitor-gt-kb-bridge-codex-thread` and `gt-kb-bridge-monitor-codex-thread` as external Codex app-thread automations whose authoritative source "lives in Codex CLI installation state, not in E:/GT-KB"; both entries still describe live `bridge/INDEX.md` scans.
- The root-boundary guard blocked a broad search containing the literal external automation path, confirming that out-of-root automation state is not a safe live inspection surface for GT-KB work.

This proposal does not mutate the external Codex app automation itself. It
cleans GT-KB-owned instructions, inventory, generated caches, and tests so
external Codex app-thread automation is not presented to agents as a live bridge
authority. If the external automation still exists and must be disabled, that
requires a separate owner-controlled Codex app automation action or an approved
automation-management tool path.

## Prior Deliberations

- `DELIB-1522` - Codex LO NO-GO on startup trigger awareness: found that Codex-side automations needed explicit owner disposition before rule-level ratification; warned not to convert observed unauthorized automations into durable rule authority.
- `DELIB-0648` - Historical Codex bridge automation repair: documents the earlier scheduled-task/index-scan lineage and its risks.
- `DELIB-20263438` - Owner requirement: corrected bridge-dispatch architecture and rule-based dispatch.
- `DELIB-20263447` - Dispatcher/Bridge CLI-first operation benchmark.
- `bridge/gtkb-no-index-startup-control-cleanout-002.md` - Sibling proposal capturing the Codex LO screenshot and generated startup-payload contradiction.
- `bridge/gtkb-no-index-dispatcher-trigger-cleanout-002.md` - Sibling proposal covering in-repo dispatcher/automation hook registrations.
- `bridge/gtkb-cli-mediated-agent-mutation-boundary-002.md` - Related design constraint: skills should sit over CLI-backed mutation surfaces where practical, and agents should not mutate GT-KB artifacts through raw ad hoc paths.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge proposals, implementation reports, and verification verdicts remain the governed work lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation artifacts and live dependencies must honor the project root boundary; no live GT-KB dependency may be required from outside `E:\GT-KB`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and machine-readable target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links the governing requirements for the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification will include spec-to-test mapping and observed commands.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health CLI surfaces are the operational dispatch authority.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - routing decisions must be based on role, subject, and activity rules, not external prompt memory.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness prompt and hook surfaces must not preserve conflicting behavior for Codex.

## Requirement Sufficiency

Existing requirements are sufficient for the in-repo cleanup. Mike's directives
say `bridge/INDEX.md` must not exist, backward compatibility should not be
preserved, every break caused by its absence is a defect, and mutating GT-KB
operations should run through governed skills or CLI surfaces.

External Codex app automation disposition may require owner action if the
automation still exists outside `E:\GT-KB`. The implementation for this proposal
must not read, depend on, or mutate `$CODEX_HOME` automation files as GT-KB
authority.

## Proposed Implementation

1. Update `config/agent-control/system-interface-map.toml` to stop describing Codex app-thread automations as live bridge monitors that scan `bridge/INDEX.md`.
2. Reclassify any remaining Codex app-thread automation entries as historical, prohibited, or pending external owner disposition; do not present them as current bridge authorities.
3. Update `.claude/rules/bridge-essential.md` and startup text so agents are not told that Codex app-thread automation is a valid Axis 2 bridge authority in the no-index dispatcher model.
4. Clear or regenerate in-root Codex hook-cache files that contain out-of-root automation-memory commands, using the governed hook/cache generation path rather than hand-editing persistent external state.
5. Add tests that fail if generated startup/context payloads instruct Codex to load or append `$CODEX_HOME` automation memory for GT-KB bridge decisions.
6. If a real external Codex app automation still exists, surface a separate owner action or approved automation-management proposal to disable it. This proposal's implementation may record the blocker but must not treat out-of-root state as a GT-KB artifact.

## Specification-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
rg -n "CODEX_HOME|automation memory|keep-working-lo|monitor-gt-kb-bridge|gt-kb-bridge-monitor|Codex app thread automation|bridge/INDEX\.md" config\agent-control .claude\rules\bridge-essential.md scripts\session_self_initialization.py scripts\cross_harness_bridge_trigger.py .codex\gtkb-hooks platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_system_interface_map.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
python -m pytest platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_system_interface_map.py platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts\session_self_initialization.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_system_interface_map.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
python -m ruff format --check scripts\session_self_initialization.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_system_interface_map.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
gt bridge dispatch config
gt bridge dispatch status --json
gt bridge dispatch health --json
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- In-repo startup/control/skill surfaces no longer instruct agents to use `$CODEX_HOME` automation memory for GT-KB bridge decisions.
- Codex app-thread automation entries are either explicitly historical/prohibited/pending owner disposition or removed from active operational guidance.
- Any remaining `bridge/INDEX.md` references in this target set are explicit historical references or negative tests.
- Dispatcher config/status/health remain the current operational surfaces.

## Risks

- The actual Codex app automation configuration may live outside `E:\GT-KB` and may not be inspectable or mutable through repo-local tools. This is a blocker for claiming the external automation is disabled, but not for removing GT-KB's active reliance on it.
- Deleting or clearing generated hook-cache files without fixing their generator would be a temporary cosmetic fix. The implementation must identify the source hook/generator path or explicitly document why a cache is safe to remove.
- If Codex app automation is still waking sessions, it may continue to confuse agents until disabled through the Codex app or an approved automation-management surface.

## Rollback

Revert changes in the target paths. Do not restore `bridge/INDEX.md` or
re-ratify external Codex app-thread automation as live bridge authority without
explicit owner disposition.
