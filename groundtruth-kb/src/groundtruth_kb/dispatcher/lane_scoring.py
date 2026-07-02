"""Advisory dispatch lane-scoring registry/projection helpers.

This Wave 1 helper is deliberately non-activating: it can seed a governed lane
matrix and render compact projection payloads, but it does not change runtime
dispatcher target selection or write harness-state/config files.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

DEFAULT_ACTIVITY_TYPES: tuple[str, ...] = ("build", "test", "spec", "ops", "project", "deliberation")
RETIRED_HARNESS_STATUSES = frozenset({"retired", "disabled", "inactive"})
PRODUCTION_READY_LIFECYCLES = frozenset({"approved"})
FRESH_EVIDENCE_STATUSES = frozenset({"fresh", "ok", "verified"})
REQUIRED_PRODUCTION_EVIDENCE: tuple[str, ...] = ("parity", "readiness", "benchmark")


@dataclass(frozen=True)
class EvidenceRef:
    """Compact evidence pointer for production lane eligibility."""

    evidence_type: str
    status: str
    ref: str | None = None
    captured_at: str | None = None
    expires_at: str | None = None


@dataclass(frozen=True)
class DispatchLane:
    """Governed lane identity plus independent behavior/gating fields."""

    lane_id: str
    harness_id: str
    provider: str
    model_route: str
    role: str
    activity_type: str
    lifecycle: str = "shadow"
    dispatch_enabled: bool = False
    shadow_enabled: bool = True
    route_selectable: bool = False
    waiver_id: str | None = None
    blockage_reasons: tuple[str, ...] = ()
    score_components: Mapping[str, float] = field(default_factory=dict)
    caps: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: Mapping[str, EvidenceRef] = field(default_factory=dict)


def lanes_from_harness_projection(
    projection: Mapping[str, Any],
    *,
    activity_types: Sequence[str] = DEFAULT_ACTIVITY_TYPES,
) -> tuple[DispatchLane, ...]:
    """Seed advisory role/activity lanes from a harness registry projection.

    The function only reads the supplied mapping. It represents fixed native
    harness routes with ``route_selectable=False`` until a later governed route
    selector exists.
    """

    lanes: list[DispatchLane] = []
    for harness in _projection_harnesses(projection):
        status = _normalize_token(harness.get("status") or "registered")
        if status in RETIRED_HARNESS_STATUSES:
            continue
        harness_id = _required_str(harness, "id")
        roles = _role_tokens(harness.get("role"))
        if not roles:
            continue
        provider = _route_provider(harness)
        model_route = _model_route(harness)
        can_receive = harness.get("can_receive_dispatch") is True
        lifecycle = "shadow" if can_receive and status == "active" else "candidate"
        shadow_enabled = can_receive and status == "active"
        for role in roles:
            for activity_type in activity_types:
                activity = _normalize_token(activity_type)
                lane_id = lane_identity(
                    harness_id=harness_id,
                    provider=provider,
                    model_route=model_route,
                    role=role,
                    activity_type=activity,
                )
                lanes.append(
                    DispatchLane(
                        lane_id=lane_id,
                        harness_id=harness_id,
                        provider=provider,
                        model_route=model_route,
                        role=role,
                        activity_type=activity,
                        lifecycle=lifecycle,
                        dispatch_enabled=False,
                        shadow_enabled=shadow_enabled,
                        route_selectable=False,
                        blockage_reasons=() if shadow_enabled else ("harness_not_dispatch_ready",),
                        score_components={
                            "quality": _float_or_zero(harness.get("dispatch_quality")),
                            "availability": _float_or_zero(harness.get("dispatch_availability")),
                            "cost": _float_or_zero(harness.get("dispatch_cost")),
                        },
                        caps=_lane_caps(harness),
                    )
                )
    return tuple(lanes)


def lane_identity(
    *,
    harness_id: str,
    provider: str,
    model_route: str,
    role: str,
    activity_type: str,
) -> str:
    """Return deterministic lane identity for harness/provider/model/role/activity."""

    return ":".join(
        _slug_token(part)
        for part in (
            harness_id,
            provider,
            model_route,
            role,
            activity_type,
        )
    )


def build_compact_projection(
    lanes: Iterable[DispatchLane],
    *,
    production: bool = False,
    as_of: str | None = None,
    source_snapshot_id: str | None = None,
    required_evidence: Sequence[str] = REQUIRED_PRODUCTION_EVIDENCE,
) -> dict[str, Any]:
    """Render compact advisory/production lane projection payload.

    Production mode fails closed: a lane is ranked only when it is explicitly
    approved, dispatch-enabled, and backed by fresh required evidence.
    """

    generated_at = as_of or datetime.now(UTC).isoformat(timespec="seconds")
    ranked: dict[str, dict[str, list[dict[str, Any]]]] = {}
    blocked: list[dict[str, Any]] = []
    for lane in sorted(lanes, key=_lane_sort_key):
        reasons = production_blockage_reasons(lane, as_of=generated_at, required_evidence=required_evidence)
        if production and reasons:
            blocked.append(
                {"lane_id": lane.lane_id, "role": lane.role, "activity_type": lane.activity_type, "reasons": reasons}
            )
            continue
        if not production and not lane.shadow_enabled:
            blocked.append(
                {
                    "lane_id": lane.lane_id,
                    "role": lane.role,
                    "activity_type": lane.activity_type,
                    "reasons": tuple(lane.blockage_reasons or ("shadow_disabled",)),
                }
            )
            continue
        ranked.setdefault(lane.role, {}).setdefault(lane.activity_type, []).append(_compact_lane(lane))

    for role_map in ranked.values():
        for activity, lane_list in role_map.items():
            role_map[activity] = sorted(lane_list, key=lambda item: (-float(item["utility"]), item["lane_id"]))

    return {
        "schema_version": 1,
        "projection_mode": "production" if production else "shadow_advisory",
        "production_activation_enabled": production,
        "source_snapshot_id": source_snapshot_id,
        "generated_at": generated_at,
        "effective_ranked_lanes": ranked,
        "blocked_lanes": blocked,
        "freshness": {
            "as_of": generated_at,
            "required_evidence": list(required_evidence),
        },
        "runtime_suppression": {
            "production_fail_closed": bool(production and blocked),
            "raw_evidence_omitted": True,
        },
    }


def production_blockage_reasons(
    lane: DispatchLane,
    *,
    as_of: str | None = None,
    required_evidence: Sequence[str] = REQUIRED_PRODUCTION_EVIDENCE,
) -> tuple[str, ...]:
    """Return fail-closed production blockage reasons for a lane."""

    reasons: list[str] = []
    if lane.lifecycle not in PRODUCTION_READY_LIFECYCLES:
        reasons.append(f"lifecycle_not_approved:{lane.lifecycle}")
    if not lane.dispatch_enabled:
        reasons.append("dispatch_disabled")
    if lane.blockage_reasons:
        reasons.extend(lane.blockage_reasons)
    for evidence_type in required_evidence:
        evidence = lane.evidence_refs.get(evidence_type)
        if evidence is None:
            reasons.append(f"missing_required_evidence:{evidence_type}")
            continue
        status = _normalize_token(evidence.status)
        if status not in FRESH_EVIDENCE_STATUSES:
            reasons.append(f"stale_required_evidence:{evidence_type}")
            continue
        if evidence.expires_at and _is_expired(evidence.expires_at, as_of=as_of):
            reasons.append(f"stale_required_evidence:{evidence_type}")
    return tuple(dict.fromkeys(reasons))


def projection_is_compact(projection: Mapping[str, Any]) -> bool:
    """Return True when projection contains no raw evidence payload sections."""

    forbidden_keys = {"raw_evidence", "evidence_payload", "benchmark_samples", "transcript"}

    def has_forbidden_payload(value: Any) -> bool:
        if isinstance(value, Mapping):
            for key, child in value.items():
                key_text = str(key)
                if key_text in forbidden_keys:
                    return True
                if "raw_evidence" in key_text and key_text != "raw_evidence_omitted":
                    return True
                if has_forbidden_payload(child):
                    return True
        elif isinstance(value, list | tuple):
            return any(has_forbidden_payload(child) for child in value)
        return False

    return not has_forbidden_payload(projection)


def _projection_harnesses(projection: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    harnesses = projection.get("harnesses")
    if not isinstance(harnesses, list):
        return ()
    return tuple(h for h in harnesses if isinstance(h, Mapping))


def _role_tokens(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = [value]
        value = parsed
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(_normalize_token(role) for role in value if _normalize_token(role))


def _route_provider(harness: Mapping[str, Any]) -> str:
    return _normalize_token(
        harness.get("provider") or harness.get("harness_type") or harness.get("harness_name") or "unknown"
    )


def _model_route(harness: Mapping[str, Any]) -> str:
    explicit = harness.get("model_route") or harness.get("model") or harness.get("model_identifier")
    if explicit:
        return _normalize_token(explicit)
    harness_type = _normalize_token(harness.get("harness_type") or harness.get("harness_name") or "native")
    return f"{harness_type}-fixed"


def _lane_caps(harness: Mapping[str, Any]) -> dict[str, Any]:
    caps: dict[str, Any] = {}
    if harness.get("dispatch_max_items") is not None:
        caps["max_items"] = harness.get("dispatch_max_items")
    elif harness.get("max_items") is not None:
        caps["max_items"] = harness.get("max_items")
    return caps


def _compact_lane(lane: DispatchLane) -> dict[str, Any]:
    utility_components = {key: float(value) for key, value in lane.score_components.items()}
    utility = _utility_score(utility_components)
    return {
        "lane_id": lane.lane_id,
        "harness_id": lane.harness_id,
        "provider": lane.provider,
        "model_route": lane.model_route,
        "role": lane.role,
        "activity_type": lane.activity_type,
        "lifecycle": lane.lifecycle,
        "dispatch_enabled": lane.dispatch_enabled,
        "shadow_enabled": lane.shadow_enabled,
        "route_selectable": lane.route_selectable,
        "utility": utility,
        "utility_components": utility_components,
        "caps": dict(lane.caps),
        "evidence_ref_count": len(lane.evidence_refs),
        "waiver_id": lane.waiver_id,
    }


def _utility_score(components: Mapping[str, float]) -> float:
    quality = float(components.get("quality") or 0.0)
    availability = float(components.get("availability") or 0.0)
    cost = float(components.get("cost") or 0.0)
    return round(quality + availability - cost, 6)


def _lane_sort_key(lane: DispatchLane) -> tuple[str, str, str, str, str]:
    return (lane.role, lane.activity_type, lane.harness_id, lane.provider, lane.model_route)


def _required_str(mapping: Mapping[str, Any], key: str) -> str:
    value = str(mapping.get(key) or "").strip()
    if not value:
        raise ValueError(f"harness projection record is missing {key!r}")
    return value


def _normalize_token(value: object) -> str:
    return str(value or "").strip().lower()


def _slug_token(value: object) -> str:
    token = _normalize_token(value)
    return re.sub(r"[^a-z0-9_.-]+", "-", token).strip("-") or "unknown"


def _float_or_zero(value: object) -> float:
    try:
        return float(value) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _is_expired(expires_at: str, *, as_of: str | None) -> bool:
    expiry = _parse_time(expires_at)
    current = _parse_time(as_of) if as_of else datetime.now(UTC)
    return expiry <= current


def _parse_time(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


__all__ = [
    "DEFAULT_ACTIVITY_TYPES",
    "REQUIRED_PRODUCTION_EVIDENCE",
    "DispatchLane",
    "EvidenceRef",
    "build_compact_projection",
    "lane_identity",
    "lanes_from_harness_projection",
    "production_blockage_reasons",
    "projection_is_compact",
]
