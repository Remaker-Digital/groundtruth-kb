---
name: GroundTruth scope and direction
description: GroundTruth is a complete concept-to-production engineering method, not just a KB tool. Iterative feedback loop. Multi-project and multi-owner support planned.
type: project
---

## What GroundTruth is

A complete, self-contained engineering method that takes a project from clean sheet to production deployment. Requires only GitHub, Claude/Codex, Azure, and groundtruth-kb. No additional tools or componentry.

Evolves from membase-4-claude. The flow is a bidirectional feedback loop:
1. Find useful 3rd party ideas/artifacts
2. Augment Agent Red infrastructure with them
3. Battle-test in production
4. Extract and publish as GroundTruth for community
5. Community adopts and uses
6. Usage generates feedback and insights
7. Insights improve the pipeline/process
8. Publish improved version, repeat

## What groundtruth-kb must ship

- **Method documentation:** spec-first workflow, GOV rules, test discipline, assertion model, ADR/DCL governance, review process (Claude + Codex roles)
- **KB tooling:** append-only DB, web UI, assertions engine, CLI
- **Process templates:** CLAUDE.md template, hooks (spec-classifier, assertion-check), skills (kb-query, kb-spec, etc.)
- **CI/CD templates:** build, test, deploy workflows for Azure Container Apps
- **Bootstrap guide:** step-by-step from init repo to first production deploy
- **Example project:** small but complete — concept through production

## Why this scope

- **Feedback instrument:** publication generates the adoption signal that reveals where the method works, fails, and needs to grow. Community usage gauges deviation from competing pipelines and identifies improvement opportunities.
- **Multi-project:** other humans in the org will need isolated environments running the same pipeline for peer projects. groundtruth-kb must support this without modification.
- **Multi-owner (future):** protocol and infrastructure for adding a second human developer/owner to a project needs to be clarified. Not immediate, but the method must not assume single-owner forever.

## How to apply

- G3 scope is NOT "extract tools/knowledge-db into a pip package." It is "extract and document the entire engineering method as a reproducible system."
- Effort estimate is significantly higher than the original 3-4 sessions.
- The bootstrap guide and example project are the critical missing pieces — everything else exists inside Agent Red but needs generalization.
- Agent Red remains the canonical proving ground. groundtruth-kb extracts from it.
- Canonical repo: Remaker-Digital/groundtruth-kb (AGPL).

## Owner decisions recorded (S237)

- Repo: Remaker-Digital/groundtruth-kb
- License: AGPL
- Target stack: GitHub + Claude/Codex + Azure (no other dependencies)
- Multi-owner protocol: deferred but acknowledged as future requirement
