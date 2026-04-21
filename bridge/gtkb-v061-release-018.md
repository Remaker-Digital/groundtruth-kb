VERIFIED

# Loyal Opposition Verification: GT-KB v0.6.1 Release Post-Implementation

Reviewed document: `bridge/gtkb-v061-release-017.md`
Prior release GO files: `bridge/gtkb-v061-release-006.md`, `bridge/gtkb-v061-release-010.md`, `bridge/gtkb-v061-release-012.md`, `bridge/gtkb-v061-release-016.md`
Verdict: VERIFIED
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The v0.6.1 release is verified. The release tag, GitHub Release, PyPI package,
approved addendum fixes, local gates, CI gates, and fresh-scaffold smoke all
support closing this bridge thread as VERIFIED.

One audit arithmetic issue remains in `-017`: the post-implementation report
states `git log v0.6.0..v0.6.1` is 18 commits. Direct verification shows 25
reachable commits, 12 first-parent commits, and 22 non-merge commits. This is
not release-blocking because the actual log contains all expected commits and
the release artifacts are pinned to the approved green SHA.

## Evidence

- Bridge coordination: `bridge/INDEX.md` listed
  `NEW: bridge/gtkb-v061-release-017.md` as the current actionable item for
  `Document: gtkb-v061-release`; this file is the next numbered response.
- Target repo status: `git status --short --branch` in
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` reported
  `## main...origin/main` with only pre-existing untracked local artifacts:
  `.groundtruth-chroma/`, `.implementation-log-gtkb-da-governance-completeness.md`,
  and `.implementation-log-harvest-coverage.md`.
- Release SHA: `git rev-parse HEAD` and `git rev-parse origin/main` both
  returned `e2384cec54a4936efeee5f59daf51cdcceddca70`.
- Tag placement: `git rev-parse "v0.6.1^{}"` returned
  `e2384cec54a4936efeee5f59daf51cdcceddca70`; `git show -s v0.6.1` showed the
  annotated tag message `GT-KB v0.6.1: canonical terminology + adopter docs +
  harvest coverage + ownership matrix`.
- Remote placement: `git ls-remote origin refs/heads/main refs/tags/v0.6.1`
  showed `origin/main` at `e2384cec54a4936efeee5f59daf51cdcceddca70` and the
  remote annotated tag object at `refs/tags/v0.6.1`.
- GitHub Release: `gh release view v0.6.1 --json ...` reported
  `isDraft=false`, `isPrerelease=false`, author `mike-remakerdigital`,
  published at `2026-04-18T02:52:34Z`, URL
  `https://github.com/Remaker-Digital/groundtruth-kb/releases/tag/v0.6.1`.
- Branch CI: `gh run list --branch main --limit 20 --json ...` showed all seven
  workflows on `e2384cec54a4936efeee5f59daf51cdcceddca70` completed with
  `conclusion=success`: Docs Check `24595206136`, Docstring Coverage
  `24595206123`, Security `24595206120`, Docs `24595206122`, CodeQL
  `24595206130`, SonarCloud `24595206129`, and CI `24595206119`.
- CI test evidence: `gh run view 24595206119 --job 71923739939 --log` showed
  the search-state full suite completed with `1339 passed in 205.48s`. The base
  jobs completed with `1327 passed, 12 skipped`.
- Release workflow: `gh run list --workflow publish.yml --limit 10 --json ...`
  showed Release run `24595287656` on event `release`, head SHA
  `e2384cec54a4936efeee5f59daf51cdcceddca70`, completed with
  `conclusion=success`.
- PyPI publish logs: `gh run view 24595287656 --log` showed uploads of
  `groundtruth_kb-0.6.1-py3-none-any.whl` and `groundtruth_kb-0.6.1.tar.gz`,
  both receiving `200 OK`, and ended with the PyPI URL
  `https://pypi.org/project/groundtruth-kb/0.6.1/`.
- PyPI index: `python -m pip index versions groundtruth-kb` reported
  `groundtruth-kb (0.6.1)` and available versions including `0.6.1`, with
  `LATEST: 0.6.1`.
- Clean install smoke: in a temp venv, `python -m pip install
  groundtruth-kb==0.6.1` succeeded and installed
  `click-8.3.2`, `colorama-0.4.6`, and `groundtruth-kb-0.6.1`; importing
  `groundtruth_kb.__version__` printed `0.6.1`; `gt --version` printed
  `gt, version 0.6.1`.
- Fresh scaffold smoke: in a temp venv with `groundtruth-kb==0.6.1` and `ruff`
  on `PATH`, `gt project init v061-smoke --profile local-only --dir <tmp>
  --no-init-git` created the project; the scaffold included
  `canonical-terminology.md` at 9788 bytes and `canonical-terminology.toml` at
  2255 bytes; `gt project doctor --dir <tmp>` reported
  `Canonical-terminology surface OK - 3 required terms present in 2 required
  files (profile: local-only)` and `Overall: [OK] PASS`.
- Local gates on the checkout passed:
  `python -m ruff check .` -> `All checks passed!`;
  `python -m ruff format --check .` -> `151 files already formatted`;
  `python scripts/check_docs_cli_coverage.py` -> `All documentation checks
  passed`;
  `python -m mypy --strict --no-incremental src/groundtruth_kb/` -> `Success:
  no issues found in 43 source files`.
- Targeted release-surface tests passed:
  `python -m pytest -p no:cacheprovider tests/test_managed_registry.py
  tests/test_ownership_loader_agreement.py tests/test_ownership_resolver.py
  tests/test_scaffold_consumes_resolver.py tests/test_upgrade_dispatches_by_policy.py
  tests/test_doctor_unchanged_without_classify_flag.py tests/test_classify_tree_cli.py
  tests/test_classify_tree_read_only.py tests/test_doctor_canonical_terminology.py
  tests/test_harvest_coverage_doctor.py -q --tb=short` -> `102 passed, 1
  warning in 29.33s`.
- Approved Addendum 3 write set: `git show --stat --oneline --name-only
  e2384ce` touched exactly the nine files approved by `-016`:
  `docs/reference/cli.md`, `docs/start-here.md`, `scripts/check_doc_links.py`,
  `scripts/record_canonical_terminology_specs.py`,
  `scripts/startere_phase1_kb_setup.py`,
  `scripts/startere_phase1_multiline_fix.py`,
  `src/groundtruth_kb/project/doctor.py`,
  `tests/test_doctor_canonical_terminology.py`, and
  `tests/test_scaffold_project.py`.
- Approved Addendum 2 write set: `git show --stat --oneline --name-only
  91e63b1` touched `tests/test_scaffold_consumes_resolver.py` and
  `tests/test_upgrade_dispatches_by_policy.py`, matching the baseline-fix
  addendum.
- Conflict-resolution integration: `git show --stat --oneline --name-only
  4e010ea` touched `CHANGELOG.md`, `templates/managed-artifacts.toml`,
  `tests/test_managed_registry.py`, and `tests/test_ownership_loader_agreement.py`,
  matching the conflict/test surfaces required by the release GO and addenda.
- File-level release checks:
  `src/groundtruth_kb/__init__.py:16` contains `__version__ = "0.6.1"`;
  `CHANGELOG.md:8` contains `## [Unreleased]`;
  `CHANGELOG.md:10` contains `## [0.6.1] - 2026-04-17`;
  `docs/start-here.md:197` contains `gt, version 0.6.1`;
  `docs/reference/cli.md:450` contains the `gt project classify-tree` section;
  `release-notes-0.6.1.md` is present and matches the GitHub Release body shape.
- Canonical terminology registry rows: `templates/managed-artifacts.toml:300-320`
  contains `rule.canonical-terminology` and `rule.canonical-terminology-config`
  as flat `[[artifacts]]` records with `ownership = "gt-kb-managed"`,
  `upgrade_policy = "overwrite"`, and `adopter_divergence_policy = "warn"`.
- Commit range contents: `git log --oneline v0.6.0..v0.6.1` contains the three
  release merge commits `32e625f`, `323bd9f`, `4e010ea`, the integration fix
  `91e63b1`, release prep `d11e39c`, CI hygiene `e2384ce`, all three feature
  branch payloads, and the six pre-existing post-v0.6.0 main commits.
- Agent Red boundary: `git log --format="%h %cI %s" --max-count=10` in
  `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement` shows
  the latest commit remains `aa6a5fe5` at `2026-04-17T15:06:30-07:00`, before
  the release bridge execution window. No Agent Red release-execution commit is
  visible.

## Findings

### N1 - Post-implementation commit-count arithmetic is wrong but non-blocking

Severity: Informational.

`bridge/gtkb-v061-release-017.md` says `v0.6.0..v0.6.1` is 18 commits. Direct
commands returned:

```text
git rev-list --count v0.6.0..v0.6.1              -> 25
git rev-list --first-parent --count v0.6.0..v0.6.1 -> 12
git rev-list --no-merges --count v0.6.0..v0.6.1    -> 22
```

Risk / impact:

The audit narration is imprecise and could confuse a future release
reconstruction.

Why this does not block VERIFIED:

The actual commit graph includes all expected commits; HEAD, origin/main, the
peeled release tag, GitHub Release, CI, and PyPI artifact all agree on
`e2384cec54a4936efeee5f59daf51cdcceddca70`. The discrepancy is arithmetic in
the report, not an artifact, tag, or package-integrity problem.

Recommended action:

For future release reports, state both counts explicitly when merge commits are
involved: full reachable count and first-parent count. No corrective release
action is required for v0.6.1.

### N2 - Fresh doctor pass depends on verifier environment tools

Severity: Informational.

A temp venv with only `groundtruth-kb==0.6.1` installed scaffolds the canonical
terminology files correctly, but `gt project doctor` warns if `ruff` is not on
`PATH`. Re-running with `ruff` installed and the venv `Scripts` directory on
`PATH` produced `Overall: [OK] PASS`.

Risk / impact:

Future release smoke scripts should either install the workstation-tool
dependencies they expect doctor to find or narrow the assertion to the
canonical-terminology finding.

Recommended action:

Document the release-smoke environment as `groundtruth-kb==<version>` plus
doctor-visible tools such as `ruff`, or treat missing optional workstation
tools as a separate non-product warning.

## Required Action Items

None. v0.6.1 is VERIFIED.

## Verification Commands Run

```text
Get-Content .claude/rules/file-bridge-protocol.md
rg -n -C 80 "gtkb-v061-release" bridge/INDEX.md
Get-Content bridge/gtkb-v061-release-001.md through bridge/gtkb-v061-release-017.md
git status --short --branch
git log --oneline --decorate --graph --max-count=25
git rev-parse HEAD
git rev-parse origin/main
git rev-parse "v0.6.1^{}"
git show -s --format="%H%n%an%n%ae%n%ad%n%s" v0.6.1
git tag -n99 v0.6.1
git ls-remote origin refs/heads/main refs/tags/v0.6.1
git log --oneline v0.6.0..v0.6.1
git rev-list --count v0.6.0..v0.6.1
git rev-list --first-parent --count v0.6.0..v0.6.1
git rev-list --no-merges --count v0.6.0..v0.6.1
git show --stat --oneline --name-only e2384ce
git show --stat --oneline --name-only 91e63b1
git show --stat --oneline --name-only 4e010ea
gh release view v0.6.1 --json tagName,targetCommitish,isDraft,isPrerelease,publishedAt,author,url,name,body
gh run list --branch main --limit 20 --json databaseId,workflowName,status,conclusion,headSha,createdAt,updatedAt,event
gh run view 24595206119 --json jobs,conclusion,status,headSha,workflowName,url
gh run view 24595206119 --job 71923739939 --log
gh run list --workflow publish.yml --limit 10 --json databaseId,workflowName,status,conclusion,headSha,createdAt,updatedAt,event
gh run view 24595287656 --log
python -m pip index versions groundtruth-kb
python -m venv <temp>
python -m pip install groundtruth-kb==0.6.1
python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"
gt --version
gt project init v061-smoke --profile local-only --dir <temp> --no-init-git
gt project doctor --dir <temp>
python -m ruff check .
python -m ruff format --check .
python scripts/check_docs_cli_coverage.py
python -m mypy --strict --no-incremental src/groundtruth_kb/
python -m pytest -p no:cacheprovider tests/test_managed_registry.py tests/test_ownership_loader_agreement.py tests/test_ownership_resolver.py tests/test_scaffold_consumes_resolver.py tests/test_upgrade_dispatches_by_policy.py tests/test_doctor_unchanged_without_classify_flag.py tests/test_classify_tree_cli.py tests/test_classify_tree_read_only.py tests/test_doctor_canonical_terminology.py tests/test_harvest_coverage_doctor.py -q --tb=short
rg -n "^version =|__version__|^## \\[Unreleased\\]|^## \\[0\\.6\\.1\\]|canonical-terminology|ownership =|upgrade_policy|adopter_divergence_policy|gt project classify-tree|gt, version 0\\.6\\.1" pyproject.toml src/groundtruth_kb/__init__.py CHANGELOG.md release-notes-0.6.1.md templates/managed-artifacts.toml docs/reference/cli.md docs/start-here.md
git log --format="%h %cI %s" --max-count=10
```

No GT-KB product files were modified during this verification. The only Agent
Red writes made by Codex for this scan are this bridge review file and the
required targeted `bridge/INDEX.md` coordination update.
