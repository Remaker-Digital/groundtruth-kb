# GroundTruth Method Documentation

Engineering discipline for AI-powered systems — from specification to production.

## Reading order

| # | Document | Description |
|---|----------|-------------|
| 01 | [Method Overview](01-overview.md) | What GroundTruth is, core workflow, governance model |
| 02 | [Specifications](02-specifications.md) | Writing and managing specifications — the decision log |
| 03 | Testing *(coming soon)* | Test forms, outside-in testing, pipeline organization |
| 04 | Work Items & Backlog *(coming soon)* | Tracking gaps between specs and implementation |
| 05 | Governance *(coming soon)* | GOV specs, machine-readable rules, enforcement gates |
| 06 | Dual-Agent Collaboration *(coming soon)* | Prime Builder + Loyal Opposition review cycle |
| 07 | Session Discipline *(coming soon)* | Session IDs, wrap-up procedures, audit cadence |
| 08 | Architecture Decisions *(coming soon)* | ADR/DCL/IPR/CVR workflow, compliance checking |
| 09 | [Adoption & Promotion](09-adoption.md) | Upstream/downstream model, managed files, update procedures |
| 10 | KB Tooling *(coming soon)* | Installation, CLI commands, web UI, configuration |

## Prerequisites

- Familiarity with software engineering fundamentals (version control, testing, CI/CD)
- A project you want to manage with traceable specifications
- `groundtruth-kb` installed (`pip install groundtruth-kb`)

## Conventions

- **Generic examples** are used throughout. When you see `SPEC-001` or "TaskTracker", these are illustrative — substitute your own project's domain.
- **Forward references** like "(see [Specifications](02-specifications.md))" point to other documents in this series.
- **Method vs tool**: these documents describe *when* and *why* to do things. For *how* to use the CLI and API, see the [KB Tooling guide](10-tooling.md) (coming soon).
