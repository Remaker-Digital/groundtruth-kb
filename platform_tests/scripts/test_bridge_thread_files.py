from __future__ import annotations

from pathlib import Path

from scripts import bridge_thread_files as helper


def test_exact_thread_files_ignore_prefix_siblings_and_drafts(tmp_path: Path) -> None:
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    for name in (
        "gtkb-finalization-tooling-batch-001.md",
        "gtkb-finalization-tooling-batch-002.md",
        "gtkb-finalization-tooling-batch-exact-target-amendment-003.md",
        "gtkb-finalization-tooling-batch-004-draft.md",
        "gtkb-finalization-tooling-batch-draft-005.md",
    ):
        (bridge / name).write_text("NEW\n", encoding="utf-8")

    paths = helper.versioned_bridge_files(tmp_path, "gtkb-finalization-tooling-batch")

    assert [path.name for path in paths] == [
        "gtkb-finalization-tooling-batch-001.md",
        "gtkb-finalization-tooling-batch-002.md",
    ]


def test_latest_status_uses_exact_canonical_chain(tmp_path: Path) -> None:
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "example-thread-001.md").write_text("NEW\n", encoding="utf-8")
    (bridge / "example-thread-child-999.md").write_text("VERIFIED\n", encoding="utf-8")
    (bridge / "example-thread-002-draft.md").write_text("VERIFIED\n", encoding="utf-8")
    (bridge / "example-thread-002.md").write_text("GO\n", encoding="utf-8")

    assert helper.latest_bridge_status_for_thread(tmp_path, "example-thread") == "GO"


def test_status_reader_ignores_envelope_lines_after_status(tmp_path: Path) -> None:
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "enveloped-thread-001.md").write_text(
        "NEW\n::init gtkb lo\n::open build\n\n# Proposal\n",
        encoding="utf-8",
    )
    (bridge / "legacy-thread-001.md").write_text("NO-GO\n\n# Legacy verdict\n", encoding="utf-8")

    assert helper.latest_bridge_status_for_thread(tmp_path, "enveloped-thread") == "NEW"
    assert helper.latest_bridge_status_for_thread(tmp_path, "legacy-thread") == "NO-GO"
