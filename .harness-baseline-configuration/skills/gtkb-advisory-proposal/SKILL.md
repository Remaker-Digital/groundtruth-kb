---
name: gtkb-advisory-proposal
description: Author a non-dispatchable advisory with either role through the native bridge CLI.
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: advisory
---
# gtkb-advisory-proposal

Use for an advisory finding, not an implementation proposal or verdict. Either
role may author ADVISORY; no role switch is needed. Re-query affected canonical
requirements, projects and work items before drawing conclusions.

Draft the claim, source, observed evidence, uncertainty, recommended next action
and Owner Decision Needed. Identify any unresolved material owner choice with
options and consequences, or say none remains. Optional recommendation words
adopt, adapt, reject, defer and monitor carry no lifecycle or permission effect.

Use `gt bridge claim --help` and `gt bridge deliver --help` for the current CLI
arguments. Claim only the advisory's next artifact, with no work-item reservation.
Author ADVISORY in the first three nonblank lines, bridge_kind:
governance_advisory, Document, Version, Date and complete author_identity,
author_harness_id, author_session_context_id and author_model. Omit ::init,
::open and recipient_role. Deliver the complete content under that exact claim
and read it back with `gt bridge show`.

Do not add a pending Classification Slot, owner-answer transcript or permission
packet. A later advisory revision needs a fresh artifact claim. Do not modify
another author's content. ADVISORY permits only ADVISORY as its successor.

Filing the report creates no implementation assignment or automatic follow-up.
The owner selects derived work, which uses a separate NEW chain and normal
specification, test and independent-review requirements. Advisory content is
ephemeral; apply any resulting owner-directed domain changes to canonical state.

Read current formal requirements and the baseline rule
`peer-solution-advisory-loop.md`. This skill does not resolve a session role or
activity; retain the explicit current binding and owner-selected scope.
