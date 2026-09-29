# Install on Windows

**Status:** Operator procedure; unified installer not yet available
**Reviewed:** 2026-09-26

GTKB does not yet have one customer-grade installer that provisions and verifies
the complete host. The current production installation is assembled through
separate, pinned component installers and Windows registration scripts.

## Before you begin

1. Review [System requirements](System-Requirements).
2. Select the permanent GTKB root. A fresh installation uses `E:\GTKB`.
3. Confirm that the required service names, scheduled-task names, and ports do
   not belong to another installation.
4. Arrange an out-of-band backup destination before claiming recoverability.
5. Use an administrator PowerShell only for steps that explicitly require it.

Do not copy the current production `E:\GT-KB` path into a fresh-install design.
That legacy root remains in use until its separately planned rename.

## Current installation layers

The complete host requires these layers:

1. **GTKB Python distribution and CLI** — installs `gt`.
2. **Pinned PostgreSQL runtime and cluster** — canonical database substrate.
3. **Native GTKB domain service** — supported HTTP authority used by clients.
4. **Host configuration** — selects the project root and native authority URL.
5. **GTKB Home** — primary interactive interface.
6. **Windows startup registration** — PostgreSQL service and GTKB scheduled
   tasks, according to the selected installation.
7. **Backup and recovery registration** — operator-owned, independently
   verified protection.

Installing only the Python package is not a complete host installation.

## Source-install operator references

Until the unified installer exists, qualified operators should use the pinned
installers and exact procedures shipped with the selected release:

- `infrastructure/postgresql/README.md`
- `infrastructure/postgresql/install.py`
- `infrastructure/postgresql/register-service.ps1`
- the native domain-service registration procedure in that infrastructure area
- `infrastructure/deepseek-web/README.md`
- `infrastructure/deepseek-web/install.py`
- `infrastructure/deepseek-web/register-home-task.ps1`

These are maintainer/operator references, not a promise that arbitrary source
checkout commands form a supported customer installer.

## Completion criterion

Installation is not complete merely because `pip`, `npm`, a service
registration command, or a scheduled-task registration command succeeded. It is
complete only after the installed host passes [Verify installation](Verify-Installation),
survives a real Windows restart, and has a tested recovery path appropriate to
its data-loss scenario.

## Planned improvement

A unified installer should orchestrate the existing installers, preview effects,
request elevation only when required, create ordinary Windows launch affordances,
verify the whole product, support repair and uninstall, and open GTKB Home after
success. That capability is not yet documented as available.
