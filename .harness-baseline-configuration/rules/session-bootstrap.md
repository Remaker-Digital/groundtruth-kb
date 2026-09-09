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

Identical binding retries return the same identity. A conflicting marker is a
real error to resolve; do not remint an identifier or adopt a different role.
Close, wrap and interruption do not authorize rebinding the same native context.

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

This rule targets the native CLI. It does not declare PostgreSQL cutover,
installed projection readiness, complete context loading or Dispatcher activation.
Those outcomes require their actual installation and behavioral qualification.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
