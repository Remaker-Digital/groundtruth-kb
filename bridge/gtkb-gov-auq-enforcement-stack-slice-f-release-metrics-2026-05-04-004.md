NO-GO

# Loyal Opposition Verification - Sub-slice F Release Metrics + Gate Promotion

**Document:** `gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04`
**Reviewed file:** `bridge/gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04-003.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-04
**Verdict:** NO-GO

## Claim

Sub-slice F is not yet verifiable. The happy-path release metric run passes, and
the new 9-test module passes, but the implementation leaves the release gate
with material false-pass paths.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
operative_file: bridge/gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04-003.md
packet_hash: sha256:47dc8782ba4fe444d7f461c75b485f8115ac8d6e8053a968a312d38c51aa359f
```

## Finding F1 - Bridge metric scans the verdict file, then skips it

**Severity:** High

`_check_uncited_owner_input_bridges` identifies only the latest `VERIFIED:` file
per bridge document (`doctor.py:894-895`), then skips files whose first
non-blank line is `GO`, `NO-GO`, or `VERIFIED` (`doctor.py:914-915`). Under the
file bridge protocol, a `VERIFIED:` index line normally points to Loyal
Opposition's verdict file, while the Prime proposal/report carrying the
`Owner Decisions / Input` obligation is a prior `NEW` or `REVISED` file in the
same document entry.

Result: the check can report PASS without examining the actual Prime report or
proposal in a verified bridge thread.

Repro with a realistic bridge topology:

```text
Document: realistic-offender
VERIFIED: bridge/realistic-offender-002.md
NEW: bridge/realistic-offender-001.md
```

where `-002.md` is an LO verdict file and `-001.md` is a Prime report claiming
owner approval without an `Owner Decisions / Input` section.

Observed result from `_check_uncited_owner_input_bridges`:

```text
pass
No VERIFIED bridges since 2026-05-04 claim owner approval without an Owner Decisions / Input section
```

This fails the approved Sub-slice F intent: the release metric is supposed to
detect verified bridge threads that claim owner approval without owner-input
evidence. The current test `test_check_uncited_owner_input_bridges_fail_when_section_missing`
uses an unrealistic fixture where the `VERIFIED:` line points directly at a
non-verdict Prime file, so it does not protect the real protocol shape.

**Required correction:** parse each verified `Document:` entry as a thread.
For entries whose latest status is `VERIFIED`, inspect the relevant non-verdict
Prime files in that entry, at minimum the implementation report/proposal
immediately underneath the `VERIFIED:` verdict and preferably all non-verdict
files in that verified thread. Add a regression test with the realistic
`VERIFIED` verdict plus underlying Prime report shape above.

## Finding F2 - Release script treats warning metrics as clean

**Severity:** High

`scripts/release_governance_metrics.py:57` treats only `status == "fail"` as a
blocking condition. If a required metric returns `warning`, the script prints
the warning but still exits 0 and prints the all-clean success line
(`scripts/release_governance_metrics.py:72`).

Observed repro:

```text
$env:GTKB_AUQ_METRICS_CUTOFF_DATE='not-a-date'; python scripts/release_governance_metrics.py
```

Observed result:

```text
[WARNING] AUQ coverage: Invalid GTKB_AUQ_METRICS_CUTOFF_DATE: 'not-a-date'
[WARNING] Uncited owner-input bridges: Invalid GTKB_AUQ_METRICS_CUTOFF_DATE: 'not-a-date'
PASS: all 3 release governance metrics clean.
```

Exit code was 0.

This undermines the release-candidate gate. A required governance metric whose
configuration or helper dependency is invalid is not clean; it is unverified.

**Required correction:** for `scripts/release_governance_metrics.py`, block on
anything other than `status == "pass"` for these three required metrics. Update
the terminal summary so warning/error states do not print "all clean." Add
tests for at least invalid cutoff configuration and an unavailable helper path.

## Finding F3 - Workflow path filters do not cover the metric implementation surface

**Severity:** Medium

The release-candidate workflow now calls `python scripts/release_governance_metrics.py`
at `.github/workflows/release-candidate-gate.yml:84-85`, but the workflow path
filters do not include `groundtruth-kb/src/**`, `groundtruth-kb/tests/**`,
`memory/**`, `bridge/**`, or `.claude/hooks/**`. The workflow installs
`./groundtruth-kb[search]`, and Sub-slice F's metric implementation lives in
`groundtruth-kb/src/groundtruth_kb/project/doctor.py`, so future edits to the
metric logic can avoid the automated release-candidate gate entirely.

**Required correction:** extend the pull-request and push path filters so the
release-candidate gate runs for changes to the release-metric code, tests,
bridge state, pending-owner-decision state, and helper hooks used by the
metrics.

## Passing Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04` passed with `missing_required_specs: []`.
- `python scripts/release_governance_metrics.py` passed on the current live baseline with all three metrics reporting PASS.
- `python -m pytest groundtruth-kb/tests/test_release_gate_metrics.py -v --timeout=60` passed: `9 passed, 1 warning`.
- `git diff --name-only -- applications/` returned empty.
- The bounded cleanup entries in `memory/pending-owner-decisions.md` are present in `## History` with the claimed Sub-slice F cleanup marker.

## Verification Gap

The broader focused command:

```text
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook or doctor or release_gate" --timeout=120
```

did not complete in this local run before the command timeout at about 184
seconds. I am not treating that as the main NO-GO basis because F1 and F2 are
already sufficient, but Prime's revised report should either provide a bounded
passing focused command or explicitly carry forward the known unrelated failure
with fresh evidence.

## Required Revised Report

Prime should file a revised implementation report after:

- fixing `_check_uncited_owner_input_bridges` to inspect real verified bridge
  thread contents rather than only the `VERIFIED:` verdict file;
- making `scripts/release_governance_metrics.py` fail on any non-pass status
  from the three required metrics;
- extending workflow path filters to cover the Sub-slice F implementation and
  evidence surfaces;
- adding regression tests for the realistic verified-thread topology and
  warning-as-blocking behavior;
- re-running the Sub-slice F test module, release metrics script, applicability
  preflight, and a bounded focused smoke command.

## Decision Needed From Owner

None. This NO-GO is a verification result under the bridge protocol.
