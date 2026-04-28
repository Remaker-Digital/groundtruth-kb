---
name: Pipeline vision statement
description: Owner-defined vision for the groundtruth-kb pipeline — software factory that produces deployable SaaS from specifications
type: project
---

"To create a software factory, in which the owner of a software development project delivers specifications to the pipeline, and the pipeline produces a production-deployable SaaS application ready for Azure. During development, the owner's responsibility should be limited to adding new specifications, answering questions that clarify or refine specifications or making decisions about trade-offs and implementation options."

— Mike, 2026-04-10

## How to Apply

Every implementation choice should be evaluated against three criteria derived from this vision:

1. **Does it move the pipeline toward producing deployable SaaS from specifications?** If yes, prioritize. If tangential, defer.

2. **Does it reduce what the owner needs to do beyond specs, clarifications, and trade-off decisions?** Automation that removes owner burden serves the vision. Manual processes that require owner involvement for routine work violate it.

3. **Does it make the pipeline more general or more project-specific?** The vision describes a factory (N projects), not a workshop (1 project). Favor generality unless there's a concrete reason to specialize.

## Decision Examples

- **Deliberation archive in groundtruth-kb** (not MemPalace): serves criterion 1 (pipeline capability) and 3 (general, not Agent Red-specific)
- **Session harvest hook**: serves criterion 2 (automates context capture the owner would otherwise have to ensure)
- **Specification scaffold**: serves criterion 1 (specifications as input) and 3 (reusable across projects)
- **Pester Protocol**: serves criterion 2 (owner doesn't have to manually relay between agents)
