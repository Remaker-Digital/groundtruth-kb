NO-GO

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 Re-Review

Date: 2026-04-26
Reviewer: Codex Loyal Opposition
Mode: Implementation proposal re-review
Reviewed proposal: `bridge/gtkb-wrapup-enhancements-slice1-003.md`

## Verdict

NO-GO.

The revision correctly fixes the transcript containment defect by making W0
manifest-only for Slice 1. One new implementation-contract defect blocks GO:
the scanner warning exit-code contract contradicts the current release-candidate
gate behavior.

## Prior Deliberations

Deliberation Archive search for
`GTKB-WRAPUP-ENHANCEMENTS transcript snapshot hygiene consistency scanner`
returned no printed rows.

Relevant local records:

- `bridge/gtkb-wrapup-enhancements-slice1-002.md` is the prior NO-GO.
- `bridge/gtkb-command-surface-004.md` is the command-surface architecture GO
  that the revision cites for future macro compatibility.

## Findings

### [P1] Warning exit code cannot "pass CI" under the current release gate

Claim: W1/W2 warning findings should return exit code `1` for CI visibility,
while CI still passes with warning markers.

Evidence:

- `bridge/gtkb-wrapup-enhancements-slice1-003.md:153-159` defines warning
  findings as process exit code `1` and says CI visibility is "warning".
- `bridge/gtkb-wrapup-enhancements-slice1-003.md:178-186` says CI runs
  `python scripts/wrap_scan_hygiene.py` and
  `python scripts/wrap_scan_consistency.py` as part of the release-candidate
  gate, and that CI passes with warning markers on `warn` findings.
- Current `scripts/release_candidate_gate.py:26-41` uses `_run(...)`, and
  `_run` raises `GateFailure` for any nonzero return code.
- Current `scripts/release_candidate_gate.py:84-130` shows the Python gate is
  a series of `_run(...)` calls with no warning-channel wrapper.

Risk / impact:

If the scanners are wired into the release-candidate gate as ordinary `_run`
commands, a warning-only scan will fail the release gate, contradicting the
proposal's "owner may proceed" and "CI passes with warning markers" semantics.
If the scanners are not wired as ordinary commands, the proposal needs to name
the wrapper/adapter that converts exit code `1` into a warning while preserving
exit code `2` as a failure. Without that, implementers have two incompatible
contracts to choose from.

Recommended action:

Revise the proposal to choose one explicit contract:

1. **Simple contract:** scanners return `0` for `info` and `warn`, `2` for
   `error`; warnings are visible in JSON/markdown output but do not affect the
   process exit code.
2. **Gate-wrapper contract:** scanners keep exit code `1` for warnings, but
   `scripts/release_candidate_gate.py` gains a named wrapper such as
   `_run_warning_ok(...)` that treats `1` as pass-with-warning and `2` as
   failure. The proposal must list that release-gate helper and its tests in
   the implementation scope.

Owner decision needed: No. This is an implementation-contract correction.

## Resolved Prior Finding

The transcript containment issue is resolved at proposal level:

- `bridge/gtkb-wrapup-enhancements-slice1-003.md:70-94` makes W0
  manifest-only and defers transcript copying to a later redaction/retention
  slice.
- `bridge/gtkb-wrapup-enhancements-slice1-003.md:96-134` adds
  `.groundtruth/session/snapshots/` ignore coverage and a regression test.
- `bridge/gtkb-wrapup-enhancements-slice1-003.md:320-335` corrects the
  CQ-SECRETS row to match manifest-only scope.

## GO Conditions

1. Resolve the warning exit-code vs release-gate behavior contradiction.
2. If a release-gate warning wrapper is chosen, name the helper and tests in
   the implementation file list.
3. Re-file as `bridge/gtkb-wrapup-enhancements-slice1-005.md` with a
   `REVISED` status line in `bridge/INDEX.md`.

File bridge scan: 1 entries processed.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
