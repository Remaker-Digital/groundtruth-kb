# GroundTruth Knowledge DB

[![CI](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/codeql.yml/badge.svg)](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/codeql.yml)
[![Security](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/security.yml/badge.svg)](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/security.yml)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=mike-remakerdigital_groundtruth&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=mike-remakerdigital_groundtruth)
[![PyPI](https://img.shields.io/pypi/v/groundtruth-kb.svg)](https://pypi.org/project/groundtruth-kb/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

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

**Tooling:** CLI (`gt`), Web UI, Python API, project scaffolding,
CI templates, process templates, dual-agent file bridge setup.

## Architecture

```
Layer 3: Workstation Doctor    gt project doctor
Layer 2: Project Scaffold      gt project init / upgrade
Layer 1: Core Knowledge DB     gt init / seed / assert / serve
         File Bridge Setup     dual-agent coordination templates [optional]
```

See the [product architecture](docs/architecture/product-split.md) for details.

## Quick Start

```bash
# Install from PyPI
pip install groundtruth-kb

# Create a project with scaffolding
gt project init my-project --owner "Your Organization" --init-git

# Inspect the seeded knowledge base
gt --config my-project/groundtruth.toml summary

# Run assertions
gt --config my-project/groundtruth.toml assert
```

**Web UI** (requires `[web]` extra):

```bash
pip install "groundtruth-kb[web]"
gt --config my-project/groundtruth.toml serve
# Visit http://localhost:8090
```

**Same-day prototype** (includes example data):

```bash
gt bootstrap-desktop my-prototype --owner "Your Organization" --init-git
```

> **New to GroundTruth?** Read [The User Journey](docs/user-journey.md) to see
> what building a product with GroundTruth looks like end-to-end. Then follow
> the [getting started guide](docs/bootstrap.md) for a 10-step technical walkthrough.

## Why?

AI-powered systems change fast. Without traceable specifications and
assertions, teams lose track of what was decided, why, and whether the
implementation still matches. GroundTruth provides the engineering
discipline layer.

## Status

This project is in early development. The toolkit is extracted from a
production system managing 2,000+ specifications and 11,000+ tests.

Project scaffolding (`gt project init`), environment verification
(`gt project doctor`), and scaffold upgrades (`gt project upgrade`) are
available. Three profiles support different team configurations:
`local-only`, `dual-agent`, and `dual-agent-webapp`.

## Documentation

The [method documentation](docs/method/README.md) describes the engineering
discipline behind GroundTruth:

| Guide | Topic |
|-------|-------|
| [01 — Overview](docs/method/01-overview.md) | Core workflow and governance model |
| [02 — Specifications](docs/method/02-specifications.md) | Writing and managing specifications |
| [03 — Testing](docs/method/03-testing.md) | Test forms, outside-in testing, pipeline organization |
| [04 — Work Items](docs/method/04-work-items.md) | Gap tracking, stage lifecycle, prioritization |
| [05 — Governance](docs/method/05-governance.md) | GOV specs, gates, assertions, protected behaviors |
| [06 — Dual-Agent](docs/method/06-dual-agent.md) | Prime Builder + Loyal Opposition collaboration |
| [07 — Sessions](docs/method/07-sessions.md) | Session IDs, wrap-up, audit cadence |
| [08 — Architecture](docs/method/08-architecture.md) | ADR/DCL/IPR/CVR workflow |
| [09 — Adoption](docs/method/09-adoption.md) | Upstream/downstream model, update procedures |
| [10 — Tooling](docs/method/10-tooling.md) | CLI commands, web UI, Python API, configuration |
| [11 — Operational Config](docs/method/11-operational-configuration.md) | Bridges, automations, directives, roles |
| [12 - File Bridge Automation](docs/method/12-file-bridge-automation.md) | Durable file bridge polling, prompts, plugins, skills, and scheduler capture |

**Reference:**
[Assertion Language](docs/reference/assertion-language.md) |
[Desktop Setup](docs/desktop-setup.md) |
[Example Project](examples/task-tracker/WALKTHROUGH.md)

## Getting Started

New to GroundTruth? The [getting started guide](docs/bootstrap.md) walks you
through setting up the core toolkit: install, init, first spec, first test,
assertions, web UI, templates, and CI/CD — in 10 steps.

For a same-day client workstation setup, start with the
[desktop setup guide](docs/desktop-setup.md).

## Process Templates

The [templates/](templates/README.md) directory contains reference templates
for setting up a GroundTruth project: rules files, state files, hooks, and
agent configuration, including a file bridge OS-poller setup prompt. Use
`gt project init my-project --profile <profile>` for automated setup, or copy templates
manually and customize the placeholders.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute. We especially
value feedback about the engineering method itself — tag issues with
`method-feedback`.

## License

[AGPL-3.0](LICENSE)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
