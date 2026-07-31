NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f1ec9-3f39-7fc0-9576-7f8e240ecb3e
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: approval_policy=never; sandbox=danger-full-access; interactive_role=prime-builder

# Implementation Proposal - Scoped revert of unauthorized LO author-metadata and guard edits

bridge_kind: prime_proposal
Document: gtkb-unauthorized-lo-author-metadata-guard-edit-revert
Version: 001
Date: 2026-07-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4953-SCOPED-LO-REVERT-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4953

requesting_role: Prime Builder
implementation_scope: source_revert
authorization_status: proposal_only
requires_review: true
requires_verification: true
implementation_data_scope: no additional database changes in this slice
target_paths: ["scripts/bridge_author_metadata.py", "scripts/bridge_metadata_audit.py", "scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/skills/proposal-review/SKILL.md", ".claude/skills/verify/SKILL.md", ".cursor/hooks.json", ".cursor/rules/gtkb-loyal-opposition.mdc", "platform_tests/hooks/test_bridge_author_metadata_gate.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_implementation_start_gate.py"]

## Claim

Revert the unauthorized 2026-07-01 Loyal Opposition protected-path edits that were made during the author-metadata placement and LO guard-parity advisory workstream. The revert must be tightly scoped to the advisory-related dirty hunks in the listed target paths, preserve unrelated shared-worktree changes, and leave forward-prevention implementation for a separate governed proposal.

## Triggering Advisory

- `bridge/gtkb-bridge-author-metadata-placement-lo-role-guard-advisory-001.md` records the incident and explicitly states that the advisory does not authorize implementation, project data updates, or commit.
- Mike approved filing this scoped revert proposal after Prime Builder reported that protected-file mutation is blocked without a live bridge `GO`.
- This proposal is the normal Prime Builder `NEW` route requested by the owner; it does not ratify the unauthorized LO diff.

## Owner Decisions / Input

- `DELIB-20260701-SCOPED-LO-REVERT-PROPOSAL-AUTH` records Mike's approval to file a normal Prime Builder proposal for the scoped revert.
- The same decision bounds this step to proposal filing and minimal authorization evidence; it does not authorize direct protected-file mutation before independent Loyal Opposition `GO`.

## Prior Deliberations

- `DELIB-20260701-SCOPED-LO-REVERT-PROPOSAL-AUTH` - owner approved the scoped revert proposal and bounded the authorization to proposal filing plus minimal project/work authorization state.
- `DELIB-20266647` - prior owner-governance context for bridge author metadata/provenance work referenced by related bridge metadata workstreams.
- `bridge/gtkb-bridge-author-metadata-placement-lo-role-guard-advisory-001.md` - Loyal Opposition advisory identifying both the unauthorized protected-path edits and the underlying forward-prevention concerns.
- Related bridge metadata work: `PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE`, WI-4938, WI-4939, and WI-4940.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - bridge artifacts must retain credible author/session/model provenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime Builder may author `NEW`/`REVISED`; Loyal Opposition must not author implementation status tokens or protected implementation work outside role authority.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - guard and hook contracts that affect multiple harnesses must be mechanically enforced through governed paths.
- `GOV-SESSION-ROLE-AUTHORITY-001` - session role authority controls role-specific bridge and file authority.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - harness role configuration must remain consistent across Codex, Claude, Cursor, Antigravity, Ollama, and OpenRouter surfaces.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-behavioral surfaces require explicit parity/disposition reasoning when touched.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - proposals touching harness surfaces must declare cross-harness disposition or typed waiver.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook-template surfaces must be treated honestly as fallback/parity surfaces rather than live Windows enforcement claims.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active GT-KB files and generated artifacts remain in-root under `E:/GT-KB`; this proposal writes only `E:/GT-KB/bridge/gtkb-unauthorized-lo-author-metadata-guard-edit-revert-001.md` and implementation work is limited to in-root target paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the advisory and owner decision are preserved as governed artifacts before mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the correction proceeds through durable proposal, work item, project authorization, implementation report, and verification surfaces.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner-approved revert crosses from advisory into actionable work and is captured as a work item/proposal rather than informal chat-only execution.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal includes concrete linked governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal names its project authorization, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map each linked spec to command evidence and observed results.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires the bounded project authorization listed above.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must remain inside the PAUTH envelope and forbidden mutation classes.

## Requirement Sufficiency

Existing requirements sufficient.

The advisory, owner decision, bridge authority rules, provenance rules, and project authorization envelope are enough to perform a scoped revert. Forward-prevention policy or hook work is outside this proposal and should use a separate proposal after this revert is verified.

## Cross-Harness Disposition

This is a parity-neutral revert across the harness surfaces it touches. Claude hook/skill surfaces, Cursor rule/config surfaces, and Codex template-adjacent surfaces are returned only to the authorized baseline for the advisory-related dirty hunks. No new per-harness behavior, waiver, or enforcement claim is introduced by this slice.

## Proposed Scope

Perform only the revert/remediation hygiene step needed to remove unauthorized LO implementation edits from the current worktree. The implementation must:

- Review current dirty hunks in every target path before mutation.
- Revert only advisory-related unauthorized edits made during the 2026-07-01 LO author-metadata placement / LO guard-parity session.
- Preserve unrelated user or Prime Builder worktree changes, including any unrelated modifications in files that overlap this target set.
- Avoid creating forward-prevention logic, new hook behavior, new tests, or policy changes in this slice.
- Avoid bridge audit-trail deletion, credential lifecycle work, production deployment, commit creation, or git history rewrite.

Paths listed in the advisory but with no observed dirty advisory-related diff at proposal time are intentionally out of scope for mutation unless the Loyal Opposition `GO` review identifies a specific in-scope dirty hunk that must be included.

## Implementation Plan

1. Reconfirm latest bridge state and work-intent claim after `GO` and before any protected-file mutation.
2. Capture a path-limited pre-revert diff summary for the target paths.
3. Restore advisory-related dirty hunks to the governed baseline using path-scoped or hunk-scoped revert mechanics; avoid blanket whole-worktree cleanup.
4. For overlap-risk files, inspect hunks manually and apply only the unauthorized revert portion.
5. Re-run a path-limited diff to confirm unauthorized placement/guard-parity additions are gone and unrelated changes remain untouched.
6. Run the verification commands below and file a post-implementation report for Loyal Opposition verification.

## Acceptance Criteria

- The unauthorized advisory-related diff is removed from the target paths.
- No unrelated dirty worktree changes are reverted.
- No forward-prevention implementation is added in this slice.
- The implementation report includes before/after diff evidence and spec-derived verification command results.
- Loyal Opposition can independently verify the revert and issue `VERIFIED` before any follow-on prevention slice is proposed.

## Specification-Derived Verification Plan

| Governing artifact | Verification evidence required after implementation |
| --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `python -m pytest platform_tests/hooks/test_bridge_author_metadata_gate.py platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short` after reverting unauthorized additions, plus bridge artifact author metadata remains valid on this proposal/report chain. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m groundtruth_kb.cli bridge show gtkb-unauthorized-lo-author-metadata-guard-edit-revert` shows a Prime-authored `NEW` followed by independent LO response before implementation. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Diff review confirms this slice removes unauthorized cross-cutting hook/test/skill changes rather than adding new enforcement. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Implementation report records Prime Builder role, work-intent claim, and `GO` bridge file before mutation. |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | Path-limited diff confirms Cursor/Codex/Claude-related guard surfaces are only reverted to the authorized baseline in this slice. |
| `ADR-CROSS-HARNESS-PARITY-001` | Cross-Harness Disposition above confirms parity-neutral revert behavior for harness surfaces. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Bridge compliance accepts the non-empty Cross-Harness Disposition section before filing. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Diff review confirms Codex template-adjacent hook behavior is not presented as a live Windows enforcement expansion in this slice. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All proposal, implementation, report, and verification artifacts remain under `E:/GT-KB`; target paths are in-root only. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Work item `WI-4953`, PAUTH, advisory, and DELIB are cited in the implementation report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The correction proceeds through proposal, GO, implementation report, and Loyal Opposition verification rather than direct protected mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The owner decision and actionable revert are captured as governed artifacts before implementation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-unauthorized-lo-author-metadata-guard-edit-revert` passes. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance/preflight confirms project authorization, project, work item, and target paths are present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report contains this table's spec-to-test mapping, exact command lines, and observed results. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation report cites `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4953-SCOPED-LO-REVERT-20260701` and stays within its allowed mutation classes. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Diff review confirms forbidden classes are absent: forward-prevention implementation, broad cleanup, audit-trail deletion, credential work, deployment, and history rewrite. |

Additional targeted verification commands:

```powershell
git diff -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/bridge_author_metadata.py scripts/bridge_metadata_audit.py scripts/gtkb_bridge_writer.py .claude/skills/proposal-review/SKILL.md .claude/skills/verify/SKILL.md .cursor/hooks.json .cursor/rules/gtkb-loyal-opposition.mdc platform_tests/hooks/test_bridge_author_metadata_gate.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_implementation_start_gate.py
python -m pytest platform_tests/hooks/test_bridge_author_metadata_gate.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-unauthorized-lo-author-metadata-guard-edit-revert
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-unauthorized-lo-author-metadata-guard-edit-revert
```

## Out Of Scope

- Implementing durable author-metadata placement enforcement.
- Adding Cursor/LO `Edit` matcher parity or new guard behavior.
- Updating `.codex/gtkb-hooks/hooks.json`, `.claude/hooks/lo-file-safety-gate.py`, `.claude/hooks/implementation-start-gate.py`, `config/governance/lo-file-safety.toml`, or `AGENTS.md` unless a concrete advisory-related dirty hunk is identified and explicitly included by the `GO` review.
- Additional project data updates beyond the already-created work item and project authorization evidence.
- Committing, pushing, release, deployment, or credential lifecycle work.

## Risks And Mitigations

- Risk: blanket path restore could erase unrelated dirty work. Mitigation: inspect and apply hunk-scoped revert where needed, with before/after diff evidence.
- Risk: reverting tests may expose baseline failures unrelated to the unauthorized diff. Mitigation: record exact targeted test results and distinguish baseline failures from revert regressions.
- Risk: forward-prevention work remains undone after the revert. Mitigation: file a separate proposal after this revert is verified, with independent scope and owner/governance authorization.

## Recommended Commit Type

fix
