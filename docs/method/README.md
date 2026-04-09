# GroundTruth Method Documentation

Engineering discipline for AI-powered systems — from specification to production.

## Reading order

| # | Document | Description |
|---|----------|-------------|
| 01 | [Method Overview](01-overview.md) | What GroundTruth is, core workflow, governance model |
| 02 | [Specifications](02-specifications.md) | Writing and managing specifications — the decision log |
| 03 | [Testing](03-testing.md) | Test forms, outside-in testing, pipeline organization |
| 04 | [Work Items & Backlog](04-work-items.md) | Tracking gaps between specs and implementation |
| 05 | [Governance](05-governance.md) | GOV specs, machine-readable rules, enforcement gates |
| 06 | [Dual-Agent Collaboration](06-dual-agent.md) | Prime Builder + Loyal Opposition review cycle |
| 07 | [Session Discipline](07-sessions.md) | Session IDs, wrap-up procedures, audit cadence |
| 08 | [Architecture Decisions](08-architecture.md) | ADR/DCL/IPR/CVR workflow, compliance checking |
| 09 | [Adoption & Promotion](09-adoption.md) | Upstream/downstream model, managed files, update procedures |
| 10 | [KB Tooling](10-tooling.md) | Installation, CLI commands, web UI, configuration |
| 11 | [Operational Configuration Capture](11-operational-configuration.md) | How to capture bridges, automations, directives, and role configuration |

## Architecture documents

| Document | Description |
|----------|-------------|
| [Product Architecture](../architecture/product-split.md) | groundtruth-kb vs groundtruth-project-kit scope split |

## Prerequisites

- Familiarity with software engineering fundamentals (version control, testing, CI/CD)
- A project you want to manage with traceable specifications
- `groundtruth-kb` installed (see [Tooling](10-tooling.md) for install instructions)

## Conventions

- **Generic examples** are used throughout. When you see `SPEC-001` or "TaskTracker", these are illustrative — substitute your own project's domain.
- **Forward references** like "(see [Specifications](02-specifications.md))" point to other documents in this series.
- **Method vs tool**: these documents describe *when* and *why* to do things. For *how* to use the CLI and API, see the KB Tooling guide (coming in a future update).
