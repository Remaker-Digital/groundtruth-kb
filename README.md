# GroundTruth KB

GroundTruth KB (GTKB) is a local-first development platform for coordinating
specification-linked software work performed with AI coding agents. It connects
current requirements, executable tests, projects, work items, independent
review, and the Git result that activates completed work.

GTKB is under active development. The current production system is hosted on
Windows and uses a native PostgreSQL domain service. The `gt` command is the
supported client surface, and GTKB Home is the primary interactive interface.

## Documentation

The **[GroundTruth KB Wiki](https://github.com/Remaker-Digital/groundtruth-kb/wiki)**
is the customer-facing product manual.

- [Product overview](https://github.com/Remaker-Digital/groundtruth-kb/wiki/Product-Overview)
- [System requirements](https://github.com/Remaker-Digital/groundtruth-kb/wiki/System-Requirements)
- [Install on Windows](https://github.com/Remaker-Digital/groundtruth-kb/wiki/Install-on-Windows)
- [Verify installation](https://github.com/Remaker-Digital/groundtruth-kb/wiki/Verify-Installation)
- [Get started](https://github.com/Remaker-Digital/groundtruth-kb/wiki/Get-Started)
- [Troubleshooting](https://github.com/Remaker-Digital/groundtruth-kb/wiki/Troubleshooting)
- [Known issues](https://github.com/Remaker-Digital/groundtruth-kb/wiki/Known-Issues)

Reviewed Wiki source lives in [`groundtruth-kb/docs/wiki/`](groundtruth-kb/docs/wiki/).
Component READMEs contain maintainer and advanced operator detail; they are not a
replacement for the customer journey in the Wiki.

Maintainers compare reviewed source with a fresh local Wiki clone before
publication:

```powershell
python scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki
```

## Installation status

Installing the `groundtruth-kb` Python distribution installs the package and the
`gt` CLI. It does **not**, by itself, provision a complete GTKB host. A working
host also requires the native PostgreSQL installation, GTKB domain service,
configuration, Windows startup registration, and GTKB Home.

A unified customer-grade Windows installer, repair workflow, and whole-product
uninstaller remain active product gaps. Until those capabilities are qualified,
installation is an operator procedure. Do not treat an old SQLite, MemBase,
Deliberation Archive, TAFE, PAUTH, `.gtkb-state`, `harness-state`, or durable
file-bridge procedure as the current product model.

## Current architecture at a glance

| Component | Purpose |
| --- | --- |
| Native PostgreSQL domain service | Canonical current records and supported mutation APIs |
| `gt` CLI | Scriptable product command surface |
| GTKB Home | Primary interactive interface on the local workstation |
| Harness baseline and projectors | Shared authored configuration and derived harness-specific projections |
| Bridge coordination | Ephemeral delivery of the next agent-authored lifecycle artifact |
| Git repositories | Durable work product and activation history |

A work item belongs to one project. Project authorization orders new work. An
agent claims the right to deliver one exact next bridge artifact, not ownership
of a work-item thread. Bridge content is ephemeral coordination, not durable
authority. Independently verified work items complete together in the project's
Git commit.

## Repository status

This repository contains the GTKB platform, its Windows-host infrastructure,
the distributable Python package under `groundtruth-kb/`, tests, and governed
documentation source. Historical files can contain retired terminology or
architecture; use the Wiki for the current customer-facing model.

## Contributing and support

- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Report an issue](https://github.com/Remaker-Digital/groundtruth-kb/issues)
- [Security policy](groundtruth-kb/SECURITY.md)

The distributable package under `groundtruth-kb/` is licensed under
AGPL-3.0-or-later. Repository-root material outside that package is covered by
the repository-root [`LICENSE`](LICENSE); review both surfaces before reuse.
