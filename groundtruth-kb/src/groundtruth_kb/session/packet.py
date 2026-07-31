"""Deterministic session-envelope and activity-packet composition service."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from groundtruth_kb.activity.profiles import CANONICAL_ACTIVITY_ORDER, load_activity_profiles
from groundtruth_kb.context.manifest import (
    ACTIVITY_PROFILES_RELATIVE_PATH,
    ACTIVITY_SHARDING_RELATIVE_PATH,
    assemble_context_manifest,
    resolve_context_registry,
)

SESSION_PACKET_KIND = "session-envelope"
ACTIVITY_PACKET_KIND = "activity-packet"
SESSION_ENVELOPE_TOKEN_CAP = 900
ACTIVITY_PACKET_TOKEN_CAP = 500
DEFAULT_CACHE_TTL_SECONDS = 300
DEFAULT_CACHE_RELATIVE_PATH = Path(".gtkb-state/session-envelope/packet-cache")

_PACKET_KIND_ALIASES = {
    "session": SESSION_PACKET_KIND,
    SESSION_PACKET_KIND: SESSION_PACKET_KIND,
    "activity": ACTIVITY_PACKET_KIND,
    ACTIVITY_PACKET_KIND: ACTIVITY_PACKET_KIND,
}

_STARTUP_SOURCE_PATHS = (
    ("session-startup-index", Path("config/agent-control/SESSION-STARTUP-INDEX.md")),
    ("prime-builder-startup-overlay", Path("config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md")),
    ("loyal-opposition-startup-overlay", Path("config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md")),
)


class PacketError(ValueError):
    """Raised when a packet request cannot be composed deterministically."""


def compose_packet(
    *,
    project_root: Path,
    packet_kind: str = SESSION_PACKET_KIND,
    activity: str | None = None,
    role: str = "prime-builder",
    ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    cache_dir: Path | None = None,
    refresh: bool = False,
    generated_at: datetime | None = None,
    budget_cap_tokens: int | None = None,
) -> dict[str, Any]:
    """Compose a budgeted packet, using a TTL/source-hash-valid cache when possible."""

    root = project_root.resolve()
    kind = _normalize_packet_kind(packet_kind)
    if ttl_seconds <= 0:
        raise PacketError("ttl_seconds must be a positive integer")
    if kind == ACTIVITY_PACKET_KIND:
        if activity is None:
            raise PacketError("activity is required for activity-packet requests")
        if activity not in CANONICAL_ACTIVITY_ORDER:
            raise PacketError(f"activity must be one of {list(CANONICAL_ACTIVITY_ORDER)}")
    elif activity is not None:
        raise PacketError("activity is only valid for activity-packet requests")
    if not isinstance(role, str) or not role.strip():
        raise PacketError("role is required")

    now = _utc(generated_at)
    expires_at = now + timedelta(seconds=ttl_seconds)
    cache_root = (cache_dir or root / DEFAULT_CACHE_RELATIVE_PATH).resolve()
    sources, source_hashes = _collect_sources(root, include_startup=kind == SESSION_PACKET_KIND)
    request = {
        "schema_version": 1,
        "packet_kind": kind,
        "activity": activity,
        "role": role.strip(),
        "ttl_seconds": ttl_seconds,
        "source_hashes": source_hashes,
        "budget_cap_tokens": budget_cap_tokens,
    }
    cache_key = _sha256_json(request)[:32]
    cache_path = cache_root / f"{cache_key}.json"

    if not refresh:
        cached = _read_valid_cache(cache_path, request=request, source_hashes=source_hashes, now=now)
        if cached is not None:
            packet = deepcopy(cached)
            packet.setdefault("cache", {})
            packet["cache"].update(
                {
                    "hit": True,
                    "status": "hit",
                    "cache_path": _display_path(cache_path, root),
                }
            )
            return _with_estimated_tokens(packet)

    packet = _build_packet(
        root=root,
        kind=kind,
        activity=activity,
        role=role.strip(),
        ttl_seconds=ttl_seconds,
        generated_at=now,
        expires_at=expires_at,
        cache_key=cache_key,
        cache_path=cache_path,
        source_pointers=sources,
        source_hashes=source_hashes,
        budget_cap_tokens=budget_cap_tokens,
    )
    _write_cache(
        cache_path,
        {
            "schema_version": 1,
            "request": request,
            "source_hashes": source_hashes,
            "created_at": _iso(now),
            "expires_at": _iso(expires_at),
            "packet": packet,
        },
    )
    return packet


def estimated_token_count(payload: dict[str, Any]) -> int:
    """Return the deterministic approximate token count used by packet budgets."""

    byte_count = len(_canonical_json(payload))
    return max(1, (byte_count + 3) // 4)


def _build_packet(
    *,
    root: Path,
    kind: str,
    activity: str | None,
    role: str,
    ttl_seconds: int,
    generated_at: datetime,
    expires_at: datetime,
    cache_key: str,
    cache_path: Path,
    source_pointers: list[dict[str, Any]],
    source_hashes: dict[str, str],
    budget_cap_tokens: int | None,
) -> dict[str, Any]:
    cap = budget_cap_tokens or (
        SESSION_ENVELOPE_TOKEN_CAP if kind == SESSION_PACKET_KIND else ACTIVITY_PACKET_TOKEN_CAP
    )
    live_query_descriptors = (
        _activity_live_query_descriptors(root, activity, role) if activity else _baseline_live_queries()
    )
    payload = _session_payload(root) if kind == SESSION_PACKET_KIND else _activity_payload(root, activity, role)
    packet = {
        "schema_version": 1,
        "packet_kind": kind,
        "status": "ready",
        "activity": activity,
        "generated_at": _iso(generated_at),
        "ttl": {
            "seconds": ttl_seconds,
            "expires_at": _iso(expires_at),
            "frame": "stable_frame_fetch_cache",
            "cache_is_authority": False,
        },
        "budget": {
            "cap_estimated_tokens": cap,
            "estimated_tokens": 0,
            "estimator": "ceil(canonical_json_bytes/4)",
        },
        "cache": {
            "hit": False,
            "status": "miss",
            "cache_key": cache_key,
            "cache_path": _display_path(cache_path, root),
            "expires_at": _iso(expires_at),
        },
        "source_pointers": source_pointers,
        "source_hashes": source_hashes,
        "live_query_descriptors": live_query_descriptors,
        "payload": payload,
    }
    packet = _with_estimated_tokens(packet)
    if packet["budget"]["estimated_tokens"] <= cap:
        return packet
    return _pointer_only_packet(packet, cap=cap)


def _session_payload(root: Path) -> dict[str, Any]:
    profiles = _load_profiles_for_root(root)
    return {
        "composition_policy": "minimal",
        "canonical_activities": list(CANONICAL_ACTIVITY_ORDER),
        "activity_headless_eligibility": {name: profile.headless_eligibility for name, profile in profiles.items()},
        "live_state_policy": "fresh-read-only",
        "activity_packet_surface": "gt session envelope packet --kind activity-packet --activity <activity>",
    }


def _activity_payload(root: Path, activity: str | None, role: str) -> dict[str, Any]:
    if activity is None:
        raise PacketError("activity is required for activity-packet requests")
    manifest = assemble_context_manifest(activity=activity, role=role, project_root=root)
    profile = _load_profiles_for_root(root)[activity]
    disposition_counts = {
        "embedded": sum(1 for item in manifest["items"] if item["disposition"] == "embedded"),
        "live_query_only": sum(1 for item in manifest["items"] if item["disposition"] == "live-query-only"),
    }
    return {
        "manifest": {
            "registry_version": manifest["registry_version"],
            "active_activity": manifest["active_activity"],
            "role": manifest["role_bootstrap"]["role"],
            "token_budget": manifest["token_budget"],
            "disposition_counts": disposition_counts,
        },
        "profile": {
            "name": profile.name,
            "version": profile.version,
            "headless_eligibility": profile.headless_eligibility,
            "skills_count": len(profile.skills),
            "terminology_count": len(profile.terminology),
        },
    }


def _pointer_only_packet(packet: dict[str, Any], *, cap: int) -> dict[str, Any]:
    pointer_packet = {
        key: value
        for key, value in packet.items()
        if key
        in {
            "schema_version",
            "packet_kind",
            "activity",
            "generated_at",
            "ttl",
            "cache",
            "source_pointers",
            "source_hashes",
            "live_query_descriptors",
        }
    }
    pointer_packet["status"] = "over_budget_pointer_only"
    pointer_packet["budget"] = {
        "cap_estimated_tokens": cap,
        "candidate_estimated_tokens": packet["budget"]["estimated_tokens"],
        "estimated_tokens": 0,
        "estimator": "ceil(canonical_json_bytes/4)",
    }
    pointer_packet["diagnostic"] = {
        "reason": "packet_budget_exceeded",
        "pointer_only": True,
        "omitted_payload": "payload",
    }
    pointer_packet = _with_estimated_tokens(pointer_packet)
    if pointer_packet["budget"]["estimated_tokens"] <= cap:
        return pointer_packet
    minimal = {
        "schema_version": 1,
        "packet_kind": packet["packet_kind"],
        "activity": packet.get("activity"),
        "status": "over_budget_pointer_only",
        "generated_at": packet["generated_at"],
        "budget": {
            "cap_estimated_tokens": cap,
            "candidate_estimated_tokens": packet["budget"]["estimated_tokens"],
            "estimated_tokens": 0,
            "estimator": "ceil(canonical_json_bytes/4)",
        },
        "diagnostic": {"reason": "packet_budget_exceeded", "pointer_only": True},
    }
    return _with_estimated_tokens(minimal)


def _baseline_live_queries() -> list[dict[str, str]]:
    return [
        {
            "source_id": "bridge-thread-state",
            "authority_class": "canonical_live_state",
            "read_route": "gt bridge state-report --json",
            "cache_policy": "live_query_only",
        },
        {
            "source_id": "membase-project-and-backlog-state",
            "authority_class": "canonical_live_state",
            "read_route": "gt projects list; gt backlog list",
            "cache_policy": "live_query_only",
        },
        {
            "source_id": "git-worktree-state",
            "authority_class": "runtime_attestation",
            "read_route": "git status --short",
            "cache_policy": "live_query_only",
        },
    ]


def _activity_live_query_descriptors(root: Path, activity: str | None, role: str) -> list[dict[str, str]]:
    if activity is None:
        return _baseline_live_queries()
    manifest = assemble_context_manifest(activity=activity, role=role, project_root=root)
    descriptors: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in manifest["items"]:
        if item["disposition"] != "live-query-only":
            continue
        key = (item["source_id"], item["read_route"])
        if key in seen:
            continue
        seen.add(key)
        descriptors.append(
            {
                "source_id": item["source_id"],
                "read_route": item["read_route"],
                "cache_policy": "live_query_only",
            }
        )
    return descriptors


def _collect_sources(root: Path, *, include_startup: bool) -> tuple[list[dict[str, str]], dict[str, str]]:
    resolution = resolve_context_registry(project_root=root)
    paths: list[tuple[str, Path]] = list(_STARTUP_SOURCE_PATHS) if include_startup else []
    paths.extend(
        (
            ("context-manifest-registry", resolution.registry_path),
            ("activity-disposition-profiles", resolution.source_root / ACTIVITY_PROFILES_RELATIVE_PATH),
            ("activity-envelope-sharding", resolution.source_root / ACTIVITY_SHARDING_RELATIVE_PATH),
        )
    )
    sources: list[dict[str, str]] = []
    source_hashes: dict[str, str] = {}
    seen: set[str] = set()
    for source_id, path in paths:
        if source_id in seen:
            continue
        seen.add(source_id)
        resolved = path if path.is_absolute() else root / path
        sources.append(
            {
                "source_id": source_id,
                "path": _display_path(resolved, root),
            }
        )
        source_hashes[source_id] = f"sha256:{_sha256_file(resolved)}" if resolved.is_file() else "missing"
    return sources, source_hashes


def _load_profiles_for_root(root: Path) -> dict[str, Any]:
    resolution = resolve_context_registry(project_root=root)
    return load_activity_profiles(
        path=resolution.source_root / ACTIVITY_PROFILES_RELATIVE_PATH,
        sharding_path=resolution.source_root / ACTIVITY_SHARDING_RELATIVE_PATH,
    )


def _read_valid_cache(
    cache_path: Path,
    *,
    request: dict[str, Any],
    source_hashes: dict[str, str],
    now: datetime,
) -> dict[str, Any] | None:
    try:
        entry = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(entry, dict):
        return None
    if entry.get("request") != request or entry.get("source_hashes") != source_hashes:
        return None
    expires_at = _parse_iso(entry.get("expires_at"))
    if expires_at is None or expires_at <= now:
        return None
    packet = entry.get("packet")
    return packet if isinstance(packet, dict) else None


def _write_cache(cache_path: Path, entry: dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(_canonical_json(entry) + b"\n")


def _normalize_packet_kind(packet_kind: str) -> str:
    kind = _PACKET_KIND_ALIASES.get(packet_kind)
    if kind is None:
        raise PacketError(f"packet_kind must be one of {sorted(_PACKET_KIND_ALIASES)}")
    return kind


def _with_estimated_tokens(packet: dict[str, Any]) -> dict[str, Any]:
    stabilized = deepcopy(packet)
    for _ in range(4):
        estimate = estimated_token_count(stabilized)
        if stabilized["budget"].get("estimated_tokens") == estimate:
            return stabilized
        stabilized["budget"]["estimated_tokens"] = estimate
    return stabilized


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha256_json(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display_path(path: Path, root: Path) -> str:
    package_root = Path(__file__).resolve().parents[1]
    try:
        return f"package:{path.resolve().relative_to(package_root).as_posix()}"
    except ValueError:
        pass
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _utc(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    return value.astimezone(UTC) if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None
