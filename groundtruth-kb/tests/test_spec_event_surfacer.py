"""The retired specification-event hook is absent from new managed delivery.

Retirement of SPEC-INTAKE-2485e9 removes event polling and per-session ledgers.
Upgrade preservation and exact command removal are exercised separately through
the existing upgrade planner and executor in test_settings_merge_drift.py.
"""

from __future__ import annotations

import pytest

from groundtruth_kb import get_templates_dir
from groundtruth_kb.project.managed_registry import (
    artifacts_for_doctor,
    artifacts_for_scaffold,
    artifacts_for_upgrade,
)


@pytest.mark.parametrize("profile", ["local-only", "dual-agent", "dual-agent-webapp"])
def test_scaffold_upgrade_and_doctor_do_not_deliver_the_retired_event_hook(profile):
    assert not (get_templates_dir() / "hooks/spec-event-surfacer.py").exists()
    for select in (artifacts_for_scaffold, artifacts_for_upgrade, artifacts_for_doctor):
        records = select(profile)
        assert all(
            record.id not in {"hook.spec-event-surfacer", "settings.hook.spec-event-surfacer.posttooluse"}
            for record in records
        )


@pytest.mark.parametrize(
    "harness", ["goose", "claude", "codex", "cursor", "antigravity", "ollama", "openrouter", "alibaba-cloud-studio"]
)
def test_projectors_do_not_emit_or_register_specification_event_polling(harness):
    from scripts.harness_projection import project_harness

    plan = project_harness.build_plan(harness)
    assert plan.writes and not plan.gaps, plan.gaps
    assert not any(path.endswith("/spec-event-surfacer.py") for path in plan.writes)
    assert not any("spec-event-surfacer.py" in content for content in plan.writes.values())
