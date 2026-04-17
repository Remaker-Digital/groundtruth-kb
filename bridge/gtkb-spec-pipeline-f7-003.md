# F7: Session Health Dashboard — REVISED

**Feature:** F7 — Session Health Dashboard
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 4 conditions from NO-GO bridge/gtkb-spec-pipeline-f7-002.md

---

## Changes From v1

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. F1/F3/F4 dependencies underdeclared | Phased: Phase A snapshots only existing `get_lifecycle_metrics()` and `get_summary()`. Phase B adds F3 quality distribution and F4 constraint coverage after those features ship. Dependencies explicitly declared. |
| 2. Existing dashboard/metrics integration | F7 extends the existing `/pipeline` dashboard and `get_lifecycle_metrics()`. The text renderer shares the same data layer. No parallel dashboard path. |
| 3. Threshold persistence undefined | Thresholds stored in the existing `environment_config` table (key='health_thresholds', JSON value). Uses existing `get_env_config()`/`insert_env_config()` API. |
| 4. Session trigger ownership | GT-KB owns: `capture_session_snapshot()` API + `gt health` CLI command + hook template `templates/hooks/session-health.py`. Downstream projects wire their session start/end to these surfaces. |

---

## Phase A: Existing Metrics Only (no F1/F3/F4 dependency)

Snapshot captures what GT-KB already computes:

```python
@dataclass
class SessionSnapshot:
    session_id: str
    timestamp: str
    metrics: dict          # From get_lifecycle_metrics()
    summary: dict          # From get_summary() — spec counts, status counts, etc.
```

**Phase B additions (after F3/F4):**
- `quality_distribution`: from F3's `get_quality_distribution()`
- `constraint_coverage`: from F4's `get_constraint_coverage()`

Phase B is backward-compatible — Phase A snapshots remain valid, Phase B adds fields.

## Existing Dashboard Integration

The existing `/pipeline` web dashboard (web/app.py:283) calls `get_lifecycle_metrics()` and `get_summary()`. F7 extends this:

1. **Snapshot storage** adds temporal dimension to the same data the web dashboard shows
2. **Delta computation** adds session-over-session comparison
3. **Text renderer** (`render_health_text()`) produces a CLI/conversation-friendly version of the same data
4. **Web dashboard enhancement** — optional: add a "trends" tab to the `/pipeline` page showing snapshot history

The data layer is shared. No duplicate computation paths.

## Threshold Persistence

Thresholds stored in the existing `environment_config` table:

```python
# Store thresholds
kdb.insert_env_config(
    key="health_thresholds",
    value=json.dumps({
        "M6_max": 0.25,      # Defect injection rate
        "M11_max": 0.01,     # Regression rate
        "M12_max": 0.15,     # Retirement rate
        "M16_min": 0.60,     # Verified with passing tests
        "M17_max": 0.50,     # Stale test ratio
        "M18_max": 0,        # Implemented without tests
    }),
    changed_by="owner",
    change_reason="Set health alert thresholds",
)

# Retrieve thresholds
config = kdb.get_env_config("health_thresholds")
thresholds = json.loads(config["value"]) if config else DEFAULT_THRESHOLDS
```

This uses existing GT-KB infrastructure — no new table needed. Thresholds are versioned (environment_config is append-only) and exportable via the standard export.

## Trigger Surfaces (GT-KB owned)

**CLI command:**
```
gt health                     # Show current health + delta from last snapshot
gt health snapshot S286       # Capture snapshot for session S286
gt health trends              # Show metric trends across recent snapshots
```

**Hook template:**
```python
# templates/hooks/session-health.py
# Projects wire this to session start/end

def on_session_start(session_id, kdb):
    """Display health dashboard at session start."""
    from groundtruth_kb.health import render_health_text, compute_delta
    delta = compute_delta(kdb)
    return render_health_text(delta)

def on_session_end(session_id, kdb):
    """Capture snapshot at session end."""
    from groundtruth_kb.health import capture_snapshot
    capture_snapshot(kdb, session_id)
```

## API Design

```python
class KnowledgeDB:
    def capture_session_snapshot(self, session_id: str) -> dict:
        """Capture current metrics as a session snapshot. Stored in session_snapshots table."""
        ...
    
    def compute_session_delta(self, current_session: str = None) -> dict:
        """Compute deltas between current state and most recent snapshot."""
        ...
    
    def get_snapshot_history(self, limit: int = 20) -> list[dict]:
        """Return recent snapshots for trend analysis."""
        ...

# Standalone module (not on KnowledgeDB class):
def render_health_text(delta: dict) -> str:
    """Format delta as text dashboard for CLI/conversation display."""
    ...

def get_alert_thresholds(kdb: KnowledgeDB) -> dict:
    """Load thresholds from env_config or return defaults."""
    ...
```

**New table:**
```sql
CREATE TABLE IF NOT EXISTS session_snapshots (
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON blob
    PRIMARY KEY (session_id)
);
```

## Test Plan (synthetic fixtures)

1. **Snapshot capture** — Insert some specs; `capture_session_snapshot("S1")`; verify snapshot stored
2. **Delta computation** — Capture S1, add specs, capture S2; `compute_session_delta("S2")`; verify deltas calculated
3. **Alert generation** — Set threshold M18_max=0; insert spec without assertion; verify alert in delta
4. **Text rendering** — Verify `render_health_text()` produces well-formed text with all sections
5. **No prior snapshot** — `compute_session_delta()` with empty snapshots table; verify graceful degradation (current state only, no deltas)
6. **Threshold persistence** — Store custom thresholds; retrieve; verify values match

## Implementation Sequence

Phase A: `session_snapshots` table, `capture_session_snapshot()`, `compute_session_delta()`, `render_health_text()`, threshold persistence via env_config, CLI `gt health`, hook template, 6 tests.
Phase B (after F3/F4): add quality distribution and constraint coverage to snapshots.

---

*Submitted by: S286-Prime*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f7-002.md*
