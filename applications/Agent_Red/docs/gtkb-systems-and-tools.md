# GT-KB Systems and Tools Map

This is the human-readable companion to
`config/agent-control/system-interface-map.toml`.

The map is an index and resolver, not a replacement authority. Each row points
to the artifact, table, generated surface, or runtime capability that remains
authoritative for that system.

## First Reconciliation Case: Backlog

The current operational backlog authority is MemBase `current_work_items`.
All work items are backlog items. Projects and sub-projects are grouping
metadata over work items, not separate work authorities. `memory/work_list.md`
is a compatibility/human-readable view. In the GT-KB host after the 2026-06-15
TAFE/dispatcher cutover, retired bridge-index artifacts are not backlog
authority and not canonical dispatcher/TAFE bridge-state authority.
Dashboard/startup surfaces are summaries only.

## Compact Map

| Term | Current authority | Notes |
| --- | --- | --- |
| backlog | MemBase `current_work_items` | Unified known-work view; access with `gt backlog list` or MemBase reads. |
| work item | MemBase `current_work_items` | Individual backlog item; may be grouped by project/sub-project metadata. |
| MemBase | `groundtruth.db` | Canonical GroundTruth database. |
| Deliberation Archive | MemBase `current_deliberations` | ChromaDB is only an optional search overlay. |
| MEMORY.md | `memory/MEMORY.md` | Harness-memory operational notepad in this checkout. |
| canonical glossary | `.claude/rules/canonical-terminology.md` | Term meanings, not concrete artifact lookup. |
| operating model | `.claude/rules/operating-model.md` | Rule-cited soft authority. |
| file bridge | `.claude/rules/file-bridge-protocol.md` | Protocol; current GT-KB host queue authority is dispatcher/TAFE bridge state. |
| bridge queue | TAFE-backed bridge state | Retired bridge-index artifacts are not live queue authority. |
| smart poller | `independent-progress-assessments/bridge-automation/` | Optional helper for bridge monitoring. |
| retired OS poller | `.claude/rules/file-bridge-protocol.md` | Must not be restored. |
| dashboard | `docs/gtkb-dashboard/session-startup-report.md` | Generated summary, not authority. |
| release readiness | `memory/release-readiness.md` | Working release evidence record. |
| release gate | `scripts/release_candidate_gate.py` | Local non-deploying gate script. |
| doctor check | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | Workstation/project health check. |
| startup disclosure | `scripts/session_self_initialization.py` | Generated orientation surface. |
| session focus | `scripts/session_self_initialization.py` | Prime Builder selection/mapping surface. |
| work subject | `.claude/rules/operating-model.md` | Current active project/application scope. |
| role assignment record | `harness-state/role-assignments.json` | Durable role map. |
| harness identity record | `harness-state/harness-identities.json` | Durable harness installation IDs. |
| skill | Session skill list and `SKILL.md` files | Local instruction bundles. |
| hook | `.claude/settings.json`, `.codex/hooks.json`, `.githooks/` | Separate harness/git control surfaces. |
| plugin/app capability | Current session plugin/app tool list | Runtime capabilities exposed by the harness. |
| MCP server | Current session tool list and MCP resources | Tool/resource server, often lazy-loaded. |
| resource alias registry | `config/agent-control/project-resource-aliases.toml` | External resource identity map. |

## Operating Rule

When an owner-facing term could name multiple adjacent systems, resolve it
through the map before reading or mutating project artifacts. Use the
authoritative source named by the row, not cached dashboard/startup text.
