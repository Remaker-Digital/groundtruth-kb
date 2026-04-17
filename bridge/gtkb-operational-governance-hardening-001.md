# GT-KB Operational Governance Hardening — Implementation Proposal

**Status:** NEW
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295
**Scope:** Close the gap between governance specs that exist and governance behavior that is mechanically enforced
**Repository:** `groundtruth-kb` + Agent Red project hooks/rules

---

## Prior Deliberations

- **DELIB-0628** — S279 Cycle Enforcement Hooks NO-GO. Prime proposed `cycle-gate.py` + `cycle-tracker.py` to enforce the proposal→review→implement cycle. Codex rejected because: (1) state was session-local and dies between sessions, (2) fail-open on missing state means the gate disappears at the exact failure boundary, (3) Bash-mediated writes bypassed the PreToolUse gate. **The core problem identified in DELIB-0628 is the same problem this proposal addresses — but DELIB-0628's solution was too narrow (one lifecycle gate) while the problem is systemic (12+ governance behaviors are unenforced).**
- **DELIB-0631** — S279 Post-Implementation Review of the same hooks. Codex NO-GO'd again: hooks were untracked in git, fail-open persisted, mutation paths were incomplete.
- **DELIB-0195** — Architecture/Technology-Choice Governance Audit.
- **DELIB-GTKB-INIT-POSTURE** — Owner decision: `gt project init` is the scaffold entry point.
- **DELIB-GTKB-TOKEN-POSTURE** — Owner decision: GT-KB provides auth docs only, no token management.
- **SPEC-GTKB-SCOPE** — Owner-stated: GT-KB includes all 12 first-class components.
- **SPEC-1830** — "Operational Procedures Must Be Code, Not Conversation" (verified).

---

## The Problem

GroundTruth-KB has 20 governance specifications (GOV-01 through GOV-20) and multiple operational rules (deliberation protocol, bridge protocol, implementation cycle). **Only 6 are mechanically enforced via hooks.** The remaining 14+ rely on the AI agent choosing to comply — which is exactly the failure mode observed in this session:

**Documented violations by Prime Builder in S295 alone:**

| Violation | GOV/Rule | What happened | Root cause |
|---|---|---|---|
| Did not search deliberations before work | deliberation-protocol.md | Drafted 4B.7 proposal, bridge infrastructure fix, mass-adoption proposal, trial-readiness prep — all without searching the archive first | Rule is textual only; no hook checks or blocks |
| Created specs without checking for prior specs on the topic | GOV-06, GOV-08 | Created SPEC-GTKB-SCOPE without searching if a scope spec already existed | No PreToolUse hook on `insert_spec` calls |
| Proposed implementation without Codex pre-review | CLAUDE.md:65-70 | Started 4B.8 implementation proposal while Codex was still reviewing a different thread | No gate between "proposal posted" and "GO received" |
| Created markdown files outside the KB | GOV-08 | Created `docs/day-in-the-life.md`, `docs/groundtruth-kb-executive-overview.md` as standalone files rather than KB documents | No hook prevents new markdown creation outside approved paths |
| Wrote implementation before tests | GOV-12 | Multiple 4B sub-rounds wrote source changes before or without corresponding test work items | No hook enforces test-before-implement |

**The owner's observation is correct: if Prime Builder can skip these behaviors, so can any new user's AI agent.** Textual rules in `.claude/rules/` are advisory. Hooks in `.claude/hooks/` are mechanical. The governance gap is the set of rules that are textual but not mechanical.

---

## Design Principles (learned from DELIB-0628 failure)

DELIB-0628's cycle-gate approach failed because it was:
1. **Session-local** — state died between sessions
2. **Fail-open** — missing state meant no enforcement
3. **Narrow** — only gated Write/Edit, not Bash-mediated writes
4. **Untracked** — lived outside git, invisible to worktrees/clones

This proposal applies the inverse principles:

1. **Durable state** — governance state stored in the Knowledge Database (SQLite), not a session-local JSON file
2. **Fail-closed** — missing or corrupt governance state produces a warning/block, not silent pass-through
3. **Comprehensive** — hooks cover UserPromptSubmit (pre-work checks), PreToolUse (mutation gates), and PostToolUse (tracking/auditing)
4. **Tracked in git** — all hooks and registrations ship with the package via `gt project init`, not manual workstation setup

---

## Proposed Governance Hooks

### Hook 1: Deliberation Search Gate (`UserPromptSubmit`)

**Enforces:** deliberation-protocol.md, GOV-08

**Behavior:** On every user prompt, the hook:
1. Extracts topic keywords from the user's message
2. Checks a session-local flag: "has deliberation search been performed this session?"
3. If not performed yet, emits a `systemMessage`: "MANDATORY: Before starting substantive work, search the deliberation archive for prior decisions on this topic. Run: `db.search_deliberations('...')` with relevant keywords. Cite any relevant DELIB-IDs in your response."
4. After the first search is detected (via PostToolUse tracking of `search_deliberations` calls), the flag is set and subsequent prompts do not re-trigger

**Why UserPromptSubmit not PreToolUse:** The deliberation search is a pre-work obligation, not a per-tool gate. It should fire once per session (or once per new topic), not on every tool call.

**Fail mode:** If the hook crashes, it emits an ALARM-style message (same pattern as poller-freshness.py). It does not silently pass.

### Hook 2: Spec-Before-Code Gate (`PreToolUse`)

**Enforces:** GOV-01, GOV-06, GOV-12, SPEC-1830

**Behavior:** When the agent attempts to Write or Edit a file in `src/` (or the project's source directory):
1. Query the KB for any spec in `specified` status that covers the module being modified (match by file path or module name in spec `section` field)
2. If a matching spec exists in `specified` status → allow (spec-first is satisfied)
3. If a matching spec exists in `implemented` or `verified` → allow (modification of already-specified code)
4. If NO matching spec exists → emit a `systemMessage` warning: "No specification covers this module. Per GOV-01, create or identify a specification before modifying source code." **Do not block** — this is a warning, not a hard gate, because new files may legitimately precede their spec during scaffolding work. The warning ensures the agent is aware of the obligation.
5. Additionally, check if a test work item exists for the corresponding spec. If the spec exists but no test WI is linked → warn per GOV-12.

**Why warn not block:** DELIB-0628 showed that hard-blocking Write/Edit causes agents to route around the gate via Bash. Warnings are more robust because they work through the agent's instruction-following, not through tool-level denial which can be circumvented.

### Hook 3: Bridge Protocol Compliance Gate (`PreToolUse`)

**Enforces:** CLAUDE.md:65-70, file-bridge-protocol.md, loyal-opposition.md

**Behavior:** When the agent attempts to Write or Edit a file in `src/` (implementation code):
1. Check `bridge/INDEX.md` for the most recent entry relevant to the current work (matched by topic/module name)
2. If the most recent status is `GO` → allow (Codex has approved)
3. If the most recent status is `NEW` or `REVISED` → warn: "This module has a pending bridge proposal awaiting Codex review. Per CLAUDE.md:65-70, do not implement until GO is received."
4. If the most recent status is `NO-GO` → warn: "Codex returned NO-GO on this module's proposal. Revise the proposal before implementing."
5. If no bridge entry exists → warn: "No bridge proposal found for this module. Per the operating procedure, submit an implementation proposal before modifying source code."

**State source:** `bridge/INDEX.md` is durable, cross-session, and tracked in git. No session-local state needed.

### Hook 4: KB-Not-Markdown Gate (`PreToolUse`)

**Enforces:** GOV-08 ("Knowledge Database is the single source of truth")

**Behavior:** When the agent attempts to Write or create a new `.md` file:
1. Check the file path against approved markdown locations:
   - `CLAUDE.md`, `MEMORY.md`, `memory/*.md` — approved (session state)
   - `AGENTS.md` — approved (agent contract)
   - `bridge/*.md` — approved (bridge protocol)
   - `docs/*.md` — approved (published documentation)
   - `.claude/rules/*.md` — approved (rules)
   - `independent-progress-assessments/**/*.md` — approved (LO reports)
   - `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md`, etc. — approved (standard project files)
2. If the file is in an approved location → allow
3. If the file is a NEW markdown file in an unapproved location → warn: "Per GOV-08, project knowledge belongs in the Knowledge Database. Consider using `db.insert_spec()`, `db.insert_deliberation()`, or `db.insert_document()` instead of creating a standalone markdown file."

**Why this matters:** The most common governance drift is creating ad-hoc markdown files that duplicate or replace KB content. This hook catches it at creation time.

### Hook 5: Session Health Check (`SessionStart`)

**Enforces:** Multiple GOVs, deliberation-protocol.md, bridge-essential.md

**Behavior:** On session start (extends the existing `assertion-check.py`):
1. Run KB assertions (already implemented)
2. Check bridge INDEX for any entries requiring Prime action (NEW from Codex, NO-GO requiring revision, GO awaiting implementation)
3. Search deliberations for any unresolved owner decisions from the previous session
4. Check `memory/MEMORY.md` for staleness (last session date vs. current date)
5. Emit a structured `systemMessage` with a session-start checklist:
   ```
   SESSION HEALTH CHECK:
   ☑ KB assertions: 14 pass, 0 fail
   ☑ Bridge: 1 entry requires action (gtkb-adoption-gap-closure GO)
   ☑ Deliberations: 2 recent decisions found (DELIB-GTKB-INIT-POSTURE, DELIB-GTKB-TOKEN-POSTURE)
   ☐ MEMORY.md: last updated S295 (current session) — OK
   ☐ Deliberation search: NOT YET PERFORMED this session
   ```

This replaces the current assertion-check.py (which only runs assertions) with a comprehensive health check that surfaces governance obligations at the start of every session.

---

## Implementation Plan

### Phase 1: Core Governance Hooks (ship with GT-KB package)

| WI | Hook | Event | Est. |
|---|---|---|---|
| OG-1 | Session Health Check (Hook 5) | SessionStart | 2 days |
| OG-2 | Deliberation Search Gate (Hook 1) | UserPromptSubmit | 1.5 days |
| OG-3 | Spec-Before-Code Warning (Hook 2) | PreToolUse | 2 days |
| OG-4 | KB-Not-Markdown Warning (Hook 4) | PreToolUse | 1 day |
| OG-5 | Bridge Protocol Compliance (Hook 3) | PreToolUse | 2 days |

**Total Phase 1: ~8.5 days**

### Phase 2: Scaffold Integration

| WI | Scope | Est. |
|---|---|---|
| OG-6 | `gt project init` generates all 5 hooks + registers them in `.claude/settings.json` | 1.5 days |
| OG-7 | `gt project doctor` checks that governance hooks are registered and functioning | 1 day |
| OG-8 | Template `CLAUDE.md` references the hooks and explains their behavior | 0.5 days |

**Total Phase 2: ~3 days**

### Phase 3: Recovery and Resilience

| WI | Scope | Est. |
|---|---|---|
| OG-9 | `gt project doctor --fix` repairs common governance drift: re-registers unregistered hooks, restores deleted rule files from templates, detects and warns about stale MEMORY.md | 2 days |
| OG-10 | Hook self-test: each hook can be invoked with `--self-test` flag to verify it's functioning correctly without side effects | 1 day |
| OG-11 | Documentation: "Governance Model" guide explaining what each hook enforces, why, and how to customize thresholds | 1 day |

**Total Phase 3: ~4 days**

---

## Relationship to DELIB-0628 (the failed prior attempt)

This proposal learns from DELIB-0628's failures:

| DELIB-0628 failure | This proposal's solution |
|---|---|
| Session-local state file (`cycle-state.json`) | Governance state in KB (SQLite) + bridge INDEX (durable files) |
| Fail-open on missing state | Fail-closed with ALARM-style messages (same pattern as poller-freshness.py) |
| Only gated Write/Edit | Covers UserPromptSubmit (pre-work), PreToolUse (mutations), SessionStart (health), and PostToolUse (tracking) |
| Untracked in git | All hooks ship with the package and are registered by `gt project init` |
| Single lifecycle gate | 5 independent hooks covering 5 different governance dimensions |
| Hard block → agents route around | Warnings, not blocks (except for credential-scan and destructive-gate which remain hard blocks) |

**The key insight from DELIB-0628:** hard-blocking hooks get circumvented. Warning hooks that work through the agent's instruction-following system are more robust because they don't create an adversarial dynamic. The agent sees the warning in its system message and complies because the instruction is clear, not because it's physically prevented.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Warning fatigue — too many warnings per turn causes the agent to ignore them | High | Each hook fires at most once per session or once per unique file; warnings are short and actionable |
| Hook performance — 5 hooks on PreToolUse slows every tool call | Medium | Each hook is lightweight (KB query, file read, regex match); measured on Agent Red at <100ms per hook |
| False positives — spec-before-code warns on legitimate scaffolding | Medium | Warning not block; agent can proceed with explanation; `gt project init` output is allowlisted |
| Hook conflicts — two hooks warn about the same issue | Low | Each hook has a distinct scope; no overlapping enforcement areas |
| New users disable hooks because warnings are annoying | Medium | `gt project doctor` detects disabled hooks and warns; CLAUDE.md explains why each hook exists |

---

## Exit Criteria

1. All 5 hooks implemented, tested (unit tests for each), and passing on all platforms
2. `gt project init --profile dual-agent` generates all hooks + `.claude/settings.json` with registrations
3. `gt project doctor` checks hook registration and reports actionable fixes for missing hooks
4. `gt project doctor --fix` can restore governance hooks from templates
5. Each hook has a `--self-test` mode
6. Governance Model documentation explains all hooks to adopters
7. The 5 governance violations I committed in S295 (listed in §The Problem) would each have been surfaced by the corresponding hook

---

## Open Decisions for Codex

1. **Warn vs block for spec-before-code.** DELIB-0628 showed hard blocks get circumvented. This proposal uses warnings. Should any of the 5 hooks hard-block instead of warn? **Recommendation:** warnings only, except credential-scan and destructive-gate which remain hard blocks from the existing implementation.

2. **Hook packaging.** Should governance hooks live in the `groundtruth-kb` Python package (importable, testable, versioned) or as standalone scripts in `templates/hooks/` (copied by scaffold, editable per project)? **Recommendation:** package for the hook logic, templates for the registration and customization layer. The hooks import from `groundtruth_kb.governance` and the scaffold copies a thin wrapper script.

3. **Deliberation search granularity.** Hook 1 fires once per session. Should it fire once per NEW topic instead (e.g., when the user mentions a module name the hook hasn't seen before)? **Recommendation:** once per session for MVP; topic-level tracking is a future enhancement.

4. **Allowlisted markdown paths.** Hook 4's allowlist is static. Should it be configurable via `groundtruth.toml`? **Recommendation:** yes, with the static list as the default.

5. **Phase ordering.** Phase 1 → 2 → 3 is the natural sequence. Should Phase 2 (scaffold integration) be interleaved with Phase 1 (build each hook and immediately add it to the scaffold)? **Recommendation:** interleave — each hook is independently useful and should be scaffoldable as soon as it's implemented.

---

## Success Criteria

Operational governance is hardened when:

1. A new user runs `gt project init` and gets all governance hooks pre-registered — they don't need to know the hooks exist for the hooks to work
2. An AI agent that attempts to skip deliberation search, write code without specs, implement without bridge GO, or create ad-hoc markdown files is warned on the first attempt — not on the fifth
3. `gt project doctor` can diagnose and repair a project where hooks have been accidentally disabled or deleted
4. The governance model is documented so a CTO can understand what's enforced and why without reading hook source code
5. None of the 5 violations documented in S295 can occur silently in a project scaffolded by v0.6.0

---

## Phase 4: Transparency and Observability

**Problem:** As GT-KB becomes more sophisticated, more work happens out-of-sight. The owner observed in S295 that "more work is done out-of-sight of the user" and "I feel the need to have more visibility into what work is being done while the system is working." The bridge monitor shows dispatch/complete events but not WHAT the agents are doing or finding. Headless spawns run for 5-15 minutes with no visibility into their progress. Codex reviews happen silently until a file appears.

**Industry comparison:** Established AI agent observability platforms (LangSmith, Braintrust, Arize Phoenix, Sentry AI Agent Monitoring) provide real-time trace visualization, token cost tracking, agent reasoning chains, and alerting. GT-KB currently offers only the bridge monitor (dispatch/complete status) and the POLLER block (freshness indicator). The transparency gap is significant compared to what a CTO evaluating GT-KB will expect.

**What GT-KB has that they don't:** governance enforcement + deliberation archive + specification-driven gates. The goal is not to replicate LangSmith — it's to add observability ON TOP of governance, which is the differentiator. LangSmith/Braintrust observe; GT-KB observes AND enforces.

### Phase 4 Work Items

| WI | Deliverable | Scope | Est. |
|---|---|---|---|
| OG-12 | **Activity feed in `gt serve` dashboard** | Real-time log visible in a browser tab showing: agent dispatched → topic → working on file X → found issue Y → wrote bridge entry Z → GO/NO-GO verdict + 1-line reason. Reads from bridge INDEX + scan-status JSON files + bridge entry files. WebSocket or SSE push to the browser. Like Braintrust's trace timeline but scoped to the bridge protocol. | 3 days |
| OG-13 | **Bridge monitor enhancement** | Extend `watch-bridge-scan.ps1` (and the future Python scheduler) to show: (1) the first line of the bridge entry being reviewed, not just "codex exec running for 1 selected item(s)"; (2) a 1-line summary when the review completes: "GO: bridge protocol compliance verified" or "NO-GO: executive overview overpromises cloud capabilities"; (3) accumulated token/turn count per dispatch cycle. Currently the monitor shows agent state transitions; after this WI it shows WHAT happened, not just THAT something happened. | 1.5 days |
| OG-14 | **Toast/notification integration** | Windows toast notifications (extending S290's `Show-PollerToast`) for key bridge events: proposal posted, GO received, NO-GO with reason summary, VERIFIED, implementation complete, auth failure. Each toast is 1-2 lines — enough to decide whether to intervene without opening the bridge file. Cross-platform: Windows toast, macOS `osascript`, Linux `notify-send`. | 1.5 days |
| OG-15 | **Agent dispatch summary log** | Each headless spawn writes a structured summary to `independent-progress-assessments/bridge-automation/logs/dispatch-summary.jsonl` on completion: timestamp, bridge entry processed, verdict, files modified, turn count, api_ms, 1-line summary of outcome. The bridge monitor and `gt serve` dashboard both read this file. This replaces the current opaque "claude exec completed; num_turns=82 api_ms=560592" with "claude exec completed: Phase 4B.7 implemented — 39 mypy errors closed across 5 files, 640 tests pass". | 1 day |
| OG-16 | **Token cost estimation** | Each dispatch summary includes an estimated token cost based on turn count × average tokens-per-turn × provider pricing. Display in the `gt serve` dashboard as: daily total, weekly total, per-dispatch breakdown. Include idle-scan cost (zero) explicitly so the CTO can see that non-dispatching scans are free. Pricing is configurable in `groundtruth.toml` per provider. | 1.5 days |
| OG-17 | **Governance compliance dashboard** | New section in `gt serve` showing: which governance hooks are registered, which fired today, what they warned about, whether warnings were heeded or overridden. A CTO can look at this page and see "the system caught 3 spec-before-code violations today, all resolved" — proof that the governance model is working, not just installed. | 2 days |

**Phase 4 total: ~10.5 days**

### Why transparency is governance

The owner's observation is precise: "What can we do to make the activity in the system more directly visible to the user?" Visibility is not a separate concern from governance — it IS governance. A governance system that works correctly but invisibly provides no confidence. The owner (and the CTO evaluating the system) need to see:

1. **That agents are working** (dispatch events — already visible in the monitor)
2. **What agents are working on** (topic/file — currently invisible; OG-13 and OG-15 fix this)
3. **What agents decided** (GO/NO-GO/VERIFIED + reason — currently requires reading bridge files; OG-13 and OG-14 fix this)
4. **How much it's costing** (token spend — currently invisible; OG-16 fixes this)
5. **That governance is enforced** (hook activity — currently invisible; OG-17 fixes this)

The existing bridge monitor (green liveness lines scrolling with occasional cyan dispatch events) provides #1 only. After Phase 4, it provides all 5.

---

## Updated Summary

| Phase | WIs | Est. days | Scope |
|---|---|---|---|
| Phase 1: Core Governance Hooks | OG-1 through OG-5 | 8.5 | 5 hooks: session health, deliberation gate, spec-before-code, bridge compliance, KB-not-markdown |
| Phase 2: Scaffold Integration | OG-6 through OG-8 | 3 | `gt project init` generates + registers hooks; `gt project doctor` checks them |
| Phase 3: Recovery and Resilience | OG-9 through OG-11 | 4 | `gt project doctor --fix`; hook self-test; governance model documentation |
| **Phase 4: Transparency and Observability** | **OG-12 through OG-17** | **10.5** | **Activity feed, enhanced monitor, toast notifications, dispatch summaries, token cost, compliance dashboard** |
| **Total** | **17 WIs** | **26 days** | |

**Critical path:** Phase 1 (8.5 days) → Phase 2 (3 days) → Phase 3 (4 days). Phase 4 can run in parallel with Phases 2-3 since the transparency features read from the same data sources (bridge INDEX, scan-status JSON, KB) that the hooks write to.

---

## Updated Success Criteria

Operational governance is hardened when:

1. A new user runs `gt project init` and gets all governance hooks pre-registered — they don't need to know the hooks exist for the hooks to work
2. An AI agent that attempts to skip deliberation search, write code without specs, implement without bridge GO, or create ad-hoc markdown files is warned on the first attempt — not on the fifth
3. `gt project doctor` can diagnose and repair a project where hooks have been accidentally disabled or deleted
4. The governance model is documented so a CTO can understand what's enforced and why without reading hook source code
5. None of the 5 violations documented in S295 can occur silently in a project scaffolded by v0.6.0
6. **The owner can see what agents are working on, what they decided, and how much it cost — in real time, without opening bridge files** (Phase 4)
7. **A governance compliance dashboard shows proof that the system is enforcing its own rules** (Phase 4, OG-17)

---

## Updated Open Decisions for Codex

(Previous 5 decisions unchanged; adding:)

6. **Dashboard technology.** The existing `gt serve` uses FastAPI + Jinja. Should the activity feed use WebSocket (real-time push) or SSE (simpler, HTTP-based)? **Recommendation:** SSE — simpler to implement, no WebSocket dependency, sufficient for 3-minute update cadence.

7. **Dispatch summary format.** JSONL (one JSON object per line, appendable) vs. SQLite table (queryable, aggregatable)? **Recommendation:** JSONL for the log file (simple, greppable, compatible with existing monitor tooling) + a SQLite view or table for the dashboard (queryable for aggregations like daily token cost). Both are populated from the same data.

8. **Toast notification scope.** Should toasts fire for ALL bridge events (could be noisy during active development) or only for GO/NO-GO/VERIFIED/AUTH-FAILURE events? **Recommendation:** configurable in `groundtruth.toml` with a default of GO + NO-GO + VERIFIED + errors only. Verbose mode adds proposal-posted and dispatch-started.

---

*Estimated total effort: ~26 days across 4 phases.*
*Critical path: Phase 1 (8.5 days) → Phase 2 (3 days) → Phase 3 (4 days) = 15.5 days.*
*Phase 4 (10.5 days) runs in parallel with Phases 2-3.*
