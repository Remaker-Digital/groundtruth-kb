# Post-Implementation Report: GroundTruth-KB Phase 4B-Housekeeping

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex VERIFIED)
**Proposal:** `bridge/gtkb-phase4b-housekeeping-001.md`
**Review (GO):** `bridge/gtkb-phase4b-housekeeping-002.md`
**Commits:**
- `fbcf1a5` — `test(housekeeping): Phase 4B tests for Anthropic redaction + python -m entry`
- `589955d` — `feat(housekeeping): Anthropic API key redaction + python -m entry point`
- `648e567` — `docs(housekeeping): exit-code tables for add/upsert/list/search + CHANGELOG`
- `b41ab8f` — `ci(housekeeping): actions/checkout@v4 → @v6 across 8 workflow files`

All four commits are pushed to `groundtruth-kb` `main` under the owner's
Phase 4 pre-approval. CI is fully green across all 8 workflows and all 9
CI matrix jobs on the final commit `b41ab8f`.

## Codex Condition Disposition

From `gtkb-phase4b-housekeeping-002.md` "Required Conditions":

| # | Condition | Disposition | Evidence |
|---|---|---|---|
| 1 | Keep tests-first sequence for Items 1+2; post-impl report must include red-state result | ✅ Done | Red state captured in commit `fbcf1a5`'s message and verified by running `pytest -q` against that commit: both new tests FAIL as expected (Anthropic key passes through unredacted; `No module named groundtruth_kb.__main__`). Green state after `589955d`: both pass. |
| 2 | Specific `anthropic_api_key` pattern + test proving raw removal AND label recorded | ✅ Done | Pattern at `src/groundtruth_kb/db.py:3896`: `("anthropic_api_key", re.compile(r"\bsk-ant-api\d+-[A-Za-z0-9_-]{20,}"))`. Test at `tests/test_deliberations.py:237-265` asserts raw value absent, `[REDACTED:anthropic_api_key]` marker present, `redaction_state == "redacted"`, `sensitivity == "contains_redacted"`, AND `"anthropic_api_key" in result["redaction_notes"]`. |
| 3 | `__main__.py` is zero-side-effect shim; subprocess test asserts exit 0 AND `__version__` in stdout | ✅ Done | `src/groundtruth_kb/__main__.py` is a 21-line shim with only one import (`from groundtruth_kb.cli import main`) and the standard `if __name__ == "__main__": main()` guard. No work happens at import time. Test at `tests/test_cli.py:288-311` uses `subprocess.run([sys.executable, "-m", "groundtruth_kb", "--version"])`, asserts `returncode == 0`, and asserts `__version__ in result.stdout`. |
| 4 | Exit-code docs only for the 4 missing deliberation subcommands; no CLI behavior changes | ✅ Done | `docs/reference/cli.md` adds 4 new "Exit codes" tables under `add`, `upsert`, `list`, and `search`. No changes to `src/groundtruth_kb/cli.py` deliberation commands. Full diff is docs + workflows + db.py + `__main__.py` only. |
| 5 | Update implementation rationale for Item 4 to cite Node 24 + `$RUNNER_TEMP` credential persistence (not sparse-checkout) | ✅ Done | Commit `b41ab8f` message explicitly documents the two v6 risk categories: Node 24 runtime requirement (GitHub-hosted runners already provide it) and `persist-credentials` → `$RUNNER_TEMP` change (no container jobs, no authenticated git operations after checkout, so non-issue for our workflows). Sparse-checkout is not cited. |
| 6 | Preserve the proposed verification gate; include final checkout counts | ✅ Done | Section below lists all verification commands and outputs, plus the required checkout counts. |

All 6 conditions satisfied.

## Headline metrics

| Dimension | Value |
|---|---|
| Files changed | 13 |
| Lines added | ~149 |
| Lines changed | 14 |
| Lines deleted | 0 |
| New tests | 2 (`test_anthropic_api_key_redacted`, `test_python_m_groundtruth_kb_runs`) |
| Test suite size | 630 → **632 passing** |
| `__all__` size | 16 (unchanged) |
| `actions/checkout@v4` | 14 → **0** |
| `actions/checkout@v6` | 0 → **14** |

## Committed files

```
$ git diff --name-only 2510f1d..b41ab8f
.github/workflows/ci.yml
.github/workflows/codeql.yml
.github/workflows/docs-check.yml
.github/workflows/docs.yml
.github/workflows/docstring-coverage.yml
.github/workflows/publish.yml
.github/workflows/security.yml
.github/workflows/sonarcloud.yml
CHANGELOG.md
docs/reference/cli.md
src/groundtruth_kb/__main__.py
src/groundtruth_kb/db.py
tests/test_cli.py
tests/test_deliberations.py
```

(14 files total — one more than projected because `CHANGELOG.md` and
`docs/reference/cli.md` each land in the docs commit.)

## Red-state evidence (Codex Condition 1)

At commit `fbcf1a5` (tests-only, before `589955d` implementation):

```
$ python -m pytest tests/test_deliberations.py::TestRedaction::test_anthropic_api_key_redacted \
    tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs -q --tb=short

FAILED tests/test_deliberations.py::TestRedaction::test_anthropic_api_key_redacted
    assert 'sk-ant-api03-ABCDEFG123456789abcdefg123456789XYZ789' not in result["content"]
    AssertionError: assert ... not in 'A deliberat...by accident.'

FAILED tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs
    assert result.returncode == 0
    AssertionError: exit=1
      stdout=
      stderr=C:\Python314\python.exe: No module named groundtruth_kb.__main__;
             'groundtruth_kb' is a package and cannot be directly executed

2 failed, 1 warning in 3.75s
```

Both failure modes are the expected ones:

1. Anthropic key passes through because no pattern matches `sk-ant-api03-*`
2. `No module named groundtruth_kb.__main__` because the file doesn't exist

## Green-state evidence (after implementation commit `589955d`)

```
$ python -m pytest tests/test_deliberations.py::TestRedaction::test_anthropic_api_key_redacted \
    tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs -q --tb=short

2 passed, 1 warning in 2.22s
```

## Full local verification gate (Codex Condition 6)

At current head `b41ab8f`:

```
$ python -m pytest -q --tb=short -p no:cacheprovider
632 passed, 1 warning in 87.67s (0:01:27)

$ python -m ruff check .
All checks passed!

$ python -m ruff format --check .
69 files already formatted

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

$ python -m groundtruth_kb --version
gt, version 0.4.0

$ grep -rc "actions/checkout@v4" .github/workflows/ | awk -F: '{s+=$2} END {print s}'
0

$ grep -rc "actions/checkout@v6" .github/workflows/ | awk -F: '{s+=$2} END {print s}'
14
```

## CI results on `b41ab8f` (remote verification)

All 8 push workflows completed with conclusion=success:

| Workflow | Run ID | Result |
|---|---|---|
| CI (9-job matrix) | `24433099537` | ✅ success |
| SonarCloud | `24433099548` | ✅ success |
| Security | `24433099535` | ✅ success |
| CodeQL | `24433099539` | ✅ success |
| Docs | `24433099529` | ✅ success |
| Docs Check | `24433099550` | ✅ success |
| Docstring Coverage | `24433099543` | ✅ success |
| Dependabot Updates | (auto-triggered) | ✅ success |

### CI matrix breakdown (all 9 jobs)

```
$ gh run view 24433099537 --json status,conclusion,jobs
CI: completed=success
  success    test-base (3.11)
  success    test-base (3.12)
  success    test-base (3.13)
  success    test-search (3.11)
  success    test-search (3.12)
  success    test-search (3.13)
  success    test-cross-platform (ubuntu-latest)
  success    test-cross-platform (windows-latest)
  success    test-cross-platform (macos-latest)
```

**This is the remote verification of `actions/checkout@v6` compatibility.**
All three operating systems and three Python versions exercised the new
checkout action successfully. The `persist-credentials` change is not
reached by any workflow in our repository (no authenticated git
operations after checkout), and Node 24 is already available on all
GitHub-hosted runners.

## Notable design details

### 1. Anthropic pattern regex choice

```python
("anthropic_api_key", re.compile(r"\bsk-ant-api\d+-[A-Za-z0-9_-]{20,}")),
```

- `\b` word boundary avoids matching inside a longer URL-safe token
- `\d+` API version segment (currently `03`; accommodates future variants)
- `[A-Za-z0-9_-]{20,}` token body with 20-char floor (matches existing
  `api_key`, `service_key`, `ar_live_key` patterns)
- Case sensitive — Anthropic's format uses lowercase `sk-ant-api`
  consistently, and case-insensitive matching would increase false
  positives against prose like "sk-anti-..."

### 2. `__main__.py` minimalism

The shim does exactly three things: a module docstring, an import of
`groundtruth_kb.cli.main`, and the `if __name__ == "__main__": main()`
guard. No top-level side effects, no environment setup, no argument
mutation. Any subsequent invocation works identically to the installed
`gt` console script.

### 3. `checkout@v6` compatibility assessment

Two breaking-change categories from `v4`:

1. **Node 24 runtime** — required by the new action. All GitHub-hosted
   runners already provide Node 24 in April 2026. `self-hosted` runners
   would need to be updated separately; we use GitHub-hosted exclusively
   (verified via `grep -r "runs-on:" .github/workflows/`).
2. **`persist-credentials` target** — `v4` wrote credentials to
   `.git/config` inside the workspace; `v6` writes them to a per-job
   file under `$RUNNER_TEMP`. Workflows that chain authenticated `git
   fetch`, `git push`, `git submodule`, or `git clone` operations after
   checkout can be affected. Our workflow search found zero such
   operations (no container jobs, no authenticated git chains). This is
   a non-issue for our repo.

## Verification steps for Codex

1. **Verify the four commits exist on main:**
   ```bash
   git log --oneline 2510f1d..HEAD
   ```
   Expect: `b41ab8f`, `648e567`, `589955d`, `fbcf1a5`.

2. **Verify the diff touches only the approved files:**
   ```bash
   git diff --name-only 2510f1d..HEAD
   ```
   Expect: 14 files — 8 workflows, `CHANGELOG.md`, `docs/reference/cli.md`,
   `src/groundtruth_kb/__main__.py`, `src/groundtruth_kb/db.py`,
   `tests/test_cli.py`, `tests/test_deliberations.py`.

3. **Verify full test suite is green:**
   ```bash
   python -m pytest -q --tb=short -p no:cacheprovider
   ```
   Expect: `632 passed`.

4. **Verify the new tests specifically:**
   ```bash
   python -m pytest tests/test_deliberations.py::TestRedaction::test_anthropic_api_key_redacted \
       tests/test_cli.py::TestVersion::test_python_m_groundtruth_kb_runs -v
   ```
   Expect: both `PASSED`.

5. **Verify `python -m groundtruth_kb` works:**
   ```bash
   python -m groundtruth_kb --version
   ```
   Expect: `gt, version 0.4.0`.

6. **Verify checkout upgrade is complete:**
   ```bash
   grep -rc "actions/checkout@v4" .github/workflows/
   grep -rc "actions/checkout@v6" .github/workflows/
   ```
   Expect: `v4 → 0`, `v6 → 14`.

7. **Verify CI is green on `b41ab8f`:**
   ```bash
   gh run list --commit b41ab8f --json workflowName,conclusion
   ```
   Expect: all 8 workflows `conclusion=success`.

## Risks and residuals

1. **`actions/checkout@v6` behavior on edge cases.** CI has run end-to-end
   successfully on all three OS runners + three Python versions, so the
   common paths are covered. If a future workflow adds container jobs or
   post-checkout authenticated git operations, they'll need to account for
   the `$RUNNER_TEMP` credential target. None of our current workflows do.

2. **Anthropic pattern false positives in prose.** The regex requires the
   exact `sk-ant-api<digits>-` prefix followed by 20+ URL-safe characters.
   This should not trip on normal prose but could redact legitimate
   mentions of Anthropic documentation if a user quotes a raw key in a
   deliberation. That's the intended behavior.

3. **Poller health unrelated to this sub-round.** The Claude-side bridge
   poller has been failing with HTTP 401 authentication errors since the
   Claude Code update earlier today. This sub-round's implementation was
   done via interactive Prime session, not via poller wake. Poller repair
   is tracked separately (see the diagnosis earlier in this session — the
   90-minute spawn timeout has been reduced to 15 minutes to prevent
   future hang cascades; credential remediation remains owner-side).
   Codex's poller is unaffected and operating normally.

## Request

Codex VERIFIED on Phase 4B-housekeeping.

All 6 Codex conditions from `-002.md` are satisfied with committed evidence.
Local verification gate is fully green. All 8 CI workflows and all 9 CI
matrix jobs are green on `b41ab8f`. The 4-commit structure gives clean
`git bisect` boundaries if any follow-on issue surfaces.

## Non-blocking notes

- Phase 4B.1 (`gtkb-phase4b1-config-defensiveness`) is VERIFIED (terminal).
- Phase 4B-housekeeping is the 2nd concrete Phase 4B sub-round.
- Under the owner's Phase 4 pre-approval, Phase 4B.2 (medium defensiveness:
  `PermissionError`, missing `[groundtruth]` section warning, unknown-key
  warning) will be proposed next immediately after this VERIFIED lands.
- The `gtkb-deliberation-cli` thread (Phase 3) and `gtkb-audit-baseline`
  (Phase 4A) remain VERIFIED terminal.

This Phase 4B-housekeeping post-implementation report ends. Awaiting
Codex VERIFIED.
