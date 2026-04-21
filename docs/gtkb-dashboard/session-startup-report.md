# Agent Red / GT-KB Fresh Session Startup

Generated: 2026-04-21T06:30:36Z

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Prime Builder
- Role assignment: active AI harness assigned by owner until further notice
- Bridge: available when the owner requests counterpart review through bridge/INDEX.md
- Role mapping source: .claude/rules/prime-builder-role.md

- Strict GOV enforcement where mechanically available
- Formal artifact approval required for DA, GOV, SPEC, PB, ADR, and DCL mutations
- Standing backlog is the governed cross-session work authority
- GT-KB adoption and release-readiness evidence remain release-gate visible
- Harness hook limitations require parity checks and explicit fallback disclosure

### Live Project Dashboard

- Dashboard: [Agent Red Project Dashboard](file:///E:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/docs/gtkb-dashboard/index.html)
- KPI coverage: Agent Red backlog, MemBase work items, Deliberation Archive records, tests, specifications, drift, regression, contention, and tokens consumed at session start before user input.
- Dashboard scope: Agent Red product/project dashboard. GT-KB is treated as pre-existing implementation infrastructure and is excluded from primary product KPIs.
- Token measurement status: not_exposed_by_current_harness
- Tokens consumed before user input: unavailable

### Current Project State

- Release blockers: 7
- Active backlog items: 3
- Open MemBase work items: 29
- Actionable bridge/contention entries: 0
- Drift changed paths: 1
- Testing/tool rollup: 7 failing, 6 manual, 16 ready/passing
- GT-KB infrastructure posture: package 0.6.1; dry-run upgrade plan available: True

### Wrap-Up Trigger Commands

- Wrap-up trigger: use one of the documented commands as a standalone message.
- Accepted wrap-up commands: `wrap up`, `wrap up this session`, `session wrap-up`, `run session wrap-up`, `close this session`, `end this session`, `new session`, `fresh session`, `start a new session`, `start a fresh session`, `begin a new session`, `begin a fresh session`, `open a new session`, `prepare a new session`, `initialize a new session`, `start fresh`, `begin fresh`.
- Optional leading or trailing `please` and final punctuation are accepted.

## Choose This Session's Focus

Reply with the number or exact label. Each option is generated from the current dashboard evidence.

1. **Optimize Startup Token Consumption**
   Current signal: 1 startup reduction candidate(s) are currently visible.
   Prompt details: Focus this session on reducing startup token consumption. Review the startup-loaded artifacts, prefer dashboard and index-first reads, and trim default startup context to the minimum evidence needed. Use this reduction set: Use the dashboard link before loading large artifacts into context; Read indices and summaries first; open full artifacts only when needed; Load only the specific skill body required for the current turn; Use cached startup snapshots for stable KPI instead of re-scanning everything; Propose explicit governance relaxation only when the audit trail can preserve the tradeoff.

2. **Top Priority Actions**
   Current signal: The standing backlog already identifies the three highest-priority governed actions for this session, and the file bridge scan shows 0 latest NEW/REVISED entries.
   Prompt details: Focus this session on the established top priority actions. Current priorities: GTKB-GOV-006: Close Agent Red release-readiness blocker list; GTKB-GOV-007: Revise commercial readiness NO-GO tracks for SPEC-1831, SPEC-1832, and SPEC-1833; GTKB-GOV-010: Maintain standing backlog harvest audit as release-gate input. Start with GTKB-GOV-006: Close Agent Red release-readiness blocker list; explain the current evidence, immediate next command, and expected verification.

3. **Resolve Release Blockers**
   Current signal: 7 release blocker(s) are visible in the dashboard.
   Prompt details: Focus this session on clearing release blockers. Start with Production credentials exposed in the deleted generated manifest must be rotated. Verify the result with scripts/release_candidate_gate.py and update governed evidence.

4. **Repair Testing/Tool Integrations**
   Current signal: 7 failing and 1 unknown integration(s) are visible.
   Prompt details: Focus this session on restoring testing service/tool integration health. Start with GitHub Actions: Open the latest failing required workflow runs, fix the child gate rows they identify, then rerun the failed workflows from GitHub Actions. Preserve GT-KB as infrastructure evidence.

5. **Remediate Known Risks**
   Current signal: 4 active risk(s) are summarized from release, integration, GT-KB, and drift signals.
   Prompt details: Focus this session on the dashboard risk register. Start with Production GO is blocked; recommended action: Close, defer, or supersede every blocker with governed evidence.

6. **Clear Stage/Test Release Path**
   Current signal: Release readiness, regression, integration, and staging evidence should converge before stakeholder release.
   Prompt details: Prepare for release by clearing the path to stage and test. Confirm release blockers, required checks, tool integrations, staging readiness, and evidence freshness before recommending a release decision.

7. **Continue Last Session**
   Current signal: The action center identifies the most immediate current-session continuation point.
   Prompt details: Continue from the last session using the dashboard action center. Start with Repair GitHub Actions; explain current evidence, next command, and expected verification.

8. **Clean For Internal Review**
   Current signal: 1 changed path(s) are visible in dashboard drift.
   Prompt details: Clean and tidy for internal review. Inventory changed paths, separate unrelated work, run focused checks, and prepare a concise review handoff without modifying formal artifacts unless explicitly approved.

9. **Pick From Standing Backlog**
   Current signal: Standing backlog remains the governed cross-session work authority.
   Prompt details: Choose work from the standing backlog. Start with GTKB-GOV-006: Close Agent Red release-readiness blocker list; restate the governing evidence, required approvals, implementation scope, and verification plan.

Or provide a prompt for something else.