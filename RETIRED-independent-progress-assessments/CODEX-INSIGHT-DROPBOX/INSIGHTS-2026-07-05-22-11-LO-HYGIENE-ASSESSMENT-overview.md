# Loyal Opposition Hygiene Assessment - Overview

## Claim

The GroundTruth-KB repository is functionally robust with no critical blockages, but exhibits moderate structural clutter, stale bytecode files, legacy hardcoded root references, and a elevated rate of informational quarantine entries in the Deliberation Archive.

## Scope Assessed

An overview assessment covering all 9 hygiene phases. The following input checks and files were analyzed:
- `python scripts/deliberation_health.py`
- `python scripts/harvest_session_deliberations.py`
- `python scripts/wrap_scan_hygiene.py`
- `python scripts/check_harness_parity.py --all`
- `git status` / `git diff`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` directory listing

## Evidence Paths and Line References

- **Conflict Quarantine Rate (14.3%):** `scripts/deliberation_health.py` output.
- **Unparsed Verdict Warnings:** `scripts/harvest_session_deliberations.py` dry-run log.
- **Stale Bytecode Remnants:** `platform_tests/scripts/__pycache__/test_doctor_kill_switch_staleness.cpython-314-pytest-9.0.2.pyc` (no matching source file `platform_tests/scripts/test_doctor_kill_switch_staleness.py`).
- **Legacy Root References:** `scripts/migrate_root_to_gtkb.py` and `scripts/wrap_scan_hygiene.py`.
- **Harness Parity Degraded/Unsupported Hooks:** `scripts/check_harness_parity.py --all` output.
- **Tracked Configuration Drift:** `.gitignore`, `pyproject.toml`, and `.codex/config.toml` modified in git status.

## Severity-Ranked Findings

### P1: Stale Bytecode and Orphaned Python Remnants
- **Finding:** Stale bytecode files (e.g. `test_doctor_kill_switch_staleness.cpython-314-pytest-9.0.2.pyc`) exist in `__pycache__` directories where the corresponding source file has been deleted. This can lead to test runners discovering phantom tests or executing obsolete code.
- **Evidence:** `task-157.log` (lines 6537-6548).
- **Classification:** `prime-action`

### P2: Legacy Root References in Active Scripts
- **Finding:** Scripts like `scripts/migrate_root_to_gtkb.py` and `scripts/wrap_scan_hygiene.py` contain hardcoded references to the old project root (e.g., `Claude-Playground`), violating the Mandatory Project Root Boundary constraint.
- **Evidence:** `task-157.log` (lines 6750-6756).
- **Classification:** `prime-action`

### P2: Elevated Deliberation Quarantine Rate
- **Finding:** Conflict Quarantine is at 14.3% (PASS is <= 5%). This indicates that a significant portion of archived deliberations are falling back to `informational` classification due to parsing or metadata matching errors.
- **Evidence:** `scripts/deliberation_health.py` report.
- **Classification:** `prime-action`

### P3: Unparsed Verdict Signals in Insight Dropbox
- **Finding:** Deliberation Harvester identifies 5 files with unparsed verdict signals matching search keywords, causing warnings during harvest.
- **Evidence:** `scripts/harvest_session_deliberations.py` dry-run output listing 5 warnings.
- **Classification:** `peer-prime-candidate`

### P3: Structural Naming Inconsistency in Dropbox
- **Finding:** Output artifacts in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` exhibit mixed naming conventions (mixed case, `.txt` vs `.md`, varying prefixes).
- **Evidence:** Directory listing of `CODEX-INSIGHT-DROPBOX`.
- **Classification:** `peer-prime-candidate`

### P4: Repository Namespace Pollution
- **Finding:** High number of stale local branches (120+) present in the local git repository.
- **Evidence:** `git branch` output.
- **Classification:** `peer-prime-candidate`

## Phase-Ranked Action Plan

### Recommended Execution Order
1. **Phase 7 (Gitignore & Scripts Triage):** Clean up stale bytecode files and python caches.
2. **Phase 5 (Terminology Drift):** Rectify hardcoded references to the old project root in active scripts.
3. **Phase 1 (DA Harvest):** Diagnose and resolve the 14.3% Conflict Quarantine rate and clean up unparsed verdict warnings.
4. **Phase 2 (Branch Cleanup):** Prune stale local git branches.
5. **Phase 8 (Naming Consistency):** Standardize naming of insight dropbox files.

## Prime Builder Implementation Sequence

1. **Clean stale python bytecode:** Run a clean command or delete all orphaned `.pyc` files in `__pycache__` directories.
2. **Fix hardcoded root references:** Audit and refactor `scripts/migrate_root_to_gtkb.py` and `scripts/wrap_scan_hygiene.py` to use dynamic root detection.
3. **Quarantine analysis:** Extract conflict quarantine entries from `groundtruth.db` and refine the parser rules in `scripts/deliberation_health.py` to correctly map them.
4. **Standardize drop box names:** Rename legacy and temporary verdict files in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` to follow the canonical naming convention.

## Peer Prime Delegation Candidates

- Stale git branch pruning (`git branch -d`).
- Bulk renaming of insight files.

## LO Verification Plan

- Re-run `python scripts/deliberation_health.py` after Phase 1 fixes to confirm Conflict Quarantine is <= 5%.
- Re-run `python scripts/wrap_scan_hygiene.py` to verify that `pyc_without_source` and `hardcoded_old_project_root` warnings are resolved.

## Explicit Do-Not-Touch / Deferred Areas

- Do not touch or modify the underlying `groundtruth.db` database schema or manually delete historic bridge files (e.g. `smart-poller` references) during this cleanup cycle, as they serve as immutable historical records.

## Owner Decisions Required

- **None:** All identified actions are standard maintenance and hygiene items covered under existing engineering guidelines.

## Residual Risk

- Stale branches on remote origins may be re-pulled if not pruned at the hosting server level.
