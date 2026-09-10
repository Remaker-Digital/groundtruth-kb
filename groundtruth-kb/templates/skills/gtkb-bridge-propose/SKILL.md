---
name: gtkb-bridge-propose
description: Author and deliver a NEW or REVISED implementation proposal for explicitly assigned GT-KB work through the native CLI, using current task context and an exact next-artifact claim.
---

# Author an implementation proposal

Use this skill as a Prime Builder context for the work selected by the owner or
dispatcher. A proposal is the agent's own complete message. The CLI validates and
delivers its authored bytes; it does not choose scope, compose decisions, repair
a header or select another agent's work.

Use the configured native authority. Obtain current instructions with
`gt context work-item <WI-ID> --json`. Read the work item, its one parent project,
applicable formal sources, linked executable test and test-plan instructions,
and prerequisites returned by that command. Resolve missing or contradictory
scope before proposing. Owner decisions change their canonical source directly;
prior deliberations and decision-history excerpts are not proposal authority.

The receiving context's role comes from its exact supplied init marker. Use its
native context identifier with `gt session show --native-context-id <context-id>
--json`; if initialization is still required, bind only the exact supplied marker
through `gt session bind`. A harness identity does not establish a role. Use only
your own harness identity and context; no peer harness inventory is required.

## Author the current proposal

For an existing attempt, read `gt bridge show <document> --content --json` and
respond to its current state. NEW begins a fresh implementation attempt;
REVISED responds to NO-GO on the existing attempt. Do not reuse a stale GO or
infer ownership of the work item from previous participation.

Before NEW, check the parent's current authorization field. If it is not
`authorized`, an interactive context asks the owner to resolve it. A headless
context follows the CLI's BLOCKED response; it does not change authorization.
Authorization changes do not cancel an already initiated chain.

Write the smallest cohesive proposal that explains the intended result, exact
targets, relevant formal requirements, test work and acceptance criteria. Include
necessary removal or supersession effects and interactions with current work.
Use current source content to justify scope; a list of IDs alone is not analysis.

A dispatchable proposal has exactly these three nonblank envelope lines, in any
order, before its typed metadata:

```text
::init gtkb lo
::open build
NEW
```

Use REVISED for a revised proposal. The envelope names the next responder.
Supply the complete metadata before the blank line introducing the body:

- `bridge_kind: implementation_proposal`
- `Document`, positive integer `Version`, and ISO calendar `Date`
- `author_identity`, `author_harness_id`, `author_session_context_id`, `author_model`
- `recipient_role: loyal-opposition`
- `Project`, `Work Item`, and the observed integer `work_item_version`
- `target_paths` and `test_artifact_targets`, each a JSON array of exact relative paths
- `spec_versions`, a JSON object mapping applicable formal IDs to the versions you read

Use the returned bound session identifier for `author_session_context_id`. Do not
invent provenance, duplicate metadata keys or include retired permission fields.
List the paths the proposal actually changes, including test artifacts. Changing
a baseline does not authorize editing a generated projection.

## Claim and deliver

Reserve the exact next message using the observed predecessor version (zero for
a fresh attempt) and the status you will author:

```text
gt bridge claim <document> --work-item-id <WI-ID> --native-context-id <context-id> --expected-version <head-version> --status <NEW-or-REVISED> --request-id <unique-request-id> --json
```

Retain the returned fence for this delivery. The claim covers only this next
artifact and expires; it does not reserve the entire work item or chain. Reuse a
request ID only when retrying the identical claim request.

Save your complete UTF-8 message in your current session's scratch directory,
then deliver it unchanged:

```text
gt bridge deliver <document> --native-context-id <context-id> --fence <returned-fence> --content-file <authored-message-file> --json
```

Credential detection refuses delivery without exposing matched values or
consuming the claim. Correct the authored content; the service never silently
redacts or rewrites it. An unavailable authority is a refusal, not a reason to
write a local bridge file or hidden state.

If acknowledgement is uncertain, read the current attempt and retry the exact
same bytes and fence when appropriate. If the claim expired or the predecessor
changed, re-read the current task and attempt before acquiring a new claim. Do
not increment versions automatically or overwrite another message.

Read back the delivered message through `gt bridge show <document> --content
--json`. Delivery ends this claim. Implementation requires an independently
authored GO and the next exact claim; proposal filing does not commit or activate
work. Leave subsequent routing to the owner or dispatcher.
