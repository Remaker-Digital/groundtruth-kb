NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 7d9535ba-4d9e-4b4d-aad3-420153139b97
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-protected-commit-aggregate-scoping-umbrella
Version: 001
Author: Prime Builder (claude, harness B)
Date: 2026-08-07 UTC
Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5938

# Implementation Proposal - Protected-Commit Checker Invocation Scoping (WI-5938 + WI-5998)

## Summary

The protected-commit authorization checker (`scripts/check_protected_commit_authorization.py`)
does not terminate on a protected-path commit. Two independent super-linear mechanisms in that
one module each re-traverse the whole 15,573-file / 151.3 MB bridge corpus many times per
invocation. This proposal fixes both by memoizing work that is already invariant within a
single invocation. It changes no gate semantics: every check that passes today still passes,
and every check that fails today still fails.

This is currently the top blocker on custodial finalization. It blocks the drain of 349
untracked bridge chain files and the filing of three after-action audit records.

## Scope And What Is Deliberately Excluded

In scope, both in `scripts/check_protected_commit_authorization.py`:

- **WI-5938** (P0) - memoize per-path verified-evidence bridge resolution
  (`_load_verified_evidence`), so each bridge thread is resolved once per invocation rather
  than once per matching packet/protected path. The work item records 110-677s per-path
  evaluation collapsing toward sub-second.
- **WI-5998** (P0) - eliminate repeated whole-snapshot ledger re-verification.
  `_verify_snapshot_ledger` has 12+ call sites and each one rglobs the materialized audit
  snapshot and sha256-hashes every non-exempt file.

**Explicitly EXCLUDED: WI-5977.** WI-5977 (narrowing the four whole-aggregate preimage digest
gates in `compensate_bridge_publication` to the target slot) is already inside the GO'd scope of
`bridge/gtkb-w0p-finalization-machinery-repair`, whose declared target paths include
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` and
`platform_tests/scripts/test_bridge_publication_preimage_scoping.py`. Including it here would
duplicate an approved thread and collide on its reserved paths. WI-5977 is cited below as
design precedent only; no file it owns is touched by this proposal.

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_protected_commit_checker_invocation_scoping.py"]

**Authorization carriage, stated plainly for the reviewer.** The cited work item is `WI-5938`,
which is a member of `PROJECT-GTKB-TIMER-GOVERNANCE` and is therefore covered by the active
whole-project authorization above. `WI-5998` was created in this session (2026-08-07) and is not
yet a member of any project, so it carries no authorization of its own; it is included here as
the second mechanism of the same defect in the same file, under the WI-5938 authorization. If the
reviewer prefers `WI-5998` to be projected and separately enumerated before implementation, that
is a reasonable `NO-GO` and the remedy is a one-line project attachment rather than a redesign.

## Evidence

Measured in session `7d9535ba-4d9e-4b4d-aad3-420153139b97` on 2026-08-07 while attempting the
owner-approved custodial finalization of `bridge/gtkb-w0-skill-rename-path-repair-004.md`
(42 declared paths, 4 of them protected `.claude/rules/*.md`):

| Observation | Value |
| --- | --- |
| Attempt 1 CPU before abandonment | 123.9s, did not return |
| Attempt 2 CPU before abandonment | 221.4s and still climbing, did not return |
| `bridge/*.md` file count | 15,573 |
| `bridge/*.md` total bytes | 158,699,247 (151.3 MB) |
| Tracked in `bridge/` at HEAD | 15,552 |
| `_verify_snapshot_ledger` call sites | 12+ (L1236, 1245, 1249, 1336, 1344, 1372, 1984, 1991, 2005, 2011, 2020, 2041) |
| `_set_snapshot_read_only` full-tree passes | 4+ (L1237, 1248, 1350, 1364), each rglob + chmod every entry |

Per-invocation cost is therefore on the order of 200,000 file open+read+hash operations and
about 2 GB of SHA-256, which matches the observed CPU. The preceding four pre-commit gates all
completed and printed PASS on the same staged set (secret scan 36 files / 0 findings; inventory
drift PASS with 42 changed and 4 protected; narrative-artifact evidence PASS 4 cleared; ruff
format PASS 16 files), so the non-termination is isolated to this module.

**The defect is monotonically worsening.** `bridge/` is append-only by protocol invariant
(`.claude/rules/bridge-essential.md`: "Never delete a bridge file; it forms the audit trail"),
so every thread ever filed permanently increases the cost of every future protected commit.
Today it blocks a 42-path commit; on the same arithmetic it will eventually block small ones.

Collateral observed twice: when the caller times out, the killed `git` leaves the pre-commit
`bash` subtree and this checker running as orphaned processes plus a 2.64 MB stale
`.git/index.lock`, each requiring manual cleanup.

## Design

Both fixes are invocation-scoped memoization of values that are already invariant for the
duration of one checker run. Neither weakens a gate.

**Mechanism A (WI-5938) - per-path evidence resolution.**
Add an invocation-scoped cache keyed by `bridge_id` in `_load_verified_evidence`. A bridge
thread's verified evidence cannot change during a single pre-commit invocation, so resolving it
once per thread instead of once per matching packet/protected path is semantics-preserving.

**Mechanism B (WI-5998) - whole-snapshot ledger re-verification.**
The audit snapshot is materialized once and is held read-only for the guarded window. Within
that window the ledger verification result is invariant unless the tree actually changes.
Replace the unconditional full rglob-and-rehash on each of the 12+ call sites with an
invocation-scoped verification memo, invalidated only at the points where the snapshot is
legitimately mutated (`_set_snapshot_read_only` transitions and the materialize boundary).
The tamper-detection intent is preserved: the first verification after any mutation boundary
still performs the full hash comparison, so drift introduced during the guarded window is still
caught. What is removed is re-hashing an unchanged tree 12 times.

This mirrors the remedy pattern WI-5977 states for its own gates: verify what the operation can
actually affect, and retain whole-aggregate digests as audit observations rather than as
repeated gates.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed. The governing
requirements below already mandate the behavior this proposal preserves; the change is a
performance repair that keeps those invariants intact. No specification capture is requested by
this proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority and the append-only invariant
  that makes this cost grow monotonically; the reason the fix must be memoization rather than
  corpus pruning.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below derives
  each test from a linked requirement.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - memoization is invocation-scoped only; no result is
  cached across invocations, so every run still derives its verdict from a fresh canonical read.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the checker is the enforcement surface for
  this protected behavior; the proposal must not weaken its accept/reject decisions.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - a deterministic gate that cannot terminate
  pushes its cost back onto owner-mediated sessions, which this repair reverses.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - cited because the applicability preflight requires
  it for this document class. Compliance is by construction and vacuous here: both target paths
  are platform paths (`scripts/` and `platform_tests/`), no file under `applications/` is read,
  written, or depended upon, and no application-placement decision is made or implied. Recorded
  explicitly so the citation is not mistaken for an unexamined checkbox.
- `.claude/rules/project-root-boundary.md` - both target paths are in-root under `E:\GT-KB`; no
  out-of-root path becomes a live dependency.

## Prior Deliberations

A Deliberation Archive search was run for this topic
(`protected commit checker whole aggregate preimage scoping performance`, and
`protected commit authorization performance bridge aggregate`, and
`WI-5977 aggregate preimage narrowing target slot`). No prior deliberation addresses
protected-commit checker aggregate scoping; the nearest hits were unrelated Loyal Opposition
verdicts. The load-bearing prior art is in work items and bridge threads rather than the archive:

- `WI-5977` (P0, open) - records the whole-aggregate-versus-target-slot analysis for the four
  `compensate_bridge_publication` preimage gates, including the safety argument for narrowing.
  This proposal adopts its reasoning pattern and excludes its files.
- `WI-5938` (P0 as of 2026-08-07, open) - the per-path memoization item, with the 110-677s
  measurement.
- `bridge/gtkb-w0-skill-rename-path-repair-001..004.md` - the finalization whose two failed
  commit attempts produced the CPU measurements above; landed at commit `629fead8c` only via an
  owner-authorized `--no-verify` override.
- `bridge/gtkb-w0p-finalization-machinery-repair-001..002.md` (GO) - the sibling thread that
  owns WI-5977 and the `write_verdict` re-entry repair.
- `WI-5658` - the existing per-git-subprocess 120s bound in this module, which establishes that
  bounding cost in this checker is accepted practice.

## Test Plan And Spec-To-Test Mapping

New module `platform_tests/scripts/test_protected_commit_checker_invocation_scoping.py`.

| Requirement | Test | Assertion |
| --- | --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - accept/reject decisions unchanged | `test_authorization_outcomes_unchanged_by_memoization` | For a fixture set of authorized and unauthorized staged path sets, the exit code and emitted reasons are identical with memoization enabled and disabled. |
| `WI-5938` - per-thread resolution happens once | `test_verified_evidence_resolved_once_per_bridge_id` | With N protected paths resolving to one bridge id, `_load_verified_evidence` performs exactly 1 underlying resolution, not N. |
| `WI-5998` - snapshot ledger verified once per mutation window | `test_snapshot_ledger_verified_once_per_window` | Across an invocation with no snapshot mutation, the full hash pass executes once; the count scales with mutation boundaries, not with call sites. |
| `WI-5998` - tamper detection preserved | `test_ledger_drift_still_detected_after_memoization` | Mutating a file inside the guarded window still raises `GateError` with the file-set-drift or bytes-drift message. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | whole module | The module is executed and reported in the implementation report. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - no cross-invocation caching | `test_memo_does_not_persist_across_invocations` | A second invocation in the same process re-derives from disk; no memo survives the invocation boundary. |

Regression lanes to execute and report: `platform_tests/scripts/test_check_protected_commit_authorization.py`
(the existing suite for this module) plus the new module, and `ruff check` and
`ruff format --check` on both changed files.

## Acceptance Criteria

1. A protected-path commit of the size of the rename verified set (42 paths, 4 protected)
   completes within a bounded, documented time budget on the current 15,573-file corpus.
2. Authorization outcomes are byte-identical to pre-change behavior for the fixture matrix in
   `test_authorization_outcomes_unchanged_by_memoization`.
3. Ledger drift introduced during the guarded window is still detected.
4. No memoized value survives an invocation boundary.
5. `platform_tests/scripts/test_check_protected_commit_authorization.py` passes unchanged.
6. `ruff check` and `ruff format --check` pass on both changed files.
7. No file owned by `bridge/gtkb-w0p-finalization-machinery-repair` is modified.
8. No other test module regresses.

## Risk And Rollback

Primary risk is weakening tamper detection while chasing throughput. Mitigated by criteria 2
and 3, which pin outcome equivalence and drift detection independently of performance.

Secondary risk is a stale memo within a single invocation producing a wrong accept. Mitigated by
invalidating at every snapshot mutation boundary and by criterion 4.

Rollback is a single-file revert of `scripts/check_protected_commit_authorization.py`; the new
test module is additive and can remain. There is no state migration, no config change, and no
gate registration change, so rollback restores exact prior behavior.

Concurrency note: this proposal touches one source file that no active work-intent claim
reserves. The sibling machinery thread's reserved paths are excluded by criterion 7.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-07, session `7d9535ba-4d9e-4b4d-aad3-420153139b97`** - asked how to
  proceed given machinery was blocked by an active worker's path reservation and the checker
  family blocks the W0.2 drain. Owner selected **"Draft one umbrella proposal for the family"**,
  which authorizes this proposal and its umbrella framing, and additionally authorized elevating
  WI-5938 to P0. WI-5938 was elevated to P0 at version 2 with that AUQ cited as the change
  reason.
- **AskUserQuestion, 2026-08-07, same session** - owner authorized the `--no-verify` override plus
  after-action record for commit `629fead8c`. That decision is the source of the CPU measurements
  in the Evidence section and of `WI-5998`.
- No further owner decision is required to review this proposal. Implementation remains gated on
  Loyal Opposition `GO` plus an implementation-start authorization packet.

## Recommended Commit Type

- Recommended commit type: `fix:` - repairs a gate that cannot complete, with no new capability
  surface. The added test module is covered by the same change.

---

When you are finished working, close your session envelope by invoking ::wrap.
