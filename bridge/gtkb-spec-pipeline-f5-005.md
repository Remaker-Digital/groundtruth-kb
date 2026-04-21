# F5: Requirement Intake Pipeline — REVISED v3

**Revision:** Addresses 3 conditions from NO-GO bridge/gtkb-spec-pipeline-f5-004.md

---

## Changes From v2

| Condition | Resolution |
|-----------|-----------|
| 1. Deliberation source_type and outcome values invalid | Changed to use existing valid values: `source_type='owner_conversation'` and `outcome='deferred'` for pending candidates. Confirmation uses `outcome='owner_decision'`. Rejection uses `outcome='no_go'`. Candidate status tracked in structured JSON content. |
| 2. Hook replacement artifact contradictory | Decision: ADD new `intake-classifier.py` template alongside existing `spec-classifier.py`. Old hook unchanged. New projects get `intake-classifier.py` via scaffold. Existing projects opt-in by swapping hook in their settings. |
| 3. Tests must verify accepted values | Tests use exact valid values from db.py:3184-3197. |

---

## Deliberation Storage — Using Existing Allowlists

Current valid source_types (db.py:3184-3193):
`lo_review`, `proposal`, `owner_conversation`, `report`, `session_harvest`, `bridge_thread`

Current valid outcomes (db.py:3195-3197):
`go`, `no_go`, `deferred`, `owner_decision`, `informational`, `None`

**Candidate storage mapping:**

| Intake state | source_type | outcome | Notes |
|-------------|-------------|---------|-------|
| Captured (pending) | `owner_conversation` | `deferred` | Raw text + classification in JSON content |
| Confirmed (promoted to spec) | `owner_conversation` | `owner_decision` | Content updated with created spec ID |
| Rejected | `owner_conversation` | `no_go` | Content updated with rejection reason |

**Structured content field:**
```python
content = json.dumps({
    "intake_type": "requirement_candidate",  # Distinguishes from regular deliberations
    "intake_status": "pending",              # "pending", "confirmed", "rejected"
    "raw_text": raw_text,
    "classification": classification,
    "confidence": confidence,
    "proposed_title": proposed_title,
    "proposed_section": proposed_section,
    "confirmed_spec_id": None,               # Set on confirm
    "rejection_reason": None,                # Set on reject
})
```

**Listing pending candidates:**
```python
def list_pending(self) -> list[dict]:
    all_deferred = kdb.list_deliberations(
        source_type='owner_conversation',
        outcome='deferred',
    )
    return [
        d for d in all_deferred
        if d.get('content_parsed', {}).get('intake_type') == 'requirement_candidate'
        and d.get('content_parsed', {}).get('intake_status') == 'pending'
    ]
```

This uses only existing API capabilities. The `intake_type` field in content distinguishes intake candidates from regular owner_conversation deliberations.

## Hook Artifact Plan

**Existing:** `templates/hooks/spec-classifier.py` — unchanged. Continues to work for all existing projects.

**New:** `templates/hooks/intake-classifier.py` — added alongside `spec-classifier.py`. New hook calls the intake API.

**Scaffold:** New projects scaffolded with `intake-classifier.py` in their `.claude/hooks/` directory. `spec-classifier.py` available as fallback template.

**Upgrade path for existing projects:** Documented in GT-KB docs. Steps: (1) Replace `spec-classifier` with `intake-classifier` in `.claude/settings.local.json`, (2) test with `gt intake list`.

**No dual-hook conflict:** Only one classifier hook is active at a time. The hook registration determines which fires.

## Revised Test Plan (7 cases)

1. **Directive classification** — "MUST" keyword; classification=directive, confidence > 0.8
2. **Exploration classification** — "what if" phrasing; classification=exploration, confidence < 0.5
3. **Capture persistence** — Capture candidate; verify deliberation with source_type='owner_conversation', outcome='deferred', content has intake_type='requirement_candidate'
4. **Confirm flow** — Capture + confirm; verify deliberation outcome updated to 'owner_decision', spec created, content has confirmed_spec_id
5. **Reject flow** — Capture + reject; verify deliberation outcome updated to 'no_go', content has rejection_reason, no spec created
6. **List pending filters** — Create 2 intake candidates + 1 regular owner_conversation deferred deliberation; verify `list_pending()` returns only the 2 intake candidates
7. **Cross-session persistence** — Capture in session A; list in session B; verify candidate still pending

---

*Submitted by: S286-Prime*
*Revision: v3 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-004.md*
