GO

# Proposal Review: POR Step 16.C Stream D Phantom WI Creation Revision 2

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16c-stream-d-phantom-wi-creation-001.md`
- `bridge/por-step16c-stream-d-phantom-wi-creation-002.md`
- `bridge/por-step16c-stream-d-phantom-wi-creation-003.md`
- `bridge/por-step16c-stream-d-phantom-wi-creation-004.md`
- `bridge/por-step16c-stream-d-phantom-wi-creation-005.md`
- `bridge/INDEX.md` entry `por-step16c-stream-d-phantom-wi-creation`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `groundtruth.db`, opened read-only for evidence queries
- Installed `groundtruth_kb.db.KnowledgeDB` API source, opened read-only

## Claim

The revised Stream D proposal is approved for implementation.

The -005 revision resolves both blocking findings from -004:

1. It replaces the `DISTINCT source_spec_id` coverage check with a grouped
   per-spec count check and requires each target spec to have exactly one
   current open hygiene WI.
2. It revises mutation-scope expectations to allow the `pipeline_events`
   `wi_created` audit row that `KnowledgeDB.insert_work_item()` creates for
   each new WI.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched current
deliberations before review.

Read-only DB results:

```text
TERM 16.C COUNT 2
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md

TERM phantom WI creation COUNT 0
TERM gamma_prime COUNT 0
TERM delta_prime COUNT 0

Explicit cited IDs:
  DELIB-0711 | owner_conversation | owner_decision | S297 | Owner Decision: SPEC-GTKB-SCOPE test-evidence invariant exception | bridge/por-step16a-verified-spec-closure-005.md
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md
```

I found no separate current deliberation for this exact Stream D bridge item
beyond the cited 16.B/16.C decisions.

## Evidence Verified

The safe classifier check still reproduces the Step 16.B counts without DB
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

DB hash at review time:

```text
SHA256 groundtruth.db EA634D9519D83F877C86DC93EF78F6FE6CCC5452CD0EC6D575CB481E0BB67CFE
```

Independent inventory and read-only DB reconciliation:

```text
inventory_stream_d_count 34
inventory_stream_d_categories {'delta_prime': 15, 'gamma_prime': 19}
missing_from_inventory []
current_spec_count 34
current_spec_status_counts {'implemented': 34}
current_spec_type_counts {'requirement': 34}
missing_from_current_specs []
target_current_wis_any_origin 34
target_current_hygiene_wis 0
target_current_open_hygiene_wis 0
strict_group_rows 0
strict_duplicate_groups []
max_wi_4digit_query WI-3184
pipeline_events_count 3592
pipeline_events_wi_created_count 22
```

The inventory's summary records the governing classifier totals at
`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:7`
through `:13`, including 15 `delta_prime` and 19 `gamma_prime` specs.

The umbrella GO condition requires Stream D to create exactly 34 hygiene WIs,
one per `gamma_prime` or `delta_prime` spec, with `origin=hygiene` and a durable
source-spec link (`bridge/por-step16c-implemented-untested-remediation-002.md:198`
through `:204`).

The -005 revision addresses the prior one-to-one verification gap:
- It defines sequential WI allocation from `WI-3185` through `WI-3218` with
  per-WI collision checks (`bridge/por-step16c-stream-d-phantom-wi-creation-005.md:64`
  through `:67`).
- It uses the installed `insert_work_item()` call shape with `id`, `title`,
  `origin`, `component`, `resolution_status`, `changed_by`, `change_reason`,
  `description`, `source_spec_id`, `priority`, and `stage`
  (`bridge/por-step16c-stream-d-phantom-wi-creation-005.md:69` through `:92`).
- It fails fast if a target spec already has more than one current open hygiene
  WI (`bridge/por-step16c-stream-d-phantom-wi-creation-005.md:97` through
  `:120`).
- It verifies coverage with grouped SQL and asserts both 34 target groups and
  `open_hygiene_count == 1` for every group
  (`bridge/por-step16c-stream-d-phantom-wi-creation-005.md:122` through `:148`).

Installed API evidence confirms the mutation-scope revision is necessary and
correct:
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2822`
  through `:2838` define the required `insert_work_item()` signature.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2853`
  through `:2877` insert the `work_items` row.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2878`
  through `:2896` record a `wi_created` event and commit.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:3752`
  through `:3755` insert into `pipeline_events`.

The proposal now permits exactly those audit mutations: `work_items` plus one
`pipeline_events` `wi_created` row per created WI, while forbidding
specification, test, assertion, deliberation, document, and unrelated table
mutations (`bridge/por-step16c-stream-d-phantom-wi-creation-005.md:182` through
`:207`).

## Findings

No blocking findings remain.

## GO Conditions

1. Implement only the -005 plan: create the script under
   `independent-progress-assessments/spec-hygiene/scripts/create_stream_d_wis.py`
   and mutate only `groundtruth.db`.
2. Use the repo/API path that calls `KnowledgeDB.insert_work_item()`; do not
   bypass the audit event path with raw SQL inserts.
3. Post-implementation report must include the full `{spec_id -> wi_id ->
   title}` mapping for all 34 target specs.
4. Post-implementation report must include the grouped SQL result showing
   exactly 34 rows and `open_hygiene_count = 1` for every target spec.
5. Post-implementation report must include the DB hash bracket and mutation
   audit showing only `work_items` and matching `pipeline_events.wi_created`
   rows changed.
6. Re-run the classifier in `--check` mode after implementation and confirm the
   gamma/delta counts remain `gamma_prime=19` and `delta_prime=15`.

## Decision Needed From Owner

None. Prime may proceed under the GO conditions above.

