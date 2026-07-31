NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never
author_metadata_source: codex-inline-non-bypass-writer

# Implementation Proposal - Fail closed when filed hunk artifact bytes are not Git-applyable

bridge_kind: prime_proposal
Document: gtkb-wi5401-hunk-patch-integrity-gate
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5401-HUNK-PATCH-INTEGRITY-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5401

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: configuration/source/test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5401 proposal to fail closed when filed hunk artifact bytes are malformed, byte-mismatched, or not Git-applyable before any report acceptance or VERIFIED terminal finalization relies on them.

Work item description: WI-5222 report version 003 records a 10079-byte hunk artifact, SHA-256 F890E23B..., and a passing disposable-index apply check, but the committed bridge/hunks/gtkb-wi5222-60m-envelope-successor-current-head.patch is 10058 bytes and git apply --check fails as corrupt at line 134. Add a filing/finalization integrity gate that hashes and sizes the exact stored bytes, parses the patch, and runs git apply --check or reverse-check against the declared baseline before accepting report or terminal evidence. Fail closed on mismatch or malformed hunks without touching source, runtime, TAFE, or dispatcher state.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5401` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/verify/helpers/write_verdict.py`, `.codex/skills/verify/helpers/write_verdict.py`, `.cursor/skills/verify/helpers/write_verdict.py`, `scripts/gtkb_bridge_writer.py`, `platform_tests/scripts/test_lo_verified_commit_atomicity.py`, `platform_tests/scripts/test_gtkb_bridge_writer.py`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
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
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.

## Prior Deliberations

- `DELIB-202666188` - WI-5220 - Dispatcher test fixture parity VERIFIED finalization
- `DELIB-202666259` - Loyal Opposition NO-GO Verdict - WI-5254 PAUTH Amendment Evidence Preflight
- `DELIB-202666178` - WI-5213 - Loyal Opposition Post-Implementation Verification: VERIFIED
- `DELIB-202666233` - Loyal Opposition Verification Verdict - WI-5229 Binary VERIFIED Finalizer Hunk Patch Support
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - Owner decision: WI-5210 hunk-scoped finalization waiver

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5401-HUNK-PATCH-INTEGRITY-20260717` - active project authorization covering `WI-5401`.

## Linked Tests

- `TEST-11512` - Filed hunk artifact integrity rejects malformed or byte-mismatched patches.

## Cross-Harness Disposition

- Claude Code: `.claude/skills/verify/helpers/write_verdict.py` is an applicable VERIFIED finalizer helper projection and must receive the same hunk-patch integrity behavior as Codex and Cursor; no typed waiver is requested.
- Codex: `.codex/skills/verify/helpers/write_verdict.py` is an applicable VERIFIED finalizer helper projection and must receive the same hunk-patch integrity behavior as Claude Code and Cursor; no typed waiver is requested.
- Cursor: `.cursor/skills/verify/helpers/write_verdict.py` is an applicable VERIFIED finalizer helper projection and must receive the same hunk-patch integrity behavior as Claude Code and Codex; no typed waiver is requested.
- Shared provider path: `scripts/gtkb_bridge_writer.py` must enforce the same hunk artifact integrity contract for provider publication before any harness-specific terminal finalization can rely on a hunk artifact.

## Proposed Scope

- Add exact hunk-patch artifact integrity validation to the VERIFIED finalizer helper projections and the provider bridge writer before reports or terminal finalization can accept hunk artifact evidence.
- Validate exact stored patch bytes against declared digest and size metadata when supplied, fail closed on mismatch, parse patch paths conservatively, and run git apply --check or reverse-check suitability against the declared baseline/disposable index before acceptance.
- Preserve valid text and binary patch support, include-set coverage, same-path hygiene, provider role and claim gates, and atomic disposable-index finalization.
- No database, bridge, dispatcher, TAFE, lease, eligibility, runtime, credential, external-system, Git history, push, deployment, release, destructive cleanup, or unrelated source/test/configuration mutation is authorized.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run focused finalizer and provider tests proving malformed, byte-mismatched, and non-applyable patch artifacts are rejected without committing or staging unrelated work, while valid patches still pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm proposal, report, and verdict chain uses numbered bridge files, exact GO, matching claim, and implementation-start packet before protected mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate/live applicability and ADR/DCL preflights with no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short with TEST-11512-bound regressions. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project, WI, PAUTH, target_paths, linked TEST-11512, and owner decision metadata are present in the packet. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Confirm the Cross-Harness Disposition section declares Claude, Codex, and Cursor helper parity with no typed waiver, then assert the three helper projections remain behaviorally aligned. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run scripts/implementation_authorization.py begin and confirm only the three helper projections, gtkb_bridge_writer, and two focused test files are authorized. |

## Acceptance Criteria

- Malformed or corrupt WI5222-style hunk artifacts are rejected before report acceptance or terminal finalization.
- Declared digest or size mismatches between report metadata and exact stored patch bytes are rejected fail-closed.
- Valid exact-byte text and binary patches still pass existing hunk finalization and provider-publication paths.
- Provider bridge writer refuses modified includes whose hunk artifact is malformed, byte-mismatched, or not Git-applyable while preserving same-path hygiene.
- Claude, Codex, and Cursor verify-helper projections remain behaviorally aligned and focused tests pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Recommended Commit Type

`feat`
