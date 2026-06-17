GO

# Proposal Review: GT-KB Phase 4B.5b Internal Helpers mypy --strict

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/gtkb-phase4b5b-internal-helpers-mypy-001.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The proposed scope is acceptable. The current GT-KB `main` checkout is at the
claimed Phase 4B.6 terminal commit, the five-file strict mypy run reproduces
exactly 40 errors, and the current CI strict gate covers only the four public
API files. Proceed with the 4B.5b internal-helper cleanup, locking scope to all
current strict errors in the five named files rather than an exact 39-error
briefing count.

## Evidence

Target repo state:

```text
git rev-parse --abbrev-ref HEAD  main
git rev-parse --short HEAD       b427bc5
git status --short
?? .coverage
?? _site_verify/
?? groundtruth.db-shm
?? groundtruth.db-wal
?? release-notes-0.4.0.md
```

The untracked files above are local residue; there were no tracked modifications
reported by `git status --short`.

Strict mypy reproduction:

```text
python -m mypy --strict --follow-imports=silent \
  src/groundtruth_kb/seed.py \
  src/groundtruth_kb/web/app.py \
  src/groundtruth_kb/reconciliation.py \
  src/groundtruth_kb/spec_scaffold.py \
  src/groundtruth_kb/project/scaffold.py

Found 40 errors in 5 files (checked 5 source files)
```

Error distribution by file from the same run:

```text
src/groundtruth_kb/spec_scaffold.py        4 errors
src/groundtruth_kb/reconciliation.py       8 errors
src/groundtruth_kb/web/app.py             12 errors
src/groundtruth_kb/seed.py                16 errors
src/groundtruth_kb/project/scaffold.py     1 error
```

Current CI strict gate:

```text
.github/workflows/ci.yml:50  mypy --strict on public API surface
.github/workflows/ci.yml:52  python -m mypy --strict \
.github/workflows/ci.yml:53  src/groundtruth_kb/db.py \
.github/workflows/ci.yml:54  src/groundtruth_kb/config.py \
.github/workflows/ci.yml:55  src/groundtruth_kb/cli.py \
.github/workflows/ci.yml:56  src/groundtruth_kb/gates.py
```

The existing regression guard is also public-API-specific:

```text
tests/test_public_api_type_checks.py:20-25
PUBLIC_API_FILES = [
    "src/groundtruth_kb/db.py",
    "src/groundtruth_kb/config.py",
    "src/groundtruth_kb/cli.py",
    "src/groundtruth_kb/gates.py",
]
```

## Required Implementation Constraints

1. Scope is the five named files and all current strict errors in those files.
   Do not chase an exact "39 errors" count.

2. Keep runtime behavior unchanged. Use annotations, local narrowing, and
   targeted casts only where the data shape is already enforced by surrounding
   code.

3. Use `TypedDict` or helper types only where they reduce repeated unsafe casts
   and reflect a stable payload shape. Do not convert this into a broad modeling
   or schema refactor.

4. Expand CI strict coverage for the five internal-helper files. Because the
   repo already has a public API mypy regression test, either add a matching
   internal-helper type-check guard or explicitly document why the CI-only gate
   is sufficient for this phase.

5. Do not stage unrelated local residue in the GT-KB checkout (`.coverage`,
   `_site_verify/`, database WAL/SHM files, or release notes).

## Verification Required After Implementation

Run and report:

```text
python -m mypy --strict --follow-imports=silent <the five target files>
python -m pytest -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

If the change is pushed to `main`, wait for GitHub Actions and include the
commit SHA plus CI run URL in the follow-up bridge report.

## Answers To Prime Questions

Lock scope at "all current errors in these five files." The locally reproduced
count is 40, matching the proposal's empirical section rather than the older
briefing count.

Prefer local narrowing and `Mapping`/`dict[str, Any]` style annotations first.
Use `TypedDict` only when it makes repeated JSON or database-row access safer
without expanding the behavioral surface.

Direct implementation on `main` is acceptable under the stated Phase 4
pre-approval and prior 4B.6 pattern, provided unrelated untracked files are not
included and CI is observed after push.

## Recommended Action

Proceed with Phase 4B.5b implementation under the constraints above.

