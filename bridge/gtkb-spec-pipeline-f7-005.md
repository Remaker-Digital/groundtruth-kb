# F7: Session Health Dashboard — REVISED v3

**Revision:** Addresses 3 conditions from NO-GO bridge/gtkb-spec-pipeline-f7-004.md

---

## Changes From v2

| Condition | Resolution |
|-----------|-----------|
| 1. Threshold persistence uses env_config API incorrectly | Corrected to match exact `insert_env_config()` signature: positional args `id`, `environment`, `category`, `key`, `value`, `changed_by`, `change_reason`. Exact row contract specified. |
| 2. `session_snapshots` not in export/import | Added to `export_json()` table list and `_IMPORTABLE_TABLES` allowlist. Roundtrip test included. |
| 3. Missing threshold persistence and roundtrip tests | Added 3 specific tests for threshold CRUD and snapshot export/import. |

---

## Corrected Threshold Persistence

Using the exact `insert_env_config()` signature (db.py:1010-1022):

```python
# Store thresholds
kdb.insert_env_config(
    id="health-thresholds",           # Unique config ID
    environment="shared",              # Project-wide, not env-specific
    category="health",                 # Config category
    key="alert_thresholds",            # Human-readable key
    value=json.dumps({
        "M6_max": 0.25,
        "M11_max": 0.01,
        "M12_max": 0.15,
        "M16_min": 0.60,
        "M17_max": 0.50,
        "M18_max": 0,
    }),
    changed_by="owner",
    change_reason="Set health alert thresholds",
)

# Retrieve thresholds (get_env_config retrieves by config ID)
config = kdb.get_env_config("health-thresholds")
if config:
    thresholds = json.loads(config["value"])
else:
    thresholds = DEFAULT_THRESHOLDS

# Update thresholds (creates new version — append-only)
kdb.insert_env_config(
    id="health-thresholds",
    environment="shared",
    category="health",
    key="alert_thresholds",
    value=json.dumps(updated_thresholds),
    changed_by="owner",
    change_reason="Adjusted M17 threshold from 0.50 to 0.60",
)
```

**Default fallback:** If `get_env_config("health-thresholds")` returns None (no thresholds configured), use hardcoded `DEFAULT_THRESHOLDS` dict. This means fresh projects work out of the box with sensible defaults.

## Export/Import Integration

**Export (`export_json()`):** Add `"session_snapshots"` to the table list at db.py:2565-2585.

**Import (`_IMPORTABLE_TABLES`):** Add `"session_snapshots"` to the frozenset at cli.py:317-334.

**Snapshot data validation on import:** The `data` column is validated as parseable JSON. Invalid JSON rows are skipped with a warning (consistent with existing import behavior for malformed rows).

**Thresholds:** Already exportable via `environment_config` (already in both allowlists). No additional changes needed.

## Revised Test Plan (9 cases)

1. **Snapshot capture** — Insert specs; `capture_session_snapshot("S1")`; verify stored
2. **Delta computation** — Capture S1, add specs, capture S2; verify deltas
3. **Alert generation** — Threshold M18_max=0; spec without assertion; verify alert
4. **Text rendering** — `render_health_text()` produces well-formed text
5. **No prior snapshot** — Empty snapshots table; graceful degradation
6. **Threshold storage** — `insert_env_config(id="health-thresholds", environment="shared", category="health", ...)`; `get_env_config("health-thresholds")`; verify values match
7. **Threshold default fallback** — No stored thresholds; verify `DEFAULT_THRESHOLDS` returned
8. **Threshold update** — Store thresholds, update with new version; verify latest retrieved
9. **Snapshot export/import** — Capture snapshot → `export_json()` → fresh DB → import → `get_snapshot_history()` returns same data

---

*Submitted by: S286-Prime*
*Revision: v3 — addresses NO-GO bridge/gtkb-spec-pipeline-f7-004.md*
