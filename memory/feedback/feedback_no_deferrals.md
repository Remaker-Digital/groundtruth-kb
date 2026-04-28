---
name: Do not defer work items without justification
description: Owner expects complete implementation when asked — do not scope down without explicit reason
type: feedback
---

When the owner asks to resolve something, implement the full solution. Do not defer work packages or scope down to an "interim slice" unless there is a genuine blocking dependency.

**Why:** Owner asked to implement the full Codex deploy spec (WP1-WP5). WP4 and WP5 were deferred without good reason — they were straightforward and should have been in the first pass.

**How to apply:** When implementing a plan with numbered work packages, implement all of them. If something truly can't be done yet (missing dependency, needs owner decision, requires infrastructure not available), state the specific blocker. "Being conservative about scope" is not a valid reason to defer.
