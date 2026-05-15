REVISED

# Implementation Proposal - Project Authorize Spec-Linkage Gate - REVISED-1 (WI-3312)

bridge_kind: implementation_proposal
Document: gtkb-project-authorize-spec-linkage-gate
Version: 003
Responds to: bridge/gtkb-project-authorize-spec-linkage-gate-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3312

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_cli_projects.py", "groundtruth.db"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-project-authorize-spec-linkage-gate-002.md`:

- **F1 (P1/blocking)** — Non-empty spec-id list is not the same as "linked approved specifications"; `["NOT-A-SPEC"]` would pass → **closed** by upgrading IP-1 from list-cardinality check to a per-ID semantic resolution: each cited spec must resolve via `db.get_spec()` to a current MemBase row of allowed subtype with approved/current lifecycle state.
- **F2 (P2)** — Live CLI error path raises `ProjectLifecycleError` (from service layer), not the raw `ValueError` → **closed** by adding `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` to target_paths and specifying a typed `ProjectAuthorizationSpecLinkageError` propagation path.

## Claim

`KnowledgeDB.insert_project_authorization()` must reject any version that reaches `status="active"` unless at least one `included_spec_ids` value resolves via `db.get_spec(id)` to a row whose `type` is in `{governance, requirement, architecture_decision, design_constraint, protected_behavior}` AND whose `status` is in the approved/current lifecycle set `{specified, implemented, verified}` (NOT `retired` or `wont_fix`). The `ProjectLifecycleService.authorize_project()` wrapper raises a typed `ProjectAuthorizationSpecLinkageError` that `cli.py` converts to `click.UsageError` with the spec citation.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

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
- `bridge/gtkb-project-authorize-spec-linkage-gate-002.md` - NO-GO under remediation.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch.
- 2026-05-15 UTC, S350+: owner directive "Please proceed with WI-3312 + WI-3313".

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. The source spec's phrase "at least one approved specification" plainly requires resolution to a real spec row of allowed subtype, not just list-cardinality. The REVISED-1 implements that literal reading.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (semantic spec resolution) + IP-2 (typed exception + CLI wiring) + IP-3 (tests) + IP-4 (no spec promotion at proposal time) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-project-authorize-spec-linkage-gate-003.md`; `REVISED:` line prepended; prior `NO-GO: -002` and `NEW: -001` preserved.

## Proposed Scope

### IP-1: Per-ID semantic spec resolution in insert_project_authorization()

In `groundtruth-kb/src/groundtruth_kb/db.py`, extend `insert_project_authorization()` (or its validation helper):

```python
APPROVED_SPEC_TYPES = {
    "governance", "requirement", "architecture_decision",
    "design_constraint", "protected_behavior",
}
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
        if row["type"] not in APPROVED_SPEC_TYPES:
            invalid_ids.append((spec_id, f"type={row['type']}-not-allowed"))
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

Called from `insert_project_authorization()` when `status == "active"`. Initial-version path subject to same check; non-active statuses (draft, revoked, completed) skip.

### IP-2: Typed exception propagation + CLI wiring

In `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`:

```python
class ProjectAuthorizationSpecLinkageError(ProjectLifecycleError):
    """Raised when authorize_project() encounters a spec-linkage validation gap."""
    def __init__(self, message: str, *, invalid_ids: list[tuple[str, str]] | None = None) -> None:
        super().__init__(message)
        self.invalid_ids = invalid_ids or []
```

In `ProjectLifecycleService.authorize_project()`, catch the new ValueError shape from IP-1 (string prefix `"Project authorization status='active' requires"`) and re-raise as `ProjectAuthorizationSpecLinkageError` carrying the invalid-ID detail.

In `groundtruth-kb/src/groundtruth_kb/cli.py`, the `projects_authorize` command catches `ProjectAuthorizationSpecLinkageError` and converts to `click.UsageError` with the citation: `"GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001: ..."`. All other `ProjectLifecycleError` shapes propagate unchanged.

### IP-3: Tests (existing surfaces; not new files)

Use the existing test files (per F2 NO-GO guidance — not new surfaces):
- `groundtruth-kb/tests/test_db.py` (DB-layer validation)
- `groundtruth-kb/tests/test_cli_projects.py` (CLI surface)

If `test_cli_projects.py` does not exist on current main, the implementation creates it AS NEW (explicitly scoped, not as regression of an existing file).

### IP-4: No spec promotion at proposal-filing time

`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` stays at `specified`. **Promotion only on VERIFIED**, when IP-1 + IP-2 + IP-3 tests all PASS.

## Specification-Derived Verification Plan

Tests in `groundtruth-kb/tests/test_db.py` and `groundtruth-kb/tests/test_cli_projects.py`:

| Scenario | Test |
|---|---|
| Active + None spec ids → blocked | `test_authorize_active_with_no_spec_ids_raises` |
| Active + empty list → blocked | `test_authorize_active_with_empty_spec_list_raises` |
| Active + unknown spec id → blocked (F1 negative) | `test_authorize_active_with_unknown_spec_id_raises` |
| Active + retired spec → blocked (F1 negative) | `test_authorize_active_with_retired_spec_raises` |
| Active + wont_fix spec → blocked (F1 negative) | `test_authorize_active_with_wont_fix_spec_raises` |
| Active + non-allowed-type (e.g., test artifact ID) → blocked | `test_authorize_active_with_non_spec_type_raises` |
| Active + one approved spec → passes | `test_authorize_active_with_one_approved_spec_succeeds` |
| Active + mix of valid + invalid → passes (one valid sufficient) | `test_authorize_active_with_valid_and_invalid_mix_succeeds` |
| Draft authorization with no specs → passes | `test_authorize_draft_with_no_specs_succeeds` |
| Status-only mutation (active→revoked) without spec change → passes | `test_authorize_status_only_change_no_spec_validation` |
| CLI: ValueError → ProjectAuthorizationSpecLinkageError → click.UsageError | `test_cli_authorize_missing_specs_emits_usage_error` |
| CLI: error message cites GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 | `test_cli_error_cites_source_spec` |
| Grandfathering: pre-existing active+no-spec rows unchanged on read | `test_existing_grandfathered_row_read_unchanged` |

Run: `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py -v` per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Acceptance Criteria

- IP-1, IP-2 landed; 13 tests PASS.
- IP-4: `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains `specified` at proposal time.
- No regression in existing `test_db.py` or `test_cli_projects.py` suites.
- Both preflights PASS.

## Risks / Rollback

- Risk: legacy `included_spec_ids` data with stale/retired IDs may exist. Mitigation: grandfathering — only NEW insertions or version bumps to `status='active'` are gated.
- Risk: `ProjectLifecycleError` catch in CLI may swallow legitimate non-linkage errors. Mitigation: typed sub-exception ensures only spec-linkage cases hit the new translation.
- Rollback: revert `_validate_active_authorization_specs` (single-function scope) + typed exception class + CLI translation.

## Recommended Commit Type

`feat` - new semantic governance gate; ~60 LOC DB + ~20 LOC lifecycle + ~10 LOC CLI + ~150 LOC tests.
