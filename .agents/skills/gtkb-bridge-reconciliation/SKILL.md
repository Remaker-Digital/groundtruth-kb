---
name: gtkb-bridge-reconciliation
description: Investigate discrepancies between bridge messages and canonical work or project state through the ordinary CLI. Use for missing work, mismatched completion evidence, or review and project-commit recovery.
license: "Proprietary - Remaker Digital"
metadata:
  project: groundtruth-kb
  category: bridge-reconciliation
---
# Bridge and work-state reconciliation

Start with the exact owner- or dispatcher-selected target. Read its current work
item, actual parent project, dependencies and operative message through the CLI:

```text
gt backlog show WI-NNNN --json
gt projects show PROJECT-ID --json
gt bridge show DOCUMENT --json
```

Substitute the selected identifiers. Use the command's current help for any
additional inspection or recovery operation. Read applicable active formal
records and compare the work item's complete intended outcome with the actual
review and integrated work product.

The database holds current scope, parent membership, review and completion facts.
A related bridge reference, a work-item mention, a message count or a historical
VERIFIED label does not establish completion. During the file-bridge transition,
numbered messages support delivery and inspection; they do not replace canonical
work state. After terminal cleanup, recovery must not require their payloads.

Independent VERIFIED records review of the exact scope and work product. It does
not assert that a commit exists. The project completes through one commit of its
complete independently verified work product. Its work items retain their parent;
bridge payloads and generated projections are excluded from that commit.

If verified bytes change or a project commit fails, use the canonical
fresh-verification and finalization recovery route. A fresh eligible context can
continue from current state. The dispatcher selects that work and authors no
proposal or verdict. Never turn a related message, umbrella relationship, commit
mention or inferred permission into a replacement review or completion result.

When recorded completion does not cover the described outcome, retain the actual
delivered work and historical evidence, identify the uncovered scope, and carry
the correction in the existing appropriate work item. Do not automatically close
or reopen work by scanning messages. Correct canonical state through its domain
CLI, then read back the exact affected records. An owner decision changes current
canonical state and agent direction directly; the interactive session log retains
the conversation. No permission packet or decision ledger is required.

Use the current active versions of these formal sources:

- DCL-STANDING-BACKLOG-DB-SCHEMA-001.
- GOV-FILE-BRIDGE-AUTHORITY-001.
- GOV-WORK-ITEM-TERMINAL-STATE-001.
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
