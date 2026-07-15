ADVISORY
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6381-9939-7500-abd6-c73d192c8c35
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner-directed bridge ADVISORY filing

bridge_kind: governance_advisory
Document: gtkb-resource-registry-pointer-drift-advisory
Version: 001
Author: Owner-directed Advisory Proposal by Prime Builder (Codex, harness A)
Date: 2026-07-15 UTC
Mode: advisory proposal
Severity: P1
Priority: P1

# Resource Registry Pointer Drift Advisory Proposal

## Source

- Owner direction in the active 2026-07-15 Prime Builder session to file this issue as a proper Advisory Proposal.
- Governed predecessor `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` and its latest VERIFIED bridge artifact, `bridge/gtkb-resource-reference-disambiguation-001-004.md`.
- Current focused test and CLI-backed state checks recorded in the claim below.

## Claim

The missing `.claude/rules/project-resource-aliases.toml` pointer is a live regression in a previously verified resource-reference design. The canonical registry remains `config/agent-control/project-resource-aliases.toml`, but the current resolver and focused tests require the non-competing pointer file. Its absence breaks deterministic resource-alias resolution and clean-checkout consistency.

This is not a request to recreate a second registry. The intended pointer contains only delegation metadata identifying the canonical registry.

Fresh checks on 2026-07-15 found:

- `Test-Path .claude/rules/project-resource-aliases.toml` returned `False`.
- `python -m pytest platform_tests/scripts/test_project_resource_aliases.py -q --tb=short` returned 2 failed and 8 passed.
- The failures are `test_governed_registry_is_valid_and_pointer_is_not_competing_registry` and `test_cli_resolves_json_alias`; both report the pointer file as missing.
- `gt bridge show gtkb-resource-reference-disambiguation-001 --json` reports the predecessor thread latest `VERIFIED` at `bridge/gtkb-resource-reference-disambiguation-001-004.md`.
- MemBase row `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` is resolved and describes the verified design as retaining the `.claude/rules/` file as a pointer to the governed registry.

Risk: current tests and CLI resolution are red even though the predecessor lifecycle is terminal. Without a new regression carrier, future sessions can mistake the resolved predecessor for current health.

## Owner Decision Needed

No additional owner decision is needed to file this ADVISORY; the owner expressly requested this Advisory Proposal.

A downstream implementation decision remains unresolved: choose Option A (tracked static pointer) or Option B (generated pointer plus contract change). The advisory recommends Option A because it restores the already-verified design with the smallest behavioral change.

## Recommended Prime Action

Classify this advisory as `adapt`.

1. Resolve the original implementation choice before protected edits:
   - Option A, recommended: restore and track the static pointer, including the required `.gitignore` negation.
   - Option B: replace the pointer requirement with deterministic generation, change the resolver/test contract, and prove race-free startup behavior.
2. Create a new regression work item or clearly linked successor instead of rewriting the verified predecessor history.
3. Route any requirement change through specification intake if Option B changes the canonical pointer contract.
4. File a normal `NEW` implementation proposal with exact target paths, current specifications, and focused verification.
5. Preserve `config/agent-control/project-resource-aliases.toml` as the sole registry authority; the pointer must remain delegation metadata only.

Candidate proposal-time paths are `.claude/rules/project-resource-aliases.toml`, `.gitignore`, `platform_tests/scripts/test_project_resource_aliases.py`, and, only for Option B, `scripts/resolve_project_resource.py`. These are not authorized edits.

## Classification Slot

Owner-directed governance advisory. Recommended disposition: `adapt` into a new regression work item and normal implementation proposal after the owner selects the pointer mechanism. This ADVISORY remains non-dispatchable and is not implementation approval.

## Prior Deliberations

- `DELIB-20260715-ADVISORY-PROPOSAL-PRIMARY-LO-INITIATION-MECHANISM`
- `DELIB-20260671` - platform source-of-truth consolidation and registry direction.
- No direct deliberation was found that supersedes the predecessor's static delegation-pointer design or resolves the Option A versus Option B question.

## Related Governed Artifacts

- `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` - resolved predecessor work item.
- `bridge/gtkb-resource-reference-disambiguation-001-004.md` - predecessor latest VERIFIED.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Duplicate And Supersession Check

No bridge thread named `gtkb-resource-registry-pointer-drift-advisory` existed before filing. The verified `gtkb-resource-reference-disambiguation-001` thread is related but not a duplicate: it established the design whose required pointer is now missing.

## Non-Approval Statement

This ADVISORY is a non-dispatchable bridge artifact and future-work initiation carrier. It is not a GO verdict, implementation proposal, project authorization, work-intent claim, implementation-start packet, or permission to modify protected files. Downstream implementation requires normal advisory disposition, requirement sufficiency, bridge proposal, independent Loyal Opposition GO, work-intent, implementation-start, report, and verification.
