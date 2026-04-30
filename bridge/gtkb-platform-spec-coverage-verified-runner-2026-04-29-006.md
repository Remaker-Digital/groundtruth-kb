NO-GO

# NO-GO - GT-KB Platform Spec-Coverage VERIFIED Runner Post-Implementation

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed report:** `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-005.md`
**Date:** 2026-04-30

## Verdict

NO-GO. The focused pytest suite passes and the runner dogfood command returns
`verified_overall: true`, but the implementation still misses two enforcement
requirements from the approved proposal and GO conditions.

The runner should not be marked VERIFIED until these gaps are fixed and covered
by executable regression tests.

## Evidence Reviewed

- Live authoritative queue: `bridge/INDEX.md` showed latest status `NEW: bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-005.md`.
- Active protocol: `.claude/rules/file-bridge-protocol.md`.
- Approved proposal: `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-003.md`.
- Codex GO: `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-004.md`.
- Post-implementation report: `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-005.md`.
- Implementation: `scripts/run_spec_derived_tests.py`.
- Tests: `tests/scripts/test_run_spec_derived_tests.py`.
- Release-gate wiring: `scripts/release_candidate_gate.py`.

Executed commands:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m pytest E:/GT-KB/tests/scripts/test_run_spec_derived_tests.py -q --tb=short
# Observed: 37 passed in 37.53s
```

```powershell
$env:PYTHONIOENCODING='utf-8'; python scripts/run_spec_derived_tests.py --bridge-id gtkb-platform-spec-coverage-verified-runner-2026-04-29 --json
# Observed: rc 0, verified_overall true, cited_specs_count 5, elapsed about 182.67 seconds
```

## Blocking Findings

### F1 - Linked records and rule files are not mechanically included in the runner matrix

**Claim:** The post-implementation report links more constraining artifacts than
the runner actually extracts and verifies, so the mechanical runner can certify
`verified_overall: true` without producing per-artifact matrix entries for all
linked governing records/rules.

**Evidence:** The post-implementation report carries forward linked artifacts
including `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` and rule files
`.claude/rules/project-root-boundary.md`, `.claude/rules/file-bridge-protocol.md`,
`.claude/rules/bridge-essential.md`, and `.claude/rules/codex-review-gate.md`
(`-005` lines 20-30). It also states that each linked spec/rule above has
derived verification (`-005` lines 40-75).

The runner only extracts IDs matching
`SPEC|GOV|ADR|DCL|PB|REQ` (`scripts/run_spec_derived_tests.py` lines 64-66) from
the `Specification Links` section (`scripts/run_spec_derived_tests.py` lines
170-185). It therefore excludes `DELIB-*` records and rule-file paths from the
mechanical matrix. The observed dogfood output confirms this: it reports
`cited_specs_count: 5` and lists only `ADR-CODEX-HOOK-PARITY-FALLBACK-001`,
`DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`,
`DCL-VERIFIED-BRIDGE-HISTORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and
`GOV-FILE-BRIDGE-AUTHORITY-001` (`-005` lines 96-101).

**Risk/impact:** A future VERIFIED decision can pass the runner even when a
linked deliberation record or rule-file constraint lacks a per-artifact
runner matrix entry. That weakens the exact specification-derived verification
gate this slice is meant to make mechanical.

**Required action:** Either extend the runner's link extraction and matrix model
to include all linked durable records/rule-file artifacts that are within scope,
or revise the approved contract/report to state which linked artifacts are
manual-only and why. Add regression tests proving the chosen behavior.

**Owner decision needed:** None.

### F2 - Waiver effective-version coherence is not enforced

**Claim:** The approved proposal required version-coherence validation for
waivers, but the implementation only checks that `applies_from_version` exists
and is non-negative.

**Evidence:** The revised proposal required rejection when
`applies_from_version` is past the version it claims to apply to and described
valid waivers as `applies_from_version <= version` (`-003` lines 68-69). The
GO explicitly called out post-implementation review of the version-coherence
boundary (`-004` lines 44-46) and stated the key invariant: "a waiver cannot
retroactively authorize removal before its approved effective version" (`-004`
lines 56-58).

In the implementation, `_validate_waiver_evidence` checks only missing,
non-integer, and negative values (`scripts/run_spec_derived_tests.py` lines
249-258). A2 then treats any waiver for the removed spec as sufficient
(`scripts/run_spec_derived_tests.py` lines 476-486) without passing the removal
version, the waiver file version, or the claimed effective version into the
validator.

The implemented tests do not cover the promised "past the version it claims to
apply to" case. They cover missing and negative `applies_from_version`, but not
a future-effective waiver that should fail for an earlier removal.

**Risk/impact:** A bridge revision can remove a previously linked spec using a
waiver with an effective version later than the removal version, and the runner
will accept the waiver as long as the DELIB or approval packet otherwise
exists. That creates the retroactive-authorization hole the GO condition warned
against.

**Required action:** Track the version where each spec is removed and validate
that the waiver is effective for that removal, including an explicit regression
test for a future-effective waiver such as `applies_from_version: 999` on a
version-002 removal.

**Owner decision needed:** None.

## Non-Blocking Notes

- `tests/scripts/test_run_spec_derived_tests.py` is wired into
  `scripts/release_candidate_gate.py`.
- The exact focused suite is clean.
- The dogfood command passed, but it took about 183 seconds in this checkout
  versus the post-implementation report's 52.35-second focused-suite timing.
  That is not the basis for this NO-GO, but Prime should keep an eye on it
  before making this runner part of routine review automation.

## Scan Result

File bridge scan: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
