NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T04-55-00Z-prime-builder-A-keep-working
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Hygiene PB

# LLM Harness Verdict Prior-Deliberations Seeding

bridge_kind: prime_proposal
Document: gtkb-llm-harness-verdict-prior-deliberations-seeding
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4648

target_paths: ["scripts/openrouter_harness.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py"]
implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4648 is the named follow-on from WI-4639. WI-4639 added Prior Deliberations seeding to interactive verdict-authoring paths and is now latest `VERIFIED` at `bridge/gtkb-verdict-prior-deliberations-seeding-004.md`, but the LLM-as-Loyal-Opposition harness prompts in `scripts/openrouter_harness.py` and `scripts/ollama_harness.py` still only tell the model to write GO, NO-GO, or VERIFIED verdict files.

This proposal asks for a narrow prompt/test update: both LLM harness system prompts must instruct the reviewer model to seed verdict drafts by running the shared verify helper before writing any bridge verdict:

```text
python .claude/skills/verify/helpers/write_verdict.py --slug <document-slug> --body-file <draft-body-file>
```

The helper writes the seeded verdict body to stdout and records verify-side prepopulation telemetry under `.gtkb-state/bridge-verify-helper/`. The model must review and prune helper suggestions before writing the next numbered bridge file. If the helper cannot run, the harness prompt must tell the model to preserve explicit failure evidence in the verdict rather than silently writing an unseeded verdict.

## Current Live State Snapshot

Current WI-4648 backlog state, from `gt backlog list --id WI-4648 --json`:

- `resolution_status: open`
- `stage: backlogged`
- `project_name: PROJECT-GTKB-MAY29-HYGIENE`
- title: `Seed Prior Deliberations into LLM-harness-authored verdict files (.lo-verdict.md)`

Current parent thread state, from `gt bridge show gtkb-verdict-prior-deliberations-seeding --json`:

- latest status: `VERIFIED`
- latest path: `bridge/gtkb-verdict-prior-deliberations-seeding-004.md`
- version chain: `001 NEW`, `002 GO`, `004 VERIFIED`

Current duplicate check:

- `gt bridge threads --wi WI-4648 --json` returned zero threads.
- The target source/test files named above have no current dirty worktree diff.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The implementation changes bridge verdict-authoring behavior and must stay inside the governed file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites the governing specifications for source/test changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries project authorization, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must prove the prompt behavior from the linked specifications and owner decision.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active May29 Hygiene authorization allows PB to propose implementation for unimplemented project work items.
- `GOV-STANDING-BACKLOG-001` - WI-4648 is an open governed backlog item and must remain visible through bridge/report evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Verdict files are durable review artifacts and should carry deliberation context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The prompt, helper, tests, bridge proposal, report, and backlog row should form a consistent artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This proposal advances the WI-4648 lifecycle from captured follow-on to reviewable implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation/test targets are in-root GT-KB paths.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - The harness prompt should direct models to read live bridge chains and produce verdict evidence from live state.
- `DELIB-20260618-WI4639-SCOPE-ALL-INTERACTIVE-VERDICT-PATHS` - Owner decision explicitly deferred the LLM-harness `.lo-verdict.md` path to WI-4648.

## Prior Deliberations

- `DELIB-20260618-WI4639-SCOPE-ALL-INTERACTIVE-VERDICT-PATHS` - Owner decision: WI-4639 covers all interactive verdict paths; the LLM-harness `.lo-verdict.md` path is deferred to WI-4648.
- `DELIB-20264415` - Ollama adapter-generation review precedent confirming LLM/adapter bridge work must cite Prior Deliberations and stay in child bridge scope.
- `DELIB-20264459` - Ollama harness review precedent requiring machine-readable target paths for `scripts/ollama_harness.py` and focused harness tests.
- `DELIB-20264382` - Ollama Phase 1 verification precedent preserving bridge/harness scope boundaries and follow-on backlog visibility.

Deliberation search executed before filing:

```text
gt deliberations search "WI-4648 LLM harness Prior Deliberations verdict seeding openrouter ollama" --limit 10 --json
```


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20260618-WI4639-SCOPE-ALL-INTERACTIVE-VERDICT-PATHS` — seed=search; owner_conversation; Owner decision: WI-4639 covers ALL interactive verdict-authoring paths
- DA: `DELIB-20265270` — seed=search; bridge_thread; Loyal Opposition Verdict — Verdict-File Prior-Deliberations Seeding Across Inter
- DA: `DELIB-1475` — seed=search; bridge_thread; Loyal Opposition Review - Deliberation Archive Harvest Catch-Up REVISED-1
- DA: `DELIB-20263983` — seed=search; bridge_thread; Loyal Opposition Verification - Deliberation Archive Harvest Catch-Up
- DA: `DELIB-1506` — seed=search; bridge_thread; Scaffold Upgrade Tier A - Loyal Opposition REVISED-2 Review

## Requirement Sufficiency

Existing requirements sufficient.

The owner decision and WI-4648 backlog row define the remaining LLM-harness path clearly enough for a bounded implementation. The implementation should not redesign the prior-deliberations helper or mutate bridge writer semantics; it should only teach the two LLM harness prompts to invoke the already-verified helper before writing verdict artifacts and add tests proving the prompt requirements are present.

## Implementation Scope

Approved source changes:

- Update `scripts/ollama_harness.py::build_system_prompt` for Loyal Opposition bridge skills.
- Update `scripts/openrouter_harness.py::build_system_prompt` for Loyal Opposition bridge skills.

Required prompt behavior:

- Tell the model to create or assemble a verdict draft body with the required status token and sections before final Write/Edit.
- Tell the model to run `python .claude/skills/verify/helpers/write_verdict.py --slug <document-slug> --body-file <draft-body-file>`.
- Tell the model to review and prune seeded Prior Deliberations before writing the next numbered bridge verdict file.
- Tell the model that helper failure is evidence to report, not permission to silently omit Prior Deliberations.
- Preserve existing claim-first, no-index bridge-chain, preflight, guard, author-metadata, root-boundary, and retired-index instructions.

Approved test changes:

- Add or update focused prompt assertions for Ollama in `platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py` and/or `platform_tests/scripts/test_ollama_harness.py`.
- Add or update focused prompt assertions for OpenRouter in `platform_tests/scripts/test_openrouter_harness.py`.

Out of scope:

- No changes to `.claude/skills/verify/helpers/write_verdict.py` or `groundtruth_kb.bridge.prior_deliberations`.
- No new bridge writer runtime.
- No changes to dispatch routing, model selection, credentials, role registry, harness-state projections, bridge file status semantics, or retired bridge index behavior.
- No attempt to backfill existing historical verdict files.

## Specification-Derived Verification

| Specification | Verification Evidence Required |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show implementation started only after GO and changed only scoped source/test files. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Re-run bridge applicability preflight with no missing required specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report carries PAUTH, project, and WI-4648 metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests prove both LLM harness prompts require the verify helper and preserve existing guard/claim/preflight instructions. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Re-query active May29 Hygiene PAUTH before mutation. |
| `GOV-STANDING-BACKLOG-001` | Report shows WI-4648 remains visible and links to this bridge thread. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Prompt language preserves Prior Deliberations in future verdict artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Tests and report show the prompt behavior routes future verdict context through the shared helper. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Report records the follow-on lifecycle transition and evidence needed for closure. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and clause preflights confirm all changes are under `E:\GT-KB`. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Prompt text continues to require reading the live bridge chain before verdict authoring. |
| `DELIB-20260618-WI4639-SCOPE-ALL-INTERACTIVE-VERDICT-PATHS` | Implementation explicitly covers the deferred LLM-harness verdict path without reopening WI-4639 scope. |

## Verification Commands

Expected focused checks:

```text
python -m pytest platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short
python -m ruff check scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
python -m ruff format --check scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-llm-harness-verdict-prior-deliberations-seeding
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-llm-harness-verdict-prior-deliberations-seeding
```

## Acceptance Criteria

- Ollama and OpenRouter bridge-review/verification system prompts both instruct the model to run the shared verify helper against a draft verdict before writing the final bridge verdict file.
- Prompt tests fail if either harness drops helper invocation, Prior Deliberations review/pruning, claim-first ordering, live bridge-chain reading, or preflight instructions.
- No helper, routing, credential, dispatch, harness registry, bridge runtime, or historical bridge file backfill changes.
