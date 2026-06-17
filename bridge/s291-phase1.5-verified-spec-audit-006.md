NO-GO

# Verification Review: S291 Phase 1.5 Verified-Spec Evidence Audit

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/s291-phase1.5-verified-spec-audit-001.md`
- `bridge/s291-phase1.5-verified-spec-audit-002.md`
- `bridge/s291-phase1.5-verified-spec-audit-003.md`
- `bridge/s291-phase1.5-verified-spec-audit-004.md`
- `bridge/s291-phase1.5-verified-spec-audit-005.md`
Artifacts inspected:
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md`
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json`
- `groundtruth.db` opened read-only via SQLite

## Claim

The audit envelope is mostly correct, but the result cannot be marked VERIFIED.
The JSON has 98 records, the ID-shape counts sum to 98, and the reported DB hash
matches the current file hash. However, the audit undercounts current
non-phantom test evidence and misclassifies `SPEC-1815` as beta even though the
current database contains 25 current real test rows linked to that spec.

## Evidence

Artifact existence and hash checks passed:

```text
Report exists: True
JSON exists: True
Current groundtruth.db SHA256:
141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
```

JSON summary also matches the submitted headline:

```text
records 98
labels {'alpha': 83, 'GOV/PB-policy': 12, 'beta': 3}
shapes {'numeric': 59, 'GOV/PB': 12, 'SPEC-*': 27}
beta ['SPEC-1813', 'SPEC-1815', 'SPEC-1817']
```

But recomputing current non-phantom evidence from the `tests` table, using the
approved definition "latest version per test id and non-empty `test_file`",
does not match the JSON. Twelve target specs are undercounted:

```text
('112', 'nonphantom', json=0, db=22)
('141', 'nonphantom', json=0, db=17)
('147', 'nonphantom', json=0, db=4)
('151', 'nonphantom', json=0, db=20)
('153', 'nonphantom', json=0, db=16)
('154', 'nonphantom', json=0, db=12)
('155', 'nonphantom', json=0, db=14)
('215', 'nonphantom', json=0, db=58)
('220', 'nonphantom', json=0, db=34)
('224', 'nonphantom', json=0, db=56)
('239', 'nonphantom', json=0, db=79)
('SPEC-1815', 'nonphantom', json=0, db=25)
```

The `SPEC-1815` case is decisive. The JSON says:

- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json:1251`
  identifies `SPEC-1815`.
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json:1253`
  labels it `beta`.
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json:1259`
  says `non_phantom_current` is `0`.
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json:1261`
  recommends direct downgrade.

Read-only DB query against latest test versions returns 25 current real rows for
`SPEC-1815`, all linked to `tests/multi_tenant/test_entitlement_service.py`.
Examples:

```text
TEST-10407 v1 SPEC-1815 tests/multi_tenant/test_entitlement_service.py test_frozen_has_all_tiers pass
TEST-10408 v1 SPEC-1815 tests/multi_tenant/test_entitlement_service.py test_frozen_rate_limits pass
TEST-10416 v1 SPEC-1815 tests/multi_tenant/test_entitlement_service.py test_resolve_gate_aliases pass
TEST-10421 v1 SPEC-1815 tests/multi_tenant/test_entitlement_service.py test_is_feature_allowed pass
TEST-10431 v1 SPEC-1815 tests/multi_tenant/test_entitlement_service.py test_initialized_flag pass
count 25
```

The file also exists at
`tests/multi_tenant/test_entitlement_service.py`.

The Markdown report repeats the same unsupported premise:

- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md:125`
  says `SPEC-1815` has 0 non-phantom current tests.
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md:128-130`
  says the current versions were reassigned away from `SPEC-1815`.
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md:231-233`
  says `SPEC-1815` is confirmed beta.

That is contradicted by the current `tests` table.

There is also an internal count inconsistency: the submitted bridge report says
83 alphas are 59 numeric plus 24 `SPEC-*` at
`bridge/s291-phase1.5-verified-spec-audit-005.md:56`, but the Markdown artifact
says `SPEC-* alphas (25 total)` at
`independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md:216`.

## Findings

### 1. `SPEC-1815` is misclassified as beta

Severity: Blocker

The approved classifier in `bridge/s291-phase1.5-verified-spec-audit-004.md`
allowed `alpha` when real evidence exists through non-phantom current test rows
or assertion runs. `SPEC-1815` has 25 current non-phantom test rows. It therefore
does not satisfy the submitted beta definition of "no current real evidence."

Risk/impact:

- Phase 2 could downgrade a verified spec that still has current KB-linked test
  evidence.
- The JSON lookup is the downstream remediation input, and it currently says
  direct downgrade for `SPEC-1815`.
- Verification condition 6 in `bridge/s291-phase1.5-verified-spec-audit-005.md`
  is not satisfied because the submitted beta set is wrong.

Required action:

- Recompute `non_phantom_current` from current latest test versions.
- Reclassify `SPEC-1815` as alpha unless Prime can provide a concrete query
  showing those 25 current rows are invalid evidence under an explicitly stated
  rule.
- Update label counts, spot-check counts, cluster totals, JSON, Markdown, and
  Phase 2 recommendations accordingly.

### 2. `non_phantom_current` is undercounted for multiple alpha specs

Severity: High

The label impact is biggest for `SPEC-1815`, but the JSON also reports
`non_phantom_current=0` for 11 alpha specs where the current DB has real test
rows. This means the output evidence fields are not reliable even where the
final label remains alpha due to assertion runs.

Risk/impact:

- Downstream traceability work would miss existing real tests.
- The audit would overstate reliance on assertion runs and understate direct
  test coverage.
- Future remediation could create duplicate assertion/test links instead of
  preserving existing evidence.

Required action:

- Fix the query used for `non_phantom_current`.
- Regenerate the JSON and Markdown evidence tables.
- Include the recomputation command and a small before/after summary in the
  revised bridge report.

### 3. Spot-check and label-count text are internally inconsistent

Severity: Medium

The bridge report's label table says 24 `SPEC-*` alphas, while the Markdown
artifact says 25 `SPEC-*` alphas. If `SPEC-1815` is reclassified as alpha, 25
will be the likely corrected value, but the current artifacts disagree.

Required action:

- Align all label, ID-shape, cluster, and spot-check counts after recomputation.

## Required Conditions For VERIFIED

1. JSON has exactly 98 records and exactly matches the Phase 1 target ID set.
2. `non_phantom_current` matches a read-only DB recomputation from latest test
   versions for every target spec.
3. `SPEC-1815` is either reclassified as alpha or accompanied by a concrete,
   query-backed exclusion rationale that explains why 25 current real test rows
   are not valid evidence.
4. Phase 2 recommendations do not direct-downgrade `SPEC-1815` unless that
   exclusion rationale is accepted.
5. Markdown, JSON, label counts, ID-shape counts, cluster totals, and
   spot-check counts are internally consistent.
6. DB hash evidence remains unchanged before and after the revised read-only
   audit.

## Decision Needed From Owner

None. This is a verification NO-GO on artifact correctness.
