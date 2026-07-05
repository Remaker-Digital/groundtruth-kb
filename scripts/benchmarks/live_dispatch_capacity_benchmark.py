#!/usr/bin/env python3
"""Deterministic local dispatch-capacity benchmark for WI-5030.

The default mode uses local no-op worker tasks. It does not start the live
dispatcher daemon, invoke AI harnesses, mutate bridge state, or spend provider
calls. Provider-backed mode is deliberately gated by an explicit flag.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import Any

DEFAULT_GLOBAL_CAPS = (1, 2, 4, 8)
DEFAULT_PER_ROLE_CAPS = (1, 2, 3)
DEFAULT_MAX_ITEMS_VALUES = (1, 2, 4)
DEFAULT_WORK_ITEMS = 24
DEFAULT_WORKER_DURATION_MS = 1.0
MODE_SIMULATED_LOCAL = "simulated-local"
MODE_PROVIDER_LIVE = "provider-live"


class ProviderLiveDispatchNotAllowed(RuntimeError):
    """Raised when provider-backed mode is requested without explicit opt-in."""


@dataclass(frozen=True)
class CapacityScenario:
    global_cap: int
    per_role_cap: int
    max_items: int
    work_items: int


@dataclass(frozen=True)
class CapacityObservation:
    global_cap: int
    per_role_cap: int
    max_items: int
    work_items: int
    batch_count: int
    logical_worker_count: int
    waves: int
    binding_constraint: str
    observed_duration_seconds: float
    throughput_items_per_second: float
    constraint_evidence: dict[str, str]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapacityBenchmarkReport:
    schema_version: int
    mode: str
    provider_backed: bool
    real_side_effects: bool
    explicit_provider_flag_required: bool
    scenario_count: int
    observations: list[CapacityObservation]
    recommended_safe_ceiling: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "provider_backed": self.provider_backed,
            "real_side_effects": self.real_side_effects,
            "explicit_provider_flag_required": self.explicit_provider_flag_required,
            "scenario_count": self.scenario_count,
            "observations": [observation.to_json_dict() for observation in self.observations],
            "recommended_safe_ceiling": dict(self.recommended_safe_ceiling),
        }


def _positive_int(value: str, *, label: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"{label} must be positive")
    return parsed


def parse_positive_int_list(value: str, *, label: str) -> tuple[int, ...]:
    parts = [part.strip() for part in value.split(",")]
    parsed = tuple(_positive_int(part, label=label) for part in parts if part)
    if not parsed:
        raise argparse.ArgumentTypeError(f"{label} requires at least one value")
    return parsed


def scenario_grid(
    *,
    global_caps: tuple[int, ...],
    per_role_caps: tuple[int, ...],
    max_items_values: tuple[int, ...],
    work_items: int,
) -> list[CapacityScenario]:
    return [
        CapacityScenario(
            global_cap=global_cap,
            per_role_cap=per_role_cap,
            max_items=max_items,
            work_items=work_items,
        )
        for global_cap, per_role_cap, max_items in itertools.product(
            global_caps,
            per_role_caps,
            max_items_values,
        )
    ]


def _binding_constraint(scenario: CapacityScenario, batch_count: int) -> str:
    ceilings = {
        "global_cap": scenario.global_cap,
        "per_role_cap": scenario.per_role_cap,
        "workload_batch_count": batch_count,
    }
    return min(ceilings.items(), key=lambda item: (item[1], item[0]))[0]


def _constraint_evidence(binding_constraint: str) -> dict[str, str]:
    return {
        "provider_rate_limit": "not_exercised_in_default_local_mode",
        "git_index_lock": "not_exercised_in_default_local_mode",
        "sqlite_write_serialization": "modeled_as_binding_constraint_input_for_wi5031",
        "host_cpu_ram": "sampled_by_wall_clock_duration_of_local_worker_waves",
        "hung_worker_slot_retention": "not_exercised_in_default_local_mode",
        "binding_constraint": binding_constraint,
    }


def _run_local_worker(duration_ms: float) -> None:
    if duration_ms > 0:
        time.sleep(duration_ms / 1000.0)


def observe_scenario(scenario: CapacityScenario, *, worker_duration_ms: float) -> CapacityObservation:
    batch_count = math.ceil(scenario.work_items / scenario.max_items)
    logical_worker_count = max(1, min(scenario.global_cap, scenario.per_role_cap, batch_count))
    waves = math.ceil(batch_count / logical_worker_count)
    binding_constraint = _binding_constraint(scenario, batch_count)

    started = time.perf_counter()
    for _wave in range(waves):
        with ThreadPoolExecutor(max_workers=logical_worker_count) as pool:
            futures = [pool.submit(_run_local_worker, worker_duration_ms) for _ in range(logical_worker_count)]
            for future in futures:
                future.result()
    elapsed = max(time.perf_counter() - started, 0.000001)
    throughput = scenario.work_items / elapsed
    return CapacityObservation(
        global_cap=scenario.global_cap,
        per_role_cap=scenario.per_role_cap,
        max_items=scenario.max_items,
        work_items=scenario.work_items,
        batch_count=batch_count,
        logical_worker_count=logical_worker_count,
        waves=waves,
        binding_constraint=binding_constraint,
        observed_duration_seconds=elapsed,
        throughput_items_per_second=throughput,
        constraint_evidence=_constraint_evidence(binding_constraint),
    )


def recommend_safe_ceiling(observations: list[CapacityObservation]) -> dict[str, Any]:
    if not observations:
        return {"status": "no_observations"}
    best = max(observations, key=lambda item: item.throughput_items_per_second)
    return {
        "status": "measured",
        "basis": "highest_local_throughput_in_deterministic_simulation",
        "global_cap": best.global_cap,
        "per_role_cap": best.per_role_cap,
        "max_items": best.max_items,
        "binding_constraint": best.binding_constraint,
        "throughput_items_per_second": best.throughput_items_per_second,
    }


def run_capacity_benchmark(
    *,
    global_caps: tuple[int, ...] = DEFAULT_GLOBAL_CAPS,
    per_role_caps: tuple[int, ...] = DEFAULT_PER_ROLE_CAPS,
    max_items_values: tuple[int, ...] = DEFAULT_MAX_ITEMS_VALUES,
    work_items: int = DEFAULT_WORK_ITEMS,
    worker_duration_ms: float = DEFAULT_WORKER_DURATION_MS,
    mode: str = MODE_SIMULATED_LOCAL,
    allow_provider_live: bool = False,
) -> CapacityBenchmarkReport:
    if mode == MODE_PROVIDER_LIVE and not allow_provider_live:
        raise ProviderLiveDispatchNotAllowed(
            "provider-backed live dispatch requires --allow-provider-live; default benchmark is local-only"
        )
    if mode == MODE_PROVIDER_LIVE:
        raise NotImplementedError("provider-backed live dispatch is gated but not implemented by this local benchmark")

    scenarios = scenario_grid(
        global_caps=global_caps,
        per_role_caps=per_role_caps,
        max_items_values=max_items_values,
        work_items=work_items,
    )
    observations = [observe_scenario(scenario, worker_duration_ms=worker_duration_ms) for scenario in scenarios]
    return CapacityBenchmarkReport(
        schema_version=1,
        mode=mode,
        provider_backed=False,
        real_side_effects=False,
        explicit_provider_flag_required=True,
        scenario_count=len(observations),
        observations=observations,
        recommended_safe_ceiling=recommend_safe_ceiling(observations),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the WI-5030 local dispatch capacity benchmark.")
    parser.add_argument("--global-caps", default=",".join(str(v) for v in DEFAULT_GLOBAL_CAPS))
    parser.add_argument("--per-role-caps", default=",".join(str(v) for v in DEFAULT_PER_ROLE_CAPS))
    parser.add_argument("--max-items-values", default=",".join(str(v) for v in DEFAULT_MAX_ITEMS_VALUES))
    parser.add_argument(
        "--work-items", type=lambda value: _positive_int(value, label="work-items"), default=DEFAULT_WORK_ITEMS
    )
    parser.add_argument("--worker-duration-ms", type=float, default=DEFAULT_WORKER_DURATION_MS)
    parser.add_argument("--mode", choices=(MODE_SIMULATED_LOCAL, MODE_PROVIDER_LIVE), default=MODE_SIMULATED_LOCAL)
    parser.add_argument(
        "--allow-provider-live", action="store_true", help="Explicitly allow provider-backed live mode."
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.worker_duration_ms < 0:
        parser.error("--worker-duration-ms must be non-negative")

    try:
        report = run_capacity_benchmark(
            global_caps=parse_positive_int_list(args.global_caps, label="global-caps"),
            per_role_caps=parse_positive_int_list(args.per_role_caps, label="per-role-caps"),
            max_items_values=parse_positive_int_list(args.max_items_values, label="max-items-values"),
            work_items=args.work_items,
            worker_duration_ms=args.worker_duration_ms,
            mode=args.mode,
            allow_provider_live=args.allow_provider_live,
        )
    except ProviderLiveDispatchNotAllowed as exc:
        parser.error(str(exc))
    payload = report.to_json_dict()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        ceiling = payload["recommended_safe_ceiling"]
        print(
            "Recommended local ceiling: "
            f"global={ceiling.get('global_cap')} "
            f"per_role={ceiling.get('per_role_cap')} "
            f"max_items={ceiling.get('max_items')} "
            f"binding={ceiling.get('binding_constraint')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
