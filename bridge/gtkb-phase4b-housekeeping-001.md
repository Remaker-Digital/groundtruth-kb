# Proposal: GroundTruth-KB Phase 4B-Housekeeping

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex GO)
**Parent baseline:** `bridge/gtkb-audit-baseline-008.md` (VERIFIED)
**Related prior:** `bridge/gtkb-phase4b1-config-defensiveness-006.md` (VERIFIED, terminal)
**Prior deliberations search:** `search_deliberations()` for "Anthropic API key redaction", "__main__.py module", "actions/checkout Node 20", and "exit code table CLI" returned only loose semantic matches (DELIB-0619, DELIB-0021/0022, DELIB-0501/0265, DELIB-0220/0567). No prior decisions directly relevant to these four housekeeping items. Fresh scope.

## Summary

A single bundled sub-round that clears the four small items surfaced by
Phase 3 and Phase 4B.1 verification passes:

1. **Anthropic API key redaction catalog gap** (surfaced in Phase 3
   while writing `test_add_content_file_redaction` — had to switch to
   AWS key because `sk-ant-api03-*` isn't matched by any pattern in
   `_REDACTION_PATTERNS`).
2. **`src/groundtruth_kb/__main__.py` missing** (Codex observation A in
   Phase 3 verification `-006.md`: `python -m groundtruth_kb` fails with
   `No module named groundtruth_kb.__main__`). Confirmed still broken
   at current head `2510f1d`.
3. **Exit-code tables missing for 4 of 7 deliberation subcommands**
   (Codex observation B in Phase 3 verification `-006.md`: `rebuild-index`,
   `get`, `link` have exit-code tables in `docs/reference/cli.md` but
   `add`, `upsert`, `list`, `search` do not).
4. **`actions/checkout@v4` deprecation** (surfaced in Phase 3 CI
   annotations: "Node.js 20 actions are deprecated. … Once Node.js 24
   becomes the default … ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION …").

Each item is independent, bounded, and separately verifiable. Bundling
them keeps the review overhead low (one GO/VERIFIED round instead of
four) without mixing concerns that would complicate a revision.

## Non-goals

- Phase 4B.2 (remaining defensiveness findings 4/5/6): separate future
  sub-round.
- Phase 4B.3–4B.6 (docstrings, types, bridge runtime, CI gates):
  separate future sub-rounds.
- Agent Red workflow files. Agent Red has 26 `actions/checkout@v*`
  occurrences but they live in a separate repo and are not in scope
  for any GT-KB sub-round.
- Rotating or revoking any actual credentials. The Anthropic pattern
  addition is a redaction catalog fix, not an incident response.

## Design (per item)

### Item 1 — Anthropic API key redaction

**Baseline state.** `src/groundtruth_kb/db.py:3870-3895` defines
`_REDACTION_PATTERNS` with 16 labeled patterns including `api_key`,
`bearer_header`, `token`, `secret`, `connection_string`,
`azure_sas_key`, `github_pat`, `service_key` (which matches the
`sk-live-*`/`pk-live-*` family), `phone`, `email`, `ip_address`,
`aws_key`, and Agent Red's `ar_live_*`/`ar_user_*`/`ar_spa_plat_*`/
`pk_live_*`/`arsk_*` families. **Anthropic's `sk-ant-api<N>-<TOKEN>`
format is not in the list.**

The existing `service_key` pattern at `db.py:3883` is:

```python
("service_key", re.compile(r"(?:sk|pk)[-_](?:live|test|prod)[-_][A-Za-z0-9]{20,}", re.IGNORECASE)),
```

It requires one of `live|test|prod` after the `sk-` prefix and so does
NOT match `sk-ant-api03-*`.

**Proposed addition.** Insert a new entry at the end of the
`_REDACTION_PATTERNS` list:

```python
# Anthropic API key family: sk-ant-api<digits>-<token>
# Covers current form (sk-ant-api03-...) and future digit variants.
("anthropic_api_key", re.compile(r"\bsk-ant-api\d+-[A-Za-z0-9_-]{20,}")),
```

Notes on the regex:

- `\b` word-boundary so we don't match inside a longer URL-safe token.
- `\d+` for the API version (currently `03`, but anticipated to change).
- `[A-Za-z0-9_-]{20,}` for the token body (20-char floor matches the
  other `{20,}` patterns in the list).
- Case sensitive (no `re.IGNORECASE`) because the `sk-ant-api` prefix
  is always lowercase in Anthropic's current format; a case-insensitive
  match would increase false positives against prose.

**Test additions.** `tests/test_deliberations.py` already has a
`TestRedaction` class (line 160) with five tests:
`test_api_key_redacted`, `test_token_redacted`, `test_phone_redacted`,
`test_email_redacted`, `test_connection_string_redacted`. Add one
new test matching the same pattern:

```python
def test_anthropic_api_key_redacted(self, db):
    """sk-ant-api<version>-<token> is redacted by the anthropic_api_key pattern."""
    content = (
        "A deliberation body mentioning a leaked key "
        "sk-ant-api03-ABCDEFG123456789abcdefg123456789XYZ789 by accident."
    )
    result = db.insert_deliberation(
        id="DELIB-REDACT-ANT",
        source_type="owner_conversation",
        title="Anthropic key redaction",
        summary="verify anthropic_api_key pattern",
        content=content,
        changed_by="test",
        change_reason="seed",
    )
    assert "sk-ant-api03-ABCDEFG123456789abcdefg123456789XYZ789" not in result["content"]
    assert result["redaction_state"] == "redacted"
    assert "anthropic_api_key" in result["redaction_notes"]
```

This mirrors the structure of `test_api_key_redacted` at
`tests/test_deliberations.py:162-177`.

### Item 2 — `src/groundtruth_kb/__main__.py`

**Baseline state.** Confirmed at current head `2510f1d`:

```
$ python -m groundtruth_kb --version
C:\Python314\python.exe: No module named groundtruth_kb.__main__;
'groundtruth_kb' is a package and cannot be directly executed
```

Codex observation A from `gtkb-deliberation-cli-006.md` flagged this
during Phase 3 verification. Prime's post-impl report incorrectly
suggested users could smoke the CLI via `python -m groundtruth_kb
deliberations --help`. That invocation has never worked.

**Proposed addition.** New file `src/groundtruth_kb/__main__.py`:

```python
"""Entry point for ``python -m groundtruth_kb``.

Delegates to :func:`groundtruth_kb.cli.main` so the package supports
module-style invocation in addition to the installed ``gt`` console
script. Useful for CI matrices that want to avoid console-script path
resolution and for one-off debugging via
``python -m groundtruth_kb <command>``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from groundtruth_kb.cli import main

if __name__ == "__main__":
    main()
```

**Test additions.** Add one new test to `tests/test_cli.py`:

```python
def test_python_m_groundtruth_kb_runs():
    """`python -m groundtruth_kb --version` exits 0 and prints the version."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "gt" in result.stdout.lower() or __version_in_stdout(result.stdout)
```

where `__version_in_stdout` verifies the output matches the pattern
`gt, version X.Y.Z` that Click's `version_option` produces. (I'll
simplify this assertion to substring-check `groundtruth_kb.__version__`
in the actual test.)

**Why subprocess**: we want to prove the module-execution path works
end-to-end, not just that `cli.main` is callable. That's the thing
Codex flagged, so the test must exercise the full
`python -m groundtruth_kb` invocation.

### Item 3 — Exit-code tables for `add`/`upsert`/`list`/`search`

**Baseline state.** `docs/reference/cli.md` has exit-code tables for
`gt deliberations rebuild-index`, `gt deliberations get`, and
`gt deliberations link` (the latter two were added in the Phase 3
commit `98463bc`). `add`, `upsert`, `list`, and `search` do not have
tables.

**Proposed addition.** Add an "Exit codes" subsection under each of the
four commands in `docs/reference/cli.md`. The codes below were read
directly from `src/groundtruth_kb/cli.py` at session time — they are
the actual codes the commands produce, not a guess:

**For `gt deliberations add`:**

| Code | Meaning |
|------|---------|
| `0` | Deliberation inserted successfully |
| `1` | Database write failed (e.g. duplicate `id`, invalid FK) |
| `2` | Click validation error: missing required flag, invalid `--source-type`/`--outcome` choice, or `--content`/`--content-file` mutual exclusion |

**For `gt deliberations upsert`:**

| Code | Meaning |
|------|---------|
| `0` | Deliberation row written or matched |
| `1` | Database write failed |
| `2` | Click validation error, including passing `--id` (which `upsert` does not accept) |

**For `gt deliberations list`:**

| Code | Meaning |
|------|---------|
| `0` | Query completed (empty result is not an error) |
| `1` | Database access failed |
| `2` | Click validation error on filter choices |

**For `gt deliberations search`:**

| Code | Meaning |
|------|---------|
| `0` | Search completed (empty result is not an error) |
| `1` | `--semantic-only` requested but ChromaDB is not installed |
| `2` | Click validation error on flag values |

**No new tests.** These tables document existing behavior. The existing
24 tests in `tests/test_cli_deliberations.py` already assert the exit
codes documented above, so the docs change is a pure reference update.

### Item 4 — `actions/checkout@v4 → v6` workflow upgrade

**Baseline state.** 14 `actions/checkout@v4` occurrences across 8
workflow files in `.github/workflows/`:

| File | Occurrences |
|---|---:|
| `ci.yml` | 3 |
| `codeql.yml` | 1 |
| `docs-check.yml` | 1 |
| `docs.yml` | 1 |
| `docstring-coverage.yml` | 1 |
| `publish.yml` | 4 |
| `security.yml` | 2 |
| `sonarcloud.yml` | 1 |
| **Total** | **14** |

**Version choice — why `@v6`, not `@v5`.** I was initially going to
propose `@v5` per the GitHub deprecation annotation text, but
`gh api repos/actions/checkout/releases` returns:

```
{"tag_name":"v6.0.2","prerelease":false,"published_at":"2026-01-09"}
{"tag_name":"v6.0.1","prerelease":false,"published_at":"2025-12-02"}
{"tag_name":"v6.0.0","prerelease":false,"published_at":"2025-11-20"}
```

`v6` has been GA since November 2025 and is currently at `v6.0.2`
(January 2026). `v5` exists but is superseded — upgrading straight to
`v6` avoids doing this same dance again in three months.

**Breaking-change check.** `actions/checkout@v6` requires Node 24 at
runtime. GitHub-hosted runners already provide Node 24 in April 2026.
The other public breaking change from `@v4` to `@v6` is a tightening
of default `sparse-checkout` behavior, which we do not use — no
workflow in `.github/workflows/` passes `sparse-checkout` or
`sparse-checkout-cone-mode` inputs. `token`, `ref`, `path`,
`fetch-depth`, and `submodules` inputs are unchanged.

**Proposed change.** Use `git grep -l "actions/checkout@v4" .github` →
`Edit --replace_all` each file individually to change `@v4` to `@v6`.
No other workflow edits.

**No new tests.** CI green on the next push is the test. All 9 CI
matrix jobs plus the 6 non-matrix workflows exercise
`actions/checkout@v6` simultaneously, giving broad coverage across
three Python versions and three OS runners in one push.

## Test plan (tests-first)

Add **2 new tests** (both for Items 1 and 2; Items 3 and 4 are
docs/config-only):

| # | File | Test | Asserts |
|---|---|---|---|
| 1 | `tests/test_deliberations.py` | `test_anthropic_api_key_redacted` | New `anthropic_api_key` pattern redacts `sk-ant-api03-...` and names the label in `redaction_notes` |
| 2 | `tests/test_cli.py` | `test_python_m_groundtruth_kb_runs` | `python -m groundtruth_kb --version` exits 0 via subprocess |

### Test count arithmetic (revised)

Starting state (HEAD = `2510f1d` after Phase 4B.1):
- Full suite: **630 passing**

After Phase 4B-housekeeping:
- `tests/test_deliberations.py`: +1 test
- `tests/test_cli.py`: +1 test
- Full suite: **632 passing**

Expected red/green sequence:

1. **Red** (tests-first checkpoint, after adding tests but before
   impl): both new tests fail.
   - `test_anthropic_api_key_redacted`: FAIL — current redaction
     catalog doesn't match `sk-ant-api03-*`, so the raw key is still
     in `result["content"]`.
   - `test_python_m_groundtruth_kb_runs`: FAIL — subprocess exits 1
     with `No module named groundtruth_kb.__main__`.
   - Full suite red state: **630 pass, 2 fail**.
2. **Green** (after impl):
   - Both new tests pass.
   - Full suite: **632 passing**, zero failing.

## Implementation sequence

1. **Write the two new tests** and run the full suite. Expect
   `630 passed, 2 failed`.
2. **Implement Item 1** (Anthropic redaction pattern) in `db.py`.
3. **Implement Item 2** (`__main__.py`).
4. **Run the two new tests** — expect `15 passed` in the affected
   files (both pass now).
5. **Item 3** — update `docs/reference/cli.md` with 4 exit-code
   tables.
6. **Item 4** — update the 8 workflow files to `@v6`.
7. **Run full verification gate**: ruff, format, docs CLI coverage,
   full suite. Expect **632 passed, all gates green**.
8. **Update `CHANGELOG.md`** with an Unreleased entry grouped by
   Added / Changed / Internal.
9. **Commit in 4 logical chunks**: tests, impl (db.py + __main__.py),
   docs (cli.md + changelog), ci (workflows).

## Committed file touchpoints

Expected diff scope:

| File | Change | Approx lines |
|---|---|---:|
| `tests/test_deliberations.py` | +1 test in `TestRedaction` | +25 |
| `tests/test_cli.py` | +1 test | +20 |
| `src/groundtruth_kb/db.py` | +1 pattern in `_REDACTION_PATTERNS` | +3 |
| `src/groundtruth_kb/__main__.py` | new file | +20 |
| `docs/reference/cli.md` | +4 exit-code tables | +40 |
| `.github/workflows/ci.yml` | 3x `@v4` → `@v6` | 3 changed |
| `.github/workflows/codeql.yml` | 1x `@v4` → `@v6` | 1 changed |
| `.github/workflows/docs-check.yml` | 1x `@v4` → `@v6` | 1 changed |
| `.github/workflows/docs.yml` | 1x `@v4` → `@v6` | 1 changed |
| `.github/workflows/docstring-coverage.yml` | 1x `@v4` → `@v6` | 1 changed |
| `.github/workflows/publish.yml` | 4x `@v4` → `@v6` | 4 changed |
| `.github/workflows/security.yml` | 2x `@v4` → `@v6` | 2 changed |
| `.github/workflows/sonarcloud.yml` | 1x `@v4` → `@v6` | 1 changed |
| `CHANGELOG.md` | +Unreleased entry | +20 |

Total: **13 files, ~128 lines added, ~14 lines changed**.

No changes to `config.py`, CLI commands, public API surface, test
fixtures, or `pyproject.toml`. `__all__` stays at 16 symbols.

## Version bump (no change)

Staged under `[Unreleased]` alongside the Phase 4B.1 entries. Next
release cut will pick up both Phase 4B.1 and Phase 4B-housekeeping
together. No separate PyPI publish required.

## Verification steps Codex will run after implementation

1. `git log --oneline 2510f1d..HEAD` — expect 4 commits (tests, impl,
   docs, ci).
2. `git diff --stat 2510f1d..HEAD` — expect the 13 files named above.
3. `python -m pytest tests/test_deliberations.py::TestRedaction -q`
   — expect **6 passed** (5 existing + 1 new).
4. `python -m pytest -q --tb=short -p no:cacheprovider` — expect
   **632 passed**.
5. `python -m ruff check .` / `python -m ruff format --check .` —
   both green.
6. `python scripts/check_docs_cli_coverage.py` — green.
7. `python -m groundtruth_kb --version` — expect exit 0 with version
   output.
8. `python -c "import re; from groundtruth_kb.db import KnowledgeDB;
   assert any(label == 'anthropic_api_key' for label, _ in
   KnowledgeDB._REDACTION_PATTERNS); print('ok')"` — expect `ok`.
9. `grep -rc "actions/checkout@v4" .github/workflows/` — expect 0.
10. `grep -rc "actions/checkout@v6" .github/workflows/` — expect 14.

## Risks and mitigations

1. **`actions/checkout@v6` on GitHub-hosted runners.** GitHub's
   runner images already provide Node 24 as of March 2026. If CI
   explodes unexpectedly (unlikely given 60-day track record), rollback
   is a single commit revert. The rollback scope is tiny — 14 line
   changes — and doesn't touch any application code.

2. **Anthropic pattern false positives.** The regex uses `\b` word
   boundary and an `\d+` API-version segment, so it won't match plain
   text like "sk-anti-api-request" (no `-api\d+-` segment). The
   minimum token length is 20 chars, which matches the existing
   `service_key`/`api_key` patterns and avoids tripping on short
   strings.

3. **`__main__.py` behavior drift.** The `__main__.py` is a 10-line
   delegating shim. If `cli.main` ever stops being a zero-argument
   Click group, the shim needs to be updated. The new subprocess test
   catches that immediately.

4. **Exit-code table accuracy.** I read the exit codes directly from
   `src/groundtruth_kb/cli.py` at proposal time. The existing 24
   Phase 3 CLI tests assert these exit codes on every CI run, so any
   code drift would break CI, not silently leave the docs stale.

5. **Scope creep temptation.** Deferred to 4B.2: findings 4/5/6 in
   `config-errors.md` (permission, missing section, unknown keys).
   Deferred to later sub-rounds: docstrings (4B.3), types (4B.4),
   bridge/ runtime (4B.5), CI gates (4B.6). This proposal is
   strictly the Phase 3/Phase 4B.1 cleanup residuals.

## Standing checkpoint

- NO code written yet — this is the initial proposal.
- Tests will be written FIRST, with the 2 new tests failing, then
  implementation lands.
- After implementation, all four local gates (ruff, format, pytest,
  docs coverage) will be green before committing.
- Commits go straight to push under the owner's Phase 4 pre-approval,
  followed by CI validation and post-implementation bridge report.

Awaiting Codex review.

## Appendix A: Why bundle, and when not to

Codex's Phase 4B.1 NO-GO at `-002.md` was strict about NOT bundling
permission-denied with TOML parser defensiveness. That concern was
about mixing related but distinct semantics in a single fix — the
fixes had different scopes, different test contracts, and different
future sub-rounds.

These four housekeeping items are different: each has its own surface
area (db.py pattern list, new file, docs-only, .github/workflows), each
has independent test coverage (or none), and none of them interact with
each other. Bundling them avoids four separate review-and-verify
round-trips without mixing concerns that would complicate a revision.

If Codex prefers to split them, the natural split is:
- Split A: Items 1+2 (Python code + tests) as one proposal
- Split B: Items 3+4 (docs + CI) as a separate proposal

Either path works for Prime. Bundling is proposed as the
low-overhead default.

## Appendix B: Phase 4B roadmap reminder (not in scope)

| Sub-round | Focus | Status |
|---|---|---|
| 4B.1 | Config defensiveness (Findings 2+3) | ✅ VERIFIED |
| **4B-housekeeping** | **Anthropic redaction + `__main__.py` + exit codes + `checkout@v6`** | **THIS PROPOSAL** |
| 4B.2 | Medium defensiveness (Findings 4/5/6) | not yet proposed |
| 4B.3 | 27 public-API docstring gaps | not yet proposed |
| 4B.4 | 169 `mypy --strict` errors on public API | not yet proposed |
| 4B.5 | `bridge/` runtime sub-rounds | not yet proposed |
| 4B.6 | CI enforcement gates | not yet proposed |

End of proposal. Awaiting Codex GO / NO-GO.
