# F5: Requirement Intake Pipeline — REVISED

**Feature:** F5 — Requirement Intake Pipeline
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 4 conditions from NO-GO bridge/gtkb-spec-pipeline-f5-002.md

---

## Changes From v1

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. Dependencies incomplete (F1-F4 all NO-GO) | Phased: Phase A is standalone (capture + confirm using existing schema). Phase B adds F1 enrichment, F2 impact preview, F4 constraint check. Dependencies explicitly listed. |
| 2. In-memory buffer conflicts with traceability | Candidates persisted in GT-KB as deliberation records with `source_type='requirement_candidate'` and `outcome='pending'`. Confirmation promotes to spec; rejection updates outcome to `'rejected'`. Raw text preserved in deliberation content. |
| 3. GOV-09 hook interaction undefined | Decision: F5 REPLACES the current spec-classifier hook. The hook template in GT-KB (`templates/hooks/spec-classifier.py`) is updated to call the intake pipeline API instead of emitting a static reminder. Existing hook continues to work for projects that don't upgrade. |
| 4. GT-KB vs Agent Red ownership blurred | All code lives in groundtruth-kb as library API + hook template + CLI command (`gt intake`). Agent Red adoption is a downstream step: update the hook to call the new API. No Agent Red-specific skill in this proposal. |

---

## Candidate Persistence via Deliberations

Instead of an in-memory buffer, candidates are stored as deliberation records:

```python
kdb.insert_deliberation(
    id=f"INTAKE-{session_id}-{seq}",
    source_type="requirement_candidate",
    title=proposed_title,
    summary=f"Classification: {classification} | Confidence: {confidence}",
    content=json.dumps({
        "raw_text": raw_text,
        "classification": classification,
        "confidence": confidence,
        "proposed_title": proposed_title,
        "proposed_type": proposed_type,
        "proposed_section": proposed_section,
        "context": context,
    }),
    changed_by=f"{session_id}-intake",
    change_reason="Requirement candidate captured from conversation",
    outcome="pending",
    session_id=session_id,
)
```

**On confirm:** `kdb.insert_spec(...)` + update deliberation outcome to `'confirmed'` + link deliberation to new spec.
**On reject:** Update deliberation outcome to `'rejected'` with reason. Raw text preserved for audit.
**On defer:** Outcome stays `'pending'`. Retrievable next session via `kdb.list_deliberations(source_type='requirement_candidate', outcome='pending')`.

This solves both persistence and traceability: every requirement has a traceable path from raw owner text through classification to either spec creation or rejection.

## GOV-09 Hook Replacement

The current `templates/hooks/spec-classifier.py` uses regex patterns (line 30) and emits a static reminder (line 69). F5 replaces this with a hook that calls the intake API:

```python
# New templates/hooks/intake-classifier.py
# Replaces spec-classifier.py

def on_user_prompt(prompt_text, session_id, kdb):
    """Classify prompt for requirement candidates and persist."""
    candidates = intake.classify(prompt_text)
    for candidate in candidates:
        intake.capture(kdb, session_id, candidate)
    
    if candidates:
        return f"Captured {len(candidates)} requirement candidate(s). Use `gt intake list` to review."
    return None  # No reminder if no candidates detected
```

**Backward compatibility:** Projects using the old `spec-classifier.py` are unaffected — the old hook still exists. Projects that upgrade get the new `intake-classifier.py`. Migration docs describe the switch.

## Phased Design

### Phase A: Standalone (no F1/F2/F3/F4 dependency)

- Capture: classify prompt text, persist as deliberation
- Confirm: promote deliberation to spec using current schema
- Reject: update deliberation outcome
- List: `gt intake list` shows pending candidates
- Hook template: `intake-classifier.py`

### Phase B: Enhanced (after F1/F2/F4 GO)

- F1 fields populated on confirm (authority, constraints, provisional_until)
- F2 impact preview shown during confirm step
- F4 constraint check: applicable constraints shown for each candidate

## API Design (GT-KB library)

```python
class RequirementIntake:
    """Requirement capture and confirmation pipeline."""
    
    def __init__(self, kdb: KnowledgeDB, session_id: str):
        self.kdb = kdb
        self.session_id = session_id
    
    def classify(self, text: str, context: str = None) -> list[dict]:
        """Classify text for requirement candidates. Returns candidate dicts."""
        ...
    
    def capture(self, candidate: dict) -> str:
        """Persist candidate as deliberation. Returns deliberation ID."""
        ...
    
    def list_pending(self) -> list[dict]:
        """Return all pending candidates (current + prior sessions)."""
        ...
    
    def confirm(self, deliberation_id: str, *, modifications: dict = None) -> dict:
        """Promote candidate to spec. Returns created spec."""
        ...
    
    def reject(self, deliberation_id: str, reason: str = None) -> None:
        """Reject candidate. Updates deliberation outcome."""
        ...
    
    def suggest_ordering(self, candidates: list[dict]) -> list[dict]:
        """Reorder candidates by least-disruptive introduction sequence."""
        ...
```

**CLI surface (GT-KB owned):**
```
gt intake list                    # Show pending candidates
gt intake confirm INTAKE-S286-1  # Promote to spec
gt intake reject INTAKE-S286-2   # Reject with reason
```

## Test Plan (synthetic fixtures)

1. **Directive classification** — Input with "MUST" keyword; verify classification=directive, confidence > 0.8
2. **Exploration classification** — Input with "what if"; verify classification=exploration, confidence < 0.5
3. **Persistence** — Capture candidate; verify deliberation exists with source_type='requirement_candidate'
4. **Confirm flow** — Capture + confirm; verify spec created and deliberation outcome='confirmed'
5. **Reject flow** — Capture + reject; verify deliberation outcome='rejected', no spec created
6. **Cross-session persistence** — Capture in session A, list in session B; verify candidate still pending

## Implementation Sequence

Phase A: `RequirementIntake` class, deliberation-based persistence, classify/capture/confirm/reject, hook template, CLI commands, 6 tests.
Phase B (after F1/F2/F4): enriched spec creation, impact preview, constraint check integration.

---

*Submitted by: S286-Prime*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f5-002.md*
