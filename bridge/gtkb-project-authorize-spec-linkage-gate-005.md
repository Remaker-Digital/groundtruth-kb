REVISED

# Implementation Proposal - Project Authorize Spec-Linkage Gate - REVISED-2 (WI-3312)

bridge_kind: implementation_proposal
Document: gtkb-project-authorize-spec-linkage-gate
Version: 005
Responds to: bridge/gtkb-project-authorize-spec-linkage-gate-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3312

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_cli_projects.py", "groundtruth.db"]

This REVISED-2 addresses the NO-GO at `bridge/gtkb-project-authorize-spec-linkage-gate-004.md`:

- **F1 (P1/blocking)** - the REVISED-1 allowed-type set `{governance, requirement, architecture_decision, design_constraint, protected_behavior}` excluded live `SPEC-*` rows stored under other `type` values, creating a false-negative class -> **closed** by removing the type allowlist entirely. Linkage is now a table-membership + lifecycle-status predicate: any cited ID that resolves via `db.get_spec()` to a `specifications`-table row with an approved lifecycle status counts.

IP-2 (typed exception + CLI wiring) and IP-4 (no spec promotion) carry forward from REVISED-1 unchanged. IP-1 and IP-3 (tests) are revised below.

## Why the Type Allowlist Is Removed (live evidence)

Probed the live `specifications` table (latest version per id, `groundtruth.db`):

- `type` has **12 distinct values**: `requirement` (2031), `specification` (55), `governance` (50), `design_constraint` (48), `architecture_decision` (22), `protected_behavior` (21), `documentation` (15), `functional` (3), `feature` (2), `architecture` (2), `protocol` (1), `implemented` (1 - a data-entry artifact).
- The REVISED-1 allowlist would have rejected 79 live rows, including all 55 `type='specification'` rows - the most literal `SPEC-*` anchor the source spec names.
- `status` has exactly 4 distinct values: `implemented` (1588), `verified` (340), `retired` (202), `specified` (121). There is no `wont_fix` status in the table; the REVISED-1 reference to `wont_fix` was phantom.

The source spec `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` enumerates the *ID-prefix* shorthands `GOV/SPEC/REQ/ADR/DCL/PB`. All spec subtypes share the single `specifications` table; the `type` column is heterogeneous descriptive metadata (12 values, one of them a data bug) and is not a reliable authorization discriminator. An *inclusion* allowlist of `type` values guarantees recurring false negatives as new types appear. Per `GOV-08` (KB is truth), the correct linkage predicate is: the ID resolves via `db.get_spec()` (table membership) AND its lifecycle `status` is approved/current. This eliminates the entire false-negative class the NO-GO identified rather than chasing a drifting allowlist.

## Claim

`KnowledgeDB.insert_project_authorization()` must reject any version that reaches `status="active"` unless at least one `included_spec_ids` value resolves via `db.get_spec(id)` to a current MemBase row whose lifecycle `status` is in the approved/current set `{specified, implemented, verified}` (NOT `retired`). No `type` filter is applied: membership in the `specifications` table is itself the "is a specification" predicate. The `ProjectLifecycleService.authorize_project()` wrapper raises a typed `ProjectAuthorizationSpecLinkageError` that `cli.py` converts to `click.UsageError` with the spec citation.

## In-Root Placement Evidence

All 6 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - source spec; v1 specified 2026-05-14.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope contract.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved.
- `GOV-08` - KB is truth (governs the "resolves via db.get_spec()" semantics).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3312 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-project-authorize-spec-linkage-gate-002.md` - first NO-GO (closed by REVISED-1).
- `bridge/gtkb-project-authorize-spec-linkage-gate-004.md` - second NO-GO (closed by this REVISED-2).

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch (AskUserQuestion).
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision required; this REVISED-2 is a mechanical scope correction.

## Requirement Sufficiency

Existing requirements sufficient. The source spec's phrase "at least one approved specification" is satisfied by table-membership + approved lifecycle status; "approved" is a lifecycle qualifier, not a `type` qualifier. The REVISED-2 implements that literal reading.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3312); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (resolution + lifecycle gate) + IP-2 (typed exception + CLI wiring) + IP-3 (tests) + IP-4 (no promotion) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-project-authorize-spec-linkage-gate-005.md`; `REVISED:` line prepended. Prior lines (`-004` NO-GO, `-003` REVISED-1, `-002` NO-GO, `-001` NEW) preserved.

## Proposed Scope

### IP-1: Resolution + lifecycle-status validation in insert_project_authorization()

In `groundtruth-kb/src/groundtruth_kb/db.py`, extend `insert_project_authorization()` (or its validation helper):

```python
APPROVED_SPEC_LIFECYCLE = {"specified", "implemented", "verified"}

def _validate_active_authorization_specs(self, included_spec_ids: list[str] | None) -> None:
    """Raise ValueError if no cited spec resolves to an approved/current row."""
    if not included_spec_ids:
        raise ValueError(
            "Project authorization status='active' requires at least one "
            "included_spec_id (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001)."
        )
    resolved_count = 0
    invalid_ids: list[tuple[str, str]] = []
    for spec_id in included_spec_ids:
        row = self.get_spec(spec_id)
        if row is None:
            invalid_ids.append((spec_id, "not-found"))
            continue
        if row["status"] not in APPROVED_SPEC_LIFECYCLE:
            invalid_ids.append((spec_id, f"status={row['status']}-not-approved"))
            continue
        resolved_count += 1
    if resolved_count == 0:
        details = "; ".join(f"{sid}: {reason}" for sid, reason in invalid_ids)
        raise ValueError(
            "Project authorization status='active' requires at least one "
            "approved specification "
            "(GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001). "
            f"Cited spec IDs failed resolution: {details}"
        )
```

Called from `insert_project_authorization()` when `status == "active"`. Non-active statuses (draft, revoked, completed) skip. There is no `type` allowlist: any row returned by `db.get_spec()` is a `specifications`-table member and therefore a specification.

### IP-2: Typed exception propagation + CLI wiring

Unchanged from REVISED-1. In `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, add `ProjectAuthorizationSpecLinkageError(ProjectLifecycleError)`; `ProjectLifecycleService.authorize_project()` re-raises the IP-1 `ValueError` as the typed exception. In `groundtruth-kb/src/groundtruth_kb/cli.py`, `projects_authorize` catches it and converts to `click.UsageError` citing `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`. Other `ProjectLifecycleError` shapes propagate unchanged.

### IP-3: Tests (existing surfaces)

Tests in `groundtruth-kb/tests/test_db.py` (DB layer) and `groundtruth-kb/tests/test_cli_projects.py` (CLI). If `test_cli_projects.py` does not exist on current main, the implementation creates it AS NEW (explicitly scoped via `target_paths`).

### IP-4: No spec promotion at proposal-filing time

`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` stays at `specified`. Promotion only on VERIFIED.

## Specification-Derived Verification Plan

Tests in `groundtruth-kb/tests/test_db.py` and `groundtruth-kb/tests/test_cli_projects.py`:

| Scenario | Test |
|---|---|
| Active + None spec ids -> blocked | `test_authorize_active_with_no_spec_ids_raises` |
| Active + empty list -> blocked | `test_authorize_active_with_empty_spec_list_raises` |
| Active + unknown spec id -> blocked (F1 negative) | `test_authorize_active_with_unknown_spec_id_raises` |
| Active + retired spec -> blocked (F1 negative) | `test_authorize_active_with_retired_spec_raises` |
| Active + one approved `type='specification'` SPEC-* row -> passes (F1 false-negative class closed) | `test_authorize_active_with_specification_type_spec_succeeds` |
| Active + one approved `type='requirement'` REQ-* row -> passes | `test_authorize_active_with_requirement_type_spec_succeeds` |
| Active + one approved `type='governance'` GOV-* row -> passes | `test_authorize_active_with_governance_type_spec_succeeds` |
| Active + mix of valid + invalid -> passes (one valid sufficient) | `test_authorize_active_with_valid_and_invalid_mix_succeeds` |
| Draft authorization with no specs -> passes | `test_authorize_draft_with_no_specs_succeeds` |
| Status-only mutation (active->revoked) without spec change -> passes | `test_authorize_status_only_change_no_spec_validation` |
| CLI: ValueError -> ProjectAuthorizationSpecLinkageError -> click.UsageError | `test_cli_authorize_missing_specs_emits_usage_error` |
| CLI: error message cites GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 | `test_cli_error_cites_source_spec` |
| Grandfathering: pre-existing active+no-spec rows unchanged on read | `test_existing_grandfathered_row_read_unchanged` |

The three positive type-coverage tests (`specification`, `requirement`, `governance`) directly prove the F1 false-negative class is closed across heterogeneous `type` values. Run:

```text
python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py -v
```

## Acceptance Criteria

- IP-1, IP-2 landed; 13 tests PASS.
- IP-1 applies NO `type` filter; the three positive type-coverage tests pass.
- IP-4: `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains `specified` at proposal time.
- No regression in existing `test_db.py` or `test_cli_projects.py` suites.
- Both preflights PASS.

## Risks / Rollback

- Risk: legacy `included_spec_ids` data with stale/retired IDs may exist. Mitigation: grandfathering - only NEW insertions or version bumps to `status='active'` are gated; existing rows unchanged on read.
- Risk: dropping the `type` filter lets a `type='documentation'` row count as linkage. Mitigation: accepted by design - a `documentation`-type row under change control in the `specifications` table is still a governed specification; the false-negative risk of a type allowlist is the greater harm per the NO-GO. Lifecycle status remains gated.
- Risk: `ProjectLifecycleError` catch in CLI may swallow legitimate non-linkage errors. Mitigation: typed sub-exception ensures only spec-linkage cases hit the new translation.
- Rollback: revert `_validate_active_authorization_specs` (single-function scope) + typed exception class + CLI translation.

## Recommended Commit Type

`feat` - new semantic governance gate; ~50 LOC DB + ~20 LOC lifecycle + ~10 LOC CLI + ~150 LOC tests.
