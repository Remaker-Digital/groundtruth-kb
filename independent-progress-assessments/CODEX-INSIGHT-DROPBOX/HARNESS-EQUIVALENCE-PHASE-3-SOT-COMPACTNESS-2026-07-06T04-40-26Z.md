# Harness Equivalence Phase 3 SoT Compactness Audit

Generated: `2026-07-06T04-40-26Z`
Bridge: `gtkb-wi4966-cli-compactness-sot-size-controls`
Project: `PROJECT-HARNESS-EQUIVALENCE-PHASE-3`
Work Item: `WI-4966`
Project Authorization: `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4966-BATCH-C-20260705`

This read-only audit classifies large source-of-truth read surfaces by routine compactness. It preserves existing compact-query coverage as coverage, not as new work.

## Summary

| Status | Count |
| --- | ---: |
| `covered` | 4 |
| `covered_by_existing_work` | 3 |
| `gap` | 2 |

## Surface Matrix

| Surface | SoT class | Status | Routine route | Archival/full route | Coverage refs | Follow-on disposition |
| --- | --- | --- | --- | --- | --- | --- |
| MemBase backlog rollup | MemBase work_items/projects | `covered` | `groundtruth-kb/.venv/Scripts/gt.exe backlog status --json` | - | GOV-STANDING-BACKLOG-001 | No new work; keep scanner-backed annotations opt-in. |
| Project authorization / PAUTH detail | MemBase project_authorizations | `gap` | `groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-HARNESS-EQUIVALENCE-PHASE-3 --json` | - | PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4966-BATCH-C-20260705 | Follow-on: add a compact project-authorization read route or a project-scoped PAUTH summary so implementation-start checks do not require the full project payload. |
| Deliberation Archive targeted search | Deliberation Archive | `covered_by_existing_work` | `groundtruth-kb/.venv/Scripts/gt.exe deliberations search "compact query modes" --limit 5 --json` | - | DELIB-202665119, DELIB-202665127 | No new work; keep --limit mandatory in routine DA examples and reports. |
| Bridge current thread summary | Bridge numbered file chain | `covered_by_existing_work` | `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi4966-cli-compactness-sot-size-controls --json --compact` | `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi4966-cli-compactness-sot-size-controls --json` | WI-4947, DELIB-202665119, bridge/gtkb-envelope-sharding-compact-query-modes-002.md | Already covered by WI-4947 compact query work; no duplicate implementation. |
| Bridge role-actionable scan | Dispatcher/TAFE bridge state plus numbered files | `covered_by_existing_work` | `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json` | - | WI-4947, DELIB-202665119, bridge/gtkb-envelope-sharding-compact-query-modes-002.md | Already covered by WI-4947 compact query work; no duplicate implementation. |
| Dispatcher health and selection status | Dispatcher daemon state | `gap` | `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json` | - | DCL-SESSION-STARTUP-TOKEN-BUDGET-001 | Follow-on: add --compact or --startup to gt bridge dispatch status, preserving full JSON behind the existing archival route. |
| Transcript/session inventory | Harness-local transcript metadata | `covered` | `groundtruth-kb/.venv/Scripts/gt.exe session envelope show --harness-name codex` | `groundtruth-kb/.venv/Scripts/python.exe scripts/wrap_capture_transcript.py --session-id <id>` | WI-4946, DELIB-202665127, scripts/wrap_capture_transcript.py | No new work; keep transcript content out of routine startup/session surfaces. |
| Advisory router scan output | LO advisory dropbox and bridge ADVISORY threads | `covered` | `groundtruth-kb/.venv/Scripts/python.exe scripts/advisory_backlog_router.py --dry-run --source both --compact` | `groundtruth-kb/.venv/Scripts/python.exe scripts/advisory_backlog_router.py --dry-run --source both` | scripts/advisory_backlog_router.py | No new work for this slice; keep --compact in routine advisory-router guidance. |
| Session/activity envelope sharding taxonomy | Harness equivalence envelope config | `covered` | `groundtruth-kb/.venv/Scripts/gt.exe benchmarks activity-envelope-load --json` | - | WI-4946, DELIB-202665127 | No new work; taxonomy baseline already covers payload class separation. |

## Gaps

### Project authorization / PAUTH detail

- Surface id: `membase-project-authorization`
- Routine route: `groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-HARNESS-EQUIVALENCE-PHASE-3 --json`
- Expected default: Routine authorization checks need a compact PAUTH summary by project/work item.
- Follow-on disposition: Follow-on: add a compact project-authorization read route or a project-scoped PAUTH summary so implementation-start checks do not require the full project payload.
- Governing specs: GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-SESSION-STARTUP-TOKEN-BUDGET-001

### Dispatcher health and selection status

- Surface id: `dispatcher-status`
- Routine route: `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json`
- Expected default: Routine dispatcher reads need a compact status route separating health rollup from raw config detail.
- Follow-on disposition: Follow-on: add --compact or --startup to gt bridge dispatch status, preserving full JSON behind the existing archival route.
- Governing specs: SPEC-INTAKE-46594e, DCL-SESSION-STARTUP-TOKEN-BUDGET-001

## Existing Coverage / No Duplicate Work

- `deliberation-archive-targeted-search` is covered by DELIB-202665119, DELIB-202665127; disposition: No new work; keep --limit mandatory in routine DA examples and reports.
- `bridge-current-thread` is covered by WI-4947, DELIB-202665119, bridge/gtkb-envelope-sharding-compact-query-modes-002.md; disposition: Already covered by WI-4947 compact query work; no duplicate implementation.
- `bridge-role-scan` is covered by WI-4947, DELIB-202665119, bridge/gtkb-envelope-sharding-compact-query-modes-002.md; disposition: Already covered by WI-4947 compact query work; no duplicate implementation.

## Citation Correction

`DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` is not used as evidence in this report. Envelope-sharding compactness context is cited through `DELIB-202665119` and `DELIB-202665127`.

## Verification Notes

- Registry validation requires unique surface ids, governing specs, compact signals for compact-flag routes, and follow-on dispositions for every gap.
- Gap rows are report-backed evidence only; this helper does not mutate MemBase, bridge state, dispatcher state, or source-of-truth data.
