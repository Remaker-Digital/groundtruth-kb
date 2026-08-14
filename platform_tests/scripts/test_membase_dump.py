# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Behavioral tests for ``scripts/membase_dump.py`` (WI-6218).

Per ``bridge/gtkb-wi6218-membase-committable-dump-005.md`` (GO at ``-006``).

Every test here exercises observable behavior of the dump service against
purpose-built fixture databases: what lands on disk, what does not, what
changes between runs, and what the service refuses to do. The live
``groundtruth.db`` is never read or written by this module.

The fixture policies are written per-test, which is itself the strongest
statement of the design's central claim: selection is data. The same fixture
database projects differently under two different policies, with no change to
the dumper.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "membase_dump.py"

# Distinctive real MemBase table names. Each is underscore-bearing, so it
# cannot plausibly occur as ordinary prose in the dumper's own text. Used to
# assert the dumper carries no governed-table list of its own.
REAL_TABLE_NAMES = (
    "pipeline_events",
    "assertion_runs",
    "deliberation_specs",
    "deliberation_work_items",
    "project_work_item_memberships",
    "project_authorizations",
    "project_artifact_links",
    "sot_artifact_revisions",
    "sot_registry_transaction_journal",
    "sot_registry_bridge_publication_capabilities",
    "test_plan_phases",
    "test_coverage",
    "work_items",
    "work_intent_claims",
    "canonical_terms",
    "backlog_snapshots",
    "operational_procedures",
    "environment_config",
    "flow_artifacts",
    "testable_elements",
    "session_prompts",
    "agent_capability_snapshots",
    "dispatch_lane_scoring_evidence",
    "sqlite_sequence",
)


@pytest.fixture(scope="module")
def dump_module():
    """Load the dump service as a module without executing ``main()``."""
    spec = importlib.util.spec_from_file_location("membase_dump", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before executing: dataclasses resolves ``cls.__module__`` through
    # ``sys.modules`` while processing the module's frozen dataclasses.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    return module


# ---------------------------------------------------------------------------
# Fixture construction
# ---------------------------------------------------------------------------

ALPHA_DDL = 'CREATE TABLE "alpha_records" (rowid INTEGER PRIMARY KEY, label TEXT, body TEXT)'
# ``raw_value`` is declared with no type, so it has BLOB affinity and SQLite
# stores whatever storage class it is given. That is what lets the round-trip
# test exercise genuine REAL and BLOB values: a TEXT-affinity column would
# convert a float to text on insert, before the dumper ever saw it.
LINK_DDL = 'CREATE TABLE "link_rows" (left_ref INTEGER, right_ref TEXT, raw_value)'
NOISE_DDL = 'CREATE TABLE "noise_events" (rowid INTEGER PRIMARY KEY, payload TEXT)'


def _build_db(
    path: Path,
    *,
    alpha_rows: int = 0,
    alpha_body: str = "body",
    alpha_rowid_step: int = 1,
    link_rows: int = 0,
    noise_rows: int = 0,
    wal: bool = False,
) -> Path:
    """Create a fixture database with three tables of known shape."""
    connection = sqlite3.connect(path)
    try:
        if wal:
            connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(ALPHA_DDL)
        connection.execute(LINK_DDL)
        connection.execute(NOISE_DDL)
        connection.execute('CREATE INDEX "idx_alpha_label" ON "alpha_records" (label)')
        for index in range(alpha_rows):
            connection.execute(
                'INSERT INTO "alpha_records" (rowid, label, body) VALUES (?, ?, ?)',
                (1 + index * alpha_rowid_step, f"label-{index}", f"{alpha_body}-{index}"),
            )
        for index in range(link_rows):
            connection.execute(
                'INSERT INTO "link_rows" (left_ref, right_ref) VALUES (?, ?)',
                (index, f"right-{index}"),
            )
        for index in range(noise_rows):
            connection.execute('INSERT INTO "noise_events" (payload) VALUES (?)', (f"noise-{index}",))
        connection.commit()
    finally:
        connection.close()
    return path


def _policy_text(
    *,
    included: tuple[str, ...] = ("alpha_records", "link_rows"),
    excluded: tuple[str, ...] = ("noise_events",),
    max_file_bytes: int = 1_000_000,
    max_total_bytes: int = 10_000_000,
    default_rows_per_chunk: int = 1_000,
    overrides: dict[str, int] | None = None,
) -> str:
    lines = [
        "schema_version = 1",
        "[budget]",
        f"max_file_bytes = {max_file_bytes}",
        f"max_total_bytes = {max_total_bytes}",
        f"default_rows_per_chunk = {default_rows_per_chunk}",
        "[include]",
        "tables = [" + ", ".join(f'"{name}"' for name in included) + "]",
    ]
    if overrides:
        lines.append("[include.rows_per_chunk]")
        lines.extend(f"{name} = {size}" for name, size in overrides.items())
    for name in excluded:
        lines.extend(
            [
                "[[exclude]]",
                f'table = "{name}"',
                'reason = "fixture exclusion"',
                "recoverable = true",
                'recovery = "rebuilt by the fixture"',
            ]
        )
    return "\n".join(lines) + "\n"


def _write_policy(tmp_path: Path, text: str, name: str = "policy.toml") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _generate(dump_module, db_path: Path, policy_path: Path) -> dict[str, bytes]:
    policy = dump_module.load_policy(policy_path)
    connection = dump_module.open_readonly(db_path)
    try:
        return dump_module.generate_artifacts(connection, policy)
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Selection policy (proposal F1.1)
# ---------------------------------------------------------------------------


def test_excluded_tables_never_appear(dump_module, tmp_path):
    """No artifact carries data from a table the policy excludes."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=20, link_rows=5, noise_rows=50)
    policy_path = _write_policy(tmp_path, _policy_text())

    artifacts = _generate(dump_module, db_path, policy_path)

    assert artifacts, "expected a non-empty projection"
    assert not any(path.startswith("noise_events/") for path in artifacts)
    joined = b"".join(artifacts.values())
    assert b"noise_events" not in joined
    assert b"noise-0" not in joined
    # The included tables did land, so the absence above is selection, not failure.
    assert b'INSERT INTO "alpha_records"' in joined
    assert b'INSERT INTO "link_rows"' in joined


def test_selection_follows_policy_not_code(dump_module, tmp_path):
    """The same database projects differently under two policies.

    This is the behavioral form of "selection is data": nothing about the
    dumper changes between these two runs.
    """
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=10, link_rows=10, noise_rows=10)
    policy_a = _write_policy(
        tmp_path,
        _policy_text(included=("alpha_records",), excluded=("link_rows", "noise_events")),
        name="a.toml",
    )
    policy_b = _write_policy(
        tmp_path,
        _policy_text(included=("noise_events",), excluded=("alpha_records", "link_rows")),
        name="b.toml",
    )

    tables_a = {path.partition("/")[0] for path in _generate(dump_module, db_path, policy_a)}
    tables_b = {path.partition("/")[0] for path in _generate(dump_module, db_path, policy_b)}

    assert tables_a == {"alpha_records"}
    assert tables_b == {"noise_events"}


def test_unclassified_table_is_a_hard_error(dump_module, tmp_path):
    """A table in neither policy set stops the dump instead of defaulting."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=5, noise_rows=5)
    policy_path = _write_policy(tmp_path, _policy_text(included=("alpha_records",), excluded=()))

    with pytest.raises(dump_module.UnclassifiedTableError) as excinfo:
        _generate(dump_module, db_path, policy_path)

    message = str(excinfo.value)
    assert "noise_events" in message
    assert "link_rows" in message


def test_policy_naming_an_absent_table_is_a_hard_error(dump_module, tmp_path):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=1)
    policy_path = _write_policy(
        tmp_path,
        _policy_text(included=("alpha_records", "not_a_real_table"), excluded=("link_rows", "noise_events")),
    )

    with pytest.raises(dump_module.MissingTableError) as excinfo:
        _generate(dump_module, db_path, policy_path)

    assert "not_a_real_table" in str(excinfo.value)


def test_dumper_has_no_hardcoded_table_list(dump_module):
    """Secondary guard: the dumper's own text names no governed table.

    The behavioral proof is ``test_selection_follows_policy_not_code``; this
    source-level assertion catches a governed-table literal creeping back in.
    """
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    leaked = sorted(name for name in REAL_TABLE_NAMES if name in source)
    assert leaked == [], f"dumper names governed tables directly: {leaked}"


def test_policy_rejects_a_table_in_both_sets(dump_module, tmp_path):
    policy_path = _write_policy(
        tmp_path,
        _policy_text(included=("alpha_records", "noise_events"), excluded=("noise_events",)),
    )
    with pytest.raises(dump_module.PolicyError):
        dump_module.load_policy(policy_path)


def test_policy_requires_recoverability_on_every_exclusion(dump_module, tmp_path):
    """An exclusion without a recorded justification is rejected."""
    text = (
        "schema_version = 1\n"
        "[budget]\nmax_file_bytes = 1000\nmax_total_bytes = 10000\ndefault_rows_per_chunk = 10\n"
        '[include]\ntables = ["alpha_records"]\n'
        '[[exclude]]\ntable = "noise_events"\nreason = "no recoverability recorded"\n'
    )
    policy_path = _write_policy(tmp_path, text)
    with pytest.raises(dump_module.PolicyError) as excinfo:
        dump_module.load_policy(policy_path)
    assert "recoverable" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Sharding (proposal F1.2)
# ---------------------------------------------------------------------------


def test_wide_table_shards_into_multiple_chunks(dump_module, tmp_path):
    """A table larger than one chunk span emits several non-empty chunks."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=250, link_rows=1, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=50))

    artifacts = _generate(dump_module, db_path, policy_path)

    chunks = sorted(path for path in artifacts if path.startswith("alpha_records/") and "schema" not in path)
    assert len(chunks) > 1, f"expected sharding, got {chunks}"
    # Chunk 0 spans rowids [0,50) and so holds 49 rows; rowid 250 opens a sixth
    # chunk. Chunk membership is the rowid range, not a count of rows.
    assert chunks == [f"alpha_records/{index:04d}.sql" for index in range(6)]
    for chunk in chunks:
        body = artifacts[chunk].decode("utf-8")
        assert body.count("INSERT INTO") > 0, f"{chunk} is an empty chunk"


def test_chunk_membership_follows_the_rowid_range_not_row_position(dump_module, tmp_path):
    """Chunk index is derived from rowid, so rowid gaps leave gaps in chunks."""
    # 6 rows at rowids 1, 101, 201, 301, 401, 501 with a 100-row chunk span.
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=6, alpha_rowid_step=100, link_rows=1, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=100))

    artifacts = _generate(dump_module, db_path, policy_path)
    chunks = sorted(path for path in artifacts if path.startswith("alpha_records/") and "schema" not in path)

    # Size-packed chunking would produce a single chunk of 6 rows. Range-keyed
    # chunking produces one chunk per occupied rowid span.
    assert chunks == [f"alpha_records/{index:04d}.sql" for index in range(6)]


def test_append_rewrites_only_tail_chunk(dump_module, tmp_path):
    """Appending a row leaves every earlier chunk byte-identical.

    This is the property that makes the projection cheap to keep in git: an
    append produces exactly one new blob, not a rewrite of the whole table.
    """
    # Gapped rowids (1, 3, 5, ... 499) so that chunk membership derived from the
    # rowid range is distinguishable from chunk membership derived from row
    # position: 250 rows occupy ten 50-wide rowid spans, not five.
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=250, alpha_rowid_step=2, link_rows=1, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=50))

    before = _generate(dump_module, db_path, policy_path)
    assert len(before) > 10

    connection = sqlite3.connect(db_path)
    try:
        connection.execute('INSERT INTO "alpha_records" (label, body) VALUES (?, ?)', ("appended", "appended-body"))
        connection.commit()
    finally:
        connection.close()

    after = _generate(dump_module, db_path, policy_path)

    # The appended row lands at rowid 500, which opens the [500,550) span.
    tail = "alpha_records/0010.sql"
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    assert changed == [tail], f"append touched more than the tail: {changed}"
    assert b"appended-body" in after[tail]
    # Everything else is byte-for-byte identical, including the schema artifact.
    for path in before:
        assert before[path] == after[path], f"{path} was rewritten by an append"


# ---------------------------------------------------------------------------
# Size budget and aggregate ceiling (proposal F1.3)
# ---------------------------------------------------------------------------


def test_no_emitted_file_exceeds_budget(dump_module, tmp_path):
    """Chunking keeps every artifact inside the per-file budget."""
    budget = 40_000
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=400, alpha_body="x" * 200, link_rows=1, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(max_file_bytes=budget, default_rows_per_chunk=100))

    artifacts = _generate(dump_module, db_path, policy_path)

    chunks = [p for p in artifacts if p.startswith("alpha_records/") and "schema" not in p]
    assert len(chunks) == 5, "fixture must actually span several chunks for this to mean anything"
    largest = max(len(content) for content in artifacts.values())
    assert largest <= budget
    # Guard against a vacuous pass: the fixture pushes chunks near the budget,
    # so it is chunking that keeps them under it, not a tiny dataset.
    assert largest > budget // 2, f"fixture too small to exercise the budget (largest {largest})"


def test_dumper_refuses_to_emit_oversized_chunk(dump_module, tmp_path):
    """The per-file guard fires rather than writing an oversized artifact."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=40, alpha_body="y" * 500, link_rows=1, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(max_file_bytes=4_000, default_rows_per_chunk=1_000))
    output = tmp_path / "out"

    with pytest.raises(dump_module.SizeBudgetExceeded) as excinfo:
        artifacts = _generate(dump_module, db_path, policy_path)
        dump_module.write_artifacts(output, artifacts)

    assert "alpha_records/0000.sql" in str(excinfo.value)
    assert not output.exists(), "fail-closed means nothing reaches disk"


def test_aggregate_dump_under_ceiling(dump_module, tmp_path):
    """The projection as a whole is measured against the aggregate ceiling."""
    ceiling = 500_000
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=300, alpha_body="z" * 100, link_rows=50, noise_rows=500)
    policy_path = _write_policy(
        tmp_path,
        _policy_text(max_file_bytes=100_000, max_total_bytes=ceiling, default_rows_per_chunk=100),
    )

    artifacts = _generate(dump_module, db_path, policy_path)

    total = sum(len(content) for content in artifacts.values())
    assert 0 < total <= ceiling
    # Exclusions are what keep the aggregate down: the excluded table alone
    # holds more rows than either included table.
    assert not any(path.startswith("noise_events/") for path in artifacts)


def test_dumper_refuses_to_exceed_aggregate_ceiling(dump_module, tmp_path):
    """The aggregate guard fires, so silent whole-corpus growth cannot land."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=300, alpha_body="z" * 100, link_rows=1, noise_rows=1)
    # Every individual chunk stays well inside the per-file budget; only the
    # aggregate is over. That isolates the ceiling guard from the file guard.
    policy_path = _write_policy(
        tmp_path,
        _policy_text(max_file_bytes=4_000, max_total_bytes=5_000, default_rows_per_chunk=10),
    )
    output = tmp_path / "out"

    with pytest.raises(dump_module.AggregateCeilingExceeded):
        artifacts = _generate(dump_module, db_path, policy_path)
        dump_module.write_artifacts(output, artifacts)

    assert not output.exists()


# ---------------------------------------------------------------------------
# Determinism, round-trip, freshness
# ---------------------------------------------------------------------------


def test_dump_is_byte_reproducible(dump_module, tmp_path):
    """Two dumps of an unchanged database are byte-identical."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=120, link_rows=30, noise_rows=10)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=50))

    first = _generate(dump_module, db_path, policy_path)
    second = _generate(dump_module, db_path, policy_path)

    assert first.keys() == second.keys()
    for path in first:
        assert first[path] == second[path], f"{path} differs between two dumps"


def test_dump_output_uses_lf_endings_only(dump_module, tmp_path):
    """Written artifacts carry no CR bytes, so the projection is stable across platforms."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=20, link_rows=5, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text())
    output = tmp_path / "out"

    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))

    written = sorted(output.rglob("*.sql"))
    assert written
    for path in written:
        assert b"\r" not in path.read_bytes(), f"{path} contains CR bytes"


def test_restore_round_trips_governed_tables(dump_module, tmp_path):
    """dump -> restore into an empty database -> re-dump is byte-identical."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=150, link_rows=40, noise_rows=25)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=50))
    output = tmp_path / "out"

    original = _generate(dump_module, db_path, policy_path)
    dump_module.write_artifacts(output, original)

    restored_db = tmp_path / "restored.db"
    dump_module.restore(output, restored_db, db_path)
    assert restored_db.exists()

    replay = _generate(dump_module, restored_db, policy_path)
    assert replay == original

    # Row counts survive, and the excluded table is genuinely absent.
    connection = sqlite3.connect(restored_db)
    try:
        assert connection.execute('SELECT COUNT(*) FROM "alpha_records"').fetchone()[0] == 150
        assert connection.execute('SELECT COUNT(*) FROM "link_rows"').fetchone()[0] == 40
        with pytest.raises(sqlite3.OperationalError):
            connection.execute('SELECT COUNT(*) FROM "noise_events"').fetchone()
    finally:
        connection.close()


def test_restore_recreates_indexes_after_loading_rows(dump_module, tmp_path):
    """Indexes are deferred to the end of the load, but they do get created.

    Deferring them is what keeps a real recovery practical; dropping them would
    silently produce a database that queries far slower than the original.
    """
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=40, link_rows=5, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=10))
    output = tmp_path / "out"
    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))

    restored_db = tmp_path / "restored.db"
    dump_module.restore(output, restored_db, db_path)

    connection = sqlite3.connect(restored_db)
    try:
        indexes = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL ORDER BY name"
            )
        ]
        # The index is usable, not merely present.
        plan = connection.execute(
            'EXPLAIN QUERY PLAN SELECT rowid FROM "alpha_records" WHERE label = ?', ("label-3",)
        ).fetchall()
    finally:
        connection.close()

    assert indexes == ["idx_alpha_label"]
    assert any("idx_alpha_label" in str(step) for step in plan), plan


def test_schema_statements_with_embedded_semicolons_restore_correctly(dump_module, tmp_path):
    """Splitting the schema artifact is quote-aware.

    A semicolon inside a string default or a partial-index predicate must not
    be mistaken for a statement terminator; a naive split would truncate the
    DDL and the restore would fail.
    """
    db_path = tmp_path / "kb.db"
    connection = sqlite3.connect(db_path)
    try:
        # SQLite stores this DDL verbatim, newlines and all. The default value
        # is a multi-line string literal whose first line ends in a semicolon,
        # which is exactly where a line-oriented splitter would cut.
        connection.execute(
            'CREATE TABLE "quirky" (\n'
            "  rowid INTEGER PRIMARY KEY,\n"
            "  label TEXT DEFAULT 'ends with a semicolon;\n"
            "second line of the default',\n"
            "  payload TEXT)"
        )
        connection.execute('CREATE INDEX "idx_quirky_partial" ON "quirky" (payload) WHERE label <> \'skip;me\'')
        for index in range(5):
            connection.execute('INSERT INTO "quirky" (payload) VALUES (?)', (f"payload-{index}",))
        connection.commit()
    finally:
        connection.close()

    policy_path = _write_policy(tmp_path, _policy_text(included=("quirky",), excluded=()))
    output = tmp_path / "out"
    original = _generate(dump_module, db_path, policy_path)
    dump_module.write_artifacts(output, original)
    assert b"ends with a semicolon;\n" in original["quirky/schema.sql"]

    restored_db = tmp_path / "restored.db"
    dump_module.restore(output, restored_db, db_path)

    connection = sqlite3.connect(restored_db)
    try:
        assert connection.execute('SELECT COUNT(*) FROM "quirky"').fetchone()[0] == 5
        default_clause = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'quirky'"
        ).fetchone()[0]
        indexes = [
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL")
        ]
    finally:
        connection.close()

    assert "ends with a semicolon;\nsecond line of the default" in default_clause
    assert indexes == ["idx_quirky_partial"]
    assert _generate(dump_module, restored_db, policy_path) == original


def test_rowid_gaps_survive_the_round_trip(dump_module, tmp_path):
    """Row identity is preserved exactly, including for tables with no rowid alias.

    ``link_rows`` declares no primary key, so its rowids are implicit. If they
    were re-assigned on restore, chunk membership would shift and the replayed
    projection would not match.
    """
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=30, link_rows=30, noise_rows=1)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute('DELETE FROM "link_rows" WHERE rowid IN (2, 3, 4, 17)')
        connection.execute('DELETE FROM "alpha_records" WHERE rowid IN (5, 6, 20)')
        connection.commit()
        source_link_rowids = [row[0] for row in connection.execute('SELECT rowid FROM "link_rows" ORDER BY rowid')]
    finally:
        connection.close()
    assert 2 not in source_link_rowids and 17 not in source_link_rowids

    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=10))
    output = tmp_path / "out"
    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))

    restored_db = tmp_path / "restored.db"
    dump_module.restore(output, restored_db, db_path)

    connection = sqlite3.connect(restored_db)
    try:
        restored_link_rowids = [row[0] for row in connection.execute('SELECT rowid FROM "link_rows" ORDER BY rowid')]
    finally:
        connection.close()
    assert restored_link_rowids == source_link_rowids


def test_check_reports_drift_without_writing(dump_module, tmp_path):
    """``check`` detects a mutated row and leaves the projection untouched."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=60, link_rows=10, noise_rows=5)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=25))
    output = tmp_path / "out"

    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))
    on_disk_before = {p: p.read_bytes() for p in sorted(output.rglob("*.sql"))}
    assert not dump_module.compare_artifacts(output, _generate(dump_module, db_path, policy_path))

    connection = sqlite3.connect(db_path)
    try:
        connection.execute('UPDATE "alpha_records" SET body = ? WHERE rowid = 3', ("mutated",))
        connection.commit()
    finally:
        connection.close()

    drifts = dump_module.compare_artifacts(output, _generate(dump_module, db_path, policy_path))

    assert [d.path for d in drifts] == ["alpha_records/0000.sql"]
    assert drifts[0].kind == "changed"
    on_disk_after = {p: p.read_bytes() for p in sorted(output.rglob("*.sql"))}
    assert on_disk_after == on_disk_before, "check must not write"


def test_check_reports_missing_and_stale_artifacts(dump_module, tmp_path):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=60, link_rows=10, noise_rows=5)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=25))
    output = tmp_path / "out"
    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))

    (output / "alpha_records" / "0001.sql").unlink()
    (output / "alpha_records" / "9999.sql").write_bytes(b"-- left over\n")

    drifts = {
        d.path: d.kind for d in dump_module.compare_artifacts(output, _generate(dump_module, db_path, policy_path))
    }

    assert drifts == {
        "alpha_records/0001.sql": "missing",
        "alpha_records/9999.sql": "stale",
    }


def test_dump_drops_stale_artifacts(dump_module, tmp_path):
    """A re-dump removes artifacts the current database no longer produces."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=120, link_rows=5, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=25))
    output = tmp_path / "out"
    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))
    assert (output / "alpha_records" / "0004.sql").exists()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute('DELETE FROM "alpha_records" WHERE rowid > 50')
        connection.commit()
    finally:
        connection.close()

    removed = dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))

    assert "alpha_records/0004.sql" in removed
    assert not (output / "alpha_records" / "0004.sql").exists()
    assert not dump_module.compare_artifacts(output, _generate(dump_module, db_path, policy_path))


# ---------------------------------------------------------------------------
# Restore safety (GO verdict V6) and WAL safety
# ---------------------------------------------------------------------------


def test_restore_refuses_the_canonical_database(dump_module, tmp_path):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=10, link_rows=2, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text())
    output = tmp_path / "out"
    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))
    before = db_path.read_bytes()

    with pytest.raises(dump_module.RestoreRefused) as excinfo:
        dump_module.restore(output, db_path, db_path)

    assert "canonical" in str(excinfo.value)
    assert db_path.read_bytes() == before, "the canonical database must be untouched"


def test_restore_refuses_an_existing_target(dump_module, tmp_path):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=10, link_rows=2, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text())
    output = tmp_path / "out"
    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))

    occupied = tmp_path / "occupied.db"
    occupied.write_bytes(b"pre-existing bytes")

    with pytest.raises(dump_module.RestoreRefused):
        dump_module.restore(output, occupied, db_path)

    assert occupied.read_bytes() == b"pre-existing bytes"


def test_restore_refuses_a_target_with_wal_sidecars(dump_module, tmp_path):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=10, link_rows=2, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text())
    output = tmp_path / "out"
    dump_module.write_artifacts(output, _generate(dump_module, db_path, policy_path))

    target = tmp_path / "live.db"
    Path(f"{target}-wal").write_bytes(b"")

    with pytest.raises(dump_module.RestoreRefused) as excinfo:
        dump_module.restore(output, target, db_path)

    assert "WAL" in str(excinfo.value)
    assert not target.exists()


def test_dump_under_a_concurrent_writer_sees_a_consistent_snapshot(dump_module, tmp_path):
    """A dump taken while another connection holds an open write completes,
    and reflects committed state only."""
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=40, link_rows=5, noise_rows=1, wal=True)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=25))

    writer = sqlite3.connect(db_path)
    try:
        writer.execute("BEGIN")
        writer.execute(
            'INSERT INTO "alpha_records" (label, body) VALUES (?, ?)',
            ("uncommitted", "uncommitted-body"),
        )

        during = _generate(dump_module, db_path, policy_path)
        assert b"uncommitted-body" not in b"".join(during.values())

        writer.commit()
    finally:
        writer.close()

    after = _generate(dump_module, db_path, policy_path)
    assert b"uncommitted-body" in b"".join(after.values())


def test_dump_leaves_the_source_database_unmodified(dump_module, tmp_path):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=40, link_rows=5, noise_rows=5)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=10))
    before = db_path.read_bytes()

    dump_module.write_artifacts(tmp_path / "out", _generate(dump_module, db_path, policy_path))

    assert db_path.read_bytes() == before


# ---------------------------------------------------------------------------
# Value serialization
# ---------------------------------------------------------------------------


def test_awkward_values_round_trip_through_the_projection(dump_module, tmp_path):
    """Quotes, newlines, NULLs, blobs, floats and unicode survive dump/restore."""
    db_path = tmp_path / "kb.db"
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(ALPHA_DDL)
        connection.execute(LINK_DDL)
        connection.execute(NOISE_DDL)
        awkward = [
            "it's got 'quotes'",
            "line one\nline two\r\nline three",
            None,
            "unicode ✓ — em dash",
            "trailing backslash \\",
            "-- not a comment; DROP TABLE alpha_records;",
        ]
        for index, body in enumerate(awkward, start=1):
            connection.execute(
                'INSERT INTO "alpha_records" (rowid, label, body) VALUES (?, ?, ?)',
                (index, f"label-{index}", body),
            )
        raw_values = [b"\x00\x01\xfe\xff", 1.5e-9, -0.0, 2**62, None, "plain text"]
        for index, raw in enumerate(raw_values):
            connection.execute(
                'INSERT INTO "link_rows" (left_ref, right_ref, raw_value) VALUES (?, ?, ?)',
                (index, f"right-{index}", raw),
            )
        connection.commit()
        source_typing = connection.execute(
            'SELECT typeof(raw_value), raw_value FROM "link_rows" ORDER BY rowid'
        ).fetchall()
    finally:
        connection.close()

    policy_path = _write_policy(tmp_path, _policy_text())
    output = tmp_path / "out"
    original = _generate(dump_module, db_path, policy_path)
    dump_module.write_artifacts(output, original)

    restored_db = tmp_path / "restored.db"
    dump_module.restore(output, restored_db, db_path)

    connection = sqlite3.connect(restored_db)
    try:
        bodies = [row[0] for row in connection.execute('SELECT body FROM "alpha_records" ORDER BY rowid')]
        restored_typing = connection.execute(
            'SELECT typeof(raw_value), raw_value FROM "link_rows" ORDER BY rowid'
        ).fetchall()
    finally:
        connection.close()

    assert bodies == awkward
    # Storage class as well as value: a REAL must not come back as text, and a
    # BLOB must not come back as a string.
    assert restored_typing == source_typing
    assert [kind for kind, _value in restored_typing] == [
        "blob",
        "real",
        "real",
        "integer",
        "null",
        "text",
    ]
    assert _generate(dump_module, restored_db, policy_path) == original


def test_sql_literal_rejects_non_representable_floats(dump_module):
    for value in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(dump_module.UnsupportedTableError):
            dump_module.sql_literal(value)


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


def test_cli_check_exits_nonzero_on_drift(dump_module, tmp_path, capsys):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=30, link_rows=5, noise_rows=2)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=10))
    output = tmp_path / "out"
    argv = [
        "--project-root",
        str(tmp_path),
        "--db",
        str(db_path),
        "--policy",
        str(policy_path),
        "--out",
        str(output),
    ]

    assert dump_module.main(["dump", *argv]) == 0
    assert dump_module.main(["check", *argv]) == 0

    connection = sqlite3.connect(db_path)
    try:
        connection.execute('INSERT INTO "alpha_records" (label, body) VALUES (?, ?)', ("new", "new"))
        connection.commit()
    finally:
        connection.close()

    capsys.readouterr()
    assert dump_module.main(["check", *argv]) == 1
    assert "drifted" in capsys.readouterr().err


def test_cli_reports_the_measured_aggregate(dump_module, tmp_path, capsys):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=60, link_rows=10, noise_rows=2)
    policy_path = _write_policy(tmp_path, _policy_text(default_rows_per_chunk=20))
    output = tmp_path / "out"

    dump_module.main(
        [
            "dump",
            "--project-root",
            str(tmp_path),
            "--db",
            str(db_path),
            "--policy",
            str(policy_path),
            "--out",
            str(output),
        ]
    )

    captured = capsys.readouterr().out
    total = sum(p.stat().st_size for p in output.rglob("*.sql"))
    assert f"{total} bytes" in captured
    assert "ceiling" in captured and "budget" in captured


def test_cli_fails_closed_with_exit_two_on_budget_violation(dump_module, tmp_path, capsys):
    db_path = _build_db(tmp_path / "kb.db", alpha_rows=40, alpha_body="y" * 500, noise_rows=1)
    policy_path = _write_policy(tmp_path, _policy_text(max_file_bytes=4_000, default_rows_per_chunk=1_000))
    output = tmp_path / "out"

    exit_code = dump_module.main(
        [
            "dump",
            "--project-root",
            str(tmp_path),
            "--db",
            str(db_path),
            "--policy",
            str(policy_path),
            "--out",
            str(output),
        ]
    )

    assert exit_code == 2
    assert "budget" in capsys.readouterr().err
    assert not output.exists()
