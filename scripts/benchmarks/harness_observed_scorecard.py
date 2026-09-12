"""Advisory observed harness scorecard benchmark.

This benchmark reads existing dispatcher and bridge evidence to summarize
per-harness launch reliability, responsiveness, and bridge-status proxy signals.
It is advisory-only: it never launches dispatch, changes ranking, updates
MemBase, writes bridge state, or changes harness eligibility.
"""

from __future__ import annotations

import json
import re
import statistics
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge.versioned_files import status_from_bridge_text

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

_VERSIONED_BRIDGE_FILE_RE = re.compile(r"^(?P<slug>[A-Za-z0-9_.-]+)-(?P<version>\d{3})\.md$")


def _parse_versioned_bridge_filename(name: str) -> tuple[str, int] | None:
    """Return ``(slug, version)`` for exact ``<slug>-NNN.md`` names only (retired thread-file helper, inlined)."""

    match = _VERSIONED_BRIDGE_FILE_RE.match(name)
    if match is None:
        return None
    return match.group("slug"), int(match.group("version"))


def _status_from_bridge_file(path: Path) -> str | None:
    """Return the canonical status token of a bridge file, retrying a case-normalized copy for historical tokens."""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    token = status_from_bridge_text(text)
    if token is not None:
        return token
    return status_from_bridge_text(text.upper())


BENCHMARK_ID = "harness_observed_scorecard"
ADVISORY_ONLY = True


def _root(project_root: Path | str | None) -> Path:
    return Path(project_root or Path(__file__).resolve().parents[2])


def _parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _window(window_start: str, window_end: str) -> tuple[datetime | None, datetime | None]:
    return _parse_dt(window_start), _parse_dt(window_end)


def _in_window(record: dict[str, Any], start: datetime | None, end: datetime | None) -> bool:
    if start is None or end is None:
        return True
    for key in ("ts", "launched_at", "completed_at", "exit_processed_at", "prior_launched_at"):
        parsed = _parse_dt(record.get(key))
        if parsed is not None:
            return start <= parsed <= end
    return True


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def _recipient_parts(recipient: Any) -> tuple[str, str]:
    text = str(recipient or "unknown")
    if ":" in text:
        role, harness_id = text.split(":", 1)
        return role or "unknown", harness_id or "unknown"
    return "unknown", text or "unknown"


def _harness_from_record(record: dict[str, Any]) -> tuple[str, str]:
    if record.get("recipient"):
        return _recipient_parts(record["recipient"])
    harness_id = str(record.get("harness_id") or record.get("author_harness_id") or "unknown")
    role = str(record.get("role") or record.get("needed_role_label") or "unknown")
    return role, harness_id


def _empty_card(harness_id: str) -> dict[str, Any]:
    return {
        "harness_id": harness_id,
        "roles": [],
        "dispatch_state_observed": False,
        "launch_count": 0,
        "successful_exit_count": 0,
        "nonzero_exit_count": 0,
        "failure_log_count": 0,
        "diagnostic_record_count": 0,
        "bridge_file_count": 0,
        "latest_bridge_thread_count": 0,
        "last_results": {},
        "failure_reasons": {},
        "failure_classes": {},
        "bridge_status_counts": {},
        "latest_bridge_status_counts": {},
        "verdict_latency_seconds": {"count": 0, "median": None, "p90": None},
        "circuit_breaker_tripped": False,
    }


def _card(cards: dict[str, dict[str, Any]], harness_id: str) -> dict[str, Any]:
    key = harness_id or "unknown"
    if key not in cards:
        cards[key] = _empty_card(key)
    return cards[key]


def _add_role(card: dict[str, Any], role: str) -> None:
    if role and role != "unknown" and role not in card["roles"]:
        card["roles"].append(role)
        card["roles"].sort()


def _load_json(path: Path) -> tuple[dict[str, Any], bool]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}, False
    return (payload if isinstance(payload, dict) else {}), True


def _jsonl_records(paths: list[Path], start: datetime | None, end: datetime | None) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    malformed = 0
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if isinstance(payload, dict) and _in_window(payload, start, end):
                records.append(payload)
    return records, malformed


def _number(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric != numeric or numeric in (float("inf"), float("-inf")):
        return None
    return numeric


def _latency_summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "median": None, "p90": None}
    ordered = sorted(values)
    p90_index = max(0, min(len(ordered) - 1, int((len(ordered) * 0.9) - 0.000001)))
    return {
        "count": len(ordered),
        "median": round(statistics.median(ordered), 3),
        "p90": round(ordered[p90_index], 3),
    }


def _increment_mapping(card: dict[str, Any], key: str, item: str) -> None:
    counts = Counter(card.get(key, {}))
    counts[str(item or "unknown")] += 1
    card[key] = _counter_dict(counts)


def _apply_dispatch_state(
    cards: dict[str, dict[str, Any]], state: dict[str, Any], latencies: dict[str, list[float]]
) -> int:
    recipients = state.get("recipients")
    if not isinstance(recipients, dict):
        return 0
    observed = 0
    for recipient, data in recipients.items():
        if not isinstance(data, dict):
            continue
        role, harness_id = _recipient_parts(recipient)
        card = _card(cards, harness_id)
        _add_role(card, role)
        card["dispatch_state_observed"] = True
        card["circuit_breaker_tripped"] = bool(data.get("circuit_breaker_tripped"))
        _increment_mapping(card, "last_results", str(data.get("last_result") or "unknown"))
        last_launch = data.get("last_launch")
        if isinstance(last_launch, dict) and last_launch.get("launched"):
            card["launch_count"] += 1
            exit_code = last_launch.get("exit_code")
            if exit_code == 0:
                card["successful_exit_count"] += 1
            elif exit_code is not None:
                card["nonzero_exit_count"] += 1
            latency = _number(last_launch.get("verdict_latency_seconds"))
            if latency is not None:
                latencies.setdefault(harness_id, []).append(latency)
        observed += 1
    return observed


def _apply_failures(cards: dict[str, dict[str, Any]], records: list[dict[str, Any]]) -> None:
    for record in records:
        role, harness_id = _harness_from_record(record)
        card = _card(cards, harness_id)
        _add_role(card, role)
        card["failure_log_count"] += 1
        _increment_mapping(card, "failure_reasons", str(record.get("reason") or "unknown"))
        failure_class = str(record.get("failure_class") or record.get("error_type") or "unknown")
        _increment_mapping(card, "failure_classes", failure_class)
        for marker in record.get("matched_markers") or ():
            if isinstance(marker, dict) and marker.get("label"):
                _increment_mapping(card, "failure_classes", str(marker["label"]))


def _apply_diagnostics(
    cards: dict[str, dict[str, Any]],
    records: list[dict[str, Any]],
    latencies: dict[str, list[float]],
) -> None:
    for record in records:
        role, harness_id = _harness_from_record(record)
        card = _card(cards, harness_id)
        _add_role(card, role)
        card["diagnostic_record_count"] += 1
        latency = _number(record.get("verdict_latency_seconds"))
        if latency is not None:
            latencies.setdefault(harness_id, []).append(latency)


def _metadata_value(text: str, key: str) -> str | None:
    prefix = f"{key}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip() or None
    return None


def _apply_bridge_statuses(
    cards: dict[str, dict[str, Any]],
    root: Path,
    start: datetime | None,
    end: datetime | None,
) -> tuple[int, int]:
    bridge_dir = root / "bridge"
    if not bridge_dir.is_dir():
        return 0, 0
    thread_latest: dict[str, tuple[int, str, str]] = {}
    bridge_file_count = 0
    for path in sorted(bridge_dir.glob("*.md")):
        parsed = _parse_versioned_bridge_filename(path.name)
        if parsed is None:
            continue
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        except OSError:
            continue
        if start is not None and end is not None and not (start <= mtime <= end):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        slug, version = parsed
        harness_id = _metadata_value(text, "author_harness_id") or "unknown"
        role = "unknown"
        identity = _metadata_value(text, "author_identity") or ""
        if identity.startswith("prime-builder"):
            role = "prime-builder"
        elif identity.startswith("loyal-opposition") or "Loyal Opposition" in identity:
            role = "loyal-opposition"
        card = _card(cards, harness_id)
        _add_role(card, role)
        card["bridge_file_count"] += 1
        _increment_mapping(card, "bridge_status_counts", status)
        bridge_file_count += 1
        if slug not in thread_latest or version > thread_latest[slug][0]:
            thread_latest[slug] = (version, status, harness_id)
    for _, status, harness_id in thread_latest.values():
        card = _card(cards, harness_id)
        card["latest_bridge_thread_count"] += 1
        _increment_mapping(card, "latest_bridge_status_counts", status)
    return bridge_file_count, len(thread_latest)


def run(window_start: str, window_end: str, project_root: Path | str | None = None) -> BenchmarkResult:
    root = _root(project_root)
    start, end = _window(window_start, window_end)
    poller = root / ".gtkb-state" / "bridge-poller"
    missing_sources: list[str] = []
    cards: dict[str, dict[str, Any]] = {}
    latencies: dict[str, list[float]] = {}

    dispatch_state, has_dispatch_state = _load_json(poller / "dispatch-state.json")
    if not has_dispatch_state:
        missing_sources.append(".gtkb-state/bridge-poller/dispatch-state.json")
    dispatch_state_recipients = _apply_dispatch_state(cards, dispatch_state, latencies)

    failure_paths = sorted(poller.glob("dispatch-failures.jsonl*")) if poller.is_dir() else []
    if not failure_paths:
        missing_sources.append(".gtkb-state/bridge-poller/dispatch-failures.jsonl*")
    failure_records, malformed_failures = _jsonl_records(failure_paths, start, end)
    _apply_failures(cards, failure_records)

    diagnostic_paths = sorted(poller.glob("dispatch-diagnostic-post.jsonl*")) if poller.is_dir() else []
    if not diagnostic_paths:
        missing_sources.append(".gtkb-state/bridge-poller/dispatch-diagnostic-post.jsonl*")
    diagnostic_records, malformed_diagnostics = _jsonl_records(diagnostic_paths, start, end)
    _apply_diagnostics(cards, diagnostic_records, latencies)

    bridge_file_count, bridge_thread_count = _apply_bridge_statuses(cards, root, start, end)
    if bridge_file_count == 0:
        missing_sources.append("bridge/*-NNN.md")

    for harness_id, values in latencies.items():
        _card(cards, harness_id)["verdict_latency_seconds"] = _latency_summary(values)

    observed_harness_count = sum(
        1
        for card in cards.values()
        if card["dispatch_state_observed"]
        or card["failure_log_count"]
        or card["diagnostic_record_count"]
        or card["bridge_file_count"]
    )
    candidate_harness_count = len(cards)
    coverage_ratio = observed_harness_count / candidate_harness_count if candidate_harness_count else 0.0

    dimensions = {
        "advisory_only": ADVISORY_ONLY,
        "mutation_boundaries": {
            "membase_mutation": False,
            "bridge_mutation": False,
            "dispatcher_ranking_mutation": False,
            "harness_eligibility_mutation": False,
        },
        "summary": {
            "candidate_harness_count": candidate_harness_count,
            "observed_harness_count": observed_harness_count,
            "dispatch_state_recipient_count": dispatch_state_recipients,
            "failure_log_record_count": len(failure_records),
            "diagnostic_record_count": len(diagnostic_records),
            "bridge_file_count": bridge_file_count,
            "bridge_thread_count": bridge_thread_count,
            "malformed_jsonl_record_count": malformed_failures + malformed_diagnostics,
            "missing_sources": missing_sources,
        },
        "harnesses": dict(sorted(cards.items())),
    }
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(coverage_ratio, 4),
        dimensions=dimensions,
        source_commit=current_source_commit(root),
        source_query=(
            ".gtkb-state/bridge-poller/dispatch-state.json; "
            "dispatch-failures.jsonl*; dispatch-diagnostic-post.jsonl*; bridge/*-NNN.md"
        ),
    )
