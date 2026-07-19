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


# Revised Implementation Proposal - Correct WI-5370 archive-pilot PAUTH to registered operation vocabulary

bridge_kind: prime_proposal
Document: gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary
Version: 003
Responds to: bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-002.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5635

target_paths: ["groundtruth.db"]

implementation_scope: metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

Correct the exact machine-readable scope defect identified by the independent
NO-GO while preserving the approved repair direction. WI-5635 is a governed,
append-only MemBase project-authorization metadata transaction against
`groundtruth.db`. It authorizes no source or test file mutation and does not
execute the WI-5370 archive service.

The implementation will append one successor version of
`PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719` through the
canonical `gt projects authorize` transaction. The successor replaces only the
unregistered machine forbidden-operation labels with registered taxonomy IDs,
preserves every substantive restriction, and proves the corrected envelope
admits only the already-approved WI-5370 40-path start packet.

## Findings Addressed

### F1 (P1) - The proposal declares a PAUTH/MemBase mutation as source work with no KB mutation

Accepted and corrected. The machine-readable metadata now declares:

```text
target_paths: ["groundtruth.db"]
implementation_scope: metadata
kb_mutation_in_scope: true
```

The scope, verification, risk, rollback, and expected-change sections now state
that this transaction is an append-only MemBase/PAUTH metadata mutation. They
explicitly authorize no source or test changes. The prior contradictory
source-work language is removed.

## Scope Changes

The implementation boundary is exactly:

1. Read back version 1 of
   `PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719`.
2. Append version 2 through the canonical `gt projects authorize` transaction,
   preserving the same PAUTH ID, project, owner decision `DELIB-202666766`,
   `WI-5370` membership, included specifications, active status, no expiry,
   allowed mutation classes, and bounded scope.
3. Replace the machine forbidden-operation array with only these registered
   IDs: `credential_lifecycle`, `dispatcher_mutation`,
   `external_system_mutation`, `git_history_rewrite`, `git_push`,
   `production_deployment`, and `release`.
4. Preserve secret disclosure, direct harness contact, provider requests,
   dispatcher configuration/role/identity/ranking/routing mutation, external
   mutation, history rewrite, push, deployment, release, a second archive
   batch, broad cleanup, and unrelated mutation as binding `scope_summary`
   prohibitions where no one-to-one registered operation ID exists.
5. Acquire and release a fresh exact WI-5370 claim only long enough to run
   `implementation_authorization.py begin --no-write` for the approved 40
   target paths and the negative widening/forbidden-operation probes.

The transaction does not run the archive service, remove source artifacts,
create archive artifacts, mutate source or test files, alter dispatcher/TAFE
configuration or runtime state, contact a harness or provider, mutate
credentials, stage or commit Git state, push, deploy, release, or touch
unrelated bytes.

`git_commit` is not added to the successor pilot PAUTH forbidden-operation
array because the separately approved WI-5370 pilot requires one exact
pathspec-limited local commit. `destructive_cleanup` is not added because the
separately approved archive-preserve transaction removes only the exact
byte-preserved source artifacts after commit success. Neither operation occurs
under WI-5635.

## Requirement Sufficiency

Existing requirements are sufficient. This revision corrects proposal
classification; it does not seek a requirement waiver or broaden the project
authorization.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-202666766` - owner decision authorizing the bounded WI-5370 terminal
  archive pilot PAUTH.
- `DELIB-202666774` - WI-5370 sprawl reconciliation owner decisions and
  findings.
- `DELIB-202666247` - prior PAUTH registered-vocabulary verification lineage.
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-002.md` - independent
  GO for the exact archive pilot that the PAUTH correction unblocks.
- `bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-002.md`
  - independent NO-GO requiring honest metadata/KB mutation classification.

## Owner Decisions / Input

- `DELIB-202666766` remains the owner decision for the exact bounded WI-5370
  pilot PAUTH.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` is active,
  project-wide, permits governed bridge and metadata work, and prohibits
  dispatcher mutation, credentials, Git commit/push/history rewrite,
  destructive cleanup, external mutation, deployment, and release.
- No new owner decision is required. This revision narrows the proposal to the
  actual PAUTH metadata transaction requested by WI-5635.

## Pre-Filing Preflight Subsection

Both candidate preflights passed against this completed revision:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md
```

Observed applicability result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
blocking_errors: []
declared_target_paths:
- groundtruth.db
packet_hash: sha256:e53374e3fc5ceda14bee853a189a1c37bbbb8e4d981ad2efc9148c841a3d0feb
```

Observed clause result:

```text
Clauses evaluated: 5
must_apply: 4
may_apply: 1
not_applicable: 0
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
Exit code: 0
```

## Specification-Derived Verification Plan

| Specification | TEST-11680 evidence |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exact before/after PAUTH readback; every machine operation resolves through the canonical taxonomy; exact 40-path no-write begin returns `authorized=true`; widened targets and forbidden operations return denied. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Version 2 preserves the PAUTH ID, project, owner decision, WI/spec membership, allowed classes, active/no-expiry state, and bounded scope while changing only registered forbidden-operation IDs plus clarifying scope text. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Prove independent WI-5635 GO, exact claim, and implementation-start packet before the metadata transaction; separately prove WI-5370 still requires its own exact claim/start authorization. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and proposal-linkage specifications | Candidate and live applicability/clause preflights pass; the implementation report responds to the operative GO and preserves the complete numbered chain. |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` and `GOV-WORK-TREE-HYGIENE-001` | Compare the no-write authorization probe with the already-approved exact 40-path pilot scope. Do not run the archive service during WI-5635. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm the only mutated target is in-root `groundtruth.db`; no adopter or external path is touched. |

## Acceptance Criteria

- The current PAUTH readback is append-only version 2 and exactly preserves
  ID, project, owner decision, WI-5370 membership, included specs, allowed
  classes, active status, no expiry, and the pilot's bounded scope.
- Every machine forbidden-operation token resolves through
  `config/governance/project-authorization-operation-taxonomy.toml`, while all
  unmatched substantive restrictions remain explicit in `scope_summary`.
- TEST-11680 passes: a valid exact WI-5370 claim plus no-write implementation
  start returns `authorized=true` for exactly the approved 40 paths; widened
  targets and forbidden operations remain denied; the claim is released.
- No archive service, source/test mutation, source removal, archive creation,
  Git staging/commit/push, dispatcher/TAFE/runtime/configuration change,
  harness/provider contact, credential operation, deployment, release, or
  unrelated mutation occurs.

## Risks / Rollback

Risk is moderate because a project-authorization envelope controls later
protected operations. The implementation fails closed if the current PAUTH
readback differs from the approved predecessor, any registered token fails
taxonomy resolution, the exact target or preserved fields drift, the negative
probes authorize widening, or claim/start authority is absent.

PAUTH history is append-only. Rollback does not rewrite or delete version 2.
If verification rejects the successor, file a separately governed version 3
that restores the last accepted machine envelope while preserving the audit
chain. No source/test rollback is applicable because WI-5635 authorizes no
source or test mutation.

## Files Expected To Change

- `groundtruth.db` only, through the canonical project-authorization metadata
  transaction.

## Recommended Commit Type

No Git commit under WI-5635. `groundtruth.db` is not staged or committed.
