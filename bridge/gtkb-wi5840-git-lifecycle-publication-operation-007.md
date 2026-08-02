REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved ::init gtkb pb; manual physical-bridge continuation with dispatcher/TAFE disabled
author_metadata_source: explicit current-session metadata

bridge_kind: prime_proposal
Document: gtkb-wi5840-git-lifecycle-publication-operation
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5840-git-lifecycle-publication-operation-006.md
Controlling GO: bridge/gtkb-wi5840-git-lifecycle-publication-operation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5840

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "platform_tests/scripts/test_git_lifecycle_publication.py"]
implementation_scope: corrective_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# REVISED Proposal — Complete Publication Fail-Closed Evidence and Remove the Local Blob Threshold

## Revision Claim

Accept both findings in version 006. The implementation will add focused
publication-path coverage for every previously disclosed fail-closed condition,
prove each denial occurs before `update-ref` or push, and add
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to the carried-forward applicability
mapping.

This revision also corrects one same-scope defect found during Prime Builder
re-evaluation: both the CLI parser and service currently hard-code a
`10_000_000` byte publication ceiling. Version 001 required the blob-size
ceiling to be an explicit argument and stated that no default may let an
under-specified invocation publish. The implementation will therefore make
`--max-blob-bytes` required and remove the service default; tests will provide
the value explicitly and require it to be positive.

This is a revised proposal, not a post-implementation report. Version 006 is
the current NO-GO, so no protected target may be edited until this exact
revision receives a fresh independent GO and Prime Builder obtains a matching
claim and implementation-start packet.

## Findings Addressed

### P1 — Accepted: seven approved denial paths lack direct executed evidence

The current 16-test module proves the happy path and many important failures,
but it does not directly execute these seven approved conditions:

1. empty publication range;
2. an unresolvable object in the range;
3. an unexpected range object type;
4. `.git/index` mutation between binding and the pre-ref recheck;
5. candidate parentage other than exactly one fetched-base parent;
6. candidate more than one commit ahead of the fetched base; and
7. source/destination ref rename denial.

The correction will add one focused test per condition. Each test will assert
the exact `OperationDenied.code`, record the command sequence, and prove that
no later mutating command occurs. Range and candidate-shape tests will exercise
the existing production guards through controlled repository/boundary seams,
not by duplicating the guard logic in tests. The index test will provide two
different snapshot byte sequences and require denial before `update-ref`. The
rename test will exercise the exact `validate_remote_push` guard invoked by the
publication operation and require denial before fetch, ref creation, or push.

No test may weaken the guard, treat a raised denial as a pass without checking
its code and side-effect boundary, or substitute source-text presence for
executed behavior.

### P3 — Accepted: advisory lifecycle applicability was omitted

`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is now linked below and mapped to the
explicit proposal, implementation-report, NO-GO, re-review, and eventual
VERIFIED lifecycle. It is advisory and was not the P1 execution blocker, but
including it prevents another avoidable applicability gap.

### Prime Builder additional finding — hard-coded blob threshold contradicts the approved input contract

Current production code contains both:

- `publish.add_argument("--max-blob-bytes", type=int, default=10_000_000)` in
  `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`; and
- `max_blob_bytes: int = 10_000_000` in
  `GitLifecycleService.publish_candidate_branch`.

Those are file-local threshold policies. They contradict version 001's
explicit-input/no-default requirement and the owner's active direction to
centralize timers, throttles, thresholds, fan-out, and concurrency policy in a
governed SoT.

The bounded correction will:

1. make CLI `--max-blob-bytes` required, with no numeric fallback;
2. make `max_blob_bytes` a required service keyword argument;
3. reject values less than one before fetch or any other side effect; and
4. update every focused invocation to supply its chosen ceiling explicitly.

This is the smallest same-scope correction. It exposes an explicit boundary
that WI-5806 can later populate from centralized typed configuration without
retaining a service-local policy. It does not create a competing timer or
threshold registry and does not duplicate WI-5806.

## Approval and Project Status Correction

WI-5840 is an active member of the active
`PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE` project. The active,
list-free, non-expiring project authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE`
version 3 allows source and test mutation for active project members while
retaining all bridge, claim, start, testing, review, and finalization gates.

The MemBase work item's legacy `approval_state: unapproved` is noncontrolling
under the owner's explicit project-only inheritance doctrine. No per-WI owner
approval or AUQ is required. This correction performs no Git push, history
rewrite, release, deployment, dispatcher mutation, or other PAUTH-forbidden
operation.

## Requirement Sufficiency

**Existing requirements sufficient.** Version 001's explicit acceptance
matrix, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`,
`ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`, and version 006 fully define the
missing test evidence. Version 001 also already requires an explicit
blob-ceiling argument with no publishing default. No new or revised formal
requirement is needed before implementation.

## Exact Scope and Exclusions

The approved target cohort remains unchanged:

- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`
- `platform_tests/scripts/test_git_lifecycle_publication.py`

Expected corrective hunks are limited to the service, CLI, and focused test.
`commands.py` remains declared because it is part of the original reviewed
cohort; it need not change unless the fresh GO identifies a concrete command
boundary requirement. Any need to touch a fifth path stops for scope review.

Explicitly excluded:

- execution of WI-5802's publication operation or any real push;
- changes to the direct-git-effect gate or read-only allowlist;
- force, deletion, upstream changes, retries, branch rename, or history rewrite;
- generalized push behavior or a second publication API;
- MemBase, project, PAUTH, WI, specification, ADR/DCL/GOV, or Deliberation
  Archive mutation;
- dispatcher, TAFE, route, harness identity, credentials, Git finalization,
  external systems, deployment, release, or destructive cleanup.

The four targets are tracked and clean at proposal time. Before implementation,
Prime Builder must re-check exact preimages, same-target bridge collisions,
claims, and live packets. The adjacent WI-5187 NO-GO remains disclosed and is
not merged into this correction.

## Proposed Test Design

| Condition | Focused fixture | Required denial/evidence |
|---|---|---|
| Empty range | Controlled `rev-list --objects` result through the publication path | `empty_publication_range`; no `update-ref`; no push |
| Unresolvable range entry | Malformed object id and failed batch-check variants | `range_object_unresolvable`; no `update-ref`; no push |
| Unexpected object type | Controlled batch-check result with unsupported type | `range_object_type_unexpected`; no `update-ref`; no push |
| Index changes | Sequential index snapshots differ after enumeration | `index_changed_during_publication`; no `update-ref`; no push |
| Wrong parentage | Candidate parent seam returns zero, two, or wrong parent | `candidate_parentage_invalid`; no `update-ref`; no push |
| More than one ahead | Candidate count seam returns a value other than one | `candidate_not_single_commit_ahead`; no `update-ref`; no push |
| Rename denial | Exact publication ref-validation guard receives differing source/destination | `remote_ref_rewrite_prohibited`; no fetch, `update-ref`, or push |
| Missing blob ceiling | Invoke CLI without `--max-blob-bytes` | parser denial before service invocation |
| Invalid blob ceiling | Invoke service/CLI with zero or negative value | bounded validation denial before fetch or mutation |
| Explicit blob ceiling | Existing success and blob-size fixtures pass explicit values | same behavior; evidence records chosen ceiling |

Test helpers may capture exact argv and controlled return values, but must not
run network operations, create external paths, or perform real remote mutation.

## Specification Links

- Required: `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — Git effects require the
  canonical authority, scope, and evidence boundary.
- Required: `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — binds the publication
  operation to exact fail-closed sequencing.
- Required: `DCL-GIT-BRANCH-BINDING-PROMOTION-001` — candidate ancestry and
  ref identity must remain exact.
- Required: `GOV-WORK-TREE-HYGIENE-001` — exact preimages, exclusion paths,
  and index stability remain binding.
- Required: `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` — remote observation
  and published-state evidence are not inferred.
- Required: `GOV-FILE-BRIDGE-AUTHORITY-001` — the numbered append-only chain
  and independent review are authoritative.
- Required: `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active
  parent-project PAUTH controls implementation start.
- Required: `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project PAUTH
  does not bypass fresh GO, claim, packet, or verification.
- Required: `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — preserve project
  and specification linkage.
- Required: `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and
  `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — require executed,
  evaluable spec-to-test evidence.
- Required: `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — existing lifecycle
  behavior must remain green.
- Advisory: `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — maps the explicit
  proposal/report/verdict lifecycle requested in P3.
- Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — preserve durable in-root
  traceability and placement.

## Prior Deliberations

- `DELIB-20260731-WI5840-PAUTH-PERMIT-GIT-COMMIT` — project PAUTH v3 and its
  retained prohibition on push, rewrite, release, and deployment.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-PREPARATION-APPROVAL` — bounded
  publication preparation track.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-CURRENT-HEAD-SELECTION` — exact
  source-tree selection for the separate WI-5802 execution.
- `DELIB-20260730-WI5802-CLEAN-BRANCH-PUBLICATION-PAUTH-V1` — separate WI-5802
  authority; not implementation authority for this source/test correction.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` and WI-5853 — historical
  NO-ACTION incident context; not implementation authority.
- `DELIB-202667722` — owner timer/threshold governance direction coordinated
  with WI-5806.
- Full physical thread versions 001 through 006, including controlling GO 002
  and current NO-GO 006.

## Owner Decisions / Input

- Owner AskUserQuestion, 2026-07-31: selected **Propose a governed publication
  verb** rather than widening the raw-Git allowlist or manually bypassing it.
- Owner approved the Git Lifecycle project's list-free PAUTH and later v3
  amendment through `DELIB-20260731-WI5840-PAUTH-PERMIT-GIT-COMMIT`.
- Owner directive in this session: active project WIs inherit implementation
  approval from their parent project; legacy per-WI approval fields do not.
- Owner directive in this session: remove hard-coded timers, throttles,
  thresholds, fan-out, and concurrency policies and centralize them in a
  governed SoT, coordinated here with WI-5806.

No new owner decision is required. A real branch push remains separately
forbidden and owner-gated; this proposal requests no push.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5840 physical bridge chain versions 001 through 006; version 006 P1 and P3 findings; DELIB-20260731-WI5840-PAUTH-PERMIT-GIT-COMMIT; DELIB-202667722",
  "canonical_authority": "REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001; ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m groundtruth_kb.git_lifecycle publish with every publication identity and max-blob-bytes value explicit",
  "before_behavior": "The publication operation implements the approved fail-closed guards, but seven guards lack direct executed fixtures and the CLI and service silently supply a 10000000-byte policy when the caller omits the ceiling.",
  "after_behavior": "Every approved guard has direct denial and side-effect-boundary evidence, and an under-specified caller is rejected because the blob ceiling is explicit, positive, and has no file-local fallback.",
  "self_descriptive_naming": "The existing publish and max-blob-bytes names remain unchanged; required input makes the operational ceiling visible at the invocation boundary.",
  "obsolete_guidance_disposition": "No guidance, command, or lifecycle route is retired. The correction completes the original version-001 verification matrix and removes a contradictory default.",
  "history_preservation": "No branch, ref, commit, remote, or bridge history is rewritten. Prior numbered bridge files remain append-only.",
  "worker_loading_paths": [],
  "superseded_guidance": [],
  "baseline": {
    "focused_tests": 16,
    "direct_missing_denial_fixtures": 7,
    "cli_blob_ceiling_has_numeric_default": true,
    "service_blob_ceiling_has_numeric_default": true
  },
  "expected_result": {
    "direct_missing_denial_fixtures": 0,
    "cli_blob_ceiling_has_numeric_default": false,
    "service_blob_ceiling_has_numeric_default": false,
    "positive_explicit_blob_ceiling_required": true,
    "real_git_effects_executed_by_tests": false
  },
  "rollback": {
    "instructions": "Revert only attributable post-GO hunks in the original four-target cohort through a separately governed transaction.",
    "verification": "Rerun the focused publication suite, the three declared Git-lifecycle regression modules, and both Ruff gates; confirm no ref or remote state changed."
  },
  "hard_invariants": [
    "the direct-git-effect gate and read-only allowlist remain unchanged",
    "no force, ref deletion, upstream change, rename, retry inference, or history rewrite is introduced",
    "every denial stops before the next side effect",
    "the blob ceiling applies only to blob objects and is supplied explicitly",
    "no real push or external-system mutation occurs during implementation or tests",
    "the diff remains inside the original four-target cohort"
  ],
  "fail_closed_conditions": [
    "empty range",
    "unresolvable object",
    "unexpected object type",
    "index mutation",
    "invalid candidate parentage",
    "candidate more than one commit ahead",
    "source and destination rename",
    "missing or non-positive blob ceiling"
  ],
  "essential_context_preservation": "Preserve the existing publication operation, exact command boundary, operation-time remote checks, candidate ancestry proofs, single compare-and-create ref, single same-name push contract, evidence result shape, and every existing Git-lifecycle regression behavior."
}
```

## Specification-Derived Verification Plan

| Requirement | Executed evidence after implementation | Expected result |
|---|---|---|
| Every enumerated failure stops before the next side effect | Nine focused denial fixtures above | Exact denial code; no later `update-ref`/push; rename denies before fetch |
| Threshold is explicit and valid | CLI omission, zero/negative, and explicit-value tests | No production numeric fallback; positive explicit value required |
| Existing publication success/failure behavior | Complete focused module | All current 16 tests plus new tests pass |
| Nonimpairment | Three declared regression modules | Existing lifecycle behavior remains green |
| Code quality | Ruff check and separate Ruff format check | Both pass for the declared cohort |
| Lifecycle evaluability | New report with exact commands/results and updated mapping | Independent reviewer can reproduce all evidence |

Required commands:

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_publication.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py platform_tests/scripts/test_git_lifecycle_maintenance.py platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle platform_tests/scripts/test_git_lifecycle_publication.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle platform_tests/scripts/test_git_lifecycle_publication.py`

The later report must state exact test counts, durations, warnings, and any
failure. Passing source presence or prior 16-test evidence cannot substitute
for the new executed denial paths.

## Acceptance Criteria

1. Each of the seven version-006 conditions has its own executed fixture and
   exact denial assertion.
2. Every denial proves no later mutating command occurs.
3. CLI and service contain no numeric blob-ceiling default; a positive explicit
   value is required before any operation begins.
4. Existing success, blob-only ceiling, protected-destination, single-fetch,
   single-ref, and no-retry behavior remains green.
5. The lifecycle advisory DCL is linked and mapped in the report.
6. The full focused and regression commands plus both Ruff gates pass and are
   recorded exactly.
7. The diff remains inside the original four-target cohort; no fifth path,
   real Git effect, dispatcher, TAFE, or KB mutation occurs.
8. A new envelope-valid post-implementation report is independently reviewed
   before any VERIFIED/finalization action.

## Risk and Rollback

- **Tests accidentally bypass the production guard.** Exercise guards through
  the actual publication/service path and assert command ordering, not duplicate
  helper logic.
- **Defensive branches are difficult to reach with a real repository.** Use
  bounded injected repository responses while retaining the public operation
  entry point and exact production guard.
- **Required threshold breaks undocumented callers.** Search all repository
  call sites before mutation and update only declared-cohort callers; any
  required fifth-path change stops for a revised scope review.
- **Adjacent Git-lifecycle ownership.** Re-check WI-5187 and every same-target
  active thread/claim immediately before start and stop on a live collision.

Rollback is a focused revert of only attributable post-GO hunks in the declared
cohort. It requires no ref deletion, push, history rewrite, KB change, or bridge
rewrite; the numbered bridge history remains append-only.

## Pre-Filing Evidence

- Version 006 is the strict current physical `NO-GO` head; this draft responds
  exactly to that file and preserves controlling GO 002.
- All four targets are tracked and clean at proposal time.
- Candidate applicability and mandatory clause preflights will be run before
  filing; any missing required/advisory spec or blocking gap stops publication.
- Harness A's Prime Builder role eligibility was checked through the canonical
  harness role projection.
- Dispatcher and TAFE remain deliberately disabled and outside scope.

## DISARM — Governance, Git, and Runtime Mechanics

This revision authorizes no source/test change before fresh GO and valid
claim/start evidence. The future packet is transaction-local evidence, not a
formal artifact or substitute for project PAUTH and independent review. No real
branch, ref, index, commit, push, remote, credential, dispatcher, TAFE,
deployment, release, or external-system mutation is requested.

## Recommended Commit Type

`test` — complete the approved fail-closed evidence and remove a contradictory
local publication threshold without adding a new publishing capability.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
