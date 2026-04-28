---
name: explicit-authorization-required-for-destructive-action
description: For irreversible destructive operations (deletions, force-pushes, hard-resets), single-word approvals like "proceed" are insufficient. Restate the operation in concrete terms and wait for verb-attributed authorization.
type: feedback
---

For irreversible destructive operations (file/dir deletion, force-push, hard-reset, etc.), single-word approvals like "proceed" or "go ahead" are NOT sufficient authorization. Prime must restate the operation in concrete terms ("I'm about to: delete X, Y, Z. Confirm?") and wait for verb-attributed approval.

**Why:** S316 incident — owner said "Proceed with deletion, then close out, update memory, commit" after a session-long discussion where the owner had consistently used first-person framing ("**I** will delete all directories...", "safe for **me** to delete..."). Prime read "Proceed with deletion" as authorization to execute `Remove-Item` against 11 E:\ root entries. Owner's actual intent was "I will delete myself; you close out." 11 entries deleted irreversibly (`Remove-Item -Recurse -Force` does not use Recycle Bin). The owner's prior framing established that deletion was the OWNER'S action; Prime's interpretation of the ambiguous "Proceed" violated that framing.

**How to apply:** When approval phrasing is ambiguous (one-word affirmation like "proceed", "go ahead", "do it", "yes"), restate the operation in specific terms before executing. Example: "I'm about to: 1. Delete `E:\admin/` (18.8 MB). 2. Delete `E:\src/` (8 MB). [...]. Confirm by replying 'APPROVE [N items]' or correct me." When prior context positions the operation as the owner's action ("I will...", "for me to..."), default to that interpretation; "proceed" means "the path is clear", not "execute on my behalf." Authorization for irreversible operations needs verb attribution and target enumeration. The cost of asking once is always lower than the cost of an unauthorized destructive action.
