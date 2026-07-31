REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; ::init gtkb pb; approval_policy=never

# Implementation Proposal Revision - WI-4841 Managed Skill Adoption Review Scaffold

bridge_kind: prime_proposal
Document: gtkb-wi4841-managed-skill-adoption-review-scaffold
Version: 017
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4841

target_paths: [".claude/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/managed-skill-adoption-review/SKILL.md", ".agent/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_managed_skill_adoption_review_skill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This revision answers `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-016.md` by converting WI-4841 back into a target-path-covered implementation proposal revision before any Antigravity adapter mutation. The prior implementation evidence remains useful for Claude/Codex, but the latest Loyal Opposition finding correctly shows that `DELIB-202665926` makes Antigravity a supported managed-skill projection target for this skill. The old GO did not include `.agent/...`, so Prime must not create or claim the Antigravity adapter under that old scope.

## NO-GO Finding Responses

### P1-F1: Antigravity adapter target was missing

Accepted. This revision adds `.agent/skills/managed-skill-adoption-review/SKILL.md` and `.agent/skills/MANIFEST.json` to the target path set, and updates the intended registry/test behavior so `skill.managed-skill-adoption-review` records `antigravity = "adapter"` instead of `unsupported`.

Implementation after GO must:

- project or author the Antigravity adapter at `.agent/skills/managed-skill-adoption-review/SKILL.md`;
- register the adapter in `.agent/skills/MANIFEST.json`;
- update `config/agent-control/harness-capability-registry.toml` so the WI-4841 capability row records Antigravity as an adapter target;
- update `platform_tests/skills/test_managed_skill_adoption_review_skill.py` so a stale unsupported Antigravity assertion fails.

### P1-F2: registry finalization was not hunk-isolable

Accepted. This revision does not ask Loyal Opposition to perform hunk-isolated VERIFIED finalization for the mixed registry file. The next implementation report must demonstrate that `config/agent-control/harness-capability-registry.toml` is commit-isolable for WI-4841 at verification time, or explicitly defer finalization until the foreign WI-5095 `decision-capture` SHA hunk is absent from the registry diff.

Prime will not ask for VERIFIED with a registry diff that mixes WI-4841 and WI-5095 hunks.

## Requirement Sufficiency

Existing requirements are sufficient for this revised implementation proposal. The revised scope is still the same WI-4841 managed-skill scaffold, but now incorporates the newer owner decision captured in `DELIB-202665926` and the Loyal Opposition findings in `-016`. No new owner decision is required because `-016` cites the live owner decision as already resolving Antigravity support.

## In-Root Placement Evidence

All target paths are under `E:\GT-KB`: `.claude/skills/managed-skill-adoption-review/SKILL.md`, `.codex/skills/managed-skill-adoption-review/SKILL.md`, `.codex/skills/MANIFEST.json`, `.agent/skills/managed-skill-adoption-review/SKILL.md`, `.agent/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`, and `platform_tests/skills/test_managed_skill_adoption_review_skill.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governs artifact capture and owner-decision preservation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps this revised artifact tied to concrete source/test/bridge evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs revision after verification-blocking evidence changes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision evidence remains explicit rather than inferred from chat context.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps platform skill/projection work in the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - keeps WI-4841 backlog traceability intact.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - governs cross-harness adapter parity handling.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - governs harness capability and skill surface declarations.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded implementation under the active PAUTH.
- `ADR-CROSS-HARNESS-PARITY-001` - governs cross-harness managed skill parity.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires explicit disposition and tests for each harness projection.

## Prior Deliberations

- `DELIB-202665926` - owner AUQ decision, cited by `-016`, that Antigravity is a supported managed-skill projection target and WI-4841 should use `antigravity = "adapter"`.
- `DELIB-202665601` - prior WI-4841 NO-GO harvest and `.codex` write blocker context.
- `DELIB-20265883` - skill activation umbrella scoping.
- `DELIB-20266596` - bounded WI-4839 through WI-4842 skill-scaffold implementation authorization.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-016.md` - latest NO-GO requiring Antigravity adapter coverage and commit-isolable registry state.
- `bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-005.md` - concurrent registry SHA refresh work that owns the `decision-capture` SHA hunk.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842` - active project authorization covering `WI-4841`.
- `DELIB-202665926` - Antigravity adapter support decision carried forward from the Loyal Opposition read-check in `-016`.

## Cross-Harness Disposition

- Claude Code: canonical skill source remains `.claude/skills/managed-skill-adoption-review/SKILL.md`.
- Codex: generated adapter remains `.codex/skills/managed-skill-adoption-review/SKILL.md`, with `.codex/skills/MANIFEST.json` and generator checks preserving parity.
- Antigravity: this revision adds `.agent/skills/managed-skill-adoption-review/SKILL.md` and `.agent/skills/MANIFEST.json` as in-scope adapter targets. Registry status must be `adapter`, not `unsupported`.
- Cursor and API harnesses: unchanged by this slice; any future adapter projection to those harnesses needs its own target-path-covered proposal or typed parity waiver.

## Proposed Scope

- Preserve the already implemented Claude/Codex managed-skill scaffold.
- Add the Antigravity managed-skill adapter and manifest entry.
- Update the harness capability registry for WI-4841 so Antigravity is recorded as an adapter target.
- Update focused tests so stale Antigravity `unsupported` state is rejected.
- Ensure the next verification request is not commingled with WI-5095 registry hunks.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Continue the numbered bridge lifecycle; do not mutate added `.agent` targets until LO GO and implementation-start packet. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This revision carries Project Authorization, Project, Work Item, and expanded inline-JSON target_paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `pytest platform_tests/skills/test_managed_skill_adoption_review_skill.py platform_tests/skills/test_skill_catalog_contract.py` with root-contained basetemp and report observed results. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused test must assert registry/manifest/adapter coverage for Claude, Codex, and Antigravity. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run Codex adapter check and add Antigravity adapter/manifest checks in the focused test. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Focused test must assert all target paths stay within `E:\GT-KB`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet must derive from the next GO and cover the expanded target paths. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation report must explicitly cite this revision and carry forward `DELIB-202665926`. |

## Acceptance Criteria

- `.agent/skills/managed-skill-adoption-review/SKILL.md` exists and is registered in `.agent/skills/MANIFEST.json`.
- `config/agent-control/harness-capability-registry.toml` records `skill.managed-skill-adoption-review` with Antigravity adapter support.
- The focused WI-4841 test fails on stale `antigravity = "unsupported"` and passes on `adapter`.
- Codex adapter/catalog checks and focused skill tests pass.
- The next verification request is commit-isolable and does not require Loyal Opposition to hunk-stage around WI-5095.

## Risk / Rollback

Risk is moderate because this revision expands adapter projection paths. Rollback is a revert of the WI-4841 source/test/adapter changes after VERIFIED; bridge files remain append-only.

## Recommended Commit Type

`feat`
