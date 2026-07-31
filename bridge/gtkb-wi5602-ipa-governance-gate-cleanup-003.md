REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5602 Retired Assessment-Surface Governance Gate Cleanup - Revised Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5602-ipa-governance-gate-cleanup
Version: 003
Responds to: bridge/gtkb-wi5602-ipa-governance-gate-cleanup-002.md
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5602-GOVERNANCE-GATE-CLEANUP-2026-07-19
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5602
target_paths: ["scripts/controlled_artifact_paths.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_protected_mutation_guard.py"]
implementation_scope: source
requires_review: true
requires_verification: true
Recommended commit type: fix:

## Revision Claim

This revision corrects the version 001 Project Authorization and narrows the
implementation to the live governance defect. The exact WI-5602 authorization
is derived from the owner's canonical retirement decision and includes only
WI-5602. The implementation will remove the retired assessment-surface prefix
from the live controlled-artifact allowlist and implementation-authorization
path recognizer, then update the two focused tests.

This revision removes
`groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py` from scope. Version 001
proposed adding the names of two noncanonical archive clones to canonical
source. The owner has since reiterated that noncanonical artifacts may not be
referenced by canonical bridge artifacts and that the retired source contents
were deleted. This proposal therefore does not cite either clone as evidence,
does not protect or preserve either clone, and does not authorize destructive
cleanup. Disposal of untracked noncanonical residue requires its own exact
governed action.

## Requirement Sufficiency

Existing requirements sufficient. The owner retirement decision, exact WI-5602
PAUTH, and linked governance specifications fully define the narrowed removal
of stale live allowlist behavior. No new or revised requirement is needed
before implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` records the
  owner's binding retirement, deletion, and canonical-carrier boundary.
- `bridge/gtkb-wi5602-ipa-governance-gate-cleanup-001.md` is the original
  proposal.
- `bridge/gtkb-wi5602-ipa-governance-gate-cleanup-002.md` is the independent
  NO-GO answered here.

## Owner Decisions / Input

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` is the owner
  decision underlying
  `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5602-GOVERNANCE-GATE-CLEANUP-2026-07-19`.
- The owner has directed that noncanonical artifacts are not canonical bridge
  evidence. This revision removes the noncanonical-clone references and does
  not request a waiver.

## Findings Addressed

### Finding Review

Response: the mismatched approval-state PAUTH is replaced with the exact,
active WI-5602 PAUTH created through `gt projects authorize`. Its
`included_work_item_ids` is exactly `["WI-5602"]`, its scope covers the two
live source gates and focused tests, and its owner-decision reference is the
on-topic retirement deliberation. The technical proposal is also narrowed to
avoid creating new canonical dependencies on noncanonical archive residue.

## Scope Changes

- Retain `scripts/controlled_artifact_paths.py`.
- Retain `scripts/implementation_authorization.py`.
- Retain the two focused test modules.
- Remove `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py`.
- Do not mutate dispatcher configuration/runtime, credentials, Git history,
  deployment, release, or untracked archive residue.

## Pre-Filing Preflight Subsection

The governed revision helper executes candidate-content applicability and
ADR/DCL clause preflights before filing and fails closed on any nonzero result.
The live thread must then pass both preflights again before implementation.

## Verification Plan

| Governing requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm latest status is independent `GO` before any protected edit and file the implementation report through the numbered bridge chain. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Read back the exact active WI-5602 PAUTH and require exact project, work-item, and target-path coverage. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run both focused pytest modules and report observed results for independent verification. |
| Retired-surface non-recreation boundary | Assert the retired prefix is absent from the live allowlist and path recognizer and is not accepted as an unprotected write target. |
| Python quality | Run `ruff check`, `ruff format --check`, and `git diff --check` on the four approved paths. |

## Risk And Rollback

Risk is low to moderate because removing an allowlist entry can expose hidden
callers that depended on the stale behavior. Focused tests and a repository
search bound that risk. Rollback is a focused revert of only the four approved
implementation paths under separate authority. Bridge and MemBase audit
records remain append-only.
