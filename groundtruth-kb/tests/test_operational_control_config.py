from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from groundtruth_kb.project.operational_control_config import (
    MAX_CATALOG_BYTES,
    OperationalControlConfigError,
    OperationalControlEnvironmentBinding,
    create_test_control_environment_snapshot,
    load_operational_control_catalog,
    load_platform_control_environment_snapshot,
    load_test_operational_control_catalog,
    resolve_operational_control,
    resolve_operational_controls,
)


def _binding(
    name: str = "GTKB_CONTROL_SAMPLE_TIMEOUT",
    *,
    ref: str = "TEST:CONTROL:SAMPLE_TIMEOUT@1",
    **changes: object,
) -> OperationalControlEnvironmentBinding:
    values = {
        "schema_ref": ref,
        "environment_name": name,
        "version": 1,
        "source_kind": "test_fixture",
    }
    values.update(changes)
    return OperationalControlEnvironmentBinding(**values)  # type: ignore[arg-type]


def _control(
    *,
    control_id: str = "sample_timeout",
    schema_ref: str = "TEST:CONTROL:SAMPLE_TIMEOUT@1",
    kind: str = "integer",
    unit: str = "seconds",
    default: str = "30",
    minimum: str = "1",
    maximum: str = "120",
    category: str = "timeout",
    scope: str = "platform",
    zero_semantics: str = "forbidden",
    migration_state: str = "active",
    capacity_observation_key: str | None = None,
) -> str:
    capacity = "" if capacity_observation_key is None else f'capacity_observation_key = "{capacity_observation_key}"\n'
    return f"""
[[controls]]
id = "{control_id}"
environment_schema_ref = "{schema_ref}"
numeric_kind = "{kind}"
unit = "{unit}"
relaxed_default = "{default}"
minimum = "{minimum}"
maximum = "{maximum}"
category = "{category}"
scope = "{scope}"
zero_semantics = "{zero_semantics}"
rationale = "Relaxed fixture policy."
tolerance_rationale = "Bounded fixture tolerance."
migration_state = "{migration_state}"
{capacity}"""


def _catalog_text(*controls: str, invariants: str = "") -> str:
    return 'schema_version = 1\nlive_value_authority = "root_env_local"\n' + "".join(controls) + invariants


def _load(tmp_path: Path, text: str, bindings: list[OperationalControlEnvironmentBinding]):
    path = tmp_path / "catalog.toml"
    path.write_text(text, encoding="utf-8")
    return load_test_operational_control_catalog(path, bindings)


def test_production_catalog_is_empty_root_bound_and_stable() -> None:
    project_root = Path(__file__).resolve().parents[2]
    catalog = load_operational_control_catalog(project_root)
    path = project_root / "config" / "governance" / "operational-controls.toml"

    assert catalog.schema_version == 1
    assert catalog.live_value_authority == "root_env_local"
    assert catalog.source_kind == "production_catalog"
    assert catalog.source_reference == "config/governance/operational-controls.toml"
    assert not catalog.definitions
    assert not catalog.invariants
    assert catalog.catalog_sha256 == "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(TypeError):
        catalog.definitions["forbidden"] = object()  # type: ignore[index,assignment]


@pytest.mark.parametrize(
    ("kind", "unit", "default", "override", "expected"),
    [
        ("integer", "seconds", "30", "45", 45),
        ("integer", "milliseconds", "100", "250", 250),
        ("integer", "count", "2", "4", 4),
        ("decimal", "ratio", "0.5", "0.75", Decimal("0.75")),
        ("decimal", "percent", "25.0", "50.5", Decimal("50.5")),
    ],
)
def test_all_numeric_kinds_and_units_resolve_with_typed_provenance(
    tmp_path: Path,
    kind: str,
    unit: str,
    default: str,
    override: str,
    expected: int | Decimal,
) -> None:
    catalog = _load(
        tmp_path,
        _catalog_text(
            _control(kind=kind, unit=unit, default=default, minimum="0", maximum="1000", zero_semantics="literal")
        ),
        [_binding()],
    )
    snapshot = create_test_control_environment_snapshot(
        catalog,
        {"GTKB_CONTROL_SAMPLE_TIMEOUT": override, "UNRELATED_SECRET": "never-retained"},
    )
    result = resolve_operational_control(catalog, snapshot, "sample_timeout")

    assert result.value == expected
    assert result.effective_value == expected
    assert result.unit == unit
    assert result.source == "test_fixture"
    assert result.catalog_sha256 == catalog.catalog_sha256
    assert result.environment_snapshot_digest == snapshot.snapshot_digest
    assert "UNRELATED_SECRET" not in snapshot.values
    assert "never-retained" not in repr(snapshot)


def test_absent_key_uses_relaxed_default_and_process_environment_is_ignored(tmp_path: Path, monkeypatch) -> None:
    catalog = _load(tmp_path, _catalog_text(_control()), [_binding()])
    monkeypatch.setenv("GTKB_CONTROL_SAMPLE_TIMEOUT", "99")
    snapshot = create_test_control_environment_snapshot(catalog, {})
    result = resolve_operational_control(catalog, snapshot, "sample_timeout")

    assert result.value == 30
    assert result.source == "catalog_relaxed_default"


@pytest.mark.parametrize("raw", ["", "   ", "abc", "121", "1.25"])
def test_present_invalid_override_never_falls_back(tmp_path: Path, raw: str) -> None:
    catalog = _load(tmp_path, _catalog_text(_control()), [_binding()])
    snapshot = create_test_control_environment_snapshot(catalog, {"GTKB_CONTROL_SAMPLE_TIMEOUT": raw})

    with pytest.raises(OperationalControlConfigError) as exc_info:
        resolve_operational_control(catalog, snapshot, "sample_timeout")
    assert exc_info.value.code in {"invalid_numeric", "invalid_override", "out_of_bounds"}


def test_binding_must_be_present_verified_platform_non_secret_and_reserved(tmp_path: Path) -> None:
    text = _catalog_text(_control())
    bad_bindings = [
        [],
        [_binding(status="stale")],
        [_binding(scope="application")],
        [_binding(classification="credential")],
        [_binding(name="SAMPLE_TIMEOUT")],
        [_binding(name="GTKB_CONTROL_API_TOKEN")],
    ]
    for index, bindings in enumerate(bad_bindings):
        path = tmp_path / f"bad-{index}.toml"
        path.write_text(text, encoding="utf-8")
        with pytest.raises(OperationalControlConfigError):
            load_test_operational_control_catalog(path, bindings)


def test_test_binding_cannot_be_used_by_production_loader(tmp_path: Path) -> None:
    (tmp_path / "config" / "governance").mkdir(parents=True)
    (tmp_path / "config" / "governance" / "operational-controls.toml").write_text(
        _catalog_text(_control()), encoding="utf-8"
    )
    with pytest.raises(OperationalControlConfigError, match="test_binding_in_production"):
        load_operational_control_catalog(tmp_path, [_binding()])


def _pair_catalog(tmp_path: Path, operator: str, margin: str = "0"):
    bindings = [
        _binding("GTKB_CONTROL_LEFT", ref="TEST:CONTROL:LEFT@1"),
        _binding("GTKB_CONTROL_RIGHT", ref="TEST:CONTROL:RIGHT@1"),
    ]
    invariants = f"""
[[invariants]]
id = "pair_relation"
left = "left"
operator = "{operator}"
right = "right"
margin = "{margin}"
"""
    catalog = _load(
        tmp_path,
        _catalog_text(
            _control(control_id="left", schema_ref="TEST:CONTROL:LEFT@1", default="2", minimum="1"),
            _control(control_id="right", schema_ref="TEST:CONTROL:RIGHT@1", default="5", minimum="1"),
            invariants=invariants,
        ),
        bindings,
    )
    return catalog


@pytest.mark.parametrize(
    ("operator", "left", "right", "margin"),
    [
        ("lt", "2", "5", "2"),
        ("lte", "3", "5", "2"),
        ("eq", "5", "5", "0"),
        ("gte", "5", "3", "2"),
        ("gt", "6", "3", "2"),
    ],
)
def test_every_invariant_operator_passes_at_its_defined_boundary(
    tmp_path: Path, operator: str, left: str, right: str, margin: str
) -> None:
    catalog = _pair_catalog(tmp_path, operator, margin)
    snapshot = create_test_control_environment_snapshot(
        catalog,
        {"GTKB_CONTROL_LEFT": left, "GTKB_CONTROL_RIGHT": right},
    )
    assert set(resolve_operational_controls(catalog, snapshot)) == {"left", "right"}


def test_invariant_violation_and_split_request_fail_closed(tmp_path: Path) -> None:
    catalog = _pair_catalog(tmp_path, "lt", "2")
    snapshot = create_test_control_environment_snapshot(
        catalog,
        {"GTKB_CONTROL_LEFT": "3", "GTKB_CONTROL_RIGHT": "5"},
    )
    with pytest.raises(OperationalControlConfigError, match="invariant_violation"):
        resolve_operational_controls(catalog, snapshot)
    with pytest.raises(OperationalControlConfigError, match="split_invariant_request"):
        resolve_operational_control(catalog, snapshot, "left")


def test_invalid_and_contradictory_invariants_are_rejected(tmp_path: Path) -> None:
    base = _catalog_text(
        _control(control_id="left", schema_ref="TEST:CONTROL:LEFT@1", default="2", minimum="1"),
        _control(control_id="right", schema_ref="TEST:CONTROL:RIGHT@1", default="5", minimum="1"),
    )
    bindings = [
        _binding("GTKB_CONTROL_LEFT", ref="TEST:CONTROL:LEFT@1"),
        _binding("GTKB_CONTROL_RIGHT", ref="TEST:CONTROL:RIGHT@1"),
    ]
    bad_fragments = [
        '[[invariants]]\nid="bad"\nleft="missing"\noperator="lt"\nright="right"\n',
        '[[invariants]]\nid="bad"\nleft="left"\noperator="eq"\nright="right"\nmargin="1"\n',
        (
            '[[invariants]]\nid="one"\nleft="left"\noperator="lt"\nright="right"\n'
            '[[invariants]]\nid="two"\nleft="right"\noperator="gt"\nright="left"\n'
        ),
    ]
    for index, fragment in enumerate(bad_fragments):
        path = tmp_path / f"invariant-{index}.toml"
        path.write_text(base + fragment, encoding="utf-8")
        with pytest.raises(OperationalControlConfigError):
            load_test_operational_control_catalog(path, bindings)


def test_catalog_snapshot_mismatch_is_rejected(tmp_path: Path) -> None:
    catalog = _load(tmp_path, _catalog_text(_control()), [_binding()])
    snapshot = create_test_control_environment_snapshot(catalog, {})
    with pytest.raises(OperationalControlConfigError, match="split_snapshot"):
        resolve_operational_controls(catalog, replace(snapshot, catalog_sha256="sha256:other"))


def test_capacity_requires_observation_and_zero_disables(tmp_path: Path) -> None:
    catalog = _load(
        tmp_path,
        _catalog_text(
            _control(
                control_id="worker_cap",
                schema_ref="TEST:CONTROL:WORKER_CAP@1",
                unit="count",
                default="0",
                minimum="0",
                category="live_worker_concurrency",
                scope="per_harness",
                zero_semantics="disable",
                capacity_observation_key="available_workers",
            )
        ),
        [_binding("GTKB_CONTROL_WORKER_CAP", ref="TEST:CONTROL:WORKER_CAP@1")],
    )
    snapshot = create_test_control_environment_snapshot(catalog, {})
    with pytest.raises(OperationalControlConfigError, match="unknown_capacity"):
        resolve_operational_control(catalog, snapshot, "worker_cap")
    result = resolve_operational_control(
        catalog,
        snapshot,
        "worker_cap",
        capacity_observations={"available_workers": 8},
    )
    assert result.effective_value == 0
    assert result.is_disabled is True


def test_unknown_or_inactive_control_fails_closed(tmp_path: Path) -> None:
    catalog = _load(
        tmp_path,
        _catalog_text(_control(migration_state="candidate")),
        [_binding()],
    )
    snapshot = create_test_control_environment_snapshot(catalog, {})
    with pytest.raises(OperationalControlConfigError, match="unknown_control"):
        resolve_operational_control(catalog, snapshot, "sample_timeout")


def test_catalog_resource_and_shape_bounds(tmp_path: Path) -> None:
    oversized = tmp_path / "oversized.toml"
    oversized.write_bytes(b"#" * (MAX_CATALOG_BYTES + 1))
    with pytest.raises(OperationalControlConfigError, match="resource_bound"):
        load_test_operational_control_catalog(oversized, [])

    malformed = tmp_path / "malformed.toml"
    malformed.write_text("not = [valid", encoding="utf-8")
    with pytest.raises(OperationalControlConfigError, match="malformed_catalog"):
        load_test_operational_control_catalog(malformed, [])

    recursive = tmp_path / "recursive.toml"
    recursive.write_text(_catalog_text(_control()) + "\n[unexpected]\nvalue = 1\n", encoding="utf-8")
    with pytest.raises(OperationalControlConfigError, match="unknown_catalog_field"):
        load_test_operational_control_catalog(recursive, [_binding()])


def test_production_environment_snapshot_is_bounded_and_declared_only(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "config" / "governance"
    catalog_dir.mkdir(parents=True)
    catalog_path = catalog_dir / "operational-controls.toml"
    catalog_path.write_text(_catalog_text(), encoding="utf-8")
    (tmp_path / ".env.local").write_text("UNRELATED_TOKEN=not-hashed\n", encoding="utf-8")

    catalog = load_operational_control_catalog(tmp_path)
    snapshot = load_platform_control_environment_snapshot(tmp_path, catalog)

    assert snapshot.source_kind == "platform_env_local"
    assert snapshot.source_reference == ".env.local"
    assert not snapshot.values
    assert "not-hashed" not in repr(snapshot)


def test_catalog_and_environment_paths_reject_missing_nonfiles_and_symlinks(tmp_path: Path) -> None:
    with pytest.raises(OperationalControlConfigError, match="missing_file"):
        load_operational_control_catalog(tmp_path)

    catalog_dir = tmp_path / "config" / "governance"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "operational-controls.toml").mkdir()
    with pytest.raises(OperationalControlConfigError, match="unsafe_path"):
        load_operational_control_catalog(tmp_path)


def test_definition_values_reject_float_nan_precision_and_inconsistent_bounds(tmp_path: Path) -> None:
    base_binding = [_binding()]
    bad_rows = [
        _control(default="NaN"),
        _control(kind="decimal", default="0.1234567891", minimum="0", maximum="1"),
        _control(default="200", minimum="1", maximum="120"),
    ]
    for index, row in enumerate(bad_rows):
        path = tmp_path / f"numeric-{index}.toml"
        path.write_text(_catalog_text(row), encoding="utf-8")
        with pytest.raises(OperationalControlConfigError):
            load_test_operational_control_catalog(path, base_binding)


def test_snapshot_and_resolved_maps_are_immutable(tmp_path: Path) -> None:
    catalog = _load(tmp_path, _catalog_text(_control()), [_binding()])
    snapshot = create_test_control_environment_snapshot(catalog, {"GTKB_CONTROL_SAMPLE_TIMEOUT": "60"})
    result = resolve_operational_controls(catalog, snapshot)
    with pytest.raises(TypeError):
        snapshot.values["GTKB_CONTROL_SAMPLE_TIMEOUT"] = "1"  # type: ignore[index]
    with pytest.raises(TypeError):
        result["sample_timeout"] = result["sample_timeout"]  # type: ignore[index]
