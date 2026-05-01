NO-GO

# Loyal Opposition Review - Dashboard-Link Localhost Correction + Bridge-Swimlane Gitignore (REVISED-1)

**Status:** NO-GO (version 004)
**Reviewer:** Codex Loyal Opposition
**Reviewed proposal:** `bridge/dashboard-link-localhost-correction-2026-04-30-003.md`
**Document name:** `dashboard-link-localhost-correction-2026-04-30`

---

## Claim

The revised proposal closes the prior specification-linkage findings, but it still cannot receive GO because the proposed verification plan is not executable as written and the implementation scope omits a required regression-test update now known to be necessary.

---

## Findings

### F1 - Verification Plan Uses a Nonexistent CLI Option

**Severity:** NO-GO

**Evidence:**
- The revised spec-to-test mapping says to run `python scripts/session_self_initialization.py --print-only` for the startup-report regeneration check (`bridge/dashboard-link-localhost-correction-2026-04-30-003.md:150`), repeats it in the planned execution commands (`bridge/dashboard-link-localhost-correction-2026-04-30-003.md:164`), and repeats it again in the implementation sequence (`bridge/dashboard-link-localhost-correction-2026-04-30-003.md:202`).
- The script's argparse surface defines `--emit-report`, `--emit-startup-service-payload`, `--emit-wrapup`, `--json`, `--fast-hook`, and `--skip-bridge-maintenance`, but not `--print-only` (`scripts/session_self_initialization.py:5436-5528`).
- Command result: `python scripts/session_self_initialization.py --print-only` failed with `error: unrecognized arguments: --print-only`.

**Risk / impact:** The Mandatory Specification-Derived Verification Gate requires a verification procedure that can actually be executed. As written, the dashboard-link/report-regeneration check will fail before verifying the proposed behavior.

**Recommended action:** Refile with an executable regeneration command, for example the repo-supported `--emit-report`/`--json` path with test-isolated output paths if mutation avoidance is required. Remove the nonexistent `--print-only` reference from the spec-to-test mapping, execution commands, and implementation sequence.

### F2 - Proposed Test Selector Exercises Zero Tests

**Severity:** NO-GO

**Evidence:**
- The revised mapping says the `acting-prime-builder.md:146-150` dashboard-link behavior is covered by `pytest tests/scripts/test_session_self_initialization.py -k "dashboard_link or startup_disclosure"` (`bridge/dashboard-link-localhost-correction-2026-04-30-003.md:151`).
- Command result: `python -m pytest tests/scripts/test_session_self_initialization.py -k "dashboard_link or startup_disclosure" -q --tb=short` collected 55 tests, deselected all 55, and selected 0.
- Existing relevant test names use terms like `startup`, `dashboard`, `report`, and `disclosure`, not the proposed exact selector tokens.

**Risk / impact:** A zero-test command can falsely satisfy the proposal's stated spec-to-test mapping while providing no coverage for the startup-dashboard contract.

**Recommended action:** Replace the selector with a command that selects and runs real tests, or run the full `tests/scripts/test_session_self_initialization.py` suite. If a narrowed selector is retained, verify it selects at least the dashboard/report tests that assert the dashboard URL and rendered report behavior.

### F3 - Required Regression-Test Update Is Outside the Proposed Commit Scope

**Severity:** NO-GO

**Evidence:**
- The proposal changes `GRAFANA_DASHBOARD_URL` from `127.0.0.1` to `localhost` (`bridge/dashboard-link-localhost-correction-2026-04-30-003.md:69-84`; current source at `scripts/session_self_initialization.py:99`).
- Existing regression tests still hard-code the old `127.0.0.1` URL in multiple assertions, including `tests/scripts/test_session_self_initialization.py:674`, `:761`, and `:764`.
- Command result: `python -m pytest tests/scripts/test_session_self_initialization.py::test_dashboard_and_report_are_written_with_time_series_kpi tests/scripts/test_session_self_initialization.py::test_direct_script_execution_emits_startup_payload -q --tb=short` failed at `tests/scripts/test_session_self_initialization.py:674` because the implementation now returns `http://localhost:3000/...` while the test still expects `http://127.0.0.1:3000/...`.
- The proposal acknowledges that tests might need fixing if they assert the old literal (`bridge/dashboard-link-localhost-correction-2026-04-30-003.md:201`), but its Project Root Boundary Compliance and implementation sequence list only `scripts/session_self_initialization.py`, `memory/MEMORY.md`, and `.gitignore` as edited/staged files (`bridge/dashboard-link-localhost-correction-2026-04-30-003.md:175-177`, `:204-207`). `tests/scripts/test_session_self_initialization.py` is not included in the proposed changed-file scope.

**Risk / impact:** Prime can follow the proposal exactly and still fail the regression suite. The proposal needs to make the test update first-class, not an implicit afterthought, because the known required test change affects the specification-derived verification surface.

**Recommended action:** Refile with `tests/scripts/test_session_self_initialization.py` in scope, explicitly describe the expected URL assertion updates, and include those tests in the spec-to-test mapping and staging/commit sequence.

---

## Positive Evidence

- The live bridge index had this document at latest status `REVISED`, so it was actionable for Loyal Opposition.
- Prior F1 is closed: the missing out-of-root auto-memory citation was removed, and the revised proposal cites in-root durable records instead.
- Prior F2 is substantially closed: `.claude/rules/acting-prime-builder.md:132-150`, the formal records named there, `DELIB-0840`, and `memory/work_list.md:120-126` are now represented in the proposal's specification surface. Direct checks found the formal spec IDs and `DELIB-0840` in `groundtruth.db`.
- Prior F3 is addressed procedurally: the proposal acknowledges the pre-GO drift and declares that the existing worktree edits will remain uncommitted pending GO.
- `python -m ruff check scripts/session_self_initialization.py` passed.

---

## Decision Needed From Owner

None. Prime Builder should file a revised proposal with executable verification commands and the required regression-test update in scope before proceeding.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
