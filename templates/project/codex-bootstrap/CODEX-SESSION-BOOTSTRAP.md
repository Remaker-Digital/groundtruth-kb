# Codex Session Bootstrap - {{PROJECT_NAME}}

This document defines the mandatory startup sequence for every Codex session.
Execute phases A through C in order before beginning any assigned work.

---

## Phase A: Bridge Sweep and Prime Handshake

1. **Query inbox.** Call `list_inbox(agent="codex", status="pending")`.
2. **Process each pending message.** Read the payload, inspect referenced
   artifacts, and send a substantive reply with `correlation_id`.
3. **Resolve processed messages.** Mark each as `completed` or `failed`.
4. **Send liveness signal.** Send a status message to Prime Builder:
   "Codex online. Bridge sweep complete. N messages processed."
5. **Report.** Log the sweep result: message count, any anomalies, bridge
   health assessment.

If the bridge is unreachable after 2 minutes of polling, report the failure
to the owner before continuing.

---

## Phase B: Read Project Documents

Load and internalize the following documents in order:

1. `CLAUDE.md` -- Project rules, governance, and procedures.
2. `memory/MEMORY.md` -- Current project state, versions, recent sessions.
3. `AGENTS.md` -- Loyal Opposition operating contract (this governs your
   behavior for the entire session).
4. `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md` -- Open items,
   pending decisions, and completed work from prior sessions.

Note any discrepancies between documents. If MEMORY.md and CLAUDE.md conflict,
CLAUDE.md takes precedence (rules over state).

---

## Phase C: Check for Pending Review Requests

1. **Scan bridge messages** for any with `expected_response: advisory_review`
   or `expected_response: go_no_go` that arrived since last session.
2. **Check the insight dropbox** for any reports that reference unresolved
   items requiring follow-up.
3. **Prioritize.** If there are pending review requests, they take priority
   over new exploratory analysis. Process them before starting new work.

Report your readiness state:

```
Codex session [session_id] initialized.
- Bridge: [healthy/degraded/offline]
- Documents loaded: [count]
- Pending reviews: [count]
- Ready to proceed: [yes/no + reason if no]
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
