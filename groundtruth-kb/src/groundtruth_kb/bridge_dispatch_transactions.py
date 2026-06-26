"""Governed bridge dispatcher config transaction helpers."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge_dispatch_config import DISPATCH_CONFIG_RELATIVE_PATH

TRANSACTION_STATE_RELATIVE_PATH = Path(".gtkb-state") / "bridge-dispatch-config-transactions"

VALID_ROLES = frozenset({"prime-builder", "loyal-opposition"})
VALID_STATUSES = frozenset({"NEW", "REVISED", "GO", "NO-GO", "VERIFIED"})
VALID_PREFERENCES = frozenset({"quality", "cost", "availability", "reviewer_precedence", "harness_id", "id"})
HARNESS_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
RULE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")

TOP_LEVEL_ORDER = ("schema_version", "selection_order")
HARNESS_FIELD_ORDER = (
    "description",
    "can_receive_dispatch",
    "can_fire_events",
    "dispatch_cost",
    "dispatch_quality",
    "dispatch_availability",
    "max_items",
    "tags",
)
RULE_FIELD_ORDER = (
    "id",
    "required_roles",
    "blocked_roles",
    "statuses",
    "session_subjects",
    "activities",
    "prefer",
)


class DispatchConfigTransactionError(ValueError):
    """Raised when a dispatcher config transaction cannot be applied safely."""


@dataclass(frozen=True)
class DispatchConfigTransactionResult:
    """Result from a dispatcher config transaction."""

    transaction: str
    status: str
    mutated: bool
    config_path: Path
    audit_path: Path | None = None
    pending_path: Path | None = None
    message: str = ""
    config: dict[str, Any] | None = None

    def to_json_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "transaction": self.transaction,
            "status": self.status,
            "mutated": self.mutated,
            "config_path": str(self.config_path),
            "message": self.message,
        }
        if self.audit_path is not None:
            payload["audit_path"] = str(self.audit_path)
        if self.pending_path is not None:
            payload["pending_path"] = str(self.pending_path)
        if self.config is not None:
            payload["config"] = self.config
        return payload


def set_eligibility(
    project_root: Path,
    harness_id: str,
    *,
    can_receive_dispatch: bool | None,
    can_fire_events: bool | None,
    dry_run: bool = False,
    defer_to_next_session: bool = False,
) -> DispatchConfigTransactionResult:
    def mutate(raw: dict[str, Any]) -> dict[str, Any]:
        harness = _require_harness(raw, harness_id)
        if can_receive_dispatch is None and can_fire_events is None:
            raise DispatchConfigTransactionError("at least one eligibility field must be provided")
        if can_receive_dispatch is not None:
            harness["can_receive_dispatch"] = bool(can_receive_dispatch)
        if can_fire_events is not None:
            harness["can_fire_events"] = bool(can_fire_events)
        return raw

    return _apply_transaction(
        project_root,
        "set-eligibility",
        {"harness_id": _validate_harness_id(harness_id)},
        mutate,
        dry_run=dry_run,
        defer_to_next_session=defer_to_next_session,
    )


def set_weights(
    project_root: Path,
    harness_id: str,
    *,
    dispatch_quality: float | None,
    dispatch_cost: float | None,
    dispatch_availability: float | None,
    dry_run: bool = False,
    defer_to_next_session: bool = False,
) -> DispatchConfigTransactionResult:
    def mutate(raw: dict[str, Any]) -> dict[str, Any]:
        harness = _require_harness(raw, harness_id)
        if dispatch_quality is None and dispatch_cost is None and dispatch_availability is None:
            raise DispatchConfigTransactionError("at least one weight field must be provided")
        if dispatch_quality is not None:
            harness["dispatch_quality"] = _validate_score("dispatch_quality", dispatch_quality)
        if dispatch_cost is not None:
            harness["dispatch_cost"] = _validate_score("dispatch_cost", dispatch_cost)
        if dispatch_availability is not None:
            harness["dispatch_availability"] = _validate_score("dispatch_availability", dispatch_availability)
        return raw

    return _apply_transaction(
        project_root,
        "set-weights",
        {"harness_id": _validate_harness_id(harness_id)},
        mutate,
        dry_run=dry_run,
        defer_to_next_session=defer_to_next_session,
    )


def set_caps(
    project_root: Path,
    harness_id: str,
    *,
    max_items: int,
    dry_run: bool = False,
    defer_to_next_session: bool = False,
) -> DispatchConfigTransactionResult:
    def mutate(raw: dict[str, Any]) -> dict[str, Any]:
        harness = _require_harness(raw, harness_id)
        harness["max_items"] = _validate_max_items(max_items)
        return raw

    return _apply_transaction(
        project_root,
        "set-caps",
        {"harness_id": _validate_harness_id(harness_id), "max_items": max_items},
        mutate,
        dry_run=dry_run,
        defer_to_next_session=defer_to_next_session,
    )


def set_rule(
    project_root: Path,
    rule_id: str,
    *,
    required_roles: tuple[str, ...] | None = None,
    blocked_roles: tuple[str, ...] | None = None,
    statuses: tuple[str, ...] | None = None,
    session_subjects: tuple[str, ...] | None = None,
    activities: tuple[str, ...] | None = None,
    prefer: tuple[str, ...] | None = None,
    dry_run: bool = False,
    defer_to_next_session: bool = False,
) -> DispatchConfigTransactionResult:
    def mutate(raw: dict[str, Any]) -> dict[str, Any]:
        rule = _require_rule(raw, rule_id)
        changed = False
        if required_roles is not None:
            rule["required_roles"] = list(_validate_roles(required_roles))
            changed = True
        if blocked_roles is not None:
            rule["blocked_roles"] = list(_validate_roles(blocked_roles))
            changed = True
        if statuses is not None:
            rule["statuses"] = list(_validate_statuses(statuses))
            changed = True
        if session_subjects is not None:
            rule["session_subjects"] = list(_validate_nonempty_strings("session_subjects", session_subjects))
            changed = True
        if activities is not None:
            rule["activities"] = list(_validate_nonempty_strings("activities", activities))
            changed = True
        if prefer is not None:
            rule["prefer"] = list(_validate_preferences(prefer))
            changed = True
        if not changed:
            raise DispatchConfigTransactionError("at least one rule field must be provided")
        return raw

    return _apply_transaction(
        project_root,
        "set-rule",
        {"rule_id": _validate_rule_id(rule_id)},
        mutate,
        dry_run=dry_run,
        defer_to_next_session=defer_to_next_session,
    )


def add_harness(
    project_root: Path,
    harness_id: str,
    *,
    description: str | None = None,
    can_receive_dispatch: bool | None = None,
    can_fire_events: bool | None = None,
    dispatch_quality: float | None = None,
    dispatch_cost: float | None = None,
    dispatch_availability: float | None = None,
    max_items: int | None = None,
    tags: tuple[str, ...] = (),
    dry_run: bool = False,
    defer_to_next_session: bool = False,
) -> DispatchConfigTransactionResult:
    def mutate(raw: dict[str, Any]) -> dict[str, Any]:
        harnesses = _harnesses(raw)
        validated_id = _validate_harness_id(harness_id)
        if validated_id in harnesses:
            raise DispatchConfigTransactionError(f"harness {validated_id!r} already exists")
        row: dict[str, Any] = {}
        if description:
            row["description"] = description
        if can_receive_dispatch is not None:
            row["can_receive_dispatch"] = bool(can_receive_dispatch)
        if can_fire_events is not None:
            row["can_fire_events"] = bool(can_fire_events)
        if dispatch_cost is not None:
            row["dispatch_cost"] = _validate_score("dispatch_cost", dispatch_cost)
        if dispatch_quality is not None:
            row["dispatch_quality"] = _validate_score("dispatch_quality", dispatch_quality)
        if dispatch_availability is not None:
            row["dispatch_availability"] = _validate_score("dispatch_availability", dispatch_availability)
        if max_items is not None:
            row["max_items"] = _validate_max_items(max_items)
        if tags:
            row["tags"] = list(_validate_nonempty_strings("tags", tags))
        harnesses[validated_id] = row
        return raw

    return _apply_transaction(
        project_root,
        "add-harness",
        {"harness_id": _validate_harness_id(harness_id)},
        mutate,
        dry_run=dry_run,
        defer_to_next_session=defer_to_next_session,
    )


def remove_harness(
    project_root: Path,
    harness_id: str,
    *,
    dry_run: bool = False,
    defer_to_next_session: bool = False,
) -> DispatchConfigTransactionResult:
    def mutate(raw: dict[str, Any]) -> dict[str, Any]:
        harnesses = _harnesses(raw)
        validated_id = _validate_harness_id(harness_id)
        if validated_id not in harnesses:
            raise DispatchConfigTransactionError(f"harness {validated_id!r} does not exist")
        del harnesses[validated_id]
        return raw

    return _apply_transaction(
        project_root,
        "remove-harness",
        {"harness_id": _validate_harness_id(harness_id)},
        mutate,
        dry_run=dry_run,
        defer_to_next_session=defer_to_next_session,
    )


def _apply_transaction(
    project_root: Path,
    transaction: str,
    parameters: dict[str, Any],
    mutate: Any,
    *,
    dry_run: bool,
    defer_to_next_session: bool,
) -> DispatchConfigTransactionResult:
    if dry_run and defer_to_next_session:
        raise DispatchConfigTransactionError("--dry-run and --defer-to-next-session are mutually exclusive")
    root = project_root.resolve()
    config_path = root / DISPATCH_CONFIG_RELATIVE_PATH
    before_bytes = _read_config_bytes(config_path)
    raw = _parse_config(before_bytes, config_path)
    updated = mutate(_clone(raw))
    rendered = _render_dispatch_config(updated).encode("utf-8")
    before_hash = _hash_bytes(before_bytes)
    after_hash = _hash_bytes(rendered)
    if dry_run:
        return DispatchConfigTransactionResult(
            transaction=transaction,
            status="dry_run",
            mutated=False,
            config_path=config_path,
            message=f"{transaction}: dry run; no files written",
            config=updated,
        )

    state_dir = root / TRANSACTION_STATE_RELATIVE_PATH
    if defer_to_next_session:
        pending_path = state_dir / "pending.jsonl"
        audit_path = state_dir / "audit.jsonl"
        record = _record(transaction, parameters, before_hash=before_hash, after_hash=after_hash, status="deferred")
        _append_jsonl(pending_path, record)
        _append_jsonl(audit_path, record)
        return DispatchConfigTransactionResult(
            transaction=transaction,
            status="deferred",
            mutated=False,
            config_path=config_path,
            audit_path=audit_path,
            pending_path=pending_path,
            message=f"{transaction}: deferred to next session; config unchanged",
            config=updated,
        )

    config_path.write_bytes(rendered)
    audit_path = state_dir / "audit.jsonl"
    _append_jsonl(
        audit_path, _record(transaction, parameters, before_hash=before_hash, after_hash=after_hash, status="applied")
    )
    # WI-4820: the cross-harness trigger resolves dispatchability from the static
    # harness-registry projection, NOT from config/dispatcher/rules.toml. The
    # projection generator already merges this overlay, so regenerate it now as a
    # write-through; otherwise the trigger keeps reading a stale projection and
    # `set-eligibility` (and the other overlay mutators) is a false-green. This
    # runs only on the applied path (dry_run / defer_to_next_session return
    # earlier), and fails soft so the rules.toml write is never half-applied.
    regen_message = _regenerate_harness_projection(root)
    message = f"{transaction}: applied"
    if regen_message:
        message = f"{message}; {regen_message}"
    return DispatchConfigTransactionResult(
        transaction=transaction,
        status="applied",
        mutated=True,
        config_path=config_path,
        audit_path=audit_path,
        message=message,
        config=updated,
    )


def _regenerate_harness_projection(root: Path) -> str:
    """Write-through the dispatcher-config overlay into the harness-registry projection.

    The cross-harness trigger resolves dispatchability from the static
    ``harness-state/harness-registry.json`` projection, not from
    ``config/dispatcher/rules.toml``. ``generate_harness_projection`` already
    merges the rules.toml overlay per harness, so regenerating here keeps the
    trigger's source consistent with the just-applied config change (WI-4820).

    Fails soft: on any error the rules.toml write is preserved and a warning
    string is returned for the caller to surface, rather than raising and leaving
    the transaction half-applied (graceful degradation per the GO review notes).
    """
    try:
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.harness_projection import generate_harness_projection

        db = KnowledgeDB(db_path=root / "groundtruth.db")
        generate_harness_projection(db, root)
        return "harness-registry projection regenerated"
    except Exception as exc:  # intentional-catch: regen must never half-fail the config write
        return (
            "WARNING: harness-registry projection regen failed "
            f"({type(exc).__name__}: {exc}); rules.toml written but the dispatch "
            "trigger may read a stale projection until the next regeneration"
        )


def _read_config_bytes(path: Path) -> bytes:
    if not path.exists():
        raise DispatchConfigTransactionError(f"dispatch config does not exist: {path}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise DispatchConfigTransactionError(f"unable to read dispatch config: {exc}") from exc


def _parse_config(data: bytes, path: Path) -> dict[str, Any]:
    try:
        raw = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise DispatchConfigTransactionError(f"unable to parse {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise DispatchConfigTransactionError("top-level dispatcher config must be a TOML table")
    _harnesses(raw)
    _rules(raw)
    return raw


def _clone(raw: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(raw))


def _harnesses(raw: dict[str, Any]) -> dict[str, Any]:
    table = raw.setdefault("harnesses", {})
    if not isinstance(table, dict):
        raise DispatchConfigTransactionError("harnesses must be a TOML table")
    for harness_id, row in table.items():
        _validate_harness_id(str(harness_id))
        if not isinstance(row, dict):
            raise DispatchConfigTransactionError(f"harness {harness_id!r} must be a TOML table")
    return table


def _rules(raw: dict[str, Any]) -> list[dict[str, Any]]:
    rules = raw.setdefault("rules", [])
    if not isinstance(rules, list) or not all(isinstance(row, dict) for row in rules):
        raise DispatchConfigTransactionError("rules must be an array of TOML tables")
    for row in rules:
        _validate_rule_id(str(row.get("id") or ""))
    return rules


def _require_harness(raw: dict[str, Any], harness_id: str) -> dict[str, Any]:
    validated_id = _validate_harness_id(harness_id)
    harnesses = _harnesses(raw)
    if validated_id not in harnesses:
        raise DispatchConfigTransactionError(f"harness {validated_id!r} does not exist")
    return harnesses[validated_id]


def _require_rule(raw: dict[str, Any], rule_id: str) -> dict[str, Any]:
    validated_id = _validate_rule_id(rule_id)
    for row in _rules(raw):
        if str(row.get("id") or "") == validated_id:
            return row
    raise DispatchConfigTransactionError(f"rule {validated_id!r} does not exist")


def _validate_harness_id(value: str) -> str:
    candidate = str(value or "").strip()
    if not candidate or HARNESS_ID_RE.fullmatch(candidate) is None:
        raise DispatchConfigTransactionError(f"invalid harness id: {value!r}")
    return candidate


def _validate_rule_id(value: str) -> str:
    candidate = str(value or "").strip()
    if not candidate or RULE_ID_RE.fullmatch(candidate) is None:
        raise DispatchConfigTransactionError(f"invalid rule id: {value!r}")
    return candidate


def _validate_score(name: str, value: float) -> float | int:
    score = float(value)
    if score < 0 or score > 100:
        raise DispatchConfigTransactionError(f"{name} must be between 0 and 100")
    return int(score) if score.is_integer() else score


def _validate_max_items(value: int) -> int:
    if int(value) < 1:
        raise DispatchConfigTransactionError("max_items must be at least 1")
    return int(value)


def _validate_roles(values: tuple[str, ...]) -> tuple[str, ...]:
    roles = _validate_nonempty_strings("roles", values)
    invalid = [role for role in roles if role not in VALID_ROLES]
    if invalid:
        raise DispatchConfigTransactionError(f"invalid role(s): {', '.join(invalid)}")
    return roles


def _validate_statuses(values: tuple[str, ...]) -> tuple[str, ...]:
    statuses = tuple(value.upper() for value in _validate_nonempty_strings("statuses", values))
    invalid = [status for status in statuses if status not in VALID_STATUSES]
    if invalid:
        raise DispatchConfigTransactionError(f"invalid status(es): {', '.join(invalid)}")
    return statuses


def _validate_preferences(values: tuple[str, ...]) -> tuple[str, ...]:
    preferences = _validate_nonempty_strings("prefer", values)
    invalid = [preference for preference in preferences if preference not in VALID_PREFERENCES]
    if invalid:
        raise DispatchConfigTransactionError(f"invalid preference(s): {', '.join(invalid)}")
    return preferences


def _validate_nonempty_strings(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    cleaned = tuple(str(value).strip() for value in values if str(value).strip())
    if not cleaned:
        raise DispatchConfigTransactionError(f"{name} must include at least one value")
    return cleaned


def _render_dispatch_config(raw: dict[str, Any]) -> str:
    lines: list[str] = []
    for key in TOP_LEVEL_ORDER:
        if key in raw:
            lines.append(f"{key} = {_toml_value(raw[key])}")
    for key in sorted(k for k in raw if k not in {*TOP_LEVEL_ORDER, "harnesses", "rules"}):
        value = raw[key]
        if isinstance(value, dict):
            raise DispatchConfigTransactionError(f"unsupported top-level table: {key}")
        lines.append(f"{key} = {_toml_value(value)}")
    rules = _rules(raw)
    if not rules:
        lines.append("rules = []")
    harnesses = _harnesses(raw)
    for harness_id in sorted(harnesses):
        lines.extend(["", f"[harnesses.{harness_id}]"])
        lines.extend(_render_table(harnesses[harness_id], HARNESS_FIELD_ORDER))
    for rule in rules:
        lines.extend(["", "[[rules]]"])
        lines.extend(_render_table(rule, RULE_FIELD_ORDER))
    return "\n".join(lines).rstrip() + "\n"


def _render_table(raw: dict[str, Any], preferred_order: tuple[str, ...]) -> list[str]:
    rendered: list[str] = []
    for key in preferred_order:
        if key in raw:
            rendered.append(f"{key} = {_toml_value(raw[key])}")
    for key in sorted(k for k in raw if k not in preferred_order):
        value = raw[key]
        if isinstance(value, dict):
            raise DispatchConfigTransactionError(f"unsupported nested table field: {key}")
        rendered.append(f"{key} = {_toml_value(value)}")
    return rendered


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    raise DispatchConfigTransactionError(f"unsupported TOML value: {value!r}")


def _record(
    transaction: str,
    parameters: dict[str, Any],
    *,
    before_hash: str,
    after_hash: str,
    status: str,
) -> dict[str, Any]:
    return {
        "after_hash": after_hash,
        "before_hash": before_hash,
        "parameters": parameters,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "transaction": transaction,
    }


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def _hash_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()
