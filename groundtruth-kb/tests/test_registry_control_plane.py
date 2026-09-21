# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Current declaration resolution, inventory boundaries and writer contention.

TOML mutation, atomic replacement/retry, fresh-process recovery and foreign-byte
preservation are covered by test_registry_current_mutation_cli.py. Exact bridge
claims and authored delivery are covered by test_native_bridge.py. Retired
SQLite projections, publication permissions and transaction receipts are not
fixtures or public APIs.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
import tomlkit

from groundtruth_kb.project import registry_control_plane
from groundtruth_kb.project.operational_control_config import (
    CATALOG_RELATIVE_PATH,
    load_operational_control_catalog,
    set_operational_controls,
)
from groundtruth_kb.project.registry_control_plane import (
    RegistryCoverageError,
    RegistryResolver,
    census_registry,
    load_registry_snapshot,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact


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
    opaque = _record("runtime", "unregistered-runtime/", "opaque_container")
    resolver = RegistryResolver([opaque])

    assert resolver.resolve("unregistered-runtime/transactions/one.json") is None
    assert resolver.resolve_operation_path("unregistered-runtime/transactions/one.json") == opaque
    assert resolver.resolve_operation_path("outside.json") is None


def _controls(root: Path, timeout: float | None = None):
    """Create explicit isolated control input using the checked-in source schema."""
    source = Path(__file__).resolve().parents[2] / CATALOG_RELATIVE_PATH
    target = root / CATALOG_RELATIVE_PATH
    document = tomlkit.parse(source.read_text(encoding="utf-8"))
    if timeout is not None:
        for row in document["controls"]:
            if row["id"] == "registry.lock.acquire_seconds":
                row["value"] = str(timeout)
            elif row["id"] == "registry.lock.max_backoff_seconds":
                row["value"] = "0.01"
            elif row["id"] == "registry.lock.initial_backoff_seconds":
                row["value"] = "0.001"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(tomlkit.dumps(document), encoding="utf-8")
    return registry_control_plane._registry_controls(root)


def test_registry_lock_uses_canonical_values_and_ignores_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controls = _controls(tmp_path, 45.5)
    for injected in ("3.0", "not-a-number", "0", "-5"):
        monkeypatch.setenv("GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS", injected)
        lock = registry_control_plane._RegistryFileLock(tmp_path / "control-plane.lock", controls=controls)
        assert lock.timeout == 45.5
        assert lock.catalog_sha256 == load_operational_control_catalog(tmp_path).catalog_sha256
    (tmp_path / CATALOG_RELATIVE_PATH).unlink()
    with pytest.raises(registry_control_plane.RegistryControlPlaneError, match="unavailable_catalog"):
        registry_control_plane._registry_controls(tmp_path)


def test_census_uses_only_git_and_application_root_boundaries(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden").write_text("x", encoding="utf-8")
    (tmp_path / "applications" / "Demo").mkdir(parents=True)
    (tmp_path / "applications" / "Demo" / "hidden.py").write_text("x", encoding="utf-8")
    (tmp_path / "applications" / "registry.toml").write_text("x", encoding="utf-8")
    (tmp_path / "unregistered-runtime" / "runtime").mkdir(parents=True)
    (tmp_path / "unregistered-runtime" / "runtime" / "visible.log").write_text("x", encoding="utf-8")
    (tmp_path / "member.txt").write_text("x", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    registry.write_bytes(serialize_registry(records))
    snapshot = load_registry_snapshot(project_root=tmp_path)
    census = census_registry(snapshot, project_root=tmp_path)
    paths = {entry.relative_path: entry for entry in census}
    assert paths[".git"].object_kind == "vcs_service_state"
    assert ".git/hidden" not in paths
    assert paths["applications/Demo"].object_kind == "hosted_application_root"
    assert "applications/Demo/hidden.py" not in paths
    assert "applications/registry.toml" in paths
    assert "unregistered-runtime/runtime/visible.log" in paths


def test_registry_lock_backoff_and_jitter_stay_under_deadline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-5869: bounded exponential backoff + jitter advances monotonically and
    never exceeds the remaining acquisition deadline.
    """
    lock_path = tmp_path / "control-plane.lock"
    sleeps: list[float] = []

    monkeypatch.setattr(time, "sleep", lambda sec: sleeps.append(sec))

    # Hold the lock with a competing handle so acquisition retries.
    blocker = registry_control_plane._RegistryFileLock(lock_path, controls=_controls(tmp_path, 0.4))
    blocker.__enter__()
    try:
        with (
            pytest.raises(registry_control_plane.RegistryFileLockAcquisitionTimeout),
            registry_control_plane._RegistryFileLock(lock_path, controls=_controls(tmp_path, 0.4)),
        ):
            pass
    finally:
        blocker.__exit__(None, None, None)

    assert sleeps, "acquisition loop must retry with backoff sleeps"
    # All sleeps are positive and bounded by the max backoff.
    assert all(0 < sec <= blocker.max_backoff for sec in sleeps)
    # Backoff grows (roughly) over attempts (jitter allows some variance).
    assert sleeps[0] <= sleeps[-1] * 2.0 + 0.1


def test_registry_lock_typed_timeout_exception(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-5869: acquisition deadline exhaustion raises the typed caller-retryable
    ``RegistryFileLockAcquisitionTimeout`` (subclass of RegistryControlPlaneError).
    """
    lock_path = tmp_path / "control-plane.lock"
    blocker = registry_control_plane._RegistryFileLock(lock_path, controls=_controls(tmp_path, 0.2))
    blocker.__enter__()
    try:
        with (
            pytest.raises(registry_control_plane.RegistryFileLockAcquisitionTimeout) as excinfo,
            registry_control_plane._RegistryFileLock(lock_path, controls=_controls(tmp_path, 0.2)),
        ):
            pass
        assert isinstance(excinfo.value, registry_control_plane.RegistryControlPlaneError)
        assert "timed out acquiring registry lock" in str(excinfo.value)
    finally:
        blocker.__exit__(None, None, None)


def test_registry_lock_reload_keeps_current_operation_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".git").mkdir(exist_ok=True)
    controls = _controls(tmp_path, 22.5)
    lock_path = tmp_path / "control-plane.lock"
    active = registry_control_plane._RegistryFileLock(lock_path, controls=controls)
    with active:
        path = tmp_path / CATALOG_RELATIVE_PATH
        before = load_operational_control_catalog(tmp_path)
        proposed = tomlkit.parse(path.read_text(encoding="utf-8"))
        for row in proposed["controls"]:
            if row["id"] == "registry.lock.acquire_seconds":
                row["value"] = "33.5"
        result = set_operational_controls(
            tmp_path, tomlkit.dumps(proposed).encode(), expected_sha256=before.catalog_sha256
        )
        assert result["changed"]
        monkeypatch.setenv("GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS", "1")
        successor = registry_control_plane._RegistryFileLock(
            lock_path, controls=registry_control_plane._registry_controls(tmp_path)
        )
        assert active.timeout == 22.5
        assert successor.timeout == 33.5
        assert active.catalog_sha256 != successor.catalog_sha256
