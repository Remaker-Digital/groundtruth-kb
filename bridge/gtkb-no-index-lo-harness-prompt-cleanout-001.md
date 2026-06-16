NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index LO Harness Prompt Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-lo-harness-prompt-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_dispatch.py", "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_routing_config.py", "platform_tests/scripts/test_openrouter_routing_deepseek.py", "bridge/gtkb-no-index-lo-harness-prompt-cleanout-*.md"]

implementation_scope: lo_harness_prompt_no_index_cleanup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

During the no-index bridge cleanup sweep, the configured Loyal Opposition harness shims were found to contain active bridge-review system-prompt instructions that still command Ollama and OpenRouter to read and update `bridge/INDEX.md`. This directly contradicts Mike's directive that `bridge/INDEX.md` must not exist and that any break caused by its deletion is a defect to fix.

This proposal covers the LO harness prompt and guard-description cleanup only. It is separate from `bridge/gtkb-no-index-dispatcher-trigger-cleanout-001.md`, which targets dispatcher/trigger scripts, work-intent fixtures, and bridge skills.

## Prior Deliberations

- `DELIB-20263438` - Owner requirement: corrected bridge-dispatch architecture; role assignment and dispatchability are orthogonal, and dispatch is rule-based over roles, subjects, and activities with availability/cost/quality selection.
- `DELIB-20261121` - Loyal Opposition insight report on bridge and multi-harness dispatch analysis; relevant because this proposal repairs the prompt layer that makes LO reviews trustworthy.
- `bridge/gtkb-no-index-implementation-authorization-bootstrap-003.md` - Bootstrap implementation report proving the implementation-start path can work without `bridge/INDEX.md`.
- `bridge/gtkb-no-index-dispatcher-trigger-cleanout-001.md` - Adjacent proposal covering dispatcher trigger and skill cleanup, discovered during the same sweep.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge proposals, reports, and verdicts remain the governed lifecycle.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and machine-readable target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links the governing requirements for the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include spec-to-test mapping and observed command evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health and harness registry surfaces are the dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch routing decisions are based on role, subject, and activity rules, not the retired index.

## Requirement Sufficiency

Existing requirements are sufficient. Mike's explicit directive is that `bridge/INDEX.md` must not exist, no backward compatibility should be preserved, and every failure caused by the deleted index is a defect. The configured LO harness prompts are active implementation surfaces, not historical archive text, so they must stop instructing agents to use the deleted index.

## Pre-Filing Self-Check

The current preflight tooling still contains a first-file catch-22 for new bridge threads:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-lo-harness-prompt-cleanout
ERR_NO_INDEX_ENTRY: no entry for bridge_id='gtkb-no-index-lo-harness-prompt-cleanout' in E:\GT-KB\bridge\INDEX.md

python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-no-index-lo-harness-prompt-cleanout
Operative file: (not found - no INDEX entry and no matching `bridge/gtkb-no-index-lo-harness-prompt-cleanout-NNN.md`)
```

This is recorded as additional evidence that legacy preflight discovery still depends on the retired index before the first versioned bridge file exists. Loyal Opposition should review the proposal content and may rerun preflights after this file exists.

## Proposed Implementation

1. Update `scripts/ollama_harness.py` and `scripts/openrouter_harness.py` bridge-review system prompts so LO agents:
   - read the full versioned bridge-file chain for the target document;
   - use `gt bridge dispatch config|status|health` for dispatcher topology and health;
   - do not read, update, or expect `bridge/INDEX.md`;
   - treat any helper requiring `bridge/INDEX.md` as defective and report the defect instead of following stale instructions.
2. Update tool descriptions and guard text that mention `bridge/INDEX.md` so they say bridge artifact mutations are guarded and the retired index must not be created or modified.
3. Update harness tests so prompt assertions check for versioned bridge-file and dispatcher CLI instructions, not index instructions.
4. Keep any test that mentions `bridge/INDEX.md` only when it is explicitly asserting denial of attempts to create or mutate the retired file.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
rg -n "Read bridge/INDEX|read bridge/INDEX|update.*bridge/INDEX|bridge/INDEX.md" scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py
python -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py -q --tb=short
python -m ruff check scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py
python -m ruff format --check scripts\ollama_harness.py scripts\openrouter_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch_prompt_restructure.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_openrouter_routing_deepseek.py
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- Active LO harness prompts no longer instruct reviewers to read, update, or expect the retired index.
- Remaining `bridge/INDEX.md` mentions in the target tests are explicit denial/historical-retirement assertions only.
- Focused tests and ruff checks pass.

## Risks

- If LO harness prompts remain stale, Ollama and OpenRouter may continue producing blocked, thin, or factually confused reviews even when dispatcher eligibility looks healthy.
- Updating prompts without tests would invite recurrence because this prompt text is not visible through normal CLI health output.
- This slice does not repair Antigravity review quality; it only removes a deterministic source of confusion from Ollama and OpenRouter.

## Rollback

Revert changes in the target files. Do not recreate `bridge/INDEX.md`; any rollback that depends on that file violates the owner directive and masks the defect.
