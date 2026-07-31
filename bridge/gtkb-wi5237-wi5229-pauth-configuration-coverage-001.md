NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; resumed fleet goal; A is PB-only

bridge_kind: governance_advisory
Document: gtkb-wi5237-wi5229-pauth-configuration-coverage
Version: 001
Date: 2026-07-14 UTC

Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5237
target_paths: ["groundtruth.db"]

# Implementation Proposal - Reissue WI-5229 PAUTH with helper configuration mutation coverage

## Summary

WI-5229 has an independent GO at `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-002.md`, but Prime Builder cannot legally acquire the implementation claim. The live `work_intent_acquire` gate fails closed before creating a claim because the active PAUTH `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714` does not allow the `configuration` mutation class for the approved verify-helper parity paths: `.claude/skills/verify/helpers/write_verdict.py`, `.codex/skills/verify/helpers/write_verdict.py`, and `.cursor/skills/verify/helpers/write_verdict.py`.

This proposal appends a version-2 correction to the same PAUTH ID, adding only the registered `configuration` mutation class while preserving the existing included work item, owner decision, source/test/bridge/governance evidence scope, and forbidden-operation boundaries. The repair is needed before the P0 WI-5229 binary VERIFIED finalizer can unblock WI-5139 and downstream PAUTH repairs.

## Claim

Prime Builder proposes a bounded PAUTH coverage repair only. It does not implement WI-5229 source or test changes, does not edit any verify-helper file, does not edit dispatcher/routing/runtime/lease state, does not replace `groundtruth.db`, and does not authorize unrelated work. Mutation scope for this proposal is the append-only `groundtruth.db` PAUTH version written through `gt projects authorize` after independent GO, matching claim, and implementation-start authorization.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` requires mutation classes to come from the governed taxonomy and denies operations whose target paths require a class not present in the active PAUTH. `WI-5237` / `TEST-11391` capture the observed failure and expected recovery. The approved WI-5229 proposal already includes the three verify-helper parity paths, so the PAUTH correction should make the existing GO executable without revising WI-5229's approved source/test scope.

## In-Root Placement Evidence

The only implementation target for this PAUTH repair is `groundtruth.db` under `E:\GT-KB`. The downstream WI-5229 helper paths are also inside `E:\GT-KB`; this proposal does not mutate them. No `applications/Agent_Red/` path, external repository, dispatcher runtime JSON, lease file, credential, deployment, Git remote, or external-system target is in scope.

## Exact Proposed PAUTH Version-2 Envelope

Append a new active version for `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714` with:

- `authorization_name`: `WI-5229 binary VERIFIED finalizer repair`
- `project_id`: `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`
- `owner_decision_deliberation_id`: `DELIB-202666199`
- `allowed_mutation_classes`, in order: `bridge`, `configuration`, `metadata`, `governance_evidence`, `source`, `test`
- `forbidden_operations`, in order: `dispatcher_mutation`, `destructive_cleanup`, `credential_lifecycle`, `production_deployment`, `git_history_rewrite`, `external_system_mutation`, `git_push`
- `included_work_item_ids`: `WI-5229`
- `included_spec_ids`: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `expires_at`: null
- `status`: active
- `changed_by`: `prime-builder/codex/A`
- `change_reason`: `WI-5237: correct WI-5229 PAUTH allowed_mutation_classes after work_intent_acquire failed closed on verify-helper configuration paths.`
- `scope_summary`: `Bounded authorization for WI-5229 to file a bridge proposal and, only after independent Loyal Opposition GO plus matching work-intent claim and implementation-start packet, repair binary-aware reviewed hunk-patch support in PublishBridgeVerdict / VERIFIED finalization. Scope is limited to finalizer writer/helper parity source, verify-helper configuration copies, focused regression tests, and bridge/governance evidence needed to unblock WI-5139 VERIFIED finalization without replacing groundtruth.db or altering commit 08cbc017.`

## Exact Mutation Command

After fresh independent GO, matching Prime Builder claim, and a successful no-write implementation-start check for this thread, execute:

```powershell
groundtruth-kb\.venv\Scripts\gt.exe projects authorize PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --id PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714 --owner-decision DELIB-202666199 --name "WI-5229 binary VERIFIED finalizer repair" --scope "Bounded authorization for WI-5229 to file a bridge proposal and, only after independent Loyal Opposition GO plus matching work-intent claim and implementation-start packet, repair binary-aware reviewed hunk-patch support in PublishBridgeVerdict / VERIFIED finalization. Scope is limited to finalizer writer/helper parity source, verify-helper configuration copies, focused regression tests, and bridge/governance evidence needed to unblock WI-5139 VERIFIED finalization without replacing groundtruth.db or altering commit 08cbc017." --allowed-mutation bridge --allowed-mutation configuration --allowed-mutation metadata --allowed-mutation governance_evidence --allowed-mutation source --allowed-mutation test --forbid dispatcher_mutation --forbid destructive_cleanup --forbid credential_lifecycle --forbid production_deployment --forbid git_history_rewrite --forbid external_system_mutation --forbid git_push --include-work-item WI-5229 --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --include-spec DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 --include-spec GOV-DOCUMENT-AUTHOR-PROVENANCE-001 --include-spec DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 --include-spec ADR-CODEX-HOOK-PARITY-FALLBACK-001 --include-spec ADR-CROSS-HARNESS-PARITY-001 --include-spec DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 --include-spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 --include-spec DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 --include-spec PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 --include-spec DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 --include-spec ADR-ISOLATION-APPLICATION-PLACEMENT-001 --changed-by prime-builder/codex/A --change-reason "WI-5237: correct WI-5229 PAUTH allowed_mutation_classes after work_intent_acquire failed closed on verify-helper configuration paths." --json
```

Do not add `--exclude-*`, `--expires-at`, `--plan-incomplete`, dispatcher, runtime, lease, credential, deployment, Git push, or external-system arguments.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - target mutation classes must be registered and present in the active PAUTH at operation time; missing `configuration` correctly denies the WI-5229 claim.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - governs append-only PAUTH envelope fields and active-version correction.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - this repair does not bypass WI-5229's existing GO, claim, implementation-start, report, or independent verification gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this correction must flow through a numbered bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the relevant governing specifications before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must execute the mapped PAUTH verification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - downstream WI-5229 finalizer/publisher behavior must preserve real author and session provenance.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries project, work item, and target path metadata.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the approved WI-5229 implementation includes Codex/Claude/Cursor verify-helper parity copies.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper-copy changes must remain cross-harness equivalent.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposal and downstream target paths remain in-root and outside adopter application scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, WI/test, PAUTH repair, implementation report, and verification remain linked as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the failed implementation gate triggers a governed correction rather than an informal bypass.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proof-blocking defect is preserved as a work item with a linked test and bridge lifecycle.

## Prior Deliberations

- `DELIB-202666199` - owner authorized the incident-specific WI-5229 binary VERIFIED finalizer PAUTH/proposal after the WI-5139 terminal publication blocker.
- `DELIB-202666173` - owner directed correction of every defect discovered during the genuine A/B/C/D/F/H governed fleet proof.
- `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-001.md` - approved WI-5229 proposal listing the verify-helper parity paths that require `configuration` coverage.
- `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-002.md` - independent D GO for WI-5229.
- `WI-5237` / `TEST-11391` - newly captured PAUTH coverage defect and expected recovery test.

## Owner Decisions / Input

- `DELIB-202666199` authorizes the WI-5229 finalizer repair PAUTH/proposal scope being corrected here.
- `DELIB-202666173` is the active fleet-goal directive requiring proof-blocking defects to be corrected through governed artifacts.
- No new owner approval is requested in this proposal; the change appends the missing registered mutation class needed for already-approved WI-5229 target paths and does not expand forbidden-operation boundaries.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Registered mutation class | Load `config/governance/project-authorization-operation-taxonomy.toml` and verify `configuration`, `bridge`, `metadata`, `governance_evidence`, `source`, and `test` are registered mutation classes. |
| Exact persisted PAUTH | Run `gt projects show-authorization PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714 --json` and compare active version, ID, status, included work item, ordered allowed classes, forbidden operations, included specs, owner decision, scope, and change reason to this proposal. |
| Work-intent unblock | Run `python scripts/bridge_claim_cli.py claim gtkb-wi5229-binary-verified-finalizer-hunk-patch --session-id <current-session> --ttl-seconds 300` and require success with no `target_mutation_class_not_allowed`; release the claim immediately after verification if WI-5229 implementation is not starting in the same transaction. |
| Implementation-start unblock | With a matching claim held, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5229-binary-verified-finalizer-hunk-patch --session-id <current-session> --no-write` and require authorization to proceed past the PAUTH target-class check. |
| Side-effect boundary | Before/after snapshots show this implementation only appends the PAUTH version and creates the implementation report; no source, test, dispatcher runtime JSON, lease, credential, deployment, Git remote/history, or unrelated worktree changes occur. |
| No bridge bypass | WI-5229 still requires its existing latest GO, matching claim, implementation-start packet, source/test/configuration helper changes, implementation report, and independent LO verification before completion. |

## Acceptance Criteria

- The active WI-5229 PAUTH includes registered `configuration` coverage for the approved verify-helper parity paths.
- A matching WI-5229 work-intent claim succeeds where it previously failed with `target_mutation_class_not_allowed` on helper configuration paths.
- The PAUTH ID cited by the WI-5229 GO-approved proposal remains the active ID, so no WI-5229 proposal revision is required solely for ID mismatch.
- The correction does not authorize dispatcher/routing edits, runtime JSON or lease edits, credential lifecycle, Git push/history rewrite, production deployment, live `groundtruth.db` replacement, commit alteration, or unrelated work.
- The correction is independently VERIFIED before WI-5229 protected implementation resumes.

## Risk And Rollback

The main risk is over-broadening the WI-5229 PAUTH. The proposal limits that risk by retaining the same PAUTH ID, one included work item, the same owner decision, the same forbidden operation IDs, and the same source/test/bridge/governance evidence scope while adding only the registered `configuration` class required by the approved helper-copy targets. If the persisted version differs from the normative envelope, stop WI-5229 implementation and use a separately GO-approved append-only successor to supersede or correct the authorization; do not delete historical rows.

## Recommended Commit Type

`fix(governance):`
