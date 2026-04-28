---
name: Bridge autonomy — never ask owner
description: Prime must sweep, poll, pester, and repair the bridge autonomously without ever asking the owner to act
type: feedback
---

Prime Builder must NEVER ask the owner to sweep the bridge, check the bridge, or repair the bridge. All bridge maintenance actions must be taken autonomously:

- Sweep pending inbound messages without asking
- Resolve completed thread closures without asking
- Run PESTER follow-ups without asking
- Repair bridge connectivity without asking

**Why:** The owner considers bridge maintenance to be Prime's responsibility, not the owner's. Asking the owner to act on bridge state is a workflow failure — it means Prime is routing routine collaboration through the owner, which violates the bridge collaboration protocol.

**How to apply:** At session start and periodically during work, sweep the inbox, resolve status messages, and follow up on pending outbound requests. Never present bridge state as something the owner needs to decide on or act on. If the bridge is broken, fix it or escalate only if a true external dependency blocks repair.
