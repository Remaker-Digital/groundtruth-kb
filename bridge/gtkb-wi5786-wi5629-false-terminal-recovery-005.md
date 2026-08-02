REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; Prime Builder; build activity
author_metadata_source: open session envelope and current transcript

# WI-5786 WI-5629 False-Terminal Recovery — Corrected Execution Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5786-wi5629-false-terminal-recovery
Version: 005
Responds to: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-004.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5786

target_paths: ["bridge/gtkb-wi5786-wi5629-false-terminal-recovery-007.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

KB Mutation: This proposal performs no MemBase write or mutation.

## Summary

Proceed with the still-required WI-5629 false-terminal recovery. Version 003's
attempt to close the work with `NO-ACTION` is preserved as invalid historical
evidence; it is not treated as closure. Version 004 correctly requires a factual
recovery report or explicit owner cancellation. No cancellation exists.

This revision restores the normal lifecycle with a fresh report slot:

```text
REVISED -005 -> independent GO -006 -> factual NEW report -007
  -> independent VERIFIED or NO-GO -008
```

After a fresh GO, Prime Builder will acquire an exact implementation claim,
finalize a fresh schema-v3 start packet bound to this revision and the GO, make
no source or test mutation, re-derive all evidence from current Git state, run
the required verification, and file only version 007. Independent Loyal
Opposition will then review and, if warranted, use the governed commit-first
finalizer for version 008.

## Response To Version 004 Findings

### F1 — NO-ACTION cannot disposition-close the accepted recovery

Accepted. Version 003 remains in the append-only chain but has no terminal or
implementation effect. This revision expressly rejects its "stale GO" and
"disposition-close" rationale. An absent claim never cancels approved work.

### F2 — No factual recovery implementation report exists

Accepted. This revision reserves version 007 as the new exact implementation
report target. The report must contain current re-derived Git inventory,
historical-chain integrity evidence, current non-regression results, the
live-baseline caveat, and the exact terminal commit cohort. No result from
version 001 is inherited without rerunning its command.

## Current Revalidated Baseline

Read-only evidence collected at HEAD
`75decbfa704fe50288aecbc5669def329a0825df`:

- Implementation commit
  `1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4` is an ancestor of HEAD and
  contains exactly:
  - `scripts/implementation_authorization.py`
  - `platform_tests/scripts/test_implementation_authorization.py`
- Historical verdict commit
  `db07f9dcfe7e7de8addc850729209278472cb0fe` is an ancestor of HEAD and
  contains 532 paths.
- Both live implementation subject paths are clean in the worktree.
- Their current live SHA-256 values are:
  - source:
    `bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891`
  - test:
    `d59aca8a1c31fc0a3b3cbc6bebc8bc542735feda79bcbeb0eeb19ccff337e98f`
- All 30 historical WI-5629 files are present. A deterministic manifest over
  `filename:sha256` lines currently hashes to
  `824d0aac5c592092af6fa01c21a7205d28506eacb6e61e480122fe5e56412049`.
- Recovery versions 001–003 are already committed in custodial sweep
  `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`; version 004 is currently an
  untracked, status-bearing Loyal Opposition verdict. This revision does not
  pretend that sweep was a scoped finalization.

The factual report must re-run and record these facts. Current-HEAD test results
are non-regression evidence only; they do not rewrite the immutable
`1aa2182b` implementation snapshot.

## Revised Terminal Commit Boundary

Because versions 001–003 are already committed, they cannot truthfully be
recommitted as new paths. The prospective recovery terminal commit must contain
exactly the uncommitted continuation cohort:

- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-004.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-005.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-006.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-007.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-008.md`

The report and terminal reviewer must revalidate that versions 004–008 are the
only staged paths. Versions 001–003 and all 30 WI-5629 historical files remain
unchanged. The source/test subjects are by-reference only and must not be
restaged or included.

## Implementation Plan

1. Obtain independent GO on this revision.
2. Revalidate the active list-free project authorization and exact work-item
   membership.
3. Acquire the exact live claim for this slug and mint a fresh schema-v3
   implementation-start packet admitting only version 007.
4. Re-derive the two-path and 532-path commit inventories and both ancestor
   checks.
5. Hash all 30 historical WI-5629 files and compare the before/after manifest.
6. Run the focused authorization suite and both Ruff gates against the clean
   live subjects.
7. Verify versions 001–003 remain the exact blobs already in HEAD and record
   version 004's preimage.
8. File version 007 as the first post-GO `NEW` implementation report through
   the governed writer.
9. Route version 007 to an independent Loyal Opposition session. A
   `VERIFIED` outcome must use the commit-first finalizer and exact five-path
   continuation cohort above.
10. Reconcile WI-5629 and WI-5786 backlog metadata only after the recovery
    verdict is commit-backed and terminal, through separately authorized
    canonical lifecycle operations.

## Requirement Sufficiency

Existing requirements sufficient. This revision changes no product behavior.
It corrects the recovery chain's execution slot and commit cohort after the
invalid version-003 closure and subsequent custodial commit changed the factual
baseline.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only lifecycle, exact role
  authority, and commit-backed terminal verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active project PAUTH,
  exact claim, and implementation-start requirements.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserve invalid v003 and the
  original WI-5629 chain as evidence.
- `GOV-ARTIFACT-APPROVAL-001` — class authority does not replace any
  separately applicable formal-artifact packet.
- `GOV-STANDING-BACKLOG-001` — post-terminal work-item reconciliation.
- `GOV-WORK-TREE-HYGIENE-001` — exact-path staging and foreign-change
  exclusion.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — NO-ACTION corrects a verdict and
  cannot serve as terminal closure.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed evidence and
  specification-to-test mapping before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — exact PAUTH,
  project, WI, and target metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete
  specification-derived verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — no terminal state without its
  required evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — correct through a new governed
  version rather than history rewriting.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all live dependencies remain
  within `E:/GT-KB`.

## Spec-To-Test Mapping And Verification Commands

| Requirement | Executed evidence required in version 007 |
| --- | --- |
| File-bridge authority and artifact lifecycle | Strict resolver on versions 001–007; exact status sequence; no mutation of previous versions |
| Project implementation authority | Current PAUTH/project/WI lookup plus successful schema-v3 packet admitting only version 007 |
| Spec-derived verification | Focused pytest suite, Ruff lint, Ruff format check, and diff check |
| Artifact preservation | Deterministic before/after 30-file manifest and exact HEAD blob checks for versions 001–003 |
| Worktree hygiene | Exact staged-path census for versions 004–008; source/test and unrelated shared paths excluded |
| Root isolation | Resolve every target and evidence path beneath `E:/GT-KB` |

Required commands include:

```powershell
git --no-optional-locks diff-tree --no-commit-id --name-only -r 1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4
git --no-optional-locks diff-tree --no-commit-id --name-only -r db07f9dcfe7e7de8addc850729209278472cb0fe
git --no-optional-locks merge-base --is-ancestor 1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4 HEAD
git --no-optional-locks merge-base --is-ancestor db07f9dcfe7e7de8addc850729209278472cb0fe HEAD
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
git --no-optional-locks diff --check -- scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5786-wi5629-false-terminal-recovery
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5786-wi5629-false-terminal-recovery
```

## Pre-Filing Preflight Evidence

Candidate applicability preflight against this exact draft passed:

- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- project-authorization operation-time evaluation: `allowed`
- evaluated cohort:
  `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-007.md`

The governed filing helper emits the final packet hash in its publication
receipt; this draft does not self-embed a content-derived hash.

The mandatory clause preflight passed with five clauses evaluated, four
`must_apply` clauses, zero evidence gaps, zero blocking gaps, and exit 0.

The advisory target-path coverage preflight reports the existing test file as an
uncovered verification path because it appears in an executed read-only test
command. That path is deliberately excluded from `target_paths`: the accepted
recovery is governance-evidence-only, the source and test are immutable
by-reference subjects, and authorizing their mutation would violate this
proposal's boundary. The implementation report must execute the test without
editing, restoring, staging, or attributing the file.

## Prior Deliberations

- `DELIB-202667533` — owner-ratified commit-first, publish-after
  finalization ordering.
- `DELIB-202667721` — active list-free Housekeeping Hardening project
  authorization covering WI-5786 through normal per-WI governance.
- `DELIB-202667720` and `DELIB-202667719` — correction and controlling
  authorization precedence.
- `DELIB-202667734` — v2 PAUTH schema-shape repair.
- `DELIB-202667348` — WI-5629 non-terminal recovery evidence precedent.
- `DELIB-202667191` and `DELIB-202667519` — bounded by-reference
  finalization precedents.
- `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS` — exact-path recovery
  discipline for stranded terminal transactions.
- Version 004 of this chain — no owner cancellation found; factual recovery or
  explicit cancellation required.

## Owner Decisions / Input

- The owner authorized the list-free Housekeeping Hardening grant in
  `DELIB-202667721`; its active version 2 remains controlling.
- The owner required the WI-5629 false terminal to be reconciled and forbade
  silent hand-staging of the malformed historical payload when WI-5786 was
  created.
- `DELIB-202667533` selects commit-first finalization ordering.
- No owner cancellation of WI-5786 exists. No new owner input is required for
  this bounded continuation.

## Acceptance Criteria

1. Version 003 remains preserved but has no closure effect.
2. Independent GO responds to this version 005 and authorizes only the version
   007 report target.
3. A fresh exact claim and schema-v3 start packet are current at execution.
4. The two-path implementation commit and 532-path false-verdict commit are
   independently re-derived and remain ancestors of HEAD.
5. The 30-file WI-5629 historical manifest is unchanged.
6. No source, test, configuration, database, dispatcher, registry, or
   projection path is modified, restored, staged, or committed.
7. Version 007 carries complete factual evidence and distinguishes immutable
   implementation evidence from current-HEAD non-regression evidence.
8. Independent verification either creates an exact commit-backed version 008
   or leaves the chain non-terminal.
9. The terminal commit contains exactly versions 004–008.
10. Backlog reconciliation occurs only after commit-backed VERIFIED.
11. No push, release, deployment, credential operation, external mutation,
    history rewrite, or destructive cleanup occurs.

## Risks And Rollback

The main risks are laundering the original false terminal, treating v003 as
closure, or absorbing shared worktree changes. The clean recovery slug,
immutable-commit distinction, five-path terminal cohort, and independent
verification prevent those outcomes.

Before terminal commit, failure leaves the chain non-terminal and the governed
writer removes any invalid candidate according to its contract. After a valid
terminal commit, corrections are append-only and separately governed. No
historical file or Git history is rewritten.

## Recommended Commit Type

`chore(bridge): finalize WI-5786 false-terminal recovery`

The recovery adds governance evidence only and changes no product behavior.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
