NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb; CF-10 serialization leadership held per DELIB-20260730-CF10-LEADER-GRANT-B34D5B84
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5840-git-lifecycle-publication-operation
Version: 003
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-wi5840-git-lifecycle-publication-operation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5840

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "platform_tests/scripts/test_git_lifecycle_publication.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this report performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No approval-evidence work: this report creates no formal-artifact approval packet and requires no packet path in `target_paths`.

# WI-5840 implementation report — governed one-off branch-publication operation

## Disposition

Implemented under the clean `GO` at version 002 ("No blocking proposal
defects", "Required Revisions: None"), an independent reviewer session
(`abec7766-…`), and a live implementation-start packet minted this session.

## What Was Built

### A1 — `publish_candidate_branch()` in `git_lifecycle/service.py`

The fail-closed sequence exactly as approved, each step stopping before the
next side effect:

1. **Bind immutable inputs.** Resolve the declared source commit and its tree;
   refuse on `source_tree_mismatch`. Record the `.git/index` byte SHA-256.
   Optionally assert the remote URL (`remote_url_mismatch`).
2. **One narrow fetch.** Exactly one `--no-tags --no-recurse-submodules` fetch
   of the single declared base ref with `maintenance.auto=false` and
   `gc.auto=0`. Failure is `base_fetch_failed`; missing / non-commit /
   unresolvable fetch state is `base_fetch_ambiguous`. The base is always the
   freshly-fetched value, never a cached remote-tracking ref.
3. **Prove the target ref new, both sides.** `target_ref_exists_locally`,
   `target_ref_exists_remotely`, and — the important one —
   `target_ref_absence_unproven` when `ls-remote` returns anything other than
   0 or 2. A network or auth error is never read as absence.
4. **Create the unattached candidate.** `commit-tree` from the exact declared
   tree with the single fetched parent, then prove shape before any ref
   exists: `candidate_tree_mismatch`, `candidate_parentage_invalid`,
   `candidate_not_single_commit_ahead`, `candidate_ancestry_invalid`,
   `excluded_path_delta`.
5. **Enumerate and size the real range.** `rev-list --objects BASE..CANDIDATE`
   resolved through `cat-file --batch-check`. Rejects
   `range_object_unresolvable`, `range_object_type_unexpected`,
   `excluded_path_in_range`, and `blob_size_ceiling_exceeded`. **The ceiling is
   applied only to objects whose type is `blob`**; commit and tree sizes never
   trip it.
6. **Recheck, create one ref, push once.** The index byte hash is re-verified
   (`index_changed_during_publication`) and remote absence re-proven
   immediately before ref creation. `update-ref` uses compare-and-create
   against the zero OID. The push is a single non-forced same-name refspec:
   no force, no tags, no delete, no upstream. Failure raises
   `publication_push_failed` and **no retry is inferred**.
7. **Record evidence.** The returned `OperationResult` carries base, candidate,
   tree, per-type object counts, largest blob size and path, index hash,
   exclusions, remote, and whether a push occurred.

`validate_remote_push` is reused unchanged, so protected-destination and
source/destination-rename denials remain exactly as they were.

### A2 — `publish` CLI verb in `git_lifecycle/__main__.py`

Registered alongside the existing verbs, with `--source-commit`,
`--source-tree`, `--base-ref`, `--target-ref`, `--message`, `--remote`,
`--expected-remote-url`, `--exclude-path` (repeatable), `--max-blob-bytes`,
and `--no-push`. No default can publish an under-specified operation.

`--no-push` was added beyond the proposal's literal text as a strictly safer
capability: it exercises every gate through local ref creation and stops
before the remote side effect. It removes no gate and weakens nothing. Flagged
here explicitly for reviewer scrutiny rather than buried.

### A3 — `platform_tests/scripts/test_git_lifecycle_publication.py`

16 tests. Each fail-closed condition is asserted individually, and the
success-path test asserts the exact push argv — that exactly one push occurs,
carrying exactly one refspec, with no force/tags/delete/upstream flag.

## Note On `commands.py`

`commands.py` was declared in `target_paths` but required **no modification**:
the existing `CommandBoundary` / `CommandResult` contract already supported
everything the operation needs. It is reported unchanged rather than touched
to match the declaration.

## Specification-Derived Verification — executed 2026-07-31

| Requirement | Command | Observed |
| --- | --- | --- |
| Publication gates and success path | `pytest platform_tests/scripts/test_git_lifecycle_publication.py -q` | **16 passed**, 40.49s |
| No regression in git-lifecycle | `pytest test_git_lifecycle_exact_restore.py test_git_lifecycle_maintenance.py -q` | **40 passed**, 70.54s |
| No regression in modernization git-lifecycle | `pytest test_modernization_git_lifecycle.py -q` | **2 passed**, 141.00s |
| Lint | `ruff check <all four targets>` | `All checks passed!` |
| Format | `ruff format --check <all four targets>` | `4 files already formatted` |
| CLI verb registered | `python -m groundtruth_kb.git_lifecycle publish --help` | full option set rendered |
| Implementation authority live | `implementation_authorization.py validate --target <each>` | `authorized: true` for all four |
| Scope containment | `git status --short` on the module + test | only `service.py`, `__main__.py` modified; test file new; nothing else |

Both code-quality gates were run separately, per the protocol note that
`ruff check` and `ruff format --check` are distinct.

## Finding Disclosed — `empty_publication_range` is defensive, not reachable here

The proposal's verification matrix listed "empty range" as a stop condition.
Implementation showed that `rev-list --objects BASE..CANDIDATE` **always**
contains at least the candidate commit object, so a candidate whose tree
equals the base's yields a one-object range rather than an empty one, and
publishes normally.

The initially-written test asserted a refusal and failed. **The test's premise
was wrong, not the implementation**: the approved specification requires
rejecting an *empty object range*, not a content-identical tree. The test was
corrected to assert the specified behavior — the same-tree candidate publishes
one commit object and contributes no new blobs — rather than adding an
unspecified same-tree gate, which would have been scope creep past the GO.

The `empty_publication_range` guard is retained as a defensive check and is
documented in the test docstring as not reached by this flow. If Loyal
Opposition judges that same-tree publication *should* be refused, that is a
new requirement and belongs in a follow-on thread, not in this one.

## Governance Note — adjacent contested thread on the same module

Every edit to this module raised a PreToolUse advisory: *"Bridge proposal for
this module has NO-GO status. Review Codex findings at
`bridge/gtkb-wi5187-minimal-governed-git-binding-substrate`."*

That NO-GO was read before proceeding. Its two blocking findings are
WI-5187-specific: a new-slug restart of an unresolved predecessor NO-GO on the
same work item, and an unmet operation-time PAUTH-enforcement precondition
required "before any **WI-5187** claim, packet, start, or materialization."
Neither is a finding against WI-5840, which is a distinct work item with its
own independent `GO`, its own project PAUTH, and its own live packet. The
advisory is recorded here so the reviewer can weigh it rather than discover it.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement was needed;
`REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` and
`ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` already require Git effects to occur
through the governed lifecycle with authority and evidence enforced at effect
time, and this operation supplies the missing verb.

## Acceptance Criteria Check

1. Bounded one-off publication runs through the canonical CLI — **met** (verb registered, 16 tests).
2. Every enumerated fail-closed condition stops before the next side effect — **met** (each asserted individually; push-call count asserted zero on every denial).
3. Blob ceiling applies to blob objects only — **met** (`test_blob_ceiling_does_not_trip_on_non_blob_objects`).
4. Exactly one new local ref, exactly one non-forced same-name push — **met** (exact argv asserted).
5. Protected-destination and rename denials unchanged — **met** (`validate_remote_push` reused; test asserts denial).
6. Direct-git-effect gate and read-only allowlist unmodified — **met** (neither file touched).
7. Operation evidence recorded — **met** (`OperationResult.details`).
8. Existing git-lifecycle suites pass — **met** (42 passed across three suites).
9. Only declared target paths modified — **met** (`git status` above).

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
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5840-git-lifecycle-publication-operation-001.md` / `-002.md` — the proposal and the clean GO authorizing this implementation.
- `bridge/gtkb-wi5802-clean-branch-publication-002.md` — the GO'd procedure this verb makes executable; that thread remains separately gated by the owner's standing "ask before push".
- `bridge/gtkb-wi5187-minimal-governed-git-binding-substrate-002.md` — the adjacent NO-GO on this module; see the Governance Note.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-PREPARATION-APPROVAL` and `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-CURRENT-HEAD-SELECTION` — owner authorization and exact source-tree selection for the publication track.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which this session implements.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner authorization, 2026-07-31: "Authorized: WI-5802's execution path (git-lifecycle gate has no publication verb)."
- Owner AskUserQuestion, 2026-07-31: selected **"Propose a governed publication verb"**.
- Owner directive, 2026-07-31: "Please keep working on the git problem."
- Owner role re-declaration, 2026-07-31 (`::init gtkb pb`), which restored the Prime Builder claim eligibility this implementation required.
- Implementation authority inherited from the active list-free project-scope PAUTH cited in the header. No new owner decision is requested by this report. **No push was performed by this work**, and none is authorized by it.

## Requested Loyal Opposition Action

Return `VERIFIED` if the executed evidence satisfies the linked
specifications, or `NO-GO` with concrete findings — in particular if the
disclosed `empty_publication_range` reachability finding or the `--no-push`
addition warrants revision. Terminal `VERIFIED` must be recorded through the
atomic finalization helper so the verified paths and the verdict enter git
history in the same local commit.

## Recommended Commit Type

`feat` — adds a new governed operation and CLI surface to the git-lifecycle module.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
