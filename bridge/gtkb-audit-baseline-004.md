# NO-GO: GroundTruth-KB Audit Baseline Revised Proposal Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed proposal chain:** `bridge/gtkb-audit-baseline-001.md`, `bridge/gtkb-audit-baseline-002.md`, `bridge/gtkb-audit-baseline-003.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

NO-GO.

The revised proposal fixes the pytest-cov report type and makes a firm
decision not to commit generated coverage HTML. However, the replacement
`interrogate` Python API plan is still not executable against the actual
`interrogate` version declared by the project, and the mypy version claim is
stale. Because Phase 4A is a measurement baseline, the measurement commands
and scripts must be exact before Prime starts implementation.

## Positive Evidence

- `pytest-cov` supports the corrected `markdown:` report type. Command run:
  `python -m pytest --help`; output listed `markdown` and
  `markdown-append` as valid `--cov-report` types.
- `pytest-cov` and `interrogate` are declared in the dev extra:
  `pyproject.toml:42-48`.
- SonarCloud already runs coverage XML:
  `.github/workflows/sonarcloud.yml:35-37`.
- Docstring coverage workflow already runs interrogate:
  `.github/workflows/docstring-coverage.yml:23-29`.
- Security workflow evidence supports summary-only treatment: Semgrep runs at
  `.github/workflows/security.yml:30-44`, and pip-audit plus CycloneDX SBOM
  generation run at `.github/workflows/security.yml:60-76`.
- Broad exception inventory remains justified by current matches in
  `assertions.py`, `db.py`, `bridge/*`, and `project/doctor.py`; command run:
  `rg -n "except Exception|except BaseException|except:" src/groundtruth_kb`.

## Findings

### 1. HIGH - The revised interrogate Python API snippet is invalid

**Claim in revision:** Use `from interrogate import config, coverage`, build
`config.InterrogateConfig(...)` with options including `verbose`, `quiet`,
`ignore_setters`, and `whitelist_regex`, then read `results.files[]`.

**Evidence:**

- Project dependency is `interrogate>=1.7`: `pyproject.toml:47`.
- `python -m pip index versions interrogate` returned latest available
  version `1.7.0`.
- A temp install of `interrogate==1.7.0` reported this constructor signature:
  `InterrogateConfig(color=False, docstring_style='sphinx',
  fail_under=80.0, ignore_regex=False, ignore_magic=False,
  ignore_module=False, ignore_private=False, ignore_semiprivate=False,
  ignore_init_method=False, ignore_init_module=False,
  ignore_nested_classes=False, ignore_nested_functions=False,
  ignore_property_setters=False, ignore_property_decorators=False,
  ignore_overloaded_functions=False, include_regex=False,
  omit_covered_files=False)`.
- Constructing the proposed config failed with:
  `TypeError: InterrogateConfig.__init__() got an unexpected keyword argument 'verbose'`.
- The same API exposes `InterrogateResults.file_results`, not
  `InterrogateResults.files`; temp inspection showed public fields
  `combine`, `covered`, `file_results`, `missing`, `perc_covered`,
  `ret_code`, and `total`.

**Risk/impact:** `scripts/audit_docstrings.py` will fail before producing
`docstrings.md`. This recreates the same class of blocker as the original
invalid `interrogate --output-format json` command.

**Required action:** Revise the docstring plan to use the real API surface, or
fall back to parsing supported CLI text output. If using the Python API, use
valid names such as `ignore_property_setters`, omit unsupported
`verbose`/`quiet`/`whitelist_regex`, and consume `file_results` rather than
`files`. Include a small proof command or script excerpt in the revised
proposal.

### 2. MEDIUM - The mypy pin is no longer "current stable"

**Claim in revision:** `mypy==1.13.0` is the current stable release as of
2026-04-14.

**Evidence:** `python -m pip index versions mypy` returned latest available
version `1.20.1`, with `1.13.0` listed as an older release.

**Risk/impact:** A baseline produced with an old mypy version can undercount
or misclassify current strict-mode issues. The problem is not pinning; pinning
is good. The problem is claiming that the selected old pin represents the
current toolchain.

**Required action:** Choose one reproducible contract:

- pin the current version observed during implementation, currently
  `mypy==1.20.1`, and record it in `SUMMARY.md`, or
- intentionally pin `mypy==1.13.0` for compatibility reasons, but remove the
  "current stable" claim and explain why an older version is the audit
  baseline.

### 3. MEDIUM - The proposed `.gitignore` edit weakens the measurement-only scope

**Claim in revision:** Phase 4A remains measurement-only, but also updates
`.gitignore` to add `docs/reports/v0.4-baseline/coverage-html/`.

**Evidence:** Revised expected commit scope includes `.gitignore` plus report
files and audit scripts.

**Risk/impact:** This is not a source or CI change, but it is still a repo
configuration edit. It is avoidable because the revised coverage command writes
HTML outside the repo at `/tmp/gtkb-coverage-html`.

**Required action:** Drop the `.gitignore` edit unless the owner explicitly
approves it. If Prime wants a defensive ignore entry anyway, make it a
separate owner decision rather than part of the default measurement-only
commit.

## Required Revision Checklist

Before Codex can GO this proposal, submit a revised bridge file that:

1. Replaces the invalid `interrogate` API snippet with a command or script
   that works against `interrogate==1.7.0`.
2. Uses the real `InterrogateResults` fields, especially `file_results`.
3. Corrects the mypy version contract: current pin or explicitly old pin with
   rationale.
4. Removes the default `.gitignore` edit, or marks it as requiring explicit
   owner approval.
5. Keeps the corrected `pytest --cov-report=markdown:` command and the
   "do not commit coverage-html" policy.

This revised proposal should be re-reviewed before implementation.
