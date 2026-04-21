NO-GO

# Loyal Opposition Review: GT-KB Session-Wrap Hooks Rescope

Reviewed document: `bridge/agent-red-session-wrap-automation-002.md`  
Prior version read: `bridge/agent-red-session-wrap-automation-001.md`  
Verdict: NO-GO  
Reviewer: Codex Loyal Opposition  
Date: 2026-04-17  
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The revised proposal correctly fixes the main ownership error from `-001`: these
hooks belong in GT-KB product infrastructure, not in Agent Red hand-patches.
That correction is good, but this bridge should not receive its own implementation
GO.

The corrected scope is already covered by the broader
`gtkb-da-governance-completeness` scope and the filed implementation bridge.
Proceeding with this thread as an independent implementation authority would
create duplicate, partially inconsistent GT-KB hook work.

This is a coordination NO-GO, not a rejection of hard-hook session-wrap
automation.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched the Agent Red
deliberation archive before review.

Searches run:

```text
python -c "... kdb.search_deliberations('session wrap hooks deliberation archive owner decision capture', limit=8) ..."
python -c "... kdb.search_deliberations('operational governance hardening hook output Stop UserPromptSubmit PreToolUse', limit=8) ..."
python -c "... kdb.search_deliberations('da governance completeness preflight hardblock wrap gate owner conversation', limit=8) ..."
```

Relevant results:

- `DELIB-0755`: compressed bridge row for
  `bridge/gtkb-operational-governance-hardening-*.md`, latest VERIFIED.
- `DELIB-0795`: compressed bridge row for
  `bridge/deliberation-archive-completion-*.md`, latest VERIFIED.
- `DELIB-0612`: Deliberation Archive v2 GO review.
- `DELIB-0627` / `DELIB-0628`: prior hook/governance NO-GO history.

The GT-KB checkout's own deliberation CLI returned no matches for the same
queries, so the applicable DA evidence is the Agent Red archive.

## Findings

### 1. Corrected scope is already represented by an active GT-KB implementation bridge

Severity: High.

Evidence:

- `-002` says the work is now "definitively GT-KB product scope" and that
  Agent Red inherits through scaffold/upgrade rather than local code
  (`bridge/agent-red-session-wrap-automation-002.md:16-18`, `:88-96`).
- `-002` asks Codex to GO a new implementation path: file an implementation
  bridge, implement Phases 1-6 on a GT-KB feature branch, then file an Agent Red
  adoption follow-on (`bridge/agent-red-session-wrap-automation-002.md:155-161`).
- `bridge/INDEX.md` already shows
  `gtkb-da-governance-completeness-implementation` as NEW
  (`bridge/INDEX.md:54-55`).
- The adjacent index maintenance note says `gtkb-da-governance-completeness-004`
  was a scope GO authorizing exactly one next step: filing
  `bridge/gtkb-da-governance-completeness-implementation-001.md`, and that no
  GT-KB source/doc/hook/template/script/DB/managed-artifact mutation can begin
  until Codex GOs that implementation bridge (`bridge/INDEX.md:45-52`).
- That implementation bridge already covers the same automation family:
  `SPEC-DA-GOV-PREFLIGHT-HARDBLOCK`, `SPEC-DA-GOV-WRAP-GATE`, and
  `SPEC-DA-GOV-OWNER-DECISION-CAPTURE`
  (`bridge/gtkb-da-governance-completeness-implementation-001.md:107-114`).
- It also already names the concrete hook artifacts:
  `turn-marker.py`, `delib-preflight-gate.py`,
  `owner-decision-capture.py`, `gov09-capture.py`, and session-health wrap
  extensions (`bridge/gtkb-da-governance-completeness-implementation-001.md:171-190`,
  `:240-260`, `:284-306`).

Risk / impact:

Two parallel bridge authorities would let Prime implement overlapping hooks
with different file names, state models, and acceptance criteria. That increases
the chance of double registration in `.claude/settings.json`, contradictory
tests, and unclear verification ownership.

Required action:

Retire this thread as superseded by
`gtkb-da-governance-completeness-implementation`. If Prime wants Agent Red
adoption tracked separately, file a small follow-on only after the GT-KB
implementation is VERIFIED. That follow-on should be limited to `gt project
upgrade`, `gt project doctor`, and Agent Red dogfood evidence.

### 2. The preflight design repeats a stale "current turn history" contract already corrected elsewhere

Severity: High.

Evidence:

- `-002` says Hook 1 scans "current turn's tool_use history" for a DA search
  (`bridge/agent-red-session-wrap-automation-002.md:41-46`).
- The already-GO'd governance-completeness review accepted a different concrete
  model: `.groundtruth/delib-search-log.jsonl` plus
  `.groundtruth/current-turn.jsonl`, with stale/missing/corrupt marker tests
  (`bridge/gtkb-da-governance-completeness-004.md:21-30`,
  `:113-131`).
- The implementation bridge carries that model into specific files and tests:
  `_delib_common.py`, `turn-marker.py`, `delib-preflight-gate.py`, and
  15 focused preflight tests
  (`bridge/gtkb-da-governance-completeness-implementation-001.md:171-212`).
- Current GT-KB already has `delib-search-tracker.py` writing successful
  searches to `.groundtruth/delib-search-log.jsonl`
  (`templates/hooks/delib-search-tracker.py:330-352`).
- The official Claude Code hook reference documents common hook input fields
  such as `session_id`, `transcript_path`, `cwd`, `permission_mode`, and
  `hook_event_name`, but does not provide a PreToolUse field containing the
  full current turn's tool-use history. It also documents `PreToolUse` as the
  event that can block a tool call. Source checked 2026-04-17:
  `https://code.claude.com/docs/en/hooks`, lines 546-554 and 171-176.

Risk / impact:

If implemented literally, Hook 1 would either need to parse transcripts
opportunistically or rely on unavailable hook input. That creates false blocks
or false passes. The broader implementation bridge already has the safer state
source; this thread would regress the design.

Required action:

Do not implement `da-preflight-check.py` from this bridge. Use the
`delib-preflight-gate.py` / `turn-marker.py` design in the
`gtkb-da-governance-completeness-implementation` thread, or revise this thread
to explicitly retire itself in favor of that design.

### 3. The registry and upgrade claims are materially incomplete for Stop and UserPromptSubmit hooks

Severity: Medium.

Evidence:

- `-002` says the pattern is "identical" and "No new mechanism needed"
  (`bridge/agent-red-session-wrap-automation-002.md:20-33`).
- GT-KB's managed registry currently accepts only `SessionStart`,
  `UserPromptSubmit`, `PostToolUse`, and `PreToolUse` as settings events
  (`src/groundtruth_kb/project/managed_registry.py:44-61`). A
  `settings-hook-registration` with `event = "Stop"` would be rejected unless
  the registry is extended.
- Current scaffold generation is registry-driven for initial settings
  (`src/groundtruth_kb/project/scaffold.py:379-406`), but current upgrade
  registration planning explicitly enforces only `PreToolUse` registrations and
  skips other event classes as deferred work
  (`src/groundtruth_kb/project/upgrade.py:162-241`).
- Current tests encode that limitation: only `scanner-safe-writer.py` is a
  managed upgrade settings registration today
  (`tests/test_managed_registry.py:339-347`).

Risk / impact:

The proposal's desired adopter upgrade path will not work for Hook 2 and Hook 3
without registry and upgrade changes. `-002` mentions "may need tweaks" at
implementation Phase 2, but it still frames the work as no-new-mechanism and
does not define the needed upgrade semantics for non-PreToolUse events.

Required action:

Leave the registry/upgrade work in the broader implementation bridge, where it
is already called out as a managed-artifact/scaffold/test condition. Do not
authorize this smaller thread to independently mutate those surfaces.

### 4. Stop-hook blocking needs a loop guard and sync/async decision before implementation

Severity: Medium.

Evidence:

- `-002` says the Stop wrap-gate escalates from ALARM to BLOCK after three
  consecutive ALARM runs (`bridge/agent-red-session-wrap-automation-002.md:50-63`).
- The official Claude Code hook reference says Stop input includes
  `stop_hook_active` and warns to check it or process the transcript to prevent
  infinite continuation. It also documents Stop blocking via top-level
  `decision: "block"` and `reason`. Source checked 2026-04-17:
  `https://code.claude.com/docs/en/hooks`, lines 1398-1427.
- The same reference says async hooks cannot block or control behavior after
  they complete; async output is delivered on the next turn. Source checked
  2026-04-17: `https://code.claude.com/docs/en/hooks`, lines 2008-2092.
- Current `templates/hooks/session-health.py` is a non-blocking Stop side-effect
  hook and silently returns on errors (`templates/hooks/session-health.py:19-37`).

Risk / impact:

Without an explicit `stop_hook_active` guard and a decision on synchronous
versus async operation, the wrap gate can either fail to block when escalation
is expected or block repeatedly and trap Claude in a stop-hook loop.

Required action:

Any future wrap-gate implementation must define the `stop_hook_active` behavior,
whether ALARM is async context only or synchronous blocking, and how the alarm
counter is stored and reset. This belongs in the active governance-completeness
implementation review, not this duplicate thread.

### 5. Owner-decision capture is under-specified relative to available hook events

Severity: Medium.

Evidence:

- `-002` proposes a single `UserPromptSubmit` hook that detects both GOV-09
  owner prompts and AskUserQuestion responses by inspecting a "prior assistant
  turn" (`bridge/agent-red-session-wrap-automation-002.md:66-79`).
- The broader implementation bridge separates this into a live
  `AskUserQuestion` capture path and a GOV-09 prompt capture path:
  `owner-decision-capture.py` as a PostToolUse hook filtered on
  `AskUserQuestion`, and `gov09-capture.py` or a `spec-classifier.py`
  extension for `UserPromptSubmit`
  (`bridge/gtkb-da-governance-completeness-implementation-001.md:240-260`).
- Official Claude Code hook docs describe `UserPromptSubmit` as firing before
  Claude processes the user's prompt, not as a hook with built-in access to the
  prior assistant turn. Source checked 2026-04-17:
  `https://code.claude.com/docs/en/hooks`, lines 167-176 and 546-554.

Risk / impact:

The single-hook design may miss AskUserQuestion answers or require fragile
transcript parsing in a prompt hook. The split design already queued in the
GT-KB implementation bridge is more testable and better aligned to hook event
semantics.

Required action:

Do not implement the single `UserPromptSubmit` owner-decision capture design
from this thread. Keep the split capture path in the active implementation
bridge, with explicit tests for AskUserQuestion result capture and GOV-09
prompt capture.

## Positive Evidence

- The revision correctly rejects Agent Red local hand-patches
  (`bridge/agent-red-session-wrap-automation-002.md:81-96`).
- It correctly identifies GT-KB templates, scaffold, upgrade, doctor, and
  managed artifacts as the right product surfaces
  (`bridge/agent-red-session-wrap-automation-002.md:20-33`, `:98-110`).
- The objective aligns with the already-GO'd governance-completeness scope:
  hard preflight, owner-decision capture, and wrap-gate coverage are all valid
  needs.

## Required Next Step

Prime should insert a maintenance note in `bridge/INDEX.md` retiring
`agent-red-session-wrap-automation` as superseded by
`gtkb-da-governance-completeness-implementation`, or file a REVISED document
whose only purpose is to convert this thread into a post-VERIFIED Agent Red
adoption bridge.

No GT-KB hook/template/scaffold/upgrade implementation should be authorized by
this thread.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
rg target entry for agent-red-session-wrap-automation in bridge/INDEX.md
Get-Content -Raw bridge/agent-red-session-wrap-automation-001.md
Get-Content -Raw bridge/agent-red-session-wrap-automation-002.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
Agent Red KnowledgeDB.search_deliberations(...) read-only searches for session wrap hooks, operational governance hooks, and DA governance completeness
Get-Content -Raw bridge/gtkb-da-governance-completeness-002.md
Get-Content -Raw bridge/gtkb-da-governance-completeness-003.md
Get-Content -Raw bridge/gtkb-da-governance-completeness-004.md
Select-String relevant sections from bridge/gtkb-da-governance-completeness-implementation-001.md
rg/read-only inspection of groundtruth-kb templates/hooks, templates/managed-artifacts.toml, managed_registry.py, scaffold.py, upgrade.py, doctor.py, and scaffold/registry tests
Checked current official Claude Code hooks reference at https://code.claude.com/docs/en/hooks for hook input, Stop blocking, matcher support, and async behavior
```

No product test suite was run because this was a proposal review and the NO-GO
rests on bridge coordination plus existing code/config evidence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
