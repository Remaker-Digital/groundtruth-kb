# {{PROJECT_NAME}}

Owner: {{OWNER}}

# GT-KB session instructions

GT-KB supplies task-scoped knowledge and a standard work process to ephemeral
agent contexts. Read current state through the native CLI. This baseline directs
behavior; current formal records and canonical project/work-item state supply
intent and status.

## Start from the supplied task

Use the exact init marker and activity supplied by the owner or dispatched
message. Bind the harness's actual native context identifier with
`gt session bind --native-context-id <id> --init-keyword "<supplied-line>" --json`
and read it back with `gt session show`. A role is immutable for that context.
Resolve missing inputs before an action that depends on them.

Load `gt context work-item <work-item> --json` and the exact dispatched bridge item
through `gt bridge show <document> --content --json`. Inspect current membership,
formal requirements, tests, dependencies and Git state. Read definitions through
`gt authority resolve "<term>"` or `gt terms show <id>` when needed.

Work only on the supplied target. Each context claims the next artifact it will
deliver, with no enduring ownership of a work item or its chain. Harnesses remain
independent and interact only through the CLI and bridge/dispatcher. Do not read
or coordinate through another harness's configuration or runtime state.

## Perform the current phase

Use the role-appropriate bridge skill in the baseline's skills directory:
`gtkb-bridge-propose`, `gtkb-proposal-review`, `gtkb-bridge`, or `gtkb-verify`.
The owner dispatches work until Dispatcher Next is qualified and activated.
Only agents author proposals and verdicts; the harness transports them.

A program sequences projects. A project groups interdependent work that completes
and commits together. Every work item has one parent project. Parent authorization
is the owner's binary ordering choice; check it before NEW. Readiness also needs
current formal intent, an executable test, independent review, a live artifact
claim and a registered checkout. These are distinct conditions.

Prime Builder proposes, implements an independently accepted proposal and reports
READY. Loyal Opposition independently reviews and verifies work it did not author.
Review evidence identifies Git mode and object identity. The final project commit
contains its complete independently verified work product. Keep bridge payloads
and generated projections out of that commit.

For changed formal intent after VERIFIED before commit, use the native restart
operation and a fresh proposal/review/implementation attempt on the same work item.
Preserve membership and existing bytes; abandoned attempts grant no effect rights.
Ordinary byte changes need fresh verification. Committed work remains terminal.

## Preserve the work and correct drift

Use only this context's registered checkout and scratch directory. Revalidate the
claim and scope through native services before protected effects. Refuse redirected
paths and preserve unrelated bytes. Let native publication finish or safely resume
the intended effect; final prose is not proof of delivery.

Apply owner choices to the affected canonical source or requested action. Session
logs retain the conversation for later harvest. Ask for unresolved material intent;
do not invent it or build a second decision/permissions archive.

Correct obsolete instructions at their authoring source. The baseline and projector
are work product; named harness configuration directories are derived output and
are refreshed mechanically. An unavailable service, contradictory active guidance
or failed check is reported with its practical recovery route, never treated as
successful completion.

Copyright: {{COPYRIGHT}}
