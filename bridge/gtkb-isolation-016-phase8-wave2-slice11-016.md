VERIFIED

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-015.md`
Scope: post-implementation revision for dashboard regeneration rehearsal lane
Verdict: VERIFIED

## Claim

VERIFIED. REVISED-1 closes the two blocking findings from `bridge/gtkb-isolation-016-phase8-wave2-slice11-014.md`: the audit hook now terminates the subprocess fail-closed on the first denied access, sample-render artifacts are quarantined whenever violations exist, and the Slice 11 Ruff issue is fixed.

The wider rehearsal package still has the known Slice 10 `_chromadb_regen.py` format failure. That is not a Slice 11 blocker.

## Evidence

- `scripts/rehearse/_dashboard_regen_runner.py:220` adds `build_audit_hook(..., terminate_after_violation=True)`.
- `scripts/rehearse/_dashboard_regen_runner.py:266` writes `violations.json` plus `violations.terminated-marker` before termination.
- `scripts/rehearse/_dashboard_regen_runner.py:282` calls `os._exit(99)` on violation in the production/default path.
- `scripts/rehearse/_dashboard_regen_runner.py:292` through `:315` records denied `open` and `subprocess.Popen.cwd` events and then routes them through the fail-closed termination path.
- `scripts/rehearse/_dashboard_regen_runner.py:202` through `:206` fixes the prior SIM110 Ruff issue with `any(...)`.
- `scripts/rehearse/_dashboard_regen.py:423` implements sample-render quarantine.
- `scripts/rehearse/_dashboard_regen.py:740` through `:752` treats returncode 99 and any non-empty violations list as `status="error"` and quarantines sample artifacts.
- `tests/scripts/test_rehearse_dashboard_regen.py:582` through `:652` adds/updates coverage for violation recording, returncode 99 handling, and quarantine behavior.

Codex verification commands:

```text
python -m pytest tests/scripts/test_rehearse_dashboard_regen.py -q --tb=short --timeout=60
51 passed, 1 skipped in 1.59s

python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
66 passed in 0.47s

python -m ruff check scripts/rehearse/_dashboard_regen.py scripts/rehearse/_dashboard_regen_runner.py tests/scripts/test_rehearse_dashboard_regen.py
All checks passed!

python -m ruff format --check scripts/rehearse/_dashboard_regen.py scripts/rehearse/_dashboard_regen_runner.py tests/scripts/test_rehearse_dashboard_regen.py
3 files already formatted
```

Live smoke:

```text
python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:\temp\agent-red-rehearsal-slice11-revised1-codex-verify
-> dashboard ... error
WARNING: optional_input_missing: src/api_versioning.py
WARNING: audit_hook_fail_closed_termination: subprocess terminated by audit hook on first of 1 violation(s); sample_render quarantined
```

Live smoke artifact inspection:

```text
status: error
violations_count: 1
subprocess_returncode: 99
deployment_copied: 5
deployment_missing: 0
deployment_copy_errors: 0
sample_render exists: False
sample_render.QUARANTINED-1-violations exists: True
violations.terminated-marker exists: True
```

The recorded first violation was:

```text
event: subprocess.Popen.cwd
cwd: E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
```

The marker file confirmed:

```text
reason: audit_hook_fail_closed
```

The broader rehearsal glob was also rerun:

```text
python -m pytest @files -q --tb=line --timeout=120
1 failed, 327 passed, 1 skipped in 8.87s
```

The only failure was `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_format_check`, caused by `scripts\rehearse\_chromadb_regen.py` needing format. That is the pre-existing Slice 10 WIP issue.

## Risk / Impact

The lane now enforces the intended proof shape: denied legacy access does not continue through the generator, and incomplete sample-render artifacts are clearly quarantined. The first live violation is a real generator-hardening signal for follow-on work: `session_self_initialization.py` still reaches outside the sandbox through a `git ls-remote` cwd path.

Residual risk is limited to platform behavior around `os._exit(99)` from an audit hook. Codex verified the live behavior on this Windows/Python 3.14 checkout, and the implementation explicitly documents why this mechanism replaced `raise PermissionError`.

## Recommended Action

Proceed with Slice 11 as verified. Track the remaining dashboard generator hardening as follow-on work, and keep the Slice 10 `_chromadb_regen.py` formatting issue in Slice 10 scope.

## Decision Needed From Owner

None.
