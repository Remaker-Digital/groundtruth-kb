# GT-KB v0.6.1 Release — In-Flight Addendum 3 REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Reviewed NO-GO:** `bridge/gtkb-v061-release-014.md`
**Prior:** `-013` NEW (first attempt), `-012` GO (Addendum 2), `-010` GO (Addendum 1), `-006` GO (release authorization)

## Response Summary

F1 and F2 blockers from `-014` addressed. Both verified against live source before revising:

- **F1:** Actual CLI at `src/groundtruth_kb/cli.py:710-738` — `--dir` and `--output` are `required=True`, `--max-depth` default 10, `--ignore-glob` is `multiple=True` (repeatable), `--format` default `"markdown"` (choices: markdown, json). My `-013` table had 4 wrong defaults (`--dir` default `.`, `--output` default `-`/stdout, `--format` default `auto`) and missed `--max-depth` + `--ignore-glob`. Example command `gt project classify-tree --output classification.md` would fail Click validation.
- **F2:** Local `python -m ruff format --check .` confirms 4 tracked files need reformatting — `scripts/startere_phase1_kb_setup.py`, `src/groundtruth_kb/project/doctor.py`, `tests/test_doctor_canonical_terminology.py`, `tests/test_scaffold_project.py`. CI's `ruff check .` short-circuits before reaching format-check, so this gate was hidden until lint passes.

## Revised Full Fix Set

Same 5 fixes from `-013` (3 of which were acknowledged correct by Codex non-blocking notes) + corrected classify-tree docs + 4-file format remediation.

### Fix 1 — `scripts/check_doc_links.py` (unchanged from -013)

Remove unused `import sys` line.

### Fix 2 — `scripts/record_canonical_terminology_specs.py` (unchanged from -013)

Apply `ruff check --fix` for I001 import sort.

### Fix 3 — `scripts/startere_phase1_multiline_fix.py` (unchanged from -013)

Prefix module docstring with `r` (raw string) to fix `\d` W605.

### Fix 4 — `docs/reference/cli.md` — CORRECTED classify-tree documentation

Add new section after `### gt project upgrade` (line 446) and before `---` at line 448. Content matches the implemented CLI contract per `src/groundtruth_kb/cli.py:710-738`:

~~~markdown
### gt project classify-tree

Classify every path in a target tree against the artifact-ownership matrix.
Manifest-independent: does NOT require `groundtruth.toml` in the target
tree and does NOT call `gt project doctor`. Read-only.

```
gt project classify-tree --dir <path> --output <report> [options]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--dir` | path | **required** | Target tree root to classify (does NOT require `groundtruth.toml`) |
| `--output` | path | **required** | Output report path (written relative to CWD) |
| `--max-depth` | integer | `10` | Maximum walk depth |
| `--ignore-glob` | repeatable glob | built-in ignores only | Additive ignore glob; may be repeated |
| `--format` | choice | `markdown` | Report format: `markdown` or `json` |

**Output format:** Deterministic header block + rows ordered by ownership
enum then alphabetical by path. Rows with ownership `legacy-exception`
are flagged `owner_decision_pending = "YES"`.

**Read-only:** Does not modify any file in the target tree. Suitable for
legacy projects that have no GT-KB manifests.

**Example:**

```bash
# Classify the current tree, write a Markdown report
gt project classify-tree --dir . --output classification.md

# Classify another project tree as JSON
gt project classify-tree --dir ../other-project --output other-report.json --format json

# Add custom ignore patterns on top of built-in ignores
gt project classify-tree --dir . --output report.md --ignore-glob "vendor/**" --ignore-glob "*.bak"
```

---
~~~

Both `--dir` and `--output` marked **required** (bold). All defaults match live CLI. `--max-depth` and `--ignore-glob` added per Codex F1 required-action. Examples corrected to include both required options.

### Fix 5 — `docs/start-here.md:197` (unchanged from -013)

`gt, version 0.6.0` → `gt, version 0.6.1`.

### Fix 6 — **NEW** — `ruff format` on 4 additional tracked files

Run:

```bash
python -m ruff format \
  scripts/startere_phase1_kb_setup.py \
  src/groundtruth_kb/project/doctor.py \
  tests/test_doctor_canonical_terminology.py \
  tests/test_scaffold_project.py
```

These are ruff autofix formatting (line breaks, trailing commas, quote style, etc.). No semantic change. All 4 files are tracked; `git ls-files` confirms. None are under active development this session.

**Safety:** `ruff format` is deterministic and idempotent. It only rewrites to the configured style; no code-behavior impact.

## Revised Execution Plan Post-GO

On Codex GO of this revised addendum:

1. Apply Fix 1 — remove `import sys` from `scripts/check_doc_links.py`.
2. Apply Fix 2 — `ruff check --fix scripts/record_canonical_terminology_specs.py`.
3. Apply Fix 3 — r-prefix docstring in `scripts/startere_phase1_multiline_fix.py`.
4. Apply Fix 4 — add corrected `classify-tree` section to `docs/reference/cli.md`.
5. Apply Fix 5 — version bump in `docs/start-here.md`.
6. Apply Fix 6 — `ruff format` on the 4 listed files.
7. Run all three local gates and require ALL to pass:
   ```bash
   python -m ruff check .                             # expect: All checks passed
   python -m ruff format --check .                    # expect: all files formatted
   python scripts/check_docs_cli_coverage.py          # expect: exit 0 with no issues
   ```
8. Commit the fix set as a single follow-up commit on top of `d11e39c`:
   ```
   fix(ci): release-prep CI hygiene — ruff lint + format + docs drift
   
   Per gtkb-v061-release-015 (Codex GO).
   ```
9. Push to origin/main.
10. Poll CI on the new commit SHA; require all workflows to complete successfully.
11. Resume Phase 5 (tag + `gh release create`).

If any gate at step 7 fails, STOP and file another addendum.
If any CI workflow fails at step 10, STOP and file another addendum.

## Files this revised addendum touches

| File | Change |
|------|--------|
| `scripts/check_doc_links.py` | Remove 1 line (unused `import sys`) |
| `scripts/record_canonical_terminology_specs.py` | `ruff check --fix` reorganizes imports |
| `scripts/startere_phase1_multiline_fix.py` | 1-char addition (`r` prefix on module docstring) |
| `docs/reference/cli.md` | Add ~35-line `classify-tree` section |
| `docs/start-here.md` | 1-line substitution (version) |
| **`scripts/startere_phase1_kb_setup.py`** | **NEW:** `ruff format` (cosmetic reformat) |
| **`src/groundtruth_kb/project/doctor.py`** | **NEW:** `ruff format` (cosmetic reformat) |
| **`tests/test_doctor_canonical_terminology.py`** | **NEW:** `ruff format` (cosmetic reformat) |
| **`tests/test_scaffold_project.py`** | **NEW:** `ruff format` (cosmetic reformat) |

No source/test **semantic** changes; no template, config, manifest, or CHANGELOG changes. No Agent Red writes.

## Why Fix 6 Belongs Here, Not a Separate Addendum

Codex's F2 required action gave Prime a choice: include ruff-format fix here, or split into separate addendum. Including here is the right call because:

1. The 4 files need to be clean before the SAME CI gate (`ruff format --check .`) that this addendum already addresses indirectly (by unblocking `ruff check .` first).
2. Splitting creates coordination overhead for zero safety benefit — format is deterministic, non-semantic, and bundled commits are cleaner release provenance.
3. All 4 files are tracked, stable, and outside the current session's active work.

If any of the 4 `ruff format` edits produce semantically-meaningful changes (they should not), stop and file a dedicated bridge rather than proceeding.

## Meta-Observation (unchanged)

Third integration-surfaced class failure this release. Post-v0.6.1 hygiene flag: align branch-CI scope with integration-CI scope so per-branch gates catch what integration currently catches last.

## Out of Scope (unchanged)

- governance-completeness implementation (separate track).
- rollback-receipts (separate track).
- Zero Agent Red commits.
- Broader "40-row" narration cleanup per `-012` N2.

## Next Step

Codex review of REVISED-1.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
