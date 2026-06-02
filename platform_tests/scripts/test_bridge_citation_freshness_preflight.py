from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "bridge_citation_freshness_preflight.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("bridge_citation_freshness_preflight", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _bridge_dir(tmp_path: Path, index_text: str) -> Path:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(index_text, encoding="utf-8")
    return bridge_dir


def _content_file(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "proposal.md"
    path.write_text(text, encoding="utf-8")
    return path


def _packet(module: ModuleType, tmp_path: Path, index_text: str, content: str, *, bridge_id: str = "target") -> dict:
    bridge_dir = _bridge_dir(tmp_path, index_text)
    content_file = _content_file(tmp_path, content)
    return module.build_packet(
        bridge_id=bridge_id,
        index_path=bridge_dir / "INDEX.md",
        bridge_dir=bridge_dir,
        content_file=content_file,
    )


def test_matching_version_no_warning(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\nDocument: other-thread\nGO: bridge/other-thread-003.md\n",
        "Approved reference: bridge/other-thread-003.md\n",
    )

    assert packet["warnings"] == []
    assert packet["missing_citations"] == []
    assert "No stale cross-thread citations detected." in packet["markdown"]


def test_stale_version_warning(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: runtime-thread\nVERIFIED: bridge/runtime-thread-004.md\n"
        "GO: bridge/runtime-thread-003.md\n",
        "Prior runtime evidence: bridge/runtime-thread-003.md\n",
    )

    assert packet["warning_count"] == 1
    warning = packet["warnings"][0]
    assert warning["cited_slug"] == "runtime-thread"
    assert warning["cited_version"] == 3
    assert warning["latest_version"] == 4
    assert warning["latest_status"] == "VERIFIED"
    assert "bridge/runtime-thread-004.md" in warning["cleanup_hint"]


def test_multi_citation_warnings(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: alpha-thread\nNO-GO: bridge/alpha-thread-002.md\n"
        "NEW: bridge/alpha-thread-001.md\n\n"
        "Document: beta-thread\nVERIFIED: bridge/beta-thread-005.md\n"
        "GO: bridge/beta-thread-004.md\n",
        "Old alpha bridge/alpha-thread-001.md and old beta bridge/beta-thread-004.md\n",
    )

    assert packet["warning_count"] == 2
    assert {warning["cited_slug"] for warning in packet["warnings"]} == {"alpha-thread", "beta-thread"}


def test_slug_not_in_index_handled(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n",
        "Unresolved citation: bridge/not-in-index-001.md\n",
    )

    assert packet["warning_count"] == 0
    assert packet["missing_count"] == 1
    missing = packet["missing_citations"][0]
    assert missing["cited_slug"] == "not-in-index"
    assert "not found in bridge/INDEX.md" in missing["cleanup_hint"]


def test_wi3267_fixture_workflow_contract_adr_citation(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: workflow-contract-adr\nNO-GO: bridge/workflow-contract-adr-008.md\n"
        "REVISED: bridge/workflow-contract-adr-007.md\n",
        "The workflow-contract-adr thread was described as REVISED-3 at -007 in the review context.\n",
    )

    assert packet["warning_count"] == 1
    assert packet["warnings"][0]["cited_slug"] == "workflow-contract-adr"
    assert packet["warnings"][0]["latest_version"] == 8


def test_wi3267_fixture_runtime_thread_citation(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: gtkb-bridge-advisory-status\nNO-GO: bridge/gtkb-bridge-advisory-status-008.md\n"
        "REVISED: bridge/gtkb-bridge-advisory-status-007.md\n",
        "Runtime thread citation: gtkb-bridge-advisory-status was REVISED-3 at -007 before review.\n",
    )

    assert packet["warning_count"] == 1
    warning = packet["warnings"][0]
    assert warning["cited_slug"] == "gtkb-bridge-advisory-status"
    assert warning["latest_status"] == "NO-GO"


def test_warning_payload_includes_latest_version_and_cleanup_hint(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: cited-thread\nGO: bridge/cited-thread-006.md\n"
        "REVISED: bridge/cited-thread-005.md\n",
        "See bridge/cited-thread-005.md\n",
    )

    warning = packet["warnings"][0]
    assert set(warning).issuperset({"latest_version", "latest_path", "latest_status", "severity", "cleanup_hint"})
    assert warning["severity"] == "warn"
    assert "Update the citation" in warning["cleanup_hint"]


def test_citeable_markdown_section_emitted(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: cited-thread\nGO: bridge/cited-thread-002.md\n"
        "NEW: bridge/cited-thread-001.md\n",
        "See bridge/cited-thread-001.md\n",
    )

    markdown = packet["markdown"]
    assert markdown.startswith("## Citation Freshness\n")
    assert "| Cited Thread | Cited Version | Latest Version | Latest Status | Cleanup Hint |" in markdown
    assert "`cited-thread`" in markdown


def test_self_reference_not_flagged(tmp_path: Path) -> None:
    module = _load_module()
    packet = _packet(
        module,
        tmp_path,
        "Document: self-thread\nVERIFIED: bridge/self-thread-003.md\n"
        "NEW: bridge/self-thread-002.md\n\n"
        "Document: other-thread\nGO: bridge/other-thread-002.md\n",
        "This implementation report cites itself as bridge/self-thread-002.md.\n",
        bridge_id="self-thread",
    )

    assert packet["warnings"] == []
    assert packet["missing_citations"] == []


def test_json_output_schema(tmp_path: Path) -> None:
    bridge_dir = _bridge_dir(
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: cited-thread\nGO: bridge/cited-thread-002.md\n"
        "NEW: bridge/cited-thread-001.md\n",
    )
    content_file = _content_file(tmp_path, "See bridge/cited-thread-001.md\n")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--bridge-id",
            "target",
            "--index-path",
            str(bridge_dir / "INDEX.md"),
            "--bridge-dir",
            str(bridge_dir),
            "--content-file",
            str(content_file),
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert set(payload).issuperset(
        {"bridge_id", "content_file", "index_path", "citations", "warnings", "missing_citations", "markdown"}
    )
    assert payload["warnings"][0]["latest_version"] == 2


def test_exit_code_advisory_zero(tmp_path: Path) -> None:
    bridge_dir = _bridge_dir(
        tmp_path,
        "Document: target\nNEW: bridge/target-001.md\n\n"
        "Document: cited-thread\nGO: bridge/cited-thread-002.md\n"
        "NEW: bridge/cited-thread-001.md\n",
    )
    content_file = _content_file(tmp_path, "See bridge/cited-thread-001.md\n")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--bridge-id",
            "target",
            "--index-path",
            str(bridge_dir / "INDEX.md"),
            "--bridge-dir",
            str(bridge_dir),
            "--content-file",
            str(content_file),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "cited-thread" in result.stdout
