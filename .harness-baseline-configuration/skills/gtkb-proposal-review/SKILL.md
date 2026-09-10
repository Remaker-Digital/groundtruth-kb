---
name: gtkb-proposal-review
description: Independently review an assigned GT-KB NEW or REVISED implementation proposal against current requirements, target scope, dependencies and executable tests, then author GO or NO-GO through the native CLI.
---

# Review an implementation proposal

Use this skill for explicitly assigned proposal review. The supplied init marker
and immutable context binding establish the role; the skill, provider and model
do not. Formal review requires a Loyal Opposition context independent of the
proposal's author. Use `gtkb-bridge` for binding, exact claims, complete authored
headers, delivery and recovery. An ordinary design discussion produces analysis,
not an implementation verdict or an owner decision record.

## Establish the review inputs

Read `gt context work-item <WI-ID> --json` and
`gt bridge show <document> --content --json`. Confirm the live response is NEW or
REVISED for the assigned work, or a proposal-phase verdict correction selected
from canonical state. Resolve the work item's one parent, current requirements,
linked executable test, test-plan instructions and prerequisites through the CLI.
Read the available attempt messages as coordination context; do not treat a past
message as durable authority or a substitute for a current formal source.

Inspect the complete proposed change and its source and test targets. Follow
current formal links to their actual content, check relevant cross-cutting
requirements, and identify omissions or contradictions. A declared reference
list is not proof that the required scope is complete. Missing or inactive
requirements must be reconciled, not silently omitted or replaced by an old
approval, retained disclosure, deliberation or another harness's state.

Reserve the intended GO or NO-GO response with `gt bridge claim`, using this
context's native identifier and the predecessor version just read. Keep the
returned fence. A conflicting or changed predecessor requires a fresh read,
not a whole-thread claim or an attempt to take over another context's work.
Use `gt bridge check` before protected effects and release an unfinished claim.

## Review the proposed behavior

Evaluate these questions against the actual source and canonical requirements:

- Does the proposal solve the specified problem, with explicit observable
  results and a complete affected scope?
- Do the project, work item, target artifacts and prerequisites describe a
  change that can complete coherently with the project's other members?
- Are assumptions supported, and are contradictory active instructions or
  consumers included in the correction?
- Are the test plan and executable test linked to the required behavior,
  including relevant refusals, failure recovery and independent successors?
- Does the approach preserve canonical state, exact artifact claims, review
  independence and unrelated work? Are side effects and recovery bounded?
- Can deletion, consolidation or a direct correction achieve the same required
  result more simply? Explain the actual alternative considered.

Inspect or run the applicable nonmutating checks. Do not implement the proposal
while reviewing it. Distinguish inspected evidence, executed checks, assumptions
and remaining uncertainty. Do not infer owner decisions; apply an explicit
owner correction to its canonical source through the supported CLI when needed.

## Author the verdict

Author GO only when the proposal is ready for implementation. Otherwise author
NO-GO with concrete findings: the observed issue, governing requirement,
consequence, affected scope and correction needed. The Prime Builder answers a
NO-GO with REVISED. A report-phase rejection uses NOT-READY under `gtkb-verify`.

Write the complete UTF-8 message in this context's scratch directory. Both GO
and NO-GO use `bridge_kind: lo_verdict`, name the actual author and session, and
address the next Prime Builder with `recipient_role: prime-builder`. Their first
three nonblank lines contain the status, `::init gtkb pb`, and the supplied
canonical activity as `::open <activity>`. Author the current Document, next
Version and Date metadata exactly once. The claimed attempt supplies Project
and Work Item identity; if the verdict repeats either field, it must match
that current claim.

The body explains the reviewed requirements, source evidence, checks and
results, simpler alternative considered, findings and required next action.
Include only evidence actually inspected or produced. No helper composes the
header, searches prior decision records, chooses the verdict or commits it.

Deliver with `gt bridge deliver <document> --native-context-id <context-id>
--fence <fence> --content-file <message-file> --json`, then read the result back
through `gt bridge show`. An unavailable authority is a refusal, not a reason to
publish to local bridge files. A GO permits the next implementation step; it
does not complete the work or commit the project. Subsequent work is dispatched
by the owner or dispatcher to an independent receiving context.
