from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "benchmarks" / "live_dispatch_capacity_benchmark.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("live_dispatch_capacity_benchmark", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_default_benchmark_is_local_and_side_effect_free() -> None:
    mod = _load_module()
    report = mod.run_capacity_benchmark(
        global_caps=(8,),
        per_role_caps=(3,),
        max_items_values=(4,),
        work_items=12,
        worker_duration_ms=0,
    )
    payload = report.to_json_dict()

    assert payload["mode"] == mod.MODE_SIMULATED_LOCAL
    assert payload["provider_backed"] is False
    assert payload["real_side_effects"] is False
    assert payload["scenario_count"] == 1
    observation = payload["observations"][0]
    assert observation["logical_worker_count"] == 3
    assert observation["binding_constraint"] == "per_role_cap"
    assert observation["constraint_evidence"]["provider_rate_limit"] == "not_exercised_in_default_local_mode"


def test_sweep_reports_recommended_safe_ceiling() -> None:
    mod = _load_module()
    report = mod.run_capacity_benchmark(
        global_caps=(1, 2),
        per_role_caps=(1, 2),
        max_items_values=(2,),
        work_items=8,
        worker_duration_ms=0,
    )
    payload = report.to_json_dict()

    assert payload["scenario_count"] == 4
    ceiling = payload["recommended_safe_ceiling"]
    assert ceiling["status"] == "measured"
    assert ceiling["global_cap"] in {1, 2}
    assert ceiling["per_role_cap"] in {1, 2}
    assert ceiling["max_items"] == 2
    assert ceiling["throughput_items_per_second"] > 0


def test_provider_live_mode_requires_explicit_flag() -> None:
    mod = _load_module()
    with pytest.raises(mod.ProviderLiveDispatchNotAllowed):
        mod.run_capacity_benchmark(mode=mod.MODE_PROVIDER_LIVE)


def test_cli_emits_json_for_small_local_sweep(capsys: pytest.CaptureFixture[str]) -> None:
    mod = _load_module()
    exit_code = mod.main(
        [
            "--global-caps",
            "2",
            "--per-role-caps",
            "2",
            "--max-items-values",
            "2",
            "--work-items",
            "4",
            "--worker-duration-ms",
            "0",
            "--json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["scenario_count"] == 1
    assert payload["observations"][0]["batch_count"] == 2
