NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Scoping

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-017-scoping-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-scoping` at latest status
`NEW` with `bridge/gtkb-isolation-017-scoping-001.md`.

I reviewed the scoping proposal against the file bridge protocol, project-root
boundary rule, the Phase 9 plan, the Phase 1 authority-matrix plan, the
application-placement ADR bridge history, and the prior Phase 8 Wave 3 closure.
This review is scoped to the scoping bridge only; no implementation files were
changed.

## Prior Deliberations

`search_deliberations()` was run before review for:

- `GTKB-ISOLATION-017 Phase 9 adopter packaging`
- `ADR-ISOLATION-APPLICATION-PLACEMENT Phase 9`
- `application isolation adopter packaging clean adopter`

Relevant prior deliberations found:

- `DELIB-1136`: compressed bridge thread for the verified
  `gtkb-isolation-009-adopter-packaging-plan-review`.
- `DELIB-1012`: GTKB-ISOLATION-009 Phase 9 adopter packaging plan review GO.
- `DELIB-1011`: GTKB-ISOLATION-009 plan-review closure VERIFIED.
- `DELIB-0877`: owner directive / industry-alignment critique for the
  GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan.
- `DELIB-0920` and `DELIB-0919`: ADR-ISOLATION-APPLICATION-PLACEMENT review
  history, including NO-GO then GO after sequencing correction.

The scoping proposal builds on the right prior thread family, but it does not
carry forward all Phase 9 decision and deliverable obligations.

## Findings

### F1 - Blocking: the scoping plan drops five of the seven Phase 9 implementation decisions

Claim: The scoping bridge says the only owner-decision item from the Phase 9
plan is mandatory-vs-opt-in isolation, and then separately defers the Agent Red
example decision to Slice 7.

Evidence:

- `bridge/gtkb-isolation-017-scoping-001.md:185` states that "the only
  owner-decision-needed item identified in the Phase 9 plan is mandatory vs
  opt-in isolation for existing adopters."
- `bridge/gtkb-isolation-017-scoping-001.md:201-207` says no decision is
  needed at GO time and lists only Slice 4 mandatory-vs-opt-in isolation and
  Slice 7 Agent Red example as deferred owner-decision items.
- The linked Phase 9 plan requires the implementation bridge to surface seven
  owner decisions before starting:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:369-396`.
  The omitted decisions are release version, backward-compatibility policy,
  publicity/transition channels, post-Phase-9 acceptance gate, and Phase 8
  rehearsal-evidence integration.

Risk / impact: A GO would authorize the umbrella slice sequence while leaving
release gating, compatibility, transition policy, completion evidence, and
Phase 8 evidence usage unmapped. Those are not cosmetic decisions; they affect
which slices are allowed to ship, how existing adopters are treated, and what
evidence closes Phase 9.

Recommended action: Revise the scoping bridge to include a decision map for all
seven Phase 9 decisions. The map can still defer decisions to per-slice bridges,
but each decision must have an owning slice, blocking point, expected owner
input shape, and implementation consequence. If any decision is intentionally
not needed for GTKB-ISOLATION-017, cite the superseding authority.

Decision needed from owner: None at this review stage. Prime can revise the
scoping plan without owner input by preserving the Phase 9 plan's existing
decision list.

### F2 - Blocking: required Phase 9 deliverables and exit criteria are not mapped to slices

Claim: The seven proposed slices cover the headline Phase 9 areas, but the
acceptance criteria do not cover several explicit deliverables and exit
criteria from the linked Phase 9 plan.

Evidence:

- The Phase 9 plan requires docs under `groundtruth-kb/docs/` plus an
  adopter-facing README quickstart block baked into `gt project init`:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:261`
  and `:425-426`. Slice 6 only says "new isolation chapter" and does not map
  the adopter README block; Slice 3's scaffold acceptance also omits the README
  artifact: `bridge/gtkb-isolation-017-scoping-001.md:92-99`,
  `bridge/gtkb-isolation-017-scoping-001.md:133-143`.
- The Phase 9 plan requires release notes covering every isolation-related
  change and post-implementation reporting that documents release-version
  gating:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:428-430`.
  No proposed slice owns release notes or release-version gating.
- The Phase 9 exit criteria require service/overlay behavior to be documented
  and tested: Phase 4 service endpoints in scaffolded `groundtruth.toml`,
  adopter README documentation, at least one scaffolded test, Phase 6 overlay
  refresh/stale behavior, example dashboard rendering, and service-down /
  overlay fallback docs:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:341-350`.
  The scoping bridge's Slice 3, Slice 5, Slice 6, and Slice 7 acceptance lists
  do not assign these obligations: `bridge/gtkb-isolation-017-scoping-001.md:92-99`,
  `:119-130`, `:139-143`, `:154-157`.

Risk / impact: The later implementation bridges could each pass their local
acceptance criteria while GTKB-ISOLATION-017 still fails the Phase 9 plan's
published exit criteria. This would create exactly the schema-vs-implementation
drift the scoping bridge identifies as a prior lifecycle risk.

Recommended action: Revise the slice plan so every Phase 9 deliverable and
exit criterion has an owning slice or an explicit supersession/waiver. At
minimum, add coverage for adopter README quickstart scaffolding, release notes,
release-version gating, service endpoint scaffold tests, overlay behavior
tests/docs, dashboard-rendering example verification, and service-down /
overlay fallback documentation.

Decision needed from owner: None for the revision unless Prime wants to change
the Phase 9 plan itself. If Prime keeps the approved Phase 9 plan intact, this
is a scope-mapping correction.

## Non-Blocking Observations

- The in-root surface mapping is broadly correct. Spot checks confirmed
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` has 1872 lines and
  `upgrade.py` has 958 lines; the cited surfaces exist under `E:\GT-KB`.
- `groundtruth-kb/tests/adopter/` does not yet exist, and
  `groundtruth-kb/examples/` currently contains only `task-tracker`, matching
  the proposal's claim that those surfaces need new Phase 9 work.
- The proposal correctly keeps implementation behind future per-slice bridge
  cycles and stays inside the root boundary.

## Gate Checks

- Root-boundary gate: PASS. The proposed active work is under `E:\GT-KB`.
- Specification-linkage gate: PASS for presence of a `Specification Links`
  section, but FAIL for completeness of carried-forward Phase 9 obligations.
- Test-derivation gate: not GO-able yet because the omitted deliverables and
  decisions have no slice-owned tests or verification mapping.

## Verdict

NO-GO. Revise the scoping bridge to carry forward all Phase 9 owner-decision
items, deliverables, and exit criteria into the slice plan before GTKB-
ISOLATION-017 proceeds to per-slice implementation bridges.

File bridge scan: 1 entry processed.
