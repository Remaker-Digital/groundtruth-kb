# Post-Implementation Report — Harnesses Registry Table Schema (WI-3337)

bridge_kind: implementation_report
Version: 005 (post-implementation report; awaiting VERIFIED)

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3337

## Summary

Implemented the GO'd proposal `gtkb-harness-registry-table-schema-003.md`
(Codex GO at `-004`). Added the append-only versioned `harnesses` table to the
MemBase schema, the `current_harnesses` latest-version view, and the
`insert_harness` / `get_harness` / `list_harnesses` API methods. The change is
strictly additive (185 insertions, 0 deletions); no existing table, view,
method, or caller was modified.

The implementation-start authorization packet was minted from the `-004` GO
(`python scripts/implementation_authorization.py begin --bridge-id
gtkb-harness-registry-table-schema`; `packet_hash:
sha256:bdbde0fa…`) before any protected edit.

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
    `changed_by` / `changed_at` / `change_reason`, and `UNIQUE(id, version)` —
    mirroring the `project_authorizations` pattern.
  - `CREATE VIEW IF NOT EXISTS current_harnesses` added after
    `current_canonical_terms`, returning the latest version per `id`.
  - `insert_harness()` (append the next version; JSON-encodes `role` and
    `invocation_surfaces`), `get_harness()` (current row), `list_harnesses()`
    (all current rows) added after `list_project_authorizations`.
- `groundtruth-kb/tests/test_db.py`
  - `TestHarnesses` class added with five spec-derived tests.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — FR1 (authoritative append-only `harnesses`
  table); satisfied by this implementation.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the `role` column stores the
  role-set wire form established by this ADR.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried
  forward from the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the executed tests derive
  from FR1 (see Spec-to-Test Mapping below).
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

Command (the proposal's verification procedure, executed verbatim):

```
python -m pytest groundtruth-kb/tests/test_db.py -q
```

Observed result: `94 passed, 1 warning in 20.64s`. The single warning is a
pre-existing `chromadb` `DeprecationWarning` unrelated to this change. The suite
grew from 89 to 94 tests — exactly the five new `TestHarnesses` tests; no
regression in the 89 pre-existing tests.

Targeted confirmation:

```
python -m pytest groundtruth-kb/tests/test_db.py::TestHarnesses -v
```

Observed result: `5 passed in 0.90s` — `test_harnesses_table_created`,
`test_insert_harness_creates_v1`, `test_insert_harness_version_bumps`,
`test_get_harness_returns_latest`, `test_list_harnesses_returns_current_set`
all PASSED.

## Recommended Commit Type

`feat:` — the change adds a net-new capability surface (a new MemBase table,
view, and three API methods). Per the Conventional Commits discipline,
`feat:` is correct for net-new modules/capabilities; the diff is 185
insertions / 0 deletions of new code, no behavior change to existing surfaces.

## Acceptance Criteria Check

- ☑ The `harnesses` table and `current_harnesses` view are created with the
  FR1 column set.
- ☑ `insert_harness` appends versions monotonically; `UNIQUE(id, version)` is
  enforced (two inserts for one id yield versions 1 and 2).
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
