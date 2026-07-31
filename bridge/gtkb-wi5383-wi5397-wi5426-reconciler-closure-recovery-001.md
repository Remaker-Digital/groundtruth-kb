NEW
::init gtkb lo
::open build

# WI-5383/WI-5397/WI-5426 Reconciler Closure Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5383-wi5397-wi5426-reconciler-closure-recovery
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined role; build activity envelope

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5383-WI5397-WI5426-CLOSURE-RECOVERY-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5383
Related Work Items: WI-5397, WI-5426

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Finish the shared two-file VERIFIED-backlog reconciliation transaction without
discarding or silently absorbing any current work. The transaction combines
three inseparable requirements already present on the same source/test surface:

1. `WI-5383` requires typed verdict-purpose classification and exact terminal
   commit coverage before an implementation work item can close.
2. `WI-5397` requires one bounded read-only Git provenance inventory per
   reconciliation run instead of process fan-out proportional to VERIFIED
   thread count.
3. `WI-5426` requires by-reference waiver detection to accept only an explicit,
   affirmative, owner-backed declaration and to reject negated, incidental, or
   malformed prose.

The current working files already contain the WI-5383 behavior and a WI-5397
batching candidate, but they remain uncommitted shared work and the waiver
detector still accepts broad `Owner Decisions / Input` keyword combinations.
The existing WI-5383 primary chain has a tracked proposal at version 001 and
untracked versions 002 through 008. A bare `VERIFIED` token in that uncommitted
chain is not terminal authority. This proposal creates a canonical-only repair
path that can independently verify and atomically finalize the complete
attributable transaction.

## Current-State Evidence

- Current source blob: `43acf0ad1dc5c3eaf6d1bb3b3db40c2e48b10971`.
- Current test blob: `857e443f1b588de33e764f1b438a05356f1b0085`.
- HEAD source blob: `14116a41bb9d89db97dfd52593c8db88e07345ab`.
- HEAD test blob: `248fa47eb4bc6d779b449ac68b878eb0728b0af7`.
- Current diff size: source `443` additions and `9` deletions; test `296`
  additions and no deletions.
- Ruff check passes, Ruff format reports both files already formatted, and
  both files compile.
- The current test module contains the WI-5397 bounded-provenance regression,
  while the source waiver matcher still includes `Owner Decisions / Input` and
  accepts keyword presence instead of a dedicated affirmative declaration.
- `WI-5426` is recorded `resolved/resolved` even though its own status detail
  says the required negated/incidental waiver regression is not implemented.
  This proposal treats that row as false closure evidence, not as completion.

These hashes describe the review baseline only. They do not authorize edits.
Every implementation gate must re-read and reclassify the current bytes.

## Pre-Filing Gate Evidence

- Candidate applicability preflight:
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, `blocking_errors: []`.
- Candidate mandatory clause preflight: 5 clauses evaluated, 4
  `must_apply`, zero evidence gaps, zero blocking gaps, exit 0.
- Phantom-spec sweep: all 19 cited specification IDs exist in live MemBase;
  14 are `specified` and 5 are `verified`.
- `target_paths` parses as an inline JSON list containing exactly the two
  authorized in-root files.

## Hard Sequencing And Authority Gates

- `WI-5501` must first reach independently VERIFIED, focused-finalized terminal
  state. This repair must not optimize or finalize against unstable concurrent
  real-index semantics.
- Independent Loyal Opposition must issue `GO` on this exact proposal.
- Prime Builder must then acquire the exact work-intent claim, schema-v3
  implementation-start packet, and operation-time authorization for both target
  paths.
- Both target paths must be rehashed and ownership-classified at operation time.
  Any unexplained drift, new peer owner, same-path collision, or predecessor
  regression blocks implementation.
- No existing bridge version is deleted or rewritten. Historical artifacts
  outside the explicit canonical evidence set are not used as authority.
- No live reconciler `--apply`, direct MemBase write, dispatcher or TAFE
  configuration/runtime mutation, harness contact, worker/lease/routing
  mutation, credential action, destructive cleanup, push, deployment, or
  release is in scope.

## Proposed Implementation

### WI-5383: strict implementation closure

- Preserve deterministic reasons `no_action_verified`,
  `malformed_target_metadata`,
  `missing_implementation_commit_coverage`, and `genuinely_closable`.
- Require the terminal verdict and every approved non-bridge target to be
  covered by the terminal verdict's containing commit.
- Preserve bridge-only legacy behavior only where no implementation target set
  exists, and preserve a by-reference exception only through the explicit
  contract below.
- Keep umbrella and repair-overbroad classification fail-closed when any child
  lacks valid closure evidence.

### WI-5397: bounded read-only provenance

- Build one request-scoped Git status, tracked-path, and commit-path inventory
  per reconciliation run and reuse it across thread classifications.
- Keep targeted and full-history classification results identical to uncached
  semantics.
- Do not persist a cache or reuse provenance across runs, implementation-start
  checks, or operation-time authorization boundaries.
- Keep Git subprocesses independent of the number of VERIFIED threads.

### WI-5426: affirmative waiver contract

- Recognize a by-reference exception only beneath a dedicated
  `## By-Reference Finalization Waiver` heading.
- Require one anchored affirmative declaration in the form
  `Owner-approved by-reference waiver: DELIB-<id>.`
- Reject `Owner Decisions / Input` prose, proposal-side references, unrelated
  sibling waivers, negated statements, missing DELIB references, duplicate
  declarations, and malformed declarations.
- Preserve the existing positive fixture for a valid dedicated owner waiver.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5383, WI-5397, WI-5426, and PAUTH-DISPATCHER-BLACK-BOX-WI5383-WI5397-WI5426-CLOSURE-RECOVERY-20260718",
  "canonical_authority": "The approved proposal target metadata, complete numbered bridge history, explicit DELIB-backed waiver declaration when present, current request-scoped Git evidence, and the terminal containing commit",
  "primary_route": "Classify verdict purpose and approved targets, build one request-scoped Git provenance inventory, validate any explicit waiver, then prove terminal commit coverage before backlog closure",
  "before_behavior": "A file-only VERIFIED token can imply closure, Git evidence can fan out per thread, and broad or negated owner prose can activate a by-reference exception",
  "after_behavior": "Only attributable implementation evidence closes work, Git provenance is bounded per run, and only a dedicated affirmative DELIB-backed declaration activates by-reference mode",
  "self_descriptive_naming": "verified_thread_closure_evidence, build_git_provenance_index, no_action_verified, malformed_target_metadata, missing_implementation_commit_coverage, genuinely_closable, and by_reference_waiver expose each decision",
  "obsolete_guidance_disposition": "Token-only closure, per-thread Git process fan-out, and broad keyword waiver matching are rejected; no historical bridge version is rewritten",
  "history_preservation": "All existing proposal, verdict, report, work-item, test, and commit records remain intact and queryable; the recovery chain adds current disposition evidence",
  "baseline": {
    "source_blob": "43acf0ad1dc5c3eaf6d1bb3b3db40c2e48b10971",
    "test_blob": "857e443f1b588de33e764f1b438a05356f1b0085",
    "source_diff": "443 additions and 9 deletions",
    "test_diff": "296 additions and 0 deletions",
    "known_gap": "The waiver detector still accepts broad Owner Decisions / Input keyword combinations"
  },
  "expected_result": {
    "closure": "Every incomplete evidence class remains open with a deterministic reason",
    "performance": "Git status, tracked-path, and history inventories are bounded independently of VERIFIED-thread count",
    "waiver": "Only one dedicated anchored affirmative DELIB-backed declaration activates by-reference mode",
    "finalization": "Independent Loyal Opposition creates one focused commit after WI-5501 terminalizes"
  },
  "rollback": {
    "instructions": "Use a separately governed focused revert of only the final source and test images",
    "preserve": "Keep bridge and MemBase history append-only and retain all unrelated worktree and index state",
    "verification": "Rerun the complete focused module and exact closure, provenance, and waiver fixtures"
  },
  "hard_invariants": [
    "No live reconciler apply or direct MemBase mutation",
    "No dispatcher or TAFE configuration, runtime, claim, lease, eligibility, or routing mutation",
    "No direct harness contact or worker impairment",
    "No Prime-authored GO or VERIFIED",
    "No unrelated dirty or staged path capture",
    "No persistent provenance cache across runs"
  ],
  "fail_closed_conditions": [
    "WI-5501 is not terminal and focused-finalized",
    "Missing or stale independent GO, work-intent claim, implementation-start packet, or operation-time authority",
    "Unexplained target-byte drift or same-path peer ownership",
    "Malformed target metadata or waiver declaration",
    "Git provenance command failure or inconsistent classification",
    "Test, lint, format, compile, diff, applicability, clause, or finalizer isolation failure"
  ],
  "essential_context_preservation": "The result retains verdict purpose, proposal targets, work-item lineage, waiver provenance, Git command status, containing commit, changed and missing paths, closure reason, predecessor state, and exact finalization include set"
}
```

## Terminal Finalization Contract

Independent Loyal Opposition must verify the final two-file implementation
against this proposal and use the canonical atomic VERIFIED finalizer. The
focused commit must contain:

- `scripts/bridge_verified_backlog_reconciler.py`;
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`;
- the currently untracked primary WI-5383 chain versions 002 through 008,
  after byte-for-byte revalidation against the reviewed chain;
- the complete status-bearing chain for this recovery thread, including its
  implementation report and new independent `VERIFIED` verdict.

The already tracked primary proposal version 001 remains in its existing
containing commit. Unrelated staged paths and unrelated dirty hunks must remain
untouched. If the atomic finalizer cannot preserve that isolation, it must
remove its candidate verdict and fail closed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct append-only bridge
  transitions and independent GO/VERIFIED.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds this bounded repair to
  the owner-backed project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents the PAUTH from
  replacing GO, claim, start, or verification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires
  per-target authority at every protected mutation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - constrains the allowed mutation
  classes and forbidden operations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires exact PAUTH,
  project, work-item, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all
  relevant governing specifications and derived tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed
  requirement-to-test evidence before VERIFIED.
- `DCL-VERIFIED-BRIDGE-HISTORY-001` - makes a status token insufficient without
  complete, attributable implementation history.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - keeps verification of an operational
  NO-ACTION distinct from implementation completion.
- `SPEC-DSI-COMMIT-GATE-001` - keeps terminal commit evidence independently
  blocking.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires unambiguous,
  machine-evaluable target and waiver evidence.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact isolation from foreign dirty and
  staged content.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires before/after,
  invariant, failure, and rollback coverage.
- `GOV-STANDING-BACKLOG-001` - governs truthful WI-5383, WI-5397, and WI-5426
  lifecycle evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps requirements, defects, tests,
  reports, and terminal evidence durable and distinct.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links the shared implementation to
  its work items, tests, bridge chain, and commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserves each proposal, report,
  verification, and closure transition as a separate lifecycle event.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and
  synthetic Git fixtures inside the GT-KB root.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes
  bounded PAUTH carriers and governed proposals for newly discovered in-scope
  bridge/TAFE/harness defects while preserving every downstream gate.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - established
  the normal VERIFIED-to-backlog reconciliation path; this repair supplies the
  missing evidence boundary before retirement.
- `bridge/gtkb-wi5383-verified-closure-evidence-001.md` - original approved
  implementation proposal whose strict closure requirements are preserved.
- `bridge/gtkb-wi5383-verified-closure-evidence-007.md` - current
  implementation report describing the uncommitted two-file candidate.
- `bridge/gtkb-wi5501-concurrent-verified-finalization-safety-001.md` - required
  predecessor for stable concurrent finalization semantics.

This proposal does not rely on any scratchpad, retired assessment carrier,
generated summary, or artifact outside `E:\GT-KB`.

## Owner Decisions / Input

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner decision
that permits this bounded PAUTH carrier and proposal. It explicitly does not
authorize protected edits or waive independent GO, exact claim/start,
operation-time authorization, testing, verification, or focused commit.

## Requirement Sufficiency

Existing requirements sufficient. The linked bridge-history, NO-ACTION,
commit-gate, evaluability, worktree-hygiene, non-impairment, project
authorization, and artifact-lifecycle specifications define the required
behavior without a new or revised formal specification.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Strict closure; `DCL-VERIFIED-BRIDGE-HISTORY-001`; `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Focused fixtures for VERIFIED-on-NO-ACTION, malformed metadata, untracked verdict, omitted target, focused commit, bridge-only legacy, and umbrella child failure | Only complete implementation evidence is closable; every invalid case returns its deterministic reason. |
| Bounded provenance; WI-5397 | Instrument `_run_git` while classifying many VERIFIED threads | One status, one tracked-path, and one history inventory per run; no per-thread Git fan-out; classifications match the unbatched oracle. |
| Affirmative waiver; WI-5426 | Add valid, negated, incidental, proposal-side, unrelated, duplicate, missing-DELIB, and malformed waiver fixtures | Only the dedicated anchored affirmative owner declaration activates by-reference mode. |
| Complete focused behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short` | Entire module passes with no timeout or live MemBase mutation. |
| Source/test quality | `groundtruth-kb/.venv/Scripts/ruff.exe check ...`; matching `ruff format --check`; `python -m py_compile ...`; `git diff --check -- ...` | All commands exit 0 on the exact two targets. |
| Canonical proposal authority | Candidate and live applicability plus mandatory clause preflights | No missing required/advisory specifications and zero blocking clause gaps. |
| Worktree isolation and finalization | Rehearse exact include set in a disposable index, inspect staged paths, then use the canonical LO finalizer | Only the two reviewed targets, primary versions 002-008, recovery chain, report, and verdict enter the focused commit; foreign staged/dirt state is preserved. |
| Non-impairment | Confirm tests use pytest-owned temporary repositories and do not invoke live `--apply` | No live MemBase, bridge history, dispatcher, TAFE, harness, worker, lease, routing, credential, push, deployment, or release mutation. |

## Acceptance Criteria

- All four WI-5383 closure reasons remain deterministic and covered.
- Git provenance process count is bounded independently of VERIFIED-thread
  population while results remain identical.
- Negated, incidental, unrelated, duplicate, and malformed waiver prose cannot
  bypass commit coverage; the dedicated affirmative DELIB-backed declaration
  remains valid.
- The complete focused test module, Ruff check, Ruff format check, compilation,
  diff check, applicability preflight, and clause preflight pass.
- WI-5501 is terminal/focused-finalized before any protected edit or terminal
  finalization under this proposal.
- Independent LO creates the focused terminal commit with no unrelated staged
  or dirty content and no Prime-authored VERIFIED verdict.
- Post-finalization MemBase reconciliation records WI-5383, WI-5397, and
  WI-5426 truthfully from committed canonical evidence.

## Risk / Rollback

The principal risk is false closure of unfinished work. Secondary risks are a
false skip of legitimate work, an overbroad waiver, stale request-scoped Git
provenance, and contamination from concurrent index writers. The implementation
fails closed on ambiguous metadata, unexplained byte drift, stale authority,
same-path collision, provenance command failure, or finalizer isolation
failure.

Rollback is a separately governed focused revert of only the final two source
and test images. Bridge and MemBase history remain append-only. No rollback may
restore token-only closure, broad keyword waiver matching, or per-thread Git
process fan-out without a new reviewed proposal.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5383-wi5397-wi5426-reconciler-closure-recovery`; no
prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered
file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the transaction repairs false implementation closure and waiver
activation while bounding the required read-only provenance work.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
