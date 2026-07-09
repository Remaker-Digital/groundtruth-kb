NEW

# Implementation Proposal - Antigravity Supported Skill-Target Parity Alignment (+ WI-4841 completion)

bridge_kind: prime_proposal
Document: gtkb-antigravity-supported-skill-target-parity-alignment
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4841

target_paths: ["platform_tests/skills/test_advisory_disposition_skill.py", "platform_tests/skills/test_skill_governance_lifecycle_skill.py", "platform_tests/skills/test_formal_artifact_packet_helper_skill.py", "platform_tests/skills/test_managed_skill_adoption_review_skill.py", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".codex/skills/managed-skill-adoption-review/SKILL.md", ".agent/skills/managed-skill-adoption-review/SKILL.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fe7b8aef-1645-4c20-87b0-155833b34351
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

## Summary

Per owner decision `DELIB-202665926` (antigravity is a supported managed-skill
projection target), align the stale `antigravity = "unsupported"` parity
assertions in the PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT skill tests to
`antigravity = "adapter"`, and complete WI-4841 (managed-skill-adoption-review)
by adding its capability registry entry and focused parity test consistent with
that decision.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202665926` (this session's owner AUQ)
ratifies antigravity support and is the typed parity waiver the WI-4839..4842
proposals contemplated ("no direct skill adapter target ... requires a separate
target-path-covered proposal or typed parity waiver"). No new requirement
capture is needed; this change aligns tests and registry to the ratified
platform behavior and completes the WI-4841 scaffold.

## Problem / Context

The Codex-style adapter generator projects managed skills to antigravity
(`.agent/skills/*` adapters plus registry `[capabilities.antigravity] status =
"adapter"`), reflecting antigravity (harness C) now being an active dispatchable
Loyal Opposition harness. Three skill parity tests still assert
`antigravity["status"] == "unsupported"`, from pre-antigravity-harness proposal
language, and now FAIL against the current registry:

- `test_advisory_disposition_skill.py` — regressing the previously VERIFIED WI-4840.
- `test_skill_governance_lifecycle_skill.py`.
- `test_formal_artifact_packet_helper_skill.py` (its 4-harness assertion loop).

WI-4841 (managed-skill-adoption-review) additionally lacks a capability registry
entry and a focused parity test; its `.claude` source and generated adapters
already exist.

## Proposed Scope

1. Align the antigravity parity assertions in the three named tests to
   `antigravity = "adapter"`, consistent with the actual registry matrix and
   `DELIB-202665926`. Where `cursor`/`ollama`/`openrouter` are asserted but not
   enumerated in a skill's registry entry, align the assertion to the registry's
   actual enumerated matrix (antigravity-only scope per `DELIB-202665926`;
   `cursor` remains `unsupported` where enumerated).
2. Complete WI-4841: add the `skill.managed-skill-adoption-review` capability
   registry entry via the canonical adapter generator
   (`scripts/generate_codex_skill_adapters.py --update-registry`), yielding
   claude=native, codex=adapter, antigravity=adapter, cursor=unsupported; and add
   `platform_tests/skills/test_managed_skill_adoption_review_skill.py` modeled on
   the sibling skill tests, asserting the antigravity=adapter matrix.
3. Track the managed-skill-adoption-review generated adapters (`.codex`, `.agent`)
   and the manifest entry (previously blocked by the now-resolved Codex `.codex`
   write boundary; generated from a write-capable harness).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target-path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - antigravity is now a supported parity target per `DELIB-202665926`.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - skill registry/adapter/catalog invariants.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `GOV-STANDING-BACKLOG-001` - WI linkage preserved.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance linkage.

## Owner Decisions / Input

- `DELIB-202665926` (owner AUQ, 2026-07-09): antigravity is a supported managed-skill projection target; align stale `antigravity = "unsupported"` tests to `antigravity = "adapter"`; serves as the typed parity waiver for WI-4839..4842.
- `PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842`: active project authorization (no expiry) covering WI-4839, WI-4840, WI-4841, WI-4842 with mutation classes source + test.

## Prior Deliberations

- `DELIB-202665926` - owner ratification; the authority for this proposal.
- `DELIB-20266596` - owner AUQ approval for bounded WI-4839..4842 skill-scaffold implementation.
- `DELIB-20265883` - owner-directed creation of PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-014.md` - prior NO-GO (blocked on the Codex `.codex` write boundary, since resolved). This umbrella supersedes that thread's remaining WI-4841 scope; the scaffold thread is to be WITHDRAWN after this thread VERIFIES.
- `bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-021.md` - prior NO-GO; its stale antigravity test assertion is aligned here.
- `bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-010.md` - VERIFIED WI-4840 whose parity test is currently regressed by the antigravity registry state and is un-regressed here.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_advisory_disposition_skill.py platform_tests/skills/test_skill_governance_lifecycle_skill.py platform_tests/skills/test_formal_artifact_packet_helper_skill.py platform_tests/skills/test_managed_skill_adoption_review_skill.py -q` -> all pass (un-regresses WI-4840). |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check` -> PASS; registry matrix consistent with `DELIB-202665926`. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_skill_catalog_contract.py -q` -> pass. |
| Code quality | `ruff check` + `ruff format --check` on the four changed/added test files. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability + clause preflights pass (`missing_required_specs: []`; 0 blocking gaps). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root under `E:/GT-KB`. |

## Acceptance Criteria

- The three regressed skill parity tests pass with `antigravity = "adapter"` assertions (WI-4840 un-regressed).
- WI-4841 managed-skill-adoption-review has a capability registry entry and a focused parity test, both consistent with the antigravity=adapter matrix.
- `generate_codex_skill_adapters.py --check` PASS; catalog-contract test pass.
- No skill outside the PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT cluster is modified.

## Cross-Harness Disposition

Per `DELIB-202665926`, antigravity (harness C, active Loyal Opposition) IS a
supported managed-skill adapter target. Claude = native canonical source;
Codex and Antigravity = generated adapters; Cursor/Ollama/OpenRouter remain
`unsupported` (per existing registry enumeration) until separately decided.

## Risks / Rollback

Low. Changes are parity-test-assertion alignment plus one new skill registry
entry and focused test, bounded to the skill-activation-enforcement cluster.
Rollback is a revert of the four test files, the registry entry, and the
managed-skill-adoption-review generated adapters/manifest entry; bridge and
project-authorization records are append-only.

## Recommended Commit Type

fix - aligns regressed parity tests to the ratified platform reality and completes the WI-4841 scaffold; no new user-facing capability beyond the scaffolded review skill.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
