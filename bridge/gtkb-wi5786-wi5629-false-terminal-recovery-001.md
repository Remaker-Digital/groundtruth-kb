NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 304c2c33-128d-4bf3-a997-17ecdcb19669
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code headless proposal worker; Prime Builder; dispatched by leader session under DELIB-202667523
author_metadata_source: explicit current-session bridge filing metadata

# WI-5786 WI-5629 False-Terminal Recovery Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5786-wi5629-false-terminal-recovery
Version: 001
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5786

target_paths: ["bridge/gtkb-wi5786-wi5629-false-terminal-recovery-003.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

KB Mutation: This proposal performs no MemBase mutation.

---

## Summary

Recover the WI-5629 false terminal `VERIFIED` through one new strict-valid
by-reference recovery chain, without editing the historical chain and without
re-staging or recommitting the already-landed implementation.

`bridge/gtkb-wi5629-corrected-malformed-verdict-chain-030.md` is labeled
`VERIFIED` and is the live head of a thirty-version thread, but it violates the
Mandatory VERIFIED Commit-Finalization Gate in
`.claude/rules/file-bridge-protocol.md`. The verdict was not created by an
atomic finalization transaction. It was swept into an unrelated 532-file bulk
commit, while the implementation it claims to verify lives in a separate
two-file commit made earlier. The verdict body also carries none of the
finalization evidence the current floor requires.

This proposal starts a clean chain rather than appending to, rewriting,
renumbering, or reinterpreting the existing one. After an independent GO, Prime
Builder will file only the declared version-003 recovery report, which
re-derives the immutable commit inventory and records independent verification
of the current committed implementation. An independent Loyal Opposition
reviewer may then create version 004 through the canonical terminal finalizer
under the commit-first ordering ratified in `DELIB-202667533` (AT-01).

## Verified Present-State Evidence

Collected read-only in this session on 2026-07-30. The version-003 report must
re-derive every item below rather than inheriting these values.

### E1 - The thread head is terminal

```powershell
gt bridge show gtkb-wi5629-corrected-malformed-verdict-chain --json --compact
```

Result:

```json
{"latest_path": "bridge/gtkb-wi5629-corrected-malformed-verdict-chain-030.md",
 "latest_status": "VERIFIED", "version_count": 30}
```

### E2 - The terminal verdict lacks finalization evidence

`bridge/gtkb-wi5629-corrected-malformed-verdict-chain-030.md` contains no
`Commit Finalization Evidence` section, no `Recommended commit type` line, no
`Commands Executed` section, and no `Spec-to-Test Mapping` section. Its sections
are Verdict, First-Line Role Eligibility And Review Independence, Independent
Verification Evidence (V1-V10), Specification-Derived Verification Summary,
Prior Deliberations, and Skills Applied.

### E3 - Implementation and verdict are in different commits

```powershell
git --no-optional-locks log --oneline -1 -- bridge/gtkb-wi5629-corrected-malformed-verdict-chain-030.md
```

Result: `db07f9dcf Synching backlog`. Versions 028, 029, and 030 all resolve to
that same commit.

The implementation subject paths resolve instead to
`1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4`
(`fix: resume implementation after report no-go`), which changed exactly
`scripts/implementation_authorization.py` and
`platform_tests/scripts/test_implementation_authorization.py`.

### E4 - The verdict commit is a bulk sweep, not an atomic finalization

```powershell
git --no-optional-locks diff-tree --no-commit-id --name-only -r db07f9dcfe7e7de8addc850729209278472cb0fe
git --no-optional-locks diff-tree --no-commit-id --name-only -r 1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4
```

Results: 532 paths and 2 paths respectively. A conforming finalization commit
contains exactly the verified path set plus the verdict artifact. A 532-path
sweep titled `Synching backlog` cannot satisfy that ceiling.

### E5 - Both commits are ancestors of HEAD

`git --no-optional-locks merge-base --is-ancestor <sha> HEAD` exits `0` for both
`db07f9dcfe7e7de8addc850729209278472cb0fe` and
`1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4`. The implementation is landed and
immutable. Nothing in this recovery reimplements it.

### E6 - Downstream metadata was resolved on the false terminal

`WI-5629` currently reads `resolution_status: resolved`, `stage: resolved`,
`changed_by: loyal-opposition/goose`, with
`change_reason: "Bridge reconciliation: missing_implementation_commit_coverage
- all linked threads terminal"`. That reconciliation consumed the defective
terminal as if it were valid.

### E7 - Project attribution drift in the historical chain

Version 030 records `Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`, version
029 records `Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE`, and the
`WI-5629` backlog row records `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE`. The
version-003 report must disclose this divergence as observed historical
evidence. This proposal proposes no correction to it; the recovery subject is
the finalization defect, not the historical chain's attribution.

## Why A Clean Chain Is Required

The historical chain terminates at `VERIFIED`. `VERIFIED` is terminal and
non-actionable under `GOV-FILE-BRIDGE-AUTHORITY-001`, so the thread cannot
accept a further valid lifecycle transition. Bridge files are append-only audit
artifacts and must never be edited, deleted, or renumbered, so the defective
verdict cannot be repaired in place.

The `WI-5648` invalid-chain precedent, and the `WI-5657` and `WI-5659` recovery
chains that followed it, established the accepted remedy: leave the historical
chain byte-for-byte intact as incident evidence, and open one fresh
strict-valid chain that carries the recovery decision and its evidence. This
proposal follows that precedent exactly.

## By-Reference Finalization Waiver

This recovery requests the same narrow waiver granted in `DELIB-202667191` for
`WI-5659` and `DELIB-202667519` for `WI-5657`: the already-committed
implementation is accepted as immutable by-reference evidence, and the one
bounded local finalization commit contains only this new chain's bridge files.

The following landed paths are by-reference verification subjects. They MUST
NOT be modified, restored, restaged, reverted, or included in the recovery
commit:

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

The waiver is a finalization-mechanics boundary only. It does not waive content
review, inventory re-derivation, test execution, review independence,
applicability preflight, clause preflight, or protected-commit verification.

The one prospective terminal commit may contain only:

- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-001.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-002.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-003.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-004.md`

## Commit-First Finalization Conformance

`DELIB-202667533` decision AT-01 is binding design authority for this chain.
The version-004 terminal transaction MUST create the local commit containing the
verdict and its cohort FIRST, and publish terminal bridge state only after that
commit exists. An interruption must strand a recoverable uncommitted verdict
file, never a published terminal without a backing commit.

This is precisely the failure class being recovered: `WI-5629` reached published
terminal state with no conforming backing commit. Reproducing the old ordering
here would recreate the defect inside its own remedy. If the finalizer cannot
create the commit, it must remove the candidate verdict and fail closed, leaving
this chain non-terminal.

## Recovery Boundary

The controlling authorization is at version 2 and allows exactly eight mutation
classes: `source`, `test`, `test_addition`, `configuration`, `documentation`,
`metadata`, `governance_evidence`, and `bridge`. Version 2 removed the
unregistered `git_commit` token that version 1 had carried in that list;
`git_commit` is a registered operation, not a mutation class, and it does not
appear in `forbidden_operations`, so governed local commit authority is
unchanged. This proposal deliberately narrows execution far inside that envelope
to `bridge` and `governance_evidence` plus one bounded local finalization
commit.

Explicitly out of scope and not performed:

- No source, test, configuration, registry, projection, dispatcher, or schema
  mutation.
- No MemBase write before terminal verification. This proposal performs no KB
  mutation.
- No edit, deletion, renumbering, or replacement of any historical `WI-5629`
  bridge file.
- No Git history rewrite, push, release, deployment, credential operation,
  external-system mutation, or destructive cleanup. Each is a forbidden
  operation under the controlling authorization.
- No absorption of `WI-5657`, `WI-5659`, or any other recovery work item.

Protected narrative artifacts and formal MemBase records are not in this
proposal's scope, so no per-artifact approval packet is required here.

## Proposed Recovery Sequence

1. An independent Loyal Opposition session reviews this design and files `GO` or
   `NO-GO` as version 002.
2. After `GO`, Prime Builder acquires a fresh work-intent claim and an
   implementation-start authorization scoped to the single declared target path,
   performs no source or test mutation, re-derives the commit inventory, reruns
   the verification families below, and files version 003.
3. A second independent Loyal Opposition session inspects the immutable diffs,
   reproduces the verification families, and either files `NO-GO` or creates
   version 004 through the canonical terminal finalizer.
4. The finalizer creates the local commit first, then publishes terminal state.
5. Only after commit-backed `VERIFIED` does Prime Builder reconcile `WI-5629`
   and `WI-5786` backlog metadata through the canonical backlog lifecycle
   service, citing the immutable implementation commit and the recovery commit.
   That post-terminal lifecycle call is not a version-003 implementation target
   and does not place `groundtruth.db` in this proposal's target set.

Expected lifecycle:

```text
NEW -001 -> GO -002 -> NEW report -003 -> VERIFIED -004
```

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` supplies the
commit-finalization gate that version 030 violated, `DELIB-202667721` supplies
the implementation authority, `DELIB-202667533` AT-01 supplies the binding
finalization ordering, and the `WI-5648` / `WI-5657` / `WI-5659` precedents
supply the clean-chain remedy. No specification amendment is needed because this
proposal changes no platform behavior; it restores correct terminal audit state
for an implementation that is already committed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - commit-finalization gate, append-only audit
  trail, and strict status lifecycle authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - controlling list-free
  whole-project authorization and implementation-start packet requirement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve the defective chain and this
  recovery chain as durable evidence.
- `GOV-ARTIFACT-APPROVAL-001` - per-artifact approval discipline, cited because
  class authorization does not substitute for it.
- `GOV-STANDING-BACKLOG-001` - `WI-5629` and `WI-5786` backlog reconciliation
  authority.
- `GOV-WORK-TREE-HYGIENE-001` - scoped staging discipline for the bounded
  terminal commit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - executed spec-derived
  evidence required before `VERIFIED`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact authorization,
  project, work-item, and target linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every cited
  authority mapped to a concrete check.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal state exists only with atomic
  commit evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - new governed artifact rather than
  edited history.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every target and evidence path
  resolves under `E:/GT-KB`.

## Prior Deliberations

- `DELIB-202667533` - AT-01 commit-first / publish-after finalization ordering;
  binding design authority for the version-004 transaction.
- `DELIB-202667721` - owner authorization issuing the controlling list-free
  whole-project grant, naming `WI-5786` as its immediate effect.
- `DELIB-202667720` - correction notice establishing that no WI-restricted grant
  covered `WI-5786`, and recording that the prior proposal worker correctly
  refused to file without coverage.
- `DELIB-202667719` - transitional controlling-authority rule; supplies the
  precedence rule that a list-free grant is controlling where both shapes exist.
- `DELIB-202667523` - owner program mandate authorizing the leader-driven
  manual fan-out that dispatched this proposal.
- `DELIB-202667191` - narrow by-reference finalization precedent (`WI-5659`).
- `DELIB-202667519` - by-reference recovery authorization precedent (`WI-5657`).
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-001.md` - accepted
  recovery-proposal shape mirrored here.
- `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-001.md` -
  accepted by-reference recovery shape mirrored here.
- `WI-5648` - resolved invalid-chain incident establishing clean replacement
  rather than mutation of historical chain bytes.

## Spec-Derived Verification Plan

| Specification | Verification | Required result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Re-derive E1-E4; run the strict lifecycle resolver against this new slug after every version | Historical defect reproduced exactly; new chain resolves strictly from 001; historical chain unchanged |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Re-query the controlling authorization; acquire an exact-session claim after `GO`; run the implementation-start gate for the one declared path | Grant active, unexpired, project-matched, list-free; exactly one target admitted; no forbidden operation consumed |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Hash every historical `WI-5629` bridge file before and after | All thirty files byte-for-byte unchanged |
| `GOV-ARTIFACT-APPROVAL-001` | Inspect the executed path set for formal-record or protected-narrative writes | None occurred, so no packet was required |
| `GOV-STANDING-BACKLOG-001` | Read `WI-5629` and `WI-5786` before proposal, after report, and after terminal verification | Both remain visible; reconciliation happens only after commit-backed `VERIFIED` |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped `git status` and staged-diff assertions before and after finalization | No source or test path staged; no unrelated path enters the commit |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Inspect the committed diff of `1aa2182bb` and run the focused suite at the report baseline | Immutable evidence matches; focused regression green or any unrelated failure disclosed precisely |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run applicability preflight plus live authorization, project, and work-item lookup | Exact triple resolves; membership active; no blocking linkage gap |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and clause preflights against each filed version | No missing required or advisory specification; zero blocking clause gaps |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect finalizer result and Git commit under AT-01 ordering | Commit exists before terminal publication; a failed finalization leaves no terminal file |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect version 003 and the exact terminal include set | Report is the only Prime Builder artifact; evidence concrete and bounded |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every target and evidence path | Every path under `E:/GT-KB`; no out-of-root dependency |

The version-003 report must record at least these commands and their exact
results:

```text
git --no-optional-locks show --stat --oneline --no-renames 1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4
git --no-optional-locks diff-tree --no-commit-id --name-only -r 1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4
git --no-optional-locks diff-tree --no-commit-id --name-only -r db07f9dcfe7e7de8addc850729209278472cb0fe
git --no-optional-locks merge-base --is-ancestor 1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4 HEAD
git --no-optional-locks merge-base --is-ancestor db07f9dcfe7e7de8addc850729209278472cb0fe HEAD
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --no-header
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
git --no-optional-locks diff --check -- scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
```

Because both by-reference subjects are long-lived shared platform files that
later work items have continued to change, the report must distinguish the
immutable commit evidence at `1aa2182bb` from the live worktree baseline. It
must not claim, stage, restore, or attribute later edits to `WI-5629`.
Current-HEAD test results are non-regression evidence only.

## Owner Decisions / Input

- `DELIB-202667721` (AUQ-20260730-HOUSEKEEPING-HARDENING-LISTFREE-PAUTH) is the
  operative owner authorization. The owner selected "List-free grant for
  HOUSEKEEPING-HARDENING", issuing
  `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` and naming
  `WI-5786` as authorized to proceed through the normal governed cycle.
- `DELIB-202667720` is the correction notice that must be read with
  `DELIB-202667719`. It records the verified census finding that zero
  authorization rows listed `WI-5786` platform-wide, and corrects the
  `DELIB-202667719` immediate-effect recital that had wrongly implied
  `WI-5786` was already covered by a WI-restricted grant. This proposal
  therefore does not cite any WI-restricted grant as its authority.
- `DELIB-202667734` (AUQ-20260730-PAUTH-GIT-COMMIT-CLASS-REPAIR) authorized the
  version-2 schema-shape repair of that grant under `WI-5809`. Version 1 listed
  the unregistered `git_commit` token among its mutation classes, which made the
  operation-time evaluator fail closed with `unknown_mutation_class` and denied
  every operation. Version 2 removes only that token; envelope intent, list-free
  work-item scope, included specs, and all prohibitions are preserved. This
  proposal is written against version 2 and cites no version-1 shape.
- `DELIB-202667719` supplies the precedence rule applied here: where a project
  holds both grant shapes, the list-free grant is controlling. This project
  retains fourteen WI-restricted grants as append-only audit history; none of
  them authorizes this work.
- `DELIB-202667533` AT-01 is the owner-ratified finalization ordering that the
  version-004 transaction must follow.
- `DELIB-202667523` is the owner program mandate authorizing the leader-driven
  manual fan-out under which this proposal was dispatched.

No further owner decision is required for this bounded recovery proposal.
Independent Loyal Opposition review remains mandatory; this Prime Builder will
not spawn, impersonate, or substitute a reviewer.

## Acceptance Criteria

1. This chain resolves strictly from version 001 with readable, authorized
   exact-session author metadata.
2. The controlling authorization resolves as active, unexpired, list-free, and
   project-matched, and the implementation-start gate admits exactly the one
   declared target path.
3. The defect is reproduced exactly: terminal `VERIFIED` at version 030, absent
   finalization evidence, and a 532-path verdict commit distinct from the
   2-path implementation commit.
4. `1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4` remains an ancestor of `HEAD` and
   its two-path inventory is re-derived exactly.
5. No source, test, configuration, registry, projection, database, or
   specification-content path is changed, restored, staged, or committed.
6. All thirty historical `WI-5629` bridge files remain byte-for-byte unchanged.
7. Version 003 records the immutable evidence, the live-baseline caveat, the
   project-attribution divergence, the executed verification, and the four-path
   terminal include set.
8. Independent Loyal Opposition review either creates version 004 with its
   backing commit created first, or leaves no terminal candidate.
9. The terminal commit contains exactly the four new-chain bridge files and no
   unrelated path.
10. Only after commit-backed `VERIFIED` are `WI-5629` and `WI-5786` reconciled
    through the canonical backlog lifecycle service with exact commit evidence.
11. No push, history rewrite, dispatcher action, release, deployment, credential
    operation, external-system mutation, or destructive cleanup occurs.

## Risks And Rollback

The principal risk is laundering a defective terminal into fresh authority by
treating recovery `GO` as retroactive blessing of the original finalization. The
new slug, the reproduce-the-defect acceptance criteria, the by-reference subject
ceiling, and the requirement that version 003 re-derive rather than inherit
evidence all guard against it.

A second risk is that the version-004 finalizer repeats the original ordering
defect and publishes terminal state without a backing commit. AT-01 ordering,
the fail-closed candidate removal requirement, and acceptance criterion 8
address it directly.

A third risk is staging unrelated worktree changes into the bounded terminal
commit, which is how the original defect arose. The four-path include ceiling
and the staged-diff assertion in the verification plan prevent it.

There is no destructive rollback. Before terminal commit, a failed helper must
remove its candidate verdict. After terminal commit, any correction is a new
governed append-only artifact or a separately authorized revert. Historical
files and the immutable implementation commit are never rewritten.

## Recommended commit type

`chore` - this chain adds governance evidence only. It creates no new capability
surface, changes no behavior, and modifies no source or test file.

Prospective terminal commit subject:

```text
chore(bridge): finalize WI-5786 WI-5629 false-terminal recovery VERIFIED (by-reference)
```

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
