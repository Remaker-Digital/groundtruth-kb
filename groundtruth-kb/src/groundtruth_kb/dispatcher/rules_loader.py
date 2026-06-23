"""Dispatch-envelope rules registry loader."""

from __future__ import annotations

import json
import re
import tomllib
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BARE_ENVELOPE_RE = re.compile(r"(?<!dispatch-)(?<!session-)(?<!topic-)\benvelope\b", re.IGNORECASE)


class DispatchRuleError(RuntimeError):
    """Raised when dispatch rules are missing or invalid."""


@dataclass(frozen=True)
class DispatchRule:
    id: str
    trigger: str
    target: str
    activity_gate: str
    payload: dict[str, Any]
    persist: bool = False


def default_rules_path(project_root: Path) -> Path:
    return project_root / "config" / "dispatcher" / "rules.toml"


def _validate_rule(raw: dict[str, Any], index: int) -> DispatchRule:
    missing = [key for key in ("id", "trigger", "target", "activity_gate", "payload") if key not in raw]
    if missing:
        raise DispatchRuleError(f"Rule {index} missing required key(s): {', '.join(missing)}")
    payload = raw["payload"]
    if not isinstance(payload, dict):
        raise DispatchRuleError(f"Rule {index} payload must be a table/object")
    activity_gate = str(raw["activity_gate"]).strip()
    if not activity_gate:
        raise DispatchRuleError(f"Rule {index} activity_gate must be non-empty")
    text = " ".join(
        [
            *(str(raw.get(key, "")) for key in ("id", "trigger", "target", "activity_gate")),
            json.dumps(payload, sort_keys=True),
        ]
    )
    if BARE_ENVELOPE_RE.search(text):
        warnings.warn(
            f"Rule {index} uses bare 'envelope'; use dispatch-envelope terminology",
            stacklevel=2,
        )
    return DispatchRule(
        id=str(raw["id"]),
        trigger=str(raw["trigger"]),
        target=str(raw["target"]),
        activity_gate=activity_gate,
        payload=payload,
        persist=bool(raw.get("persist", False)),
    )


def validate_rules(data: dict[str, Any]) -> list[DispatchRule]:
    raw_rules = data.get("rules", [])
    if raw_rules is None:
        return []
    if not isinstance(raw_rules, list):
        raise DispatchRuleError("rules must be a list")
    rules: list[DispatchRule] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_rules, start=1):
        if not isinstance(raw, dict):
            raise DispatchRuleError(f"Rule {index} must be a table/object")
        # Skip bridge rules (which are handled separately by bridge_dispatch_config)
        if (
            "trigger" not in raw
            and "target" not in raw
            and "activity_gate" not in raw
            and ("required_roles" in raw or "statuses" in raw or "prefer" in raw)
        ):
            continue
        rule = _validate_rule(raw, index)
        if rule.id in seen_ids:
            raise DispatchRuleError(f"Rule {index} duplicates id {rule.id!r}")
        seen_ids.add(rule.id)
        rules.append(rule)
    return rules


def load_rules(path: Path) -> list[DispatchRule]:
    if not path.is_file():
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise DispatchRuleError(f"Invalid TOML in {path}: {exc}") from exc
    return validate_rules(data)
