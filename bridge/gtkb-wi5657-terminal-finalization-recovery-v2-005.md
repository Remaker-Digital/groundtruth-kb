REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review
author_metadata_source: explicit current-session owner direction

# WI-5657 Strict-Chain Terminal Recovery Proposal - Revised

bridge_kind: prime_proposal
Document: gtkb-wi5657-terminal-finalization-recovery-v2
Version: 005
Date: 2026-07-28 UTC
Responds to: bridge/gtkb-wi5657-terminal-finalization-recovery-v2-004.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5657-TERMINAL-RECOVERY-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5657

target_paths: ["bridge/gtkb-wi5657-protected-commit-superseded-verified-005.md", "bridge/gtkb-wi5657-terminal-finalization-recovery-v2-007.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

KB Mutation: This proposal performs no MemBase mutation.

---

## Revision Claim

This revision keeps the clean v2 terminal-recovery design, preserves every
closure accepted by version 004, and corrects every new finding in that review.
The historical facts remain explicit: two earlier
recovery chains are strict-invalid, while the original implementation chain was
strict-valid and has now been retired append-only at terminal `WITHDRAWN`
version 005 under the owner's recorded decision. The owner directed, "Continue
v2 and retire the old chain."

The post-GO recovery report is explicitly `NEW`, not `NO-ACTION`. If this
revision receives GO at version 006, Prime Builder will file the report at
version 007 and an independent Loyal Opposition reviewer may terminally verify
it at version 008. The terminal commit boundary is no longer a brittle fixed
count: it is exactly every versioned file of this v2 chain that exists at
finalization time plus the single owner-directed old-chain retirement artifact,
and no other path.

No source, test, configuration, registry, projection, specification, or direct
database-content mutation is proposed. Commit
`7b838d9e7606a8b1f8be75ade78881f63beda170` remains immutable by-reference
implementation evidence.

## Findings Addressed Across Versions 002 And 004

### FINDING-P1-001 - Corrected historical-chain disposition and owner choice

The version-001 statement that all three historical chains were strict-invalid
was wrong. Fresh strict-resolver checks establish:

- `gtkb-wi5657-terminal-finalization-recovery` is strict-invalid because its
  initial `NEW` uses bare `author_identity: codex`; the resolver cannot derive
  an authorized role.
- `gtkb-wi5657-terminal-finalization-audit-recovery` is strict-invalid for the
  same bare-identity reason.
- `gtkb-wi5657-protected-commit-superseded-verified` was strict-valid and ended
  at `NO-GO` version 004.

The corrected premise was routed to the owner. `DELIB-202667520` records the
exact response, "Continue v2 and retire the old chain." Prime Builder therefore
filed append-only
`bridge/gtkb-wi5657-protected-commit-superseded-verified-005.md` with status
`WITHDRAWN`. A fresh strict-resolver read reports versions 001 through 005 as
strict, latest status `WITHDRAWN`, and zero blocking diagnostics. Versions 001
through 004 remain unchanged. The two strict-invalid chains also remain
unchanged as incident evidence.

The withdrawal is a terminal lifecycle disposition, not implementation work and
not verification of the old report. All further terminal-recovery work proceeds
through this clean v2 chain.

The withdrawal was filed before a GO because it was the owner's append-only
lifecycle disposition, not implementation. The strict resolver classifies
`WITHDRAWN` as a Prime-or-owner-authored terminal status, `NO-GO -> WITHDRAWN`
is an allowed transition, and `DELIB-202667520` directly authorized this exact
action. It changed no protected implementation target and conferred no
implementation authority. This revision declares the existing withdrawal path
as a target only so its bytes can be made durable in the eventual bounded
terminal commit; that declaration does not retroactively characterize its
authoring as implementation.

### FINDING-P2-002 - Post-GO report pinned to NEW

The intended lifecycle, if this revision receives GO on the present round, is:

```text
NEW -001 -> NO-GO -002 -> REVISED -003 -> NO-GO -004
         -> REVISED -005 -> GO -006
         -> NEW -007 recovery report -> VERIFIED -008
```

The version-007 report MUST use `NEW`. Its zero-source-mutation character is
described in the report body and `## Files Changed`; it does not make the report
`NO-ACTION`. If another review round intervenes, version numbers advance
monotonically and the same status roles and terminal include invariant apply.

### FINDING-P3-003 - Finalization boundary made review-round invariant

The terminal finalizer may include exactly every versioned file belonging to
`gtkb-wi5657-terminal-finalization-recovery-v2` at finalization time plus the
single owner-directed retirement artifact
`bridge/gtkb-wi5657-protected-commit-superseded-verified-005.md`. It MUST NOT
include any source, test, configuration, registry, projection, database,
specification, or any other old-thread, foreign-thread, or unrelated path. This
invariant survives any additional NO-GO and REVISED round.

### Version 004 FINDING-P1-001 - Retirement durability path made explicit

The withdrawal file is currently untracked. It is therefore an explicit member
of both `target_paths` and the eventual terminal include set. The finalizer must
commit it atomically with the complete v2 chain; no separate or future
transaction is assumed. This is the narrow option (a) recommended by the
reviewer and stays inside the active PAUTH's `bridge` mutation class and
`DELIB-202667520`'s exact owner direction.

### Version 004 FINDING-P3-002 - Pre-GO disposition basis disclosed

The withdrawal's authoring basis is the terminal lifecycle rule and the direct
owner decision, not an implementation GO or report target. Its later inclusion
in the terminal commit is a durability operation under this proposal's bounded
finalization authority. The distinction is explicit so an auditor need not
infer why an owner-directed `WITHDRAWN` status existed before this implementation
proposal received a verdict.

### Version 004 FINDING-P3-003 - Decision collection provenance disclosed

`DELIB-202667520` has no `source_ref` and does not claim an AskUserQuestion UI
event. The owner supplied the exact sentence "Continue v2 and retire the old
chain" as a direct transcript reply after the corrected strict-valid and
strict-invalid facts were presented. This revision relies on that substantive,
explicit owner reply and makes no stronger channel-provenance claim.

### WI-5704 baseline refresh

WI-5704 is terminally complete. Its finalized commit is
`ec7e6b378329fdc6529a25311232235417ccda41` with subject
`fix(governance): prevent transient registry index recurrence (WI-5704)`.
The WI-5657 evidence paths are currently clean at HEAD rather than carrying the
uncommitted overlap described in version 001. Because WI-5704 is later work,
the WI-5657 report must still distinguish immutable commit `7b838d9e...`
evidence from current-HEAD non-regression evidence and must not attribute the
later source/test state to WI-5657.

## Recovery Boundary

The active authorization permits only `bridge`, `governance_evidence`, and
`metadata` mutation classes. It permits one bounded local terminal-finalization
commit and canonical WI-5657 backlog reconciliation after terminal verification.
It does not authorize source, test, configuration, registry,
registry-projection, database schema, specification content, or direct
database-content mutation.

This revision and its future report perform no MemBase operation. The only later
MemBase operation permitted by the owner authorization is a canonical service
update of WI-5657 after terminal verification. No registry or specification row
may be changed.

No history rewrite, push, dispatcher action, release, deployment, credential
operation, external-system mutation, destructive cleanup, or specification
deletion is permitted.

## Historical Chain Disposition

The two strict-invalid historical recovery chains remain unchanged and authorize
no work:

- `gtkb-wi5657-terminal-finalization-recovery`
- `gtkb-wi5657-terminal-finalization-audit-recovery`

Their initial files use bare `author_identity: codex`, so the strict resolver
cannot establish an authorized Prime Builder role. They remain incident and
audit evidence and are not repaired, rewritten, deleted, or continued.

The strict-valid old implementation chain
`gtkb-wi5657-protected-commit-superseded-verified` is now terminally
`WITHDRAWN` at version 005 under `DELIB-202667520`. Its prior versions remain
byte-for-byte unchanged. It authorizes no implementation and will not compete
with this v2 recovery thread.

## By-Reference Finalization Waiver

`DELIB-202667519` explicitly authorizes immutable commit
`7b838d9e7606a8b1f8be75ade78881f63beda170` as by-reference implementation
evidence and permits one bounded local canonical terminal finalization.
Therefore these already-committed paths MUST NOT be re-staged or included in the
recovery commit:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-001.md`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-002.md`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-003.md`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-004.md`

The waiver is only a finalization-mechanics boundary. It does not waive content,
inventory, test, review-independence, applicability, clause, candidate-hash, or
protected-commit verification.

The prospective terminal commit may include exactly the complete set of
versioned files in this v2 chain as it exists when terminal VERIFIED is filed,
plus
`bridge/gtkb-wi5657-protected-commit-superseded-verified-005.md`, and no other
path. The retirement file is not covered by the waiver above and MUST be
committed. On the present expected lifecycle, the v2 portion is versions 001
through 008. If an additional review round occurs, the complete-chain set grows
accordingly; no fixed count may be used as authority.

## Owner Decisions / Input

- `DELIB-202667520` records the corrected facts and the owner's exact response,
  "Continue v2 and retire the old chain." It authorizes the append-only old-chain
  withdrawal and this corrected v2 continuation. The response was supplied
  directly in the owner transcript; no AskUserQuestion marker or `source_ref`
  is asserted.
- `DELIB-202667519` records the owner's earlier response, "Authorize WI-5657
  exactly as stated," and supplies the bounded recovery authority carried by the
  active PAUTH.
- `DELIB-202667182` authorized the original two-path source/test fix. It remains
  provenance for immutable commit `7b838d9e...` but does not supply this recovery
  or retirement authority.
- Manual Loyal Opposition review remains required. Prime Builder will not spawn,
  impersonate, or substitute a reviewer.

No additional owner decision is required for this revised proposal.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202667519`, `DELIB-202667520`, the
active singleton PAUTH, and the linked specifications fully describe the
bounded recovery and corrected chain disposition. No specification amendment is
needed because this proposal changes no platform behavior; it restores terminal
audit state for an implementation already committed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations And Evidence

- `DELIB-202667520` - owner disposition after correction of the historical
  strict-valid/strict-invalid facts.
- `DELIB-202667519` - owner authorization for the clean v2 recovery scope.
- `DELIB-202667182` - owner authorization for the original checker fix.
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-002.md` - controlling
  NO-GO whose three findings this revision addresses.
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-005.md` - terminal
  old-chain withdrawal filed under `DELIB-202667520`.
- `bridge/gtkb-wi5657-terminal-finalization-recovery-002.md` - first recovery
  NO-GO establishing that source/test paths must be by-reference only.
- `bridge/gtkb-wi5657-terminal-finalization-audit-recovery-006.md` - later
  recovery NO-GO establishing the governance-evidence and commit authority now
  supplied by the active PAUTH.
- commit `7b838d9e7606a8b1f8be75ade78881f63beda170` - immutable implementation and
  historical audit evidence.
- commit `ec7e6b378329fdc6529a25311232235417ccda41` - later WI-5704 terminal
  baseline; current-state non-regression context only.

## Spec-Derived Verification Plan

| Specification | Verification | Required result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run strict lifecycle resolution over this v2 chain and all three historical chains | v2 transitions are strict and role-correct; two historical chains fail only for documented bare identity; old valid chain is terminal WITHDRAWN with zero diagnostics |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Query the active PAUTH, acquire an exact-session claim only after GO, and run implementation-start authorization for the declared report path | Singleton WI, allowed classes only, no forbidden operation consumed, exact report target authorized |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Compare historical and current chain inventories and hashes | Additive recovery and withdrawal evidence; no pre-existing bridge artifact rewritten or deleted |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-derive immutable commit inventory, inspect committed test diff, and run focused protected-commit checker tests at report baseline | Immutable evidence matches and focused regression remains green, with later unrelated baseline differences disclosed |
| `GOV-STANDING-BACKLOG-001` | Read WI-5657 before report, after report, and after terminal verification | One WI remains visible and is reconciled only after VERIFIED |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run applicability preflight and live PAUTH/project/WI lookup | Exact triple resolves with no missing or blocking linkage |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and clause preflights against this exact candidate | No missing required/advisory specification and zero blocking clause gaps |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Inspect the first status of the post-GO report | Report is NEW; zero-mutation facts remain report evidence and never select NO-ACTION |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect old-chain withdrawal, finalizer result, and local commit | Old chain stays terminal WITHDRAWN; v2 VERIFIED exists only with atomic commit evidence |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect the report and terminal include set | Finalization contains the complete v2 chain plus the single named retirement artifact and no other path |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every target and evidence path under `E:/GT-KB` | No out-of-root dependency or artifact |
| `GOV-WORK-TREE-HYGIENE-001` | Run scoped status, staged-diff, and final commit inventory checks | No source/test or unrelated staging enters the recovery commit |

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

The report must distinguish immutable `7b838d9e...` implementation evidence
from current HEAD, including later WI-5704 changes. Current-HEAD tests are
non-regression evidence only. No source/test path may be claimed, staged,
restored, or attributed to WI-5657.

## Acceptance Criteria

1. This v2 chain resolves strictly from version 001 with readable, authorized
   exact-session metadata and no invalid transition.
2. The active PAUTH resolves to WI-5657 only, allows exactly `bridge`,
   `governance_evidence`, and `metadata`, and does not forbid the one bounded
   local terminal commit.
3. The two strict-invalid chains are named accurately and remain unchanged; the
   old strict-valid chain resolves at terminal `WITHDRAWN` version 005 under
   `DELIB-202667520` with zero blocking diagnostics.
4. Commit `7b838d9e7606a8b1f8be75ade78881f63beda170` remains an ancestor and its
   six-path inventory is re-derived exactly.
5. No source, test, configuration, registry, projection, database,
   specification-content, or foreign-thread path other than the single named
   `bridge/gtkb-wi5657-protected-commit-superseded-verified-005.md` retirement
   artifact is changed, restored, staged, or committed by v2
   implementation/finalization.
6. After controlling GO, the Prime Builder recovery report uses status `NEW`
   and records immutable evidence, the current-baseline caveat, focused
   verification, and the complete-chain finalization invariant.
7. Independent Loyal Opposition review either creates terminal VERIFIED and
   the local finalization commit atomically or leaves no terminal candidate.
8. The terminal commit contains exactly every versioned file of this v2 chain
   present at finalization plus the single named retirement artifact and no
   other path; no fixed v2 version count is authoritative.
9. Only after VERIFIED, the canonical backlog service reconciles WI-5657 and
   cites both the immutable implementation commit and terminal recovery commit.
10. No push, history rewrite, dispatcher action, release, deployment,
    credential operation, external-system mutation, or cleanup occurs.

## Risks And Rollback

The primary risk is laundering invalid historical evidence into fresh
authority. The clean slug, strict resolver, exact-session metadata, corrected
per-chain disposition, and terminal withdrawal of the strict-valid old chain
prevent that. A second risk is accidentally staging later source/test changes
or another active thread; the complete-v2-chain-plus-one-named-retirement
invariant and staged-diff assertion bound the finalizer.

There is no destructive rollback. Before terminal commit, a failed helper must
remove its candidate verdict. After terminal commit, corrections are new
governed append-only artifacts or a separately authorized revert. Historical
files and immutable commit `7b838d9e...` are never rewritten.

## Recommended Commit Type

`chore(bridge): finalize WI-5657 terminal recovery`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
