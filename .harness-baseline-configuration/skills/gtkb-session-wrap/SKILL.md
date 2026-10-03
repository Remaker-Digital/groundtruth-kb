---
name: gtkb-session-wrap
description: Harvest authorized canonical knowledge on explicit close or wrap and present an ephemeral continuation from current state.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: knowledge-management
  references:
    - references/audit-checklist.md
    - references/handoff-template.md
---
# Close and wrap

An explicit `::close` directs activity-scoped canonical knowledge harvest.
An explicit `::wrap` directs context-wide canonical knowledge harvest within the
already authorized work. A lifecycle notification or an opportunity before ending
may present useful read-only guidance; it does not perform harvest or other
mutations by itself. Disclose unavailable lifecycle-hook support instead of
claiming that a hook ran.

## Read the current assignment

Resolve this context's immutable binding with
`gt session show --native-context-id <actual-native-context-id> --json`.
Use its returned identity for attribution. Never derive identity from a recent
session, memory file or handoff. Close and wrap clear the transient activity;
they do not delete, retire, change or rebind the immutable context identity.

For assigned work, re-read `gt context work-item <WI-ID> --json`, the exact
dispatched `gt bridge show <document> --content --json`, and Git status/HEAD in
this context's registered checkout. A bridge message is authoritative at receipt
and has no continuing authority. A claim reserves one next artifact. A successor
obtains its own claim from canonical state; no previous agent must return.

## Harvest the authorized knowledge

Inspect the session's actual work and owner directions. Correct adequately
defined facts and requirements directly in their existing canonical domains:
formal records, projects, work items, tests and terminology as applicable.
Use the supported native `record` or domain-specific command with the current
version and authored provenance. Consult that command's help for its fields;
read back every result. Do not invent a separate harvest service or bypass a
refusal. Leave a specific unresolved condition when the supported writer cannot
perform the required change.

Apply owner decisions directly to the affected authoritative source or requested
action. Interactive logs retain the conversation for later harvest. Do not copy
bridge messages, prompts or transcripts into a session history or permission
archive, or make a deliberation a required source of approval. Do not classify
every message or noun merely to satisfy a collection checklist.

Record test observations with the commands, exact tested inputs and coverage
limits. A partial suite does not verify a whole requirement. Preserve unexecuted
and failed obligations. The author of an implementation does not issue its
independent verification. A work item becomes terminal through the complete
project commit, not through a wrap summary or a changed prose label.

Finish or release this context's outstanding artifact action through the native
bridge command and read back the outcome. If delivery is uncertain, inspect its
exact canonical slot before retrying. Preserve another context's claims and
unrelated bytes. Do not transfer a held claim to a suggested successor.

## Tear down this context's scratch

After the harvest is read back, remove this context's disposable scratch
directory with
`gt session scratch-teardown --native-context-id <actual-native-context-id> --json`.
The service derives `scratchpad/<session-context-id>` from the immutable
binding and removes exactly that directory; it refuses an unbound context, a
redirected root or directory, and never follows a link out of the directory.
Read the result: `removed` and `absent` are complete; `partial` lists every
surviving entry with its reason (an open handle, a denied deletion) and the
command exits 1. Report a partial outcome as unfinished cleanup with its
recovery route; close the holder and rerun the verb. Do not delete the
directory with a recursive shell removal: the destructive gate blocks that
form and the verb is the sanctioned route. No session-end hook runs the
teardown; the verb is explicit, and an unavailable lifecycle hook is disclosed,
not simulated. Teardown does not touch another context's directory, the
registered checkout, formal history or the immutable binding.

## Bound the effects and report

Close, wrap and notifications never implicitly stage, commit, push, publish,
deploy, change project authorization, activate a harness or dispatcher, clean
unrelated work, tear down another context's scratch or send external messages. Existing explicit direction for a
separate concrete effect remains subject to its review, scope and execution
conditions; do not request the same authorization again.

Use the [harvest checks](references/audit-checklist.md) for the selected work.
Present a concise result: canonical changes and readbacks, observed tests and
limitations, the scratch teardown outcome, pending artifacts, unresolved
choices and useful next actions.
Suggestions do not dispatch work. When useful, present the
[continuation template](references/handoff-template.md) as ephemeral owner-copyable
text. It is not saved as a prompt object or recovery authority. A fresh context
must be able to reconstruct its assignment through CLI and bridge without that
text, prior-agent memory or contact with another harness.

Formal retrieval: DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001,
PB-SESSION-WRAP-UP-PROACTIVE-001, DCL-ACTIVITY-CONTEXT-MANIFEST-001,
ADR-SESSION-MARKER-AND-ACTIVITY-RECORD-MODEL-001, SPEC-0452 (scratch lifecycle).
