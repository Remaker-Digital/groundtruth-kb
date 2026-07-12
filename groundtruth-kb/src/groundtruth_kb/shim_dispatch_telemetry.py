"""Privacy-bounded telemetry for dispatcher-launched shim harness runs.

The module deliberately constructs every persisted value from a small allowlist.
It must never serialize prompts, messages, tool arguments/results, provider
bodies, environment values, credentials, or exception text.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_ID = "gtkb.shim_dispatch_telemetry.v1"
QUERY_SCHEMA_ID = "gtkb.shim_dispatch_telemetry.query.v1"
SCHEMA_VERSION = 1
DISPATCH_RUNS_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller" / "dispatch-runs"
DISPATCH_ID_ENV_VAR = "GTKB_BRIDGE_POLLER_RUN_ID"
SESSION_ID_ENV_VAR = "GTKB_INHERITED_SESSION_ID"
PRIMARY_BRIDGE_ID_ENV_VAR = "GTKB_DISPATCH_PRIMARY_BRIDGE_ID"
MAX_TELEMETRY_RECORD_BYTES = 1_000_000

CANONICAL_TOOL_NAMES = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash", "PublishBridgeVerdict"})
STOP_REASONS = frozenset(
    {
        "verdict_emitted",
        "final_response",
        "max_turn_exhaustion",
        "no_progress_loop",
        "session_timeout",
        "provider_error",
        "guard_error",
        "process_error",
        "external_timeout",
        "external_termination",
        "role_document_invalid",
    }
)
EXIT_STATUSES = frozenset({"completed", "failed", "succeeded", "external_termination", "partial"})
SUCCESSFUL_REVIEW_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})
QUERY_GROUPS = frozenset(
    {
        "harness",
        "provider_model",
        "role",
        "stop_reason",
        "bridge_version_count",
        "target_path_count",
        "linked_spec_count",
        "verification_command_count",
    }
)
_BRIDGE_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_WORK_ITEM_RE = re.compile(r"\bWI-[A-Za-z0-9-]+\b")
_SPEC_RE = re.compile(r"\bSPEC-[A-Za-z0-9-]+\b")
_VERIFICATION_COMMAND_RE = re.compile(r"^(?:python(?:3)?|pytest|ruff)\b", re.IGNORECASE)
_NUMERIC_USAGE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
)


@dataclass(frozen=True)
class TelemetryWriteResult:
    """Bounded, non-sensitive write outcome for callers and diagnostics."""

    written: bool
    path: Path | None
    diagnostic: str | None = None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _nonempty_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _safe_nonnegative_number(value: object) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value < 0:
        return None
    return value


def _safe_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _runs_directory(project_root: Path) -> Path:
    return project_root.resolve() / DISPATCH_RUNS_RELATIVE_PATH


def telemetry_path(project_root: Path, dispatch_id: str) -> Path:
    """Return the sole current v1 record path for a dispatched run."""

    normalized = _nonempty_string(dispatch_id)
    if normalized is None or not _BRIDGE_IDENTIFIER_RE.fullmatch(normalized):
        raise ValueError("dispatch_id must be a non-empty identifier")
    return _runs_directory(project_root) / f"{normalized}.telemetry.json"


def _safe_bridge_id(value: object) -> str | None:
    normalized = _nonempty_string(value)
    if normalized is None or not _BRIDGE_IDENTIFIER_RE.fullmatch(normalized):
        return None
    return normalized


def _safe_work_item_ids(values: Iterable[object]) -> list[str]:
    result = sorted(
        {str(value) for value in values if isinstance(value, str) and _WORK_ITEM_RE.fullmatch(value.strip())}
    )
    return result


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write one UTF-8 document and atomically replace the prior current record."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as stream:
        temporary_path = Path(stream.name)
        try:
            json.dump(payload, stream, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        if path.stat().st_size > MAX_TELEMETRY_RECORD_BYTES:
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _first_number(mapping: Mapping[str, Any], *keys: str) -> int | float | None:
    for key in keys:
        value = _safe_nonnegative_number(mapping.get(key))
        if value is not None:
            return value
    return None


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _observed_usage(
    response: Mapping[str, Any] | None,
) -> tuple[dict[str, int | float], tuple[int | float, str] | None]:
    """Extract only approved scalar usage/cost fields from a provider response."""

    if not isinstance(response, Mapping):
        return {}, None
    usage = _mapping(response.get("usage"))
    prompt_details = _mapping(usage.get("prompt_tokens_details"))
    completion_details = _mapping(usage.get("completion_tokens_details"))
    values: dict[str, int | float] = {}
    candidates = {
        "input_tokens": _first_number(usage, "input_tokens", "prompt_tokens"),
        "output_tokens": _first_number(usage, "output_tokens", "completion_tokens"),
        "total_tokens": _first_number(usage, "total_tokens"),
        "cache_read_tokens": _first_number(
            usage,
            "cache_read_tokens",
            "cache_read_input_tokens",
        ),
        "cache_write_tokens": _first_number(
            usage,
            "cache_write_tokens",
            "cache_creation_input_tokens",
        ),
    }
    if candidates["cache_read_tokens"] is None:
        candidates["cache_read_tokens"] = _first_number(prompt_details, "cached_tokens")
    if candidates["cache_write_tokens"] is None:
        candidates["cache_write_tokens"] = _first_number(completion_details, "cached_tokens")
    # Ollama's native response supplies the two direct evaluation counters at
    # the response root. It does not claim a provider-reported total.
    if candidates["input_tokens"] is None:
        candidates["input_tokens"] = _first_number(response, "prompt_eval_count")
    if candidates["output_tokens"] is None:
        candidates["output_tokens"] = _first_number(response, "eval_count")
    for key, value in candidates.items():
        if value is not None:
            values[key] = value

    cost_source = _mapping(response.get("cost"))
    cost_amount = _first_number(cost_source, "amount", "total")
    cost_currency = _nonempty_string(cost_source.get("currency"))
    if cost_amount is None:
        cost_amount = _first_number(usage, "cost", "cost_amount", "total_cost")
        cost_currency = cost_currency or _nonempty_string(usage.get("cost_currency"))
    if cost_amount is None:
        cost_amount = _first_number(response, "cost", "cost_amount", "total_cost")
        cost_currency = cost_currency or _nonempty_string(response.get("cost_currency"))
    return values, (cost_amount, cost_currency) if cost_amount is not None and cost_currency is not None else None


def _usage_summary(observations: list[dict[str, int | float]], provider_turn_count: int) -> dict[str, Any]:
    fields: dict[str, int | float | None] = {}
    for field in _NUMERIC_USAGE_FIELDS:
        values = [observation.get(field) for observation in observations]
        # A field is known only when every observed provider turn reported it.
        # This prevents a partial provider response from becoming an invented
        # aggregate total. Direct provider-reported zeros remain valid.
        if provider_turn_count and len(values) == provider_turn_count and all(value is not None for value in values):
            fields[field] = sum(values)  # type: ignore[arg-type]
        else:
            fields[field] = None
    any_usage = any(observation for observation in observations)
    complete = provider_turn_count > 0 and all(
        all(field in observation for field in ("input_tokens", "output_tokens", "total_tokens"))
        for observation in observations
    )
    return {
        "coverage": "complete" if complete else ("partial" if any_usage else "unavailable"),
        **fields,
    }


def _cost_summary(observations: list[tuple[int | float, str] | None], provider_turn_count: int) -> dict[str, Any]:
    present = [observation for observation in observations if observation is not None]
    if provider_turn_count and len(present) == provider_turn_count:
        currencies = {currency for _, currency in present}
        if len(currencies) == 1:
            return {
                "amount": sum(amount for amount, _ in present),
                "currency": next(iter(currencies)),
                "source": "provider_reported",
            }
    return {"amount": None, "currency": None, "source": None}


def _empty_complexity() -> dict[str, int | None]:
    return {
        "bridge_version_count": None,
        "target_path_count": None,
        "linked_spec_count": None,
        "verification_command_count": None,
    }


def dispatch_context(project_root: Path, bridge_document_id: str | None) -> dict[str, Any]:
    """Derive safe correlation IDs and raw counts from a bridge document only."""

    bridge_id = _safe_bridge_id(bridge_document_id)
    if bridge_id is None:
        return {
            "bridge_document_id": None,
            "bridge_thread_id": None,
            "related_work_item_ids": [],
            "thread_complexity": _empty_complexity(),
        }
    bridge_dir = project_root.resolve() / "bridge"
    versioned_name = re.compile(rf"^{re.escape(bridge_id)}-\d{{3,}}\.md$")
    paths = sorted(path for path in bridge_dir.glob(f"{bridge_id}-*.md") if versioned_name.fullmatch(path.name))
    if not paths:
        return {
            "bridge_document_id": bridge_id,
            "bridge_thread_id": bridge_id,
            "related_work_item_ids": [],
            "thread_complexity": _empty_complexity(),
        }
    contents: list[str] = []
    for path in paths:
        try:
            contents.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    if not contents:
        return {
            "bridge_document_id": bridge_id,
            "bridge_thread_id": bridge_id,
            "related_work_item_ids": [],
            "thread_complexity": _empty_complexity(),
        }
    latest = contents[-1]
    target_paths = 0
    match = re.search(r"^target_paths:\s*(\[[^\r\n]*\])\s*$", latest, flags=re.IGNORECASE | re.MULTILINE)
    if match:
        try:
            parsed = json.loads(match.group(1))
            target_paths = len(parsed) if isinstance(parsed, list) else 0
        except json.JSONDecodeError:
            target_paths = 0
    combined = "\n".join(contents)
    return {
        "bridge_document_id": bridge_id,
        "bridge_thread_id": bridge_id,
        "related_work_item_ids": _safe_work_item_ids(_WORK_ITEM_RE.findall(combined)),
        "thread_complexity": {
            "bridge_version_count": len(paths),
            "target_path_count": target_paths,
            "linked_spec_count": len(set(_SPEC_RE.findall(combined))),
            "verification_command_count": sum(
                1 for line in combined.splitlines() if _VERIFICATION_COMMAND_RE.match(line.strip())
            ),
        },
    }


def _role_provenance(
    project_root: Path, session_id: str | None, harness_name: str
) -> tuple[str | None, str | None, bool]:
    """Read role authority from the worker document; never from dispatch metadata."""

    if session_id is None:
        return None, None, False
    try:
        from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance

        provenance = resolve_worker_role_provenance(
            project_root.resolve(), current_session_id=session_id, harness_name=harness_name
        )
    except (EnvelopeError, OSError, ValueError):
        return None, None, False
    role = _nonempty_string(provenance.get("role"))
    if role is None:
        return None, None, False
    session_document = Path("harness-state") / harness_name / "session-envelopes" / f"{session_id}.json"
    legacy_document = Path("harness-state") / harness_name / "session-envelope.json"
    document_id = session_document if (project_root / session_document).is_file() else legacy_document
    return role, document_id.as_posix(), True


class NullDispatchTelemetry:
    """No-op observer used for ordinary non-dispatch shim invocation."""

    enabled = False
    diagnostic: str | None = None

    def record_turn(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def set_model(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def finish(self, *_args: Any, **_kwargs: Any) -> TelemetryWriteResult:
        return TelemetryWriteResult(written=False, path=None)


class DispatchTelemetryObserver:
    """Collect a single dispatch's allowlisted measurements and persist atomically."""

    enabled = True

    def __init__(
        self,
        project_root: Path,
        *,
        dispatch_id: str,
        run_id: str,
        harness_id: str,
        harness_name: str,
        provider: str,
        model_id: str | None,
        model_version: str | None,
        turn_budget: int | None,
        session_context_id: str | None,
        bridge_document_id: str | None,
    ) -> None:
        self.project_root = project_root.resolve()
        self.dispatch_id = dispatch_id
        self.run_id = run_id
        self.harness_id = _nonempty_string(harness_id)
        self.harness_name = _nonempty_string(harness_name)
        self.provider = _nonempty_string(provider)
        self.model_id = _nonempty_string(model_id)
        self.model_version = _nonempty_string(model_version)
        self.turn_budget = _safe_int(turn_budget)
        self.session_context_id = _nonempty_string(session_context_id)
        self.started_at = _utc_now()
        self._started_monotonic = time.monotonic()
        self._turns: list[dict[str, Any]] = []
        self._tool_counts: Counter[str] = Counter()
        self._usage_observations: list[dict[str, int | float]] = []
        self._cost_observations: list[tuple[int | float, str] | None] = []
        self._finished = False
        self._result: TelemetryWriteResult | None = None
        self.diagnostic: str | None = None
        self.context = dispatch_context(self.project_root, bridge_document_id)
        role, source_document_id, role_document_valid = _role_provenance(
            self.project_root,
            self.session_context_id,
            self.harness_name or "",
        )
        self.role = role
        self.role_source_document_id = source_document_id
        self.role_document_valid = role_document_valid

    def set_model(self, model_id: str | None, model_version: str | None) -> None:
        if model_id is not None:
            self.model_id = _nonempty_string(model_id)
        if model_version is not None:
            self.model_version = _nonempty_string(model_version)

    def record_turn(
        self,
        index: int,
        tool_names: Iterable[object],
        *,
        provider_response: Mapping[str, Any] | None = None,
    ) -> None:
        if self._finished or not isinstance(index, int) or index < 1:
            return
        names = [name for name in tool_names if isinstance(name, str) and name in CANONICAL_TOOL_NAMES]
        self._turns.append({"index": index, "tool_names": names})
        self._tool_counts.update(names)
        usage, cost = _observed_usage(provider_response)
        self._usage_observations.append(usage)
        self._cost_observations.append(cost)

    def _envelope(self, *, stop_reason: str, exit_status: str) -> dict[str, Any]:
        completed_at = _utc_now()
        elapsed_ms = max(0, round((time.monotonic() - self._started_monotonic) * 1000))
        provider_turn_count = len(self._usage_observations)
        return {
            "schema_id": SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "correlation": {
                "dispatch_id": self.dispatch_id,
                "run_id": self.run_id,
                "bridge_document_id": self.context["bridge_document_id"],
                "bridge_thread_id": self.context["bridge_thread_id"],
                "related_work_item_ids": self.context["related_work_item_ids"],
                "session_context_id": self.session_context_id,
            },
            "worker": {
                "harness_id": self.harness_id,
                "harness_name": self.harness_name,
                "provider": self.provider,
                "model_id": self.model_id,
                "model_version": self.model_version,
                "role": self.role,
                "role_source_document_id": self.role_source_document_id,
            },
            "timing": {
                "started_at": self.started_at,
                "completed_at": completed_at,
                "elapsed_ms": elapsed_ms,
            },
            "budget": {"turn_budget": self.turn_budget, "turns_used": len(self._turns)},
            "turns": list(self._turns),
            "tool_calls": {
                "total": sum(self._tool_counts.values()),
                "by_name": dict(sorted(self._tool_counts.items())),
            },
            "outcome": {
                "stop_reason": stop_reason,
                "exit_status": exit_status,
                "exit_code": None,
                "bridge_status": None,
            },
            "usage": _usage_summary(self._usage_observations, provider_turn_count),
            "cost": _cost_summary(self._cost_observations, provider_turn_count),
            "thread_complexity": self.context["thread_complexity"],
        }

    def finish(self, *, stop_reason: str, exit_status: str | None = None) -> TelemetryWriteResult:
        if self._finished and self._result is not None:
            return self._result
        self._finished = True
        normalized_stop_reason = stop_reason if stop_reason in STOP_REASONS else "process_error"
        if not self.role_document_valid:
            normalized_stop_reason = "role_document_invalid"
        normalized_exit_status = exit_status if exit_status in EXIT_STATUSES else None
        if normalized_exit_status is None:
            normalized_exit_status = (
                "completed" if normalized_stop_reason in {"final_response", "verdict_emitted"} else "failed"
            )
        payload = self._envelope(stop_reason=normalized_stop_reason, exit_status=normalized_exit_status)
        path = telemetry_path(self.project_root, self.dispatch_id)
        try:
            _atomic_write_json(path, payload)
        except Exception:
            self.diagnostic = "telemetry_write_failed"
            self._result = TelemetryWriteResult(written=False, path=path, diagnostic=self.diagnostic)
            return self._result
        self._result = TelemetryWriteResult(written=True, path=path)
        return self._result


def create_dispatch_telemetry_observer(
    project_root: Path,
    *,
    harness_id: str,
    harness_name: str,
    provider: str,
    model_id: str | None,
    model_version: str | None,
    turn_budget: int | None,
    environ: Mapping[str, str] | None = None,
) -> DispatchTelemetryObserver | NullDispatchTelemetry:
    """Create an observer only when the dispatcher supplied a run identifier."""

    env = os.environ if environ is None else environ
    dispatch_id = _safe_bridge_id(env.get(DISPATCH_ID_ENV_VAR))
    if dispatch_id is None:
        return NullDispatchTelemetry()
    session_context_id = _nonempty_string(env.get(SESSION_ID_ENV_VAR)) or dispatch_id
    bridge_document_id = _safe_bridge_id(env.get(PRIMARY_BRIDGE_ID_ENV_VAR))
    return DispatchTelemetryObserver(
        project_root,
        dispatch_id=dispatch_id,
        run_id=dispatch_id,
        harness_id=harness_id,
        harness_name=harness_name,
        provider=provider,
        model_id=model_id,
        model_version=model_version,
        turn_budget=turn_budget,
        session_context_id=session_context_id,
        bridge_document_id=bridge_document_id,
    )


def _base_partial_envelope(project_root: Path, dispatch_id: str, bridge_document_id: str | None) -> dict[str, Any]:
    context = dispatch_context(project_root, bridge_document_id)
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "correlation": {
            "dispatch_id": dispatch_id,
            "run_id": dispatch_id,
            "bridge_document_id": context["bridge_document_id"],
            "bridge_thread_id": context["bridge_thread_id"],
            "related_work_item_ids": context["related_work_item_ids"],
            "session_context_id": dispatch_id,
        },
        "worker": {
            "harness_id": None,
            "harness_name": None,
            "provider": None,
            "model_id": None,
            "model_version": None,
            "role": None,
            "role_source_document_id": None,
        },
        "timing": {"started_at": None, "completed_at": None, "elapsed_ms": None},
        "budget": {"turn_budget": None, "turns_used": None},
        "turns": [],
        "tool_calls": {"total": None, "by_name": {}},
        "outcome": {
            "stop_reason": "external_termination",
            "exit_status": "partial",
            "exit_code": None,
            "bridge_status": None,
        },
        "usage": {"coverage": "unavailable", **{field: None for field in _NUMERIC_USAGE_FIELDS}},
        "cost": {"amount": None, "currency": None, "source": None},
        "thread_complexity": context["thread_complexity"],
    }


def reconcile_dispatch_telemetry(
    project_root: Path,
    dispatch_id: str,
    *,
    launched_at: str | None = None,
    completed_at: str | None = None,
    elapsed_ms: int | float | None = None,
    exit_code: int | None = None,
    exit_status: str | None = None,
    stop_reason: str | None = None,
    bridge_status: str | None = None,
    bridge_document_id: str | None = None,
) -> TelemetryWriteResult:
    """Merge only known dispatcher facts, creating a partial record if necessary."""

    path = telemetry_path(project_root, dispatch_id)
    payload = _read_json_object(path)
    if payload is None or payload.get("schema_id") != SCHEMA_ID:
        payload = _base_partial_envelope(project_root, dispatch_id, bridge_document_id)
    correlation = _mapping(payload.get("correlation"))
    payload["correlation"] = dict(correlation)
    payload["correlation"]["dispatch_id"] = dispatch_id
    payload["correlation"]["run_id"] = _nonempty_string(correlation.get("run_id")) or dispatch_id
    if bridge_document_id is not None:
        context = dispatch_context(project_root, bridge_document_id)
        for key in ("bridge_document_id", "bridge_thread_id", "related_work_item_ids"):
            payload["correlation"][key] = context[key]
        payload["thread_complexity"] = context["thread_complexity"]

    timing = dict(_mapping(payload.get("timing")))
    if launched_at is not None:
        timing["started_at"] = _nonempty_string(launched_at)
    if completed_at is not None:
        timing["completed_at"] = _nonempty_string(completed_at)
    safe_elapsed_ms = _safe_nonnegative_number(elapsed_ms)
    if safe_elapsed_ms is not None:
        timing["elapsed_ms"] = round(safe_elapsed_ms)
    payload["timing"] = timing

    outcome = dict(_mapping(payload.get("outcome")))
    if stop_reason in STOP_REASONS:
        outcome["stop_reason"] = stop_reason
    if exit_status in EXIT_STATUSES:
        outcome["exit_status"] = exit_status
    if isinstance(exit_code, int) and not isinstance(exit_code, bool):
        outcome["exit_code"] = exit_code
    if bridge_status in SUCCESSFUL_REVIEW_STATUSES:
        outcome["bridge_status"] = bridge_status
    payload["outcome"] = outcome

    try:
        _atomic_write_json(path, payload)
    except Exception:
        return TelemetryWriteResult(written=False, path=path, diagnostic="telemetry_write_failed")
    return TelemetryWriteResult(written=True, path=path)


def _record_group_value(record: Mapping[str, Any], group_by: str) -> str:
    worker = _mapping(record.get("worker"))
    outcome = _mapping(record.get("outcome"))
    complexity = _mapping(record.get("thread_complexity"))
    if group_by == "harness":
        return _nonempty_string(worker.get("harness_name")) or "unknown"
    if group_by == "provider_model":
        provider = _nonempty_string(worker.get("provider")) or "unknown"
        model = _nonempty_string(worker.get("model_id")) or "unknown"
        return f"{provider}/{model}"
    if group_by == "role":
        return _nonempty_string(worker.get("role")) or "unknown"
    if group_by == "stop_reason":
        return _nonempty_string(outcome.get("stop_reason")) or "unknown"
    value = complexity.get(group_by)
    return str(value) if isinstance(value, int) else "unknown"


def _matches_query_filters(
    record: Mapping[str, Any],
    *,
    harness: str | None,
    provider_model: str | None,
    role: str | None,
    stop_reason: str | None,
    complexity: str | None,
    complexity_value: int | None,
) -> bool:
    worker = _mapping(record.get("worker"))
    outcome = _mapping(record.get("outcome"))
    if harness is not None and worker.get("harness_name") != harness:
        return False
    if provider_model is not None and _record_group_value(record, "provider_model") != provider_model:
        return False
    if role is not None and worker.get("role") != role:
        return False
    if stop_reason is not None and outcome.get("stop_reason") != stop_reason:
        return False
    if complexity is None:
        return True
    observed_complexity = _record_group_value(record, complexity)
    return observed_complexity != "unknown" and (
        complexity_value is None or observed_complexity == str(complexity_value)
    )


def query_dispatch_telemetry(
    project_root: Path,
    *,
    group_by: str = "harness",
    harness: str | None = None,
    provider_model: str | None = None,
    role: str | None = None,
    stop_reason: str | None = None,
    complexity: str | None = None,
    complexity_value: int | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return a bounded read-only distribution over successful reconciled reviews."""

    if group_by not in QUERY_GROUPS:
        raise ValueError(f"group_by must be one of {sorted(QUERY_GROUPS)}")
    if complexity is not None and complexity not in {
        "bridge_version_count",
        "target_path_count",
        "linked_spec_count",
        "verification_command_count",
    }:
        raise ValueError("complexity must name a raw thread-complexity count")
    if complexity_value is not None:
        if complexity is None:
            raise ValueError("complexity_value requires a complexity dimension")
        if isinstance(complexity_value, bool) or not isinstance(complexity_value, int) or complexity_value < 0:
            raise ValueError("complexity_value must be a non-negative integer")
    bounded_limit = min(max(int(limit), 1), 200)
    path_rows: list[tuple[float, Path]] = []
    for path in _runs_directory(project_root).glob("*.telemetry.json"):
        try:
            path_rows.append((path.stat().st_mtime, path))
        except OSError:
            continue
    paths = [path for _, path in sorted(path_rows, key=lambda row: row[0], reverse=True)]
    distribution: Counter[str] = Counter()
    examined = 0
    matched = 0
    for path in paths[:bounded_limit]:
        record = _read_json_object(path)
        if record is None or record.get("schema_id") != SCHEMA_ID:
            continue
        examined += 1
        outcome = _mapping(record.get("outcome"))
        if outcome.get("exit_status") != "succeeded" or outcome.get("bridge_status") not in SUCCESSFUL_REVIEW_STATUSES:
            continue
        if not _matches_query_filters(
            record,
            harness=harness,
            provider_model=provider_model,
            role=role,
            stop_reason=stop_reason,
            complexity=complexity,
            complexity_value=complexity_value,
        ):
            continue
        matched += 1
        distribution[_record_group_value(record, group_by)] += 1
    return {
        "schema_id": QUERY_SCHEMA_ID,
        "group_by": group_by,
        "filters": {
            "harness": harness,
            "provider_model": provider_model,
            "role": role,
            "stop_reason": stop_reason,
            "complexity": complexity,
            "complexity_value": complexity_value,
        },
        "successful_reconciled_review_count": matched,
        "distribution": [{"value": value, "count": count} for value, count in sorted(distribution.items())],
        "bounds": {"record_limit": bounded_limit, "records_examined": examined, "records_available": len(paths)},
    }


def read_dispatch_telemetry_records(
    project_root: Path,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Read bounded canonical telemetry records for diagnostic projection.

    Records remain internal input to the diagnostic allowlist; callers must not
    serialize unrecognized fields from a telemetry file.
    """
    bounded_limit = min(max(int(limit), 1), 50)
    path_rows: list[tuple[float, Path]] = []
    for path in _runs_directory(project_root).glob("*.telemetry.json"):
        try:
            path_rows.append((path.stat().st_mtime, path))
        except OSError:
            continue
    result: list[dict[str, Any]] = []
    for _mtime, path in sorted(path_rows, key=lambda row: (row[0], row[1].name), reverse=True):
        record = _read_json_object(path)
        if record is None or record.get("schema_id") != SCHEMA_ID:
            continue
        worker = _mapping(record.get("worker"))
        if harness_id is not None and worker.get("harness_id") != harness_id:
            continue
        if harness_name is not None and worker.get("harness_name") != harness_name:
            continue
        result.append(record)
        if len(result) >= bounded_limit:
            break
    return result
