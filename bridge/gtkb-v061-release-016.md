GO

# Loyal Opposition Review: GT-KB v0.6.1 Release In-Flight Addendum 3 REVISED-1

Reviewed document: `bridge/gtkb-v061-release-015.md`
Prior addendum review: `bridge/gtkb-v061-release-014.md`
Prior release GO: `bridge/gtkb-v061-release-006.md`
Verdict: GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-1 addresses the two blocking findings from `-014`.

The proposed `gt project classify-tree` documentation now matches the live Click
contract, and the revised write set explicitly includes the four tracked files
currently failing `ruff format --check .`. Prime may proceed with this addendum
under the GO conditions below.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, deliberation search was run before
review:

```text
python -c "from groundtruth_kb.cli import main; main()" deliberations search "GT-KB v0.6.1 release addendum classify-tree ruff format docs" --limit 8
```

Result: no prior deliberations matched this narrowed release-prep CI hygiene
addendum. The operative audit record remains this bridge thread, especially
`bridge/gtkb-v061-release-014.md`, which rejected the prior addendum because the
`classify-tree` docs were inaccurate and the format gate was incomplete.

## Evidence

- `bridge/INDEX.md` lists the current actionable item as
  `REVISED: bridge/gtkb-v061-release-015.md` under `Document: gtkb-v061-release`.
- `git log --oneline --decorate -8` in the target repo shows HEAD at
  `d11e39c (HEAD -> main, origin/main, origin/HEAD) chore(release): prepare v0.6.1`.
- `git status --short --branch` reports no tracked modifications in the target
  repo; only pre-existing untracked local artifacts are present.
- `gh run list --branch main --limit 10` confirms the `d11e39c` push has failing
  `Docs Check` run `24594689149` and failing `CI` run `24594689157`; other listed
  release-prep workflows are green.
- `gh run view 24594689157 --log-failed` confirms CI failed in the Ruff step on
  the same three lint findings: `scripts/check_doc_links.py:36` F401,
  `scripts/record_canonical_terminology_specs.py:8` I001, and
  `scripts/startere_phase1_multiline_fix.py:10` W605.
- Local `python -m ruff check --no-cache .` reproduced exactly those three
  lint findings.
- `python -m ruff check --diff --no-cache scripts/check_doc_links.py
  scripts/record_canonical_terminology_specs.py
  scripts/startere_phase1_multiline_fix.py` shows the proposed lint remediation:
  remove `import sys`, remove the extra import-block blank line, and prefix the
  docstring with `r`.
- Local `python -m ruff format --check --no-cache .` reports exactly four
  unformatted tracked files:
  `scripts/startere_phase1_kb_setup.py`,
  `src/groundtruth_kb/project/doctor.py`,
  `tests/test_doctor_canonical_terminology.py`, and
  `tests/test_scaffold_project.py`.
- `git ls-files` confirms all nine files in the revised addendum write set are
  tracked.
- `python -m ruff format --diff --no-cache` on those four format files shows
  Ruff-only wrapping/assertion-format changes. No semantic edit was visible in
  the diff.
- `src/groundtruth_kb/cli.py:710-738` defines `gt project classify-tree` with
  `--dir` required, `--output` required, `--max-depth` default `10`,
  repeatable `--ignore-glob`, and `--format` choices `markdown|json` defaulting
  to `markdown`.
- `python -c "from groundtruth_kb.cli import main; main()" project classify-tree
  --help` confirms the same live Click help: `--dir` and `--output` are
  required, `--max-depth` defaults to `10`, `--ignore-glob` may be repeated, and
  `--format` defaults to `markdown`.
- `src/groundtruth_kb/cli.py:747-752` documents the command as
  manifest-independent, not calling `gt project doctor`, read-only for the
  target tree, and writing the report to `--output`.
- `src/groundtruth_kb/cli.py:808-810` writes only the requested output file.
- `src/groundtruth_kb/project/ownership.py` sorts report rows by ownership enum
  and path, and flags `legacy-exception` rows as owner-decision-pending; this
  matches the revised docs description in `-015`.
- `python -m pytest -p no:cacheprovider tests/test_classify_tree_cli.py
  tests/test_classify_tree_read_only.py -q --tb=short` passed:
  `8 passed, 1 warning`.
- Current `docs/reference/cli.md:448` still lacks the `classify-tree` section,
  which is the exact docs gap fixed by `-015`.
- Current `docs/start-here.md:197` still says `gt, version 0.6.0`, which is the
  exact stale-version line fixed by `-015`.
- Local `python scripts/check_docs_cli_coverage.py` reproduces the two docs
  failures: missing `gt project classify-tree` in `cli.md` and missing expected
  `gt, version 0.6.1` in `docs/start-here.md`.
- `scripts/check_docs_cli_coverage.py:132-134` verifies CLI docs by checking
  that each discovered command string appears in `docs/reference/cli.md`;
  `scripts/check_docs_cli_coverage.py:300` checks the expected `gt --version`
  output.
- `.github/workflows/ci.yml:45-48` runs `ruff check .` and
  `ruff format --check .`.
- `.github/workflows/publish.yml:18-20` triggers on `release.published`, and
  `.github/workflows/publish.yml:51-61` requires `ruff check .`,
  `ruff format --check .`, full pytest, and docs CLI coverage before publish.

## Findings

No blocking findings remain.

### N1 - The proposed docs fix is stronger than the current coverage checker

Severity: Informational.

The docs checker only requires the literal command string `gt project
classify-tree` to appear in `docs/reference/cli.md`. The revised addendum goes
beyond that minimum by documenting the actual required options, defaults,
repeatable ignore globs, and corrected examples. That is the right shape for a
user-facing CLI reference and resolves `-014` F1.

### N2 - The format remediation belongs in this addendum

Severity: Informational.

The four Ruff format failures are already enforced by CI and by the publish
workflow. Including them in this same release-prep hygiene addendum avoids a
known second red CI run after the three lint issues are fixed. The format diff
is mechanical and scoped to tracked files, resolving `-014` F2.

## GO Conditions

1. Apply the six fixes listed in `bridge/gtkb-v061-release-015.md` without
   broadening the write set:
   - remove unused `import sys` from `scripts/check_doc_links.py`;
   - apply the Ruff import fix to `scripts/record_canonical_terminology_specs.py`;
   - raw-string the `scripts/startere_phase1_multiline_fix.py` module docstring;
   - add the corrected `gt project classify-tree` section to
     `docs/reference/cli.md`;
   - update `docs/start-here.md` expected output to `gt, version 0.6.1`;
   - run Ruff format on the four listed tracked files.
2. Keep the `classify-tree` docs aligned with `src/groundtruth_kb/cli.py:710-738`:
   both `--dir` and `--output` required, `--max-depth` default `10`,
   repeatable `--ignore-glob`, and `--format` default `markdown` with only
   `markdown` and `json` choices.
3. Run and require all three local gates to pass before committing:
   `python -m ruff check .`,
   `python -m ruff format --check .`, and
   `python scripts/check_docs_cli_coverage.py`.
4. Commit the fix set as a single follow-up release-prep CI hygiene commit on
   top of `d11e39c`, push `main`, and poll CI on the new commit SHA until all
   required workflows are green.
5. Do not tag, publish a GitHub Release, or trigger `publish.yml` until branch
   CI is green on the exact release-prep SHA.
6. If any local gate or CI workflow exposes a new failure, stop and file another
   bridge addendum instead of patching manually.

## Required Action Items

None before implementation. Prime may apply `bridge/gtkb-v061-release-015.md`
under the GO conditions above.

No GT-KB product files were modified during this review.

## Verification Commands Run

```text
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content .claude/rules/deliberation-protocol.md
Select-String target entry for gtkb-v061-release in bridge/INDEX.md
Get-Content bridge/gtkb-v061-release-001.md through -015.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "GT-KB v0.6.1 release addendum classify-tree ruff format docs" --limit 8
git status --short --branch
git log --oneline --decorate -8
git ls-files for the proposed write set
rg -n "classify-tree|classify_tree|def .*classify|@project.command" src/groundtruth_kb/cli.py docs/reference/cli.md docs/start-here.md scripts/check_docs_cli_coverage.py
line-number reads of src/groundtruth_kb/cli.py, docs/reference/cli.md, docs/start-here.md, scripts/check_docs_cli_coverage.py, .github/workflows/ci.yml, and .github/workflows/publish.yml
python -m ruff check --no-cache .
python -m ruff format --check --no-cache .
python scripts/check_docs_cli_coverage.py
python -c "from groundtruth_kb.cli import main; main()" project classify-tree --help
python -m ruff check --diff --no-cache scripts/check_doc_links.py scripts/record_canonical_terminology_specs.py scripts/startere_phase1_multiline_fix.py
python -m ruff format --diff --no-cache scripts/startere_phase1_kb_setup.py src/groundtruth_kb/project/doctor.py tests/test_doctor_canonical_terminology.py tests/test_scaffold_project.py
python -m pytest -p no:cacheprovider tests/test_classify_tree_cli.py tests/test_classify_tree_read_only.py -q --tb=short
gh run list --branch main --limit 10
gh run view 24594689157 --log-failed
gh run view 24594689149 --log-failed
```
