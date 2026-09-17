# Session bootstrap

GT-KB agents start in `E:\GT-KB`. The harness loads its mechanically generated
configuration from the canonical `.harness-baseline-configuration` sources.
A generated configuration is a delivery format, not an independent authority.
Correct shared behavior in the baseline and projector, never by editing a
harness projection or reading another harness's configuration.

## Establish the actual context

Use the exact `::init gtkb pb` or `::init gtkb lo` delivered by the owner or in
the received dispatchable bridge message. The marker establishes the role of
this context. A harness, model, previous session, queue or environment default
cannot supply a missing role. Preserve the owner's first message as input;
startup must not discard it or select work on the owner's behalf.

Use the actual native context identifier supplied by the harness. With the
native authority configured, resolve its existing immutable binding through:

```text
gt session show --native-context-id <actual-native-context-id> --json
```

If this context is not yet bound, use the exact received marker:

```text
gt session bind --native-context-id <actual-native-context-id> --init-keyword "<exact-received-init-line>" --json
```

The bind response contains `status` and `binding`. `init_requested` reports a
new binding; `already_initialized_idempotent` reports an identical retry,
including a matching concurrent creation. Use the immutable `binding` object
for attribution. `gt session show` returns that binding directly. The result
status describes this invocation only; it is never stored on the binding and
does not grant an activity, bridge action or authority.

After resolving the binding, load bounded current startup context:

```text
gt context session --native-context-id <actual-native-context-id> --json
```

This read returns the binding, current startup, role-resolution and isolation
formal records, and the authored session-bootstrap and operating-model rules
from the authority service's selected project root. It creates no session state
and refuses missing or inactive formal sources and missing, redirected,
unreadable or oversized baseline files (at most 64 KiB per named file).
Canonical records share one read snapshot; the two baseline files are read
separately. This bounded view does not establish complete semantic closure.
Resolve additional relevant requirements through the reported retrieval routes.
The service cannot observe the receiving host's transient activity, active
tools, skills, plug-ins, executed hooks or startup token consumption. Supply
those observations from the current host where available; retain the stated
unavailability otherwise. Never treat this response as completed host startup.

Identical binding retries return the same identity. A conflicting marker is a
real error to resolve; do not remint an identifier or adopt a different role.
Close, wrap and interruption do not authorize rebinding the same native context.

The binding command accepts the complete received prompt and scans its exact
marker lines. Distinct valid markers return `session_init_conflict`; near misses
without a valid marker return `invalid_init_marker`. Explicitly invoking bind
with no marker returns `no_init_marker`; ordinary owner input alone is not an
initialization request. Read the diagnostic and recovery route, including the
accepted marker evidence and line numbers of near misses. Unknown token text
and surrounding owner input are omitted from diagnostic output. Do not replace
a rejected declaration with a guessed marker.

Disclose the observed subject, immutable role and context identity, relevant
governance stance, and the skills, plug-ins, directives and hooks known to be
active for the selected work. State unavailable inputs and authority conflicts
with their current retrieval routes. Installation metadata and file presence
cannot establish that a capability or hook ran.

Report startup token consumption before the first owner input only where the
harness supplies that measurement; otherwise say it is unavailable. Preserve
the input. Suggest index-first canonical retrieval, targeted skills and
progressive disclosure to reduce context cost. A current dashboard link may aid
navigation; do not generate a startup cache or treat a snapshot as current
canonical context. Changes to required governance or scope need owner direction.

`::open` selects one transient activity: `ops`, `deliberation`, `build`, `test`,
`spec` or `project`. Input aliases `operations` and `specification` resolve to
`ops` and `spec`. Use the explicit selection, never infer an activity from role
or work metadata. Repeating the same selection has no effect; changing it does
not implicitly harvest or grant authority. Close, wrap or context termination
clears the selection. Activity is not a persistent child of the session binding.

## Load the assigned task

The owner dispatches work until Dispatcher Next is separately qualified and
activated. A queue is orientation and does not assign a target. Each successor
context reconstructs its assigned work through the CLI and the received bridge
message, without contacting or depending on a previous agent or another harness.

With the native authority configured, load the exact assigned work item:

```text
gt context work-item <work-item-id>
```

Use `--json` when structured output is useful. Read the actual work scope,
parent project and program, formal requirements, linked test and active test-plan
instructions, predecessors and readiness. The reader loads current declared
formal relationships together; this does not by itself discover every semantic
intersection. Resolve any additional applicable requirements through current
formal sources. Load the applicable baseline role/activity instructions and
architecture shards when available; a missing required input is a platform defect,
not permission to invent a replacement authority.

Missing, inactive, changed or unavailable required context must remain visible
with its diagnostic and recovery route. Obtain current inputs before the affected
decision or effect. A startup banner, descriptor list, local report, timestamp,
TTL or matching digest does not certify current knowledge. Never substitute a
stored session packet, cached handoff or dashboard for a failed canonical read.
The native service does not fall back to SQLite when unavailable.

## Application specification intake

When the assigned work's current project selects an application repository,
use that exact project ID and the registered application's configuration to
read the next missing core specification before continuing the application work:

```text
gt --config <application-root>/groundtruth.toml core-specs next-question --project-id <project-id> --json
```

Run this read again in each fresh or successor context. Present only the one
returned question; a complete or explicitly disabled result presents none.
Never choose the first project in a repository, infer an enrollment from a
directory name, or use local notes to decide which requirements are complete.
An unavailable authority remains visible; it does not imply completion.

Apply an explicit owner answer directly with `gt core-specs answer`, using the
selected project, returned slot and current expected version, actor and reason.
Use `--source not_applicable` only for an explicit not-applicable answer.
An inference or a request needing clarification does not complete a slot.
Re-read on a version conflict; do not replay the answer automatically.
The next read derives progress from current canonical specifications. It writes
no prompt block, local database or session progress flag. Respect the explicit
application configuration or invocation opt-out and keep JSON invocations
noninteractive. No additional enrollment record or answer archive is created.

## Continue through the bridge

The received bridge instruction supplies the next action. Read the current
attempt and acquire the exact next-artifact claim through the CLI before its
protected effect. A claim never grants ownership of a work item or its chain.
A new context may perform the next action regardless of who authored earlier
messages, while preserving independent review and current scope checks.

Authorization is the parent project's `authorized` or `not authorized` field.
Check it before filing a NEW implementation proposal. It is not a per-mutation
permission record, and later changes do not revoke an already initiated chain.
A work item has one project; programs sequence projects and grant no authority.
Independent verification precedes the complete-project commit. No startup hook
selects work, implements repairs, declares verification or commits automatically.

Close and wrap perform their scoped canonical knowledge harvest and may present
an ephemeral continuation to the owner. They do not automatically commit, stash,
publish, deploy or create a retained handoff object. Apply owner decisions to the
relevant authoritative source and agent direction; interactive logs retain the
conversation. Preserve unrelated work and report defects without fabricating
missing role, activity, scope, review or completion facts.

Before ending, proactively present useful read-only wrap-up guidance, unresolved
work and concrete next actions when a lifecycle notification or an equivalent
agent opportunity exists. State unavailable hook support honestly. A suggestion
does not dispatch work or authorize harvest. Explicit close or wrap directs its
scoped harvest within existing owner authorization; do not ask again for an
action already authorized. An automatic notification never supplies authority
for a canonical mutation or external effect.

This rule targets the native CLI. It does not declare PostgreSQL cutover,
installed projection readiness, complete context loading or Dispatcher activation.
Those outcomes require their actual installation and behavioral qualification.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
