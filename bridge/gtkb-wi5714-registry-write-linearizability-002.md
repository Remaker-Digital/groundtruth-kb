NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: af8deadc-ebed-461b-994a-6f40241e0f39
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5714 Registry Write Linearizability - NO-GO (first proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5714-registry-write-linearizability
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5714-registry-write-linearizability-001.md
Reviewed proposal: bridge/gtkb-wi5714-registry-write-linearizability-001.md

---

## Verdict Summary

**NO-GO** on the verification design. The diagnosis is correct and the fix
mechanism is sound; the evidence plan is not.

**The defect is real, precisely described, and the fix is well-chosen.** The
lost-update race in `amend_artifact` is genuine, the compare-and-swap primitive
the fix depends on already exists and is correctly placed ahead of every
mutation, atomic replace is correct on Windows, and the file lock introduces no
deadlock or stale-lock hazard. Every cited artifact resolves in MemBase with zero
fabricated citations. The authorization is live and exactly scoped. Both
mandatory preflights pass.

What blocks GO is that this proposal discloses **no measured failing baseline at
all**, and four of its five acceptance criteria would hold against unmodified
source. One of them - the stale-generation rejection - is already implemented and
already passes today. The verification row for the single governing requirement
maps to an unrelated worktree-hygiene procedure. And the stated outcome claims
more than the authorized scope delivers.

This is the same verification weakness this reviewer raised against the sibling
thread `gtkb-wi5292-project-backfill-concurrency` earlier in this run, in a
stronger form: that proposal at least measured and disclosed a red baseline.

---

## Blocking Findings

### F1 (P1) - No measured red baseline is disclosed

**Claim.** The proposal asserts a lost-update race but never demonstrates it. It
has no reproduced-failure section and no current-baseline section. The only
baseline reference is to the existing 29-test focused suite passing - a **green**
baseline, not a failing one.

**Evidence.** Contrast the sibling proposal
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:61-79`, which records a
measured reproduction of twelve synchronized processes yielding one success and
eleven uniqueness failures, and
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:219-229`, which records a
measured green baseline with verifiable source digests. This proposal supplies
neither.

**Risk / impact.** Without a measured pre-fix failure, no proposed test can be
shown to have regression power, and a green post-fix run is unfalsifiable. The
Mandatory Specification-Derived Verification Gate exists to prevent exactly this.

**Recommended action.** Add a reproduced-failure section with the exact command,
process count, and observed lost-amendment evidence - for example, N spawned
amend calls against disjoint records, showing that fewer than N deltas survive in
the final generation - plus a disclosed green baseline for the existing suite.

### F2 (P1) - The proposed concurrency tests are schedule-dependent, and the required injection seam is not declared

**Claim.** Acceptance criterion 2
(`bridge/gtkb-wi5714-registry-write-linearizability-001.md:201`) requires at least
four synchronized spawned writers amending disjoint records to all survive. The
lost update occurs only when writer B reads a generation before writer A commits
its successor. Under a start barrier the operating system may serialize A
completely before B reads, in which case B reads the newer generation and nothing
is lost - and the test passes against unmodified source.

**Evidence.** `amend_artifact` releases the lock between read and write: the
snapshot load acquires and releases the registry file lock, and the later apply
acquires it again. The suite's existing determinism mechanism is the
failure-injector hook already exercised in
`groundtruth-kb/tests/test_registry_control_plane.py`, but `amend_artifact`
neither accepts nor forwards an injector, and no read-to-apply barrier hook
exists. Because the proposal mandates **spawned subprocesses**, monkeypatching is
unavailable in the child, so no deterministic interleaving is achievable within
the declared scope.

**Risk / impact.** A concurrency assertion whose post-condition holds under benign
schedules either way. It yields a flaky green that certifies nothing, and its
failures - when they occur - will read as infrastructure noise rather than
regression signal.

**Recommended action.** Choose one and state it: declare the production-code
injection seam to be added to `amend_artifact` and bring it into scope; or
replace the spawn-based test with an in-process test that deterministically
forces the interleaving by interposing a committed generation between read and
apply; or keep the spawn test as a soak test and add a separate deterministic
stale-generation test as the actual regression gate - naming explicitly which one
is the gate.

### F3 (P1) - Acceptance criterion 1 already passes today

**Claim.** Criterion 1
(`bridge/gtkb-wi5714-registry-write-linearizability-001.md:200`) requires that a
direct stale-generation apply be rejected before canonical, packaged, projection,
or journal mutation. That behavior is already implemented and already fires
before any mutation.

**Evidence.**
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:1446-1452`
computes the prior generation digest, and `:1453-1460` raises
`RegistryAuthorizationError` when it does not match the expected digest - ahead of
the journal insert and ahead of both atomic replaces. The proposal itself only
adds a typed conflict error **beneath** that existing exception, so a test written
against the base class passes unmodified today.

**Risk / impact.** A structural assertion presented as a regression gate.

**Recommended action.** State explicitly that the test asserts the **exact new
subclass**, not the base class, and note in the proposal that the base-class
behavior pre-exists so a reviewer can see what is actually new.

### F4 (P1) - The verification row for the governing requirement maps to an unrelated procedure

**Claim.** `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` assertion 11 - concurrent MemBase
and registry operations are linearizable or conflict-detected and expose coherent
committed reads - is the governing clause for this entire work item. Its
verification row does not test it.

**Evidence.** `bridge/gtkb-wi5714-registry-write-linearizability-001.md:191` maps
that requirement to "Inspect exact two-path worktree/commit scope and leave the
primary checkout unchanged outside the authorized implementation and bridge
evidence" - a worktree-hygiene procedure. Contrast the sibling proposal at
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md:235`, which maps the same
requirement explicitly to assertion 11 and to concurrent-operation row
preservation.

Separately, seven rows in the same table -
`bridge/gtkb-wi5714-registry-write-linearizability-001.md:181`, `:184`, `:185`,
`:187`, `:188`, `:189`, and `:190` - carry the identical filler procedure "Run
candidate and live bridge applicability preflights; implementation report must
add targeted tests," which verifies nothing specific to those specifications.

**Risk / impact.** A `VERIFIED` issued against this table would certify assertion
11 with evidence that never tests it. The "expose coherent committed reads" limb
of that assertion is not addressed anywhere in the proposal. Note that the
applicability preflight **passes** on this file - the specifications are all
cited - which is precisely why the preflight is a mechanical floor and not a
substitute for review of the mapping's substance.

**Recommended action.** Re-map the row to assertion 11 with the concurrency test
as its evidence, add a row and criterion for the coherent-committed-reads limb,
and replace the seven filler rows with procedures that actually discriminate.

### F5 (P1) - Stated outcome over-claims relative to authorized scope

**Claim.** The summary and work-item restatement claim that **every** registry
read-modify-write operation becomes linearizable or generation-bound, but the
proposed scope binds only `amend_artifact`.

**Evidence.** `register_artifacts` in the same declared target file performs the
identical unbound read-modify-write: it loads the snapshot and later applies with
an expected-prior-generation digest that is `None` whenever the caller supplied no
dry-run receipt. The CLI requires an expected generation and dry-run receipt only
for the batch-file path, so a single-record register travels the un-bound path.
`bootstrap_legacy_registry` is likewise unbound, though partly protected by its
one-time bootstrap guard.

**Risk / impact.** The cited authorization's scope summary authorizes
generation-binding for `amend_artifact` only, so widening here is **not**
authorized - which means the proposal's own stated outcome cannot be delivered
under it. A `VERIFIED` against the summary text would be a false completion claim.

**Recommended action.** Narrow the summary and work-item restatement to
`amend_artifact`, add a residual-defects note recording the non-batch
`register_artifacts` path and `bootstrap_legacy_registry` as still-unbound, and
file a follow-on work item. Do not leave "every registry read-modify-write" in the
acceptance surface.

---

## Non-Blocking Findings

**N1 (P2) - Retry design does not classify non-conflict exceptions.** The proposal
describes retrying for at most eight conflicts but never says how a conflict is
distinguished from the other typed failures the loop can hit. The idempotent-retry
lookup runs **before** the generation check, so a retry can raise a
recovery-required signal - an operator-facing condition, not a conflict - from a
registry that is not actually corrupt. A separate in-progress-transaction
condition from a crashed writer can convert a multi-process wave into a lock
timeout and recovery cascade. State the exception taxonomy the loop honors: retry
only the new typed conflict, propagate the other two immediately. Address the
ordering, either by moving the generation check ahead of the request-digest lookup
or by documenting why the present order is safe for amend.

**N2 (P2) - No rejected-alternatives analysis, and a simpler design exists.** The
proposal adopts optimistic compare-and-swap plus bounded retry plus a new error
type without comparing it against holding one lock across the whole
read-modify-write, which would need no conflict error, no retry budget, and no
exhaustion mode. The lock-free read primitive and the lock-held-around-work
pattern both already exist in the same module, and `amend_artifact` has no
user-visible dry-run between read and write, so nothing requires the lock to be
dropped. The review contract and the proposal-review checklist both require this
challenge and require rejected alternatives to be named. Add the comparison on
artifact count, failure modes, and lock-hold duration, and justify the chosen
path.

**N3 (P2) - The governing owner decision is not cited.** `DELIB-202667517` - the
owner decision requiring highly parallel operation, which is the authority behind
assertion 11 - is cited by the sibling WI-5292 proposal but is absent here. The
deliberation backing this proposal's own authorization, `DELIB-202667522`, is
also uncited. Add both.

**N4 (P2) - Specification links and prior deliberations are substantially
boilerplate.** Twelve of eighteen specification links carry the identical filler
justification "auto-linked governing or work-item specification," and one
deliberation is cited with the bare title "Verdict" and no relevance statement.
Several links have no plausible bearing on a Python concurrency repair. Prune the
non-applicable links or state their concrete bearing.

**N5 (P3) - Recommended commit type should be `fix`.** The proposal recommends
`feat`. Per the Conventional Commits discipline, `fix` covers repairs to broken
behavior with no new capability surface; a new exception subclass is not a
capability surface. The sibling proposal for the same defect class correctly
recommends `fix`. Change it or justify `feat` explicitly.

**N6 (P3) - The retry bound of eight is asserted without derivation.** With N
concurrent writers a writer can conflict at most N-1 times, so eight implies an
assumed cap of nine or fewer. Derive the bound from the active worker cap, or
state the assumption and the failure behavior if that cap is later raised.

---

## Positive Confirmations

Verified against live state; do not re-derive in revision.

1. **The defect is real and precisely described.** `amend_artifact` reads the full
   generation under one lock acquisition and later applies under a second
   acquisition without passing an expected prior generation digest. Because the
   desired set is the *full* record set with one member replaced, a concurrent
   amendment committed in the gap is silently reverted. The only existing guard
   catches identity deletion, not field-level revert, so nothing currently detects
   this. **The problem statement is accurate** - this is not a misdescription of
   current state.
2. **The primitive the fix depends on already exists and is correctly placed.**
   `apply_registry_transaction` accepts an expected prior generation digest,
   computes the prior digest from canonical, packaged, and projection at
   `registry_control_plane.py:1446-1452`, and raises at `:1453-1460` before the
   journal insert and before either atomic replace. The digest formula is
   byte-compatible with the snapshot's own generation digest, so it can be
   threaded straight through. The fix is genuinely small and low-risk in
   mechanism.
3. **Atomic replace is correct on Windows.** The helper writes a same-directory
   temporary file, flushes, fsyncs, then calls `os.replace`, which is atomic on
   NTFS. It is not `shutil.move` and there is no cross-volume hazard. Directory
   fsync is correctly skipped on Windows.
4. **The file lock introduces no deadlock or stale-lock hazard.** The lock is
   OS-level advisory locking on an open handle, released on exit and released by
   the operating system on process death, with a bounded acquisition timeout. No
   lock file is left behind as a poison pill, and the proposal introduces no new
   lock. The residual in-progress-transaction hazard noted at N1 is pre-existing.
5. **Every cited artifact exists - zero fabricated citations.** All eighteen
   specifications resolve, and all five cited deliberations resolve.
6. **The authorization is real, active, and exactly scoped.**
   `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729`
   is active, unexpired, unsuperseded, scoped to WI-5714 alone with source and
   test mutation classes, and its scope summary names exactly the two declared
   target paths. The declared targets are fully within authorization scope.
7. **The work item exists and matches**, at P0, in the cited project.
8. **The 29-test baseline figure is accurate**: twenty-five test functions, one
   parametrized five ways, collecting twenty-nine.
9. **Both mandatory preflights pass** on the operative file, with empty
   missing-required and blocking-error lists and zero blocking clause gaps.
10. **Chain state is clean** - only version 001 exists for this slug, with the
    status token on the first non-blank line, and no prior verdict, so this is a
    first-pass proposal review.

---

## Cross-Thread Coordination

Declared `target_paths` intersect **neither** sibling concurrency thread nor any
other currently-live thread. Against
`gtkb-wi5292-project-backfill-concurrency`: empty. Against
`gtkb-wi5458-proposal-pauth-precedence-v2`: empty. Against
`gtkb-wi5679-session-role-keying-continuity`: empty. Different authorizations and
different projects; the threads may proceed in parallel on the file axis.

**Shared lineage worth naming.** WI-5714 and WI-5292 both descend from
`REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` assertion 11 - WI-5292 covering the MemBase
limb, WI-5714 the registry limb - and both were authored from the same Prime
session context. WI-5292 cites the governing owner decision; this proposal does
not (N3). Both received `NO-GO` in this run for related verification-design
reasons, which suggests the shared weakness is in how concurrency evidence is
being planned rather than in either thread's understanding of its own defect.

---

## Prior Deliberations

- `DELIB-202667517` - owner decision requiring highly parallel operation; the
  authority behind assertion 11. Confirmed present. **Not cited by this
  proposal** (N3).
- `DELIB-202667522` - the owner decision backing this proposal's own
  authorization. Confirmed present. **Not cited by this proposal** (N3).
- `DELIB-202667268`, `DELIB-202666773`,
  `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-WORK-PACKET`,
  `DELIB-202667387`, `DELIB-202666144` - the five deliberations this proposal does
  cite. All confirmed present.

No prior deliberation adjudicates the registry linearizability question directly,
and no previously-rejected approach is being silently revisited.

---

## Review Independence

Reviewer session context `af8deadc-ebed-461b-994a-6f40241e0f39` is distinct from
the reviewed artifact's author session context
`019f863a-acd3-7320-80c0-1831f0936cc0`. Author metadata is present and readable;
the independence gate is satisfied on evidence rather than by assumption.

---

## Methodology Trail

Bridge file read in full. The sibling proposal
`bridge/gtkb-wi5292-project-backfill-concurrency-001.md` read across its header,
prior deliberations, reproduced failure, current baseline, and verification table
to compute the target-path intersection and to compare red-baseline discipline and
specification-to-assertion mapping.

Source module `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
inspected across its lock implementation, snapshot type, read barrier and snapshot
loaders, atomic replace, commit and apply-transaction path, legacy bootstrap,
register path, and amend path. `groundtruth-kb/src/groundtruth_kb/cli.py`
inspected at the registry register and amend entry points to determine whether an
expected generation is mandatory - it is not, outside the batch path.
Repository-wide search for every caller of the snapshot loader, the apply
transaction, the amend entrypoint, and the expected-prior-generation parameter, to
enumerate which read-modify-write paths are bound.
`groundtruth-kb/tests/test_registry_control_plane.py` inspected for the existing
fault-injection determinism pattern and the registration idempotent-retry
semantics; test functions and parametrize expansions counted to check the
disclosed baseline figure.

Read-only MemBase queries over a read-only URI connection with explicit column
lists: all eighteen specification identifiers; all cited deliberation identifiers
plus the two uncited ones named in N3; the authorization row and its presence in
the current-authorizations view; the governing requirement's assertion payload,
confirming assertion 11 as the governing clause; and the work-item row.

Both mandatory preflights run directly by this reviewer against the operative
file. Target-path intersections computed against every currently-live thread.

Not run: the focused pytest suite, because this is a pre-implementation proposal
with no implementation to exercise.

No file was created, modified, or deleted in the reviewed scope. No mutating
command was run.

---

## Applicability Preflight

- packet_hash: `sha256:39bfdd70594a9148f6eb006105be417d01332a74395a6480e17ee584fde34dd2`
- candidate_evidence_hash: `sha256:59838751ab85ee823bfccb8589920e453b7c5364d83b6dd66333428d842869f6`
- bridge_document_name: `gtkb-wi5714-registry-write-linearizability`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_registry_control_plane.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5714-registry-write-linearizability-001.md`
- operative_file: `bridge/gtkb-wi5714-registry-write-linearizability-001.md`
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
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

The preflight passes because every triggered specification is **cited**. It does
not and cannot assess whether each citation's verification row is substantive;
F4 is that assessment.

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5714-registry-write-linearizability`
- Operative file: `bridge\gtkb-wi5714-registry-write-linearizability-001.md`
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

---

## What Revision Requires

F1 through F5. The fix design itself needs no change:

1. Disclose a measured red baseline for the lost-update race, plus a green
   baseline for the existing suite (F1).
2. Declare how the concurrency test achieves deterministic interleaving, and name
   which test is the regression gate (F2).
3. Assert the new exception subclass rather than the pre-existing base class, and
   say that the base behavior pre-exists (F3).
4. Re-map the governing requirement's row to assertion 11 with the concurrency
   test as evidence, cover the coherent-committed-reads limb, and replace the
   seven filler rows (F4).
5. Narrow the stated outcome to `amend_artifact`, record the residual unbound
   paths, and file a follow-on work item (F5).

Fold in N1's exception taxonomy, N2's rejected-alternatives comparison, N3's two
missing deliberations, N4's link pruning, N5's commit type, and N6's retry-bound
derivation while revising.

Everything else carries forward unchanged: the problem statement, the choice of
generation-binding as the mechanism, the existing compare-and-swap placement, the
authorization scope, and the target-path declaration.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
