# 0. Vision

GroundTruth KB exists to support a software factory: the owner of a software
development project delivers specifications to the pipeline, and the pipeline
produces a production-deployable SaaS application ready for Azure.

During development, the owner's responsibility should be limited to:

1. Adding new specifications.
2. Answering questions that clarify or refine specifications.
3. Making decisions about trade-offs and implementation options.

## Operational Interpretation

This vision is a prioritization rule for design, implementation, and review.
Prefer choices that move routine execution burden from the owner into
specifications, automated checks, agent workflows, traceability, and deployment
evidence.

Down-rank approaches that require the owner to supervise deployment plumbing,
manually reconcile spec/code drift, inspect generated artifacts for basic
correctness, or remember process state across agents. Treat those requirements
as design smells unless the owner explicitly chooses them as a trade-off.

For Prime Builder and Loyal Opposition work, use this decision filter:

> Does this reduce the owner's role to specifications, clarifications, and
> decisions?

If the answer is no, the report or proposal should identify what owner burden
remains, why it remains, and whether it should be automated, specified, or
accepted as an explicit owner decision.
