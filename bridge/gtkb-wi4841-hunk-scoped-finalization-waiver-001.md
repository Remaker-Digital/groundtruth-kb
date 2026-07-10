NEW

# WI-4841 Hunk-Scoped Finalization Under Owner Waiver

bridge_kind: prime_proposal
Document: gtkb-wi4841-hunk-scoped-finalization-waiver
Version: 001
Date: 2026-07-10 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4841

target_paths: [".claude/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/managed-skill-adoption-review/SKILL.md", ".agent/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_managed_skill_adoption_review_skill.py"]

implementation_scope: source, tests, repository-state finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4841 is independently verified as implementation-quality, but its terminal path is blocked by foreign entries and unrelated source-hash refreshes interleaved with the WI-4841 Antigravity manifest object. This proposal uses the owner-recorded narrow waiver to finalize only WI-4841-owned artifacts without changing, staging, or attributing foreign shared-tree content.

The proposal does not revive the rejected foreign-first route. It permits one hand-authored index patch solely to add the existing `skill.managed-skill-adoption-review` object to the staged Antigravity manifest representation. The working tree remains untouched for every foreign object and SHA refresh. The patch and final commit remain subject to this proposal's independent Loyal Opposition GO, implementation-start authorization, focused tests, and hunk-scoped verification.

## Scope And Explicit Denylist

The finalization may stage and commit only the seven declared targets, subject to these tighter limits:

- The Antigravity manifest may contain only the complete object whose `capability_id` is `skill.managed-skill-adoption-review`; no other object, source SHA refresh, ordering change, or formatting change is permitted in the staged index.
- The Codex manifest may contain only the complete `skill.managed-skill-adoption-review` object.
- The capability registry may contain only the appended `[[capabilities]]` block whose `id` is `skill.managed-skill-adoption-review`.
- The four skill/test paths must contain the already-reviewed WI-4841 managed-skill content only.

The following are prohibited from staging, committing, editing, or attribution under this bridge: the foreign `skill.formal-artifact-packet-helper`, `skill.skill-governance-lifecycle`, `skill.advisory-disposition`, `skill.advisory-proposal`, and `skill.advisory-intake` Antigravity manifest objects; every unrelated source SHA refresh; every unrelated adapter; `groundtruth.db`; and generated `harness-state/harness-registry.json`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires a numbered Prime proposal, independent LO GO, and governed finalization rather than a direct owner-chat bypass.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserves the live-GO and exact-target-path precondition despite the owner waiver.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active PAUTH must cover WI-4841 without broadening this proposal's target list.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the concrete owner-waiver, finalization, and parity constraints to be linked before review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH, project, WI, and inline JSON target paths above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires focused executed evidence and an exact staged/committed path audit before verification.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - the parent `NO-ACTION` exposed the prior verdict's non-executable route; this child supplies a governed replacement.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires the Claude, Codex, and Antigravity managed-skill declarations to remain coherent.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - require equivalent canonical/adapter coverage and regression checks across the declared harnesses.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the superseding owner choice and the commingled-tree exception as governed durable evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all finalization paths and checks remain inside `E:\\GT-KB`.

## Prior Deliberations

- `DELIB-20260710-WI4841-HUNK-SCOPED-FINALIZATION-WAIVER` - the explicit owner decision authorizing this WI-4841-only finalization route and superseding the prior route only for this purpose.
- `DELIB-202666072` - prior foreign-first decision, superseded only as to the WI-4841 finalization route.
- `DELIB-202665926` - owner decision that Antigravity is a supported managed-skill projection target for WI-4841.
- `DELIB-20266596` - bounded skill-scaffold authorization context for WI-4839 through WI-4842.
- `gtkb-wi4841-managed-skill-adoption-review-scaffold-018` - original GO for the seven WI-4841 paths.
- `gtkb-wi4841-managed-skill-adoption-review-scaffold-024` - finalization-only NO-GO identifying the commingled manifest issue.
- `gtkb-wi4841-managed-skill-adoption-review-scaffold-025` - PB NO-ACTION documenting why foreign-first had no live writable authority.
- `WI-5105` - recurring commingled shared-registry finalization class.

## Owner Decisions / Input

- `DELIB-20260710-WI4841-HUNK-SCOPED-FINALIZATION-WAIVER` records the owner's selection of the hunk-scoped waiver route in this session. It authorizes only the narrow finalization method and explicitly retains the GO, implementation-start, independent review, and no-sweep requirements.

## Requirement Sufficiency

Existing requirements sufficient. The active WI-4841 PAUTH, original implementation evidence, and the new owner decision fully specify a narrow finalization method. No new product behavior, harness projection, registry schema, or foreign skill content is authorized.

## Cross-Harness Disposition

- Claude Code: the existing canonical managed-skill implementation remains the authority for this finalization.
- Codex: the existing generated managed-skill adapter and manifest entry are finalized together with the canonical implementation.
- Antigravity: the existing generated adapter, its manifest object, and its adapter registry declaration are finalized together with the canonical implementation.
- Cursor, Ollama, OpenRouter, and Goose: unchanged by this finalization; their existing unsupported or suspended declarations are neither altered nor newly waived.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and PB authorization rules | Obtain a fresh independent LO GO, work-intent claim, and implementation-start packet before staging any protected path. | Every gate passes before index mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests\\skills\\test_managed_skill_adoption_review_skill.py platform_tests\\skills\\test_skill_catalog_contract.py -q --tb=short --basetemp .harness-tmp\\wi4841-waiver`. | All focused skill and catalog tests pass. |
| Cross-harness parity rules | Run `groundtruth-kb\\.venv\\Scripts\\python.exe scripts\\generate_codex_skill_adapters.py --check` and `groundtruth-kb\\.venv\\Scripts\\python.exe scripts\\generate_antigravity_skill_adapters.py --check`. | Both projections are current and include the managed-skill adapter. |
| Owner waiver scope | Inspect the staged diff and require that the staged Antigravity manifest contains only the `skill.managed-skill-adoption-review` object; require no foreign ID or unrelated SHA refresh in `git diff --cached`. | Exact hunk isolation; foreign working-tree rows remain unstaged. |
| Harness onboarding and parity | Parse the staged registry and manifests, asserting the managed-skill capability has canonical Claude plus Codex and Antigravity adapters. | Only the WI-4841 capability block and adapter entries are staged. |
| Commit hygiene | Require `git diff --cached --name-only` to equal the seven target paths, then commit only that index. Confirm the working tree retains foreign rows afterward. | No `groundtruth.db`, generated projection, or foreign path enters the commit. |

## Acceptance Criteria

- A valid independent GO authorizes exactly this proposal before protected paths are staged.
- The final commit contains the WI-4841 canonical skill, Codex adapter, Antigravity adapter, focused test, owned Codex/registry entries, and only the WI-4841 object in the Antigravity manifest.
- The staged Antigravity manifest diff contains none of the foreign IDs or foreign SHA refreshes named above.
- Focused tests and both adapter checks pass.
- `groundtruth.db`, `harness-state/harness-registry.json`, and all foreign shared-tree work remain unstaged and uncommitted.
- A post-implementation report supplies exact test, staged-diff, and commit evidence for independent Loyal Opposition verification.

## Risk / Rollback

The primary risk is that a hand-authored index patch can accidentally absorb foreign content. The workflow therefore validates the staged path set and the staged manifest object before commit, while leaving the worktree unchanged for foreign rows. Rollback is one revert of the narrowly scoped finalization commit; bridge and deliberation artifacts remain append-only.

## Recommended Commit Type

`feat` - finalizes the new managed-skill capability across its canonical and supported adapter projections without altering foreign capability work.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
