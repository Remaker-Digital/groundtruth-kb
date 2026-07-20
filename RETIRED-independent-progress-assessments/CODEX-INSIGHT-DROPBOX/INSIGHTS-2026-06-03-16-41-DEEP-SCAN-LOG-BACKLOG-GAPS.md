# Deep Scan Log and Backlog Gap Review

Prepared: 2026-06-03 16:41 America/Los_Angeles
Prepared by: Codex Loyal Opposition
Scope: Codex and Claude Code log surfaces, live GT-KB code/artifacts, and live MemBase backlog/project state

## Claim

Three backlog gaps remain materially under-owned after reviewing the logs, current code, and current backlog:

1. A previously owner-approved project for harness automation readiness was never captured in the authoritative backlog.
2. LO advisory routing debt is still treated mainly as unprojected intake, not as executable drain work inside the existing advisory projects.
3. Current Codex bridge-worker logging is dominated by repetitive migration INFO noise, and that signal-quality defect is not backlog-owned.

## Evidence Base

- Runtime logs:
  - `.claude/hooks/.codex-bridge-worker.log`
  - `independent-progress-assessments/bridge-automation/logs/claude-*.stdout.log`
  - `independent-progress-assessments/bridge-automation/logs/codex-*.stderr.log`
- Current source/artifacts:
  - `groundtruth-kb/src/groundtruth_kb/db.py`
  - `groundtruth-kb/src/groundtruth_kb/_logging.py`
  - `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
  - `scripts/advisory_backlog_router.py`
- Current backlog authority:
  - SQLite queries against `groundtruth.db` on 2026-06-03

## Finding 1

### Observation

The June 2 deep-scan memory records owner approval for a new project named `GTKB Harness Automation Readiness`, but the live `projects` table does not contain that project. The prior report itself was only routed into the backlog as `WI-4262` (`Route LO advisory: INSIGHTS-2026-06-02-DEEP-SCAN-BACKLOG-RECOMMENDATIONS.md`) and did not produce the first-class project capture it recommended.

### Deficiency Rationale

This is not just a missing convenience label. The platform already has partial readiness mechanics:

- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` injects `CLAUDE_CODE_OAUTH_TOKEN`, writes status JSON, and detects zero-turn no-ops.
- Historical Claude automation failures still surfaced as runtime `401` and `429` outcomes in the bridge-automation logs instead of a preflight readiness verdict.

Without the project capture, the approved work family is still effectively orphaned and future scans will keep rediscovering the same gap.

### Proposed Solution / Enhancement

Create the missing project `GTKB Harness Automation Readiness` and immediately seed it with two WIs:

1. `Add harness bridge-readiness doctor with auth/quota/no-op classification`
2. `Expose bridge-harness readiness in startup/status surfaces with redacted reason codes`

### Option Rationale

A dedicated project is still the least-regret shape. Existing reliability projects are already broad. This work has a distinct operator-facing contract: determine whether automation is ready before spending a scheduled bridge attempt.

## Finding 2

### Observation

Live backlog state still shows severe advisory intake debt:

- `3080` non-terminal work items with no `project_name`
- `775` non-terminal work items whose title begins `Route LO advisory:`
- Existing active projects `GTKB-LO-ADVISORY-INTAKE` and `Loyal Opposition opportunity-radar` currently have `0` non-terminal member work items

Current router behavior also remains verbose in the common no-new-work case. `scripts/advisory_backlog_router.py` still serializes the full `skipped_existing` list in `RouterResult.as_json()` and the CLI still prints that full JSON payload unconditionally.

### Deficiency Rationale

The platform admits advisories but does not turn the debt into executable drain work. That means recurring scans continue to generate low-value route items faster than the system dispositions them, and even the dry-run tooling spends tokens emitting already-known rows.

### Proposed Solution / Enhancement

Add two WIs under the existing advisory project family rather than creating another umbrella project:

1. Under `GTKB-LO-ADVISORY-INTAKE`:
   - `Create executable drain policy for Route LO advisory backlog (aging, clustering, and disposition lanes)`
2. Under `Loyal Opposition opportunity-radar` or `GTKB-LO-ADVISORY-INTAKE`:
   - `Add compact summary mode to advisory_backlog_router dry-run output`

### Option Rationale

This work already has project homes. The gap is decomposition, not project discovery. Reusing the existing projects avoids further fragmentation and directly converts the current advisory pile into actionable work.

## Finding 3

### Observation

The live Codex worker log is currently dominated by repeated migration lines. On 2026-06-03 alone, `.claude/hooks/.codex-bridge-worker.log` contains `2432` lines, of which `2419` are repeated `groundtruth_kb.db INFO Applied migration ...` entries. Current bridge logging is configured through `groundtruth-kb/src/groundtruth_kb/_logging.py`, where `_setup_bridge_logging()` defaults the package logger to `INFO` for bridge entry points. Current tests explicitly preserve INFO-level migration emission (`groundtruth-kb/tests/test_bridge_logging.py`).

### Deficiency Rationale

This is a live signal-quality defect:

- real warnings are crowded out by repetitive migration chatter
- bridge-worker logs grow quickly without adding decision value
- recurring scans have to spend effort separating meaningful diagnostics from mechanically repeated INFO

No active backlog item currently owns this bridge-log-noise reduction.

### Proposed Solution / Enhancement

Add one WI under `GTKB-DASHBOARD-OBSERVABILITY`:

- `Suppress or aggregate repetitive KnowledgeDB migration INFO in bridge-worker logs`

Suggested acceptance:

- repeated bridge invocations do not emit one migration triplet per activation when nothing changed
- real WARNING/ERROR lines remain visible at the default bridge log level
- tests cover bridge logging behavior for migrations under default INFO settings

### Option Rationale

This belongs in observability/signal quality, not schema migration work. The defect is not the migration logic itself; it is the operator-hostile log shape produced by the current logging contract.

## Addressed Vs. Unaddressed

### Addressed since prior scans

- Claude token handoff and zero-turn no-op detection are implemented in `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`.
- Windows governance preflight recommendations from the June 2 harness-log audit were captured as `WI-4255` through `WI-4258`.
- Bridge signal-quality recommendations from the June 2 harness-log audit were captured as `WI-4253` and `WI-4254`.

### Still unaddressed

- The owner-approved harness-readiness project was not captured in `projects`.
- Advisory-route backlog drain is still not decomposed into executable work under its own active projects.
- Bridge-worker migration log noise remains live and uncaptured.

## Recommended Backlog Additions

### New project recommendation

- `GTKB Harness Automation Readiness`

### New work-item recommendations

- `Add harness bridge-readiness doctor with auth/quota/no-op classification`
  - Home: new project `GTKB Harness Automation Readiness`
- `Expose bridge-harness readiness in startup/status surfaces with redacted reason codes`
  - Home: new project `GTKB Harness Automation Readiness`
- `Create executable drain policy for Route LO advisory backlog (aging, clustering, and disposition lanes)`
  - Home: `GTKB-LO-ADVISORY-INTAKE`
- `Add compact summary mode to advisory_backlog_router dry-run output`
  - Home: `GTKB-LO-ADVISORY-INTAKE` or `Loyal Opposition opportunity-radar`
- `Suppress or aggregate repetitive KnowledgeDB migration INFO in bridge-worker logs`
  - Home: `GTKB-DASHBOARD-OBSERVABILITY`

## Recommended Precedence

1. Capture `GTKB Harness Automation Readiness` first, because it was already owner-approved and is currently missing from backlog authority.
2. Add advisory-drain WIs next, because intake debt is actively compounding.
3. Add the bridge log-noise WI after that, because it improves recurring scan signal but does not block capture of the first two classes.

## Owner Decisions Needed

1. Reconfirm project creation for `GTKB Harness Automation Readiness`, because the prior approval did not result in a live project record.
2. Decide whether advisory debt should be drained primarily by aging/disposition rules, topic clustering, or explicit Prime triage lanes.
3. Decide whether bridge migration log reduction should default to suppression, aggregation, or a lower default log level for KnowledgeDB migration records.
