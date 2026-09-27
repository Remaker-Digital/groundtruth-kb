# System requirements

**Status:** Current known requirements; complete sizing qualification remains open
**Reviewed:** 2026-09-26

## Supported host

The currently documented and operated GTKB host is Windows on an NTFS volume.
The present procedures assume PowerShell and Windows service/scheduled-task
facilities. Cross-platform client or host support must not be inferred from the
Python package alone.

## Required software

| Requirement | Current use |
| --- | --- |
| Python 3.11 or newer | GTKB package, CLI, installers, and operator tools |
| Git | Product and application work product |
| PowerShell | Windows installation and service registration |
| Node.js 20 or newer | GTKB Home installation and runtime |
| Supported web browser | GTKB Home |

Some supported harnesses have additional requirements. For example, Goose hook
execution on Windows currently depends on `sh` supplied by Git for Windows.

## Local ports

The standard production configuration currently uses loopback listeners,
including:

| Port | Component |
| ---: | --- |
| 8765 | Native GTKB authority service |
| 3080 | GTKB Home |

Dashboard and optional model services can require additional ports. Verify the
installation's actual configuration before reserving, exposing, or filtering a
port. GTKB documentation does not authorize exposing a loopback-only service to
the LAN or public Internet.

## Accounts and credentials

- Access to the GTKB repository or distribution channel is required.
- Selected AI harnesses and model providers can require their own accounts.
- GTKB does not make a harness credential a project-authorization record.
- Never place plaintext secrets in Wiki pages, issue reports, shell history, or
  agent instructions.

## Capacity

Minimum and recommended CPU, memory, disk, and installation-duration figures
have not yet completed customer-facing qualification. Treat this as a known
documentation and product-packaging gap. Operators should measure the complete
installed host, including PostgreSQL, GTKB Home, logs, backups, and any optional
local model services, before setting workstation standards.

See [Install on Windows](Install-on-Windows) and [Known issues](Known-Issues).
