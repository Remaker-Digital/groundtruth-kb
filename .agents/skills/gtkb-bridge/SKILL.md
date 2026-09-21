---
name: gtkb-bridge
description: Progress explicitly dispatched GT-KB work through authored bridge messages, exact next-artifact claims, implementation, independent review and complete-project finalization using the native CLI.
---

# Progress a bridge attempt

Use the configured native authority and the role bound to this context's exact
supplied init marker. The owner or dispatcher selects the work. A queue is an
orientation aid, not an instruction to select another target. Use only this
context's identity and checkout; no other harness is a source of instructions,
state, capacity or review authority.

## Bind the supplied context

When this native context is not already bound, use the actual native context
identifier provided by the harness and the exact init line supplied in the task:

```text
gt session bind --native-context-id <context-id> --init-keyword "<exact-supplied-init-line>" --json
gt session show --native-context-id <context-id> --json
```

Read back the immutable identity and role. Identical retries resolve the same
binding. Never infer an init line or role from a provider, model, skill, registry
row or inherited environment variable. If the native identifier or supplied
init/activity is missing, resolve that input before a state-changing operation.
The harness transports instructions and tools; it does not create role records.

## Read the assigned work

Read `gt context work-item <WI-ID> --json` for the current work item, its one
parent project, formal sources, executable test, test-plan instructions and
prerequisites. Read `gt bridge show <document> --content --json` for the current
attempt and its available message chain. `gt bridge queue --role <pb-or-lo>
--json` and `gt bridge state-report --json` provide current coordination views.

For an owner-selected bridge workload launched through the OpenRouter, Ollama
or Alibaba provider CLI, supply both `--bridge-document <document>` and
`--bridge-version <exact-successor-version>`. A bridge-review or verification
skill also requires that explicit pair. The provider verifies the exact delivered
successor through the native CLI before reporting successful completion; final
prose cannot replace delivery. An init marker establishes context only. It does
not select a bridge target or require a bridge response for ordinary non-bridge
work. The launcher preserves the complete owner prompt and never extracts an
assignment from prose, a queue or a prior context.

The delivered message identifies the next task; reconstruct current requirements
from their canonical sources before acting. Bridge content is disposable and
cannot establish durable authority or substitute for current work/project state.
Resolve incomplete or contradictory requirements without inventing a parent,
permission record, owner decision or completed result.

## Choose the lawful response

| Received state | Receiving role and next authored response |
|---|---|
| NEW or REVISED | Loyal Opposition reviews the proposal and authors GO or NO-GO. |
| NO-GO | Prime Builder addresses the rejection in REVISED. |
| GO | Prime Builder implements the accepted scope and authors READY. |
| READY | Loyal Opposition independently tests the work and authors VERIFIED or NOT-READY. |
| NOT-READY | Prime Builder corrects the work/report and authors READY. |
| VERDICT-REJECTED | A Loyal Opposition context independently corrects the rejected verdict using the current proposal or report phase. |

Prime Builder may reject a noncompliant, PB-addressed GO, NO-GO or NOT-READY
with VERDICT-REJECTED. WITHDRAWN closes a pre-GO attempt; SUPERSEDED records
canonical evidence that the scoped subject no longer exists. Neither substitutes
for implementing live work. BLOCKED is the headless pre-proposal response to a
parent that is not authorized. ADVISORY carries no execution authority.

VERIFIED is completion of independent review of exact bytes. It is not a commit
or a dispatchable message. Fresh verification after changed bytes or a failed
project commit is selected from canonical coordination state; the dispatcher
authors no verdict. A material formal-intent change after VERIFIED requires
an explicit abandonment/restart through the CLI and a fresh NEW proposal,
independent GO, implementation and verification on the same uncommitted work
item. Preserve its membership and existing work; do not reuse the old GO or
create a replacement work item. Resolve current claims and any possible Git
integration before restarting. Committed work remains terminal.

## Author and deliver the next message

For NEW or REVISED, use `gtkb-bridge-propose` and its current task-context and
observed-version requirements. Check the parent's authorization only before NEW.
Later responses use the initiated chain; do not recreate authorization checks.

Every message is authored in full by the agent. A dispatchable head contains its
status, the next recipient's `::init gtkb <pb-or-lo>`, and `::open <activity>` as
the first three nonblank lines. Metadata follows before the body. Include
`bridge_kind`, `Document`, `Version`, `Date`, `author_identity`,
`author_harness_id`, `author_session_context_id`, and the actual `author_model`;
placeholder model values are refused. NEW, REVISED and BLOCKED also require
`Project` and `Work Item`. Other successors use the exact claimed attempt;
optional repeated linkage must match it. Dispatchable messages also name
`recipient_role` as `prime-builder` or `loyal-opposition`. Non-dispatchable
messages omit both envelope lines and the recipient field. Advisory author
provenance remains mandatory. Supply each key once.
READY uses `bridge_kind: implementation_report`; verdicts use `lo_verdict`.
The service validates the complete message without composing or repairing it.

Reserve the exact next artifact, using the predecessor version you read:

```text
gt bridge claim <document> --work-item-id <WI-ID> --native-context-id <context-id> --expected-version <head-version> --status <authored-status> --request-id <unique-request-id> --json
```

Retain the returned fence. This expiring claim reserves one message, not the
work item or thread. Use `gt bridge check <document> --native-context-id
<context-id> --fence <fence> --json` before a protected effect. Save the complete
UTF-8 message in this session's scratch directory, then deliver it:

```text
gt bridge deliver <document> --native-context-id <context-id> --fence <fence> --content-file <message-file> --json
```

Credential matches cause a refusal without disclosing the value, consuming the
claim or rewriting the message. Correct the authored content. If acknowledgement
is uncertain, read back the attempt and retry identical bytes and fence when
appropriate; do not manufacture a new version. Delivery consumes the claim.
Read back the result with `gt bridge show <document> --content --json`.

The tool gate uses the native service through `gt bridge check-effects
--native-context-id <context-id> --cwd <actual-tool-directory> --path <target>
--json`; repeat `--path` for each concrete effect. It checks the current binding,
exact live implementation claim, current inputs and registered checkout at the
moment of the call. Scratch drafts stay in `scratchpad/<bound-session-id>`.
This read-only check creates no permission record and does not replace the exact
fence required by work publication or bridge delivery. If it refuses an effect,
correct the identified scope, claim or service condition before retrying.

## Implement and report

After GO, the dispatched Prime Builder claims READY and opens its checkout:

```text
gt bridge worktree <document> --native-context-id <context-id> --fence <fence> --json
```

Work inside the returned checkout on the accepted source and test targets. Save
the returned `artifact_preimages` object as JSON in session scratch; it is the
expected preimage for publishing that work, not a permission or authority record.
Run the linked test plan and inspect the actual result against the requirements.
Publish only this claim's artifacts:

```text
gt bridge publish-work <document> --native-context-id <context-id> --fence <fence> --preimages-file <artifact-preimages-json> --json
```

Author READY with the actual changes, tests, results and remaining limitations.
Do not generate NEW as an implementation report, copy another author's header,
claim successful tests that were not run, or commit per message.

## Independently verify and finalize

Loyal Opposition loads current requirements and work through the CLI and its
own claimed checkout, performs the applicable review and tests, and obtains
`gt bridge artifacts <document> --json`. This reports each path's Git mode and normalized object ID;
it does not perform the review. VERIFIED includes `verified_artifacts` containing
the exact reviewed JSON map, for example
`{"code.py":{"mode":"100755","object_id":"<Git object ID>"}}`; deletion is
represented by `null`. An executable-bit-only change invalidates the review. Changed or forbidden scope must be
reconciled before further effects; no old claim or snapshot grants an exception.

When the service reports that every member is independently VERIFIED, the
verifying context reads current project state and commits the complete project:

```text
gt projects commit <project-id> --native-context-id <context-id> --expected-version <project-version> --message-file <authored-commit-message> --json
```

The message cites every retiring work item as `(WI-NNNN)`. Normal hooks run;
bridge content, generated configurations and unrelated work stay outside the
work-product commit. The CLI prepares the reviewed cohort, commits and confirms
the Git fact. Follow its typed failure and fresh-review results. After an
uncertain confirmation, inspect Git and current state and use
`gt projects confirm-commit --help` to confirm the same commit; do not create a
second commit or reset history. Project commit establishes activation and
terminality; producing generated configurations is a separate operational task.

## Interrupted or invalidated work

Release an unfinished claim with `gt bridge release <document>
--native-context-id <context-id> --fence <fence> --json`. A fresh context reads
canonical work and attempt state and obtains its own next-artifact claim.

A changed predecessor, expired claim or invalid stored target requires a fresh
read and a lawful response. Where canonical state demonstrates a broken or
invalidated non-VERIFIED attempt and no live claim remains, use `gt bridge
abandon --help` for the supported abandonment operation and begin a fresh NEW
from current requirements. Do not inherit GO, claims or effects from discarded
messages. An unavailable authority never justifies local file publication or
hidden state. Leave subsequent dispatch to the owner or dispatcher.

## Confirm delivery before reporting completion

After authoring and delivering the assigned successor, verify the canonical
result with:

```sh
gt bridge check-delivery <document> --version <authored-version> --native-context-id <context-id> --json
```

The check reads current canonical state and proves the exact document/version
was delivered by this context. A held or released claim, unrelated delivery,
final model prose or unavailable authority cannot satisfy it. It writes no
message and changes no claim or work state. Missing proof returns typed
`bridge_delivery_incomplete`; recover through current CLI facts, never by
having a harness author, repair or publish the message.

After terminal cleanup, only the final delivery's immutable author-context
identifier joins the minimum terminal identity. The message payload and earlier
authors are purged. An earlier delivery that has already been purged cannot be
proved by this readback and returns incomplete rather than inventing retained
evidence. Headless provider launchers receive the assigned document and exact
successor version explicitly; those values identify work, not authorization.
