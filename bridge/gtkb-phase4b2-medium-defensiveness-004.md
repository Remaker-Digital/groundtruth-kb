# VERIFIED: GroundTruth-KB Phase 4B.2 Medium Config Defensiveness

**Document:** `gtkb-phase4b2-medium-defensiveness`
**Reviewed report:** `bridge/gtkb-phase4b2-medium-defensiveness-003.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-15
**Verdict:** VERIFIED

## Rationale

The Phase 4B.2 implementation satisfies the conditions from the GO review in
`bridge/gtkb-phase4b2-medium-defensiveness-002.md`. The committed code wraps
`PermissionError` in `GTConfigError` with exception chaining, warns for missing
`[groundtruth]` without implying `[gates]` or `[search]` are ignored, warns for
unknown config keys by name, updates the reference docs, and passes the agreed
verification gate.

I found one non-blocking audit-trail discrepancy: the post-implementation report
says the `tests/test_reconciliation.py` fixture correction was made in the
implementation commit, but git shows it landed in the tests-first commit
`0119462`. This does not change the verification result because the commit
message documents the fixture correction, the final behavior is verified, and
the change is test-only.

## Evidence

### Bridge review scope

Read the full active bridge entry and referenced versions:

- `bridge/gtkb-phase4b2-medium-defensiveness-003.md`
- `bridge/gtkb-phase4b2-medium-defensiveness-002.md`
- `bridge/gtkb-phase4b2-medium-defensiveness-001.md`

### GroundTruth-KB checkout state

Reviewed checkout:

```text
E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
git rev-parse --short HEAD
-> 249cdd4

git status --short
-> ?? .coverage
-> ?? _site_verify/
-> ?? release-notes-0.4.0.md
```

The untracked files were left untouched.

Commit sequence matches the report:

```text
git log --oneline b41ab8f..HEAD
-> 249cdd4 docs: Phase 4B.2 - update Exceptions section, add Warnings section
-> eb3c6a8 feat(config): Phase 4B.2 - PermissionError wrap + TOML section warnings
-> 0119462 test(config): Phase 4B.2 tests-first - permission, missing section, unknown keys
```

Diff scope matches the report:

```text
git diff --stat b41ab8f..HEAD
-> CHANGELOG.md                    |  26 ++++++++++
-> docs/reference/configuration.md |  43 ++++++++++++++--
-> src/groundtruth_kb/config.py    |  59 +++++++++++++++++-----
-> tests/test_config.py            | 105 +++++++++++++++++++++++++++++++++++++++-
-> tests/test_reconciliation.py    |   2 +-
-> 5 files changed, 216 insertions(+), 19 deletions(-)
```

### GO condition verification

1. Tests-first red state is documented. `bridge/gtkb-phase4b2-medium-defensiveness-003.md`
   reports `15 passed, 4 failed`, and commit `0119462` records the red state in
   its commit message. `git show --name-status --oneline 0119462 eb3c6a8 249cdd4`
   shows `0119462` changed tests, `eb3c6a8` changed `src/groundtruth_kb/config.py`,
   and `249cdd4` changed docs.

2. `PermissionError` is wrapped in `GTConfigError` with the path, a permissions
   hint, and `from exc` chaining. Evidence:
   `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:28`
   documents `GTConfigError`; line 35 names `PermissionError`; lines 150-155
   catch `PermissionError` before `TOMLDecodeError` and raise `GTConfigError`
   from the original exception.

3. Missing `[groundtruth]` warning wording does not imply the whole file is
   ignored. Evidence:
   `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:163`
   emits the warning; lines 165-168 say core settings use env/defaults while
   `[gates]` and `[search]` sections remain applied; lines 176-189 still route
   those sections into known config fields.

4. Warning stacklevel points at the external `GTConfig.load()` call site.
   Evidence: `config.py:170` uses `stacklevel=3` for the helper warning and
   `config.py:111` uses `stacklevel=2` for the `GTConfig.load()` unknown-key
   warning. A focused smoke test reported `missing_filename=<stdin>` at the
   caller line and `unknown_filename=<stdin>` at the caller line.

5. Unknown-key warning names key(s) and does not warn for supported `[gates]`
   or `[search]` values. Evidence:
   `config.py:104-112` diffs merged keys against dataclass fields and names the
   sorted unknown keys. Focused smoke output:

```text
known_sections_warning_count= 0
known_sections_gates= ['pkg:Gate']
known_sections_chroma= C:\Users\micha\AppData\Local\Temp\tmpjqh8dc0s\chroma
unknown_count= 1
unknown_message= groundtruth config has unknown keys that will be ignored: ['bran_color']. Check for typos in your groundtruth.toml.
```

6. Docs were updated. Evidence:
   `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\configuration.md:187`
   starts the exception table; line 190 documents `GTConfigError` for invalid
   TOML and permissions problems with chained causes; line 215 starts the new
   Warnings section; lines 222-227 document missing `[groundtruth]`, unknown
   keys, and call-site warning locations.

7. Verification gate passes:

```text
python -m pytest tests/test_config.py -q --tb=short
-> 19 passed, 1 warning in 0.19s

python -m pytest -q --tb=short -p no:cacheprovider
-> 636 passed, 1 warning in 87.61s

python -m ruff check .
-> All checks passed!

python -m ruff format --check .
-> 69 files already formatted

python scripts/check_docs_cli_coverage.py
-> All documentation checks passed.

python -c "from groundtruth_kb import __all__; print(len(__all__))"
-> 16
```

The single warning in both pytest runs is the pre-existing ChromaDB
`DeprecationWarning` from
`C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\chromadb\telemetry\opentelemetry\__init__.py:128`.

## Findings

No blocking findings.

Low-severity report accuracy note: `bridge/gtkb-phase4b2-medium-defensiveness-003.md`
attributes the `tests/test_reconciliation.py` fixture correction to the
implementation commit. Git evidence shows the correction was part of `0119462`,
the tests-first commit:

```text
git show --name-status --oneline 0119462
-> 0119462 test(config): Phase 4B.2 tests-first - permission, missing section, unknown keys
-> M tests/test_config.py
-> M tests/test_reconciliation.py
```

Impact: audit-trail wording only. The commit message itself documents the
fixture correction, and the final verification gate passes.

## Required Action Items

None. VERIFIED.
