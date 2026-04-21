# Verification Review: GT-KB Phase 4B.5b Internal Helpers mypy --strict

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/gtkb-phase4b5b-internal-helpers-mypy-003.md`
- `bridge/gtkb-phase4b5b-internal-helpers-mypy-004.md`
Prior GO: `bridge/gtkb-phase4b5b-internal-helpers-mypy-002.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Inspected HEAD: `31d2c39`

## Claim

The implementation is not yet verifiable because the GT-KB checkout fails the
required formatting gate. The type-checking work itself is clean locally, and
the test suite passes, but `python -m ruff format --check .` reports that the
new internal-helper type-check regression file would be reformatted.

## Evidence

Target repo state:

```text
git rev-parse --short HEAD        31d2c39
git rev-parse --short origin/main 31d2c39
git log --oneline -3
31d2c39 ci(mypy): add strict gate + regression guard for 5 internal helpers (4B.5b)
4870e7d fix(mypy): phase 4B.5b -- internal helpers (5 files, 40 errors)
b427bc5 fix(mypy): restore except-block chromadb=None pattern to avoid [no-redef]
```

Local strict mypy on the five target files passes:

```text
python -m mypy --strict --follow-imports=silent \
  src/groundtruth_kb/seed.py \
  src/groundtruth_kb/web/app.py \
  src/groundtruth_kb/reconciliation.py \
  src/groundtruth_kb/spec_scaffold.py \
  src/groundtruth_kb/project/scaffold.py

Success: no issues found in 5 source files
```

The public and internal helper type-check regression tests pass:

```text
python -m pytest tests/test_internal_helpers_type_checks.py tests/test_public_api_type_checks.py -q --tb=short
2 passed, 1 warning in 36.78s
```

The full local test suite passes, with the current observed count at 639 tests:

```text
python -m pytest -q --tb=short
639 passed, 1 warning in 134.97s
```

Ruff lint passes but format check fails:

```text
python -m ruff check .
All checks passed!

python -m ruff format --check .
Would reformat: tests\test_internal_helpers_type_checks.py
1 file would be reformatted, 71 files already formatted
```

Formatter diff:

```diff
--- tests\test_internal_helpers_type_checks.py
+++ tests\test_internal_helpers_type_checks.py
@@ -62,6 +62,5 @@
         timeout=120,
     )
     assert result.returncode == 0, (
-        f"mypy --strict found issues on internal helpers:\n"
-        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
+        f"mypy --strict found issues on internal helpers:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
     )
```

CI observation:

```text
gh run list --commit 31d2c39 --limit 20 --json databaseId,status,conclusion,name,headSha,url,createdAt
[]
```

No GitHub Actions runs were visible for `31d2c39` from this checkout at review
time, so CI green could not be confirmed.

## Blocking Finding

The required verification command `python -m ruff format --check .` is not clean.
This violates the GO verification requirements and should be fixed before this
item is marked VERIFIED.

## Required Action Items

1. Run `python -m ruff format tests/test_internal_helpers_type_checks.py` or make
   the equivalent one-line formatting change manually.

2. Re-run and report:

```text
python -m ruff format --check .
python -m ruff check .
python -m mypy --strict --follow-imports=silent <five target files>
python -m pytest tests/test_internal_helpers_type_checks.py tests/test_public_api_type_checks.py -q --tb=short
python -m pytest -q --tb=short
```

3. Confirm CI status for the final pushed commit, or state clearly if GitHub
   Actions did not trigger and why.

## Residual Risk

No type-checking blocker was found locally. The current blocker is formatting
plus missing CI observation for the pushed head.

