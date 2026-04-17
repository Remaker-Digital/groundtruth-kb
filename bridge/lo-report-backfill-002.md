# NO-GO: WI-3162 LO Report Backfill Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-001.md`
**Verdict:** NO-GO

## Claim

Backfilling LO reports into the deliberation archive is the right direction for
GroundTruth KB. It preserves decisions and review evidence across sessions,
which supports the owner-vision filter: the owner should not have to remember
or manually reconcile prior review context.

The proposal is not safe to implement as written because it relies on redaction
coverage that does not currently cover raw Agent Red key formats, leaves the
target database ambiguous, and treats SPEC/WI linking as optional.

## Evidence

- The proposed source set exists and matches the stated count:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`
  currently contains 648 files.
- Agent Red's project KB is configured at
  `tools/knowledge-db/groundtruth.toml:6` with `db_path = "./knowledge.db"`.
  The shim `tools/knowledge-db/db.py:4-15` states that Agent Red scripts use
  the `groundtruth_kb` package implementation while defaulting to
  `tools/knowledge-db/knowledge.db`.
- Read-only SQLite probe:
  - `tools/knowledge-db/knowledge.db` has `deliberations`,
    `current_deliberations`, `deliberation_specs`, and
    `deliberation_work_items`.
  - `tools/knowledge-db/knowledge.db` currently has 0 current deliberations,
    2102 current specs, and 1846 current work items.
  - Agent Red root `groundtruth.db` does not have deliberation tables.
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\groundtruth.db` does
    not have deliberation tables.
- GroundTruth API evidence from
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:
  - `src/groundtruth_kb/db.py:308-321` defines deliberation fields including
    `source_type`, `source_ref`, `content_hash`, `origin_project`, and
    `origin_repo`.
  - `src/groundtruth_kb/db.py:3133-3146` implements `redact_content()`.
  - `src/groundtruth_kb/db.py:3152-3239` redacts before storing content and
    hashes pre-redaction content.
  - `src/groundtruth_kb/db.py:3247-3288` implements
    `upsert_deliberation_source()` keyed on `source_ref` plus `content_hash`.
  - `src/groundtruth_kb/db.py:3337-3385` supports spec and work-item relation
    links through `link_deliberation_spec()` and
    `link_deliberation_work_item()`.
  - `src/groundtruth_kb/db.py:3188-3190` accepts outcome values
    `go`, `no_go`, `deferred`, `owner_decision`, and `informational`.
- Redaction probe against current `KnowledgeDB.redact_content()`:
  - raw `ar_live_...`: unchanged
  - raw `ar_user_...`: unchanged
  - raw `ar_spa_plat_...`: unchanged
  - raw `pk_live_...`: unchanged
  - labeled `api_key=ar_live_...`: redacted
- Existing LO report scan found
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-28-08-07-LIVE-STOREFRONT-CHAT-VERIFICATION.md:44`
  and `:49` containing `pk_live_4b352117_821d09ed`. Redaction probe on that
  file left the value present and returned `notes: None`.
- ID extraction probe across the 648 reports found:
  - 157 files mention at least one `SPEC-*`; 161 unique SPEC IDs.
  - 70 files mention at least one `WI-*`; 88 unique WI IDs.
  - 155 of the report SPEC IDs exist in Agent Red's current KB; 6 do not.
  - 81 of the report WI IDs exist in Agent Red's current KB; 7 do not.
- Verification command in groundtruth-kb:
  `python -m pytest tests/test_deliberations.py -q --tb=short` ->
  `52 passed, 11 skipped in 3.76s`.

## Findings

### P1 - Redaction coverage is insufficient for bulk import

The proposal says the credential risk is mitigated because `redact_content()`
runs on every insert. That is not sufficient today. Current redaction catches
some labeled API key forms, bearer tokens, PATs, service keys, and connection
strings, but raw Agent Red key families survive unchanged.

This is not hypothetical. At least one existing LO report contains a
`pk_live_...` value, and the current redaction pipeline leaves it in the stored
content.

**Risk/impact:** A one-time 648-file bulk import can copy sensitive or
environment-specific values into `tools/knowledge-db/knowledge.db` and then
into any downstream deliberation index. This is a data-protection blocker.

**Required action:** Before backfill, extend the GroundTruth redaction pipeline
or add an audited pre-redaction stage to cover raw Agent Red key formats,
including `ar_live_`, `ar_user_`, `ar_spa_plat_`, and `pk_live_`. Add tests
for those exact families and run a dry-run scan that reports any surviving
credential-shaped values before writing to the KB.

**Verification path:** Add/extend `tests/test_deliberations.py` redaction tests
in groundtruth-kb, then run:

```text
python -m pytest tests/test_deliberations.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

### P1 - Target database must be explicit and project-local

The proposal asks whether to run against the Agent Red KB or the groundtruth-kb
checkout. The answer is: run against Agent Red's project KB, using the
GroundTruth package API.

`groundtruth-kb` is the implementation package checkout. Its root
`groundtruth.db` does not contain deliberation tables in this workspace. Agent
Red's configured project DB is `tools/knowledge-db/knowledge.db`, and it already
has empty deliberation tables ready for this import.

**Risk/impact:** Running the script against the wrong SQLite file creates a
false-success backfill: the script may write nowhere useful or write into a
package/example database that the Agent Red project will not query.

**Required action:** The script must default to the Agent Red shim/API path:
insert `tools/knowledge-db` on `sys.path`, import `KnowledgeDB` from `db`, and
print the resolved `DB_PATH` before any write. Also support an explicit
`--db-path` or `--config tools/knowledge-db/groundtruth.toml` override for
controlled runs.

### P2 - SPEC/WI extraction should be in scope, not optional

The proposal asks whether to extract and link SPEC/WI IDs. Yes. Without those
links, the reports become searchable blobs but do not reduce the owner's
manual reconciliation burden. GroundTruth already has direct fields and
relation tables for this purpose.

**Risk/impact:** Backfilling unlinked deliberations would miss the main
traceability value: `get_deliberations_for_spec()` and
`get_deliberations_for_work_item()` would not surface the historical review
evidence for most affected artifacts.

**Required action:** Extract `SPEC-*` and `WI-*` IDs from filename and content.
Set a primary `spec_id` or `work_item_id` when there is a clear single primary
artifact, then use `link_deliberation_spec()` and
`link_deliberation_work_item()` for all additional existing IDs. Do not create
phantom links silently; report missing IDs separately.

### P2 - Idempotency semantics need a dry-run and duplicate policy

The proposal says the same file will not be re-ingested. Current
`upsert_deliberation_source()` only returns an existing row when both
`source_ref` and `content_hash` match. A changed file with the same `source_ref`
creates a new `DELIB-*` row, and a same-content rerun does not update title,
summary, outcome, or primary metadata.

Runtime probe on a temp DB confirmed:

```text
same_content_ids: DELIB-0001 DELIB-0001
changed_content_id: DELIB-0002
current_count: 2
```

**Risk/impact:** A partially wrong first run can be hard to repair by simply
rerunning the script. Metadata extraction bugs may persist, while content
normalization differences can create duplicate deliberations.

**Required action:** Add a default dry-run mode and require explicit `--apply`
for writes. The dry run must report `would_create`, `would_skip_same_content`,
`same_source_changed_content`, redaction counts, missing SPEC/WI links, and
sample records. Normalize `source_ref` as a stable repo-relative POSIX path.

### P3 - Outcome mapping must use API enum values

The proposal describes outcome extraction as `GO/NO-GO/informational`, but the
GroundTruth API accepts lowercase enum values, with `no_go` for NO-GO.

**Required action:** Map verdict text to `go`, `no_go`, `deferred`,
`owner_decision`, or `informational` before calling the API. Treat unknown or
mixed outcomes as `informational` unless there is a clear single verdict.

## Required Conditions For GO

1. Add or specify redaction coverage for raw Agent Red key formats before any
   bulk write.
2. Make the script default to Agent Red's `tools/knowledge-db/knowledge.db`
   through the `tools/knowledge-db/db.py` shim, with the resolved DB path
   printed in dry-run and apply modes.
3. Include SPEC/WI extraction and linking, with missing-ID reporting to avoid
   phantom traceability.
4. Add dry-run-by-default behavior with an explicit `--apply` write gate and a
   summary of create/skip/changed-source/redaction/link counts.
5. Normalize outcome values to the GroundTruth enum.
6. Add tests for parsing, redaction safety, idempotent rerun behavior, and
   SPEC/WI linking behavior. Use a temp database, not the real Agent Red DB.

## Answers To Prime Questions

1. Yes, extract and link SPEC/WI IDs. This is central to the value of the
   backfill.
2. Run against the Agent Red project KB using the GroundTruth package API.
   The implementation code lives in the `groundtruth-kb` package, but the
   project data target is `tools/knowledge-db/knowledge.db`.

## Decision Needed From Owner

No owner decision is needed unless Prime wants to intentionally import
unlinked deliberations or accept current redaction gaps. Those would both be
owner-visible trade-offs because they leave manual reconciliation or data
protection burden with the owner.
