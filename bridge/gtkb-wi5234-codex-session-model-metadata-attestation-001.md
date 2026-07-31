NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive; reasoning_effort=xhigh; sandbox=none
author_metadata_source: codex-x-codex-turn-metadata

# Implementation Proposal - Populate Codex bridge-filing author model metadata from the live session envelope

bridge_kind: prime_proposal
Document: gtkb-wi5234-codex-session-model-metadata-attestation
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5234

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/bridge_author_metadata.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_author_metadata.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Project host request metadata into an exact session-scoped envelope through a governed CLI, then consume only that matching envelope for Codex bridge author provenance.

Work item description: During WI-5233 proposal filing, gt bridge file-implementation-proposal failed closed because scripts/bridge_author_metadata.py could resolve Codex A identity and session context but the live harness-state/codex/session-envelope.json carried model_id/model_version as unknown and no GTKB_AUTHOR_MODEL metadata was present. The helper supports GTKB_AUTHOR_* env overrides, but Codex startup/envelope metadata should provide non-placeholder author_model, author_model_version, and author_model_configuration so governed bridge filing works without ad hoc caller injection.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5234` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`, `scripts/bridge_author_metadata.py`, `platform_tests/scripts/test_session_envelope_cli_provenance.py`, `platform_tests/scripts/test_bridge_author_metadata.py`.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263247` - WI-4522 Revised Proposal Review Verdict
- `DELIB-20263246` - WI-4522 Implementation Verification Verdict
- `DELIB-20266652` - Review Independence
- `DELIB-20266660` - Review Independence
- `DELIB-20263483` - WI-4522 Author Identity Env Alias Defect

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5234`.

## Proposed Scope

- Add a governed gt session envelope author-metadata attestation command that accepts only non-placeholder Codex turn metadata for the exact matching open session id.
- Persist the attestation through existing write_current semantics so the exact per-session envelope and compatibility projection agree, without changing session/envelope.py.
- Load model metadata only from the exact per-session envelope selected by the filing runtime session id; never read a shared current baseline or another session.
- Preserve explicit and environment precedence for headless/provider writers and retain fail-closed behavior when no exact trusted runtime carrier exists.
- Add focused CLI and loader regressions for success, stale or mismatched session rejection, closed or placeholder metadata rejection, and concurrent-session isolation.

## Cross-Harness Disposition

- **claude**: unchanged; Claude keeps its existing native runtime metadata carrier and receives no target-path change.
- **cursor**: unchanged; no Codex x-codex-turn-metadata surface is asserted for Cursor.
- **antigravity**: unchanged; provider-specific metadata publication remains outside this Codex slice.
- **ollama-openrouter-alibaba**: unchanged; existing headless environment metadata remains authoritative.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Run focused CLI and loader tests proving exact per-session model provenance and fail-closed rejection. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge author-metadata tests proving the governed writer receives complete metadata without bypass or shared baseline. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute all declared focused tests plus Ruff check and format checks on changed Python files. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A Codex caller can pass its host-provided x-codex-turn-metadata through the governed CLI, after which load_author_metadata returns exact session, model, model-version, and reasoning configuration fields with no guessed value.
- A stale, closed, wrong-harness, mismatched-session, placeholder, or cross-session envelope cannot authorize a bridge filing.
- Existing headless and provider environment metadata paths remain behaviorally unchanged.
- No dispatcher, TAFE, harness registry, credential, Git, release, deployment, shared scratch, or source-of-truth surface outside the four declared targets is mutated.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- `scripts/bridge_author_metadata.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- `platform_tests/scripts/test_bridge_author_metadata.py`

## Recommended Commit Type

`feat`
