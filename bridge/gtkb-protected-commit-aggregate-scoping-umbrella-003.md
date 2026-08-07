REVISED
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
Version: 003
Author: Prime Builder (claude, harness B)
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-protected-commit-aggregate-scoping-umbrella-002.md
Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5938

# REVISED - Protected-Commit Checker: Scope The Index-Snapshot Branch To One Bridge Thread

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_protected_commit_checker_invocation_scoping.py"]

## Why This Is REVISED After A GO

**The `-001` root cause was wrong, and the `-002` GO rested on it.** I am withdrawing that
analysis rather than implementing against it. No implementation was performed under the GO; the
implementation-start packet was created, then this revision was filed instead.

`-001` claimed the cost was `_verify_snapshot_ledger` re-hashing the whole 15,573-file bridge
corpus from 12+ call sites, and that `_load_verified_evidence` resolved evidence once per
protected path. Direct measurement refuted both claims:

| `-001` claim | Measured reality |
| --- | --- |
| `_load_verified_evidence` is a dominant cost (WI-5938: "110-677s") | **2.97s** for the exact 4 protected `.claude/rules/*.md` paths that hung the checker, 628 packets scanned |
| Per-path/per-packet resolution is unbounded | The WI-5659 prefilter reduces **628 packets to 11 survivors** |
| Each snapshot spans the whole corpus | The per-packet call site passes `precomputed_head_entries=head_entries_by_bridge.get(bridge_id, ())` (L1689), so its snapshot holds **one thread's files** |
| WI-5658 work still outstanding | Already implemented: `_committed_bridge_entries_by_id` (L1614-1631) enumerates committed bridge history once and groups by bridge id |

Memoizing a 2.97s function would have produced a measurable no-op while reporting success. That
is the failure mode this revision exists to prevent.

Method: `_load_verified_evidence` was invoked directly against `HEAD=629fead8c` with the four
protected paths, under `faulthandler.dump_traceback_later` so a stall would name its own frame.
It returned in 2.97s with 1 evidence entry and 6 diagnostic errors. No stall occurred.

## Corrected Root Cause (measured, single mechanism)

The cost is a **scoping asymmetry in `_bridge_snapshot`**. It has three ways to build a snapshot,
and exactly one of them is unfiltered:

| Branch | Site | Scope |
| --- | --- | --- |
| `precomputed_head_entries` | L1113-1116, used by the per-packet loop at L1689 | one bridge thread |
| `else` (re-enumerate) | L1117-1125, filters with `exact_re = ^bridge/<bridge_id>-\d{3}\.md$` | one bridge thread |
| **`index_snapshot`** | **L1108-1111, `_materialize_index_tree`** | **ENTIRE index tree - no bridge_id filter** |

`_materialize_index_tree` (L997-1012) calls `_materialize_entries(root, snapshot_root,
_index_entries(root, snapshot), ...)`. `_index_entries` is unfiltered, so this branch materializes
every index entry into the temp snapshot.

The caller at **L1982** takes that branch: `with _bridge_snapshot(root, bridge_id, snapshot) as
bridge_snapshot:` passes `index_snapshot` positionally and no `precomputed_head_entries`. The
guarded region that follows then re-traverses that whole-tree snapshot repeatedly:
`_verify_snapshot_ledger` at L1984, L1991, L2005, L2011, L2020, L2041, plus `_immutable_snapshot`
blocks at L1985 and L1999, each of which internally performs one more
`_verify_snapshot_ledger` + two `_set_snapshot_read_only` full-tree `chmod` passes +
`_snapshot_guard_identities` (which hashes every path again).

So the actual per-invocation cost is **one whole-index materialize, then on the order of eight
full rglob+sha256 traversals and four full chmod traversals of ~15.5k materialized files** -
consistent with the observed 123.9s and 221.4s-still-climbing.

The defect is still monotonically worsening for the same reason: `bridge/` is append-only per
`.claude/rules/bridge-essential.md`, so the unfiltered branch grows with total bridge history.

## Corrected Design (one surgical change)

Make the `index_snapshot` branch scope to the requested `bridge_id`, exactly as its two sibling
branches already do. Concretely: filter the entries handed to `_materialize_entries` with the same
`^bridge/<bridge_id>-\d{3}\.md$` predicate the `else` branch uses at L1122, so all three branches
produce a per-thread snapshot.

Consequences:

- The 8 verification traversals and 4 chmod traversals then operate on one thread's files
  (single digits), not ~15.5k. Cost becomes independent of total bridge history.
- **No gate semantics change.** The guarded region's only consumer is
  `resolve_bridge_lifecycle(snapshot_root, bridge_id)` plus `_approved_chain`, both of which read
  only that one thread's files. Entries for unrelated threads are materialized, hashed, chmod'd,
  and then never read. Removing them removes work, not checks.
- Tamper detection is preserved in full for the files that are actually consulted: the ledger for
  the scoped set is still verified at every existing call site, and drift in any consulted file
  still raises `GateError`.

This is the same remedy pattern WI-5977 states for its own gates - verify what the operation can
actually affect, and treat unrelated aggregate entries as benign - applied to the snapshot scope
rather than to a digest comparison.

**Scope reduction versus `-001`:** the memoization work described in `-001` is dropped entirely.
No memo, no cache, no invalidation logic, and therefore none of the stale-memo risk the `-002`
verdict flagged as a residual. WI-5938 remains open and is explicitly **not** claimed as fixed by
this proposal; its premise needs re-measurement in its own thread, and this proposal's evidence
section is the input for that.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement. The change makes one branch
consistent with the two beside it while preserving every gate outcome. No specification capture is
requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is a bridge artifact under `bridge/**`; append-only
  discipline observed, and the append-only invariant is why the unfiltered branch degrades.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the checker is the enforcement surface for
  this protected behavior; accept/reject outcomes must not change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - mapping below derives each test from a
  linked requirement.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - no caching is introduced; every invocation still derives
  its verdict from a fresh canonical read. This revision strengthens compliance relative to `-001`,
  which proposed memoization.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - a deterministic gate that cannot terminate pushes
  its cost onto owner-mediated sessions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - cited because the applicability preflight requires it
  for this document class; compliance is vacuous, both targets are platform paths and nothing under
  `applications/` is read, written, or depended upon.
- `.claude/rules/project-root-boundary.md` - both targets are in-root.

## Prior Deliberations

- `bridge/gtkb-protected-commit-aggregate-scoping-umbrella-001.md` (NEW) and `-002.md` (GO) - the
  superseded analysis and the verdict that rested on it. `-002`'s residual risks (memo weakening
  tamper detection; stale in-invocation memo) are both moot because memoization is dropped.
- `WI-5977` (P0, open) - the whole-aggregate-versus-target-slot pattern this revision applies;
  owned by the sibling machinery thread and still excluded from `target_paths`.
- `WI-5938` (P0, open) - premise now contradicted by measurement; deliberately NOT claimed fixed.
- `WI-5658` and `WI-5659` - the two prior optimizations of this module, already landed; the
  reason the per-packet path is fast and the reason this revision looks elsewhere.
- `bridge/gtkb-w0-skill-rename-path-repair-001..004.md` (VERIFIED, landed `629fead8c` under an
  owner-authorized `--no-verify` override) - the commit whose two failed attempts produced the CPU
  measurements. `WI-5998` records that incident.
- No Deliberation Archive record addresses protected-commit snapshot scoping; searches for
  `protected commit authorization performance bridge aggregate` and
  `WI-5977 aggregate preimage narrowing target slot` returned only unrelated verdicts.

## Test Plan And Spec-To-Test Mapping

New module `platform_tests/scripts/test_protected_commit_checker_invocation_scoping.py`.

| Requirement | Test | Assertion |
| --- | --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - outcomes unchanged | `test_authorization_outcomes_unchanged_by_snapshot_scoping` | For a fixture matrix of authorized and unauthorized staged path sets, exit code and emitted reasons are identical before and after the scoping change. |
| Corrected root cause - index-snapshot branch is scoped | `test_index_snapshot_branch_materializes_only_target_thread` | Building a snapshot via the `index_snapshot` branch for `bridge_id` X materializes only `bridge/X-NNN.md` entries; an unrelated thread's file present in the index is absent from the snapshot ledger. |
| All three branches agree on scope | `test_all_three_snapshot_branches_scope_identically` | For the same `bridge_id`, the ledgers produced by the `precomputed_head_entries`, `else`, and `index_snapshot` branches contain the same relative path set. |
| Tamper detection preserved | `test_ledger_drift_still_detected_for_scoped_set` | Mutating a file inside the guarded window still raises `GateError` with the file-set-drift or bytes-drift message. |
| Lifecycle resolution unaffected | `test_resolve_bridge_lifecycle_unaffected_by_scoping` | `resolve_bridge_lifecycle` returns the same resolution against a scoped snapshot as against an unscoped one for the same thread. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_no_cross_invocation_state_introduced` | No module-level cache or memo is added; a second invocation re-derives from disk. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | whole module | Executed and reported in the implementation report. |

Regression lanes to execute and report: `platform_tests/scripts/test_check_protected_commit_authorization.py`,
the new module, and `ruff check` plus `ruff format --check` on both changed files. The
implementation report will also record a wall-clock measurement of a protected-path commit before
and after, since acceptance criterion 1 is a timing claim.

## Acceptance Criteria

1. A protected-path commit comparable to the rename verified set (42 paths, 4 protected) completes
   within a bounded, documented time budget on the current 15,573-file corpus, with before/after
   wall-clock recorded in the implementation report.
2. Authorization outcomes are identical to pre-change behavior across the fixture matrix.
3. All three `_bridge_snapshot` branches scope to the requested `bridge_id`.
4. Ledger drift inside the guarded window is still detected.
5. No cache, memo, or cross-invocation state is introduced.
6. `platform_tests/scripts/test_check_protected_commit_authorization.py` passes unchanged.
7. `ruff check` and `ruff format --check` pass on both changed files.
8. No file owned by `bridge/gtkb-w0p-finalization-machinery-repair` is modified, and WI-5938 is not
   claimed as fixed.
9. No other test module regresses.

## Risk And Rollback

Primary risk is that some consumer inside the guarded region at L1982-2041 reads a bridge file
belonging to a thread other than `bridge_id`, in which case scoping would remove a file it needs.
Criterion 5 of the test plan pins lifecycle-resolution equivalence, and criterion 2 pins outcome
equivalence, which together would surface such a dependency as a test failure rather than as a
silent authorization change. The reviewer is specifically asked to check this assumption, since it
is the load-bearing one.

Secondary risk is that the observed timing improvement is smaller than predicted, i.e. that a
third mechanism also contributes. Criterion 1 requires a measured before/after rather than an
assumed one, so a shortfall is reported rather than hidden. Two prior hypotheses in this thread
were already refuted by measurement; the criterion exists because of that history.

Rollback is a single-file revert of `scripts/check_protected_commit_authorization.py`; the test
module is additive. No state migration, no config change, no gate registration change.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-07, session `7d9535ba-4d9e-4b4d-aad3-420153139b97`** - owner selected
  "Draft one umbrella proposal for the family", which authorized this thread, and additionally
  authorized elevating WI-5938 to P0 (applied at WI-5938 version 2).
- **AskUserQuestion, 2026-08-07, same session** - owner authorized the `--no-verify` override plus
  after-action record for commit `629fead8c`, the incident that produced the CPU measurements.
- This revision narrows scope relative to the owner-approved umbrella framing: it fixes one
  measured mechanism instead of two hypothesized ones. No new owner decision is required to review
  it. Implementation remains gated on a fresh Loyal Opposition `GO` and a re-created
  implementation-start authorization packet.

## Recommended Commit Type

- Recommended commit type: `fix:` - repairs a gate that cannot complete, no new capability surface.

---

When you are finished working, close your session envelope by invoking ::wrap.
