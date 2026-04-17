# Review: S291 Phase 1.5 Verified-Spec Evidence Audit Proposal

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/s291-phase1.5-verified-spec-audit-001.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The read-only audit direction is valuable, but the proposal is not ready for GO
because its target universe is wrong. The proposal says Phase 1.5 should inspect
79 remaining verified specs after subtracting 9 already-remediated specs and
10 in-flight control-plane specs from the Phase 1 phantom-verified population.
That subtraction removes zero specs from the Phase 1 JSON set.

## Prior Deliberations

No exact prior deliberation was found for `verified spec evidence audit`,
`P0a track`, `98 verified phantom`, `per-spec triage`, or
`verified spec phantom`.

The deliberation archive does contain adjacent anti-phantom-evidence context:

- `DELIB-0045` - Phase 3 Advisory Review: Test Program Rewrite Proposal
  (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-27-19-34-PHASE3-ADVISORY.md`)
- `DELIB-0046` - Phase 3 Implementation Proposal Advisory Review
  (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-27-19-37.md`)

Those deliberations do not reject this proposal, but a revised proposal should
cite them as adjacent prior guidance on avoiding symbolic gates and phantom
evidence.

## Evidence

`bridge/s291-phase1.5-verified-spec-audit-001.md:33` through
`bridge/s291-phase1.5-verified-spec-audit-001.md:36` claims the universe is:
98 verified specs with category-(a) phantom rows, minus 9 already remediated
specs, minus 10 in-flight control-plane specs, for 79 remaining specs.

I reran the proposal's own set operation against
`independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json`:

```text
phantom_verified 98
already_overlap 0 []
spa_overlap 0 []
target_after_subtract 98
already_not_in_phantom ['SPEC-0439', 'SPEC-0604', 'SPEC-0661', 'SPEC-0811', 'SPEC-1076', 'SPEC-1078', 'SPEC-1097', 'SPEC-1138', 'SPEC-1165']
spa_not_in_phantom ['SPEC-1816', 'SPEC-1818', 'SPEC-1819', 'SPEC-1820', 'SPEC-1821', 'SPEC-1822', 'SPEC-1823', 'SPEC-1824', 'SPEC-1826', 'SPEC-1827']
```

The current DB also confirms that all 98 specs in the Phase 1
phantom-verified set are still currently `verified`:

```text
current_status_counts_for_phase1_phantom_verified {'verified': 98}
```

The ID shape of the actual 98-spec set is mixed, which explains why the manual
`SPEC-*` exclusion lists do not intersect it:

```text
id_shape {'numeric': 59, 'other': 12, 'SPEC': 27}
first examples ['101', '102', '103', '104', '105', '107', '108', '109']
other examples GOV-01, GOV-02, GOV-03, GOV-04, GOV-05, GOV-06, GOV-08, PB-001
SPEC examples include SPEC-1519..SPEC-1533, SPEC-1813, SPEC-1815, SPEC-1817
```

Spot DB checks show the mismatch concretely:

```text
101 current status=verified title=pytest configuration (pyproject.toml)
102 current status=verified title=Test requirements file (requirements-test.txt)
135 current status=verified title=Prompt optimization and prefix caching
SPEC-0439 current status=verified, but is not in the Phase 1 phantom-verified set
SPEC-1816 current status=implemented after remediation, but is not in the Phase 1 phantom-verified set
SPEC-1815 current status=verified and is in the Phase 1 phantom-verified set
SPEC-1817 current status=verified and is in the Phase 1 phantom-verified set
```

## Findings

### Finding 1 - The audit would inspect the wrong population

Severity: Blocker

The proposed invariant "79 specs in, 79 specs out" is false for the proposal's
source data and code sketch. The actual computed target remains 98. A GO would
authorize a report and JSON whose cardinality check is disconnected from the
Phase 1 categorization data.

Risk/impact:

- The audit could skip 19 specs that still belong to the current
  phantom-verified population.
- Future Phase 2 remediation would be planned from a bad lookup table.
- The 9 + 10 exclusions would give a false sense that prior bridge work reduced
  this particular Phase 1 slice.

Required action:

- Recompute the target universe from the Phase 1 JSON and current DB.
- State whether Phase 1.5 is auditing the exact 98 Phase 1
  phantom-verified specs, including numeric/GOV/PB IDs, or a different
  canonical `SPEC-*` slice.
- If excluding the 9 + 10 bridge-remediated specs, provide an explicit
  normalization map proving they correspond to rows in the 98-spec set. If no
  such map exists, remove those exclusions.
- Update all expected counts, test-plan invariants, and verification conditions.

### Finding 2 - The proposal does not account for noncanonical IDs

Severity: High

Only 27 of the 98 Phase 1 phantom-verified spec IDs start with `SPEC-`. The rest
are 59 numeric IDs and 12 other IDs such as GOV/PB identifiers. The proposed
method treats the population as ordinary canonical spec IDs and then subtracts
only canonical `SPEC-*` lists.

Risk/impact:

- Cluster inference and remediation recommendations may misclassify legacy
  numbered specs or governance/policy specs as ordinary product requirements.
- A later remediation proposal may choose the wrong action: link evidence,
  downgrade, retire, or normalize IDs.

Required action:

- Add an ID-shape section with counts for numeric, other, and canonical
  `SPEC-*` IDs.
- Treat ID hygiene as a first-class audit axis. For numeric/GOV/PB rows,
  decide whether the next proposal is evidence repair, ID normalization, or
  retirement/subsumption before recommending status changes.

## Answers To Open Questions

Cluster definition: use concrete DB fields when present, especially `section`,
`type`, and title. Because the actual set has mixed ID shapes, include
ID-shape/component grouping as its own cluster dimension; title inference should
be secondary.

Spot-check budget: 5 per category is too small if the revised audit still has
only three alpha/beta/gamma categories. Use at least 10 per category, or 10% per
high-risk ID-shape/cluster, whichever is larger. Sample numeric, GOV/PB, and
canonical `SPEC-*` groups separately.

Reclassification escalation: if using 5 spot-checks per category, revise on
more than 1 reclassification. If using 10, keep Phase 1's more-than-2 rule.

Subsumption detection: "phantom row for A whose current version points at
active spec B" is not sufficient by itself. Confirm B's current passing evidence
covers A's behavior, or classify the case as ID recycling/placeholder drift
rather than true subsumption.

Exclusion lists: manual lists are not authoritative for this audit unless they
intersect the computed source set. Query the Phase 1 JSON and current DB first,
then cite bridge files only as explanation for exclusions that actually overlap.

Prioritization: since the Phase 1 set is still 98 current `verified` specs,
prioritize verified-status risk first, then no-real-evidence signals, high
phantom-row count, and high-risk ID shapes.

## Required Revision

Submit a revised proposal that:

1. Replaces the 79-count universe with a computed, reproducible target set.
2. Includes the exact command/query used to derive the target count.
3. Adds ID-shape counts and handling rules for numeric/GOV/PB IDs.
4. Either removes the 9 + 10 exclusions or proves an ID-normalization mapping
   from those exclusions into the computed Phase 1 target set.
5. Updates the Markdown/JSON output contracts, sanity checks, and verification
   conditions to the corrected target count.
6. Adds a Prior Deliberations section citing `DELIB-0045` and `DELIB-0046` as
   adjacent context, or explains why they are not applicable.
7. Keeps the read-only DB hash bracket and no-KB-write constraints.

## Decision Needed From Owner

None. This is a proposal-correction NO-GO, not an owner policy decision.
