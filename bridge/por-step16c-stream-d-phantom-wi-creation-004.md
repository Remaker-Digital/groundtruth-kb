NO-GO

# Proposal Review: POR Step 16.C Stream D Phantom WI Creation Revised

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16c-stream-d-phantom-wi-creation-001.md`
- `bridge/por-step16c-stream-d-phantom-wi-creation-002.md`
- `bridge/por-step16c-stream-d-phantom-wi-creation-003.md`
- `bridge/INDEX.md` entry `por-step16c-stream-d-phantom-wi-creation`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `bridge/spec-hygiene-untested-verified-008.md`
- `bridge/spec-hygiene-spa-remediation-006.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `groundtruth.db`, opened read-only for evidence queries
- Installed `groundtruth_kb.db.KnowledgeDB` API source, opened read-only

## Claim

The revised Stream D proposal is close, but not approved for implementation yet.

The -003 revision fixes the prior executable API gap, defines deterministic WI ID
allocation, and correctly anchors the 34 target specs in the 16.B inventory.
However, two remaining exit-contract defects would make post-implementation
verification weaker than the umbrella requires:

1. The proposed "exactly one current open hygiene WI per Stream D source spec"
   invariant is not actually enforced by the proposed SQL.
2. The "only `work_items` table mutations" exit criterion is impossible when
   using the approved `KnowledgeDB.insert_work_item()` API, because that API
   also records `pipeline_events` audit rows.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched current deliberations
before review.

Read-only DB results:

```text
TERM 16.C COUNT 2
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md

Explicit cited IDs:
  DELIB-0711 | owner_conversation | owner_decision | S297 | Owner Decision: SPEC-GTKB-SCOPE test-evidence invariant exception | bridge/por-step16a-verified-spec-closure-005.md
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md
```

I found no separate current deliberation for this exact Stream D bridge item
beyond the cited 16.B/16.C decisions.

## Evidence Verified

The classifier still reproduces the governing Step 16.B counts without DB
mutation:

```text
python independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py --check

--check mode: no files written
target_count: 193
category_counts: {'alpha_prime': 151, 'beta_prime': 4, 'delta_prime': 15, 'gamma_prime': 19, 'zeta_prime': 4}
assertions non_null=170 semantically_non_empty=164
with_any_historical_test_file (distinct specs): 159
sum_per_spec_distinct_historical_file_paths: 167
unique_historical_file_paths_across_target: 53
with_any_test_id_reassignment (total specs): 41
with_any_test_id_reassignment_by_category: {'alpha_prime': 37, 'zeta_prime': 4}
DB hash pre==post: True
```

Independent inventory and DB reconciliation:

```text
inventory_stream_d_count 34
inventory_stream_d_categories {'delta_prime': 15, 'gamma_prime': 19}
current_spec_count 34
current_spec_status_counts {'implemented': 34}
current_spec_type_counts {'requirement': 34}
missing_specs []
target_current_wis_any_origin 34
target_current_hygiene_wis 0
target_current_open_hygiene_wis 0
max_wi_4digit_query WI-3184
max_wi_numeric_query WI-3184
sha256 EA634D9519D83F877C86DC93EF78F6FE6CCC5452CD0EC6D575CB481E0BB67CFE
```

The inventory itself records the governing counts at
`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:7`
through `:13`, including 15 `delta_prime` and 19 `gamma_prime` specs. Example
target entries begin at `:4627` for `SPEC-1653` (`delta_prime`) and `:4653` for
`SPEC-1707` (`gamma_prime`).

Current API evidence:
- `tools/knowledge-db/db.py:42` points the Agent Red shim at repo-root
  `groundtruth.db`.
- `tools/knowledge-db/db.py:98` defines the Agent Red `KnowledgeDB` wrapper over
  the installed `groundtruth_kb.db.KnowledgeDB`.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2822`
  through `:2838` define the required `insert_work_item()` signature.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2879`
  through `:2896` record a `wi_created` event and commit the transaction.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:3752`
  through `:3755` show `_record_event()` inserts into `pipeline_events`.

Precedent WI rows support the proposed call shape:

```text
WI-3178..WI-3182: origin=hygiene, component=Backend, resolution_status=open, priority=low, stage=created
WI-3183..WI-3184: origin=hygiene, component=knowledge-db, resolution_status=open, priority=medium, stage=created
pipeline_events count 3592
pipeline_events wi_created count 22
```

## Findings

### Finding 1: The proposed post-condition does not enforce one-to-one coverage

Severity: blocking.

The revised proposal states that it enforces "exactly one current open hygiene WI
per Stream D source spec" (`bridge/por-step16c-stream-d-phantom-wi-creation-003.md:175`
through `:177`). But the SQL immediately above it selects only `DISTINCT
source_spec_id` and asserts `len(covered) == 34`
(`bridge/por-step16c-stream-d-phantom-wi-creation-003.md:164` through `:173`).

That proves every target spec has at least one open hygiene WI. It does not
prove that each target has exactly one. A duplicated open hygiene WI for one
target would still count as one distinct `source_spec_id`.

This matters because the umbrella GO condition requires "exactly 34 hygiene WIs,
one per `gamma_prime` or `delta_prime` spec"
(`bridge/por-step16c-implemented-untested-remediation-002.md:198` through
`:204`). The DB schema does not enforce uniqueness by `(source_spec_id, origin,
resolution_status)`: `current_work_items` is a latest-version view by WI `id`,
and `work_items` is unique only on `(id, version)`.

Current DB state has zero target hygiene WIs, so a clean first run should be
simple:

```text
target_current_hygiene_wis 0
target_current_open_hygiene_wis 0
proposed_distinct_open_hygiene_coverage 0
strict_open_hygiene_group_count 0 duplicate_groups []
```

Risk/impact: post-implementation verification could accept duplicate open
hygiene WIs while still claiming the one-to-one umbrella condition is satisfied.

Required action: revise the pre-flight and post-condition so they fail on
duplicates. The post-condition should verify both the total row count and the
per-spec count, for example:

```sql
SELECT source_spec_id, COUNT(*) AS open_hygiene_count
FROM current_work_items
WHERE source_spec_id IN ({34_spec_ids})
  AND origin = 'hygiene'
  AND resolution_status = 'open'
GROUP BY source_spec_id;
```

Acceptance should require exactly 34 grouped rows and every
`open_hygiene_count = 1`. The pre-flight should similarly fail fast if a target
already has more than one current open hygiene WI.

### Finding 2: The mutation-scope exit criterion contradicts the required API

Severity: blocking.

The proposal's sharpened exit criteria require the DB hash bracket to document
"only `work_items` table mutations (no spec, test, or other-table changes)"
(`bridge/por-step16c-stream-d-phantom-wi-creation-003.md:224` through `:225`).

But the same proposal correctly requires use of `KnowledgeDB.insert_work_item()`
(`bridge/por-step16c-stream-d-phantom-wi-creation-003.md:90` through `:117`).
The installed API inserts the `work_items` row and then records a lifecycle event
before commit:

```text
groundtruth_kb/db.py:2879-2896 insert_work_item() calls _record_event(... "wi_created" ...)
groundtruth_kb/db.py:3752-3755 _record_event() INSERTs into pipeline_events
```

Risk/impact: a correct implementation through the repo API will necessarily
change `pipeline_events` in addition to `work_items`. As written, the post-impl
report cannot satisfy the proposal's own exit criterion unless Prime bypasses
the API with raw SQL, which would be worse because it would skip the KB audit
path.

Required action: revise the mutation-scope exit criterion to allow the expected
audit mutations:

```text
Allowed DB table mutations: work_items rows for created WIs plus one
pipeline_events row with event_type='wi_created' per created WI. No mutations to
specifications, tests, test_coverage, assertion_runs, or unrelated tables.
```

The post-impl report should include the created WI IDs and matching
`pipeline_events.artifact_id` rows, or explicitly state the event-count delta.

## Required Action Items

1. Replace the distinct-source post-condition with a grouped one-to-one check:
   exactly 34 current open hygiene WI rows, exactly one for each Stream D spec.
2. Make the pre-flight fail fast on duplicate current open hygiene WIs for any
   target source spec.
3. Revise the mutation-scope exit criterion to permit the expected
   `pipeline_events` audit rows created by `KnowledgeDB.insert_work_item()`,
   while still forbidding spec/test/assertion/unrelated table mutations.
4. Resubmit as the next revised bridge file.

## Decision Needed From Owner

None. This is a mechanical verification-contract correction for Prime before
implementation.
