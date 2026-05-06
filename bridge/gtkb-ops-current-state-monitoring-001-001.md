NEW

# Implementation Proposal - GTKB-OPS-CURRENT-STATE-MONITORING-001: Deterministic Operating State Surface

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Architecture and implementation proposal
**Risk tier:** Medium-high (startup/status behavior, dashboard data model, bridge/smart-poller visibility, local health probes; no production deployment)
**Backlog item:** `GTKB-OPS-CURRENT-STATE-MONITORING-001 - Deterministic gt status / dashboard / startup operating-state reporting`

---

## Background

`GTKB-OPS-CURRENT-STATE-MONITORING-001` exists because GT-KB has useful
component checks, but no single deterministic current-operating-state surface
for the owner, startup, CLI, and dashboard. Today, an agent reconstructs state
from scattered files: doctor output, dashboard runtime files, bridge state,
smart-poller dispatch state, hooks, SQLite/MemBase, ChromaDB, memory rows, and
process checks.

That repeated reconstruction should be code. The current bridge item
`bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04-001.md` is a
deliberate `NO-GO` advisory, not implementation approval. It tells Prime Builder
to file a normal proposal before changing code.

This proposal creates that review packet. It does not implement `gt status`,
dashboard schema changes, or startup changes until Loyal Opposition returns
`GO`.

## Current Evidence Snapshot

| Evidence | Source | Relevance |
|---|---|---|
| Backlog row exists and names this next step | `memory/work_list.md` row `GTKB-OPS-CURRENT-STATE-MONITORING-001` | Requires filing the normal implementation proposal before code changes |
| Advisory recommends deterministic status subsystem | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-OPERATING-STATE-MONITORING-ADVISORY-2026-05-04.md` | Defines component scope, owner constraints, command shape, dashboard tables, and startup integration |
| Bridge advisory makes the gap visible | `bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04-001.md` | Latest status `NO-GO` is Prime-actionable as a request to file the normal proposal |
| Doctor already checks smart-poller and dispatch freshness | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | Existing deterministic checks can be reused, but full doctor is too broad for owner-facing status |
| Dashboard command surface already exists | `groundtruth-kb/src/groundtruth_kb/cli.py` `dashboard` commands | The dashboard can ingest the same collector output instead of reimplementing state checks |
| Dashboard refresh service has a narrow health endpoint | `groundtruth-kb/src/groundtruth_kb/dashboard_service.py` | Current `/health` is service-local and does not report GT-KB component state |
| ChromaDB fallback behavior exists | `groundtruth-kb/src/groundtruth_kb/db.py` and deliberation/search tests | Status must distinguish semantic-index healthy/fallback/unavailable states |

## Specification Links

Cross-cutting specs required for bridge proposals:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) - `bridge/INDEX.md` is the live
  authority for this proposal. Compliance: this document is filed under
  `bridge/`, and the index entry is inserted with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) -
  implementation proposals must cite every relevant governing specification.
  Compliance: this section lists bridge, backlog, artifact-governance,
  root-boundary, startup, dashboard, smart-poller, and deterministic-services
  constraints.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) - any later
  implementation report must carry forward these links and map executed tests
  to linked requirements. Compliance: this proposal includes a
  specification-derived test plan.

Standing-backlog authority:

- `GOV-STANDING-BACKLOG-001` v2 (verified) - standing backlog is durable
  cross-session work authority. Compliance: this proposal is filed because the
  standing backlog records `GTKB-OPS-CURRENT-STATE-MONITORING-001` and directs
  Prime Builder to file this bridge proposal.
- `PB-STANDING-BACKLOG-CONTINUITY-001` (verified) - Prime Builder must not
  bypass standing backlog continuity. Compliance: this proposal preserves the
  backlog row's scope and does not substitute a different monitoring program.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (verified) - backlog items are
  selectable work authority. Compliance: this bridge proposal is the governed
  route from backlog entry to implementation.

Artifact-oriented governance:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) - concrete requirements,
  decisions, risks, procedures, and future work should be preserved as durable
  artifacts. Compliance: operating state becomes deterministic artifact output,
  not chat-only status reconstruction.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) - project memory is a
  traceable artifact graph. Compliance: every status component will link to the
  source files/probes that produced it.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) - artifacts require clear
  lifecycle states. Compliance: component state uses explicit `PASS`, `WARN`,
  `FAIL`, and `UNKNOWN` states with documented thresholds.

Role, bridge, and root-boundary rules:

- `.claude/rules/file-bridge-protocol.md` - governs proposal filing, `GO`,
  implementation reports, and `VERIFIED`.
- `.claude/rules/codex-review-gate.md` - forbids implementation changes before
  Loyal Opposition `GO` when the bridge is active.
- `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md`
  - constrain Prime Builder authority and review handoff behavior.
- `.claude/rules/loyal-opposition.md` - constrains Loyal Opposition review and
  verification behavior after this `NEW` entry is filed.
- `.claude/rules/canonical-terminology.md` - defines GT-KB, Internal Developer
  Platform, application, MemBase, bridge, Prime Builder, and Loyal Opposition
  terminology used by this proposal.
- `.claude/rules/project-root-boundary.md` - all active GT-KB files must remain
  under `E:\GT-KB`; GT-KB application files must remain under
  `E:\GT-KB\applications\`. Compliance: the status collector must not read
  `E:\Claude-Playground` or treat external/archive paths as live GT-KB state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified/specified in live
  preflight data) - application/root placement and platform/application
  isolation must be respected. Compliance: status output must identify GT-KB
  platform state separately from hosted application state and must not treat
  Agent Red as a live GT-KB artifact unless Mike explicitly declares Agent Red
  work.

Operating-state advisory context:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive AI work should move
  behind deterministic services and CLI/plumbing where possible. Compliance:
  operating state is collected by deterministic code, not LLM-authored
  inspection.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - the verified smart-poller is
  the intended opt-out automation path when functioning; the retired OS poller
  remains halted. Compliance: status distinguishes retired poller state from
  verified smart-poller freshness.
- `DELIB-1418` and `DELIB-0909` - prior bridge/smart-poller records relevant to
  notification activation, queue state, and historical NO-GO evidence.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-OPERATING-STATE-MONITORING-ADVISORY-2026-05-04.md`
  - source advisory for this backlog item.
- `bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04-001.md` -
  Prime-visible handoff advisory for this proposal.

The proposed tests derive from these linked specs as follows: bridge authority
drives index/file checks; spec-linkage drives applicability preflight and
section checks; verified-spec testing drives the implementation report's
spec-to-test mapping; standing-backlog specs drive proposal/backlog parity;
artifact-governance specs drive stable JSON and explicit component states;
root-boundary/isolation specs drive path containment and platform/application
separation; deterministic-services records drive no-LLM/no-API tests.

## Prior Deliberations

Search performed per `.claude/rules/deliberation-protocol.md`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "operating state monitoring gt status ChromaDB SQLite dashboard smart-poller startup no LLM API" --limit 10
```

Relevant results:

| Record | Relevance |
|---|---|
| `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` | Confirms verified smart-poller is the intended opt-out automation path when functioning, while retired OS poller remains halted |
| `DELIB-1418` | Prior verified bridge-poller notification activation thread; useful evidence for current smart-poller state surfaces |
| `DELIB-0909` | Prior smart-poller NO-GO/review context; relevant to bridge runtime status and historical implementation concerns |
| `DELIB-1000`, `DELIB-1001`, `DELIB-1002` | Dashboard industry-alignment review records; adjacent context for dashboard data surfaces |
| `DELIB-1083` | Startup token/premature wrap-up feedback; adjacent context for reducing startup reconstruction burden |

No deliberation found in this search rejects a deterministic operating-state
surface. The relevant records support deterministic status collection, clear
smart-poller semantics, and dashboard/startup visibility.

## Owner Decisions And Input

No new owner decision is needed to file this proposal. The advisory records the
2026-05-04 owner constraints:

- do not add an API key or use parallel API/LLM inspection for this workflow;
- use deterministic code/procedures instead of agent-authored inspection;
- expose current GT-KB operating state through CLI, dashboard, and session
  startup.

Prime Builder may choose exact command names in this proposal. The recommended
default is `gt status`.

## Goal

Create a single deterministic operating-state collector and consume it from:

- `gt status`,
- `gt status --json`,
- `gt status --startup --json`,
- generated dashboard SQLite tables and panels,
- session startup status rendering.

The collector answers: "What is GT-KB doing right now, and what components are
healthy, degraded, failed, or unknown?"

It should not answer broader release/readiness questions that belong to
`gt project doctor`.

## Proposed Implementation Scope

### Slice 1 - Collector, schema, and text renderer

Add a package module:

- `groundtruth-kb/src/groundtruth_kb/operating_state.py`

or, if the implementation grows beyond one file:

- `groundtruth-kb/src/groundtruth_kb/operating_state/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/operating_state/collector.py`
- `groundtruth-kb/src/groundtruth_kb/operating_state/models.py`
- `groundtruth-kb/src/groundtruth_kb/operating_state/render.py`

The collector returns deterministic JSON with:

- collection timestamp,
- resolved project root,
- package/version/git summary,
- component states,
- findings,
- probe durations,
- source paths read,
- any unavailable probe reason.

Component states:

```text
PASS    - component is available and fresh enough
WARN    - component is available but stale, degraded, noisy, or incomplete
FAIL    - component is unavailable, corrupt, malformed, or violates a boundary
UNKNOWN - component cannot be determined without unsafe or out-of-scope work
```

### Slice 2 - Component probes

Minimum probes:

1. Project root/config: resolved root, `groundtruth.toml`, package version, git
   branch/commit/ahead/dirty summary.
2. SQLite/MemBase: DB path, existence, read-only open, core table presence,
   `PRAGMA integrity_check`, source DB mtime, WAL/SHM age where present, and a
   placeholder for snapshot freshness after backup work lands.
3. ChromaDB: import availability, resolved `chroma_path`, directory existence,
   collection existence/count when possible, semantic smoke query when indexed
   data exists, fallback mode, and index freshness compared with `groundtruth.db`
   where determinable.
4. Bridge queue: parse live `bridge/INDEX.md`, report latest actionable counts
   by role, latest terminal/non-terminal counts, malformed entries, and missing
   file references.
5. Smart-poller: dispatch-state freshness, audit-event freshness, duplicate
   runner/lock indicators, notification freshness, pending counts by recipient,
   and known classification-noise indicators.
6. Dashboard runtime: dashboard DB mtime, refresh service `/health`, Grafana
   PID liveness, optional localhost Grafana health, and dashboard data freshness.
7. Hooks/rules/startup: required hook registrations, durable operating role,
   startup report freshness, pending owner-action count, and status-generation
   failure state.

### Slice 3 - CLI surface

Extend `groundtruth-kb/src/groundtruth_kb/cli.py` with:

```text
gt status
gt status --json
gt status --startup
gt status --startup --json
gt status --component bridge
gt status --component dashboard
gt status --component db
gt status --component chroma
```

`gt status --startup` must be compact and owner-facing. It should not run long
tests, mutate state, or require network access except localhost dashboard health
probes. If a probe cannot run safely, the status is `UNKNOWN` or `WARN`, with
the reason included.

Exit-code recommendation:

- `0` when all included components are `PASS` or expected `UNKNOWN`;
- `1` when any included component is `WARN`;
- `2` when any included component is `FAIL`;
- `3` when the status collector itself crashes or cannot produce a schema-valid
  report.

### Slice 4 - Dashboard ingestion

Update dashboard refresh so it ingests the same collector output, not a separate
dashboard-only implementation.

Recommended generated SQLite tables:

```text
operating_state_snapshots
operating_state_components
operating_state_findings
```

Recommended dashboard panels:

- Operating State by Component
- Bridge and Smart-Poller
- MemBase and ChromaDB
- Dashboard Runtime
- Startup Readiness

The dashboard must show data freshness and the collector timestamp so stale
dashboard data cannot look like current status.

### Slice 5 - Session startup integration

Update startup instructions/procedure so fresh-session startup displays
deterministic status output from:

```text
gt status --startup --json
```

or an equivalent stable function call if the CLI is unavailable during local
startup. The rule should tell the harness to render the status command output,
not manually reconstruct component state from scattered files.

If the status command fails, that failure is itself the startup operating-state
result and should be shown plainly.

### Out Of Scope

- No LLM/API calls or additional API keys.
- No production deployment or external service provisioning.
- No retired OS poller restoration.
- No broad doctor replacement.
- No formal artifact mutation beyond the bridge proposal/report lifecycle.
- No Agent Red repository mutation or Agent Red live-state probing unless Mike
  explicitly declares Agent Red work.
- No long-running tests from `gt status --startup`.

## Acceptance Criteria

1. `gt status --startup --json` produces schema-valid status output in a clean
   fixture project without reading outside the project root.
2. The status collector has no LLM/API dependency and introduces no new API key
   requirement.
3. CLI text and JSON output are deterministic and tested.
4. ChromaDB healthy/fallback/unavailable/empty states are distinguishable.
5. SQLite healthy/corrupt/stale-or-unknown-snapshot states are distinguishable.
6. Dashboard running/stale/stopped states are distinguishable.
7. Smart-poller fresh/stale/noisy/stopped states are distinguishable.
8. Bridge queue counts distinguish Prime-actionable `GO`/`NO-GO` from Loyal
   Opposition-actionable `NEW`/`REVISED`.
9. Startup consumes command output rather than agent reconstruction.
10. Dashboard tables and panels are populated from the same collector output.
11. Root-boundary tests prove the collector does not treat archive or external
    locations as live GT-KB state.

## Specification-Derived Test Plan

| Test ID | Requirement source | Verification |
|---|---|---|
| `T-bridge-index` | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` latest entry is `NEW` for this proposal, and the named file exists |
| `T-preflight` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ops-current-state-monitoring-001` passes before implementation |
| `T-spec-test-map` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps every linked spec to executed tests |
| `T-no-llm` | Advisory owner constraint; `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Tests/import checks prove no LLM/API client dependency and no new API key requirement |
| `T-schema` | Artifact-governance specs | Fixture tests validate stable JSON schema and component finding shape |
| `T-cli` | Existing `gt` CLI surface | `CliRunner` tests cover `gt status`, `--json`, `--startup`, component filters, and exit codes |
| `T-db` | MemBase/SQLite probe requirement | Fixture tests cover healthy DB, missing DB, malformed/corrupt DB, WAL/SHM age reporting |
| `T-chroma` | ChromaDB probe requirement | Tests cover import unavailable, path missing, empty collection, fallback, and healthy semantic index where dependency is present |
| `T-bridge-roles` | File-bridge protocol | Fixture index tests prove role-actionable counts by latest status: Prime `GO`/`NO-GO`, Loyal Opposition `NEW`/`REVISED` |
| `T-smart-poller` | `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` | Fixture state tests cover fresh/stale/stopped/noisy smart-poller status without restoring retired OS poller |
| `T-dashboard` | Dashboard ingestion scope | Dashboard refresh tests prove operating-state tables are populated from collector output |
| `T-startup` | Startup integration scope | Startup/report tests prove startup displays deterministic status output and no longer requires manual state reconstruction |
| `T-root-boundary` | `.claude/rules/project-root-boundary.md`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Collector fixture tests reject reads from `E:\Claude-Playground` and keep live paths under `E:\GT-KB` |

Suggested command set for the first implementation report:

```powershell
cd groundtruth-kb
python -m pytest tests/test_operating_state.py tests/test_cli.py tests/test_dashboard.py tests/test_doctor_smart_poller.py -q --tb=short
python -m ruff check src tests
python -m ruff format --check src tests
```

The exact test file names may change during implementation, but the report must
map back to the test IDs above.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `gt status` becomes another broad doctor report | Owner-facing status stays noisy and slow | Keep status compact; reserve broad readiness checks for `gt project doctor` |
| Dashboard reimplements different logic | CLI/dashboard disagree | Make dashboard ingest collector output only |
| Startup still reconstructs status manually | Token burden and inconsistent answers remain | Startup instructions must call/render deterministic status output |
| ChromaDB fallback looks healthy | Semantic search degradation remains hidden | Explicitly distinguish unavailable, fallback, empty, stale, and healthy states |
| Smart-poller fresh/noisy ambiguity persists | Prime queue state remains confusing | Report both freshness and classification-noise indicators |
| Status reads archive or external project state | Violates root-boundary contract | Path containment tests and explicit source-path reporting |
| Live probes make startup slow or flaky | Startup becomes less usable | Keep startup probes bounded and local; long checks remain out of scope |

## Recommended Review Questions

1. Is `gt status` the correct command name, or should this be under
   `gt project status` to avoid ambiguity with general shell status?
2. Does the component list cover the owner-facing startup/status need without
   becoming a broad doctor replacement?
3. Are `PASS`/`WARN`/`FAIL`/`UNKNOWN` sufficient, or should component state use
   the same `ALLOW`/`WARN`/`ASK`/`DENY` vocabulary as the AUQ policy gate only
   for action-gating surfaces?
4. Should dashboard ingestion be in the first implementation slice, or should
   Loyal Opposition narrow first `GO` to collector + CLI + tests?

## Prime Builder Recommendation

Proceed with collector + schema + CLI + dashboard ingestion + startup rendering
after Loyal Opposition `GO`.

If Loyal Opposition considers that too broad, the fallback should be a narrower
first implementation slice for collector + CLI + tests, followed by a separate
dashboard/startup bridge. The important constraint is that all surfaces consume
one deterministic collector rather than each reconstructing operating state.

