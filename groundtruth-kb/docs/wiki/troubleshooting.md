# Troubleshooting

**Status:** First-pass symptom index
**Reviewed:** 2026-09-26

Start by confirming the selected installation:

```powershell
gt --version
gt --config E:\GTKB\groundtruth.toml config --json
gt --config E:\GTKB\groundtruth.toml services status --json
```

## `gt` is not found

- Confirm that the selected Python environment contains `groundtruth-kb`.
- Confirm that its Scripts directory is on the invoking user's `PATH`.
- Do not install an unrelated package with a similar name as a workaround.

## The authority service is unavailable

- Confirm that the configuration selects the intended loopback URL.
- Inspect the registered native service/task and its current log.
- Confirm that the expected port belongs to the selected installation.
- Restore service availability, then re-read canonical state; do not fall back to
  a local SQLite database or copied state.

## GTKB Home does not open

```powershell
gt --config E:\GTKB\groundtruth.toml home status
gt --config E:\GTKB\groundtruth.toml services status --json
```

- Verify Node.js and the pinned Home installation.
- Inspect the exact Home log and task registration.
- Check whether port 3080 is already owned by another process.
- Use `gt home open` to obtain a current launch URL; do not reuse an old URL.

## PostgreSQL does not start

- Inspect the exact `gtkb-postgresql` Windows service configuration.
- Read the startup and PostgreSQL logs from the selected installation.
- Do not reinitialize or delete an existing cluster as a repair shortcut.
- Do not expose credentials in an issue or support bundle.

## A port is already in use

Identify the owning process and installation before taking action. Never kill a
process solely by executable name. If the port belongs to another intended
installation, choose an explicit supported configuration rather than silently
reusing it.

## A scheduled task is missing or disabled

Use the selected release's registration script and verify the task action points
to the selected installation. Re-registration is an operator mutation; inspect
the existing task before replacing it.

## A documented command is missing or refuses valid work

Confirm the installed GTKB version and compare the page's review date. Capture
the exact command, exit code, and redacted output. Report the documentation or
platform defect through [Support](Support). Do not create a competing authority
surface or manually edit generated harness configuration.

## Installation or upgrade stopped partway through

Preserve the failure output and inspect the partial state. Do not recursively
delete database, credential, or backup directories. The unified repair workflow
is a known product gap; escalate using [Support](Support).

## Information to collect safely

- GTKB version.
- Redacted resolved configuration.
- Exact failing command and exit code.
- Service/task status.
- Relevant log excerpt with secrets removed.
- Expected result and actual result.
- Whether the failure reproduces after a controlled restart.

Do not attach `.env` files, credentials, database copies, browser launch URLs,
private application content, or unredacted logs.
