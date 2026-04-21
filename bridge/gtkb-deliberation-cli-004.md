# GO: GroundTruth-KB Deliberation CLI Revised Proposal Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed proposal chain:** `bridge/gtkb-deliberation-cli-001.md`, `bridge/gtkb-deliberation-cli-002.md`, `bridge/gtkb-deliberation-cli-003.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO, with implementation conditions.

The revised proposal resolves the two blocking API-contract mismatches from
the prior NO-GO. Splitting append-only `add` from idempotent `upsert` now
matches the existing `KnowledgeDB` API, and the default `search` behavior now
preserves SQLite text fallback instead of making the CLI less capable than the
Python API.

Prime may implement, but the conditions below must be honored before the
post-implementation review can be VERIFIED.

## Evidence Reviewed

- Current `gt deliberations` CLI exposes only `rebuild-index`:
  `src/groundtruth_kb/cli.py:667-689`.
- `insert_deliberation()` requires caller-supplied `id`, `summary`,
  `changed_by`, and `change_reason`: `src/groundtruth_kb/db.py:3917-3926`.
- `upsert_deliberation_source()` has no `id` parameter and auto-generates a
  new `DELIB-NNNN` when no matching source/content hash exists:
  `src/groundtruth_kb/db.py:4012-4051`.
- Existing tests prove upsert ID generation and idempotence:
  `tests/test_deliberations.py:519-596`.
- `search_deliberations()` explicitly supports ChromaDB semantic search with
  SQLite LIKE fallback and annotates result rows with `search_method`:
  `src/groundtruth_kb/db.py:4301-4374`.
- Existing fallback tests cover text-match search and stable result fields:
  `tests/test_deliberations.py:653-717` and
  `tests/test_deliberations.py:752-778`.
- Link methods do not validate target existence:
  `src/groundtruth_kb/db.py:4132-4150`; lookup helpers exist at
  `src/groundtruth_kb/db.py:980-983` and `src/groundtruth_kb/db.py:2807-2809`.
- Local repo state note: target checkout had unrelated untracked
  `_site_verify/`; Codex did not modify it.

## Findings

### 1. GO - `add` / `upsert` split resolves the prior HIGH finding

**Claim:** Revised proposal splits append-only writes into
`gt deliberations add --id ...` and idempotent source-content writes into
`gt deliberations upsert` with no `--id` flag.

**Evidence:** This now matches the DB signatures:
`insert_deliberation(id=...)` at `src/groundtruth_kb/db.py:3917-3926` and
`upsert_deliberation_source(source_type, source_ref, content, **kwargs)` at
`src/groundtruth_kb/db.py:4012-4018`.

**Risk/impact:** Low. The API boundary is now coherent.

**Required implementation condition:** Keep `upsert --id` unavailable and
covered by a Click exit-2 test as proposed.

### 2. GO - Default search fallback is now aligned with the stable API

**Claim:** Revised proposal makes default `gt deliberations search` call
`KnowledgeDB.search_deliberations()` and preserve fallback results.

**Evidence:** The DB method documents and implements semantic search followed
by SQLite LIKE fallback at `src/groundtruth_kb/db.py:4301-4374`.

**Risk/impact:** Low if the CLI does not add its own ChromaDB requirement on
the default path.

**Required implementation condition:** The base-install CLI search test must
expect a successful `text_match` path, not an install error.

### 3. MEDIUM - `--semantic-only` must be defined as a real no-fallback mode

**Claim:** Revised proposal adds `--semantic-only` as an opt-in failure mode
when semantic search is unavailable.

**Evidence:** The only public DB search method currently falls back to SQLite
LIKE when ChromaDB is unavailable, empty, throws, or returns no relevant
semantic result: `src/groundtruth_kb/db.py:4314-4357`. Therefore a CLI flag
called `--semantic-only` cannot be implemented by blindly calling
`search_deliberations()` and trusting its return value.

**Risk/impact:** If the flag is not explicitly enforced, scripts asking for
semantic-only behavior can silently receive `search_method="text_match"`.

**Required implementation condition:** Implement and test an explicit
contract:

- either `--semantic-only` fails when ChromaDB is unavailable and also rejects
  text-match fallback rows, or
- rename the flag to something narrower such as `--require-chromadb` and
  document that text fallback may still occur after semantic search yields no
  relevant result.

### 4. MEDIUM - `upsert` cannot report `inserted` versus `matched` from the DB return alone

**Claim:** Revised proposal defaults to output such as
`upsert: inserted` versus `upsert: matched`.

**Evidence:** `upsert_deliberation_source()` returns only the deliberation row
for both paths: existing row at `src/groundtruth_kb/db.py:4027-4033`, new row
via `insert_deliberation()` at `src/groundtruth_kb/db.py:4035-4051`. The return
value has no inserted/matched marker.

**Risk/impact:** A naive implementation can misreport idempotence status or
duplicate the DB's content-hash lookup logic in the CLI.

**Required implementation condition:** Choose one:

- simplify text output to print the ID only, while JSON returns the row, or
- add a deliberate preflight/postflight check with tests proving both
  `inserted` and `matched` output cases.

### 5. LOW - If `list --limit` survives from the original proposal, it needs a contract

**Evidence:** `list_deliberations()` accepts filters but no limit parameter:
`src/groundtruth_kb/db.py:4067-4100`. The original proposal included
`gt deliberations list ... [--limit <N>]`; the revised proposal does not
clearly restate whether that option remains.

**Risk/impact:** Low. CLI-side slicing is acceptable, but undocumented drift
between docs, tests, and implementation would be avoidable.

**Required implementation condition:** Either implement and test CLI-side
`--limit`, or remove it from the docs and examples.

## Required Action Items For Implementation

1. Implement `add` and `upsert` as separate commands with no `--id` on
   `upsert`.
2. Preserve default SQLite text fallback for `search`.
3. Define and test the exact `--semantic-only` behavior.
4. Resolve `upsert` inserted/matched output as described above.
5. Keep link validation in the CLI layer if the DB API remains permissive.
6. Keep docs and `scripts/check_docs_cli_coverage.py` aligned with the final
   command surface.

## Verification Expected After Implementation

Run, at minimum:

```bash
python -m pytest tests/test_cli_deliberations.py -q --tb=short
python -m pytest -q --tb=short
python -m ruff check .
python -m ruff format --check .
python scripts/check_docs_cli_coverage.py
```

This review approves implementation of the revised proposal under those
conditions.
