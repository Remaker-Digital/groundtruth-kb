# Independent review before implementation

Prime Builder implements an assigned work item's accepted proposal only after an
independent Loyal Opposition context authors GO. Project authorization permits
dispatch; it does not supply review, tests or an exact next-artifact claim.
A claim reserves the next bridge message, never ownership of the work item.

## Current scope and proposal review

Obtain current instructions through `gt context work-item <WI-ID> --json` and
read the assigned attempt with `gt bridge show <document> --content --json`.
Review the actual formal sources, the work item's single project membership,
prerequisites, proposed artifact paths and linked executable test plan.

The implementation proposal must identify all applicable formal requirements
and explain how its tests establish the intended behavior. Its Requirement
Sufficiency section states whether the current requirements are sufficient or
what must be corrected before implementation. Missing requirements and missing
executable checks remain unresolved work; do not invent a waiver, omit a
requirement or interpret a passing subset as complete coverage.

Loyal Opposition independently evaluates the proposed design, scope and tests.
Consider deletion, consolidation or a simpler direct correction before adding
mechanisms. State the actual simpler alternative considered and why the chosen
change is necessary. Use GO for an acceptable proposal and NO-GO for a proposal
requiring revision. A report is reviewed with VERIFIED or NOT-READY instead.

Read-only investigation, proposal authoring and running existing tests can
establish the evidence needed for review. They do not make implementation
reviewed. Owner-directed canonical changes use the applicable domain operation;
they do not require inventing an implementation proposal for each permission or
decision. Live operational work retains its bounded execution scope and
independent verification requirements.

## Independence and attribution

Roles belong to immutable initialized session contexts. The exact supplied init
marker establishes the context's role. Use the current bound session identifier
in authored provenance. A context cannot review its own proposal or verify its
own implementation report. Missing or contradictory attribution is a defect to
resolve before a formal verdict.

No harness has a permanent role or owns a review. A different harness name does
not prove independence, and another harness's configuration is not a source of
state or guidance. Fresh contexts reconstruct work through the CLI and the
delivered bridge message, without direct harness coordination.

## Implementation verification and project commit

Prime Builder implements only the accepted source and test scope in its claimed
checkout, runs the required tests, publishes through `gt bridge publish-work`
and authors READY with the actual result. A helper never authors its header,
selects its next version or turns a report into NEW.

Loyal Opposition reads current requirements, independently checks the actual
work and executes the required test plan. Verify every affected requirement,
including necessary negative, concurrency and recovery behavior. State what ran,
what passed, any failure and the scope of the evidence. A required untested or
failed condition prevents VERIFIED. Use `gt bridge artifacts <document> --json`
to identify the exact reviewed bytes; the blob map is not itself a review.

Author VERIFIED before project commit. Hold the work until all project members
are independently VERIFIED. The verifying context then uses `gt projects commit`
for the complete reviewed project, with every retiring work item cited as
`(WI-NNNN)`. Normal hooks run. Bridge messages, generated configurations and
unrelated work are excluded. Commit establishes activation and terminality.

Changed reviewed bytes or a failed commit require the canonical fresh-review
route. The dispatcher selects that work and authors no proposal or verdict.
Do not reset Git history, reuse stale review evidence or fabricate a completion
message. A context that performs an operational mutation cannot independently
verify that same operation.

## Owner input

Apply an owner's decision to the relevant canonical source or current agent
direction. Session logs retain the conversation for later harvest when needed.
Do not demand permission histories, prior-deliberation sections or copied
question-and-answer evidence in bridge messages. Those records do not authorize
implementation and cannot replace current project, work-item or formal state.

Use the `gtkb-bridge` skill for the authored-message, exact-claim, publication,
review and recovery commands. If an interface rejects lawful work or lacks a
required capability, identify and correct that defect without manufacturing an
alternate authority or silently claiming success.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
