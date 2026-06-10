Document: gtkb-architecture-governance-hygiene-investigation

**Status:** NEW  
**From:** LO (Mike/Clarification)  
**To:** PB  
**Date:** 2026-06-10  
**Subject:** Architecture & Governance Hygiene Investigation — 50 Work Items

---

## Request

Conduct comprehensive codebase investigation to identify **50 highest-value enhancement/correction work items** addressing systemic friction:
- Poor design choices (bridge/dispatcher)
- Stray/obsolete artifacts
- Conflicting specifications
- Specification deviations
- Unclear prompt language
- Overly-aggressive hooks
- Structural detritus

## Source

Prompt refined through owner clarification session. Full specification saved to:
`independent-progress-assessments/GT-KB-Architecture-Hygiene-Investigation-Prompt.md`

## Key Requirements

1. **Investigate all scopes:** Core platform, governance artifacts, demo apps, harness config, bridge infrastructure, MemBase, Deliberation Archive, CI/CD
2. **Six value dimensions (priority order):** Technical Debt → Spec Compliance → Maintainability → Functional Correctness → Governance Hygiene → Operational Excellence
3. **Six focus areas:** Design Choices, Artifact Hygiene, Spec Integrity, Prompt/Role Clarity, Mechanical Enforcement, Structural Detritus
4. **Overlap handling:** Re-evaluate existing backlog items, augment or create distinct as needed
5. **Output:** Categorized findings report with 50 items, each with owner touchpoint questions
6. **Process:** Investigation is read-only; implementation comes after grill-me sessions per item

## Success Criteria
- Surface unknown issues
- Confirm suspected issues  
- Enable immediate prioritization
- Exactly 50 actionable items

## Deliverables
- Categorized findings report
- Executive summary with quick-wins
- Per-item owner touchpoint questions
- Cross-reference map
- Methodology appendices

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

---

**Action Required:** Begin investigation per full specification. Report back with findings document ready for item-by-item grill-me sessions.
