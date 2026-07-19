NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user

# Defect-Fix Proposal - Repair WI-5396 terminal finalization with canonical in-root evidence

bridge_kind: prime_proposal
Document: gtkb-wi5563-session-envelope-canonical-finalization-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5563

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_fab13_retention_policy.py"]

## Claim

Adopt, independently reverify, and focused-finalize the exact current WI-5396
implementation candidate without changing its semantic bytes. The candidate
prevents a nested in-root pytest fixture from causing session-envelope Git
attestation to scan the ancestor GT-KB repository, bounds both Git probes, and
fails soft without weakening Git evidence for an exact project root.

## Defect / Reproduction

The committed baseline does not contain WI-5396's exact-root and bounded-probe
repair. The authoritative worktree contains two uncommitted, whole-file
candidate diffs with canonical MemBase ownership:

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
  SHA-256 `B427D4AF8E744F5D449411649A28C7C32E9A56D10C570FD19DC0B7A06307C26F`
- `platform_tests/scripts/test_fab13_retention_policy.py`
  SHA-256 `FBB7416590323EF32FF19C00273C667D8EE2A8841D5FC94ABC3FFFB380C7F72E`

The source candidate first resolves `git rev-parse --show-toplevel`, requires
that normalized top level to equal the supplied project root, and only then
runs `git status --short`. Both subprocesses have a five-second bound and
return explicit unavailable reasons on timeout, execution failure, or
top-level mismatch. An exact root still returns complete dirty evidence,
bounded only in the existing display summary.

Fresh current-byte verification produced:

- Four WI-5396 Git-attestation regressions: `4 passed`.
- Complete FAB-13 module: `7 passed, 1 failed`. The sole failure is
  `test_dispatch_runs_prune_preserves_live_pid_artifacts`, canonically owned by
  WI-5404 and outside this proposal. This proposal must not absorb or repair
  that fixture.
- Ruff check: passed.
- Ruff format check: both files already formatted.
- Python compilation: passed.

## In-Root Placement Evidence

Both target paths and every governed artifact used by this transaction are
inside the mandatory `E:\GT-KB` project root. No external, retired,
harness-local, or otherwise noncanonical artifact is evidence for this
proposal.

## Specification Links

- `DCL-VERIFIED-BRIDGE-HISTORY-001` - requires a coherent canonical review and
  finalization history rather than treating invalid terminal metadata as
  implementation authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before the
  hash-bound adoption transaction and independent VERIFIED before finalization.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact ownership and scoped retirement
  of the two dirty implementation paths without absorbing foreign work.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - governs the session-envelope
  attestation behavior being preserved and reverified.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the exact-root,
  timeout, bounded-output, and nonimpairment behaviors to be exercised before
  VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds this
  implementation proposal to its governing contracts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to
  WI-5563, its active project, and the active Tree Stabilization PAUTH.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires all live GT-KB source,
  tests, evidence, and governed workflow artifacts to stay inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the implementation,
  tests, ownership records, review, and finalization evidence to remain one
  traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the accepted candidate to
  move through explicit proposal, implementation-report, VERIFIED, and
  finalized states without treating stale terminal metadata as completion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the durable WI-5396 and
  WI-5563 records to remain the canonical carriers for this defect and repair.

## Prior Deliberations

- `DELIB-202666274` - owner-approved Tree Stabilization project authority and
  exact-ownership discipline.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - canonical artifacts
  may not depend on noncanonical evidence.
- MemBase `WI-5396` - owns the exact-root session-envelope implementation
  behavior.
- MemBase `WI-5563` - owns canonical re-review and focused finalization of the
  two hash-bound candidate files.
- MemBase `WI-5404` - separately owns the unrelated live-PID fixture failure
  in the shared test module.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` is active and
  authorizes source, test, bridge, metadata, and governance-evidence work for
  Tree Stabilization while retaining separate Git-commit authority and every
  review/start gate.
- The owner requires canonical-only evidence and exact mechanical
  finalization. This proposal does not infer authority to stage, commit, push,
  deploy, release, mutate dispatcher/TAFE/harness state, or alter credentials.

## Requirement Sufficiency

Existing requirements sufficient.

Requirement sufficiency is complete for this bounded repair. No known
requirement gaps remain. The exact candidate hashes, functional behavior,
verification commands, unrelated shared-file failure, exclusions, and
finalization boundary are explicit.

## Proposed Scope

### IP-1 - Hash-bound candidate adoption

After independent GO, acquire the exact WI-5563 work-intent claim and
schema-v3 implementation-start packet. Recompute both SHA-256 values and fail
closed on any drift. Adopt the exact current candidate bytes without editing
either target.

### IP-2 - Canonical reverification and implementation report

Run the complete verification plan from the governed worktree. File a
canonical implementation report that records exact command results, both
target hashes, the WI-5404 exclusion, and the absence of semantic edits.

### IP-3 - Independent verification and focused finalization

Require an independent Loyal Opposition verdict against the canonical report
and exact current bytes. A VERIFIED finalizer may include only the two declared
implementation targets and the complete canonical bridge history resolved by
the governed finalizer. Git commit remains separately gated by the exact
finalizer authority; GO alone does not authorize it.

This proposal is filed as the next numbered bridge file at
`bridge/gtkb-wi5563-session-envelope-canonical-finalization-repair-001.md`.
All prior numbered bridge files remain append-only and are neither deleted nor
rewritten.

## Specification-Derived Verification Plan

| Requirement | Verification command or evidence | Pass condition |
|---|---|---|
| Exact candidate identity | `Get-FileHash -Algorithm SHA256` for both target paths | Both hashes exactly match the values in this proposal before report filing and finalization |
| Exact-root containment | `python -m pytest platform_tests/scripts/test_fab13_retention_policy.py::test_session_envelope_git_status_rejects_ancestor_top_level -q --tb=short` | Pass; status is not invoked for an ancestor repository |
| Bounded complete evidence at an exact root | `python -m pytest platform_tests/scripts/test_fab13_retention_policy.py::test_session_envelope_git_status_is_bounded -q --tb=short` | Pass; exact root is accepted and complete line count is retained |
| Top-level probe timeout | `python -m pytest platform_tests/scripts/test_fab13_retention_policy.py::test_session_envelope_git_status_top_level_timeout_fails_soft -q --tb=short` | Pass with explicit unavailable reason |
| Status probe timeout | `python -m pytest platform_tests/scripts/test_fab13_retention_policy.py::test_session_envelope_git_status_status_timeout_fails_soft -q --tb=short` | Pass with explicit unavailable reason |
| Shared-module nonimpairment | `python -m pytest platform_tests/scripts/test_fab13_retention_policy.py -q --tb=short` | The four WI-5396 tests pass; any remaining failure is exactly the unchanged WI-5404 node and is disclosed, not absorbed |
| Static quality | `ruff check` and `ruff format --check` on both targets; `python -m py_compile` on both targets | All pass |
| Worktree hygiene | `git diff --check --` for both targets and exact scoped diff review | No whitespace errors; only the hash-bound WI-5396 diffs are present |
| Harness nonimpairment | Read-only process/config review plus frozen harness-parity rerun when finalizing | No process termination, eligibility/routing/config change, or harness impairment; frozen parity remains green |
| Canonical finalization | Governed finalizer dry-run/readback | Only declared implementation targets plus canonical thread history are selected; any hash, ownership, or authority drift fails closed |

## Acceptance Criteria

1. Independent GO addresses this exact two-file, no-semantic-edit transaction.
2. A matching claim and schema-v3 implementation-start packet authorize both
   paths.
3. Both target hashes remain exact through implementation-report filing.
4. The four WI-5396 tests pass and the full module's unrelated WI-5404 result
   is explicitly disclosed without modification.
5. Ruff, formatting, compilation, whitespace, applicability, and mandatory
   clause gates pass.
6. Independent Loyal Opposition returns VERIFIED against canonical evidence.
7. The exact finalizer commits only the two implementation targets and
   canonical thread history under separately valid mechanical authority.
8. No dispatcher, TAFE, harness, runtime-envelope data, credential, push,
   deployment, release, or unrelated worktree state changes.

## Risks / Rollback

- **Hash drift:** fail closed and return for a fresh reviewed proposal; never
  adopt changed bytes by implication.
- **Shared-test commingling:** WI-5404 remains a separate hunk owner. Any
  WI-5404 byte appearing before WI-5563 finalization requires a fresh exact
  attribution or a hunk-scoped finalizer.
- **Ancestor Git scan recurrence:** the focused exact-root and timeout tests
  are mandatory; unavailable Git evidence must remain explicit and fail soft.
- **Finalizer overreach:** finalizer dry-run/readback must prove the exact
  include set before any real-index or commit action.
- **Rollback:** because the candidate is not semantically edited here, a
  failed review leaves current bytes untouched and uncommitted. Any later
  committed rollback requires its own governed transaction.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` - no semantic edit;
  exact hash-bound adoption only.
- `platform_tests/scripts/test_fab13_retention_policy.py` - no semantic edit;
  exact hash-bound adoption only.
- The next canonical WI-5563 bridge entries created by the governed protocol.

## Exclusions

- WI-5404's live-PID fixture repair.
- Any other hunk in the shared test module.
- Dispatcher/TAFE configuration or runtime state.
- Harness role, eligibility, routing, allowance, or process lifetime.
- Runtime session-envelope data.
- Direct bridge-file mutation outside the governed writer/finalizer.
- Credentials, Git push/history rewrite, deployment, release, or external
  systems.
- Every unrelated dirty worktree path.

## Recommended Commit Type

`fix`
