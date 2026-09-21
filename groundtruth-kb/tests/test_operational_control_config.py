"""Behavioral contract for the single live operational-control artifact."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

import pytest
import tomlkit
from click.testing import CliRunner

import groundtruth_kb
from groundtruth_kb.cli import main
from groundtruth_kb.project import operational_control_config as controls


def _control(ident="sample_timeout", **changes):
    row = {
        "id": ident,
        "description": "Explicit isolated fixture control.",
        "numeric_kind": "integer",
        "unit": "seconds",
        "value": "30",
        "minimum": "1",
        "maximum": "120",
        "category": "timeout",
        "scope": "per_operation",
        "zero_semantics": "forbidden",
        "rationale": "Fixture policy.",
        "tolerance_rationale": "Explicit fixture bounds.",
        "migration_state": "active",
        "consumers": ["fixture.consumer"],
        "evidence_refs": ["fixture:observation"],
        "reload_behavior": "next_operation",
        "failure_disposition": "refuse_new_operation",
        "observability": ["catalog_sha256", "refusal_code"],
    }
    row.update(changes)
    return row


def _bytes(*rows, invariants=None):
    return tomlkit.dumps({"schema_version": 2, "controls": list(rows), "invariants": invariants or []}).encode("utf-8")


def _write(root, payload):
    path = root / controls.CATALOG_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir(exist_ok=True)
    path.write_bytes(payload)
    return path


def _load(root, payload):
    _write(root, payload)
    return controls.load_operational_control_catalog(root)


def _pair(left="2", right="5", operator="lt", margin="0"):
    return _bytes(
        _control("left", value=left),
        _control("right", value=right),
        invariants=[{"id": "pair", "left": "left", "operator": operator, "right": "right", "margin": margin}],
    )


def test_production_catalog_has_live_values_and_immutable_source_identity():
    root = Path(__file__).resolve().parents[2]
    path = root / controls.CATALOG_RELATIVE_PATH
    catalog = controls.load_operational_control_catalog(root)
    document = tomlkit.parse(path.read_text(encoding="utf-8"))
    assert catalog.schema_version == 2
    assert catalog.definitions
    assert catalog.catalog_sha256 == "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    assert {key: str(row.value) for key, row in catalog.definitions.items()} == {
        row["id"]: str(row["value"]) for row in document["controls"]
    }
    assert "live_value_authority" not in document
    assert all("relaxed_default" not in row and "environment_schema_ref" not in row for row in document["controls"])
    with pytest.raises(TypeError):
        catalog.definitions["other"] = object()


@pytest.mark.parametrize(
    ("kind", "unit", "value", "expected"),
    [
        ("integer", "seconds", "45", 45),
        ("integer", "milliseconds", "100", 100),
        ("integer", "count", "4", 4),
        ("decimal", "ratio", "0.75", Decimal("0.75")),
        ("decimal", "percent", "50.5", Decimal("50.5")),
    ],
)
def test_all_numeric_kinds_and_units_resolve_with_typed_provenance(tmp_path, kind, unit, value, expected):
    catalog = _load(
        tmp_path, _bytes(_control(numeric_kind=kind, unit=unit, value=value, minimum="0", zero_semantics="literal"))
    )
    resolved = controls.resolve_operational_controls(catalog)
    result = resolved["sample_timeout"]
    assert result.value == result.effective_value == expected
    assert type(result.value) is type(expected)
    assert result.unit == unit
    assert result.catalog_sha256 == catalog.catalog_sha256
    assert controls.control_value(resolved, "sample_timeout", unit=unit) == expected


@pytest.mark.parametrize("injected", ["45", "", "bad", "0", "-5"])
def test_only_canonical_live_values_are_read_and_environment_is_ignored(tmp_path, monkeypatch, injected):
    path = _write(tmp_path, _bytes(_control(value="33")))
    (tmp_path / ".env.local").write_text("GTKB_CONTROL_SAMPLE_TIMEOUT=91\n", encoding="utf-8")
    monkeypatch.setenv("GTKB_CONTROL_SAMPLE_TIMEOUT", injected)
    original_open = Path.open
    opened = []

    def guarded_open(self, *args, **kwargs):
        opened.append(self)
        assert self == path, "An unrelated environment or configuration file was opened"
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    catalog = controls.load_operational_control_catalog(tmp_path)
    assert (
        controls.control_value(controls.resolve_operational_controls(catalog), "sample_timeout", unit="seconds") == 33
    )
    assert opened == [path]


@pytest.mark.parametrize(
    "value",
    ["", "   ", "abc", "121", "1.25", True, 1.0, "NaN", "Infinity", "0.0000000001", "1e999", "1e999999999", "1" * 129],
)
def test_invalid_live_value_refuses_without_default(tmp_path, value):
    payload = _bytes(_control(value=value))
    path = _write(tmp_path, payload)
    with pytest.raises(controls.OperationalControlConfigError):
        controls.load_operational_control_catalog(tmp_path)
    assert path.read_bytes() == payload


@pytest.mark.parametrize(
    "field",
    [
        "value",
        "unit",
        "consumers",
        "evidence_refs",
        "rationale",
        "tolerance_rationale",
        "observability",
        "reload_behavior",
        "failure_disposition",
    ],
)
def test_definition_requires_explicit_value_and_operational_metadata(field):
    row = _control()
    del row[field]
    with pytest.raises(controls.OperationalControlConfigError, match="invalid_control_shape"):
        controls.validate_operational_control_bytes(_bytes(row))


@pytest.mark.parametrize(
    "change",
    [
        {"environment_schema_ref": "OLD:BINDING"},
        {"relaxed_default": "30"},
        {"unit": "minutes"},
        {"consumers": []},
        {"consumers": ["same", "same"]},
        {"scope": "unknown"},
        {"reload_behavior": "restart"},
        {"failure_disposition": "use_cache"},
        {"maximum": "20"},
        {"minimum": "0"},
        {"capacity_observation_key": "workers"},
    ],
)
def test_obsolete_or_contradictory_definition_fields_refuse(change):
    with pytest.raises(controls.OperationalControlConfigError):
        controls.validate_operational_control_bytes(_bytes(_control(**change)))


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
def test_every_invariant_operator_passes_at_its_defined_boundary(tmp_path, operator, left, right, margin):
    catalog = _load(tmp_path, _pair(left, right, operator, margin))
    assert set(controls.resolve_operational_controls(catalog)) == {"left", "right"}


def test_invariant_violation_and_split_request_fail_closed(tmp_path):
    with pytest.raises(controls.OperationalControlConfigError, match="invariant_violation"):
        controls.validate_operational_control_bytes(_pair("3", "5", "lt", "2"))
    catalog = _load(tmp_path, _pair())
    with pytest.raises(controls.OperationalControlConfigError, match="split_invariant_request"):
        controls.resolve_operational_controls(catalog, ["left"])
    with pytest.raises(controls.OperationalControlConfigError, match="duplicate_control_request"):
        controls.resolve_operational_controls(catalog, ["left", "left"])


@pytest.mark.parametrize(
    "case", ["missing", "self", "margin", "duplicate-id", "duplicate-pair", "unit", "kind", "inactive"]
)
def test_invalid_and_contradictory_invariants_are_rejected(case):
    doc = tomlkit.parse(_pair().decode())
    invariant = doc["invariants"][0]
    if case == "missing":
        invariant["left"] = "missing"
    elif case == "self":
        invariant["right"] = "left"
    elif case == "margin":
        invariant["operator"] = "eq"
        invariant["margin"] = "1"
    elif case in ("duplicate-id", "duplicate-pair"):
        other = dict(invariant)
        other["id"] = "pair" if case == "duplicate-id" else "another_pair"
        doc["invariants"].append(other)
    elif case == "unit":
        doc["controls"][1]["unit"] = "count"
    elif case == "kind":
        doc["controls"][1]["numeric_kind"] = "decimal"
    else:
        doc["controls"][1]["migration_state"] = "retired"
    with pytest.raises(controls.OperationalControlConfigError):
        controls.validate_operational_control_bytes(tomlkit.dumps(doc).encode())


@pytest.mark.parametrize(
    ("value", "observed", "effective", "disabled"),
    [(0, 8, 0, True), (8, 0, 0, True), (8, 3, 3, False), (3, 8, 3, False)],
)
def test_capacity_requires_observation_and_zero_disables(tmp_path, value, observed, effective, disabled):
    catalog = _load(
        tmp_path,
        _bytes(
            _control(
                "worker_cap",
                unit="count",
                value=str(value),
                minimum="0",
                category="live_worker_concurrency",
                scope="per_harness",
                zero_semantics="disable",
                capacity_observation_key="available_workers",
            )
        ),
    )
    for observations in (
        None,
        {"available_workers": None},
        {"available_workers": True},
        {"available_workers": -1},
        {"wrong": 8},
    ):
        with pytest.raises(controls.OperationalControlConfigError):
            controls.resolve_operational_controls(catalog, capacity_observations=observations)
    result = controls.resolve_operational_controls(catalog, capacity_observations={"available_workers": observed})[
        "worker_cap"
    ]
    assert result.effective_value == effective
    assert result.is_disabled is disabled


def test_observed_capacity_revalidates_coupled_invariant(tmp_path):
    rows = [
        _control(
            key,
            unit="count",
            value=value,
            minimum="0",
            category="capacity",
            zero_semantics="disable",
            capacity_observation_key=key + "_observed",
        )
        for key, value in [("left", "2"), ("right", "5")]
    ]
    catalog = _load(
        tmp_path,
        _bytes(*rows, invariants=[{"id": "pair", "left": "left", "operator": "lt", "right": "right", "margin": "0"}]),
    )
    with pytest.raises(controls.OperationalControlConfigError, match="invariant_violation"):
        controls.resolve_operational_controls(catalog, capacity_observations={"left_observed": 2, "right_observed": 1})


@pytest.mark.parametrize("state", ["candidate", "retired", "superseded"])
def test_unknown_or_inactive_control_fails_closed(tmp_path, state):
    catalog = _load(tmp_path, _bytes(_control(migration_state=state)))
    for key in ("sample_timeout", "unknown"):
        with pytest.raises(controls.OperationalControlConfigError, match="unknown_control"):
            controls.resolve_operational_controls(catalog, [key])


def test_unit_mismatch_and_immutable_maps(tmp_path):
    catalog = _load(tmp_path, _bytes(_control()))
    values = controls.resolve_operational_controls(catalog)
    with pytest.raises(controls.OperationalControlConfigError, match="unit_mismatch"):
        controls.control_value(values, "sample_timeout", unit="milliseconds")
    with pytest.raises(controls.OperationalControlConfigError, match="unknown_control"):
        controls.control_value(values, "unknown", unit="seconds")
    with pytest.raises(TypeError):
        values["sample_timeout"] = object()


@pytest.mark.parametrize(
    "case",
    [
        "bytes",
        "invalid-utf8",
        "invalid-toml",
        "old-schema",
        "unknown-root",
        "control-shape",
        "duplicate-key",
        "count",
        "prose",
    ],
)
def test_catalog_resource_and_shape_bounds(case):
    if case == "bytes":
        payload = b" " * (controls.MAX_CATALOG_BYTES + 1)
    elif case == "invalid-utf8":
        payload = b"\xff"
    elif case == "invalid-toml":
        payload = b"not valid TOML"
    elif case == "old-schema":
        payload = b'schema_version=1\nlive_value_authority="root_env_local"\ncontrols=[]\ninvariants=[]\n'
    elif case == "unknown-root":
        payload = _bytes(_control()) + b"\n[unexpected]\nvalue=1\n"
    elif case == "control-shape":
        payload = b'schema_version=2\ncontrols=["bad"]\ninvariants=[]\n'
    elif case == "duplicate-key":
        payload = _bytes(_control(), _control())
    elif case == "count":
        payload = tomlkit.dumps(
            {"schema_version": 2, "controls": [{}] * (controls.MAX_CONTROL_COUNT + 1), "invariants": []}
        ).encode()
    else:
        payload = _bytes(_control(description="x" * (controls.MAX_PROSE_LENGTH + 1)))
    with pytest.raises(controls.OperationalControlConfigError):
        controls.validate_operational_control_bytes(payload)


def test_catalog_paths_reject_missing_nonfiles_and_unreadable(tmp_path, monkeypatch):
    with pytest.raises(controls.OperationalControlConfigError, match="unavailable_catalog"):
        controls.load_operational_control_catalog(tmp_path)
    path = tmp_path / controls.CATALOG_RELATIVE_PATH
    path.mkdir(parents=True)
    with pytest.raises(controls.OperationalControlConfigError, match="unsafe_path"):
        controls.load_operational_control_catalog(tmp_path)
    path.rmdir()
    _write(tmp_path, _bytes(_control()))
    real_open = Path.open

    def deny(self, *args, **kwargs):
        if self == path:
            raise PermissionError("controlled read denial")
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", deny)
    with pytest.raises(controls.OperationalControlConfigError, match="unavailable_catalog"):
        controls.load_operational_control_catalog(tmp_path)


def test_parent_reparse_point_is_refused(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    _write(outside, _bytes(_control()))
    if os.name == "nt":

        def quote(path):
            return "'" + str(path).replace("'", "''") + "'"

        command = (
            f"New-Item -ItemType Junction -Path {quote(root / 'config')} -Target {quote(outside / 'config')} | Out-Null"
        )
        run = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert run.returncode == 0, run.stdout + run.stderr
    else:
        (root / "config").symlink_to(outside / "config", target_is_directory=True)
    with pytest.raises(controls.OperationalControlConfigError, match="unsafe_path"):
        controls.load_operational_control_catalog(root)


def test_atomic_set_changes_next_snapshot_without_changing_active_snapshot(tmp_path):
    before = _load(tmp_path, _pair())
    active = controls.resolve_operational_controls(before)
    proposed = _pair("4", "7")
    diff = controls.diff_operational_controls(tmp_path, proposed)
    assert set(diff["controls"]) == {"left", "right"}
    assert diff["controls"]["left"]["before"]["value"] == 2
    assert diff["controls"]["left"]["after"]["value"] == 4
    result = controls.set_operational_controls(tmp_path, proposed, expected_sha256=before.catalog_sha256)
    assert result["changed"] and result["reload_behavior"] == "next_operation"
    after = controls.load_operational_control_catalog(tmp_path)
    assert active["left"].value == 2
    assert controls.resolve_operational_controls(after)["left"].value == 4
    assert before.catalog_sha256 != after.catalog_sha256 == result["catalog_sha256"]
    again = controls.set_operational_controls(tmp_path, proposed, expected_sha256=after.catalog_sha256)
    assert not again["changed"]


def test_invalid_and_stale_set_preserve_canonical_bytes(tmp_path):
    path = _write(tmp_path, _pair())
    before = path.read_bytes()
    snapshot = controls.load_operational_control_catalog(tmp_path)
    for payload, expected in [(_pair("9", "3"), snapshot.catalog_sha256), (_pair("4", "7"), "sha256:stale")]:
        with pytest.raises(controls.OperationalControlConfigError):
            controls.set_operational_controls(tmp_path, payload, expected_sha256=expected)
        assert path.read_bytes() == before
        assert not list(path.parent.glob(".control-update-*"))


def test_competing_writer_refuses_then_releases(tmp_path):
    _write(tmp_path, _pair())
    snapshot = controls.load_operational_control_catalog(tmp_path)
    with controls._writer_lock(controls._writer_lock_path(tmp_path)), ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            controls.set_operational_controls, tmp_path, _pair("4", "7"), expected_sha256=snapshot.catalog_sha256
        )
        with pytest.raises(controls.OperationalControlConfigError, match="writer_busy"):
            future.result(timeout=10)
    result = controls.set_operational_controls(tmp_path, _pair("4", "7"), expected_sha256=snapshot.catalog_sha256)
    assert result["changed"]


def test_replacement_failure_preserves_old_file_and_removes_temporary(tmp_path, monkeypatch):
    path = _write(tmp_path, _pair())
    before = path.read_bytes()
    snapshot = controls.load_operational_control_catalog(tmp_path)

    def fail(*args):
        raise PermissionError("controlled replacement denial")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(controls.OperationalControlConfigError, match="replace_failed"):
        controls.set_operational_controls(tmp_path, _pair("4", "7"), expected_sha256=snapshot.catalog_sha256)
    assert path.read_bytes() == before
    assert not list(path.parent.glob(".control-update-*"))


def test_invalid_current_file_never_uses_cached_good_snapshot(tmp_path):
    path = _write(tmp_path, _pair())
    snapshot = controls.load_operational_control_catalog(tmp_path)
    path.write_bytes(b"invalid TOML")
    with pytest.raises(controls.OperationalControlConfigError, match="malformed_catalog"):
        controls.load_operational_control_catalog(tmp_path)
    assert controls.resolve_operational_controls(snapshot)["left"].value == 2


def test_cli_show_validate_diff_set_selects_configured_root_and_preserves_unrelated_files(tmp_path, monkeypatch):
    selected = tmp_path / "selected"
    caller = tmp_path / "caller"
    selected.mkdir()
    caller.mkdir()
    path = _write(selected, _pair())
    config = selected / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    (caller / "groundtruth.toml").write_text('[groundtruth]\napp_title="Wrong caller"\n', encoding="utf-8")
    sentinel = selected / "groundtruth.db"
    sentinel.write_bytes(b"untouched database sentinel")
    proposal = caller / "proposed.toml"
    proposal.write_bytes(_pair("4", "7"))
    monkeypatch.chdir(caller)
    runner = CliRunner()

    def invoke(*args):
        result = runner.invoke(main, ["--config", str(config), "controls", *args])
        assert result.exit_code == 0, (result.output, result.exception)
        return json.loads(result.output)

    shown = invoke("show")
    assert shown["source_reference"] == str(path)
    assert invoke("validate")["catalog_sha256"] == shown["catalog_sha256"]
    assert invoke("validate", "--input", str(proposal))["valid"]
    assert set(invoke("diff", "--input", str(proposal))["controls"]) == {"left", "right"}
    assert path.read_bytes() == _pair()
    changed = invoke("set", "--input", str(proposal), "--expected-sha256", shown["catalog_sha256"])
    assert changed["changed"]
    assert invoke("show")["controls"]["left"]["value"] == 4
    assert sentinel.read_bytes() == b"untouched database sentinel"
    assert not (caller / controls.CATALOG_RELATIVE_PATH).exists()


@pytest.mark.parametrize("command", ["show", "validate", "diff", "set"])
def test_cli_controls_are_cold_local_operations(tmp_path, command):
    path = _write(tmp_path, _pair())
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    proposal = tmp_path / "proposal.toml"
    proposal.write_bytes(_pair("4", "7"))
    snapshot = controls.load_operational_control_catalog(tmp_path)
    args = ["--config", str(config), "controls", command]
    if command in ("diff", "set"):
        args += ["--input", str(proposal)]
    if command == "set":
        args += ["--expected-sha256", snapshot.catalog_sha256]
    script = r"""
import json, socket, sqlite3, sys
import psycopg
def deny(*args, **kwargs):
    raise AssertionError("Control operation attempted database or network access")
socket.socket.connect=deny
sqlite3.connect=deny
sqlite3.dbapi2.connect=deny
psycopg.connect=deny
from click.testing import CliRunner
import groundtruth_kb
from groundtruth_kb.cli import main
result=CliRunner().invoke(main,json.loads(sys.argv[1]))
assert result.exit_code==0,(result.output,result.exception)
print(json.dumps({"output":json.loads(result.output),"origin":groundtruth_kb.__file__}))
"""
    package = Path(groundtruth_kb.__file__).resolve().parent.parent
    env = {key: value for key, value in os.environ.items() if not key.startswith(("GT_", "PG")) and key != "PYTHONPATH"}
    env.update(PYTHONPATH=str(package), PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, "-P", "-c", script, json.dumps(args)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert Path(json.loads(result.stdout)["origin"]).resolve().is_relative_to(package)
    assert path.read_bytes() == (_pair("4", "7") if command == "set" else _pair())


@pytest.mark.parametrize("defect", ["missing-key", "unit", "kind", "binding", "relation", "inactive"])
def test_setter_refuses_incompatible_registry_consumer_contract(tmp_path, defect):
    source = Path(__file__).resolve().parents[2] / controls.CATALOG_RELATIVE_PATH
    before = source.read_bytes()
    target = _write(tmp_path, before)
    original = controls.load_operational_control_catalog(tmp_path)
    proposal = tomlkit.parse(before.decode("utf-8"))
    if defect == "missing-key":
        proposal["controls"] = [r for r in proposal["controls"] if r["id"] != "registry.git_probe_seconds"]
    elif defect == "relation":
        proposal["invariants"].pop(-1)
    else:
        row = next(r for r in proposal["controls"] if r["id"] == "registry.git_probe_seconds")
        field, value = {
            "unit": ("unit", "count"),
            "kind": ("numeric_kind", "integer"),
            "binding": ("consumers", ["unrelated.consumer"]),
            "inactive": ("migration_state", "retired"),
        }[defect]
        row[field] = value
        if defect == "kind":
            row["minimum"] = "1"  # Keep generic integer validation valid; exercise the consumer contract.
    with pytest.raises(controls.OperationalControlConfigError, match="consumer_contract"):
        controls.set_operational_controls(
            tmp_path, tomlkit.dumps(proposal).encode(), expected_sha256=original.catalog_sha256
        )
    assert target.read_bytes() == before


def test_writer_mutex_refuses_nonregular_file_before_open(tmp_path, monkeypatch):
    import stat
    from types import SimpleNamespace

    path = _write(tmp_path, _pair())
    original = controls.load_operational_control_catalog(tmp_path)
    mutex = tmp_path / ".git" / controls.WRITER_LOCK_NAME
    mutex.touch()
    real_lstat = Path.lstat
    real_open = Path.open

    def observed_lstat(self, *args, **kwargs):
        if self == mutex:
            return SimpleNamespace(st_mode=stat.S_IFIFO, st_file_attributes=0)
        return real_lstat(self, *args, **kwargs)

    def guarded_open(self, *args, **kwargs):
        assert self != mutex, "A nonregular writer mutex was opened"
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", observed_lstat)
    monkeypatch.setattr(Path, "open", guarded_open)
    with pytest.raises(controls.OperationalControlConfigError, match="unsafe_path"):
        controls.set_operational_controls(tmp_path, _pair("4", "7"), expected_sha256=original.catalog_sha256)
    assert path.read_bytes() == _pair()


@pytest.mark.parametrize("problem", ["unit", "kind", "binding", "inactive", "negative", "renamed", "missing"])
def test_inventory_git_probe_consumer_contract_rejects_invalid_replacement(tmp_path: Path, problem: str) -> None:
    root = Path(__file__).resolve().parents[2]
    original = (root / controls.CATALOG_RELATIVE_PATH).read_bytes()
    path = tmp_path / controls.CATALOG_RELATIVE_PATH
    path.parent.mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    path.write_bytes(original)
    document = tomlkit.parse(original.decode("utf-8"))
    row = next(r for r in document["controls"] if r["id"] == controls.INVENTORY_GIT_PROBE_CONTROL)
    if problem == "unit":
        row["unit"] = "count"
    elif problem == "kind":
        row["numeric_kind"] = "integer"
        row["minimum"] = "1"
    elif problem == "binding":
        row["consumers"] = ["other.consumer"]
    elif problem == "inactive":
        row["migration_state"] = "candidate"
    elif problem == "negative":
        row["minimum"] = "-1"
        row["value"] = "-0.5"
        row["zero_semantics"] = "literal"  # Reach the positive inventory-consumer contract check.
    elif problem == "renamed":
        row["id"] = "other.git_probe_seconds"
    elif problem == "missing":
        document["controls"] = [r for r in document["controls"] if r["id"] != controls.INVENTORY_GIT_PROBE_CONTROL]
    snapshot = controls.load_operational_control_catalog(tmp_path)
    with pytest.raises(controls.OperationalControlConfigError, match="consumer_contract"):
        controls.set_operational_controls(
            tmp_path, tomlkit.dumps(document).encode("utf-8"), expected_sha256=snapshot.catalog_sha256
        )
    assert path.read_bytes() == original


@pytest.mark.parametrize("remove", ["registry", "all"])
def test_replacement_cannot_drop_a_whole_configured_consumer(tmp_path: Path, remove: str) -> None:
    root = Path(__file__).resolve().parents[2]
    original = (root / controls.CATALOG_RELATIVE_PATH).read_bytes()
    path = _write(tmp_path, original)
    snapshot = controls.load_operational_control_catalog(tmp_path)
    document = tomlkit.parse(original.decode("utf-8"))
    document["controls"] = (
        [] if remove == "all" else [r for r in document["controls"] if not r["id"].startswith("registry.")]
    )
    document["invariants"] = []
    with pytest.raises(controls.OperationalControlConfigError, match="consumer_contract"):
        controls.set_operational_controls(
            tmp_path, tomlkit.dumps(document).encode("utf-8"), expected_sha256=snapshot.catalog_sha256
        )
    assert path.read_bytes() == original


def test_setter_refuses_invalid_current_artifact_without_erasing_it(tmp_path: Path) -> None:
    payload = b"invalid TOML"
    path = _write(tmp_path, payload)
    expected = "sha256:" + hashlib.sha256(payload).hexdigest()
    with pytest.raises(controls.OperationalControlConfigError, match="malformed_catalog"):
        controls.set_operational_controls(tmp_path, _pair(), expected_sha256=expected)
    assert path.read_bytes() == payload


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    identity = [
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.autocrlf=false",
        "-c",
        "core.safecrlf=false",
    ]
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    return subprocess.run(
        ["git", *identity, "-C", str(root), *args],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def _junction(link: Path, target: Path) -> bool:
    """Create a directory link at ``link``; False when the host cannot create one."""
    if os.name != "nt":
        os.symlink(target, link, target_is_directory=True)
        return True

    def quote(path):
        return "'" + str(path).replace("'", "''") + "'"

    command = f"New-Item -ItemType Junction -Path {quote(link)} -Target {quote(target)} | Out-Null"
    run = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return run.returncode == 0 and link.exists()


def _governance_status(root: Path, *flags: str) -> list[str]:
    run = _git(root, "status", "--porcelain", *flags, "--", "config/governance")
    assert run.returncode == 0, run.stdout + run.stderr
    return run.stdout.splitlines()


def test_no_op_set_leaves_the_governance_tree_clean_and_locks_in_git_metadata(tmp_path):
    if shutil.which("git") is None:
        pytest.skip("git is not on PATH")
    init = _git(tmp_path, "init")
    assert init.returncode == 0, init.stdout + init.stderr
    _write(tmp_path, _pair())
    for step in (("add", "config/governance"), ("commit", "-m", "fixture")):
        run = _git(tmp_path, *step)
        assert run.returncode == 0, run.stdout + run.stderr
    governance = tmp_path / "config" / "governance"
    snapshot = controls.load_operational_control_catalog(tmp_path)
    result = controls.set_operational_controls(tmp_path, _pair(), expected_sha256=snapshot.catalog_sha256)
    assert result["changed"] is False
    assert _governance_status(tmp_path) == []
    assert _governance_status(tmp_path, "--ignored") == []
    assert list(governance.rglob("*.lock")) == []
    assert list(governance.glob(".control-update-*")) == []
    assert (tmp_path / ".git" / controls.WRITER_LOCK_NAME).is_file()
    changed = controls.set_operational_controls(tmp_path, _pair("4", "7"), expected_sha256=snapshot.catalog_sha256)
    assert changed["changed"] is True
    assert _governance_status(tmp_path) == [" M config/governance/operational-controls.toml"]
    assert list(governance.rglob("*.lock")) == []
    assert sorted(p.name for p in governance.iterdir()) == ["operational-controls.toml"]


def test_writer_lock_resolves_linked_worktree_metadata_from_the_gitdir_file(tmp_path):
    root = tmp_path / "wt"
    meta = tmp_path / "meta" / "worktrees" / "wt"
    meta.mkdir(parents=True)
    _write(root, _pair())
    (root / ".git").rmdir()
    (root / ".git").write_text(f"gitdir: {meta}\n", encoding="utf-8")
    expected = meta.resolve() / controls.WRITER_LOCK_NAME
    assert controls._writer_lock_path(root) == expected
    (root / ".git").write_text("gitdir: ../meta/worktrees/wt\n", encoding="utf-8")
    assert controls._writer_lock_path(root) == expected
    snapshot = controls.load_operational_control_catalog(root)
    result = controls.set_operational_controls(root, _pair("4", "7"), expected_sha256=snapshot.catalog_sha256)
    assert result["changed"] is True
    assert (root / controls.CATALOG_RELATIVE_PATH).read_bytes() == _pair("4", "7")
    assert sorted(p.name for p in (root / "config" / "governance").iterdir()) == ["operational-controls.toml"]
    assert expected.is_file()
    assert list(root.rglob("*.lock")) == []


def test_writer_refuses_roots_without_git_metadata_before_reading(tmp_path, monkeypatch):
    path = tmp_path / controls.CATALOG_RELATIVE_PATH
    path.parent.mkdir(parents=True)
    path.write_bytes(_pair())
    expected = "sha256:" + hashlib.sha256(_pair()).hexdigest()
    real_open = Path.open

    def guarded_open(self, *args, **kwargs):
        assert self != path, "The catalog was opened before the writer mutex was resolved"
        return real_open(self, *args, **kwargs)

    def refused(match):
        with monkeypatch.context() as patch:
            patch.setattr(Path, "open", guarded_open)
            with pytest.raises(controls.OperationalControlConfigError, match=match):
                controls.set_operational_controls(tmp_path, _pair("4", "7"), expected_sha256=expected)
        assert path.read_bytes() == _pair()
        assert list(tmp_path.rglob("*.lock")) == []

    refused("writer_unavailable")
    entry = tmp_path / ".git"
    entry.write_text("not a worktree pointer\n", encoding="utf-8")
    refused("writer_unavailable")
    entry.write_text("gitdir: missing/metadata\n", encoding="utf-8")
    refused("writer_unavailable")
    entry.unlink()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    if not _junction(entry, elsewhere):
        pytest.skip("The host cannot create a directory junction")
    refused("unsafe_path")
