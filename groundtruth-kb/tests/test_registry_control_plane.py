# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Specification-derived tests for the WI-5441 registry control plane."""

from __future__ import annotations

import json
import multiprocessing
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path

import pytest
from click.testing import CliRunner
from scripts.bridge_work_intent_registry import acquire
from scripts.bridge_work_intent_registry import release as release_claim

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import registry_control_plane, sot_registry
from groundtruth_kb.project.registry_control_plane import (
    IMPLEMENTATION_ARTIFACTS,
    LEGACY_COVERAGE_MODES,
    RegistryAuthorizationError,
    RegistryCoverageError,
    RegistryGenerationConflict,
    RegistryProjectionMismatch,
    RegistryRecoveryRequired,
    RegistryResolver,
    RegistryTransactionInProgress,
    amend_artifact,
    append_passive_observation,
    apply_registry_transaction,
    bootstrap_legacy_registry,
    census_registry,
    compensate_bridge_publication,
    consume_bridge_publication_capability,
    consume_observation_capability,
    load_registry_snapshot,
    mint_bridge_publication_capability,
    mint_observation_capability,
    preview_registry_registration,
    recover_bridge_publication,
    recover_registry,
    recover_wi5441_bridge_aggregate,
    register_artifacts,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import (
    SoTArtifact,
    _load_toml_unlocked,
    load_projection,
    load_toml,
    sync_projection,
)


def _record(record_id: str, storage_path: str, coverage_mode: str = "exact") -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path=storage_path,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="gt registry register",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode=coverage_mode,
    )


def _fixture_generation(tmp_path: Path, records: list[SoTArtifact]) -> tuple[Path, Path, Path]:
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        tmp_path
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    registry.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    payload = serialize_registry(records)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(records, db_path, changed_by="test", change_reason="fixture")
    return registry, packaged, db_path


def _transaction_kwargs(tmp_path: Path, registry: Path, packaged: Path, db_path: Path) -> dict[str, object]:
    return {
        "actor_session": "test-session",
        "changed_by": "test/prime-builder",
        "change_reason": "WI-5441 test transaction",
        "start_packet_hash": "sha256:test-start",
        "pauth_id": "PAUTH-WI5441-TEST",
        "bridge_id": "gtkb-wi5441-registry-control-plane-reverse-coverage",
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }


def _spawned_amend_worker(
    artifact_id: str,
    note: str,
    project_root: str,
    registry_path: str,
    packaged_registry_path: str,
    db_path: str,
    barrier: object,
    results: object,
) -> None:
    """Force each spawned writer to take its first snapshot at one generation."""

    real_load = registry_control_plane.load_registry_snapshot
    first_read = True

    def synchronized_first_load(*args: object, **kwargs: object) -> object:
        nonlocal first_read
        snapshot = real_load(*args, **kwargs)
        if first_read:
            first_read = False
            barrier.wait(timeout=30)  # type: ignore[attr-defined]
        return snapshot

    registry_control_plane.load_registry_snapshot = synchronized_first_load  # type: ignore[assignment]
    kwargs = {
        "actor_session": f"spawn-{artifact_id}",
        "changed_by": "test/prime-builder",
        "change_reason": "WI-5714 spawned writer",
        "start_packet_hash": "sha256:test-start",
        "pauth_id": "PAUTH-WI5714-TEST",
        "bridge_id": "gtkb-wi5714-registry-write-linearizability",
        "project_root": Path(project_root),
        "registry_path": Path(registry_path),
        "packaged_registry_path": Path(packaged_registry_path),
        "db_path": Path(db_path),
    }
    try:
        amend_artifact(artifact_id, {"notes": note}, **kwargs)
        results.put(("ok", artifact_id))  # type: ignore[attr-defined]
    except BaseException as exc:
        results.put(("error", artifact_id, type(exc).__name__, str(exc)))  # type: ignore[attr-defined]


def _spawned_snapshot_reader(
    ordinal: int,
    project_root: str,
    registry_path: str,
    packaged_registry_path: str,
    db_path: str,
    start_barrier: object,
    inside_read_barrier: object,
    results: object,
) -> None:
    """Prove every spawned reader is simultaneously inside the optimistic path."""

    real_marker = registry_control_plane._read_terminal_generation_marker
    marker_reads = 0

    def synchronized_first_marker(path: Path) -> object:
        nonlocal marker_reads
        marker = real_marker(path)
        marker_reads += 1
        if marker_reads == 1:
            inside_read_barrier.wait(timeout=300)  # type: ignore[attr-defined]
        return marker

    registry_control_plane._read_terminal_generation_marker = synchronized_first_marker  # type: ignore[assignment]
    try:
        start_barrier.wait(timeout=300)  # type: ignore[attr-defined]
        started = time.monotonic()
        snapshot = load_registry_snapshot(
            project_root=Path(project_root),
            registry_path=Path(registry_path),
            packaged_registry_path=Path(packaged_registry_path),
            db_path=Path(db_path),
        )
        results.put(  # type: ignore[attr-defined]
            (
                "ok",
                ordinal,
                started,
                time.monotonic(),
                snapshot.generation_digest,
                len(snapshot.records),
                marker_reads,
            )
        )
    except BaseException as exc:
        results.put(("error", ordinal, type(exc).__name__, str(exc)))  # type: ignore[attr-defined]


def _terminal_generation_fixture(
    tmp_path: Path,
    records: list[SoTArtifact],
) -> tuple[Path, Path, Path]:
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    apply_registry_transaction(
        records,
        operation="amend",
        **_transaction_kwargs(tmp_path, registry, packaged, db_path),
    )
    return registry, packaged, db_path


def test_reviewed_legacy_map_is_exactly_fifty_and_explicit() -> None:
    assert len(LEGACY_COVERAGE_MODES) == 50
    assert set(LEGACY_COVERAGE_MODES.values()) == {
        "exact",
        "recursive",
        "glob",
        "opaque_container",
        "virtual",
    }
    assert LEGACY_COVERAGE_MODES["bridge-versioned-files"] == "glob"
    assert LEGACY_COVERAGE_MODES["generated-runtime-state-tree"] == "opaque_container"
    assert LEGACY_COVERAGE_MODES["governance-config-tree"] == "recursive"


def test_resolver_rejects_unsafe_case_collision_and_overlap() -> None:
    with pytest.raises(RegistryCoverageError, match="project-relative"):
        RegistryResolver([_record("escape", "../outside.txt")])
    with pytest.raises(RegistryCoverageError, match="case-fold"):
        RegistryResolver([_record("one", "A.txt"), _record("two", "a.txt")])
    with pytest.raises(RegistryCoverageError, match="ambiguous"):
        RegistryResolver(
            [
                _record("tree", "tree/", "recursive"),
                _record("leaf", "tree/leaf.txt"),
            ]
        )


def test_opaque_container_authorizes_operations_without_claiming_child_identity() -> None:
    opaque = _record("runtime", ".gtkb-state/", "opaque_container")
    resolver = RegistryResolver([opaque])

    assert resolver.resolve(".gtkb-state/transactions/one.json") is None
    assert resolver.resolve_operation_path(".gtkb-state/transactions/one.json") == opaque
    assert resolver.resolve_operation_path("outside.json") is None


def test_registry_lock_timeout_generous_default_and_env_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-5788: control-plane lock acquisition timeout is generous + env-configurable.

    Precedence: explicit caller value > ``GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS``
    env var > generous default. A missing/malformed/non-positive env var fails
    open to the generous default (never fail-closed), and the default is well
    above the retired 30s deadline that hard-failed under sustained concurrent
    writers. Lock semantics are unchanged; only the acquisition-wait deadline
    is resolved here.
    """
    lock_path = tmp_path / "control-plane.lock"

    # Generous default when no env var is set (fail-open, not the retired 30s).
    monkeypatch.delenv("GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS", raising=False)
    default_timeout = registry_control_plane._RegistryFileLock(lock_path).timeout
    assert default_timeout == registry_control_plane._DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS
    assert default_timeout >= 120.0
    assert default_timeout != 30.0

    # Env var overrides the default.
    monkeypatch.setenv("GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS", "45.5")
    assert registry_control_plane._RegistryFileLock(lock_path).timeout == 45.5

    # Explicit caller value wins over both env var and default.
    assert registry_control_plane._RegistryFileLock(lock_path, timeout=3.0).timeout == 3.0

    # Malformed or non-positive env values fail open to the generous default.
    for bad in ("not-a-number", "0", "-5"):
        monkeypatch.setenv("GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS", bad)
        assert (
            registry_control_plane._RegistryFileLock(lock_path).timeout
            == registry_control_plane._DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS
        )


def test_snapshot_requires_byte_identical_packaged_mirror(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    packaged.write_text("drift", encoding="utf-8")
    with pytest.raises(Exception, match="byte-identical"):
        load_registry_snapshot(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        )


def test_snapshot_reports_projection_drift_as_typed_failure(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    changed = [replace(records[0], mutation_api="changed")]
    payload = serialize_registry(changed)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)

    with pytest.raises(RegistryProjectionMismatch, match="parity failure"):
        load_registry_snapshot(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        )


def test_terminal_marker_binds_committed_new_and_aborted_old_digests(tmp_path: Path) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(tmp_path, records)

    committed = registry_control_plane._read_terminal_generation_marker(db_path)
    assert committed is not None
    with sqlite3.connect(db_path) as conn:
        committed_row = conn.execute(
            "SELECT new_canonical_digest, new_packaged_digest, new_projection_digest "
            "FROM sot_registry_transaction_journal ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
    assert committed.journal_state == "committed"
    assert (committed.canonical_digest, committed.packaged_digest, committed.projection_digest) == committed_row

    changed = [replace(records[0], notes="candidate")]

    def fail_after_prepare(phase: str) -> None:
        if phase == "after_prepare":
            raise RuntimeError(phase)

    with pytest.raises(RuntimeError, match="after_prepare"):
        apply_registry_transaction(
            changed,
            operation="amend",
            failure_injector=fail_after_prepare,
            **_transaction_kwargs(tmp_path, registry, packaged, db_path),
        )
    recover_registry(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    aborted = registry_control_plane._read_terminal_generation_marker(db_path)
    assert aborted is not None
    with sqlite3.connect(db_path) as conn:
        aborted_row = conn.execute(
            "SELECT old_canonical_digest, old_packaged_digest, old_projection_digest "
            "FROM sot_registry_transaction_journal ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
    assert aborted.journal_state == "aborted"
    assert (aborted.canonical_digest, aborted.packaged_digest, aborted.projection_digest) == aborted_row


def test_stable_snapshot_reads_two_markers_without_exclusive_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(tmp_path, records)
    real_marker = registry_control_plane._read_terminal_generation_marker
    marker_reads = 0

    def counted_marker(path: Path) -> object:
        nonlocal marker_reads
        marker_reads += 1
        return real_marker(path)

    class ForbiddenExclusiveLock:
        def __init__(self, path: Path, timeout: float = 30.0) -> None:
            del path, timeout

        def __enter__(self) -> object:
            raise AssertionError("stable optimistic reader acquired the exclusive lock")

        def __exit__(self, *args: object) -> None:
            del args

    monkeypatch.setattr(registry_control_plane, "_read_terminal_generation_marker", counted_marker)
    monkeypatch.setattr(registry_control_plane, "_RegistryFileLock", ForbiddenExclusiveLock)
    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert [record.id for record in snapshot.records] == ["member"]
    assert marker_reads == 2


def test_changed_marker_replays_snapshot_exclusive_exactly_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(tmp_path, records)
    marker = registry_control_plane._read_terminal_generation_marker(db_path)
    assert marker is not None
    markers = iter((marker, replace(marker, row_digest=marker.row_digest + "-changed")))
    real_exclusive = registry_control_plane._load_registry_snapshot_exclusive
    fallback_calls = 0

    def changed_marker(path: Path) -> object:
        del path
        return next(markers)

    def counted_exclusive(paths: object) -> object:
        nonlocal fallback_calls
        fallback_calls += 1
        return real_exclusive(paths)  # type: ignore[arg-type]

    monkeypatch.setattr(registry_control_plane, "_read_terminal_generation_marker", changed_marker)
    monkeypatch.setattr(registry_control_plane, "_load_registry_snapshot_exclusive", counted_exclusive)
    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert [record.id for record in snapshot.records] == ["member"]
    assert fallback_calls == 1


def test_second_marker_read_failure_replays_snapshot_exclusive_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(tmp_path, records)
    marker = registry_control_plane._read_terminal_generation_marker(db_path)
    assert marker is not None
    marker_reads = 0
    real_exclusive = registry_control_plane._load_registry_snapshot_exclusive
    fallback_calls = 0

    def failing_second_marker(path: Path) -> object:
        nonlocal marker_reads
        del path
        marker_reads += 1
        if marker_reads == 1:
            return marker
        raise sqlite3.OperationalError("marker read failed")

    def counted_exclusive(paths: object) -> object:
        nonlocal fallback_calls
        fallback_calls += 1
        return real_exclusive(paths)  # type: ignore[arg-type]

    monkeypatch.setattr(registry_control_plane, "_read_terminal_generation_marker", failing_second_marker)
    monkeypatch.setattr(registry_control_plane, "_load_registry_snapshot_exclusive", counted_exclusive)
    assert load_registry_snapshot(project_root=tmp_path).records == tuple(records)
    assert fallback_calls == 1


def test_stable_toml_body_error_preserves_exact_exception_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, _, _ = _terminal_generation_fixture(tmp_path, records)
    sentinel = RuntimeError("exact body error")

    def fail_parse(*args: object, **kwargs: object) -> list[SoTArtifact]:
        del args, kwargs
        raise sentinel

    monkeypatch.setattr(sot_registry, "_load_toml_bytes", fail_parse)
    with pytest.raises(RuntimeError, match="exact body error") as captured:
        load_toml(registry)
    assert captured.value is sentinel


def test_changed_marker_replays_toml_body_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, _, db_path = _terminal_generation_fixture(tmp_path, records)
    marker = registry_control_plane._read_terminal_generation_marker(db_path)
    assert marker is not None
    markers = iter((marker, replace(marker, row_digest=marker.row_digest + "-changed")))
    real_parse = sot_registry._load_toml_bytes
    parse_calls = 0
    real_barrier = registry_control_plane._exclusive_registry_read_barrier
    fallback_calls = 0

    def changed_marker(path: Path) -> object:
        del path
        return next(markers)

    def fail_once(payload: bytes, *, allow_missing_coverage: bool = False) -> list[SoTArtifact]:
        nonlocal parse_calls
        parse_calls += 1
        if parse_calls == 1:
            raise RuntimeError("interposed body error")
        return real_parse(payload, allow_missing_coverage=allow_missing_coverage)

    @contextmanager
    def counted_barrier(**kwargs: object):
        nonlocal fallback_calls
        fallback_calls += 1
        with real_barrier(**kwargs) as paths:
            yield paths

    monkeypatch.setattr(registry_control_plane, "_read_terminal_generation_marker", changed_marker)
    monkeypatch.setattr(sot_registry, "_load_toml_bytes", fail_once)
    monkeypatch.setattr(registry_control_plane, "_exclusive_registry_read_barrier", counted_barrier)
    assert load_toml(registry) == records
    assert parse_calls == 2
    assert fallback_calls == 1


def test_missing_and_incomplete_markers_use_exclusive_compatibility(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [_record("member", "member.txt")]
    missing_root = tmp_path / "missing"
    missing_root.mkdir()
    (missing_root / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _fixture_generation(missing_root, records)
    real_lock = registry_control_plane._RegistryFileLock
    lock_entries = 0

    class CountedLock(real_lock):
        def __enter__(self) -> object:
            nonlocal lock_entries
            lock_entries += 1
            return super().__enter__()

    monkeypatch.setattr(registry_control_plane, "_RegistryFileLock", CountedLock)
    assert load_registry_snapshot(project_root=missing_root).records == tuple(records)
    missing_lock_entries = lock_entries

    incomplete_root = tmp_path / "incomplete"
    incomplete_root.mkdir()
    (incomplete_root / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(incomplete_root, records)
    lock_entries = missing_lock_entries
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE sot_registry_transaction_journal SET new_projection_digest = NULL "
            "WHERE rowid = (SELECT MAX(rowid) FROM sot_registry_transaction_journal)"
        )
    assert load_registry_snapshot(project_root=incomplete_root).records == tuple(records)
    assert lock_entries == 2


def test_standalone_loaders_fall_back_when_generation_companions_are_missing(tmp_path: Path) -> None:
    records = [_record("member", "member.txt")]

    toml_root = tmp_path / "toml"
    toml_root.mkdir()
    (toml_root / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, _ = _terminal_generation_fixture(toml_root, records)
    packaged.unlink()
    assert load_toml(registry) == records

    projection_root = tmp_path / "projection"
    projection_root.mkdir()
    (projection_root / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(projection_root, records)
    registry.unlink()
    packaged.unlink()
    assert load_projection(db_path) == records


def test_optimistic_sqlite_connection_is_query_only_and_never_creates(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    with registry_control_plane._open_registry_read_only_connection(db_path) as conn:
        assert conn.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute("CREATE TABLE forbidden_write (id INTEGER)")

    missing = tmp_path / "missing.db"
    with pytest.raises(sqlite3.OperationalError), registry_control_plane._open_registry_read_only_connection(missing):
        pass
    assert not missing.exists()


def test_public_loaders_use_query_only_generation_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, _, db_path = _terminal_generation_fixture(tmp_path, records)
    real_open = registry_control_plane._open_registry_read_only_connection
    query_only_values: list[int] = []

    @contextmanager
    def observed_open(path: Path):
        with real_open(path) as conn:
            query_only_values.append(conn.execute("PRAGMA query_only").fetchone()[0])
            yield conn

    monkeypatch.setattr(registry_control_plane, "_open_registry_read_only_connection", observed_open)
    assert load_toml(registry) == records
    assert load_projection(db_path) == records
    assert query_only_values and set(query_only_values) == {1}


def test_writer_interposition_returns_one_complete_new_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [_record("member", "member.txt")]
    desired = [replace(records[0], notes="writer committed")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(tmp_path, records)
    reader_entered = threading.Event()
    writer_done = threading.Event()
    writer_errors: list[BaseException] = []
    real_projection_load = registry_control_plane._load_projection_from_connection
    projection_calls = 0

    def interposed_projection(conn: object, **kwargs: object) -> list[SoTArtifact]:
        nonlocal projection_calls
        projection_calls += 1
        if projection_calls == 1:
            reader_entered.set()
            if not writer_done.wait(300):
                raise TimeoutError("writer did not complete during optimistic read")
        return real_projection_load(conn, **kwargs)  # type: ignore[arg-type]

    def writer() -> None:
        if not reader_entered.wait(300):
            writer_errors.append(TimeoutError("reader never entered optimistic projection read"))
            writer_done.set()
            return
        try:
            apply_registry_transaction(
                desired,
                operation="amend",
                **_transaction_kwargs(tmp_path, registry, packaged, db_path),
            )
        except BaseException as exc:
            writer_errors.append(exc)
        finally:
            writer_done.set()

    monkeypatch.setattr(registry_control_plane, "_load_projection_from_connection", interposed_projection)
    writer_thread = threading.Thread(target=writer, daemon=True)
    writer_thread.start()
    snapshot = load_registry_snapshot(project_root=tmp_path)
    writer_thread.join(timeout=300)
    assert not writer_thread.is_alive()
    assert writer_errors == []
    assert snapshot.records == tuple(desired)


def test_four_spawned_readers_overlap_while_writer_lock_is_held(tmp_path: Path) -> None:
    records = [_record("member", "member.txt")]
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    registry, packaged, db_path = _terminal_generation_fixture(tmp_path, records)
    paths = registry_control_plane.RegistryPaths.resolve(project_root=tmp_path)
    context = multiprocessing.get_context("spawn")
    start_barrier = context.Barrier(5)
    inside_read_barrier = context.Barrier(4)
    results = context.Queue()
    processes = [
        context.Process(
            target=_spawned_snapshot_reader,
            args=(
                ordinal,
                str(tmp_path),
                str(registry),
                str(packaged),
                str(db_path),
                start_barrier,
                inside_read_barrier,
                results,
            ),
        )
        for ordinal in range(4)
    ]
    deadline = time.monotonic() + 300
    outcomes: list[tuple[object, ...]] = []
    try:
        with registry_control_plane._RegistryFileLock(paths.lock_path):
            for process in processes:
                process.start()
            start_barrier.wait(timeout=max(0.1, deadline - time.monotonic()))
            for _ in processes:
                outcomes.append(results.get(timeout=max(0.1, deadline - time.monotonic())))
    finally:
        for process in processes:
            process.join(timeout=max(0.0, deadline - time.monotonic()))
            if process.is_alive():
                process.terminate()
                process.join(timeout=30)
        results.close()
        results.join_thread()

    assert all(process.exitcode == 0 for process in processes), outcomes
    assert len(outcomes) == 4 and all(outcome[0] == "ok" for outcome in outcomes), outcomes
    assert len({outcome[4] for outcome in outcomes}) == 1
    assert {outcome[5] for outcome in outcomes} == {1}
    assert {outcome[6] for outcome in outcomes} == {2}
    assert max(float(outcome[2]) for outcome in outcomes) < min(float(outcome[3]) for outcome in outcomes)


@pytest.mark.parametrize(
    ("phase", "outcome"),
    [
        ("after_prepare", "old"),
        ("after_canonical_replace", "new"),
        ("after_packaged_replace", "new"),
        ("after_db_update", "new"),
        ("after_journal_commit", "new"),
    ],
)
def test_fault_phases_never_expose_mixed_generation(tmp_path: Path, phase: str, outcome: str) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    old = [_record("one", "one.txt")]
    desired = [*old, _record("two", "two.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, old)

    def fail_at(observed: str) -> None:
        if observed == phase:
            raise RuntimeError(phase)

    with pytest.raises(RuntimeError, match=phase):
        apply_registry_transaction(
            desired,
            operation="register",
            failure_injector=fail_at,
            **_transaction_kwargs(tmp_path, registry, packaged, db_path),
        )
    if phase != "after_journal_commit":
        with pytest.raises(RegistryTransactionInProgress):
            load_registry_snapshot(
                project_root=tmp_path,
                registry_path=registry,
                packaged_registry_path=packaged,
                db_path=db_path,
            )
    recover_registry(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert {record.id for record in snapshot.records} == ({"one"} if outcome == "old" else {"one", "two"})


def test_registry_recovery_marks_unknown_digest_combination_repair_required(
    tmp_path: Path,
) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    old = [_record("one", "one.txt")]
    desired = [*old, _record("two", "two.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, old)

    def fail_after_canonical(observed: str) -> None:
        if observed == "after_canonical_replace":
            raise RuntimeError(observed)

    with pytest.raises(RuntimeError, match="after_canonical_replace"):
        apply_registry_transaction(
            desired,
            operation="register",
            failure_injector=fail_after_canonical,
            **_transaction_kwargs(tmp_path, registry, packaged, db_path),
        )
    packaged.write_text("unknown generation\n", encoding="utf-8")

    with pytest.raises(RegistryRecoveryRequired, match="mixed or unknown generation"):
        recover_registry(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        )

    conn = sqlite3.connect(db_path)
    try:
        state = conn.execute(
            "SELECT journal_state FROM sot_registry_transaction_journal ORDER BY rowid DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    assert state == "repair_required"


def test_identical_transaction_retry_returns_same_receipt(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    records = [_record("one", "one.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    first = apply_registry_transaction(records, operation="amend", **kwargs)
    second = apply_registry_transaction(records, operation="amend", **kwargs)
    assert second.receipt_digest == first.receipt_digest
    assert second.idempotent_retry is True


def test_registry_transaction_updates_both_declaration_revisions(tmp_path: Path) -> None:
    records = [
        _record("canonical-registry", "config/registry/sot-artifacts.toml"),
        _record(
            "packaged-registry",
            "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml",
        ),
    ]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)

    apply_registry_transaction(
        records,
        operation="amend",
        **_transaction_kwargs(tmp_path, registry, packaged, db_path),
    )

    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert registry_currentness(snapshot, project_root=tmp_path, db_path=db_path) == {
        "current": True,
        "missing_revisions": [],
        "stale": [],
    }


def test_bootstrap_binds_exact_legacy_input_and_is_idempotent(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[2] / "config" / "registry" / "sot-artifacts.toml"
    current_records = _load_toml_unlocked(source, allow_missing_coverage=True)
    old_records = [record for record in current_records if record.id in LEGACY_COVERAGE_MODES]
    assert {record.id for record in old_records} == set(LEGACY_COVERAGE_MODES)
    legacy_payload = serialize_registry(old_records)
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        tmp_path
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    registry.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    registry.write_bytes(legacy_payload)
    packaged.write_bytes(legacy_payload)
    for artifact in IMPLEMENTATION_ARTIFACTS:
        target = tmp_path / artifact.storage_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# fixture\n", encoding="utf-8")
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(old_records, db_path, changed_by="test", change_reason="legacy fixture")
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    first = bootstrap_legacy_registry(**kwargs)
    second = bootstrap_legacy_registry(**kwargs)
    assert first.receipt_digest == second.receipt_digest
    assert second.idempotent_retry is True
    assert registry.read_bytes() == packaged.read_bytes()
    records = load_toml(registry)
    assert len(records) == 54
    assert all(record.coverage_mode is not None for record in records)


def test_census_uses_only_git_and_application_root_boundaries(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden").write_text("x", encoding="utf-8")
    (tmp_path / "applications" / "Demo").mkdir(parents=True)
    (tmp_path / "applications" / "Demo" / "hidden.py").write_text("x", encoding="utf-8")
    (tmp_path / "applications" / "registry.toml").write_text("x", encoding="utf-8")
    (tmp_path / ".gtkb-state" / "runtime").mkdir(parents=True)
    (tmp_path / ".gtkb-state" / "runtime" / "visible.log").write_text("x", encoding="utf-8")
    (tmp_path / "member.txt").write_text("x", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    census = census_registry(snapshot, project_root=tmp_path)
    paths = {entry.relative_path: entry for entry in census}
    assert paths[".git"].object_kind == "vcs_service_state"
    assert ".git/hidden" not in paths
    assert paths["applications/Demo"].object_kind == "hosted_application_root"
    assert "applications/Demo/hidden.py" not in paths
    assert "applications/registry.toml" in paths
    assert ".gtkb-state/runtime/visible.log" in paths


def test_opaque_container_may_register_a_service_owned_file(tmp_path: Path) -> None:
    records = [_record("database", "groundtruth.db", "opaque_container")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)

    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    assert snapshot.resolver.resolve("groundtruth.db") == records[0]


def test_passive_observation_records_view_without_authorizing_content(tmp_path: Path) -> None:
    member = tmp_path / "member.txt"
    member.write_text("before", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    member.write_text("direct owner edit", encoding="utf-8")

    revisions = append_passive_observation(
        target_paths=["member.txt"],
        evidence_view="working_tree",
        evidence_source_reference="filesystem-audit:test",
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM sot_artifact_revisions WHERE revision_id = ?",
            (revisions[0],),
        ).fetchone()
    finally:
        conn.close()
    assert member.read_text(encoding="utf-8") == "direct owner edit"
    assert row["actor_session"] == "unattributed_external"
    assert row["evidence_view"] == "working_tree"
    assert row["evidence_source_reference"] == "filesystem-audit:test"


def test_passive_observation_accepts_exact_aggregate_record_id(tmp_path: Path) -> None:
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "existing-001.md").write_text("NEW\n", encoding="utf-8")
    records = [_record("bridge-versioned-files", "bridge/*-[0-9][0-9][0-9].md", "glob")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        **_transaction_kwargs(tmp_path, registry, packaged, db_path),
    )
    (bridge / "observed-001.md").write_text("NEW\n", encoding="utf-8")

    revisions = append_passive_observation(
        record_ids=["bridge-versioned-files"],
        evidence_source_reference="aggregate-observer:test",
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    assert len(revisions) == 1
    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=db_path,
        record_ids={"bridge-versioned-files"},
    )["current"]


def test_registration_preview_binds_generation_manifest_and_authority(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    current = [_record("one", "one.txt")]
    addition = _record("two", "two.txt")
    registry, packaged, db_path = _fixture_generation(tmp_path, current)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    observer_digests = {
        "capability_inventory": f"sha256:{1:064x}",
        "governed_knowledge": f"sha256:{2:064x}",
        "package_and_entrypoint": f"sha256:{3:064x}",
        "physical_census": f"sha256:{4:064x}",
        "registered_dependency_closure": f"sha256:{5:064x}",
    }
    evidence_digest = f"sha256:{6:064x}"
    preview = preview_registry_registration(
        [addition],
        actor_session=str(kwargs["actor_session"]),
        start_packet_hash=str(kwargs["start_packet_hash"]),
        pauth_id=str(kwargs["pauth_id"]),
        bridge_id=str(kwargs["bridge_id"]),
        candidate_manifest_sha256="sha256:manifest",
        observer_input_digests=observer_digests,
        reconciliation_evidence_digest=evidence_digest,
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    receipt = register_artifacts(
        [addition],
        expected_generation_digest=preview.starting_generation_digest,
        candidate_manifest_sha256=preview.candidate_manifest_sha256,
        observer_input_digests=observer_digests,
        reconciliation_evidence_digest=evidence_digest,
        dry_run_receipt=preview.dry_run_receipt,
        **kwargs,
    )
    retry = register_artifacts(
        [addition],
        expected_generation_digest=preview.starting_generation_digest,
        candidate_manifest_sha256=preview.candidate_manifest_sha256,
        observer_input_digests=observer_digests,
        reconciliation_evidence_digest=evidence_digest,
        dry_run_receipt=preview.dry_run_receipt,
        **kwargs,
    )

    assert preview.candidate_count == 1
    assert preview.observer_input_digests == dict(sorted(observer_digests.items()))
    assert preview.reconciliation_evidence_digest == evidence_digest
    assert preview.desired_record_count == 2
    assert receipt.record_count == 2
    assert retry.idempotent_retry is True
    assert retry.journal_id == receipt.journal_id
    assert {
        record.id
        for record in load_registry_snapshot(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        ).records
    } == {"one", "two"}

    with pytest.raises(RegistryAuthorizationError, match="exact dry-run receipt"):
        register_artifacts(
            [addition],
            expected_generation_digest=preview.starting_generation_digest,
            candidate_manifest_sha256=preview.candidate_manifest_sha256,
            observer_input_digests={**observer_digests, "physical_census": f"sha256:{7:064x}"},
            reconciliation_evidence_digest=evidence_digest,
            dry_run_receipt=preview.dry_run_receipt,
            **kwargs,
        )


def test_observation_capability_is_bound_single_use_and_updates_revision(tmp_path: Path) -> None:
    member = tmp_path / "member.txt"
    member.write_text("before", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = {
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }
    capability = mint_observation_capability(
        target_paths=["member.txt"],
        session_id="session",
        tool_event_id="event",
        bridge_id="bridge",
        start_packet_hash="packet",
        pauth_decision={"allowed": True},
        operation="edit",
        authorized=True,
        **kwargs,
    )
    member.write_text("after", encoding="utf-8")
    revisions = consume_observation_capability(
        capability=capability["capability"],
        target_paths=["member.txt"],
        preimage_digests=capability["preimage_digests"],
        session_id="session",
        tool_event_id="event",
        bridge_id="bridge",
        start_packet_hash="packet",
        operation="edit",
        tool_succeeded=True,
        tool_result={"ok": True},
        changed_by="test",
        change_reason="test observation",
        **kwargs,
    )
    assert len(revisions) == 1
    with pytest.raises(RegistryAuthorizationError, match="already consumed"):
        consume_observation_capability(
            capability=capability["capability"],
            target_paths=["member.txt"],
            preimage_digests=capability["preimage_digests"],
            session_id="session",
            tool_event_id="event",
            bridge_id="bridge",
            start_packet_hash="packet",
            operation="edit",
            tool_succeeded=True,
            tool_result={"ok": True},
            changed_by="test",
            change_reason="replay",
            **kwargs,
        )


def test_amend_rejects_identity_locator_coverage_and_lifecycle_fields(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("member", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)

    for field, value in (
        ("id", "replacement"),
        ("storage_path", "replacement.txt"),
        ("coverage_mode", "recursive"),
        ("lifecycle", "deprecated"),
    ):
        with pytest.raises(RegistryAuthorizationError, match="transition authority"):
            amend_artifact("member", {field: value}, **kwargs)


def test_amend_spawned_disjoint_writers_preserve_every_accepted_delta(tmp_path: Path) -> None:
    records = [_record(f"member-{index}", f"member-{index}.txt") for index in range(4)]
    for record in records:
        (tmp_path / record.storage_path).write_text(record.id, encoding="utf-8")
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(4)
    results = context.Queue()
    processes = [
        context.Process(
            target=_spawned_amend_worker,
            args=(
                record.id,
                f"accepted-{record.id}",
                str(tmp_path),
                str(registry),
                str(packaged),
                str(db_path),
                barrier,
                results,
            ),
        )
        for record in records
    ]

    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=60)
        assert process.exitcode == 0

    outcomes = [results.get(timeout=5) for _ in processes]
    assert sorted(outcomes) == sorted(("ok", record.id) for record in records)
    snapshot = load_registry_snapshot(project_root=tmp_path)
    assert {record.id: record.notes for record in snapshot.records} == {
        record.id: f"accepted-{record.id}" for record in records
    }
    assert registry.read_bytes() == packaged.read_bytes()


def test_amend_generation_mismatch_raises_exact_conflict_before_mutation(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("member", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)
    stale = load_registry_snapshot(project_root=tmp_path)
    desired = [replace(stale.records[0], notes="committed")]
    apply_registry_transaction(
        desired,
        operation="amend",
        expected_prior_generation_digest=stale.generation_digest,
        **kwargs,
    )
    before_files = (registry.read_bytes(), packaged.read_bytes())
    with sqlite3.connect(db_path) as conn:
        before_rows = conn.execute("SELECT COUNT(*) FROM sot_registry_transaction_journal").fetchone()[0]

    with pytest.raises(RegistryGenerationConflict) as raised:
        apply_registry_transaction(
            desired,
            operation="amend",
            expected_prior_generation_digest=stale.generation_digest,
            **kwargs,
        )

    assert type(raised.value) is RegistryGenerationConflict
    assert (registry.read_bytes(), packaged.read_bytes()) == before_files
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sot_registry_transaction_journal").fetchone()[0] == before_rows


def test_amend_rebases_declared_delta_after_deterministic_interposed_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [_record("first", "first.txt"), _record("second", "second.txt")]
    for record in records:
        (tmp_path / record.storage_path).write_text(record.id, encoding="utf-8")
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)
    real_apply = registry_control_plane.apply_registry_transaction
    calls = 0

    def interposed_apply(desired: object, **apply_kwargs: object) -> object:
        nonlocal calls
        calls += 1
        if calls == 1:
            current = load_registry_snapshot(project_root=tmp_path)
            interposed = [
                replace(record, notes="accepted-second") if record.id == "second" else record
                for record in current.records
            ]
            real_apply(
                interposed,
                operation="amend",
                expected_prior_generation_digest=current.generation_digest,
                **kwargs,
            )
        return real_apply(desired, **apply_kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(registry_control_plane, "apply_registry_transaction", interposed_apply)
    amend_artifact("first", {"notes": "accepted-first"}, **kwargs)

    assert calls == 2
    snapshot = load_registry_snapshot(project_root=tmp_path)
    assert {record.id: record.notes for record in snapshot.records} == {
        "first": "accepted-first",
        "second": "accepted-second",
    }
    assert registry.read_bytes() == packaged.read_bytes()


def test_amend_retry_exhaustion_is_eight_attempts_and_has_no_side_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "member.txt").write_text("member", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)
    before_files = (registry.read_bytes(), packaged.read_bytes())
    before_snapshot = load_registry_snapshot(project_root=tmp_path)
    with sqlite3.connect(db_path) as conn:
        before_rows = conn.execute("SELECT COUNT(*) FROM sot_registry_transaction_journal").fetchone()[0]
    attempts = 0

    def always_conflict(*args: object, **apply_kwargs: object) -> object:
        nonlocal attempts
        attempts += 1
        raise RegistryGenerationConflict("forced conflict")

    monkeypatch.setattr(registry_control_plane, "apply_registry_transaction", always_conflict)
    with pytest.raises(RegistryGenerationConflict, match="forced conflict"):
        amend_artifact("member", {"notes": "never committed"}, **kwargs)

    assert attempts == 8
    assert (registry.read_bytes(), packaged.read_bytes()) == before_files
    after_snapshot = load_registry_snapshot(project_root=tmp_path)
    assert after_snapshot.records == before_snapshot.records
    assert after_snapshot.declaration_digest == before_snapshot.declaration_digest
    assert after_snapshot.packaged_digest == before_snapshot.packaged_digest
    assert after_snapshot.projection_digest == before_snapshot.projection_digest
    assert after_snapshot.generation_digest == before_snapshot.generation_digest
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sot_registry_transaction_journal").fetchone()[0] == before_rows


@pytest.mark.parametrize(
    "failure",
    [
        RegistryAuthorizationError("ordinary authorization failure"),
        RegistryTransactionInProgress("transaction in progress"),
        RegistryRecoveryRequired("recovery required"),
        RegistryCoverageError("coverage failure"),
        RuntimeError("unexpected failure"),
    ],
)
def test_amend_retries_only_generation_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: BaseException
) -> None:
    (tmp_path / "member.txt").write_text("member", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)
    attempts = 0

    def fail_once(*args: object, **apply_kwargs: object) -> object:
        nonlocal attempts
        attempts += 1
        raise failure

    monkeypatch.setattr(registry_control_plane, "apply_registry_transaction", fail_once)
    with pytest.raises(type(failure), match=str(failure)):
        amend_artifact("member", {"notes": "not committed"}, **kwargs)

    assert attempts == 1


def test_registry_cli_exposes_governed_control_plane_commands() -> None:
    result = CliRunner().invoke(main, ["registry", "--help"])

    assert result.exit_code == 0, result.output
    for command in ("register", "amend", "inspect", "recover", "validate"):
        assert command in result.output


def test_registry_cli_register_amend_sync_and_direct_observe_denial(tmp_path: Path) -> None:
    member = tmp_path / "member.txt"
    member.write_text("member", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\nproject_root = "{tmp_path.as_posix()}"\ndb_path = "{db_path.as_posix()}"\n',
        encoding="utf-8",
    )
    second = _record("second", "second.txt")
    (tmp_path / "second.txt").write_text("second", encoding="utf-8")
    authority = [
        "--bridge-id",
        "gtkb-wi5441-registry-control-plane-reverse-coverage",
        "--session-id",
        "test-session",
        "--start-packet-hash",
        "sha256:test-start",
        "--pauth-id",
        "PAUTH-WI5441-TEST",
        "--changed-by",
        "test/prime-builder",
        "--change-reason",
        "WI-5441 CLI fixture",
    ]
    runner = CliRunner()

    registered = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "register",
            "--record-json",
            json.dumps(asdict(second)),
            *authority,
        ],
    )
    assert registered.exit_code == 0, registered.output
    assert {record.id for record in load_registry_snapshot(project_root=tmp_path).records} == {
        "member",
        "second",
    }

    amended = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "amend",
            "second",
            "--changes-json",
            json.dumps({"notes": "amended through CLI"}),
            *authority,
        ],
    )
    assert amended.exit_code == 0, amended.output
    snapshot = load_registry_snapshot(project_root=tmp_path)
    assert next(record for record in snapshot.records if record.id == "second").notes == "amended through CLI"

    synced = runner.invoke(main, ["--config", str(config), "registry", "sync"])
    assert synced.exit_code == 0, synced.output
    assert "diagnostic-only" in synced.output

    event = tmp_path / "event.json"
    event.write_text("{}", encoding="utf-8")
    observed = runner.invoke(
        main,
        ["--config", str(config), "registry", "observe", "--event-file", str(event)],
    )
    assert observed.exit_code != 0
    assert "capability" in observed.output.lower()


def _bridge_publication_fixture(
    tmp_path: Path,
) -> tuple[str, str, bytes, Path, dict[str, object]]:
    slug = "typed-publication-fixture"
    session_id = "publication-session"
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    records = [
        _record(
            "bridge-versioned-files",
            "bridge/*-[0-9][0-9][0-9].md",
            "glob",
        )
    ]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        **_transaction_kwargs(tmp_path, registry, packaged, db_path),
    )
    assert acquire(slug, session_id, project_root=tmp_path)
    content = (
        "NEW\n"
        "::init gtkb pb\n"
        "::open build\n"
        "author_identity: prime-builder/codex\n"
        "author_harness_id: test\n"
        f"author_session_context_id: {session_id}\n"
        "author_model: fixture\n"
        "author_model_version: fixture\n"
        "author_model_configuration: unit-test\n"
        "author_metadata_source: unit-test\n\n"
        "# Typed Publication Fixture\n\n"
        "bridge_kind: prime_proposal\n"
        f"Document: {slug}\n"
        "Version: 001\n"
        "Project Authorization: PAUTH-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-0001\n"
        'target_paths: ["scripts/example.py"]\n'
    ).encode()
    target = bridge_dir / f"{slug}-001.md"
    kwargs: dict[str, object] = {
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }
    return slug, session_id, content, target, kwargs


def test_bridge_publication_capability_is_exact_single_use_and_current(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    receipt = consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=session_id,
        changed_by="test",
        change_reason="typed bridge publication",
        **kwargs,
    )
    assert receipt.capability_state == "consumed"
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
    )["current"]
    with pytest.raises(RegistryAuthorizationError, match="already consumed"):
        consume_bridge_publication_capability(
            capability=minted["capability"],
            target_path=target,
            content=content,
            session_id=session_id,
            changed_by="test",
            change_reason="replay",
            **kwargs,
        )


def test_three_sequential_bridge_publications_remain_current_without_manual_observation(
    tmp_path: Path,
) -> None:
    first_slug, session_id, first_content, first_target, kwargs = _bridge_publication_fixture(tmp_path)
    publications = [(first_slug, first_content, first_target)]
    for index in range(2, 4):
        slug = f"typed-publication-fixture-{index}"
        publications.append(
            (
                slug,
                first_content.replace(first_slug.encode(), slug.encode()),
                first_target.with_name(f"{slug}-001.md"),
            )
        )

    for index, (slug, content, target) in enumerate(publications):
        if index:
            assert acquire(slug, session_id, project_root=tmp_path)
        minted = mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target,
            content=content,
            session_id=session_id,
            compliance_digest=f"sha256:test-compliance-{index}",
            **kwargs,
        )
        target.write_bytes(content)
        consume_bridge_publication_capability(
            capability=minted["capability"],
            target_path=target,
            content=content,
            session_id=session_id,
            changed_by="test",
            change_reason=f"sequential publication {index + 1}",
            **kwargs,
        )
        snapshot = load_registry_snapshot(**kwargs)
        assert registry_currentness(
            snapshot,
            project_root=tmp_path,
            db_path=kwargs["db_path"],
            record_ids={"bridge-versioned-files"},
        )["current"]
        release_claim(slug, session_id, project_root=tmp_path)


def test_bridge_publication_compensation_restores_preimage_currentness(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=session_id,
        changed_by="test",
        change_reason="typed bridge publication",
        **kwargs,
    )
    receipt = compensate_bridge_publication(
        capability=minted["capability"],
        target_path=target,
        session_id=session_id,
        reason="downstream publication failure",
        changed_by="test",
        **kwargs,
    )
    assert receipt.capability_state == "compensated"
    assert not target.exists()
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
    )["current"]


def test_bridge_publication_rejects_missing_claim(tmp_path: Path) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    release_claim(slug, session_id, project_root=tmp_path)

    with pytest.raises(RegistryAuthorizationError, match="exact live work-intent claim"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target,
            content=content,
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )


def test_bridge_publication_rejects_session_status_path_and_compliance_mismatches(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)

    with pytest.raises(RegistryAuthorizationError, match="author session and claim session differ"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target,
            content=content,
            session_id="other-session",
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="exact requested terminal state"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="REVISED",
            target_path=target,
            content=content,
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="invalid candidate bridge lifecycle"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=2,
            status="NEW",
            target_path=target.with_name(f"{slug}-002.md"),
            content=content.replace(b"Version: 001", b"Version: 002"),
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="target mismatch"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target.with_name("wrong-001.md"),
            content=content,
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="bindings must be non-empty"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target,
            content=content,
            session_id=session_id,
            compliance_digest="",
            **kwargs,
        )


def test_bridge_publication_rejects_content_mismatch_and_fabricated_capability(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)

    with pytest.raises(RegistryAuthorizationError, match="content binding mismatch"):
        consume_bridge_publication_capability(
            capability=minted["capability"],
            target_path=target,
            content=content + b"\n",
            session_id=session_id,
            changed_by="test",
            change_reason="tampered content",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="unknown or fabricated"):
        consume_bridge_publication_capability(
            capability="fabricated-capability",
            target_path=target,
            content=content,
            session_id=session_id,
            changed_by="test",
            change_reason="fabricated capability",
            **kwargs,
        )
    compensate_bridge_publication(
        capability=minted["capability"],
        target_path=target,
        session_id=session_id,
        reason="negative binding test cleanup",
        changed_by="test",
        **kwargs,
    )


def test_bridge_publication_rejects_expired_capability(tmp_path: Path) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    with sqlite3.connect(str(kwargs["db_path"])) as conn:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities SET expires_at = ? WHERE capability_hash = ?",
            ("2000-01-01T00:00:00Z", minted["capability_hash"]),
        )

    with pytest.raises(RegistryAuthorizationError, match="capability expired"):
        consume_bridge_publication_capability(
            capability=minted["capability"],
            target_path=target,
            content=content,
            session_id=session_id,
            changed_by="test",
            change_reason="expired capability",
            **kwargs,
        )
    compensate_bridge_publication(
        capability=minted["capability"],
        target_path=target,
        session_id=session_id,
        reason="expiry test cleanup",
        changed_by="test",
        **kwargs,
    )


def test_bridge_publication_recovery_finalizes_crash_idempotently(tmp_path: Path) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)

    receipt = recover_bridge_publication(
        target_path=target,
        session_id=session_id,
        mode="finalize",
        changed_by="test",
        change_reason="finish crashed publication",
        **kwargs,
    )
    retry = recover_bridge_publication(
        target_path=target,
        session_id=session_id,
        mode="finalize",
        changed_by="test",
        change_reason="idempotent finish",
        **kwargs,
    )

    assert receipt.capability_hash == minted["capability_hash"]
    assert receipt.capability_state == "consumed"
    assert retry.revision_id == receipt.revision_id
    with sqlite3.connect(str(kwargs["db_path"])) as conn:
        revision_count = conn.execute(
            "SELECT COUNT(*) FROM sot_artifact_revisions WHERE capability_hash = ?",
            (minted["capability_hash"],),
        ).fetchone()[0]
    assert revision_count == 1


def test_bridge_publication_recovery_rolls_back_expired_crash(tmp_path: Path) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    with sqlite3.connect(str(kwargs["db_path"])) as conn:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities "
            "SET capability_state = 'expired' WHERE capability_hash = ?",
            (minted["capability_hash"],),
        )

    receipt = recover_bridge_publication(
        target_path=target,
        session_id=session_id,
        mode="rollback",
        changed_by="test",
        change_reason="roll back crashed publication",
        **kwargs,
    )

    assert receipt.capability_state == "compensated"
    assert not target.exists()
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
        record_ids={"bridge-versioned-files"},
    )["current"]


def test_bridge_publication_recovery_rejects_byte_mismatch(tmp_path: Path) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content + b"tampered")

    with pytest.raises(RegistryAuthorizationError, match="exact row"):
        recover_bridge_publication(
            target_path=target,
            session_id=session_id,
            mode="finalize",
            changed_by="test",
            change_reason="must fail closed",
            **kwargs,
        )


def test_compensation_failure_observes_retained_file_and_preserves_audit_state(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content + b"tampered")

    with pytest.raises(RegistryRecoveryRequired, match="target bytes changed"):
        compensate_bridge_publication(
            capability=minted["capability"],
            target_path=target,
            session_id=session_id,
            reason="compensation must retain unknown bytes",
            changed_by="test",
            **kwargs,
        )

    with sqlite3.connect(str(kwargs["db_path"])) as conn:
        conn.row_factory = sqlite3.Row
        capability_row = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (minted["capability_hash"],),
        ).fetchone()
        revision = conn.execute(
            "SELECT * FROM sot_artifact_revisions WHERE entry_id = 'bridge-versioned-files' ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
    assert target.exists()
    assert capability_row["capability_state"] == "recovery_required"
    assert revision["operation"] == "direct_in_place_content_change"
    assert revision["evidence_source_reference"] == minted["capability_hash"]
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
        record_ids={"bridge-versioned-files"},
    )["current"]


def test_compensation_failure_observes_exactly_restored_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=session_id,
        changed_by="test",
        change_reason="typed bridge publication",
        **kwargs,
    )
    real_append = registry_control_plane._append_revision
    calls = 0

    def fail_once(*args: object, **call_kwargs: object) -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("injected compensation revision failure")
        return real_append(*args, **call_kwargs)

    monkeypatch.setattr(registry_control_plane, "_append_revision", fail_once)
    with pytest.raises(RuntimeError, match="injected compensation"):
        compensate_bridge_publication(
            capability=minted["capability"],
            target_path=target,
            session_id=session_id,
            reason="exercise exact restoration",
            changed_by="test",
            **kwargs,
        )

    assert target.read_bytes() == content
    with sqlite3.connect(str(kwargs["db_path"])) as conn:
        conn.row_factory = sqlite3.Row
        capability_row = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (minted["capability_hash"],),
        ).fetchone()
        revision = conn.execute(
            "SELECT * FROM sot_artifact_revisions WHERE entry_id = 'bridge-versioned-files' ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
    assert capability_row["capability_state"] == "recovery_required"
    assert revision["operation"] == "direct_in_place_content_change"
    assert revision["evidence_source_reference"] == minted["capability_hash"]
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
        record_ids={"bridge-versioned-files"},
    )["current"]


def test_retired_wi5441_recovery_entry_point_fails_closed() -> None:
    with pytest.raises(RegistryAuthorizationError, match="is retired"):
        recover_wi5441_bridge_aggregate(
            actor_session="session",
            bridge_id="bridge",
            start_packet_hash="packet",
            pauth_id="pauth",
            changed_by="test",
            change_reason="must not run",
        )
