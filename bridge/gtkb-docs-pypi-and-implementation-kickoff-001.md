# GT-KB Documentation Update + Implementation Kickoff

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Implementation Proposal (Multi-Part)  
**Prior Deliberations:** DELIB-0709 (all 8 GO gate), DELIB-0316 (GT-KB publishing plan), DELIB-0633 (GT-KB strategic assessment)

## Context

All 8 GT-KB specification pipeline feature proposals have reached GO status
through the bridge review process (F1-F8). Per DELIB-0709, the next steps are:

1. Cross-check alignment across all 8 proposals
2. Implement in dependency order

Additionally, groundtruth-kb v0.3.1 was published to PyPI today (2026-04-13).
The owner designated the "Sarah Scenario" user experience document
(DOC-SARAH-SCENARIO) as the anchor reference for all GT-KB documentation.

This proposal covers three work streams:

- **Part A:** GT-KB documentation update (PyPI install + Sarah scenario)
- **Part B:** F1-F8 cross-check alignment
- **Part C:** Implementation sequence confirmation

## Part A: GT-KB Documentation Update

### Objective

Update the groundtruth-kb repository documentation to reflect PyPI availability
and integrate the Sarah scenario as the highlighted introduction.

### Changes

#### A1. README.md

- **Add PyPI badge** to the badge row:
  `[![PyPI](https://img.shields.io/pypi/v/groundtruth-kb.svg)](https://pypi.org/project/groundtruth-kb/)`
- **Update Quick Start** install command:
  - From: `pip install "groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.3.0"`
  - To: `pip install groundtruth-kb`
- **Keep GitHub install** as an alternative for pinned versions
- **Add link** to the user journey page in the intro section

#### A2. docs/index.md

- **Update Quick Start** install command (same as README)
- **Add prominent link** to the user journey as first navigation item:
  "New here? Start with [The User Journey](user-journey.md) to see what
  building with GroundTruth looks like."

#### A3. docs/start-here.md

- **Update Step 1** install command to `pip install groundtruth-kb`
- **Remove** the "GitHub-only distribution" admonition note
- **Add** PyPI note: "Install from PyPI. Pin to a specific version with
  `pip install groundtruth-kb==0.3.1` for reproducible installs."
- **Update** version expectation from `0.3.0` to `0.3.1`

#### A4. docs/user-journey.md (NEW)

Create a new documentation page adapted from the Sarah scenario
(DOC-SARAH-SCENARIO, source: `Agent Red/docs/vision/groundtruth-kb-user-experience-scenario.md`).

Adaptations from the Agent Red version:
- Remove Agent Red-specific references (Azure Container Apps details, Cosmos DB
  specifics) and generalize to "your cloud provider"
- Keep the 7-phase structure (Phase 0-7)
- Keep the skill matrices per phase (these are the most valuable part)
- Keep the "What Sarah IS doing" sections (they define the owner's role)
- Keep the honest gaps section (builds trust with potential adopters)
- Add the GT-KB feature mapping table (F1-F8 to phases)
- Add a "Getting Started" call-to-action linking to start-here.md

This page becomes the **primary introduction** for potential adopters. It
answers "What would it actually be like to use this?" before diving into
technical documentation.

#### A5. docs/method/00-vision.md

- **Keep** the existing content (it serves as an internal decision filter for
  Prime/Codex work)
- **Add** a cross-reference at the top: "For a concrete walkthrough of this
  vision in practice, see [The User Journey](../user-journey.md)."

#### A6. Version references

Global find-and-replace in docs:
- `v0.3.0` → `v0.3.1` in install commands and version expectations
- Leave changelog entries and historical references as-is

### File touchpoints

| File | Action |
|------|--------|
| `README.md` | Edit: badge, install cmd, link |
| `docs/index.md` | Edit: install cmd, nav link |
| `docs/start-here.md` | Edit: install cmd, note, version |
| `docs/user-journey.md` | Create: adapted Sarah scenario |
| `docs/method/00-vision.md` | Edit: add cross-reference |
| `mkdocs.yml` (if exists) | Edit: add user-journey to nav |

### Verification

- `python -m build` succeeds (no packaging impact)
- `gt --version` shows 0.3.1 (already done)
- Docs build cleanly (mkdocs build, if configured)
- All internal links resolve

## Part B: F1-F8 Cross-Check Alignment

### Objective

Per DELIB-0709, verify that all 8 GO'd proposals are mutually consistent,
that the dependency graph is correct, and that no interface contracts are
missing.

### Dependency graph (from work list)

```
F1 (Schema Enrichment)
  |
  +-- F2 (Change Impact) + F3 (Quality Gate)
  |     |
  |     +-- F4 (Constraint Propagation) + F5 (Intake Pipeline) + F7 (Health Dashboard)
  |           |
  |           +-- F6 (Scaffold Generator) + F8 (Provenance Reconciliation)
  |
  +-- AR migration (Agent Red integration)
```

### Cross-check items

1. **F1 → F2 interface:** F2's blast-radius analysis depends on F1's
   `stability`, `affected_by` fields. Verify F2's GO proposal references
   these exact field names.

2. **F1 → F3 interface:** F3's quality scoring depends on F1's `testability`,
   `authority` fields. Verify scoring formula references match F1's schema.

3. **F3 → F7 interface:** F7's session health metrics aggregate F3's quality
   scores. Verify metric definitions are consistent.

4. **F1 → F5 interface:** F5's intake pipeline writes specs with F1's enriched
   schema. Verify F5 populates all required F1 fields.

5. **F4 → F1 interface:** F4's constraint propagation writes `affected_by`
   arrays into specs. This is an F1 field. Verify bidirectional consistency.

6. **F6 → F1+F3 interface:** F6's scaffold generator produces seed specs that
   must conform to F1's schema and pass F3's minimum quality threshold.

7. **F8 → F1 interface:** F8's reconciliation reads `authority`, `file_targets`,
   `provisional_expiry` from specs. All are F1 fields. Verify field names match.

8. **No circular dependencies:** Verify no feature requires another feature
   that depends on it.

### Cross-check method

Read each GO proposal's "Interface Contracts" or equivalent section. Tabulate
all field names, method signatures, and data flows. Flag any:
- Name mismatches between producer and consumer
- Missing fields that a downstream feature expects
- Contradictory assumptions about data formats or lifecycle states

### Deliverable

Cross-check report appended to this bridge document (or as a new version)
confirming alignment or identifying issues to resolve before implementation.

## Part C: Implementation Sequence Confirmation

### Confirmed order (per DELIB-0709 and work list)

| Phase | Features | Rationale |
|-------|----------|-----------|
| 0 | Part A (docs) | Non-code, unblocks user adoption |
| 1 | F1 (Schema Enrichment) | Foundation — all other features depend on F1's schema |
| 2 | F2 + F3 (Impact + Quality) | Depend only on F1; independent of each other |
| 3 | F4 + F5 + F7 (Constraints + Intake + Dashboard) | Depend on F1-F3; independent of each other |
| 4 | F6 + F8 (Scaffold + Reconciliation) | Depend on all prior features |
| 5 | AR migration | Adapt Agent Red to use GT-KB's new features |

### Per-feature implementation approach

Each feature in Phases 1-4 follows the standard bridge protocol:
1. Prime writes implementation proposal (scope, files, tests)
2. Codex reviews → GO/NO-GO
3. Prime implements + tests
4. Prime writes post-implementation report
5. Codex verifies → VERIFIED/NO-GO

Phase 0 (docs) is submitted as Part A of this proposal. Implementation can
begin immediately upon GO for Part A, without waiting for the cross-check to
complete.

Phase 5 (AR migration) will be scoped after Phases 1-4 are complete and the
new GT-KB features are released.

## Request

Codex review requested for:
1. **Part A** — Documentation changes described above
2. **Part B** — Cross-check methodology and items
3. **Part C** — Implementation sequence

GO for Part A authorizes immediate documentation work in the groundtruth-kb
repo. GO for Parts B+C authorizes the cross-check analysis and confirms the
implementation sequence.

---

*This proposal targets the groundtruth-kb repository (documentation) and
the Agent Red repository (KB records, bridge coordination).*
