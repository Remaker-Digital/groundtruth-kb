NEW
::init gtkb pb
::open build

# WI-5704 Transient Registry Index Recurrence Prevention

bridge_kind: prime_proposal
Document: gtkb-wi5704-transient-index-recurrence-prevention
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-28 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5704-TRANSIENT-INDEX-REPAIR-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5704

target_paths: [".gitignore", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py"]

implementation_scope: defect_fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The WI-5441 terminal-finalization commit `f9e85829e` accidentally tracked
`.gtkb-index-hl705ij2/index`. The source is deterministic:
`scripts/check_protected_commit_authorization.py` creates its immutable index
snapshot with `TemporaryDirectory(prefix=".gtkb-index-", dir=root)` even
though the same module already exposes `_scratch_root(root)` for ignored,
guarded runtime state.

The current tree has the transient path deleted, but WI-5706 cannot obtain an
implementation-start packet because the canonical operation-time classifier
correctly returns `unclassified` for that path. This proposal prevents a
recurrence and adds only the narrow classification needed for a separately
authorized cleanup plan to describe the exact transient path. It does not
perform the WI-5706 deletion.

## Defect Reproduction

The following current-state evidence is independently reproducible:

1. `scripts/check_protected_commit_authorization.py:901` creates the temporary
   index directory at the repository root.
2. `scripts/check_protected_commit_authorization.py:574-587` already provides
   `_scratch_root(root)`, which creates and validates `.gtkb-state` against
   root escape, symlink, junction, and reparse-point hazards.
3. Commit `f9e85829e` contains `.gtkb-index-hl705ij2/index`; the current
   worktree records its deletion.
4. The canonical registry resolver finds no exact or structural membership for
   `.gtkb-index-hl705ij2/index`, so the tracked transient is disposable rather
   than a load-bearing artifact.
5. Current `classify_target('.gtkb-index-hl705ij2/index')` returns
   `unclassified`, and WI-5706 implementation start consequently returns
   `target_mutation_class_not_allowed` before creating a packet.
6. The focused pre-change baseline is 159 passing tests:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --no-header --tb=short
```

## In-Root Placement Evidence

All five implementation targets are inside `E:\GT-KB`. Runtime snapshots will
move from the repository root into `E:\GT-KB\.gtkb-state`, also inside the
mandatory project-root boundary. No external file is read as authority or
written as output.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` - registry membership is the sole
  keep/disposable authority; classification as repository metadata does not
  create registry membership.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - registered identity
  changes remain separately authorized; this item permits deletion only when
  canonical registry resolution confirms no membership.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the exact safe
  transient-index shape must be mechanically classifiable without broadening
  unrelated dot-prefixed targets.
- `GOV-WORK-TREE-HYGIENE-001` - runtime scratch must not recur as tracked
  repository content, and cleanup must be deterministic.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - success, failure, and
  interruption paths must converge to the same no-transient postcondition.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the owner decision and
  PAUTH bound this proposal to five exact target paths and registered mutation
  classes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation remains gated by an
  independent GO, matching claim, implementation-start packet, report, and
  terminal verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - each applicable
  specification is linked to concrete verification below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the live PAUTH,
  project, and work-item triple is declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal verification
  requires an executed result for every verification family in this proposal.
- `GOV-STANDING-BACKLOG-001` - WI-5704 and TEST-11722 are the canonical
  planning and acceptance records for this defect.

## Prior Deliberations

- `DELIB-202667518` - the owner authorized WI-5704 exactly as stated, including
  the five implementation paths and explicit exclusions.
- `DELIB-202667516` - the owner separately authorized WI-5706 repair-forward;
  that deletion remains outside this proposal and depends on this repair.

## Owner Decisions / Input

`DELIB-202667518` records the owner's exact response, "Authorize WI-5704
exactly as stated." It is bound to WI-5704 and is the owner evidence for
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5704-TRANSIENT-INDEX-REPAIR-20260728`.
No additional owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision, WI-5704 v4,
TEST-11722 v4, linked specifications, and exact PAUTH determine the required
behavior without a new specification or interpretive choice.

## Proposed Implementation

1. Change `_index_snapshot` to obtain the existing validated
   `_scratch_root(root)` and create `.gtkb-index-<random>/index` beneath that
   ignored runtime root. Retain the immutable index identity, read-only mode,
   sanitized `GIT_INDEX_FILE`, and before/after identity checks unchanged.
2. Add `.gtkb-index-*/` to `.gitignore` as a defense against any root-level
   recurrence from older or interrupted code paths. This is a backup control,
   not the primary cleanup mechanism.
3. Add one exact root-transient matcher to the protected-commit checker. Reject
   staged add, modify, copy, and rename records that would create, retain, or
   move content into `.gtkb-index-<safe-suffix>/index`. The cleanup exception
   is deletion only.
4. Bind the deletion exception to a coherent canonical registry snapshot. A
   staged deletion passes this transient-specific rule only when the resolver
   returns no registry membership. Missing or incoherent registry authority
   cannot grant the exception. A registered path continues through the
   existing identity-transition denial.
5. Extend `classify_target` so only the normalized exact shape
   `.gtkb-index-[a-z0-9_]{8}/index` returns `repository_metadata`. This matches
   Python's current temporary-name alphabet and length. The classification
   permits a governed plan to describe the operation; it does not register the
   path or authorize an operation by itself.
6. Add focused tests for exact positive and negative classifier shapes,
   staging behavior, registry membership behavior, cleanup across normal exit,
   exception, and `KeyboardInterrupt`, and preservation of real-index and
   reconciliation behavior.

## Explicit Exclusions

This proposal performs no KB mutation.

- No staging, committing, restoring, or deleting
  `.gtkb-index-hl705ij2/index`; that is WI-5706.
- No canonical registry TOML, packaged mirror, MemBase, `groundtruth.db`, or
  registry journal mutation.
- No edit to
  `config/governance/project-authorization-operation-taxonomy.toml`; the
  canonical `repository_metadata` class already exists.
- No bridge or advisory deletion.
- No dispatcher activation or configuration change.
- No history rewrite, push, credential action, release, or deployment.
- No broad classification of `.gtkb-index-*`, arbitrary dot-prefixed paths,
  directories, alternate filenames, uppercase suffixes, separators, or parent
  traversal.

## Specification-Derived Verification Plan

| Specification | Verification | Required result |
|---|---|---|
| `GOV-PLATFORM-SOT-REGISTRY-001` | Load the coherent registry through the canonical reader; test unregistered and registered transient-path deletion cases | Only a registry-confirmed no-membership deletion receives the cleanup exception; no registry generation changes. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Stage a registered exact transient-shaped fixture deletion and an unregistered fixture deletion | Registered identity deletion is denied; the exact unregistered cleanup deletion is permitted. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Focused classifier and envelope tests for the positive exact shape plus malformed suffix, alternate leaf, directory-only, nested, uppercase, traversal, and unrelated dot paths | Only `.gtkb-index-[a-z0-9_]{8}/index` is `repository_metadata`; all negatives remain `unclassified`. |
| `GOV-WORK-TREE-HYGIENE-001` | Exercise `_index_snapshot` on normal exit, raised exception, and `KeyboardInterrupt`; scan both root and `.gtkb-state` afterward | No `.gtkb-index-*` directory remains after each outcome, and no root transient is created during the context. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Repeat the focused snapshot tests and compare resulting path inventories | Identical no-transient postcondition on every run and every exit path. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Mandatory applicability preflight, implementation-start begin after GO, and packet target/class inspection | Active PAUTH and packet contain exactly the five targets and required classes; excluded operations remain excluded. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict lifecycle resolution and bridge compliance audit for proposal, report, and verdict | Valid append-only NEW to GO/NO-GO to report to VERIFIED/NO-GO lifecycle with independent review. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Final-content proposal and report compliance audits | No placeholder, missing specification, or unmapped cited authority. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight and live PAUTH/project/WI lookup | The exact triple resolves and WI-5704 is included once. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report every table row plus focused command outcomes | Every linked specification has fresh executed evidence. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5704 --json` before implementation and after terminal verdict | WI-5704 remains the linked work authority and reaches a terminal resolution only after verification. |

Focused implementation command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --no-header --tb=short
```

Focused quality gates:

```text
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
```

Post-implementation checks must also show the real Git index path remains
unchanged, registry validation remains valid and coherent, and a dry-run of the
subsequent WI-5706 implementation start classifies its sole target as
`repository_metadata` without creating a packet or mutating WI-5706.

## Acceptance Criteria

1. `_index_snapshot` never creates `.gtkb-index-*` directly under the project
   root and cleans its scratch directory after success, exception, and
   interruption.
2. `.gitignore` contains one effective `.gtkb-index-*/` defensive rule.
3. The commit checker rejects staged addition, modification, copy, rename
   source, and rename destination records involving the exact root transient
   file, except for a pure deletion whose path has no canonical registry
   membership.
4. A missing, incoherent, or matching registry record cannot grant the cleanup
   exception.
5. Only `.gtkb-index-[a-z0-9_]{8}/index` classifies as
   `repository_metadata`; unrelated dot-prefixed or malformed paths remain
   `unclassified`.
6. The pre-change 159-test focused baseline remains green with the new
   regressions added, and focused Ruff check/format gates pass.
7. Registry declaration, packaged mirror, projection, generation digest, and
   record count are unchanged.
8. WI-5706's target becomes mechanically describable, but this item does not
   acquire its claim, create its packet, stage its deletion, or alter its
   bridge chain.

## Risk / Rollback

The principal risk is over-broad classification or a deletion exception that
silently weakens registered identity protection. Exact full-path matching,
negative tests, and canonical registry resolution bound that risk. A second
risk is changing immutable-index security behavior while relocating scratch;
tests therefore preserve the existing chmod, identity, sanitized environment,
real-index non-mutation, and reparse-point checks.

Before finalization, rollback is limited to restoring the five target files to
their preimages and clearing only WI-5704 staging. After a governed terminal
commit, any defect requires a new append-only repair-forward; no reset, amend,
rebase, history rewrite, or push is authorized.

## Files Expected To Change

- `.gitignore`
- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`

## Recommended Commit Type

`fix`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
