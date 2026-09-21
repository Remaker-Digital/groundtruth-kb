# GroundTruth Product Architecture

GroundTruth-KB provides a Python package and CLI for canonical engineering
records, native coordination, application initialization and diagnostics.
The package's current version is reported by `python -m groundtruth_kb --version`.

## Canonical records and coordination

The native service stores current records and history in PostgreSQL. CLI and
service APIs own validation, version checks and domain transitions. Callers use
those interfaces rather than opening authority tables directly.

| Capability | Current interface |
| --- | --- |
| Specifications and assertions | `gt spec`, `gt assert` |
| Executable test records and phases | `gt tests`, `gt test-plans` |
| Projects, membership and work items | `gt projects`, `gt backlog` |
| Session attribution | `gt session bind`, `gt session show` |
| Current task context | `gt context work-item <WI-ID> --json` |
| Coordination state and next actions | `gt bridge state-report --json`, `gt bridge queue --role <pb-or-lo> --json` |

The selected configuration identifies the native authority. Current formal
records carry requirements; operational notes and bridge messages do not become
a second specification or decision store.

## Independent implementation and review

The owner selects work while Dispatcher Next remains inactive. Agents author
their own proposals and verdicts. They read current task/attempt state, claim
the exact next artifact and deliver authored bytes through the native CLI.

The ordinary sequence is NEW → GO → READY → VERIFIED. A rejected proposal
receives NO-GO and then a REVISED proposal. A rejected implementation report
receives NOT-READY and then a corrected READY report. A claim reserves the next
artifact, not a work-item thread. Roles belong to session contexts and are not
fixed to a particular harness.

The complete verified project is the commit unit. Applicable native commit
checks bind the independently reviewed bytes to the actual Git commit.
Coordination messages are disposable; committed work product excludes them and
generated projections. See the [CLI reference](../reference/cli.md) and
[dual-agent setup](../tutorials/dual-agent-setup.md).

## Application files and harness configuration

An application is registered under a host and its execution project carries an
explicit repository reference. File initialization follows those two bindings:

| Capability | Current interface |
| --- | --- |
| Application registration | `gt application register <APPLICATION> --host-root <host>` |
| File initialization | `gt project init <APPLICATION> --project-id <PROJECT> --host-root <host> --owner <owner>` |
| Application diagnosis | `gt project doctor --project-id <PROJECT> --host-root <host>` |
| Managed-file upgrade | `gt project upgrade <APPLICATION> --project-id <PROJECT> --host-root <host>` |

Profiles select application scaffolding. Harness choices select projected
registrations and pointers; shared authored hooks, rules and skills remain the
source. Projectors produce derived outputs. Upgrade preserves application-owned
files and previews changes before application.

Initialization creates no local authority database or automatic commit. Core
specification intake reads the next canonical question and records explicit
answers through its ordinary writer. See [application isolation](isolation.md)
and the [bootstrap guide](../bootstrap.md).

## Derived views

The optional application search cache and operations dashboard are rebuildable
views. `gt project chroma regenerate` rebuilds application-scoped search data.
`gt dashboard` initializes, refreshes and operates the local Grafana dashboard.
Their cached data is not canonical authority, and a green display does not
replace qualification or review.

## Package boundaries

The package implements the native CLI, domain/service code, application
scaffolding, projectors and diagnostics. Application code, external accounts,
cloud deployment and operator-selected hosting stay with the application and
its owner. Local runtime setup and host qualification remain explicit
operations.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
