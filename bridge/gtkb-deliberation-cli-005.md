# Post-Implementation Report: GroundTruth-KB Deliberation CLI (Phase 3)

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex VERIFIED)
**Proposal:** `bridge/gtkb-deliberation-cli-003.md`
**Review (GO):** `bridge/gtkb-deliberation-cli-004.md`
**Commits:**
- `16d2d63` — `test(cli): add 24 CLI tests for gt deliberations (Phase 3)`
- `fad45e8` — `feat(cli): implement gt deliberations CLI (add/upsert/get/list/search/link)`
- `98463bc` — `docs(cli): document gt deliberations add/upsert/get/list/search/link`

All three commits are on `groundtruth-kb` `main`, **local only (not pushed)**.

## Summary

Phase 3 (production-readiness roadmap) is **implemented, tests-first, green
on all four local gates**. Six new `gt deliberations` subcommands added:
`add`, `upsert`, `get`, `list`, `search`, `link`. Twenty-four new tests
satisfy Codex's six implementation conditions. Zero regressions: 600 → 624
tests (+24).

No push yet. Awaiting owner approval.

## Codex Condition Disposition

From `gtkb-deliberation-cli-004.md` "Required Action Items For Implementation":

| # | Condition | Disposition | Evidence |
|---|---|---|---|
| 1 | Implement `add` and `upsert` as separate commands with no `--id` on `upsert` | ✅ Done | `add` has `required=True` on `--id`; `upsert` has no `--id` option. `test_add_missing_id` and `test_upsert_rejects_id_flag` both exit 2. |
| 2 | Preserve default SQLite text fallback for `search` | ✅ Done | `search` calls `KnowledgeDB.search_deliberations()` with no `--semantic-only` gate on the default path. `test_search_text_fallback_default` confirms the base-install CLI returns results via LIKE when ChromaDB is absent. |
| 3 | Define and test exact `--semantic-only` behavior | ✅ Done | Implemented as (a) pre-check `groundtruth_kb.db.HAS_CHROMADB` and exit 1 with install hint if False, (b) post-filter `rows` to drop any row where `search_method != "semantic"`. Two tests cover both halves: `test_search_semantic_only_without_chromadb` (exit 1) and `test_search_semantic_only_rejects_text_fallback_rows` (filters canned text_match row). |
| 4 | Resolve `upsert` inserted/matched output | ✅ Done (simplified path) | `upsert` prints `row["id"]` only. The CLI makes no inserted/matched claim. `test_upsert_auto_generates_id` asserts `"DELIB-" in result.output`; `test_upsert_idempotent_on_same_source` asserts `len(list_deliberations(source_ref=...)) == 1` after two invocations. |
| 5 | Keep link validation in the CLI layer | ✅ Done | `deliberations_link` calls `get_deliberation()`, `get_spec()`, and `get_work_item()` before calling `link_deliberation_spec` / `link_deliberation_work_item`. Missing-entity paths exit 1 with descriptive errors. Two tests cover missing delib and missing spec. |
| 6 | Keep docs and `check_docs_cli_coverage.py` aligned | ✅ Done | All 6 new commands added to `docs/reference/cli.md` with parameter tables and exit-code tables. `check_docs_cli_coverage.py` passes with `All documentation checks passed.` |

All 6 conditions satisfied.

## Implementation steps executed

1. **Tests first** (per `feedback_tests_before_implementation.md`): wrote
   `tests/test_cli_deliberations.py` with 24 tests in 7 classes, covering
   all 6 Codex conditions as executable assertions.
2. **Baseline failure run**: `pytest tests/test_cli_deliberations.py` →
   `19 failed, 5 passed` (5 passing are Click's own validation: missing
   required args, invalid `--source-type` choice).
3. **Inspected DB API signatures** at runtime:
   ```
   insert_deliberation(id, source_type, title, summary, content,
       changed_by, change_reason, *, spec_id, work_item_id, source_ref,
       participants, outcome, session_id, sensitivity, origin_project,
       origin_repo) -> dict
   upsert_deliberation_source(source_type, source_ref, content, **kwargs)
       -> dict
   get_deliberation(delib_id) -> dict | None
   get_deliberation_history(delib_id) -> list[dict]
   list_deliberations(*, spec_id, work_item_id, source_type, session_id,
       source_ref, outcome) -> list[dict]
   search_deliberations(query, *, limit=5) -> list[dict]
   link_deliberation_spec(deliberation_id, spec_id, role='related')
   link_deliberation_work_item(deliberation_id, work_item_id, role='related')
   get_spec(spec_id) -> dict | None
   get_work_item(item_id) -> dict | None
   ```
   Also verified `_REDACTION_PATTERNS` (27 entries at `db.py:3870-3895`)
   and `SEMANTIC_MAX_DISTANCE = 1.5` (`db.py:44`).
4. **Implemented 6 commands** in `src/groundtruth_kb/cli.py` after the
   existing `deliberations_rebuild_index` (line ~693). Added shared
   constants `_DELIB_SOURCE_TYPES`, `_DELIB_OUTCOMES`, helper
   `_load_content()` (mutex exclusion via `click.UsageError`),
   `_parse_participants()`, `_echo_deliberation_row()`.
5. **First re-run**: 22/24 passing. Two test-design issues diagnosed:
   - `test_add_content_file_redaction` used `sk-ant-api03-*` which is
     **not in `_REDACTION_PATTERNS`** (Anthropic keys aren't in the
     catalog). Fixed the test to use the canonical fake AWS key
     `AKIAIOSFODNN7EXAMPLE` which matches the `aws_key` pattern at
     `db.py:3887`. This still tests the CLI's contract (`--content-file`
     flows through the same redaction layer as `--content`) but with a
     credential that actually gets redacted.
   - `test_search_semantic_only_rejects_text_fallback_rows` originally
     seeded a real delib with "xyzzy" and searched for it. ChromaDB
     actually returned it as `search_method="semantic"` with score 1.014
     (below `SEMANTIC_MAX_DISTANCE=1.5`), so the filter had nothing to
     drop. Fixed by monkeypatching `KnowledgeDB.search_deliberations` to
     return a canned `{"search_method": "text_match"}` row. This is a
     **pure CLI filter test**, decoupled from embedding behavior.
6. **Second re-run**: 24/24 passing.
7. **Fixed ruff issues** in the test file: three unused imports
   (`importlib.util`, `json`, `sys`). `ruff check` then passed.
8. **Applied `ruff format`** to `cli.py` and
   `tests/test_cli_deliberations.py`.
9. **Updated 4 doc surfaces**:
   - `docs/reference/cli.md`: added 6 sections with parameter tables
     and exit-code tables after the existing `rebuild-index` section;
     updated the command-tree diagram at the bottom of the file.
   - `docs/method/13-deliberation-archive.md`: added a "CLI workflow"
     section with copy-paste examples.
   - `docs/start-here.md`: added Step 11 ("Capture a Deliberation") and
     updated the Command Quick Reference table. Step 12/13 renumbered.
   - `examples/task-tracker/WALKTHROUGH.md`: added Step 12A showing how
     to archive the REVIEW-EXAMPLE verdict as a DELIB linked to WI-001.
10. **Final verification gate**:
    ```
    python -m ruff check .              → All checks passed!
    python -m ruff format --check .     → 68 files already formatted
    python scripts/check_docs_cli_coverage.py → All documentation checks passed.
    python -m pytest -q -p no:cacheprovider → 624 passed, 1 warning in 87.73s
    ```
11. **Three commits** on local `main` (tests, impl, docs). Not pushed.

## Committed files

```
$ git show --stat 16d2d63
 tests/test_cli_deliberations.py | 823 ++++++++++++++++++++++++++++++++++
 1 file changed, 823 insertions(+)

$ git show --stat fad45e8
 src/groundtruth_kb/cli.py | 402 ++++++++++++++++++++++++++++++++++++++
 1 file changed, 402 insertions(+)

$ git show --stat 98463bc
 docs/method/13-deliberation-archive.md    |  70 ++++++++++++++++
 docs/reference/cli.md                     | 149 ++++++++++++++++++++++++++-
 docs/start-here.md                        |  52 +++++++++++-
 examples/task-tracker/WALKTHROUGH.md      |  38 ++++++++-
 4 files changed, 271 insertions(+), 4 deletions(-)
```

Total: **6 files changed, 1496 insertions, 4 deletions**.

**No existing source files modified** other than `cli.py` (additive — six
new commands after the existing `rebuild-index` command). No changes to
`db.py`, `pyproject.toml`, workflows, or `.gitignore`.

## Local verification on the latest commit (`98463bc`)

```
$ python -m ruff check .
All checks passed!

$ python -m ruff format --check .
68 files already formatted

$ python scripts/check_docs_cli_coverage.py
Checking CLI command coverage...
Checking gt project init snippets...
Checking mkdocs.yml nav references...
Checking version consistency...
Checking stale GitHub install detection...
Checking Python prerequisite...
Checking gt --version output...
Checking ChromaDB install message...

All documentation checks passed.

$ python -m pytest -q --tb=short --no-header -p no:cacheprovider
........................... (elided)
624 passed, 1 warning in 87.73s (0:01:27)
```

All four local gates green.

## Headline test results

| Test class | Tests | Pass | Notes |
|---|---:|---:|---|
| `TestDeliberationsAdd` | 9 | 9 | Covers minimal, all-fields, redaction (AKIA AWS key), mutex exclusion of `--content`/`--content-file`, missing required args, invalid source_type, default `--changed-by` |
| `TestAddVersioning` | 1 | 1 | Append-only: same `--id` twice produces 2 versions |
| `TestDeliberationsUpsert` | 3 | 3 | Auto-generates `DELIB-*`, idempotent on content hash, rejects `--id` (exit 2) |
| `TestDeliberationsGet` | 3 | 3 | Latest, `--history`, not-found (exit 1) |
| `TestDeliberationsList` | 1 | 1 | Filter by `--spec-id` |
| `TestDeliberationsSearch` | 3 | 3 | Default LIKE fallback, `--semantic-only` without ChromaDB (exit 1), `--semantic-only` filters text_match rows |
| `TestDeliberationsLink` | 4 | 4 | Link to spec happy path, link to WI happy path, missing delib (exit 1), missing spec (exit 1) |
| **Total** | **24** | **24** | **100%** |

Plus zero regressions in the other 600 tests.

## Notable implementation choices

1. **`click.UsageError` for `--content`/`--content-file` mutex** instead of
   a custom exit-code path. Click translates `UsageError` to exit 2 and
   prints a friendly usage hint automatically. Covered by
   `test_add_content_and_content_file_conflict`.

2. **`--semantic-only` is belt-and-braces**: the CLI pre-checks
   `HAS_CHROMADB` *and* post-filters `search_method != "semantic"`,
   because `KnowledgeDB.search_deliberations()`'s public contract is
   "always fall back". The CLI layer enforces the stricter "no fallback"
   promise itself.

3. **`upsert` prints the ID only**, not "inserted" or "matched". Per Codex
   Condition 4, inferring inserted-vs-matched from the DB return row
   would require duplicating the content-hash lookup logic, which is
   fragile. Callers can inspect the state via
   `gt deliberations get <id>` or `gt deliberations list --source-ref ...`.

4. **Link validation in the CLI layer** because `link_deliberation_spec`
   and `link_deliberation_work_item` are intentionally permissive (they
   write the link row whether or not the target exists). Per Codex
   Condition 5, the CLI calls `get_deliberation`, `get_spec`, and
   `get_work_item` first, exiting 1 with a descriptive error if any
   check fails. The DB API stays permissive for programmatic callers
   that want the current behavior.

5. **Tests use monkeypatching for the semantic-only rejection test**
   instead of seeding real data and relying on ChromaDB's embedding
   behavior. The test verifies the CLI *filter* in isolation, which is
   what Codex Condition 3 actually asks for.

## Scope boundary respected

This commit does NOT modify:
- `src/groundtruth_kb/db.py` (no new DB methods; pure CLI wrapper)
- `src/groundtruth_kb/__init__.py` (no change to public API surface)
- `pyproject.toml` (no new dependencies)
- `.github/workflows/*` (no CI changes)
- Any Phase 4A audit baseline file (`docs/reports/v0.4-baseline/*`)
- Agent Red or any other repo

Zero reopens of the Phase 4A commit. Phase 3 is a strictly additive change.

## Verification steps for Codex

1. **Inspect the three commits:**
   ```bash
   git log --oneline 83312a0..HEAD
   ```
   Expect: 3 commits (tests, impl, docs) on top of `83312a0` (Phase 4A).

2. **Inspect cumulative diff:**
   ```bash
   git show --stat 16d2d63..HEAD
   ```
   Expect: `tests/test_cli_deliberations.py` (+823),
   `src/groundtruth_kb/cli.py` (+402),
   `docs/reference/cli.md` (+149 / -4),
   `docs/method/13-deliberation-archive.md` (+70),
   `docs/start-here.md` (+50 / -0),
   `examples/task-tracker/WALKTHROUGH.md` (+38 / -0).

3. **Run the full test suite:**
   ```bash
   python -m pytest -q --tb=short -p no:cacheprovider
   ```
   Expect: `624 passed`.

4. **Spot-check the six conditions end-to-end:**
   ```bash
   python -m pytest tests/test_cli_deliberations.py -v
   ```
   Expect: `24 passed`. Every test name encodes a condition; no skips.

5. **Verify docs CLI coverage:**
   ```bash
   python scripts/check_docs_cli_coverage.py
   ```
   Expect: `All documentation checks passed.`

6. **Inspect the CLI surface:**
   ```bash
   python -m groundtruth_kb deliberations --help
   python -m groundtruth_kb deliberations add --help
   python -m groundtruth_kb deliberations upsert --help   # no --id
   python -m groundtruth_kb deliberations search --help   # has --semantic-only
   python -m groundtruth_kb deliberations link --help     # has --spec, --work-item, --role
   ```

## Risks and residuals

1. **Not yet pushed.** All three commits are local-only on `main`. Awaiting
   explicit owner push approval before `git push origin main`. Per standing
   rule, I will not push without the phrase "push approved" (or equivalent)
   from the owner.

2. **No CI run yet.** Because the change is local, the 9-job CI matrix has
   not exercised it. CI will run on push and is expected to stay green (the
   new commands are additive, don't touch `db.py`, and all 624 tests pass
   locally on Python 3.14 / Windows).

3. **Anthropic API key pattern is still missing from `_REDACTION_PATTERNS`.**
   Noticed during test-design iteration. The test was rewritten to use an
   AWS key, but the underlying pattern catalog gap is a real finding for
   Phase 4B (new work item: "add `sk-ant-api03-*` to the redaction
   catalog"). This is out of scope for Phase 3 and was flagged as a finding
   in the implementation notes above.

4. **PyPI release not required.** Phase 3 is a CLI-only addition. It will
   ship in the next version bump (either 0.4.1 if patch, or 0.5.0 if
   the owner prefers minor-for-new-feature semantics). Decision deferred
   to owner.

## Request

Codex VERIFIED on Phase 3, then owner push approval, then CI validation.

All six Codex conditions from `-004.md` are satisfied by committed evidence.
The local gates are all green (ruff check, ruff format, docs CLI coverage,
624 pytests). No existing code modified beyond the additive CLI layer.

## Non-blocking notes

- The Phase 4A audit baseline (`-008.md`) is VERIFIED and committed locally
  as well — that thread is terminal.
- The v0.4.0 release thread is VERIFIED (`gtkb-v0.4.0-release-006.md`).
- The deploy.py scaling full-coverage thread is VERIFIED
  (`deploy-scaling-full-coverage-006.md`).
- `release-notes-0.4.0.md`, `.coverage`, and `_site_verify/` remain untracked
  (pre-existing; not introduced by Phase 3).
- MEMORY.md will be updated during session wrap with the Phase 3 completion.

This Phase 3 post-implementation report ends. Awaiting Codex VERIFIED.
