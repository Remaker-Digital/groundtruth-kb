"""Typed, fail-closed resolution for governed operational controls.

The checked-in catalog owns definitions, relaxed defaults, units, bounds, and
relations.  The root ``.env.local`` remains the only production authority for
live platform overrides.  This module deliberately performs no import-time I/O
and never consults ``os.environ``.

WI-5806 is a foundation slice: the production catalog initially contains no
active definitions.  Later consumer migrations must provide bindings produced
by the governed environment-schema surface and switch the consumer in the same
governed change.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import TypeAlias

__all__ = [
    "MAX_CATALOG_BYTES",
    "MAX_CONTROL_COUNT",
    "MAX_ENVIRONMENT_BYTES",
    "MAX_INVARIANT_COUNT",
    "OperationalControlCatalog",
    "OperationalControlConfigError",
    "OperationalControlDefinition",
    "OperationalControlEnvironmentBinding",
    "OperationalControlInvariant",
    "PlatformControlEnvironmentSnapshot",
    "ResolvedOperationalControl",
    "create_test_control_environment_snapshot",
    "load_operational_control_catalog",
    "load_platform_control_environment_snapshot",
    "load_test_operational_control_catalog",
    "resolve_operational_control",
    "resolve_operational_controls",
]

NumericValue: TypeAlias = int | Decimal

CATALOG_RELATIVE_PATH = Path("config") / "governance" / "operational-controls.toml"
CATALOG_SCHEMA_VERSION = 1
LIVE_VALUE_AUTHORITY = "root_env_local"

MAX_CATALOG_BYTES = 256 * 1024
MAX_ENVIRONMENT_BYTES = 1024 * 1024
MAX_CONTROL_COUNT = 512
MAX_INVARIANT_COUNT = 512
MAX_ENVIRONMENT_LINES = 4096
MAX_IDENTIFIER_LENGTH = 128
MAX_ENVIRONMENT_NAME_LENGTH = 128
MAX_PROSE_LENGTH = 2048
MAX_ENVIRONMENT_VALUE_LENGTH = 4096
MAX_NUMERIC_DIGITS = 24
MAX_DECIMAL_PLACES = 9
MAX_ABSOLUTE_VALUE = Decimal("1000000000000000000")

_CONTROL_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
_INVARIANT_ID_RE = _CONTROL_ID_RE
_SCHEMA_REF_RE = re.compile(r"^[A-Z0-9][A-Z0-9._:@/-]{0,127}$")
_ENVIRONMENT_NAME_RE = re.compile(r"^GTKB_CONTROL_[A-Z0-9_]+$")
_SECRET_SEGMENTS = frozenset({"AUTH", "CREDENTIAL", "KEY", "PASSWORD", "SECRET", "TOKEN"})

_NUMERIC_KINDS = frozenset({"integer", "decimal"})
_UNITS = frozenset({"seconds", "milliseconds", "count", "ratio", "percent"})
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
_CAP_CATEGORIES = frozenset({"capacity", "fan_out", "live_worker_concurrency"})
_SCOPES = frozenset({"platform", "per_dispatch", "per_harness", "per_operation", "per_role"})
_ZERO_SEMANTICS = frozenset({"disable", "forbidden", "literal"})
_MIGRATION_STATES = frozenset({"active", "candidate", "retired", "superseded"})
_OPERATORS = frozenset({"eq", "gt", "gte", "lt", "lte"})

_CATALOG_KEYS = frozenset({"schema_version", "live_value_authority", "controls", "invariants"})
_CONTROL_KEYS = frozenset(
    {
        "id",
        "environment_schema_ref",
        "numeric_kind",
        "unit",
        "relaxed_default",
        "minimum",
        "maximum",
        "category",
        "scope",
        "zero_semantics",
        "rationale",
        "tolerance_rationale",
        "migration_state",
        "capacity_observation_key",
    }
)
_REQUIRED_CONTROL_KEYS = _CONTROL_KEYS - {"capacity_observation_key"}
_INVARIANT_KEYS = frozenset({"id", "left", "operator", "right", "margin"})
_REQUIRED_INVARIANT_KEYS = _INVARIANT_KEYS - {"margin"}


class OperationalControlConfigError(RuntimeError):
    """A deterministic, typed operational-control configuration failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True, slots=True)
class OperationalControlEnvironmentBinding:
    """Attested non-secret environment-schema field used by one control."""

    schema_ref: str
    environment_name: str
    version: int
    scope: str = "platform"
    classification: str = "non_secret"
    field_kind: str = "operational_control"
    status: str = "verified"
    source_kind: str = "governed_env_schema"


@dataclass(frozen=True, slots=True)
class OperationalControlDefinition:
    """One immutable, validated catalog definition."""

    control_id: str
    environment_schema_ref: str
    environment_name: str
    environment_schema_version: int
    numeric_kind: str
    unit: str
    relaxed_default: NumericValue
    minimum: NumericValue
    maximum: NumericValue
    category: str
    scope: str
    zero_semantics: str
    rationale: str
    tolerance_rationale: str
    migration_state: str
    capacity_observation_key: str | None
    definition_digest: str


@dataclass(frozen=True, slots=True)
class OperationalControlInvariant:
    """A relation evaluated over values from one catalog/environment snapshot."""

    invariant_id: str
    left_control_id: str
    operator: str
    right_control_id: str
    margin: NumericValue


@dataclass(frozen=True, slots=True)
class OperationalControlCatalog:
    """An immutable parsed catalog bound to its exact source bytes."""

    schema_version: int
    live_value_authority: str
    definitions: Mapping[str, OperationalControlDefinition]
    invariants: tuple[OperationalControlInvariant, ...]
    catalog_sha256: str
    source_kind: str
    source_reference: str


@dataclass(frozen=True, slots=True)
class PlatformControlEnvironmentSnapshot:
    """A bounded snapshot containing only declared operational-control values."""

    source_kind: str
    source_reference: str
    catalog_sha256: str
    values: Mapping[str, str]
    snapshot_digest: str


@dataclass(frozen=True, slots=True)
class ResolvedOperationalControl:
    """A typed control value with complete bounded provenance."""

    control_id: str
    value: NumericValue
    effective_value: NumericValue
    unit: str
    source: str
    is_disabled: bool
    catalog_schema_version: int
    catalog_sha256: str
    definition_digest: str
    environment_snapshot_digest: str
    environment_source_kind: str
    capacity_observation_key: str | None


def _fail(code: str, detail: str) -> None:
    raise OperationalControlConfigError(code, detail)


def _sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _canonical_digest(value: object) -> str:
    return _sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))


def _bounded_text(value: object, *, field: str, maximum: int = MAX_PROSE_LENGTH) -> str:
    if not isinstance(value, str):
        _fail("invalid_text", f"{field} must be a string")
    normalized = value.strip()
    if not normalized:
        _fail("invalid_text", f"{field} must not be empty")
    if len(normalized) > maximum:
        _fail("resource_bound", f"{field} exceeds {maximum} characters")
    return normalized


def _closed_value(value: object, *, field: str, allowed: frozenset[str]) -> str:
    normalized = _bounded_text(value, field=field, maximum=MAX_IDENTIFIER_LENGTH)
    if normalized not in allowed:
        _fail("unknown_enum", f"{field}={normalized!r} is not one of {sorted(allowed)}")
    return normalized


def _positive_version(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail("invalid_version", f"{field} must be a positive integer")
    return value


def _numeric(value: object, *, kind: str, field: str) -> NumericValue:
    if isinstance(value, (bool, float)) or not isinstance(value, (int, str, Decimal)):
        _fail("invalid_numeric", f"{field} must be an exact {kind} value")
    text = str(value).strip()
    if not text:
        _fail("invalid_numeric", f"{field} must not be empty")
    try:
        decimal = Decimal(text)
    except InvalidOperation:
        _fail("invalid_numeric", f"{field}={text!r} is not numeric")
    if not decimal.is_finite():
        _fail("invalid_numeric", f"{field} must be finite")
    if abs(decimal) > MAX_ABSOLUTE_VALUE:
        _fail("resource_bound", f"{field} exceeds the numeric magnitude bound")
    significant_digits = len(decimal.as_tuple().digits)
    decimal_places = max(0, -decimal.as_tuple().exponent)
    if significant_digits > MAX_NUMERIC_DIGITS or decimal_places > MAX_DECIMAL_PLACES:
        _fail("resource_bound", f"{field} exceeds numeric precision bounds")
    if kind == "integer":
        if decimal != decimal.to_integral_value():
            _fail("invalid_numeric", f"{field} must be an integer")
        return int(decimal)
    return decimal


def _binding_map(
    bindings: Iterable[OperationalControlEnvironmentBinding], *, allow_test_bindings: bool
) -> dict[str, OperationalControlEnvironmentBinding]:
    result: dict[str, OperationalControlEnvironmentBinding] = {}
    environment_names: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, OperationalControlEnvironmentBinding):
            _fail("invalid_schema_binding", "environment bindings must use OperationalControlEnvironmentBinding")
        schema_ref = _bounded_text(binding.schema_ref, field="binding.schema_ref", maximum=MAX_IDENTIFIER_LENGTH)
        if not _SCHEMA_REF_RE.fullmatch(schema_ref):
            _fail("invalid_schema_binding", f"schema reference {schema_ref!r} is not canonical")
        if schema_ref in result:
            _fail("duplicate_schema_binding", f"schema reference {schema_ref!r} is duplicated")
        name = _bounded_text(
            binding.environment_name,
            field=f"{schema_ref}.environment_name",
            maximum=MAX_ENVIRONMENT_NAME_LENGTH,
        )
        if not _ENVIRONMENT_NAME_RE.fullmatch(name):
            _fail("invalid_schema_binding", f"environment name {name!r} is outside GTKB_CONTROL_ namespace")
        if _SECRET_SEGMENTS.intersection(name.split("_")):
            _fail("secret_class_binding", f"environment name {name!r} contains a secret-class segment")
        if name in environment_names:
            _fail("duplicate_environment_name", f"environment name {name!r} is duplicated")
        _positive_version(binding.version, field=f"{schema_ref}.version")
        if binding.scope != "platform":
            _fail("cross_scope_binding", f"schema reference {schema_ref!r} is not platform-scoped")
        if binding.classification != "non_secret":
            _fail("secret_class_binding", f"schema reference {schema_ref!r} is not non-secret")
        if binding.field_kind != "operational_control":
            _fail("invalid_schema_binding", f"schema reference {schema_ref!r} has the wrong field kind")
        if binding.status != "verified":
            _fail("stale_schema_binding", f"schema reference {schema_ref!r} is not verified")
        if binding.source_kind not in {"governed_env_schema", "test_fixture"}:
            _fail("invalid_schema_binding", f"schema reference {schema_ref!r} has an unknown source kind")
        if binding.source_kind == "test_fixture" and not allow_test_bindings:
            _fail("test_binding_in_production", f"schema reference {schema_ref!r} is test-only")
        result[schema_ref] = binding
        environment_names.add(name)
    return result


def _regular_file_bytes(path: Path, *, root: Path | None, maximum: int, label: str) -> bytes:
    if path.is_symlink():
        _fail("unsafe_path", f"{label} must not be a symlink: {path}")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        _fail("missing_file", f"{label} is unavailable: {path}: {exc}")
    if not resolved.is_file():
        _fail("unsafe_path", f"{label} is not a regular file: {path}")
    if root is not None:
        try:
            resolved.relative_to(root.resolve(strict=True))
        except (OSError, ValueError):
            _fail("root_escape", f"{label} escapes the project root: {path}")
    try:
        size = resolved.stat().st_size
    except OSError as exc:
        _fail("unreadable_file", f"cannot stat {label}: {path}: {exc}")
    if size > maximum:
        _fail("resource_bound", f"{label} exceeds {maximum} bytes")
    try:
        payload = resolved.read_bytes()
    except OSError as exc:
        _fail("unreadable_file", f"cannot read {label}: {path}: {exc}")
    if len(payload) != size:
        _fail("unstable_read", f"{label} changed while it was read: {path}")
    return payload


def _catalog_from_bytes(
    payload: bytes,
    *,
    source_kind: str,
    source_reference: str,
    bindings: Iterable[OperationalControlEnvironmentBinding],
    allow_test_bindings: bool,
) -> OperationalControlCatalog:
    if len(payload) > MAX_CATALOG_BYTES:
        _fail("resource_bound", f"catalog exceeds {MAX_CATALOG_BYTES} bytes")
    try:
        text = payload.decode("utf-8", errors="strict")
        document = tomllib.loads(text)
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        _fail("malformed_catalog", f"catalog is not strict UTF-8 TOML: {exc}")
    document_keys = set(document)
    required_catalog_keys = {"schema_version", "live_value_authority"}
    if not document_keys >= required_catalog_keys or document_keys - _CATALOG_KEYS:
        _fail(
            "unknown_catalog_field",
            f"catalog fields must use only {sorted(_CATALOG_KEYS)} and include {sorted(required_catalog_keys)}",
        )
    schema_version = _positive_version(document["schema_version"], field="schema_version")
    if schema_version != CATALOG_SCHEMA_VERSION:
        _fail("unknown_schema", f"unsupported catalog schema_version={schema_version}")
    authority = _bounded_text(document["live_value_authority"], field="live_value_authority")
    if authority != LIVE_VALUE_AUTHORITY:
        _fail("unknown_authority", f"live_value_authority must be {LIVE_VALUE_AUTHORITY!r}")
    control_rows = document.get("controls", [])
    invariant_rows = document.get("invariants", [])
    if not isinstance(control_rows, list) or not all(isinstance(item, dict) for item in control_rows):
        _fail("invalid_catalog_shape", "controls must be an array of tables")
    if not isinstance(invariant_rows, list) or not all(isinstance(item, dict) for item in invariant_rows):
        _fail("invalid_catalog_shape", "invariants must be an array of tables")
    if len(control_rows) > MAX_CONTROL_COUNT or len(invariant_rows) > MAX_INVARIANT_COUNT:
        _fail("resource_bound", "catalog collection count exceeds its bound")

    binding_by_ref = _binding_map(bindings, allow_test_bindings=allow_test_bindings)
    definitions: dict[str, OperationalControlDefinition] = {}
    used_schema_refs: set[str] = set()
    used_environment_names: set[str] = set()
    for index, row in enumerate(control_rows):
        label = f"controls[{index}]"
        keys = set(row)
        if not keys >= _REQUIRED_CONTROL_KEYS or keys - _CONTROL_KEYS:
            _fail("invalid_control_shape", f"{label} has missing or unknown fields")
        control_id = _bounded_text(row["id"], field=f"{label}.id", maximum=MAX_IDENTIFIER_LENGTH)
        if not _CONTROL_ID_RE.fullmatch(control_id):
            _fail("invalid_control_id", f"{control_id!r} is not canonical")
        if control_id in definitions:
            _fail("duplicate_control", f"control {control_id!r} is duplicated")
        schema_ref = _bounded_text(
            row["environment_schema_ref"],
            field=f"{label}.environment_schema_ref",
            maximum=MAX_IDENTIFIER_LENGTH,
        )
        binding = binding_by_ref.get(schema_ref)
        if binding is None:
            _fail("missing_schema_binding", f"control {control_id!r} lacks schema binding {schema_ref!r}")
        if schema_ref in used_schema_refs or binding.environment_name in used_environment_names:
            _fail("duplicate_environment_binding", f"control {control_id!r} reuses an environment binding")
        kind = _closed_value(row["numeric_kind"], field=f"{label}.numeric_kind", allowed=_NUMERIC_KINDS)
        unit = _closed_value(row["unit"], field=f"{label}.unit", allowed=_UNITS)
        minimum = _numeric(row["minimum"], kind=kind, field=f"{label}.minimum")
        maximum = _numeric(row["maximum"], kind=kind, field=f"{label}.maximum")
        default = _numeric(row["relaxed_default"], kind=kind, field=f"{label}.relaxed_default")
        if minimum > maximum or not minimum <= default <= maximum:
            _fail("invalid_bounds", f"control {control_id!r} has inconsistent inclusive bounds")
        category = _closed_value(row["category"], field=f"{label}.category", allowed=_CATEGORIES)
        scope = _closed_value(row["scope"], field=f"{label}.scope", allowed=_SCOPES)
        zero_semantics = _closed_value(row["zero_semantics"], field=f"{label}.zero_semantics", allowed=_ZERO_SEMANTICS)
        if category in _CAP_CATEGORIES:
            if kind != "integer" or unit != "count" or zero_semantics != "disable" or minimum != 0:
                _fail(
                    "invalid_cap_contract",
                    f"control {control_id!r} must be integer/count with minimum 0 and zero_semantics='disable'",
                )
        elif zero_semantics == "forbidden" and minimum <= 0 <= maximum:
            _fail("invalid_zero_semantics", f"control {control_id!r} permits a forbidden zero")
        rationale = _bounded_text(row["rationale"], field=f"{label}.rationale")
        tolerance = _bounded_text(row["tolerance_rationale"], field=f"{label}.tolerance_rationale")
        migration_state = _closed_value(
            row["migration_state"], field=f"{label}.migration_state", allowed=_MIGRATION_STATES
        )
        observation_key = row.get("capacity_observation_key")
        if observation_key is not None:
            observation_key = _bounded_text(
                observation_key,
                field=f"{label}.capacity_observation_key",
                maximum=MAX_IDENTIFIER_LENGTH,
            )
            if category not in _CAP_CATEGORIES:
                _fail("invalid_capacity_binding", f"control {control_id!r} cannot consume capacity evidence")
        material = {
            "id": control_id,
            "environment_schema_ref": schema_ref,
            "environment_name": binding.environment_name,
            "environment_schema_version": binding.version,
            "numeric_kind": kind,
            "unit": unit,
            "relaxed_default": str(default),
            "minimum": str(minimum),
            "maximum": str(maximum),
            "category": category,
            "scope": scope,
            "zero_semantics": zero_semantics,
            "rationale": rationale,
            "tolerance_rationale": tolerance,
            "migration_state": migration_state,
            "capacity_observation_key": observation_key,
        }
        definitions[control_id] = OperationalControlDefinition(
            control_id=control_id,
            environment_schema_ref=schema_ref,
            environment_name=binding.environment_name,
            environment_schema_version=binding.version,
            numeric_kind=kind,
            unit=unit,
            relaxed_default=default,
            minimum=minimum,
            maximum=maximum,
            category=category,
            scope=scope,
            zero_semantics=zero_semantics,
            rationale=rationale,
            tolerance_rationale=tolerance,
            migration_state=migration_state,
            capacity_observation_key=observation_key,
            definition_digest=_canonical_digest(material),
        )
        used_schema_refs.add(schema_ref)
        used_environment_names.add(binding.environment_name)

    invariants: list[OperationalControlInvariant] = []
    invariant_ids: set[str] = set()
    endpoint_pairs: set[frozenset[str]] = set()
    for index, row in enumerate(invariant_rows):
        label = f"invariants[{index}]"
        keys = set(row)
        if not keys >= _REQUIRED_INVARIANT_KEYS or keys - _INVARIANT_KEYS:
            _fail("invalid_invariant_shape", f"{label} has missing or unknown fields")
        invariant_id = _bounded_text(row["id"], field=f"{label}.id", maximum=MAX_IDENTIFIER_LENGTH)
        if not _INVARIANT_ID_RE.fullmatch(invariant_id) or invariant_id in invariant_ids:
            _fail("duplicate_invariant", f"invariant {invariant_id!r} is invalid or duplicated")
        left = _bounded_text(row["left"], field=f"{label}.left", maximum=MAX_IDENTIFIER_LENGTH)
        right = _bounded_text(row["right"], field=f"{label}.right", maximum=MAX_IDENTIFIER_LENGTH)
        if left == right or left not in definitions or right not in definitions:
            _fail("invalid_invariant_endpoint", f"invariant {invariant_id!r} has missing or identical endpoints")
        pair = frozenset({left, right})
        if pair in endpoint_pairs:
            _fail("contradictory_invariant", f"controls {sorted(pair)} have more than one declared relation")
        left_definition = definitions[left]
        right_definition = definitions[right]
        if (left_definition.numeric_kind, left_definition.unit) != (
            right_definition.numeric_kind,
            right_definition.unit,
        ):
            _fail("incompatible_invariant", f"invariant {invariant_id!r} mixes kinds or units")
        operator = _closed_value(row["operator"], field=f"{label}.operator", allowed=_OPERATORS)
        margin = _numeric(
            row.get("margin", 0),
            kind=left_definition.numeric_kind,
            field=f"{label}.margin",
        )
        if margin < 0 or (operator == "eq" and margin != 0):
            _fail("invalid_invariant_margin", f"invariant {invariant_id!r} has an invalid margin")
        invariants.append(
            OperationalControlInvariant(
                invariant_id=invariant_id,
                left_control_id=left,
                operator=operator,
                right_control_id=right,
                margin=margin,
            )
        )
        invariant_ids.add(invariant_id)
        endpoint_pairs.add(pair)

    return OperationalControlCatalog(
        schema_version=schema_version,
        live_value_authority=authority,
        definitions=MappingProxyType(definitions),
        invariants=tuple(invariants),
        catalog_sha256=_sha256(payload),
        source_kind=source_kind,
        source_reference=source_reference,
    )


def load_operational_control_catalog(
    project_root: Path,
    environment_bindings: Iterable[OperationalControlEnvironmentBinding] = (),
) -> OperationalControlCatalog:
    """Load the canonical production catalog without consulting live values."""

    root = Path(project_root).resolve(strict=True)
    path = root / CATALOG_RELATIVE_PATH
    payload = _regular_file_bytes(path, root=root, maximum=MAX_CATALOG_BYTES, label="operational-control catalog")
    return _catalog_from_bytes(
        payload,
        source_kind="production_catalog",
        source_reference=CATALOG_RELATIVE_PATH.as_posix(),
        bindings=environment_bindings,
        allow_test_bindings=False,
    )


def load_test_operational_control_catalog(
    path: Path,
    environment_bindings: Iterable[OperationalControlEnvironmentBinding],
) -> OperationalControlCatalog:
    """Load a bounded explicit test fixture; never labels it as production."""

    fixture = Path(path)
    payload = _regular_file_bytes(fixture, root=None, maximum=MAX_CATALOG_BYTES, label="test catalog")
    return _catalog_from_bytes(
        payload,
        source_kind="test_fixture",
        source_reference=str(fixture),
        bindings=environment_bindings,
        allow_test_bindings=True,
    )


def _active_environment_names(catalog: OperationalControlCatalog) -> set[str]:
    return {
        definition.environment_name
        for definition in catalog.definitions.values()
        if definition.migration_state == "active"
    }


def _snapshot(
    *,
    catalog: OperationalControlCatalog,
    source_kind: str,
    source_reference: str,
    supplied_values: Mapping[str, str],
) -> PlatformControlEnvironmentSnapshot:
    wanted = _active_environment_names(catalog)
    retained: dict[str, str] = {}
    for name, value in supplied_values.items():
        if name not in wanted:
            continue
        if not isinstance(value, str):
            _fail("invalid_environment_value", f"{name} must be a string")
        if len(value) > MAX_ENVIRONMENT_VALUE_LENGTH:
            _fail("resource_bound", f"{name} exceeds the environment-value bound")
        if name in retained:
            _fail("duplicate_environment_value", f"{name} is duplicated")
        retained[name] = value
    material = {
        "catalog_sha256": catalog.catalog_sha256,
        "source_kind": source_kind,
        "source_reference": source_reference,
        "values": sorted(retained.items()),
    }
    return PlatformControlEnvironmentSnapshot(
        source_kind=source_kind,
        source_reference=source_reference,
        catalog_sha256=catalog.catalog_sha256,
        values=MappingProxyType(retained),
        snapshot_digest=_canonical_digest(material),
    )


def _declared_environment_values(payload: bytes, names: set[str]) -> dict[str, str]:
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        _fail("malformed_environment", f".env.local is not strict UTF-8: {exc}")
    lines = text.splitlines()
    if len(lines) > MAX_ENVIRONMENT_LINES:
        _fail("resource_bound", f".env.local exceeds {MAX_ENVIRONMENT_LINES} lines")
    selected: dict[str, str] = {}
    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        candidate = stripped[7:].lstrip() if stripped.startswith("export ") else stripped
        if "=" not in candidate:
            possible_name = candidate.split(maxsplit=1)[0]
            if possible_name in names:
                _fail("malformed_environment", f"declared key {possible_name} lacks '=' on line {line_number}")
            continue
        raw_name, raw_value = candidate.split("=", 1)
        name = raw_name.strip()
        if name not in names:
            continue
        if name in selected:
            _fail("duplicate_environment_value", f"declared key {name} is duplicated")
        value = raw_value.strip()
        if len(value) > MAX_ENVIRONMENT_VALUE_LENGTH:
            _fail("resource_bound", f"{name} exceeds the environment-value bound")
        selected[name] = value
    return selected


def load_platform_control_environment_snapshot(
    project_root: Path,
    catalog: OperationalControlCatalog,
) -> PlatformControlEnvironmentSnapshot:
    """Read root ``.env.local`` once and retain only active declared keys."""

    if catalog.source_kind != "production_catalog":
        _fail("catalog_source_mismatch", "production environment reads require the production catalog")
    root = Path(project_root).resolve(strict=True)
    catalog_path = root / CATALOG_RELATIVE_PATH
    current_catalog = _regular_file_bytes(
        catalog_path,
        root=root,
        maximum=MAX_CATALOG_BYTES,
        label="operational-control catalog",
    )
    if _sha256(current_catalog) != catalog.catalog_sha256:
        _fail("stale_catalog", "catalog bytes changed before the environment snapshot")
    env_path = root / ".env.local"
    payload = _regular_file_bytes(
        env_path,
        root=root,
        maximum=MAX_ENVIRONMENT_BYTES,
        label="platform .env.local",
    )
    selected = _declared_environment_values(payload, _active_environment_names(catalog))
    return _snapshot(
        catalog=catalog,
        source_kind="platform_env_local",
        source_reference=".env.local",
        supplied_values=selected,
    )


def create_test_control_environment_snapshot(
    catalog: OperationalControlCatalog,
    values: Mapping[str, str],
    *,
    snapshot_id: str = "fixture",
) -> PlatformControlEnvironmentSnapshot:
    """Create an explicit test-only snapshot without process-environment access."""

    if catalog.source_kind != "test_fixture":
        _fail("catalog_source_mismatch", "test snapshots require a test fixture catalog")
    reference = _bounded_text(snapshot_id, field="snapshot_id", maximum=MAX_IDENTIFIER_LENGTH)
    return _snapshot(
        catalog=catalog,
        source_kind="test_fixture",
        source_reference=reference,
        supplied_values=values,
    )


def _evaluate_invariant(
    invariant: OperationalControlInvariant,
    resolved: Mapping[str, ResolvedOperationalControl],
) -> None:
    left = resolved[invariant.left_control_id].effective_value
    right = resolved[invariant.right_control_id].effective_value
    margin = invariant.margin
    if invariant.operator == "lt":
        passes = left + margin < right
    elif invariant.operator == "lte":
        passes = left + margin <= right
    elif invariant.operator == "eq":
        passes = left == right
    elif invariant.operator == "gte":
        passes = left >= right + margin
    else:
        passes = left > right + margin
    if not passes:
        _fail(
            "invariant_violation",
            f"{invariant.invariant_id} failed for {invariant.left_control_id} and {invariant.right_control_id}",
        )


def resolve_operational_controls(
    catalog: OperationalControlCatalog,
    environment_snapshot: PlatformControlEnvironmentSnapshot,
    control_ids: Sequence[str] | None = None,
    *,
    capacity_observations: Mapping[str, int | None] | None = None,
) -> Mapping[str, ResolvedOperationalControl]:
    """Resolve one closed control set from one immutable catalog/snapshot pair."""

    if environment_snapshot.catalog_sha256 != catalog.catalog_sha256:
        _fail("split_snapshot", "environment snapshot belongs to a different catalog")
    active = {
        control_id: definition
        for control_id, definition in catalog.definitions.items()
        if definition.migration_state == "active"
    }
    requested = list(active) if control_ids is None else list(control_ids)
    if len(requested) != len(set(requested)):
        _fail("duplicate_control_request", "requested control ids must be unique")
    unknown = sorted(set(requested) - set(active))
    if unknown:
        _fail("unknown_control", f"unknown or inactive controls: {unknown}")
    requested_set = set(requested)
    applicable_invariants: list[OperationalControlInvariant] = []
    for invariant in catalog.invariants:
        endpoint_count = len({invariant.left_control_id, invariant.right_control_id} & requested_set)
        if endpoint_count == 1:
            _fail("split_invariant_request", f"{invariant.invariant_id} endpoints must resolve together")
        if endpoint_count == 2:
            applicable_invariants.append(invariant)

    observations = dict(capacity_observations or {})
    expected_observations = {
        definition.capacity_observation_key
        for control_id, definition in active.items()
        if control_id in requested_set and definition.capacity_observation_key is not None
    }
    unexpected_observations = set(observations) - expected_observations
    if unexpected_observations:
        _fail("unknown_capacity_observation", f"unexpected capacity observations: {sorted(unexpected_observations)}")

    resolved: dict[str, ResolvedOperationalControl] = {}
    for control_id in requested:
        definition = active[control_id]
        if definition.environment_name in environment_snapshot.values:
            raw_value: object = environment_snapshot.values[definition.environment_name]
            if not raw_value.strip():
                _fail("invalid_override", f"present override {definition.environment_name} is empty")
            source = (
                "platform_env_local" if environment_snapshot.source_kind == "platform_env_local" else "test_fixture"
            )
        else:
            raw_value = definition.relaxed_default
            source = "catalog_relaxed_default"
        value = _numeric(raw_value, kind=definition.numeric_kind, field=definition.environment_name)
        if not definition.minimum <= value <= definition.maximum:
            _fail("out_of_bounds", f"{control_id}={value} is outside inclusive bounds")
        effective_value = value
        observation_key = definition.capacity_observation_key
        if observation_key is not None:
            observed = observations.get(observation_key)
            if isinstance(observed, bool) or not isinstance(observed, int) or observed < 0:
                _fail("unknown_capacity", f"{control_id} requires non-negative capacity {observation_key!r}")
            effective_value = min(value, observed)
        is_disabled = definition.zero_semantics == "disable" and effective_value == 0
        resolved[control_id] = ResolvedOperationalControl(
            control_id=control_id,
            value=value,
            effective_value=effective_value,
            unit=definition.unit,
            source=source,
            is_disabled=is_disabled,
            catalog_schema_version=catalog.schema_version,
            catalog_sha256=catalog.catalog_sha256,
            definition_digest=definition.definition_digest,
            environment_snapshot_digest=environment_snapshot.snapshot_digest,
            environment_source_kind=environment_snapshot.source_kind,
            capacity_observation_key=observation_key,
        )
    for invariant in applicable_invariants:
        _evaluate_invariant(invariant, resolved)
    return MappingProxyType(resolved)


def resolve_operational_control(
    catalog: OperationalControlCatalog,
    environment_snapshot: PlatformControlEnvironmentSnapshot,
    control_id: str,
    *,
    capacity_observations: Mapping[str, int | None] | None = None,
) -> ResolvedOperationalControl:
    """Resolve one control, refusing to split an invariant-coupled pair."""

    return resolve_operational_controls(
        catalog,
        environment_snapshot,
        [control_id],
        capacity_observations=capacity_observations,
    )[control_id]
