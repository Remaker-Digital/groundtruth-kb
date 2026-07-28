NEW
::init gtkb pb
::open build

# WI-5659 Protected-Commit Finalizer Reconciliation v2

bridge_kind: prime_proposal
Document: gtkb-wi5659-protected-commit-finalizer-reconciliation-v2
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-28 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Create one strict-lifecycle recovery chain for independent verification and
backlog reconciliation of WI-5659's already-landed protected-commit finalizer
repair. This proposal performs no source, test, registry, or KB mutation. The
two declared target paths are by-reference inspection and test subjects only.

The immutable implementation commits are:

- `f0b27999a2a39d8465fbb7e9fb5c3dda07d635eb` - restore governed commit
  finalization through the four owner-authorized WI-5659 mechanisms.
- `c0c4c40e4347e4462c3eaf7b4f3b8ac6881b920a` - bound mechanism 4 to the
  authorized audit-scratch subtree.

Both commits resolve, and `c0c4c40e4` is an ancestor of current HEAD. This
proposal authorizes no rewrite, restaging, revert, or competing implementation.

## Why A Clean Thread Is Required

Two preserved historical threads cannot accept another valid version:

1. Strict resolution of
   `gtkb-wi5659-checker-verified-evidence-prefilter` fails at version 024:

   ```text
   WRONG_STATUS_AUTHOR_ROLE
   Status REVISED has wrong or unreadable author role None:
   bridge/gtkb-wi5659-checker-verified-evidence-prefilter-024.md
   ```

2. Strict candidate publication on
   `gtkb-wi5659-protected-commit-finalizer-repair` fails at version 001:

   ```text
   WRONG_STATUS_AUTHOR_ROLE
   Status NEW has wrong or unreadable author role None:
   bridge/gtkb-wi5659-protected-commit-finalizer-repair-001.md
   ```

Governed publication attempts against both threads failed before writing a new
bridge file. Their temporary claims were released. Appending cannot repair an
invalid historical predecessor, and editing append-only audit bytes is not
permitted. The resolved WI-5648 invalid-chain precedent requires a fresh clean
replacement thread.

This v2 thread begins with current resolver-readable Prime Builder metadata and
is the sole proposed operative recovery authority. Both old threads remain
immutable incident evidence.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` and WI-5648
require a fresh chain for structurally invalid append-only history.
`DELIB-202667191` authorizes a narrow by-reference finalization route while
preserving independent review and end-to-end staged authorization. No new
source behavior or owner choice is introduced.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - strict numbered lifecycle authority and
  role-correct status authorship.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve both invalid historical
  chains and this recovery chain as durable evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - use a new governed artifact rather
  than editing history.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - leave WI-5659 open until terminal
  verification exists.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - retain exact PAUTH,
  project, work-item, and target linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - map each cited
  authority to concrete checks.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - require fresh executed
  evidence before VERIFIED.

## Prior Deliberations And Evidence

- `DELIB-202667191` - narrow by-reference finalization with independent staged
  authorization.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-024.md` - historical
  implementation report with unreadable role metadata; immutable evidence.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-028.md` - complete
  historical implementation receipt.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-029.md` - operational
  hold, explicitly not an implementation rejection.
- `bridge/gtkb-wi5659-protected-commit-finalizer-repair-002.md` - NO-GO that
  rejected a competing retroactive implementation proposal.
- `WI-5648` - resolved invalid-chain incident establishing clean replacement
  rather than mutation of historical chain bytes.

## Owner Decisions / Input

No new owner decision is required. The active PAUTH is an exact singleton for
WI-5659 and the two source/test subjects. This proposal narrows execution to
inspection, testing, report publication, independent verification, and terminal
backlog reconciliation.

## Proposed Recovery Sequence

1. Loyal Opposition independently reviews this recovery design and files GO or
   NO-GO.
2. After GO, Prime Builder performs no source or test mutation. It reruns the
   approved verification commands and files a `NO-ACTION` implementation
   report on this v2 thread with exact commit ancestry and command results.
3. An independent Loyal Opposition session inspects the immutable diffs and
   reruns the required verification families.
4. If correct, that reviewer uses the canonical terminal wrapper to create and
   atomically commit VERIFIED on this v2 thread.
5. Only after commit-backed VERIFIED may WI-5659 be marked resolved with exact
   verdict and commit evidence.

Expected lifecycle:

```text
NEW -001 -> GO -002 -> NO-ACTION -003 -> VERIFIED -004
```

## Current Reproducible Evidence

### Historical chain rejection

Direct strict resolution and governed candidate publication reproduce the two
`WRONG_STATUS_AUTHOR_ROLE` failures above. Neither failed publication created a
new bridge artifact, and both claims were released.

### Historical operational hold cleared

```powershell
Test-Path -LiteralPath .git\index.lock
```

Result: `False`. No lock was removed, overwritten, or bypassed.

### Complete focused module

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_protected_commit_authorization.py -q --no-header --tb=short
```

Result: exit `0`; `146 passed, 1 warning in 95.78s`. The warning is the existing
unknown pytest option `asyncio_mode`; there were no failures, errors, skips, or
timeouts.

### Commit identity and ancestry

Both exact implementation commits resolve. `git merge-base --is-ancestor
c0c4c40e4 HEAD` exits `0`.

## Scope Boundaries

This proposal performs no KB mutation.

- No source or test mutation.
- No MemBase, `groundtruth.db`, registry declaration, projection, or journal
  mutation before terminal backlog reconciliation.
- No edit, deletion, replacement, or renumbering of either invalid historical
  chain.
- No Git history rewrite, push, release, deployment, credential action, or
  dispatcher activation.
- No absorption of WI-5657, WI-5658, WI-5441, WI-5704, WI-5705, or WI-5706.

## Files Expected To Change

None during recovery execution. This v2 bridge chain is the only new audit
artifact sequence.

## By-Reference Verification Subjects

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

These paths MUST NOT be modified or restaged by this recovery. Their committed
diff, ancestry, and runtime behavior remain fully reviewable.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict resolver passes on this v2 chain and continues to reject both old chains; status authorship and transitions match NEW, GO, NO-ACTION, VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Old chains remain byte-identical incident evidence; v2 contains the complete recovery decision and results. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5659 remains open before commit-backed VERIFIED and is resolved only afterward. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live PAUTH lookup confirms active exact-singleton WI-5659 scope and the two by-reference subjects. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and clause preflights report no missing required/advisory specification and no blocking clause gap. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent reviewer inspects both immutable commit diffs and reproduces the full focused suite plus terminal staged checker. |

## Acceptance Criteria

- [x] Strict reproducible evidence proves both historical threads cannot accept
  a valid continuation.
- [x] This v2 thread is recovery-only and claims no retroactive source
  implementation authority.
- [x] Immutable commits and exact by-reference subjects are identified.
- [x] Historical lock is absent and the full focused suite is green.
- [x] Finite valid lifecycle and terminal boundary are explicit.
- [ ] Manual independent GO remains pending.
- [ ] Post-GO NO-ACTION report and independent commit-backed VERIFIED remain
  pending.

## Risk And Rollback

The principal risk is treating recovery GO as permission to rewrite landed
source. The zero-mutation sequence, by-reference subjects, and mandatory
NO-ACTION report prevent that. If review rejects this design, append a revision
to this valid v2 chain; do not modify source commits or historical bridge files.

## Recommended Commit Type

chore
