NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: prime_proposal
Document: gtkb-active-status-capability-gate-formalization-content-drafts
Project Authorization: PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4213
target_paths: [".gtkb-state/formal-spec-drafts/wi-4213-adr-role-status-orthogonality-001-v2.md", ".gtkb-state/formal-spec-drafts/wi-4213-dcl-single-active-per-role-dispatch-001-v2.md", ".gtkb-state/formal-spec-drafts/wi-4213-req-harness-registry-001-v3.md"]

# Implementation Proposal: Active-Status Capability Gate Formalization Content Drafts

## Summary

The approved `gtkb-active-status-capability-gate-formalization` proposal authorizes the formal DB rows and approval packets for WI-4213. The governed `gt spec update` command also requires in-root content files as inputs before it can write those final artifacts. The implementation-start hook correctly blocks creating those draft files because they are not in the original target path list.

This proposal authorizes only the three formal spec content draft files needed as inputs for the existing formalization thread. It does not authorize DB mutation or approval packet creation; those remain governed by `gtkb-active-status-capability-gate-formalization`.

## Prior Deliberations

- `bridge/gtkb-active-status-capability-gate-formalization-001.md` and `bridge/gtkb-active-status-capability-gate-formalization-002.md` approve the WI-4213 formal artifact mutation slice.
- `bridge/gtkb-implementation-start-requirement-sufficiency-owner-direction-phrase-006.md` verifies the parser fix that lets the formalization start gate pass.
- WI-4213 records active as bridge-event reception capability and keeps WI-3513 separate as the durable bridge writer contention fix.
- DELIB-2813 records the owner directive to continue until the listed items are completed under the active project authorization.

## Owner Decisions / Input

No new owner decision is required. This is a support-file authorization for the already-approved WI-4213 formalization thread and does not expand the substantive formalization scope.

## Specification Links

- ADR-ROLE-STATUS-ORTHOGONALITY-001
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001
- REQ-HARNESS-REGISTRY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-STANDING-BACKLOG-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001

## Requirement Sufficiency

Existing requirements sufficient.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Draft files contain formal spec prose only; no credentials or environment values. | Helper credential scan and content review. | |
| CQ-PATHS-001 | Yes | Mutate only the three `.gtkb-state/formal-spec-drafts/wi-4213-*` files listed in target_paths. | `git diff --name-only -- .gtkb-state/formal-spec-drafts`. | |
| CQ-COMPLEXITY-001 | Yes | Preserve current DB descriptions and add/replace only WI-4213 capability-gate text. | Content diff review and dry-run packet preview. | |
| CQ-CONSTANTS-001 | Yes | Use the same terms across all drafts: durable role, status, event_driven_hooks, bridge-event reception capability, WI-3513. | `rg` checks on draft content. | |
| CQ-SECURITY-001 | Yes | State fail-closed dispatch exclusion for missing/false event-driven capability. | Draft content review. | |
| CQ-DOCS-001 | Yes | Drafts are formal documentation inputs and must be owner-presentable markdown. | Content review and spec-update dry-run. | |
| CQ-TESTS-001 | Yes | Dry-run all three `gt spec update` commands before final mutation. | `python -m groundtruth_kb spec update ... --dry-run --json` for each file. | |
| CQ-LOGGING-001 | N/A | Draft generation does not change runtime logging. | N/A. | No runtime logging path changes. |
| CQ-VERIFICATION-001 | Yes | Verify files exist, contain required markers, and pass spec-update dry-run validation. | Commands listed in the implementation report. | |

## Scope

In scope:

- Create `.gtkb-state/formal-spec-drafts/wi-4213-adr-role-status-orthogonality-001-v2.md`.
- Create `.gtkb-state/formal-spec-drafts/wi-4213-dcl-single-active-per-role-dispatch-001-v2.md`.
- Create `.gtkb-state/formal-spec-drafts/wi-4213-req-harness-registry-001-v3.md`.
- Preserve existing live spec descriptions while adding or replacing only WI-4213 active-status capability-gate text.
- Run `gt spec update --dry-run --json` against each draft to confirm the governed update command accepts the content and predicts the expected v2/v2/v3 packet paths.

Out of scope:

- Mutating `groundtruth.db`.
- Creating `.groundtruth/formal-artifact-approvals/*.json` packets.
- Editing source code, harness registry records, dispatch resolver code, or bridge writer serialization.
- Resolving WI-4213 before the final formalization and registry/dispatch follow-up are verified.

## Acceptance Criteria

- All three draft files exist at the listed target paths.
- ADR draft states active status is capability-gated by bridge-event reception capability.
- DCL draft states event-driven dispatch requires role match, active status, and bridge-event reception capability.
- REQ draft supersedes stale single-prime-builder role wording with role/status/capability orthogonality and permits Antigravity C role retention while inactive/registered and non-event-capable.
- All drafts explicitly keep WI-3513 as the separate bridge write-contention fix.
- `gt spec update --dry-run --json` succeeds for ADR v2, DCL v2, and REQ v3.

## Specification-Derived Verification Plan

- ADR-ROLE-STATUS-ORTHOGONALITY-001: `rg "bridge-event reception capability|event_driven_hooks|WI-3513" .gtkb-state/formal-spec-drafts/wi-4213-adr-role-status-orthogonality-001-v2.md` and ADR dry-run.
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001: `rg "event_driven_hooks|non-event-capable|WI-3513" .gtkb-state/formal-spec-drafts/wi-4213-dcl-single-active-per-role-dispatch-001-v2.md` and DCL dry-run.
- REQ-HARNESS-REGISTRY-001: `rg "FR10|Antigravity harness C|WI-3513" .gtkb-state/formal-spec-drafts/wi-4213-req-harness-registry-001-v3.md` and REQ dry-run.
- GOV-FILE-BRIDGE-AUTHORITY-001: file this proposal through the bridge helper and preserve the bridge/INDEX.md state.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: include command evidence in the implementation report before Loyal Opposition verification.

## Pre-Filing Preflight

Manual preflight before filing: this proposal is limited to draft input files required by `gt spec update`; the original formalization thread retains authority over DB and approval-packet mutations. All target paths are in-root and under `.gtkb-state/formal-spec-drafts/`.

## Risk And Rollback

Risk: a draft could accidentally drop existing spec prose. Mitigation: generate each draft from the current DB description and verify the dry-run update before final mutation. Rollback deletes or supersedes the draft files; final formal artifacts are not mutated by this proposal.
