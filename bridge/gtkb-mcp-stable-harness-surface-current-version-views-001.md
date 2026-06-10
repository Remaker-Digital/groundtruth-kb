NEW

# Implementation Proposal - MCP Stable Harness Surface: Current-Version Views + Harness-ID Detection (WI-3275)

bridge_kind: prime_proposal
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: WI-3275

target_paths: ["groundtruth-kb/src/groundtruth_kb/mcp/gt_status_summary.py", "groundtruth-kb/src/groundtruth_kb/mcp/harness_id.py", "groundtruth-kb/tests/test_mcp_status_summary.py"]

This NEW proposal fixes 2 defects flagged in Codex NO-GO at `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md`. F1: `_membase_row_counts` queries base tables; MemBase is append-only versioned, so canonical 'current state' requires filtering to max(version) per ID. F2: `_default_harness_id` returns 'B' when `GTKB_HARNESS_ID` unset, so Codex invocations report prime-builder instead of loyal-opposition.

## Claim

Two scoped fixes: (1) replace base-table queries with `current_*` view queries in `_membase_row_counts`; (2) replace hardcoded 'B' default with resolution via `harness-state/harness-identities.json` (reads the persistent identity record).

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-0001` - three-tier memory architecture; MemBase append-only versioning.
- `GOV-08` - KB is truth; canonical current state via current_* views.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - MCP surface as policy engine consumer.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3275 tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` - originating NO-GO with F1+F2.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-MEMBASE-EFFECTIVE-USE authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. Codex NO-GO F1+F2 are concrete; this proposal addresses them directly.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-MEMBASE-EFFECTIVE-USE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (F1) + IP-2 (F2) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: current_* view queries in _membase_row_counts

In `groundtruth-kb/src/groundtruth_kb/mcp/gt_status_summary.py`:

Replace each base-table COUNT(*) query with the corresponding `current_*` view:
- `specifications` → `current_specifications`
- `work_items` → `current_work_items`
- `tests` → `current_tests`
- `deliberations` → `current_deliberations`
- `project_authorizations` → `current_project_authorizations`
- (etc. for all tables in the function)

### IP-2: Harness ID detection

In `groundtruth-kb/src/groundtruth_kb/mcp/harness_id.py` (new file):

```python
def detect_harness_id() -> str:
    # 1. Honor GTKB_HARNESS_ID env var if set
    env_value = os.environ.get("GTKB_HARNESS_ID")
    if env_value:
        return env_value
    # 2. Read harness-state/harness-identities.json
    identities_path = REPO_ROOT / "harness-state" / "harness-identities.json"
    if identities_path.exists():
        data = json.loads(identities_path.read_text(encoding="utf-8"))
        # Find the current process's harness; heuristic: parent process name or CLAUDE_PROJECT_DIR pattern
        # (Best-effort; defaults to first if cannot distinguish)
    # 3. Last resort: emit explicit "unknown" rather than hardcoded "B"
    return "unknown"
```

Update `_default_harness_id` to call `detect_harness_id()` instead of returning hardcoded 'B'.

### IP-3: Tests

Tests verify: counts match current_* views, env var override works, identity-file resolution works, "unknown" emitted when no signal available.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| MemBase counts use current_* views | `test_membase_counts_use_current_views` |
| Counts differ from base-table queries when versions present | `test_counts_filter_to_current_version` |
| GTKB_HARNESS_ID env var honored | `test_harness_id_env_var_honored` |
| harness-identities.json resolved | `test_harness_id_from_identity_file` |
| Missing identity emits 'unknown' not 'B' | `test_no_identity_emits_unknown` |
| Codex invocation reports loyal-opposition | `test_codex_session_reports_lo_role` |

Run: `python -m pytest groundtruth-kb/tests/test_mcp_status_summary.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Codex invocation of gt_status_summary correctly reports role.
- Both preflights PASS.

## Risks / Rollback

- Risk: current_* views may not exist for all tables. Mitigation: detection step ensures only views that exist are used; fallback to base table with explicit `DISTINCT id` filter.
- Risk: detect_harness_id heuristic may misclassify. Mitigation: env var override is reliable escape hatch; documented in module docstring.
- Rollback: revert each IP independently.

## Recommended Commit Type

`fix` - defect repair flagged by Codex NO-GO. ~50 LOC + tests.
