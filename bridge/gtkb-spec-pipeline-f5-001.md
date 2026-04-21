# F5: Requirement Intake Pipeline — Implementation Proposal

**Feature:** F5 — Requirement Intake Pipeline
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** P2 (chat misinterpretation), P3 (assumption-driven implementation)
**Dependencies:** F1 (records to enriched schema), F2 (blast radius preview during confirmation)
**Prior deliberations:** DELIB-0708 (structured interview vision), DELIB-0709 (all proposals before implementation), DELIB-0710 (completeness at right time)

---

## Problem Statement

In the current workflow, the path from owner statement to KB spec is: owner says something → AI detects spec language (GOV-09 hook) → AI writes spec → spec enters KB. This has three gaps:

1. **No distinction between exploration and commitment.** The owner may be brainstorming, asking "what if," or describing a problem — not stating a requirement. GOV-09 triggers on keywords ("must", "should", numbered criteria) regardless of intent. The owner observed that "some chat language is misinterpreted and causes dramatic changes to specifications with relatively little warning."

2. **No structured enrichment at capture time.** When a requirement enters the KB, it carries only what the AI inferred from the conversation. The AI fills in section, scope, tags, priority, and assertions using its own judgment — which is where assumption-driven implementation (P3) starts. The owner's intent is compressed into the AI's interpretation.

3. **No sequencing intelligence.** Requirements enter the KB in the order the owner mentions them, not in the order that minimizes disruption. The owner's vision (DELIB-0708): "An ideal GT-KB would have asked me questions in a structured and ordered way that would have ensured all requirements specifications were clear, valid and introduced in the least disruptive order."

## Proposed Solution

A **3-stage requirement intake pipeline** that sits between conversation and KB, providing structured capture, explicit confirmation, and intelligent sequencing.

### Stage 1: Capture

The AI identifies potential requirements from the conversation and captures them in a **session-scoped candidate buffer** — NOT in the KB.

Each candidate is a lightweight record:

```python
@dataclass
class RequirementCandidate:
    raw_text: str              # The owner's exact words
    classification: str        # 'directive', 'question', 'exploration', 'constraint', 'preference'
    confidence: float          # AI's confidence this is a real requirement (0.0-1.0)
    proposed_title: str        # AI's draft spec title
    proposed_type: str         # From F1 schema: requirement, governance, etc.
    proposed_authority: str    # From F1 schema: stated, inferred, etc.
    proposed_section: str      # Where this belongs
    context: str               # Surrounding conversation for reference
    impact_preview: dict       # From F2: blast radius if this became a spec
    timestamp: str
```

**Classification rules:**
- `directive`: Owner uses imperative language (MUST, SHALL, need, require). High confidence.
- `constraint`: Owner states a limitation or boundary. High confidence.
- `preference`: Owner expresses a preference without mandate. Medium confidence.
- `question`: Owner is asking, not telling. Low confidence — capture for reference but don't promote.
- `exploration`: Owner is thinking out loud. Low confidence — capture but flag as exploratory.

The capture stage preserves the **raw text** — the owner's exact words. This is critical: the AI's interpretation (proposed_title) is a draft, not a commitment. The raw text is the ground truth for what the owner actually said.

### Stage 2: Confirm

At natural pause points — or on demand via a `/confirm-requirements` command — the pipeline presents captured candidates to the owner:

```
Requirement candidates from this session:
                                                                    
1. [DIRECTIVE] "the widget must support WhatsApp escalation"        
   → Proposed: SPEC-NNNN "Widget WhatsApp Escalation Channel"      
   → Section: WIDGET_UI | Impact: moderate (12 related specs)      
   → Constraints: ADR-004 (canonical identity) applies             
                                                                    
2. [EXPLORATION] "what if we added SMS as a channel too?"           
   → Not promoted (classified as exploration)                       
   → Promote? [y/n]                                                 
                                                                    
3. [PREFERENCE] "I'd prefer to keep the auth flow simple"          
   → Proposed constraint on SPEC-0429 (auth flow)                  
   → Impact: contained (2 related specs)                            
```

The owner can:
- **Confirm** a candidate → promoted to Stage 3
- **Reject** a candidate → discarded (not deleted — archived as a deliberation with outcome=rejected)
- **Reclassify** a candidate → change from exploration to directive, or vice versa
- **Modify** the proposed title, section, or type before promotion
- **Defer** a candidate → kept in buffer for future session

### Stage 3: Record

Confirmed candidates are promoted to KB specs using the enriched schema (F1). The pipeline:

1. Runs F2 impact analysis one final time with the confirmed spec data
2. Generates assertions appropriate to the spec's tier (from F3's tier recommendation)
3. Populates `authority=stated` (owner confirmed), `constraints`, and `affected_by` (from F4's check_constraints)
4. Inserts the spec into the KB
5. Creates work items per GOV-12 (work item creation triggers test creation)
6. Archives the capture-confirm-record chain as a deliberation for traceability

### Sequencing Intelligence

The intake pipeline doesn't just record requirements — it **advises on ordering**. When multiple candidates are confirmed simultaneously:

1. **Dependency analysis:** If candidate A's section is constrained by candidate B's scope, B should be specified first
2. **Foundation-first:** Governance and architecture specs are promoted before feature specs
3. **Provisional marking:** If a candidate requires infrastructure that doesn't exist yet, it's marked `authority=provisional` with `provisional_until` pointing to the infrastructure spec

This implements the owner's vision: "all temporary implementations were identified as such purely because they precede the stage of the development when formal specifications for those areas are applied."

## Counterfactual Test

**If F5 had existed during the ZK requirement intake:**
- The owner's statement about operator data access would have been captured as a `directive` candidate
- Impact preview would have shown blast_radius=systemic with >100 affected specs
- The owner would have seen the scope BEFORE any spec was created
- The pipeline would have advised: "This is an architectural constraint. Recommend creating as ADR first, then propagating via F4, before modifying any functional specs."
- The phased approach would have prevented the big-bang redesign

**If F5 had existed during chat misinterpretation incidents:**
- Casual remarks would be classified as `exploration` or `question` (low confidence)
- They would NOT automatically become specs
- The owner would see them in the confirm step and say "no, that was just a thought"
- Only `directive` classifications with explicit confirmation would enter the KB

## API Design

```python
class RequirementIntake:
    """Session-scoped requirement capture and confirmation pipeline."""
    
    def capture(
        self,
        raw_text: str,
        context: str = None,
    ) -> RequirementCandidate:
        """Classify and capture a potential requirement from conversation."""
        ...
    
    def list_candidates(
        self,
        classification: str = None,
        min_confidence: float = 0.0,
    ) -> list[RequirementCandidate]:
        """Return current session's captured candidates."""
        ...
    
    def confirm(
        self,
        candidate_index: int,
        modifications: dict = None,  # Override proposed title, section, etc.
    ) -> dict:
        """Promote a candidate to KB spec. Returns the created spec."""
        ...
    
    def reject(
        self,
        candidate_index: int,
        reason: str = None,
    ) -> None:
        """Reject a candidate. Archived as deliberation."""
        ...
    
    def suggest_ordering(
        self,
        candidates: list[RequirementCandidate] = None,
    ) -> list[RequirementCandidate]:
        """Return candidates reordered by least-disruptive introduction sequence."""
        ...
```

## Test Plan

1. **Directive classification** — Input "the system MUST encrypt all data at rest"; verify classification=directive, confidence>0.8
2. **Exploration classification** — Input "what if we added dark mode?"; verify classification=exploration, confidence<0.5
3. **Confirm flow** — Capture directive, confirm it; verify spec appears in KB with authority=stated
4. **Reject flow** — Capture candidate, reject it; verify deliberation archived with outcome=rejected
5. **Impact preview** — Capture directive in constrained section; verify impact_preview shows applicable constraints
6. **Sequencing** — Capture 3 candidates (governance, feature, infrastructure); verify suggest_ordering returns governance first

## Implementation Sequence

1. Define `RequirementCandidate` dataclass
2. Implement classification logic (keyword + pattern matching + confidence scoring)
3. Implement session-scoped candidate buffer (in-memory, not persisted)
4. Implement confirm/reject flows with KB insertion and deliberation archival
5. Implement sequencing logic (dependency analysis, foundation-first ordering)
6. Integrate with F2 (impact preview on capture) and F4 (constraint check on confirm)
7. Write tests (6 cases above)
8. Create `/confirm-requirements` skill for Agent Red

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Classification errors cause requirements to be missed | All candidates are visible in the buffer regardless of classification; owner can reclassify |
| Confirmation step adds friction to fast-moving conversations | Batch confirmation (confirm all directives at once); defer for later sessions |
| Sequencing logic is naive for complex dependency chains | Start with section-based heuristics; enhance with constraint graph analysis after F4 ships |
| Session-scoped buffer is lost if session crashes | Archive candidates to a session-recovery file; not a critical data loss since the conversation is the source of truth |

## Open Questions for Codex Review

1. Should the candidate buffer persist across sessions, or should each session start fresh?
2. Should the AI be allowed to auto-confirm high-confidence directives, or must every candidate go through explicit confirmation?
3. How should the intake pipeline interact with the existing GOV-09 hook? Replace it, or layer on top?
4. Should deferred candidates have an expiration, or persist indefinitely until addressed?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F5*
