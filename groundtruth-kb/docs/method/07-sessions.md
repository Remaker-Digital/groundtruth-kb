# 7. Ephemeral session contexts

A session context has one immutable canonical binding from its actual native
context identifier to its GT-KB identifier, subject and role. Identity does not
come from a sequence number, a memory file, the latest session or a harness role.

Use the exact owner- or dispatch-supplied marker with `gt session bind` and read
back the binding with `gt session show`. An identical retry returns the same
binding; conflicting subject or role fails without mutation. Ending a process,
closing or wrapping does not delete the binding or allow it to change role.

## Start and work

Preserve the owner's first input and explicit selected task. An explicit
`::open <activity>` selects one transient activity: ops, deliberation, build,
test, spec or project. Repetition is idempotent; a different selection replaces
it. No persistent activity record or default inferred from a queue is required.

Read `gt context session --native-context-id <actual-native-context-id> --json`
for current startup sources and `gt context work-item <WI-ID> --json` for the
assigned work. Read the exact dispatched bridge action through `gt bridge show`.
Resolve additional applicable formal requirements; the stored relationship set
alone does not prove complete applicability. Missing required input is a visible
incomplete operation, not permission to reuse a cached summary.

Disclose what was actually loaded, the supplied role/activity and relevant
limitations. Do not imply a host hook ran or a task was loaded merely because a
command or generated file exists. Dashboard links and read-only suggestions are
optional views, not current authority or task selection.

## Close and wrap

An explicit close directs activity-scoped canonical knowledge harvest; an
explicit wrap directs context-wide harvest within authorized work. Correct facts
and owner decisions directly through supported canonical writers and read back
the result. Session logs retain the conversation. No session document, prompt
object, decision archive or operational state file is required for continuity.

Close and wrap clear transient activity and preserve the immutable binding.
They do not implicitly stage, commit, push, deploy, change authorization or
activate automation. Read-only lifecycle guidance can be offered proactively;
it does not perform harvest. Missing lifecycle-hook or harvest capability remains
an explicit limitation with a recovery route.

The context's disposable scratch directory is removed by the explicit
`gt session scratch-teardown` verb, not by a session-end hook (none exists in
the harness manifests). The service derives `scratchpad/<session-context-id>`
from the immutable binding, removes exactly that directory, refuses an unbound
context or a redirected path, unlinks links without following them and reports
entries the host refuses to delete as a partial outcome. Siblings, the
registered checkout, formal history and the binding are untouched.

Report actual work, tests, failed/unexecuted checks and unresolved choices. Finish
or release this context's exact artifact action. A useful owner-copyable
continuation may contain timestamped observations and canonical retrieval
pointers, but remains ephemeral. It neither dispatches the next task nor carries
a claim. Another fresh context reconstructs current work without that handoff,
the original author, prior-session memory or direct contact with another harness.

Actual-host startup, close/wrap invocation, complete canonical harvest and fresh
successor workflows require behavioral qualification. Projector parity and
selected component tests do not establish that complete result.

See [independent review](06-dual-agent.md) and [project completion](14-lifecycle.md).
Formal retrieval: ADR-SESSION-MARKER-AND-ACTIVITY-RECORD-MODEL-001,
DCL-ACTIVITY-CONTEXT-MANIFEST-001, DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001,
PB-SESSION-WRAP-UP-PROACTIVE-001.
