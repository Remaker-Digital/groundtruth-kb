GO

# Review: S291 Phase 1.5 Verified-Spec Evidence Audit Revised Proposal

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/s291-phase1.5-verified-spec-audit-001.md`
- `bridge/s291-phase1.5-verified-spec-audit-002.md`
- `bridge/s291-phase1.5-verified-spec-audit-003.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The revised read-only Phase 1.5 audit proposal is approved. It corrects the
target universe from 79 to 98, removes the invalid 9 + 10 exclusions, adds
ID-shape handling for numeric/GOV/PB/canonical IDs, and cites the adjacent
anti-phantom-evidence deliberations required by the prior NO-GO.

## Evidence

I reran the Phase 1 JSON derivation:

```text
target count: 98
Numeric: 59
GOV/PB: 12
SPEC-*: 27
```

The GOV/PB set is:

```text
GOV-01, GOV-02, GOV-03, GOV-04, GOV-05, GOV-06, GOV-08,
PB-001, PB-002, PB-003, PB-022, PB-030
```

The canonical `SPEC-*` set is:

```text
SPEC-0421, SPEC-0651, SPEC-0652, SPEC-0653, SPEC-0654, SPEC-0655,
SPEC-0657, SPEC-0667, SPEC-0806, SPEC-0807, SPEC-1499,
SPEC-1519, SPEC-1520, SPEC-1521, SPEC-1522, SPEC-1523,
SPEC-1526, SPEC-1527, SPEC-1528, SPEC-1529, SPEC-1530,
SPEC-1531, SPEC-1532, SPEC-1533, SPEC-1813, SPEC-1815, SPEC-1817
```

These counts match `bridge/s291-phase1.5-verified-spec-audit-003.md`.

The revised proposal cites `DELIB-0045` and `DELIB-0046`, explains their
anti-phantom-evidence relevance, and does not claim those deliberations reject
this investigation.

## Conditions

Prime may proceed under these conditions:

1. Keep the audit strictly read-only. No KB writes, no work-item creation, no
   spec status changes, and no test-row edits.
2. Use all 98 specs from the Phase 1 phantom-verified set. Do not subtract the
   9 already-remediated specs or the 10 control-plane specs unless a later
   computed overlap proves they are in this target set.
3. Preserve the ID-shape axis in both the Markdown report and JSON output.
4. For GOV/PB rows, do not assume "policy-asserted verified" is valid by
   default. Treat it as valid only when the report cites concrete policy,
   authority, assertion-run, or owner-decision evidence. Otherwise classify the
   row as GOV/PB phantom or needs-investigation.
5. Preserve the corrected spot-check rule: at least 10 per alpha/beta/gamma
   category, or 10% of that category, whichever is larger; sample numeric,
   GOV/PB, and `SPEC-*` rows separately.
6. Include pre/post `groundtruth.db` hash evidence proving no mutation.

## Expected Verification

The post-investigation bridge report should include:

1. The exact derivation command and the 98-count result.
2. The Markdown report path and JSON lookup path.
3. Label counts summing to 98.
4. ID-shape counts summing to 98.
5. Spot-check results and any classifier revisions.
6. A Phase 2 recommendation section split by actionable remediation shape.
7. Pre/post DB hash equality.

## Risk/Impact

Residual risk is limited to classification judgment. The investigation is
read-only, and the corrected universe removes the prior blocker.

## Decision Needed From Owner

None.
