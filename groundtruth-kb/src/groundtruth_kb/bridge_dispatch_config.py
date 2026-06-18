"""Bridge dispatch configuration, status, and ranking helpers."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge_dispatch_rules import DispatchContext, DispatchRule

DISPATCH_CONFIG_RELATIVE_PATH = Path("config") / "dispatcher" / "rules.toml"
DISPATCH_STATE_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller" / "dispatch-state.json"

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
DISPATCH_ROLES = (ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION)

DEFAULT_SELECTION_ORDER = ("availability", "cost", "quality", "reviewer_precedence", "harness_id")
RUNTIME_FAILURE_RESULTS = {
    "provider_failure_backoff_active",
    "work_intent_acquire_failed",
    "max_turn_exhaustion",
    "no_verdict_produced",
}
RUNTIME_FAILURE_CLASSES = {
    "max_turn_exhaustion",
    "provider_failure",
    "provider_failure_backoff_active",
    "work_intent_acquire_failed",
}


@dataclass(frozen=True)
class HarnessDispatchConfig:
    """Per-harness dispatch overlay from the dispatcher config."""

    harness_id: str
    can_receive_dispatch: bool | None = None
    can_fire_events: bool | None = None
    dispatch_cost: float | None = None
    dispatch_quality: float | None = None
    dispatch_availability: float | None = None
    max_items: int | None = None
    tags: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, harness_id: str, raw: dict[str, Any]) -> HarnessDispatchConfig:
        return cls(
            harness_id=harness_id,
            can_receive_dispatch=_optional_bool(raw.get("can_receive_dispatch")),
            can_fire_events=_optional_bool(raw.get("can_fire_events")),
            dispatch_cost=_optional_float(raw.get("dispatch_cost", raw.get("cost"))),
            dispatch_quality=_optional_float(raw.get("dispatch_quality", raw.get("quality"))),
            dispatch_availability=_optional_float(raw.get("dispatch_availability", raw.get("availability"))),
            max_items=_optional_int(raw.get("max_items")),
            tags=_string_tuple(raw.get("tags")),
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "harness_id": self.harness_id,
            "can_receive_dispatch": self.can_receive_dispatch,
            "can_fire_events": self.can_fire_events,
            "dispatch_cost": self.dispatch_cost,
            "dispatch_quality": self.dispatch_quality,
            "dispatch_availability": self.dispatch_availability,
            "max_items": self.max_items,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class BridgeDispatchConfig:
    """Parsed dispatcher configuration."""

    path: Path
    exists: bool
    schema_version: int
    selection_order: tuple[str, ...] = DEFAULT_SELECTION_ORDER
    harnesses: dict[str, HarnessDispatchConfig] = field(default_factory=dict)
    rules: tuple[DispatchRule, ...] = ()
    errors: tuple[str, ...] = ()

    def overlay_for(self, harness_id: str) -> HarnessDispatchConfig | None:
        return self.harnesses.get(harness_id)

    def matching_rules(self, context: DispatchContext) -> tuple[DispatchRule, ...]:
        matches = tuple(rule for rule in self.rules if rule.matches(context))
        if matches:
            return matches
        if context.status or context.session_subject or context.activity:
            return ()
        return tuple(rule for rule in self.rules if _role_only_match(rule, context.required_role))

    def selection_order_for(self, context: DispatchContext) -> tuple[str, ...]:
        for rule in self.matching_rules(context):
            if rule.prefer:
                return rule.prefer
        return self.selection_order

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "schema_version": self.schema_version,
            "selection_order": list(self.selection_order),
            "harnesses": {hid: cfg.to_json_dict() for hid, cfg in sorted(self.harnesses.items())},
            "rules": [rule.to_json_dict() for rule in self.rules],
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class BridgeDispatchStatus:
    """Current dispatch topology and health view."""

    config: BridgeDispatchConfig
    harnesses: tuple[dict[str, Any], ...]
    selected_by_role: dict[str, list[dict[str, Any]]]
    health_status: str
    health_findings: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.to_json_dict(),
            "harnesses": list(self.harnesses),
            "selected_by_role": self.selected_by_role,
            "health_status": self.health_status,
            "health_findings": list(self.health_findings),
        }


def load_bridge_dispatch_config(project_root: Path) -> BridgeDispatchConfig:
    """Read ``config/dispatcher/rules.toml`` and return a tolerant config object."""
    path = project_root.resolve() / DISPATCH_CONFIG_RELATIVE_PATH
    if not path.exists():
        return BridgeDispatchConfig(path=path, exists=False, schema_version=1, errors=("dispatch config missing",))
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return BridgeDispatchConfig(path=path, exists=True, schema_version=1, errors=(str(exc),))
    if not isinstance(raw, dict):
        return BridgeDispatchConfig(path=path, exists=True, schema_version=1, errors=("top-level TOML is not a table",))

    harness_table = raw.get("harnesses", {})
    harnesses: dict[str, HarnessDispatchConfig] = {}
    if isinstance(harness_table, dict):
        for harness_id, row in harness_table.items():
            if isinstance(row, dict):
                harnesses[str(harness_id)] = HarnessDispatchConfig.from_mapping(str(harness_id), row)

    rules_raw = raw.get("rules", [])
    rules: list[DispatchRule] = []
    if isinstance(rules_raw, list):
        for row in rules_raw:
            if isinstance(row, dict):
                rules.append(DispatchRule.from_mapping(row))

    schema_version = _optional_int(raw.get("schema_version")) or 1
    selection_order = _string_tuple(raw.get("selection_order")) or DEFAULT_SELECTION_ORDER
    return BridgeDispatchConfig(
        path=path,
        exists=True,
        schema_version=schema_version,
        selection_order=selection_order,
        harnesses=harnesses,
        rules=tuple(rules),
    )


def apply_dispatch_config_to_record(
    record: dict[str, Any],
    config: BridgeDispatchConfig | None,
) -> dict[str, Any]:
    """Overlay dispatch config fields onto one projected harness record."""
    if config is None:
        return record
    harness_id = str(record.get("id") or "")
    overlay = config.overlay_for(harness_id)
    if overlay is None:
        return record
    updated = dict(record)
    if overlay.can_fire_events is not None:
        updated["can_fire_events"] = overlay.can_fire_events
        updated["event_driven_hooks"] = overlay.can_fire_events
    if overlay.can_receive_dispatch is not None:
        updated["can_receive_dispatch"] = overlay.can_receive_dispatch
    if overlay.dispatch_cost is not None:
        updated["dispatch_cost"] = overlay.dispatch_cost
    if overlay.dispatch_quality is not None:
        updated["dispatch_quality"] = overlay.dispatch_quality
    if overlay.dispatch_availability is not None:
        updated["dispatch_availability"] = overlay.dispatch_availability
    if overlay.max_items is not None:
        updated["dispatch_max_items"] = overlay.max_items
    if overlay.tags:
        updated["dispatch_tags"] = list(overlay.tags)
    return updated


def select_dispatch_candidates(
    records: list[dict[str, Any]],
    config: BridgeDispatchConfig,
    context: DispatchContext,
) -> list[dict[str, Any]]:
    """Return active, dispatchable records admitted by ``context``, ranked."""
    candidates: list[dict[str, Any]] = []
    for raw in records:
        if not isinstance(raw, dict):
            continue
        record = apply_dispatch_config_to_record(dict(raw), config)
        if _record_status(record) != "active":
            continue
        roles = _record_roles(record)
        if context.required_role not in roles and not (
            context.required_role == ROLE_PRIME_BUILDER and "acting-prime-builder" in roles
        ):
            continue
        if record.get("can_receive_dispatch") is not True:
            continue
        if config.rules and not config.matching_rules(context):
            continue
        candidates.append(record)
    order = config.selection_order_for(context)
    return sorted(candidates, key=lambda record: _rank_key(record, order))


def collect_bridge_dispatch_status(project_root: Path) -> BridgeDispatchStatus:
    """Collect the current dispatch config and harness eligibility state."""
    root = project_root.resolve()
    config = load_bridge_dispatch_config(root)
    projection = _load_projection(root)
    raw_records = [record for record in projection.get("harnesses", []) if isinstance(record, dict)]
    records = tuple(apply_dispatch_config_to_record(dict(record), config) for record in raw_records)
    selected_by_role: dict[str, list[dict[str, Any]]] = {}
    findings: list[str] = []

    if config.errors:
        findings.extend(f"config error: {error}" for error in config.errors)

    active_event_sources = [
        record for record in records if _record_status(record) == "active" and record.get("can_fire_events") is True
    ]
    if not active_event_sources:
        findings.append("no active event-firing harness is available; scheduled wake fallback may be required")

    for role in DISPATCH_ROLES:
        context = DispatchContext(required_role=role)
        selected = select_dispatch_candidates(list(records), config, context)
        selected_by_role[role] = [_candidate_summary(record) for record in selected]
        role_holders = [
            record for record in records if _record_status(record) == "active" and role in _record_roles(record)
        ]
        if not role_holders:
            findings.append(f"no active harness holds role {role!r}")
        if not selected:
            findings.append(f"no active dispatchable harness is eligible for role {role!r}")

    findings.extend(_runtime_dispatch_findings(root, selected_by_role))

    health = (
        "FAIL"
        if any(
            "no active dispatchable" in finding
            or finding.startswith("config error")
            or finding.startswith("dispatch runtime failure")
            for finding in findings
        )
        else "PASS"
    )
    if health == "PASS" and findings:
        health = "WARN"
    return BridgeDispatchStatus(
        config=config,
        harnesses=tuple(_candidate_summary(record) for record in records),
        selected_by_role=selected_by_role,
        health_status=health,
        health_findings=tuple(findings),
    )


def format_bridge_dispatch_status(status: BridgeDispatchStatus) -> str:
    """Render a compact human-readable dispatch status report."""
    lines = [
        f"Bridge dispatch health: {status.health_status}",
        f"Config: {status.config.path}",
        "",
        "Harnesses:",
    ]
    for record in status.harnesses:
        roles = ", ".join(record.get("role", [])) or "(none)"
        lines.append(
            "- {id} {name}: roles=[{roles}], active={active}, dispatchable={dispatchable}, "
            "fires_events={fires}, cost={cost}, quality={quality}, availability={availability}".format(
                id=record.get("id"),
                name=record.get("harness_name"),
                roles=roles,
                active=record.get("status") == "active",
                dispatchable=record.get("can_receive_dispatch"),
                fires=record.get("can_fire_events"),
                cost=record.get("dispatch_cost"),
                quality=record.get("dispatch_quality"),
                availability=record.get("dispatch_availability"),
            )
        )
    lines.append("")
    lines.append("Selected candidates:")
    for role in DISPATCH_ROLES:
        ids = [str(row.get("id")) for row in status.selected_by_role.get(role, [])]
        lines.append(f"- {role}: {', '.join(ids) if ids else '(none)'}")
    if status.health_findings:
        lines.append("")
        lines.append("Findings:")
        lines.extend(f"- {finding}" for finding in status.health_findings)
    return "\n".join(lines)


def _load_projection(root: Path) -> dict[str, Any]:
    try:
        from groundtruth_kb.harness_projection import read_roles

        return read_roles(root)
    except Exception:  # intentional-catch: autogenerated check fix
        path = root / "harness-state" / "harness-registry.json"
        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {"harnesses": []}
        except Exception:  # intentional-catch: autogenerated check fix
            return {"harnesses": []}


def _runtime_dispatch_findings(root: Path, selected_by_role: dict[str, list[dict[str, Any]]]) -> list[str]:
    state, errors = _load_dispatch_runtime_state(root)
    findings = list(errors)
    recipients = state.get("recipients")
    if not isinstance(recipients, dict):
        return findings

    selected_keys: set[str] = set(DISPATCH_ROLES)
    for role, rows in selected_by_role.items():
        for row in rows:
            harness_id = str(row.get("id") or "").strip()
            if harness_id:
                selected_keys.add(f"{role}:{harness_id}")

    seen: set[str] = set()
    for recipient_key in sorted(selected_keys):
        row = recipients.get(recipient_key)
        if not isinstance(row, dict):
            continue
        for finding in _runtime_findings_for_recipient(recipient_key, row):
            if finding not in seen:
                findings.append(finding)
                seen.add(finding)
    return findings


def _load_dispatch_runtime_state(root: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    path = root / DISPATCH_STATE_RELATIVE_PATH
    if not path.exists():
        return {}, ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, (f"dispatch runtime warning: unable to read {DISPATCH_STATE_RELATIVE_PATH}: {exc}",)
    if not isinstance(payload, dict):
        return {}, (f"dispatch runtime warning: {DISPATCH_STATE_RELATIVE_PATH} is not a JSON object",)
    return payload, ()


def _runtime_findings_for_recipient(recipient_key: str, row: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    pending_count = _int_value(row.get("pending_count"), default=0)
    selected_count = _int_value(row.get("selected_count"), default=0)
    has_pending_work = pending_count > 0 or selected_count > 0
    failure_class = str(row.get("failure_class") or "").strip()
    last_result = str(row.get("last_result") or "").strip()
    last_launch = row.get("last_launch") if isinstance(row.get("last_launch"), dict) else {}
    launch_reason = str(last_launch.get("reason") or "").strip()

    if row.get("circuit_breaker_tripped") is True and has_pending_work:
        findings.append(
            f"dispatch runtime failure: {recipient_key} circuit breaker is tripped with pending_count={pending_count}"
        )
    if last_result in RUNTIME_FAILURE_RESULTS and has_pending_work:
        findings.append(
            f"dispatch runtime failure: {recipient_key} last_result={last_result} with pending_count={pending_count}"
        )
    if failure_class in RUNTIME_FAILURE_CLASSES and has_pending_work:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} failure_class={failure_class} with pending_count={pending_count}"
        )
    if launch_reason == "work_intent_acquire_failed" and has_pending_work:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} work intent acquisition failed with pending_count={pending_count}"
        )
    if last_result == "unchanged" and has_pending_work:
        findings.append(
            f"dispatch runtime warning: {recipient_key} last_result=unchanged with pending_count={pending_count}"
        )
    return findings


def _candidate_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "harness_name": record.get("harness_name"),
        "harness_type": record.get("harness_type"),
        "role": sorted(_record_roles(record)),
        "status": record.get("status"),
        "can_receive_dispatch": record.get("can_receive_dispatch"),
        "can_fire_events": record.get("can_fire_events"),
        "event_driven_hooks": record.get("event_driven_hooks"),
        "reviewer_precedence": record.get("reviewer_precedence"),
        "dispatch_cost": record.get("dispatch_cost"),
        "dispatch_quality": record.get("dispatch_quality"),
        "dispatch_availability": record.get("dispatch_availability"),
        "dispatch_max_items": record.get("dispatch_max_items"),
    }


def _rank_key(record: dict[str, Any], order: tuple[str, ...]) -> tuple[Any, ...]:
    values: list[Any] = []
    for sort_field in order:
        name = sort_field.strip().lower()
        if name in {"availability", "dispatch_availability"}:
            values.append(-_float_value(record.get("dispatch_availability"), default=50.0))
        elif name in {"cost", "dispatch_cost"}:
            values.append(_float_value(record.get("dispatch_cost"), default=50.0))
        elif name in {"quality", "dispatch_quality"}:
            values.append(-_float_value(record.get("dispatch_quality"), default=50.0))
        elif name == "reviewer_precedence":
            values.append(_int_value(record.get("reviewer_precedence"), default=1_000_000))
        elif name in {"harness_id", "id"}:
            values.append(str(record.get("id") or ""))
        else:
            values.append(str(record.get(name) or ""))
    values.append(str(record.get("id") or ""))
    return tuple(values)


def _role_only_match(rule: DispatchRule, role: str) -> bool:
    lowered = role.strip().lower()
    return lowered in {r.lower() for r in rule.required_roles} and lowered not in {
        r.lower() for r in rule.blocked_roles
    }


def _record_status(record: dict[str, Any]) -> str:
    return str(record.get("status") or "").strip().lower()


def _record_roles(record: dict[str, Any]) -> set[str]:
    role = record.get("role")
    if isinstance(role, str):
        return {role.strip().lower()} if role.strip() else set()
    if isinstance(role, (list, tuple, set, frozenset)):
        return {str(item).strip().lower() for item in role if str(item).strip()}
    return set()


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _float_value(value: Any, *, default: float) -> float:
    parsed = _optional_float(value)
    return default if parsed is None else parsed


def _int_value(value: Any, *, default: int) -> int:
    parsed = _optional_int(value)
    return default if parsed is None else parsed


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set, frozenset)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())
