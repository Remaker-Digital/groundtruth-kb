# Deep Scan Backlog Delta Review

Prepared: 2026-06-03 16:58 America/Los_Angeles
Prepared by: Codex Loyal Opposition
Scope: Codex/Claude operational logs, live GT-KB source/artifacts, and current MemBase backlog state

## Claim

The current Deep Scan reduces to three legitimate backlog gaps and two previously recommended items that should now be retired from the recommendation set because the codebase already implemented them.

Remaining real gaps:

1. The owner-approved harness-readiness project still does not exist in authoritative backlog state.
2. Advisory-routing debt is still largely parked as unprojected route items, and the active advisory projects have no open member work items.
3. Current Codex bridge-worker logs are still dominated by repetitive KnowledgeDB migration INFO lines, with no active backlog ownership for that signal-quality defect.

No longer recommended as new backlog additions:

1. Formal parked/deferred bridge semantics, because `DEFERRED` is implemented and tested in live GT-KB code.
2. Legacy-root authority-resolution surfacing, because active detection and authority-resolution commands now exist in `groundtruth-kb`.

## Evidence Base

- Logs and transcript-like runtime surfaces:
  - [E:\GT-KB\.claude\hooks\.codex-bridge-worker.log](</E:\GT-KB/.claude/hooks/.codex-bridge-worker.log>)
  - [E:\GT-KB\independent-progress-assessments\bridge-automation\logs\claude-scan.log](</E:\GT-KB/independent-progress-assessments/bridge-automation/logs/claude-scan.log>)
  - [E:\GT-KB\independent-progress-assessments\bridge-automation\logs\scan.log](</E:\GT-KB/independent-progress-assessments/bridge-automation/logs/scan.log>)
  - [E:\GT-KB\independent-progress-assessments\bridge-automation\logs\bridge-monitor-watchdog.log](</E:\GT-KB/independent-progress-assessments/bridge-automation/logs/bridge-monitor-watchdog.log>)
  - [E:\GT-KB\independent-progress-assessments\bridge-automation\logs\bridge-liveness-alert.log](</E:\GT-KB/independent-progress-assessments/bridge-automation/logs/bridge-liveness-alert.log>)
- Live source/artifact surfaces:
  - [E:\GT-KB\scripts\advisory_backlog_router.py](</E:\GT-KB/scripts/advisory_backlog_router.py>)
  - [E:\GT-KB\groundtruth-kb\src\groundtruth_kb\_logging.py](</E:\GT-KB/groundtruth-kb/src/groundtruth_kb/_logging.py>)
  - [E:\GT-KB\groundtruth-kb\tests\test_bridge_logging.py](</E:\GT-KB/groundtruth-kb/tests/test_bridge_logging.py>)
  - [E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\doctor.py](</E:\GT-KB/groundtruth-kb/src/groundtruth_kb/project/doctor.py>)
  - [E:\GT-KB\groundtruth-kb\tests\test_doctor_legacy_root.py](</E:\GT-KB/groundtruth-kb/tests/test_doctor_legacy_root.py>)
  - [E:\GT-KB\groundtruth-kb\tests\test_bridge_detector.py](</E:\GT-KB/groundtruth-kb/tests/test_bridge_detector.py>)
- Current backlog authority:
  - SQLite queries against `groundtruth.db` on 2026-06-03 via `groundtruth-kb/.venv/Scripts/python.exe`

## What The Logs Still Show

### Pattern A: Claude automation historically failed on auth/readiness before doing useful work

Evidence:

- `claude-scan.log` still records repeated `WARN: .local/claude-oauth-token.txt missing` and `ERROR: claude exec exited with 1` events on 2026-05-05.
- The current Claude scan script includes explicit token handoff, status JSON, and zero-turn validation in [E:\GT-KB\independent-progress-assessments\bridge-automation\claude-file-bridge-scan.ps1](</E:\GT-KB/independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1>), so the mechanism improved.

Interpretation:

- The expensive failure mode is better handled technically, but the approved backlog home for an operator-facing readiness surface is still missing.

### Pattern B: Advisory routing is correct but still produces large low-value no-change output

Evidence:

- The June 3 advisory report already documented a dry run that scanned `745` advisories and created `0` rows while still emitting the full `skipped_existing` list.
- Live code still serializes `skipped_existing` in `RouterResult.as_json()` and the CLI still prints that full JSON unconditionally from `main()` in [E:\GT-KB\scripts\advisory_backlog_router.py](</E:\GT-KB/scripts/advisory_backlog_router.py>).

Interpretation:

- This is not a correctness bug. It is still a recurring token-cost and operator-visibility issue.

### Pattern C: The current Codex worker log is still overwhelmingly migration noise

Evidence:

- The tail of [E:\GT-KB\.claude\hooks\.codex-bridge-worker.log](</E:\GT-KB/.claude/hooks/.codex-bridge-worker.log>) is almost entirely repeated `groundtruth_kb.db INFO Applied migration ...` triplets.
- [E:\GT-KB\groundtruth-kb\src\groundtruth_kb\_logging.py](</E:\GT-KB/groundtruth-kb/src/groundtruth_kb/_logging.py>) still sets bridge logging to `INFO` by default.
- [E:\GT-KB\groundtruth-kb\tests\test_bridge_logging.py](</E:\GT-KB/groundtruth-kb/tests/test_bridge_logging.py>) still explicitly preserves INFO-level migration emission.

Interpretation:

- The current behavior is intentional, but it remains a poor operational default for recurring bridge scans.

### Historical patterns that no longer drive new backlog recommendations

Evidence:

- Early `.codex-bridge-worker.log` lines show old resident-worker failures such as `loop error: 'canonical_message'` and repeated `WinError 206` command-line overflows.
- `scan.log` now shows the Codex automated bridge scan operating with a bounded `cap=1`, and current priority work is no longer about those historical worker explosions.
- `bridge-monitor-watchdog.log` and `bridge-liveness-alert.log` contain old April 25 alert-loop failures, but the June 2 harness-log audit already routed current bridge-signal issues into `WI-4253` and `WI-4254`.

Interpretation:

- Those older failures are useful historical evidence, but they are not the best remaining uncaptured backlog opportunities.

## Verification Against Current Code And Artifacts

### Addressed since earlier Deep Scans

#### 1. Parked/deferred bridge semantics are implemented

Evidence:

- `DEFERRED` is part of the live bridge status enum and parser in [E:\GT-KB\groundtruth-kb\src\groundtruth_kb\bridge\detector.py](</E:\GT-KB/groundtruth-kb/src/groundtruth_kb/bridge/detector.py>) and related bridge modules.
- Tests cover `DEFERRED` parsing and non-actionability in [E:\GT-KB\groundtruth-kb\tests\test_bridge_detector.py](</E:\GT-KB/groundtruth-kb/tests/test_bridge_detector.py>) and related bridge tests.

Conclusion:

- Remove parked/deferred bridge semantics from the list of missing backlog additions. That recommendation was valid on 2026-06-02 but is stale now.

#### 2. Legacy-root authority detection and authority-resolution surfacing are implemented

Evidence:

- The CLI exposes `authority resolve` and `authority status` in [E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py](</E:\GT-KB/groundtruth-kb/src/groundtruth_kb/cli.py>).
- Active legacy-root detection exists in [E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\doctor.py](</E:\GT-KB/groundtruth-kb/src/groundtruth_kb/project/doctor.py>).
- Regression coverage exists in [E:\GT-KB\groundtruth-kb\tests\test_doctor_legacy_root.py](</E:\GT-KB/groundtruth-kb/tests/test_doctor_legacy_root.py>).

Conclusion:

- Remove live-authority/legacy-root detection from the list of missing backlog additions. The platform now has an implemented surface, even if future refinement is still possible.

### Still Unaddressed

#### 1. The approved harness-readiness project is still missing

Evidence:

- Current projects contain `GTKB-DASHBOARD-OBSERVABILITY` and `GTKB-LO-ADVISORY-INTAKE`, but no project named `GTKB Harness Automation Readiness`.
- The June 2 and June 3 deep-scan advisories were routed only as unprojected advisory rows:
  - `WI-4262 | Route LO advisory: INSIGHTS-2026-06-02-DEEP-SCAN-BACKLOG-RECOMMENDATIONS.md | None`
  - `WI-4284 | Route LO advisory: INSIGHTS-2026-06-03-16-41-DEEP-SCAN-LOG-BACKLOG-GAPS.md | None`

Conclusion:

- This remains the highest-precedence backlog gap because the owner already approved it and the authoritative backlog still does not reflect that approval.

#### 2. Advisory-routing debt still lacks executable drain work

Evidence:

- Current open `Route LO advisory:` count is `741`.
- Current open unprojected work-item count is `818`.
- `GTKB-LO-ADVISORY-INTAKE` exists and is active, but a live query returned no open member work items assigned to that project.
- `PROJECT-GTKB-LO-ADVISORY-ROUTING` likewise returned no open member work items.
- `Loyal Opposition opportunity-radar` exists only as a retired project.

Conclusion:

- The system still admits advisories faster than it turns them into concrete drain work. This is a real backlog-shape gap, not just a logging annoyance.

#### 3. Bridge-worker migration-noise reduction is still uncaptured

Evidence:

- No open work items are currently assigned to `GTKB-DASHBOARD-OBSERVABILITY`.
- No current work item title surfaced a direct owner for suppressing or aggregating repetitive migration INFO in bridge-worker logs.

Conclusion:

- This remains a clean standalone WI candidate under an existing observability project.

## Backlog Coverage Assessment

### Already captured elsewhere

- Bridge signal-quality diagnostics:
  - `WI-4253` under `PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY`
  - `WI-4254` under `PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY`
- Windows governance preflight surface:
  - `WI-4255` through `WI-4258` under `PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE`
- Wrap-scan scanner-owned artifact policy:
  - `WI-4259` under `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`

### Still not captured well enough

- Approved harness-readiness project missing from `current_projects`
- Advisory-drain execution work missing from active advisory projects
- Bridge-worker migration-noise WI missing from observability ownership

## Recommended Backlog Additions

### Project approval to reconfirm

- `GTKB Harness Automation Readiness`

Why this is still needed:

- It was already approved in substance.
- The current code proves there is a coherent problem family around auth/quota/no-op readiness.
- The authoritative backlog still lacks the actual project record.

Suggested first work items:

- `Add harness bridge-readiness doctor with auth/quota/no-op classification`
- `Expose bridge-harness readiness in startup/status surfaces with redacted reason codes`

### Work items to add under existing projects

- Under `GTKB-LO-ADVISORY-INTAKE`:
  - `Create executable drain policy for Route LO advisory backlog (aging, clustering, and disposition lanes)`
  - `Add compact summary mode to advisory_backlog_router dry-run output`
- Under `GTKB-DASHBOARD-OBSERVABILITY`:
  - `Suppress or aggregate repetitive KnowledgeDB migration INFO in bridge-worker logs`

## Recommended Precedence

1. Reconfirm and capture `GTKB Harness Automation Readiness` first.
2. Add the advisory-drain work items next.
3. Add the bridge-worker migration-noise item after that.

Reason:

- The first item is already owner-approved and missing from authority.
- The second reduces recurring backlog growth and token waste.
- The third is valuable but does not block the first two.

## Owner Questions To Ask In Dependency Order

Only one owner question should be asked now.

Recommended first question:

- Reconfirm whether the previously approved project should now be captured canonically as `GTKB Harness Automation Readiness`, with the two readiness work items above seeded immediately.

Later questions, only after that is resolved:

- Which advisory-drain policy should dominate: aging/disposition, clustering, or explicit triage lanes?
- Should bridge-worker migration noise be reduced by suppression, aggregation, or a lower default logger level?
