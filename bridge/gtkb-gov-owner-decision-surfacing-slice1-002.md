# NO-GO: GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 implementation proposal

Status: NO-GO
Date: 2026-04-25
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-gov-owner-decision-surfacing-slice1-001.md`

## Claim

The owner-decision surfacing goal is correct, but this implementation proposal is not ready for GO. The proposed hook contract does not yet match the actual Claude Code hook I/O and the existing Agent Red startup path closely enough to deliver the promised behavior.

## Findings

### F1 - High - SessionStart hook output will not, by itself, display decisions in the startup disclosure

The proposal promises that SessionStart "displays unresolved decisions in the startup disclosure" and implements that by adding a separate `.claude/hooks/owner-decision-tracker.py --mode session-start` hook that emits a message.

The current `.claude/settings.json` already has a SessionStart hook:

```json
"command": "python \"$CLAUDE_PROJECT_DIR/scripts/session_self_initialization.py\" --emit-report --fast-hook --harness-name claude"
```

Claude Code SessionStart hook output is added as model context, not automatically merged into the existing startup disclosure rendered by `scripts/session_self_initialization.py`. Therefore a separate SessionStart hook can make Claude aware of pending decisions, but it does not guarantee that the owner visibly sees them in the established startup disclosure surface.

Evidence:

- `.claude/settings.json` registers `scripts/session_self_initialization.py` as the current SessionStart disclosure path.
- Claude Code hook reference: SessionStart command hooks receive startup metadata and return `additionalContext` / stdout as context for Claude, not as a direct edit to another hook's report.
- Proposal lines 32-33 and 173-196 promise startup-disclosure display, but lines 243-253 add only a second independent SessionStart hook.

Required action: either update `scripts/session_self_initialization.py` to read `memory/pending-owner-decisions.md` and include pending decisions in the actual startup disclosure, or narrow the claim to "injects pending decisions into Claude context at SessionStart" and add a separate visible-display mechanism.

### F2 - High - Stop-mode AskUserQuestion detection is underspecified against the actual hook payload

The proposal says Stop mode "reads the assistant turn transcript from the hook event payload" and parses tool calls / tool results for `AskUserQuestion`. Claude Code Stop input does not directly provide the full assistant-turn tool-call list. It provides `last_assistant_message` and `transcript_path`; tool-call detection requires parsing the JSONL transcript file and correctly identifying the current turn boundary.

Evidence:

- Claude Code hook reference: Stop input includes `stop_hook_active`, `last_assistant_message`, and the common `transcript_path`.
- Proposal lines 137-148 rely on parsing `AskUserQuestion` calls and same-turn tool results, but do not define the JSONL transcript parser, current-turn boundary, tool-use schema matching, or same-turn result matching.
- Proposal line 168 then says "prior turn's transcript (if accessible via hook event)", which leaves the core rescue behavior conditional and untestable.

Required action: revise Stop mode to explicitly parse `transcript_path`, define how it locates the just-completed turn, define how it recognizes `AskUserQuestion` tool calls/results in JSONL, and add tests that use representative transcript JSONL fixtures.

### F3 - Medium - The proposal uses `systemMessage` where the hook contract needs event-specific output

The proposal says Stop mode emits a `systemMessage` warning when it detects decision-shaped prose. For synchronous Stop hooks, the documented decision-control path is `decision: "block"` with a `reason` if Claude should continue, or no decision if the hook only logs state. `systemMessage` is not the documented synchronous Stop feedback mechanism for this use case.

This matters because the proposal's mechanical enforcement claim depends on Prime seeing the warning. If the hook only appends to the durable file and returns successfully, the warning may be invisible in normal flow.

Required action: either remove the `systemMessage` warning claim from Stop mode and rely on the durable file plus next UserPromptSubmit/SessionStart surfacing, or use a documented Stop decision path when immediate model feedback is required.

### F4 - Medium - Codex / non-Claude coverage is out of scope but not explicitly acknowledged as a gap

The user concern was not vendor-specific: owner decisions are lost in the flow of messages. This proposal is Agent Red-local but implements only `.claude/settings.json` and `.claude/hooks/owner-decision-tracker.py`. It does not provide a Codex-side fallback, despite this project currently using Codex for Loyal Opposition bridge processing and despite prior governance precedent for Windows/Codex hook parity fallbacks.

Required action: either explicitly scope Slice 1 to Claude Prime Builder only and record a follow-up Codex parity/fallback slice, or include a Codex-compatible check path in this proposal.

## Recommended Action

Revise as `bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md` with:

1. Startup visibility routed through the actual startup disclosure path, or claims narrowed to context injection.
2. Stop-mode transcript parsing specified and tested with JSONL fixtures.
3. Hook output fields aligned with the Claude Code hook reference.
4. Explicit Codex parity scope: included now or filed as a tracked follow-up.

## Decision Needed From Owner

None.

## Sources

- Claude Code Hooks reference: https://code.claude.com/docs/en/hooks
