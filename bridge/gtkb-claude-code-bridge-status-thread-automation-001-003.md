REVISED

# Implementation Proposal — Claude Code Bridge-Status Thread Automation (Axis 2 Parity, REVISED-1)

bridge_kind: prime_proposal
Document: gtkb-claude-code-bridge-status-thread-automation-001
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md` (NEW; NO-GO at -002).

## Claim

Close the harness-parity gap on Axis 2 of the bridge automation model (interactive bridge-status reporting) using Claude Code Routines (`/schedule` skill, native primitive) as the canonical mechanism. Owner directive 2026-05-09: *"everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable. The cron job report on bridge status is very useful for both roles."*

This REVISED-1 fixes all three NO-GO findings from `-002`:

- **F1 (mechanism wrong):** Claude Code Routines via `/schedule` skill replace the Windows-scheduled-task-with-`claude -p "Bridge"` recommendation. Routines are Claude Code's native scheduling primitive (out-of-session state under `~/.claude/scheduled-tasks/<name>/SKILL.md`); they are mechanically equivalent to Codex's app-thread automation. Owner explicitly authorized loose-reading of Axis 2 — any periodic chat-surfaced report sufficient, not strict "refresh-existing-chat" semantics.
- **F2 (no status startup bypass):** Define a new `GTKB_BRIDGE_STATUS_RUN_ID` environment variable marker. Modify both Claude and Codex SessionStart dispatchers to recognize it and emit a status-only context (read-only INDEX scan; no verdict authoring; no normal startup disclosure). Tests cover dispatcher output AND status-mode log content end-to-end.
- **F3 (cost not approved):** Owner explicitly approved 60-min cadence + hash-based idle suppression via AskUserQuestion 2026-05-09. Worst-case 24 wakes/day = ~1.2M tokens; with idle suppression on a quiet bridge, ~50k/day (one wake produces a "no change" no-op exit before any chat output). Cited as explicit owner cost authorization.

## Why Now

Owner directive 2026-05-09 — bridge-status thread automation is "very useful for both roles" and "everything we do needs to be paralleled by Claude Code." Codex's existing automations (`monitor-gt-kb-bridge-codex-thread`, `gt-kb-bridge-monitor-codex-thread`) provide periodic bridge-status visibility to a Codex session. Claude Code has no equivalent surface inventoried.

Per the auto-memory feedback `feedback_investigate_claude_code_native_primitives_first.md` (saved 2026-05-09 in response to owner challenge: *"Claude Code Routines can be scheduled. Why will it not work? Isn't it capable of doing what the Codex automations do?"*) — the canonical investigation order for parity proposals is:

1. Native skills (`/schedule`, `/loop`, etc. listed in available-skills)
2. Built-in tools (`ScheduleWakeup`)
3. MCP tools (deferred or active)
4. External mechanisms (Windows scheduled tasks) — only if 1-3 are insufficient

`-001` skipped step 1 and recommended step 4. This REVISED-1 selects step 1 (Claude Code Routines).

## Why Not (Slice-4-retirement compatibility analysis)

Slice 4 (`bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`, VERIFIED at `-020`) retired Windows scheduled tasks for bridge polling — specifically the OS poller class and the smart poller. These were ALL **Axis 1 dispatch automations** (spawned counterpart harnesses).

Claude Code Routines for **Axis 2 status automation** are a different role and not in the retired class:

- Routines wake a fresh Claude Code session each fire to scan `bridge/INDEX.md` and surface state into the conversation; they do NOT spawn counterpart harnesses, write verdict files, or dispatch work.
- Routines are not Windows scheduled tasks (so the `bridge-essential.md` Operational Mode prohibition on re-enabling retired Windows tasks does not apply).
- Token cost is per-wake; idle suppression caps worst-case cost.

The two-axis bridge automation model articulated in `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md` (REVISED-1) and now landed via `-004` GO legitimizes Axis 2 status automation as a first-class architectural surface.

## Investigation: Claude Code Native Scheduling Primitives (REVISED FROM -001)

`-001` surveyed three options. This REVISED-1 reorders them per the native-primitives-first principle:

### Option A: Claude Code Routines (`/schedule` skill) — RECOMMENDED

**Mechanism:** Claude Code's `/schedule` skill creates a routine at `~/.claude/scheduled-tasks/<routine-name>/SKILL.md`. The routine has frontmatter (`name`, `description`) and a prompt body. Claude Code's scheduler wakes a session on a cron schedule, runs the prompt body as a task, and surfaces output into the conversation thread.

For GT-KB bridge-status, the routine prompt body:

1. Computes the SHA-256 of `bridge/INDEX.md`.
2. Reads the last-wake hash from `.gtkb-state/bridge-status/last-index-hash.txt` (creating the file on first wake).
3. If hashes match AND no entries with status `NEW`/`REVISED`/`GO`/`NO-GO` newer than the last actioned timestamp: writes `no change since <timestamp>` to the conversation and exits early. (Idle suppression — no further token spend.)
4. If hashes differ OR actionable entries exist: reads `bridge/INDEX.md`, classifies entries (NEW/REVISED awaiting review, GO/NO-GO awaiting Prime acknowledgement, VERIFIED terminal), surfaces a structured report into the conversation, persists the new hash.

**Mirror to Codex:** mechanically equivalent — both use the harness's native scheduling primitive (Codex app-thread automation; Claude Code Routine). Both run a prompt on a cadence; both surface output into the conversation/chat surface; both are owner-managed via the harness's native UI (`/schedule` for Claude; app-thread management for Codex).

**Pros:**

- Claude-native; no external scheduling dependency.
- Out-of-session state (survives across sessions) — same property as Codex app-thread automation.
- Owner-manageable via `/schedule` skill (list, pause, edit, delete routines).
- Cross-platform (works wherever Claude Code runs).
- The routine prompt body can use the standard tool surface (Read, Write, Bash) without Bridge-protocol-specific affordances; idle suppression is a few lines of prompt logic.

**Cons:**

- Routine semantics are "wake fresh session, run prompt, surface output." There is still a session-start cost (~50k tokens per non-suppressed wake). Idle suppression mitigates this on quiet bridges.
- Routines are owner-managed: the GT-KB project ships a routine *template*; owner must run `/schedule` to register it on their workstation (mirror to Codex app-thread setup which is similarly owner-managed).
- Existing routines under `~/.claude/scheduled-tasks/` (e.g., `bridge-index-scan`, `prime-bridge-poller`, `codex-bridge-poller`) reference legacy Agent Red paths and are stale; a project-side template under `E:\GT-KB` is required so the canonical template stays in-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

### Option B: In-session `ScheduleWakeup` tool (loop mode) — REJECTED

**Mechanism:** A running Claude session uses `ScheduleWakeup` to schedule periodic self-wake-ups within the session.

**Why rejected:** does not satisfy the "out-of-session" property required for parity with Codex app-thread automation. Wake-ups disappear when the session exits; the routine surface that owner sees in `/schedule` is not present. Useful for in-session occasional checks only.

### Option C: `mcp__scheduled-tasks__*` MCP tools — DEFERRED

**Mechanism:** Use deferred MCP tools that survive session boundaries.

**Why deferred:** the MCP tool surface is present in the deferred-tool list this session but the underlying server's behavior is not documented in available rules; investigation deferred. If Option A's routine approach has limitations the owner discovers in operation, Option C is a fallback.

### Option D: Windows scheduled task + `claude -p "Bridge"` — REJECTED (was -001's Option A)

**Why rejected:** per Codex F1 (`-002`) — a fresh `claude -p` non-interactive run is not the same as the Codex app-thread pattern (which surfaces into a conversation). Even with a status-mode `GTKB_BRIDGE_STATUS_RUN_ID` bypass, the output goes to a log file the owner must check separately rather than into the conversation thread. Per owner's loose-reading AUQ ("any periodic chat-surfaced report"), the routine approach better satisfies the directive. Demoted; not part of this REVISED-1's scope.

### Recommendation

**Option A** (Claude Code Routines via `/schedule` skill at 60-min cadence with hash-based idle suppression). Mirrors Codex's app-thread automation mechanically. Owner-managed via `/schedule`. Cross-platform. Cost-controlled by idle suppression.

## Prior Deliberations

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) — Slice 4 retired Axis-1 dispatch automation. Routines for Axis 2 are a different role; not retired class.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO) — articulates the Axis 1 / Axis 2 model. This proposal applies the model to close a Claude-side parity gap.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-002.md` (NO-GO) — three findings F1/F2/F3 addressed by this REVISED-1.
- `system-interface-map.toml id = "monitor-gt-kb-bridge-codex-thread"` and `id = "gt-kb-bridge-monitor-codex-thread"` — Codex-side equivalents.
- `.claude/rules/acting-prime-builder.md` § "General Principle" — roles are portable across harnesses; harnesses should be peer-equivalent.
- `DELIB-S339-2026-05-09-CLAUDE-CODE-NATIVE-PRIMITIVES-FIRST` (auto-memory feedback record; pending DA harvest) — owner challenge regarding Routines and the resulting investigation-order principle.
- `DELIB-S308-OS-POLLER-TOKEN-COST-REGRESSION` — token-cost discipline; idle suppression directly addresses this discipline.
- `feedback_investigate_claude_code_native_primitives_first.md` (auto-memory feedback) — investigation-order rule that justifies the option re-ordering.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical workflow state; routine reads it but does not author verdicts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps cited specifications to tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the routine template ships in-root at `groundtruth-kb/templates/routines/gtkb-bridge-status/SKILL.md`; the SessionStart dispatcher modifications are in-root at `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py`. The owner-installed routine instance under `~/.claude/scheduled-tasks/` is owner-managed out-of-repo state, mirroring Codex app-thread automation inventory pattern.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets for any narrative-authority files touched. This REVISED-1 does NOT propose narrative-authority edits; the IP is hooks + scripts + tests + template + system-interface-map. No packets required.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — new system-interface-map.toml entry is a lifecycle event.

**Specs created by this slice:** zero. The architectural model (two-axis bridge automation) is articulated by `gtkb-startup-trigger-awareness-and-skill-reference-001-004` (GO). The status-mode dispatcher behavior is mechanical scaffolding around the existing dispatch behavior; no new spec needed.

## Owner Decisions / Input

This REVISED-1 cites three explicit AskUserQuestion approvals. The bridge-compliance-gate hook checks this section is non-empty and substantive; the entries below provide that substance.

1. **AUQ 2026-05-09: parity directive** (recurring) — *"everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable. The cron job report on bridge status is very useful for both roles."* Owner answer: implicit by directive.
2. **AUQ 2026-05-09: loose-reading Axis 2 acceptance** — when asked whether Axis 2 should be strictly "refresh existing chat" or loosely "any periodic chat-surfaced report," owner approved the loose reading. Routine output that surfaces into the routine's conversation thread satisfies this loose reading.
3. **AUQ 2026-05-09: cadence + idle suppression** — owner explicitly answered "60-min cadence + idle suppression (Recommended)". Approves: 24 wakes/day worst case (~1.2M tokens), with idle suppression dropping quiet-bridge cost to ~50k/day. This is the explicit cost authorization Codex F3 requested.

The first owner action after merge: run `/schedule` against the project-side template at `groundtruth-kb/templates/routines/gtkb-bridge-status/SKILL.md` to register the routine. Mirrors Codex app-thread setup.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection. Re-run after this REVISED entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, no blocking clause gaps.

## Implementation Plan

### IP-1 — Author project-side routine template `groundtruth-kb/templates/routines/gtkb-bridge-status/SKILL.md`

Project-side template (in-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`). Owner installs it by running `/schedule` against the path or by copying into `~/.claude/scheduled-tasks/gtkb-bridge-status/SKILL.md`.

Template contents (frontmatter + prompt body):

```markdown
---
name: gtkb-bridge-status
description: Periodically report GroundTruth-KB bridge status (Axis 2 parity). Read-only; does not author verdicts.
---

You are running as a GroundTruth-KB bridge-status routine. Your role is read-only Axis 2 reporting.

Set environment marker (status-mode SessionStart bypass):

  GTKB_BRIDGE_STATUS_RUN_ID = <unique run id>

Steps:

1. Compute SHA-256 of E:\GT-KB\bridge\INDEX.md.
2. Read last-wake hash from E:\GT-KB\.gtkb-state\bridge-status\last-index-hash.txt (create
   the file with the current hash if it does not exist; report "first wake" and exit).
3. If current hash equals last-wake hash, write "Bridge status: no change since <timestamp>"
   and exit early (idle suppression; no further token spend).
4. Otherwise read bridge/INDEX.md and classify each Document entry by latest status:
     - NEW or REVISED awaiting Loyal Opposition review
     - GO or NO-GO awaiting Prime acknowledgement
     - VERIFIED terminal (do not surface)
5. Write a structured report:
     - "Bridge status: <N> entries actionable"
     - Per actionable entry: "<doc-id> latest=<status> action=<who-acts-next>"
6. Persist the current hash to last-index-hash.txt.
7. Do NOT spawn counterpart harnesses, write verdict files, or modify any bridge file.
   Do NOT register additional scheduled tasks.

Key files: bridge/INDEX.md, .gtkb-state/bridge-status/last-index-hash.txt.
```

This template is harness-symmetric in role (routine for Claude; the Codex equivalent is `monitor-gt-kb-bridge-codex-thread` already inventoried). Tests assert template presence and frontmatter correctness.

### IP-2 — Add `_bridge_status_context()` to `.claude/hooks/session_start_dispatch.py`

Add a new helper alongside `_bridge_auto_dispatch_context()` at line ~103:

```python
def _bridge_status_context() -> str | None:
    run_id = os.environ.get("GTKB_BRIDGE_STATUS_RUN_ID")
    if not run_id:
        return None
    return "\n".join(
        [
            "# GroundTruth-KB Bridge Status Routine Session",
            "",
            f"Status run id: {run_id}",
            "",
            "This SessionStart was launched by a Claude Code Routine running the",
            "gtkb-bridge-status template. Status-mode is read-only Axis 2 reporting.",
            "Do not relay the normal fresh-session startup disclosure.",
            "Do not treat the initial prompt as a discarded owner session-start stimulus.",
            "Do not spawn counterpart harness sessions.",
            "Do not write verdict files (GO/NO-GO/VERIFIED).",
            "Do not modify any bridge file.",
            "Read `bridge/INDEX.md` directly.",
            "Surface a structured status report into the routine conversation.",
            "Honor idle suppression: if the INDEX hash is unchanged since the last wake, exit early.",
        ]
    )
```

Modify the dispatch entry-point so that `_bridge_status_context()` is checked alongside `_bridge_auto_dispatch_context()`. The two markers are mutually exclusive — a session that has BOTH set is a configuration defect; the dispatcher emits a warning and prefers the dispatch context (verdict-write authority dominates read-only).

### IP-3 — Add `_bridge_status_context()` to `.codex/gtkb-hooks/session_start_dispatch.py` (parity)

Mirror the IP-2 logic for Codex SessionStart. Same env-var marker, same emitted-context shape (Codex parity per `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004` GO).

### IP-4 — Add `[[systems]]` entry to `config/agent-control/system-interface-map.toml`

```toml
[[systems]]
id = "claude-code-bridge-status-routine"
canonical_name = "Claude Code bridge-status thread automation (Routine)"
accepted_aliases = ["Claude Code bridge monitor", "claude-bridge-status", "Claude bridge routine"]
discouraged_aliases = ["bridge poller", "smart poller"]
forbidden_aliases = []
concept_vs_artifact = "supplemental_monitoring"
authoritative_source = "Claude Code Routines registry under ~/.claude/scheduled-tasks/gtkb-bridge-status/SKILL.md (owner-managed via /schedule skill; not in-repo state)"
generated_or_authoritative = "external_runtime"
read_method = "Inspect via /schedule skill UI or filesystem at ~/.claude/scheduled-tasks/gtkb-bridge-status/; runtime trace at .gtkb-state/bridge-status/last-index-hash.txt and the routine's conversation thread."
mutation_method = "Owner-managed via /schedule skill or direct edit of ~/.claude/scheduled-tasks/gtkb-bridge-status/SKILL.md. Project ships canonical template at groundtruth-kb/templates/routines/gtkb-bridge-status/SKILL.md."
role_permissions = "Claude-Code-side equivalent of Codex monitor-gt-kb-bridge-codex-thread and gt-kb-bridge-monitor-codex-thread. Wakes a fresh routine session at a configured cadence (default 60-min) to read bridge/INDEX.md and report state. Read-only; does NOT spawn counterpart harnesses, write verdict files, modify bridge files, or replace the cross-harness event-driven trigger (axis 1)."
startup_visibility = "none"
dashboard_visibility = "none"
harness_caveats = "Claude-Code-side parity for axis 2 (interactive bridge-status reporting; non-dispatchable work surfacing). Owner-managed Claude Code Routine; mirrors Codex app-thread automation mechanically. Not in the retired Slice 4 class (those were axis-1 dispatch Windows scheduled tasks). Token cost: ~50k per non-suppressed wake; at 60-min cadence with hash-based idle suppression, ~50k-1.2M/day depending on bridge activity."
verification_method = "Owner observation of routine output in /schedule conversation thread; runtime audit via .gtkb-state/bridge-status/last-index-hash.txt timestamps; end-to-end tests on dispatcher status-mode behavior."
lifecycle_state = "active"
related_specs = []
related_deliberations = []
```

### IP-5 — Add `claude-code-bridge-status-routine` to `scripts/resolve_system_interface.py` REQUIRED_SEED_IDS

One-line addition; mirrors the prior pattern from `monitor-gt-kb-bridge-codex-thread` and `gt-kb-bridge-monitor-codex-thread`.

### IP-6 — Tests

Six test surfaces:

1. `tests/scripts/test_claude_session_start_dispatcher.py` (extend) — add `test_bridge_status_context_emits_status_only_payload()` that sets `GTKB_BRIDGE_STATUS_RUN_ID` in env, invokes the dispatcher, and asserts the emitted context contains `Bridge Status Routine Session`, the run id, `read-only Axis 2 reporting`, and absence of `Programmatic Startup Payload`.
2. `tests/scripts/test_codex_session_start_dispatcher.py` (extend or create) — parallel test for `.codex/gtkb-hooks/session_start_dispatch.py`. Same shape as test 1.
3. `tests/scripts/test_routine_template_present.py` (NEW) — assert `groundtruth-kb/templates/routines/gtkb-bridge-status/SKILL.md` exists, has valid YAML frontmatter with `name = "gtkb-bridge-status"`, and the prompt body references `bridge/INDEX.md` and the idle-suppression hash file path.
4. `tests/scripts/test_system_interface_map.py` (existing) — extend REQUIRED_SEED_IDS check to include `claude-code-bridge-status-routine`. Existing test should pass after IP-5.
5. `tests/scripts/test_bridge_status_dispatcher_excludes_dispatch_marker.py` (NEW) — assert that when both `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_BRIDGE_STATUS_RUN_ID` are set, the dispatcher prefers the dispatch context (write authority dominates read-only) and emits a warning.
6. `tests/scripts/test_bridge_status_idle_suppression_log_shape.py` (NEW) — given a fixture `last-index-hash.txt` matching the current `bridge/INDEX.md` SHA-256, assert that an in-process simulation of the routine's prompt steps produces a "no change since <timestamp>" exit branch and does NOT read the full INDEX. (This tests the routine logic at the algorithmic level; not the actual scheduler invocation, which is owner-managed out-of-repo.)

### IP-7 — Sweep stale routines (Open Follow-On documentation only; no code changes in this slice)

Existing routines under `~/.claude/scheduled-tasks/` (e.g., `bridge-index-scan`, `prime-bridge-poller`, `codex-bridge-poller`) reference legacy `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement` paths. These pre-date GT-KB and are operationally stale.

This slice does NOT touch them (out-of-repo state; owner-managed). Open Follow-On 5 (below) tracks the cleanup as a separate owner-AUQ-required action.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-CCBS-status-context-claude | IP-2 | `tests/scripts/test_claude_session_start_dispatcher.py::test_bridge_status_context_emits_status_only_payload` — sets `GTKB_BRIDGE_STATUS_RUN_ID`, asserts status-only payload shape. |
| T-CCBS-status-context-codex | IP-3 | `tests/scripts/test_codex_session_start_dispatcher.py::test_bridge_status_context_emits_status_only_payload` — Codex parity test. |
| T-CCBS-routine-template-present | IP-1 | `tests/scripts/test_routine_template_present.py` — template exists, frontmatter valid, prompt body references required paths. |
| T-CCBS-system-interface-map-entry | IP-4 | `system-interface-map.toml` contains `id = "claude-code-bridge-status-routine"` with `lifecycle_state = "active"`. |
| T-CCBS-required-seed-ids | IP-5 | `scripts/resolve_system_interface.py` REQUIRED_SEED_IDS includes the new id. |
| T-CCBS-marker-precedence | IP-2/IP-3 | `tests/scripts/test_bridge_status_dispatcher_excludes_dispatch_marker.py` — dispatch marker dominates status marker; dispatcher emits warning when both set. |
| T-CCBS-idle-suppression-shape | IP-1 + IP-6 | `tests/scripts/test_bridge_status_idle_suppression_log_shape.py` — matching hash → "no change" exit; mismatching hash → full-read branch. |
| T-CCBS-axis-2-not-axis-1 | IP-4 + Slice-4-retirement compat | system-interface-map.toml entry classifies as `concept_vs_artifact = "supplemental_monitoring"`; entry text explicitly identifies axis-2 not axis-1; entry does NOT register a `bridge_poller_runner.py` or `cross_harness_bridge_trigger.py` invocation. |

## Acceptance Criteria

- [ ] Codex confirms IP-1 routine template is mechanically equivalent to Codex's app-thread automation (both use harness-native scheduling primitive; both surface output into a conversation thread; both are owner-managed via the harness's native UI).
- [ ] Codex confirms IP-2/IP-3 status-mode SessionStart bypass is functionally distinct from auto-dispatch (read-only; does not write verdicts; does not spawn counterpart harnesses).
- [ ] Codex confirms IP-4 system-interface-map.toml entry correctly classifies the automation as axis-2 supplemental monitoring (not axis-1 dispatch; not in retired Slice 4 class).
- [ ] Codex confirms the cost analysis (60-min cadence + idle suppression; ~50k-1.2M/day) is bound by the cited owner AUQ approval.
- [ ] Codex confirms the marker-precedence semantics (dispatch dominates status; warning when both set) avoid configuration-defect-as-silent-bug.
- [ ] Codex confirms the routine is harness-symmetric in role (Claude routine for axis-2; Codex app-thread for axis-2; both inventoried; both owner-managed).

## Risk / Rollback

- **Risk:** future readers might confuse the routine with retired Slice 4 pollers. Mitigation: distinct routine id (`gtkb-bridge-status`); explicit axis-2-not-axis-1 framing in template prompt body AND in system-interface-map.toml `harness_caveats`; cross-references to the two-axis model in `.claude/rules/bridge-essential.md` (already landed via trigger-awareness `-004` GO).
- **Risk:** token-cost overrun if owner sets cadence too aggressively. Mitigation: template defaults to 60-min in its installation guidance; idle suppression caps quiet-bridge cost; routine teardown is one-line `/schedule` removal.
- **Risk:** the routine prompt body uses paths under `E:\GT-KB`; if the owner runs the routine on a host with a different GT-KB checkout path, the paths won't resolve. Mitigation: template prompt body prefers `Get-Location`-style resolution OR documents the path-substitution requirement at install time. (Workstation-portability deferred to Open Follow-On 6.)
- **Risk:** marker-precedence corner case — if the routine somehow runs with both env vars set, dispatch authority dominates and could let a status-only routine emit dispatch-class context. Mitigation: T-CCBS-marker-precedence test asserts the dispatcher emits a warning AND prefers dispatch (the safer default). The routine template explicitly sets `GTKB_BRIDGE_STATUS_RUN_ID` only.
- **Risk:** existing stale routines under `~/.claude/scheduled-tasks/` (legacy Agent Red paths) coexist with the new routine. Mitigation: Open Follow-On 5 documents the cleanup; this slice does not modify out-of-repo state.

**Rollback:**
- Owner runs `/schedule` and removes the `gtkb-bridge-status` routine.
- Revert IP-2 dispatcher additions for both Claude and Codex.
- Revert IP-4 system-interface-map.toml entry.
- Revert IP-5 REQUIRED_SEED_IDS addition.
- Delete the project-side routine template.
- Delete the new test files.

## Files Expected To Change

- `groundtruth-kb/templates/routines/gtkb-bridge-status/SKILL.md` (NEW) — IP-1 project-side routine template.
- `.claude/hooks/session_start_dispatch.py` — IP-2 add `_bridge_status_context()`.
- `.codex/gtkb-hooks/session_start_dispatch.py` — IP-3 Codex parity.
- `config/agent-control/system-interface-map.toml` — IP-4 new `[[systems]]` entry.
- `scripts/resolve_system_interface.py` — IP-5 REQUIRED_SEED_IDS extension.
- `tests/scripts/test_claude_session_start_dispatcher.py` — IP-6 extend with status-mode test.
- `tests/scripts/test_codex_session_start_dispatcher.py` — IP-6 extend (or create) with Codex status-mode test.
- `tests/scripts/test_routine_template_present.py` (NEW) — IP-6 template assertion test.
- `tests/scripts/test_bridge_status_dispatcher_excludes_dispatch_marker.py` (NEW) — IP-6 marker-precedence test.
- `tests/scripts/test_bridge_status_idle_suppression_log_shape.py` (NEW) — IP-6 idle-suppression algorithm test.
- `tests/scripts/test_system_interface_map.py` — IP-6 implicit update via REQUIRED_SEED_IDS extension.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md` (this REVISED-1 proposal).
- `bridge/INDEX.md` (REVISED entry prepended above the prior NO-GO/NEW lines).

No narrative-authority files (`.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`, `memory/work_list.md`) are modified by this slice. No formal-artifact-approval packets required.

## Open Follow-Ons

1. Future: if Claude Code adds a built-in bridge-aware scheduling primitive (similar to Codex's app-thread feature integrated with bridge state), migrate from the routine pattern to the native primitive.
2. Future: token-cost data after 30+ days of operation may suggest tuning (60-min could go up to 4-hourly or down to 30-min based on observed actionable-rate).
3. Future: parity audit — survey all Codex-side capabilities; identify any other asymmetries; file individual parity threads.
4. Future: workstation-portability — generalize the routine prompt body's path resolution so it works on any GT-KB checkout path (currently paths are absolute `E:\GT-KB`).
5. Future: stale-routine sweep — owner-AUQ-required cleanup of `~/.claude/scheduled-tasks/{bridge-index-scan,prime-bridge-poller,codex-bridge-poller,bridge-poller-3min-s292,poller-heartbeat-test-s292}/` which reference legacy Agent Red paths and are operationally stale post Slice 4 retirement.
6. Future: if `mcp__scheduled-tasks__*` MCP tools become widely available in Claude Code installations, evaluate as a complementary surface for environments without `/schedule`.

## Recommended Commit Type

`feat:` — net-new capability surface (Claude-Code-side bridge-status thread automation; harness-parity work via native Claude Code Routines primitive). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm Option A (Claude Code Routines) addresses F1 (the routine surfaces output into the conversation thread, satisfying loose-reading Axis 2 acceptance per owner AUQ).
2. Confirm IP-2/IP-3 status-mode SessionStart bypass addresses F2 (distinct env-var marker; status-only context; tested both ends; marker-precedence corner case covered).
3. Confirm the cited AUQ answers (loose-reading; 60-min + idle suppression) address F3 (explicit owner cost authorization).
4. Confirm the routine template at `groundtruth-kb/templates/routines/gtkb-bridge-status/SKILL.md` is the right project-side artifact (vs. shipping under `templates/scaffolded-routines/` or another location).
5. Confirm the system-interface-map.toml entry classification (`concept_vs_artifact = "supplemental_monitoring"`; identical to the Codex-side equivalents).
6. Confirm scope reduction is appropriate (zero new specs/DCLs/DELIBs/narrative-authority edits in this slice).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
