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

# WI-5786 WI-5629 False-Terminal Recovery — Owner-Approval Evidence Correction

bridge_kind: prime_proposal
Document: gtkb-wi5786-wi5629-false-terminal-recovery
Version: 007
Responds to: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-006.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5786

target_paths: ["bridge/gtkb-wi5786-wi5629-false-terminal-recovery-009.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

KB Mutation: This proposal performs no MemBase write or mutation.

## Summary

Continue the bounded, evidence-only WI-5786 recovery. Version 006 correctly
required durable owner-approval evidence, but incorrectly treated the legacy
work-item `approval_state` label as an implementation-authority gate. The owner
approval is now explicit and durable in
`DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL`.

The authoritative execution chain remains conjunctive: active project
authorization, independent GO, exact live claim, and fresh schema-v3
implementation-start packet. The compatibility field `approval_state` neither
grants nor blocks execution and will not be fabricated or directly mutated.

Because versions 006 and 007 consumed the former report slots, the corrected
lifecycle is:

```text
REVISED -007 -> independent GO -008 -> factual NEW report -009
  -> independent VERIFIED or NO-GO -010
```

No source, test, configuration, dispatcher, registry, projection, or database
change is in implementation scope. The report will re-derive evidence from the
current repository and independent Loyal Opposition will control any terminal
verdict and exact commit-first finalization.

## Revision Claim

Prime Builder session `019f9b59-52a0-75b2-9973-bd5601f98e9f` acquired the
exact `draft` work-intent claim for this slug at `2026-08-01T09:01:18Z`, rowid
`35975`, with expiry `2026-08-01T10:01:18Z`. The claim was current before
substantive drafting and will be released after governed publication.

## Response To Version 006 Finding

### P1 — Work-item approval is absent

Resolved with both durable owner evidence and the controlling authority model.

- `DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL` records the owner's
  persistent instruction to terminalize every Dispatcher Next constituent,
  derived, and upstream-dependent work item and expressly approves this bounded
  WI-5786 recovery under all normal gates.
- The WI-5786 row already records the exact source owner directive: reconcile
  WI-5629 before using it as a clean dependency and do not silently hand-stage
  the malformed VERIFIED payload.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` v2 is
  active, unexpired, list-free, and covers active project member WI-5786.
- `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py` states that
  `approval_state` is historical metadata only and that project authorization,
  live GO, and implementation-start are the implementation authority chain.
  Its transition validator likewise states that changing the legacy label does
  not grant or block authority.
- `gt backlog update` exposes no `approval_state` mutation option. Writing that
  field directly would bypass the canonical lifecycle and create misleading
  authority evidence.

The version-006 request for owner approval is therefore satisfied. The stale
legacy label is disclosed rather than laundered, and execution still cannot
begin without an independent GO, exact claim, and fresh start packet.

## Current Revalidated Baseline

At HEAD `75decbfa704fe50288aecbc5669def329a0825df`:

- Implementation commit
  `1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4` is an ancestor and contains
  exactly `scripts/implementation_authorization.py` and
  `platform_tests/scripts/test_implementation_authorization.py`.
- False-verdict commit
  `db07f9dcfe7e7de8addc850729209278472cb0fe` is an ancestor and contains
  532 paths; it is not represented as a scoped terminal transaction.
- The two live subject paths are clean. Their current SHA-256 hashes are
  `bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891`
  and `d59aca8a1c31fc0a3b3cbc6bebc8bc542735feda79bcbeb0eeb19ccff337e98f`.
- All 30 historical WI-5629 files are present; the deterministic
  `filename:sha256` manifest hash is
  `824d0aac5c592092af6fa01c21a7205d28506eacb6e61e480122fe5e56412049`.
- Recovery versions 001–003 are committed in custodial sweep
  `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`. Versions 004–006 are
  untracked continuation evidence. No claim is made that the sweep was scoped
  finalization.

Every baseline fact must be re-run after GO. Current-HEAD test results are
non-regression evidence only and do not rewrite the immutable implementation
snapshot.

## Revised Terminal Commit Boundary

The prospective terminal commit must contain exactly the then-uncommitted
continuation cohort:

- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-004.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-005.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-006.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-007.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-008.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-009.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-010.md`

The terminal reviewer must revalidate this cohort immediately before staging
and commit. Versions 001–003 and every historical WI-5629 file remain unchanged;
the source/test subjects are by-reference only and must not be staged.

## Implementation Plan

1. Obtain independent GO responding to version 007.
2. Revalidate the active project authorization, WI membership, exact path
   overlap, and current Git/bridge state.
3. Acquire a fresh `go_implementation` claim and finalize a schema-v3 start
   packet admitting only version 009.
4. Re-derive both commit inventories and ancestor checks, the 30-file manifest,
   and exact HEAD blobs for recovery versions 001–003.
5. Run the focused authorization suite, Ruff lint, Ruff format check, and
   path-scoped diff check without editing the subject files.
6. File version 009 as the factual `NEW` implementation report through the
   governed writer.
7. Route version 009 to a session-independent Loyal Opposition reviewer. A
   terminal outcome must use the governed commit-first finalizer with the exact
   seven-path continuation cohort.
8. Reconcile WI-5629 and WI-5786 backlog metadata only after commit-backed
   terminal verification through separately authorized canonical operations.

## Requirement Sufficiency

Existing requirements sufficient. This revision changes no runtime or product
behavior. It corrects the recovery proposal's owner-approval evidence and
execution version slots while preserving the already-governed exact-path,
by-reference, commit-first recovery contract.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only role authority and terminal
  lifecycle.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project PAUTH, claim, and
  implementation-start authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — owner/project approval does
  not bypass bridge review.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time
  revalidation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve and repair forward.
- `GOV-ARTIFACT-APPROVAL-001` — separately applicable formal-artifact gates.
- `GOV-STANDING-BACKLOG-001` — post-terminal metadata reconciliation.
- `GOV-WORK-TREE-HYGIENE-001` — exact-path staging and foreign-change
  exclusion.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — version 003 cannot terminalize the
  chain.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed evidence before
  VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — exact linkage and
  test derivation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — evidence-bearing lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all dependencies stay under
  `E:/GT-KB`.

## Spec-To-Test Mapping And Verification Commands

| Requirement | Evidence required in version 009 |
| --- | --- |
| Bridge authority and lifecycle | Strict resolver over versions 001–009; exact status sequence and immutable prior versions |
| Project implementation authority | Current PAUTH/project/WI reads plus successful schema-v3 packet for version 009 |
| Specification-derived verification | Focused pytest, Ruff lint, Ruff format, and diff check |
| Artifact preservation | Before/after 30-file manifest and HEAD-blob checks for versions 001–003 |
| Worktree hygiene | Exact versions 004–010 staged census; every foreign path excluded |
| Root isolation | Every target and evidence path resolves beneath `E:/GT-KB` |

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

## Prior Deliberations

- `DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL` — explicit scoped
  owner approval for this bounded recovery.
- `DELIB-202667721` — controlling list-free Housekeeping Hardening project
  authorization.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and
  `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-level
  approval is authoritative; per-WI approval labels are retired compatibility
  metadata.
- `DELIB-202667533` — commit-first, publish-after finalization ordering.
- `DELIB-202667348` — WI-5629 non-terminal recovery evidence.
- `DELIB-202667191`, `DELIB-202667519`, and
  `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS` — bounded by-reference and
  stranded-terminal recovery discipline.

## Owner Decisions / Input

- The owner explicitly approved this bounded WI-5786 continuation in
  `DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL` as part of the
  persistent Dispatcher Next mandate.
- The controlling project approval is `DELIB-202667721`, expressed through the
  active list-free PAUTH cited above.
- The owner has not cancelled WI-5786. No further owner decision is required
  before independent review.

## Pre-Filing Preflight Subsection

Candidate applicability preflight against this revision passed with
`preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, `blocking_errors: []`, and operation-time PAUTH
status `allowed` for the exact version-009 target cohort. Mandatory clause
preflight evaluated five clauses, classified four `must_apply`, found zero
evidence gaps and zero blocking gaps, and exited 0. The filing helper will rerun
both content-bound checks and refuse publication on any blocking result. The
by-reference test command may produce advisory target-coverage output for the
existing test file; it is deliberately not a mutation target.

## Acceptance Criteria

1. Durable scoped owner approval is cited and independently validated.
2. No reviewer treats legacy `approval_state` metadata as authority or mutates
   it to manufacture authority.
3. Independent GO responds to version 007 and authorizes only version 009.
4. A fresh exact claim and schema-v3 start packet are current at execution.
5. Both immutable commit inventories, both ancestor checks, the 30-file
   manifest, and the live subject hashes are re-derived.
6. No source, test, configuration, database, dispatcher, registry, projection,
   or unrelated shared path is modified, restored, staged, or committed.
7. Version 009 distinguishes immutable implementation evidence from current
   non-regression evidence.
8. Independent verification either creates an exact commit-backed version 010
   or leaves the chain non-terminal.
9. The terminal commit contains exactly versions 004–010.
10. Backlog reconciliation occurs only after commit-backed terminal evidence.
11. No push, release, deployment, credential work, external mutation, history
    rewrite, or destructive cleanup occurs.

## Risk And Rollback

The principal risks are laundering WI-5629's false terminal, mistaking legacy
metadata for authority, or absorbing concurrent worktree changes. Durable owner
evidence, conjunctive operation-time gates, by-reference evidence, and exact
seven-path finalization constrain those risks.

Before terminal commit, any failure leaves the chain non-terminal and permits a
fresh append-only revision. After valid terminal commit, correction remains
append-only. No source or historical bridge content is rewritten.

## Recommended Commit Type

`chore(bridge): finalize WI-5786 false-terminal recovery`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
