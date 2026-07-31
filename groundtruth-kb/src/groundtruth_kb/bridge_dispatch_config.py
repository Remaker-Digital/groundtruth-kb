"""Bridge dispatch configuration, status, and ranking helpers."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import random
import re
import sqlite3
import sys
import tomllib
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge_dispatch_rules import DispatchContext, DispatchRule

DISPATCH_CONFIG_RELATIVE_PATH = Path("config") / "dispatcher" / "rules.toml"
DISPATCH_STATE_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller" / "dispatch-state.json"
DISPATCH_QUALITY_INPUT_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller" / "dispatch-quality-inputs.json"
DISPATCH_RUNS_RELATIVE_PATH = DISPATCH_STATE_RELATIVE_PATH.parent / "dispatch-runs"
OPERATOR_QUIESCE_RELATIVE_PATH = DISPATCH_STATE_RELATIVE_PATH.parent / "operator-quiesce.json"

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
DISPATCH_ROLES = (ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION)
OPERATOR_QUIESCE_ACTIVE_REASON = "operator_quiesce_active"

DEFAULT_SELECTION_ORDER = ("quality", "cost", "availability", "reviewer_precedence", "harness_id")
GOVERNANCE_GRADE_LO_MIN_QUALITY = 80.0
DISPATCH_CONFIG_HARNESS_AUTHORITY_FIELDS = frozenset(
    {
        "can_receive_dispatch",
        "can_fire_events",
        "dispatch_cost",
        "dispatch_quality",
        "dispatch_availability",
    }
)
RUNTIME_FAILURE_RESULTS = {
    "all_slugs_quarantined",
    "circuit_breaker_active",
    "dispatch_target_resolution_failed",
    "implementation_authorization_packet_failed",
    "launch_failed",
    "no_active_target_for_role",
    "no_ready_target_for_role",
    "provider_failure",
    "target_unlaunchable",
    "work_intent_acquire_failed",
    "max_turn_exhaustion",
    "no_verdict_produced",
}
RUNTIME_BACKPRESSURE_RESULTS = frozenset(
    {
        OPERATOR_QUIESCE_ACTIVE_REASON,
        "provider_failure_backoff_active",
        "provider_rate_limited",
        "retry_delay_enforced",
        "spawn_rate_limited",
    }
)
RUNTIME_FAILURE_CLASSES = {
    "guard_denial",
    "guard_denied_write",
    "max_turn_exhaustion",
    "missing_bridge_verdict",
    "no_verdict_produced",
    "process_terminated_abruptly",
    "provider_failure",
    "provider_configuration_failure",
    "cursor_headless_cli_unavailable",
    "subprocess_execution_failed",
    "worker_timeout",
    "work_intent_acquire_failed",
    "verified_finalization_missing_commit",
}
RUNTIME_BACKPRESSURE_CLASSES = frozenset({"provider_failure_backoff_active", "provider_rate_limited"})
RUNTIME_FAILURE_LAUNCH_REASONS = RUNTIME_FAILURE_RESULTS | {
    "previous_launch_failed",
    "subprocess_execution_failed",
}
RUNTIME_BACKPRESSURE_LAUNCH_REASONS = RUNTIME_BACKPRESSURE_RESULTS | RUNTIME_BACKPRESSURE_CLASSES
# WI-4718/WI-4768: non-launch outcomes ('launch_failed') whose last_launch.reason
# indicates benign backpressure rather than a dispatcher failure. The runtime
# collapses all non-launch spawn results to last_result="launch_failed"; only the
# reason field distinguishes saturation from failure.
BENIGN_NONLAUNCH_LAUNCH_REASONS = frozenset(
    {"all_impl_auth_quarantined", "concurrency_cap_reached", "per_role_concurrency_cap_reached"}
)
DISPATCH_BUDGET_BENIGN_LAUNCH_REASONS = frozenset(
    {
        "dispatch_budget_session_cap_reached",
        "dispatch_budget_daily_cap_reached",
    }
)
BENIGN_NONLAUNCH_LAUNCH_REASONS = BENIGN_NONLAUNCH_LAUNCH_REASONS | DISPATCH_BUDGET_BENIGN_LAUNCH_REASONS
DOCUMENT_LEASE_HELD_NONLAUNCH_REASON = "document_lease_held"
IMPL_AUTH_QUARANTINED_NONLAUNCH_REASON = "all_impl_auth_quarantined"
SELECTED_DOCUMENTS_INCOMPLETE_RESULT = "selected_documents_incomplete"
HEALTH_STATUS_RANK = {"PASS": 0, "WARN": 1, "FAIL": 2}
GIT_LOCK_WARN_AGE_SECONDS = 15 * 60
GIT_LOCK_FAIL_AGE_SECONDS = 60 * 60
RECENT_RUN_FAILURE_MARKERS = (
    ("provider_rate_limited", "provider_rate_limited"),
    ("HTTP 429", "provider_rate_limited"),
    ("max-turn exhaustion", "max_turn_exhaustion"),
    ("repeated no-progress tool loop", "max_turn_exhaustion"),
    ("session timeout exceeded before Ollama chat turn", "worker_timeout"),
    ("session timeout exceeded before OpenRouter chat turn", "worker_timeout"),
    ("OPENROUTER_API_KEY environment variable is not set", "provider_configuration_failure"),
    ("Cursor Agent CLI not found", "cursor_headless_cli_unavailable"),
    ("passed to Electron/Chromium", "cursor_headless_cli_unavailable"),
)
RECENT_RUN_TEXT_READ_LIMIT = 12_000
PID_CREATE_TIME_SUFFIX = ".create_time_epoch"
PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS = 1.0
RECENT_RUN_SUFFIXES = (".stdout.log", ".stderr.log", ".exit_code", ".pid", PID_CREATE_TIME_SUFFIX)
TERMINAL_DISPATCH_BRIDGE_STATUSES = frozenset({"VERIFIED", "WITHDRAWN", "RETIRED", "SUPERSEDED"})
TERMINAL_WORK_ITEM_RESOLUTION_STATUSES = frozenset({"verified", "resolved", "retired", "wont_fix", "not_a_defect"})
_WORK_ITEM_METADATA_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:Work Items?|work_item_ids?|work_item_id)\s*:\s*(?P<value>.+)$",
    re.IGNORECASE,
)
_WORK_ITEM_ID_RE = re.compile(r"\bWI-\d+\b", re.IGNORECASE)
_BRIDGE_VERSION_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")
_WORK_ITEM_HEADER_READ_BUDGET_BYTES = 16_384
_DISPATCH_WORKER_ENV_VARS = (
    "GTKB_BRIDGE_POLLER_RUN_ID",
    "GTKB_DISPATCH_ID",
    "GTKB_WORK_INTENT_SESSION_ID",
)


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _coerce_utc(value: dt.datetime) -> dt.datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value.astimezone(dt.UTC)


def _isoformat_z(value: dt.datetime) -> str:
    return _coerce_utc(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso_datetime(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return _coerce_utc(dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00")))
    except ValueError:
        return None


def _operator_quiesce_path(project_root: Path) -> Path:
    return project_root.resolve() / OPERATOR_QUIESCE_RELATIVE_PATH


def _read_operator_quiesce_payload(project_root: Path) -> tuple[dict[str, Any] | None, str | None]:
    path = _operator_quiesce_path(project_root)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, None
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(raw, dict):
        return None, "operator quiesce state is not a JSON object"
    return raw, None


def _write_operator_quiesce_payload(project_root: Path, payload: dict[str, Any]) -> None:
    path = _operator_quiesce_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}-{uuid.uuid4().hex[:8]}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(path)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def _is_dispatched_worker_context(environ: dict[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    for key in _DISPATCH_WORKER_ENV_VARS:
        value = str(env.get(key) or "")
        if "-prime-builder-" in value or "-loyal-opposition-" in value:
            return True
    return False


def operator_quiesce_status(project_root: Path, *, now: dt.datetime | None = None) -> dict[str, Any]:
    """Return effective operator-quiesce status without mutating state."""
    root = project_root.resolve()
    path = _operator_quiesce_path(root)
    now_utc = _coerce_utc(now or _now_utc())
    payload, error = _read_operator_quiesce_payload(root)
    base: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "active": False,
        "status": "inactive",
        "reason": None,
        "actor": None,
        "issued_at": None,
        "expires_at": None,
        "ttl_seconds": None,
        "remaining_seconds": None,
        "warning": None,
    }
    if error is not None:
        base["status"] = "invalid"
        base["warning"] = error
        return base
    if payload is None:
        return base

    for key in (
        "reason",
        "actor",
        "issued_at",
        "expires_at",
        "ttl_seconds",
        "cleared_at",
        "cleared_by",
        "clear_reason",
        "updated_at",
    ):
        if key in payload:
            base[key] = payload.get(key)

    if payload.get("active") is not True:
        base["status"] = "cleared" if payload.get("cleared_at") else "inactive"
        return base

    expires_at = _parse_iso_datetime(payload.get("expires_at"))
    if expires_at is None:
        base["status"] = "invalid"
        base["warning"] = "active operator quiesce state has no valid expires_at"
        return base

    remaining = (expires_at - now_utc).total_seconds()
    base["remaining_seconds"] = max(0.0, remaining)
    if remaining <= 0:
        base["status"] = "expired"
        return base

    base["active"] = True
    base["status"] = "active"
    return base


def set_operator_quiesce(
    project_root: Path,
    *,
    reason: str,
    actor: str,
    ttl_seconds: int | None = None,
    expires_at: str | None = None,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    """Set a time-bound operator quiesce with required reason and actor metadata."""
    reason = reason.strip()
    actor = actor.strip()
    if not reason:
        raise ValueError("operator quiesce reason is required")
    if not actor:
        raise ValueError("operator quiesce actor is required")

    now_utc = _coerce_utc(now or _now_utc())
    expires_dt = _parse_iso_datetime(expires_at) if expires_at else None
    if expires_dt is None:
        if ttl_seconds is None:
            raise ValueError("operator quiesce requires --ttl-seconds or --expires-at")
        if ttl_seconds <= 0:
            raise ValueError("operator quiesce ttl_seconds must be positive")
        expires_dt = now_utc + dt.timedelta(seconds=ttl_seconds)
    if expires_dt <= now_utc:
        raise ValueError("operator quiesce expires_at must be in the future")

    ttl = int((expires_dt - now_utc).total_seconds())
    payload = {
        "schema_version": 1,
        "active": True,
        "actor": actor,
        "reason": reason,
        "issued_at": _isoformat_z(now_utc),
        "expires_at": _isoformat_z(expires_dt),
        "ttl_seconds": ttl,
        "updated_at": _isoformat_z(now_utc),
    }
    _write_operator_quiesce_payload(project_root, payload)
    return operator_quiesce_status(project_root, now=now_utc)


def clear_operator_quiesce(
    project_root: Path,
    *,
    actor: str,
    reason: str,
    now: dt.datetime | None = None,
    environ: dict[str, str] | None = None,
    allow_dispatched_worker: bool = False,
) -> dict[str, Any]:
    """Clear operator quiesce unless the caller is an autonomous dispatch worker."""
    actor = actor.strip()
    reason = reason.strip()
    if not actor:
        raise ValueError("operator quiesce clear actor is required")
    if not reason:
        raise ValueError("operator quiesce clear reason is required")
    if not allow_dispatched_worker and _is_dispatched_worker_context(environ):
        raise ValueError("dispatched workers may not clear an active operator quiesce")

    now_utc = _coerce_utc(now or _now_utc())
    previous = operator_quiesce_status(project_root, now=now_utc)
    payload = {
        "schema_version": 1,
        "active": False,
        "cleared_at": _isoformat_z(now_utc),
        "cleared_by": actor,
        "clear_reason": reason,
        "previous": previous,
        "updated_at": _isoformat_z(now_utc),
    }
    _write_operator_quiesce_payload(project_root, payload)
    return operator_quiesce_status(project_root, now=now_utc)


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
    max_items_override: bool = False
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
            max_items=_valid_dispatch_max_items(raw.get("max_items")),
            max_items_override=_optional_bool(raw.get("max_items_override")) is True,
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
            "max_items_override": self.max_items_override,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class DispatchBudgetHarnessConfig:
    """Per-harness dispatch budget metadata."""

    harness_id: str
    model: str | None = None
    estimated_usd_per_dispatch: float | None = None
    pricing: str = "priced"

    @property
    def unpriced(self) -> bool:
        return self.pricing == "unpriced"

    @classmethod
    def from_mapping(cls, harness_id: str, raw: dict[str, Any]) -> DispatchBudgetHarnessConfig:
        pricing = str(raw.get("pricing") or "").strip().lower()
        if not pricing:
            pricing = "unpriced" if _optional_bool(raw.get("unpriced")) is True else "priced"
        if pricing not in {"priced", "unpriced"}:
            pricing = "priced"
        return cls(
            harness_id=harness_id,
            model=_optional_string(raw.get("model")),
            estimated_usd_per_dispatch=_optional_nonnegative_float(
                raw.get("estimated_usd_per_dispatch", raw.get("estimated_cost_usd"))
            ),
            pricing=pricing,
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "harness_id": self.harness_id,
            "model": self.model,
            "estimated_usd_per_dispatch": self.estimated_usd_per_dispatch,
            "pricing": self.pricing,
            "unpriced": self.unpriced,
        }


@dataclass(frozen=True)
class DispatchBudgetConfig:
    """Declarative dispatch cost budget gate."""

    enabled: bool = False
    per_session_usd: float | None = None
    per_user_daily_usd: float | None = None
    soft_session_usd: float | None = None
    unknown_model_policy: str = "fail_closed"
    unpriced_model_policy: str = "fail_open"
    harnesses: dict[str, DispatchBudgetHarnessConfig] = field(default_factory=dict)
    errors: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Any) -> DispatchBudgetConfig:
        if raw is None:
            return cls()
        if not isinstance(raw, dict):
            return cls(errors=("budget section is not a table; budget gate disabled",))
        errors: list[str] = []
        enabled = _optional_bool(raw.get("enabled"))
        if enabled is None:
            enabled = False
        per_session = _optional_nonnegative_float(raw.get("per_session_usd"))
        per_user_daily = _optional_nonnegative_float(raw.get("per_user_daily_usd"))
        soft_session = _optional_nonnegative_float(raw.get("soft_session_usd"))
        for key, parsed in (
            ("per_session_usd", per_session),
            ("per_user_daily_usd", per_user_daily),
            ("soft_session_usd", soft_session),
        ):
            if raw.get(key) is not None and parsed is None:
                errors.append(f"{key} must be a non-negative number; ignoring value")
        unknown_policy = _budget_policy(raw.get("unknown_model_policy"), default="fail_closed")
        unpriced_policy = _budget_policy(raw.get("unpriced_model_policy"), default="fail_open")
        harnesses_raw = raw.get("harnesses", {})
        harnesses: dict[str, DispatchBudgetHarnessConfig] = {}
        if isinstance(harnesses_raw, dict):
            for harness_id, row in harnesses_raw.items():
                if isinstance(row, dict):
                    harnesses[str(harness_id)] = DispatchBudgetHarnessConfig.from_mapping(str(harness_id), row)
                else:
                    errors.append(f"budget.harnesses.{harness_id} is not a table; ignoring row")
        elif harnesses_raw:
            errors.append("budget.harnesses is not a table; ignoring harness budget rows")
        if errors:
            enabled = False
        return cls(
            enabled=enabled,
            per_session_usd=per_session,
            per_user_daily_usd=per_user_daily,
            soft_session_usd=soft_session,
            unknown_model_policy=unknown_policy,
            unpriced_model_policy=unpriced_policy,
            harnesses=harnesses,
            errors=tuple(errors),
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "per_session_usd": self.per_session_usd,
            "per_user_daily_usd": self.per_user_daily_usd,
            "soft_session_usd": self.soft_session_usd,
            "unknown_model_policy": self.unknown_model_policy,
            "unpriced_model_policy": self.unpriced_model_policy,
            "harnesses": {hid: cfg.to_json_dict() for hid, cfg in sorted(self.harnesses.items())},
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class BridgeDispatchConfig:
    """Parsed dispatcher configuration."""

    path: Path
    exists: bool
    schema_version: int
    selection_order: tuple[str, ...] = DEFAULT_SELECTION_ORDER
    harnesses: dict[str, HarnessDispatchConfig] = field(default_factory=dict)
    budget: DispatchBudgetConfig = field(default_factory=DispatchBudgetConfig)
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
            "budget": self.budget.to_json_dict(),
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
    consistency_findings: tuple[str, ...] = ()
    runtime_classifications: tuple[dict[str, Any], ...] = ()
    operator_quiesce: dict[str, Any] = field(default_factory=dict)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.to_json_dict(),
            "harnesses": list(self.harnesses),
            "selected_by_role": self.selected_by_role,
            "health_status": self.health_status,
            "health_findings": list(self.health_findings),
            "consistency_findings": list(self.consistency_findings),
            "runtime_classifications": list(self.runtime_classifications),
            "operator_quiesce": dict(self.operator_quiesce),
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
    budget = DispatchBudgetConfig.from_mapping(raw.get("budget", raw.get("dispatch_budget")))
    return BridgeDispatchConfig(
        path=path,
        exists=True,
        schema_version=schema_version,
        selection_order=selection_order,
        harnesses=harnesses,
        budget=budget,
        rules=tuple(rules),
    )


def apply_dispatch_config_to_record(
    record: dict[str, Any],
    config: BridgeDispatchConfig | None,
) -> dict[str, Any]:
    """Overlay policy-only dispatch config fields onto one projected harness record.

    WI-5012 moved dispatch capability and ranking authority to the harness
    registry/MemBase projection. ``rules.toml`` may still carry per-harness
    policy such as caps or tags, but it must not override the five authoritative
    dispatch fields.
    """
    if config is None:
        return record
    harness_id = str(record.get("id") or "")
    overlay = config.overlay_for(harness_id)
    if overlay is None:
        return record
    updated = dict(record)
    canonical_max_items = _valid_dispatch_max_items(updated.get("dispatch_max_items"))
    existing_source = str(updated.get("dispatch_max_items_source") or "").strip()
    if existing_source == "dispatcher_config_fallback":
        # collect_bridge_dispatch_status() applies the overlay before candidate
        # selection applies it again. Do not relabel our own fallback as a
        # canonical registry value on the second pass.
        canonical_max_items = None
    if overlay.max_items_override and overlay.max_items is not None:
        updated["dispatch_max_items"] = overlay.max_items
        updated["dispatch_max_items_source"] = "dispatcher_config_override"
    elif canonical_max_items is not None:
        updated["dispatch_max_items"] = canonical_max_items
        updated["dispatch_max_items_source"] = "harness_registry"
    elif overlay.max_items is not None:
        updated["dispatch_max_items"] = overlay.max_items
        updated["dispatch_max_items_source"] = "dispatcher_config_fallback"
    if overlay.tags:
        updated["dispatch_tags"] = list(overlay.tags)
    return updated


def apply_dispatch_quality_input_to_record(
    record: dict[str, Any],
    quality_snapshot: dict[str, Any] | None,
    context: DispatchContext,
    *,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    """Overlay governed benchmark-derived quality input onto a candidate record.

    When a WI-4791 quality snapshot is supplied, it is authoritative for
    ``dispatch_quality``. Missing, stale, or malformed inputs fail closed by
    removing the quality value; the existing LO quality floor then rejects the
    candidate when quality participates in ranking.
    """

    if quality_snapshot is None:
        return record
    updated = dict(record)
    row = _quality_input_for_record(updated, quality_snapshot, context)
    if row is None:
        updated["dispatch_quality"] = None
        updated["dispatch_quality_evidence_status"] = "missing"
        updated["dispatch_quality_block_reason"] = "missing_benchmark_quality"
        return updated
    quality = _optional_float(row.get("dispatch_quality"))
    if quality is None:
        updated["dispatch_quality"] = None
        updated["dispatch_quality_evidence_status"] = "malformed"
        updated["dispatch_quality_block_reason"] = "malformed_benchmark_quality"
        return updated
    status = str(row.get("status") or "stale").strip().lower()
    if status not in {"fresh", "ok", "verified"} or _quality_input_expired(row, now=now):
        updated["dispatch_quality"] = None
        updated["dispatch_quality_evidence_status"] = status or "stale"
        updated["dispatch_quality_block_reason"] = "stale_benchmark_quality"
        return updated
    updated["dispatch_quality"] = max(0.0, min(100.0, quality))
    updated["dispatch_quality_evidence_status"] = status
    if row.get("evidence_ref"):
        updated["dispatch_quality_evidence_ref"] = row.get("evidence_ref")
    return updated


def select_dispatch_candidates(
    records: list[dict[str, Any]],
    config: BridgeDispatchConfig,
    context: DispatchContext,
    *,
    rng: Any | None = None,
    quality_snapshot: dict[str, Any] | None = None,
    now: dt.datetime | None = None,
) -> list[dict[str, Any]]:
    """Return active, dispatchable records admitted by ``context``, ranked."""
    candidates: list[dict[str, Any]] = []
    order = config.selection_order_for(context)
    for raw in records:
        if not isinstance(raw, dict):
            continue
        record = apply_dispatch_config_to_record(dict(raw), config)
        record = apply_dispatch_quality_input_to_record(record, quality_snapshot, context, now=now)
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
        if not _passes_governance_grade_lo_quality_floor(record, context, order):
            continue
        candidates.append(record)
    return _rank_candidates_with_uniform_tiebreak(candidates, order, rng=rng)


def collect_bridge_dispatch_status(project_root: Path) -> BridgeDispatchStatus:
    """Collect the current dispatch config and harness eligibility state."""
    root = project_root.resolve()
    config = load_bridge_dispatch_config(root)
    quality_snapshot, quality_findings = _load_dispatch_quality_snapshot(root)
    projection = _load_projection(root)
    raw_records = [record for record in projection.get("harnesses", []) if isinstance(record, dict)]
    records = tuple(apply_dispatch_config_to_record(dict(record), config) for record in raw_records)
    selected_by_role: dict[str, list[dict[str, Any]]] = {}
    findings: list[str] = []
    consistency_findings = _dispatch_config_consistency_findings(raw_records, config)
    quiesce = operator_quiesce_status(root)

    if config.errors:
        findings.extend(f"config error: {error}" for error in config.errors)
    findings.extend(f"dispatch budget config warning: {error}" for error in config.budget.errors)
    findings.extend(quality_findings)
    findings.extend(consistency_findings)
    if quiesce.get("active"):
        findings.append(
            "dispatch operator quiesce active "
            f"until {quiesce.get('expires_at')}: "
            f"reason={quiesce.get('reason')!r}, actor={quiesce.get('actor')!r}"
        )
    elif quiesce.get("status") == "invalid":
        findings.append(f"dispatch operator quiesce state invalid: {quiesce.get('warning')}")
    for role in DISPATCH_ROLES:
        context = DispatchContext(required_role=role)
        selected = select_dispatch_candidates(list(records), config, context, quality_snapshot=quality_snapshot)
        selected_by_role[role] = [_candidate_summary(record) for record in selected]
        role_holders = [
            record for record in records if _record_status(record) == "active" and role in _record_roles(record)
        ]
        if not role_holders:
            findings.append(f"no active harness holds role {role!r}")
        if not selected:
            findings.append(f"no active dispatchable harness is eligible for role {role!r}")

    runtime_findings, runtime_classifications = _runtime_dispatch_evaluation(root, selected_by_role)
    findings.extend(runtime_findings)

    # WI-4789 / SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001 v2 (per-role FAIL):
    # overall health is FAIL only for genuine dispatch impossibility — a
    # configuration error, or a required role with no dispatch-eligible harness
    # (the per-role "no active dispatchable" finding). Selection ignores runtime
    # backoff, so that finding reflects config/topology impossibility, not a
    # transient state. A recoverable "dispatch runtime failure" finding (e.g. a
    # tripped circuit breaker) on a still-eligible harness yields WARN, not FAIL.
    health_degrading_findings = _health_degrading_dispatch_findings(findings, runtime_classifications)
    health = (
        "FAIL"
        if any(
            "no active dispatchable" in finding or finding.startswith("config error")
            for finding in health_degrading_findings
        )
        else "PASS"
    )
    if health == "PASS" and health_degrading_findings:
        health = "WARN"
    return BridgeDispatchStatus(
        config=config,
        harnesses=tuple(_candidate_summary(record) for record in records),
        selected_by_role=selected_by_role,
        health_status=health,
        health_findings=tuple(findings),
        consistency_findings=tuple(consistency_findings),
        runtime_classifications=tuple(runtime_classifications),
        operator_quiesce=quiesce,
    )


def collect_bridge_dispatch_health(
    project_root: Path,
    *,
    routing_status: BridgeDispatchStatus | None = None,
) -> dict[str, Any]:
    """Return the owner-facing dispatch health rollup."""
    root = project_root.resolve()
    status = routing_status or collect_bridge_dispatch_status(root)
    routing_dimension = _routing_config_health_dimension(status)
    complex_dimension = _complex_lifecycle_health_dimension(root)
    git_lock_dimension = _git_lock_health_dimension(root)
    aggregate = _max_health_status(
        str(routing_dimension["health_status"]),
        str(complex_dimension["health_status"]),
        str(git_lock_dimension["health_status"]),
    )
    dimensions = {
        "complex_lifecycle": complex_dimension,
        "git_lock_health": git_lock_dimension,
        "routing_config": routing_dimension,
    }
    findings: list[str] = []
    for dimension_name, dimension in dimensions.items():
        for finding in dimension.get("findings", []):
            findings.append(f"{dimension_name}: {finding}")
    return {
        "schema_version": 1,
        "health_status": aggregate,
        "dimensions": dimensions,
        "complex_lifecycle": complex_dimension,
        "git_lock_health": git_lock_dimension,
        "routing_config": routing_dimension,
        "findings": findings,
        "selected_by_role": status.selected_by_role,
        "config_path": str(status.config.path),
    }


def _routing_config_health_dimension(status: BridgeDispatchStatus) -> dict[str, Any]:
    return {
        "name": "routing_config",
        "health_status": status.health_status,
        "findings": list(status.health_findings),
        "selected_by_role": status.selected_by_role,
        "config_path": str(status.config.path),
        "consistency_findings": list(status.consistency_findings),
        "runtime_classifications": list(status.runtime_classifications),
        "operator_quiesce": dict(status.operator_quiesce),
    }


def _complex_lifecycle_health_dimension(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    daemon_script = root / "scripts" / "gtkb_dispatcher_daemon.py"
    if not daemon_script.is_file():
        return {
            "name": "complex_lifecycle",
            "enabled": False,
            "health_status": "PASS",
            "findings": [],
            "reason": "dispatcher complex daemon script is not present under this project root",
        }
    try:
        from groundtruth_kb.dispatcher_complex import collect_complex_health

        payload = collect_complex_health(root)
    except Exception as exc:  # noqa: BLE001 - health command must isolate lifecycle probe failures
        return {
            "name": "complex_lifecycle",
            "enabled": True,
            "health_status": "FAIL",
            "findings": [f"complex lifecycle probe failed: {exc}"],
            "error": str(exc),
        }
    return {
        "name": "complex_lifecycle",
        "enabled": True,
        "health_status": str(payload.get("health_status") or "FAIL"),
        "aggregate_status": payload.get("aggregate_status"),
        "healthy": payload.get("healthy"),
        "components": payload.get("components", {}),
        "findings": list(payload.get("findings") or []),
    }


def _git_lock_health_dimension(project_root: Path) -> dict[str, Any]:
    lock_path = project_root.resolve() / ".git" / "index.lock"
    payload: dict[str, Any] = {
        "name": "git_lock_health",
        "health_status": "PASS",
        "findings": [],
        "lock_path": str(lock_path),
        "present": False,
        "age_seconds": None,
        "warn_age_seconds": GIT_LOCK_WARN_AGE_SECONDS,
        "fail_age_seconds": GIT_LOCK_FAIL_AGE_SECONDS,
    }
    try:
        modified_at = lock_path.stat().st_mtime
    except FileNotFoundError:
        return payload
    except OSError as exc:
        payload["health_status"] = "FAIL"
        payload["findings"] = [f"FAIL git lock probe: cannot inspect {lock_path}: {exc}"]
        return payload

    age_seconds = max(0.0, _now_utc().timestamp() - modified_at)
    payload["present"] = True
    payload["age_seconds"] = age_seconds
    if age_seconds >= GIT_LOCK_FAIL_AGE_SECONDS:
        status = "FAIL"
    elif age_seconds >= GIT_LOCK_WARN_AGE_SECONDS:
        status = "WARN"
    else:
        return payload

    payload["health_status"] = status
    payload["findings"] = [
        (
            f"{status} git lock: {lock_path} has existed for {age_seconds:.1f}s. "
            "Confirm no live git process holds it, then remove the stale lock."
        )
    ]
    return payload


def _max_health_status(*statuses: str) -> str:
    result = "PASS"
    for status in statuses:
        normalized = status.upper()
        if HEALTH_STATUS_RANK.get(normalized, 0) > HEALTH_STATUS_RANK[result]:
            result = normalized
    return result


def _read_windows_persistent_env_var(name: str, scope: str) -> str | None:
    """Read a persistent Windows environment variable without mutating it."""
    try:
        import winreg
    except ImportError:
        return None

    root_and_path = {
        "User": (winreg.HKEY_CURRENT_USER, "Environment"),
        "Machine": (
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        ),
    }.get(scope)
    if root_and_path is None:
        return None
    root, path = root_and_path
    try:
        with winreg.OpenKey(root, path) as key:
            value, _value_type = winreg.QueryValueEx(key, name)
    except FileNotFoundError:
        return None
    if value is None:
        return None
    return str(value)


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
    budget = status.config.budget
    lines.append(
        f"Budget: enabled={budget.enabled}, "
        f"per_session_usd={budget.per_session_usd}, "
        f"per_user_daily_usd={budget.per_user_daily_usd}"
    )
    lines.append("")
    quiesce = status.operator_quiesce
    if quiesce:
        if quiesce.get("active"):
            lines.append(
                "Operator quiesce: active "
                f"until {quiesce.get('expires_at')} "
                f"(actor={quiesce.get('actor')}, reason={quiesce.get('reason')})"
            )
        else:
            lines.append(f"Operator quiesce: {quiesce.get('status') or 'inactive'}")
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
    findings, _classifications = _runtime_dispatch_evaluation(root, selected_by_role)
    return findings


def _health_degrading_dispatch_findings(
    findings: list[str],
    runtime_classifications: list[dict[str, Any]],
) -> list[str]:
    neutral_findings: set[str] = set()
    for classification in runtime_classifications:
        if _int_value(classification.get("live_inflight_dispatch_count"), default=0) != 0:
            continue
        stale_failure_reason = str(classification.get("stale_failure_reason") or "")
        for finding in classification.get("findings", ()):
            if (
                stale_failure_reason == "current all_impl_auth_quarantined non-launch"
                and _is_impl_auth_quarantine_stale_finding(str(finding))
            ) or (
                _is_terminal_reconciliation_stale_reason(stale_failure_reason)
                and _is_terminal_reconciliation_stale_finding(str(finding))
            ):
                neutral_findings.add(str(finding))
    return [finding for finding in findings if finding not in neutral_findings]


def _is_impl_auth_quarantine_stale_finding(finding: str) -> bool:
    return "stale failure evidence ignored (current all_impl_auth_quarantined non-launch)" in finding


def _is_terminal_reconciliation_stale_reason(reason: str) -> bool:
    return reason.startswith("referenced bridge document terminal") or reason.startswith(
        "referenced bridge work item terminal"
    )


def _is_terminal_reconciliation_stale_finding(finding: str) -> bool:
    return "stale failure evidence ignored (referenced bridge " in finding


def _runtime_dispatch_evaluation(
    root: Path,
    selected_by_role: dict[str, list[dict[str, Any]]],
) -> tuple[list[str], list[dict[str, Any]]]:
    state, errors = _load_dispatch_runtime_state(root)
    findings = list(errors)
    classifications: list[dict[str, Any]] = []
    recipients = state.get("recipients")

    selected_keys = _selected_runtime_recipient_keys(selected_by_role)

    seen: set[str] = set()
    current_rows: dict[str, dict[str, Any]] = {}
    if isinstance(recipients, dict):
        selected_keys.update(_terminal_bridge_stale_recipient_keys(root, recipients))
        for recipient_key in sorted(selected_keys):
            row = recipients.get(recipient_key)
            if not isinstance(row, dict):
                continue
            current_rows[recipient_key] = row
            classification = _runtime_classification_for_recipient(
                recipient_key,
                row,
                project_root=root,
                runs_dir=root / DISPATCH_RUNS_RELATIVE_PATH,
            )
            classifications.append(classification)
            for finding in classification["findings"]:
                if finding not in seen:
                    findings.append(finding)
                    seen.add(finding)

    recent_findings, recent_classifications = _runtime_recent_run_evaluation(root, selected_keys, current_rows)
    classifications.extend(recent_classifications)
    for finding in recent_findings:
        if finding not in seen:
            findings.append(finding)
            seen.add(finding)
    return findings, classifications


def _selected_runtime_recipient_keys(selected_by_role: dict[str, list[dict[str, Any]]]) -> set[str]:
    selected_keys: set[str] = set(DISPATCH_ROLES)
    for role, rows in selected_by_role.items():
        for row in rows:
            harness_id = str(row.get("id") or "").strip()
            if harness_id:
                selected_keys.add(f"{role}:{harness_id}")
    return selected_keys


def _runtime_recent_run_evaluation(
    root: Path,
    selected_keys: set[str],
    current_rows: dict[str, dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    runs_dir = root / DISPATCH_RUNS_RELATIVE_PATH
    if not runs_dir.exists():
        return [], []
    latest_by_recipient: dict[str, dict[str, Any]] = {}
    for row in _recent_run_rows(runs_dir):
        recipient = _recent_run_recipient(row["dispatch_id"], selected_keys)
        if recipient is None:
            continue
        current = latest_by_recipient.get(recipient)
        if current is None or float(row.get("last_modified_epoch", 0.0)) > float(
            current.get("last_modified_epoch", 0.0)
        ):
            latest_by_recipient[recipient] = row

    findings: list[str] = []
    classifications: list[dict[str, Any]] = []
    for recipient, row in sorted(latest_by_recipient.items()):
        current_row = current_rows.get(recipient)
        if current_row is not None and _optional_int(current_row.get("pending_count")) == 0:
            continue
        failure_class = _recent_run_failure_class(row)
        if failure_class is None:
            continue
        exit_code = row.get("exit_code")
        dispatch_id = str(row.get("dispatch_id") or "")
        is_backpressure = failure_class in RUNTIME_BACKPRESSURE_CLASSES
        severity = "WARN" if is_backpressure else "FAIL"
        finding_kind = "warning" if is_backpressure else "failure"
        finding = f"dispatch runtime {finding_kind}: {recipient} latest_run={dispatch_id} failure_class={failure_class}"
        if isinstance(exit_code, int) and not isinstance(exit_code, bool):
            finding += f" exit_code={exit_code}"
        findings.append(finding)
        classifications.append(
            {
                "recipient": recipient,
                "severity": severity,
                "source": "recent_run",
                "dispatch_id": dispatch_id,
                "exit_code": exit_code if isinstance(exit_code, int) and not isinstance(exit_code, bool) else None,
                "failure_class": failure_class,
                "findings": (finding,),
            }
        )
    return findings, classifications


def _recent_run_rows(runs_dir: Path) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    try:
        paths = list(runs_dir.iterdir())
    except OSError:
        return []
    for path in paths:
        dispatch_id = _recent_run_dispatch_id(path)
        if dispatch_id is None:
            continue
        row = rows.setdefault(dispatch_id, {"dispatch_id": dispatch_id})
        try:
            modified = path.stat().st_mtime
        except OSError:
            modified = 0.0
        row["last_modified_epoch"] = max(float(row.get("last_modified_epoch", 0.0)), modified)
        if path.name.endswith(".stderr.log"):
            row["stderr_path"] = path
            row["stderr_bytes"] = _path_size(path)
        elif path.name.endswith(".stdout.log"):
            row["stdout_bytes"] = _path_size(path)
        elif path.name.endswith(".exit_code"):
            row["exit_code"] = _read_int(path)
    return list(rows.values())


def _recent_run_dispatch_id(path: Path) -> str | None:
    name = path.name
    for suffix in RECENT_RUN_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return None


def _recent_run_recipient(dispatch_id: str, selected_keys: set[str]) -> str | None:
    for key in sorted((key for key in selected_keys if ":" in key), key=len, reverse=True):
        role, harness_id = key.split(":", 1)
        if f"-{role}-{harness_id}-" in dispatch_id:
            return key
    return None


def _recent_run_failure_class(row: dict[str, Any]) -> str | None:
    stderr_text = _read_bounded_text(row.get("stderr_path"))
    for marker, failure_class in RECENT_RUN_FAILURE_MARKERS:
        if marker in stderr_text:
            return failure_class
    exit_code = row.get("exit_code")
    if isinstance(exit_code, int) and not isinstance(exit_code, bool) and exit_code != 0:
        if exit_code == 4294967295:
            return "process_terminated_abruptly"
        if exit_code == 124:
            return "worker_timeout"
        return "subprocess_execution_failed"
    return None


def _read_bounded_text(path_value: Any) -> str:
    if not isinstance(path_value, Path):
        return ""
    try:
        with path_value.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.read(RECENT_RUN_TEXT_READ_LIMIT)
    except OSError:
        return ""


def _path_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _read_int(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _read_float(path: Path) -> float | None:
    try:
        return float(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _pid_alive(pid: int) -> bool:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return False
    if pid_int <= 0:
        return False
    try:
        import psutil  # noqa: PLC0415

        return bool(psutil.pid_exists(pid_int))
    except Exception:  # noqa: BLE001
        pass
    if os.name == "nt":
        try:
            import ctypes  # noqa: PLC0415

            process_query_limited_information = 0x1000
            still_active = 259
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.OpenProcess(process_query_limited_information, False, pid_int)
            if handle:
                try:
                    exit_code = ctypes.c_ulong()
                    if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                        return exit_code.value == still_active
                    return True
                finally:
                    kernel32.CloseHandle(handle)
        except Exception:  # noqa: BLE001
            pass
    try:
        os.kill(pid_int, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _pid_create_time_epoch(pid: int) -> float | None:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return None
    if pid_int <= 0:
        return None
    try:
        import psutil  # noqa: PLC0415

        return float(psutil.Process(pid_int).create_time())
    except Exception:  # noqa: BLE001
        return None


def _pid_create_time_matches(pid: int, expected_epoch: Any) -> bool:
    try:
        expected = float(expected_epoch)
    except (TypeError, ValueError):
        return False
    actual = _pid_create_time_epoch(pid)
    if actual is None:
        return False
    return abs(actual - expected) <= PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS


def _append_findings_once(findings: list[str], seen: set[str], new_findings: tuple[str, ...]) -> None:
    for finding in new_findings:
        if finding not in seen:
            findings.append(finding)
            seen.add(finding)


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
    return list(_runtime_classification_for_recipient(recipient_key, row)["findings"])


def _runtime_classification_for_recipient(
    recipient_key: str,
    row: dict[str, Any],
    *,
    project_root: Path | None = None,
    runs_dir: Path | None = None,
) -> dict[str, Any]:
    findings: list[str] = []
    pending_count = _int_value(row.get("pending_count"), default=0)
    selected_count = _int_value(row.get("selected_count"), default=0)
    has_pending_work = pending_count > 0 or selected_count > 0
    failure_class = str(row.get("failure_class") or "").strip()
    last_result = str(row.get("last_result") or "").strip()
    last_launch = row.get("last_launch") if isinstance(row.get("last_launch"), dict) else {}
    launch_reason = str(last_launch.get("reason") or "").strip()
    launch_exit_failure = str(last_launch.get("exit_failure_reason") or "").strip()
    live_inflight_dispatch_count = _recipient_live_dispatch_count(runs_dir, recipient_key)
    has_visible_backpressure = has_pending_work or live_inflight_dispatch_count > 0
    stale_failure_reason = _stale_failure_evidence_reason(
        recipient_key,
        row,
        last_launch,
        project_root=project_root,
        runs_dir=runs_dir,
    )
    current_runtime_failure_signal = any(
        (
            last_result in RUNTIME_FAILURE_RESULTS or last_result.endswith("_dispatch_not_ready"),
            launch_reason in RUNTIME_FAILURE_LAUNCH_REASONS,
            launch_exit_failure in RUNTIME_FAILURE_RESULTS | RUNTIME_FAILURE_CLASSES,
            row.get("circuit_breaker_tripped") is True,
        )
    )
    failure_evidence_present = any(
        (
            failure_class in RUNTIME_FAILURE_CLASSES,
            failure_class in RUNTIME_BACKPRESSURE_CLASSES,
            last_result in RUNTIME_FAILURE_RESULTS or last_result.endswith("_dispatch_not_ready"),
            last_result in RUNTIME_BACKPRESSURE_RESULTS,
            launch_reason in RUNTIME_FAILURE_LAUNCH_REASONS,
            launch_reason in RUNTIME_BACKPRESSURE_LAUNCH_REASONS,
            launch_exit_failure in RUNTIME_FAILURE_RESULTS | RUNTIME_FAILURE_CLASSES,
            launch_exit_failure in RUNTIME_BACKPRESSURE_RESULTS | RUNTIME_BACKPRESSURE_CLASSES,
            row.get("circuit_breaker_tripped") is True,
        )
    )
    lease_held_nonlaunch = (
        last_result == DOCUMENT_LEASE_HELD_NONLAUNCH_REASON or launch_reason == DOCUMENT_LEASE_HELD_NONLAUNCH_REASON
    )
    impl_auth_quarantined_nonlaunch = (
        last_result == IMPL_AUTH_QUARANTINED_NONLAUNCH_REASON or launch_reason == IMPL_AUTH_QUARANTINED_NONLAUNCH_REASON
    )
    if (
        stale_failure_reason is None
        and (lease_held_nonlaunch or impl_auth_quarantined_nonlaunch)
        and has_pending_work
        and failure_evidence_present
        and not current_runtime_failure_signal
    ):
        stale_failure_reason = (
            "current document_lease_held non-launch"
            if lease_held_nonlaunch
            else "current all_impl_auth_quarantined non-launch"
        )
    ignore_failure_fields = bool(stale_failure_reason and has_pending_work and failure_evidence_present)

    if ignore_failure_fields:
        findings.append(
            "dispatch runtime warning: "
            f"{recipient_key} stale failure evidence ignored ({stale_failure_reason}) "
            f"with pending_count={pending_count}"
        )

    if row.get("circuit_breaker_tripped") is True and has_pending_work and not ignore_failure_fields:
        findings.append(
            f"dispatch runtime failure: {recipient_key} circuit breaker is tripped with pending_count={pending_count}"
        )
    last_result_is_runtime_failure = last_result in RUNTIME_FAILURE_RESULTS or last_result.endswith(
        "_dispatch_not_ready"
    )
    # WI-4718: 'launch_failed' is the generic non-launch token written by the
    # dispatcher runtime for ANY non-launch outcome; the specific cause is
    # last_launch.reason. Defer to it so benign backpressure is not misreported
    # as a runtime failure. Backpressure reasons stay visible as warnings, while
    # genuine failure reasons or an absent reason still flag below.
    if last_result == "launch_failed" and (
        launch_reason in BENIGN_NONLAUNCH_LAUNCH_REASONS or launch_reason in RUNTIME_BACKPRESSURE_LAUNCH_REASONS
    ):
        last_result_is_runtime_failure = False
    if last_result_is_runtime_failure and has_pending_work and not ignore_failure_fields:
        findings.append(
            f"dispatch runtime failure: {recipient_key} last_result={last_result} with pending_count={pending_count}"
        )
    if last_result in RUNTIME_BACKPRESSURE_RESULTS and has_visible_backpressure and not ignore_failure_fields:
        findings.append(
            "dispatch runtime warning: "
            f"{recipient_key} backpressure last_result={last_result} "
            f"with pending_count={pending_count}, live_inflight={live_inflight_dispatch_count}"
        )
    if (
        last_result == SELECTED_DOCUMENTS_INCOMPLETE_RESULT
        or launch_exit_failure == SELECTED_DOCUMENTS_INCOMPLETE_RESULT
    ) and has_pending_work:
        missing_documents = last_launch.get("incomplete_documents")
        findings.append(
            "dispatch runtime warning: "
            f"{recipient_key} selected_documents_incomplete "
            f"missing_documents={missing_documents if isinstance(missing_documents, list) else []} "
            f"with pending_count={pending_count}"
        )
    if last_result == "launch_failed" and launch_reason in DISPATCH_BUDGET_BENIGN_LAUNCH_REASONS and has_pending_work:
        cap_value = last_launch.get("per_session_usd")
        if cap_value is None:
            cap_value = last_launch.get("per_user_daily_usd")
        findings.append(
            f"dispatch runtime warning: {recipient_key} budget gate held "
            f"(projected_usd={last_launch.get('projected_usd')}, cap_usd={cap_value}, "
            f"reason={launch_reason}) with pending_count={pending_count}"
        )
    elif last_result == "launch_failed" and launch_reason in BENIGN_NONLAUNCH_LAUNCH_REASONS and has_pending_work:
        live = _int_value(last_launch.get("live_count", last_launch.get("per_role_live")), default=0)
        cap = _int_value(last_launch.get("cap", last_launch.get("per_role_cap")), default=0)
        findings.append(
            f"dispatch runtime warning: {recipient_key} saturated "
            f"(live_count={live}/cap={cap}, reason={launch_reason}) with pending_count={pending_count}"
        )
    if failure_class in RUNTIME_FAILURE_CLASSES and has_pending_work and not ignore_failure_fields:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} failure_class={failure_class} with pending_count={pending_count}"
        )
    if failure_class in RUNTIME_BACKPRESSURE_CLASSES and has_visible_backpressure and not ignore_failure_fields:
        findings.append(
            "dispatch runtime warning: "
            f"{recipient_key} backpressure failure_class={failure_class} "
            f"with pending_count={pending_count}, live_inflight={live_inflight_dispatch_count}"
        )
    if launch_reason in RUNTIME_FAILURE_LAUNCH_REASONS and has_pending_work and not ignore_failure_fields:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} last_launch.reason={launch_reason} with pending_count={pending_count}"
        )
    if launch_reason in RUNTIME_BACKPRESSURE_LAUNCH_REASONS and has_visible_backpressure and not ignore_failure_fields:
        findings.append(
            "dispatch runtime warning: "
            f"{recipient_key} backpressure last_launch.reason={launch_reason} "
            f"with pending_count={pending_count}, live_inflight={live_inflight_dispatch_count}"
        )
    if (
        launch_exit_failure in RUNTIME_FAILURE_RESULTS | RUNTIME_FAILURE_CLASSES
        and has_pending_work
        and not ignore_failure_fields
    ):
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} last_launch.exit_failure_reason={launch_exit_failure} "
            f"with pending_count={pending_count}"
        )
    if (
        launch_exit_failure in RUNTIME_BACKPRESSURE_RESULTS | RUNTIME_BACKPRESSURE_CLASSES
        and has_visible_backpressure
        and not ignore_failure_fields
    ):
        findings.append(
            "dispatch runtime warning: "
            f"{recipient_key} backpressure last_launch.exit_failure_reason={launch_exit_failure} "
            f"with pending_count={pending_count}, live_inflight={live_inflight_dispatch_count}"
        )
    if launch_reason == "work_intent_acquire_failed" and has_pending_work and not ignore_failure_fields:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} work intent acquisition failed with pending_count={pending_count}"
        )
    fallback_skipped = row.get("fallback_skipped_candidates")
    if isinstance(fallback_skipped, list) and has_pending_work:
        for candidate in fallback_skipped:
            if not isinstance(candidate, dict):
                continue
            reason = str(candidate.get("reason") or "").strip()
            candidate_recipient = str(candidate.get("recipient") or candidate.get("harness_id") or "").strip()
            failure_label = str(candidate.get("failure_class") or "").strip()
            if reason in RUNTIME_FAILURE_RESULTS or reason.endswith("_dispatch_not_ready"):
                suffix = f", failure_class={failure_label}" if failure_label else ""
                findings.append(
                    "dispatch runtime failure: "
                    f"{recipient_key} skipped fallback {candidate_recipient} reason={reason}{suffix} "
                    f"with pending_count={pending_count}"
                )
            elif reason in RUNTIME_BACKPRESSURE_RESULTS:
                suffix = f", failure_class={failure_label}" if failure_label else ""
                findings.append(
                    "dispatch runtime warning: "
                    f"{recipient_key} skipped fallback {candidate_recipient} backpressure reason={reason}{suffix} "
                    f"with pending_count={pending_count}"
                )
    if last_result == "unchanged" and has_pending_work and live_inflight_dispatch_count == 0:
        findings.append(
            f"dispatch runtime warning: {recipient_key} last_result=unchanged with pending_count={pending_count}"
        )
    quarantined_threads = row.get("quarantined_threads")
    if isinstance(quarantined_threads, list) and quarantined_threads:
        slugs: list[str] = []
        for entry in quarantined_threads:
            if isinstance(entry, dict):
                slug = entry.get("slug")
                if isinstance(slug, str) and slug:
                    slugs.append(slug)
        unique_slugs = sorted(set(slugs))
        if unique_slugs:
            findings.append(
                f"dispatch runtime warning: {recipient_key} has "
                f"{len(unique_slugs)} bridge thread(s) quarantined for malformed status token: "
                f"{unique_slugs}"
            )
    health_degrading_findings = [
        finding
        for finding in findings
        if not (
            live_inflight_dispatch_count == 0
            and (
                (
                    stale_failure_reason == "current all_impl_auth_quarantined non-launch"
                    and _is_impl_auth_quarantine_stale_finding(finding)
                )
                or (
                    _is_terminal_reconciliation_stale_reason(stale_failure_reason or "")
                    and _is_terminal_reconciliation_stale_finding(finding)
                )
            )
        )
    ]
    severity = "PASS"
    if any(finding.startswith("dispatch runtime failure") for finding in health_degrading_findings):
        severity = "FAIL"
    elif health_degrading_findings:
        severity = "WARN"
    return {
        "recipient": recipient_key,
        "severity": severity,
        "pending_count": pending_count,
        "selected_count": selected_count,
        "last_result": last_result or None,
        "failure_class": failure_class or None,
        "last_launch_reason": launch_reason or None,
        "last_launch_exit_failure_reason": launch_exit_failure or None,
        "live_inflight_dispatch_count": live_inflight_dispatch_count,
        "stale_failure_evidence": bool(stale_failure_reason),
        "stale_failure_reason": stale_failure_reason,
        "findings": tuple(findings),
    }


def _recipient_live_dispatch_count(runs_dir: Path | None, recipient_key: str) -> int:
    if runs_dir is None or ":" not in recipient_key:
        return 0
    role_label, harness_id = recipient_key.split(":", 1)
    role_label = role_label.strip()
    harness_id = harness_id.strip()
    if not role_label or not harness_id:
        return 0
    dispatch_id_token = f"-{role_label}-{harness_id}-"
    live = 0
    try:
        pid_files = list(runs_dir.glob("*.pid"))
    except OSError:
        return 0
    for pid_path in pid_files:
        dispatch_id = pid_path.name[: -len(".pid")]
        if dispatch_id_token not in dispatch_id:
            continue
        status_path = runs_dir / f"{dispatch_id}.exit_code"
        try:
            if status_path.exists() and status_path.stat().st_size > 0:
                continue
        except OSError:
            continue
        pid = _read_int(pid_path)
        if pid is None or not _pid_alive(pid):
            continue
        expected = _read_float(runs_dir / f"{dispatch_id}{PID_CREATE_TIME_SUFFIX}")
        if expected is None or not _pid_create_time_matches(pid, expected):
            continue
        live += 1
    return live


def _stale_failure_evidence_reason(
    recipient_key: str,
    row: dict[str, Any],
    last_launch: dict[str, Any],
    *,
    project_root: Path | None = None,
    runs_dir: Path | None = None,
) -> str | None:
    terminal_reason = _terminal_bridge_reconciliation_reason(project_root, row)
    if terminal_reason is not None:
        return terminal_reason
    if ":" not in recipient_key:
        return None
    expected = recipient_key.strip()
    evidence_recipients = _recipient_evidence_values(row, last_launch)
    if not evidence_recipients or expected in evidence_recipients:
        return _stale_dispatch_run_liveness_reason(runs_dir, last_launch)
    return "recipient evidence points to " + ", ".join(sorted(evidence_recipients))


def _terminal_bridge_stale_recipient_keys(root: Path, recipients: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for recipient_key, row in recipients.items():
        if not isinstance(recipient_key, str) or ":" not in recipient_key or not isinstance(row, dict):
            continue
        if not _recipient_state_has_visible_residue(row):
            continue
        if _terminal_bridge_reconciliation_reason(root, row) is not None:
            keys.add(recipient_key)
    return keys


def _recipient_state_has_visible_residue(row: dict[str, Any]) -> bool:
    pending_count = _int_value(row.get("pending_count"), default=0)
    selected_count = _int_value(row.get("selected_count"), default=0)
    return pending_count > 0 or selected_count > 0


def _terminal_bridge_reconciliation_reason(project_root: Path | None, row: dict[str, Any]) -> str | None:
    bridge_ids = _bridge_ids_from_runtime_row(row)
    if project_root is None or not bridge_ids:
        return None
    statuses = {bridge_id: _latest_bridge_status_for_document(project_root, bridge_id) for bridge_id in bridge_ids}
    if not statuses or any(status is None for status in statuses.values()):
        return None
    if any(status == "NO-ACTION" for status in statuses.values()):
        return None
    if all(status in TERMINAL_DISPATCH_BRIDGE_STATUSES for status in statuses.values() if status is not None):
        rendered = ", ".join(f"{bridge_id}={status}" for bridge_id, status in sorted(statuses.items()))
        return f"referenced bridge document terminal ({rendered})"
    return _terminal_work_item_reconciliation_reason(project_root, bridge_ids)


def _bridge_ids_from_runtime_row(row: dict[str, Any]) -> list[str]:
    ids: list[str] = []

    def _add(value: Any) -> None:
        if isinstance(value, str) and value.strip():
            slug = value.strip()
            if slug not in ids:
                ids.append(slug)

    def _add_from_mapping(mapping: dict[str, Any]) -> None:
        _add(mapping.get("primary_bridge_id"))
        _add(mapping.get("bridge_id"))
        for key in ("selected_documents", "document_names"):
            raw = mapping.get(key)
            if isinstance(raw, list):
                for item in raw:
                    _add(item)

    _add_from_mapping(row)
    last_launch = row.get("last_launch")
    if isinstance(last_launch, dict):
        _add_from_mapping(last_launch)
    return ids


def _bridge_version_files_for_thread(project_root: Path, bridge_id: str) -> list[Path]:
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return []
    versioned: list[tuple[int, Path]] = []
    for path in bridge_dir.glob("*.md"):
        match = _BRIDGE_VERSION_FILE_RE.match(path.name)
        if match is None or match.group("slug") != bridge_id:
            continue
        versioned.append((int(match.group("version")), path))
    return [path for _version, path in sorted(versioned, key=lambda row: row[0], reverse=True)]


def _work_item_ids_for_bridge_thread(project_root: Path, bridge_id: str) -> list[str]:
    work_item_ids: list[str] = []
    for path in _bridge_version_files_for_thread(project_root, bridge_id):
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:_WORK_ITEM_HEADER_READ_BUDGET_BYTES]
        except OSError:
            continue
        for line in head.splitlines():
            match = _WORK_ITEM_METADATA_LINE_RE.match(line)
            if match is None:
                continue
            for raw_work_item_id in _WORK_ITEM_ID_RE.findall(match.group("value")):
                work_item_id = raw_work_item_id.upper()
                if work_item_id not in work_item_ids:
                    work_item_ids.append(work_item_id)
        if work_item_ids:
            return work_item_ids
    return work_item_ids


def _work_item_resolution_status(project_root: Path, work_item_id: str) -> str | None:
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return None
    try:
        with sqlite3.connect(db_path) as con:
            row = con.execute(
                "SELECT resolution_status FROM current_work_items WHERE id = ? LIMIT 1",
                (work_item_id,),
            ).fetchone()
    except sqlite3.Error:
        return None
    if row is None or row[0] is None:
        return None
    return str(row[0]).strip()


def _terminal_work_item_evidence_for_bridge(project_root: Path, bridge_id: str) -> dict[str, Any] | None:
    work_item_ids = _work_item_ids_for_bridge_thread(project_root, bridge_id)
    if not work_item_ids:
        return None
    statuses: list[dict[str, str]] = []
    for work_item_id in work_item_ids:
        resolution_status = _work_item_resolution_status(project_root, work_item_id)
        if resolution_status is None:
            return None
        normalized = resolution_status.lower()
        if normalized not in TERMINAL_WORK_ITEM_RESOLUTION_STATUSES:
            return None
        statuses.append({"id": work_item_id, "resolution_status": normalized})
    rendered = ", ".join(f"{row['id']}={row['resolution_status']}" for row in statuses)
    return {
        "reason": f"referenced work item terminal ({rendered})",
        "work_items": statuses,
    }


def _terminal_work_item_reconciliation_reason(project_root: Path | None, bridge_ids: list[str]) -> str | None:
    if project_root is None or not bridge_ids:
        return None
    terminal: list[tuple[str, str]] = []
    for bridge_id in bridge_ids:
        evidence = _terminal_work_item_evidence_for_bridge(project_root, bridge_id)
        if evidence is None:
            return None
        terminal.append((bridge_id, str(evidence["reason"])))
    rendered = ", ".join(f"{bridge_id}: {reason}" for bridge_id, reason in terminal)
    return f"referenced bridge work item terminal ({rendered})"


def _latest_bridge_status_for_document(project_root: Path, bridge_id: str) -> str | None:
    bridge_id = bridge_id.strip()
    if not bridge_id:
        return None
    helper = _load_bridge_thread_files_helper(project_root)
    if helper is None:
        return None
    return helper.latest_bridge_status_for_thread(
        project_root,
        bridge_id,
        status_reader=_status_from_bridge_file,
    )


def _load_bridge_thread_files_helper(project_root: Path):
    helper_path = project_root / "scripts" / "bridge_thread_files.py"
    if not helper_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_gtkb_bridge_thread_files_for_dispatch_config", helper_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        token = stripped.split(maxsplit=1)[0].strip("#>*-`").upper()
        return token
    return None


def _stale_dispatch_run_liveness_reason(runs_dir: Path | None, last_launch: dict[str, Any]) -> str | None:
    if runs_dir is None:
        return None
    dispatch_id = str(last_launch.get("dispatch_id") or "").strip()
    if not dispatch_id:
        return None
    pid_path = runs_dir / f"{dispatch_id}.pid"
    status_path = runs_dir / f"{dispatch_id}.exit_code"
    try:
        exited = status_path.exists() and status_path.stat().st_size > 0
    except OSError:
        exited = False
    if exited:
        return f"recorded dispatch {dispatch_id} has exited"
    launched = last_launch.get("launched") is True or "pid" in last_launch
    if not launched and not pid_path.exists():
        return None
    pid = _read_int(pid_path)
    if pid is None:
        pid = _optional_int(last_launch.get("pid"))
    if pid is None:
        return f"recorded dispatch {dispatch_id} has no live worker pid"
    if not _pid_alive(pid):
        return f"recorded dispatch {dispatch_id} has no live worker"
    expected = last_launch.get("pid_create_time_epoch")
    if expected is None:
        expected = _read_float(runs_dir / f"{dispatch_id}{PID_CREATE_TIME_SUFFIX}")
    if expected is None:
        return f"recorded dispatch {dispatch_id} has no verified live worker provenance"
    if not _pid_create_time_matches(pid, expected):
        return f"recorded dispatch {dispatch_id} live worker provenance does not match"
    return None


def _recipient_evidence_values(row: dict[str, Any], last_launch: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    _add_recipient_evidence(values, last_launch.get("recipient"))
    selected_candidate = last_launch.get("selected_candidate")
    if isinstance(selected_candidate, dict):
        _add_recipient_evidence(values, selected_candidate.get("recipient"))
    row_candidate = row.get("selected_candidate")
    if isinstance(row_candidate, dict):
        _add_recipient_evidence(values, row_candidate.get("recipient"))
    return values


def _add_recipient_evidence(values: set[str], value: Any) -> None:
    if isinstance(value, str) and value.strip():
        values.add(value.strip())


def _dispatch_config_consistency_findings(
    raw_records: list[dict[str, Any]],
    config: BridgeDispatchConfig,
) -> list[str]:
    findings: list[str] = []
    for raw in raw_records:
        harness_id = str(raw.get("id") or "").strip()
        if not harness_id:
            continue
        overlay = config.overlay_for(harness_id)
        if overlay is None:
            continue
        deprecated = [
            field
            for field in sorted(DISPATCH_CONFIG_HARNESS_AUTHORITY_FIELDS)
            if getattr(overlay, field, None) is not None
        ]
        if deprecated:
            fields = ", ".join(deprecated)
            findings.append(
                "dispatch config policy warning: "
                f"harness {harness_id} rules.toml carries deprecated authoritative field(s) "
                f"{fields}; ignored in favor of harness-registry/MemBase"
            )
    return findings


def _load_dispatch_quality_snapshot(project_root: Path) -> tuple[dict[str, Any] | None, tuple[str, ...]]:
    path = project_root / DISPATCH_QUALITY_INPUT_RELATIVE_PATH
    if not path.is_file():
        return None, ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, (f"dispatch quality input warning: cannot read {path}: {exc}",)
    if not isinstance(payload, dict):
        return None, (f"dispatch quality input warning: {path} is not a JSON object",)
    if not isinstance(payload.get("quality_inputs"), list):
        return payload, (f"dispatch quality input warning: {path} has no quality_inputs list",)
    return payload, ()


def _quality_input_for_record(
    record: dict[str, Any],
    quality_snapshot: dict[str, Any],
    context: DispatchContext,
) -> dict[str, Any] | None:
    rows = quality_snapshot.get("quality_inputs")
    if not isinstance(rows, list):
        return None
    harness_id = str(record.get("id") or "").strip()
    role = context.required_role.strip().lower()
    activity = str(getattr(context, "activity", "") or "*").strip().lower() or "*"
    wildcard: dict[str, Any] | None = None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("harness_id") or "").strip() != harness_id:
            continue
        if str(row.get("role") or "").strip().lower() != role:
            continue
        row_activity = str(row.get("activity_type") or "*").strip().lower() or "*"
        if row_activity == activity:
            return row
        if row_activity == "*":
            wildcard = row
    return wildcard


def _quality_input_expired(row: dict[str, Any], *, now: dt.datetime | None) -> bool:
    expires_at = _parse_iso_datetime(row.get("expires_at"))
    if expires_at is None:
        return False
    return expires_at <= _coerce_utc(now or _now_utc())


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
        "dispatch_max_items_source": record.get("dispatch_max_items_source"),
        "dispatch_quality_evidence_status": record.get("dispatch_quality_evidence_status"),
        "dispatch_quality_evidence_ref": record.get("dispatch_quality_evidence_ref"),
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
            continue
        else:
            values.append(str(record.get(name) or ""))
    return tuple(values)


def _rank_candidates_with_uniform_tiebreak(
    candidates: list[dict[str, Any]],
    order: tuple[str, ...],
    *,
    rng: Any | None = None,
) -> list[dict[str, Any]]:
    ranked = sorted(candidates, key=lambda record: _rank_key(record, order))
    if len(ranked) < 2:
        return ranked

    ranked_with_random_ties: list[dict[str, Any]] = []
    index = 0
    while index < len(ranked):
        rank_key = _rank_key(ranked[index], order)
        tied_group = [ranked[index]]
        index += 1
        while index < len(ranked) and _rank_key(ranked[index], order) == rank_key:
            tied_group.append(ranked[index])
            index += 1
        if len(tied_group) > 1:
            (rng or random).shuffle(tied_group)
        ranked_with_random_ties.extend(tied_group)
    return ranked_with_random_ties


def _passes_governance_grade_lo_quality_floor(
    record: dict[str, Any],
    context: DispatchContext,
    order: tuple[str, ...],
) -> bool:
    if context.required_role != ROLE_LOYAL_OPPOSITION:
        return True
    if not _selection_order_includes_quality(order):
        return True
    quality = _float_value(record.get("dispatch_quality"), default=50.0)
    return quality >= GOVERNANCE_GRADE_LO_MIN_QUALITY


def _selection_order_includes_quality(order: tuple[str, ...]) -> bool:
    return any(name.strip().lower() in {"quality", "dispatch_quality"} for name in order)


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


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    parsed = str(value).strip()
    return parsed or None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _optional_nonnegative_float(value: Any) -> float | None:
    parsed = _optional_float(value)
    if parsed is None or parsed < 0:
        return None
    return parsed


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


def _valid_dispatch_max_items(value: Any) -> int | None:
    parsed = _optional_int(value)
    return parsed if parsed is not None and parsed >= 1 else None


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


def _budget_policy(value: Any, *, default: str) -> str:
    parsed = str(value or default).strip().lower().replace("-", "_")
    return parsed if parsed in {"fail_open", "fail_closed"} else default
