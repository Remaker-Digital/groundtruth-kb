# NO-GO: WI-3142 Credential Scan Narrowing Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-003.md`
**Prior review:** `bridge/credential-scan-narrowing-002.md`
**Verdict:** NO-GO

## Claim

The revised proposal fixes the main design errors from v1 on paper:
path-scoped suppression, broader project key coverage, `TEST_USER_KEY`, and
both former blanket-exclusion files are now in scope.

It is still not ready for GO because the approved fixture inventory is
incomplete and the expanded regex set has a wider repo impact that is not yet
accounted for.

## Evidence

- `bridge/credential-scan-narrowing-003.md` proposes `_FIXTURE_FILES` for both
  `tests/conftest.py` and
  `tests/multi_tenant/test_middleware_pipeline.py`.
- `bridge/credential-scan-narrowing-003.md` proposes `_FIXTURE_VALUES` with
  only the six `tests/conftest.py` values.
- The same proposal states that inline keys in
  `tests/multi_tenant/test_middleware_pipeline.py` still "need to be
  inventoried and added."
- Running the proposal's regex shapes over the two approved fixture files found:
  - `tests/conftest.py:169-180`: six matches, all in the proposed
    `_FIXTURE_VALUES`.
  - `tests/multi_tenant/test_middleware_pipeline.py:193`:
    `arsk_completely_invalid_key`.
  - `tests/multi_tenant/test_middleware_pipeline.py:582`,
    `:602`, `:666`, and `:687`: `ar_spa_plat_INVALID_STALE_TOKEN`.
- Running the same proposed regex family over `src`, `tests`, `scripts`, and
  `evaluation`, excluding only the two proposed fixture files, found 94 matching
  lines in 36 files. Examples include:
  - `evaluation/run_quality_live.py:20`:
    `PREVIEW_WIDGET_KEY` fallback `pk_live_c79a2bd0_960a9c23`.
  - `evaluation/seed_quality_kb.py:51`:
    raw `ar_user_rema_...` fallback.
  - `tests/contract/test_chat_provider.py:95-214`:
    repeated `pk_live_test_placeholder`.
  - `tests/widget/test_transcript_persistence.py:22` and `:142-146`:
    deterministic `pk_live_*` values.
  - `tests/multi_tenant/test_apikey_reset.py:405-505`:
    deterministic `ar_live_test_*` values.
- Current hook evidence from prior review still applies:
  `.claude/hooks/credential-scan.py:105-106` currently excludes both files
  entirely, and `.claude/hooks/credential-scan.py:48-50` currently misses
  several real key families.

## Findings

### P1 - `test_middleware_pipeline.py` is still not fully scoped

The revised design adds `tests/multi_tenant/test_middleware_pipeline.py` to
the approved fixture files, but does not add its inline deterministic values
to `_FIXTURE_VALUES`. Under the proposed regexes, edits containing
`ar_spa_plat_INVALID_STALE_TOKEN` or `arsk_completely_invalid_key` in that file
would be blocked even though the proposal explicitly treats the file as an
approved fixture/negative-path test surface.

**Risk/impact:** Prime can remove the blanket exclusion and immediately make
routine edits to the same approved test file fail. That is a false-positive
regression inside the exact file the proposal claims to handle.

**Required action:** Inventory the inline values in
`tests/multi_tenant/test_middleware_pipeline.py` before GO. Either add exact
path-scoped values for `arsk_completely_invalid_key` and
`ar_spa_plat_INVALID_STALE_TOKEN`, or refactor the test file to import/use
central fixture constants that are already in `_FIXTURE_VALUES`. Add tests that
prove those exact values are allowed only in that approved file.

### P2 - Expanded detection blast radius is not assessed

The revised proposal expands key detection well beyond the two excluded files.
That is probably necessary for real security coverage, but it is not a narrow
`conftest.py` change anymore. The proposed regex family already matches 94
lines in 36 files outside the two approved fixtures.

Some of those matches look like existing violations that should be fixed
(`evaluation/run_quality_live.py` and `evaluation/seed_quality_kb.py` have
live-looking fallback keys). Others are deterministic test values that may need
a deliberate fixture/migration policy.

**Risk/impact:** Without an explicit repo audit and disposition, the hook can
either become noisy and block normal test maintenance, or it can expose real
hardcoded values without a plan to remediate them.

**Required action:** Add a pre-implementation audit section listing matches
from the proposed regexes outside the two fixture files and classifying each
group as:

1. fix now because it is a real hardcoded credential/default;
2. migrate to shared test fixtures;
3. allow with path-and-value scoped fixture suppression; or
4. intentionally block going forward.

At minimum, address the `evaluation/*` live-looking fallbacks in the same work
item or split them into an explicit follow-up risk item.

### P3 - Make match-value extraction explicit

The proposed regexes include surrounding quotes, while `_FIXTURE_VALUES`
contains unquoted raw values. The proposal says to "extract the matched value,"
which is the right intent, but the implementation must explicitly strip quotes
or use a named capture group for the raw value.

**Required action:** Specify `pattern.finditer()` with a named `(?P<value>...)`
capture or a small helper that normalizes matched quoted strings before
checking `_FIXTURE_VALUES`. Add a regression test for this exact path so a
quoted fixture literal does not fail to suppress.

## Required Conditions For GO

1. Complete the `tests/multi_tenant/test_middleware_pipeline.py` inline value
   inventory and include exact path-scoped handling for those values.
2. Add a repo-wide proposed-regex audit and disposition for the 36 files / 94
   matching lines outside the two approved fixtures, with immediate handling or
   explicit follow-up for live-looking defaults.
3. Specify quoted-match normalization or named capture groups for fixture
   value comparison.
4. Keep the prior required tests: approved fixture values allowed only in
   approved files, real-looking project keys blocked in approved files, no
   global suppression, and FQDN/connection-string detection still working.

## Answer To Prime Question

Inventory `test_middleware_pipeline.py` inline values in this proposal. It is
not sufficient to note that imported `conftest.py` constants are covered,
because the file also contains inline literals that the revised regexes match.

## Decision Needed From Owner

No owner decision is needed unless Prime wants the expanded scanner to block
all existing deterministic test keys outside the two approved fixture files.
That may be a valid security posture, but it should be explicit because it is
a broader operational change than narrowing `conftest.py`.
