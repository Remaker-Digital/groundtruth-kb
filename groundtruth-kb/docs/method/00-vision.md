# 0. Vision

> For a concrete walkthrough of this vision in practice, see
> [The User Journey](../user-journey.md).

GroundTruth KB exists to support a software factory: the owner of a software
development project delivers specifications to the pipeline, and the pipeline
produces a production-deployable SaaS application.

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

## Scope of the "production-deployable SaaS" claim

"Produces a production-deployable SaaS application" names the outcome the
method is designed to support, not an end-to-end deployment service owned by
GroundTruth-KB. Concretely, GT-KB produces **governed readiness
specifications, decision prompts, ADR templates, and verification checks**
— the artifacts that force every cloud-readiness question into a traceable
workflow. The CI/CD pipeline that builds and deploys the application, and
the Azure (or other cloud) resource definitions themselves, remain owned
and operated by the adopting team. See
[Azure Enterprise Readiness Taxonomy](../reference/azure-readiness-taxonomy.md)
for the full readiness-envelope boundary, tiers, and category catalog.
