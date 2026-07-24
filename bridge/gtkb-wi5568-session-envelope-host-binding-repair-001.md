NEW
::init gtkb pb
::open build

# Defect-Fix Proposal - Session-stated role override not honored after context-refresh SessionStart re-derivation

bridge_kind: prime_proposal
Document: gtkb-wi5568-session-envelope-host-binding-repair
Version: 001
Date: 2026-07-24 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


Project Authorization: PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-WI5568-RUNTIME-20260724
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-5568

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_claim_cli.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The SessionStart envelope-open command currently creates a timestamp-derived
session document even when the Codex host exposes a stable CODEX_THREAD_ID.
A later SessionStart-like refresh can therefore bypass the original exact
transcript-role document and re-derive durable-registry fallback authority.
The existing attest-author-metadata command repairs the mismatch after the
fact, but that is not a runtime persistence guarantee.

WI-5568 will bind an initial valid Codex host task ID to its first envelope
document and resume that exact open document on a later host-identical refresh.
It will preserve the original transcript-derived Prime Builder or Loyal
Opposition role, reject contradictory role-bearing refresh input without
overwriting the document, and prove that bridge-claim provenance resolves from
the exact host document without a manual attestation workaround.

## Defect / Reproduction

1. Set CODEX_THREAD_ID to a stable task identifier and invoke
   gt session envelope open with ::init gtkb pb.
2. The current CLI does not consume CODEX_THREAD_ID and calls open_session
   without a session_id, so the result has a timestamp-derived identifier.
3. Invoke envelope open again in the same host context without a role-bearing
   init marker. The current path creates a new envelope and may use
   durable-registry fallback instead of the prior transcript-derived role.
4. The later attest-author-metadata rebind can create the missing exact
   document, demonstrating the gap but not preventing the first re-derivation.

The regression is reproduced by focused temporary-project CLI tests; no
production harness state is used as test input.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`, `platform_tests/scripts/test_session_envelope_cli_provenance.py`, `platform_tests/scripts/test_bridge_claim_cli.py`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - requires the independent GO, work claim,
  implementation-start packet, and LO-only terminal verification.
- DCL-SESSION-ROLE-RESOLUTION-001 - requires transcript-defined interactive
  role authority to outlive refresh and registry fallback to remain non-binding
  when that evidence exists.
- ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001 - requires transcript role
  persistence through compaction, resume, and SessionStart-like boundaries.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and
  DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - require the concrete
  specification and PAUTH/project/WI links in this proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - requires the focused
  behavior and claim regressions before VERIFIED.
- GOV-STANDING-BACKLOG-001 - makes WI-5568 the authoritative work unit.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001,
  ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, and
  DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - require this owner decision, PAUTH,
  proposal, report, and verification chain.

## Prior Deliberations

- `DELIB-20260724-WI5568-RUNTIME-SCOPE-AUTHORIZATION` - owner authorizes
  only this host-binding, refresh-persistence, and focused regression scope.

## Owner Decisions / Input

- `DELIB-20260724-WI5568-RUNTIME-SCOPE-AUTHORIZATION` records the owner
  approval received in this session.
- `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-WI5568-RUNTIME-20260724` is active,
  includes only WI-5568 and source/test/governance-evidence mutation classes,
  and forbids broad role-authority purge and unrelated worktree changes.

## Proposed Scope

1. In cli_session_handoff.py, validate a non-empty single-line
   CODEX_THREAD_ID when it is present for the Codex harness. Bind the first
   role-bearing envelope-open to that exact session ID rather than a
   timestamp-derived ID.
2. Before any fallback role derivation, load the exact open host-keyed
   envelope. When the refresh provides no conflicting explicit role/subject
   assertion, return or resume the existing document unchanged in authority
   fields. When it conflicts, fail before writing either projection.
3. Preserve the current non-Codex and no-host-ID behavior. Do not treat a
   shared projection, a legacy global marker, or a different session document
   as host-session authority.
4. Add focused envelope CLI tests for initial host binding, refresh
   persistence without a repeated init marker, and conflicting refresh
   rejection. Add a focused bridge-claim regression proving the host-bound
   document supplies Prime Builder provenance.
5. Do not modify session/envelope.py unless the bounded CLI implementation
   cannot use its existing exact-session read/write APIs; any such expansion
   requires a revised proposal and fresh LO review.

## Requirement Sufficiency

Existing requirements sufficient. The WI-5568 defect record,
DELIB-20260724-WI5568-RUNTIME-SCOPE-AUTHORIZATION, active PAUTH, and the
cited role-persistence and bridge specifications define the required behavior
and verification. No revised requirement is needed before implementation.

## Bridge Filing

This proposal is filed as the next numbered, versioned bridge artifact at
bridge/gtkb-wi5568-session-envelope-host-binding-repair-001.md. The bridge
chain is append-only: no prior numbered file is deleted, replaced, or
rewritten.


## Specification-Derived Verification Plan

| Requirement / property | Focused verification | Expected result |
| --- | --- | --- |
| Initial host binding | Envelope CLI test with CODEX_THREAD_ID and ::init gtkb pb | Returned and authoritative session ID equal the host ID; provenance is transcript-derived Prime Builder |
| Refresh persistence | Invoke envelope open again for the same host without an init marker | Exact prior envelope remains the authority; no durable-registry fallback replaces its role |
| Conflict fail-closed | Reopen same host with contradictory ::init gtkb lo | Nonzero result; authoritative document and projection remain byte-identical |
| Claim interoperability | Focused bridge-claim CLI test using the host ID | Claim resolves Prime Builder provenance from the exact session document without attest-author-metadata |
| Existing envelope CLI behavior | python -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py -q | Pass |
| Claim behavior | python -m pytest platform_tests/scripts/test_bridge_claim_cli.py -q | Pass |
| Quality | python -m ruff check and python -m ruff format --check on the three target paths | Pass |
| Change hygiene | git diff --check on the three target paths and live bridge/clause preflights | Pass with no blocking gaps |

## Acceptance Criteria

1. A valid Codex host task ID is the authoritative session ID from first
   role-bearing envelope-open, without a separate metadata-attestation rebind.
2. A same-host SessionStart-like refresh without a new role assertion
   preserves the original transcript-derived role and exact session document.
3. A conflicting refresh fails before changing the exact document or shared
   projection.
4. Bridge claim provenance resolves from the host-bound Prime Builder document.
5. Only the three declared files are changed, all focused tests and quality
   gates pass, and no broad role-authority purge is folded into this repair.

## Risks / Rollback

Primary risk is treating a shared current projection as session authority and
thereby reintroducing cross-session clobbering. The repair must read only the
exact host-keyed document and fail closed on conflicts. A second risk is
changing behavior for non-Codex or host-ID-absent runs; regression tests must
preserve their existing fallback behavior.

Rollback is a single scoped commit reverting only the three declared paths.
Do not revert, rewrite, or absorb prior envelope, bridge, deliberation, or
unrelated worktree artifacts.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`

## Recommended Commit Type

`fix`
