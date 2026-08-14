#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""MemBase committable dump service (WI-6218).

Per ``bridge/gtkb-wi6218-membase-committable-dump-005.md`` (GO at ``-006``).

The canonical MemBase database is gitignored, so governed content lives on one
disk and a clone cannot reconstruct it. This service projects the governed
subset of that database into deterministic, diffable, git-trackable text.

Three modes:

``dump``
    Serialize the governed subset to ``<out>/<table>/schema.sql`` plus
    ``<out>/<table>/<NNNN>.sql`` data chunks. Byte-reproducible for an
    unchanged database.

``check``
    Regenerate in memory and compare against the on-disk projection. Reports
    drift and writes nothing. This is the freshness instrument.

``restore``
    Rebuild a SQLite database from a projection into a *new* file. Refuses to
    target the canonical database.

Three properties carry the design:

1. **Selection is data, not code.** The include and exclude sets live in
   ``config/membase-dump/dump-policy.toml``. This module contains no literal
   list of governed table names; a table present in the database but absent
   from the policy is a hard error, so schema growth cannot silently enter or
   silently escape the projection.

2. **Sharding uses a fixed row-range key.** A chunk holds a fixed span of the
   table's rowid space (``chunk_index = rowid // rows_per_chunk``), not a
   size-packed run of rows. Because the database is append-only, new rows land
   in the tail chunk and every earlier chunk stays byte-identical across
   re-dumps, producing no new git blob. Size-packed chunks would reflow on
   every append and rewrite the whole table.

3. **Budgets fail closed.** Every artifact is generated in memory and checked
   against a per-file budget and an aggregate ceiling *before* anything is
   written, so an oversized projection raises instead of landing on disk.

Row identity is preserved exactly: rowid values are emitted explicitly when the
table has no ``INTEGER PRIMARY KEY`` alias column, because the source database
has rowid gaps and re-assigned rowids would change chunk membership and break
byte-reproducibility of a restored copy.

Schema coverage is tables and their indexes. Views are deliberately not
projected: they are derived objects recreated by the platform's own schema
initialization, which is already tracked in git.
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

DEFAULT_POLICY_RELPATH = "config/membase-dump/dump-policy.toml"
DEFAULT_OUTPUT_RELPATH = "membase-dump"
DEFAULT_DB_RELPATH = "groundtruth.db"

SCHEMA_FILENAME = "schema.sql"
ARTIFACT_SUFFIX = ".sql"
HEADER_PREFIX = "-- gtkb-membase-dump"
INDEX_STATEMENT_RE = re.compile(r"^CREATE\s+(UNIQUE\s+)?INDEX\b", re.IGNORECASE)

_SUPPORTED_POLICY_SCHEMA_VERSIONS = frozenset({1})


class DumpError(RuntimeError):
    """Base class for every fail-closed condition in this service."""


class PolicyError(DumpError):
    """The policy file is malformed, or disagrees with the live schema."""


class UnclassifiedTableError(PolicyError):
    """A table exists in the database but appears in neither policy set."""


class MissingTableError(PolicyError):
    """The policy names a table that the database does not have."""


class UnsupportedTableError(DumpError):
    """A selected table cannot be projected deterministically."""


class SizeBudgetExceeded(DumpError):
    """A single artifact would exceed the per-file budget."""


class AggregateCeilingExceeded(DumpError):
    """The projection as a whole would exceed the aggregate ceiling."""


class RestoreRefused(DumpError):
    """A restore target was rejected for safety."""


@dataclass(frozen=True)
class ExcludedTable:
    """One excluded table with its recorded justification."""

    table: str
    reason: str
    recoverable: bool
    recovery: str


@dataclass(frozen=True)
class DumpPolicy:
    """The include/exclude sets, chunk sizing, and size budgets."""

    schema_version: int
    max_file_bytes: int
    max_total_bytes: int
    default_rows_per_chunk: int
    included: frozenset[str]
    excluded: Mapping[str, ExcludedTable]
    rows_per_chunk_overrides: Mapping[str, int]

    def rows_per_chunk(self, table: str) -> int:
        return self.rows_per_chunk_overrides.get(table, self.default_rows_per_chunk)


@dataclass(frozen=True)
class Drift:
    """One difference between the on-disk projection and a fresh one."""

    path: str
    kind: str  # "missing" | "stale" | "changed"

    def describe(self) -> str:
        wording = {
            "missing": "absent on disk",
            "stale": "on disk but not produced by the current database",
            "changed": "content differs from the current database",
        }
        return f"{self.path}: {wording[self.kind]}"


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def sql_literal(value: object) -> str:
    """Render one column value as a deterministic SQLite literal.

    Text keeps embedded newlines verbatim rather than escaping them: SQLite
    string literals allow raw newlines, and keeping them makes a changed row
    show as a line-level diff instead of one enormous changed line.
    """
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise UnsupportedTableError(
                "NaN and infinity have no SQLite literal form and cannot be projected deterministically"
            )
        return repr(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "X'" + bytes(value).hex().upper() + "'"
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    raise UnsupportedTableError(f"unsupported column value type: {type(value).__name__}")


def load_policy(policy_path: Path) -> DumpPolicy:
    """Parse and validate the selection policy."""
    try:
        raw = tomllib.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PolicyError(f"policy file not found: {policy_path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise PolicyError(f"policy file is not valid TOML: {policy_path}: {exc}") from exc

    schema_version = raw.get("schema_version")
    if schema_version not in _SUPPORTED_POLICY_SCHEMA_VERSIONS:
        raise PolicyError(
            f"unsupported policy schema_version {schema_version!r}; "
            f"supported: {sorted(_SUPPORTED_POLICY_SCHEMA_VERSIONS)}"
        )

    budget = raw.get("budget") or {}
    try:
        max_file_bytes = int(budget["max_file_bytes"])
        max_total_bytes = int(budget["max_total_bytes"])
        default_rows_per_chunk = int(budget["default_rows_per_chunk"])
    except KeyError as exc:
        raise PolicyError(f"policy [budget] is missing required key {exc}") from exc
    if min(max_file_bytes, max_total_bytes, default_rows_per_chunk) <= 0:
        raise PolicyError("policy [budget] values must all be positive")
    if max_file_bytes > max_total_bytes:
        raise PolicyError("policy [budget].max_file_bytes exceeds max_total_bytes")

    include_section = raw.get("include") or {}
    included_raw = include_section.get("tables")
    if not isinstance(included_raw, list) or not included_raw:
        raise PolicyError("policy [include].tables must be a non-empty array")
    included = [str(name) for name in included_raw]
    if len(set(included)) != len(included):
        raise PolicyError("policy [include].tables contains duplicates")

    overrides_raw = include_section.get("rows_per_chunk") or {}
    if not isinstance(overrides_raw, dict):
        raise PolicyError("policy [include.rows_per_chunk] must be a table")
    overrides: dict[str, int] = {}
    for name, value in overrides_raw.items():
        size = int(value)
        if size <= 0:
            raise PolicyError(f"policy [include.rows_per_chunk] value for {name!r} must be positive")
        if name not in set(included):
            raise PolicyError(f"policy [include.rows_per_chunk] names {name!r}, which is not included")
        overrides[str(name)] = size

    excluded: dict[str, ExcludedTable] = {}
    for entry in raw.get("exclude") or []:
        if not isinstance(entry, dict):
            raise PolicyError("each [[exclude]] entry must be a table")
        missing = {"table", "reason", "recoverable", "recovery"} - set(entry)
        if missing:
            raise PolicyError(f"[[exclude]] entry is missing required keys: {sorted(missing)}")
        name = str(entry["table"])
        if name in excluded:
            raise PolicyError(f"[[exclude]] names {name!r} more than once")
        excluded[name] = ExcludedTable(
            table=name,
            reason=str(entry["reason"]),
            recoverable=bool(entry["recoverable"]),
            recovery=str(entry["recovery"]),
        )

    overlap = set(included) & set(excluded)
    if overlap:
        raise PolicyError(f"tables appear in both policy sets: {sorted(overlap)}")

    return DumpPolicy(
        schema_version=int(schema_version),
        max_file_bytes=max_file_bytes,
        max_total_bytes=max_total_bytes,
        default_rows_per_chunk=default_rows_per_chunk,
        included=frozenset(included),
        excluded=excluded,
        rows_per_chunk_overrides=overrides,
    )


def open_readonly(db_path: Path) -> sqlite3.Connection:
    """Open the database read-only.

    ``mode=ro`` guarantees the service can never mutate the source. The caller
    wraps reads in a deferred transaction so a WAL database yields one
    consistent snapshot even while another connection is writing.
    """
    if not db_path.exists():
        raise DumpError(f"database not found: {db_path}")
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.isolation_level = None
    return connection


def list_tables(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").fetchall()
    return [row[0] for row in rows]


def _columns(connection: sqlite3.Connection, table: str) -> list[tuple[str, str, int]]:
    rows = connection.execute(f"PRAGMA table_info({_quote_ident(table)})").fetchall()
    return [(row[1], row[2] or "", row[5]) for row in rows]


def _rowid_alias(columns: Sequence[tuple[str, str, int]]) -> str | None:
    """Return the column that aliases rowid, or None if there is no alias.

    SQLite makes a column an alias for rowid only when it is the sole primary
    key and its declared type is exactly INTEGER.
    """
    primary_keys = [column for column in columns if column[2]]
    if len(primary_keys) == 1 and primary_keys[0][1].strip().upper() == "INTEGER":
        return primary_keys[0][0]
    return None


def _schema_sql(connection: sqlite3.Connection, table: str) -> str:
    table_sql = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    if table_sql is None or not table_sql[0]:
        raise MissingTableError(f"no CREATE statement recorded for table {table!r}")
    statements = [table_sql[0]]
    index_rows = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'index' AND tbl_name = ? AND sql IS NOT NULL ORDER BY name",
        (table,),
    ).fetchall()
    statements.extend(row[0] for row in index_rows)
    body = "".join(f"{statement.strip()};\n" for statement in statements)
    return f"{HEADER_PREFIX} schema table={table}\n{body}"


def _table_artifacts(connection: sqlite3.Connection, table: str, rows_per_chunk: int) -> dict[str, bytes]:
    """Generate ``schema.sql`` plus every non-empty data chunk for one table."""
    columns = _columns(connection, table)
    if not columns:
        raise MissingTableError(f"table {table!r} has no columns")

    alias = _rowid_alias(columns)
    column_names = [name for name, _type, _pk in columns]
    if alias is None:
        # No INTEGER PRIMARY KEY alias: carry rowid explicitly so a restored
        # copy reproduces the exact row identity, and therefore the exact
        # chunk membership, of the source.
        select_names = ["rowid", *column_names]
        insert_names = select_names
        order_expression = "rowid"
    else:
        select_names = column_names
        insert_names = column_names
        order_expression = _quote_ident(alias)

    selected = ", ".join(_quote_ident(name) for name in select_names)
    query = f"SELECT {selected}, rowid FROM {_quote_ident(table)} ORDER BY {order_expression}"
    try:
        cursor = connection.execute(query)
    except sqlite3.OperationalError as exc:
        raise UnsupportedTableError(
            f"table {table!r} cannot be ordered by rowid (WITHOUT ROWID tables are not projected): {exc}"
        ) from exc

    insert_prefix = (
        f"INSERT INTO {_quote_ident(table)} ({', '.join(_quote_ident(name) for name in insert_names)}) VALUES ("
    )

    artifacts: dict[str, bytes] = {f"{table}/{SCHEMA_FILENAME}": _schema_sql(connection, table).encode("utf-8")}

    current_index: int | None = None
    buffer: list[str] = []

    def flush() -> None:
        if current_index is None:
            return
        start = current_index * rows_per_chunk
        header = (
            f"{HEADER_PREFIX} table={table} chunk={current_index:04d} rowid_range=[{start},{start + rows_per_chunk})\n"
        )
        name = f"{table}/{current_index:04d}{ARTIFACT_SUFFIX}"
        artifacts[name] = (header + "".join(buffer)).encode("utf-8")
        buffer.clear()

    for row in cursor:
        rowid = row[-1]
        values = row[:-1]
        index = rowid // rows_per_chunk
        if index != current_index:
            flush()
            current_index = index
        buffer.append(insert_prefix + ", ".join(sql_literal(value) for value in values) + ");\n")
    flush()

    return artifacts


def generate_artifacts(connection: sqlite3.Connection, policy: DumpPolicy) -> dict[str, bytes]:
    """Produce the whole projection in memory, keyed by output-relative path.

    Generating everything before writing is what makes the budget checks
    fail closed: an oversized projection raises without touching the disk.
    """
    present = set(list_tables(connection))
    classified = policy.included | set(policy.excluded)

    unclassified = sorted(present - classified)
    if unclassified:
        raise UnclassifiedTableError(
            "these tables exist in the database but appear in neither policy set: "
            f"{unclassified}. Add each one to [include].tables or an [[exclude]] "
            "entry so the selection stays an explicit, reviewable decision."
        )

    absent = sorted(policy.included - present)
    if absent:
        raise MissingTableError(f"policy includes tables that the database does not have: {absent}")

    connection.execute("BEGIN")
    try:
        artifacts: dict[str, bytes] = {}
        for table in sorted(policy.included):
            artifacts.update(_table_artifacts(connection, table, policy.rows_per_chunk(table)))
    finally:
        connection.execute("ROLLBACK")

    _enforce_budgets(artifacts, policy)
    return artifacts


def _enforce_budgets(artifacts: Mapping[str, bytes], policy: DumpPolicy) -> None:
    oversized = sorted(
        (path, len(content)) for path, content in artifacts.items() if len(content) > policy.max_file_bytes
    )
    if oversized:
        detail = ", ".join(f"{path} ({size} bytes)" for path, size in oversized)
        raise SizeBudgetExceeded(
            f"artifacts exceed the {policy.max_file_bytes}-byte per-file budget: {detail}. "
            "Lower rows_per_chunk for the affected table, or exclude it."
        )
    total = sum(len(content) for content in artifacts.values())
    if total > policy.max_total_bytes:
        raise AggregateCeilingExceeded(
            f"projection totals {total} bytes, over the {policy.max_total_bytes}-byte "
            "aggregate ceiling. Narrow the include set or raise the ceiling deliberately."
        )


def _artifact_paths(output_dir: Path) -> list[str]:
    if not output_dir.exists():
        return []
    return sorted(
        path.relative_to(output_dir).as_posix() for path in output_dir.rglob(f"*{ARTIFACT_SUFFIX}") if path.is_file()
    )


def _existing_artifacts(output_dir: Path) -> dict[str, bytes]:
    return {relpath: (output_dir / relpath).read_bytes() for relpath in _artifact_paths(output_dir)}


def write_artifacts(output_dir: Path, artifacts: Mapping[str, bytes]) -> list[str]:
    """Write the projection and drop artifacts the current database no longer produces."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for relpath, content in sorted(artifacts.items()):
        target = output_dir / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    removed = sorted(set(_artifact_paths(output_dir)) - set(artifacts))
    for relpath in removed:
        (output_dir / relpath).unlink()
    for directory in sorted(output_dir.rglob("*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    return removed


def compare_artifacts(output_dir: Path, artifacts: Mapping[str, bytes]) -> list[Drift]:
    """Compare a freshly generated projection against the one on disk."""
    on_disk = _existing_artifacts(output_dir)
    drifts: list[Drift] = []
    for relpath in sorted(set(artifacts) | set(on_disk)):
        expected = artifacts.get(relpath)
        actual = on_disk.get(relpath)
        if actual is None:
            drifts.append(Drift(relpath, "missing"))
        elif expected is None:
            drifts.append(Drift(relpath, "stale"))
        elif expected != actual:
            drifts.append(Drift(relpath, "changed"))
    return drifts


def _chunk_sort_key(relpath: str) -> tuple[str, int, str]:
    table, _, filename = relpath.partition("/")
    if filename == SCHEMA_FILENAME:
        return (table, -1, filename)
    return (table, int(filename.removesuffix(ARTIFACT_SUFFIX)), filename)


def _split_statements(script: str) -> list[str]:
    """Split a schema artifact into individual statements.

    ``sqlite3.complete_statement`` is quote-aware, so a semicolon inside a
    string literal or a quoted identifier does not split a statement.
    """
    statements: list[str] = []
    buffer = ""
    for line in script.splitlines(keepends=True):
        if not buffer and line.lstrip().startswith("--"):
            continue
        buffer += line
        if sqlite3.complete_statement(buffer):
            statements.append(buffer.strip())
            buffer = ""
    if buffer.strip():
        statements.append(buffer.strip())
    return statements


def _same_path(left: Path, right: Path) -> bool:
    """Compare two paths without requiring either to exist.

    ``resolve()`` is used where possible so symlinks and short names collapse;
    case is normalized because the platform root is a case-insensitive volume.
    """

    def normalize(path: Path) -> str:
        candidate = path.resolve() if path.exists() else path.absolute()
        return os.path.normcase(os.path.normpath(str(candidate)))

    return normalize(left) == normalize(right)


def restore(dump_dir: Path, target: Path, canonical_db: Path) -> int:
    """Rebuild a database from a projection into a new file.

    Refuses the canonical database outright, and refuses any target that
    already exists or carries WAL sidecars, so a restore can never overwrite
    live state.

    Load order is tables, then rows, then indexes. Creating the indexes up
    front would make every insert pay index maintenance: measured against the
    live projection that reduced the load to roughly 56 kB/s, which is hours
    for the real corpus. Deferring them keeps a recovery practical.

    Durability pragmas are disabled for the load. The target is a brand-new
    file that is discarded on failure, so there is nothing to protect from a
    torn write, and the canonical database is never the target.
    """
    if _same_path(target, canonical_db):
        raise RestoreRefused(
            f"refusing to restore over the canonical database at {canonical_db}. "
            "Restore to a new path; promoting it is a deliberate owner act."
        )
    if target.exists():
        raise RestoreRefused(f"refusing to overwrite an existing file: {target}")
    for sidecar in (f"{target}-wal", f"{target}-shm"):
        if Path(sidecar).exists():
            raise RestoreRefused(f"refusing to restore beside an active WAL sidecar: {sidecar}")

    artifacts = _existing_artifacts(dump_dir)
    if not artifacts:
        raise DumpError(f"no projection artifacts found under {dump_dir}")

    ordered = sorted(artifacts, key=_chunk_sort_key)
    table_statements: list[str] = []
    index_statements: list[str] = []
    for relpath in ordered:
        if not relpath.endswith(f"/{SCHEMA_FILENAME}"):
            continue
        for statement in _split_statements(artifacts[relpath].decode("utf-8")):
            if INDEX_STATEMENT_RE.match(statement):
                index_statements.append(statement)
            else:
                table_statements.append(statement)

    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    try:
        connection.execute("PRAGMA journal_mode = OFF")
        connection.execute("PRAGMA synchronous = OFF")
        connection.execute("PRAGMA foreign_keys = OFF")
        for statement in table_statements:
            connection.execute(statement)
        for relpath in ordered:
            if relpath.endswith(f"/{SCHEMA_FILENAME}"):
                continue
            connection.executescript(artifacts[relpath].decode("utf-8"))
        for statement in index_statements:
            connection.execute(statement)
        connection.commit()
    finally:
        connection.close()
    return len(artifacts)


def _resolve_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    return Path(__file__).resolve().parent.parent


def _paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    root = _resolve_root(args.project_root)
    database = Path(args.db).resolve() if args.db else root / DEFAULT_DB_RELPATH
    policy = Path(args.policy).resolve() if args.policy else root / DEFAULT_POLICY_RELPATH
    output = Path(args.out).resolve() if args.out else root / DEFAULT_OUTPUT_RELPATH
    return root, database, policy, output


def _summarize(artifacts: Mapping[str, bytes], policy: DumpPolicy, stream) -> None:
    per_table: dict[str, tuple[int, int]] = {}
    for relpath, content in artifacts.items():
        table = relpath.partition("/")[0]
        count, size = per_table.get(table, (0, 0))
        per_table[table] = (count + 1, size + len(content))
    for table in sorted(per_table):
        count, size = per_table[table]
        print(f"  {table}: {count} file(s), {size} bytes", file=stream)
    total = sum(len(content) for content in artifacts.values())
    largest = max((len(content) for content in artifacts.values()), default=0)
    print(
        f"total: {len(artifacts)} file(s), {total} bytes "
        f"(ceiling {policy.max_total_bytes}); largest file {largest} bytes "
        f"(budget {policy.max_file_bytes})",
        file=stream,
    )


def _generate(args: argparse.Namespace) -> tuple[dict[str, bytes], DumpPolicy, Path]:
    _root, database, policy_path, output = _paths(args)
    policy = load_policy(policy_path)
    connection = open_readonly(database)
    try:
        return generate_artifacts(connection, policy), policy, output
    finally:
        connection.close()


def cmd_dump(args: argparse.Namespace) -> int:
    artifacts, policy, output = _generate(args)
    removed = write_artifacts(output, artifacts)
    print(f"wrote projection to {output}")
    _summarize(artifacts, policy, sys.stdout)
    for relpath in removed:
        print(f"  dropped stale artifact: {relpath}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    artifacts, policy, output = _generate(args)
    drifts = compare_artifacts(output, artifacts)
    if not drifts:
        print(f"projection at {output} is current")
        _summarize(artifacts, policy, sys.stdout)
        return 0
    print(f"projection at {output} has drifted from the database:", file=sys.stderr)
    for drift in drifts:
        print(f"  {drift.describe()}", file=sys.stderr)
    print(f"{len(drifts)} artifact(s) drifted", file=sys.stderr)
    return 1


def cmd_restore(args: argparse.Namespace) -> int:
    root, database, _policy_path, output = _paths(args)
    dump_dir = Path(args.dump_dir).resolve() if args.dump_dir else output
    written = restore(dump_dir, Path(args.target), database)
    print(f"restored {written} artifact(s) from {dump_dir} into {args.target}")
    print(f"(project root {root}; canonical database at {database} untouched)")
    return 0


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-root", default=None, help="override the resolved project root")
    parser.add_argument("--db", default=None, help="path to the source database")
    parser.add_argument("--policy", default=None, help="path to the selection policy")
    parser.add_argument("--out", default=None, help="projection output directory")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="membase_dump.py", description="Project the governed MemBase subset to tracked text."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dump_parser = subparsers.add_parser("dump", help="write the projection")
    _add_common(dump_parser)
    dump_parser.set_defaults(handler=cmd_dump)

    check_parser = subparsers.add_parser("check", help="report drift without writing")
    _add_common(check_parser)
    check_parser.set_defaults(handler=cmd_check)

    restore_parser = subparsers.add_parser("restore", help="rebuild a database from a projection")
    _add_common(restore_parser)
    restore_parser.add_argument("--target", required=True, help="new database file to create")
    restore_parser.add_argument("--dump-dir", default=None, help="projection directory to read")
    restore_parser.set_defaults(handler=cmd_restore)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        return int(args.handler(args))
    except DumpError as exc:
        print(f"membase_dump: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
