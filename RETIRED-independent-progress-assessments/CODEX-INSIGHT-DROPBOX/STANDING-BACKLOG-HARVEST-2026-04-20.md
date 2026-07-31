# Standing Backlog Harvest Snapshot - 2026-04-20

## Claim

The standing backlog has been formalized and partially populated, but a full
pre-existing artifact harvest was not complete before this report. This
snapshot records the currently discovered high-signal backlog sources and
creates explicit follow-up items so the remaining reconciliation is durable.

## Evidence

- `memory/work_list.md` is the current human-readable standing backlog.
- `scripts/audit_standing_backlog_sources.py` now audits bridge, MemBase
  work-item, and release-readiness sources.
- `bridge/INDEX.md` latest-status inventory from the audit:
  - `GO`: 2
  - `NO-GO`: 4
  - `VERIFIED`: 99
- Current actionable bridge entries:
  - `GO`: `gtkb-azure-cicd-gates`
  - `GO`: `agent-red-bridge-dispatcher-deferral-enforcement`
  - `NO-GO`: `commercial-readiness-spec-1833-ready-propagation`
  - `NO-GO`: `commercial-readiness-spec-1831-startup-wiring`
  - `NO-GO`: `commercial-readiness-spec-verification`
  - `NO-GO`: `agent-red-bridge-dispatcher-deferral-enforcement-implementation`
- `groundtruth.db` work item counts include:
  - `open`: 1994
  - `new`: 14
  - `in_progress`: 4
  - `unresolved`: 8
  - `blocked`: 1
  - `specified`: 17
  - `created`: 1
  - `deferred`: 1
- `memory/release-readiness.md` still lists seven release blockers:
  credential rotation, git history purge decision, SonarCloud pass, security
  scan pass, branch provenance reconciliation, exact-candidate Python 3.12 CI,
  and commercial durability launch-scope decision.

## Risk / Impact

Without a structured harvest pass, future sessions may treat the standing
backlog as complete while live bridge statuses, MemBase work items, or
release-readiness blockers remain outside the work authority. That would
violate `GOV-STANDING-BACKLOG-001` and
`PB-STANDING-BACKLOG-CONTINUITY-001`.

## Recommended Action

Use the new `GTKB-GOV-004` through `GTKB-GOV-010` standing-backlog items as the
harvest completion path:

- reconcile MemBase work-item populations into backlog snapshots,
- reconcile live bridge GO/NO-GO entries,
- close or explicitly defer release-readiness blockers,
- split commercial readiness NO-GOs into implementable revised bridge threads,
- repair bridge dispatcher deferral enforcement,
- execute or supersede the Azure CI/CD gates GO,
- keep the audit script and tests in the release gate until an upstream
  GT-KB doctor replaces them.

## Decision Needed From Owner

None for this snapshot. Additional owner decisions may be needed by the
individual backlog items, especially credential-history purge, commercial
durability launch scope, and bridge dispatcher mute authority.
