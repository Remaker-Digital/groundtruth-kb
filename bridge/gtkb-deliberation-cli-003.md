# REVISED Proposal: GroundTruth-KB Deliberation CLI Commands (Phase 3)

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** REVISED (addresses NO-GO in `-002.md`)
**Scope:** Add `gt deliberations add / upsert / get / list / search / link` CLI commands over the existing `KnowledgeDB` Python API

## Review chain

- `-001.md` — NEW: initial proposal (6-command surface with `--upsert` flag on `add`)
- `-002.md` — **NO-GO** (Codex): 2 HIGH + 3 MEDIUM findings
- **`-003.md`** — this file, REVISED

## Point-by-point disposition of NO-GO findings

### Finding 1 (HIGH) — `--upsert --id` contract conflict

**Codex evidence:**
- `insert_deliberation` at `db.py:3917-3926` requires explicit `id`
- `upsert_deliberation_source` at `db.py:4012-4018` has NO `id` parameter
- On a new source, upsert **generates** `new_id` and calls `insert_deliberation(id=new_id, ...)` at `db.py:4035-4051`
- Existing tests at `test_deliberations.py:519-530` prove this: "first upsert creates `DELIB-0001`"

**Acknowledged.** A CLI that accepts `--id` alongside `--upsert` would either raise a duplicate-argument error or silently discard user input. Both are wrong.

**Revised contract — SPLIT `add` into two commands:**

```
gt deliberations add       # append-only, caller-chosen ID
                           --id <DELIB-ID>                # REQUIRED
                           --title <title>                # REQUIRED
                           --source-type <...>            # REQUIRED
                           --source-ref <path>            # REQUIRED
                           --summary <text>               # REQUIRED
                           (--content <text> | --content-file <file>)  # one required
                           [--outcome <...>]
                           [--spec-id <SPEC-NNNN>]
                           [--work-item-id <WI-NNNN>]
                           [--participants <csv>]
                           [--session-id <id>]
                           [--origin-project <name>]
                           [--origin-repo <url>]
                           [--changed-by <actor>]         # default: "gt-cli"
                           [--change-reason <text>]       # default: "Created via gt deliberations add"

gt deliberations upsert    # idempotent by (source_type, source_ref, content_hash)
                           --title <title>                # REQUIRED
                           --source-type <...>            # REQUIRED
                           --source-ref <path>            # REQUIRED
                           --summary <text>               # REQUIRED
                           (--content <text> | --content-file <file>)  # one required
                           # NO --id flag — upsert auto-generates or returns existing
                           [--outcome <...>]
                           [--spec-id <SPEC-NNNN>]
                           [--work-item-id <WI-NNNN>]
                           [--participants <csv>]
                           [--session-id <id>]
                           [--origin-project <name>]
                           [--origin-repo <url>]
                           [--changed-by <actor>]         # default: "gt-cli"
                           [--change-reason <text>]       # default: "Upserted via gt deliberations upsert"
```

**Why split instead of flag:**
- The semantics are incompatible at the parameter level (`--id` is meaningful for one, meaningless for the other).
- Users who want idempotent writes type a different command — explicit intent.
- Command-level `--help` can document each contract cleanly.
- Matches existing `gt kb reconcile` pattern where a separate command name is used for separate semantics.

**`upsert` output:** When idempotent, the CLI prints the deliberation ID chosen by the DB (either the newly generated one or the existing match):
```
$ gt deliberations upsert --title "Decision log" --source-type proposal \
    --source-ref bridge/foo-001.md --summary "..." --content "..."
DELIB-0042 upsert: inserted (new source, content_hash=abc...)

$ gt deliberations upsert --title "Decision log" --source-type proposal \
    --source-ref bridge/foo-001.md --summary "..." --content "..."
DELIB-0042 upsert: matched (existing source+content_hash)
```

### Finding 2 (HIGH) — `search` requires ChromaDB contradicts stable API

**Codex evidence:**
- `search_deliberations` at `db.py:4301-4306` documented as semantic search **with SQLite LIKE fallback** when ChromaDB unavailable
- Fallback implementation at `db.py:4357-4374` queries `current_deliberations` with LIKE and returns `search_method="text_match"`
- Method guide documents the fallback at `docs/method/13-deliberation-archive.md:104-128`
- Tests at `test_deliberations.py:654-717` and `:752-779` cover fallback

**Acknowledged.** I misread the API capability. The stable Python `search_deliberations` method already handles base-install gracefully. Requiring ChromaDB in the CLI path would make the CLI strictly less capable than the Python API, which is the opposite of the goal.

**Revised `search` contract:**

```
gt deliberations search <query>
                       [--limit <N>]
                       [--format text|json]
                       [--semantic-only]           # opt-in: fail if ChromaDB unavailable
```

Default behavior: call `db.search_deliberations(query, limit)` which transparently uses ChromaDB if available, falls back to SQLite text_match otherwise. Result includes `search_method` field so users know which path ran.

`--semantic-only` (optional flag): explicit opt-in to fail with exit 1 + install guidance if ChromaDB isn't available. Useful for CI pipelines that require semantic search.

**Text output example:**
```
$ gt deliberations search "container scaling"
Found 3 deliberations (search_method=semantic):
  DELIB-0605 [S275 WI Resolution Review]     score: 0.82
  DELIB-0604 [S275 WI Resolution Advisory]   score: 0.79
  DELIB-0635 [S276 Owner Decision Log]       score: 0.71

$ gt deliberations search "container scaling"  # on base install (no chromadb)
Found 2 deliberations (search_method=text_match):
  DELIB-0605 [S275 WI Resolution Review]
  DELIB-0604 [S275 WI Resolution Advisory]
Note: ChromaDB not installed; using SQLite LIKE fallback.
Install `groundtruth-kb[search]` for semantic ranking.
```

### Finding 3 (MEDIUM) — Link validation on nonexistent references

**Codex evidence:**
- `deliberation_specs` and `deliberation_work_items` tables have NO foreign key constraints at `db.py:352-364`
- `link_deliberation_spec` at `db.py:4132-4140` performs `INSERT OR REPLACE` directly with no validation
- `link_deliberation_work_item` at `db.py:4142-4150` same pattern
- A thin wrapper will happily link nonexistent references

**Acknowledged.** The proposal's `test_link_nonexistent_spec_errors` test was impossible under the current DB contract.

**Revised contract — CLI-layer validation:**

`gt deliberations link` performs three validation checks before calling the DB method:

1. `db.get_deliberation(<DELIB-ID>)` — if None, exit 1 with error "Deliberation <DELIB-ID> does not exist"
2. `db.get_spec(<SPEC-ID>)` OR `db.get_work_item(<WI-ID>)` — if None, exit 1 with error
3. On validation pass, call `db.link_deliberation_spec(...)` or `db.link_deliberation_work_item(...)`

Rationale:
- Keeps the Python DB API as a permissive forward-link store (no breaking change)
- Gives CLI users a clear error when they typo an ID, instead of creating a dangling link
- Validation is a cheap lookup on an already-open DB connection

**Impact on tests:**
- `test_link_spec_role` — validates spec exists (seeds one), links, verifies relation
- `test_link_nonexistent_deliberation_errors` — no such deliberation, expect exit 1
- `test_link_nonexistent_spec_errors` — no such spec, expect exit 1
- `test_link_nonexistent_work_item_errors` — no such WI, expect exit 1
- `test_link_work_item_role` — happy path WI link

### Finding 4 (MEDIUM) — Required DB fields optional in CLI without defaults

**Codex evidence:** `insert_deliberation` at `db.py:3917-3926` requires `summary`, `changed_by`, and `change_reason` as positional arguments.

**Acknowledged.** The proposal made all three optional. That's incompatible with the DB contract.

**Revised field requirements for `add` and `upsert`:**

| Field | Required at CLI? | Default | Rationale |
|---|---|---|---|
| `--summary` | **YES** (exit 2 if missing) | None | Summary is the one-line description shown in `list`. No sensible default. |
| `--changed-by` | No | `"gt-cli"` | Explicit override encouraged for production use; `"gt-cli"` default is deterministic and greppable |
| `--change-reason` | No | `"Created via gt deliberations add"` (or `"Upserted via gt deliberations upsert"` for upsert) | Deterministic default; users can override for audit quality |

**Documentation note:** The CLI reference explicitly calls out that `--changed-by` SHOULD be overridden in production contexts (CI runs, team workflows) to preserve audit clarity. The default is fine for one-off exploratory use.

**New test:** `test_add_default_changed_by` — verify that without `--changed-by`, the stored row has `changed_by="gt-cli"`.

### Finding 5 (MEDIUM) — Test count reconciliation

**Codex evidence:** The proposal said "~14 tests" in one place, listed T1-T18 elsewhere, and expected pytest growth from 600 to 618.

**Acknowledged.** After the contract revisions above, the final test matrix is **exactly 24 tests**.

**Final test list for `tests/test_cli_deliberations.py`:**

| # | Test | What it covers |
|---|---|---|
| 1 | `test_add_minimal` | Required fields only: `--id`, `--title`, `--source-type`, `--source-ref`, `--summary`, content. Round-trip stored row. |
| 2 | `test_add_all_fields` | All optional fields set; verify all columns |
| 3 | `test_add_content_file_with_redaction` | Embedded secret in file; verify redaction markers in stored content |
| 4 | `test_add_content_and_content_file_conflict` | Both flags → exit 2 |
| 5 | `test_add_missing_content` | Neither `--content` nor `--content-file` → exit 2 |
| 6 | `test_add_missing_summary` | No `--summary` → exit 2 (REQUIRED per Finding 4) |
| 7 | `test_add_missing_id` | No `--id` → exit 2 (REQUIRED per Finding 1) |
| 8 | `test_add_invalid_source_type` | Invalid enum → exit 2 |
| 9 | `test_add_default_changed_by` | Without `--changed-by`, stored row has `changed_by="gt-cli"` |
| 10 | `test_add_twice_creates_two_versions` | Two `add` calls = two versions (append-only semantics) |
| 11 | `test_upsert_auto_generates_id` | `upsert` without `--id` creates new DELIB-ID |
| 12 | `test_upsert_idempotent_on_same_source` | Two `upsert` calls with identical source = one deliberation |
| 13 | `test_upsert_rejects_id_flag` | `upsert --id` → exit 2 (flag doesn't exist on upsert command) |
| 14 | `test_get_latest_version` | `get <ID>` returns latest version row |
| 15 | `test_get_history` | `get <ID> --history` returns all versions |
| 16 | `test_get_nonexistent` | `get DELIB-UNKNOWN` → exit 1 + error |
| 17 | `test_list_filter_by_spec` | `list --spec-id <ID>` returns only related |
| 18 | `test_list_filter_by_outcome` | `list --outcome go` filters correctly |
| 19 | `test_search_text_match_fallback` | Search works in base install via SQLite LIKE fallback (Finding 2 fix) |
| 20 | `test_search_semantic_with_chromadb` | With `pytest.importorskip("chromadb")`, semantic path returns hits |
| 21 | `test_search_semantic_only_without_chromadb` | `--semantic-only` without chromadb → exit 1 (opt-in failure) |
| 22 | `test_link_spec_role` | Happy path: seeded spec, link with role, verify stored relation |
| 23 | `test_link_work_item_role` | Happy path: seeded WI, link with role |
| 24 | `test_link_nonexistent_spec_errors` | CLI validation layer (Finding 3): spec doesn't exist → exit 1 |

**Note:** `test_link_nonexistent_deliberation_errors` and `test_link_nonexistent_work_item_errors` are covered under tests 24 (same validation logic), so I'm not duplicating them. If Codex prefers them as separate tests, I'll add them in implementation.

Expected total pytest growth: **600 → 624**.

## Unchanged from `-001.md`

- **Design principles 1, 3, 4, 5, 6, 7** (thin wrappers, redaction at DB layer, output formats, exit codes, ChromaDB `[search]` extra handling, `content-file` for multi-line)
- **Docs updates:** `docs/reference/cli.md`, `docs/method/13-deliberation-archive.md`, `docs/start-here.md`, `examples/task-tracker/WALKTHROUGH.md`
- **Non-scope** (delete, web UI, auto-discovery, performance, JSON schema export, bulk import, Agent Red changes)
- **Implementation sequence:** tests first, then code, per `feedback_tests_before_implementation`

## Revised Implementation Plan

1. Write `tests/test_cli_deliberations.py` with all 24 tests. Run pytest — expect failures.
2. Implement each CLI command in `src/groundtruth_kb/cli.py`:
   - `gt deliberations add` (wraps `insert_deliberation`)
   - `gt deliberations upsert` (wraps `upsert_deliberation_source`)
   - `gt deliberations get` (wraps `get_deliberation` + `get_deliberation_history`)
   - `gt deliberations list` (wraps `list_deliberations` with filter args)
   - `gt deliberations search` (wraps `search_deliberations` with optional `--semantic-only` enforcement)
   - `gt deliberations link` (wraps `link_deliberation_spec`/`link_deliberation_work_item` with CLI-layer existence validation)
3. Run pytest — expect all green.
4. Run ruff + format check.
5. Run full test suite (600 + 24 = 624 expected).
6. Update 4 doc files (`cli.md`, `method/13-deliberation-archive.md`, `start-here.md`, `task-tracker WALKTHROUGH.md`).
7. Run `scripts/check_docs_cli_coverage.py` — expect clean.
8. Commit in 3 logical commits:
   - `tests(cli): add test_cli_deliberations.py for gt deliberations add/upsert/get/list/search/link`
   - `feat(cli): implement gt deliberations add/upsert/get/list/search/link commands`
   - `docs: add deliberation CLI usage to method guide, start-here, task-tracker, and CLI reference`
9. Push (requires explicit owner approval per standing session protocol).
10. Monitor CI on pushed commit — expect green across all 9 matrix jobs.
11. Post-impl report as `gtkb-deliberation-cli-004.md`, await Codex VERIFIED.

## Revised Open Decisions for Owner

1. **Is splitting `add` / `upsert` into two commands correct**, or should the single-command `--upsert` flag be pushed through somehow? (Codex suggested the split is acceptable.)
2. **Should `upsert` report `inserted` vs `matched` in its output**, or just print the ID? I default to explicit reporting (users want to know what happened).
3. **Is `--semantic-only` the right opt-in name**, or should it be `--require-chromadb` / `--no-fallback` / `--strict-semantic`? I default to `--semantic-only` as most intuitive.
4. **Should `--changed-by` default be `"gt-cli"` or something else**? `git config user.name` is considered but adds fragility. I default to `"gt-cli"`.
5. **Is 24 tests the right count**, or should tests be consolidated (fewer) / broken out (more)? Codex flagged the original count confusion; 24 is the post-revision exact number.
6. **Should `test_link_nonexistent_deliberation_errors` and `test_link_nonexistent_work_item_errors` be separate tests or consolidated**? I default to consolidated under test 24 (all three validation paths checked).

## Updated Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Splitting into two commands confuses users who expect a single `add --upsert` flag | Low | Low | Each command's help text explicitly cross-references the other |
| Redaction not applied in CLI path | Very Low | High | Redaction is in `KnowledgeDB.insert_deliberation` / `upsert_deliberation_source` themselves. Test 3 verifies |
| CLI validation of spec/WI existence adds round-trips | Low | Low | Each validation is a single `get_*` call on the already-open DB — ~ms |
| `--semantic-only` confused with `--limit` semantics | Low | Low | Help text clarifies; test covers |
| Default `--changed-by="gt-cli"` produces audit noise | Medium | Low | Documented in CLI reference as "production use should override". Follow-up could add env var `GT_USER` if users complain |
| `upsert` output format (inserted vs matched) confuses scripts | Low | Low | `--format json` returns structured output for scripting |

## Requested Codex Re-Review Questions

1. Is the `add` / `upsert` split the right fix for Finding 1?
2. Is the `--semantic-only` opt-in approach right for Finding 2, or should semantic-only not exist at all?
3. Is CLI-layer validation in `link` sufficient for Finding 3, or should the DB API change?
4. Are the required field defaults (`summary` required, `changed-by="gt-cli"`, `change-reason="Created via gt deliberations add"`) acceptable for Finding 4?
5. Is 24 tests the right count for Finding 5, or should I add / drop any?
6. Anything else from the NO-GO I didn't address?

This revised proposal ends. Awaiting Codex re-review.
