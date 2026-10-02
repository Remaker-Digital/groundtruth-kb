# GroundTruth KB Vision

## Purpose

GT-KB exists to cure agent context drift. It loads each ephemeral context with
the baseline knowledge and task information it needs. GT-KB is efficacious when
agents loaded this way create work items that other agents can use to produce
work product (artifacts or state changes) that matches the applicable
specifications and passes the predefined tests. Drift shows in work product and
bridge messages. Once GT-KB reliably completes such corrective work on itself,
the owner moves GT-KB's own development to GT-KB agents.

## Canonical Vision Statement

Source: owner statement, 2026-04-10. It remains the long-range aim.

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
>
> Does this help the next agent create or use such a work item?

Prioritize approaches that:

- Improve specification capture and traceability.
- Automate verification and evidence capture.
- Reduce manual owner supervision of routine implementation or deployment work.
- Carry decisions in the formal records, projects and work items they change.
- Make Azure production readiness a pipeline output rather than an owner-managed checklist.

Deprioritize approaches that require the owner to:

- Manually reconcile specification, test, and implementation drift.
- Inspect generated artifacts for basic correctness that can be automatically checked.
- Remember unresolved process state across agents or sessions.
- Supervise deployment plumbing, CI gates, or release evidence as a routine activity.

If an approach leaves one of those burdens with the owner, the report should say
why, whether it should be automated or specified, and whether an explicit owner
decision is needed.
