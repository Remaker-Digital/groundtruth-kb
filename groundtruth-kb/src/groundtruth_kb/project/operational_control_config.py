"""One validated live control artifact, read afresh at each operation boundary.

DCL-CENTRAL-DYNAMIC-OPERATIONAL-CONTROLS-001 selects the existing TOML carrier.
There are no environment, package-location, source-value or cached fallbacks.
Schema limits bound parsing; they are format limits, not runtime tuning values.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
import sys
import tempfile
import tomllib
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import Any, NoReturn, TypeAlias

NumericValue: TypeAlias = int | Decimal
CATALOG_RELATIVE_PATH = Path("config/governance/operational-controls.toml")
CATALOG_SCHEMA_VERSION = 2
# Retained bounded-format limits. Changing these changes the accepted format.
MAX_CATALOG_BYTES = 256 * 1024
MAX_CONTROL_COUNT = 512
MAX_INVARIANT_COUNT = 512
MAX_IDENTIFIER_LENGTH = 128
MAX_PROSE_LENGTH = 2048
MAX_NUMERIC_DIGITS = 24
MAX_DECIMAL_PLACES = 9
MAX_ABSOLUTE_VALUE = Decimal("1000000000000000000")
_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
_UNITS = frozenset({"seconds", "milliseconds", "count", "ratio", "percent"})
_KINDS = frozenset({"integer", "decimal"})
_STATES = frozenset({"active", "candidate", "retired", "superseded"})
_CATEGORIES = frozenset(
    {
        "capacity",
        "expiry",
        "fan_out",
        "grace_window",
        "live_worker_concurrency",
        "rate_limit",
        "retry_count",
        "retry_schedule",
        "threshold",
        "throttle",
        "timeout",
        "timer",
        "ttl",
    }
)
_CAPS = frozenset({"capacity", "fan_out", "live_worker_concurrency"})
_SCOPES = frozenset({"platform", "per_dispatch", "per_harness", "per_operation", "per_role"})
_OPERATORS = frozenset({"eq", "gt", "gte", "lt", "lte"})
_CONTROL_FIELDS = frozenset(
    {
        "id",
        "description",
        "numeric_kind",
        "unit",
        "value",
        "minimum",
        "maximum",
        "category",
        "scope",
        "zero_semantics",
        "rationale",
        "tolerance_rationale",
        "migration_state",
        "consumers",
        "evidence_refs",
        "reload_behavior",
        "failure_disposition",
        "observability",
        "capacity_observation_key",
    }
)


# Required keys, units and relationships are consumer contracts, never live values.
REGISTRY_CONTROL_UNITS: Mapping[str, str] = MappingProxyType(
    {
        "registry.lock.acquire_seconds": "seconds",
        "registry.lock.initial_backoff_seconds": "seconds",
        "registry.lock.max_backoff_seconds": "seconds",
        "registry.lock.backoff_factor": "ratio",
        "registry.lock.jitter_min_ratio": "ratio",
        "registry.lock.jitter_max_ratio": "ratio",
        "registry.git_probe_seconds": "seconds",
    }
)
_REGISTRY_CONSUMER = "groundtruth_kb.project.registry_control_plane"
INVENTORY_GIT_PROBE_CONTROL = "inventory.git_probe_seconds"
_INVENTORY_CONSUMER = "scripts.timer_inventory"
_REGISTRY_RELATIONS = frozenset(
    {
        ("registry.lock.initial_backoff_seconds", "lte", "registry.lock.max_backoff_seconds"),
        ("registry.lock.max_backoff_seconds", "lt", "registry.lock.acquire_seconds"),
        ("registry.lock.jitter_min_ratio", "lte", "registry.lock.jitter_max_ratio"),
    }
)


class OperationalControlConfigError(RuntimeError):
    """A visible refusal with an actionable reason and no fallback."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> NoReturn:
    raise OperationalControlConfigError(code, detail)


def _sha(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _text(value: object, field: str, maximum: int = MAX_PROSE_LENGTH) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        _fail("invalid_text", f"{field} must be nonempty text within the format bound")
    return value.strip()


def _enum(value: object, field: str, allowed: frozenset[str]) -> str:
    text = _text(value, field, MAX_IDENTIFIER_LENGTH)
    if text not in allowed:
        _fail("unknown_enum", f"{field} must be one of {sorted(allowed)}")
    return text


def _identifier(value: object, field: str) -> str:
    text = _text(value, field, MAX_IDENTIFIER_LENGTH)
    if not _ID.fullmatch(text):
        _fail("invalid_identifier", f"{field} must be a stable lowercase key")
    return text


def _strings(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or len(value) > MAX_CONTROL_COUNT:
        _fail("invalid_metadata", f"{field} must be a nonempty bounded array of text")
    values = tuple(_text(item, field) for item in value)
    if len(set(values)) != len(values):
        _fail("invalid_metadata", f"{field} contains duplicate entries")
    return values


def _numeric(value: object, *, kind: str, field: str) -> NumericValue:
    if isinstance(value, (bool, float)) or not isinstance(value, (int, str, Decimal)):
        _fail("invalid_numeric", f"{field} must be an exact {kind} value")
    text = str(value).strip()
    if not text or len(text) > MAX_IDENTIFIER_LENGTH:
        _fail("invalid_numeric", f"{field} is empty or outside the numeric format bound")
    try:
        number = Decimal(text)
    except InvalidOperation:
        _fail("invalid_numeric", f"{field} must be numeric")
    if not number.is_finite():
        _fail("invalid_numeric", f"{field} must be finite")
    parts = number.as_tuple()
    exponent = parts.exponent
    if not isinstance(exponent, int):
        _fail("invalid_numeric", f"{field} must have a finite exponent")
    if (
        number.copy_abs() > MAX_ABSOLUTE_VALUE
        or len(parts.digits) > MAX_NUMERIC_DIGITS
        or max(0, -exponent) > MAX_DECIMAL_PLACES
    ):
        _fail("resource_bound", f"{field} exceeds numeric format bounds")
    if kind == "integer":
        if number != number.to_integral_value():
            _fail("invalid_numeric", f"{field} must be an integer")
        return int(number)
    return number


@dataclass(frozen=True, slots=True)
class OperationalControlDefinition:
    control_id: str
    description: str
    numeric_kind: str
    unit: str
    value: NumericValue
    minimum: NumericValue
    maximum: NumericValue
    category: str
    scope: str
    zero_semantics: str
    rationale: str
    tolerance_rationale: str
    migration_state: str
    consumers: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    reload_behavior: str
    failure_disposition: str
    observability: tuple[str, ...]
    capacity_observation_key: str | None


@dataclass(frozen=True, slots=True)
class OperationalControlInvariant:
    invariant_id: str
    left_control_id: str
    operator: str
    right_control_id: str
    margin: NumericValue


@dataclass(frozen=True, slots=True)
class OperationalControlCatalog:
    schema_version: int
    definitions: Mapping[str, OperationalControlDefinition]
    invariants: tuple[OperationalControlInvariant, ...]
    catalog_sha256: str
    source_reference: str


@dataclass(frozen=True, slots=True)
class ResolvedOperationalControl:
    control_id: str
    value: NumericValue
    effective_value: NumericValue
    unit: str
    is_disabled: bool
    catalog_sha256: str
    capacity_observation_key: str | None


def _invariants_hold(invariants: Sequence[OperationalControlInvariant], values: Mapping[str, NumericValue]) -> None:
    for invariant in invariants:
        left = values[invariant.left_control_id]
        right = values[invariant.right_control_id]
        margin = invariant.margin
        checks = {
            "lt": left + margin < right,
            "lte": left + margin <= right,
            "eq": left == right,
            "gte": left >= right + margin,
            "gt": left > right + margin,
        }
        if not checks[invariant.operator]:
            _fail(
                "invariant_violation",
                f"{invariant.invariant_id} failed for {invariant.left_control_id} and {invariant.right_control_id}",
            )


def validate_operational_control_bytes(
    payload: bytes, *, source_reference: str = "proposed artifact"
) -> OperationalControlCatalog:
    if len(payload) > MAX_CATALOG_BYTES:
        _fail("resource_bound", "catalog exceeds the format byte bound")
    try:
        document = tomllib.loads(payload.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError):
        _fail("malformed_catalog", "catalog must be strict UTF-8 TOML")
    if set(document) != {"schema_version", "controls", "invariants"}:
        _fail(
            "invalid_catalog_shape",
            "catalog requires exactly schema_version, controls and invariants; environment authority is obsolete",
        )
    version = document["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != CATALOG_SCHEMA_VERSION:
        _fail("unknown_schema", "catalog must use schema_version 2 with live values")
    raw_controls = document["controls"]
    raw_invariants = document["invariants"]
    if (
        not isinstance(raw_controls, list)
        or len(raw_controls) > MAX_CONTROL_COUNT
        or not isinstance(raw_invariants, list)
        or len(raw_invariants) > MAX_INVARIANT_COUNT
    ):
        _fail("invalid_catalog_shape", "controls and invariants must be bounded arrays of tables")
    definitions: dict[str, OperationalControlDefinition] = {}
    for raw in raw_controls:
        if (
            not isinstance(raw, dict)
            or not set(raw) >= _CONTROL_FIELDS - {"capacity_observation_key"}
            or set(raw) - _CONTROL_FIELDS
        ):
            _fail("invalid_control_shape", "control entry has missing or unknown fields")
        ident = _identifier(raw["id"], "control.id")
        if ident in definitions:
            _fail("duplicate_control", f"control {ident} is duplicated")
        kind = _enum(raw["numeric_kind"], f"{ident}.numeric_kind", _KINDS)
        unit = _enum(raw["unit"], f"{ident}.unit", _UNITS)
        value = _numeric(raw["value"], kind=kind, field=f"{ident}.value")
        minimum = _numeric(raw["minimum"], kind=kind, field=f"{ident}.minimum")
        maximum = _numeric(raw["maximum"], kind=kind, field=f"{ident}.maximum")
        if minimum > maximum or not minimum <= value <= maximum:
            _fail("out_of_bounds", f"{ident} has an out-of-bound value or inconsistent bounds")
        category = _enum(raw["category"], f"{ident}.category", _CATEGORIES)
        zero = _enum(raw["zero_semantics"], f"{ident}.zero_semantics", frozenset({"disable", "forbidden", "literal"}))
        if zero == "forbidden" and minimum <= 0 <= maximum:
            _fail("invalid_zero_semantics", f"{ident} permits forbidden zero")
        observation = raw.get("capacity_observation_key")
        if observation is not None:
            observation = _identifier(observation, f"{ident}.capacity_observation_key")
        if category in _CAPS and (
            kind != "integer" or unit != "count" or minimum != 0 or zero != "disable" or observation is None
        ):
            _fail(
                "invalid_cap_contract",
                f"{ident} requires integer/count, minimum zero, disable semantics and a capacity observation",
            )
        if observation is not None and category not in _CAPS:
            _fail("invalid_cap_contract", f"{ident} has a capacity observation outside a capacity category")
        definitions[ident] = OperationalControlDefinition(
            ident,
            _text(raw["description"], f"{ident}.description"),
            kind,
            unit,
            value,
            minimum,
            maximum,
            category,
            _enum(raw["scope"], f"{ident}.scope", _SCOPES),
            zero,
            _text(raw["rationale"], f"{ident}.rationale"),
            _text(raw["tolerance_rationale"], f"{ident}.tolerance_rationale"),
            _enum(raw["migration_state"], f"{ident}.migration_state", _STATES),
            _strings(raw["consumers"], f"{ident}.consumers"),
            _strings(raw["evidence_refs"], f"{ident}.evidence_refs"),
            _enum(raw["reload_behavior"], f"{ident}.reload_behavior", frozenset({"next_operation"})),
            _enum(raw["failure_disposition"], f"{ident}.failure_disposition", frozenset({"refuse_new_operation"})),
            _strings(raw["observability"], f"{ident}.observability"),
            observation,
        )
    invariants: list[OperationalControlInvariant] = []
    seen: set[str] = set()
    endpoint_pairs: set[frozenset[str]] = set()
    for raw in raw_invariants:
        if not isinstance(raw, dict) or set(raw) != {"id", "left", "operator", "right", "margin"}:
            _fail("invalid_invariant_shape", "invariant requires exactly id, left, operator, right and margin")
        ident = _identifier(raw["id"], "invariant.id")
        left = _identifier(raw["left"], f"{ident}.left")
        right = _identifier(raw["right"], f"{ident}.right")
        if ident in seen or left == right or left not in definitions or right not in definitions:
            _fail("invalid_invariant", f"{ident} has duplicate identity or invalid endpoints")
        pair = frozenset({left, right})
        if pair in endpoint_pairs:
            _fail("contradictory_invariant", f"{ident} repeats a relation between the same endpoints")
        if (
            (definitions[left].numeric_kind, definitions[left].unit)
            != (definitions[right].numeric_kind, definitions[right].unit)
            or definitions[left].migration_state != "active"
            or definitions[right].migration_state != "active"
        ):
            _fail("invalid_invariant", f"{ident} endpoints must be active and share kind and unit")
        operator = _enum(raw["operator"], f"{ident}.operator", _OPERATORS)
        margin = _numeric(raw["margin"], kind=definitions[left].numeric_kind, field=f"{ident}.margin")
        if margin < 0 or operator == "eq" and margin != 0:
            _fail("invalid_invariant", f"{ident} has an invalid margin")
        seen.add(ident)
        endpoint_pairs.add(pair)
        invariants.append(OperationalControlInvariant(ident, left, operator, right, margin))
    registry_present = bool(REGISTRY_CONTROL_UNITS.keys() & definitions.keys()) or any(
        _REGISTRY_CONSUMER in definition.consumers for definition in definitions.values()
    )
    if registry_present:
        for key, unit in REGISTRY_CONTROL_UNITS.items():
            definition = definitions.get(key)
            if definition is None or definition.migration_state != "active":
                _fail("consumer_contract", f"Registry consumer requires active key {key}")
            if (
                definition.unit != unit
                or definition.numeric_kind != "decimal"
                or _REGISTRY_CONSUMER not in definition.consumers
            ):
                _fail(
                    "consumer_contract",
                    f"Registry consumer requires decimal/{unit} key {key} with its consumer binding",
                )
        relations = {(item.left_control_id, item.operator, item.right_control_id) for item in invariants}
        if not relations >= _REGISTRY_RELATIONS:
            _fail("consumer_contract", "Registry consumer requires its coupled backoff/wait and jitter relations")
    inventory_present = INVENTORY_GIT_PROBE_CONTROL in definitions or any(
        _INVENTORY_CONSUMER in definition.consumers for definition in definitions.values()
    )
    if inventory_present:
        definition = definitions.get(INVENTORY_GIT_PROBE_CONTROL)
        if definition is None or definition.migration_state != "active":
            _fail("consumer_contract", "Inventory Git probe requires its active control key")
        if (
            definition.unit != "seconds"
            or definition.numeric_kind != "decimal"
            or _INVENTORY_CONSUMER not in definition.consumers
            or definition.value <= 0
        ):
            _fail(
                "consumer_contract",
                "Inventory Git probe requires a positive decimal/seconds value and its consumer binding",
            )
    _invariants_hold(invariants, {key: value.value for key, value in definitions.items()})
    return OperationalControlCatalog(
        version, MappingProxyType(definitions), tuple(invariants), _sha(payload), source_reference
    )


def _safe_path(project_root: Path) -> Path:
    try:
        root = project_root.resolve(strict=True)
        if not root.is_dir():
            _fail("unsafe_path", "selected project root is not a directory")
        path = root / CATALOG_RELATIVE_PATH
        for item in (path, *path.parents):
            if item == root:
                break
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(
                stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0
            ):
                _fail("unsafe_path", "control artifact and parents must not be redirected")
        if not path.is_file():
            _fail("unsafe_path", "control artifact is not a regular file")
        return path
    except OSError as exc:
        _fail(
            "unavailable_catalog", f"control artifact is unavailable ({type(exc).__name__}); restore its canonical file"
        )


def _read(path: Path) -> bytes:
    try:
        with path.open("rb") as stream:
            value = stream.read(MAX_CATALOG_BYTES + 1)
    except OSError as exc:
        _fail("unavailable_catalog", f"cannot read control artifact ({type(exc).__name__})")
    if len(value) > MAX_CATALOG_BYTES:
        _fail("resource_bound", "catalog exceeds the format byte bound")
    return value


def load_operational_control_catalog(project_root: Path) -> OperationalControlCatalog:
    """Read a fresh immutable snapshot from the explicitly selected root."""
    path = _safe_path(project_root)
    return validate_operational_control_bytes(_read(path), source_reference=str(path))


def resolve_operational_controls(
    catalog: OperationalControlCatalog,
    control_ids: Sequence[str] | None = None,
    *,
    capacity_observations: Mapping[str, int | None] | None = None,
) -> Mapping[str, ResolvedOperationalControl]:
    active = {
        key: definition for key, definition in catalog.definitions.items() if definition.migration_state == "active"
    }
    requested = list(active) if control_ids is None else list(control_ids)
    if len(set(requested)) != len(requested):
        _fail("duplicate_control_request", "requested controls must be unique")
    if set(requested) - active.keys():
        _fail("unknown_control", "requested key is absent or inactive; no fallback is available")
    applicable = []
    for invariant in catalog.invariants:
        count = len({invariant.left_control_id, invariant.right_control_id} & set(requested))
        if count == 1:
            _fail("split_invariant_request", f"{invariant.invariant_id} endpoints must resolve together")
        if count == 2:
            applicable.append(invariant)
    observations = dict(capacity_observations or {})
    expected = {
        active[key].capacity_observation_key for key in requested if active[key].capacity_observation_key is not None
    }
    if set(observations) - expected:
        _fail("unknown_capacity_observation", "unexpected capacity observations")
    resolved = {}
    for key in requested:
        definition = active[key]
        effective = definition.value
        observation_key = definition.capacity_observation_key
        if observation_key is not None:
            observed = observations.get(observation_key)
            if isinstance(observed, bool) or not isinstance(observed, int) or observed < 0:
                _fail("unknown_capacity", f"{key} requires a non-negative measured capacity")
            effective = min(effective, observed)
        resolved[key] = ResolvedOperationalControl(
            key,
            definition.value,
            effective,
            definition.unit,
            definition.zero_semantics == "disable" and effective == 0,
            catalog.catalog_sha256,
            observation_key,
        )
    _invariants_hold(applicable, {key: value.effective_value for key, value in resolved.items()})
    return MappingProxyType(resolved)


def control_value(controls: Mapping[str, ResolvedOperationalControl], key: str, *, unit: str) -> NumericValue:
    if key not in controls:
        _fail("unknown_control", f"required key {key} is absent")
    value = controls[key]
    if value.unit != unit:
        _fail("unit_mismatch", f"{key} requires {unit}, found {value.unit}")
    return value.effective_value


def catalog_dict(catalog: OperationalControlCatalog) -> dict[str, Any]:
    """Keep exact decimal values as strings in deterministic JSON output."""

    def encode(value: Any) -> Any:
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, (tuple, list)):
            return [encode(item) for item in value]
        if isinstance(value, dict):
            return {key: encode(item) for key, item in value.items()}
        return value

    return {
        "schema_version": catalog.schema_version,
        "catalog_sha256": catalog.catalog_sha256,
        "source_reference": catalog.source_reference,
        "controls": {key: encode(asdict(value)) for key, value in sorted(catalog.definitions.items())},
        "invariants": [encode(asdict(value)) for value in catalog.invariants],
    }


def diff_operational_controls(project_root: Path, proposed: bytes) -> dict[str, Any]:
    before = catalog_dict(load_operational_control_catalog(project_root))
    after = catalog_dict(validate_operational_control_bytes(proposed))
    changes = {
        key: {"before": before["controls"].get(key), "after": after["controls"].get(key)}
        for key in sorted(before["controls"].keys() | after["controls"].keys())
        if before["controls"].get(key) != after["controls"].get(key)
    }
    return {
        "before_sha256": before["catalog_sha256"],
        "after_sha256": after["catalog_sha256"],
        "controls": changes,
        "invariants": {"before": before["invariants"], "after": after["invariants"]},
    }


@contextmanager
def _writer_lock(path: Path) -> Iterator[None]:
    """One nonblocking OS mutex; there is no retry timer or retained lease."""
    lock_path = path.with_name(path.name + ".lock")
    if lock_path.exists() or lock_path.is_symlink():
        info = lock_path.lstat()
        if (
            not stat.S_ISREG(info.st_mode)
            or stat.S_ISLNK(info.st_mode)
            or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            _fail("unsafe_path", "control writer lock must not be redirected")
    try:
        handle = lock_path.open("a+b")
    except OSError as exc:
        _fail("writer_unavailable", f"control writer mutex is unavailable ({type(exc).__name__})")
    with handle:
        try:
            handle.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            _fail("writer_busy", "another control writer is active; read current state and retry")
        try:
            yield
        finally:
            handle.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def set_operational_controls(project_root: Path, proposed: bytes, *, expected_sha256: str) -> dict[str, Any]:
    """Validate the entire replacement, compare current bytes and replace once.

    Direct owner edits need not take the cooperative mutex. A second read catches
    edits observed before replacement; post-replacement readback detects drift.
    No transaction/rollback guarantee is made for an uncooperative racing editor.
    """
    after = validate_operational_control_bytes(proposed)
    path = _safe_path(project_root)
    with _writer_lock(path):
        _safe_path(project_root)
        before = _read(path)
        if _sha(before) != expected_sha256:
            _fail("generation_conflict", "control artifact changed; show current state before retrying")
        current = validate_operational_control_bytes(before)
        known_keys = set(REGISTRY_CONTROL_UNITS) | {INVENTORY_GIT_PROBE_CONTROL}
        removed = (known_keys & current.definitions.keys()) - after.definitions.keys()
        if removed:
            _fail("consumer_contract", "Replacement removes required controls for a currently configured consumer")
        changed = before != proposed
        if changed:
            temporary: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".control-update-", delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(proposed)
                    stream.flush()
                    os.fsync(stream.fileno())
                if _read(_safe_path(project_root)) != before:
                    _fail("generation_conflict", "control artifact changed during validation")
                os.replace(temporary, path)
                temporary = None
            except OSError as exc:
                _fail("replace_failed", f"control replacement failed ({type(exc).__name__}); inspect current state")
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        if _read(_safe_path(project_root)) != proposed:
            _fail("readback_conflict", "control artifact differs after replacement; inspect current state")
    return {
        "changed": changed,
        "before_sha256": expected_sha256,
        "catalog_sha256": after.catalog_sha256,
        "reload_behavior": "next_operation",
        "control_count": len(after.definitions),
    }
