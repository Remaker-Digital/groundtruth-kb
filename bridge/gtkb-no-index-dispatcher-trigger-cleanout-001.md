NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Dispatcher Trigger Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-dispatcher-trigger-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_work_intent_auto_extend.py", ".claude/skills/bridge/SKILL.md", ".codex/skills/bridge/SKILL.md", ".claude/skills/bridge-config/SKILL.md", ".codex/skills/bridge-config/SKILL.md", "bridge/gtkb-no-index-dispatcher-trigger-cleanout-*.md"]

implementation_scope: dispatcher_trigger_no_index_cleanup, skill_instruction_cleanup, work_intent_fixture_cleanup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The bootstrap repair in `bridge/gtkb-no-index-implementation-authorization-bootstrap-003.md` restored implementation-start authorization without the retired bridge index. The next active defect is that dispatch/runtime surfaces and work-intent tests still preserve index-only language or fixtures:

- `scripts/cross_harness_bridge_trigger.py` still advertises and reads live `bridge/INDEX.md`.
- `scripts/single_harness_bridge_dispatcher.py` still advertises and prompts workers to read live `bridge/INDEX.md`.
- `platform_tests/scripts/test_bridge_work_intent_registry.py`, `test_work_intent_role_eligibility.py`, and `test_work_intent_auto_extend.py` still build `bridge/INDEX.md` fixtures instead of status-bearing versioned bridge files.
- `.claude/skills/bridge/SKILL.md` and `.codex/skills/bridge/SKILL.md` still contain compatibility-view instructions that tell agents to update/read the retired index.
- The `bridge-config` skill correctly tells agents not to summarize the retired index, but still calls it a deprecated generated compatibility view; that wording must be hardened to say the file must not exist and that breaks are defects.

This proposal covers the next implementation slice only. It does not attempt to clean every remaining historical/audit fixture in the repo.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim; the prior broad cleanout GO could not mint a packet, so this compliant proposal is required.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge proposals, implementation reports, and verification verdicts remain the governed work lifecycle.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and machine-readable target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links the governing requirements for the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification will include spec-to-test mapping and observed commands.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the dispatcher/status/health CLI and harness registry are the dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - routing decisions must be based on role, subject, and activity rules, independent of a retired index file.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped cleanup. Mike's directives are explicit: do not preserve backward compatibility for the retired index; every break caused by its absence is a defect to fix; and agents must use the dispatcher CLI/skills and versioned bridge files rather than `bridge/INDEX.md`.

## Proposed Implementation

1. Replace trigger/dispatcher bridge-state discovery with versioned bridge-file scanning or the existing dispatcher/TAFE state surfaces. Do not recreate or require `bridge/INDEX.md`.
2. Update trigger and dispatcher help text, worker prompts, diagnostics, and health evidence so they describe the no-index dispatcher model.
3. Rewrite focused work-intent tests to create status-bearing bridge files (`bridge/<slug>-NNN.md`) instead of index-only fixtures.
4. Harden the bridge and bridge-config skills so active instructions say:
   - `bridge/INDEX.md` must not exist.
   - Dispatcher topology/health comes from `gt bridge dispatch config|status|health`.
   - Thread state for proposal/report chains comes from versioned bridge files or dispatcher/TAFE state, not a compatibility view.
   - Any helper that requires the retired index is defective and must be fixed or retired.
5. Preserve only clearly historical/audit references outside this target set.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
rg -n "bridge/INDEX\\.md|bridge\\\\INDEX\\.md|reads live bridge/INDEX|Read bridge/INDEX|sole authoritative|compatibility view|generated compatibility" scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py .claude\skills\bridge\SKILL.md .codex\skills\bridge\SKILL.md .claude\skills\bridge-config\SKILL.md .codex\skills\bridge-config\SKILL.md platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py
python -m pytest platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py platform_tests\scripts\test_bridge_claim_cli.py -q --tb=short
python -m ruff check scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py scripts\bridge_work_intent_registry.py platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py
python -m ruff format --check scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py scripts\bridge_work_intent_registry.py platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_work_intent_auto_extend.py
gt bridge dispatch status --json
gt bridge dispatch health --json
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- No active target in this proposal instructs agents or code to read/write/require the retired index. Historical mentions must be explicitly marked as historical, not compatibility.
- Work-intent and claim tests pass using versioned bridge files.
- Ruff checks pass.
- Dispatcher config/status/health remain PASS and report the eligible LO targets.

## Risks

- The trigger scripts are large and may still have index assumptions in prompt construction, diagnostics, dedupe signatures, or tests. The implementation must avoid a superficial docstring-only fix.
- Existing dispatch state may contain historical index-derived signatures. The implementation should treat stale state as diagnostic history, not live authority.
- LO review quality is still uneven: Antigravity wrote a terminal VERIFIED for the bootstrap but Ollama correctly found that verdict too generic. Verification for this proposal should prefer Ollama or require a focused Antigravity prompt with explicit evidence requirements.

## Rollback

Revert changes in the target paths. Do not recreate `bridge/INDEX.md`; a rollback that depends on that file violates the owner directive and would mask the defect.
