NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review
author_metadata_source: x-codex-turn-metadata

# WI-5657 Strict-Chain Terminal Recovery Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5657-terminal-finalization-recovery-v2
Version: 001
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5657-TERMINAL-RECOVERY-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5657

target_paths: ["bridge/gtkb-wi5657-terminal-finalization-recovery-v2-003.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

KB Mutation: This proposal performs no MemBase mutation.

---

## Summary

Recover WI-5657 through one new strict-resolver-valid bridge chain without
changing or re-staging its already-committed implementation. Commit
`7b838d9e7606a8b1f8be75ade78881f63beda170` is immutable, by-reference
implementation evidence. It contains the WI-5657 protected-commit checker fix,
its focused tests, and four historical bridge files.

All existing WI-5657 bridge threads remain unchanged as incident and audit
evidence. Their pre-enforcement author metadata makes them non-continuable under
the strict lifecycle resolver. This proposal starts a clean thread rather than
trying to append to, rewrite, delete, or reinterpret an invalid history.

After an independent GO, Prime Builder will file only the declared version-003
recovery report. That report will re-derive the immutable commit inventory and
record the existing implementation evidence. An independent Loyal Opposition
reviewer may then create version 004 through the canonical terminal VERIFIED
finalizer. A successful finalizer transaction is limited to the four files in
this new chain. After terminal verification, Prime Builder will separately
reconcile only WI-5657's canonical backlog metadata with the resulting evidence
through the canonical backlog lifecycle service. That post-terminal lifecycle
call is not a version-003 implementation target and does not place
`groundtruth.db` in this proposal's target set.

## Recovery Boundary

The active authorization permits only `bridge`, `governance_evidence`, and
`metadata` mutation classes. It permits one bounded local terminal-finalization
commit and WI-5657 backlog reconciliation. It does not authorize source, test,
configuration, registry, registry-projection, database schema, specification
content, or direct database-content mutation.

This proposal and its version-003 report perform no MemBase operation. The only
later MemBase operation permitted by the owner authorization is a canonical
service update of WI-5657 after terminal verification. No registry or
specification row may be changed.
No history rewrite, push, dispatcher action, release, deployment, credential
operation, external-system mutation, destructive cleanup, or specification
deletion is permitted.

## Historical Chain Disposition

The following historical threads are retained unchanged and authorize no new
work:

- `gtkb-wi5657-protected-commit-superseded-verified`
- `gtkb-wi5657-terminal-finalization-recovery`
- `gtkb-wi5657-terminal-finalization-audit-recovery`

Their files remain evidence of the original implementation and failed recovery
attempts. This new thread does not repair them in place. It also does not treat
their latest logical status as executable authority because the strict resolver
cannot establish a valid author role at the initial transition.

## By-Reference Finalization Waiver

`DELIB-202667519` explicitly authorizes the immutable commit as by-reference
implementation evidence and permits one bounded local canonical terminal
finalization. Therefore these already-committed paths MUST NOT be re-staged or
included in the recovery commit:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-001.md`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-002.md`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-003.md`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-004.md`

The waiver is only a finalization-mechanics boundary. It does not waive content,
inventory, test, review-independence, applicability, clause, candidate-hash, or
protected-commit verification.

The one prospective terminal commit may include only:

- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-001.md`
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-002.md`
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-003.md`
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-004.md`

Version 002 must be an independent GO or NO-GO. Version 003 is created only
after GO and is the sole Prime Builder implementation artifact in this scope.
Version 004 may be terminal VERIFIED only when the canonical helper creates it
and the local commit atomically; otherwise the helper must remove the partial
candidate and fail closed.

## Owner Decisions / Input

- `DELIB-202667519` records the owner's exact response, "Authorize WI-5657
  exactly as stated," and the complete recovery boundary used by the active
  PAUTH.
- `DELIB-202667182` authorized the original two-path source/test fix. It remains
  provenance for the immutable implementation but does not supply this recovery
  authority.
- Manual Loyal Opposition review remains required. This Prime Builder will not
  spawn, impersonate, or substitute a reviewer.

No additional owner decision is required for this bounded recovery proposal.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202667519`, the active singleton
PAUTH, and the linked specifications below fully describe the authorized
recovery. No specification amendment is needed because this proposal changes no
platform behavior; it restores terminal audit state for an implementation that
is already committed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations And Evidence

- `DELIB-202667519` - owner authorization for this exact recovery scope.
- `DELIB-202667182` - owner authorization for the original checker fix.
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-004.md` - original
  implementation report review and failed terminal-finalizer evidence.
- `bridge/gtkb-wi5657-terminal-finalization-recovery-002.md` - first recovery
  NO-GO, establishing that source/test paths must be by-reference only.
- `bridge/gtkb-wi5657-terminal-finalization-audit-recovery-006.md` - later
  recovery NO-GO, establishing the missing governance-evidence and commit
  authority now supplied by the new PAUTH.
- commit `7b838d9e7606a8b1f8be75ade78881f63beda170` - immutable implementation
  and historical audit evidence.

## Spec-Derived Verification Plan

| Specification | Verification | Required result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the strict lifecycle resolver against this new slug after every version | NEW to GO/NO-GO and any later transitions are valid; historical invalid chains remain unchanged |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Query the new PAUTH, acquire an exact-session claim after GO, and run the implementation-start gate for the one declared report path | Singleton WI, exact classes, no forbidden operation consumed, one exact target |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Compare new-chain and historical-chain inventories | Recovery evidence is additive; no historical artifact is rewritten or deleted |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-derive commit inventory, inspect the committed test diff, and run the focused protected-commit checker suite at the report baseline | Immutable evidence matches; focused regression remains green or any later unrelated failure is disclosed precisely |
| `GOV-STANDING-BACKLOG-001` | Read WI-5657 before proposal, after report, and after terminal verification | One work item remains visible and reaches terminal reconciliation only after VERIFIED |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run applicability preflight and live PAUTH/project/WI lookup | Exact triple resolves; no missing or blocking linkage |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and clause preflights against the filed proposal | No missing required/advisory specification and zero blocking clause gaps |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect finalizer result and Git commit | Terminal VERIFIED exists only with atomic commit evidence; failed finalization leaves no terminal file |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect version 003 and exact terminal include set | Report is the only PB artifact; evidence remains concrete and bounded |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every target and evidence path under `E:/GT-KB` | No out-of-root dependency or artifact |
| `GOV-WORK-TREE-HYGIENE-001` | Run scoped status and staged-diff checks before and after finalization | No source/test staging; no unrelated path enters the commit |

The implementation report must record at least these commands and exact results:

```text
git show --stat --oneline --no-renames 7b838d9e7606a8b1f8be75ade78881f63beda170
git diff-tree --no-commit-id --name-only -r 7b838d9e7606a8b1f8be75ade78881f63beda170
git merge-base --is-ancestor 7b838d9e7606a8b1f8be75ade78881f63beda170 HEAD
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --no-header
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
```

Because WI-5704 currently owns uncommitted later edits on both source/test
evidence paths, the report must distinguish immutable commit evidence from the
live worktree baseline. It must not claim, stage, restore, or attribute those
later edits to WI-5657. Current-HEAD tests are non-regression evidence only.

## Acceptance Criteria

1. The new chain resolves strictly from version 001 with readable, authorized
   exact-session metadata.
2. The active PAUTH resolves to WI-5657 only, allows exactly bridge,
   governance_evidence, and metadata, and does not forbid the one bounded local
   terminal commit.
3. Commit `7b838d9e7606a8b1f8be75ade78881f63beda170` remains an ancestor and its
   six-path inventory is re-derived exactly.
4. No source, test, configuration, registry, projection, database, or
   specification-content path is changed, restored, staged, or committed.
5. Version 003 records the exact immutable evidence, live-baseline caveat,
   focused verification, and four-path terminal include set.
6. Independent Loyal Opposition review either creates version 004 and the local
   finalization commit atomically or leaves no terminal candidate.
7. The terminal commit contains exactly the four new-chain bridge files and no
   unrelated path.
8. Only after VERIFIED, the canonical backlog service reconciles WI-5657 and
   cites both the immutable implementation commit and terminal recovery commit.
9. All historical WI-5657 chain files remain byte-for-byte unchanged.
10. No push, history rewrite, dispatcher action, release, deployment,
    credential operation, external-system mutation, or cleanup occurs.

## Risks And Rollback

The primary risk is laundering an invalid historical chain into fresh authority.
The new slug, strict resolver check, exact-session metadata, and explicit
historical disposition prevent that. A second risk is accidentally staging
WI-5704's later source/test edits; the four-path terminal include ceiling and
staged-diff assertion prevent it.

There is no destructive rollback. Before terminal commit, a failed helper must
remove its candidate verdict. After terminal commit, any correction is a new
governed append-only artifact or separately authorized revert. Historical files
and the immutable implementation commit are never rewritten.

## Recommended Commit Type

`chore(bridge): finalize WI-5657 terminal recovery`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
