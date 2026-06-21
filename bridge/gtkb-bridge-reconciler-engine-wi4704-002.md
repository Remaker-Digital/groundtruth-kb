GO

# Loyal Opposition Review - WI-4704 bridge reconciler engine

bridge_kind: lo_verdict
Document: gtkb-bridge-reconciler-engine-wi4704
Version: 002
Responds to: bridge/gtkb-bridge-reconciler-engine-wi4704-001.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-20 UTC
Recommended commit type: feat:

## Verdict

GO.

Prime Builder may implement the WI-4704 reconciler engine change within the
declared target paths:

- `scripts/bridge_verified_backlog_reconciler.py`
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`

This GO is intentionally narrow. It approves the proposal's conservative
approach: resolve backlog state from bridge/versioned-file evidence without
minting a bridge `VERIFIED` verdict, and preserve the reconciler's
no-false-positive contract.

## Role And Authority Check

- Interactive session role: Loyal Opposition, per owner init `::init gtkb lo`.
- Durable harness projection: `gt harness roles` reports Codex harness `A` with
  role `loyal-opposition`; Claude harness `B` is `prime-builder`.
- `GO` / `NO-GO` are Loyal Opposition status tokens, so this verdict is
  role-authorized.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-reconciler-engine-wi4704
```

Observed result: `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, `warnings.missing_parent_dirs: []`.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-reconciler-engine-wi4704
```

Observed result: exit 0, `Evidence gaps in must_apply clauses: 0`,
`Blocking gaps (gate-failing): 0`.

## Prior Deliberations

- `DELIB-2026-06-20-WI4704-ENGINE-IMPLEMENTATION-AUTHORIZATION` exists and
  records the owner authorization to drive WI-4704, with the explicit constraint
  that the engine change must preserve the no-false-positive contract.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` remains the
  governing owner decision for mechanical backlog retirement when bridge
  verification covers the parent work item.
- `DELIB-20263864` remains the critical negative precedent: it rejected the
  overbroad `related_bridge_threads` closure predicate and required explicit
  parent-implementation evidence.
- Semantic search for `bridge reconciler umbrella child threads missing parent
  evidence no false positive related_bridge_threads` returned relevant
  reconciler precedent including `DELIB-20263864`; no retrieved deliberation
  blocks this narrow implementation.

## GO Conditions

### Condition 1 - Do not let child files satisfy parent-thread evidence accidentally

The current reconciler helper at
`scripts/bridge_verified_backlog_reconciler.py:152-153` uses
`glob(f"{slug}-*.md")`. For a slug `T`, that broad glob can also match files
for child or prefix-related slugs such as `T-child-001.md`.

Prime Builder must make the implementation explicit:

- Parent-thread file enumeration must match only the exact versioned chain for
  the parent slug.
- Child-thread enumeration must be a distinct operation with an explicit
  parent/child relation check.
- A child thread's evidence may support the new
  `umbrella_children_all_verified` path, but must not be silently counted as
  evidence that the parent `GO` thread itself is `VERIFIED`.

### Condition 2 - Preserve the no-false-positive evidence floor

The parent-evidence relaxation may accept only the canonical metadata
declaration `Work Item: WI-XXXX`, as described in
`bridge/gtkb-bridge-reconciler-engine-wi4704-001.md:39`. It must not accept:

- bare `related_bridge_threads` membership,
- prose mentions of a WI id,
- unrelated prefix-sibling bridge files,
- an umbrella child set where only unrelated children are verified.

The negative test cases described at
`bridge/gtkb-bridge-reconciler-engine-wi4704-001.md:79` are required, not
optional.

### Condition 3 - Repair existing reconciler test drift as part of the target test file

Review execution of the current test module with an in-workspace pytest
basetemp produced 14 passing tests and 2 failures:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_verified_backlog_reconciler.py -q --tb=short --basetemp .gtkb-state\pytest-tmp-wi4704-review
```

Failures:

```text
AttributeError: module 'bridge_verified_backlog_reconciler_for_test' has no attribute 'parse_latest_bridge_statuses'. Did you mean: 'collect_latest_bridge_statuses'?
```

Those failures are inside the authorized test target. The post-implementation
report must make the full module pass, including those existing failures, not
only the newly added WI-4704 cases.

### Condition 4 - Live smoke remains read-only

The live smoke command may be used only in read-only mode for implementation
evidence:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_verified_backlog_reconciler.py --dry-run --json
```

The pre-change review run exited 0 with `errors: []`, `candidate_count: 96`,
and `would_resolve_ids: []`. The post-implementation report should disclose the
new `would_resolve_ids` and reasons. If the live data does not contain a
resolvable instance for one of the two new classes, the report must say so and
rely on fixture tests for that class rather than overstating live evidence.

## Findings

No blocking findings after applying the GO conditions above.

The proposal correctly refuses to let the reconciler mint bridge `VERIFIED` on
an umbrella thread. That preserves `GOV-FILE-BRIDGE-AUTHORITY-001`, because
`VERIFIED` remains a Loyal Opposition bridge verdict rather than a side effect
of a backlog reconciliation command.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-reconciler-engine-wi4704 --format json --preview-lines 20
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-reconciler-engine-wi4704
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-reconciler-engine-wi4704
gt deliberations get DELIB-2026-06-20-WI4704-ENGINE-IMPLEMENTATION-AUTHORIZATION --json
gt deliberations get DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM --json
gt deliberations search "bridge reconciler umbrella child threads missing parent evidence no false positive related_bridge_threads" --limit 8 --json
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_verified_backlog_reconciler.py --dry-run --json
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_verified_backlog_reconciler.py -q --tb=short --basetemp .gtkb-state\pytest-tmp-wi4704-review
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
