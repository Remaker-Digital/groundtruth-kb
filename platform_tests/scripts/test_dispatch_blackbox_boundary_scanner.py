from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_PATH = REPO_ROOT / "scripts" / "dispatch_blackbox_boundary_scanner.py"


@pytest.fixture(scope="module")
def scanner():
    spec = importlib.util.spec_from_file_location("dispatch_blackbox_boundary_scanner", SCANNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_blackbox_boundary_scanner"] = module
    spec.loader.exec_module(module)
    return module


def test_safe_worker_context_packet_has_no_findings(scanner) -> None:
    text = (
        "Ordinary worker uses gt bridge dispatch worker-context --self --json.\n"
        "The assigned-content packet is mediated and worker-safe.\n"
    )

    assert scanner.scan_text(text, source="safe.txt") == []


def test_boundary_scanner_classifies_violation_families(scanner) -> None:
    text = "\n".join(
        [
            "ordinary worker Get-Content harness-state/harness-registry.json",
            "ordinary worker apply_patch .gtkb-state/dispatcher-daemon/status.json",
            "assigned proposal came from bridge/gtkb-topic-001.md",
            "ops envelope may mutate dispatcher_runtime.py internals directly",
            "build envelope mutates black-box internals",
            "unsupported surface waiver accepted",
        ]
    )

    classes = [finding.finding_class for finding in scanner.scan_text(text, source="bad.txt")]

    assert "direct_protected_read" in classes
    assert "direct_protected_mutation" in classes
    assert "missing_worker_safe_packet_usage" in classes
    assert "ops_build_authority_confusion" in classes
    assert "case_authorization_bypass" in classes
    assert "unsupported_surface_waiver_gap" in classes


def test_case_authorization_evidence_prevents_build_bypass(scanner) -> None:
    text = (
        "Implementation-start evidence: implementation_authorization.py begin.\n"
        "build envelope mutates black-box internals for scripts/gtkb_dispatcher_daemon.py.\n"
    )

    classes = [finding.finding_class for finding in scanner.scan_text(text, source="authorized.txt")]

    assert "case_authorization_bypass" not in classes


def test_closure_status_blocks_on_nonterminal_member_work(scanner, tmp_path, monkeypatch) -> None:
    evidence = tmp_path / "safe.txt"
    evidence.write_text("ordinary worker uses worker-context assigned-content packet\n", encoding="utf-8")

    monkeypatch.setattr(
        scanner,
        "_member_completion_status",
        lambda _root, project_id: {
            "project_id": project_id,
            "completion_ready": False,
            "nonterminal_work_item_ids": ["WI-5401"],
        },
    )

    report = scanner.closure_status(
        project_root=tmp_path,
        project_id="PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
        evidence_paths=[evidence],
    )

    assert report["ready"] is False
    assert report["member_completion_ready"] is False
    assert report["blocking_boundary_finding_count"] == 0


def test_closure_status_blocks_on_boundary_findings(scanner, tmp_path, monkeypatch) -> None:
    evidence = tmp_path / "bad.txt"
    evidence.write_text("ordinary worker cat harness-state/harness-registry.json\n", encoding="utf-8")

    monkeypatch.setattr(
        scanner,
        "_member_completion_status",
        lambda _root, project_id: {
            "project_id": project_id,
            "completion_ready": True,
            "nonterminal_work_item_ids": [],
        },
    )

    report = scanner.closure_status(
        project_root=tmp_path,
        project_id="PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
        evidence_paths=[evidence],
    )

    assert report["ready"] is False
    assert report["member_completion_ready"] is True
    assert report["blocking_boundary_finding_count"] >= 1
    classes = {finding["finding_class"] for finding in report["findings"]}
    assert "direct_protected_read" in classes


def test_closure_status_ready_when_members_verified_and_scan_clean(scanner, tmp_path, monkeypatch) -> None:
    evidence = tmp_path / "safe.txt"
    evidence.write_text("ordinary worker uses worker-context assigned-content packet\n", encoding="utf-8")

    monkeypatch.setattr(
        scanner,
        "_member_completion_status",
        lambda _root, project_id: {
            "project_id": project_id,
            "completion_ready": True,
            "nonterminal_work_item_ids": [],
        },
    )

    report = scanner.closure_status(
        project_root=tmp_path,
        project_id="PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
        evidence_paths=[evidence],
    )

    assert report["ready"] is True
    assert report["boundary_finding_count"] == 0
