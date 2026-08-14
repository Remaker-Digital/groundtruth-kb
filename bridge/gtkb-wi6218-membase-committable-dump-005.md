REVISED
::init gtkb lo
::open build

# WI-6218 — MemBase Committable Dump (scoped, sharded, size-budgeted)

bridge_kind: prime_proposal
Document: gtkb-wi6218-membase-committable-dump
Version: 005
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: a49752e4-5a9f-4290-bceb-910693b5271f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6218
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B

target_paths: ["scripts/membase_dump.py", ".gitignore", "platform_tests/scripts/test_membase_dump.py", "config/membase-dump/dump-policy.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation; it reads the database and writes
text artifacts, adds one policy file, amends `.gitignore`, and adds one
regression-test module.

Responds to: bridge/gtkb-wi6218-membase-committable-dump-004.md

---

## Why This Refile Exists (`-005`)

`-004` recorded **NO-GO on one mechanical ground only** and stated the substance
of `-003` was reviewed and accepted, with all four `-002` Required-For-GO items
resolved and the measurement independently verified.

The block was provenance, not content: `-003` carried `author_identity: claude`,
a bare harness name with no role prefix. `bridge_lifecycle_resolver._author_role`
searches the identity string for a role token, so the bare form resolves `None`,
the operative version is classified legacy-shaped, and the typed publication
authorization refuses **any** verdict on the thread — including the GO the
reviewer had drafted.

Cause, stated plainly: the filing helper used for `-003` passed only model fields
in its author metadata and let the writer derive the identity, which produced the
bare form. The helper now passes `author_identity` and `author_harness_id`
explicitly, so this class cannot recur from that path.

**No content below this section changed from `-003`.** The table-selection policy, the
sharding design, the size budget and the sequencing stand exactly as reviewed.

## What Changed From `-001`

`-002` recorded **NO-GO on F1**: the dump as scoped would be ~786 MB and would
recreate the failure that already made `develop` unpushable. The verdict was
explicit that the design was sound and the *selection* had to change.

This revision keeps the design — deterministic text projection with a freshness
check — and adds the four things `-002` required: a table-selection policy,
sharding, a test-enforced size budget, and an explicit statement of interaction
with `WI-6138` / `WI-5431`.

The authorization citation also moves to `...-20260814B`, whose class set
(`metadata`, `repository_metadata`) is the one this thread's artifacts and
`.gitignore` amendment actually need.

## Independent Measurement

`-002`'s estimate is confirmed and extended. Measured this session against the
live database, sampling up to 200 rows per table for average serialized width:

| Table | Rows | Avg row | Est. dump text | Disposition |
|---|---:|---:|---:|---|
| `pipeline_events` | 1,667,646 | 405 B | **644.2 MB** | EXCLUDE |
| `deliberations` | 13,977 | 8,039 B | **107.2 MB** | INCLUDE (sharded) |
| `sot_registry_bridge_publication_capabilities` | 2,336 | 12,860 B | 28.6 MB | EXCLUDE |
| `assertion_runs` | 105,123 | 223 B | 22.5 MB | EXCLUDE |
| `sot_registry_transaction_journal` | 18 | 746,075 B | 12.8 MB | EXCLUDE |
| `sot_artifact_revisions` | 6,896 | 1,843 B | 12.1 MB | EXCLUDE |
| `tests` | 29,013 | 392 B | 10.9 MB | INCLUDE (sharded) |
| `test_plan_phases` | 1,433 | 4,949 B | 6.8 MB | INCLUDE |
| `work_items` | 12,425 | 563 B | 6.7 MB | INCLUDE |
| `specifications` | 10,220 | 398 B | 3.9 MB | INCLUDE |
| `documents` | 271 | 14,203 B | 3.7 MB | INCLUDE |
| `project_work_item_memberships` | 4,720 | 353 B | 1.6 MB | INCLUDE |
| `session_prompts` | 612 | 2,379 B | 1.4 MB | INCLUDE |
| `project_authorizations` | 1,009 | 1,214 B | 1.2 MB | INCLUDE |
| remaining 44 tables | — | — | < 0.8 MB each | per policy |

**Whole-database total: 868.0 MB across 58 tables** (DB file 901.5 MB). `-002`
measured ~786 MB over six tables; the gap is the three tables it did not
sample — `sot_registry_bridge_publication_capabilities`,
`sot_registry_transaction_journal` and `sot_artifact_revisions` — which add
53.5 MB between them. `sot_registry_transaction_journal` is the notable one:
**18 rows averaging 746 KB each**, i.e. large embedded payloads, not row
volume.

**Governed subset after exclusions: ~147.8 MB.** This confirms `-002`'s central
point — table filtering alone is not sufficient, because `deliberations` at
107.2 MB is 73% of the governed subset and on its own exceeds the 100 MB hard
limit.

## Corrected Scope

### 1. Table-selection policy (`config/membase-dump/dump-policy.toml`)

Selection is data, not code, so the policy is reviewable and diffable
independently of the dumper.

**Included — governed content**, the artifact classes `-001` named as the
purpose: `specifications`, `work_items`, `deliberations`, `documents`,
`project_authorizations`, `projects`, `project_work_item_memberships`, `tests`,
`test_plans`, `test_plan_phases`, `test_coverage`, `deliberation_work_items`,
`operational_procedures`, `environment_config`, `session_prompts`,
`sot_artifacts`, `flow_artifacts`, and their peers.

**Excluded — runtime telemetry and derived/rebuildable state**, each with a
recorded reason and a recoverability statement:

| Excluded table | Reason | Recoverable? |
|---|---|---|
| `pipeline_events` | runtime telemetry; no governance value | No — accepted as non-durable |
| `assertion_runs` | execution history; regenerated by running assertions | Yes, by re-running |
| `sot_registry_transaction_journal` | registry transaction payloads (746 KB/row) | No — accepted as non-durable; the resulting registry state is in `sot_artifacts` |
| `sot_registry_bridge_publication_capabilities` | derived publication capability cache | Yes, by republication |
| `sot_artifact_revisions` | revision history of registry artifacts | No — accepted as non-durable |

Answering `-002`'s explicit question: three of the five exclusions are **not**
recoverable elsewhere and are accepted as non-durable. That is a real loss and
is stated rather than glossed. If the owner or reviewer judges
`sot_artifact_revisions` or the registry journal to be governance-bearing, they
move to INCLUDE and the sharding below absorbs them — the design does not
change, only the policy row.

The policy file is the single source of the include/exclude sets; the dumper has
no hard-coded table list.

### 2. Sharding with a stable row-range key

Each included table dumps to `membase-dump/<table>/<NNNN>.sql`, chunked by a
**fixed row-count range on the table's primary ordering key** (rowid or primary
key), not by accumulated byte size.

Fixed ranges rather than size-packing is the load-bearing choice, and it is what
answers `-002` requirement 4. MemBase is append-only: new rows land at the tail.
With a stable range key, an append rewrites **only the tail chunk**; every
earlier chunk is byte-identical across re-dumps and produces no new git blob.
Size-packed chunks would reflow on every append and rewrite the whole table.

`deliberations` at 107.2 MB becomes roughly 5 chunks under the budget below;
`tests` becomes 1-2. Most included tables remain a single chunk.

### 3. Size budget enforced by test

**25 MB per emitted file**, well under the 100 MB hard limit, leaving headroom
for row-width growth inside an existing chunk range. The test suite fails if any
emitted artifact exceeds it, so growth is caught at authoring time rather than
at push time. The dumper also fails closed rather than emitting an oversized
file.

A second test asserts the **aggregate** dump stays under a stated ceiling, so
silent whole-corpus growth is visible too.

### 4. Interaction with `WI-6138` and `WI-5431`

**This lands after the object-store reclamation, not before.** `WI-6138` (P0,
open) records that `develop` is permanently unpushable because 58 commits carry
~460 MB `groundtruth.db` blobs; `WI-5431` (P1, open) records ~5 GB/day `.git`
regrowth with a 441 GB outage precedent. Committing new large artifacts onto a
branch that already cannot be pushed would compound both.

Concretely, the sequencing this proposal requests:

1. The dumper, the policy file and the tests land and run **without** committing
   a dump (scope items 1-3, 5). The `check` mode is usable immediately.
2. The **first committed dump** (scope item 6) is gated on `WI-6138`
   reclamation completing.

**Growth profile.** Steady-state governed content is ~148 MB across ~20 chunk
files. A typical session appends to `deliberations`, `work_items` and
`specifications`, touching the tail chunk of each — roughly 25 MB of changed
text per commit in the worst case, and far less in the common case where the
tail chunks are partially filled. That is a per-commit blob cost measured in
tens of MB against a repository whose current problem is 460 MB blobs per
commit, so the profile is compatible with `WI-5431`'s reclamation rather than
compounding it. The fixed-range chunking is what makes this true; without it,
every commit would rewrite ~148 MB.

### 5. Dumper and check mode (`scripts/membase_dump.py`)

`dump` / `restore` / `check` as in `-001`, with deterministic output: tables
sorted, rows ordered by the range key, stable literal formatting, LF endings, no
timestamps in the artifact body. `check` compares the on-disk dump against a
freshly generated one and reports drift without writing.

### 6. `.gitignore` negation and the first dump commit

`.gitignore` gains a negation for `membase-dump/**` so the artifacts are
tracked while `groundtruth.db` itself stays ignored (`.gitignore:180`,
unchanged). The first dump commit is gated per item 4 above.

## Spec-Derived Verification Plan

| Requirement | Test | Expected |
|---|---|---|
| `-002` F1.1 selection policy | `test_excluded_tables_never_appear` | no `INSERT INTO "pipeline_events"` (or any excluded table) in any emitted artifact |
| `-002` F1.1 policy is data | `test_dumper_has_no_hardcoded_table_list` | the include/exclude sets come from `dump-policy.toml`; the dumper module contains no literal table-name list |
| `-002` F1.2 sharding | `test_deliberations_shards_into_multiple_chunks` | `deliberations` emits > 1 chunk; every chunk is non-empty |
| `-002` F1.3 size budget | `test_no_emitted_file_exceeds_budget` | every emitted file < 25 MB; **suite fails if violated** |
| `-002` F1.3 aggregate ceiling | `test_aggregate_dump_under_ceiling` | total emitted bytes under the stated ceiling |
| `-002` F1.4 growth profile | `test_append_rewrites_only_tail_chunk` | after inserting a row into a fixture table, exactly one chunk file changes and all earlier chunks are byte-identical |
| determinism | `test_dump_is_byte_reproducible` | two consecutive dumps of an unchanged DB are byte-identical |
| round-trip | `test_restore_round_trips_governed_tables` | dump → restore into an empty DB → re-dump is byte-identical |
| freshness | `test_check_reports_drift_without_writing` | `check` detects a mutated row and leaves the dump untouched |
| fail-closed | `test_dumper_refuses_to_emit_oversized_chunk` | a synthetic oversized row range raises rather than writing |

Fixture databases are used for the behavioral tests; the live DB is used only
for the read-only size measurement above.

## Specification Links

- `GOV-STANDING-BACKLOG-001` v5 — the governed content this dump exists to make
  clonable.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — `check` mode is the freshness
  contract; the size figures above are fresh measurements, not carried-forward
  estimates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifacts over transient
  state; the exclusion policy records which state is deliberately not durable.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — bridge audit-trail discipline governing
  this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — protocol gates
  governing this document.

## Requirement Sufficiency

Existing requirements sufficient. The exclusion policy makes an explicit
durability judgement about five tables; that judgement is recorded in the policy
file and surfaced for review here rather than being asserted as a requirement.
If the reviewer or owner disagrees with any row, it moves between the sets
without a design change.

## Owner Decisions / Input

- Owner decision of record `DELIB-20260814-WI6218-DUMP-STRATEGY-AND-WI6220-BATCHED-APPROVALS`:
  deterministic SQL dump is the selected strategy. Unchanged by this revision —
  the strategy stands; only the selection narrows.
- Owner decisions `DELIB-20260814-PHASE2-PAUTH-BRIDGE-MUTATION-CLASS` and
  `DELIB-20260814-PHASE2-PAUTH-BRIDGE-CLASS-NON-B` added the `bridge` mutation
  class to the Phase-2 execution authorizations, permitting this thread's
  eventual report.
- **Surfaced for owner awareness, not requested as a decision now:** three
  excluded tables are not recoverable elsewhere and are accepted as
  non-durable. If the owner wants any of them preserved, that is a policy-row
  change, and the sequencing gate below is the natural moment to raise it.
- **Sequencing dependency:** the first committed dump is gated on `WI-6138`
  reclamation. If the owner wants the dump committed sooner, that is a blocking
  owner decision and would be raised via AskUserQuestion at that point — it is
  not being requested in this proposal.

## Prior Deliberations

- `bridge/gtkb-wi6218-membase-committable-dump-002.md` — the NO-GO this
  revision answers; F1's four requirements map to scope items 1-4.
- `DELIB-20260814-WI6218-DUMP-STRATEGY-AND-WI6220-BATCHED-APPROVALS` — the
  owner strategy decision.
- `WI-6138` (P0, open) — `develop` permanently unpushable; the gate for the
  first committed dump.
- `WI-5431` (P1, open) — `.git` object-store regrowth; the growth-profile
  constraint the fixed-range chunking is designed against.
- `WI-6275` — registry `source_sha256` drift, filed this session; unrelated to
  this thread but shares the "the registry is large and derived" theme relevant
  to the exclusion policy.

## Cross-Harness Disposition

`scripts/membase_dump.py` is a shared project script, not a per-harness
surface, and no harness configuration file changes. No harness-specific
behavior is introduced, so no projection or waiver is required.

## Risk / Rollback

The excluded tables are the risk: three are accepted as non-durable, so a
catastrophic loss of `groundtruth.db` would lose them. That is a narrowing of
`-001`'s implied guarantee and is stated plainly so the reviewer can weigh it
against the 868 MB the full dump would cost.

The size budget and the fail-closed emitter mean the dumper cannot reproduce the
`WI-6138` failure mode even if the policy is later widened carelessly — the test
suite fails first.

Rollback is reverting the script, the policy file and the `.gitignore`
negation; no committed dump exists to unwind until the item-4 gate is cleared.

## Recommended Commit Type

`feat` — a new deterministic dump service plus its policy and tests. This is a
new capability surface, not a repair, so `feat` is the honest type despite the
work originating from a defect-driven need.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
