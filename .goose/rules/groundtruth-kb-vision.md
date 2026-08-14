<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project goose`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# GroundTruth KB Vision

Source: owner statement, 2026-04-10.

## Canonical Vision Statement

GroundTruth KB exists to create a software factory in which the owner of a
software development project delivers specifications to the pipeline, and the
pipeline produces a production-deployable SaaS application ready for Azure.

During development, the owner's responsibility should be limited to:

1. Adding new specifications.
2. Answering questions that clarify or refine specifications.
3. Making decisions about trade-offs and implementation options.

## Operational Decision Filter

For Loyal Opposition and Prime Builder reviews, proposals, and implementation choices, ask:

> Does this reduce the owner's role to specifications, clarifications, and
> decisions?

Prioritize approaches that:

- Improve specification capture and traceability.
- Automate verification and evidence capture.
- Reduce manual owner supervision of routine implementation or deployment work.
- Preserve decisions, trade-offs, and rationale across sessions and agents.
- Make Azure production readiness a pipeline output rather than an owner-managed checklist.

Deprioritize approaches that require the owner to:

- Manually reconcile specification, test, and implementation drift.
- Inspect generated artifacts for basic correctness that can be automatically checked.
- Remember unresolved process state across agents or sessions.
- Supervise deployment plumbing, CI gates, or release evidence as a routine activity.

If an approach leaves one of those burdens with the owner, the report should say
why, whether it should be automated or specified, and whether an explicit owner
decision is needed.
