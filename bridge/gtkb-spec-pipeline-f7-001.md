# F7: Session Health Dashboard — Implementation Proposal

**Feature:** F7 — Session Health Dashboard
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** Drift detection (enables visibility into all 5 vectors)
**Dependencies:** F1 (metrics include enrichment coverage)
**Prior deliberations:** DELIB-0710 (quality ranking)

---

## Problem Statement

GT-KB computes lifecycle metrics (M2, M4, M6, M10-M12, M16-M18) but has no mechanism to:
1. **Snapshot metrics at session boundaries** — so deltas can be computed
2. **Display metrics at session start** — so the AI and owner see the current state
3. **Alert on drift** — when metrics exceed thresholds or change significantly between sessions

Without session-over-session comparison, degradation is invisible. Agent Red's M17 (stale test ratio) reached 99.4% — a number that accumulated gradually but was never surfaced as a trend. M18 (implemented without tests) reached 112 specs without triggering any alarm.

## Proposed Solution

A **session health system** with three components: snapshot capture, delta computation, and dashboard rendering.

### Component 1: Metric Snapshots

At session end, GT-KB captures a snapshot of all computable metrics plus corpus statistics:

```python
@dataclass
class SessionSnapshot:
    session_id: str
    timestamp: str
    metrics: dict              # {metric_id: {value, unit, ...}}
    corpus_stats: dict         # {total_specs, by_status, by_type, by_authority, ...}
    quality_distribution: dict # From F3: {tier: count, avg_score, ...}
    constraint_coverage: dict  # From F4: {covered, uncovered, ...}
    enrichment_coverage: dict  # From F1: {fields_populated, fields_missing, ...}
```

Stored in a new GT-KB table: `session_snapshots(session_id, timestamp, data JSON)`.

### Component 2: Delta Computation

At session start, GT-KB computes deltas between the current state and the most recent snapshot:

```python
@dataclass
class SessionDelta:
    current: SessionSnapshot
    previous: SessionSnapshot
    deltas: dict               # {metric_id: {previous, current, change, direction}}
    alerts: list[DriftAlert]   # Metrics that exceeded thresholds or changed significantly
```

### Component 3: Dashboard Rendering

A formatted text block suitable for display in the AI conversation:

```
Session S287 — Project Health
Specs: 2,108 (+3)  Tests: 11,070 (+15)  Open WIs: 2 (+2)
Verified: 15.6% (+0.2%)  Assertions: 83.9% (+0.2%)

Quality Scores (F3):  Avg 0.62 (+0.01)
  Directive:      890 specs (42.2%)
  Behavioral:     1,105 specs (52.4%)
  Architectural:  113 specs (5.4%)

Constraint Coverage (F4):  87.3% (+1.2%)
  ADR-006 (ZK): 412/445 specs covered
  DCL-002 (transport): 89/89 specs covered

Drift Alerts:
  ! M17 stale test ratio 99.4% — threshold 50% — EXCEEDS
  ! M18 implemented without tests: 112 — threshold 0 — EXCEEDS
  ~ 3 new specs without authority field — enrichment gap
```

### Alert Thresholds

| Metric | Threshold | Alert Level |
|--------|----------|-------------|
| M6 defect injection rate | >25% | Warning |
| M11 regression rate | >1% | Critical |
| M12 retirement rate | >15% | Warning |
| M16 verified with passing tests | <60% | Warning |
| M17 stale test ratio | >50% | Critical |
| M18 implemented without tests | >0 | Warning |
| Quality score average | <0.5 | Warning |
| Constraint coverage | <80% | Warning |
| Enrichment coverage | <90% | Warning |

Thresholds are configurable per project. Defaults derived from Agent Red experience.

## Counterfactual Test

**If F7 had existed from session 1:**
- M17 (stale test ratio) would have been flagged as a trend: 10% → 30% → 60% → 99.4% across sessions. The drift would have been visible at 30%, not discovered at 99.4%
- M18 (untested specs) would have been visible from the first session it exceeded 0, prompting corrective action at 10 instead of 112
- Quality score trends would have shown whether spec quality was improving or degrading over time
- Constraint coverage would have shown gaps in ZK propagation as new specs were added to constrained sections

## API Design

```python
class KnowledgeDB:
    def capture_session_snapshot(
        self,
        session_id: str,
    ) -> SessionSnapshot:
        """Capture current metrics and corpus stats as a session snapshot."""
        ...
    
    def compute_session_delta(
        self,
        session_id: str = None,  # If None, compares current state to latest snapshot
    ) -> SessionDelta:
        """Compute deltas between current state and a previous snapshot."""
        ...
    
    def render_health_dashboard(
        self,
        delta: SessionDelta = None,
    ) -> str:
        """Render a formatted text dashboard. If no delta, shows current state only."""
        ...
    
    def get_alert_thresholds(self) -> dict:
        """Return current alert thresholds."""
        ...
    
    def set_alert_thresholds(self, thresholds: dict) -> None:
        """Override default alert thresholds for this project."""
        ...
```

### New Table

```sql
CREATE TABLE IF NOT EXISTS session_snapshots (
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON blob of SessionSnapshot
    PRIMARY KEY (session_id)
);
```

## Test Plan

1. **Snapshot capture** — Capture snapshot; verify all metrics and corpus stats populated
2. **Delta computation** — Capture two snapshots with changes between; verify deltas calculated correctly
3. **Alert generation** — Set threshold, create condition that exceeds it; verify alert generated
4. **Dashboard rendering** — Verify output is well-formatted and includes all sections
5. **No previous snapshot** — Verify graceful handling when no prior snapshot exists (first session)
6. **Configurable thresholds** — Set custom thresholds; verify alerts use custom values

## Implementation Sequence

1. Create `session_snapshots` table in GT-KB schema
2. Implement `capture_session_snapshot()` using existing `get_lifecycle_metrics()` + F1/F3/F4 coverage queries
3. Implement `compute_session_delta()` with delta calculation and alert logic
4. Implement `render_health_dashboard()` text formatter
5. Implement threshold configuration (defaults + per-project overrides)
6. Write tests (6 cases above)
7. Create session-start skill/hook integration for Agent Red

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Dashboard is too verbose for routine sessions | Compact mode: show only alerts and significant deltas; full mode on demand |
| Metric computation is slow on large corpora | Cache intermediate results; session snapshots avoid recomputing historical metrics |
| Alert fatigue from too many warnings | Tiered alerts: critical (blocks), warning (shows), info (available on demand) |

## Open Questions for Codex Review

1. Should the dashboard be rendered automatically at session start, or invocable via skill/command?
2. Should snapshots be stored in GT-KB's database or in a separate file (to avoid bloating the KB)?
3. Should alert thresholds be stored in the KB (as a spec or config) or in a project configuration file?
4. Should the dashboard include recommendations (e.g., "consider adding tests for 112 untested specs") or just present data?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F7*
