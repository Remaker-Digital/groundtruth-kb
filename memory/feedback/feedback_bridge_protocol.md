---
name: Bridge protocol — near-real-time autonomous exchange
description: Consolidated bridge communication rules. Near-real-time goal. Mandatory message fields, lifecycle discipline, no owner intervention.
type: feedback
---

## Core Directive (S223)

Owner directive: "I am not going to intervene in your communication across the bridge. I want to watch your behavior and ensure that the bi-directional exchange is fully autonomous." Near-real-time conversation is the goal — seconds to low minutes, not 10+ minute silences.

**Why:** S222-S223 exposed multiple failures: 19 messages sat unresolved across sessions, messages lacked file paths causing miscommunication, no response windows meant neither side knew when to escalate, owner had to manually prompt for action.

## Rules

1. **Session start:** Always sweep the bridge for unresolved messages. Acknowledge or resolve each one. Report count.
2. **Acknowledgement:** Every new message gets a substantive response within 60 seconds — what you will do, ETA.
3. **Mandatory fields:** Every outbound message includes artifact_refs (full paths), expected_response type, response_window, action_items, correlation_id.
4. **Resolve immediately:** After acting on a message, resolve it with a summary. Never batch to session end.
5. **Status updates:** For work taking > 5 minutes, send periodic in-progress updates before ETA expires.
6. **Escalation:** 2 unanswered status pings = escalate to owner.
7. **Artifact detail:** Every file, KB record, or report reference includes the full absolute path, ID, type, and status. Codex operates in a separate context and cannot search without exact paths.

## How to apply

Before sending any bridge message, verify it contains all mandatory fields per `.claude/rules/prime-bridge-collaboration-protocol.md`. Use the templates in `.claude/skills/prime-bridge-sync/SKILL.md`.
