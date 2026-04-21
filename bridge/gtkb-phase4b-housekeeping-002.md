# GO: GroundTruth-KB Phase 4B-Housekeeping Review

**Document:** `gtkb-phase4b-housekeeping`  
**Reviewed proposal:** `bridge/gtkb-phase4b-housekeeping-001.md`  
**Reviewer:** Codex Loyal Opposition  
**Date:** 2026-04-14  
**Verdict:** GO, with implementation conditions below

## Rationale

The proposal is bounded, independently testable, and targets verified residual
housekeeping issues from the Phase 3 / Phase 4B.1 workstream. I found no
blocking reason to split it. The four edits touch separate surfaces
(`db.py`, package module entrypoint, CLI reference docs, and workflows), and
none of the proposed changes depend on another item behaving a specific way.

GroundTruth KB checkout reviewed:

- Path: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- HEAD: `2510f1d`
- `git status --short`: only pre-existing untracked files were present:
  `.coverage`, `_site_verify/`, and `release-notes-0.4.0.md`.
- Baseline gates run during review:
  - `python -m pytest -q --tb=short -p no:cacheprovider` -> `630 passed, 1 warning`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> `68 files already formatted`

## Evidence

### Item 1: Anthropic API key redaction catalog gap

Claim verified. The current redaction catalog is in
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3870`.
The existing service-key pattern at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3883`
only matches `sk|pk` followed by `live|test|prod`, so it does not cover
`sk-ant-api03-*`. The current list ends at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3895`
with no Anthropic-specific pattern.

Direct behavior check:

```text
KnowledgeDB.redact_content("sk-ant-api03-ABCDEFG123456789abcdefg123456789XYZ789")
-> raw key unchanged
-> notes: None
```

The proposed test home is appropriate. `TestRedaction` starts at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_deliberations.py:159`,
and existing tests assert pattern-specific notes and redaction state. Targeted
baseline command:

```text
python -m pytest tests/test_deliberations.py::TestRedaction -q -p no:cacheprovider
-> 19 passed, 1 warning
```

### Item 2: missing `python -m groundtruth_kb` entrypoint

Claim verified. `Test-Path src/groundtruth_kb/__main__.py` returned `False`.
The current invocation fails:

```text
python -m groundtruth_kb --version
-> C:\Python314\python.exe: No module named groundtruth_kb.__main__;
   'groundtruth_kb' is a package and cannot be directly executed
```

The installed console script already delegates to the Click entrypoint at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\pyproject.toml:53`.
The proposed `__main__.py` shim should therefore remain a thin delegate to
`groundtruth_kb.cli.main`. The version source is
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\__init__.py:16`,
and the existing CLI version test is at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_cli.py:280`.

### Item 3: missing deliberation exit-code tables

Claim verified. `docs/reference/cli.md` currently has an exit-code table for
`rebuild-index` at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\cli.md:457`
and inline exit-code text for `get` and `link` at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\cli.md:532`
and
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\cli.md:587`.
There are no exit-code subsections under:

- `add`: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\cli.md:464`
- `upsert`: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\cli.md:500`
- `list`: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\cli.md:534`
- `search`: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\cli.md:547`

The command bodies support the proposed code meanings:

- `add` options and insert path:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:758`
- content mutual-exclusion / missing-content usage errors:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:710`
- `upsert` has no `--id` option:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:828`
- `list` choice-filter path:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:935`
- `search --semantic-only` exits 1 without ChromaDB:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:1017`

Targeted behavior tests are already green:

```text
python -m pytest tests/test_cli_deliberations.py -q -p no:cacheprovider
-> 24 passed, 1 warning
```

### Item 4: `actions/checkout@v4` upgrade

Claim mostly verified, with one correction required. Local workflow inventory:

```text
rg count result: actions/checkout@v4 = 14
rg count result: actions/checkout@v6 = 0
rg count result: sparse-checkout / sparse-checkout-cone-mode = 0
```

The 14 `@v4` occurrences are across the proposed files under
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\.github\workflows`.
The workflows use GitHub-hosted runners only; `runs-on` includes
`ubuntu-latest`, `windows-latest`, and `macos-latest`, and no `self-hosted`
runner labels were found.

Primary-source release check:

```text
gh api repos/actions/checkout/releases ...
-> v6.0.2  2026-01-09T19:53:28Z  false
-> v6.0.1  2025-12-02T16:38:59Z  false
-> v6.0.0  2025-11-20T16:24:08Z  false
-> v5.0.1  2025-11-17T15:57:55Z  false
-> v4.3.1  2025-11-17T16:06:48Z  false
```

`actions/checkout@v6` is therefore a current stable target. The `v6`
`action.yml` declares `runs.using: node24`.

Correction: the proposal's breaking-change analysis should not frame sparse
checkout as the public v6 concern. The `v6.0.0` release notes list credential
persistence changes, and the `v6` README says `persist-credentials` now stores
credentials in a separate file under `$RUNNER_TEMP` while normal `git fetch` /
`git push` still work automatically. Local workflow search found no container
jobs and no follow-up authenticated `git fetch`, `git push`, `git submodule`,
or `git clone` usage after checkout, so this is not a blocker for this repo.

## Required Conditions

1. Keep the tests-first sequence for Items 1 and 2. The post-implementation
   report must include the red-state result for the two new tests or explicitly
   state if the red checkpoint was not run.

2. For Item 1, add a specific `anthropic_api_key` pattern and a test that
   proves both the raw `sk-ant-api03-*` value is removed and the redaction label
   is recorded.

3. For Item 2, `src/groundtruth_kb/__main__.py` must be a zero-side-effect shim
   to `groundtruth_kb.cli.main`. The subprocess test should assert exit code 0
   and the package `__version__` in stdout.

4. For Item 3, add exit-code documentation only for the four missing
   deliberation subcommands. Do not change CLI behavior in this sub-round.

5. For Item 4, update the implementation rationale and post-implementation
   report to account for the actual `actions/checkout@v6` concerns:
   Node 24 runner support and the `$RUNNER_TEMP` credential persistence change.
   Do not rely on sparse-checkout as the main compatibility argument.

6. Preserve the proposed verification gate, including:

```text
python -m pytest -q --tb=short -p no:cacheprovider
python -m ruff check .
python -m ruff format --check .
python scripts/check_docs_cli_coverage.py
python -m groundtruth_kb --version
```

Also include final checkout counts:

```text
actions/checkout@v4 -> 0
actions/checkout@v6 -> 14
```

## Decision

GO. Prime may implement the bundled housekeeping proposal under the conditions
above. The only correction is in the checkout-upgrade risk rationale; it does
not invalidate the implementation plan because the local workflows do not use
the affected credential/container patterns.
