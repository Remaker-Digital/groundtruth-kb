"""Synthetic dispatch envelope for harness quality benchmarks.

The envelope is benchmark input data only. It does not invoke dispatcher
workers, mutate durable harness roles, or write live GT-KB state.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from scripts.benchmarks import harness_quality_manifest as manifest


@dataclass(frozen=True)
class BenchmarkDispatchEnvelope:
    """One synthetic benchmark dispatch envelope."""

    dispatch_envelope_id: str
    run_id: str
    harness_id: str
    benchmark_mode: str
    provider: str
    model: str
    author_model_configuration: str
    run_tier: str
    fixture_id: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _require_known(value: str, *, label: str, allowed: set[str]) -> str:
    normalized = value.strip()
    if normalized not in allowed:
        raise ValueError(f"unknown {label}: {value!r}")
    return normalized


def require_benchmark_mode(benchmark_mode: str) -> str:
    """Return a valid synthetic benchmark mode or raise ``ValueError``."""

    modes = {mode.id: mode for mode in manifest.BENCHMARK_MODES}
    mode = modes.get(benchmark_mode.strip())
    if mode is None:
        raise ValueError(f"unknown benchmark_mode: {benchmark_mode!r}")
    if mode.durable_role_changes_allowed:
        raise ValueError("benchmark modes must not allow durable role changes")
    return mode.id


def require_run_tier(run_tier: str) -> str:
    """Return a valid benchmark run tier or raise ``ValueError``."""

    return _require_known(run_tier, label="run_tier", allowed={tier.id for tier in manifest.RUN_TIERS})


def _require_nonblank(value: str, *, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


def envelope_id_for(payload: dict[str, str]) -> str:
    """Return a stable id for the envelope's defining fields."""

    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "bench-env-" + hashlib.sha256(blob).hexdigest()[:16]


def create_benchmark_dispatch_envelope(
    *,
    run_id: str,
    harness_id: str,
    benchmark_mode: str,
    provider: str,
    model: str,
    author_model_configuration: str,
    run_tier: str,
    fixture_id: str,
) -> BenchmarkDispatchEnvelope:
    """Build a validated synthetic envelope for one fixture/harness run."""

    payload = {
        "run_id": _require_nonblank(run_id, label="run_id"),
        "harness_id": _require_nonblank(harness_id, label="harness_id"),
        "benchmark_mode": require_benchmark_mode(benchmark_mode),
        "provider": _require_nonblank(provider, label="provider"),
        "model": _require_nonblank(model, label="model"),
        "author_model_configuration": _require_nonblank(
            author_model_configuration,
            label="author_model_configuration",
        ),
        "run_tier": require_run_tier(run_tier),
        "fixture_id": _require_nonblank(fixture_id, label="fixture_id"),
    }
    return BenchmarkDispatchEnvelope(
        dispatch_envelope_id=envelope_id_for(payload),
        **payload,
    )


__all__ = [
    "BenchmarkDispatchEnvelope",
    "create_benchmark_dispatch_envelope",
    "envelope_id_for",
    "require_benchmark_mode",
    "require_run_tier",
]
