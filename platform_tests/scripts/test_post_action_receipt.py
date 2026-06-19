"""Tests for the post-action audit receipt contract."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "post_action_receipt.py"


@pytest.fixture(scope="module")
def receipt_module():
    spec = importlib.util.spec_from_file_location("post_action_receipt", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["post_action_receipt"] = module
    spec.loader.exec_module(module)
    return module


def _receipt(receipt_module, **overrides: Any):
    values: dict[str, Any] = {
        "receipt_id": "receipt-001",
        "generated_at": "2026-06-19T12:00:00Z",
        "mutation_class": "file",
        "action_summary": "Added a post-action receipt module.",
        "initiating_authority": "PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA",
        "bridge_thread": "agent-disposition-wi4590-post-action-receipts-slice1",
        "bridge_version": "002",
        "work_item": "WI-4590",
        "target_paths": ("scripts/post_action_receipt.py",),
        "commands_run": ({"command": "pytest", "exit_code": 0},),
        "verification_evidence": ({"kind": "pytest", "observed": "1 passed"},),
        "residual_dirty_tree": ("scripts/post_action_receipt.py",),
        "commit_push_recommended": False,
        "commit_push_rationale": "Commit after Loyal Opposition verification.",
        "author_identity": "prime-builder/codex",
        "author_harness_id": "A",
        "author_session_context_id": "dispatch-session",
        "author_model": "gpt-5-codex",
    }
    values.update(overrides)
    return receipt_module.PostActionReceipt(**values)


def test_validate_receipt_rejects_each_required_field(receipt_module) -> None:
    for field_name in receipt_module.REQUIRED_TEXT_FIELDS:
        receipt = receipt_module.receipt_to_dict(_receipt(receipt_module))
        receipt[field_name] = ""

        errors = receipt_module.validate_receipt(receipt)

        assert any(field_name in error for error in errors)


def test_validate_receipt_rejects_invalid_mutation_class(receipt_module) -> None:
    receipt = _receipt(receipt_module, mutation_class="database")

    errors = receipt_module.validate_receipt(receipt)

    assert any("mutation_class" in error for error in errors)


def test_validate_receipt_rejects_missing_initiating_authority(receipt_module) -> None:
    receipt = _receipt(receipt_module, initiating_authority="")

    errors = receipt_module.validate_receipt(receipt)

    assert any("initiating_authority" in error for error in errors)


def test_validate_receipt_rejects_missing_author_provenance(receipt_module) -> None:
    receipt = _receipt(receipt_module, author_harness_id="")

    errors = receipt_module.validate_receipt(receipt)

    assert any("author_harness_id" in error for error in errors)


def test_write_receipt_round_trips_and_refuses_overwrite(receipt_module, tmp_path: Path) -> None:
    receipt = _receipt(receipt_module)

    path = receipt_module.write_receipt(receipt, project_root=tmp_path)

    assert path == tmp_path / ".gtkb-state" / "post-action-receipts" / "2026-06-19" / "receipt-001.json"
    assert json.loads(path.read_text(encoding="utf-8")) == receipt_module.receipt_to_dict(receipt)
    with pytest.raises(FileExistsError):
        receipt_module.write_receipt(receipt, project_root=tmp_path)


def test_write_receipt_isolated_to_post_action_receipts(receipt_module, tmp_path: Path) -> None:
    path = receipt_module.write_receipt(_receipt(receipt_module), project_root=tmp_path)

    assert path.relative_to(tmp_path).as_posix().startswith(".gtkb-state/post-action-receipts/")
    assert not (tmp_path / "groundtruth.db").exists()
    assert not (tmp_path / "bridge").exists()


def _write_packet(root: Path, slug: str) -> None:
    packet = {
        "bridge_id": slug,
        "go_file": f"bridge/{slug}-002.md",
        "packet_hash": "sha256:fixture",
        "project_authorization": {
            "id": "PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA",
            "work_item_id": "WI-4590",
        },
        "target_path_globs": ["./scripts/post_action_receipt.py"],
    }
    packet_dir = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    packet_dir.mkdir(parents=True, exist_ok=True)
    (packet_dir / f"{slug}.json").write_text(json.dumps(packet), encoding="utf-8")


def _write_go_thread(root: Path, slug: str) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / f"{slug}-001.md").write_text("NEW\n\nFixture proposal.\n", encoding="utf-8")
    (bridge / f"{slug}-002.md").write_text("GO\n\nFixture verdict.\n", encoding="utf-8")


def _write_prime_registry(root: Path) -> None:
    registry = {
        "schema_version": 1,
        "harnesses": [{"id": "A", "harness_name": "codex", "role": ["prime-builder"], "status": "active"}],
    }
    registry_dir = root / "harness-state"
    registry_dir.mkdir(parents=True, exist_ok=True)
    (registry_dir / "harness-registry.json").write_text(json.dumps(registry), encoding="utf-8")


def _claim_work_intent(root: Path, slug: str) -> None:
    scripts_dir = PROJECT_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import bridge_work_intent_registry

    _write_go_thread(root, slug)
    _write_prime_registry(root)
    assert bridge_work_intent_registry.acquire(
        slug,
        "2026-06-19T12-16-32Z-prime-builder-A-abc123",
        project_root=root,
    )


def _init_git_dirty_tree(root: Path) -> None:
    if shutil.which("git") is None:
        pytest.skip("git is required for dirty-tree fixture")
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True, capture_output=True)
    tracked = root / "tracked.txt"
    tracked.write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
    tracked.write_text("dirty\n", encoding="utf-8")


def test_gather_evidence_correlates_claim_packet_and_dirty_tree(receipt_module, tmp_path: Path) -> None:
    slug = "agent-disposition-wi4590-post-action-receipts-slice1"
    _write_packet(tmp_path, slug)
    _claim_work_intent(tmp_path, slug)
    _init_git_dirty_tree(tmp_path)

    receipt = receipt_module.gather_evidence(
        project_root=tmp_path,
        bridge_thread=slug,
        action_summary="Add receipt contract.",
        commands_run=[{"command": "pytest", "exit_code": 0}],
        author_identity="prime-builder/codex",
        author_harness_id="A",
        author_session_context_id="2026-06-19T12-16-32Z-prime-builder-A-abc123",
        author_model="gpt-5-codex",
    )

    data = receipt_module.receipt_to_dict(receipt)
    assert data["initiating_authority"] == "PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA"
    assert data["work_item"] == "WI-4590"
    assert data["bridge_version"] == "002"
    assert data["target_paths"] == ["scripts/post_action_receipt.py"]
    assert "tracked.txt" in data["residual_dirty_tree"]
    assert data["evidence_sources"]["implementation_packet_present"] is True
    assert data["evidence_sources"]["work_intent_claim_present"] is True
    kinds = {item["kind"] for item in data["verification_evidence"] if isinstance(item, dict)}
    assert {"implementation_authorization_packet", "work_intent_claim"} <= kinds
    assert receipt_module.validate_receipt(receipt) == []


def test_gather_evidence_tolerates_missing_sources(receipt_module, tmp_path: Path) -> None:
    receipt = receipt_module.gather_evidence(
        project_root=tmp_path,
        bridge_thread="missing-thread",
        action_summary="Draft candidate.",
        initiating_authority="manual-authority",
        work_item="WI-4590",
        target_paths=["scripts/post_action_receipt.py"],
        author_identity="prime-builder/codex",
        author_harness_id="A",
        author_session_context_id="session",
        author_model="gpt-5-codex",
    )

    data = receipt_module.receipt_to_dict(receipt)
    assert data["bridge_thread"] == "missing-thread"
    assert data["evidence_sources"]["implementation_packet_present"] is False
    assert data["evidence_sources"]["work_intent_claim_present"] is False
