REVISED

# Implementation Proposal - GTKB-OPS-CURRENT-STATE-MONITORING-001: Deterministic Operating State Surface

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-06
**Type:** Architecture and implementation proposal
**Risk tier:** Medium-high (startup/status behavior, dashboard data model, bridge/smart-poller visibility, local health probes; no production deployment)
**Backlog item:** `GTKB-OPS-CURRENT-STATE-MONITORING-001 - Deterministic gt status / dashboard / startup operating-state reporting`
**Supersedes:** `bridge/gtkb-ops-current-state-monitoring-001-001.md`
**Addresses:** Loyal Opposition `-002` F1, owner-decision section heading not recognized by the gate.

---

## NO-GO Acknowledgement

Loyal Opposition `-002` correctly found that `-001` used `Owner Decisions And
Input`, while the bridge compliance contract recognizes `Owner Decisions` or
`Owner Decisions / Input`. This revision uses the exact required heading and
enumerates the owner constraints relied on by this proposal.

## Background

GT-KB has useful component checks, but no single deterministic
current-operating-state surface for the owner, startup, CLI, and dashboard.
Today, an agent reconstructs state from scattered files: doctor output,
dashboard runtime files, bridge state, smart-poller dispatch state, hooks,
SQLite/MemBase, ChromaDB, memory rows, and process checks.

That repeated reconstruction should be code. The current bridge item
`bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04-001.md` is a
deliberate `NO-GO` advisory, not implementation approval. This proposal creates
the normal review packet and does not implement status, dashboard, or startup
changes until Loyal Opposition returns `GO`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md` with latest status `REVISED`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation
  proposals must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation report
  must carry forward these links and map executed tests to requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - the standing backlog records
  this work item and directs Prime Builder to file the bridge proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - operating state must become
  deterministic artifact output with explicit lifecycle states.
- `.claude/rules/file-bridge-protocol.md` and
  `.claude/rules/codex-review-gate.md` - no implementation before `GO`.
- `.claude/rules/project-root-boundary.md` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - status output must keep GT-KB
  platform state separate from hosted application state and must not treat
  `E:\Claude-Playground` or Agent Red as live GT-KB state.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repeated AI inspection should
  move behind deterministic service/CLI behavior.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - the verified smart-poller is
  the intended opt-out automation path when functioning; the retired OS poller
  remains halted.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-OPERATING-STATE-MONITORING-ADVISORY-2026-05-04.md`
  and `bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04-001.md` -
  source advisory and Prime-visible handoff for this work.

## Prior Deliberations

Search/reference check carried forward from `-001`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "operating state monitoring gt status ChromaDB SQLite dashboard smart-poller startup no LLM API" --limit 10
```

Relevant records include `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`,
`DELIB-1418`, `DELIB-0909`, dashboard alignment records `DELIB-1000` through
`DELIB-1002`, and `DELIB-1083`. No cited deliberation rejects a deterministic
operating-state surface.

## Owner Decisions / Input

- **2026-05-04 owner constraint:** do not add an API key or use parallel
  API/LLM inspection for this workflow.
- **2026-05-04 owner constraint:** use deterministic code and procedures rather
  than agent-authored inspection.
- **2026-05-04 owner desired surface:** expose current GT-KB operating state
  through CLI, dashboard, and session startup.
- **Source evidence:** the constraints are recorded in
  `bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04-001.md` and the
  source advisory report named above.
- **Current owner input needed:** none. The exact command name can be reviewed
  through this proposal; the recommended default remains `gt status`.

## Goal

Create one deterministic operating-state collector consumed by:

- `gt status`,
- `gt status --json`,
- `gt status --startup --json`,
- generated dashboard SQLite tables and panels,
- session startup status rendering.

The collector answers: "What is GT-KB doing right now, and what components are
healthy, degraded, failed, or unknown?" It does not replace broad release or
installation readiness checks in `gt project doctor`.

## Proposed Implementation Scope

1. Add `groundtruth_kb.operating_state` with a stable JSON schema and text
   renderer.
2. Report component states as `PASS`, `WARN`, `FAIL`, or `UNKNOWN`, with source
   paths, probe duration, and unavailable-probe reasons.
3. Probe project root/config, SQLite/MemBase, ChromaDB, bridge queue,
   smart-poller, dashboard runtime, hooks/rules, and startup readiness.
4. Add CLI support for `gt status`, `gt status --json`, `gt status --startup`,
   `gt status --startup --json`, and component filters.
5. Update dashboard refresh to ingest the same collector output rather than a
   separate dashboard-only implementation.
6. Update startup procedure so fresh-session startup renders deterministic
   status output instead of reconstructing state manually.

## Acceptance Criteria

1. `gt status --startup --json` produces schema-valid status output in a clean
   fixture project without reading outside the GT-KB root.
2. The collector has no LLM/API dependency and introduces no API key.
3. CLI text and JSON output are deterministic and tested.
4. ChromaDB, SQLite/MemBase, dashboard, smart-poller, and bridge states have
   distinguishable healthy/degraded/failed/unknown cases.
5. Bridge queue counts distinguish Prime-actionable `GO`/`NO-GO` from Loyal
   Opposition-actionable `NEW`/`REVISED`.
6. Dashboard tables and panels are populated from the same collector output.
7. Startup consumes command output rather than agent reconstruction.
8. Root-boundary tests prove the collector does not treat archive or external
   locations as live GT-KB state.

## Specification-Derived Test Plan

| Test ID | Requirement source | Verification |
|---|---|---|
| `T-bridge-index` | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` latest entry is `REVISED` for this proposal and the named file exists |
| `T-preflight` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ops-current-state-monitoring-001` passes |
| `T-spec-test-map` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps every linked spec to executed tests |
| `T-no-llm` | Owner constraint and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Tests/import checks prove no LLM/API dependency and no new API key |
| `T-cli` | Existing `gt` CLI surface | CLI tests cover text, JSON, startup mode, component filters, and exit codes |
| `T-db-chroma` | Component-state requirements | Fixture tests cover healthy, missing, corrupt/unavailable, fallback, and stale cases |
| `T-bridge-roles` | File-bridge protocol | Fixture index tests prove latest-status role-actionable counts |
| `T-dashboard-startup` | Dashboard/startup scope | Tests prove dashboard and startup consume collector output |
| `T-root-boundary` | Root-boundary and isolation specs | Fixture tests reject archive/external live-state reads |

Suggested command set for the first implementation report:

```powershell
cd groundtruth-kb
python -m pytest tests/test_operating_state.py tests/test_cli.py tests/test_dashboard.py tests/test_doctor_smart_poller.py -q --tb=short
python -m ruff check src tests
python -m ruff format --check src tests
```

## Out Of Scope

- No LLM/API calls or additional API keys.
- No production deployment or external service provisioning.
- No retired OS poller restoration.
- No broad doctor replacement.
- No formal artifact mutation beyond the bridge proposal/report lifecycle.
- No Agent Red repository mutation or Agent Red live-state probing unless Mike
  explicitly declares Agent Red work.
- No long-running tests from `gt status --startup`.

## Prime Builder Recommendation

Proceed after Loyal Opposition `GO`. If the combined collector, CLI, dashboard,
and startup scope is too broad for one implementation, the fallback should be a
first implementation slice for collector plus CLI, followed by a separate
dashboard/startup bridge. The shared constraint is one deterministic collector.
