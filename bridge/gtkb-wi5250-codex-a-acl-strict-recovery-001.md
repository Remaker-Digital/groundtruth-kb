NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: gpt-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled and untouched
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5250-codex-a-acl-strict-recovery
Version: 001
Date: 2026-08-01 UTC
Supersedes strict-invalid chain: bridge/gtkb-wi5250-codex-a-dispatch-readiness-001.md through bridge/gtkb-wi5250-codex-a-dispatch-readiness-020.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250

target_paths: [".codex"]

implementation_scope: configuration metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: none

# WI-5250 Strict Recovery — Exact `.codex` Root ACL Repair

## Recovery Claim

The historical WI-5250 thread cannot accept a lawful successor. Strict
lifecycle resolution rejects version 008 because its `Responds to:` value adds
the annotation `(REVISED)` instead of exactly naming version 007. The numbered
history remains immutable and is retained as evidence only.

This fresh proposal restores the exact bounded repair approved in historical
versions 017 and 018 against the current live ACL state. It also cites the
owner's current exact implementation approval,
`DELIB-20260801-WI5250-EXACT-IMPLEMENTATION-APPROVAL`.

No ACL or other target mutation is authorized by this proposal alone. Prime
Builder must receive a fresh independent `GO`, hold this exact thread claim,
and pass schema-v3 implementation-start authorization for exact `.codex`
before the one permitted metadata write.

## Current Live Evidence

Read-only Check mode was executed through the canonical helper:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/repair_codex_dotdir_acl.ps1 -ProjectRoot E:/GT-KB -Mode Check -Json
```

Observed result:

- target: exact `E:/GT-KB/.codex`;
- checked objects: `223`;
- read errors: `0`;
- risky Deny rules: exactly `2`;
- both rules are non-inherited and attached to exact `.codex` for SID
  `S-1-5-21-2908765920-875073000-2352713335-4168283502`;
- rule 1: rights
  `DeleteSubdirectoriesAndFiles, Write, Delete, ReadPermissions, Synchronize`,
  inheritance `None`, propagation `None`;
- rule 2: rights `1074987350`, inheritance
  `ContainerInherit, ObjectInherit`, propagation `InheritOnly`;
- required current-user Modify allow is present for
  `DESKTOP-G6Q5ANI\micha` / SID
  `S-1-5-21-955887351-2727327028-1487890216-1001`;
- required sandbox Modify allow is present for `CodexSandboxUsers` / SID
  `S-1-5-21-955887351-2727327028-1487890216-1003`;
- `needs_repair=true`.

Fresh `python scripts/verify_codex_dispatch.py --json` independently reports
`codex_dotdir_acl_ok=false`, `static_dispatchable=false`, and
`dispatchable=false`. It reports `can_receive_dispatch=true`, but the separate
no-window proof is expired (`codex_no_window_verification_expired`). This
proposal repairs only the ACL fact and must not claim or renew full live
dispatchability.

## Exact Authorized Operation

1. Re-run canonical Check mode immediately before mutation and fail closed
   unless the exact precondition above still holds: two matching root rules,
   zero descendant risky rules, zero errors, and both required allows present.
2. Read exact `.codex` with `Get-Acl` and hold the complete security descriptor
   in memory for bounded rollback.
3. Fingerprint every root ACE using identity, access-control type, rights,
   inheritance flags, propagation flags, and inherited state; also capture the
   owner and inheritance-protection state.
4. Select only the two exact non-inherited Deny `FileSystemAccessRule` objects
   for the stated SID. Stop without writing if the selected count or any rule
   fingerprint differs from the live evidence.
5. Clone the descriptor in memory and call `RemoveAccessRuleSpecific` once for
   each of the two selected rule objects.
6. Before writing, prove both target fingerprints are absent, all non-target
   fingerprints are unchanged, both required Modify allows remain present,
   and no ACE was added.
7. Apply that descriptor once with `Set-Acl -LiteralPath E:/GT-KB/.codex`.
8. Immediately read back exact `.codex`; require zero target fingerprints,
   equality of every non-target fingerprint, unchanged owner and
   inheritance-protection state, and both required allows.
9. Re-run canonical Check mode and `verify_codex_dispatch.py --json` read-only.
   Require ACL readiness true and report the separate no-window result exactly
   as observed without renewal or overstatement.
10. File a canonical implementation report with before/after fingerprint
    counts and exact bounded results for independent verification.

## Bounded Rollback

If immediate readback shows any non-target ACE, owner,
inheritance-protection, or required-Allow change, restore the complete original
in-memory descriptor once with `Set-Acl`, verify that restoration, and file a
blocker report. Rollback does not authorize recursion, descendant writes, or
speculative normalization.

## Explicit Exclusions

- No recursive ACL operation and no `.codex` descendant ACL or file-content
  mutation.
- No `SetAccessRule`, `ResetAccessRule`, inheritance-changing API, raw-SID
  `icacls /remove:d`, or retry of the disproven historical mechanism.
- No dispatcher or TAFE configuration, activation, routing, ranking,
  eligibility, roles, models, caps, state, leases, locks, workers, process
  control, proof renewal, harness invocation, reoffer, or provider call.
- No Git staging, commit, push, history rewrite, cleanup, credentials,
  deployment, release, external-system mutation, or unrelated worktree
  adoption.
- All generated artifacts and the numbered bridge file remain in-root under
  `E:/GT-KB`; no artifact is created or required outside the project root.

This proposal performs no KB or MemBase mutation, does not create or update any
specification, work item, test record, deliberation, project, authorization, or
other `groundtruth.db` row, and therefore does not include `groundtruth.db` in
`target_paths`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20260801-WI5250-EXACT-IMPLEMENTATION-APPROVAL` records the owner's
  current approval of WI-5250 as written.
- `DELIB-202666203` authorizes governed restoration of Codex A readiness while
  preserving bridge and dispatcher-state boundaries.
- `DELIB-202666274` is the owner decision behind the active project PAUTH.
- Historical versions 017 and 018 define and independently approve the exact
  two-rule root repair; versions 019 and 020 establish that `NO-ACTION` did not
  close it.
- WI-5571 / TEST-11622 separately own recurrence causation and durability.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No further owner decision is required for this proposal. The exact WI-5250
implementation is approved, and the active project PAUTH version 2 allows the
configuration-metadata class while preserving the independent GO, claim,
implementation-start, nonimpairment, and independent verification gates.

The owner's dispatcher/TAFE hold remains binding. Neither runtime will be
enabled, reconfigured, or mutated by this work.

## Requirement Sufficiency

Existing requirements are sufficient. The current ACL state exactly activates
the correction branch previously approved by independent review; the separate
durability question remains in WI-5571 and does not broaden this repair.

## Specification-Derived Verification

| Requirement | Executed evidence required in the implementation report |
| --- | --- |
| `TEST-11404`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Exact-root post-check reports zero risky Deny rules, zero errors, both required allows, and ACL readiness true. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Exactly two target rule fingerprints disappear; every non-target ACE, owner, and protection property remains equal. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Read-only evidence confirms A remains Prime Builder only. |
| Bridge and project-authorization specifications | Fresh independent GO, exact claim, and schema-v3 implementation-start precede the write. |
| Dispatcher control specifications | All dispatcher observations are read-only; configuration/topology remain untouched. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reproduces fingerprint equality, Check-mode result, and honest readiness classification before terminal verdict. |

## Acceptance Criteria

- The exact precondition remains current at operation time.
- Exactly the two named root Deny objects are removed.
- Every non-target ACE, owner, protection state, and required allow is unchanged.
- Canonical post-check reports zero risky denies and zero errors.
- The readiness verifier reports ACL truth and the separate no-window state
  without renewal or overstatement.
- No excluded surface or operation is touched.
- Independent Loyal Opposition verification remains required.

## Risk

ACL edits can broaden or impair access if object selection is imprecise. Exact
rule-object selection, complete before/after fingerprints, one root write,
immediate readback, and the bounded in-memory rollback constrain that risk.
The larger operational risk—rule recurrence—remains explicitly assigned to
WI-5571 rather than being falsely declared solved here.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
