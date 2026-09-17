# Bridge protocol and project completion

Bridge messages carry the next assigned task. Current specifications, projects,
work items, tests and completion state come from the authoritative database
through the CLI. A bridge message is not a durable specification, owner decision
record, permission record or evidence that a Git commit exists.

Use the canonical `gtkb-bridge` skill for command details, `gtkb-proposal-review`
for proposals and `gtkb-verify` for implementation reports. Load each skill from
this harness's own generated configuration. Do not load a peer harness's rules,
settings, helpers or session state.

## Context and assigned work

Use only the exact init marker supplied by the owner or dispatched message.
Bind the receiving native context with `gt session bind`, then read the immutable
binding through `gt session show`. A harness, model, environment variable or
previous context does not assign this context's role. The supplied activity is
explicit; do not infer one from a queue or helper.

Read `gt context work-item <WI-ID> --json` and
`gt bridge show <document> --content --json`. Resolve current formal requirements,
the single parent project, prerequisites, executable test and full test-plan
instructions. Report missing or contradictory requirements. Do not silently
omit them or use historical messages as replacement authority.

Programs sequence projects and grant no execution authority. Projects group
interdependent work that completes and commits together. Each work item belongs
to one project. The project's authorization field gates initial dispatch and
NEW proposal delivery; it does not invalidate an already initiated bridge chain.
Project authorization is separate from review, concurrency and effect checks.
Until Dispatcher Next is qualified and activated, the owner selects work.

## Claim one next artifact

Use `gt bridge claim` with this native context, the exact observed head version,
the intended response and a unique request identifier. Retain the returned fence.
The claim reserves one next artifact; it never owns a work item or thread.
Another fresh context can continue from the canonical result.

Before a protected effect, use `gt bridge check` with that document, native
context and fence. Obtain the context's checkout through `gt bridge worktree`.
Keep work within its returned paths and preserve unrelated bytes. The service
rechecks current scope and claims; an old GO or prior successful check cannot
supply permission after the relevant inputs or reservation change.

Publish implementation artifacts through `gt bridge publish-work`, using the
preimages returned when loading the checkout. Then author the READY report.
Do not directly change another context's checkout or use a peer's scratch space.
Release an unfinished claim through the CLI. After interruption or uncertain
results, read current canonical state before retrying; never inherit a lost
claim, abandoned attempt or discarded GO.

## Author the complete message

The agent authors every proposal and verdict. Dispatcher selects work and
maintains coordination state; it never writes a proposal or verdict.

A dispatchable head contains exactly one status token and the receiving role's
`::init gtkb <pb|lo>` and canonical `::open <activity>` within its first three
nonblank lines. These lines may occur in any order. The receiving role is the
next responder, not the author. A non-dispatchable head omits both envelope
lines and `recipient_role`.

Author each metadata key exactly once: `bridge_kind`, Document, Version, Date,
`author_identity`, `author_harness_id`, `author_session_context_id` and
`author_model`. Dispatchable messages also carry `recipient_role` as
`prime-builder` or `loyal-opposition`. Use the canonical binding returned to this
context for authored session attribution. A native runtime identifier is not
that canonical binding.

NEW, REVISED and BLOCKED identify Project and Work Item with plain canonical
metadata lines. Other lifecycle messages inherit the exact claimed relationship;
if they repeat those identifiers, the values must match. An unscoped ADVISORY
does not acquire work-item membership by citing work in prose. A NEW or REVISED
proposal carries its exact `target_paths`, `test_artifact_targets`, observed
`work_item_version` and `spec_versions`. Use the current CLI context to obtain
these versions. State the intended result, governing requirements, affected
artifacts, implementation approach, complete verification plan and justified
exclusions. Do not invent authority identifiers or silently update the proposal
to newer inputs its author has not reviewed.

Save the complete UTF-8 message in this context's scratch directory and use
`gt bridge deliver` with the document, native context, fence and content file.
Read back the result. The service validates and stores authored content without
filling provenance, rewriting headers, allocating a different authored version,
appending disclosures or changing the message body. Correct a refused message
from current facts and retry through the CLI. Do not write raw bridge storage.

## Canonical bridge kinds

| Authored status | Required bridge_kind |
|---|---|
| NEW, REVISED | implementation_proposal |
| GO, NO-GO, NOT-READY, VERIFIED, SUPERSEDED | lo_verdict |
| READY | implementation_report |
| ADVISORY | governance_advisory |
| VERDICT-REJECTED | governance_review |
| BLOCKED, WITHDRAWN | operational_state_change |

The native taxonomy maps each current status to one kind. Retired aliases and
index reconciliation cannot be authored as a current kind. A kind does not
change role, routing, authorization, claim or lifecycle rules. Historical text
remains inert; do not rewrite it or infer a successor from an obsolete kind.

## Statuses and review

| Status | Author | Next responder |
|---|---|---|
| NEW, REVISED | Prime Builder | Loyal Opposition |
| GO, NO-GO | Loyal Opposition | Prime Builder |
| READY | Prime Builder | Loyal Opposition |
| NOT-READY | Loyal Opposition | Prime Builder |
| VERDICT-REJECTED | Prime Builder | Loyal Opposition |
| VERIFIED, SUPERSEDED | Loyal Opposition | None |
| WITHDRAWN, BLOCKED | Prime Builder | None |
| ADVISORY | Either role | None |

The ordinary chain is NEW proposal, GO, implementation, READY report, independent
verification and VERIFIED. NO-GO rejects a proposal and requires REVISED.
NOT-READY rejects a report and requires corrected READY. READY carries
`bridge_kind: implementation_report`; verdicts use `lo_verdict`. NEW is never an
implementation report.

VERDICT-REJECTED addresses a governance defect in a PB-addressed GO, NO-GO or
NOT-READY. It is not a way to reject a terminal or non-dispatchable message.
WITHDRAWN ends a pre-GO attempt. SUPERSEDED closes work whose scoped subject is
no longer live, with canonical abandonment and the disposition of any residual
work; it is not verification. BLOCKED is the headless initial refusal when the
parent is not authorized. In an interactive session, ask the owner instead.
ADVISORY is informational and never supplies execution authority.

Historical nonconforming messages, including NO-ACTION and DEFERRED, are readable
only with their actual status and disposition. Obsolete statuses do not become current aliases or grant
claims, implementation readiness or completion. Never fabricate a transition or
repair another author's provenance to keep an obsolete chain running.

Review must be independent of the implementing context. Test the specified
behavior against the actual work product, including relevant refusals,
concurrency, preservation and recovery. Report executed commands or inspections,
observed results and limitations honestly. A passing narrow suite is not proof
of a complete proposal. For operations, the verifier must not perform the
operation it verifies. An evidence anchor or asserted test result is not proof
that the cited behavior was inspected or executed.

## Lawful successors

Use this relation with current claim, role, scope and review checks. A listed
successor does not waive those checks. The active
SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001 defines the contract; the package vocabulary
is its single implementation relation.

| Current status | Permitted next status |
|---|---|
| start | NEW, BLOCKED, ADVISORY |
| BLOCKED | NEW, WITHDRAWN |
| NEW, REVISED | GO, NO-GO, WITHDRAWN, SUPERSEDED |
| NO-GO | REVISED, WITHDRAWN, VERDICT-REJECTED, SUPERSEDED |
| GO | READY, VERDICT-REJECTED, SUPERSEDED |
| READY | VERIFIED, NOT-READY, SUPERSEDED |
| NOT-READY | READY, VERDICT-REJECTED, SUPERSEDED |
| VERDICT-REJECTED | GO, NO-GO, NOT-READY, SUPERSEDED |
| VERIFIED | VERIFIED |
| ADVISORY | ADVISORY |
| WITHDRAWN, SUPERSEDED | None |

VERIFIED to VERIFIED requires canonical fresh-verification work after changed
reviewed bytes or a failed project commit. It grants no proposal or implementation
permission for new formal intent. ADVISORY remains an advisory-only chain.

## Verification precedes the project commit

VERIFIED records independent review of exact final work product. Include the
`verified_artifacts` map from the CLI only after reviewing and testing the bytes
it identifies. VERIFIED is not a commit and does not make the work terminal.
Leave reviewed work uncommitted while any sibling still needs verification.

When canonical state reports the entire project ready, the independent verifying
context uses `gt projects commit` with the current project version and its
authored commit-message file. Cite every retiring work item as `(WI-NNNN)`.
Normal Git hooks run. The one project commit contains the complete reviewed
work product and excludes bridge payloads, generated projections and unrelated
changes. Confirmed Git state establishes activation and terminality; publication
provides durability. Do not create per-verdict commits or archive bridge content
in Git.

Changed reviewed bytes require fresh review of the affected work. A failed
project commit is typed canonical finalization state, not a Dispatcher verdict.
After an uncertain acknowledgement, inspect Git and use the CLI to confirm the
same commit. Never reset history, manufacture a second commit or reuse stale GO.
Material formal-intent change after VERIFIED and before commit requires a fresh
proposal, independent proposal review, implementation and verification attempt on
the same uncommitted work item, preserving its membership and existing artifact
bytes. Close the obsolete attempt through the canonical CLI and start NEW from
current formal requirements. Do not reuse the old GO, fabricate WITHDRAWN or
create a replacement work item. Committed work remains terminal.

Terminal cleanup purges bridge payloads and retains only the minimum identity,
disposition, commit identity and time required to prevent replay. Out-of-band
backups provide recovery. Owner decisions change authoritative state and agent
direction directly; interactive logs retain their conversational history.
