from __future__ import annotations

from typing import Any

from groundtruth_kb.harness_projection import build_projection


def _projected_record(invocation_surfaces: dict[str, Any]) -> dict[str, Any]:
    row = {
        "id": "D",
        "harness_name": "ollama",
        "harness_type": "ollama",
        "role": ["loyal-opposition"],
        "status": "active",
        "invocation_surfaces": invocation_surfaces,
    }
    return build_projection([row])["harnesses"][0]


def test_canonical_dispatch_eligibility_precedes_headless_fallback() -> None:
    record = _projected_record(
        {
            "dispatch": {"can_receive_dispatch": False, "can_fire_events": True},
            "headless": {"argv": ["python", "scripts/ollama_harness.py"], "can_receive_dispatch": True},
        }
    )

    assert record["can_receive_dispatch"] is False
    assert record["can_fire_events"] is False
    assert record["invocation_surfaces"]["dispatch"]["can_fire_events"] is False


def test_headless_eligibility_remains_a_fallback_when_dispatch_value_is_absent() -> None:
    record = _projected_record(
        {
            "dispatch": {"can_fire_events": True},
            "headless": {"argv": ["python", "scripts/ollama_harness.py"], "can_receive_dispatch": True},
        }
    )

    assert record["can_receive_dispatch"] is True
    assert record["can_fire_events"] is False
