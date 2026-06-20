#!/usr/bin/env python3
"""Read-only protocol enforcement health reporter for GT-KB."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATUS_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)$")
VERSIONED_BRIDGE_RE = re.compile(r"^(?P<slug>.+?)-(?P<version>\d{3,})\.md$")

STATE_DIR = Path(".gtkb-state/protocol-enforcement")
IMPLEMENTATION_PACKET_DIR = Path(".gtkb-state/implementation-authorizations/by-bridge")
POST_ACTION_RECEIPTS_DIR = Path(".gtkb-state/post-action-receipts")

PRIME_ACTIONABLE = frozenset({"GO", "NO-GO"})
LOYAL_OPPOSITION_ACTIONABLE = frozenset({"NEW", "REVISED"})

PROTECTED_BLOCK_NEXT_ACTIONS = {
    "missing_bridge_go": "restore_bridge_go_or_revise_thread",
    "missing_implementation_packet": "create_implementation_start_packet",
    "stale_implementation_packet": "refresh_implementation_start_packet",
    "missing_or_stale_claim": "acquire_work_intent_claim",
    "target_out_of_scope": "revise_scope_or_select_authorized_target",
    "target_outside_project_root": "move_target_inside_project_root",
    "forbidden_operation": "stop_and_request_authorized_scope",
}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _project_root(project_root: str | Path | None = None) -> Path:
    return Path(project_root).resolve() if project_root else Path.cwd().resolve()


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _first_status(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        return line if STATUS_RE.fullmatch(line) else None
    return None


def _bridge_slug_and_version(path: Path) -> tuple[str, int]:
    match = VERSIONED_BRIDGE_RE.fullmatch(path.name)
    if match:
        return match.group("slug"), int(match.group("version"))
    return path.stem, 1


def _bridge_threads(root: Path) -> dict[str, dict[str, Any]]:
    bridge_dir = root / "bridge"
    threads: dict[str, dict[str, Any]] = {}
    if not bridge_dir.is_dir():
        return threads

    versions_by_slug: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for path in sorted(bridge_dir.glob("*.md")):
        status = _first_status(path)
        if not status:
            continue
        slug, version = _bridge_slug_and_version(path)
        rel_path = _relative(root, path)
        versions_by_slug[slug][version] = {
            "path": rel_path,
            "status": status,
            "version": version,
        }

    for slug, versions in versions_by_slug.items():
        chain = [versions[number] for number in sorted(versions, reverse=True)]
        if not chain:
            continue
        threads[slug] = {
            "latest_path": chain[0]["path"],
            "latest_status": chain[0]["status"],
            "version_chain": chain,
        }
    return dict(sorted(threads.items()))


def _implementation_packet(root: Path, slug: str) -> dict[str, Any] | None:
    packet_path = root / IMPLEMENTATION_PACKET_DIR / f"{slug}.json"
    data = _read_json(packet_path)
    return data if isinstance(data, dict) else None


def _work_intent_claim(root: Path, slug: str) -> dict[str, Any] | None:
    db_path = root / "groundtruth.db"
    if not db_path.is_file():
        return None
    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error:
        return None
    try:
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'work_intent_claims'"
        ).fetchone()
        if table is None:
            return None
        row = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (slug,)).fetchone()
        return dict(row) if row is not None else None
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def _is_packet_stale(packet: dict[str, Any], generated_at: str) -> bool:
    expires_at = _parse_iso(str(packet.get("expires_at") or ""))
    generated = _parse_iso(generated_at) or datetime.now(UTC)
    return bool(expires_at and expires_at <= generated)


def _is_claim_stale(claim: dict[str, Any], generated_at: str) -> bool:
    generated = _parse_iso(generated_at) or datetime.now(UTC)
    expires_at = _parse_iso(str(claim.get("ttl_expires_at") or ""))
    if expires_at and expires_at <= generated:
        return True
    if claim.get("claim_kind") == "go_implementation":
        grace = _parse_iso(str(claim.get("implementation_grace_expires_at") or ""))
        return bool(grace and grace <= generated)
    return False


def _entries_from_state_file(root: Path, relative_path: Path) -> list[dict[str, Any]]:
    data = _read_json(root / relative_path)
    if data is None:
        return []
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = data.get("items") or data.get("entries") or []
    else:
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def _receipt_index(root: Path) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {"receipt_ids": set(), "bridge_threads": set()}
    receipts_dir = root / POST_ACTION_RECEIPTS_DIR
    if not receipts_dir.is_dir():
        return index
    for path in sorted(receipts_dir.rglob("*.json")):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        receipt_id = data.get("receipt_id")
        bridge_thread = data.get("bridge_thread")
        if isinstance(receipt_id, str) and receipt_id:
            index["receipt_ids"].add(receipt_id)
        if isinstance(bridge_thread, str) and bridge_thread:
            index["bridge_threads"].add(bridge_thread)
    return index


def _item(
    *,
    category: str,
    severity: str,
    evidence: dict[str, Any],
    next_action: str,
    owner_visible: bool = False,
) -> dict[str, Any]:
    return {
        "category": category,
        "severity": severity,
        "evidence": evidence,
        "next_action": next_action,
        "owner_visible": owner_visible,
    }


def _add_bridge_disposition_items(
    items: list[dict[str, Any]],
    threads: dict[str, dict[str, Any]],
    root: Path,
    generated_at: str,
) -> None:
    for slug, thread in threads.items():
        latest_status = str(thread["latest_status"])
        evidence = {
            "bridge_thread": slug,
            "latest_path": thread["latest_path"],
            "latest_status": latest_status,
        }
        if latest_status == "NO-GO":
            items.append(
                _item(
                    category="unresolved_no_go",
                    severity="warning",
                    evidence=evidence,
                    next_action="prime_builder_revise_or_record_blocker",
                )
            )
        elif latest_status == "ADVISORY":
            items.append(
                _item(
                    category="unresolved_advisory",
                    severity="warning",
                    evidence=evidence,
                    next_action="owner_disposition_required",
                    owner_visible=True,
                )
            )
        elif latest_status == "GO":
            packet = _implementation_packet(root, slug)
            if packet is None:
                items.append(
                    _item(
                        category="missing_implementation_packet",
                        severity="blocked",
                        evidence=evidence,
                        next_action="create_implementation_start_packet",
                    )
                )
                continue
            if _is_packet_stale(packet, generated_at):
                packet_evidence = evidence | {"packet_path": (IMPLEMENTATION_PACKET_DIR / f"{slug}.json").as_posix()}
                items.append(
                    _item(
                        category="stale_implementation_packet",
                        severity="blocked",
                        evidence=packet_evidence,
                        next_action="refresh_implementation_start_packet",
                    )
                )
                continue
            claim = _work_intent_claim(root, slug)
            if claim is None:
                items.append(
                    _item(
                        category="missing_work_intent_claim",
                        severity="blocked",
                        evidence=evidence,
                        next_action="acquire_work_intent_claim",
                    )
                )
            elif _is_claim_stale(claim, generated_at):
                items.append(
                    _item(
                        category="stale_work_intent_claim",
                        severity="blocked",
                        evidence=evidence | {"claim_session_id": claim.get("session_id")},
                        next_action="renew_work_intent_claim",
                    )
                )


def _add_protected_mutation_items(items: list[dict[str, Any]], root: Path) -> None:
    for entry in _entries_from_state_file(root, STATE_DIR / "protected-mutation-blocks.json"):
        reason_code = str(entry.get("reason_code") or "protected_mutation_blocked")
        items.append(
            _item(
                category="protected_mutation_block",
                severity=str(entry.get("severity") or "blocked"),
                evidence={
                    "reason_code": reason_code,
                    "bridge_thread": entry.get("bridge_thread"),
                    "target_paths": entry.get("target_paths") or [],
                    "details": entry.get("details") or "",
                },
                next_action=PROTECTED_BLOCK_NEXT_ACTIONS.get(reason_code, "inspect_protected_mutation_block"),
                owner_visible=bool(entry.get("owner_visible", False)),
            )
        )


def _add_receipt_items(items: list[dict[str, Any]], root: Path) -> None:
    receipt_index = _receipt_index(root)
    for entry in _entries_from_state_file(root, STATE_DIR / "completed-mutations.json"):
        if entry.get("receipt_required", True) is False:
            continue
        receipt_id = entry.get("receipt_id")
        bridge_thread = entry.get("bridge_thread")
        has_receipt = False
        if isinstance(receipt_id, str) and receipt_id:
            has_receipt = receipt_id in receipt_index["receipt_ids"]
        if not has_receipt and isinstance(bridge_thread, str) and bridge_thread:
            has_receipt = bridge_thread in receipt_index["bridge_threads"]
        if has_receipt:
            continue
        items.append(
            _item(
                category="missing_post_action_receipt",
                severity=str(entry.get("severity") or "warning"),
                evidence={
                    "bridge_thread": bridge_thread,
                    "receipt_id": receipt_id,
                    "mutation_class": entry.get("mutation_class"),
                },
                next_action="write_or_link_post_action_receipt",
            )
        )


def _add_external_mutation_items(items: list[dict[str, Any]], root: Path) -> None:
    for entry in _entries_from_state_file(root, STATE_DIR / "external-mutation-requests.json"):
        authorized = entry.get("authorized", entry.get("has_authorization", False))
        if authorized:
            continue
        items.append(
            _item(
                category="external_mutation_authorization_gap",
                severity=str(entry.get("severity") or "blocked"),
                evidence={
                    "bridge_thread": entry.get("bridge_thread"),
                    "target": entry.get("target"),
                    "mutation_class": entry.get("mutation_class") or "external_service",
                },
                next_action="obtain_external_mutation_authorization",
                owner_visible=bool(entry.get("owner_visible", True)),
            )
        )


def _source_paths(root: Path) -> list[str]:
    candidates = [
        root / "bridge",
        root / IMPLEMENTATION_PACKET_DIR,
        root / POST_ACTION_RECEIPTS_DIR,
        root / STATE_DIR / "protected-mutation-blocks.json",
        root / STATE_DIR / "completed-mutations.json",
        root / STATE_DIR / "external-mutation-requests.json",
        root / "groundtruth.db",
    ]
    return sorted(_relative(root, path) for path in candidates if path.exists())


def _summary(threads: dict[str, dict[str, Any]], items: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts = Counter(str(item["category"]) for item in items)
    severity_counts = Counter(str(item["severity"]) for item in items)
    status_counts = Counter(str(thread["latest_status"]) for thread in threads.values())
    return {
        "bridge_actionability": {
            "prime_builder": sum(status_counts[status] for status in PRIME_ACTIONABLE),
            "loyal_opposition": sum(status_counts[status] for status in LOYAL_OPPOSITION_ACTIONABLE),
        },
        "categories": dict(sorted(category_counts.items())),
        "severities": dict(sorted(severity_counts.items())),
        "latest_statuses": dict(sorted(status_counts.items())),
        "total_items": len(items),
    }


def generate_report(project_root: str | Path | None = None, *, generated_at: str | None = None) -> dict[str, Any]:
    """Return deterministic protocol-enforcement visibility data without mutation."""
    root = _project_root(project_root)
    timestamp = generated_at or now_iso()
    threads = _bridge_threads(root)
    items: list[dict[str, Any]] = []

    _add_bridge_disposition_items(items, threads, root, timestamp)
    _add_protected_mutation_items(items, root)
    _add_receipt_items(items, root)
    _add_external_mutation_items(items, root)

    items.sort(
        key=lambda item: (
            str(item["category"]),
            str(item["severity"]),
            str(item["evidence"].get("bridge_thread") or ""),
            str(item["next_action"]),
        )
    )
    status = "healthy"
    if any(item["severity"] == "blocked" for item in items):
        status = "blocked"
    elif items:
        status = "warning"

    return {
        "status": status,
        "generated_at": timestamp,
        "source_paths": _source_paths(root),
        "summary": _summary(threads, items),
        "items": items,
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Protocol Enforcement Health: {report['status']}",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- total_items: {report['summary']['total_items']}",
        "",
        "## Items",
    ]
    for item in report["items"]:
        evidence = item["evidence"]
        bridge_thread = evidence.get("bridge_thread") or "(none)"
        lines.append(f"- {item['severity']} {item['category']} [{bridge_thread}]: {item['next_action']}")
    if not report["items"]:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args(argv)

    report = generate_report(args.project_root)
    if args.format == "markdown":
        print(_markdown(report), end="")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
