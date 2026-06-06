"""Check and maintain the bridge/INDEX.md role-intent sentinel.

Slice 1 only: this script maintains a non-authoritative checksum mirror in
``bridge/INDEX.md``. Durable role authority is ``harness-state/harness-registry.json``
(canonical role registry per Slice 1 retirement) plus
``harness-state/harness-identities.json``. The legacy
retired role mirror is orphan/compat and is not
authoritative.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

ROLE_PRIME = "prime-builder"
ROLE_LOYAL = "loyal-opposition"
ROLE_ACTING_PRIME = "acting-prime-builder"
SENTINEL_TITLE = "Role-intent sentinel (per GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL, Slice 1; NON-AUTHORITATIVE)"
SENTINEL_RE = re.compile(
    r"<!-- Role-intent sentinel \(per GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL,"
    r" Slice 1; NON-AUTHORITATIVE\):\n.*?^-->",
    re.MULTILINE | re.DOTALL,
)
FIELD_RE = re.compile(r"^\s*(?P<key>[^:]+):\s*(?P<value>.*?)\s*$")


@dataclass(frozen=True)
class RoleIntentState:
    prime_harness_id: str | None
    prime_harness_name: str | None
    loyal_harness_id: str | None
    loyal_harness_name: str | None
    topology: str


@dataclass(frozen=True)
class Sentinel:
    prime_harness_id: str | None
    loyal_harness_id: str | None
    topology: str
    updated_at: datetime


def project_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def normalize_role_field(raw: Any) -> frozenset[str]:
    if raw is None or raw == "":
        return frozenset()
    if isinstance(raw, str):
        token = raw.strip().lower()
        return frozenset({token}) if token in {ROLE_PRIME, ROLE_LOYAL, ROLE_ACTING_PRIME} else frozenset()
    if isinstance(raw, (list, tuple, set, frozenset)):
        tokens = {
            str(value).strip().lower()
            for value in raw
            if str(value).strip().lower() in {ROLE_PRIME, ROLE_LOYAL, ROLE_ACTING_PRIME}
        }
        return frozenset(tokens)
    return frozenset()


def identity_names(identity_doc: dict[str, Any]) -> dict[str, str]:
    harnesses = identity_doc.get("harnesses")
    if not isinstance(harnesses, dict):
        return {}
    names: dict[str, str] = {}
    for raw_name, raw_record in harnesses.items():
        if not isinstance(raw_record, dict):
            continue
        harness_id = str(raw_record.get("id") or "").strip()
        if harness_id:
            names[harness_id] = str(raw_name).strip()
    return names


def display_name(
    harness_id: str | None, names_by_id: dict[str, str], role_record: dict[str, Any] | None = None
) -> str | None:
    if not harness_id:
        return None
    name = names_by_id.get(harness_id)
    if not name and role_record:
        name = str(role_record.get("harness_type") or "").strip()
    return name.title() if name else harness_id


def build_role_intent_state(
    role_doc: dict[str, Any],
    identity_doc: dict[str, Any],
) -> RoleIntentState:
    harnesses = role_doc.get("harnesses")
    if not isinstance(harnesses, dict):
        harnesses = {}
    names_by_id = identity_names(identity_doc)

    prime_ids: list[str] = []
    loyal_ids: list[str] = []
    for raw_id, raw_record in harnesses.items():
        if not isinstance(raw_record, dict):
            continue
        harness_id = str(raw_id).strip()
        role_set = normalize_role_field(raw_record.get("role"))
        if ROLE_PRIME in role_set or ROLE_ACTING_PRIME in role_set:
            prime_ids.append(harness_id)
        if ROLE_LOYAL in role_set:
            loyal_ids.append(harness_id)

    prime_id = sorted(prime_ids)[0] if prime_ids else None
    loyal_id = sorted(loyal_ids)[0] if loyal_ids else None
    if prime_id and loyal_id and prime_id == loyal_id:
        topology = "single_harness"
    elif prime_id and loyal_id:
        topology = "multi_harness"
    elif prime_id:
        topology = "prime_only"
    elif loyal_id:
        topology = "loyal_opposition_only"
    else:
        topology = "unassigned"

    prime_record = harnesses.get(prime_id) if isinstance(harnesses.get(prime_id), dict) else None
    loyal_record = harnesses.get(loyal_id) if isinstance(harnesses.get(loyal_id), dict) else None
    return RoleIntentState(
        prime_harness_id=prime_id,
        prime_harness_name=display_name(prime_id, names_by_id, prime_record),
        loyal_harness_id=loyal_id,
        loyal_harness_name=display_name(loyal_id, names_by_id, loyal_record),
        topology=topology,
    )


def format_harness(harness_id: str | None, harness_name: str | None) -> str:
    if not harness_id:
        return "none"
    if harness_name:
        return f"{harness_id} ({harness_name})"
    return harness_id


def render_sentinel(state: RoleIntentState, *, updated_at: datetime | None = None) -> str:
    updated = updated_at or datetime.now(UTC).replace(microsecond=0)
    timestamp = updated.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return (
        f"<!-- {SENTINEL_TITLE}:\n"
        "     Authority: harness-state/harness-registry.json (role; canonical registry per Slice 1 retirement) + "
        "harness-state/harness-identities.json (identity).\n"
        "     This sentinel is a checksum mirror only. "
        "It MUST NOT be used to override the durable role record.\n"
        f"     Prime Builder harness:    {format_harness(state.prime_harness_id, state.prime_harness_name)}\n"
        f"     Loyal Opposition harness: {format_harness(state.loyal_harness_id, state.loyal_harness_name)}\n"
        f"     Topology:                 {state.topology}\n"
        f"     Sentinel updated:         {timestamp}\n"
        "-->"
    )


def sentinel_bounds(index_text: str) -> tuple[int, int] | None:
    match = SENTINEL_RE.search(index_text)
    if not match:
        return None
    return match.start(), match.end()


def extract_sentinel_text(index_text: str) -> str | None:
    bounds = sentinel_bounds(index_text)
    if not bounds:
        return None
    return index_text[bounds[0] : bounds[1]]


def _field_map(sentinel_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in sentinel_text.splitlines():
        match = FIELD_RE.match(line.strip(" <-!>"))
        if match:
            fields[match.group("key").strip()] = match.group("value").strip()
    return fields


def _parse_harness_value(value: str) -> str | None:
    if value.lower() == "none":
        return None
    token = value.split(" ", 1)[0].strip()
    return token or None


def parse_sentinel(index_text: str) -> Sentinel:
    sentinel_text = extract_sentinel_text(index_text)
    if sentinel_text is None:
        raise ValueError("bridge/INDEX.md role-intent sentinel is missing")
    fields = _field_map(sentinel_text)
    missing = [
        key
        for key in [
            "Prime Builder harness",
            "Loyal Opposition harness",
            "Topology",
            "Sentinel updated",
        ]
        if key not in fields
    ]
    if missing:
        raise ValueError(f"bridge/INDEX.md role-intent sentinel is malformed; missing: {', '.join(missing)}")
    timestamp = fields["Sentinel updated"]
    try:
        updated_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"bridge/INDEX.md role-intent sentinel timestamp is invalid: {timestamp}") from exc
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=UTC)
    return Sentinel(
        prime_harness_id=_parse_harness_value(fields["Prime Builder harness"]),
        loyal_harness_id=_parse_harness_value(fields["Loyal Opposition harness"]),
        topology=fields["Topology"],
        updated_at=updated_at.astimezone(UTC),
    )


def validate_sentinel(
    index_text: str,
    expected: RoleIntentState,
    *,
    now: datetime | None = None,
    freshness_days: int = 7,
) -> list[str]:
    errors: list[str] = []
    try:
        sentinel = parse_sentinel(index_text)
    except ValueError as exc:
        return [str(exc)]

    current_time = now or datetime.now(UTC)
    if sentinel.updated_at < current_time.astimezone(UTC) - timedelta(days=freshness_days):
        errors.append(
            "bridge/INDEX.md role-intent sentinel is stale; run "
            "`python scripts/check_index_role_intent_sentinel.py --update`"
        )
    if sentinel.prime_harness_id != expected.prime_harness_id:
        errors.append(
            "Prime Builder harness mismatch: sentinel="
            f"{sentinel.prime_harness_id or 'none'} durable={expected.prime_harness_id or 'none'}"
        )
    if sentinel.loyal_harness_id != expected.loyal_harness_id:
        errors.append(
            "Loyal Opposition harness mismatch: sentinel="
            f"{sentinel.loyal_harness_id or 'none'} durable={expected.loyal_harness_id or 'none'}"
        )
    if sentinel.topology != expected.topology:
        errors.append(f"Topology mismatch: sentinel={sentinel.topology} durable={expected.topology}")
    return errors


def insert_or_replace_sentinel(index_text: str, sentinel_text: str) -> str:
    bounds = sentinel_bounds(index_text)
    if bounds:
        return index_text[: bounds[0]] + sentinel_text + index_text[bounds[1] :]

    lines = index_text.splitlines(keepends=True)
    insert_at = 0
    for index, line in enumerate(lines):
        if line.startswith("Document:"):
            insert_at = index
            break
    else:
        insert_at = len(lines)

    prefix = "".join(lines[:insert_at]).rstrip() + "\n"
    suffix = "".join(lines[insert_at:])
    return f"{prefix}{sentinel_text}\n{suffix}"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", newline="\n", delete=False, dir=path.parent) as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def update_index(index_path: Path, state: RoleIntentState, *, updated_at: datetime | None = None) -> str:
    original = index_path.read_text(encoding="utf-8")
    updated = insert_or_replace_sentinel(original, render_sentinel(state, updated_at=updated_at))
    atomic_write(index_path, updated)
    return updated


def latest_statuses(index_text: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    current_doc: str | None = None
    for raw_line in index_text.splitlines():
        line = raw_line.strip()
        if line.startswith("Document:"):
            current_doc = line.removeprefix("Document:").strip()
            continue
        if current_doc and re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED):", line):
            statuses.setdefault(current_doc, line.split(":", 1)[0])
    return statuses


def counts_output(index_text: str) -> str:
    statuses = latest_statuses(index_text)
    prime_count = sum(1 for status in statuses.values() if status in {"GO", "NO-GO"})
    lo_count = sum(1 for status in statuses.values() if status in {"NEW", "REVISED", "ADVISORY"})
    return f"active_prime_authorization_count={prime_count}\nactive_lo_advisory_count={lo_count}\n"


def _role_doc_from_registry(registry_doc: dict) -> dict:
    """Adapt the registry list-of-dicts schema to the dict-keyed-by-id schema
    that ``build_role_intent_state()`` consumes.

    ``harness-state/harness-registry.json`` is the canonical role registry per
    Slice 1 retirement of the orphan role mirror. Its
    ``harnesses`` field is a list of dicts (one per harness id). The legacy
    role-mirror format was a flat dict keyed by harness id, which
    ``build_role_intent_state()`` expects. This adapter bridges the two without
    requiring an API change to the existing builder.
    """
    harnesses_list = registry_doc.get("harnesses") or []
    harnesses_dict: dict = {}
    if isinstance(harnesses_list, list):
        for entry in harnesses_list:
            if isinstance(entry, dict):
                hid = str(entry.get("id") or "").strip()
                if hid:
                    harnesses_dict[hid] = entry
    return {"harnesses": harnesses_dict}


def state_from_files(project_root: Path) -> RoleIntentState:
    return build_role_intent_state(
        _role_doc_from_registry(load_json(project_root / "harness-state" / "harness-registry.json")),
        load_json(project_root / "harness-state" / "harness-identities.json"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=project_root_from_script())
    parser.add_argument("--index-path", type=Path)
    parser.add_argument("--freshness-days", type=int, default=7)
    parser.add_argument("--update", action="store_true", help="Rewrite the sentinel from durable role authority.")
    parser.add_argument("--counts", action="store_true", help="Print live advisory counts without writing INDEX.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root.resolve()
    index_path = args.index_path or project_root / "bridge" / "INDEX.md"
    state = state_from_files(project_root)

    if args.counts:
        sys.stdout.write(counts_output(index_path.read_text(encoding="utf-8")))
        return 0

    if args.update:
        update_index(index_path, state)
        print(f"Updated role-intent sentinel in {index_path}")
        return 0

    errors = validate_sentinel(
        index_path.read_text(encoding="utf-8"),
        state,
        freshness_days=args.freshness_days,
    )
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("bridge/INDEX.md role-intent sentinel is present, fresh, and consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
