NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Verified Staging Finalization Gate

bridge_kind: prime_proposal
Document: gtkb-ollama-phase2-verified-staging-finalization-gate
Version: 001
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4383
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-WI-4383-STAGING-FINALIZATION-GATE
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Date: 2026-06-06 UTC
Requires verification: true
Recommended commit type: feat
target_paths: ["scripts/harness_roles.py", "platform_tests/scripts/test_ollama_role_promotion.py", "bridge/INDEX.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-009.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-010.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-011.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-012.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-013.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-014.md"]

## Summary

The Ollama Phase 2 role-promotion child is latest VERIFIED at `bridge/gtkb-ollama-integration-phase-2-role-promotion-014.md`, but the verified implementation cannot be staged for the required milestone commit because protected target staging still consults the active implementation-start packet. The original role-promotion packet is now terminal by design because the bridge thread is VERIFIED.

This proposal authorizes only the finalization act: acquire a fresh implementation-start packet for this finalization thread, stage the exact already-VERIFIED Ollama role-promotion files, create the required conventional milestone commit, and file a short implementation report with commit evidence. It does not reopen the terminal role-promotion implementation thread and does not change the implementation-start gate.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` records the owner directive to complete remaining Ollama phases while preserving bridge GO/VERIFIED gates and the self-review prohibition.
- The owner explicitly instructed this session: "Proceed with completing all Ollama phases and related work" and then "You are prime Builder. Please continue."
- No new owner choice is required. This is a mechanical finalization bridge needed to commit the already VERIFIED role-promotion milestone without bypassing hooks.

## Requirement Sufficiency

Existing requirements are sufficient.

The bridge protocol, implementation-start gate, and project authorization envelope already require a GO packet before protected-file staging. This proposal uses that mechanism rather than changing it. No new GOV, ADR, or DCL is required for this scoped finalization bridge.

## Prior Deliberations

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` - owner directive to complete Ollama Phase 2+ through governed bridge milestones.
- `DELIB-20260663` - Phase 1 Ollama owner-decision anchor; establishes the harness onboarding and governance context.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - bridge VERIFIED backlog reconciler behavior that resolved `WI-4382` when the role-promotion thread reached VERIFIED.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - role/status separation relevant to the underlying role-promotion milestone.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this finalization is filed as a bridge proposal and awaits Loyal Opposition GO before protected staging.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications and maps verification to each applicable behavior.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work item metadata are declared above.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - `WI-4383` is an active member of `PROJECT-GTKB-OLLAMA-INTEGRATION` and is included in the active PAUTH named above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the finalization report must include command evidence for packet acquisition, staging, commit, focused pytest, ruff check, and ruff format-check.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - protected staging must use a fresh implementation-start packet for this GO'd finalization bridge.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH bounds this work to source/test/bridge artifacts and forbids bypassing bridge GO/VERIFIED.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the finalization avoids hook bypass flags, alternate index plumbing, stale terminal packet reuse, and unrelated GO packets.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root GT-KB platform/bridge files under `E:\GT-KB`.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` - the committed implementation belongs to the Ollama harness adoption project.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - the role-promotion milestone is part of completing governed harness onboarding.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the blocker is preserved as `WI-4383`, a PAUTH, and this bridge record instead of being handled as an untracked workaround.

## Proposed Scope

1. Acquire an implementation-start packet for this bridge after Loyal Opposition GO.
2. Stage only the verified Ollama role-promotion implementation files and bridge chain named in `target_paths`.
3. Create the milestone commit with conventional type `feat`, with no push and no hook bypass.
4. File the implementation report for this finalization bridge with the commit hash, staging result, and focused verification evidence.

## Explicit Non-Scope

- No edits to `scripts/implementation_start_gate.py`.
- No edits to `scripts/implementation_authorization.py`.
- No alternate index plumbing, hook bypass flags, or unrelated GO packets.
- No source changes beyond staging the already VERIFIED role-promotion implementation.
- No role promotion of harness D and no mutation of Ollama dispatch routing.
- No push.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use existing files and command evidence only; do not add credential-shaped fixtures. | Existing helper credential scan and git hooks remain active. | |
| CQ-PATHS-001 | Yes | Stage with explicit in-root pathspecs only. | Cached diff path list is checked before commit. | |
| CQ-COMPLEXITY-001 | N/A | No implementation code is edited in this finalization bridge. | Baseline review confirms no code-edit scope. | No implementation code is edited. |
| CQ-CONSTANTS-001 | N/A | No constants or runtime logic are changed. | Baseline review confirms no code-edit scope. | No constants are edited. |
| CQ-SECURITY-001 | Yes | Do not use hook-bypass flags, alternate index plumbing, or unrelated authorization packets. | Implementation report cites the exact staging and commit commands. | |
| CQ-DOCS-001 | Yes | Preserve bridge audit trail with proposal, implementation report, and LO verification. | Bridge thread reaches GO then NEW report, then LO verdict. | |
| CQ-TESTS-001 | Yes | Re-run focused Ollama role-promotion pytest evidence before finalization report. | Focused pytest result is recorded in the report. | |
| CQ-LOGGING-001 | N/A | No runtime logging surface is changed. | Baseline review confirms no logging-surface scope. | No runtime logging surface is edited. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, scoped ruff check, scoped ruff format-check, and bridge preflights. | Commands recorded in the implementation report. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: proposal reaches GO before protected staging; implementation report is filed afterward.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run the bridge applicability preflight for this bridge id.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: proposal includes the three machine-readable project-linkage lines and passes helper compliance audit.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`: `WI-4383` and `PROJECT-GTKB-OLLAMA-INTEGRATION` show active membership and active PAUTH inclusion.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: implementation report includes exact command evidence for packet acquisition, staging, commit, pytest, ruff check, and ruff format-check.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: implementation-start packet acquisition succeeds for this bridge before protected staging.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: active PAUTH includes only `WI-4383`, source/test/bridge mutation classes, and forbids bypass operations.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: staging succeeds only under this bridge packet; no hook bypass, alternate index plumbing, or unrelated authorization is used.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: cached diff path list shows only in-root GT-KB paths for this milestone commit.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` and `GOV-HARNESS-ONBOARDING-CONTRACT-001`: focused Ollama role-promotion tests and scoped ruff checks are re-run before or during finalization.

## Verification Commands After GO

- Acquire the implementation-start packet for this bridge id.
- Stage the exact `target_paths` set, then inspect the cached diff path list.
- Run focused pytest covering Ollama role promotion, dispatch, dispatch verifier, and doctor coverage.
- Run scoped ruff check and scoped ruff format-check for the Ollama role-promotion and dispatch surfaces.
- Create the milestone commit with message `feat: complete ollama phase 2 role promotion closure`.

## Risk / Rollback

Risk is low because the proposal does not edit implementation code. The main risk is accidental staging of unrelated dirty files. Mitigation: use explicit pathspecs and confirm the cached diff path list before commit.

Rollback before commit: unstage explicit paths only. Rollback after commit, if needed, is a normal revert commit; do not rewrite history without owner direction.

## Acceptance Criteria

- Loyal Opposition GO is recorded for this finalization proposal.
- Implementation-start packet is acquired for this bridge, not for the terminal role-promotion bridge and not for an unrelated GO.
- The exact role-promotion files listed in scope are staged and committed with `feat: complete ollama phase 2 role promotion closure`.
- Focused pytest and scoped ruff check/format-check pass and are cited in the implementation report.
- No push is performed.

## Pre-Filing Applicability Preflight

Content-file applicability preflight is enforced by the helper-mediated bridge write path. The live indexed preflight must be rerun by Loyal Opposition before GO.

## ADR/DCL Clause Preflight

Clause preflight must be rerun by Loyal Opposition before GO. The proposal includes the required project metadata, owner input section, specification links, and spec-derived verification plan.
