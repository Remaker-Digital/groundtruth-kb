# Deep Scan Backlog Recommendations - Loyal Opposition

Prepared: 2026-06-02
Prepared by: Codex Loyal Opposition
Scope: Codex and Claude bridge-automation logs, live GT-KB code/artifacts, live MemBase backlog state

## Claim

The Deep Scan found four distinct classes of transcript-derived issues:

1. Some historically expensive failures have already been addressed in code and tests.
2. Some issues are only partially addressed: the local mechanism improved, but the operator-facing readiness or authority surface is still missing.
3. Several remaining costs are backlog-shape problems rather than code bugs, especially large amounts of unprojected advisory routing work.
4. The highest-value backlog additions are narrow and mechanical. Most broad umbrella projects already exist and should not be duplicated.

## Evidence Base

- Transcript corpus:
  - `independent-progress-assessments/bridge-automation/logs/codex-*.stderr.log`
  - `independent-progress-assessments/bridge-automation/logs/codex-*.stdout.log`
  - `independent-progress-assessments/bridge-automation/logs/claude-*.stderr.log`
  - `independent-progress-assessments/bridge-automation/logs/claude-*.stdout.log`
- Current code/artifacts:
  - `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
  - `independent-progress-assessments/bridge-automation/repair-claude-token-handoff.ps1`
  - `platform_tests/scripts/test_cli_backlog_status.py`
  - `.claude/rules/canonical-terminology.md`
  - `AGENTS.md`
  - `bridge/INDEX.md`
- Current backlog state:
  - SQLite queries against `groundtruth.db` on 2026-06-02

## What The Logs Show

### Pattern 1 - Claude headless automation repeatedly failed on credentials and later on limits.

- Evidence:
  - `independent-progress-assessments/bridge-automation/logs/claude-20260414T163350Z.stdout.log` shows `401` invalid authentication credentials.
  - `independent-progress-assessments/bridge-automation/logs/claude-20260505T162301Z.stdout.log` shows `429` limit exhaustion.
- Risk / impact:
  - Automation can fail before doing useful bridge work.
  - The current operator workflow still discovers some readiness failures by trying and failing.

### Pattern 2 - Codex automation repeatedly suffered Windows-shell and tool-startup friction.

- Evidence:
  - `independent-progress-assessments/bridge-automation/logs/codex-20260411T145509Z.stderr.log` shows `prime-bridge` MCP startup failure, SQLite/query failures, and file-lock cleanup issues.
  - `independent-progress-assessments/bridge-automation/logs/codex-20260411T150409Z.stderr.log` and `...151309Z.stderr.log` show PowerShell quoting and regex parse failures.
  - `independent-progress-assessments/bridge-automation/logs/codex-20260411T152809Z.stderr.log` shows repeated path/glob misuse and Windows command-shape errors.
- Risk / impact:
  - Review work burns cycles on shell portability instead of governed logic.
  - The same command-shape mistakes recur across sessions.

### Pattern 3 - Bridge work repeatedly no-ops on stale, already-actioned, or parked work.

- Evidence:
  - `independent-progress-assessments/bridge-automation/logs/claude-20260425T060335Z.stdout.log` documents a reconciliation-only pass caused by stale bridge state and missing INDEX alignment.
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-02-GLOSSARY-CLI-SCAN.md` documents repeated "parking marker" / parked-thread churn.
  - Live backlog state on 2026-06-02 shows 731 open `Route LO advisory:` work items and 807 open items with `project_name IS NULL`.
- Risk / impact:
  - The system spends model budget proving "nothing new happened."
  - Backlog triage cost compounds because advisory routing debt is not reduced structurally.

### Pattern 4 - Historical authority confusion was real.

- Evidence:
  - `independent-progress-assessments/bridge-automation/logs/codex-20260411T145509Z.stderr.log` shows automated work rooted at `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`.
  - `AGENTS.md` now explicitly forbids using `E:\Claude-Playground` as a live GT-KB root.
- Risk / impact:
  - Wrong-root work invalidates evidence and forces later reconciliation.

## What Is Already Addressed

### A. Claude zero-turn silent no-op detection is implemented.

- Evidence:
  - `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` now:
    - discovers the latest Claude binary dynamically,
    - injects `CLAUDE_CODE_OAUTH_TOKEN` from a local handoff file,
    - forces `--output-format json`,
    - rejects zero-API-duration no-op runs,
    - writes machine-readable scan status.
- Risk / impact:
  - The old silent-failure mode is materially reduced.
- Recommended action:
  - Do not add another generic "fix Claude no-ops" umbrella item. That class is already partially solved.

### B. Read-only backlog status scanning exists and is regression-tested.

- Evidence:
  - `platform_tests/scripts/test_cli_backlog_status.py` covers scanner-backed `gt backlog status` behavior, including read-only guarantees, orphan reporting, retire-ready output, and scanner caveats.
  - Recent history includes:
    - `2566d586 feat(cli): add \`gt backlog status\` read-only deterministic status report`
    - `aab07ff9 fix(backlog): repair status scanner coverage`
- Risk / impact:
  - The discoverability/status area is not a blind spot anymore.
- Recommended action:
  - Avoid proposing a duplicate generic "backlog status report" item.

### C. Some startup and terminology work is already backlog-owned.

- Evidence:
  - Active projects already include:
    - `PROJECT-GTKB-STARTUP-REFRACTOR-001`
    - `PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001`
    - `PROJECT-GTKB-COMMAND-SURFACE`
    - `PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS`
    - `PROJECT-GTKB-BRIDGE-RECONCILIATION`
    - `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- Risk / impact:
  - Creating duplicate umbrella projects would fragment ownership.
- Recommended action:
  - New recommendations should prefer adding focused work-items to these active homes unless a truly missing cross-cutting project is required.

## What Remains Under-Owned Or Uncaptured

### 1. Headless harness readiness is still not exposed as one deterministic operator surface.

- Evidence:
  - Current code improves token handoff and no-op detection, but live transcript evidence still shows failures surfacing as `401` and `429` run results rather than a prior readiness verdict.
  - SQLite scan on 2026-06-02 found no open work item explicitly targeting Claude/Codex headless auth/quota readiness, OAuth-token freshness, or bridge-harness capacity state.
- Risk / impact:
  - The mechanism improved, but the operator still learns about readiness by incurring failed scheduled work.
- Recommended action:
  - Add a focused backlog home for harness automation readiness.
- Decision needed from owner:
  - Should readiness expose only redacted pass/fail state, or also categorized reasons such as `auth_invalid`, `token_missing`, `quota_exhausted`, and `binary_noop`?

### 2. Parked/deferred bridge semantics are still convention, not protocol.

- Evidence:
  - The scan found transcript language around `parking marker`, parked work, and repeated no-op fires, but no open work item explicitly formalizing a canonical parked/deferred bridge status or slug-mute protocol.
  - SQLite pattern search on 2026-06-02 found no open work items for `slug mute`, `parking marker`, `parked`, or `deferred status`.
- Risk / impact:
  - The bridge keeps paying repeated scanning cost for work intentionally not ready to move.
- Recommended action:
  - Add a protocol-level work item under bridge reliability.
- Decision needed from owner:
  - Which long-term status vocabulary should be canonical: `DEFERRED`, `PARKED`, or a non-status mute/defer control?

### 3. Live authority resolution still lacks a direct deterministic surface.

- Evidence:
  - Historical wrong-root usage is now prohibited by contract, but the scan found no open work item explicitly for a live authority-resolution command or a doctor check dedicated to forbidden legacy-root references in active artifacts.
  - SQLite pattern search on 2026-06-02 found no open work items for `authority resolve` or `live authority`.
- Risk / impact:
  - The owner rule exists, but the fast operator question "what is authoritative right now?" still requires manual reasoning across docs and runtime state.
- Recommended action:
  - Add a deterministic authority-resolution item under source-of-truth freshness or command surface.
- Decision needed from owner:
  - Should forbidden legacy-root references hard-fail doctor/gates or start as warn-only?

### 4. LO advisory routing debt is clearly real, but the active advisory projects do not own concrete drain work.

- Evidence:
  - Live MemBase state on 2026-06-02:
    - 807 open items with `project_name IS NULL`
    - 731 open items with titles beginning `Route LO advisory:`
  - Active projects exist:
    - `PROJECT-GTKB-LO-ADVISORY-INTAKE`
    - `PROJECT-GTKB-LO-ADVISORY-ROUTING`
  - Querying open work items assigned to those project names returned no current open member items.
- Risk / impact:
  - The backlog already admits the problem but is not decomposed into executable drain work.
  - Advisory debt will continue to bury fresher findings.
- Recommended action:
  - Add concrete drain/aging/prioritization work items to the existing LO advisory projects rather than creating another umbrella.
- Decision needed from owner:
  - Whether old advisory-route items should be dispositioned by aging rules, topic clustering, or one-by-one Prime triage.

## Recommended Precedence

1. Add harness-readiness and authority-resolution items first.
2. Formalize parked/deferred bridge semantics next.
3. Add LO advisory backlog-drain work after the protocol/readiness surfaces exist.

Reason:
- Readiness and authority defects block or distort automation.
- Parked/deferred semantics reduce recurring no-op cost.
- Advisory drain work becomes cheaper once routing and defer semantics are explicit.

## Recommended Backlog Additions

### New Project Recommendation

#### Project: GTKB Harness Automation Readiness

- Why this should be a project:
  - The transcript evidence shows a distinct problem family not cleanly owned today: headless harness auth/quota/no-op readiness before bridge work starts.
  - Existing reliability and command-surface projects are broad; this needs a crisp operator-facing readiness contract.
- Suggested scope:
  - Deterministic readiness checks for Claude/Codex headless bridge automation.
  - Redacted auth/quota/no-op classification.
  - Operator-safe output for startup, doctor, and scheduled bridge automation.
- Decision needed from owner:
  - Approve or reject creating a dedicated project instead of burying this inside generic reliability work.

### Individual Work-Item Recommendations

#### WI Candidate 1

- Title:
  - `Add harness bridge-readiness doctor with auth/quota/no-op classification`
- Preferred home:
  - New project `GTKB Harness Automation Readiness`
- Why:
  - No current open WI explicitly owns this.

#### WI Candidate 2

- Title:
  - `Expose bridge-harness readiness in startup/status surfaces with redacted reason codes`
- Preferred home:
  - New project `GTKB Harness Automation Readiness`
- Why:
  - The mechanism exists, but the owner/operator surface does not.

#### WI Candidate 3

- Title:
  - `Formalize parked/deferred bridge semantics and slug-level mute controls`
- Preferred home:
  - `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- Why:
  - Transcript evidence shows repeated parked-work churn; no explicit open WI owns the semantics.

#### WI Candidate 4

- Title:
  - `Add live authority-resolution CLI and legacy-root detector for active GT-KB artifacts`
- Preferred home:
  - `PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS`
- Why:
  - Wrong-root history is real; current protection is rule-based more than operator-mechanical.

#### WI Candidate 5

- Title:
  - `Create executable drain plan for unprojected LO advisory routing backlog`
- Preferred home:
  - `PROJECT-GTKB-LO-ADVISORY-ROUTING`
- Why:
  - 731 open `Route LO advisory:` items and no concrete open drain WIs under the active advisory projects.

#### WI Candidate 6

- Title:
  - `Add aging and clustering policy for Route LO advisory backlog items`
- Preferred home:
  - `PROJECT-GTKB-LO-ADVISORY-INTAKE`
- Why:
  - The debt is too large for manual one-off routing to remain the default.

## Owner-Grilling Sequence

Per the owner-input protocol, approvals should be requested one project at a time after grilling on the specific tradeoff. Recommended order:

1. `GTKB Harness Automation Readiness`
2. parked/deferred bridge semantics work under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
3. LO advisory drain work under the existing LO advisory projects

## Bottom Line

Do not add duplicate broad projects for startup, bridge reconciliation, terminology, or generic reliability. Those already exist.

The real gaps from this Deep Scan are:

1. no deterministic harness-readiness project/home for auth/quota/no-op automation health,
2. no formal parked/deferred bridge semantics,
3. no direct authority-resolution surface,
4. no executable drain plan for the advisory-routing backlog pile.
