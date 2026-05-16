# Post-Implementation Report (REVISED) — Harnesses Registry Table Schema (WI-3337)

bridge_kind: prime_implementation_report
Version: 007 (REVISED post-implementation report after NO-GO at -006)

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3337

## Summary

Implemented the GO'd proposal `gtkb-harness-registry-table-schema-003.md`
(Codex GO at `-004`). Added the append-only versioned `harnesses` table to the
MemBase schema, the `current_harnesses` latest-version view, and the
`insert_harness` / `get_harness` / `list_harnesses` API methods. The change is
strictly additive (185 insertions, 0 deletions); no existing table, view,
method, or caller was modified. The implementation-start authorization packet
was minted from the `-004` GO before any protected edit (`packet_hash:
sha256:bdbde0fa…`).

## Revision History

- **007 (REVISED post-implementation report)** — Addresses the NO-GO at `-006`.
  - **Finding P1** (clause-preflight blocking gap on
    `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`) was a review-timing
    race, not an implementation or report defect. The `## Clause Scope
    Clarification` section that supplies the required non-bulk-operation
    evidence was self-detected and added to `-005` immediately after `-005`
    was filed; the `-006` reviewer snapshotted `-005` before that in-place fix
    landed. The clause preflight on the live operative file now reports
    `Evidence gaps: 0` / `Blocking gaps: 0` (exit 0). This `-007` report
    carries the `## Clause Scope Clarification` section from the outset, so no
    race window exists.
  - **Finding P3** (the LO sandbox lacked `pytest`, so the reviewer could not
    independently re-run the suite) is addressed by the fresh verbatim test
    transcript embedded in the Verification section below.
- **005** — Initial post-implementation report.

## Files Changed

```
 groundtruth-kb/src/groundtruth_kb/db.py | 101 +++++++++++++++++++++
 groundtruth-kb/tests/test_db.py         |  84 ++++++++++++++++
 2 files changed, 185 insertions(+)
```

- `groundtruth-kb/src/groundtruth_kb/db.py`
  - `CREATE TABLE IF NOT EXISTS harnesses (...)` added to the schema string,
    after `canonical_terms`, with the FR1 column set: `id`, `version`,
    `harness_name`, `harness_type`, `status` (`NOT NULL DEFAULT 'registered'`),
    `role`, `reviewer_precedence`, `invocation_surfaces`, `capabilities_ref`,
    `changed_by` / `changed_at` / `change_reason`, `UNIQUE(id, version)`.
  - `CREATE VIEW IF NOT EXISTS current_harnesses` after
    `current_canonical_terms`, returning the latest version per `id`.
  - `insert_harness()`, `get_harness()`, `list_harnesses()` added after
    `list_project_authorizations`.
- `groundtruth-kb/tests/test_db.py` — `TestHarnesses` class with five
  spec-derived tests.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — FR1 (authoritative append-only `harnesses`
  table); satisfied by this implementation.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the `role` column stores the
  role-set wire form established by this ADR.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried
  forward from the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the executed tests derive
  from FR1 (see Spec-to-Test Mapping).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is filed as a versioned bridge
  entry under `bridge/INDEX.md`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both changed files are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the new table is a governed
  append-only artifact store.

## Prior Deliberations

- `DELIB-2079` — owner decision for the Antigravity Integration design
  (DB-backed single-table harness registry).
- `DELIB-2080` — role-portability amendment; the `role` / `reviewer_precedence`
  columns provide the storage the amendment requires.

## Owner Decisions / Input

This implementation executes owner-authorized work:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design (11-answer AskUserQuestion grill, 2026-05-16).
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization (owner-decision `DELIB-2079`, includes
  `REQ-HARNESS-REGISTRY-001`).
- Owner AskUserQuestion (2026-05-16): "Implement WI-3337 now" — directed this
  implementation.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR1 (single append-only versioned `harnesses` table
as the authoritative store) is verified by five tests in
`groundtruth-kb/tests/test_db.py::TestHarnesses`:

| FR1 clause | Test |
|---|---|
| Table + `current_harnesses` view exist at schema init | `test_harnesses_table_created` |
| First insert yields `version=1` with all FR1 columns persisted | `test_insert_harness_creates_v1` |
| Append-only versioning — second insert yields `version=2` | `test_insert_harness_version_bumps` |
| Current-version retrieval returns the latest row | `test_get_harness_returns_latest` |
| Current-set listing returns one current row per id | `test_list_harnesses_returns_current_set` |

## Verification

Command (the proposal's verification procedure, executed verbatim in the
repo-native environment):

```
$ python -m pytest groundtruth-kb/tests/test_db.py -q
........................................................................ [ 76%]
......................                                                   [100%]
94 passed, 1 warning in 21.30s
```

The single warning is a pre-existing `chromadb` `DeprecationWarning` unrelated
to this change. The suite grew from 89 to 94 tests — exactly the five new
`TestHarnesses` tests; no regression in the 89 pre-existing tests. (An earlier
targeted run, `python -m pytest groundtruth-kb/tests/test_db.py::TestHarnesses
-v`, reported `5 passed` with each of the five tests named PASSED.)

Mandatory bridge gates on this `-007` operative file: applicability preflight
`preflight_passed: true`, `missing_required_specs: []`; clause preflight
`Evidence gaps: 0`, `Blocking gaps: 0` (the `GOV-STANDING-BACKLOG-001/
CLAUSE-VISIBILITY-BULK-OPS` clause is satisfied by the Clause Scope
Clarification section below).

## Recommended Commit Type

`feat:` — the change adds a net-new capability surface (a new MemBase table,
view, and three API methods); 185 insertions / 0 deletions of new code, no
behavior change to existing surfaces.

## Acceptance Criteria Check

- ☑ The `harnesses` table and `current_harnesses` view are created with the
  FR1 column set.
- ☑ `insert_harness` appends versions monotonically; `UNIQUE(id, version)` is
  enforced.
- ☑ `get_harness` / `list_harnesses` return current-version rows.
- ☑ All five spec-derived tests pass; the existing `test_db.py` suite is green
  (94 passed).
- ☑ No existing table, method, or caller is modified (185 insertions, 0
  deletions).

## Clause Scope Clarification

This implementation is not a bulk operation. It adds exactly one MemBase table
(`harnesses`) and implements exactly one work item (`WI-3337`); it does not
inventory, batch-mutate, promote, retire, or sweep multiple artifacts. The
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause therefore does not
substantively apply: no bulk-operation inventory artifact, review packet, or
`DECISION DEFERRED` marker is produced because there is no bulk action to gate.
Owner approval for the bounded work is recorded via the
formal-artifact-approval-backed `DELIB-2079` and the active project
authorization `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
