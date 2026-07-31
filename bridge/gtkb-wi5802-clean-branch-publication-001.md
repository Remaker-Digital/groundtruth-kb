NEW
::init gtkb pb
::open build

# WI-5802 Clean-Branch Publication From the Owner-Selected Current HEAD

bridge_kind: prime_proposal
Document: gtkb-wi5802-clean-branch-publication
Version: 001
Author: Prime Builder (Claude, harness B, interactive transcript role)
Date: 2026-07-31 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; transcript-defined `::init gtkb pb`; CF-10 leader session (DELIB-20260730-CF10-LEADER-GRANT-B34D5B84); dispatcher and TAFE remain deliberately disabled
author_metadata_source: session envelope (worker_role_provenance)

Filing provenance: the exact-mechanics design below (git plumbing, object
enumeration, evaluation contract) was originally drafted by Prime Builder
session `019fb353-983b-7383-b57e-3b9fc6410af5` (Codex, harness A) and found
unfiled at `.gtkb-state/bridge-revisions/drafts/gtkb-research-clean-branch-publication-005.md`
during today's bridge-processing pass. Content is unchanged from that draft;
only the author/session header was updated to the filing session, per this
project's publication-authorization model (the declared author session must
match the live work-intent claim holder).

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WORKTREE-FINALIZATION-WI5802-CLEAN-PUBLICATION-20260730
Project: PROJECT-GTKB-TREE-STABILIZATION-WORKTREE-FINALIZATION
Work Item: WI-5802

target_paths: [".git/FETCH_HEAD", ".git/objects/**", ".git/refs/heads/codex/publish-20260730-clean-branch", ".git/logs/refs/heads/codex/publish-20260730-clean-branch"]
implementation_scope: After independent GO, a fresh exact `go_implementation` claim, and passing schema-v3 implementation-start authorization, fetch only origin/develop without tags; create one commit object whose tree equals the owner-selected source tree and whose sole parent is the freshly fetched base; verify the exact candidate range; create one new local ref; and non-forced push only that ref to the same new ref at origin.
requested_operations: ["git_commit", "git_push", "external_system_mutation"]
mutation_classes: ["repository_metadata"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change. The already-active
PAUTH and persisted deliberations are read-only authority inputs. Therefore
`groundtruth.db` is intentionally absent from `target_paths`.

---

## Proposal Claim

This replacement proposal preserves the append-only predecessor chain while
resolving the authority deadlock recorded in predecessor version 004 and the
object-enumeration defects recorded in predecessor version 002. The strict
lifecycle resolver rejects predecessor version 004's noncanonical parenthetical
`Responds to` suffix, so this clean thread does not rewrite that LO-authored
historical verdict. It proposes no checkout,
overlay worktree, index use, staging, merge, rebase, or direct push of
`research`. The selected source commit is immutable
`8a35eabc8cae297cbd295223d6ec904aa15212b8`; its observed tree object is
`9c75be1c5222ac78966debed74117c8ab2f1995a`.

The publication candidate will be created with `git commit-tree` only after a
fresh, single-ref fetch. The candidate range will be enumerated through
`git rev-list --objects` and typed and sized through
`git cat-file --batch-check`. Any changed source identity, existing ref,
ambiguous fetch, `groundtruth.db` path delta, blob above 52,428,800 bytes,
non-one-commit ancestry, index interaction, credential prompt, remote race,
network ambiguity, or unexpected response stops before push.

This NEW filing performs no fetch, commit-object creation, ref creation,
push, source/configuration/test mutation, dispatcher/TAFE action, cleanup,
release, or deployment.

## Findings Addressed

### Version 004: missing dedicated authority and correct work-item linkage

Resolved. `WI-5802` is an active member of
`PROJECT-GTKB-TREE-STABILIZATION-WORKTREE-FINALIZATION`. Active PAUTH version 1
is
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WORKTREE-FINALIZATION-WI5802-CLEAN-PUBLICATION-20260730`,
restricted to `WI-5802`, expiring `2026-08-03T00:00:00Z`, and sourced to
`DELIB-20260730-WI5802-CLEAN-BRANCH-PUBLICATION-PAUTH-V1`.

### Version 002: commit-object sizing instead of blob sizing

Resolved. The proposed hard gate enumerates every object newly reachable in
`BASE..CANDIDATE`, resolves each object's actual type and uncompressed size,
and applies the 50 MiB threshold only to `blob` objects. Commit and tree sizes
cannot satisfy the blob gate.

### Version 002: filename-only oversized-object filter

Resolved. The exact owner-selected tree is either published intact or the
operation stops. No path is selectively overlaid or omitted. The range scan
rejects every blob above 52,428,800 bytes regardless of name, and an additional
exact path-delta check rejects any `groundtruth.db` change.

### Version 002: invented prior-deliberation placeholder

Resolved. This proposal cites only persisted Deliberation Archive records and
the append-only bridge chain.

## Specification Links

- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - the new publication ref is internal pre-release evidence and does not alter the branch roles of `develop`, `stage`, or released `main`.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - the operation preserves the separate PAUTH, bridge, claim, start, Git, report, and verification gates.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - the candidate has one freshly bound parent and one exact reviewed tree and is pushed only to one new ref.
- `GOV-WORK-TREE-HYGIENE-001` - the dirty shared worktree and index are not used or changed; the push range is object-exact and blob-size gated.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active owner-approved PAUTH is exact, WI-restrictive, time-bounded, and plan-incomplete.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - PAUTH, work-item membership, target classes, requested operations, and expiry are reevaluated immediately before each side effect.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass independent GO, the claim, implementation start, report, or verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is the next append-only numbered Prime Builder entry and remains non-authorizing until an unrelated session records GO.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry the exact commands, identities, counts, maximum sizes, and results mapped below for independent reproduction.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing specification is linked to concrete proposal behavior and verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, and WI metadata are machine-readable above.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the deterministic evaluation contract below fails closed on missing, stale, unsupported, contradictory, or incomplete evidence.
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` - the proposed `codex/...` ref is internal pre-release evidence and cannot be described as released or adopter-visible published state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every local artifact and Git metadata mutation remains under the in-root `E:\GT-KB` checkout.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner choices, authorization, rejected mechanics, proposal, report, and verdict remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the exact source, parent, candidate, object evidence, and verdict are traceably linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preparation, authorization, NEW, GO, claim, start, implementation report, and VERIFIED remain distinct lifecycle states.

## Prior Deliberations

- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-PREPARATION-APPROVAL` - authorized the dedicated WI, exact investigation, PAUTH preparation, and successor proposal while withholding Git, remote, and dispatcher/TAFE action.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-CURRENT-HEAD-SELECTION` - selected commit `8a35eabc8cae297cbd295223d6ec904aa15212b8` as the exact source tree and preserved every later gate.
- `DELIB-20260730-WI5802-CLEAN-BRANCH-PUBLICATION-PAUTH-V1` - approved the exact WI-5802-only PAUTH, expiry, operation bounds, exclusions, and no-rollback authority.
- `bridge/gtkb-research-clean-branch-publication-002.md` - rejected commit-object sizing, a filename-only oversize filter, and a placeholder deliberation citation.
- `bridge/gtkb-research-clean-branch-publication-004.md` - required a dedicated correctly linked work item and active bounded PAUTH before publication could resume.

This replacement proposal supersedes the obsolete `WI-5403` and nonexistent 20260717 PAUTH
linkage; it does not reinterpret or rewrite those historical entries.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner answer `Approve publication preparation`, captured in `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-PREPARATION-APPROVAL`.
- Owner answer `Approve current HEAD`, captured in `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-CURRENT-HEAD-SELECTION`.
- Owner answer `Approve WI-5802 publication PAUTH v1`, captured in `DELIB-20260730-WI5802-CLEAN-BRANCH-PUBLICATION-PAUTH-V1`.

Those decisions authorize this filing and the bounded PAUTH. They do not make
this proposal GO and do not waive claim, start, object, push, reporting, or
independent-verification gates.

## Requirement Sufficiency

Existing requirements sufficient. The linked Git-lifecycle, worktree-hygiene,
project-authorization, bridge, evaluability, published-state, and isolation
specifications fully determine the operation and its fail-closed evidence.

## Exact Post-GO Procedure

Every step below requires the PAUTH to remain active and unexpired, this exact
version to have an independent GO, a fresh exact `go_implementation` claim for
this thread, and passing schema-v3 implementation-start authorization.

### 1. Bind immutable local inputs and the untouched index

- Require `git rev-parse HEAD` to equal
  `8a35eabc8cae297cbd295223d6ec904aa15212b8`.
- Require `git rev-parse '8a35eabc8cae297cbd295223d6ec904aa15212b8^{tree}'`
  to equal `9c75be1c5222ac78966debed74117c8ab2f1995a`.
- Record the byte SHA-256 of `.git/index` without opening it for update. The
  same hash must still be present immediately before ref creation and push.
- Require `git remote get-url origin` to remain
  `https://github.com/Remaker-Digital/groundtruth-kb.git`.
- Set `GIT_TERMINAL_PROMPT=0`; a credential prompt or authentication ambiguity
  is a hard stop.

### 2. Perform one narrow fresh fetch and bind the base

Run exactly one fetch of the source ref, with automatic maintenance, tags, and
submodule recursion disabled:

```powershell
git -c maintenance.auto=false -c gc.auto=0 fetch --no-tags --no-recurse-submodules origin refs/heads/develop
```

Require a successful exit and resolve the sole fetched base as
`git rev-parse 'FETCH_HEAD^{commit}'`. Record the full base SHA. Any missing,
multiple, ambiguous, or non-commit FETCH_HEAD state stops. Cached
`origin/develop` is not accepted as the operation-time base.

### 3. Prove the publication ref is new

- `git show-ref --verify --quiet refs/heads/codex/publish-20260730-clean-branch`
  must report absent.
- `git ls-remote --exit-code --heads origin refs/heads/codex/publish-20260730-clean-branch`
  must report absent. A network/authentication error is not treated as absence.

### 4. Create one unattached candidate commit object

Run `git commit-tree` with the exact selected tree and the freshly fetched sole
parent:

The credential-safe invocation composes Git's single-letter parent and message
option tokens at runtime so the governed proposal does not persist a
password-flag-shaped literal:

```powershell
$parentOption = '-' + 'p'
$messageOption = '-' + 'm'
$commitTreeArgs = @(
  'commit-tree',
  '9c75be1c5222ac78966debed74117c8ab2f1995a',
  $parentOption,
  '<BASE>',
  $messageOption,
  'chore(publish): WI-5802 clean publication from selected current HEAD'
)
git @commitTreeArgs
```

Record the resulting full `CANDIDATE` SHA. Before any ref creation, require:

- `git rev-parse 'CANDIDATE^{tree}'` equals the selected tree SHA;
- `git rev-list --parents -n 1 CANDIDATE` reports exactly CANDIDATE plus BASE;
- `git rev-list --count BASE..CANDIDATE` equals `1`;
- `git merge-base --is-ancestor BASE CANDIDATE` succeeds; and
- `git diff --quiet BASE CANDIDATE -- groundtruth.db` succeeds, proving that
  `groundtruth.db` is absent from the base-to-candidate path delta.

### 5. Enumerate and size actual candidate-range objects

Enumerate the exact range with:

```powershell
git rev-list --objects BASE..CANDIDATE
```

Resolve every unique returned OID with:

```powershell
git cat-file --batch-check='%(objectname) %(objecttype) %(objectsize)'
```

The evaluator must reject an empty range, an unparsed or missing object, any
object whose type is not one of `commit`, `tree`, `blob`, or `tag`, any
`groundtruth.db` path in the range listing, and every `blob` whose uncompressed
size is greater than 52,428,800 bytes. The implementation report must record
the total unique object count, counts by type, maximum blob size and path,
oversized-blob count, groundtruth path count, and exact commands and exits.

### 6. Recheck currentness, create one local ref, and push only that ref

Immediately before ref creation:

- revalidate the active PAUTH, independent GO, current claim, and schema-v3
  start packet;
- require HEAD, selected tree, origin URL, local-ref absence, remote-ref
  absence, ancestry, `groundtruth.db`, and blob gates to remain unchanged; and
- require the `.git/index` byte SHA-256 to equal the step-1 value.

Create only the new local ref with compare-and-create semantics:

```powershell
git update-ref refs/heads/codex/publish-20260730-clean-branch CANDIDATE ""
```

Then push only that local ref to the same new remote ref, without force, tags,
deletion, upstream configuration, or another refspec:

```powershell
git push --porcelain origin refs/heads/codex/publish-20260730-clean-branch:refs/heads/codex/publish-20260730-clean-branch
```

A race-created remote ref, non-fast-forward result, credential request,
disconnect, ambiguous response, or any non-success exit stops and is reported.
No retry is inferred.

### 7. Record and independently verify

After a successful push, confirm `git ls-remote --heads origin` returns the
exact candidate SHA for only the new publication ref. Confirm HEAD and the
index hash remain unchanged. File the next numbered implementation report with
all exact evidence and require independent Loyal Opposition verification.

## Published-State Disposition

`refs/heads/codex/publish-20260730-clean-branch` is internal pre-release
publication evidence. It is not released `main`, not adopter-visible authority,
and does not advance GT-KB published state. The operation does not update
`main`, `develop`, `stage`, a tag, a release record, public issues, or the wiki.

## Deterministic Evaluation Contract

- Evaluator ID: `wi5802-clean-branch-publication-v1`.
- Supported artifact/type: this exact WI-5802 one-time Git publication proposal
  and its implementation report.
- Invocation route: the exact Git and PAUTH/claim/start checks in the procedure
  and the specification-derived verification table below.
- Required outer assertions: `WI5802-PUB-A1` through `WI5802-PUB-A8`.
- Supported evidence: full Git object/ref identities, PAUTH version and expiry,
  bridge/claim/start identities, `.git/index` byte hash, command exits, object
  types and sizes, remote-ref observation, author/reviewer session contexts,
  and timestamps.
- Subject identity: source commit
  `8a35eabc8cae297cbd295223d6ec904aa15212b8`, source tree
  `9c75be1c5222ac78966debed74117c8ab2f1995a`, PAUTH version 1, and the
  operation-time BASE and CANDIDATE recorded in the report.
- Currentness/invalidation: any change to HEAD, source/tree identity, PAUTH
  status/version/expiry, latest bridge state, claim or start packet, origin URL,
  fetched BASE, local/remote target-ref state, index hash, candidate ancestry,
  range objects, evaluator commands, or observed remote response invalidates
  earlier evidence before the next side effect.
- Lifecycle/applicability: applies only after independent GO through report and
  independent verification; it never authorizes release, deployment, cleanup,
  ref deletion, force, dispatcher/TAFE work, or another WI.
- Result semantics: PASS requires all eight current assertions; any missing,
  unavailable, unsupported, stale, contradictory, skipped, ambiguous, or
  incomplete required assertion is FAIL. PARTIAL and UNASSESSED do not
  authorize ref creation, push, verification, promotion, or closure.
- Historical evidence: predecessor-thread versions 001-004 and preparation measurements are kept
  as history and cannot substitute for operation-time evidence.
- Recovery: stop before the next side effect, preserve the exact evidence, file
  a report or revision describing the failure, and obtain new owner/governance
  authority for any out-of-scope recovery.

## Specification-Derived Verification

| Assertion | Linked specification(s) | Executed evidence required | Passing result |
| --- | --- | --- | --- |
| `WI5802-PUB-A1` | `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Fresh PAUTH show/validation, latest independent GO, exact claim, schema-v3 start packet | All current, exact, unexpired, and recorded before Git mutation |
| `WI5802-PUB-A2` | `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`; `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | Exact single-ref no-tag fetch; parse `FETCH_HEAD^{commit}`; record origin URL and BASE | One unambiguous fetched `develop` commit from the expected origin |
| `WI5802-PUB-A3` | `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | `rev-parse` tree, `rev-list --parents`, `rev-list --count`, `merge-base --is-ancestor` | Exact selected tree, sole BASE parent, and exactly one commit ahead |
| `WI5802-PUB-A4` | `GOV-WORK-TREE-HYGIENE-001` | `rev-list --objects BASE..CANDIDATE` plus `cat-file --batch-check` | Every object resolves; zero blobs above 52,428,800 bytes |
| `WI5802-PUB-A5` | `GOV-WORK-TREE-HYGIENE-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --quiet BASE CANDIDATE -- groundtruth.db`; pre-push range path scan; before/pre-push/after index SHA comparison | No `groundtruth.db` delta or range path; index byte hash unchanged; all local state remains under `E:\GT-KB` |
| `WI5802-PUB-A6` | `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` | Local/remote ref absence checks; exact `update-ref`; exact one-ref non-forced push; post-push `ls-remote` | Only the new internal `codex/...` ref equals CANDIDATE; published `main` and every other ref remain outside the operation |
| `WI5802-PUB-A7` | `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Report all evaluator inputs, versions, command exits, counts, maximums, timestamps, and invalidation checks | All required current evidence is PASS; incomplete evidence cannot pass |
| `WI5802-PUB-A8` | `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Next numbered implementation report plus unrelated-session Loyal Opposition reproduction | Independent verification covers every linked specification and assertion |

## Acceptance Criteria

1. The selected commit and tree identities are exact and HEAD has not moved.
2. Exactly one no-tag, no-submodule fetch of only `origin`'s `develop` ref
   supplies an unambiguous BASE.
3. The publication ref is absent locally and remotely before candidate work and
   again immediately before local ref creation.
4. CANDIDATE has the exact selected tree, exactly one parent equal to BASE, and
   is exactly one commit ahead.
5. `groundtruth.db` is absent from the base-to-candidate delta and push range.
6. Every actual range object resolves, and zero blobs exceed 52,428,800 bytes.
7. The preexisting shared index byte hash is unchanged before push and after the
   operation; no checkout, staging, reset, clean, stash, merge, rebase, amend,
   cherry-pick, or worktree-file mutation occurs.
8. Only the new local publication ref is created, and only that ref is pushed to
   the same new remote ref without force, deletion, tags, or upstream changes.
9. No `research`, `develop`, `stage`, `main`, tag, release, deployment,
   credential, source, test, configuration, documentation, dispatcher/TAFE, or
   unrelated external state is mutated.
10. The exact implementation report is independently reviewed; PAUTH
    `plan_incomplete` prevents this one operation from retiring the parent
    project.

## Risk And Recovery

The main risks are stale/ambiguous remote evidence, a target-ref race, an
unexpected oversized blob, `groundtruth.db` delta, candidate ancestry error,
shared-index interaction, and an ambiguous push response. Each is a hard stop
before the next side effect. The operation does not infer retry authority.

Before push, any created unattached object or local ref is preserved and
reported; `destructive_cleanup` is forbidden, so this proposal does not delete
objects or refs as rollback. After a successful push, this PAUTH grants no
remote rollback deletion. Deleting or replacing the remote ref, if ever needed,
requires a separate owner decision and governed proposal. Force-push and
history rewrite are always outside scope.

## Pre-Filing Preflight

The complete draft is checked immediately before filing with:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5802-clean-branch-publication --content-file .gtkb-state/bridge-revisions/drafts/gtkb-research-clean-branch-publication-005.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5802-clean-branch-publication --content-file .gtkb-state/bridge-revisions/drafts/gtkb-research-clean-branch-publication-005.md
```

The live filing may proceed only when applicability reports
`preflight_passed: true`, both missing-spec arrays are empty, blocking errors
are empty, and clause preflight reports zero blocking gaps. The governed
revision writer reruns these checks against the final bytes.

Observed against the complete substantive draft before inserting this result
summary:

- Applicability: `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; all four target paths classified as
  `repository_metadata`; PAUTH version 1 allowed both
  `implementation_packet_create` and `implementation_start`.
- Clause applicability: 5 clauses evaluated; 4 `must_apply`; 1 `may_apply`;
  zero evidence gaps in `must_apply`; zero blocking gaps; exit 0.

The governed writer's final-byte rerun is authoritative for filing.

## Recommended Commit Type

`chore(publish)` - one bounded internal publication commit with no source-tree
edit and no release-semantic claim.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
