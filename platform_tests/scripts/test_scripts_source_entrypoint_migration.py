"""Integration checks for WI-4333 scripts-source harness-state migration."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "groundtruth-kb" / "src"
for path in (REPO_ROOT, SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _projection() -> dict[str, Any]:
    return {
        "harnesses": [
            {
                "id": "A",
                "harness_name": "codex",
                "harness_type": "codex",
                "role": ["loyal-opposition"],
            },
            {
                "id": "C",
                "harness_name": "antigravity",
                "harness_type": "antigravity",
                "status": "registered",
                "role": ["loyal-opposition"],
                "invocation_surfaces": {"headless": {"argv": ["gemini", "--prompt", "{prompt}"]}},
            },
        ]
    }


def test_cross_harness_trigger_uses_projection_reader_shim(monkeypatch: Any, tmp_path: Path) -> None:
    """The trigger adapts the canonical projection without direct JSON reads."""
    import scripts.cross_harness_bridge_trigger as trigger

    calls: list[Path] = []

    def fake_load_harness_projection(project_root: Path) -> dict[str, Any]:
        calls.append(project_root)
        return _projection()

    monkeypatch.setattr(trigger, "load_harness_projection", fake_load_harness_projection)

    roles_doc = trigger._read_role_assignments(tmp_path)
    identities_doc = trigger._read_harness_identities(tmp_path)

    assert roles_doc["harnesses"]["A"]["role"] == ["loyal-opposition"]
    assert identities_doc["harnesses"]["codex"]["id"] == "A"
    assert calls == [tmp_path, tmp_path]


def test_verify_antigravity_dispatch_uses_projection_reader_shim(monkeypatch: Any, tmp_path: Path) -> None:
    """Antigravity dispatch verification loads recipient records via the shim."""
    import scripts.verify_antigravity_dispatch as verify

    calls: list[Path] = []

    def fake_load_harness_projection(project_root: Path) -> dict[str, Any]:
        calls.append(project_root)
        return _projection()

    monkeypatch.setattr(verify, "load_harness_projection", fake_load_harness_projection)

    record = verify.load_harness_record(tmp_path, "C")

    assert record["harness_name"] == "antigravity"
    assert calls == [tmp_path]


def test_system_interface_map_has_no_retired_role_assignment_authority() -> None:
    """Config may retain retired-evidence mentions, but not live authority."""
    text = (REPO_ROOT / "config" / "agent-control" / "system-interface-map.toml").read_text(encoding="utf-8")

    assert 'authoritative_source = "harness-state/role-assignments.json"' not in text
    assert 'read_method = "Read harness-state/role-assignments.json after resolving harness identity."' not in text
    assert 'authoritative_source = "harness-state/harness-registry.json"' in text
    assert "groundtruth_kb.harness_projection.read_roles" in text
