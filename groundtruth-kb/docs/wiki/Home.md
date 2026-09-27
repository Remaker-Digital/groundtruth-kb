# GroundTruth KB documentation

**Status:** Current documentation home

**Audience:** Evaluators, installers, developers, and operators
**Reviewed:** 2026-09-26

GroundTruth KB (GTKB) is a local-first development platform for coordinating
specification-linked software work performed with AI coding agents. It connects
current requirements, executable tests, projects, work items, independent
review, and the Git result that activates completed work.

GTKB is under active development. The current production installation is a
Windows-hosted system whose canonical records are served by a native PostgreSQL
domain service. The `gt` command is the supported client surface. GTKB Home is
the primary interactive interface.

## Choose your path

| I want to... | Start here |
| --- | --- |
| Understand the product | [Product overview](Product-Overview) |
| Evaluate prerequisites and current limitations | [System requirements](System-Requirements) and [Known issues](Known-Issues) |
| Install GTKB on Windows | [Install on Windows](Install-on-Windows) |
| Check an existing installation | [Verify installation](Verify-Installation) |
| Start using the product | [Get started](Get-Started) |
| Open the primary interface | [GTKB Home](GTKB-Home) |
| Understand the operating model | [Core concepts](Core-Concepts) |
| Diagnose a problem | [Troubleshooting](Troubleshooting) |
| Operate the background components | [Services](Services) |
| Upgrade or remove GTKB | [Upgrade](Upgrade) or [Uninstall](Uninstall) |
| Ask for help or report a defect | [Support](Support) |

## Important installation notice

Installing the `groundtruth-kb` Python package installs the Python distribution
and the `gt` command. It does **not**, by itself, provision a complete GTKB host.
A working host also requires the native PostgreSQL installation, the GTKB domain
service, configuration, and GTKB Home. The present installation procedure is an
operator procedure while a unified installer is developed.

Do not use retired SQLite, MemBase, Deliberation Archive, TAFE, PAUTH,
`.gtkb-state`, `harness-state`, or durable file-bridge instructions as a current
installation or authority model.

## Documentation policy

This Wiki is the customer-facing product documentation. Reviewed source lives in
`groundtruth-kb/docs/wiki/` in the main repository and is published here through
the Wiki publisher. Component READMEs remain useful maintainer references, but a
customer should not need to browse the source tree to discover the next ordinary
installation, launch, learning, or recovery step.

The product source and issue tracker are in the
[GTKB repository](https://github.com/Remaker-Digital/groundtruth-kb).
