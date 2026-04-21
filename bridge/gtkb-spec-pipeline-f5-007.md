# F5: Requirement Intake Pipeline — REVISED v4

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f5-006.md

---

## Changes From v3

| Condition | Resolution |
|-----------|-----------|
| 1. `list_pending()` filters on `content_parsed` but `_row_to_dict()` does not parse `content` | Intake API parses `json.loads(d["content"])` internally before filtering. Does not require GT-KB core changes. Added explicit roundtrip test. |

---

## Deliberation Content Parsing Strategy

**Problem:** `_row_to_dict()` (db.py:3732-3763) parses a fixed allowlist of JSON fields (`assertions`, `results`, `tags`, `context`, etc.) but `content` is NOT in that list. So `d.get('content_parsed')` returns `None` for all deliberation rows.

**Chosen approach:** The intake module parses `content` internally via `json.loads(d["content"])`. This avoids modifying GT-KB core (`_row_to_dict`), keeps the deliberation content field opaque at the DB layer, and confines structured-content semantics to the intake feature.

**Rationale for NOT adding `content` to `_row_to_dict()`:**
- `content` is used by all deliberation types, most storing free-text, not JSON
- Parsing all `content` fields as JSON would silently produce `content_parsed: None` for non-JSON rows (no exception, just missing key) — confusing
- The intake feature is the only consumer of structured content; it should own the parsing

## Revised `list_pending()` Implementation

```python
import json

def list_pending(self) -> list[dict]:
    """List pending requirement intake candidates.
    
    Parses deliberation content as JSON internally since _row_to_dict()
    does not include 'content' in its JSON parsing allowlist (db.py:3736-3749).
    """
    all_deferred = self.kdb.list_deliberations(
        source_type='owner_conversation',
        outcome='deferred',
    )
    candidates = []
    for d in all_deferred:
        # Parse content as JSON — intake candidates store structured JSON,
        # while regular deliberations may store free text
        raw_content = d.get('content', '')
        if not raw_content or not isinstance(raw_content, str):
            continue
        try:
            parsed = json.loads(raw_content)
        except (json.JSONDecodeError, TypeError):
            continue  # Not JSON — not an intake candidate
        
        if (
            isinstance(parsed, dict)
            and parsed.get('intake_type') == 'requirement_candidate'
            and parsed.get('intake_status') == 'pending'
        ):
            d['_content_parsed'] = parsed  # Attach for caller convenience
            candidates.append(d)
    
    return candidates
```

**Key behaviors:**
- `json.loads()` is called on `d["content"]` (raw string), not `d.get("content_parsed")`
- Non-JSON content is silently skipped (it's a regular deliberation, not an intake candidate)
- `_content_parsed` is attached to the row dict for caller convenience but is NOT part of the DB layer contract
- No GT-KB core changes required

## Storage Contract (unchanged from v3)

| Intake state | source_type | outcome | content (JSON) |
|-------------|-------------|---------|----------------|
| Captured (pending) | `owner_conversation` | `deferred` | `{"intake_type": "requirement_candidate", "intake_status": "pending", ...}` |
| Confirmed (promoted) | `owner_conversation` | `owner_decision` | `{"intake_type": "requirement_candidate", "intake_status": "confirmed", "confirmed_spec_id": "SPEC-NNNN", ...}` |
| Rejected | `owner_conversation` | `no_go` | `{"intake_type": "requirement_candidate", "intake_status": "rejected", "rejection_reason": "...", ...}` |

## Hook Artifact Plan (unchanged from v3)

- Existing `spec-classifier.py` unchanged
- New `intake-classifier.py` added alongside
- Scaffold uses new hook; existing projects opt-in

## Revised Test Plan (8 cases)

1. **Directive classification** — "MUST" keyword; classification=directive, confidence > 0.8
2. **Exploration classification** — "what if" phrasing; classification=exploration, confidence < 0.5
3. **Capture persistence** — Capture candidate; verify deliberation with source_type='owner_conversation', outcome='deferred', content is valid JSON with intake_type='requirement_candidate'
4. **Confirm flow** — Capture + confirm; verify outcome updated to 'owner_decision', spec created, content has confirmed_spec_id
5. **Reject flow** — Capture + reject; verify outcome updated to 'no_go', content has rejection_reason
6. **List pending with JSON parsing** — Create 2 intake candidates + 1 regular owner_conversation deliberation with free-text content + 1 owner_conversation with malformed JSON content; verify `list_pending()` returns exactly the 2 intake candidates (proves `json.loads` parsing works on actual row dicts from `list_deliberations()`)
7. **Cross-session persistence** — Capture in session A; list in session B; verify candidate still pending
8. **List pending roundtrip** — Insert a deliberation with `insert_deliberation()`, call `list_deliberations()`, pass the row to `list_pending()`'s filtering logic; verify the candidate appears. This test fails if `content` is not a parseable string in the returned row dict.

---

*Submitted by: S287-Prime*
*Revision: v4 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-006.md*
