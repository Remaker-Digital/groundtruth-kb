# GroundTruth Knowledge DB

A specification-driven governance toolkit for AI engineering teams.

Track specifications, tests, work items, and architecture decisions with
append-only versioning. Built for teams that need traceable, auditable
engineering decisions.

## At a Glance

| Capability | Description |
|-----------|-------------|
| **Specifications** | Decision log for what the system must do |
| **Tests** | Verify implementation meets specifications |
| **Work Items** | Track gaps between specs and implementation |
| **Architecture Decisions** | ADR/DCL workflow for cross-cutting choices |
| **Assertions** | Continuously verify spec-implementation alignment |
| **Governance Gates** | Pluggable enforcement at lifecycle transitions |

## Architecture

```
Layer 3: Workstation Doctor    gt project doctor
Layer 2: Project Scaffold      gt project init / upgrade
Layer 1: Core Knowledge DB     gt init / seed / assert / serve
         File Bridge Setup     dual-agent coordination templates [optional]
```

## Quick Start

```bash
pip install "groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.3.0"
gt project init my-project --owner "Your Organization" --init-git
gt --config my-project/groundtruth.toml summary
```

See the [Bootstrap Guide](bootstrap.md) for a complete 10-step walkthrough.

## Tooling

- **CLI** (`gt`) — init, seed, assert, summary, history, config, serve, project management
- **Web UI** — read-only dashboard with branding, filtering, and assertion results
- **Python API** — direct database access for automation and CI/CD
- **Project Scaffolding** — three profiles for different team configurations
- **CI Templates** — test, build, and deploy workflow templates
- **Process Templates** — CLAUDE.md, MEMORY.md, hooks, and rules
- **File Bridge Setup** — dual-agent coordination templates (Prime Builder + Loyal Opposition)
