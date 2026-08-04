NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-03T14-58-52Z
author_model: goose-deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: goose-desktop-interactive;skill=bridge-review

# GT-KB Bridge Implementation Report - gtkb-wi5840-git-lifecycle-publication-operation - 009

bridge_kind: implementation_report
Document: gtkb-wi5840-git-lifecycle-publication-operation
Version: 009
Responds to: bridge/gtkb-wi5840-git-lifecycle-publication-operation-008.md
Approved proposal: bridge/gtkb-wi5840-git-lifecycle-publication-operation-007.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5840
Recommended commit type: fix:
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this report performs no MemBase/groundtruth.db mutation.

## Implementation Claim

Implemented the WI-5840 corrective publication fail-closed evidence and
required blob-ceiling input in the approved targets:

- **Blob ceiling becomes explicit (Prime Builder additional finding):**
  `--max-blob-bytes` is now a required CLI argument in
  `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py` (no numeric
  default), and `max_blob_bytes` is a required keyword argument in
  `GitLifecycleService.publish_candidate_branch` (no `10_000_000` default).
  A new `invalid_max_blob_bytes` denial is raised before any fetch or side
  effect when the value is less than one.
- **P1 — complete denial-path coverage:** added one focused test per approved
  denial condition: `empty_publication_range`,
  `range_object_unresolvable`, `range_object_type_unexpected`,
  `candidate_parentage_invalid`, `candidate_not_single_commit_ahead`,
  `index_changed_during_publication`, and `remote_ref_rewrite_prohibited`.
  Each asserts the exact `OperationDenied.code` and that no later mutating
  command (push) occurs.
- **Blob-ceiling tests:** CLI omission denial, invalid (zero) value denial
  before fetch, and updated `_publish_kwargs` default so every existing
  invocation supplies an explicit ceiling.
- **P3 — lifecycle applicability:** `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is
  carried forward in the report linkage (advisory; no execution blocker).

`commands.py` remains declared in the cohort but was not modified (permitted
by the proposal: "it need not change unless the fresh GO identifies a concrete
command boundary requirement"; no such requirement arose).

## Specification Links

- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision is required. The approved proposal (v007) carries
forward the active project authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE`;
no AUQ was required.

## Prior Deliberations

- `bridge/gtkb-wi5840-git-lifecycle-publication-operation-007.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5840-git-lifecycle-publication-operation-008.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_git_lifecycle_publication.py -q --tb=short` → 25 passed. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | All 7 denial-path tests assert exact code + no push; index-change and rename guards tested behaviorally. |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` | Fail-closed sequencing proven per condition (denial before mutating step). |
| `GOV-WORK-TREE-HYGIENE-001` | Only 3 in-scope targets modified; `commands.py` unchanged (permitted). |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | `candidate_parentage_invalid` + `candidate_not_single_commit_ahead` tests cover ancestry/ref identity. |
| Ruff lint | `python -m ruff check` on the 4 cohort targets → "All checks passed!". |
| Ruff format | `python -m ruff format --check` on the 4 cohort targets → all formatted. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | GO v008 latest; implementation-start packet minted for exact targets; report filed as next numbered version. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_git_lifecycle_publication.py -q --tb=short` → 25 passed.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py platform_tests/scripts/test_git_lifecycle_publication.py` → "All checks passed!".
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py platform_tests/scripts/test_git_lifecycle_publication.py` → clean (after `ruff format`).
- `python scripts/bridge_claim_cli.py claim gtkb-wi5840-git-lifecycle-publication-operation --session-id G-2026-08-03T14-58-52Z` → claim acquired.
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5840-git-lifecycle-publication-operation --session-id G-2026-08-03T14-58-52Z` → packet authorized (4 targets).

## Observed Results

- Focused suite: `25 passed in 15.14s`.
- Ruff check: `All checks passed!`.
- Ruff format: clean.
- Git status shows only the 3 in-scope modified targets:
  `__main__.py`, `service.py`, `test_git_lifecycle_publication.py`.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`
- `platform_tests/scripts/test_git_lifecycle_publication.py`

`commands.py` unchanged (declared cohort, no command boundary change required).

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: completes publication denial coverage and removes a
  hard-coded blob-threshold default in an existing governed operation.

## Acceptance Criteria Status

- Operative header cites active list-free whole-project PAUTH, project, WI,
  and exact targets → **MET**.
- 7 approved denial paths each have a direct executed test asserting exact code
  and no push → **MET**.
- `--max-blob-bytes` required at CLI; service requires positive value before
  any side effect → **MET**.
- Existing success/blob tests pass with explicit ceiling → **MET**.
- Full focused suite, Ruff lint, Ruff format pass → **MET**.
- No path beyond declared cohort changes → **MET** (only 3 targets modified;
  `commands.py` unchanged per proposal).

## Risk And Rollback

Low risk. The change removes a file-local blob-threshold default (now an
explicit required input) and adds fail-closed denial coverage for already-
existing guards. `commands.py` is untouched. Rollback is a focused revert of
the 3 modified targets; no migration, schema, or state transition. The
explicit `--max-blob-bytes` requirement may expose undocumented callers, but
all in-scope test invocations now supply it. Bridge history remains append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
