GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Scoping Revision

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-017-scoping-003.md`
Role: Codex Loyal Opposition
Verdict: GO with binding carry-forward condition

## Review Scope

The live bridge index showed `gtkb-isolation-017-scoping` at latest status
`REVISED` with `bridge/gtkb-isolation-017-scoping-003.md`. Codex is operating
as Loyal Opposition through the harness-local durable role record at
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001`, `-002`, `-003`) against
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`,
`.claude/rules/codex-review-gate.md`, and the linked Phase 9 plan:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`.

This review is scoped to the scoping bridge only. No implementation files were
changed.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `GTKB-ISOLATION-017 Phase 9 adopter packaging`
- `ADR-ISOLATION-APPLICATION-PLACEMENT Phase 9`
- `application isolation adopter packaging clean adopter`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. The active prior review context is
therefore the bridge thread itself: `bridge/gtkb-isolation-017-scoping-001.md`
and Codex NO-GO `bridge/gtkb-isolation-017-scoping-002.md`.

The prior NO-GO had two blocking findings:

- F1: five of seven Phase 9 owner decisions were dropped from the scoping map.
- F2: required Phase 9 deliverables and exit criteria were not assigned to
  slices.

## Findings

No blocking findings remain.

### F1 Resolution - PASS

Claim: The revision now maps all seven Phase 9 implementation decisions.

Evidence:

- The Phase 9 source requires seven decisions to be surfaced:
  `GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:369-396`.
- The revision maps all seven decisions with owning slice, blocking point,
  expected owner input, and implementation consequence:
  `bridge/gtkb-isolation-017-scoping-003.md:39-55`.

Risk / impact: The prior risk of silently dropping release version,
compatibility policy, transition channels, acceptance gate, and Phase 8
rehearsal-evidence decisions is resolved for scoping purposes.

Recommended action: Carry these decision rows into the relevant per-slice
implementation bridges.

Decision needed from owner: None at this scoping GO.

### F2 Resolution - PASS

Claim: The revision now assigns the omitted Phase 9 deliverables and exit
criteria to implementation slices.

Evidence:

- The Phase 9 source requires service/overlay documentation and testing:
  `GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:341-352`.
- The Phase 9 source requires CI-visible regression coverage and registry
  drift detection:
  `GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:398-413`.
- The Phase 9 source requires implementation deliverables including the
  adopter README block, examples, release notes, and release-version-gating
  report:
  `GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:415-430`.
- The revision assigns AST gate CI and registry-drift detection to Slice 2:
  `bridge/gtkb-isolation-017-scoping-003.md:78-91`.
- It assigns the adopter README quickstart block and Phase 4 service endpoint
  scaffold to Slice 3:
  `bridge/gtkb-isolation-017-scoping-003.md:93-115`.
- It assigns Phase 8 rehearsal-evidence integration to Slice 4:
  `bridge/gtkb-isolation-017-scoping-003.md:117-131`.
- It assigns clean-adopter CI and overlay tests to Slice 5:
  `bridge/gtkb-isolation-017-scoping-003.md:133-149`.
- It assigns service-down and overlay-fallback documentation to Slice 6:
  `bridge/gtkb-isolation-017-scoping-003.md:151-171`.
- It assigns dashboard-rendering example verification to Slice 7:
  `bridge/gtkb-isolation-017-scoping-003.md:173-184`.
- It assigns release notes, release-version gating, and program closeout to
  Slice 8:
  `bridge/gtkb-isolation-017-scoping-003.md:186-200`.

Risk / impact: The prior risk that later implementation bridges could pass
local acceptance while failing Phase 9 exit criteria is resolved at the scoping
level.

Recommended action: Each per-slice bridge must carry forward the exact linked
Phase 9 obligations it owns and provide spec-derived tests or documentation
verification for them.

Decision needed from owner: None at this scoping GO.

## Binding Carry-Forward Condition

Slice 8 must surface decision 5, the post-Phase-9 acceptance gate, before Slice
8 implementation starts. The scoping table currently lists the blocking point
as "Slice 8 post-implementation report - Acceptance Criteria"
(`bridge/gtkb-isolation-017-scoping-003.md:49`). That wording is acceptable for
this scoping GO only because Slice 8 is a future bridge with its own review
gate, but it must not become a post hoc completion criterion.

Required condition for the Slice 8 implementation bridge:

- Ask for or cite the owner decision that defines the Phase 9 acceptance gate
  before implementing closeout artifacts.
- Treat the post-implementation report as evaluation against the already chosen
  criterion, not as the first point where the criterion is defined.

If Slice 8 does not satisfy this condition, Loyal Opposition should NO-GO the
Slice 8 bridge.

## Gate Checks

- Root-boundary gate: PASS. Proposed active work remains under `E:\GT-KB`;
  cited external paths are historical only.
- Specification-linkage gate: PASS. The revision includes a `Specification
  Links` section and carries forward the Phase 9 plan plus bridge/governance
  constraints.
- Test-derivation gate for scoping: PASS. Implementation is deferred to
  per-slice bridges; each slice now has concrete acceptance criteria that can
  be converted into spec-derived tests or verification.
- Existing-surface spot check: PASS. The cited project surfaces exist under
  `groundtruth-kb/src/groundtruth_kb/project/`; `doctor.py` has 1872 lines and
  `upgrade.py` has 958 lines. `groundtruth-kb/tests/adopter/` does not yet
  exist, and `groundtruth-kb/examples/` currently contains `task-tracker`, which
  is consistent with the proposal's gap framing.

## Verdict

GO. `GTKB-ISOLATION-017` may proceed to per-slice implementation bridge
proposals, subject to normal bridge review and the Slice 8 carry-forward
condition above.

File bridge scan: 1 entry processed.
