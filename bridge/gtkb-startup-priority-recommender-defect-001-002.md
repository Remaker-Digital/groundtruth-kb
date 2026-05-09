GO

# Loyal Opposition Review - Startup Priority Recommender Defect

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-startup-priority-recommender-defect-001-001.md`
Verdict: GO

## Claim

The proposal identifies a real startup recommendation defect and is safe to
implement within the proposed Slice 1 scope, subject to the conditions below.
The current recommender builds `top_priority_actions` from
`memory/work_list.md` ordering only, while the live bridge index records the
same three currently recommended items as latest `VERIFIED`.

## Evidence Checked

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-priority-recommender-defect-001` passed with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-priority-recommender-defect-001` passed in mandatory mode with 5 clauses evaluated, 4 `must_apply`, and 0 blocking gaps.
- `python -m groundtruth_kb secrets scan --paths bridge/gtkb-startup-priority-recommender-defect-001-001.md --json --fail-on=` returned `finding_count: 0`.
- Direct module check of `_backlog_metrics()` currently returns `GTKB-ENV-INVENTORY-001`, `GTKB-SYSTEMS-TERMINOLOGY-MAP-001`, and `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` as the top three actions.
- Live `bridge/INDEX.md` records latest `VERIFIED` statuses for `gtkb-env-inventory-001`, `gtkb-systems-terminology-map-001`, and `gtkb-resource-reference-disambiguation-001`.

## Review Answers

1. The best-effort work-item-ID to bridge `Document:` mapping is acceptable
   for Slice 1. Unmapped items must preserve current behavior and remain
   eligible for recommendation.
2. The `**Status:** VERIFIED (residual: ...)` annotation is sufficient for
   this slice as an explicit human override. A new `recommend_until` field
   would expand scope into backlog schema design and is not required here.
3. Diagnostic logging is sufficient. Do not add noisy user-visible startup
   disclosure text unless the existing startup diagnostics surface already has
   a bounded machine-readable place for the filtered IDs.

## GO Conditions

The implementation report must prove:

1. VERIFIED filtering uses only the live `bridge/INDEX.md` latest status for
   bridge state, not cached dashboard/startup report counts.
2. Work-item IDs are mapped deterministically by lowercasing and hyphenating,
   for example `GTKB-ENV-INVENTORY-001` to `gtkb-env-inventory-001`.
3. Unmapped work items remain active and eligible for `top_priority_actions`.
4. A work-list entry containing `**Status:** VERIFIED (residual: ...)`
   remains eligible despite a mapped latest `VERIFIED` bridge thread.
5. Tests are added for the stale VERIFIED filter, mapping convention,
   unmapped fallback, residual override, and live/current-tree regression.
6. The proposal's acceptance command must be corrected. The current CLI does
   not accept `--no-write`; Prime must either implement and test that flag or
   use an existing supported verification shape, such as `--json` with
   explicit scratch `--dashboard-dir` and `--history-path` under `E:\GT-KB`.
7. Targeted tests for `tests/scripts/test_session_self_initialization.py`
   pass after the implementation.
8. The release-candidate gate command named in the proposal is run, or any
   skipped lane is explicitly justified with the same command/output discipline
   used by the bridge report.

## Notes

The proposal says Slice 1 will make no `bridge/INDEX.md` changes. Treat that as
referring to production implementation files only. The normal bridge
post-implementation report and index status update are still required before
VERIFIED.
