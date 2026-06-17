NO-GO

# Verification Review: POR Step 16.B Methodology Review

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16b-methodology-review-001.md`
- `bridge/por-step16b-methodology-review-002.md`
- `bridge/por-step16b-methodology-review-003.md`
- `bridge/INDEX.md` entry `por-step16b-methodology-review`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py`
- `independent-progress-assessments/spec-hygiene/scripts/archive_16b_deliberation.py`
- `groundtruth.db` opened read-only for verification queries

## Claim

The Step 16.B classifier and inventory substantially satisfy the prior GO's
core methodology requirements: the target set is 193 specs, the revised
classification is exhaustive, semantic assertion handling is present, the
analysis hash bracket shows no DB mutation, and `DELIB-0712` exists as the
single archived methodology decision.

However, the submitted post-implementation report and methodology document
misreport two summary count fields that were specifically in the scope of
Codex condition 3, "row counts versus distinct spec counts." This needs a
revised bridge submission before VERIFIED.

## Evidence Verified

Read-only checks against the generated inventory:

```text
inventory_target_count: 193
inventory_category_counts:
  alpha_prime: 151
  beta_prime: 4
  delta_prime: 15
  gamma_prime: 19
  zeta_prime: 4
inventory_categories_sum: 193
inventory_unclassified_count: 0
inventory_db_hash_pre:  6B2FF7D1B9154C884D4A7BAFB4036B83E5B35986CB75D2514CBCA5ED10AE536D
inventory_db_hash_post: 6B2FF7D1B9154C884D4A7BAFB4036B83E5B35986CB75D2514CBCA5ED10AE536D
inventory_db_mutated: false
```

Relevant artifact lines:
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5`
  through `:13` record the pre/post hashes, target count, and category counts.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:28`
  records `db_mutated: false`.
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:51`
  through `:53` open SQLite with `mode=ro`.
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:323`
  through `:325` assert exhaustive classification and zero unclassified rows.

Read-only DB recomputation:

```text
target_count_db: 193
current_tests stale rows across target specs: 130
current_tests stale distinct specs: 118
specs with historical test_file: 159
specs with assertion_runs overall_passed=1: 170
sum of per-spec distinct historical test_file paths: 167
```

`DELIB-0712` verification:

```text
delib_0712_rows: 1
outcome: owner_decision_pending
source_type: methodology_review
source_ref: bridge/por-step16b-methodology-review-002.md
session_id: S297
changed_by: prime_builder
content_hash duplicates: 1
current_db_sha256: ABE5591A4300317D552C92F202049E5123D5094D97E43CF3262B251FEFD9760A
```

The live/historical case split also matches the claim:

```text
current_tests last_result distribution includes lowercase stale/pass only for
the relevant common states; historical tests contains STALE=136, PASS=135,
NOT_RUN=9, passed=1.
```

## Findings

### 1. Required: fix count-semantics drift in the report artifacts

The generated inventory reports:

```text
with_any_test_id_reassignment: 41
total_historical_distinct_file_paths: 167
```

Evidence:
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:22`
  reports `with_any_test_id_reassignment: 41`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:26`
  reports `total_historical_distinct_file_paths: 167`.
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:282`
  through `:287` compute these values from specs with any reassignment and the
  sum of per-spec distinct historical files.
- Independent read-only recomputation matched the inventory: 159 specs with
  historical paths, but 167 per-spec distinct historical paths.

The submitted bridge report instead says:

```text
with_any_test_id_reassignment: 37
total_historical_distinct_file_paths: 159
```

Evidence:
- `bridge/por-step16b-methodology-review-003.md:54` reports 37 reassignments.
- `bridge/por-step16b-methodology-review-003.md:58` reports 159 historical
  distinct file paths.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md:60`
  repeats "159 paths".

This is not only a typo in the bridge file. The methodology document's own
text later says `37/151 alpha'` and `4/4 zeta'` specs had reassignment drift
at `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md:228`,
which sums to 41 and agrees with the JSON.

Impact: the main classification decision still appears valid, but the report
does not cleanly satisfy the prior condition to separate row counts, path
counts, and distinct spec counts. Specifically, 159 is the distinct spec count
with any historical test file, not the sum of per-spec distinct historical
file paths.

Required action:
- Revise the methodology report and post-implementation bridge report so the
  count labels and values match the generated inventory.
- If both values are useful, label them separately, for example:
  `specs_with_any_historical_test_file = 159`,
  `sum_per_spec_distinct_historical_file_paths = 167`, and optionally
  `unique_historical_file_paths_across_target = 53`.
- Correct `with_any_test_id_reassignment` to 41, or split it as
  `alpha_prime = 37` and `zeta_prime = 4`.

### 2. Required: make the verification hook compatible with file safety

The post-implementation report asks Codex to run:

```text
python independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py
```

But the classifier writes the inventory file unconditionally:

- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:334`
  calls `JSON_OUT.write_text(...)`.

This automated scan is only permitted to create the new bridge review file and
make the targeted `bridge/INDEX.md` coordination update. Running the hook in
place would modify an existing Prime-created artifact, which violates the
project file-safety contract.

Impact: Codex can still verify the facts with read-only DB and JSON checks, as
done above, but the published verification hook is not safe for automated
Loyal Opposition scans.

Required action:
- Add a read-only verification mode such as `--check`/`--no-write`, or make the
  output path configurable so Codex can write outside the repo.
- Alternatively, revise the bridge report to document that rerunning the
  classifier rewrites the inventory and requires explicit owner approval under
  the file-safety contract.

## Conditions Already Satisfied

- Exhaustive classification: satisfied by inventory count sum 193 and zero
  unclassified rows.
- Explicit file-backed/no-pass category: satisfied by `zeta_prime: 4`.
- Semantic assertion handling: satisfied by separate non-null and semantic
  fields in the inventory and report.
- Current versus historical case issue: satisfied; live `current_tests` is not
  affected by historical uppercase rows.
- Isolated DELIB archive: satisfied at the evidence level. `DELIB-0712` exists
  once with `source_type=methodology_review` and `outcome=owner_decision_pending`.

## Required Action Items

1. Submit a revised bridge post-implementation report correcting the count
   drift above.
2. Correct the methodology report's count labels/values so it agrees with the
   generated JSON and direct DB recomputation.
3. Provide a file-safety-compatible verification hook or explicitly label the
   existing classifier command as a write operation requiring owner approval.

## Decision Needed From Owner

None. This NO-GO is corrective, not a rejection of the 16.B methodology result.
Once the reporting and verification-hook issues are corrected, this thread
should be eligible for VERIFIED without reworking the classifier.
