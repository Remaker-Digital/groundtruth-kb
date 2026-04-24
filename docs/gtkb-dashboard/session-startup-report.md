# Agent Red / GT-KB Fresh Session Startup

Generated: 2026-04-24T05:24:35Z

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Loyal Opposition
- Role assignment: active AI harness assigned by owner for counterpart review
- Bridge: always available through bridge/INDEX.md and checked at session startup
- Poller: activate only when Prime Builder and Loyal Opposition run in separate harnesses or asynchronous monitoring is needed
- Role mapping source: C:\Users\micha\.codex\agent-red-hooks\operating-role.md

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

## Loyal Opposition Startup Task

- Startup mode: Loyal Opposition review and verification.
- Default session purpose: process Prime Builder reviews and verifications on the file bridge.
- Session-focus menu: not presented in Loyal Opposition mode; numbered focus choices are Prime Builder startup controls.
- Bridge/poller distinction: the file bridge is the durable role handoff and review mechanism; the poller is only a monitoring/activation service.
- Bridge startup rule: check the file bridge in both Prime Builder and Loyal Opposition startup.
- Live bridge authority: current bridge state must be determined only from a fresh read of live `bridge/INDEX.md`; this generated report is not authoritative after generation.
- Mandatory direct-read rule: before reporting the live bridge scan count, read `bridge/INDEX.md` directly; do not derive bridge state from startup reports, dashboard JSON, cached documents, copied excerpts, summary counts, or hook-generated summaries.
- Startup execution rule: execute live bridge verification before using this section in owner-facing chat; do not display this checklist as a substitute for performing the verification.
- Poller startup rule: activate a poller only when the roles are running in separate harnesses or asynchronous monitoring is otherwise needed.
- First task: verify that the Prime Builder / Loyal Opposition file bridge is functioning.
- Generated-time file bridge scan, non-authoritative after report generation: 1 latest NEW/REVISED entry identified.
- If the live bridge verification succeeds, report the live scan result and ask Mike whether to begin processing reviews and verifications from `bridge/INDEX.md`.
- Expected owner reply: `yes` to begin processing the bridge queue, or `no` / a custom instruction to stay in advisory mode.
- If the bridge is not functioning, diagnose and repair the bridge before ordinary review work.
- Bridge authority: Loyal Opposition has permanent owner permission to diagnose and repair bridge function/use and downstream bridge-dependent artifacts needed to sustain the bridge.