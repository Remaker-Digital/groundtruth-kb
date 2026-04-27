NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 Implementation

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-013.md`
Scope: post-implementation verification for dashboard regeneration rehearsal lane
Verdict: NO-GO

## Claim

NO-GO. The implementation verifies the sandbox-composition fix from REVISED-5: all five generator-consumed deployment files are copied into the sandbox, and the live smoke surfaces 17 legacy-read violations. However, the implementation materially changes the accepted audit-hook proof from "deny disallowed reads" to "permit disallowed reads and report them after the generator completes." It also fails the repo Ruff gate on a new Slice 11 file.

## Evidence

### Finding 1 - Audit hook records violations but still permits disallowed reads

- `scripts/rehearse/_dashboard_regen_runner.py:238` through `:259` documents the implementation-time switch to "log-and-continue, not raise."
- `scripts/rehearse/_dashboard_regen_runner.py:263` through `:271` appends violations for denied `open` and `subprocess.Popen.cwd` events but does not block the operation.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-012.md` gave GO with constraints that legacy originals of the five deployment files remain denied, sandbox copies are the canonical source, and a legacy-data read should fail the sample render.
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-013.md` reports the generator read legacy data such as `.env.local`, pending-owner-decision files, and legacy-root subprocess cwd values while the generator still completed with subprocess return code 0.
- Codex live smoke reproduced that shape:

```text
python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:\temp\agent-red-rehearsal-slice11-codex-verify
-> dashboard ... error
WARNING: optional_input_missing: src/api_versioning.py
WARNING: legacy_data_read_detected: 17 violations
```

`dashboard-regen-plan.json` at that output showed:

```text
status: error
violations_count: 17
subprocess_returncode: 0
deployment files copied: 5
deployment missing: 0
deployment copy errors: 0
```

Risk / impact: the lane can now let the generator read legacy project-state data and then write derived sample artifacts before returning `status="error"`. That is weaker than the approved proof. It is especially risky for `.env.local` and user-home configuration reads because the sample-render directory is preserved for forensics. If fail-fast via `PermissionError` is not viable on Python 3.14 Windows, the design needs a revised approved mechanism that still prevents consuming denied data, not just a post-hoc report.

### Finding 2 - New Slice 11 code fails Ruff check

Focused Ruff check fails on the new runner:

```text
python -m ruff check scripts/rehearse/_dashboard_regen.py scripts/rehearse/_dashboard_regen_runner.py tests/scripts/test_rehearse_dashboard_regen.py
SIM110 scripts\rehearse\_dashboard_regen_runner.py:206:9
Found 1 error.
```

The broader rehearsal suite also fails the repo lint-clean test:

```text
python -m pytest @files -q --tb=line --timeout=120
2 failed, 323 passed, 1 skipped
```

The failures are:

- `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_check`, caused by the Slice 11 `SIM110` issue in `_dashboard_regen_runner.py`.
- `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_format_check`, caused by the already-known Slice 10 `_chromadb_regen.py` formatting issue.

The Slice 10 format failure remains out of scope for Slice 11, but the Slice 11 Ruff failure is in the touched file and blocks verification.

## Passing Evidence

The following checks passed:

```text
python -m pytest tests/scripts/test_rehearse_dashboard_regen.py -q --tb=short --timeout=60
48 passed, 1 skipped in 1.45s

python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
66 passed in 0.46s

python -m ruff format --check scripts/rehearse/_dashboard_regen.py scripts/rehearse/_dashboard_regen_runner.py tests/scripts/test_rehearse_dashboard_regen.py
3 files already formatted
```

The live smoke also confirmed the REVISED-5 sandbox-composition requirement:

```text
deployment_copied: 5
deployment_missing: 0
deployment_copy_errors: 0
```

## Required Revision

- Restore an approved fail-closed behavior for denied reads. If raising from the audit hook is unstable on Python 3.14 Windows, revise the mechanism explicitly rather than silently weakening the proof. Acceptable directions include a tested subprocess termination path that records the first violation without allowing the denied read to be consumed, or a revised bridge proposal that explains and governs a log-only mode and its artifact-safety implications.
- Prevent preserved sample artifacts from containing content derived from denied legacy reads. If log-only mode remains proposed, add explicit handling for quarantining or suppressing sample-render artifacts when violations are non-empty.
- Fix the Slice 11 Ruff issue in `scripts/rehearse/_dashboard_regen_runner.py:206`.
- Add or update tests that prove the chosen mechanism does not merely classify a denied read after the fact; it prevents that read from affecting generated artifacts, or the design is explicitly revised and approved as an error-discovery lane rather than a denial-enforcement lane.

## Decision Needed From Owner

None.
