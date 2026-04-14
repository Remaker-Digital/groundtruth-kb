# Proposal: GroundTruth-KB Deliberation CLI Commands (Phase 3 of production-readiness roadmap)

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW
**Scope:** Add `gt deliberations add / get / list / search / link` CLI commands as thin wrappers over the existing `KnowledgeDB` Python API
**Parent roadmap:** `bridge/gtkb-production-readiness-003.md` (GO at `-004.md`)
**Depends on:** None — can run in parallel with `gtkb-v0.4.0-release-001.md` and `gtkb-audit-baseline-001.md`

## Owner direction

> "In parallel" — Owner decision 3, 2026-04-14, on sequencing Phase 2 / 3 / 4A

## Prior Deliberations

Searches: `gt deliberations CLI add search list`, `deliberation archive Python API wrapper`, `insert_deliberation upsert_deliberation_source`:

- **DELIB-0651** (S279 Deliberation Archive Completion Post-Implementation Review): Core deliberation archive API (schema, Python methods, ChromaDB semantic search) is Codex-VERIFIED and stable.
- **DELIB-0652 / 0653** (S279): Deliberation archive proposal + revisions — API surface stable.
- **DELIB-0703 / 0704** (S282-S283): ChromaDB semantic search implementation and review — stable.
- **DELIB-0649** (S283): Deliberation Archive Completion Advisory — completion confirmed.
- **`gtkb-production-readiness-003.md`** lines 269-317: Original CLI scope proposal for Phase 3. Includes `add/get/list/search/link` with `--upsert` flag for idempotent source-based writes. This proposal inherits that design.
- **`gtkb-production-readiness-004.md`** Non-blocking note 3 (Codex): "Phase 2 should define idempotence clearly. `src/groundtruth_kb/db.py:3917` exposes append-only `insert_deliberation()`, while `src/groundtruth_kb/db.py:4012` exposes idempotent `upsert_deliberation_source()`. A CLI `add` command must state whether repeat calls create a new version, return an existing source/content match, or offer separate flags for both behaviors." This proposal addresses this by defaulting to `insert_deliberation` (append-only) and providing `--upsert` to switch to `upsert_deliberation_source`.

No prior deliberation has proposed a CLI for deliberations. The current CLI (`docs/reference/cli.md:437`) exposes only `gt deliberations rebuild-index`. The Python API has been complete since v0.2.x.

## Observation

### Current state

- **Python API (stable, since v0.2.x):** `KnowledgeDB` exposes 11 deliberation methods at `src/groundtruth_kb/db.py:3913-4392`:
  - `insert_deliberation` (line 3917) — append-only, creates a new version on each call
  - `upsert_deliberation_source` (line 4012) — idempotent by `source_type + source_ref + content_hash`
  - `get_deliberation` (line 4053) — latest version of a specific DELIB-ID
  - `get_deliberation_history` (line 4058) — all versions
  - `list_deliberations` (line 4067) — enumerate with filters (spec_id, work_item_id, source_type, session_id, outcome, source_ref)
  - `get_deliberations_for_spec` (line 4102) — by spec relation
  - `get_deliberations_for_work_item` (line 4117) — by WI relation
  - `link_deliberation_spec` (line 4132) — add role-labeled spec relation
  - `link_deliberation_work_item` (line 4142) — add role-labeled WI relation
  - `search_deliberations` (line 4301) — ChromaDB semantic search
  - `rebuild_deliberation_index` (line 4376) — maintenance only (already has CLI)

- **CLI surface today:** One command — `gt deliberations rebuild-index` (cli.py:674-689). Developers who want to insert/query deliberations must write Python glue code.

- **Tests:** `tests/test_deliberations.py` is 1226 lines, 69/69 passing, covers the Python API comprehensively with `@requires_chromadb` gating for search-dependent tests.

### Documentation state

- Method guide `docs/method/13-deliberation-archive.md` has a "Python API" section (line 163+) with `insert_deliberation()` examples but NO CLI section.
- CLI reference `docs/reference/cli.md` has a minimal "Deliberation Commands" section (line 437) with only `rebuild-index`.
- Start-here walkthrough (`docs/start-here.md`) mentions `gt deliberations rebuild-index` in a "What's Next" bullet but does not walk through hands-on deliberation usage.

## Deficiency Rationale

**The flagship feature (Deliberation Archive) has effectively zero CLI surface.** This filters out a significant adoption population:

1. **Bash-first / shell-centric developers** cannot try the feature without committing to Python glue code.
2. **CI/CD integration** has no natural entry point for scripted deliberation capture (e.g., capturing a deploy decision during a release workflow).
3. **Exploratory users** who want a "paste a 10-line README and see something happen" introduction currently have to read the method guide's Python examples.
4. **Developers trying GT-KB before committing** to the full KnowledgeDB API pattern are forced to commit anyway.

The Python API itself is solid and fully covered by tests. The CLI gap is a pure ergonomics issue — no domain logic needs to be written, only CLI wrappers.

## Proposed Solution

### CLI command surface

```
gt deliberations add       [--upsert]
                           --id <DELIB-ID>
                           --title <title>
                           --source-type <proposal|lo_review|owner_conversation|report|session_harvest|bridge_thread>
                           --source-ref <path-or-uri>
                           (--content <text> | --content-file <file>)
                           [--summary <text>]
                           [--outcome <go|no_go|deferred|owner_decision|informational>]
                           [--spec-id <SPEC-NNNN>]
                           [--work-item-id <WI-NNNN>]
                           [--participants <csv>]
                           [--session-id <session>]
                           [--origin-project <name>]
                           [--origin-repo <url>]
                           [--changed-by <actor>]
                           [--change-reason <text>]

gt deliberations get       <DELIB-ID>
                           [--history]          # show all versions
                           [--format text|json]

gt deliberations list      [--spec-id <id>]
                           [--work-item-id <id>]
                           [--source-type <type>]
                           [--outcome <outcome>]
                           [--session-id <id>]
                           [--source-ref <pattern>]
                           [--limit <N>]
                           [--format text|json]

gt deliberations search    <query>
                           [--limit <N>]
                           [--format text|json]

gt deliberations link      <DELIB-ID>
                           (--spec <SPEC-ID> | --work-item <WI-ID>)
                           [--role <related|rejected_alternative|supersedes|...>]

gt deliberations rebuild-index      # unchanged, already exists
```

### Design principles

1. **Thin wrappers only.** Each command calls the existing `KnowledgeDB` method. No new domain logic in the CLI layer. No new business rules.

2. **`add` default is append-only (`insert_deliberation`).** The `--upsert` flag switches to `upsert_deliberation_source` semantics. Rationale:
   - Default `insert_deliberation` matches the principle of explicit intent — each CLI `add` creates a new version.
   - `--upsert` is opt-in for callers who want idempotence (e.g., CI scripts that might re-run).
   - Both paths hit the same redaction logic (applied inside `KnowledgeDB` at write-time), so there's no redaction bypass risk.

3. **Content input: `--content <text>` or `--content-file <file>` (mutually exclusive).** `--content-file` is needed for multi-line content and to avoid shell escaping of long bodies. If neither is provided, error with exit 2.

4. **Redaction happens at the DB layer, not the CLI layer.** I verified this by reading `KnowledgeDB.insert_deliberation` (db.py:3917) and `upsert_deliberation_source` (db.py:4012) — both call `_redact_content(content)` before the INSERT. The CLI doesn't need to redact anything.

5. **Output formats: `text` (default, human-readable) and `json` (machine-readable).** Matches existing `gt` commands like `gt config`, `gt summary`.

6. **`search` requires the ChromaDB `[search]` extra.** If chromadb isn't installed, error with exit 1 and a helpful "install with groundtruth-kb[search]" message — same pattern as the existing `rebuild-index` command.

7. **Exit codes follow existing GT-KB CLI conventions:**
   - 0 = success
   - 1 = runtime failure (db error, chromadb not installed, linked spec/WI not found, etc.)
   - 2 = argument validation error (missing required flag, invalid enum value, etc.)

### Test plan

New file: `tests/test_cli_deliberations.py` (~400 lines, 14 tests)

| ID | Test | Purpose |
|---|---|---|
| T1 | `test_add_minimal` | Round-trip: add deliberation with required fields only, verify DB row exists |
| T2 | `test_add_all_fields` | All optional flags, verify all columns populated correctly |
| T3 | `test_add_content_file` | `--content-file` with an on-disk file containing embedded credentials — verify redaction happens (indirect: assert redaction pattern markers appear in stored content) |
| T4 | `test_add_content_and_content_file_conflict` | Both `--content` and `--content-file` → exit 2 |
| T5 | `test_add_missing_content` | Neither `--content` nor `--content-file` → exit 2 |
| T6 | `test_add_default_is_append` | Two `add` calls for same source → two different versions (insert_deliberation behavior) |
| T7 | `test_add_upsert_idempotent` | Two `add --upsert` calls with same source → one version (upsert_deliberation_source behavior) |
| T8 | `test_add_invalid_source_type` | Invalid enum → exit 2 |
| T9 | `test_get_latest_version` | Get returns latest version of existing DELIB-ID |
| T10 | `test_get_history` | `--history` returns all versions |
| T11 | `test_get_nonexistent` | Unknown DELIB-ID → exit 1 + error message |
| T12 | `test_list_filter_by_spec` | List with `--spec-id` returns only related deliberations |
| T13 | `test_search_text_match_no_chromadb` | Without chromadb extra, `search` exits 1 with helpful message |
| T14 | `test_search_semantic_with_chromadb` | With chromadb extra (via `pytest.importorskip`), returns hits for a seeded deliberation |
| T15 | `test_link_spec_role` | Link command adds role-labeled spec relation |
| T16 | `test_link_work_item` | Link command adds WI relation |
| T17 | `test_link_nonexistent_spec_errors` | Linking to non-existent spec → exit 1 |
| T18 | `test_json_output_format` | `--format json` returns parseable JSON |

All tests use `click.testing.CliRunner` (consistent with `test_cli.py`).

### Documentation updates

1. `docs/reference/cli.md` — replace the single-command "Deliberation Commands" section with a full section covering all 6 commands (add, get, list, search, link, rebuild-index). Each command gets: synopsis, options, examples, exit codes.

2. `docs/method/13-deliberation-archive.md` — add a "CLI Usage" section between "Semantic search" and "Python API". Show the same examples as the Python API section, but with `gt deliberations ...` commands.

3. `docs/start-here.md` — add an optional "Step 11: Record a deliberation" section showing:
   ```bash
   gt deliberations add \
     --id DELIB-TUTORIAL-0001 \
     --title "Why we chose SQLite over JSON" \
     --source-type owner_conversation \
     --source-ref "start-here.md" \
     --outcome owner_decision \
     --content "We chose SQLite because..."
   gt deliberations list
   gt deliberations get DELIB-TUTORIAL-0001
   ```

4. `examples/task-tracker/WALKTHROUGH.md` — add a section showing how a fictional task-tracker project would capture a deliberation when the team picks a database backend. Seed script (`examples/task-tracker/seed.py` or similar) pre-creates a sample deliberation so `gt deliberations list` in a fresh task-tracker project shows real content.

### Implementation sequence

**Tests first, then code** per `feedback_tests_before_implementation`:

1. Write `tests/test_cli_deliberations.py` with all 18 tests. Run pytest — expect failures (commands don't exist yet).
2. Implement each CLI command in `src/groundtruth_kb/cli.py` as a thin wrapper over `KnowledgeDB` methods.
3. Run pytest — expect all green.
4. Run ruff + format check.
5. Run the full test suite to check for regressions on the existing 600 tests.
6. Update docs.
7. Run `scripts/check_docs_cli_coverage.py` — expect clean (the script validates CLI command documentation).
8. Commit in 3 logical commits:
   - Commit 1: Tests only (failing)
   - Commit 2: CLI implementation (tests now green)
   - Commit 3: Documentation updates

## Option Rationale

**Alternative: `gt deliberations add` has no `--upsert` flag; use separate `gt deliberations upsert` command.** Rejected. Adds CLI surface without semantic benefit. Users want to add a deliberation idempotently if they know they might re-run — a flag on `add` is the natural ergonomic choice. The behavior difference is one method call, not a different code path.

**Alternative: `search` is a top-level command (`gt search deliberations <query>`), not a subcommand.** Rejected. Breaks the hierarchy — other artifact types (specs, work items) are under `gt` directly but deliberations are consistently in the `gt deliberations` namespace. Staying consistent is more important than minimal keystrokes.

**Alternative: Add `gt deliberations delete` for completeness.** Rejected. Deliberations are append-only (GOV-08, KB is truth). There is no delete semantic. A future "retract" feature would be a new version with `outcome=retracted` — doesn't need CLI plumbing.

**Alternative: `get` returns latest and `get --all-versions` returns history; no separate `--history` flag.** Considered. The current proposal uses `--history` because it mirrors `get_deliberation_history` which is a separate Python method. Either naming is defensible.

**Alternative: Implement CLI commands first, write tests after.** Rejected. `feedback_tests_before_implementation` is explicit: tests before implementation, no exceptions.

**Alternative: Fold docs updates into a Phase 3.5.** Rejected. Docs are part of the Phase 3 deliverable; shipping CLI without docs creates a discoverability gap.

## Implementation Context (Prime Builder)

**Scope boundary:** groundtruth-kb repo only. New file `tests/test_cli_deliberations.py`. Modifications to `src/groundtruth_kb/cli.py`, `docs/reference/cli.md`, `docs/method/13-deliberation-archive.md`, `docs/start-here.md`, `examples/task-tracker/WALKTHROUGH.md`. Possible new seed script at `examples/task-tracker/seed_deliberations.py`.

**No changes to:** `db.py`, `config.py`, schema, tests other than the new file, CI/publish workflows, `pyproject.toml`.

**Preconditions:**
- Phase 1 of production-readiness roadmap VERIFIED (done — `gtkb-production-readiness-006.md`)
- Branch CI green on `origin/main` (true — `993f31b`)
- Python API for deliberations stable (true — covered by 69/69 tests in `test_deliberations.py`)

**Open decisions required from owner:**
1. **Is the scope right?** 6 commands (add, get, list, search, link, rebuild-index), ~14-18 tests, ~4 doc files.
2. **Does the task-tracker example need a code change,** or is a docs-only walkthrough sufficient? I default to docs + seed script.
3. **Should `get --format json` return the full row or a curated subset?** I default to full row (matches `list --format json`).
4. **Should `list` pagination use `--limit` only, or `--limit` + `--offset`?** I default to `--limit` only for v0.4.0; add `--offset` if users ask.
5. **Should `search` expose all ChromaDB `limit` + `similarity_threshold` options,** or only `--limit`? I default to `--limit` only.

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| CLI breaks on obscure click option combination | Low | Low | Tests cover argument validation |
| Redaction not applied in the CLI path (bypass bug) | Very Low | High | Redaction is in `KnowledgeDB.insert_deliberation` itself — the CLI calls that method. Tests explicitly verify redaction by asserting markers appear |
| `search` command hangs on ChromaDB startup | Low | Medium | Existing `rebuild-index` has the same startup path and doesn't hang in practice |
| `add --content-file` has Windows path handling issues | Low | Low | Use `pathlib.Path` throughout. Existing `tests/test_cli.py` demonstrates the pattern works |
| JSON output format drifts between commands | Low | Low | Single `_format_result(result, fmt)` helper, reused |
| Users confused by `--upsert` semantics | Medium | Low | Docstring and doc examples show both cases. Error messages clarify if users try something wrong |
| CLI tests take too long to run in CI matrix | Low | Low | 18 tests using `CliRunner` are fast (<1s each). Total addition ~15s |

## Test Plan Summary

| Phase | Tests added | Files touched |
|---|---|---|
| Phase 3 implementation | 14-18 new tests in `tests/test_cli_deliberations.py` | `src/groundtruth_kb/cli.py` (+~300 lines), `tests/test_cli_deliberations.py` (new, ~400 lines), 4 doc files, optional seed script |

Expected total pytest growth: 600 → 618 tests. Ruff clean. Docs CLI coverage clean.

## Requested Codex Review Questions

1. **Is the 6-command CLI surface the right scope** (add, get, list, search, link, rebuild-index)? Missing anything? Too many?
2. **Is `--upsert` the right idempotence control**, or should `add` and `upsert` be separate commands?
3. **Test plan adequacy:** 14-18 tests sufficient, or should the coverage be broader (e.g., test redaction in CLI path specifically)?
4. **Are the docs updates correctly scoped?** (cli.md, method guide, start-here, task-tracker example) Anything else needed?
5. **Should this proposal be split into Phase 3A (CLI commands) and Phase 3B (docs)?** Both are in-scope here.
6. **Is there a test / implementation order reversal concern?** (Tests first, then code — matches feedback_tests_before_implementation.)

## Non-scope

- Web UI for deliberations (the existing web UI serves specs/WIs; adding deliberations is a bigger proposal)
- API for deleting/retracting deliberations (append-only by design)
- Auto-discovery of deliberation sources from file paths (too much magic; manual creation is the API contract)
- Performance optimization (not a production issue at current scale)
- JSON schema export of the deliberation row format
- Bulk import from a file (`gt deliberations import <path>`) — could be a v0.5.x addition
- Export to markdown / JSON (`gt deliberations export <path>`) — could be a v0.5.x addition
- Agent Red changes (none; Agent Red gets the new CLI automatically via upstream pip upgrade)

This proposal ends. Awaiting Codex review.
