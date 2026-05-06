"""Deterministic AUQ policy-gate engine."""

from __future__ import annotations

import hashlib
import json
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VALID_OUTCOMES = frozenset({"ALLOW", "WARN", "ASK", "DENY"})
DEFAULT_REGISTRY_RELATIVE = Path("config") / "agent-control" / "auq-policy-gates.toml"


@dataclass(frozen=True)
class PolicyRule:
    """One registry rule for an action class."""

    action: str
    outcome: str
    message: str
    adapter_installed: bool
    ask_options: tuple[str, ...] = ()


@dataclass(frozen=True)
class PolicyRegistry:
    """Parsed policy registry plus integrity hash."""

    schema_version: int
    registry_id: str
    registry_path: Path | None
    registry_hash: str
    actions: dict[str, PolicyRule]


@dataclass(frozen=True)
class ReceiptValidation:
    """Validation result for a scoped approval receipt."""

    valid: bool
    reason: str

    def to_json_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "reason": self.reason}


@dataclass(frozen=True)
class PolicyDecision:
    """Deterministic policy decision output."""

    action: str
    scope: str
    paths: tuple[str, ...]
    outcome: str
    message: str
    ask_options: tuple[str, ...]
    adapter_installed: bool
    registry_hash: str
    registry_path: str | None
    receipt: ReceiptValidation
    reasons: tuple[str, ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "scope": self.scope,
            "paths": list(self.paths),
            "outcome": self.outcome,
            "message": self.message,
            "ask_options": list(self.ask_options),
            "adapter_installed": self.adapter_installed,
            "registry_hash": self.registry_hash,
            "registry_path": self.registry_path,
            "receipt": self.receipt.to_json_dict(),
            "reasons": list(self.reasons),
        }


def load_policy_registry(path: Path | None = None, *, start: Path | None = None) -> PolicyRegistry:
    """Load the AUQ policy registry from an explicit path or parent search."""
    registry_path = _resolve_registry_path(path, start=start or Path.cwd())
    if registry_path is None:
        raise FileNotFoundError(f"policy registry not found at {DEFAULT_REGISTRY_RELATIVE}")
    _reject_archive_path(registry_path)
    text = registry_path.read_text(encoding="utf-8")
    data = tomllib.loads(text)
    return _parse_registry(data, registry_path=registry_path, registry_hash=_hash_text(text))


def check_policy(
    *,
    action: str,
    scope: str,
    paths: tuple[Path, ...] = (),
    registry: PolicyRegistry,
    receipt: dict[str, Any] | None = None,
    now: float | None = None,
) -> PolicyDecision:
    """Evaluate a policy decision without installing any operational adapter."""
    action = action.strip()
    scope = scope.strip()
    if action not in registry.actions:
        raise ValueError(f"unknown policy action {action!r}")
    rule = registry.actions[action]
    normalized_paths = _normalize_paths(paths)
    path_reasons = _path_reasons(scope, normalized_paths)
    receipt_validation = validate_receipt(
        receipt,
        action=action,
        scope=scope,
        paths=normalized_paths,
        registry_hash=registry.registry_hash,
        now=now,
    )

    outcome = rule.outcome
    message = rule.message
    reasons = list(path_reasons)
    if any(reason.startswith("archive path") for reason in path_reasons):
        outcome = "DENY"
        message = "Archive paths must not be treated as live GT-KB artifacts."
    elif any(reason.startswith("platform path") for reason in path_reasons):
        outcome = "DENY"
        message = "Application-scope action targets a platform-owned path."
    elif outcome == "ASK" and receipt_validation.valid:
        outcome = "ALLOW"
        message = "Scoped approval receipt accepted."
        reasons.append("valid approval receipt")

    return PolicyDecision(
        action=action,
        scope=scope,
        paths=normalized_paths,
        outcome=outcome,
        message=message,
        ask_options=rule.ask_options if outcome == "ASK" else (),
        adapter_installed=rule.adapter_installed,
        registry_hash=registry.registry_hash,
        registry_path=str(registry.registry_path) if registry.registry_path else None,
        receipt=receipt_validation,
        reasons=tuple(reasons),
    )


def validate_receipt(
    receipt: object | None,
    *,
    action: str,
    scope: str,
    paths: tuple[str, ...],
    registry_hash: str,
    now: float | None = None,
) -> ReceiptValidation:
    """Validate a scoped approval receipt for one action invocation."""
    if receipt is None:
        return ReceiptValidation(False, "receipt absent")
    if not isinstance(receipt, dict):
        return ReceiptValidation(False, "receipt must be an object")
    current_time = now if now is not None else time.time()
    if receipt.get("action") != action:
        return ReceiptValidation(False, "action mismatch")
    if receipt.get("scope") != scope:
        return ReceiptValidation(False, "scope mismatch")
    if tuple(receipt.get("paths", [])) != paths:
        return ReceiptValidation(False, "path mismatch")
    if receipt.get("registry_hash") != registry_hash:
        return ReceiptValidation(False, "registry hash mismatch")
    expires_at = receipt.get("expires_at")
    if not isinstance(expires_at, int | float):
        return ReceiptValidation(False, "expiry missing")
    if expires_at <= current_time:
        return ReceiptValidation(False, "receipt expired")
    return ReceiptValidation(True, "receipt valid")


def _resolve_registry_path(path: Path | None, *, start: Path) -> Path | None:
    if path is not None:
        return path.resolve()
    current = start.resolve()
    for candidate_root in (current, *current.parents):
        candidate = candidate_root / DEFAULT_REGISTRY_RELATIVE
        if candidate.exists():
            return candidate
    return None


def _parse_registry(data: dict[str, Any], *, registry_path: Path, registry_hash: str) -> PolicyRegistry:
    schema_version = int(data.get("schema_version", 0))
    if schema_version != 1:
        raise ValueError(f"unsupported policy registry schema_version={schema_version!r}")
    registry_id = str(data.get("registry_id", "")).strip()
    if not registry_id:
        raise ValueError("policy registry requires registry_id")
    raw_actions = data.get("actions", {})
    if not isinstance(raw_actions, dict) or not raw_actions:
        raise ValueError("policy registry requires [actions.*] entries")

    actions: dict[str, PolicyRule] = {}
    for action, raw_rule in raw_actions.items():
        if not isinstance(raw_rule, dict):
            raise ValueError(f"action {action!r} must be a table")
        outcome = str(raw_rule.get("outcome", "")).upper()
        if outcome not in VALID_OUTCOMES:
            raise ValueError(f"action {action!r} has invalid outcome {outcome!r}")
        ask_options = tuple(str(option) for option in raw_rule.get("ask_options", ()))
        if outcome == "ASK" and not 2 <= len(ask_options) <= 3:
            raise ValueError(f"ASK action {action!r} must define two to three ask_options")
        actions[action] = PolicyRule(
            action=action,
            outcome=outcome,
            message=str(raw_rule.get("message", "")).strip(),
            adapter_installed=bool(raw_rule.get("adapter_installed", False)),
            ask_options=ask_options,
        )
    return PolicyRegistry(
        schema_version=schema_version,
        registry_id=registry_id,
        registry_path=registry_path,
        registry_hash=registry_hash,
        actions=actions,
    )


def _normalize_paths(paths: tuple[Path, ...]) -> tuple[str, ...]:
    return tuple(sorted(str(path.resolve()) for path in paths))


def _path_reasons(scope: str, paths: tuple[str, ...]) -> tuple[str, ...]:
    reasons: list[str] = []
    for path in paths:
        normalized = path.replace("/", "\\").lower()
        if "\\claude-playground" in normalized:
            reasons.append(f"archive path: {path}")
        if scope == "application" and "\\groundtruth-kb\\src\\groundtruth_kb\\" in normalized:
            reasons.append(f"platform path in application scope: {path}")
        if scope == "application" and "\\config\\agent-control\\" in normalized:
            reasons.append(f"platform path in application scope: {path}")
    return tuple(reasons)


def _reject_archive_path(path: Path) -> None:
    normalized = str(path).replace("/", "\\").lower()
    if "\\claude-playground" in normalized:
        raise ValueError(f"{path} is an archive path and must not be used as the policy registry")


def _hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_receipt(path: Path | None) -> dict[str, Any] | None:
    """Load a receipt JSON file when supplied."""
    if path is None:
        return None
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"receipt JSON at {path} must be an object")
    return {str(key): value for key, value in loaded.items()}
