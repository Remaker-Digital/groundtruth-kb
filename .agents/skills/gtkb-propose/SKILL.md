---
name: gtkb-propose
description: Compose a complete NEW or REVISED implementation proposal from the assigned work and current native context, then deliver the agent-authored message through the exact next-artifact claim.
metadata:
  project: groundtruth-kb
  category: implementation and planning
---

# Compose an implementation proposal

Use this skill to explain the intended change for work explicitly assigned to
this Prime Builder context. Use `gtkb-bridge-propose` for the full native delivery
procedure and `file-bridge-protocol` for lifecycle and independent review duties.
Load those sources from this harness's generated configuration. The agent writes
the proposal; no helper selects scope, seeds authority, authors decisions or
repairs the header.

## Read current inputs

Use the actual native context identifier and its exact supplied role/activity.
Read `gt session show --native-context-id <context-id> --json` and bind only the
literal supplied init marker if necessary. Read
`gt context work-item <WI-ID> --json` for the work item, its single parent project,
prerequisites, applicable current formal sources, executable test and test plan.
For an existing attempt, also read `gt bridge show <document> --content --json`.

NEW starts a fresh implementation attempt; REVISED follows NO-GO on its existing
attempt. Before NEW, the parent project must be authorized. An interactive
context asks the owner to resolve a missing authorization; headless work follows
the native BLOCKED route. Do not change authorization to make a proposal pass.
A later authorization change does not cancel an initiated chain. Missing scope,
current formal input or executable test must be resolved before proceeding.

## Explain the complete change

Write the intended before/after behavior, governing requirements and rationale;
exact source and test artifact paths; implementation approach and affected
interfaces; removal/supersession effects; dependencies and concurrency; complete
verification commands, expected results and failure/recovery checks; operational
effects and their containment; and justified exclusions. Reconcile any material
unanswered owner choice explicitly. A reference list or structural check is not
substantive review or behavioral evidence.

Use exact relative artifact paths, without glob patterns, generated harness
paths, bridge payloads or temporary state. Read and include the current work-item
version and all applicable formal versions. Do not silently bind a newer version
than the one used to write the proposal. Incorporate needed information directly;
prior deliberations, handoffs and old bridge messages are not current authority.

## Authored header example

Replace every dollar placeholder from the current reads and actual attribution.
Use NEW or REVISED as appropriate, with the next claimed positive version. These
placeholders are explanatory text; the CLI never fills them or invents provenance.
Keep the metadata together before the blank line introducing the complete body.

```text
::init gtkb lo
::open build
$status
bridge_kind: implementation_proposal
Document: $document
Version: $next_version
Date: $date
author_identity: $author_identity
author_harness_id: $harness_id
author_session_context_id: $bound_session_id
author_model: $model
recipient_role: loyal-opposition
Project: $project_id
Work Item: $work_item_id
work_item_version: $work_item_version
target_paths: $target_paths_json
test_artifact_targets: $test_targets_json
spec_versions: $spec_versions_json

$complete_body
```

Project and Work Item are the current canonical identifiers, never permission
carriers. The native service resolves and checks their relationship against the
claim. The envelope addresses the next responder; authored session attribution
uses the returned bound session identifier, not an invented harness role.

## Claim, deliver and read back

Reserve one exact next artifact using the observed head version, intended status
and a unique request ID. Reuse the ID only for the identical retry:

```text
gt bridge claim <document> --work-item-id <WI-ID> --native-context-id <context-id> --expected-version <head-version> --status <NEW-or-REVISED> --request-id <unique-request-id> --json
```

Save the complete UTF-8 message only in `scratchpad/<bound-session-id>` and use
the returned fence. The claim reserves this next artifact, not the work item or
thread. Deliver without modifying another context's files:

```text
gt bridge deliver <document> --native-context-id <context-id> --fence <returned-fence> --content-file <authored-message-file> --json
gt bridge show <document> --content --json
```

Compare exact readback with the authored bytes. A refused header, stale scope or
unavailable authority is not permission to write raw bridge storage. Reconcile
current facts; keep an uncertain acknowledgement distinct from a failed write.
Retry the exact bytes/fence only when current state permits it. Release an
unfinished live claim through the CLI. Independent GO and the next claim are
required before implementation; filing a proposal does not commit or activate it.

Current requirements: DCL-BRIDGE-KIND-TAXONOMY-ENUM-001 and
DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001. Implementation validation is in
the native bridge service; source bindings and a passing parser are only part of
the complete verification duty. The former scaffold and file writer are retired.
