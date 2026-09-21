---
name: gtkb-session-wrap-scan
description: Inspect current assigned work and unresolved harvest conditions without producing a session snapshot or performing wrap mutations.
allowed-tools: Bash, Read
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: session-management
---
# Read-only wrap orientation

For the selected work, inspect current canonical state before deciding what
an explicit close or wrap needs to harvest. This guidance is optional read-only
orientation. It does not create a session snapshot, write a report, perform
harvest or require a new owner override before an already authorized action.

Use the actual native context identifier with `gt session show`. Read the
assigned `gt context work-item` and exact `gt bridge show` result, then Git
status/HEAD in the registered checkout. Do not infer a session ID, choose a
queued target or substitute a cached scan for an unavailable canonical read.
Preserve unrelated work and another context's claims.

Use the [current harvest checks](../gtkb-session-wrap/references/audit-checklist.md)
and [wrap procedure](../gtkb-session-wrap/SKILL.md) to distinguish facts already
recorded from missing or failed canonical writes. Report useful observations,
untested obligations and unresolved conditions inline. A suggestion neither
dispatches work nor proves it completed.

An explicit close or wrap directs its scoped canonical harvest under
DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001. A notification or this inspection does
not. The immutable binding remains intact; any later successor obtains its own
claim from current state without a persisted handoff or peer-harness contact.

Legacy snapshot and scanner scripts are not the ordinary wrap route. Their
remaining readers, standalone diagnostic duties and behavioral qualification
must be reconciled in their current work scope. This guidance does not retire
broader hygiene or benchmark requirements, qualify the complete harvest workflow
or establish actual-host lifecycle behavior.
