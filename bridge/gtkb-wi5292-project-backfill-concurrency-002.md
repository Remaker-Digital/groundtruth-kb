NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: af8deadc-ebed-461b-994a-6f40241e0f39
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5292 Concurrency-Safe Project Artifact Backfill - NO-GO (first proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5292-project-backfill-concurrency
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5292-project-backfill-concurrency-001.md
Reviewed proposal: bridge/gtkb-wi5292-project-backfill-concurrency-001.md

---

## Verdict Summary

**NO-GO** on two narrow findings, both concerning the *verification* design
rather than the *fix* design.

**The diagnosis and the remedy are correct and should not be re-derived.** The
race is real, precisely located, and the chosen primitive is the right one. The
refusal to paper over the race with a broad conflict-ignore or a blanket
integrity-error catch is correct and should survive revision unchanged. Both
disclosed source baselines reproduce byte-exactly. All ten linked specifications
resolve live, all three cited deliberations exist, and both mandatory preflights
pass.

What blocks GO is that one of the two new tests, **as specified**, would pass
against the unfixed code, and one acceptance criterion has no stated observation
mechanism. Both are cheap to close and neither requires redesigning the fix.

---

## Blocking Findings

### F1 (P2) - The mapped rollback test would pass against unfixed code

**Claim.** The proposal maps `PROJECT-DEP-A2` (failed operation is atomic) to a
single new test described at
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:124-126` and tabulated
at `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:236`. As specified,
that test does not discriminate between the fixed and the unfixed
implementation, so it carries no regression power.

**Evidence.**

- `groundtruth-kb/src/groundtruth_kb/db.py:2436-2437` holds the only commit in
  the backfill method, and it is guarded. There is no rollback call and no
  explicit transaction start anywhere in the method body, which spans
  `groundtruth-kb/src/groundtruth_kb/db.py:2345-2437`.
- `groundtruth-kb/src/groundtruth_kb/db.py:2451-2483` executes the membership
  insert and returns without committing.
- `groundtruth-kb/src/groundtruth_kb/db.py:1754-1758` constructs the connection
  without an explicit isolation level, so the connection runs in the Python
  driver's legacy implicit-transaction mode.
  `groundtruth-kb/src/groundtruth_kb/db.py:1760` enables WAL journaling.

**Why that defeats the test.** Today an exception raised mid-loop leaves every
insert uncommitted inside an open implicit transaction. Under WAL, a separate
observer connection sees none of those rows, and they are discarded when the
connection is closed without committing. The proposal's stated expected result
at `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:288` is therefore
already true before the fix whenever the assertion is made from a fresh
connection. The test would go green on day one and stay green even if the
proposed rollback call were later deleted.

**Risk / impact.** `PROJECT-DEP-A2` would carry a passing test with no power to
detect the regression it purports to guard, and that test would be inherited
into the terminal `VERIFIED` verdict as spec-derived evidence. This is the exact
failure mode the Mandatory Specification-Derived Verification Gate exists to
prevent, and it is why this is blocking rather than advisory.

**Recommended action.** In the revision, state the observer connection
explicitly. The test discriminates only if it asserts against the same
connection returned by the private connection accessor, where the uncommitted
rows are visible today and are erased by the proposed rollback. Additionally,
disclose a measured red baseline for this test against unmodified source,
exactly as the concurrency reproduction was baselined at
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:61-79`. That baseline is
what converts the assertion from a claim into evidence.

### F2 (P2) - Acceptance Criterion 3 has no specified observation mechanism

**Claim.** AC3 at `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:250-251`
requires that a repeat run appends no rows and requires no write transaction on
the no-gap path. The proposal never states how the absence of a write
transaction is observed.

**Evidence.** The only verification-plan row touching this property, at
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:238`, degrades it to a
post-condition about successful reads and unchanged history counts. That holds
identically whether or not a write transaction was taken. No other row in the
table at `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:233-242`
asserts transaction behavior.

**Risk / impact.** The lock-free steady-state path is the proposal's sole
mitigation for the principal risk it identifies itself: over-serializing every
read-only CLI open. If the property is never asserted, that guardrail is
unverified, and a later refactor could silently make every read-only CLI start
acquire a write lock with no test turning red.

**Recommended action.** Name a concrete mechanism and map it to AC3 in the
verification table - for example asserting the connection reports no open
transaction after the no-gap call, or installing a statement trace callback and
asserting no immediate-transaction statement is emitted on that path.

---

## Non-Blocking Findings

### N1 (P3) - Immediate-transaction autocommit precondition is not recorded

Step 1 of the remedy at
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:95` begins an immediate
transaction on the existing connection. Under the legacy isolation mode
confirmed at `groundtruth-kb/src/groundtruth_kb/db.py:1754-1758`, that raises an
operational error if an implicit transaction is already open. This is safe today
because the sole call site is immediately preceded by a commit, but the
precondition is latent and undocumented. Record it in the method docstring,
which is already in scope.

### N2 (P3) - Residual failure class after busy-timeout exhaustion

AC6 at `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:255-256` keeps
the existing busy timeout as the sole bounded contention mechanism. Under
sufficient contention a contender surfaces a database-locked operational error
rather than an integrity error. The failure class changes rather than
disappearing. With a 30-second timeout against a bounded backfill this is low
probability; one sentence acknowledging the residual bound would make the claim
precise.

### N3 (P3) - Duplicate WI-5251 is scoped out with no reconciliation path

The proposal scopes out WI-5251 at
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:150` and characterises
it at `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:200-201`. WI-5251
is presently open at P1 and describes the same defect. After WI-5292 reaches
`VERIFIED`, an open P1 for an already-fixed defect remains in the backlog.
Keeping it out of this packet is correct and the no-KB-mutation declaration at
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:29` should not change,
but a follow-on backlog reconciliation should be noted so the duplicate is not
orphaned.

---

## Positive Confirmations

These were verified against live state and must not be re-litigated in revision.

1. **The defect is real and precisely located.**
   `groundtruth-kb/src/groundtruth_kb/db.py:2367-2368` is an unguarded
   check-then-insert: the existence test is immediately followed by the projects
   insert. `groundtruth-kb/src/groundtruth_kb/db.py:2439-2441` shows the
   existence helper is a bare select in autocommit, holding no lock, so its
   result is stale by the time the insert executes. The same shape recurs for
   membership at `groundtruth-kb/src/groundtruth_kb/db.py:2451-2483`.
2. **The remedy closes the race.** Under WAL, an immediate transaction acquires
   the write lock and establishes the read snapshot at acquisition, so the
   mandated in-transaction re-read at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:96-97` observes the
   winner's committed rows. An immediate transaction also invokes the busy
   handler, whereas upgrading a deferred read transaction yields a snapshot-busy
   condition that does not. The primitive choice is correct, not merely
   convenient.
3. **Refusing to suppress integrity defects is correct**, per
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:107-113`. With a
   uniqueness constraint on identifier and version on both tables, a blanket
   ignore would mask genuine duplicate-version and foreign-key defects.
4. **Both disclosed source baselines reproduce byte-exactly.** Independently
   recomputed SHA-256 digests match the declared values at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:226-229`:
   `f30a24f1785b23bbdf70bab6af9958f49fd40b1eb285bd31d598a12e99d506f7` for the
   source module and
   `927860cbf371056429f24291425a5c5744a1a0cc391a3a687bd971295c2655b4` for the
   test module.
5. **The concurrency test, unlike the rollback test, has genuine regression
   power.** The pre-implementation reproduction at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:61-79` recorded one
   success and eleven failures across twelve synchronized processes. That is a
   measured red baseline, and the wide race window makes the red state robust
   rather than knife-edge. F1 asks the rollback test to meet the bar this test
   already sets.
6. **All ten linked specifications resolve live in MemBase**, each at status
   `specified`, including `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` at the cited
   version 2. No fabricated citation.
7. **All three cited deliberations exist** with matching subject matter:
   `DELIB-202667517`, `DELIB-202667521`, and `DELIB-202666274`.
8. **Scope is correct and nothing is smuggled in.** The backfill is wholly
   contained in the source module and its only call site is in the same file. No
   CLI, schema, pragma, or configuration change is implied. The no-KB-mutation
   declaration is accurate, and the declared target paths are disjoint from
   every other currently-actionable bridge thread.
9. **All required sections are present and substantive**, none placeholder:
   specification links at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:156-187`, prior
   deliberations at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:189-201`, requirement
   sufficiency at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:211-217` with exactly
   one operative state, owner decisions at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:203-209`, recommended
   commit type at
   `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:338`, inline-JSON
   target paths at `bridge/gtkb-wi5292-project-backfill-concurrency-001.md:24`,
   and the status token on the first non-blank line.

---

## Prior Deliberations

Deliberation Archive searched for prior decisions on project-artifact backfill
concurrency using the semantic search entrypoint with the query "project
artifact backfill concurrency race work_items project_name". Nearest hits are
project-layer and backlog-layer records, not this race:

- `DELIB-20264060` - Loyal Opposition Verification, First-Class Project
  Artifacts. Establishes the project and membership artifact layer this backfill
  projects into; does not address concurrent initialization.
- `DELIB-20264063` - Loyal Opposition Review, First-Class Project Artifacts And
  Subject Workflow Model. Same layer, same absence.
- `DELIB-20261050` - Backlog Progress Report, Loyal Opposition Advisory.
  Backlog-layer only.

No prior deliberation adjudicates this race, and no previously-rejected approach
is being silently revisited. The proposal's own three cited deliberations are
the correct governing authorities and were confirmed present.

---

## Review Independence

Reviewer session context `af8deadc-ebed-461b-994a-6f40241e0f39` is distinct from
the reviewed artifact's author session context
`019f863a-acd3-7320-80c0-1831f0936cc0`. Author metadata is present and readable;
the independence gate is satisfied on evidence rather than by assumption.

---

## Methodology Trail

Files inspected: the reviewed proposal in full; the source module regions
`groundtruth-kb/src/groundtruth_kb/db.py:1750-1767`,
`groundtruth-kb/src/groundtruth_kb/db.py:2345-2394`, and
`groundtruth-kb/src/groundtruth_kb/db.py:2425-2486`; the target test module and
the busy-timeout test module for structure; the bridge compliance gate for the
verdict-filing contract; and the bridge state-report module for queue authority.

Commands run, all read-only: `gt bridge state-report`; `gt harness roles`;
`scripts/bridge_applicability_preflight.py` against this thread;
`scripts/adr_dcl_clause_preflight.py` against this thread; independent SHA-256
recomputation of both declared baseline files; a Deliberation Archive semantic
search; MemBase read-only queries for the ten linked specifications, the three
cited deliberations, the cited project authorization, and the current work-item
rows for WI-5292 and WI-5251; and a deterministic target-path intersection
across all three currently-actionable threads.

No file was created, modified, or deleted in the reviewed scope. The proposal's
focused-test and lint claims are statically corroborated - test counts reconcile
and both digests match - but were not independently executed; they must be
executed at post-implementation verification.

---

## Applicability Preflight

- packet_hash: `sha256:86621a6d62ad64f3c0f5dce3cde3c08211bee328f1fe5f8aeff73ff933c2f76d`
- candidate_evidence_hash: `sha256:037de5d9a6e620310d13df2ec0cfe84d0155b93caf443dc0ad661329c8ef40bb`
- bridge_document_name: `gtkb-wi5292-project-backfill-concurrency`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_project_artifacts.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5292-project-backfill-concurrency-001.md`
- operative_file: `bridge/gtkb-wi5292-project-backfill-concurrency-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5292-project-backfill-concurrency`
- Operative file: `bridge\gtkb-wi5292-project-backfill-concurrency-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

Both mandatory preflights pass against the reviewed operative file. The
preflight floor is satisfied; this NO-GO rests on the specification-derived
verification gate, not on a mechanical gap.

---

## What Revision Requires

Only F1 and F2. Concretely:

1. Specify the observer connection for the rollback test and disclose its
   measured red baseline against unmodified source (F1).
2. Name an observation mechanism for the no-write-transaction property on the
   no-gap path and map it to AC3 in the verification table (F2).

Optionally fold in N1 as a docstring precondition and N2 as one sentence on the
residual timeout class, and note N3 as follow-on backlog reconciliation.

Everything else in version 001 is accepted. The fix design, the primitive
choice, the refusal to suppress integrity defects, the scope boundary, the
specification linkage, and both source baselines carry forward unchanged.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
