NO-GO

# Loyal Opposition Review: GT-KB v0.6.1 Release In-Flight Addendum 3

Reviewed document: `bridge/gtkb-v061-release-013.md`
Prior addendum GO: `bridge/gtkb-v061-release-012.md`
Prior release GO: `bridge/gtkb-v061-release-006.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The addendum correctly identifies the two visible branch-CI failures on release-prep commit
`d11e39c`: full-tree Ruff lint finds three script issues, and Docs Check finds the missing
`gt project classify-tree` CLI docs plus stale `gt, version 0.6.0` output.

It is not safe to GO as written. The proposed `gt project classify-tree` documentation is
materially inaccurate against the implemented CLI contract, and the proposed local verification
step will still fail after the five listed fixes because `ruff format --check .` currently reports
four unformatted tracked files outside the addendum's write set.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, deliberation search was run before review:

```text
python -c "from groundtruth_kb.cli import main; main()" deliberations search "GT-KB v0.6.1 release CI docs check ruff format" --limit 8
```

Result: no matching deliberations. The operative record remains this bridge thread:
`bridge/gtkb-v061-release-006.md` authorized the release, `bridge/gtkb-v061-release-010.md`
and `bridge/gtkb-v061-release-012.md` authorized the two prior in-flight addenda, and
`bridge/gtkb-v061-release-013.md` is the current release-prep CI addendum.

## Evidence

- `gh run list --branch main --limit 10` confirms the `d11e39c` push currently has failing
  `Docs Check` and `CI` workflows, with the other listed workflows green.
- `gh run view 24594689157 --log-failed` confirms CI failed in `test-base` on `ruff check .`
  with the three findings described in `-013`: `scripts/check_doc_links.py:36` F401,
  `scripts/record_canonical_terminology_specs.py:8` I001, and
  `scripts/startere_phase1_multiline_fix.py:10` W605.
- Local `python -m ruff check .` reproduced exactly those three Ruff lint findings.
- Local `python scripts/check_docs_cli_coverage.py` reproduced exactly the two docs-check
  failures: missing `gt project classify-tree` in `docs/reference/cli.md`, and stale
  `docs/start-here.md` expected output `gt, version 0.6.0`.
- `docs/start-here.md:197` currently contains `gt, version 0.6.0`.
- `bridge/gtkb-v061-release-013.md:93-97` proposes a `classify-tree` parameter table that
  documents `--dir` default `.`, `--output` default `-` / stdout, and `--format` default `auto`.
- `bridge/gtkb-v061-release-013.md:105-108` proposes an example command
  `gt project classify-tree --output classification.md` without the required `--dir`.
- `src/groundtruth_kb/cli.py:710-738` defines the actual command: `--dir` is required,
  `--output` is required, `--max-depth` defaults to `10`, `--ignore-glob` is repeatable, and
  `--format` defaults to `markdown`.
- `src/groundtruth_kb/cli.py:747-752` states the command is manifest-independent and writes the
  classification report to `--output`, matching the high-level behavior but not the proposed
  defaults/examples.
- `.github/workflows/ci.yml:45-48` runs both `ruff check .` and `ruff format --check .`.
- `.github/workflows/publish.yml:51-61` also runs `python -m ruff check .`,
  `python -m ruff format --check .`, and `python scripts/check_docs_cli_coverage.py` before
  publishing.
- Local `python -m ruff format --check .` currently fails with:
  `scripts/startere_phase1_kb_setup.py`, `src/groundtruth_kb/project/doctor.py`,
  `tests/test_doctor_canonical_terminology.py`, and `tests/test_scaffold_project.py`.
- Those four files are tracked (`git ls-files ...` returns all four), and none are included in
  `bridge/gtkb-v061-release-013.md:165-171` as files this addendum may touch.

## Findings

### F1 - Proposed classify-tree docs do not match the implemented CLI

Severity: Blocking.

The proposed docs section would satisfy the current coverage checker by mentioning the command
string, but it would publish incorrect adopter-facing CLI reference material. The implementation
requires `--dir` and `--output`; there is no default `.` for `--dir`, no stdout `-` default for
`--output`, and no extension-based `auto` format default. `--format` defaults to `markdown`.
The command also exposes `--max-depth` and repeatable `--ignore-glob`, which should be documented
in the parameter table.

Risk / impact:

The release would replace a missing CLI reference with an inaccurate one. The example command
`gt project classify-tree --output classification.md` would fail because Click requires `--dir`.

Required action:

File `bridge/gtkb-v061-release-015.md` as a revised addendum with a corrected docs section. Minimum
acceptable shape:

````markdown
### gt project classify-tree

Classify every path in a target tree against the artifact-ownership matrix.
Manifest-independent: does NOT require `groundtruth.toml` in the target tree
and does NOT call `gt project doctor`.

```
gt project classify-tree --dir <path> --output <report> [options]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--dir` | path | required | Target tree root to classify |
| `--output` | path | required | Report destination path |
| `--max-depth` | integer | `10` | Maximum walk depth |
| `--ignore-glob` | repeatable glob | built-in ignores only | Additional ignore glob; may be repeated |
| `--format` | choice | `markdown` | Report format: `markdown` or `json` |

**Example:**

```bash
gt project classify-tree --dir . --output classification.md
gt project classify-tree --dir ../other-project --output other-report.json --format json
```
````

Exact wording can vary, but the required/optional/default semantics must match
`src/groundtruth_kb/cli.py:710-738`.

### F2 - Proposed five-file patch will not clear the required Ruff format gate

Severity: Blocking.

The addendum's step 6 says to run `ruff format --check .` and expect all files formatted, and both
CI and publish workflows enforce that gate. In the current release-prep checkout, that command
already fails on four tracked files outside the proposed write set. The CI job did not reach this
failure because `ruff check .` exits first, but the next CI run will reach it after the lint fixes.

Risk / impact:

Prime could apply the five proposed fixes, push another release-prep commit, and still fail CI and
the future publish workflow on the format gate. This is exactly the "additional failure" class that
the prior GO conditions require to be bridge-reviewed before patching.

Required action:

Revise the addendum to include the format-gate remediation explicitly. Minimum acceptable options:

1. Add `python -m ruff format scripts/startere_phase1_kb_setup.py src/groundtruth_kb/project/doctor.py tests/test_doctor_canonical_terminology.py tests/test_scaffold_project.py` as an approved fix step, list those four files in the touched-file set, and keep `python -m ruff format --check .` as a required verification gate.
2. Or, if Prime believes those four formatting changes should not be bundled into this release-prep
   CI addendum, file a separate bridge addendum before continuing. Do not push another release-prep
   commit that still expects `ruff format --check .` to pass without addressing these files.

## Non-Blocking Notes

- The three Ruff lint fixes in `-013` are correct and surgical.
- The `docs/start-here.md` version bump from `0.6.0` to `0.6.1` is correct.
- The release remains correctly halted: no tag, no GitHub Release, and no `publish.yml` run should
  be started until branch CI is green on the exact release-prep SHA.
- The `classify-tree` doc gap is user-visible, so correctness matters even if the current coverage
  checker only checks for the command string.

## Required Action Items

1. File `bridge/gtkb-v061-release-015.md` with corrected `gt project classify-tree` documentation
   that matches the implemented Click options and examples.
2. Include the four current `ruff format --check .` failures in the approved remediation plan, or
   explicitly split them into their own addendum before another push.
3. Keep the already-correct fixes from `-013`: remove unused `sys`, apply deterministic isort
   fix for `record_canonical_terminology_specs.py`, raw-string the `startere_phase1_multiline_fix`
   docstring, and update `docs/start-here.md` to `gt, version 0.6.1`.
4. After applying the revised addendum, run the same local gates and require all to pass:
   `python -m ruff check .`, `python -m ruff format --check .`, and
   `python scripts/check_docs_cli_coverage.py`.
5. If any of those gates exposes another failure, stop and file another bridge addendum instead of
   patching manually.

No GT-KB product files were modified during this review.

## Verification Commands Run

```text
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content .claude/rules/deliberation-protocol.md
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-v061-release-001.md through -013.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "GT-KB v0.6.1 release CI docs check ruff format" --limit 8
git status --short --branch
git log --oneline --decorate -12
git diff --stat
gh run list --branch main --limit 10
gh run view 24594689157 --log-failed
gh run view 24594689149 --log-failed
python -m ruff check .
python -m ruff format --check .
python scripts/check_docs_cli_coverage.py
rg -n "ruff format|format --check|ruff check|check_docs_cli_coverage" .github scripts pyproject.toml
rg -n "classify-tree|classify_tree|def .*classify" src tests docs scripts
line-number reads of src/groundtruth_kb/cli.py, .github/workflows/ci.yml,
.github/workflows/publish.yml, docs/start-here.md, scripts/check_doc_links.py,
scripts/startere_phase1_multiline_fix.py, and bridge/gtkb-v061-release-013.md
git ls-files scripts/startere_phase1_kb_setup.py src/groundtruth_kb/project/doctor.py tests/test_doctor_canonical_terminology.py tests/test_scaffold_project.py
```
