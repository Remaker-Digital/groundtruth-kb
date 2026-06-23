"""Regression tests for the Codex apply_patch bridge-compliance adapter."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-gate-apply-patch-adapter.py"


def _load_adapter():
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_apply_patch_adapter", ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_extract_bridge_writes_includes_bridge_index_update(tmp_path: Path) -> None:
    adapter = _load_adapter()
    index_path = tmp_path / "bridge" / "INDEX.md"
    index_path.parent.mkdir()
    index_path.write_text(
        "Document: sample\nNEW: bridge/sample-001.md\n",
        encoding="utf-8",
    )

    patch = """*** Begin Patch
*** Update File: bridge/INDEX.md
@@
 Document: sample
+GO: bridge/sample-002.md
 NEW: bridge/sample-001.md
*** End Patch
"""

    writes = adapter.extract_bridge_writes(patch, root=tmp_path)

    assert len(writes) == 1
    assert writes[0].file_path == "bridge/INDEX.md"
    assert writes[0].content == "Document: sample\nGO: bridge/sample-002.md\nNEW: bridge/sample-001.md\n"


def test_apply_patch_adapter_rejects_malformed_bridge_index_via_canonical_gate(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    adapter = _load_adapter()
    index_path = tmp_path / "bridge" / "INDEX.md"
    index_path.parent.mkdir()
    index_path.write_text(
        "Document: sample\nNEW: bridge/sample-001.md\n",
        encoding="utf-8",
    )
    patch = """*** Begin Patch
*** Update File: bridge/INDEX.md
@@
 Document: sample
+BROKEN: literal \\n text
 NEW: bridge/sample-001.md
*** End Patch
"""
    payload = {"cwd": str(tmp_path), "tool_input": {"patch": patch}}
    calls = []

    def fake_run_canonical(payload_arg, write):
        calls.append((payload_arg, write))
        return 2, '{"decision": "deny", "reason": "bridge/INDEX.md is malformed"}', ""

    monkeypatch.setattr(adapter, "_run_canonical", fake_run_canonical)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))

    assert adapter.main() == 2

    captured = capsys.readouterr()
    assert "bridge/INDEX.md is malformed" in captured.out
    assert len(calls) == 1
    assert calls[0][1].file_path == "bridge/INDEX.md"
    assert "literal \\n text" in calls[0][1].content


def test_extract_bridge_writes_preserves_versioned_bridge_file_behavior(tmp_path: Path) -> None:
    adapter = _load_adapter()
    patch = """*** Begin Patch
*** Add File: bridge/sample-003.md
+NEW
+
+bridge_kind: implementation_report
*** End Patch
"""

    writes = adapter.extract_bridge_writes(patch, root=tmp_path)

    assert len(writes) == 1
    assert writes[0].file_path == "bridge/sample-003.md"
    assert writes[0].content == "NEW\n\nbridge_kind: implementation_report\n"


def test_extract_bridge_writes_includes_lo_verdict_file(tmp_path: Path) -> None:
    adapter = _load_adapter()
    patch = """*** Begin Patch
*** Add File: bridge/sample-003.lo-verdict.md
+GO
+
+# Loyal Opposition Verdict
*** End Patch
"""

    writes = adapter.extract_bridge_writes(patch, root=tmp_path)

    assert len(writes) == 1
    assert writes[0].file_path == "bridge/sample-003.lo-verdict.md"
    assert writes[0].content == "GO\n\n# Loyal Opposition Verdict\n"


def test_apply_patch_adapter_blocks_overwrite_of_existing_versioned_bridge_file(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """Adapter propagates the canonical gate denial when apply_patch targets an existing
    versioned bridge file — the overwrite guard fires for the apply_patch path (WI-4740)."""
    adapter = _load_adapter()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    existing = bridge_dir / "gtkb-demo-001.md"
    existing.write_text("NEW\n\n# Original proposal\n", encoding="utf-8")

    patch = """*** Begin Patch
*** Update File: bridge/gtkb-demo-001.md
@@
 NEW

-# Original proposal
+# Overwritten proposal - should fail
*** End Patch
"""
    payload = {"cwd": str(tmp_path), "tool_input": {"patch": patch}}
    calls: list = []

    def fake_run_canonical(payload_arg, write):
        calls.append(write)
        return (
            2,
            '{"decision": "deny", "reason": "Bridge append-only boundary violation: '
            'gtkb-demo-001.md already exists on disk."}',
            "",
        )

    monkeypatch.setattr(adapter, "_run_canonical", fake_run_canonical)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))

    result = adapter.main()

    assert result == 2
    assert len(calls) >= 1
    captured = capsys.readouterr()
    assert "Bridge append-only boundary violation" in captured.out
