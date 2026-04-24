# Agent Red / GT-KB Fresh Session Startup

Generated: 2026-04-24T04:30:36Z

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Prime Builder
- Role assignment: active AI harness assigned by owner through durable operating-role record
- Bridge: always available through bridge/INDEX.md and checked at session startup
- Poller: activate only when Prime Builder and Loyal Opposition run in separate harnesses or asynchronous monitoring is needed
- Role mapping source: .claude/rules/operating-role.md

- Strict GOV enforcement where mechanically available
- Formal artifact approval required for DA, GOV, SPEC, PB, ADR, and DCL mutations
- Standing backlog is the governed cross-session work authority
- GT-KB adoption and release-readiness evidence remain release-gate visible
- Harness hook limitations require parity checks and explicit fallback disclosure

### Live Project Dashboard

- Dashboard: Agent Red Project Dashboard: [http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard](http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard)
- Browser opening: use the harness-controlled browser for live dashboard inspection; startup open request: enabled; current mode: `harness_browser`. Startup hooks must not launch the operating system default browser unless explicitly configured with `dashboard_open_mode: system_default_browser`.
- KPI coverage: Agent Red backlog, MemBase work items, Deliberation Archive records, tests, specifications, drift, regression, contention, and tokens consumed at session start before user input.
- Dashboard scope: Agent Red product/project dashboard.
- Token measurement status: not_exposed_by_current_harness
- Tokens consumed before user input: unavailable

### Current Project State

- Release blockers: 0
- Active backlog items: 1
- Open MemBase work items: 29
- Dashboard-scoped bridge/contention entries, non-authoritative for queue state: 1
- Drift changed paths: 8
- Testing/tool rollup: 0 failing, 6 manual, 16 ready/passing
- GT-KB infrastructure posture: package 0.6.1; dry-run upgrade plan available: True

### Active Work Subject

- Default work subject: Application Focus
- Current work subject: Application Focus
- Application label: Agent Red
- Application work subject means owner direction is interpreted as work on the unique application being built with GroundTruth-KB.
- GT-KB Infrastructure work subject is active only when explicitly declared.
- Application work subject commands: `work subject application`, `application mode`, `app mode`, `agent red mode`.
- GT-KB work subject commands: `work subject GT-KB`, `GT-KB mode`, `GT-KB infrastructure mode`, `GroundTruth-KB mode`.
- Canonical state file: `.claude/session/work-subject.json` (legacy `.claude/hooks/.workstream-focus-state.json` migrated on next owner command).

### Session Overlay Status (Non-Authoritative)

- Overlay root: `.groundtruth/session/overlays` (ignored by git, non-authoritative by construction).
- Overlays are copy-only context; canonical state lives in the KB, MemBase, Deliberation Archive, and source files.
- Current overlay: none active; startup context read directly from live files.
- no current session overlay; startup context is sourced from live files

### Fresh-Session Input Semantics

- The first owner message in a fresh session is a session-start stimulus only; do not interpret it as a focus choice, task prompt, approval, answer, or other informational input.
- After presenting this startup disclosure and the session-focus choices, wait for Mike's next message before choosing or mapping session work.

### Wrap-Up Trigger Commands

- Wrap-up trigger: use one of the documented commands as a standalone message.
- Accepted wrap-up commands: `wrap up`, `wrap up this session`, `session wrap-up`, `run session wrap-up`, `close this session`, `end this session`, `new session`, `fresh session`, `start a new session`, `start a fresh session`, `begin a new session`, `begin a fresh session`, `open a new session`, `prepare a new session`, `initialize a new session`, `start fresh`, `begin fresh`.
- Optional leading or trailing `please` and final punctuation are accepted.

## Choose This Session's Focus

Reply with the number or exact label. Each option is generated from the current dashboard evidence.

1. **Optimize Startup Token Consumption**
   Current signal: 2 startup reduction candidate(s) are currently visible.
   Prompt details: Focus this session on reducing startup token consumption. Review the startup-loaded artifacts, prefer dashboard and index-first reads, and trim default startup context to the minimum evidence needed. Use this reduction set: Use the dashboard link before loading large artifacts into context; Read indices and summaries first; open full artifacts only when needed; Load only the specific skill body required for the current turn; Use cached startup snapshots for stable KPI instead of re-scanning everything; Propose explicit governance relaxation only when the audit trail can preserve the tradeoff.

2. **Top Priority Actions**
   Current signal: The standing backlog already identifies the visible highest-priority governed actions for this session, and the file bridge scan shows 0 latest NEW/REVISED entries.
   Prompt details: Focus this session on the established top priority actions. Current priorities: GTKB-GOV-010: Maintain standing backlog harvest audit as release-gate input. Start with GTKB-GOV-010: Maintain standing backlog harvest audit as release-gate input; explain the current evidence, immediate next command, and expected verification.

3. **Resolve Release Blockers**
   Current signal: 0 release blocker(s) are visible in the dashboard.
   Prompt details: Focus this session on clearing release blockers. Start with run the release gate and confirm no blocker evidence is stale. Verify the result with scripts/release_candidate_gate.py and update governed evidence.

4. **Repair Testing/Tool Integrations**
   Current signal: 0 failing and 2 unknown integration(s) are visible.
   Prompt details: Focus this session on restoring testing service/tool integration health. Start with Chromatic: Verify `CHROMATIC_PROJECT_TOKEN`, inspect the Chromatic build for visual diffs or build errors, accept intentional baselines or fix regressions, then rerun Chromatic. Preserve GT-KB as infrastructure evidence.

5. **Remediate Known Risks**
   Current signal: 2 active risk(s) are summarized from release, integration, GT-KB, and drift signals.
   Prompt details: Focus this session on the dashboard risk register. Start with GT-KB scaffold drift; recommended action: Review `gt project upgrade --dry-run` and apply only after owner approval.

6. **Clear Stage/Test Release Path**
   Current signal: Release readiness, regression, integration, and staging evidence should converge before stakeholder release.
   Prompt details: Prepare for release by clearing the path to stage and test. Confirm release blockers, required checks, tool integrations, staging readiness, and evidence freshness before recommending a release decision.

7. **Clean For Internal Review**
   Current signal: 8 changed path(s) are visible in dashboard drift.
   Prompt details: Clean and tidy for internal review. Inventory changed paths, separate unrelated work, run focused checks, and prepare a concise review handoff without modifying formal artifacts unless explicitly approved.

8. **Pick From Standing Backlog**
   Current signal: Standing backlog remains the governed cross-session work authority.
   Prompt details: Choose work from the standing backlog. Start with GTKB-GOV-010: Maintain standing backlog harvest audit as release-gate input; restate the governing evidence, required approvals, implementation scope, and verification plan.

9. **Commit and push to GitHub**
   Current signal: Local changes can be packaged into an evidence-backed GitHub update when the working tree is ready.
   Prompt details: Prepare a scoped commit and push it to GitHub. Inventory changed paths, separate unrelated work, run focused verification, commit only the intended scope, push the branch, and report the resulting GitHub evidence.

10. **Merge to main, build and push to the staging environment**
   Current signal: A reviewed GitHub branch can advance into the staging release lane after required checks and approvals are green.
   Prompt details: Merge the reviewed branch to main, build the release artifact, and push it to the staging environment. Confirm required GitHub checks, release-gate evidence, branch provenance, build output, and staging deployment status.

11. **Execute end-to-end tests in the staging environment**
   Current signal: Staging must prove the candidate through live end-to-end coverage before production promotion.
   Prompt details: Execute the staging end-to-end test plan. Verify environment health, run the governed E2E suites against staging, capture failures with evidence, and update release-readiness records with the staging result.

12. **Push staged-and-tested build to production, then smoke test**
   Current signal: Production promotion is only available after the staged build has passed required gates and owner approval is recorded.
   Prompt details: Promote the staged-and-tested build to production, then run production smoke tests. Confirm explicit production approval, artifact provenance, deployment status, smoke-test evidence, rollback readiness, and release records.

13. **Continue Last Session**
   Current signal: The action center and 2 latest GO/NO-GO bridge responses define the current-session continuation scope.
   Prompt details: Continue from the last session using the dashboard action center and any latest GO/NO-GO bridge responses, including responses produced by a prior Loyal Opposition session. Start by inventorying the latest GO/NO-GO bridge entries, then continue with Review GT-KB scaffold upgrade plan; explain current evidence, next command, and expected verification.

Or provide a prompt for something else.