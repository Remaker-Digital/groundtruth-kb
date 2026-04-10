# GroundTruth Knowledge DB

A specification-driven governance toolkit for AI engineering teams.

Track specifications, tests, work items, and architecture decisions with
append-only versioning. Built for teams that need traceable, auditable
engineering decisions.

## What is this?

GroundTruth implements a method for managing AI system quality:

1. **Specifications** describe what the system must do (decision log, not build spec)
2. **Tests** verify that the implementation meets the specifications
3. **Work items** track the gap between specs and implementation
4. **Architecture decisions** (ADRs) record cross-cutting technical choices
5. **Assertions** continuously verify that specs and implementation stay aligned

Everything is stored in an append-only SQLite database with full version
history. No UPDATE, no DELETE — every change is a new version.

groundtruth-kb is the **core toolkit** — it manages the knowledge database,
governance gates, assertions, and project scaffolding.  See the
[product architecture](docs/architecture/product-split.md) for details.

## Quick start

```bash
# Install from GitHub (not published to PyPI)
pip install "groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.1.2"

# Bootstrap a desktop-ready prototype project
gt bootstrap-desktop my-project --owner "Your Organization" --init-git

# Inspect the seeded project
gt --config my-project/groundtruth.toml summary

# Open the web UI (requires [web] extra)
pip install "groundtruth-kb[web] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.1.2"
gt --config my-project/groundtruth.toml serve
# Visit http://localhost:8090
```

## Why?

AI-powered systems change fast. Without traceable specifications and
assertions, teams lose track of what was decided, why, and whether the
implementation still matches. GroundTruth provides the engineering
discipline layer.

## Status

This project is in early development. The toolkit is extracted from a
production system where it has managed 2,000+ specifications and 11,000+
tests. The extraction and packaging for standalone use is in progress.

Project scaffolding (`gt project init`), environment verification
(`gt project doctor`), and scaffold upgrades (`gt project upgrade`) are
included in the package.  See the
[product architecture](docs/architecture/product-split.md) for details.

## Documentation

The [method documentation](docs/method/README.md) describes the engineering discipline behind GroundTruth:

- [Method Overview](docs/method/01-overview.md) — what GroundTruth is, core workflow, governance model
- [Specifications](docs/method/02-specifications.md) — writing and managing specifications
- [Testing](docs/method/03-testing.md) — test forms, outside-in testing, pipeline organization
- [Work Items & Backlog](docs/method/04-work-items.md) — tracking gaps, stage lifecycle, prioritization
- [Governance](docs/method/05-governance.md) — GOV specs, gates, assertions, protected behaviors
- [Dual-Agent Collaboration](docs/method/06-dual-agent.md) — Prime Builder + Loyal Opposition
- [Session Discipline](docs/method/07-sessions.md) — session IDs, wrap-up, audit cadence
- [Architecture Decisions](docs/method/08-architecture.md) — ADR/DCL/IPR/CVR workflow
- [Adoption & Promotion](docs/method/09-adoption.md) — upstream/downstream model, update procedures
- [KB Tooling](docs/method/10-tooling.md) — CLI commands, web UI, Python API, configuration

- [Operational Configuration Capture](docs/method/11-operational-configuration.md) - bridges, automations, directives, and role inventory
- [Desktop Setup Guide](docs/desktop-setup.md) - same-day client workstation bootstrap and prerequisites

## Getting Started

New to GroundTruth? The [getting started guide](docs/bootstrap.md) walks you
through setting up the core toolkit in your project: install, init, first spec,
first test, assertions, web UI, templates, and CI/CD — in 10 steps.

If you need a same-day client workstation setup, start with the
[desktop setup guide](docs/desktop-setup.md).

## Process Templates

The [templates/](templates/README.md) directory contains reference templates for
setting up a GroundTruth project: rules files, state files, hooks, and agent
configuration. Copy them into your project and customize the placeholders.
GroundTruth includes reference templates for capturing bridge and automation
configuration.  Use `gt project init --profile <profile>` for automated setup.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute. We
especially value feedback about the engineering method itself — tag
issues with `method-feedback`.

## License

[AGPL-3.0](LICENSE)
