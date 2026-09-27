# Verify installation

**Status:** Current first-pass verification guide
**Reviewed:** 2026-09-26

Use the configuration installed for the same host as the native service. Replace
`E:\GTKB` only when verifying an intentionally different installation.

## 1. Confirm the CLI and selected configuration

```powershell
gt --version
gt --config E:\GTKB\groundtruth.toml config --json
```

Confirm that the resolved project root and authority URL identify the intended
installation. Successful configuration display does not prove service health.

## 2. Inspect services

```powershell
gt --config E:\GTKB\groundtruth.toml services status --json
gt --config E:\GTKB\groundtruth.toml service status --json
```

Treat missing, stopped, mismatched, or unreachable components as failures to
diagnose. Do not infer health from a process identifier alone.

## 3. Read canonical state

```powershell
gt --config E:\GTKB\groundtruth.toml projects list --json
gt --config E:\GTKB\groundtruth.toml backlog list --json
```

These reads prove that the selected client can reach the selected service and
receive current responses. They do not prove release qualification.

## 4. Open GTKB Home

```powershell
gt --config E:\GTKB\groundtruth.toml home status
gt --config E:\GTKB\groundtruth.toml home open
```

Confirm that the browser displays the expected GTKB branding and current
services/status pages. Do not reuse a sign-in URL as a permanent shortcut.

## 5. Run the applicable host doctor

Use the doctor command documented by the installed release and resolve every
blocking finding. Warnings must be understood and deliberately accepted; they
are not automatic passes.

## 6. Verify restart behavior

After the initial checks, perform a real Windows restart during a controlled
installation qualification. Re-run the service, canonical-read, and Home checks.
Registration records or prior launch logs are not substitutes for post-restart
readiness.

## 7. Verify recovery separately

A healthy live service is not backup evidence. Follow [Backup and restore](Backup-and-Restore)
and prove recovery from the copy meant to survive the selected loss scenario.
