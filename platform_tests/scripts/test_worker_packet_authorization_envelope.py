# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression tests for dispatch-created implementation authorization packets."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUTH_PATH = PROJECT_ROOT / "scripts" / "implementation_authorization.py"


@pytest.fixture(scope="module")
def auth_module():
    name = "implementation_authorization_worker_packet_test"
    spec = importlib.util.spec_from_file_location(name, AUTH_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_index(project_root: Path, blocks: list[str]) -> None:
    path = project_root / "bridge" / "INDEX.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Bridge Index\n\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")


def _write_proposal(project_root: Path, slug: str, target_paths: list[str]) -> None:
    path = project_root / "bridge" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# Fixture proposal {slug}",
                "",
                f"target_paths: {json.dumps(target_paths)}",
                "",
                "## Specification Links",
                "",
                "- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge authority.",
                "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - spec linkage.",
                "",
                "## Requirement Sufficiency",
                "",
                "Existing requirements are sufficient.",
                "",
                "## Verification Plan",
                "",
                "Run `python -m pytest platform_tests/scripts/test_worker_packet_authorization_envelope.py -q`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (project_root / "bridge" / f"{slug}-002.md").write_text("GO\n\nFixture GO.\n", encoding="utf-8")


def _setup_go(project_root: Path, slug: str, target_paths: list[str]) -> None:
    (project_root / "groundtruth.toml").write_text("# synthetic root\n", encoding="utf-8")
    _write_proposal(project_root, slug, target_paths)
    _write_index(project_root, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])


def test_dispatch_issue_writes_named_packets_and_current_pointer(auth_module, tmp_path: Path) -> None:
    _setup_go(tmp_path, "bridge-a", ["scripts/a.py"])
    _setup_go(tmp_path, "bridge-b", ["scripts/b.py"])
    _write_index(
        tmp_path,
        [
            "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b.md\n",
            "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a.md\n",
        ],
    )

    context = auth_module.issue_dispatch_authorization_packets(
        tmp_path,
        ["bridge-a", "bridge-b"],
        dispatch_id="dispatch-123",
    )

    assert context["dispatch_id"] == "dispatch-123"
    assert context["current_bridge_id"] == "bridge-a"
    assert [packet["bridge_id"] for packet in context["packets"]] == ["bridge-a", "bridge-b"]
    assert json.loads(auth_module.packet_path(tmp_path).read_text(encoding="utf-8"))["bridge_id"] == "bridge-a"
    assert auth_module.packet_path_for_bridge(tmp_path, "bridge-a").is_file()
    assert auth_module.packet_path_for_bridge(tmp_path, "bridge-b").is_file()


def test_dispatch_issue_fails_without_partial_writes(auth_module, tmp_path: Path) -> None:
    _setup_go(tmp_path, "bridge-a", ["scripts/a.py"])
    _write_index(
        tmp_path,
        [
            "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a.md\n",
            "Document: missing-bridge\nGO: bridge/missing-bridge-002.md\nNEW: bridge/missing-bridge.md\n",
        ],
    )

    with pytest.raises(auth_module.AuthorizationError):
        auth_module.issue_dispatch_authorization_packets(
            tmp_path,
            ["bridge-a", "missing-bridge"],
            dispatch_id="dispatch-123",
        )

    assert not auth_module.packet_path(tmp_path).exists()
    assert not auth_module.packet_path_for_bridge(tmp_path, "bridge-a").exists()
