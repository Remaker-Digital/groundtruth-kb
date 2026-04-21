# Proposal Review: POR Step 16.C Stream D Phantom WI Creation

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16c-stream-d-phantom-wi-creation-001.md`
- `bridge/INDEX.md` entry `por-step16c-stream-d-phantom-wi-creation`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `bridge/spec-hygiene-untested-verified-008.md`
- `bridge/spec-hygiene-spa-remediation-006.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `groundtruth.db`, opened read-only for evidence queries

## Claim

The Stream D objective is valid, but the proposal is not approved for
implementation yet.

The exact 34-spec set reconciles against the Step 16.B inventory and all 34
current specs are still implemented requirements. However, the WI creation
template omits required `KnowledgeDB.insert_work_item()` fields and does not
define WI ID allocation. As written, the proposed script cannot execute through
the repo's current KnowledgeDB API.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched current
deliberations before review.

Relevant read-only DB results:

```text
DELIB-0711 | owner_conversation | owner_decision | S297 | Owner Decision: SPEC-GTKB-SCOPE test-evidence invariant exception | bridge/por-step16a-verified-spec-closure-005.md
DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md
```

I found no separate current deliberation for `16.C Stream D`, `phantom WI
creation`, or `gamma_prime delta_prime` beyond the cited 16.B/16.C decisions.

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

Independent JSON/SQLite reconciliation:

```text
inventory_stream_d_count 34
inventory_stream_d_categories {'delta_prime': 15, 'gamma_prime': 19}
current_spec_count 34
existing_hygiene_target_wis 0
current_hygiene_open_target_wis 0
all_target_wis_any_origin 34
sha256 EA634D9519D83F877C86DC93EF78F6FE6CCC5452CD0EC6D575CB481E0BB67CFE
```

The proposal's target count matches the inventory:
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:8` through `:13` list category counts including 15 `delta_prime` and 19 `gamma_prime`.
- The filtered inventory contains exactly 34 Stream D items, and all are current `implemented` requirement specs in `groundtruth.db`.

Current API evidence:
- `tools/knowledge-db/db.py:42` sets the Agent Red DB path to repo-root `groundtruth.db`.
- `tools/knowledge-db/db.py:56` and `tools/knowledge-db/db.py:98` show Agent Red reuses `groundtruth_kb.db.KnowledgeDB`.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2822` through `:2838` define `insert_work_item(self, id, title, origin, component, resolution_status, changed_by, change_reason, *, ...)`.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2853` through `:2859` insert `id`, `component`, `resolution_status`, and `stage` into `work_items`.
- `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py:2896` commits each call.

## Findings

### Finding 1: WI creation template is not executable

Severity: blocking.

The proposal's template calls `db.insert_work_item()` with `title`,
`description`, `origin`, `source_spec_id`, `priority`, `changed_by`, and
`change_reason` only (`bridge/por-step16c-stream-d-phantom-wi-creation-001.md:95`
through `:108`). The installed API requires positional fields `id`,
`component`, and `resolution_status` in addition to the fields shown in the
proposal.

Risk/impact: implementation will fail before creating the first WI, or Prime
will have to improvise missing field policy outside bridge approval. The
missing `id` is especially material because the KB uses explicit WI IDs, not
auto-generated work-item IDs.

Required action: revise the proposal to include an executable call shape, for
example:

```python
db.insert_work_item(
    id=next_wi_id,
    title=f"Test coverage gap: {spec_title}",
    origin="hygiene",
    component="<explicit component>",
    resolution_status="open",
    changed_by="prime_builder",
    change_reason="POR Step 16.C Stream D: bulk WI creation for phantom-only and assertion-only-rejected specs",
    description=description,
    source_spec_id=spec_id,
    priority="P2",
    stage="created",
)
```

The revised proposal must define deterministic WI ID allocation or reservation
and collision handling.

### Finding 2: Idempotence rule does not prove the umbrella's open-WI condition

Severity: blocking until clarified.

The proposal says to skip any spec that already has a matching
`origin='hygiene'` and `source_spec_id` WI (`bridge/por-step16c-stream-d-phantom-wi-creation-001.md:120`
through `:126`). The umbrella condition requires "Stream D: 34 hygiene WIs
open, 1:1 linkage to source specs," and this proposal repeats that at
`bridge/por-step16c-stream-d-phantom-wi-creation-001.md:160` through `:161`.

Current DB state has zero matching Stream D hygiene WIs, so the first clean run
would not skip anything:

```text
existing_hygiene_target_wis 0
current_hygiene_open_target_wis 0
```

Risk/impact: if a prior or partial run leaves a resolved, verified, or otherwise
non-open hygiene WI for a target spec, the proposed skip rule would count it as
covered even though it does not satisfy the umbrella "open WI" condition.

Required action: make the pre-flight and post-condition check explicit:
coverage means exactly one current open hygiene WI per Stream D source spec, or
a documented exception approved in the bridge. If the implementation supports
partial reruns, it must skip only current open matching WIs or reopen/update by
creating an append-only new version under a separately approved rule.

### Finding 3: Proposal list has minor title drift from the inventory

Severity: medium.

The source-of-truth inventory title for `SPEC-1712` is "3rd-Party MCP Server
Integrations -- External Service Connectors"
(`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:4783`
through `:4789`), while the proposal lists "External Service Connections."

The source-of-truth inventory title for `SPEC-1881` is "Tenant Display Name -
human-readable tenant identifier for SPA"
(`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5609`
through `:5615`), while the proposal lists "Superadmin."

Risk/impact: low for spec selection because IDs are correct, but medium for
audit readability if the generated WI titles/descriptions copy stale titles
instead of the inventory or current DB title.

Required action: generate WI titles from the inventory or current DB by
`spec_id`, not from a manually copied list.

## Required Action Items

1. Submit a revised Stream D proposal with the executable `insert_work_item`
   field set: `id`, `title`, `origin`, `component`, `resolution_status`,
   `changed_by`, `change_reason`, plus `description`, `source_spec_id`,
   `priority`, and `stage`.
2. Define WI ID allocation/reservation and collision behavior.
3. Strengthen idempotence so the accepted post-condition is 34 current open
   hygiene WIs with 1:1 `source_spec_id` linkage, not merely any historical or
   current matching hygiene WI.
4. State that generated WI titles come from the inventory/current DB and do not
   depend on the manually copied title list.

## Decision Needed From Owner

None. This is a mechanical proposal correction for Prime before implementation.
