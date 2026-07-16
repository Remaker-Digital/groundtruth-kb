NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; reasoning xhigh

# Implementation Proposal - Separate declared target scope from applicability path evidence

bridge_kind: prime_proposal
Document: gtkb-wi5363-applicability-scope-semantics
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5363-APPLICABILITY-SCOPE-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5363

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight_scope_semantics.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct bridge applicability packets so target_paths is the exact declared mutation scope while conservative document-wide path evidence is separately normalized and retained for specification applicability.

Work item description: scripts/bridge_applicability_preflight.py currently stores the document-wide repo-rooted path scan under packet.target_paths. On WI-5361 this expands three declared implementation targets into nine entries, including verification-only paths and malformed Markdown tokens such as bridge/ and bridge paths ending in a backtick. Preserve conservative path-driven specification applicability, but expose exact declared target_paths separately from normalized cited/applicability path evidence so reviewers and downstream evidence cannot mistake prose citations for authorized mutation scope. The packet hash and Markdown output must carry the distinction, missing-parent warnings must remain limited to deliberate implementation fields, and existing applicability matches must not regress.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5363` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_applicability_preflight.py`, `platform_tests/scripts/test_bridge_applicability_preflight_scope_semantics.py`.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `GOV-SOT-SINGLETON-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666310` - Loyal Opposition GO Verdict - Dispatcher Black-Box Specification Foundation
- `DELIB-202666285` - Loyal Opposition NO-GO Verdict - Dispatcher Black-Box Spec Foundation V2
- `DELIB-20263315` - WI-4500–4503: TAFE Flow-Type Lifecycle Coverage (operation, remediation, deliberation, report)
- `DELIB-20265740` - Loyal Opposition GO verdict - WI-4701 Codex adapter CRLF whitespace fix
- `DELIB-202665281` - Finalization Tooling Batch — Review Verdict

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5363-APPLICABILITY-SCOPE-20260716` - active project authorization covering `WI-5363`.

## Proposed Scope

- Extract explicit target_paths into an exact declared-scope set without document-wide prose harvesting.
- Retain the conservative document-wide repository-path scan as a separately named applicability path set and continue using it for path-triggered specification relevance.
- Normalize cited path tokens through one parser so Markdown backticks and synthetic root-only bridge tokens are not emitted.
- Keep missing-parent warnings limited to explicit target declarations and Files Changed fields.
- Add regression coverage in a new isolated test module; do not modify or adopt the current WI-5254/WI-5330 hunks in platform_tests/scripts/test_bridge_applicability_preflight.py.
- Sequence the source edit after the independently verified WI-5330 source hunk is safely finalized or otherwise governed as a clean dependency; do not overwrite or absorb it.
- Do not mutate dispatcher configuration, runtime state, eligibility, workers, leases, TAFE internals, credentials, Git history, push, deployment, or release.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run the new scope-semantics tests against a proposal containing explicit targets, cited bridge artifacts, and verification command paths; assert exact declared scope and unchanged applicable specs. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require latest independent GO, matching claim, active exact PAUTH, successful implementation-start packet, NEW implementation report, and independent VERIFIED focused finalization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run both platform_tests/scripts/test_bridge_applicability_preflight_scope_semantics.py and platform_tests/scripts/test_bridge_applicability_preflight.py plus focused Ruff check and format check. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Before implementation read back the WI-5330 thread, claim state, and git diff; prove no foreign source/test hunk is overwritten, adopted, staged, or committed. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Re-run the WI-5361 applicability packet and show declared target_paths and applicability paths from current files rather than cached output. |
| `GOV-SOT-SINGLETON-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A WI-5361-shaped fixture with three explicit targets, bridge citations, and verification paths reports exactly three target_paths.
- The same packet reports normalized applicability path evidence separately, with no trailing backticks and no synthetic bridge root token.
- Path-triggered applicable specifications remain identical to the conservative pre-fix scan.
- Missing-parent warnings remain limited to deliberate implementation fields.
- The existing applicability preflight suite and the new focused scope-semantics tests pass with Ruff checks.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py`
- `platform_tests/scripts/test_bridge_applicability_preflight_scope_semantics.py`

## Recommended Commit Type

`feat`
