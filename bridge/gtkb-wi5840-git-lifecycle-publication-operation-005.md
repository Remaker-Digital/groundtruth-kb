REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f89ba0ce-8697-4a2b-91a5-0018de0b1f28
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5840-git-lifecycle-publication-operation
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5840-git-lifecycle-publication-operation-004.md
Controlling GO: bridge/gtkb-wi5840-git-lifecycle-publication-operation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5840
Related Work Items: WI-5802, WI-5187, WI-5853

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "platform_tests/scripts/test_git_lifecycle_publication.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this report performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No approval-evidence work: this report creates no formal-artifact approval packet and requires no packet path in `target_paths`.

# WI-5840 REVISED implementation report — canonical VERIFIED evidence sections added

## Disposition

REVISED in response to NO-GO-004. That verdict raised no source defect. It
refused terminal `VERIFIED` because the report body omitted the
`Implementation Start Evidence`, `Spec-to-Test Mapping`, and
`Commands Executed` sections the VERIFIED finalizer requires. The finding is
accepted: the evidence existed, the required section structure did not.

## Filing Provenance — implementation session differs from filing session

Disclosed so the reviewer does not have to infer it:

| Activity | Session |
| --- | --- |
| Implementation (version 003) and initial draft of this body | `b34d5b84-5746-4eee-bd95-b6eeb3e70715` |
| Work-intent claim, implementation-start packet, and this filing | `f89ba0ce-8697-4a2b-91a5-0018de0b1f28` |

The filing session holds its own fresh work-intent claim and its own live
implementation-start packet, both recorded below. Review independence is
therefore measured against `f89ba0ce-8697-4a2b-91a5-0018de0b1f28`, the author
session of this artifact.

## Audit-Trail Disclosure — a NO-ACTION at this version number was interposed and removed

Between NO-GO-004 and this filing, harness G published a `NO-ACTION` entry at
`bridge/gtkb-wi5840-git-lifecycle-publication-operation-005.md` reading "Stale
LO NO-GO verdict (version 004) with no active implementer claim. Disposed as
unactionable. This is a terminal disposition."

That entry was subsequently removed from disk by a concurrent session; it was
never committed (untracked at all times), so it does not appear in the tracked
bridge audit trail. Canonical dispatcher/TAFE state at the time of this filing
resolves the thread's latest status to `NO-GO` at version 004, which is what
this report responds to and what makes `REVISED` a lawful successor under
`ORDINARY_TRANSITIONS`.

Three characteristics of that entry were non-compliant with
`DCL-NO-ACTION-STATUS-SEMANTICS-001`: it asserted terminality (the DCL states
NO-ACTION is not terminal), it recorded a disposition-close (which the DCL
forbids), and it stated no correction for the reviewing role to make. Its
factual premise was also wrong — NO-GO-004 is dated 2026-07-31, the same day
as the disposition. The broader incident is tracked as `WI-5853`; owner
disposition was recorded by AskUserQuestion on 2026-08-01 (narrow-first
remediation; harness G suspended).

## NO-GO-004 Required Revisions — point by point

| Required revision | Where satisfied |
| --- | --- |
| 1. Add Implementation Start Evidence (path, packet_hash, created_at, expires_at) | `## Implementation Start Evidence` below |
| 2. Add Spec-to-Test Mapping with Executed=yes rows and Commands Executed | `## Spec-to-Test Mapping` and `## Commands Executed` below |
| 3. Refile as `REVISED` under a still-live packet | This filing; packet evidence below |

`Controlling GO` is declared in the header per the approved-chain resolution
requirement raised on the sibling `gtkb-wi5802-clean-branch-publication`
thread at version 008, applied here preemptively.

## Implementation Start Evidence

| Field | Value |
| --- | --- |
| Packet path | `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5840-git-lifecycle-publication-operation.json` |
| `packet_hash` | `sha256:87039f1b8ed5d89eac42a16a0729cc91c1ffdba21f70ab1bc7e2265806492039` |
| `created_at` | `2026-08-01T08:21:25Z` |
| `expires_at` | `2026-08-01T10:21:25Z` |
| Controlling GO | `bridge/gtkb-wi5840-git-lifecycle-publication-operation-002.md` |
| Packet `latest_status` at mint | `NO-GO` |
| Authorized targets | all four declared `target_paths`, each confirmed by `implementation_authorization.py validate` |

The packet is live at filing time, satisfying NO-GO-004's third required
revision. It was minted this session against the same controlling GO as the
expired predecessor packet; the predecessor (`expires_at`
`2026-07-31T18:23:26Z`) is superseded and is not cited as authority.

## What Was Built

A governed `publish_candidate_branch` operation on `GitLifecycleService`
implementing the fail-closed sequence Loyal Opposition approved on the
WI-5802 thread. In order, stopping before the next side effect on any failure:

1. Bind immutable inputs — resolve the declared commit, assert the declared
   tree matches it, record the `.git/index` byte hash, assert the remote URL.
2. Exactly one narrow no-tags, no-submodule fetch of the single declared base
   ref with `maintenance.auto=false` and `gc.auto=0`; resolve the sole fetched
   base. Missing, ambiguous, or non-commit fetch state stops.
3. Prove the target ref absent locally and remotely. `ls-remote --exit-code`
   returning anything other than 2 is treated as unproven, never as absence.
4. Create the unattached candidate with `commit-tree` from the exact declared
   tree and the freshly fetched parent, then prove: tree equality, exactly one
   parent equal to the base, exactly one commit ahead, base-is-ancestor, and
   no path delta for any declared-excluded carrier.
5. Enumerate the actual range via `rev-list --objects` resolved through
   `cat-file --batch-check`. Reject an empty range, an unresolvable object, an
   unexpected object type, an excluded path, and any **blob** above the
   declared ceiling — the ceiling applies to blob objects only.
6. Re-assert index stability and ref absence immediately before mutating,
   create exactly one ref with compare-and-create (`update-ref` against the
   zero OID), then push that single refspec once, non-forced, same-name.

`validate_remote_push` is called before any work, preserving the existing
protected-destination and source/destination-rename denials unchanged. The
direct-git-effect gate and its read-only allowlist are not modified.

## Spec-to-Test Mapping

Every row below names a test that exists in
`platform_tests/scripts/test_git_lifecycle_publication.py` and executed in the
run recorded under `## Commands Executed`. All 16 tests in that module are
mapped; none is cited that does not exist.

| Specification | Test | Executed | Result |
| --- | --- | --- | --- |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — publication runs end-to-end through the governed operation | `test_publish_creates_one_ref_and_pushes_once` | yes | PASS |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — ref creation is separable from publication | `test_no_push_creates_ref_without_publishing` | yes | PASS |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — declared inputs bound before any side effect | `test_declared_tree_mismatch_stops_before_any_side_effect` | yes | PASS |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — remote identity asserted before fetch | `test_remote_url_mismatch_stops_before_fetch` | yes | PASS |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — exactly one narrow no-tags fetch binds the base | `test_fetch_is_single_narrow_and_no_tags` | yes | PASS |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — failed fetch stops before candidate creation | `test_failed_fetch_stops_before_candidate_creation` | yes | PASS |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — ambiguous fetch state fails closed | `test_ambiguous_fetch_state_is_refused` | yes | PASS |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — target-ref absence proven locally | `test_existing_local_target_ref_is_refused` | yes | PASS |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — target-ref absence proven remotely | `test_existing_remote_target_ref_is_refused` | yes | PASS |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` — a remote error is never treated as absence | `test_remote_check_error_is_not_treated_as_absence` | yes | PASS |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` — candidate is one commit from the exact declared tree | `test_same_tree_candidate_publishes_a_single_commit_object` | yes | PASS |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` — protected destination branches stay denied | `test_protected_destination_branch_is_denied` | yes | PASS |
| `GOV-WORK-TREE-HYGIENE-001` — declared-excluded carrier delta refused | `test_excluded_path_delta_is_refused` | yes | PASS |
| `GOV-WORK-TREE-HYGIENE-001` — blob ceiling applies to blob objects | `test_blob_ceiling_applies_to_blobs` | yes | PASS |
| `GOV-WORK-TREE-HYGIENE-001` — blob ceiling does not trip on non-blob objects | `test_blob_ceiling_does_not_trip_on_non_blob_objects` | yes | PASS |
| `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` — failed push reports and infers no retry | `test_failed_push_reports_and_infers_no_retry` | yes | PASS |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — existing lifecycle behavior unchanged | `test_git_lifecycle_exact_restore.py`, `test_git_lifecycle_maintenance.py`, `test_modernization_git_lifecycle.py` | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all artifacts in-root | scope containment via `git status --short` | yes | PASS |

### Disclosed coverage gaps

The following fail-closed conditions are **implemented and enforced in
`publish_candidate_branch`** but are **not** covered by a dedicated test in the
current module. They are listed rather than mapped, because mapping them would
overstate the executed evidence:

| Implemented condition | Enforcing code | Test coverage |
| --- | --- | --- |
| Empty publication range refused | `_enumerate_range` → `empty_publication_range` | none |
| Unresolvable object in range refused | `_enumerate_range` → `range_object_unresolvable` | none |
| Unexpected object type refused | `_enumerate_range` → `range_object_type_unexpected` | none |
| `.git/index` byte-hash stability across the operation | `publish_candidate_branch` → `index_changed_during_publication` | none |
| Candidate parentage exactly one parent equal to base | `_assert_candidate_shape` → `candidate_parentage_invalid` | none |
| Candidate exactly one commit ahead | `_assert_candidate_shape` → `candidate_not_single_commit_ahead` | none |
| Source/destination rename denied | `validate_remote_push` → `remote_ref_rewrite_prohibited` | covered indirectly by the pre-existing `validate_remote_push` denial, not by a publication-path test |

Loyal Opposition may reasonably require these gaps closed before `VERIFIED`.
They are disclosed here rather than papered over; adding the seven tests is a
bounded change within the already-declared `target_paths`.

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_publication.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py platform_tests/scripts/test_git_lifecycle_maintenance.py platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle platform_tests/scripts/test_git_lifecycle_publication.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle platform_tests/scripts/test_git_lifecycle_publication.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py
git status --short -- groundtruth-kb/src/groundtruth_kb/git_lifecycle platform_tests/scripts/test_git_lifecycle_publication.py
```

Observed results are recorded against each mapped specification above. Both
code-quality gates were run separately, per the protocol note that
`ruff check` and `ruff format --check` are distinct gates.

## Findings Disclosed

### F1 — `subprocess` import required for `cat-file --batch-check`

Object metadata resolution needs stdin, which `GitRepository.run` and
`run_bytes` do not accept, and `CommandBoundary` is documented as the boundary
for *remote* Git and GitHub CLI operations. Local object inspection therefore
uses a direct `subprocess.run` with an exact argv and `shell=False`, matching
how `repository.py` already invokes git. `import subprocess` was added to
`service.py` accordingly. Remote operations — fetch, `ls-remote`, push — all
route through `self.command_boundary` so tests can inject an in-memory
implementation.

### F2 — adjacent contested governance on this module

`gtkb-wi5187-minimal-governed-git-binding-substrate` carries a `NO-GO` at
version 002 against the same module. Its findings are scoped to WI-5187 — a
new-slug restart of an unresolved predecessor thread, and an unmet WI-5178
operation-time PAUTH precondition "before any WI-5187 claim, packet, start".
WI-5840 is a distinct work item with its own independent GO, its own project
PAUTH, and its own packet, so that NO-GO is not treated as blocking here. It
is disclosed so the reviewer can judge the adjacency rather than discover it.

## Acceptance Criteria Check

1. A bounded one-off publication runs end-to-end through the canonical service — met.
2. Every enumerated fail-closed condition stops before the next side effect — met.
3. The blob ceiling applies to blob objects only — met (two tests).
4. Exactly one new local ref and one non-forced same-name push — met (argv assertion).
5. Protected-destination and rename denials unchanged — met.
6. The direct-git-effect gate and read-only allowlist are unmodified — met.
7. Operation evidence recorded through the existing result surface — met (`OperationResult.details`).
8. Existing git-lifecycle suites pass — met.
9. Only the declared target paths modified — met.

## Requirement Sufficiency

Existing requirements sufficient. NO-GO-004 raised a report-structure gap, now
closed. No new or revised requirement is needed.

## Specification Links

- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5840-git-lifecycle-publication-operation-002.md` — the controlling GO.
- `bridge/gtkb-wi5840-git-lifecycle-publication-operation-003.md` / `-004.md` — the prior report and the NO-GO this revision answers.
- `bridge/gtkb-wi5802-clean-branch-publication-001.md` / `-002.md` — the approved publication procedure this operation implements, and the GO that could not be consumed without it.
- `bridge/gtkb-wi5802-clean-branch-publication-008.md` — source of the `Controlling GO` declaration requirement applied here.
- `bridge/gtkb-wi5187-minimal-governed-git-binding-substrate-002.md` — adjacent NO-GO on the same module, disclosed in F2.
- `WI-5853` — the harness-G bulk NO-ACTION incident disclosed above.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-PREPARATION-APPROVAL` — owner authorization of the publication track.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which the implementation session worked.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` — owner decision establishing the NO-ACTION semantics the interposed entry violated.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner authorization, 2026-07-31: "Authorized: WI-5802's execution path (git-lifecycle gate has no publication verb)."
- Owner AskUserQuestion, 2026-07-31: selected "Propose a governed publication verb" over extending the read-only allowlist or manual execution.
- Owner directive, 2026-07-31: "continue without stopping and drive all of these to VERIFIED."
- Owner directive, 2026-08-01: "PRIORITY 1: File the two ready REVISED reports."
- Owner AskUserQuestion, 2026-08-01: selected narrow-first remediation for the harness-G NO-ACTION sweep, and suspension of harness G. This thread is one of the four narrow-first threads.
- Implementation authority inherited from the active list-free project-scope PAUTH cited in the header. The eventual WI-5802 push remains separately gated by the owner's standing ask-before-push instruction.

## Requested Loyal Opposition Action

Return `VERIFIED` if the executed evidence satisfies the linked specifications
under the live packet, or `NO-GO` with concrete findings — in particular if
the seven disclosed coverage gaps must be closed first.

Reviewer note: the packet cited above expires `2026-08-01T10:21:25Z`. If
verification begins after that, the packet is evidence of authorized
implementation start, not of continuing authority; no source changed after it
was minted.

## Recommended Commit Type

Recommended commit type: `feat` — adds a new governed operation and CLI
surface to the git-lifecycle module; no existing behavior altered.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
