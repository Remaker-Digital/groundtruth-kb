# SQLite snapshots (retired command)

The live `gt db snapshot` command, its scheduled Windows task
(`install_db_snapshot_task.ps1`) and the doctor's snapshot freshness and
output-allowlist checks are retired (O-7 R22). A SQLite snapshot is neither a
health criterion nor a production fallback: the PostgreSQL authority is the
only current state, and it is recovered from physical backups and WAL archives.

What remains is the explicit offline migration input. `gt db postgres
export-current --sqlite-snapshot <FILE>` reads one immutable, integrity-checked
SQLite snapshot produced by `groundtruth_kb.db_snapshot.create_snapshot`
(staging directory, `PRAGMA integrity_check`, atomic same-volume publish,
synced-path refusal). That function is library-only and is exercised by the
migration qualification, not by ordinary operation.

The `[backup]` configuration section keeps its meaning for that explicit
migration input; see the [Configuration Reference](reference/configuration.md).
