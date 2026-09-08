# PostgreSQL installation and operator tools

The authoritative placement and service boundary are defined by the current
ADR-POSTGRESQL-AUTHORITY-SUBSTRATE-001, its companion DCL, and
GOV-POSTGRESQL-LAN-AUTHORITY-SERVICE-001 in MemBase. This directory contains
installation source and operator instructions. Installing a server does not
change the selected GT-KB database.

The native Windows x64 distribution is pinned in release.json, including its
download checksum. The package comes from the EDB binary distribution linked
by the [PostgreSQL Windows download page](https://www.postgresql.org/download/windows/).
The installer extracts the server, command-line tools, extension libraries and
licenses. It does not install pgAdmin or StackBuilder.

| Location under infrastructure/postgresql | Purpose |
|---|---|
| install.py, archive_wal.py, register-service.ps1, release.json | Tracked installation source |
| runtime/<build>/ | Installed PostgreSQL binaries and archiver |
| data/ | PostgreSQL cluster |
| credentials/ | Protected administrator and service libpq configuration |
| logs/ | Seven rotating daily server logs and startup output |
| wal/ | Complete archived WAL segments |
| backups/ | Local backup staging; not protection against loss of this disk |

Runtime and state directories are ignored by Git. The installer protects
data, credentials, logs, WAL and backup staging using NTFS permissions before
writing them. The GT-KB service login is neither a superuser nor a role/database
administrator. PostgreSQL listens on 127.0.0.1 only.

From a checked-out GT-KB source tree, install into an explicit permanent root:

    & E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe infrastructure/postgresql/install.py --root E:\GT-KB

An existing cluster, credentials directory or runtime destination causes a
refusal; the installer never reinitializes or overwrites them. A failed partial
installation requires inspection, not an automatic recursive removal. An
already downloaded archive can be supplied with --archive; its pinned checksum
is still verified. This installer bootstraps a new cluster, not a version upgrade.

The initial start runs under the installing account. To register the installed
server for automatic startup, run this command in an administrator PowerShell:

    .\infrastructure\postgresql\register-service.ps1 -Root E:\GT-KB

The service is named gtkb-postgresql and runs as Windows LocalService. The
registration script grants that account access to the runtime, cluster, logs
and WAL, but not client credential files. It refuses a same-named service
pointing at another installation. After registration, verify service startup
and a new successful WAL archive under that service account.

Before service registration, the native operator commands are:

    $pg = 'E:\GT-KB\infrastructure\postgresql\runtime\18.6-3\bin'
    $data = 'E:\GT-KB\infrastructure\postgresql\data'
    & "$pg\pg_ctl.exe" status -D $data
    & "$pg\pg_ctl.exe" start -D $data -l 'E:\GT-KB\infrastructure\postgresql\logs\startup.log' -w
    & "$pg\pg_ctl.exe" stop -D $data -m fast -w

The service process uses credentials/pg_service.conf, service gtkb_authority.
Operators use gtkb_admin; no password belongs in shell arguments or agent
configuration. The administrator service intentionally has no fixed database
name so an explicitly selected isolated recovery/test database can be used.
Normal agents use the GT-KB CLI, not these database tools.

Physical backups use pg_basebackup with streamed WAL and are checked using
pg_verifybackup. The continuous archive stores complete WAL files without
overwriting different bytes; an identical retry is safe. Keep a verified base
backup and its complete required WAL sequence together. Do not prune WAL by age
alone. Copy recovery material to an out-of-band location appropriate to the
failure scenario before claiming protection against primary-storage loss.
See the [PostgreSQL recovery contract](https://www.postgresql.org/docs/18/continuous-archiving.html).

The opt-in recovery test creates a physical backup, verifies its manifest,
commits another row, archives WAL, restores to a separate directory and port,
and replays to a named restore point. It verifies both rows and stops the
restored instance. Its configured source must be a disposable native installation
outside the repository and all linked worktrees:

    $env:GTKB_NATIVE_POSTGRES_HOME = 'E:\GTKB-realignment-validation\native-install-qualification\infrastructure\postgresql'
    & E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/test_postgres_native_recovery.py --basetemp E:\GTKB-realignment-validation\new-recovery-run -q

Passing this drill demonstrates its isolated recovery scenario. Ordinary CLI
cutover, the authority service, unattended backup/retention, service startup
and a storage-loss recovery copy require their own operational validation.
